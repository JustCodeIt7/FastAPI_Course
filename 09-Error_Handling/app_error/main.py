from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator

app = FastAPI()


# 1. Using HTTPException for Standard HTTP Errors
# HTTPException is FastAPI's built-in way to return HTTP error responses.
@app.get("/items-http-exception/{item_id}")
# It's useful for common HTTP errors like 404 Not Found, 403 Forbidden, etc.
async def read_item_http_exception(item_id: int):
    if item_id == 0:
        # Raising HTTPException immediately stops processing and sends the error response.
        raise HTTPException(status_code=404, detail="Item not found via HTTPException")
    return {"item_id": item_id}


# 2. Pydantic Validation Errors
# Pydantic model for request body validation
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None

    # Pydantic validators can raise ValueError for invalid data.
    @validator('name')
    # FastAPI automatically catches these ValueErrors during request body validation
    def name_must_not_be_empty(cls, value):
        # and returns a 422 Unprocessable Entity response with detailed error information.
        if not value.strip():
            raise ValueError("Name must not be empty")
        return value

    @validator('price')
    def price_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("Price must be positive")
        return value


# Route for demonstrating request validation error
@app.post("/items-validation/")
# When a POST request is made to this endpoint with invalid data (e.g., empty name or non-positive price),
async def create_item_validation(item: Item):
    # FastAPI's automatic Pydantic validation will kick in. It will catch the ValueError raised by the validators in the Item model and return a 422 Unprocessable Entity response.
    return item


# 3. Custom Exceptions and Handlers
# Define a custom exception class. This allows us to create specific error types for our application logic, making error handling more granular.
class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


# This decorator registers a custom exception handler for UnicornException.
@app.exception_handler(UnicornException)
# When UnicornException is raised anywhere in the application, this function will be called.
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    # It returns a custom JSONResponse, allowing full control over the error structure and status code.
    return JSONResponse(
        status_code=418,  # I'm a teapot - a fun, non-standard status code
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


# Route that raises our custom UnicornException
@app.get("/unicorns/{name}")
# This route demonstrates how raising our custom UnicornException
async def read_unicorn(name: str):
    # will be caught by the unicorn_exception_handler defined above.
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}


# 4. FastAPI's Default Error Handling for Unhandled Exceptions
# Example of a generic error that will be caught by FastAPI's default handler
@app.get("/divide/{number}")
# If an unhandled Python exception occurs (that isn't HTTPException or a custom handled one), FastAPI's default error handler will catch it.
async def divide_by_zero(number: int):
    if number == 0:
        # This will raise a ZeroDivisionError. FastAPI's default handler will catch this and return a 500 Internal Server Error.
        result = 1 / 0
        # This line won't be reached
        return {"result": result}
    return {"result": 10 / number}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
