from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr, SecretStr
from rich import print
from rich.pretty import pprint


# User model representing application users
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str
    email: EmailStr
    full_name: str
    bio: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = True
    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")


# Post model representing blog posts
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


# Comment model representing comments on posts
class Comment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    author_id: UUID = Field(foreign_key="user.id")
    post_id: UUID = Field(foreign_key="post.id")
    author: User = Relationship(back_populates="comments")
    post: Post = Relationship(back_populates="comments")


# Model for creating a new user with input validation
class UserCreate(SQLModel):
    username: str
    email: EmailStr
    full_name: str
    bio: Optional[str] = None
    password: SecretStr


# Model for creating a new post with input validation
class PostCreate(SQLModel):
    title: str
    content: str
    published: bool = False


# Model for creating a new comment with input validation
class CommentCreate(SQLModel):
    content: str


if __name__ == "__main__":
    from sqlmodel import create_engine
    from database import create_db_and_tables
    from sqlmodel import Session

    # Initialize database engine
    engine = create_engine("sqlite:///blog.db")
    create_db_and_tables()

    with Session(engine) as session:
        # Create a new user
        user = User(username="test", email="jb@gmail.com", full_name="John Doe")
        session.add(user)
        session.commit()
        session.refresh(user)
        pprint(user, expand_all=True)

        # Create a new post authored by the user
        post = Post(title="Test Post", content="This is a test post", author_id=user.id)
        session.add(post)
        session.commit()
        session.refresh(post)
        pprint(post, expand_all=True)

        # Create a new comment on the post by the user
        comment = Comment(content="This is a test comment", author_id=user.id, post_id=post.id)
        session.add(comment)
        session.commit()
        session.refresh(comment)
        pprint(comment, expand_all=True)
