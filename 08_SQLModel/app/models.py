# models.py
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4


class UserModel(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(index=True)
    email: str = Field(index=True)
    full_name: str
    bio: Optional[str] = None
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)

    posts: List["PostModel"] = Relationship(back_populates="author")
    comments: List["CommentModel"] = Relationship(back_populates="author")


class PostModel(SQLModel, table=True):
    __tablename__ = "posts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    published: bool = Field(default=False)

    author_id: UUID = Field(foreign_key="users.id")
    author: UserModel = Relationship(back_populates="posts")
    comments: List["CommentModel"] = Relationship(back_populates="post")


class CommentModel(SQLModel, table=True):
    __tablename__ = "comments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    author_id: UUID = Field(foreign_key="users.id")
    post_id: UUID = Field(foreign_key="posts.id")

    author: UserModel = Relationship(back_populates="comments")
    post: PostModel = Relationship(back_populates="comments")
