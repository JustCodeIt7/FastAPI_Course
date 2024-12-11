# test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import p06_app, Base, get_db, BlogPost, PostStatus

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_blog.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    p06_app.dependency_overrides[get_db] = override_get_db
    with TestClient(p06_app) as c:
        yield c


def create_test_post(
    db,
    title="Test Post",
    content="Test Content",
    author="Test Author",
    status=PostStatus.DRAFT,
):
    post = BlogPost(title=title, content=content, author=author, status=status)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def create_test_posts(db, count=10):
    for i in range(count):
        create_test_post(
            db,
            title=f"Test Post {i}",
            content=f"Test Content {i}",
            author=f"Author {i}",
        )


def test_create_post(client):
    response = client.post(
        "/posts/",
        json={"title": "New Post", "content": "New Content", "author": "New Author"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "New Post"


def test_create_post_with_existing_title(client):
    response = client.post(
        "/posts/",
        json={"title": "Test Post", "content": "New Content", "author": "New Author"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "A post with this title already exists"


def test_list_posts(client):
    response = client.get("/posts/")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_post(client):
    response = client.get("/posts/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Post"


def test_get_post_not_found(client):
    response = client.get("/posts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_update_post(client):
    response = client.patch("/posts/1", json={"title": "Updated Post"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Post"


def test_update_post_invalid_status_transition(client):
    response = client.patch("/posts/1", json={"status": "archived"})
    assert response.status_code == 200
    response = client.patch("/posts/1", json={"status": "published"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot transition from archived to published"


def test_delete_post(client):
    response = client.delete("/posts/1")
    assert response.status_code == 204
    response = client.get("/posts/1")
    assert response.status_code == 404


if __name__ == "__main__":
    import uvicorn
    
    