# routers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from uuid import UUID
from datetime import datetime
from starlette.responses import HTMLResponse

from database import get_session
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

router = APIRouter()


# ========================================
# ROOT ENDPOINT
# ========================================
@router.get("/", response_class=HTMLResponse)
def read_root():
    """
    Root endpoint that returns a simple HTML welcome page.
    """
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
@router.post("/users/", response_model=UserBase, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """
    Create and store a new user in the database if username or email is not already
    registered.
    """
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
        hashed_password=user.password.get_secret_value(),  # Replace with proper hashing in production
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """
    Fetches a paginated list of users from the database.
    """
    users = session.exec(select(UserModel).offset(skip).limit(limit)).all()
    return users


@router.put("/users/{user_id}", response_model=User)
def update_user(user_id: UUID, user_update: UserUpdate, session: Session = Depends(get_session)):
    """
    Updates the details of an existing user.
    """
    db_user = session.get(UserModel, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_data = user_update.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = user_data.pop("password").get_secret_value()
    for key, value in user_data.items():
        setattr(db_user, key, value)
    db_user.updated_at = datetime.utcnow()
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# ========================================
# POST ENDPOINTS
# ========================================
@router.post("/posts/", response_model=Post, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, user_id: UUID, session: Session = Depends(get_session)):
    """
    Creates a new post for a given user. Ensures the user exists before creating the post.
    """
    user = session.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_post = PostModel(**post.model_dump(), author_id=user_id)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@router.get("/posts/", response_model=List[Post])
def read_posts(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """
    Fetches a paginated list of posts from the database.
    """
    posts = session.exec(select(PostModel).offset(skip).limit(limit)).all()
    return posts


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
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
@router.post(
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
    post = session.get(PostModel, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    user = session.get(UserModel, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_comment = CommentModel(**comment.model_dump(), author_id=user_id, post_id=post_id)
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment
