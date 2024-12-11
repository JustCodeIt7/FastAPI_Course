# test_blog.py
import requests

BASE_URL = "http://localhost:8000"


def test_blog_api():
    # Create a post
    print("\n1. Creating a new blog post:")
    post_data = {
        "title": "My First Post",
        "content": "This is the content of my first post!",
    }
    response = requests.post(f"{BASE_URL}/posts/", json=post_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    post_id = response.json()["id"]

    # Get all posts
    print("\n2. Getting all posts:")
    response = requests.get(f"{BASE_URL}/posts/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    # Get specific post
    print(f"\n3. Getting post {post_id}:")
    response = requests.get(f"{BASE_URL}/posts/{post_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    # Delete post
    print(f"\n4. Deleting post {post_id}:")
    response = requests.delete(f"{BASE_URL}/posts/{post_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    # Create post
    print("\n5. Creating a new blog post:")
    post_data = {
        "title": "My Second Post",
        "content": "This is the content of my second post!",
    }
    response = requests.post(f"{BASE_URL}/posts/", json=post_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    post_id = response.json()["id"]

    # Update post content
    print(f"\n6. Updating post {post_id}:")
    update_data = {
        "content": "This is the updated content of my second post!",
    }
    response = requests.patch(f"{BASE_URL}/posts/{post_id}", json=update_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    # Get specific post
    print(f"\n7. Getting post {post_id}:")
    response = requests.get(f"{BASE_URL}/posts/{post_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    test_blog_api()
