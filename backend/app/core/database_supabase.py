"""
Database configuration using only Supabase client
No SQLAlchemy - pure Supabase approach
"""
from app.core.config import settings
from supabase import create_client, Client
from typing import Dict, List, Optional, Any
import json
import os

# Regular Supabase client setup - this is our primary database interface
supabase: Client = create_client(settings.supabase_url, settings.supabase_anon_key)

# Service role client with admin privileges (used to bypass RLS when needed)
service_role_key = settings.supabase_service_role_key
if service_role_key:
    try:
        admin_supabase: Client = create_client(settings.supabase_url, service_role_key)
        print("✅ Supabase admin client initialized successfully")
    except Exception as e:
        print(f"⚠️ Failed to initialize admin client: {e}")
        admin_supabase = None
else:
    print("⚠️ No SUPABASE_SERVICE_ROLE_KEY found, admin functions will not be available")
    admin_supabase = None

print("✅ Supabase client initialized successfully")
print(f"🔗 Connected to: {settings.supabase_url}")

# Test the connection
try:
    # Simple test to verify connection
    response = supabase.table('users').select('id').limit(1).execute()
    print("✅ Supabase connection test successful")
except Exception as e:
    print(f"⚠️ Supabase connection test info: {e}")
    print("   This is normal if tables don't exist yet")

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return supabase

# For backward compatibility with existing code
def get_db():
    """Database dependency - returns Supabase client"""
    return supabase

# Admin client with service role key for bypassing RLS
def get_admin_db():
    """Returns admin Supabase client with service role key (bypasses RLS)"""
    if not admin_supabase:
        raise Exception("Admin database client not available. Check SUPABASE_SERVICE_ROLE_KEY")
    return admin_supabase

