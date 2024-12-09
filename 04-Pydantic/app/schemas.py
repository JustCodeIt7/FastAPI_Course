# app/schemas.py

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from .utils import format_example


class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

    class Config:
        schema_extra = format_example("123 Main St", "New York", "USA", "10001")


class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    full_name: Optional[str] = None
    age: int = Field(..., ge=0, le=120)
    address: Optional[Address] = None

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "age": 30,
                "address": Address.Config.schema_extra["example"],
            }
        }


class Order(BaseModel):
    id: int
    items: List[str]
    total: float = Field(..., gt=0)
    customer_address: Address
    order_date: datetime = Field(default_factory=datetime.now)

    @validator("items")
    def validate_items(cls, v):
        if not v:
            raise ValueError("Order must contain at least one item")
        return v

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "items": ["item1", "item2"],
                "total": 99.99,
                "customer_address": Address.Config.schema_extra["example"],
            }
        }


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool = True

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "is_active": True,
            }
        }
