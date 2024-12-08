# Query Parameters Tutorial
from typing import Optional, List
from fastapi import FastAPI, Query
from enum import Enum
from pydantic import BaseModel
from starlette.responses import HTMLResponse

app = FastAPI(title="Query Parameters Tutorial")
# /path-param/?limit=10

# Sample Database
sample_data = [
    {"id": 1, "name": "Laptop", "category": "electronics", "price": 999.99},
    {"id": 2, "name": "Headphones", "category": "electronics", "price": 99.99},
    {"id": 3, "name": "Coffee Mug", "category": "kitchen", "price": 9.99},
    {"id": 4, "name": "Book", "category": "books", "price": 19.99},
    {"id": 5, "name": "Smartphone", "category": "electronics", "price": 699.99},
    {"id": 6, "name": "Tablet", "category": "electronics", "price": 299.99},
    {"id": 7, "name": "Microwave", "category": "appliances", "price": 150.0},
    {"id": 8, "name": "Sofa", "category": "furniture", "price": 499.99},
    {"id": 9, "name": "Chair", "category": "furniture", "price": 199.99},
    {"id": 10, "name": "Desk", "category": "furniture", "price": 299.99},
]


# Enum for sorting options to restrict sort_by parameter to specific fields.
class SortBy(str, Enum):
    name = "name"
    price = "price"
    category = "category"


# Pydantic Models: Defines the structure of the Item response model.
class Item(BaseModel):
    id: int
    name: str
    category: str
    price: float


# Root Endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <html>
        <head>
            <title>FastAPI Query Parameters Tutorial</title>
        </head>
        <body>
            <h1>Welcome to the FastAPI Query Parameters Tutorial</h1>
            <p>This is a demonstration of how to use query parameters in FastAPI.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


# ===============================
# Pagination Endpoint
# ===============================
# Endpoint to retrieve items with pagination using skip and limit query parameters.
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    """
    Get items with pagination using query parameters.

    Parameters:
    - skip: Number of items to skip (default: 0)
    - limit: Maximum number of items to return (default: 10)

    Example:
    GET http://localhost:8000/items/?skip=0&limit=5
    """
    return sample_data[skip : skip + limit]


# ===============================
# Search Endpoint
# ===============================
# Endpoint to search for items based on an optional query parameter.
@app.get("/items/search/")
async def search_items(q: Optional[str] = None):
    """
    Search items with an optional query parameter.

    Parameters:
    - q: Search term to filter items by name (optional)

    Example:
    GET http://localhost:8000/items/search/?q=laptop
    """
    if q:
        return [item for item in sample_data if q.lower() in item["name"].lower()]

    return sample_data


# ===============================
# Filter Endpoint
# ===============================
# Endpoint to filter items based on price range and category.
@app.get("/items/filter/")
async def filter_items(
    min_price: float = 0.0,
    max_price: float = float("inf"),
    category: Optional[str] = None,
):
    """
    Filter items by price range and category.

    Parameters:
    - min_price: Minimum price to filter items (default: 0.0)
    - max_price: Maximum price to filter items (default: Infinity)
    - category: Category to filter items (optional)

    Example:
    GET http://localhost:8000/items/filter/?min_price=10&max_price=100&category=electronics
    """
    # Filter items within the specified price range
    filtered_items = [
        item for item in sample_data if min_price <= item["price"] <= max_price
    ]
    # If category is specified, further filter the items by category
    if category:
        filtered_items = [
            item
            for item in filtered_items
            if item["category"].lower() == category.lower()
        ]
    return filtered_items


# ===============================
# Sort Endpoint
# ===============================
# Endpoint to sort items based on a specified field and order.
@app.get("/items/sort/")
async def sort_items(sort_by: SortBy, descending: bool = False):
    """
    Sort items by a specific field.

    Parameters:
    - sort_by: Field to sort by (options: name, price, category)
    - descending: Sort in descending order if true (default: False)

    Example:
    GET http://localhost:8000/items/sort/?sort_by=price&descending=true
    """
    sorted_items = sorted(sample_data, key=lambda x: x[sort_by], reverse=descending)
    return sorted_items


# ===============================
# Validation Endpoint
# ===============================
# Endpoint to retrieve items with validated query parameters for pagination and search.
@app.get("/items/validate/")
async def validate_items(
    page: int = Query(1, gt=0, description="Page number, must be greater than 0"),
    size: int = Query(
        10, ge=1, le=100, description="Number of items per page, between 1 and 100"
    ),
    search: str = Query(
        None,
        min_length=3,
        max_length=50,
        description="Search term with minimum 3 and maximum 50 characters",
    ),
):
    """
    Get items with validated query parameters.

    Parameters:
    - page: Page number (must be > 0)
    - size: Number of items per page (1-100)
    - search: Search term to filter items by name (optional, 3-50 characters)

    Example:
    GET http://localhost:8000/items/validate/?page=1&size=10&search=laptop
    """
    # Calculate the start and end indices for pagination
    start = (page - 1) * size
    end = start + size

    # Initialize filtered_items with all items
    filtered_items = sample_data

    # If a search term is provided, filter items by name
    if search:
        filtered_items = [
            item for item in filtered_items if search.lower() in item["name"].lower()
        ]
    return {
        "page": page,
        "size": size,
        "total": len(filtered_items),
        "items": filtered_items[start:end],
    }


# Application Entry Point
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=True,
    )
