# tests/test_main.py

import pytest
from fastapi.testclient import TestClient
from main import app
from uuid import UUID

client = TestClient(app)

# -------------------------
# Helper Functions (Optional)
# -------------------------


def create_user(
    username: str, email: str, full_name: str, bio: str = None, password: str = "password123"
):
    response = client.post(
        "/users",
        json={
            "username": username,
            "email": email,
            "full_name": full_name,
            "bio": bio,
            "password": password,
        },
    )
    return response


def create_post(title: str, content: str, author_id: str, published: bool = False):
    response = client.post(
        "/posts",
        params={"author_id": author_id},
        json={"title": title, "content": content, "published": published},
    )
    return response


def create_comment(post_id: str, author_id: str, content: str):
    response = client.post(
        f"/posts/{post_id}/comments", params={"author_id": author_id}, json={"content": content}
    )
    return response


# -------------------------
# User Tests
# -------------------------


def test_create_user():
    response = create_user(
        username="testuser",
        email="testuser@example.com",
        full_name="Test User",
        bio="This is a test user.",
        password="securepassword123",
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test User"
    assert data["bio"] == "This is a test user."
    assert data["is_active"] is True
    assert UUID(data["id"])


def test_list_users():
    # Ensure at least one user exists
    create_user(
        username="listuser",
        email="listuser@example.com",
        full_name="List User",
        bio="List user bio.",
    )
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_user():
    # Create a user
    create_resp = create_user(
        username="specificuser",
        email="specific@example.com",
        full_name="Specific User",
        bio="Specific user bio.",
    )
    user_id = create_resp.json()["id"]

    # Retrieve the user
    get_resp = client.get(f"/users/{user_id}")
    assert get_resp.status_code == 200
    user_data = get_resp.json()
    assert user_data["id"] == user_id
    assert user_data["username"] == "specificuser"


# -------------------------
# Post Tests
# -------------------------


def test_create_post():
    # Create a user
    user_resp = create_user(
        username="postauthor",
        email="author@example.com",
        full_name="Post Author",
        bio="Author bio.",
    )
    author_id = user_resp.json()["id"]

    # Create a post
    post_resp = create_post(
        title="First Post",
        content="This is the content of the first post.",
        author_id=author_id,
        published=True,
    )
    assert post_resp.status_code == 200
    post_data = post_resp.json()
    assert "id" in post_data
    assert post_data["title"] == "First Post"
    assert post_data["content"] == "This is the content of the first post."
    assert post_data["published"] is True
    assert post_data["author_id"] == author_id
    assert post_data["author"]["id"] == author_id


def test_list_posts():
    # Create a user and a post
    user_resp = create_user(
        username="postlister",
        email="postlister@example.com",
        full_name="Post Lister",
        bio="Lister bio.",
    )
    author_id = user_resp.json()["id"]

    create_post(title="List Post", content="Content for listing.", author_id=author_id)

    # List posts
    response = client.get("/posts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_post():
    # Create a user and a post
    user_resp = create_user(
        username="postgetter",
        email="postgetter@example.com",
        full_name="Post Getter",
        bio="Getter bio.",
    )
    author_id = user_resp.json()["id"]

    post_resp = create_post(
        title="Specific Post", content="Content of the specific post.", author_id=author_id
    )
    post_id = post_resp.json()["id"]

    # Retrieve the post
    get_resp = client.get(f"/posts/{post_id}")
    assert get_resp.status_code == 200
    post_data = get_resp.json()
    assert post_data["id"] == post_id
    assert post_data["title"] == "Specific Post"


# -------------------------
# Comment Tests
# -------------------------


def test_create_comment():
    # Create a user and a post
    user_resp = create_user(
        username="commenter",
        email="commenter@example.com",
        full_name="Commenter User",
        bio="Commenter bio.",
    )
    author_id = user_resp.json()["id"]

    post_resp = create_post(
        title="Post for Comment",
        content="Content of the post to be commented on.",
        author_id=author_id,
    )
    post_id = post_resp.json()["id"]

    # Create a comment
    comment_resp = create_comment(
        post_id=post_id, author_id=author_id, content="This is a comment."
    )
    assert comment_resp.status_code == 200
    comment_data = comment_resp.json()
    assert "id" in comment_data
    assert comment_data["content"] == "This is a comment."
    assert comment_data["author_id"] == author_id
    assert comment_data["post_id"] == post_id
    assert comment_data["author"]["id"] == author_id


def test_get_comment():
    # Create a user, a post, and a comment
    user_resp = create_user(
        username="commentgetter",
        email="commentgetter@example.com",
        full_name="Comment Getter",
        bio="Getter bio.",
    )
    author_id = user_resp.json()["id"]

    post_resp = create_post(
        title="Post for Specific Comment", content="Content of the post.", author_id=author_id
    )
    post_id = post_resp.json()["id"]

    comment_resp = create_comment(post_id=post_id, author_id=author_id, content="Specific comment.")
    comment_id = comment_resp.json()["id"]

    # Retrieve the comment
    get_resp = client.get(f"/comments/{comment_id}")
    assert get_resp.status_code == 200
    comment_data = get_resp.json()
    assert comment_data["id"] == comment_id
    assert comment_data["content"] == "Specific comment."
