# models.py
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from uuid import UUID, uuid4


# ------------------------------
# UserModel: Database Model for Users
# ------------------------------
class UserModel(SQLModel, table=True):
    """
    Represents a user in the system.
    Includes user profile information and relationships with posts and comments.
    """

    __tablename__ = "users"

    # Core Fields
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(index=True, min_length=3, max_length=50)
    email: EmailStr = Field(index=True)
    full_name: str = Field(min_length=1, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)

    # Relationships
    posts: List["PostModel"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    comments: List["CommentModel"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# ------------------------------
# PostModel: Database Model for Posts
# ------------------------------
class PostModel(SQLModel, table=True):
    """
    Represents a blog post authored by a user.
    Contains relationships with the author and comments on the post.
    """

    __tablename__ = "posts"

    # Core Fields
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    published: bool = Field(default=False)

    # Foreign Keys and Relationships
    author_id: UUID = Field(foreign_key="users.id")  # Links the post to a user
    author: UserModel = Relationship(back_populates="posts")
    comments: List["CommentModel"] = Relationship(
        back_populates="post", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# ------------------------------
# CommentModel: Database Model for Comments
# ------------------------------
class CommentModel(SQLModel, table=True):
    """
    Represents a comment within the system.
    Each comment is linked to a user (author) and a post.
    """

    __tablename__ = "comments"

    # Core Fields
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str = Field(min_length=1, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # Foreign Keys and Relationships
    author_id: UUID = Field(foreign_key="users.id")  # Links the comment to a user
    post_id: UUID = Field(foreign_key="posts.id")  # Links the comment to a post
    author: UserModel = Relationship(back_populates="comments")
    post: PostModel = Relationship(back_populates="comments")
