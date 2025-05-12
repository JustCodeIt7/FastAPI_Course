from typing import Union, List, Dict, Optional
from fastapi import FastAPI, Query, Path, Body, HTTPException
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Request Body Tutorial API",
    description="A FastAPI app demonstrating request bodies for a YouTube tutorial",
    version="1.0.0"
)

# ==================== BASIC REQUEST BODY EXAMPLE ====================

class Item(BaseModel):
    """Basic Pydantic model for demonstrating request body validation"""
    name: str
    description: Optional[str] = Field(
        None, 
        title="Item description",
        description="Optional detailed description of the item",
        max_length=300
    )
    price: float = Field(..., gt=0, description="Price must be greater than zero")
    tax: Optional[float] = Field(None, ge=0, description="Tax amount if applicable")
    tags: List[str] = Field(default=[])
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Smartphone",
                "description": "Latest model with high-resolution camera",
                "price": 799.99,
                "tax": 79.99,
                "tags": ["electronics", "gadgets"]
            }
        }

@app.post("/items/", response_model=Dict[str, Union[str, Item]])
async def create_item(item: Item):
    """
    Create a new item with the provided details.
    
    This is the most basic example of using a request body.
    The Pydantic model validates the incoming JSON automatically.
    """
    # Calculate price with tax if tax is provided
    result = {"message": "Item created successfully", "item": item}
    return result

# ==================== NESTED MODELS EXAMPLE ====================

class Image(BaseModel):
    """Model for item images"""
    url: str
    name: Optional[str] = None
    
class ProductCategory(str, Enum):
    """Enum for product categories"""
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    FOOD = "food"
    OTHER = "other"

class Product(BaseModel):
    """Advanced model demonstrating nested models and complex validation"""
    id: Optional[int] = None
    name: str
    category: ProductCategory
    price: float = Field(..., gt=0)
    is_available: bool = True
    images: List[Image] = []
    metadata: Dict[str, str] = Field(default={})
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

@app.post("/products/", response_model=Product)
async def create_product(product: Product):
    """
    Create a product with a complex nested structure.
    
    This example shows:
    - Nested models (Product contains Image objects)
    - Enum validation
    - Custom validators
    - Dictionary fields
    """
    # In a real app, you would save to database here
    product.id = 123  # Simulating database ID assignment
    return product

# ==================== MULTIPLE BODY PARAMETERS ====================

class User(BaseModel):
    """User information model"""
    username: str
    email: str  # In a real app, you might want to use EmailStr from pydantic
    full_name: Optional[str] = None

@app.post("/order/")
async def create_order(
    user: User, 
    item: Item = Body(...),
    quantity: int = Body(..., gt=0),
    priority: bool = Body(False)
):
    """
    Create an order with multiple body parameters.
    
    This demonstrates how to receive multiple objects in the request body.
    FastAPI will expect a JSON with keys 'user', 'item', 'quantity', and 'priority'.
    """
    order_total = item.price * quantity
    if item.tax:
        tax_amount = item.tax * quantity
        order_total += tax_amount
    
    return {
        "user": user,
        "item": item,
        "quantity": quantity,
        "priority": priority,
        "order_total": order_total
    }

# ==================== BODY WITH PATH AND QUERY PARAMETERS ====================

@app.put("/items/{item_id}")
async def update_item(
    item_id: int = Path(..., title="The ID of the item to update", ge=1),
    item: Item = Body(...),
    q: Optional[str] = Query(None, max_length=50)
):
    """
    Update an item, combining path parameters, query parameters, and a request body.
    
    - Path parameter: item_id
    - Query parameter: q
    - Request body: item
    """
    result = {"message": "Item updated successfully", "item_id": item_id, "item": item}
    
    if q:
        result["query_param"] = q
        
    return result

# ==================== SINGULAR VALUES IN THE BODY ====================

@app.post("/items/{item_id}/set-importance")
async def set_item_importance(
    item_id: int,
    importance: int = Body(..., gt=0, lt=6),
    notes: Optional[str] = Body(None)
):
    """
    Set the importance level of an item.
    
    This demonstrates how to receive singular values in the request body,
    not wrapped in a model.
    """
    return {
        "item_id": item_id,
        "importance": importance,
        "notes": notes
    }

# ==================== EMBEDDING A SINGLE MODEL IN THE BODY ====================

@app.post("/items/create-with-extra/")
async def create_item_with_extra(
    item: Item = Body(
        ...,
        embed=True,
        examples={
            "normal": {
                "summary": "A normal example",
                "value": {
                    "name": "Headphones",
                    "description": "Noise-cancelling bluetooth headphones",
                    "price": 149.99,
                    "tax": 15.00,
                    "tags": ["audio", "electronics"]
                }
            },
            "discounted": {
                "summary": "A discounted item example",
                "value": {
                    "name": "Sale Item",
                    "price": 9.99,
                    "tags": ["sale"]
                }
            }
        }
    )
):
    """
    Create an item with the embed parameter.
    
    When embed=True, FastAPI will expect a JSON with the model wrapped in a key
    with the same name as the parameter (in this case, 'item').
    
    This also demonstrates how to provide multiple examples for documentation.
    """
    return {"message": "Item created with embedded body", "item": item}

# Run the application if executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
