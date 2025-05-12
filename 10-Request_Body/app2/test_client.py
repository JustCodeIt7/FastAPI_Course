import httpx
import json
import asyncio
from pprint import pprint

# Base URL for our FastAPI application
BASE_URL = "http://localhost:8000"

async def test_api_endpoints():
    """
    Function to test various API endpoints with different request body scenarios.
    This script can be used to demonstrate how to interact with the API in the YouTube tutorial.
    """
    async with httpx.AsyncClient() as client:
        print("\n" + "="*50)
        print("FASTAPI REQUEST BODY EXAMPLES")
        print("="*50)
        
        # ==================== BASIC REQUEST BODY EXAMPLE ====================
        print("\n1. BASIC REQUEST BODY EXAMPLE")
        basic_item = {
            "name": "Laptop",
            "description": "High-performance laptop for developers",
            "price": 1299.99,
            "tax": 129.99,
            "tags": ["electronics", "computers"]
        }
        
        response = await client.post(f"{BASE_URL}/items/", json=basic_item)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        
        # ==================== NESTED MODELS EXAMPLE ====================
        print("\n2. NESTED MODELS EXAMPLE")
        product = {
            "name": "Smart TV",
            "category": "electronics",
            "price": 799.99,
            "is_available": True,
            "images": [
                {"url": "https://example.com/tv1.jpg", "name": "Front view"},
                {"url": "https://example.com/tv2.jpg", "name": "Side view"}
            ],
            "metadata": {
                "resolution": "4K",
                "screen_size": "55 inches",
                "refresh_rate": "120Hz"
            }
        }
        
        response = await client.post(f"{BASE_URL}/products/", json=product)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        
        # ==================== MULTIPLE BODY PARAMETERS ====================
        print("\n3. MULTIPLE BODY PARAMETERS")
        order_data = {
            "user": {
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe"
            },
            "item": {
                "name": "Headphones",
                "description": "Wireless noise-cancelling headphones",
                "price": 199.99,
                "tax": 20.00,
                "tags": ["audio", "electronics"]
            },
            "quantity": 2,
            "priority": True
        }
        
        response = await client.post(f"{BASE_URL}/order/", json=order_data)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        
        # ==================== BODY WITH PATH AND QUERY PARAMETERS ====================
        print("\n4. BODY WITH PATH AND QUERY PARAMETERS")
        update_item = {
            "name": "Updated Item",
            "description": "This item has been updated",
            "price": 49.99,
            "tax": 5.00,
            "tags": ["updated", "modified"]
        }
        
        response = await client.put(
            f"{BASE_URL}/items/42?q=search_term", 
            json=update_item
        )
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        
        # ==================== SINGULAR VALUES IN THE BODY ====================
        print("\n5. SINGULAR VALUES IN THE BODY")
        importance_data = {
            "importance": 3,
            "notes": "This is a moderately important item"
        }
        
        response = await client.post(
            f"{BASE_URL}/items/123/set-importance", 
            json=importance_data
        )
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        
        # ==================== EMBEDDING A SINGLE MODEL IN THE BODY ====================
        print("\n6. EMBEDDING A SINGLE MODEL IN THE BODY")
        embedded_item = {
            "item": {
                "name": "Gaming Mouse",
                "description": "High-precision gaming mouse",
                "price": 59.99,
                "tax": 6.00,
                "tags": ["gaming", "peripherals"]
            }
        }
        
        response = await client.post(f"{BASE_URL}/items/create-with-extra/", json=embedded_item)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        
        print("\nAll tests completed!")

# Run the test function
if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
