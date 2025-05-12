from typing import Union, List, Dict, Optional, Any
from fastapi import FastAPI, Body, HTTPException, Depends
from pydantic import BaseModel, Field, root_validator, validator, create_model
from enum import Enum
import uvicorn
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Advanced Request Body Features",
    description="Demonstrating advanced request body features in FastAPI",
    version="1.0.0"
)

# ==================== MODEL INHERITANCE ====================

class BaseItem(BaseModel):
    """Base model with common fields"""
    name: str
    description: Optional[str] = None
    price: float
    
class ClothingItem(BaseItem):
    """Clothing item model inheriting from BaseItem"""
    size: str  # S, M, L, XL
    color: str
    material: Optional[str] = None
    
class ElectronicItem(BaseItem):
    """Electronic item model inheriting from BaseItem"""
    brand: str
    model_number: str
    warranty_years: int = 1
    voltage: Optional[float] = None

@app.post("/clothing/", response_model=ClothingItem)
async def create_clothing_item(item: ClothingItem):
    """Create a clothing item using model inheritance"""
    return item

@app.post("/electronics/", response_model=ElectronicItem)
async def create_electronic_item(item: ElectronicItem):
    """Create an electronic item using model inheritance"""
    return item

# ==================== UNION TYPES AND DISCRIMINATED UNIONS ====================

class ItemType(str, Enum):
    CLOTHING = "clothing"
    ELECTRONIC = "electronic"
    BOOK = "book"

class BookItem(BaseItem):
    """Book item model inheriting from BaseItem"""
    author: str
    isbn: str
    pages: int
    
class GenericItem(BaseModel):
    """Model that can represent different types of items using a discriminator field"""
    item_type: ItemType
    item: Dict[str, Any]
    
    @root_validator
    def validate_item_type(cls, values):
        """Validate that the item data matches the specified item_type"""
        item_type = values.get('item_type')
        item_data = values.get('item')
        
        if not item_type or not item_data:
            return values
            
        # Basic validation based on item type
        if item_type == ItemType.CLOTHING and 'size' not in item_data:
            raise ValueError("Clothing items must have a size")
        elif item_type == ItemType.ELECTRONIC and 'brand' not in item_data:
            raise ValueError("Electronic items must have a brand")
        elif item_type == ItemType.BOOK and 'isbn' not in item_data:
            raise ValueError("Book items must have an ISBN")
            
        return values

@app.post("/generic-items/")
async def create_generic_item(item: GenericItem):
    """
    Create an item using a discriminated union approach.
    
    This demonstrates how to handle different types of items using a discriminator field.
    """
    return {"message": f"Created {item.item_type} item", "data": item}

# ==================== NESTED RELATIONSHIPS AND COMPLEX DATA ====================

class Address(BaseModel):
    street: str
    city: str
    state: str
    country: str
    postal_code: str

class Customer(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    addresses: List[Address] = []

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    product_id: int
    name: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    
    @property
    def total_price(self) -> float:
        return self.quantity * self.unit_price

class Order(BaseModel):
    id: Optional[int] = None
    customer: Customer
    items: List[OrderItem] = Field(..., min_items=1)
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('items')
    def validate_items_not_empty(cls, v):
        if not v:
            raise ValueError("Order must have at least one item")
        return v
    
    @property
    def total_amount(self) -> float:
        return sum(item.quantity * item.unit_price for item in self.items)

@app.post("/orders/", response_model=Order)
async def create_order(order: Order):
    """
    Create a complex order with nested relationships.
    
    This demonstrates:
    - Deeply nested models
    - List fields with validation
    - Computed properties
    - Enum fields
    - Datetime handling
    """
    # In a real app, you would save to database here
    order.id = 12345  # Simulating database ID assignment
    return order

# ==================== DYNAMIC REQUEST BODIES ====================

@app.post("/dynamic-config/")
async def update_configuration(config: Dict[str, Any] = Body(...)):
    """
    Accept a dynamic configuration object.
    
    This demonstrates how to handle request bodies with unknown structure
    using Dict[str, Any].
    """
    # In a real app, you would validate and process the config here
    return {"message": "Configuration updated", "applied_settings": len(config), "config": config}

# ==================== DEPENDENCY INJECTION WITH REQUEST BODIES ====================

def validate_item(item: BaseItem = Body(...)):
    """
    A dependency that validates an item and can be reused across endpoints.
    
    This demonstrates how to use Depends with request bodies.
    """
    if item.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be positive")
    return item

@app.post("/validated-items/")
async def create_validated_item(item: BaseItem = Depends(validate_item)):
    """Create an item using a dependency for validation"""
    return {"message": "Validated item created", "item": item}

# Run the application if executed directly
if __name__ == "__main__":
    uvicorn.run("models:app", host="0.0.0.0", port=8001, reload=True)
