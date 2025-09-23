# Document Upload Troubleshooting Script
# This script will help diagnose issues with document upload functionality

import requests
import json
import os
from pprint import pprint

# Configuration
API_BASE_URL = "http://localhost:8000"
EMAIL = "amirhossein.bayani@gmail.com"  # Replace with your actual email
PASSWORD = "14087AhB"        # Replace with your actual password
DEBUG = True  # Set to True to see detailed request/response info

def log_debug(message):
    """Print debug message if DEBUG is True"""
    if DEBUG:
        print(f"[DEBUG] {message}")

def login():
    """Authenticate and get JWT token"""
    login_url = f"{API_BASE_URL}/api/auth/login"
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    log_debug(f"Login request to: {login_url}")
    log_debug(f"Login data: {login_data}")
    
    try:
        response = requests.post(login_url, json=login_data)
        log_debug(f"Login response status: {response.status_code}")
        log_debug(f"Login response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            log_debug(f"Login response data: {json.dumps(data, indent=2)}")
            
            # Check for Supabase token first - this is more likely to work
            token = data.get("supabase_token")
            if not token:
                # Fall back to access_token
                token = data.get("access_token")
                
            if token:
                log_debug(f"Successfully obtained token (first 10 chars): {token[:10]}...")
                return token
            else:
                print(f"ERROR: Login successful but no token returned. Response: {data}")
                return None
        else:
            print(f"ERROR: Login failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"ERROR: Exception during login: {str(e)}")
        return None

def get_api_routes():
    """Get available API routes (if OpenAPI docs are enabled)"""
    docs_url = f"{API_BASE_URL}/openapi.json"
    
    try:
        response = requests.get(docs_url)
        if response.status_code == 200:
            data = response.json()
            paths = data.get("paths", {})
            print("\nAvailable API Routes:")
            for path, methods in paths.items():
                print(f"  {path}")
                for method in methods:
                    print(f"    - {method.upper()}")
            return True
        else:
            print(f"Could not fetch API routes: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Exception fetching API routes: {str(e)}")
        return False

def verify_server_running():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"⚠️ API server returned non-200 status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running or not reachable")
        return False
    except Exception as e:
        print(f"❌ Error checking API server: {str(e)}")
        return False

def get_projects(token):
    """Get list of user's projects"""
    projects_url = f"{API_BASE_URL}/api/projects"
    headers = {"Authorization": f"Bearer {token}"}
    
    log_debug(f"Projects request to: {projects_url}")
    log_debug(f"Headers: {headers}")
    
    try:
        response = requests.get(projects_url, headers=headers)
        log_debug(f"Projects response status: {response.status_code}")
        
        if response.status_code == 200:
            projects = response.json()
            print(f"\nFound {len(projects)} projects:")
            for i, project in enumerate(projects):
                print(f"  {i+1}. ID: {project.get('id')}, Name: {project.get('name')}")
            return projects
        else:
            print(f"ERROR: Failed to get projects with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"ERROR: Exception while getting projects: {str(e)}")
        return []

def create_project(token, name="Test Project", description="Project for testing document upload"):
    """Create a new project if none exists"""
    project_url = f"{API_BASE_URL}/api/projects"
    headers = {"Authorization": f"Bearer {token}"}
    project_data = {
        "name": name,
        "description": description
    }
    
    log_debug(f"Create project request to: {project_url}")
    log_debug(f"Project data: {project_data}")
    
    try:
        response = requests.post(project_url, json=project_data, headers=headers)
        log_debug(f"Create project response status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            project = response.json()
            print(f"✅ Created new project: ID={project.get('id')}, Name={project.get('name')}")
            return project
        else:
            print(f"ERROR: Failed to create project with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"ERROR: Exception while creating project: {str(e)}")
        return None

def create_test_file():
    """Create a simple text file for testing"""
    file_path = "test_document.txt"
    try:
        with open(file_path, "w") as f:
            f.write("This is a test document content for upload testing.\n")
            f.write("This file was created by the document upload troubleshooting script.\n")
        print(f"✅ Created test file: {file_path}")
        return file_path
    except Exception as e:
        print(f"ERROR: Failed to create test file: {str(e)}")
        return None

def upload_document_debug(token, project_id, file_path):
    """Upload document with detailed debugging information"""
    # First, check if the upload endpoint exists
    url_check = f"{API_BASE_URL}/api/documents/project/{project_id}/upload"
    headers = {"Authorization": f"Bearer {token}"}
    
    log_debug(f"Checking upload endpoint: {url_check}")
    log_debug(f"Headers: {headers}")
    
    # Try a HEAD request first to check if the endpoint exists
    try:
        head_response = requests.head(url_check, headers=headers)
        log_debug(f"HEAD response status: {head_response.status_code}")
        log_debug(f"HEAD response headers: {dict(head_response.headers)}")
        
        # Proceed with the actual upload
        upload_url = f"{API_BASE_URL}/api/documents/project/{project_id}/upload"
        
        # Prepare the multipart form data
        with open(file_path, 'rb') as f:
            file_content = f.read()
            
        files = {
            'file': (os.path.basename(file_path), file_content, 'text/plain')
        }
        
        form_data = {
            'name': 'Test Document',
            'description': 'This is a test document uploaded for troubleshooting'
        }
        
        log_debug(f"Upload request to: {upload_url}")
        log_debug(f"Files: {files.keys()}")
        log_debug(f"Form data: {form_data}")
        
        # Make the upload request
        response = requests.post(
            upload_url,
            headers=headers,
            files=files,
            data=form_data
        )
        
        log_debug(f"Upload response status: {response.status_code}")
        log_debug(f"Upload response headers: {dict(response.headers)}")
        
        if response.status_code in [200, 201]:
            print("✅ Document uploaded successfully!")
            try:
                result = response.json()
                print(f"Document ID: {result.get('id')}")
                print(f"Document name: {result.get('name')}")
                return result
            except:
                print(f"Could not parse JSON response: {response.text[:100]}")
                return {"success": True, "response": response.text[:100]}
        else:
            print(f"❌ Upload failed with status code: {response.status_code}")
            print(f"Error response: {response.text}")
            
            # Provide troubleshooting guidance
            if response.status_code == 404:
                print("\n📋 TROUBLESHOOTING TIPS FOR 404 ERROR:")
                print("1. Verify the API server is running (we already checked)")
                print("2. Check if the URL is correct - should be /api/documents/project/{project_id}/upload")
                print("3. Verify project_id exists in the database")
                print("4. Check FastAPI route registration in backend/main.py")
                print("5. Make sure the auth token is valid and not expired")
                print("6. Check if you need to use 'documents_supabase' router in main.py")
            elif response.status_code == 401:
                print("\n📋 TROUBLESHOOTING TIPS FOR 401 ERROR:")
                print("1. Your authentication token may be invalid or expired")
                print("2. Try logging in again to get a fresh token")
            
            return {"success": False, "status_code": response.status_code, "error": response.text}
    except Exception as e:
        print(f"❌ ERROR: Exception during document upload: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Main execution function"""
    print("\n====== Document Upload Troubleshooting ======\n")
    
    # Step 1: Check if server is running
    if not verify_server_running():
        print("\n❌ Cannot proceed: API server is not running")
        return
    
    # Step 2: Try to get API routes (if OpenAPI is enabled)
    get_api_routes()
    
    # Step 3: Login to get auth token
    token = login()
    if not token:
        print("\n❌ Cannot proceed: Authentication failed")
        return
    
    # Step 4: Get projects or create one if needed
    projects = get_projects(token)
    project_id = None
    
    if projects and len(projects) > 0:
        project_id = projects[0].get('id')
        print(f"\nUsing existing project with ID: {project_id}")
    else:
        print("\nNo projects found. Creating a new project...")
        new_project = create_project(token)
        if new_project:
            project_id = new_project.get('id')
        else:
            print("\n❌ Cannot proceed: Failed to create a project")
            return
    
    # Step 5: Create a test file
    file_path = create_test_file()
    if not file_path:
        print("\n❌ Cannot proceed: Failed to create test file")
        return
    
    # Step 6: Upload document
    print("\nAttempting to upload document...")
    result = upload_document_debug(token, project_id, file_path)
    
    # Step 7: Cleanup
    try:
        os.remove(file_path)
        print(f"\nCleaned up test file: {file_path}")
    except Exception as e:
        print(f"\nFailed to clean up test file: {str(e)}")
    
    # Final report
    print("\n====== Troubleshooting Summary ======")
    if result and result.get('success', False):
        print("✅ Document upload successful!")
    else:
        print("❌ Document upload failed.")
        print("\nCheck backend/app/api/documents_supabase.py to verify the upload endpoint is properly defined.")
        print("Also verify that backend/main.py correctly includes the document router.")

if __name__ == "__main__":
    main()