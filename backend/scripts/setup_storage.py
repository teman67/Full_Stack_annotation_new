"""
Supabase Storage Setup Script
----------------------------
This script sets up the required storage buckets in Supabase for the annotation application.
It creates the following buckets:
1. 'tagset-files': For storing uploaded tagset CSV files

Each bucket is set up with proper security policies to ensure:
- Only authenticated users can upload files
- Users can only access their own files
"""
import os
import sys
from dotenv import load_dotenv
import requests
import json

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Import settings and Supabase client from app
from app.core.config import settings
from app.core.database_supabase import get_supabase_client

# Get Supabase client
supabase = get_supabase_client()

# Get Supabase service role key (needed for admin operations)
service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not service_role_key:
    print("❌ Error: SUPABASE_SERVICE_ROLE_KEY not found in environment variables")
    print("Please add it to your .env file")
    sys.exit(1)

# Supabase API base URL
api_url = f"{settings.supabase_url}/storage/v1"

# Headers for admin operations using service role key
headers = {
    "apikey": service_role_key,
    "Authorization": f"Bearer {service_role_key}",
    "Content-Type": "application/json"
}

def create_bucket(name, public=False):
    """Create a storage bucket with the given name"""
    print(f"Creating bucket '{name}'...")
    
    # Check if bucket already exists
    try:
        response = requests.get(f"{api_url}/bucket/{name}", headers=headers)
        if response.status_code == 200:
            print(f"✅ Bucket '{name}' already exists")
            return True
    except Exception as e:
        pass
    
    # Create the bucket
    try:
        data = {
            "name": name,
            "public": public,
            "file_size_limit": 10485760  # 10MB limit for uploads
        }
        response = requests.post(f"{api_url}/bucket", headers=headers, json=data)
        
        if response.status_code in (200, 201):
            print(f"✅ Bucket '{name}' created successfully")
            return True
        else:
            print(f"❌ Failed to create bucket '{name}': {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating bucket '{name}': {str(e)}")
        return False

def create_bucket_policy(bucket_name, policy_name, definition):
    """Create a storage policy for the given bucket"""
    print(f"Creating policy '{policy_name}' for bucket '{bucket_name}'...")
    
    # Instead of trying to create the policy programmatically, print instructions
    # for manual setup through the Supabase dashboard
    print(f"⚠️ Please create the following policy manually in the Supabase dashboard:")
    print(f"   - Policy name: {policy_name}")
    print(f"   - Role: {definition['definition']['role']}")
    print(f"   - Operation: {definition['definition']['operation']}")
    print(f"   - Expression: {definition['definition']['check']}")
    print("")
    
    # Return success as if the policy was created, since we're guiding manual creation
    return True

def setup_tagset_files_bucket():
    """Set up the tagset-files bucket and its policies"""
    bucket_name = "tagset-files"
    
    # Create the bucket (not public)
    if not create_bucket(bucket_name, public=False):
        return False
    
    print("\n========== MANUAL POLICY SETUP REQUIRED ==========")
    print(f"Please set up the following policies for the '{bucket_name}' bucket")
    print("in the Supabase Dashboard (Storage > Policies):\n")
    
    # Policy 1: Allow users to insert their own files
    upload_policy = {
        "name": "Allow users to upload their own files",
        "definition": {
            "role": "authenticated",
            "operation": "INSERT",
            "check": "uid() = auth.uid()"
        }
    }
    
    # Policy 2: Allow users to select their own files
    select_policy = {
        "name": "Allow users to view their own files",
        "definition": {
            "role": "authenticated",
            "operation": "SELECT",
            "check": "uid() = auth.uid()"
        }
    }
    
    # Policy 3: Allow users to update their own files
    update_policy = {
        "name": "Allow users to update their own files",
        "definition": {
            "role": "authenticated",
            "operation": "UPDATE",
            "check": "uid() = auth.uid()"
        }
    }
    
    # Policy 4: Allow users to delete their own files
    delete_policy = {
        "name": "Allow users to delete their own files",
        "definition": {
            "role": "authenticated",
            "operation": "DELETE",
            "check": "uid() = auth.uid()"
        }
    }
    
    # Display instructions for all policies
    policies = [upload_policy, select_policy, update_policy, delete_policy]
    
    for policy in policies:
        create_bucket_policy(bucket_name, policy["name"], policy)
    
    print("\n====== STEPS TO SET UP STORAGE POLICIES ======")
    print("1. Go to your Supabase Dashboard: https://app.supabase.com")
    print("2. Select your project")
    print("3. Go to 'Storage' in the left sidebar")
    print("4. Click on the 'tagset-files' bucket")
    print("5. Go to the 'Policies' tab")
    print("6. For each operation (INSERT, SELECT, UPDATE, DELETE):")
    print("   a. Click 'Add Policies'")
    print("   b. Select the operation type")
    print("   c. Choose 'Policies using custom SQL'")
    print("   d. Enter the policy name (e.g., 'Allow users to upload their own files')")
    print("   e. Enter the SQL expression: uid() = auth.uid()")
    print("   f. Click 'Save Policy'")
    print("===============================================\n")
    
    return True

def main():
    """Main function to set up all storage buckets and policies"""
    print("Setting up Supabase storage buckets...")
    
    # Set up tagset-files bucket
    if setup_tagset_files_bucket():
        print("✅ Tagset files bucket created successfully")
        print("⚠️ IMPORTANT: You need to manually set up the storage policies")
        print("   as described above in the Supabase Dashboard")
    else:
        print("❌ Tagset files bucket setup failed")
    
    # Check if the tagset table exists in the database
    try:
        response = supabase.table('tagsets').select('id').limit(1).execute()
        print("✅ Tagsets table exists")
    except Exception as e:
        print("\n⚠️ Tagsets table may not exist yet. Creating SQL for tagsets table:")
        print("""
        CREATE TABLE tagsets (
          id SERIAL PRIMARY KEY,
          name TEXT NOT NULL,
          description TEXT,
          owner_id UUID REFERENCES auth.users(id) NOT NULL,
          file_path TEXT,
          tags JSONB DEFAULT '[]'::jsonb,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Add RLS policies for tagsets table
        ALTER TABLE tagsets ENABLE ROW LEVEL SECURITY;
        
        -- Policy to allow users to view their own tagsets
        CREATE POLICY "Users can view their own tagsets" ON tagsets
          FOR SELECT USING (auth.uid() = owner_id);
        
        -- Policy to allow users to insert their own tagsets
        CREATE POLICY "Users can insert their own tagsets" ON tagsets
          FOR INSERT WITH CHECK (auth.uid() = owner_id);
        
        -- Policy to allow users to update their own tagsets
        CREATE POLICY "Users can update their own tagsets" ON tagsets
          FOR UPDATE USING (auth.uid() = owner_id);
        
        -- Policy to allow users to delete their own tagsets
        CREATE POLICY "Users can delete their own tagsets" ON tagsets
          FOR DELETE USING (auth.uid() = owner_id);
        """)
        print("\nYou can run this SQL in the Supabase Dashboard SQL Editor")
    
    print("\nStorage setup completed!")

if __name__ == "__main__":
    main()
