# schemas.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, SecretStr
from uuid import UUID


class UserBase(BaseModel):
    """
    Base model for a user.

    Attributes:
        id (UUID): The unique identifier of the user.
        username (str): The username of the user.
        email (EmailStr): The email address of the user.
        full_name (str): The full name of the user.
        bio (Optional[str]): A short biography of the user, if provided.
        created_at (datetime): The timestamp when the user was created.
        updated_at (Optional[datetime]): The timestamp when the user was last updated, if applicable.
        is_active (bool): Indicates whether the user account is active.
    """

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    email: EmailStr
    full_name: str
    bio: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool


class PostBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    published: bool
    author_id: UUID


class CommentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    author_id: UUID
    post_id: UUID


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


class Comment(CommentBase):
    author: UserBase


class Post(PostBase):
    author: UserBase
    comments: List[Comment] = []


class User(UserBase):
    posts: List[Post] = []
    comments: List[Comment] = []


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    password: Optional[SecretStr] = None
