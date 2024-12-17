# schemas.py
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, SecretStr
from datetime import datetime


# Base Models (Responses)
class UserBase(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    full_name: str
    bio: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    author_id: UUID
    post_id: UUID

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    published: bool
    author_id: UUID

    class Config:
        orm_mode = True


# Request Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    password: SecretStr


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    published: bool = False


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


# Response Models with Relationships
class Comment(CommentBase):
    author: UserBase

    class Config:
        orm_mode = True


class Post(PostBase):
    author: UserBase
    comments: List[Comment] = []

    class Config:
        orm_mode = True


class User(UserBase):
    posts: List[Post] = []
    comments: List[Comment] = []

    class Config:
        orm_mode = True
