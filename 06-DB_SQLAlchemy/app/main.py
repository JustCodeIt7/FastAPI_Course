# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum

# Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enums
class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# Database Model
class BlogPost(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(50), nullable=False)
    status = Column(SQLAlchemyEnum(PostStatus), default=PostStatus.DRAFT)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


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


# Pydantic Models
class PostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    content: str = Field(..., min_length=50)
    author: str = Field(..., min_length=2, max_length=50)
    status: PostStatus = PostStatus.DRAFT


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    content: Optional[str] = Field(None, min_length=50)
    status: Optional[PostStatus] = None


class Post(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    views: int

    class Config:
        from_attributes = True


# FastAPI App
p06_app = FastAPI(title="Blog API with SQLAlchemy and Error Handling")


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Helper functions
def get_post_or_404(db: Session, post_id: int) -> BlogPost:
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if post is None:
        raise PostNotFoundException()
    return post


def check_title_exists(
    db: Session, title: str, exclude_id: Optional[int] = None
) -> bool:
    query = db.query(BlogPost).filter(BlogPost.title.ilike(title))
    if exclude_id:
        query = query.filter(BlogPost.id != exclude_id)
    return query.first() is not None


# API Endpoints
@p06_app.post(
    "/posts/",
    response_model=Post,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"description": "Post with this title already exists"}},
)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """Create a new blog post"""
    if check_title_exists(db, post.title):
        raise PostTitleExistsException()

    db_post = BlogPost(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@p06_app.get(
    "/posts/",
    response_model=List[Post],
    responses={204: {"description": "No posts found"}},
)
async def list_posts(
    skip: int = 0,
    limit: int = 10,
    status: Optional[PostStatus] = None,
    db: Session = Depends(get_db),
):
    """List all posts with optional filtering and pagination"""
    query = db.query(BlogPost)

    if status:
        query = query.filter(BlogPost.status == status)

    posts = query.offset(skip).limit(limit).all()

    if not posts:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return posts


@p06_app.get(
    "/posts/{post_id}",
    response_model=Post,
    responses={404: {"description": "Post not found"}},
)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a specific post by ID"""
    post = get_post_or_404(db, post_id)
    post.views += 1
    db.commit()
    return post


@p06_app.patch(
    "/posts/{post_id}",
    response_model=Post,
    responses={
        404: {"description": "Post not found"},
        400: {"description": "Invalid status transition or title already exists"},
    },
)
async def update_post(
    post_id: int, post_update: PostUpdate, db: Session = Depends(get_db)
):
    """Update a post"""
    post = get_post_or_404(db, post_id)

    if post_update.title and check_title_exists(db, post_update.title, post_id):
        raise PostTitleExistsException()

    if post_update.status:
        if (
            post.status == PostStatus.ARCHIVED
            and post_update.status != PostStatus.ARCHIVED
        ):
            raise InvalidStatusTransitionException(post.status, post_update.status)

    update_data = post_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)
    return post


@p06_app.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Post not found"}},
)
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete a post"""
    post = get_post_or_404(db, post_id)
    db.delete(post)
    db.commit()
    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:p06_app", host="0.0.0.0", port=8000, log_level="debug", reload=True
    )
