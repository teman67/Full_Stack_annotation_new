from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db, get_supabase_client, get_db_adapter
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models import User, UserProfile
from app.schemas import (
    UserCreate, User as UserSchema, Token, Register, Login,
    PasswordReset, PasswordUpdate
)
from app.services.supabase_auth import supabase_auth
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserSchema)
async def register(user_data: Register, db: Session = Depends(get_db)):
    """Register a new user using Supabase Auth"""
    
    # Use Supabase adapter if SQLAlchemy is not available
    if db is None:
        from app.core.supabase_adapter import get_supabase_adapter
        adapter = get_supabase_adapter()
        
        # Check if user already exists
        existing_user = adapter.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user with Supabase adapter
        try:
            result = adapter.create_user(
                email=user_data.email,
                password=user_data.password,
                user_data={"name": user_data.name}
            )
            
            return UserSchema(
                id=result["user"].id,
                email=result["user"].email,
                name=user_data.name,
                is_active=True,
                email_verified=False
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}"
            )
    
    # Original SQLAlchemy code for when database is available
    # Check if user already exists in our database
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Register user with Supabase
    supabase_result = await supabase_auth.sign_up_with_email(
        email=user_data.email,
        password=user_data.password,
        user_metadata={"name": user_data.name}
    )
    
    if not supabase_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {supabase_result['error']}"
        )
    
    # Create user in our database
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=None,  # We'll use Supabase for auth
        is_active=True,
        email_verified=False  # Supabase will handle email verification
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create user profile
    user_profile = UserProfile(user_id=db_user.id)
    db.add(user_profile)
    db.commit()
    
    return db_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with email and password using Supabase Auth"""
    # Authenticate with Supabase
    supabase_result = await supabase_auth.sign_in_with_email(
        email=form_data.username,
        password=form_data.password
    )
    
    if not supabase_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from our database
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in database"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Use Supabase access token
    supabase_session = supabase_result["data"].session
    access_token = supabase_session.access_token
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Alternative login endpoint for OAuth2PasswordRequestForm"""
    return await login(form_data, db)

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using Supabase"""
    supabase_result = await supabase_auth.refresh_token(refresh_token)
    
    if not supabase_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    supabase_session = supabase_result["data"].session
    access_token = supabase_session.access_token
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout using Supabase"""
    # Note: In a real implementation, you might want to invalidate the token
    # For now, client should just remove the token
    return {"message": "Successfully logged out"}

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """Request password reset using Supabase"""
    # Use Supabase to send password reset email
    supabase_result = await supabase_auth.reset_password(reset_data.email)
    
    if supabase_result["success"]:
        return {"message": "If the email exists, a reset link has been sent"}
    else:
        # Don't reveal if email exists
        return {"message": "If the email exists, a reset link has been sent"}

@router.post("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email address"""
    # TODO: Implement email verification logic
    return {"message": "Email verified successfully"}

# OAuth endpoints (placeholder for future implementation)
@router.get("/oauth/google")
async def google_oauth():
    """Initiate Google OAuth"""
    # TODO: Implement Google OAuth
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OAuth not implemented yet"
    )

@router.get("/oauth/github")
async def github_oauth():
    """Initiate GitHub OAuth"""
    # TODO: Implement GitHub OAuth
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OAuth not implemented yet"
    )

@router.get("/oauth/linkedin")
async def linkedin_oauth():
    """Initiate LinkedIn OAuth"""
    # TODO: Implement LinkedIn OAuth
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OAuth not implemented yet"
    )

@router.post("/oauth/callback")
async def oauth_callback():
    """Handle OAuth callback"""
    # TODO: Implement OAuth callback
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OAuth not implemented yet"
    )
