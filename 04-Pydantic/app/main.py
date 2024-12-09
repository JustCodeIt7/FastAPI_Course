# app/main.py

from fastapi import FastAPI
import uvicorn
from app.routers import users, orders  # Changed to absolute import
from app.exceptions import (
    handle_validation_exception,
    handle_http_exception,
)  # Changed to absolute import
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(
    title="FastAPI Tutorial",
    description="A complete example of FastAPI with Pydantic",
    version="1.0.0",
)

# Include routers
app.include_router(users.router)
app.include_router(orders.router)

# Register exception handlers
app.add_exception_handler(RequestValidationError, handle_validation_exception)
app.add_exception_handler(StarletteHTTPException, handle_http_exception)


@app.get("/")
async def get_root():
    return {"message": "Hello FastAPI!"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
