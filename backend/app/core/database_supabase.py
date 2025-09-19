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
            response = self.client.table('users').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
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
                "owner_id": user_id,
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
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        try:
            response = self.client.table('projects').select('*').eq('id', project_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Get project error: {e}")
            return None
    
    def update_project(self, project_id: str, update_data: Dict) -> Dict:
        """Update a project"""
        try:
            response = self.client.table('projects').update(update_data).eq('id', project_id).execute()
            return {"success": True, "data": response.data[0] if response.data else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_project(self, project_id: str) -> Dict:
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
    
    def get_project_documents(self, project_id: str) -> List[Dict]:
        """Get all documents for a project"""
        try:
            response = self.client.table('documents').select('*').eq('project_id', project_id).execute()
            return response.data or []
        except Exception as e:
            print(f"Get documents error: {e}")
            return []
    
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
