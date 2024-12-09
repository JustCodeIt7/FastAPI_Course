# SECTION 1: IMPORTS AND SETUP
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field, validator, field_validator
from typing import List, Optional
from datetime import datetime
import uvicorn

# Initialize FastAPI app with metadata
app = FastAPI(
    title="FastAPI Tutorial",
    description="A complete example of FastAPI with Pydantic",
    version="1.0.0",
)

# SECTION 2: PYDANTIC MODELS - BASE MODELS


# Address model to be reused in other models
class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

    # Example data for documentation purposes
    class Config:
        schema_extra = {
            "example": {
                "street": "123 Main St",
                "city": "New York",
                "country": "USA",
                "postal_code": "10001",
            }
        }


# SECTION 3: PYDANTIC MODELS - USER RELATED


# User data model with validation constraints
class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    full_name: Optional[str] = None
    age: int = Field(..., ge=0, le=120)
    address: Optional[Address] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "age": 30,
                "address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "country": "USA",
                    "postal_code": "10001",
                },
            }
        }


# SECTION 4: PYDANTIC MODELS - ORDER RELATED


# Order model with a custom validator for items
class Order(BaseModel):
    id: int
    items: List[str]
    total: float = Field(..., gt=0)
    customer_address: Address
    order_date: datetime = Field(default_factory=datetime.now)

    # Ensure the order has at least one item
    @field_validator("items")
    def validate_items(cls, v):
        if not v:
            raise ValueError("Order must contain at least one item")
        return v

    # Example data for documentation
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "items": ["item1", "item2"],
                "total": 99.99,
                "customer_address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "country": "USA",
                    "postal_code": "10001",
                },
            }
        }


# SECTION 5: PYDANTIC MODELS - USER AUTH RELATED


# Base user model for account management
class UserBase(BaseModel):
    username: str
    email: str


# Extends base user model with password for creation
class UserCreate(UserBase):
    password: str


# User response model excluding sensitive data
class UserResponse(UserBase):
    id: int
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "is_active": True,
            }
        }


# SECTION 6: ERROR HANDLERS


# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation Error",
            "errors": [
                {"loc": str(error["loc"]), "msg": error["msg"], "type": error["type"]}
                for error in exc.errors()
            ],
        },
    )


# Handle HTTP exceptions uniformly
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# SECTION 7: API ENDPOINTS - BASIC


# Root endpoint to confirm the API is up
@app.get("/")
async def root():
    return {"message": "Hello FastAPI!"}


# SECTION 8: API ENDPOINTS - USER OPERATIONS


# Endpoint to create a user with input validation
@app.post("/users/", response_model=User)
async def create_user(user: User):
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Username 'admin' is reserved")
    return user


# Endpoint for creating a user with password, returning limited info
@app.post("/users/create/", response_model=UserResponse)
async def create_user_with_password(user: UserCreate):
    # Simulated user creation process
    new_user = UserResponse(id=1, username=user.username, email=user.email)
    return new_user


# Endpoint to retrieve a user by username
@app.get("/users/{username}")
async def get_user(username: str):
    if username == "not_found":
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": username, "message": "User found"}


# Paginated list of users
@app.get("/users/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 10):
    users = [
        UserResponse(id=i, username=f"user{i}", email=f"user{i}@example.com")
        for i in range(skip, skip + limit)
    ]
    return users


# SECTION 9: API ENDPOINTS - ORDER OPERATIONS


# Endpoint to create an order with validation
@app.post("/orders/", response_model=Order)
async def create_order(order: Order):
    return order


# SECTION 10: MAIN EXECUTION

# Launch the application
if __name__ == "__main__":
    uvicorn.run("main-v2:app", host="0.0.0.0", port=8000, reload=True)
