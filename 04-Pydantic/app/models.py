from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID, uuid4


# Input models (Base models) - Used when creating/updating data
# Output models (Response models) - Used when returning data with relationships
# Base models without relationships. Use these models to create & updating data in your API.
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID, uuid4


############## Request Models (for input validation) ##############
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    password: str = Field(..., min_length=6)  # Added for user creation


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    published: bool = False


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


############## Base models (for responses) ##############
class UserBase(BaseModel):
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


############## Response models with relationships ##############
class Comment(CommentBase):
    author: UserBase


class Post(PostBase):
    author: UserBase
    comments: List[Comment] = []


class User(UserBase):
    posts: List[Post] = []
    comments: List[Comment] = []
