# Import necessary libraries  
from fastapi import FastAPI, HTTPException  
from pydantic import BaseModel, field_validator  
import enum  
from typing import List, Optional, Dict  

# ==================== ENUMS ====================  
# Define possible status values for blog posts  
class PostStatus(str, enum.Enum):  
    DRAFT = "draft"          # Initial state  
    PUBLISHED = "published"  # Visible to readers  
    ARCHIVED = "archived"    # Removed from active posts  

# ==================== PYDANTIC MODELS ====================  
# Base model for common attributes  
class PostBase(BaseModel):  
    title: str  
    content: str  
    author: str  

# Model for creating new posts  
class PostCreate(PostBase):  
    @field_validator('title')
    def validate_title(cls, title):  
        # Check if title starts with capital letter  
        if not title[0].isupper():  
            raise ValueError("Title must start with a capital letter")  

        # Check minimum length  
        if len(title) < 5:  
            raise ValueError("Title must be at least 5 characters long")  

        # Check maximum length  
        if len(title) > 100:  
            raise ValueError("Title cannot be longer than 100 characters")  

        # Check for special characters  
        if not title.replace(" ", "").isalnum():  
            raise ValueError("Title can only contain letters, numbers, and spaces")  

        return title
    
    @field_validator('content')
    def validate_content(cls, content):
        # Check minimum length
        if len(content) < 10:
            raise ValueError("Content must be at least 10 characters long")

        return content
    
    @field_validator('author')
    def validate_author(cls, author):
        # Check minimum length
        if len(author) < 5:
            raise ValueError("Author name must be at least 5 characters long")

        # Check maximum length
        if len(author) > 50:
            raise ValueError("Author name cannot be longer than 50 characters")

        return author
    
    status: PostStatus = PostStatus.DRAFT
    
    @field_validator('status')
    def validate_status(cls, status):
        # Check if status is a valid choice
        if status not in PostStatus:
            raise ValueError("Invalid status value")

        return status   

# Model for updating existing posts  
class PostUpdate(BaseModel):  
    # All fields optional for partial updates  
    title: Optional[str] = None  
    content: Optional[str] = None  
    author: Optional[str] = None  
    status: Optional[PostStatus] = None  

# Complete post model including ID and status  
class Post(PostBase):  
    id: int  
    status: PostStatus  

# ==================== IN-MEMORY DATABASE ====================  
# Dictionary to store posts  
posts_db: Dict[int, Post] = {}  
# Counter for post IDs  
post_id_counter = 1  

# ==================== FASTAPI APP ====================  
app = FastAPI(title="Blog API with Pydantic")  

# ==================== API ROUTES ====================  
# Create new post  
@app.post("/posts/", response_model=Post, status_code=201)  
def create_post(post: PostCreate):  
    global post_id_counter  

    # Check for duplicate titles  
    if any(p.title == post.title for p in posts_db.values()):  
        raise HTTPException(  
            status_code=400,   
            detail="A post with this title already exists"  
        )  

    # Create new post  
    new_post = Post(  
        id=post_id_counter,  
        status=PostStatus.DRAFT,  
        **post.dict()  
    )  
    posts_db[post_id_counter] = new_post  
    post_id_counter += 1  

    return new_post  

# Get all posts  
@app.get("/posts/", response_model=List[Post])  
def list_posts():  
    return list(posts_db.values())  

# Get single post by ID  
@app.get("/posts/{post_id}", response_model=Post)  
def get_post(post_id: int):  
    if post_id not in posts_db:  
        raise HTTPException(status_code=404, detail="Post not found")  
    return posts_db[post_id]  

# Update existing post  
@app.patch("/posts/{post_id}", response_model=Post)  
def update_post(post_id: int, post_update: PostUpdate):  
    # Check if post exists  
    if post_id not in posts_db:  
        raise HTTPException(status_code=404, detail="Post not found")  

    post = posts_db[post_id]  

    # Validate status transitions  
    if (post_update.status and   
        post.status == PostStatus.ARCHIVED and   
        post_update.status != PostStatus.ARCHIVED):  
        raise HTTPException(  
            status_code=400,  
            detail="Cannot transition from archived to published"  
        )  

    # Update post attributes  
    update_data = post_update.dict(exclude_unset=True)  
    updated_post = Post(  
        **{  
            **post.dict(),  
            **update_data  
        }  
    )  
    posts_db[post_id] = updated_post  

    return updated_post  

# Delete post  
@app.delete("/posts/{post_id}", status_code=204)  
def delete_post(post_id: int):  
    if post_id not in posts_db:  
        raise HTTPException(status_code=404, detail="Post not found")  

    del posts_db[post_id]  
    return None  

# ==================== MAIN ====================  
if __name__ == "__main__":  
    import uvicorn  
    uvicorn.run(  
        "main:app",  
        host="0.0.0.0",  
        port=8000,  
        log_level="debug",  
        reload=True  
    )  