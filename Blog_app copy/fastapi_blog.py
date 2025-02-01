# fastapi_blog.py

"""
Tutorial: Building a Simple Blog Website with FastAPI, SQLModel, and Jinja2 Templates

Instructions:
1. Install the required packages:

   pip install fastapi uvicorn jinja2 sqlmodel

   Optionally, install 'python-multipart' if you need to process HTML form data:
   pip install python-multipart

2. Create a file named `fastapi_blog.py` and copy the code below into it.

3. Run the app:

   uvicorn fastapi_blog:app --reload

4. Visit http://127.0.0.1:8000 to access the blog homepage.

This tutorial demonstrates:
- Setting up a FastAPI app.
- Using SQLModel (an ORM based on SQLAlchemy) to create and manage a database.
- Rendering HTML templates with Jinja2 to display pages.
- Basic CRUD operations (Create, Read, Update, Delete) for blog posts.

Feel free to modify, expand, or customize to suit your needs.
"""

from typing import Optional
from fastapi import FastAPI, Request, Form, Depends, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Field, create_engine, Session, select
import uvicorn

# ----------------------
# Database & Models
# ----------------------


# Define the SQLModel for blog posts
class BlogPost(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str


# Create the SQLite database engine
DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(DATABASE_URL, echo=True)

# Initialize the FastAPI application
app = FastAPI(title="FastAPI Blog Tutorial")

# Setup templates directory
templates = Jinja2Templates(directory="templates")

# Mount a static directory if you have CSS, JS, images, etc.
# Make sure you create a 'static' folder for your static assets.
app.mount("/static", StaticFiles(directory="static"), name="static")


# ----------------------
# Create the database tables
# ----------------------
@app.on_event("startup")
def on_startup():
    # Create the tables in the database if they don't exist
    SQLModel.metadata.create_all(engine)


# ----------------------
# Utility function to get a session
# ----------------------


def get_session():
    with Session(engine) as session:
        yield session


# ----------------------
# Routes
# ----------------------


# 1. Home route - lists all blog posts
@app.get("/", response_class=HTMLResponse)
def read_home(request: Request, session: Session = Depends(get_session)):
    statement = select(BlogPost)
    results = session.exec(statement).all()
    return templates.TemplateResponse("home.html", {"request": request, "posts": results})


# 2. Create new post (GET - form, POST - process form)
@app.get("/create", response_class=HTMLResponse)
def create_post_form(request: Request):
    return templates.TemplateResponse("create_post.html", {"request": request})


@app.post("/create")
def create_post(
    title: str = Form(...), content: str = Form(...), session: Session = Depends(get_session)
):
    new_post = BlogPost(title=title, content=content)
    session.add(new_post)
    session.commit()
    session.refresh(new_post)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


# 3. View a single post
@app.get("/posts/{post_id}", response_class=HTMLResponse)
def read_post(post_id: int, request: Request, session: Session = Depends(get_session)):
    post = session.get(BlogPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("view_post.html", {"request": request, "post": post})


# 4. Update a post (GET - form, POST - process form)
@app.get("/posts/{post_id}/edit", response_class=HTMLResponse)
def edit_post_form(post_id: int, request: Request, session: Session = Depends(get_session)):
    post = session.get(BlogPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})


@app.post("/posts/{post_id}/edit")
def edit_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    session: Session = Depends(get_session),
):
    post = session.get(BlogPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.title = title
    post.content = content
    session.add(post)
    session.commit()
    session.refresh(post)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


# 5. Delete a post
@app.post("/posts/{post_id}/delete")
def delete_post(post_id: int, session: Session = Depends(get_session)):
    post = session.get(BlogPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    session.delete(post)
    session.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


# ----------------------
# HTML Templates (Inline Examples)
# ----------------------

# For a real application, you would place these templates in a /templates folder.
# In order to demonstrate inline code, below are minimal HTML templates.
# If you'd like to store them separately, remove these and create real files.

# Example: home.html
# {{% raw %}}
# <html>
# <head><title>Blog Home</title></head>
# <body>
#     <h1>Welcome to the Blog</h1>
#     <a href="/create">Create a New Post</a>
#     <ul>
#     {% for post in posts %}
#         <li>
#             <a href="/posts/{{ post.id }}">{{ post.title }}</a>
#             <form method="post" action="/posts/{{ post.id }}/delete" style="display:inline;">
#                 <button type="submit">Delete</button>
#             </form>
#             <a href="/posts/{{ post.id }}/edit">Edit</a>
#         </li>
#     {% endfor %}
#     </ul>
# </body>
# </html>
# {{% endraw %}}

# Example: create_post.html
# {{% raw %}}
# <html>
# <head><title>Create Post</title></head>
# <body>
#     <h1>Create a New Post</h1>
#     <form method="post" action="/create">
#         <label for="title">Title:</label>
#         <input type="text" id="title" name="title" required><br><br>
#         <label for="content">Content:</label><br>
#         <textarea id="content" name="content" rows="5" cols="30" required></textarea><br><br>
#         <button type="submit">Create</button>
#     </form>
# </body>
# </html>
# {{% endraw %}}

# Example: view_post.html
# {{% raw %}}
# <html>
# <head><title>{{ post.title }}</title></head>
# <body>
#     <h1>{{ post.title }}</h1>
#     <p>{{ post.content }}</p>
#     <a href="/">Back to Home</a>
# </body>
# </html>
# {{% endraw %}}

# Example: edit_post.html
# {{% raw %}}
# <html>
# <head><title>Edit Post</title></head>
# <body>
#     <h1>Edit Post</h1>
#     <form method="post" action="/posts/{{ post.id }}/edit">
#         <label for="title">Title:</label>
#         <input type="text" id="title" name="title" value="{{ post.title }}" required><br><br>
#         <label for="content">Content:</label><br>
#         <textarea id="content" name="content" rows="5" cols="30" required>{{ post.content }}</textarea><br><br>
#         <button type="submit">Save</button>
#     </form>
#     <a href="/">Back to Home</a>
# </body>
# </html>
# {{% endraw %}}

if __name__ == "__main__":
    uvicorn.run("fastapi_blog:app", host="127.0.0.1", port=8000, reload=True)
