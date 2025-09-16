"""
Project routes using only Supabase client - requires verified users
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.core.database_supabase import get_db_service, DatabaseService
from app.core.auth_middleware import require_verified_user
from app.schemas import ProjectCreate, ProjectUpdate

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_projects(
    current_user = Depends(require_verified_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all projects for the current verified user"""
    user_id = str(current_user.id)
    projects = db_service.get_user_projects(user_id)
    return projects

@router.post("/", response_model=Dict[str, Any])
async def create_project(
    project_data: ProjectCreate,
    current_user = Depends(require_verified_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Create a new project (verified users only)"""
    user_id = str(current_user.id)
    
    result = db_service.create_project(
        user_id=user_id,
        name=project_data.name,
        description=project_data.description
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create project: {result['error']}"
        )
    
    return {
        "message": "Project created successfully",
        "project": result["data"]
    }

@router.get("/{project_id}", response_model=Dict[str, Any])
async def get_project(
    project_id: str,
    current_user = Depends(require_verified_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get a specific project (verified users only)"""
    user_id = str(current_user.id)
    
    # Get project and verify ownership
    project = db_service.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.get("owner_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    return project

@router.put("/{project_id}", response_model=Dict[str, Any])
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user = Depends(require_verified_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Update a project (verified users only)"""
    user_id = str(current_user.id)
    
    # Verify ownership
    project = db_service.get_project_by_id(project_id)
    if not project or project.get("owner_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    result = db_service.update_project(project_id, project_data.dict(exclude_unset=True))
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update project: {result['error']}"
        )
    
    return {
        "message": "Project updated successfully",
        "project": result["data"]
    }

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user = Depends(require_verified_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Delete a project (verified users only)"""
    user_id = str(current_user.id)
    
    # Verify ownership
    project = db_service.get_project_by_id(project_id)
    if not project or project.get("owner_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    result = db_service.delete_project(project_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete project: {result['error']}"
        )
    
    return {"message": "Project deleted successfully"}
