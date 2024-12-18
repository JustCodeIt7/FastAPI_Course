from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship


# User model
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str
    email: str
    full_name: str
    bio: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = True

    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")


# Post model
class Post(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    published: bool = False
    author_id: UUID = Field(foreign_key="user.id")

    author: User = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")


# Comment model
class Comment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    author_id: UUID = Field(foreign_key="user.id")
    post_id: UUID = Field(foreign_key="post.id")

    author: User = Relationship(back_populates="comments")
    post: Post = Relationship(back_populates="comments")
