# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date
import re

app = FastAPI(title="User Registration System")


# Pydantic Models
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    birth_date: date
    phone_number: Optional[str] = None

    # Custom validator for username
    @field_validator("username")
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v

    # Custom validator for phone number
    @field_validator("phone_number")
    def phone_number_format(cls, v):
        if v is None:
            return v
        pattern = re.compile(r"^\+?1?\d{9,15}$")
        if not pattern.match(v):
            raise ValueError("Invalid phone number format")
        return v


class UserCreate(UserBase):
    password: str

    # Custom validator for password strength
    @field_validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain an uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain a lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain a number")
        return v


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


# Simulated database
users_db = []
user_id_counter = 1


# API Endpoints
@app.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    global user_id_counter

    # Check if email already exists
    if any(u["email"] == user.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if username already exists
    if any(u["username"] == user.username for u in users_db):
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create user dictionary
    user_dict = user.dict()
    user_dict["id"] = user_id_counter
    users_db.append(user_dict)
    user_id_counter += 1

    # Remove password from response
    del user_dict["password"]
    return user_dict


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Example usage and testing
@app.get("/")
async def read_root():
    return {
        "message": "Welcome to User Registration System",
        "endpoints": {
            "create_user": "/users/ (POST)",
            "get_user": "/users/{user_id} (GET)",
        },
    }


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, log_level="debug", reload=True)
