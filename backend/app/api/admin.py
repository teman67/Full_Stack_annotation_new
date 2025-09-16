from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.dependencies import get_admin_user
from app.models import User, Project, Document, Annotation
from app.schemas import (
    User as UserSchema, AdminUserUpdate, PlatformStats
)

router = APIRouter()

@router.get("/users", response_model=List[UserSchema])
async def get_all_users(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user_by_id(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update any user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields if provided
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin
    if user_data.email_verified is not None:
        user.email_verified = user_data.email_verified
    
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete any user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-deletion
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.post("/users/{user_id}/promote")
async def promote_user_to_admin(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Promote user to admin"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_admin = True
    db.commit()
    
    return {"message": f"User {user.email} promoted to admin"}

@router.post("/users/{user_id}/demote")
async def demote_admin_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Remove admin privileges from user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-demotion
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote yourself"
        )
    
    user.is_admin = False
    db.commit()
    
    return {"message": f"Admin privileges removed from {user.email}"}

@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get platform statistics (admin only)"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    total_users = db.query(User).count()
    total_projects = db.query(Project).count()
    total_documents = db.query(Document).count()
    total_annotations = db.query(Annotation).count()
    
    # Active users in last 30 days (simplified - you'd track login activity)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users_last_30_days = db.query(User).filter(
        User.created_at >= thirty_days_ago
    ).count()
    
    return PlatformStats(
        total_users=total_users,
        total_projects=total_projects,
        total_documents=total_documents,
        total_annotations=total_annotations,
        active_users_last_30_days=active_users_last_30_days
    )

@router.get("/logs")
async def get_system_logs(
    admin_user: User = Depends(get_admin_user)
):
    """Get system logs and audit trail (admin only)"""
    # TODO: Implement proper logging system
    return {"message": "System logs not implemented yet"}

@router.post("/announcements")
async def create_announcement(
    admin_user: User = Depends(get_admin_user)
):
    """Create platform announcement (admin only)"""
    # TODO: Implement announcement system
    return {"message": "Announcement system not implemented yet"}
