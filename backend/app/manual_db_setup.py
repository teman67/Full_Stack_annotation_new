"""
Manual Database Setup Script
Creates necessary tables using direct SQL through Supabase admin
"""
from app.core.database_supabase import admin_supabase
import json

def create_tables_manually():
    """Create tables manually using Supabase admin client"""
    print("=== MANUAL DATABASE SETUP ===")
    
    if not admin_supabase:
        print("❌ Admin client not available")
        return False
    
    try:
        # Create projects table
        print("Creating projects table...")
        projects_sql = """
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            owner_id TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );
        """
        
        # Create documents table  
        print("Creating documents table...")
        documents_sql = """
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            project_id INTEGER NOT NULL,
            uploaded_by TEXT NOT NULL,
            file_path TEXT,
            file_size INTEGER,
            file_type TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );
        """
        
        # Try using PostgREST directly
        try:
            # Use the admin client to execute SQL
            admin_supabase.postgrest.session.post(
                f"{admin_supabase.postgrest.url}/rpc/exec",
                json={"sql": projects_sql},
                headers=admin_supabase.postgrest.session.headers
            )
            print("✅ Projects table creation attempted")
            
            admin_supabase.postgrest.session.post(
                f"{admin_supabase.postgrest.url}/rpc/exec", 
                json={"sql": documents_sql},
                headers=admin_supabase.postgrest.session.headers
            )
            print("✅ Documents table creation attempted")
            
        except Exception as direct_error:
            print(f"Direct SQL execution failed: {direct_error}")
            print("Try creating tables manually in Supabase dashboard")
            
            print("\n=== MANUAL SETUP INSTRUCTIONS ===")
            print("Go to your Supabase dashboard > SQL Editor and run:")
            print("\n1. Projects table:")
            print(projects_sql)
            print("\n2. Documents table:")
            print(documents_sql)
            
    except Exception as e:
        print(f"Setup error: {e}")
        return False
    
    return True

def insert_sample_data():
    """Insert sample project data"""
    print("\n=== INSERTING SAMPLE DATA ===")
    
    try:
        # Insert sample project
        project_data = {
            "id": 1,
            "name": "Sample Project",
            "description": "Auto-created project for testing",
            "owner_id": "5adb01e4-e12a-4b90-8830-7ce4e0ed69d8"
        }
        
        # Try direct insertion
        response = admin_supabase.table('projects').insert(project_data).execute()
        print(f"✅ Sample project inserted: {response.data}")
        return True
        
    except Exception as e:
        print(f"Sample data insertion failed: {e}")
        print("You can insert manually in Supabase dashboard:")
        print("INSERT INTO projects (id, name, description, owner_id) VALUES")
        print("(1, 'Sample Project', 'Auto-created project', '5adb01e4-e12a-4b90-8830-7ce4e0ed69d8');")
        return False

if __name__ == "__main__":
    create_tables_manually()
    insert_sample_data()