from datetime import datetime
from pydantic import BaseModel, field_validator, EmailStr
from typing import List, Optional


class User(BaseModel):
    username: str
    email: EmailStr
    bio: Optional[str] = None

    # Example validator: ensure username length
    @field_validator('username')
    def username_length(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return v


class Comment(BaseModel):
    author: User
    content: str
    created_at: datetime = datetime.utcnow()


class Post(BaseModel):
    title: str
    content: str
    author: User
    published_at: datetime = datetime.utcnow()
    tags: List[str] = []
    comments: List[Comment] = []

    @field_validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v

    # For demonstration, we might also add a custom validator 
    # to ensure content length is reasonable.
    @field_validator('content')
    def content_length(cls, v):
        if len(v) < 10:
            raise ValueError("Post content must be at least 10 characters long")
        return v


# Example usage:
if __name__ == "__main__":
    # Create a user
    author = User(username="janedoe", email="jane@example.com", bio="Tech enthusiast and blogger.")

    # Create a post
    post = Post(
        title="My First Blog Post",
        content="Hello, world! Welcome to my new blog.",
        author=author,
        tags=["introduction", "personal"]
    )

    # Add a comment
    commenter = User(username="john123", email="john@domain.com")
    comment = Comment(author=commenter, content="Great post, looking forward to more!")
    post.comments.append(comment)

    # Print the serialized post
    print(post.dict())  # Convert to dictionary
    print(post.model_dump_json(indent=2))  # Pretty-print JSON