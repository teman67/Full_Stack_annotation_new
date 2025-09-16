"""
Authentication middleware for protecting routes
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict
from app.core.database_supabase import get_db_service, DatabaseService

security = HTTPBearer()

async def require_verified_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_service: DatabaseService = Depends(get_db_service)
) -> Dict:
    """
    Middleware to ensure user is authenticated and email is verified
    Use this dependency on any route that requires a verified user
    """
    try:
        token = credentials.credentials
        result = db_service.get_current_user(token)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["error"],
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = result["user"]
        
        # Check if email is verified
        if not user.email_confirmed_at:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email verification required. Please verify your email before using this feature.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_service: DatabaseService = Depends(get_db_service)
) -> Dict:
    """
    Get current user without requiring verification (for endpoints that work for any authenticated user)
    """
    try:
        token = credentials.credentials
        result = db_service.get_current_user(token)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["error"],
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return result["user"]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
