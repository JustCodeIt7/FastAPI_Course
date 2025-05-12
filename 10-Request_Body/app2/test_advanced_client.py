import httpx
import json
import asyncio
from pprint import pprint
from datetime import datetime

# Base URL for our FastAPI application with advanced models
BASE_URL = "http://localhost:8001"

async def test_advanced_api_endpoints():
    """
    Function to test advanced API endpoints with complex request body scenarios.
    This script demonstrates how to interact with the advanced API features.
    """
    async with httpx.AsyncClient() as client:
        print("\n" + "="*50)
        print("FASTAPI ADVANCED REQUEST BODY EXAMPLES")
        print("="*50)
        
        # ==================== MODEL INHERITANCE ====================
        print("\n1. MODEL INHERITANCE - CLOTHING ITEM")
        clothing_item = {
            "name": "Cotton T-Shirt",
            "description": "Comfortable cotton t-shirt",
            "price": 19.99,
            "size": "L",
            "color": "Blue",
            "material": "100% Cotton"
        }
        
        response = await client.post(f"{BASE_URL}/clothing/", json=clothing_item)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        
        print("\nMODEL INHERITANCE - ELECTRONIC ITEM")
        electronic_item = {
            "name": "Smartphone",
            "description": "Latest model smartphone",
            "price": 899.99,
            "brand": "TechBrand",
            "model_number": "TB-2023X",
            "warranty_years": 2,
            "voltage": 5.0
        }
        
        response = await client.post(f"{BASE_URL}/electronics/", json=electronic_item)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        
        # ==================== DISCRIMINATED UNIONS ====================
        print("\n2. DISCRIMINATED UNIONS")
        
        # Clothing item using discriminated union
        generic_clothing = {
            "item_type": "clothing",
            "item": {
                "name": "Jeans",
                "description": "Denim jeans",
                "price": 49.99,
                "size": "32",
                "color": "Dark Blue",
                "material": "Denim"
            }
        }
        
        response = await client.post(f"{BASE_URL}/generic-items/", json=generic_clothing)
        print(f"\nGeneric Clothing - Status Code: {response.status_code}")
        pprint(response.json())
        
        # Electronic item using discriminated union
        generic_electronic = {
            "item_type": "electronic",
            "item": {
                "name": "Wireless Earbuds",
                "description": "Bluetooth earbuds with noise cancellation",
                "price": 129.99,
                "brand": "AudioTech",
                "model_number": "AT-WE100",
                "warranty_years": 1
            }
        }
        
        response = await client.post(f"{BASE_URL}/generic-items/", json=generic_electronic)
        print(f"\nGeneric Electronic - Status Code: {response.status_code}")
        pprint(response.json())
        
        # Book item using discriminated union
        generic_book = {
            "item_type": "book",
            "item": {
                "name": "Python Programming",
                "description": "A comprehensive guide to Python",
                "price": 39.99,
                "author": "John Smith",
                "isbn": "978-1234567890",
                "pages": 450
            }
        }
        
        response = await client.post(f"{BASE_URL}/generic-items/", json=generic_book)
        print(f"\nGeneric Book - Status Code: {response.status_code}")
        pprint(response.json())
        
        # ==================== NESTED RELATIONSHIPS AND COMPLEX DATA ====================
        print("\n3. NESTED RELATIONSHIPS AND COMPLEX DATA")
        order = {
            "customer": {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "addresses": [
                    {
                        "street": "123 Main St",
                        "city": "Anytown",
                        "state": "CA",
                        "country": "USA",
                        "postal_code": "12345"
                    },
                    {
                        "street": "456 Work Ave",
                        "city": "Businessville",
                        "state": "CA",
                        "country": "USA",
                        "postal_code": "67890"
                    }
                ]
            },
            "items": [
                {
                    "product_id": 101,
                    "name": "Wireless Mouse",
                    "quantity": 2,
                    "unit_price": 24.99
                },
                {
                    "product_id": 102,
                    "name": "USB-C Hub",
                    "quantity": 1,
                    "unit_price": 45.99
                }
            ],
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        response = await client.post(f"{BASE_URL}/orders/", json=order)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        
        # ==================== DYNAMIC REQUEST BODIES ====================
        print("\n4. DYNAMIC REQUEST BODIES")
        dynamic_config = {
            "theme": "dark",
            "notifications": {
                "email": True,
                "sms": False,
                "push": True
            },
            "display": {
                "sidebar": "left",
                "font_size": 14,
                "show_avatars": True
            },
            "api_keys": [
                "ak_123456789",
                "ak_987654321"
            ]
        }
        
        response = await client.post(f"{BASE_URL}/dynamic-config/", json=dynamic_config)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        
        # ==================== DEPENDENCY INJECTION WITH REQUEST BODIES ====================
        print("\n5. DEPENDENCY INJECTION WITH REQUEST BODIES")
        validated_item = {
            "name": "Validated Item",
            "description": "This item is validated by a dependency",
            "price": 29.99
        }
        
        response = await client.post(f"{BASE_URL}/validated-items/", json=validated_item)
        print(f"Status Code: {response.status_code}")
        pprint(response.json())
        
        print("\nAll advanced tests completed!")

# Run the test function
if __name__ == "__main__":
    asyncio.run(test_advanced_api_endpoints())
