from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, status
from sqlmodel import Session, select
from typing import List
from uuid import UUID
from database import create_db_and_tables, get_session
from models import User, Post, Comment, UserCreate, PostCreate, CommentCreate

app = FastAPI(title="Blog API")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


# User Endpoints
@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    new_user = User(**user.dict())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@app.get("/users/", response_model=List[User])
def get_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: UUID, user_update: UserCreate, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update user fields
    user.username = user_update.username
    user.email = user_update.email
    user.full_name = user_update.full_name
    user.bio = user_update.bio
    user.updated_at = datetime.utcnow()

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Post Endpoints
@app.post("/users/{user_id}/posts/", response_model=Post)
def create_post(user_id: UUID, post: PostCreate, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_post = Post(**post.dict(), author_id=user_id)
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return new_post


@app.get("/posts/", response_model=List[Post])
def get_posts(session: Session = Depends(get_session)):
    posts = session.exec(select(Post)).all()
    return posts


@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: UUID, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


# Comment Endpoints
@app.post("/posts/{post_id}/comments/", response_model=Comment)
def create_comment(post_id: UUID, comment: CommentCreate, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    new_comment = Comment(**comment.dict(), post_id=post_id)
    session.add(new_comment)
    session.commit()
    session.refresh(new_comment)
    return new_comment


@app.get("/posts/{post_id}/comments/", response_model=List[Comment])
def get_post_comments(post_id: UUID, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post.comments


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: UUID, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    session.delete(post)
    session.commit()
    return {"message": "Post deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application with reload enabled
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
