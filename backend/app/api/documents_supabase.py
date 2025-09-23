from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
import json
import uuid
import os
from datetime import datetime

from app.core.database_supabase import get_db_service, DatabaseService
from app.core.config import settings
from app.dependencies_supabase import get_current_user

router = APIRouter()

@router.get("/project/{project_id}")
async def get_project_documents(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all documents for a project"""
    # Verify project access
    project = db_service.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if current user is owner or collaborator
    if project.get("owner_id") != current_user.get("id"):
        # Check if user is a collaborator
        collaborator = db_service.check_project_collaborator(project_id, current_user.get("id"))
        if not collaborator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project"
            )
    
    # Get documents from Supabase
    documents = db_service.get_documents_by_project_id(project_id)
    return documents

@router.post("/project/{project_id}")
async def create_document(
    project_id: int,
    name: str,
    content: str,
    description: Optional[str] = None,
    tags: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Create a new document manually"""
    # Verify project access
    project = db_service.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if current user is owner or collaborator
    if project.get("owner_id") != current_user.get("id"):
        # Check if user is a collaborator
        collaborator = db_service.check_project_collaborator(project_id, current_user.get("id"))
        if not collaborator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project"
            )
    
    # Parse tags if provided
    tag_list = []
    if tags:
        try:
            tag_list = json.loads(tags)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tags format"
            )
    
    # Create document in Supabase
    document_data = {
        "name": name,
        "content": content,
        "description": description,
        "tags": tag_list,
        "project_id": project_id,
        "uploaded_by": current_user.get("id"),
        "file_path": None,  # No file for manual creation
        "file_size": 0,
        "file_type": None,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    document = db_service.create_document(document_data)
    return document

@router.post("/project/{project_id}/upload")
async def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Upload a document file"""
    # Verify project access
    project = db_service.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if current user is owner or collaborator
    if project.get("owner_id") != current_user.get("id"):
        # Check if user is a collaborator
        collaborator = db_service.check_project_collaborator(project_id, current_user.get("id"))
        if not collaborator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project"
            )
    
    # Check file type
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.allowed_file_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.allowed_file_types}"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Check file size
    if len(file_content) > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_upload_size / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Set storage path in Supabase Storage
    storage_path = f"documents/{project_id}/{unique_filename}"
    
    # Upload file to Supabase Storage
    db_service.upload_file_to_storage("documents", storage_path, file_content)
    
    # Parse document name
    document_name = name if name else file.filename
    
    # Parse tags if provided
    tag_list = []
    if tags:
        try:
            tag_list = json.loads(tags)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tags format"
            )
    
    # Extract text content based on file type
    content = ""
    if file_extension == 'txt':
        content = file_content.decode('utf-8')
    else:
        # For other file types, you might want to use a library to extract text
        # This is a simplified version that doesn't extract text from non-text files
        content = f"Content of {file.filename} (non-text file)"
    
    # Create document record in database
    document_data = {
        "name": document_name,
        "content": content,
        "description": description,
        "tags": tag_list,
        "project_id": project_id,
        "uploaded_by": str(current_user.get("id")),  # Ensure UUID is stored as string
        "file_path": storage_path,
        "file_size": len(file_content),
        "file_type": file_extension,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    # Print debug info for document creation
    print(f"Creating document with data: project_id={project_id}, uploaded_by={document_data['uploaded_by']}, name={document_name}")
    
    document = db_service.create_document(document_data)
    return document

@router.get("/{document_id}")
async def get_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get a specific document"""
    # Get document
    document = db_service.get_document_by_id(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to the document's project
    project_id = document.get("project_id")
    project = db_service.get_project_by_id(project_id)
    
    # Check if current user is owner or collaborator
    if project.get("owner_id") != current_user.get("id"):
        # Check if user is a collaborator
        collaborator = db_service.check_project_collaborator(project_id, current_user.get("id"))
        if not collaborator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this document"
            )
    
    return document

@router.put("/{document_id}")
async def update_document(
    document_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Update document metadata"""
    # Get document
    document = db_service.get_document_by_id(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to the document's project
    project_id = document.get("project_id")
    project = db_service.get_project_by_id(project_id)
    
    # Check if current user is owner or collaborator
    if project.get("owner_id") != current_user.get("id"):
        # Check if user is a collaborator
        collaborator = db_service.check_project_collaborator(project_id, current_user.get("id"))
        if not collaborator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this document"
            )
    
    # Prepare update data
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if tags is not None:
        try:
            tag_list = json.loads(tags)
            update_data["tags"] = tag_list
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tags format"
            )
    
    # Update document
    updated_document = db_service.update_document(document_id, update_data)
    return updated_document

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Delete a document"""
    # Get document
    document = db_service.get_document_by_id(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to the document's project
    project_id = document.get("project_id")
    project = db_service.get_project_by_id(project_id)
    
    # Check if current user is owner
    if project.get("owner_id") != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can delete documents"
        )
    
    # Delete file from storage if it exists
    file_path = document.get("file_path")
    if file_path:
        try:
            db_service.delete_file_from_storage("documents", file_path)
        except Exception as e:
            # Log error but continue with document deletion
            print(f"Error deleting file from storage: {e}")
    
    # Delete document from database
    db_service.delete_document(document_id)
    
    return {"message": "Document deleted successfully"}