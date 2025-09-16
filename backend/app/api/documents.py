from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import aiofiles
import os

from app.core.database import get_db
from app.core.config import settings
from app.dependencies import get_current_user
from app.models import Document, Project, User
from app.schemas import (
    DocumentCreate, DocumentUpdate, Document as DocumentSchema
)

router = APIRouter()

@router.get("/project/{project_id}", response_model=List[DocumentSchema])
async def get_project_documents(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents for a project"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    documents = db.query(Document).filter(Document.project_id == project_id).all()
    return documents

@router.post("/project/{project_id}", response_model=DocumentSchema)
async def create_document(
    project_id: int,
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new document"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db_document = Document(
        name=document_data.name,
        content=document_data.content,
        project_id=project_id,
        uploaded_by=current_user.id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

@router.post("/project/{project_id}/upload", response_model=DocumentSchema)
async def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document file"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check file type
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.allowed_file_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.allowed_file_types}"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
        )
    
    # Save file
    upload_dir = os.path.join(settings.upload_dir, str(project_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Extract text content (simplified - you might want to use proper parsers)
    if file_extension == 'txt':
        text_content = content.decode('utf-8')
    else:
        # For PDF/DOCX, you'd use proper parsers
        text_content = "File uploaded - text extraction not implemented for this type"
    
    # Create document record
    db_document = Document(
        name=file.filename,
        content=text_content,
        project_id=project_id,
        uploaded_by=current_user.id,
        file_path=file_path
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    document = db.query(Document).join(Project).filter(
        Document.id == document_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document

@router.put("/{document_id}", response_model=DocumentSchema)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a document"""
    document = db.query(Document).join(Project).filter(
        Document.id == document_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update fields if provided
    if document_data.name is not None:
        document.name = document_data.name
    if document_data.content is not None:
        document.content = document_data.content
    
    db.commit()
    db.refresh(document)
    
    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    document = db.query(Document).join(Project).filter(
        Document.id == document_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file if exists
    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
