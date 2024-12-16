# %%
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, SecretStr
from uuid import UUID, uuid4
from pprint import pp, pprint


# %%
############## Base models (for responses) ##############
class UserBase(BaseModel):
    # Setting from_attributes=True allows the model to populate fields from object attributes, which is useful when dealing with ORM models or other objects where data is accessed via attributes rather than dictionary keys.
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    email: EmailStr
    full_name: str
    bio: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool


user_base = UserBase(
    id=uuid4(),
    username="johndoe",
    email="john@example.com",
    full_name="John Doe",
    bio="Python developer",
    created_at=datetime.now(timezone.utc),
    updated_at=None,
    is_active=True,
)
pprint(user_base.model_dump())


# %%
class PostBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    published: bool
    author_id: UUID


post_base = PostBase(
    id=uuid4(),
    title="Getting Started with FastAPI",
    content="FastAPI is a modern web framework...",
    created_at=datetime.now(timezone.utc),
    updated_at=None,
    published=True,
    author_id=user_base.id,
)
pprint(post_base.model_dump())


# %%
class CommentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    author_id: UUID
    post_id: UUID


comment_base = CommentBase(
    id=uuid4(),
    content="Great article! Very helpful.",
    created_at=datetime.now(timezone.utc),
    updated_at=None,
    author_id=user_base.id,
    post_id=post_base.id,
)
pprint(comment_base.model_dump())


# %%
############## Request Models (for input validation) ######


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    password: SecretStr


user_create = UserCreate(
    username="johndoe",
    email="john@example.com",
    full_name="John Doe",
    bio="Python developer",
    password="secure123",
)
pprint(user_create.model_dump())


# %%
class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    published: bool = False


post_create = PostCreate(
    title="Getting Started with FastAPI",
    content="FastAPI is a modern web framework...",
    published=True,
)
pprint(post_create.model_dump())


# %%
class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


comment_create = CommentCreate(content="Great article! Very helpful.")
pprint(comment_create.model_dump())

# %%
############ Response models with relationships ############


class Comment(CommentBase):
    author: UserBase


print(comment_base.model_dump())

comment = Comment(**comment_base.model_dump(), author=user_base)
pprint(comment.model_dump())


# %%
class Post(PostBase):
    author: UserBase
    comments: List[Comment] = []


post = Post(**post_base.model_dump(), author=user_base, comments=[comment, comment])
pprint(post.model_dump())

# %%


class User(UserBase):
    posts: List[Post] = []
    comments: List[Comment] = []


user = User(**user_base.model_dump(), posts=[post, post], comments=[comment, comment])
pprint(user.model_dump())
# %%

# %%
# Final example showing how all models work together
# Create a new user

# Create a new user
new_user = UserCreate(
    username="testuser",
    email="test@example.com",
    full_name="Test User",
    bio="Testing the models",
    password="testpass123",
)

pprint(new_user.model_dump())
# %%

# Simulate user creation response
user_response = UserBase(
    id=uuid4(),
    username=new_user.username,
    email=new_user.email,
    full_name=new_user.full_name,
    bio=new_user.bio,
    created_at=datetime.utcnow(),
    updated_at=None,
    is_active=True,
)

pprint(user_response.model_dump())

# %%
# Create a full user response with relationships
full_user = User(**user_response.model_dump(), posts=[post], comments=[comment])
pprint(full_user.model_dump_json(indent=2))

# %%
