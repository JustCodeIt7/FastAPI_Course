# %%
from pydantic import BaseModel, field_validator, EmailStr, Field, SecretStr
from typing import List, Optional, Union
from datetime import datetime, timezone

# %%


# BaseModel is the base class for Pydantic models
class User(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    middle_name: Union[str, None] = None
    password: SecretStr

    # Example validator: ensure username length
    @field_validator("username")
    def username_length(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return v

    @field_validator("email")
    def email_length(cls, v):
        # Ensure email is at least 3 characters long
        if len(v) < 3:
            raise ValueError("Email must be at least 3 characters long")
        return v


# %%
class Comment(BaseModel):
    # Nested model for comments
    author: User
    content: str
    # Default value for created_at is the current time. A unique timestamp is generated for each comment.
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# %%
class Post(BaseModel):
    title: str
    content: str
    author: User
    # Default value for published_at is the current time. A unique timestamp is generated for each post.
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # Optional tags field
    tags: Optional[List[str]] = None
    # List of comments (initialized as empty list) using default_factory. Unique comments are added to the list.
    comments: List[Comment] = Field(default_factory=list)

    @field_validator("title")
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v

    # to ensure content length is reasonable.
    @field_validator("content")
    def content_length(cls, v):
        if len(v) < 10:
            raise ValueError("Post content must be at least 10 characters long")
        return v


# %%

# if __name__ == "__main__":
# Create a user
author = User(
    username="janedoe",
    email="jane@example.com",
    full_name="Jane Doe",
    middle_name="Mary",
    password=SecretStr("password123"),
)

# %%
# Create a post
post = Post(
    title="My First Blog Post",
    content="Hello, world! Welcome to my new blog.",
    author=author,
    tags=["introduction", "personal"],
)

# %%
# Add a comment
commenter = User(
    username="john123",
    email="john@domain.com",
    full_name="John Smith",
    password=SecretStr("password123"),
)
comment = Comment(author=commenter, content="Great post, looking forward to more!")
comment_2 = Comment(author=author, content="Another great post!")
post.comments.append(comment)
post.comments.append(comment_2)

# %%
# Print the serialized post
print(post.model_dump_json(indent=2))

# %%
