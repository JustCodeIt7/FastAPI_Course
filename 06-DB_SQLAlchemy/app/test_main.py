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


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


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


def test_create_post(client, db_session):
    response = client.post(
        "/posts/",
        json={"title": "New Post", "content": "New Content", "author": "New Author"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "New Post"
    post_id = response.json()["id"]
    db_post = db_session.query(BlogPost).filter_by(id=post_id).first()
    assert db_post.title == "New Post"
    assert db_post.content == "New Content"
    assert db_post.author == "New Author"
    assert db_post.status == PostStatus.DRAFT


def test_create_post_with_existing_title(client, db_session):
    create_test_post(db_session)
    response = client.post(
        "/posts/",
        json={"title": "Test Post", "content": "New Content", "author": "New Author"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "A post with this title already exists"


def test_list_posts(client, db_session):
    create_test_posts(db_session)
    response = client.get("/posts/")
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 10


def test_get_post(client, db_session):
    post = create_test_post(db_session)
    response = client.get(f"/posts/{post.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Post"
    assert response.json()["content"] == "Test Content"
    assert response.json()["author"] == "Test Author"


def test_get_post_not_found(client):
    response = client.get("/posts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_update_post_title(client, db_session):
    post = create_test_post(db_session)
    response = client.patch(f"/posts/{post.id}", json={"title": "Updated Post"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Post"
    updated_post = db_session.query(BlogPost).filter_by(id=post.id).first()
    assert updated_post.title == "Updated Post"


def test_update_post_content(client, db_session):
    post = create_test_post(db_session)
    response = client.patch(f"/posts/{post.id}", json={"content": "Updated Content"})
    assert response.status_code == 200
    assert response.json()["content"] == "Updated Content"
    updated_post = db_session.query(BlogPost).filter_by(id=post.id).first()
    assert updated_post.content == "Updated Content"


def test_update_post_author(client, db_session):
    post = create_test_post(db_session)
    response = client.patch(f"/posts/{post.id}", json={"author": "Updated Author"})
    assert response.status_code == 200
    assert response.json()["author"] == "Updated Author"
    updated_post = db_session.query(BlogPost).filter_by(id=post.id).first()
    assert updated_post.author == "Updated Author"


def test_update_post_status(client, db_session):
    post = create_test_post(db_session)
    response = client.patch(f"/posts/{post.id}", json={"status": PostStatus.PUBLISHED})
    assert response.status_code == 200
    assert response.json()["status"] == PostStatus.PUBLISHED
    updated_post = db_session.query(BlogPost).filter_by(id=post.id).first()
    assert updated_post.status == PostStatus.PUBLISHED


def test_update_post_invalid_status_transition(client, db_session):
    post = create_test_post(db_session)
    response = client.patch(f"/posts/{post.id}", json={"status": PostStatus.ARCHIVED})
    assert response.status_code == 200
    response = client.patch(f"/posts/{post.id}", json={"status": PostStatus.PUBLISHED})
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot transition from archived to published"


def test_delete_post(client, db_session):
    post = create_test_post(db_session)
    response = client.delete(f"/posts/{post.id}")
    assert response.status_code == 204
    response = client.get(f"/posts/{post.id}")
    assert response.status_code == 404


def test_delete_nonexistent_post(client):
    response = client.delete("/posts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_create_post_with_invalid_title_length(client, db_session):
    response = client.post(
        "/posts/",
        json={"title": "Hi", "content": "New Content", "author": "New Author"},
    )
    assert response.status_code == 422
    assert any(
        "value_error.any_str.min_length" in error["type"]
        for error in response.json()["detail"]
    )


def test_create_post_with_missing_fields(client, db_session):
    response = client.post(
        "/posts/",
        json={"title": "New Post", "author": "New Author"},
    )
    assert response.status_code == 422
    assert any("field required" in error["msg"] for error in response.json()["detail"])


def test_update_post_with_invalid_title_length(client, db_session):
    post = create_test_post(db_session)
    response = client.patch(f"/posts/{post.id}", json={"title": "Hi"})
    assert response.status_code == 422
    assert any(
        "value_error.any_str.min_length" in error["type"]
        for error in response.json()["detail"]
    )


def test_update_post_with_missing_fields(client, db_session):
    post = create_test_post(db_session)
    response = client.patch(f"/posts/{post.id}", json={})
    assert response.status_code == 422
    assert any("field required" in error["msg"] for error in response.json()["detail"])
