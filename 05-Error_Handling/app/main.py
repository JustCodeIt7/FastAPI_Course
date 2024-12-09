# main.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

p05_app = FastAPI(title="Simple Library API")


# Pydantic Models
class Book(BaseModel):
    id: Optional[int] = None
    title: str
    author: str
    published: bool = False
    created_at: Optional[datetime] = None


# Simulated database
books_db = {}
counter = 1


# API Endpoints
@p05_app.post("/books/", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    """Create a new book"""
    global counter
    book.id = counter
    book.created_at = datetime.now()
    books_db[counter] = book
    counter += 1
    return book


@p05_app.get("/books/", response_model=List[Book])
async def get_books(skip: int = 0, limit: int = 10):
    """Get all books with pagination"""
    return list(books_db.values())[skip : skip + limit]


@p05_app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int):
    """Get a specific book by ID"""
    if book_id not in books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return books_db[book_id]


@p05_app.put("/books/{book_id}", response_model=Book)
async def update_book(book_id: int, book: Book):
    """Update a book"""
    if book_id not in books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    book.id = book_id
    book.created_at = books_db[book_id].created_at
    books_db[book_id] = book
    return book


@p05_app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    """Delete a book"""
    if book_id not in books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    del books_db[book_id]
    return None


# root route
@p05_app.get("/")
async def read_root():
    return {"message": "Welcome to the Simple Library API"}


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(
        "main:p05_app", host="0.0.0.0", port=8000, log_level="debug", reload=True
    )
