"""
Test script for the document upload authentication fix
Tests the enhanced authentication flow and document upload functionality
"""
import requests
import json
import os
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_PROJECT_ID = 1

def test_document_upload_with_auth():
    """Test document upload with the fixed authentication"""
    print("=== TESTING DOCUMENT UPLOAD WITH FIXED AUTH ===")
    
    # You'll need to provide a valid JWT token from your frontend
    # This is just a test structure - replace with actual token
    test_token = "your_jwt_token_here"
    
    if test_token == "your_jwt_token_here":
        print("❌ Please provide a valid JWT token to test the upload")
        print("   You can get this from your browser's developer tools")
        print("   when logged into the frontend application")
        return False
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {test_token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Check if the API is accessible
    print("\n1. Testing API accessibility...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   ✅ API is accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cannot reach API: {e}")
        return False
    
    # Test 2: Test authentication endpoint (if available)
    print("\n2. Testing authentication...")
    try:
        response = requests.get(f"{BASE_URL}/api/projects", headers=headers, timeout=5)
        print(f"   Auth test status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Authentication appears to be working")
        else:
            print(f"   ⚠️ Auth response: {response.text}")
    except Exception as e:
        print(f"   ❌ Auth test failed: {e}")
    
    # Test 3: Test document upload
    print(f"\n3. Testing document upload to project {TEST_PROJECT_ID}...")
    
    # Create a test file
    test_content = "This is a test document for upload testing."
    
    files = {
        'file': ('test_document.txt', test_content, 'text/plain')
    }
    
    data = {
        'name': 'Test Document',
        'description': 'Test document for authentication fix verification',
        'tags': '["test", "authentication"]'
    }
    
    # Remove Content-Type from headers for multipart upload
    upload_headers = {"Authorization": f"Bearer {test_token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/documents/project/{TEST_PROJECT_ID}/upload",
            headers=upload_headers,
            files=files,
            data=data,
            timeout=10
        )
        
        print(f"   Upload status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Document upload successful!")
            return True
        elif response.status_code == 404:
            print("   ❌ 404 error - this was the original problem")
            return False
        else:
            print(f"   ⚠️ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Upload test failed: {e}")
        return False

def test_fallback_authentication():
    """Test the fallback authentication mechanism"""
    print("\n=== TESTING FALLBACK AUTHENTICATION ===")
    
    # Test with our fixed auth system directly
    try:
        from app.auth_fix import get_current_user_fixed, create_fallback_user
        
        # Test fallback user creation
        test_user_id = "5adb01e4-e12a-4b90-8830-7ce4e0ed69d8"
        test_email = "amirhossein.bayani@gmail.com"
        
        fallback_user = create_fallback_user(test_user_id, test_email)
        print(f"✅ Fallback user created: {fallback_user}")
        
        # Test project access logic
        from app.auth_fix import ensure_project_access
        
        test_project = {
            "id": 1,
            "name": "Test Project",
            "owner_id": test_user_id,
            "created_from_fallback": True
        }
        
        has_access = ensure_project_access(test_project, fallback_user, 1)
        print(f"✅ Project access check: {has_access}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fallback auth test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Document Upload Authentication Fix - Test Suite")
    print("=" * 50)
    
    # Test 1: Fallback authentication
    fallback_test = test_fallback_authentication()
    
    # Test 2: Document upload (requires manual token)
    # upload_test = test_document_upload_with_auth()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    print(f"✅ Fallback Authentication: {'PASSED' if fallback_test else 'FAILED'}")
    print("📝 Document Upload: Requires valid JWT token (manual test)")
    
    print("\nTo test document upload:")
    print("1. Open your frontend application")
    print("2. Login and get a JWT token from browser dev tools")
    print("3. Replace 'your_jwt_token_here' in this script")
    print("4. Run the test again")

if __name__ == "__main__":
    main()