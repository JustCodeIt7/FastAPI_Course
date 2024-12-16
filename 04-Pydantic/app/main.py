# main.py
from fastapi import FastAPI, HTTPException, Depends, status
from typing import List
from datetime import datetime, timezone
from uuid import UUID, uuid4
from models import UserCreate, UserBase, User, PostCreate, Post, CommentCreate, Comment

app = FastAPI(title="Blog API")

# In-memory database (for demonstration)
db = {"users": {}, "posts": {}, "comments": {}}


# Dependency to get current user (simplified auth)
async def get_current_user(user_id: UUID) -> UserBase:
    user = db["users"].get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# User endpoints
@app.post("/users/", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    user_id = uuid4()
    current_time = datetime.now(timezone.utc)

    new_user = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "bio": user.bio,
        "created_at": current_time,
        "updated_at": None,
        "is_active": True,
        "posts": [],
        "comments": [],
    }

    db["users"][user_id] = new_user
    return new_user


@app.get("/users/", response_model=List[UserBase])
async def get_users():
    return list(db["users"].values())


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: UUID):
    if user_id not in db["users"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db["users"][user_id]


# Post endpoints
@app.post("/users/{user_id}/posts/", response_model=Post)
async def create_post(
    user_id: UUID, post: PostCreate, current_user: UserBase = Depends(get_current_user)
):
    post_id = uuid4()
    current_time = datetime.now(timezone.utc)

    new_post = {
        "id": post_id,
        "title": post.title,
        "content": post.content,
        "created_at": current_time,
        "updated_at": None,
        "published": post.published,
        "author_id": user_id,
        "author": db["users"][user_id],
        "comments": [],
    }

    db["posts"][post_id] = new_post
    db["users"][user_id]["posts"].append(new_post)
    return new_post


@app.get("/posts/", response_model=List[Post])
async def get_posts():
    return list(db["posts"].values())


@app.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: UUID):
    if post_id not in db["posts"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return db["posts"][post_id]


# Comment endpoints
@app.post("/posts/{post_id}/comments/", response_model=Comment)
async def create_comment(
    post_id: UUID, comment: CommentCreate, current_user: UserBase = Depends(get_current_user)
):
    if post_id not in db["posts"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comment_id = uuid4()
    current_time = datetime.now(timezone.utc)

    new_comment = {
        "id": comment_id,
        "content": comment.content,
        "created_at": current_time,
        "updated_at": None,
        "author_id": current_user["id"],
        "post_id": post_id,
        "author": current_user,
    }

    db["comments"][comment_id] = new_comment
    db["posts"][post_id]["comments"].append(new_comment)
    db["users"][current_user["id"]]["comments"].append(new_comment)
    return new_comment


@app.get("/posts/{post_id}/comments/", response_model=List[Comment])
async def get_post_comments(post_id: UUID):
    if post_id not in db["posts"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return db["posts"][post_id]["comments"]


# ==================== MAIN ====================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
