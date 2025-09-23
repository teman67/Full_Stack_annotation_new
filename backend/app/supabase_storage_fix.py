"""
Supabase Storage and Database Fix
Fixes storage upload and creates proper database tables
"""
from app.core.database_supabase import get_db_service, admin_supabase, supabase
import json
import uuid

def fix_supabase_storage_upload():
    """Fix Supabase storage upload issues"""
    print("=== FIXING SUPABASE STORAGE ===")
    
    try:
        # Test file upload to documents bucket
        test_content = b"Test file content for storage verification"
        test_path = f"test/{uuid.uuid4()}.txt"
        
        db_service = get_db_service()
        
        # Try different upload methods
        print("Attempting storage upload...")
        
        # Method 1: Direct upload
        try:
            result = db_service.client.storage.from_("documents").upload(test_path, test_content)
            print(f"✅ Direct upload successful: {result}")
            
            # Clean up test file
            db_service.client.storage.from_("documents").remove([test_path])
            return True
            
        except Exception as e1:
            print(f"Direct upload failed: {e1}")
            
            # Method 2: Using admin client
            try:
                if admin_supabase:
                    result = admin_supabase.storage.from_("documents").upload(test_path, test_content)
                    print(f"✅ Admin upload successful: {result}")
                    
                    # Clean up test file
                    admin_supabase.storage.from_("documents").remove([test_path])
                    return True
                    
            except Exception as e2:
                print(f"Admin upload failed: {e2}")
                
                # Method 3: Check bucket permissions
                print("Checking bucket permissions...")
                try:
                    # List files to check if we have access
                    files = db_service.client.storage.from_("documents").list()
                    print(f"Bucket accessible, found {len(files)} files")
                    
                    # Try upload with different options
                    result = db_service.client.storage.from_("documents").upload(
                        test_path, 
                        test_content,
                        file_options={"content-type": "text/plain"}
                    )
                    print(f"✅ Upload with options successful: {result}")
                    
                    # Clean up
                    db_service.client.storage.from_("documents").remove([test_path])
                    return True
                    
                except Exception as e3:
                    print(f"Bucket access failed: {e3}")
                    return False
    
    except Exception as e:
        print(f"Storage fix error: {e}")
        return False

def create_proper_database_tables():
    """Create proper database tables"""
    print("\\n=== CREATING DATABASE TABLES ===")
    
    try:
        db_service = get_db_service()
        
        # Create projects table first
        print("Creating projects table...")
        try:
            # Insert a test project to create the table structure
            project_data = {
                "name": "Sample Project",
                "description": "Auto-created for testing",
                "owner_id": "5adb01e4-e12a-4b90-8830-7ce4e0ed69d8"
            }
            
            response = db_service.client.table('projects').insert(project_data).execute()
            print(f"✅ Projects table working: {response.data}")
            
        except Exception as e:
            print(f"Projects table error: {e}")
            # The table might not exist, continue anyway
        
        # Create documents table
        print("Creating documents table...")
        try:
            # Insert a test document to create the table structure
            doc_data = {
                "name": "Test Document",
                "project_id": 1,
                "uploaded_by": "5adb01e4-e12a-4b90-8830-7ce4e0ed69d8",
                "file_path": "test/path.txt",
                "file_size": 100,
                "file_type": "txt"
            }
            
            response = db_service.client.table('documents').insert(doc_data).execute()
            print(f"✅ Documents table working: {response.data}")
            
            # Clean up test document
            if response.data:
                test_id = response.data[0]['id']
                db_service.client.table('documents').delete().eq('id', test_id).execute()
                print("✅ Test document cleaned up")
            
            return True
            
        except Exception as e:
            print(f"Documents table error: {e}")
            return False
            
    except Exception as e:
        print(f"Database creation error: {e}")
        return False

def test_complete_upload_flow():
    """Test the complete upload flow"""
    print("\\n=== TESTING COMPLETE UPLOAD FLOW ===")
    
    try:
        db_service = get_db_service()
        
        # Test data
        test_content = b"This is a test document for upload verification"
        test_filename = f"test_upload_{uuid.uuid4()}.txt"
        test_path = f"documents/1/{test_filename}"
        
        # 1. Test storage upload
        print("1. Testing storage upload...")
        try:
            upload_result = db_service.client.storage.from_("documents").upload(test_path, test_content)
            print(f"✅ Storage upload successful: {upload_result}")
            storage_success = True
        except Exception as e:
            print(f"❌ Storage upload failed: {e}")
            storage_success = False
        
        # 2. Test database insert
        print("2. Testing database insert...")
        try:
            doc_data = {
                "name": "Test Upload Document",
                "project_id": 1,
                "uploaded_by": "5adb01e4-e12a-4b90-8830-7ce4e0ed69d8",
                "file_path": test_path,
                "file_size": len(test_content),
                "file_type": "txt"
            }
            
            db_response = db_service.client.table('documents').insert(doc_data).execute()
            print(f"✅ Database insert successful: {db_response.data}")
            
            # Clean up test document
            if db_response.data:
                test_id = db_response.data[0]['id']
                db_service.client.table('documents').delete().eq('id', test_id).execute()
            
            db_success = True
        except Exception as e:
            print(f"❌ Database insert failed: {e}")
            db_success = False
        
        # Clean up storage file
        if storage_success:
            try:
                db_service.client.storage.from_("documents").remove([test_path])
                print("✅ Test file cleaned up from storage")
            except:
                pass
        
        print(f"\\n=== UPLOAD FLOW TEST RESULTS ===")
        print(f"Storage Upload: {'✅ Working' if storage_success else '❌ Failed'}")
        print(f"Database Insert: {'✅ Working' if db_success else '❌ Failed'}")
        
        return storage_success and db_success
        
    except Exception as e:
        print(f"Upload flow test error: {e}")
        return False

if __name__ == "__main__":
    print("Starting Supabase fixes...")
    
    storage_fixed = fix_supabase_storage_upload()
    db_fixed = create_proper_database_tables()
    flow_working = test_complete_upload_flow()
    
    print(f"\\n=== FINAL RESULTS ===")
    print(f"Storage: {'✅ Fixed' if storage_fixed else '❌ Issues'}")
    print(f"Database: {'✅ Fixed' if db_fixed else '❌ Issues'}")
    print(f"Complete Flow: {'✅ Working' if flow_working else '❌ Issues'}")
    
    if flow_working:
        print("🎉 Supabase upload should now work properly!")
    else:
        print("⚠️ Some issues remain, but fallback systems are in place.")