# main.py
from fastapi import FastAPI
from pydantic import BaseModel, Field  # Field can be used for additional validation and metadata
from typing import Union  # For older Python versions (pre 3.10) for optional types

# ------------------------------------------------------------------------------------
# Introduction to Request Bodies with FastAPI
# ------------------------------------------------------------------------------------
# When a client (like a web browser or another application) needs to send data
# to your API, it sends it in the "request body".
# Your API, in turn, almost always sends data back in a "response body".
#
# FastAPI uses Pydantic models to define the structure and data types of
# request bodies. This brings several benefits:
# 1. Data Parsing: FastAPI automatically reads the request body (e.g., JSON)
#    and converts it into Python objects.
# 2. Data Validation: It validates the incoming data against the Pydantic model.
#    If the data is invalid, FastAPI returns a clear error message indicating
#    what went wrong and where.
# 3. Type Hinting & Editor Support: You get excellent editor support (autocompletion,
#    type checking) because the data is represented by typed Pydantic models.
# 4. Automatic Documentation: FastAPI uses these models to generate OpenAPI schemas,
#    which are then used to create interactive API documentation (like Swagger UI
#    or ReDoc).
#
# Common HTTP methods for sending data in a request body are POST, PUT, PATCH,
# and DELETE. While FastAPI supports request bodies with GET requests, it's
# generally discouraged as it's not well-defined in HTTP specifications and
# might not be supported by all tools or proxies.
# ------------------------------------------------------------------------------------

# Initialize the FastAPI application
app = FastAPI(
    title="FastAPI Request Body Tutorial",
    description="An application to demonstrate how to use request bodies in FastAPI.",
    version="1.0.0"
)


# ------------------------------------------------------------------------------------
# 1. Defining a Pydantic Model for the Request Body
# ------------------------------------------------------------------------------------
# First, you import `BaseModel` from `pydantic`.
# Then, you create a class that inherits from `BaseModel`. This class defines
# the schema of your request body.
# Each attribute in the class represents a field in the expected JSON object.

class Item(BaseModel):
    """
    Represents an item with a name, description, price, and optional tax.
    This model will be used to define the structure of the request body for
    creating or updating items.
    """
    name: str  # A required string field
    description: Union[str, None] = None  # An optional string field, default is None
    # For Python 3.10+, you can use: description: str | None = None
    price: float  # A required float field
    tax: Union[float, None] = None  # An optional float field, default is None

    # For Python 3.10+, you can use: tax: float | None = None

    # You can also add example data for the OpenAPI documentation
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Super Widget",
                "description": "A very useful widget.",
                "price": 19.99,
                "tax": 1.99
            }
        }


# Example of a model with more specific validation using Field
class UserProfile(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="The unique username for the user.")
    email: str = Field(..., example="user@example.com", description="The user's email address.")
    full_name: Union[str, None] = Field(None, max_length=100, description="The full name of the user.")
    age: Union[int, None] = Field(None, ge=18, description="The age of the user, must be 18 or older.")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "age": 30
            }
        }


# ------------------------------------------------------------------------------------
# 2. Using the Pydantic Model in a Path Operation (Basic Request Body)
# ------------------------------------------------------------------------------------
# To use this model as a request body, you declare it as a type hint for a
# parameter in your path operation function.
# FastAPI will then expect a JSON body matching the `Item` model structure.

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    """
    Create an item.

    - **item**: The request body should be a JSON object matching the `Item` model.
      - `name` (str): Required.
      - `description` (str, optional): Optional.
      - `price` (float): Required.
      - `tax` (float, optional): Optional.

    FastAPI handles:
    1. Reading the JSON from the request body.
    2. Converting types (e.g., string to float if possible and defined).
    3. Validating the data: If data is missing or has the wrong type,
       FastAPI returns a 422 Unprocessable Entity error.
    4. Providing the validated data as the `item` parameter.
    """
    # The `item` parameter will be an instance of the `Item` model.
    # You can access its attributes directly:
    # print(f"Received item name: {item.name}")
    # print(f"Received item price: {item.price}")

    # For the response, we can simply return the received item.
    # FastAPI will automatically serialize this Pydantic model instance back into a JSON response.
    return item


# ------------------------------------------------------------------------------------
# 3. Using the Model's Data Inside the Function
# ------------------------------------------------------------------------------------
# You can access the attributes of the model instance directly.
# You can also convert the Pydantic model to a dictionary using `item.dict()`.

@app.post("/items/calculate_total/")
async def create_item_with_total(item: Item):
    """
    Create an item and calculate its total price including tax if provided.

    - **item**: The request body should be a JSON object matching the `Item` model.

    This endpoint demonstrates accessing model attributes and performing operations.
    It returns the item's data along with a calculated `price_with_tax`.
    """
    item_data = item.dict()  # Convert the Pydantic model to a Python dictionary

    if item.tax is not None:  # Check if the optional 'tax' field was provided
        price_with_tax = item.price + item.tax
        item_data.update({"price_with_tax": price_with_tax})
    else:
        item_data.update({"price_with_tax": item.price})

    return item_data


# ------------------------------------------------------------------------------------
# 4. Request Body + Path Parameters
# ------------------------------------------------------------------------------------
# You can declare path parameters and a request body at the same time.
# FastAPI will correctly identify which parameters come from the path and
# which come from the request body.

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    """
    Update an item by its ID.

    - **item_id**: The ID of the item to update (taken from the path).
    - **item**: The request body containing the updated item data (JSON object matching `Item` model).

    Returns a dictionary containing the `item_id` and the updated item data.
    In a real application, you would use `item_id` to fetch an existing record
    and then update it with the data from the `item` request body.
    """
    # In a real app, you'd use item_id to find and update the item in a database.
    # For this example, we'll just return the id and the new data.
    return {"item_id": item_id, **item.dict()}  # Using dictionary unpacking


# ------------------------------------------------------------------------------------
# 5. Request Body + Path Parameters + Query Parameters
# ------------------------------------------------------------------------------------
# You can also declare body, path, and query parameters all at the same time.
# FastAPI will recognize each of them and take the data from the correct place.
# - Parameters defined in the path (e.g., `{item_id}`) are path parameters.
# - Parameters that are Pydantic models are request bodies.
# - Parameters with singular types (int, str, float, bool, etc.) are query parameters.

@app.put("/items/{item_id}/details")
async def update_item_details(
        item_id: int,
        item: Item,
        notify_user: Union[bool, None] = None,  # A query parameter (e.g., /items/1/details?notify_user=true)
        # Python 3.10+: notify_user: bool | None = None
        discount_code: Union[str, None] = None  # Another optional query parameter
        # Python 3.10+: discount_code: str | None = None
):
    """
    Update item details, with an option to notify the user via a query parameter.

    - **item_id**: The ID of the item to update (from path).
    - **item**: The request body with item data (JSON object matching `Item` model).
    - **notify_user** (query, optional): A boolean flag to indicate if the user should be notified.
    - **discount_code** (query, optional): A string for a discount code.

    FastAPI distinguishes:
    - `item_id`: path parameter (because it's in the path string).
    - `item`: request body (because its type is a Pydantic model `Item`).
    - `notify_user` & `discount_code`: query parameters (because they are standard Python types
      and not in the path).
    """
    result = {"item_id": item_id, **item.dict()}

    if notify_user is not None:  # Check if the query parameter was provided
        result.update({"notification_sent": notify_user})

    if discount_code:
        result.update({"applied_discount_code": discount_code})
        # You might apply discount logic here
        if "price_with_tax" in result:  # If we already calculated this from a previous example
            result["price_with_tax"] *= 0.9  # Apply a 10% discount
        elif "price" in result:
            result["price"] *= 0.9

    return result


# ------------------------------------------------------------------------------------
# 6. Request Body with more complex Pydantic model and Field validation
# ------------------------------------------------------------------------------------

@app.post("/users/profile/", response_model=UserProfile)
async def create_user_profile(profile: UserProfile):
    """
    Create a new user profile.

    - **profile**: The request body should be a JSON object matching the `UserProfile` model.
      This model includes more specific validation rules using `Field`.

    FastAPI will validate the input against these rules (e.g., `min_length`, `ge`).
    """
    # `profile` is an instance of UserProfile, already validated.
    # You can now save it to a database, etc.
    # For this example, we just return it.
    return profile


if __name__ == "__main__":
    import uvicorn

    # This part is for easily running the app with `python main.py`
    # For production, it's better to use `uvicorn main:app --host 0.0.0.0 --port 8000`
    uvicorn.run(app, host="127.0.0.1", port=8000)
