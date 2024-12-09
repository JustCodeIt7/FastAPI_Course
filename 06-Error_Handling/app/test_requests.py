# test_requests.py
import requests
import json
from datetime import date

# Base URL
BASE_URL = "http://localhost:8000"


def test_create_user():
    # Test 1: Valid user creation
    valid_user = {
        "email": "john.doe@example.com",
        "username": "johndoe123",
        "full_name": "John Doe",
        "birth_date": "1990-01-01",
        "phone_number": "+1234567890",
        "password": "Password123",
    }

    response = requests.post(f"{BASE_URL}/users/", json=valid_user)
    print("\nTest 1 - Valid User Creation:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 2: Invalid email format
    invalid_email_user = valid_user.copy()
    invalid_email_user["email"] = "invalid-email"

    response = requests.post(f"{BASE_URL}/users/", json=invalid_email_user)
    print("\nTest 2 - Invalid Email Format:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test 3: Weak password
    weak_password_user = valid_user.copy()
    weak_password_user["password"] = "weak"

    response = requests.post(f"{BASE_URL}/users/", json=weak_password_user)
    print("\nTest 3 - Weak Password:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    test_create_user()
