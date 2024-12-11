# test_api.py  
import requests  
import random  
from faker import Faker  
import json  

# Initialize Faker  
fake = Faker()  

# API base URL  
BASE_URL = "http://localhost:8000"  

def generate_post():  
    """Generate fake blog post data"""  
    return {  
        "title": fake.unique.catch_phrase(),  
        "content": fake.text(max_nb_chars=200),  
        "author": fake.name()  
    }  

def test_api():  
    """Test all API endpoints"""  
    print("🚀 Starting API tests...\n")  

    # Test POST endpoint - Create posts  
    print("📝 Testing POST /posts/")  
    created_posts = []  
    for _ in range(5):  
        post_data = generate_post()  
        response = requests.post(f"{BASE_URL}/posts/", json=post_data)  
        if response.status_code == 201:  
            created_posts.append(response.json())  
            print(f"✅ Created post: {post_data['title']}")  
        else:  
            print(f"❌ Failed to create post: {response.json()}")  
    print()  

    # Test GET all posts  
    print("📚 Testing GET /posts/")  
    response = requests.get(f"{BASE_URL}/posts/")  
    if response.status_code == 200:  
        posts = response.json()  
        print(f"✅ Retrieved {len(posts)} posts")  
    else:  
        print("❌ Failed to retrieve posts")  
    print()  

    # Test GET single post  
    if created_posts:  
        post_id = created_posts[0]['id']  
        print(f"📖 Testing GET /posts/{post_id}")  
        response = requests.get(f"{BASE_URL}/posts/{post_id}")  
        if response.status_code == 200:  
            print(f"✅ Retrieved post: {response.json()['title']}")  
        else:  
            print("❌ Failed to retrieve post")  
    print()  

    # Test PATCH endpoint  
    if created_posts:  
        post_id = created_posts[0]['id']  
        print(f"✏️ Testing PATCH /posts/{post_id}")  
        update_data = {  
            "title": fake.unique.catch_phrase(),  
            "status": "published"  
        }  
        response = requests.patch(f"{BASE_URL}/posts/{post_id}", json=update_data)  
        if response.status_code == 200:  
            print(f"✅ Updated post: {response.json()['title']}")  
        else:  
            print(f"❌ Failed to update post: {response.json()}")  
    print()  

    # Test invalid status transition  
    if created_posts:  
        post_id = created_posts[0]['id']  
        print("🚫 Testing invalid status transition")  
        # First set to archived  
        requests.patch(f"{BASE_URL}/posts/{post_id}", json={"status": "archived"})  
        # Then try to set to published  
        response = requests.patch(f"{BASE_URL}/posts/{post_id}", json={"status": "published"})  
        if response.status_code == 400:  
            print("✅ Successfully caught invalid status transition")  
        else:  
            print("❌ Failed to catch invalid status transition")  
    print()  

    # Test DELETE endpoint  
    if created_posts:  
        post_id = created_posts[-1]['id']  
        print(f"🗑️ Testing DELETE /posts/{post_id}")  
        response = requests.delete(f"{BASE_URL}/posts/{post_id}")  
        if response.status_code == 204:  
            print(f"✅ Deleted post {post_id}")  
            # Verify deletion  
            response = requests.get(f"{BASE_URL}/posts/{post_id}")  
            if response.status_code == 404:  
                print("✅ Verified post deletion")  
        else:  
            print("❌ Failed to delete post")  
    print()  

def main():  
    """Main function to run the tests"""  
    try:  
        # Check if API is running  
        requests.get(BASE_URL)  
        test_api()  
    except requests.exceptions.ConnectionError:  
        print("❌ Error: API is not running. Please start the FastAPI server first.")  
        print("Run: uvicorn app.main:p06_app --reload")  

if __name__ == "__main__":  
    main()  