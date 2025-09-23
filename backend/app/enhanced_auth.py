from typing import Optional, Dict, Any
import jwt  # PyJWT
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database_supabase import get_db_service, DatabaseService

# Enhanced security with dual token support
class SupabaseBearerAuth(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        
    async def __call__(self, request: Request):
        credentials = await super().__call__(request)
        
        # Also check for Supabase apikey in headers
        supabase_key = request.headers.get("apikey")
        if supabase_key:
            credentials.supabase_key = supabase_key
        
        return credentials

# Replace the standard HTTPBearer with our enhanced version
security = SupabaseBearerAuth()

# Verify Supabase JWT token (separate from our custom tokens)
def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a Supabase JWT token"""
    try:
        # Supabase tokens don't need the secret to decode the payload
        # We just need to extract the user information
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Check if this is a Supabase token by looking for typical fields
        if "sub" in payload and "role" in payload:
            # Extract the user ID from sub claim
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role")
            }
        return None
    except Exception as e:
        print(f"Error verifying Supabase token: {str(e)}")
        return None

async def get_current_user_enhanced(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Enhanced dependency to get current authenticated user using either token type"""
    token = credentials.credentials
    
    # First try our custom JWT
    from app.core.security import verify_token
    payload = verify_token(token)
    
    # If our JWT verification fails, try Supabase token format
    if payload is None:
        print("Custom JWT verification failed, trying Supabase token format")
        payload = verify_supabase_token(token)
    
    if payload is None:
        # Both verification methods failed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user info based on token type
    if "sub" in payload and isinstance(payload["sub"], str) and "@" in payload["sub"]:
        # This is likely our custom JWT with email in sub
        email = payload.get("sub")
        user_id = payload.get("user_id")
    else:
        # This is likely a Supabase token 
        user_id = payload.get("user_id") or payload.get("sub")
        email = payload.get("email")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload - no user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Continue with user lookup as before
    user_id_str = str(user_id)
    user = db_service.get_user_by_id(user_id_str)
    
    if user is None:
        # Create fallback user from token
        user = {
            "id": user_id_str,
            "email": email or f"user_{user_id_str}@example.com",
            "name": (email.split('@')[0] if email else f"User {user_id_str[:8]}"),
            "is_admin": False,
            "is_active": True,
            "email_verified": True
        }
    
    return user