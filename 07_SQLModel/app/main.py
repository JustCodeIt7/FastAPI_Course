# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from typing import List
from uuid import UUID
import uvicorn
from datetime import datetime

from starlette.responses import HTMLResponse

from database import get_session, init_db
from models import UserModel, PostModel, CommentModel
from schemas import (
    UserCreate,
    UserBase,
    UserUpdate,  # Add this to schemas.py
    PostCreate,
    CommentCreate,
    User,
    Post,
    Comment,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Blog API", lifespan=lifespan)


#  root endpoint
@app.get("/")
def read_root():
    html_content = """
    <html>
        <head>
            <title>Blog API</title>
        </head>
        <body>
            <h1>Welcome to the Blog API</h1>
            <p>Check the <a href="/docs">API documentation</a> for more information.</p>
        </body>
    </html>
    """

    return HTMLResponse(content=html_content, status_code=200)


# User endpoints
@app.post("/users/", response_model=UserBase, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    # Check if username or email already exists
    existing_user = session.exec(
        select(UserModel).where(
            (UserModel.username == user.username) | (UserModel.email == user.email)
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

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
def read_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.exec(select(UserModel).offset(skip).limit(limit)).all()
    return users


@app.put("/users/{user_id}", response_model=User)
def update_user(
    user_id: UUID, user_update: UserUpdate, session: Session = Depends(get_session)
):
    db_user = session.get(UserModel, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_data = user_update.model_dump(exclude_unset=True)

    # Update password if provided
    if "password" in user_data:
        user_data["hashed_password"] = user_data.pop("password").get_secret_value()
        # In production, properly hash the password here

    for key, value in user_data.items():
        setattr(db_user, key, value)

    db_user.updated_at = datetime.utcnow()
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# Post endpoints
@app.post("/posts/", response_model=Post, status_code=status.HTTP_201_CREATED)
def create_post(
    post: PostCreate, user_id: UUID, session: Session = Depends(get_session)
):
    # Verify user exists
    user = session.get(UserModel, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_post = PostModel(**post.model_dump(), author_id=user_id)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@app.get("/posts/", response_model=List[Post])
def read_posts(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    posts = session.exec(select(PostModel).offset(skip).limit(limit)).all()
    return posts


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: UUID, session: Session = Depends(get_session)):
    db_post = session.get(PostModel, post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    session.delete(db_post)
    session.commit()
    return None


# Comment endpoints
@app.post(
    "/posts/{post_id}/comments/",
    response_model=Comment,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: UUID,
    comment: CommentCreate,
    user_id: UUID,
    session: Session = Depends(get_session),
):
    # Verify post exists
    post = session.get(PostModel, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    # Verify user exists
    user = session.get(UserModel, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_comment = CommentModel(
        **comment.model_dump(), author_id=user_id, post_id=post_id
    )
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


@app.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: UUID, session: Session = Depends(get_session)):
    db_comment = session.get(CommentModel, comment_id)
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    session.delete(db_comment)
    session.commit()
    return None


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
