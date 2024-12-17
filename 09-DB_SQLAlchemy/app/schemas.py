# schemas.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, SecretStr
from uuid import UUID


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)


class UserCreate(UserBase):
    password: SecretStr


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    password: Optional[SecretStr] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    published: bool = False


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    author_id: str
    author: UserResponse

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    author_id: str
    post_id: str
    author: UserResponse

    class Config:
        from_attributes = True
