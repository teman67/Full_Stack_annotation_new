# Direct API Testing Script - Using Supabase Key
# This script bypasses the custom JWT and uses Supabase's token directly

import requests
import json
import os
from pprint import pprint
import base64

# Configuration
API_BASE_URL = "http://localhost:8000"
SUPABASE_URL = "https://toyattjeguduxpiwpzrl.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRveWF0dGplZ3VkdXhwaXdwenJsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc0MDE4MjksImV4cCI6MjA3Mjk3NzgyOX0.HXS_mPVnMr1hPUAzMrm0nDbnpSiWEPTWEDNxfwFChoE"

EMAIL = "amirhossein.bayani@gmail.com"
PASSWORD = "14087AhB"
DEBUG = True

def log_debug(message):
    """Print debug message if DEBUG is True"""
    if DEBUG:
        print(f"[DEBUG] {message}")

def login_with_supabase():
    """Login directly with Supabase"""
    login_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    log_debug(f"Supabase login request to: {login_url}")
    
    try:
        response = requests.post(login_url, json=login_data, headers=headers)
        log_debug(f"Supabase login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_debug(f"Supabase login response: {json.dumps(data, indent=2)[:200]}...")
            
            # Get the access token from Supabase
            access_token = data.get("access_token")
            if access_token:
                log_debug(f"Successfully obtained Supabase token (first 10 chars): {access_token[:10]}...")
                return access_token
            else:
                print(f"ERROR: Login successful but no token returned")
                return None
        else:
            print(f"ERROR: Supabase login failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"ERROR: Exception during Supabase login: {str(e)}")
        return None

def login_with_backend():
    """Login using the backend API"""
    login_url = f"{API_BASE_URL}/api/auth/login"
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    log_debug(f"Backend login request to: {login_url}")
    
    try:
        response = requests.post(login_url, json=login_data)
        log_debug(f"Backend login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_debug(f"Backend login response: {json.dumps(data, indent=2)}")
            
            # Get the JWT token and/or the Supabase token
            jwt_token = data.get("access_token")
            supabase_token = data.get("supabase_token")
            
            # Return both tokens for testing
            return {
                "jwt": jwt_token,
                "supabase": supabase_token
            }
        else:
            print(f"ERROR: Backend login failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"ERROR: Exception during backend login: {str(e)}")
        return None

def decode_jwt(token):
    """Decode and print JWT token parts without verification"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return "Not a valid JWT token format"
        
        # Decode header and payload
        header_bytes = base64.urlsafe_b64decode(parts[0] + '=' * (4 - len(parts[0]) % 4))
        payload_bytes = base64.urlsafe_b64decode(parts[1] + '=' * (4 - len(parts[1]) % 4))
        
        header = json.loads(header_bytes)
        payload = json.loads(payload_bytes)
        
        return {
            "header": header,
            "payload": payload,
            "signature": parts[2][:10] + "..." # Just show part of the signature
        }
    except Exception as e:
        return f"Error decoding JWT: {str(e)}"

def get_projects(token):
    """Test getting projects with various token configurations"""
    projects_url = f"{API_BASE_URL}/api/projects"
    
    # Test with different authorization header formats
    auth_headers = [
        {"Authorization": f"Bearer {token}"},
        {"apikey": token, "Authorization": f"Bearer {token}"}
    ]
    
    for i, headers in enumerate(auth_headers):
        log_debug(f"\nTest #{i+1} - Projects request with headers: {headers}")
        
        try:
            response = requests.get(projects_url, headers=headers)
            log_debug(f"Projects response status: {response.status_code}")
            
            if response.status_code == 200:
                projects = response.json()
                print(f"\nSuccess! Found {len(projects)} projects:")
                for proj in projects:
                    print(f"  ID: {proj.get('id')}, Name: {proj.get('name')}")
                return projects
            else:
                log_debug(f"Failed with status code: {response.status_code}")
                log_debug(f"Response: {response.text}")
        except Exception as e:
            log_debug(f"Exception: {str(e)}")
    
    print("\nAll attempts to get projects failed")
    return []

def main():
    """Main execution flow"""
    print("\n====== JWT Authentication Troubleshooting ======\n")
    
    # Step 1: Get token directly from Supabase
    print("Testing direct Supabase authentication...")
    supabase_token = login_with_supabase()
    
    if not supabase_token:
        print("❌ Could not authenticate with Supabase directly")
    else:
        print("✅ Supabase authentication successful")
        
        # Decode and analyze the token
        print("\nAnalyzing Supabase token:")
        token_data = decode_jwt(supabase_token)
        pprint(token_data)
        
        # Try to use Supabase token directly
        print("\nTesting API access with Supabase token...")
        projects = get_projects(supabase_token)
    
    # Step 2: Get token from backend
    print("\nTesting backend authentication...")
    backend_tokens = login_with_backend()
    
    if not backend_tokens:
        print("❌ Could not authenticate with backend")
    else:
        print("✅ Backend authentication successful")
        
        # Analyze JWT token
        if backend_tokens.get("jwt"):
            print("\nAnalyzing JWT token:")
            jwt_data = decode_jwt(backend_tokens["jwt"])
            pprint(jwt_data)
            
            # Try to use JWT token
            print("\nTesting API access with JWT token...")
            projects = get_projects(backend_tokens["jwt"])
        
        # Analyze Supabase token if present
        if backend_tokens.get("supabase"):
            print("\nAnalyzing Supabase token from backend:")
            supabase_data = decode_jwt(backend_tokens["supabase"])
            pprint(supabase_data)
            
            # Try to use Supabase token
            print("\nTesting API access with Supabase token from backend...")
            projects = get_projects(backend_tokens["supabase"])
    
    print("\n====== Troubleshooting Summary ======")
    print("If all authentication attempts failed, the issue might be:")
    print("1. The server's SECRET_KEY is not updated - restart the server")
    print("2. The JWT verification logic is incorrect")
    print("3. The FastAPI dependencies are not properly handling the tokens")
    print("\nCheck the backend/app/dependencies_supabase.py file to see how tokens are verified.")

if __name__ == "__main__":
    main()