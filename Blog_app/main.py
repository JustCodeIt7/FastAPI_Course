# main.py (updated)
from datetime import datetime
from typing import Optional, Annotated

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Field, Session, SQLModel, create_engine, select

# --------------------------
# FastAPI App Configuration
# --------------------------
app = FastAPI(title="FastAPI Blog Tutorial", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --------------------------
# Database Configuration
# --------------------------
sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


# Create type annotation for dependencies
SessionDep = Annotated[Session, Depends(get_session)]


# --------------------------
# Database Models
# --------------------------
class Blog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    author: str = Field(default="Anonymous")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# --------------------------
# Application Routes
# --------------------------
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, session: SessionDep):
    """
    Corrected dependency declaration using Annotated
    """
    statement = select(Blog).order_by(Blog.created_at.desc())
    posts = session.exec(statement).all()

    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})


@app.post("/create_post", response_class=HTMLResponse)
async def create_post(
    request: Request,
    session: SessionDep,
    title: str = Form(...),
    content: str = Form(...),
    author: str = Form("Anonymous"),
):
    new_post = Blog(title=title, content=content, author=author)
    session.add(new_post)
    session.commit()

    return templates.TemplateResponse(
        "partials/redirect.html",
        {"request": request, "redirect_url": app.url_path_for("read_root")},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
