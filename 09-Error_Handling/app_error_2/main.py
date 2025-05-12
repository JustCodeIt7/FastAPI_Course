# Import necessary modules from FastAPI and Pydantic
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional

# Initialize the FastAPI application
app = FastAPI()


# Define a custom exception class that inherits from Python's base Exception class.
# This allows us to create specific error types for our application.
class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name  # Store the name associated with the exception


# Register an exception handler for our custom UnicornException.
# This function will be called whenever a UnicornException is raised.
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    # Return a custom JSON response when a UnicornException occurs.
    # The status code 418 "I'm a teapot" is often used for fun, illustrative examples.
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


# Define a Pydantic model for the request body of the /items/ endpoint.
# This model validates the structure and types of incoming data.
class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None  # Optional field with a default value of None


# Define a simple root endpoint.
@app.get("/")
async def read_root():
    # Returns a basic JSON response.
    return {"Hello": "World"}


# Define an endpoint that demonstrates raising an HTTPException.
# HTTPException is FastAPI's standard way to return HTTP error responses.
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    # If the item_id is 42, raise an HTTPException indicating "Item not found".
    if item_id == 42:
        raise HTTPException(status_code=404, detail="Item not found")
    # Otherwise, return the item_id and the optional query parameter q.
    return {"item_id": item_id, "q": q}


# Define an endpoint that demonstrates raising our custom UnicornException.
@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    # If the name is "yolo", raise our custom UnicornException.
    if name == "yolo":
        raise UnicornException(name=name)
    # Otherwise, return the unicorn's name.
    return {"unicorn_name": name}


# Define an endpoint for creating items, which uses the Item Pydantic model for request body validation.
# This endpoint can trigger a RequestValidationError if the request body is invalid.
@app.post("/items/")
async def create_item(item: Item):
    # If the request body is valid according to the Item model, return the item.
    return item


# Override the default RequestValidationError handler.
# This allows us to customize the response format for validation errors.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Return a JSON response with status code 422 (Unprocessable Entity).
    # The response includes detailed information about the validation errors and the original request body.
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )


# Define an endpoint that demonstrates raising HTTPException in a more complex scenario,
# such as when updating an item.
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    # Simulate a scenario where the item to be updated is not found.
    if item_id not in [1, 2, 3]:  # Example: item IDs 1, 2, 3 exist
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    # Simulate a validation error for the item's price.
    if item.price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")
    # If all checks pass, return a success message along with item details.
    return {"item_id": item_id, "item_name": item.name, "message": "Item updated successfully"}


# This block allows the script to be run directly using `python main.py`.
# It starts the Uvicorn ASGI server to serve the FastAPI application.
if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI app with Uvicorn, listening on all available network interfaces (0.0.0.0)
    # and on port 8000.
    uvicorn.run(app, host="0.0.0.0", port=8000)
