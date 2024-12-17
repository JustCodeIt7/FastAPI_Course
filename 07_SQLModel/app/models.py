# models.py
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship


class UserModel(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    bio: Optional[str] = None
    hashed_password: str  # Changed from password to hashed_password
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    # Relationships
    posts: List["PostModel"] = Relationship(back_populates="author")
    comments: List["CommentModel"] = Relationship(back_populates="author")


class PostModel(SQLModel, table=True):
    __tablename__ = "posts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    content: str
    published: bool = Field(default=True)  # Add this line
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    author_id: UUID = Field(foreign_key="users.id")

    # Relationships
    author: UserModel = Relationship(back_populates="posts")
    comments: List["CommentModel"] = Relationship(back_populates="post")


class CommentModel(SQLModel, table=True):
    __tablename__ = "comments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    author_id: UUID = Field(foreign_key="users.id")
    post_id: UUID = Field(foreign_key="posts.id")

    # Relationships
    author: UserModel = Relationship(back_populates="comments")
    post: PostModel = Relationship(back_populates="comments")
