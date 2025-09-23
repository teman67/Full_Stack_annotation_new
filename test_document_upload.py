"""
Simple test script for uploading documents to the API
"""
import requests
import json
import os

# Configuration
API_BASE_URL = "http://localhost:8000/api"
EMAIL = "your-email@example.com"  # Replace with your actual email
PASSWORD = "your-password"        # Replace with your actual password

def login():
    """Get authentication token"""
    login_url = f"{API_BASE_URL}/auth/login"
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    response = requests.post(login_url, json=login_data)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"Login successful! Token: {token[:10]}...")
        return token
    else:
        print(f"Login failed with status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def get_projects(token):
    """Get list of available projects"""
    projects_url = f"{API_BASE_URL}/projects"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(projects_url, headers=headers)
    
    if response.status_code == 200:
        projects = response.json()
        print(f"Found {len(projects)} projects:")
        for project in projects:
            print(f"  ID: {project.get('id')}, Name: {project.get('name')}")
        return projects
    else:
        print(f"Failed to get projects with status code: {response.status_code}")
        print(f"Response: {response.text}")
        return []

def create_test_file():
    """Create a simple test file"""
    file_path = "test_document.txt"
    with open(file_path, "w") as f:
        f.write("This is a test document content.")
    return file_path

def upload_document(token, project_id, file_path):
    """Upload document to project"""
    upload_url = f"{API_BASE_URL}/documents/project/{project_id}/upload"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Prepare multipart form data
    files = {
        "file": (os.path.basename(file_path), open(file_path, "rb"), "text/plain")
    }
    data = {
        "name": "Test Document",
        "description": "This is a test document uploaded via Python"
    }
    
    print(f"Uploading document to URL: {upload_url}")
    print(f"Headers: {headers}")
    print(f"Files: {files}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(
            upload_url,
            headers=headers,
            files=files,
            data=data
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("Document uploaded successfully!")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.json()
        else:
            print(f"Upload failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error during upload: {str(e)}")
        return None

def main():
    """Main execution function"""
    # Login to get token
    token = login()
    if not token:
        print("Cannot continue without authentication token.")
        return
    
    # Get list of projects
    projects = get_projects(token)
    if not projects:
        print("No projects found. Please create a project first.")
        return
    
    # Use the first project ID or specify a particular one
    project_id = projects[0].get('id')
    print(f"Using project ID: {project_id}")
    
    # Create test file
    file_path = create_test_file()
    print(f"Created test file: {file_path}")
    
    # Upload document
    result = upload_document(token, project_id, file_path)
    
    # Clean up
    os.remove(file_path)
    print(f"Deleted test file: {file_path}")

if __name__ == "__main__":
    main()