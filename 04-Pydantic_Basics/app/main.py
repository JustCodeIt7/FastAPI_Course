# main.py
from datetime import datetime
from uuid import uuid4
from typing import List

from fastapi import FastAPI, HTTPException, Depends
from models import UserCreate, User, PostCreate, Post, CommentCreate, Comment

app = FastAPI()

# In-memory "database" for demonstration
fake_users_db = {}
fake_posts_db = {}
fake_comments_db = {}


########################################
# Utility Functions (Mimicking a DB)
########################################
def get_user_by_id(user_id):
    return fake_users_db.get(str(user_id))


def get_post_by_id(post_id):
    return fake_posts_db.get(str(post_id))


def get_comment_by_id(comment_id):
    return fake_comments_db.get(str(comment_id))


########################################
# Users
########################################
@app.post("/users", response_model=User)
def create_user(user_data: UserCreate):
    # In a real scenario:
    # 1. Hash the password
    # 2. Save the user to the database

    new_id = uuid4()
    now = datetime.utcnow()
    user_dict = {
        "id": new_id,
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "bio": user_data.bio,
        "created_at": now,
        "updated_at": None,
        "is_active": True,
        "posts": [],
        "comments": [],
    }
    fake_users_db[str(new_id)] = user_dict
    return user_dict


# get users
@app.get("/users", response_model=List[User])
def list_users():
    return list(fake_users_db.values())


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


########################################
# Posts
########################################
@app.post("/posts", response_model=Post)
def create_post(post_data: PostCreate, author_id: str):
    # Check if author exists
    author = get_user_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    new_id = uuid4()
    now = datetime.utcnow()
    post_dict = {
        "id": new_id,
        "title": post_data.title,
        "content": post_data.content,
        "created_at": now,
        "updated_at": None,
        "published": post_data.published,
        "author_id": author["id"],
        "author": author,
        "comments": [],
    }

    # Add post to database
    fake_posts_db[str(new_id)] = post_dict

    # Add the post reference to the user
    author["posts"].append(post_dict)
    return post_dict


@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: str):
    post = get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.get("/posts", response_model=List[Post])
def list_posts():
    return list(fake_posts_db.values())


########################################
# Comments
########################################
@app.post("/posts/{post_id}/comments", response_model=Comment)
def create_comment(post_id: str, comment_data: CommentCreate, author_id: str):
    # Check if post exists
    post = get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if author exists
    author = get_user_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    new_id = uuid4()
    now = datetime.utcnow()
    comment_dict = {
        "id": new_id,
        "content": comment_data.content,
        "created_at": now,
        "updated_at": None,
        "author_id": author["id"],
        "post_id": post["id"],
        "author": author,
    }

    # Add comment to database and to the post
    fake_comments_db[str(new_id)] = comment_dict
    post["comments"].append(comment_dict)
    # Add comment to user's comments
    author["comments"].append(comment_dict)

    return comment_dict


@app.get("/comments/{comment_id}", response_model=Comment)
def get_comment(comment_id: str):
    comment = get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


# ==================== MAIN ====================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
