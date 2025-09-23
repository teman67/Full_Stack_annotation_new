"""
Minimal JWT Authentication Test Script
This script directly tests the JWT token generation and verification
"""
import requests
import os
import json
import base64
import sys
import time

# Configuration
API_URL = "http://localhost:8000"
EMAIL = "amirhossein.bayani@gmail.com"
PASSWORD = "14087AhB"

def decode_jwt(token):
    """Decode JWT token without verification to inspect its content"""
    parts = token.split('.')
    if len(parts) != 3:
        return "Invalid token format"
    
    # Padding adjustment for base64url decoding
    padding = '=' * (4 - len(parts[1]) % 4)
    payload_bytes = base64.urlsafe_b64decode(parts[1] + padding)
    
    try:
        payload = json.loads(payload_bytes)
        return payload
    except:
        return "Invalid payload format"

def login():
    """Perform login and get token"""
    print(f"Logging in with email: {EMAIL}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json={"email": EMAIL, "password": PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            
            if token:
                print("✅ Successfully logged in and received token")
                payload = decode_jwt(token)
                print(f"Token payload: {json.dumps(payload, indent=2)}")
                return token
            else:
                print("❌ No token in response")
                return None
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception during login: {str(e)}")
        return None

def test_api(token):
    """Test API access with token"""
    print(f"\nTesting API access with token")
    
    # Test endpoints
    endpoints = [
        "/api/projects",
        "/api/auth/me"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting endpoint: {endpoint}")
            response = requests.get(
                f"{API_URL}{endpoint}", 
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Success!")
                try:
                    print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
                except:
                    print(f"Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def main():
    """Main test function"""
    print("=== JWT Authentication Test ===\n")
    
    # Step 1: Login to get token
    token = login()
    if not token:
        print("\n❌ Authentication test failed: Could not obtain token")
        sys.exit(1)
    
    # Step 2: Test API access
    test_api(token)

if __name__ == "__main__":
    main()