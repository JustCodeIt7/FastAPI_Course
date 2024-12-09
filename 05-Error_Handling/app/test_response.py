# test_library.py
import requests
import json

BASE_URL = "http://localhost:8000"


def test_library_api():
    # Create a book
    print("\n1. Creating a new book:")
    book_data = {
        "title": "The FastAPI Handbook",
        "author": "John Doe",
        "published": True,
    }
    response = requests.post(f"{BASE_URL}/books/", json=book_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    book_id = response.json()["id"]

    # Get all books
    print("\n2. Getting all books:")
    response = requests.get(f"{BASE_URL}/books/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Get specific book
    print(f"\n3. Getting book {book_id}:")
    response = requests.get(f"{BASE_URL}/books/{book_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Update book
    print(f"\n4. Updating book {book_id}:")
    book_data["title"] = "Updated FastAPI Handbook"
    response = requests.put(f"{BASE_URL}/books/{book_id}", json=book_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Delete book
    print(f"\n5. Deleting book {book_id}:")
    response = requests.delete(f"{BASE_URL}/books/{book_id}")
    print(f"Status Code: {response.status_code}")


if __name__ == "__main__":
    test_library_api()
