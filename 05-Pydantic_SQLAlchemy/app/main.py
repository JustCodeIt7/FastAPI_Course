# main.py

from datetime import datetime
from uuid import uuid4
from typing import List

from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session

from models import UserCreate, User, PostCreate, Post, CommentCreate, Comment
from models_db import UserDB, PostDB, CommentDB
from database import SessionLocal, engine, Base

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


########################################
# Users
########################################
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = (
        db.query(UserDB)
        .filter((UserDB.username == user_data.username) | (UserDB.email == user_data.email))
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    new_user = UserDB(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        bio=user_data.bio,
        created_at=datetime.utcnow(),
        is_active=True,
    )
    # TODO: Hash the password before storing
    # e.g., new_user.hashed_password = hash_password(user_data.password.get_secret_value())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Get all users
@app.get("/users", response_model=List[User])
def list_users(db: Session = Depends(get_db)):
    users = db.query(UserDB).all()
    return users


# Get a specific user by ID
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


########################################
# Posts
########################################
@app.post("/posts", response_model=Post, status_code=status.HTTP_201_CREATED)
def create_post(post_data: PostCreate, author_id: str, db: Session = Depends(get_db)):
    # Check if author exists
    author = db.query(UserDB).filter(UserDB.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    new_post = PostDB(
        title=post_data.title,
        content=post_data.content,
        published=post_data.published,
        created_at=datetime.utcnow(),
        author_id=author_id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# Get all posts
@app.get("/posts", response_model=List[Post])
def list_posts(db: Session = Depends(get_db)):
    posts = db.query(PostDB).all()
    return posts


# Get a specific post by ID
@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


########################################
# Comments
########################################
@app.post("/posts/{post_id}/comments", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: str, comment_data: CommentCreate, author_id: str, db: Session = Depends(get_db)
):
    # Check if post exists
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if author exists
    author = db.query(UserDB).filter(UserDB.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    new_comment = CommentDB(
        content=comment_data.content,
        created_at=datetime.utcnow(),
        author_id=author_id,
        post_id=post_id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


# Get a specific comment by ID
@app.get("/comments/{comment_id}", response_model=Comment)
def get_comment(comment_id: str, db: Session = Depends(get_db)):
    comment = db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


# ==================== MAIN ====================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
