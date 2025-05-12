# FastAPI Request Body Tutorial

This project demonstrates how to work with request bodies in FastAPI. It was created for a YouTube tutorial on FastAPI request validation and processing.

## Project Structure

- `main.py`: Basic FastAPI application demonstrating common request body patterns
- `models.py`: Advanced FastAPI application showing complex request body scenarios
- `test_client.py`: Test script for the basic API endpoints
- `test_advanced_client.py`: Test script for the advanced API endpoints

## Features Demonstrated

### Basic Features (main.py)
1. Simple request body validation with Pydantic models
2. Nested models and complex data structures
3. Multiple body parameters in a single endpoint
4. Combining path/query parameters with request bodies
5. Singular values in request bodies
6. Embedded request bodies with examples

### Advanced Features (models.py)
1. Model inheritance
2. Discriminated unions with type selectors
3. Complex nested relationships
4. Dynamic request bodies
5. Dependency injection with request bodies

## Prerequisites

- Python 3.7+
- FastAPI
- Uvicorn
- Httpx (for test clients)

## Installation

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn httpx
```

## Running the Applications

Start the basic API:

```bash
# From the app2 directory
uvicorn main:app --reload
```

Start the advanced API:

```bash
# From the app2 directory
uvicorn models:app --port 8001 --reload
```

## Testing the Endpoints

Both APIs come with test clients that demonstrate how to interact with the endpoints.

```bash
# Test the basic API endpoints
python test_client.py

# Test the advanced API endpoints
python test_advanced_client.py
```

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- Basic API: http://localhost:8000/docs
- Advanced API: http://localhost:8001/docs

## YouTube Tutorial Structure

1. Introduction to Request Bodies in FastAPI
2. Creating Basic Pydantic Models
3. Validating Input with Field Constraints
4. Nested Models and Complex Data Structures
5. Handling Multiple Body Parameters
6. Combining Path/Query Parameters with Request Bodies
7. Advanced: Model Inheritance and Polymorphism
8. Advanced: Complex Validation with Validators
9. Advanced: Working with Dynamic Data
10. Best Practices and Performance Considerations

## License

MIT
