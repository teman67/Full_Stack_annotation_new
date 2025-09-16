#!/usr/bin/env python3
"""
Simple test for Supabase registration
"""
import requests
import json

def test_registration_simple():
    """Simple registration test"""
    url = "http://localhost:8001/api/auth/register"
    
    data = {
        "email": "testuser123@example.com", 
        "password": "TestPassword123!",
        "name": "Test User"
    }
    
    print(f"Testing registration at: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
        else:
            print("❌ Registration failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_registration_simple()
