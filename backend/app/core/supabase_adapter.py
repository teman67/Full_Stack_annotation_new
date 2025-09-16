"""
Supabase Database Adapter
This module provides a bridge between SQLAlchemy models and Supabase client operations
"""
from typing import Dict, List, Optional, Any
from supabase import Client
from app.core.config import settings
from fastapi import HTTPException
import json

class SupabaseAdapter:
    """
    Adapter to use Supabase client for database operations
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
    
    def create_user(self, email: str, password: str, user_data: Optional[Dict] = None) -> Dict:
        """Create a new user account"""
        try:
            # Create auth user
            auth_response = self.client.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            if auth_response.user:
                # Create user profile in database
                user_profile = {
                    "id": auth_response.user.id,
                    "email": email,
                    "created_at": auth_response.user.created_at,
                    **(user_data or {})
                }
                
                # Insert into users table
                profile_response = self.client.table('users').insert(user_profile).execute()
                
                return {
                    "user": auth_response.user,
                    "profile": profile_response.data[0] if profile_response.data else None
                }
            else:
                raise HTTPException(status_code=400, detail="Failed to create user")
                
        except Exception as e:
            print(f"User creation error: {e}")
            raise HTTPException(status_code=400, detail=f"User creation failed: {str(e)}")
    
    def authenticate_user(self, email: str, password: str) -> Dict:
        """Authenticate user login"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                return {
                    "user": response.user,
                    "session": response.session,
                    "access_token": response.session.access_token
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
        except Exception as e:
            print(f"Authentication error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            response = self.client.table('users').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Get user error: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            response = self.client.table('users').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Get user by email error: {e}")
            return None
    
    def create_project(self, user_id: str, name: str, description: str = None) -> Dict:
        """Create a new project"""
        try:
            project_data = {
                "owner_id": user_id,
                "name": name,
                "description": description,
                "created_at": "now()"
            }
            
            response = self.client.table('projects').insert(project_data).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Project creation error: {e}")
            raise HTTPException(status_code=400, detail=f"Project creation failed: {str(e)}")
    
    def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get all projects for a user"""
        try:
            response = self.client.table('projects').select('*').eq('owner_id', user_id).execute()
            return response.data or []
        except Exception as e:
            print(f"Get projects error: {e}")
            return []
    
    def create_document(self, project_id: str, filename: str, content: str, user_id: str) -> Dict:
        """Create a new document"""
        try:
            document_data = {
                "project_id": project_id,
                "filename": filename,
                "content": content,
                "uploaded_by": user_id,
                "created_at": "now()"
            }
            
            response = self.client.table('documents').insert(document_data).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Document creation error: {e}")
            raise HTTPException(status_code=400, detail=f"Document creation failed: {str(e)}")
    
    def get_project_documents(self, project_id: str) -> List[Dict]:
        """Get all documents for a project"""
        try:
            response = self.client.table('documents').select('*').eq('project_id', project_id).execute()
            return response.data or []
        except Exception as e:
            print(f"Get documents error: {e}")
            return []
    
    def create_annotation(self, document_id: str, user_id: str, annotation_data: Dict) -> Dict:
        """Create a new annotation"""
        try:
            annotation = {
                "document_id": document_id,
                "user_id": user_id,
                "created_at": "now()",
                **annotation_data
            }
            
            response = self.client.table('annotations').insert(annotation).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Annotation creation error: {e}")
            raise HTTPException(status_code=400, detail=f"Annotation creation failed: {str(e)}")
    
    def get_document_annotations(self, document_id: str) -> List[Dict]:
        """Get all annotations for a document"""
        try:
            response = self.client.table('annotations').select('*').eq('document_id', document_id).execute()
            return response.data or []
        except Exception as e:
            print(f"Get annotations error: {e}")
            return []

# Global adapter instance
_supabase_adapter = None

def get_supabase_adapter() -> SupabaseAdapter:
    """Get or create Supabase adapter instance"""
    global _supabase_adapter
    if _supabase_adapter is None:
        from app.core.database import supabase
        _supabase_adapter = SupabaseAdapter(supabase)
    return _supabase_adapter
