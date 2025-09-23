import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Service key has higher privileges

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("Error: Missing Supabase credentials. Make sure SUPABASE_URL and SUPABASE_SERVICE_KEY are set in your .env file")
    exit(1)

# Setup headers for API requests
headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

def create_storage_bucket():
    """Create a 'documents' storage bucket if it doesn't exist"""
    print("\n=== Creating 'documents' storage bucket ===")
    
    # Check if bucket exists
    response = requests.get(
        f"{SUPABASE_URL}/storage/v1/bucket/documents",
        headers=headers
    )
    
    if response.status_code == 200:
        print("Storage bucket 'documents' already exists")
        return
    
    # Create bucket if it doesn't exist
    data = {
        "id": "documents",
        "name": "documents",
        "public": False,
        "file_size_limit": 10485760,  # 10MB limit
        "allowed_mime_types": ["application/pdf", "text/plain", "text/csv"]
    }
    
    response = requests.post(
        f"{SUPABASE_URL}/storage/v1/bucket",
        headers=headers,
        data=json.dumps(data)
    )
    
    if response.status_code == 200:
        print("Successfully created 'documents' storage bucket")
    else:
        print(f"Error creating storage bucket: {response.status_code}")
        print(response.text)

def create_storage_policies():
    """Create RLS policies for the documents bucket"""
    print("\n=== Creating storage policies for 'documents' bucket ===")
    
    # Create policy for users to upload their own documents
    upload_policy = {
        "name": "Allow authenticated users to upload",
        "definition": "((bucket_id = 'documents'::text) AND (auth.role() = 'authenticated'::text))"
    }
    
    response = requests.post(
        f"{SUPABASE_URL}/storage/v1/bucket/documents/policies",
        headers=headers,
        data=json.dumps(upload_policy)
    )
    
    if response.status_code == 200:
        print("Successfully created upload policy")
    elif response.status_code == 409:
        print("Upload policy already exists")
    else:
        print(f"Error creating upload policy: {response.status_code}")
        print(response.text)
    
    # Create policy for users to read their own documents
    download_policy = {
        "name": "Allow authenticated users to download",
        "definition": "((bucket_id = 'documents'::text) AND (auth.role() = 'authenticated'::text))"
    }
    
    response = requests.post(
        f"{SUPABASE_URL}/storage/v1/bucket/documents/policies",
        headers=headers,
        data=json.dumps(download_policy)
    )
    
    if response.status_code == 200:
        print("Successfully created download policy")
    elif response.status_code == 409:
        print("Download policy already exists")
    else:
        print(f"Error creating download policy: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("Setting up Supabase storage...")
    create_storage_bucket()
    create_storage_policies()
    print("\nSetup complete!")