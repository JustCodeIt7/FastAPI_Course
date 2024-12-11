from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Define a Pydantic model for the item
class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

@app.post("/items/")
async def create_item(item: Item):
    """
    Create an item with a request body.
    
    Args:
        item (Item): The item data to be created.

    Returns:
        dict: The created item data.
    """
    return {"message": "Item created", **item.dict()}

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    """
    Update an item with a request body and path parameter.
    
    Args:
        item_id (int): The ID of the item to be updated.
        item (Item): The new data for the item.

    Returns:
        dict: The updated item data along with its ID.
    """
    return {"message": "Item updated", "item_id": item_id, **item.dict()}

@app.put("/items/{item_id}")
async def update_item_with_query(item_id: int, item: Item, q: Union[str, None] = None):
    """
    Update an item with a request body, path parameter, and query parameter.
    
    Args:
        item_id (int): The ID of the item to be updated.
        item (Item): The new data for the item.
        q (Union[str, None]): An optional query parameter.

    Returns:
        dict: The updated item data along with its ID and any provided query parameters.
    """
    result = {"message": "Item updated", "item_id": item_id, **item.dict()}
    if q:
        result.update({"query": q})
    return result

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
