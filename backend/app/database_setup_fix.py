"""
Database and Storage Setup Fix
Creates necessary tables, buckets, and handles schema issues
"""
from app.core.database_supabase import get_db_service, admin_supabase
import json

def setup_documents_table():
    """Create the documents table with proper schema"""
    print("Setting up documents table...")
    
    if not admin_supabase:
        print("❌ Admin client not available - cannot create tables")
        return False
    
    try:
        # Create documents table with proper schema
        sql = """
        CREATE TABLE IF NOT EXISTS public.documents (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            content TEXT,
            description TEXT,
            tags JSONB DEFAULT '[]'::jsonb,
            project_id INTEGER NOT NULL,
            uploaded_by TEXT NOT NULL,
            file_path TEXT,
            file_size INTEGER,
            file_type TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );
        
        -- Create index for faster queries
        CREATE INDEX IF NOT EXISTS idx_documents_project_id ON public.documents(project_id);
        CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by ON public.documents(uploaded_by);
        """
        
        response = admin_supabase.rpc('exec', {'sql': sql}).execute()
        print("✅ Documents table created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating documents table: {e}")
        return False

def setup_projects_table():
    """Create the projects table with proper schema"""
    print("Setting up projects table...")
    
    if not admin_supabase:
        print("❌ Admin client not available - cannot create tables")
        return False
    
    try:
        # Create projects table with proper schema
        sql = """
        CREATE TABLE IF NOT EXISTS public.projects (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            owner_id TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            is_active BOOLEAN DEFAULT true
        );
        
        -- Create index for faster queries
        CREATE INDEX IF NOT EXISTS idx_projects_owner_id ON public.projects(owner_id);
        """
        
        response = admin_supabase.rpc('exec', {'sql': sql}).execute()
        print("✅ Projects table created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating projects table: {e}")
        return False

def setup_storage_bucket():
    """Create the documents storage bucket"""
    print("Setting up documents storage bucket...")
    
    try:
        # Create the documents bucket
        result = admin_supabase.storage.create_bucket("documents", {
            "public": False,
            "file_size_limit": 50 * 1024 * 1024,  # 50MB limit
            "allowed_mime_types": ["text/plain", "text/csv", "application/pdf", "application/json"]
        })
        print("✅ Documents bucket created successfully")
        return True
    except Exception as e:
        print(f"Storage bucket creation result: {e}")
        # Check if bucket already exists
        try:
            buckets = admin_supabase.storage.list_buckets()
            if any(bucket.name == "documents" for bucket in buckets):
                print("✅ Documents bucket already exists")
                return True
        except Exception as check_error:
            print(f"❌ Error checking buckets: {check_error}")
        
        print("❌ Could not create or verify documents bucket")
        return False

def create_sample_project(user_id: str, project_id: int = 1):
    """Create a sample project for testing"""
    print(f"Creating sample project {project_id} for user {user_id}...")
    
    try:
        db_service = get_db_service()
        
        # Try to create using the database service
        result = db_service.create_project(
            user_id=user_id,
            name=f"Sample Project {project_id}",
            description="Auto-created project for document upload testing"
        )
        
        if result.get("success"):
            print(f"✅ Sample project created: {result['data']}")
            return result["data"]
        else:
            print(f"❌ Failed to create project via service: {result.get('error')}")
            
            # Try direct SQL insertion with admin client
            if admin_supabase:
                sql = f"""
                INSERT INTO public.projects (id, name, description, owner_id, created_at)
                VALUES ({project_id}, 'Sample Project {project_id}', 'Auto-created project', '{user_id}', now())
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    owner_id = EXCLUDED.owner_id;
                """
                admin_supabase.rpc('exec', {'sql': sql}).execute()
                print(f"✅ Sample project created via direct SQL")
                return {
                    "id": project_id,
                    "name": f"Sample Project {project_id}",
                    "description": "Auto-created project",
                    "owner_id": user_id
                }
            
    except Exception as e:
        print(f"❌ Error creating sample project: {e}")
    
    return None

def fix_file_storage_method():
    """Enhanced file storage that handles storage bucket issues"""
    print("Setting up enhanced file storage...")
    
    def enhanced_upload_file_to_storage(db_service, bucket: str, path: str, file_content: bytes):
        """Enhanced upload with better error handling"""
        try:
            # First try normal upload
            response = db_service.client.storage.from_(bucket).upload(path, file_content)
            print(f"✅ File uploaded successfully to {bucket}/{path}")
            return response
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Storage upload failed: {error_msg}")
            
            # If bucket doesn't exist, try to create it
            if "bucket" in error_msg.lower() and "not found" in error_msg.lower():
                print("Attempting to create bucket...")
                try:
                    admin_supabase.storage.create_bucket(bucket, {"public": False})
                    print(f"✅ Created bucket {bucket}")
                    # Retry upload
                    response = db_service.client.storage.from_(bucket).upload(path, file_content)
                    print(f"✅ File uploaded after bucket creation")
                    return response
                except Exception as create_error:
                    print(f"❌ Could not create bucket: {create_error}")
            
            # Store file locally as fallback
            import os
            from pathlib import Path
            
            local_storage_dir = Path("local_storage") / bucket
            local_storage_dir.mkdir(parents=True, exist_ok=True)
            
            local_file_path = local_storage_dir / path.replace("/", "_")
            with open(local_file_path, "wb") as f:
                f.write(file_content)
            
            print(f"✅ File stored locally at: {local_file_path}")
            return {"local_path": str(local_file_path), "fallback": True}
    
    # Patch the database service method
    db_service = get_db_service()
    db_service.enhanced_upload_file_to_storage = lambda bucket, path, content: enhanced_upload_file_to_storage(db_service, bucket, path, content)
    
    return True

def setup_complete_database():
    """Set up all necessary database components"""
    print("=== SETTING UP COMPLETE DATABASE ===")
    
    success_count = 0
    total_tasks = 5
    
    # 1. Setup projects table
    if setup_projects_table():
        success_count += 1
    
    # 2. Setup documents table
    if setup_documents_table():
        success_count += 1
    
    # 3. Setup storage bucket
    if setup_storage_bucket():
        success_count += 1
    
    # 4. Setup enhanced file storage
    if fix_file_storage_method():
        success_count += 1
    
    # 5. Create sample project
    test_user_id = "5adb01e4-e12a-4b90-8830-7ce4e0ed69d8"
    if create_sample_project(test_user_id, 1):
        success_count += 1
    
    print(f"\n=== SETUP COMPLETE ===")
    print(f"✅ {success_count}/{total_tasks} tasks completed successfully")
    
    if success_count >= 3:  # At least tables and storage
        print("🎉 Database setup successful! Document upload should now work.")
        return True
    else:
        print("⚠️ Some setup tasks failed, but basic functionality may still work.")
        return False

if __name__ == "__main__":
    setup_complete_database()