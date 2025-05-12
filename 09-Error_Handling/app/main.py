# main.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

from requests import Response

p05_app = FastAPI(title="Blog API with Error Handling")


# Custom Exceptions
class PostNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


class PostTitleExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A post with this title already exists",
        )


class InvalidStatusTransitionException(HTTPException):
    def __init__(self, current_status: str, new_status: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {current_status} to {new_status}",
        )


# Enums
class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# Pydantic Models
class PostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    content: str = Field(..., min_length=50)
    author: str = Field(..., min_length=2, max_length=50)
    status: PostStatus = PostStatus.DRAFT


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    views: int = 0

    class Config:
        from_attributes = True


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    content: Optional[str] = Field(None, min_length=50)
    status: Optional[PostStatus] = None


# Simulated database
posts_db: Dict[int, Dict] = {}
counter = 1


# Helper functions
def get_post_or_404(post_id: int) -> dict:
    if post_id not in posts_db:
        raise PostNotFoundException()
    return posts_db[post_id]


def check_title_exists(title: str, exclude_id: Optional[int] = None) -> bool:
    return any(
        post["title"].lower() == title.lower()
        for post_id, post in posts_db.items()
        if post_id != exclude_id
    )


# API Endpoints
@p05_app.post(
    "/posts/",
    response_model=Post,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Post with this title already exists"},
    },
)
async def create_post(post: PostCreate):
    """Create a new blog post"""
    global counter

    if check_title_exists(post.title):
        raise PostTitleExistsException()

    current_time = datetime.now()
    post_dict = post.dict()
    post_dict.update(
        {
            "id": counter,
            "created_at": current_time,
            "updated_at": current_time,
            "views": 0,
        }
    )

    posts_db[counter] = post_dict
    counter += 1
    return post_dict


@p05_app.get(
    "/posts/",
    response_model=List[Post],
    responses={204: {"description": "No posts found"}},
)
async def list_posts(
        skip: int = 0, limit: int = 10, status: Optional[PostStatus] = None
):
    """List all posts with optional filtering and pagination"""
    posts = list(posts_db.values())

    if status:
        posts = [post for post in posts if post["status"] == status]

    if not posts:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return posts[skip: skip + limit]


@p05_app.get(
    "/posts/{post_id}",
    response_model=Post,
    responses={404: {"description": "Post not found"}},
)
async def get_post(post_id: int):
    """Get a specific post by ID"""
    post = get_post_or_404(post_id)
    post["views"] += 1
    return post


@p05_app.patch(
    "/posts/{post_id}",
    response_model=Post,
    responses={
        404: {"description": "Post not found"},
        400: {"description": "Invalid status transition or title already exists"},
    },
)
async def update_post(post_id: int, post_update: PostUpdate):
    """Update a post"""
    post = get_post_or_404(post_id)

    if post_update.title and check_title_exists(post_update.title, post_id):
        raise PostTitleExistsException()

    if post_update.status:
        current_status = PostStatus(post["status"])
        if (
                current_status == PostStatus.ARCHIVED
                and post_update.status != PostStatus.ARCHIVED
        ):
            raise InvalidStatusTransitionException(current_status, post_update.status)

    update_data = post_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()

    post.update(update_data)
    return post


@p05_app.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Post not found"}},
)
async def delete_post(post_id: int):
    """Delete a post"""
    get_post_or_404(post_id)  # Check if post exists
    del posts_db[post_id]
    return None


# Root endpoint
@p05_app.get("/")
async def read_root():
    return {
        "message": "Welcome to the Blog API",
        "version": "1.0",
        "documentation": "/docs",
    }


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(
        "main:p05_app", host="0.0.0.0", port=8000, log_level="debug", reload=True
    )
