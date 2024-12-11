# app/main.py  
from fastapi import FastAPI, HTTPException, Depends  
from sqlalchemy import create_engine, Column, Integer, String, Enum  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker, Session  
from pydantic import BaseModel  
import enum  
from typing import List, Optional  

# Database setup  
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"  
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})  
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  
Base = declarative_base()  

# Enums  
class PostStatus(str, enum.Enum):  
    DRAFT = "draft"  
    PUBLISHED = "published"  
    ARCHIVED = "archived"  

# Database Models  
class BlogPost(Base):  
    __tablename__ = "posts"  

    id = Column(Integer, primary_key=True, index=True)  
    title = Column(String, unique=True, index=True)  
    content = Column(String)  
    author = Column(String)  
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)  

# Pydantic Models  
class PostBase(BaseModel):  
    title: str  
    content: str  
    author: str  

class PostCreate(PostBase):  
    pass  

class PostUpdate(BaseModel):  
    title: Optional[str] = None  
    content: Optional[str] = None  
    author: Optional[str] = None  
    status: Optional[PostStatus] = None  

class Post(PostBase):  
    id: int  
    status: PostStatus  

    class Config:  
        orm_mode = True  

# Create tables  
Base.metadata.create_all(bind=engine)  

# Dependency  
def get_db():  
    db = SessionLocal()  
    try:  
        yield db  
    finally:  
        db.close()  

# FastAPI app  
p06_app = FastAPI()  

# Routes  
@p06_app.post("/posts/", response_model=Post, status_code=201)  
def create_post(post: PostCreate, db: Session = Depends(get_db)):  
    db_post = db.query(BlogPost).filter(BlogPost.title == post.title).first()  
    if db_post:  
        raise HTTPException(status_code=400, detail="A post with this title already exists")  

    db_post = BlogPost(**post.dict())  
    db.add(db_post)  
    db.commit()  
    db.refresh(db_post)  
    return db_post  

@p06_app.get("/posts/", response_model=List[Post])  
def list_posts(db: Session = Depends(get_db)):  
    return db.query(BlogPost).all()  

@p06_app.get("/posts/{post_id}", response_model=Post)  
def get_post(post_id: int, db: Session = Depends(get_db)):  
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()  
    if post is None:  
        raise HTTPException(status_code=404, detail="Post not found")  
    return post  

@p06_app.patch("/posts/{post_id}", response_model=Post)  
def update_post(post_id: int, post_update: PostUpdate, db: Session = Depends(get_db)):  
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()  
    if db_post is None:  
        raise HTTPException(status_code=404, detail="Post not found")  

    # Check status transition  
    if post_update.status and db_post.status == PostStatus.ARCHIVED:  
        if post_update.status != PostStatus.ARCHIVED:  
            raise HTTPException(  
                status_code=400,  
                detail="Cannot transition from archived to published"  
            )  
    update_data = post_update.dict(exclude_unset=True)  
    for key, value in update_data.items():  
        setattr(db_post, key, value)  

    db.commit()  
    db.refresh(db_post)  
    return db_post  

@p06_app.delete("/posts/{post_id}", status_code=204)  
def delete_post(post_id: int, db: Session = Depends(get_db)):  
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()  
    if db_post is None:  
        raise HTTPException(status_code=404, detail="Post not found")  

    db.delete(db_post)  
    db.commit()  
    return None  



if __name__ == "__main__":

    # Use this for debugging purposes only

    import uvicorn

    uvicorn.run(
        "main:p06_app", host="0.0.0.0", port=8000, log_level="debug", reload=True
    )
