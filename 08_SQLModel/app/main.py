# main.py
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlmodel import Session
from typing import List
from uuid import UUID  # Added missing UUID import
import uvicorn
from datetime import datetime

from database import get_session, init_db
from models import UserModel, PostModel, CommentModel
from schemas import (
    UserCreate,
    UserBase,
    PostCreate,
    PostBase,
    CommentCreate,
    CommentBase,
    User,
    Post,
    Comment,
)


# Define lifespan context manager (replacing @app.on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown
    pass


# Create FastAPI app with lifespan
app = FastAPI(title="Blog API", lifespan=lifespan)


# User endpoints
@app.post("/users/", response_model=UserBase)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = UserModel(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        bio=user.bio,
        hashed_password=user.password.get_secret_value(),  # In production, use proper password hashing
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    users = session.query(UserModel).offset(skip).limit(limit).all()
    return users


# Post endpoints
@app.post("/posts/", response_model=Post)
def create_post(post: PostCreate, user_id: UUID, session: Session = Depends(get_session)):
    db_post = PostModel(**post.model_dump(), author_id=user_id)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@app.get("/posts/", response_model=List[Post])
def read_posts(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    posts = session.query(PostModel).offset(skip).limit(limit).all()
    return posts


# Comment endpoints
@app.post("/posts/{post_id}/comments/", response_model=Comment)
def create_comment(
    post_id: UUID, comment: CommentCreate, user_id: UUID, session: Session = Depends(get_session)
):
    db_comment = CommentModel(**comment.model_dump(), author_id=user_id, post_id=post_id)
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
