from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, SQLModel, create_engine, Session, select


# Define the database models
class User(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str


class Post(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    author_id: int = Field(foreign_key="user.id")


# Create the database engine
sqlite_file_name = "simple_blog.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


# Create the database and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Dependency to get a session
def get_session():
    with Session(engine) as session:
        yield session


# Initialize FastAPI app
app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


# User Endpoints
@app.post("/users/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users/", response_model=List[User])
def read_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users


# Post Endpoints
@app.post("/posts/", response_model=Post)
def create_post(post: Post, session: Session = Depends(get_session)):
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@app.get("/posts/", response_model=List[Post])
def read_posts(session: Session = Depends(get_session)):
    posts = session.exec(select(Post)).all()
    return posts


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application with reload enabled
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
