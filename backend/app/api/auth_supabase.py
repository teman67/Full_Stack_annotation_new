"""
Authentication routes using only Supabase client
No SQLAlchemy dependencies
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta, datetime
from typing import Dict, Any, Optional

from app.core.database_supabase import get_db_service, DatabaseService
from app.core.security import create_access_token
from app.core.config import settings
from app.schemas import (
    UserCreate, User as UserSchema, Token, Register, Login,
    PasswordReset, PasswordUpdate
)

router = APIRouter()
security = HTTPBearer()

# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        
        # Decode our custom JWT token
        from app.core.security import verify_token
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user info from the token payload
        email = payload.get("sub")
        user_id = payload.get("user_id")
        
        if not email or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Try to get user from users table first
        user_record = db_service.get_user_by_email(email)
        
        print(f"DEBUG: Looking up user for email: {email}")
        print(f"DEBUG: User record found: {user_record is not None}")
        
        if user_record:
            # User exists in users table
            print(f"DEBUG: User record name: {user_record.get('name')}")
            user_data = {
                "id": user_record.get("id", int(user_id.replace("-", "")[:8], 16) if isinstance(user_id, str) else user_id),
                "email": email,
                "name": user_record.get("name", email.split("@")[0]),
                "is_active": user_record.get("is_active", True),
                "is_admin": user_record.get("is_admin", False),
                "email_verified": user_record.get("email_verified", True),
                "created_at": datetime.fromisoformat(user_record["created_at"]) if user_record.get("created_at") else datetime.utcnow(),
                "updated_at": datetime.fromisoformat(user_record["updated_at"]) if user_record.get("updated_at") else datetime.utcnow(),
            }
        else:
            # User doesn't exist in users table, create basic user data from token
            email_prefix = email.split("@")[0].split(".")[0].capitalize()
            print(f"DEBUG: Creating user data for email: {email}")
            print(f"DEBUG: Extracted name: {email_prefix}")
            
            user_data = {
                "id": int(user_id.replace("-", "")[:8], 16) if isinstance(user_id, str) else user_id,
                "email": email,
                "name": email_prefix,  # Extract first part before dots and capitalize
                "is_active": True,
                "is_admin": False,
                "email_verified": True,  # They must be verified if they can log in
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        
        return UserSchema(**user_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=Dict[str, Any])
async def register(user_data: Register, db_service: DatabaseService = Depends(get_db_service)):
    """Register a new user using Supabase"""
    
    # Check if user already exists
    existing_user = db_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user with Supabase
    result = db_service.create_user(
        email=user_data.email,
        password=user_data.password,
        name=user_data.name
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {result['error']}"
        )
    
    return {
        "message": result.get("message", "User registered successfully"),
        "user": {
            "id": str(result["user"].id),
            "email": str(result["user"].email),
            "name": user_data.name,
            "is_active": True,
            "email_verified": result["user"].email_confirmed_at is not None,
            "created_at": result["user"].created_at.isoformat() if hasattr(result["user"], 'created_at') and result["user"].created_at else None
        },
        "email_verification_required": result["user"].email_confirmed_at is None
    }

@router.post("/login", response_model=Token)
async def login(user_data: Login, db_service: DatabaseService = Depends(get_db_service)):
    """Login user using Supabase"""
    
    # Authenticate with Supabase
    result = db_service.authenticate_user(user_data.email, user_data.password)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create our own access token for consistency
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": result["user"].email, "user_id": result["user"].id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "supabase_token": result["access_token"]  # Also return Supabase token
    }

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_service: DatabaseService = Depends(get_db_service)
):
    """OAuth2 compatible token endpoint"""
    
    # Authenticate with Supabase
    result = db_service.authenticate_user(form_data.username, form_data.password)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": result["user"].email, "user_id": result["user"].id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: UserSchema = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service),
):
    """Get current user information"""
    return current_user

@router.post("/resend-verification")
async def resend_verification_email(
    email_data: Dict[str, str], 
    db_service: DatabaseService = Depends(get_db_service)
):
    """Resend email verification"""
    email = email_data.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required"
        )
    
    result = db_service.resend_verification_email(email)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to resend verification email: {result['error']}"
        )
    
    return {"message": "Verification email sent successfully"}

@router.post("/verify-email")
async def verify_email(
    verification_data: Dict[str, str],
    db_service: DatabaseService = Depends(get_db_service)
):
    """Verify email using token from email link"""
    print(f"DEBUG: Received verification data: {verification_data}")
    
    token_hash = verification_data.get("token_hash")
    type_param = verification_data.get("type", "email")
    
    print(f"DEBUG: token_hash: {token_hash}")
    print(f"DEBUG: type: {type_param}")
    
    if not token_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token hash is required"
        )
    
    result = db_service.verify_email_token(token_hash, type_param)
    print(f"DEBUG: Verification result: {result}")
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email verification failed: {result['error']}"
        )
    
    return {
        "message": "Email verified successfully",
        "user": {
            "id": str(result["user"].id),
            "email": str(result["user"].email),
            "email_verified": True
        }
    }

@router.post("/forgot-password")
async def forgot_password(email: str, db_service: DatabaseService = Depends(get_db_service)):
    """Request password reset"""
    try:
        # Use Supabase auth for password reset
        result = db_service.client.auth.reset_password_email(email)
        return {"message": "Password reset email sent if user exists"}
    except Exception as e:
        # Don't reveal if user exists or not
        return {"message": "Password reset email sent if user exists"}

@router.post("/logout")
async def logout(db_service: DatabaseService = Depends(get_db_service)):
    """Logout user"""
    try:
        db_service.client.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        return {"message": "Logged out successfully"}  # Always return success
