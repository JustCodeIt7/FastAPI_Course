from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.post("/items/")
async def create_item(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    """
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

# Example for demonstrating multiple body parameters
class User(BaseModel):
    username: str
    full_name: Optional[str] = None

@app.post("/items_and_user/")
async def create_item_and_user(item: Item, user: User):
    return {"item": item.dict(), "user": user.dict()}

# Example for demonstrating singular values in body
@app.post("/items_with_importance/")
async def create_item_with_importance(item: Item, importance: int):
    return {"item": item.dict(), "importance": importance}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
