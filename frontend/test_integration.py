#!/usr/bin/env python3
"""
Test script to verify frontend-backend authentication integration
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_backend_health():
    """Test if backend is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"✅ Backend health check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("\n🔐 Testing Authentication Endpoints...")
    
    # Test registration
    print("\n1. Testing Registration:")
    test_user = {
        "name": "Test User",
        "email": "test@example.com", 
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        print(f"   Registration status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Registration successful")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ⚠️  Registration response: {response.text}")
    except Exception as e:
        print(f"   ❌ Registration failed: {e}")
    
    # Test login
    print("\n2. Testing Login:")
    login_data = {
        "username": "test@example.com",  # OAuth2PasswordRequestForm uses 'username'
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token", 
            data=login_data,  # Form data, not JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"   Login status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"   ✅ Login successful")
            print(f"   Access token received: {token_data.get('access_token', 'Not found')[:20]}...")
            
            # Test authenticated endpoint
            print("\n3. Testing Authenticated Endpoint:")
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            print(f"   /auth/me status: {me_response.status_code}")
            if me_response.status_code == 200:
                print(f"   ✅ User info retrieved successfully")
                user_info = me_response.json()
                print(f"   User: {user_info.get('name')} ({user_info.get('email')})")
            else:
                print(f"   ❌ Failed to get user info: {me_response.text}")
        else:
            print(f"   ❌ Login failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Login test failed: {e}")

def main():
    print("🚀 Frontend-Backend Authentication Integration Test")
    print("=" * 50)
    
    if test_backend_health():
        test_auth_endpoints()
    else:
        print("❌ Backend is not accessible. Please ensure it's running on port 8000.")
    
    print("\n" + "=" * 50)
    print("✅ Integration test completed!")

if __name__ == "__main__":
    main()
