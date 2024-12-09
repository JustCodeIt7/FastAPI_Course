# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Model
class BlogPost(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


# Pydantic Models
class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# FastAPI App
app = FastAPI(
    title="Simple Blog API",
    description="A simple blog API built with FastAPI and SQLAlchemy",
    version="1.0.0",
)


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Tags Metadata
tags_metadata = [
    {
        "name": "posts",
        "description": "Operations with blog posts. Create, read, and delete posts.",
    }
]


# API Endpoints
@app.post(
    "/posts/",
    response_model=Post,
    tags=["posts"],
    summary="Create a new blog post",
    description="Create a new blog post with the provided title and content.",
)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """
    Create a new blog post with the following parameters:

    - **title**: required string
    - **content**: required string
    """
    db_post = BlogPost(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get(
    "/posts/",
    response_model=List[Post],
    tags=["posts"],
    summary="Get all blog posts",
    description="Retrieve a list of all blog posts with pagination support.",
)
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get all blog posts with pagination:

    - **skip**: number of posts to skip (default: 0)
    - **limit**: maximum number of posts to return (default: 10)
    """
    posts = db.query(BlogPost).offset(skip).limit(limit).all()
    return posts


@app.get(
    "/posts/{post_id}",
    response_model=Post,
    tags=["posts"],
    summary="Get a specific blog post",
    description="Retrieve a specific blog post by its ID.",
)
def read_post(post_id: int, db: Session = Depends(get_db)):
    """
    Get a specific blog post by ID:

    - **post_id**: required integer ID of the post
    """
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.delete(
    "/posts/{post_id}",
    tags=["posts"],
    summary="Delete a blog post",
    description="Delete a specific blog post by its ID.",
)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific blog post by ID:

    - **post_id**: required integer ID of the post to delete
    """
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}


#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run("p06_app.main:p06_app", host="0.0.0.0", port=8000, reload=True)
