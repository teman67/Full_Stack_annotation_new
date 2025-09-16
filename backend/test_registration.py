#!/usr/bin/env python3
"""
Test user registration with the new Supabase adapter approach
"""
import requests
import json

def test_user_registration():
    """Test user registration via the API"""
    
    # API endpoint
    url = "http://localhost:8001/api/auth/register"
    
    # Test user data
    user_data = {
        "email": "test.user@example.com",
        "password": "TestPassword123!",
        "name": "Test User"
    }
    
    print("Testing user registration...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(user_data, indent=2)}")
    
    try:
        response = requests.post(url, json=user_data)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print("❌ Registration failed!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get("http://localhost:8001/docs")
        if response.status_code == 200:
            print("✅ API is running and accessible")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

if __name__ == "__main__":
    print("=== User Registration Test ===\n")
    
    # First check if API is running
    if test_api_health():
        print()
        test_user_registration()
    else:
        print("Please make sure the backend server is running on http://localhost:8001")
