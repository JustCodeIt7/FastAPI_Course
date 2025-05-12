from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional

# -----------------------------------------
# Application Setup
# -----------------------------------------
# Create a FastAPI instance with metadata for interactive docs
app = FastAPI(
    title="FastAPI Request Body Tutorial",
    description="Demonstration of sending and receiving data via request bodies in FastAPI",
    version="1.0.0"
)


# -----------------------------------------
# 1. Define Pydantic Model for Request Body
# -----------------------------------------
class Item(BaseModel):
    name: str  # Required: the name of the item
    description: Optional[str] = None  # Optional: description, defaults to None
    price: float  # Required: base price
    tax: Optional[float] = None  # Optional: tax amount


# -----------------------------------------
# 2. Basic POST Endpoint: Echo the Item
# -----------------------------------------
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    """
    - Reads JSON request body and validates against Item model.
    - Returns the same item data.
    """
    return item


# -----------------------------------------
# 3. POST with Computation: Price with Tax
# -----------------------------------------
@app.post("/items/with-tax", response_model=dict)
async def create_item_with_tax(item: Item):
    """
    - Calculates price including tax if provided.
    - Demonstrates .dict() method and dynamic response content.
    """
    item_data = item.dict()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_data.update({"price_with_tax": price_with_tax})
    return item_data


# -----------------------------------------
# 4. PUT Endpoint: Path Parameter + Request Body
# -----------------------------------------
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    """
    - `item_id` is taken from the URL path.
    - `item` is taken from the request body.
    """
    return {"item_id": item_id, **item.dict()}


# -----------------------------------------
# 5. PUT Endpoint: Path, Query, and Body
# -----------------------------------------
@app.put("/items/{item_id}/with-query")
async def update_item_with_query(
        item_id: int,
        item: Item,
        q: Optional[str] = None  # Query parameter: optional
):
    """
    - Demonstrates mixing path, query, and body parameters.
    - FastAPI infers sources automatically.
    """
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result


# -----------------------------------------
# 6. POST Without Pydantic: Using Body()
# -----------------------------------------
@app.post("/items/body-only")
async def create_item_body_only(
        name: str = Body(..., description="Name of the item"),
        description: Optional[str] = Body(None, description="Optional description"),
        price: float = Body(..., description="Base price"),
        tax: Optional[float] = Body(None, description="Optional tax amount")
):
    """
    - Shows how to declare individual body fields without a model.
    - Useful for simple or singular values.
    """
    item = {
        "name": name,
        "description": description,
        "price": price,
        "tax": tax
    }
    if tax is not None:
        item.update({"price_with_tax": price + tax})
    return item


# -----------------------------------------
# To Run:
# uvicorn fastapi_request_body_tutorial:app --reload
# Open http://127.0.0.1:8000/docs for Swagger UI
# -----------------------------------------
if __name__ == "__main__":
    import uvicorn

    # This part is for easily running the app with `python main.py`
    # For production, it's better to use `uvicorn main:app --host 0.0.0.0 --port 8000`
    uvicorn.run(app, host="127.0.0.1", port=8000)
