# models.py
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from uuid import UUID, uuid4


class UserModel(SQLModel, table=True):
    __tablename__ = "users"

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
        back_populates="author", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    comments: List["CommentModel"] = Relationship(
        back_populates="author", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class PostModel(SQLModel, table=True):
    __tablename__ = "posts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    published: bool = Field(default=False)

    # Foreign keys and relationships
    author_id: UUID = Field(foreign_key="users.id")
    author: UserModel = Relationship(back_populates="posts")
    comments: List["CommentModel"] = Relationship(
        back_populates="post", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class CommentModel(SQLModel, table=True):
    __tablename__ = "comments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str = Field(min_length=1, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # Foreign keys and relationships
    author_id: UUID = Field(foreign_key="users.id")
    post_id: UUID = Field(foreign_key="posts.id")

    author: UserModel = Relationship(back_populates="comments")
    post: PostModel = Relationship(back_populates="comments")


# Keep your existing Pydantic models for request/response schemas
