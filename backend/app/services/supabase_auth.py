from supabase import Client
from typing import Optional, Dict, Any
import logging
from app.core.database import get_supabase_client
from app.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseAuthService:
    """
    Supabase authentication service for handling user auth operations
    """
    
    def __init__(self):
        self.client: Client = get_supabase_client()
    
    async def sign_up_with_email(self, email: str, password: str, user_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sign up a new user with email and password"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            return {"success": True, "data": response}
        except Exception as e:
            logger.error(f"Supabase sign up error: {e}")
            return {"success": False, "error": str(e)}
    
    async def sign_in_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in with email and password"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {"success": True, "data": response}
        except Exception as e:
            logger.error(f"Supabase sign in error: {e}")
            return {"success": False, "error": str(e)}
    
    async def sign_out(self, access_token: str) -> Dict[str, Any]:
        """Sign out user"""
        try:
            # Set the session with the access token
            self.client.auth.set_session(access_token, "")
            response = self.client.auth.sign_out()
            return {"success": True, "data": response}
        except Exception as e:
            logger.error(f"Supabase sign out error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user(self, access_token: str) -> Dict[str, Any]:
        """Get user information from access token"""
        try:
            # Set the session with the access token
            self.client.auth.set_session(access_token, "")
            response = self.client.auth.get_user()
            return {"success": True, "data": response}
        except Exception as e:
            logger.error(f"Supabase get user error: {e}")
            return {"success": False, "error": str(e)}
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            response = self.client.auth.refresh_session(refresh_token)
            return {"success": True, "data": response}
        except Exception as e:
            logger.error(f"Supabase refresh token error: {e}")
            return {"success": False, "error": str(e)}
    
    async def reset_password(self, email: str) -> Dict[str, Any]:
        """Send password reset email"""
        try:
            response = self.client.auth.reset_password_email(email)
            return {"success": True, "data": response}
        except Exception as e:
            logger.error(f"Supabase password reset error: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_user(self, access_token: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information"""
        try:
            # Set the session with the access token
            self.client.auth.set_session(access_token, "")
            response = self.client.auth.update_user(updates)
            return {"success": True, "data": response}
        except Exception as e:
            logger.error(f"Supabase update user error: {e}")
            return {"success": False, "error": str(e)}
    
    # OAuth methods (for future implementation)
    async def sign_in_with_oauth(self, provider: str, redirect_to: Optional[str] = None) -> Dict[str, Any]:
        """Sign in with OAuth provider (Google, GitHub, etc.)"""
        try:
            response = self.client.auth.sign_in_with_oauth({
                "provider": provider,
                "options": {
                    "redirect_to": redirect_to
                }
            })
            return {"success": True, "data": response}
        except Exception as e:
            logger.error(f"Supabase OAuth sign in error: {e}")
            return {"success": False, "error": str(e)}

# Singleton instance
supabase_auth = SupabaseAuthService()
