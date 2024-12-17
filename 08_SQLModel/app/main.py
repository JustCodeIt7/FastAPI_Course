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
    UserUpdate,
    PostCreate,
    CommentCreate,
    User,
    Post,
    Comment,
)


# ========================================
# LIFESPAN EVENT (LIFECYCLE MANAGEMENT)
# ========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application lifespan using an asynchronous context manager.

    This function is intended to initialize resources at the start of the
    application's lifecycle and ensure proper cleanup when the application
    shuts down. It performs the necessary setup (e.g., database initialization)
    and yields control to allow the application to run.
    """
    init_db()
    yield


# ========================================
# APPLICATION SETUP
# ========================================
# Initialize FastAPI application with a custom lifecycle
app = FastAPI(title="Blog API", lifespan=lifespan)


# ========================================
# ROOT ENDPOINT
# ========================================
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


# ========================================
# USER ENDPOINTS
# ========================================
@app.post("/users/", response_model=UserBase, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """
    Create and store a new user in the database if username or email is not already
    registered. This function checks for existing users with the same username
    or email. If none exist, the new user is stored in the database with the
    provided details. Proper password hashing should be implemented in a
    production environment.
    """
    # Check if a user with the same username or email exists
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
    # Create and store the new user in the database
    db_user = UserModel(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        bio=user.bio,
        hashed_password=user.password.get_secret_value(),  # Replace with proper hashing in production
    )
    session.add(db_user)
    session.commit()  # Save the user to the database
    session.refresh(db_user)  # Refresh to get updated fields like `id`
    return db_user


@app.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """
    Fetches a paginated list of users from the database.
    """
    users = session.exec(select(UserModel).offset(skip).limit(limit)).all()
    return users


@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: UUID, user_update: UserUpdate, session: Session = Depends(get_session)):
    """
    Updates the details of an existing user.
    """
    db_user = session.get(UserModel, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Update only the provided fields
    user_data = user_update.model_dump(exclude_unset=True)
    if "password" in user_data:
        # Hash the password before updating
        user_data["hashed_password"] = user_data.pop("password").get_secret_value()
    for key, value in user_data.items():
        setattr(db_user, key, value)
    db_user.updated_at = datetime.utcnow()  # Update the modification timestamp
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# ========================================
# POST ENDPOINTS
# ========================================
@app.post("/posts/", response_model=Post, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, user_id: UUID, session: Session = Depends(get_session)):
    """
    Creates a new post for a given user. Ensures the user exists before creating the post.
    """
    user = session.get(UserModel, user_id)  # Verify the user exists
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Create and store the new post in the database
    db_post = PostModel(**post.model_dump(), author_id=user_id)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@app.get("/posts/", response_model=List[Post])
def read_posts(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """
    Fetches a paginated list of posts from the database.
    """
    posts = session.exec(select(PostModel).offset(skip).limit(limit)).all()
    return posts


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: UUID, session: Session = Depends(get_session)):
    """
    Deletes a post by its ID if it exists.
    """
    db_post = session.get(PostModel, post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    session.delete(db_post)
    session.commit()
    return None


# ========================================
# COMMENT ENDPOINTS
# ========================================
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
    """
    Creates a new comment on a post by a user. Ensures both the post and the user exist.
    """
    # Verify the post exists
    post = session.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    # Verify the user exists
    user = session.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Create and store the new comment in the database
    db_comment = CommentModel(**comment.model_dump(), author_id=user_id, post_id=post_id)
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


# ========================================
# MAIN FUNCTION (APPLICATION ENTRY POINT)
# ========================================
if __name__ == "__main__":
    # Run the FastAPI application with reload enabled
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
