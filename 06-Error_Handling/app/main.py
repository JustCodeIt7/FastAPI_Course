# main.py
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, constr, validator
from typing import Optional, List, Dict, Union
from enum import Enum
from datetime import datetime

app = FastAPI(title="Library API - Response Handling Demo")


# Enums for Status
class BookStatus(str, Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    MAINTENANCE = "maintenance"
    LOST = "lost"


# Custom Exception Classes
class BookNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found in the library",
        )


class BookNotAvailableException(HTTPException):
    def __init__(self, status: BookStatus):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book is currently {status}",
        )


# Pydantic Models
class BookBase(BaseModel):
    title: constr(min_length=1, max_length=100)
    author: constr(min_length=1, max_length=100)
    isbn: constr()


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int
    status: BookStatus
    last_updated: datetime

    class Config:
        orm_mode = True


class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: datetime


class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict] = None
    timestamp: datetime


# Simulated database
books_db: Dict[int, dict] = {}
book_id_counter = 1


# Helper Functions
def create_error_response(error: str, detail: str) -> ErrorResponse:
    return ErrorResponse(error=error, detail=detail, timestamp=datetime.now())


def create_success_response(
    message: str, data: Optional[Dict] = None
) -> SuccessResponse:
    return SuccessResponse(message=message, data=data, timestamp=datetime.now())


# API Endpoints
@app.post(
    "/books/",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Book successfully created"},
        400: {"model": ErrorResponse, "description": "Invalid book data"},
    },
)
async def create_book(book: BookCreate):
    global book_id_counter

    # Check if ISBN already exists
    if any(b["isbn"] == book.isbn for b in books_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book with this ISBN already exists",
        )

    book_dict = book.dict()
    book_dict.update(
        {
            "id": book_id_counter,
            "status": BookStatus.AVAILABLE,
            "last_updated": datetime.now(),
        }
    )

    books_db[book_id_counter] = book_dict
    book_id_counter += 1

    return create_success_response(message="Book successfully created", data=book_dict)


@app.get(
    "/books/{book_id}",
    response_model=Union[Book, ErrorResponse],
    responses={
        200: {"model": Book, "description": "Book details retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Book not found"},
    },
)
async def get_book(book_id: int):
    if book_id not in books_db:
        raise BookNotFoundException()
    return books_db[book_id]


@app.patch(
    "/books/{book_id}/status",
    response_model=SuccessResponse,
    responses={
        200: {"description": "Book status updated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid status update"},
        404: {"model": ErrorResponse, "description": "Book not found"},
    },
)
async def update_book_status(book_id: int, status: BookStatus):
    if book_id not in books_db:
        raise BookNotFoundException()

    books_db[book_id]["status"] = status
    books_db[book_id]["last_updated"] = datetime.now()

    return create_success_response(
        message=f"Book status updated to {status}", data=books_db[book_id]
    )


@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Book successfully deleted"},
        404: {"model": ErrorResponse, "description": "Book not found"},
    },
)
async def delete_book(book_id: int):
    if book_id not in books_db:
        raise BookNotFoundException()

    del books_db[book_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/books/",
    response_model=List[Book],
    responses={
        200: {"description": "List of all books"},
        204: {"description": "No books found"},
    },
)
async def list_books():
    books = list(books_db.values())
    if not books:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return books


# Custom exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            error=exc.__class__.__name__, detail=str(exc.detail)
        ).dict(),
    )


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
