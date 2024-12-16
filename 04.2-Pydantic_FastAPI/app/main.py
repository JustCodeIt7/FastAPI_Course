# main.py
from fastapi import FastAPI, HTTPException, Depends, status
from typing import List
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi.responses import HTMLResponse
from models import UserCreate, UserBase, User, PostCreate, Post, CommentCreate, Comment

app = FastAPI(title="Blog API")

# In-memory database (for demonstration)
db = {"users": {}, "posts": {}, "comments": {}}


# root endpoint
@app.get("/")
async def root():
    html_content = """
    <html>
        <head>
            <title>Blog API</title>
        </head>
        <body>
            <h1>Welcome to the Blog API</h1>
            <p>Check the <a href="/docs">API documentation</a> for more information.</p>
            
            <h2>Endpoints</h2>
            
            <h3>Users</h3>
            <ul>
                <li><a href="/users/">Get all users</a></li>
                <li><a href="/users/{user_id}">Get user by ID</a></li>
                <li><a href="/users/">Create a new user</a></li>
            </ul>
            
            
            <h3>Posts</h3>
            <ul>
                <li><a href="/posts/">Get all posts</a></li>
                <li><a href="/posts/{post_id}">Get post by ID</a></li>
                <li><a href="/users/{user_id}/posts/">Create a new post</a></li>
            </ul>
            
            <h3>Comments</h3>
            <ul>
                <li><a href="/posts/{post_id}/comments/">Get all comments for a post</a></li>
                <li><a href="/posts/{post_id}/comments/">Create a new comment</a></li>
            </ul>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


# Dependency to get current user (simplified auth)


################ Users Endpoints ################


################ Posts Endpoints ################


################ Comments Endpoints ################


# Application Entry Point
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=True,
    )
