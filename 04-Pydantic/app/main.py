# Import necessary libraries  
# FastAPI for building the API  
from fastapi import FastAPI, HTTPException, Depends  
# SQLAlchemy for database operations  
from sqlalchemy import create_engine, Column, Integer, String, Enum  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker, Session  
# Pydantic for data validation  
from pydantic import BaseModel  
# Standard library imports  
import enum  
from typing import List, Optional  

# ==================== DATABASE SETUP ====================  
# Configure SQLite database  
# Using SQLite for simplicity - can be changed to PostgreSQL or MySQL  
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"  
engine = create_engine(  
    SQLALCHEMY_DATABASE_URL,   
    connect_args={"check_same_thread": False}  # SQLite specific argument  
)  
# Create database session  
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  
# Base class for SQLAlchemy models  
Base = declarative_base()  

# ==================== ENUMS ====================  
# Define possible status values for blog posts  
class PostStatus(str, enum.Enum):  
    DRAFT = "draft"          
    PUBLISHED = "published"  
    ARCHIVED = "archived"    
# ==================== DATABASE MODELS ====================  
# SQLAlchemy model for database table  
class BlogPost(Base):  
    __tablename__ = "posts"  

    # Primary key  
    id = Column(Integer, primary_key=True, index=True)  
    # Unique title field with index for faster queries  
    title = Column(String, unique=True, index=True)  
    # Post content  
    content = Column(String)  
    # Author of the post  
    author = Column(String)  
    # Post status with default value  
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)  

# ==================== PYDANTIC MODELS ====================  
# Base model for common attributes  
class PostBase(BaseModel):  
    title: str  
    content: str  
    author: str  

# Model for creating new posts  
class PostCreate(PostBase):  
    pass  

# Model for updating existing posts  
class PostUpdate(BaseModel):  
    # All fields optional for partial updates  
    title: Optional[str] = None  
    content: Optional[str] = None  
    author: Optional[str] = None  
    status: Optional[PostStatus] = None  

# Complete post model including database fields  
class Post(PostBase):  
    id: int  
    status: PostStatus  

    class Config:  
        # Enable ORM mode for Pydantic  
        orm_mode = True  

# Create database tables  
Base.metadata.create_all(bind=engine)  

# ==================== DATABASE DEPENDENCY ====================  
# Dependency for database sessions  
def get_db():  
    db = SessionLocal()  
    try:  
        yield db  
    finally:  
        # Ensure database connection is closed  
        db.close()  

# ==================== FASTAPI APP ====================  
p06_app = FastAPI()  

# ==================== API ROUTES ====================  
# Create new post  
@p06_app.post("/posts/", response_model=Post, status_code=201)  
def create_post(post: PostCreate, db: Session = Depends(get_db)):  
    # Check for duplicate titles  
    db_post = db.query(BlogPost).filter(BlogPost.title == post.title).first()  
    if db_post:  
        raise HTTPException(status_code=400, detail="A post with this title already exists")  

    # Create new post  
    db_post = BlogPost(**post.dict())  
    db.add(db_post)  
    db.commit()  
    db.refresh(db_post)  
    return db_post  

# Get all posts  
@p06_app.get("/posts/", response_model=List[Post])  
def list_posts(db: Session = Depends(get_db)):  
    return db.query(BlogPost).all()  

# Get single post by ID  
@p06_app.get("/posts/{post_id}", response_model=Post)  
def get_post(post_id: int, db: Session = Depends(get_db)):  
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()  
    if post is None:  
        raise HTTPException(status_code=404, detail="Post not found")  
    return post  

# Update existing post  
@p06_app.patch("/posts/{post_id}", response_model=Post)  
def update_post(post_id: int, post_update: PostUpdate, db: Session = Depends(get_db)):  
    # Check if post exists  
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()  
    if db_post is None:  
        raise HTTPException(status_code=404, detail="Post not found")  

    # Validate status transitions  
    # Cannot change status from archived to anything else  
    if post_update.status and db_post.status == PostStatus.ARCHIVED:  
        if post_update.status != PostStatus.ARCHIVED:  
            raise HTTPException(  
                status_code=400,  
                detail="Cannot transition from archived to published"  
            )  

    # Update post attributes  
    update_data = post_update.dict(exclude_unset=True)  
    for key, value in update_data.items():  
        setattr(db_post, key, value)  

    db.commit()  
    db.refresh(db_post)  
    return db_post  

# Delete post  
@p06_app.delete("/posts/{post_id}", status_code=204)  
def delete_post(post_id: int, db: Session = Depends(get_db)):  
    # Check if post exists  
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()  
    if db_post is None:  
        raise HTTPException(status_code=404, detail="Post not found")  

    # Delete post  
    db.delete(db_post)  
    db.commit()  
    return None  

# ==================== MAIN ====================  
if __name__ == "__main__":  
    # Run the application (development only)  
    import uvicorn  
    uvicorn.run(  
        "main:p06_app",   
        host="0.0.0.0",   
        port=8000,   
        log_level="debug",   
        reload=True  
    )  