class DatabaseService:
    """
    Database service using Supabase client
    Replaces SQLAlchemy operations with Supabase calls
    """
    
    def __init__(self, client: Client):
        self.client = client
    
    # User operations
    def create_user(self, email: str, password: str, name: str = None) -> Dict:
        """Create a new user with email verification"""
        try:
            # Create auth user with email verification enabled
            auth_response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "email_redirect_to": "http://localhost:3000/auth/verify",  # Redirect after email verification
                    "data": {
                        "name": name
                    }
                }
            })
            
            if auth_response.user:
                # Also create a record in the users table for easier querying
                try:
                    user_record = {
                        "id": str(auth_response.user.id),
                        "email": email,
                        "name": name or email.split("@")[0],
                        "is_active": True,
                        "is_admin": False,
                        "email_verified": auth_response.user.email_confirmed_at is not None,
                        "created_at": auth_response.user.created_at.isoformat() if auth_response.user.created_at else None,
                        "updated_at": auth_response.user.updated_at.isoformat() if auth_response.user.updated_at else None
                    }
                    
                    # Insert into users table
                    self.client.table('users').insert(user_record).execute()
                except Exception as table_error:
                    print(f"Warning: Could not create users table record: {table_error}")
                    # Don't fail registration if users table insert fails
                
                # User created but needs email verification
                return {
                    "success": True,
                    "user": auth_response.user,
                    "profile": {
                        "id": str(auth_response.user.id),
                        "email": email,
                        "name": name,
                        "is_active": True,
                        "email_verified": auth_response.user.email_confirmed_at is not None
                    },
                    "message": "Registration successful! Please check your email to verify your account before logging in."
                }
            else:
                return {"success": False, "error": "Failed to create auth user"}
                
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def authenticate_user(self, email: str, password: str) -> Dict:
        """Authenticate user with email verification check"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                # Check if email is verified
                if not response.user.email_confirmed_at:
                    return {
                        "success": False, 
                        "error": "Email not verified. Please check your email and verify your account before logging in.",
                        "error_code": "EMAIL_NOT_VERIFIED"
                    }
                
                return {
                    "success": True,
                    "user": response.user,
                    "session": response.session,
                    "access_token": response.session.access_token,
                    "email_verified": True
                }
            else:
                return {"success": False, "error": "Invalid credentials"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            response = self.client.table('users').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Get user by email error: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            # Ensure user_id is a string to handle UUID correctly
            user_id_str = str(user_id)
            
            # Try to get from users table first
            try:
                response = self.client.table('users').select('*').eq('id', user_id_str).execute()
                if response.data and len(response.data) > 0:
                    return response.data[0]
            except Exception as users_error:
                print(f"Error querying users table: {users_error}")
            
            # If that fails, try to get directly from auth.users (need admin access)
            try:
                # We need admin client for this (bypasses RLS)
                from app.core.database_supabase import admin_supabase
                if admin_supabase:
                    # Get user from auth.users directly
                    user_response = admin_supabase.table('auth.users').select('*').eq('id', user_id_str).execute()
                    if user_response.data and len(user_response.data) > 0:
                        auth_user = user_response.data[0]
                        # Create a simplified user object
                        return {
                            "id": auth_user.get("id"),
                            "email": auth_user.get("email"),
                            "name": auth_user.get("raw_user_meta_data", {}).get("name", auth_user.get("email").split('@')[0]),
                            "is_admin": False,  # Default
                            "is_active": True,  # Default
                            "email_verified": auth_user.get("email_confirmed_at") is not None
                        }
            except Exception as auth_error:
                print(f"Error querying auth.users table: {auth_error}")
                
            # Last resort: try to get from auth API
            try:
                # Get user data from Supabase Auth API
                user_response = self.client.auth.admin.get_user_by_id(user_id_str)
                if user_response:
                    user_data = user_response.user
                    # Create a simplified user object
                    return {
                        "id": user_data.id,
                        "email": user_data.email,
                        "name": getattr(user_data, 'user_metadata', {}).get('name', user_data.email.split('@')[0]) if user_data.email else None,
                        "is_admin": False,  # Default
                        "is_active": True,  # Default
                        "email_verified": user_data.email_confirmed_at is not None
                    }
            except Exception as api_error:
                print(f"Error getting user from Auth API: {api_error}")
            
            # All methods failed
            return None
        except Exception as e:
            print(f"Get user by ID error: {e}")
            return None
    
    # Email verification methods
    def resend_verification_email(self, email: str) -> Dict:
        """Resend verification email"""
        try:
            response = self.client.auth.resend({
                "type": "signup",
                "email": email,
                "options": {
                    "email_redirect_to": "http://localhost:3000/auth/verify"
                }
            })
            return {"success": True, "message": "Verification email sent successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def verify_email_token(self, token_hash: str, type: str = "email") -> Dict:
        """Verify email using token from email link"""
        try:
            print(f"DEBUG: Attempting to verify token_hash: {token_hash} with type: {type}")
            
            response = self.client.auth.verify_otp({
                "token_hash": token_hash,
                "type": type
            })
            
            print(f"DEBUG: Supabase response: {response}")
            
            if response.user:
                print(f"DEBUG: Verification successful for user: {response.user.email}")
                return {
                    "success": True,
                    "message": "Email verified successfully",
                    "user": response.user
                }
            else:
                print("DEBUG: No user returned from verification")
                return {"success": False, "error": "Invalid or expired verification token"}
        except Exception as e:
            print(f"DEBUG: Verification error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_current_user(self, access_token: str) -> Dict:
        """Get current user from access token"""
        try:
            # Set the session
            response = self.client.auth.get_user(access_token)
            
            if response.user:
                # Check if email is verified
                if not response.user.email_confirmed_at:
                    return {
                        "success": False,
                        "error": "Email not verified",
                        "error_code": "EMAIL_NOT_VERIFIED"
                    }
                
                return {
                    "success": True,
                    "user": response.user,
                    "email_verified": True
                }
            else:
                return {"success": False, "error": "Invalid token"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Project operations
    def create_project(self, user_id: str, name: str, description: str = None) -> Dict:
        """Create a new project"""
        try:
            project_data = {
                "owner_id": str(user_id),  # Ensure UUID is stored as string
                "name": name,
                "description": description,
            }
            
            response = self.client.table('projects').insert(project_data).execute()
            return {"success": True, "data": response.data[0] if response.data else None}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get all projects for a user"""
        try:
            response = self.client.table('projects').select('*').eq('owner_id', user_id).execute()
            return response.data or []
        except Exception as e:
            print(f"Get projects error: {e}")
            return []
    
    def get_project_by_id(self, project_id: int) -> Optional[Dict]:
        """Get project by ID"""
        try:
            response = self.client.table('projects').select('*').eq('id', project_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Get project error: {e}")
            return None
            
    def check_project_collaborator(self, project_id: int, user_id: str) -> Optional[Dict]:
        """Check if user is a collaborator on the project"""
        try:
            response = self.client.table('project_collaborators').select('*').eq('project_id', project_id).eq('user_id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Check collaborator error: {e}")
            return None
    
    def update_project(self, project_id: int, update_data: Dict) -> Dict:
        """Update a project"""
        try:
            response = self.client.table('projects').update(update_data).eq('id', project_id).execute()
            return {"success": True, "data": response.data[0] if response.data else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_project(self, project_id: int) -> Dict:
        """Delete a project"""
        try:
            response = self.client.table('projects').delete().eq('id', project_id).execute()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Document operations
    def create_document(self, project_id: str, filename: str, content: str, user_id: str) -> Dict:
        """Create a new document"""
        try:
            document_data = {
                "project_id": project_id,
                "filename": filename,
                "content": content,
                "uploaded_by": user_id,
            }
            
            response = self.client.table('documents').insert(document_data).execute()
            return {"success": True, "data": response.data[0] if response.data else None}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Document operations
    def get_documents_by_project_id(self, project_id: int) -> List[Dict]:
        """Get all documents for a project"""
        try:
            response = self.client.table('documents').select('*').eq('project_id', project_id).execute()
            return response.data or []
        except Exception as e:
            print(f"Get documents error: {e}")
            return []
    
    def get_document_by_id(self, document_id: int) -> Optional[Dict]:
        """Get a document by ID"""
        try:
            response = self.client.table('documents').select('*').eq('id', document_id).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Get document error: {e}")
            return None
    
    def create_document(self, document_data: Dict) -> Dict:
        """Create a new document"""
        try:
            # Check if documents table exists first
            try:
                # Quick check to see if the table exists
                self.client.table('documents').select('id').limit(1).execute()
            except Exception as table_error:
                print(f"Error checking documents table: {table_error}")
                print("Attempting to create documents table...")
                
                # Try to create the documents table if it doesn't exist
                admin_client = None
                try:
                    from app.core.database_supabase import admin_supabase
                    if admin_supabase:
                        admin_client = admin_supabase
                except ImportError:
                    pass
                
                if admin_client:
                    try:
                        # Create the documents table using SQL
                        sql = """
                        CREATE TABLE IF NOT EXISTS documents (
                            id SERIAL PRIMARY KEY,
                            name TEXT NOT NULL,
                            content TEXT,
                            description TEXT,
                            tags JSONB,
                            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                            uploaded_by UUID NOT NULL REFERENCES auth.users(id),
                            file_path TEXT,
                            file_size INTEGER,
                            file_type TEXT,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
                        );
                        """
                        admin_client.rpc('execute_sql', {'sql': sql}).execute()
                        print("Created documents table successfully")
                    except Exception as create_error:
                        print(f"Error creating documents table: {create_error}")
                        raise  # Re-raise to be caught by outer try
            
            # Ensure uploaded_by is stored as string to handle UUID correctly
            if "uploaded_by" in document_data:
                document_data["uploaded_by"] = str(document_data["uploaded_by"])
            
            print(f"Inserting document: project_id={document_data.get('project_id')}, name={document_data.get('name')}")
            print(f"Uploaded by: {document_data.get('uploaded_by')}")
            
            response = self.client.table('documents').insert(document_data).execute()
            if response.data:
                print(f"Document created successfully with ID: {response.data[0].get('id')}")
                return response.data[0]
            else:
                print("Document creation response had no data")
                return None
        except Exception as e:
            print(f"Create document error: {e}")
            # Return a dict with error info instead of None
            return {"error": str(e), "success": False}
    
    def update_document(self, document_id: int, update_data: Dict) -> Dict:
        """Update a document"""
        try:
            response = self.client.table('documents').update(update_data).eq('id', document_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Update document error: {e}")
            return None
    
    def delete_document(self, document_id: int) -> bool:
        """Delete a document"""
        try:
            response = self.client.table('documents').delete().eq('id', document_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Delete document error: {e}")
            return False
    
    def upload_file_to_storage(self, bucket: str, path: str, file_content: bytes) -> Dict:
        """Upload a file to Supabase Storage"""
        try:
            response = self.client.storage.from_(bucket).upload(path, file_content)
            return response
        except Exception as e:
            print(f"Upload file error: {e}")
            raise e
    
    def delete_file_from_storage(self, bucket: str, path: str) -> Dict:
        """Delete a file from Supabase Storage"""
        try:
            response = self.client.storage.from_(bucket).remove([path])
            return response
        except Exception as e:
            print(f"Delete file error: {e}")
            raise e
            
    # Legacy method for backward compatibility
    def get_project_documents(self, project_id: str) -> List[Dict]:
        """Get all documents for a project (legacy method)"""
        return self.get_documents_by_project_id(project_id)
    
    # Annotation operations
    def create_annotation(self, document_id: str, user_id: str, annotation_data: Dict) -> Dict:
        """Create a new annotation"""
        try:
            annotation = {
                "document_id": document_id,
                "user_id": user_id,
                **annotation_data
            }
            
            response = self.client.table('annotations').insert(annotation).execute()
            return {"success": True, "data": response.data[0] if response.data else None}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_document_annotations(self, document_id: str) -> List[Dict]:
        """Get all annotations for a document"""
        try:
            response = self.client.table('annotations').select('*').eq('document_id', document_id).execute()
            return response.data or []
        except Exception as e:
            print(f"Get annotations error: {e}")
            return []

# Global database service instance
db_service = DatabaseService(supabase)

def get_db_service() -> DatabaseService:
    """Get database service instance"""
    return db_service
