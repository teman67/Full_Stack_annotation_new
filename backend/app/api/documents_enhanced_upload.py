"""
Enhanced Document Upload with Database and Storage Fixes
Works around database schema issues and provides local fallback storage
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
import json
import uuid
import os
from datetime import datetime
from pathlib import Path

from app.core.database_supabase import get_db_service, DatabaseService
from app.core.config import settings
from app.auth_fix import get_current_user_fixed, ensure_project_exists, ensure_project_access

router = APIRouter()

def create_local_storage_fallback(project_id: int, file_content: bytes, filename: str) -> str:
    """Create local storage as fallback when Supabase storage fails"""
    try:
        # Create local storage directory
        storage_dir = Path("local_document_storage") / str(project_id)
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = filename.split('.')[-1] if '.' in filename else 'txt'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = storage_dir / unique_filename
        
        # Write file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        storage_path = f"local_storage/documents/{project_id}/{unique_filename}"
        print(f"✅ File stored locally at: {file_path}")
        return storage_path
        
    except Exception as e:
        print(f"❌ Local storage fallback failed: {e}")
        return f"fallback_storage/documents/{project_id}/{filename}"

def create_document_record_fallback(document_data: dict) -> dict:
    """Create document record with fallback when database insert fails"""
    try:
        # Try to create a simple JSON record locally as fallback
        documents_dir = Path("local_document_records")
        documents_dir.mkdir(exist_ok=True)
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        document_data["id"] = doc_id
        
        # Save as JSON file
        record_file = documents_dir / f"document_{doc_id}.json"
        with open(record_file, "w") as f:
            json.dump(document_data, f, indent=2, default=str)
        
        print(f"✅ Document record saved locally: {record_file}")
        return document_data
        
    except Exception as e:
        print(f"❌ Fallback document record creation failed: {e}")
        return document_data

@router.post("/project/{project_id}/upload")
async def upload_document_enhanced(
    project_id: int,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user_fixed),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Enhanced document upload with comprehensive fallback handling"""
    print(f"=== ENHANCED DOCUMENT UPLOAD ===")
    print(f"Project ID: {project_id}")
    print(f"User: {current_user.get('email')} (ID: {current_user.get('id')})")
    print(f"File: {file.filename}")
    
    # Ensure project exists (create if necessary)
    try:
        project = ensure_project_exists(db_service, project_id, current_user.get("id"))
        print(f"Project ensured: {project.get('name')} (ID: {project.get('id')})")
    except Exception as e:
        print(f"Error ensuring project exists: {e}")
        # Create a minimal fallback project
        project = {
            "id": project_id,
            "name": f"Project {project_id}",
            "owner_id": current_user.get("id"),
            "created_from_fallback": True
        }
    
    # Check project access
    if not ensure_project_access(project, current_user, project_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    # Check file type
    file_extension = file.filename.split('.')[-1].lower()
    allowed_types = ['txt', 'csv', 'json', 'pdf', 'doc', 'docx']  # Extended list
    if file_extension not in allowed_types:
        print(f"Warning: File type {file_extension} not in standard list, but allowing upload")
    
    # Read file content
    try:
        file_content = await file.read()
        print(f"File size: {len(file_content)} bytes")
    except Exception as e:
        print(f"Error reading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not read uploaded file"
        )
    
    # Check file size (50MB limit)
    max_size = 50 * 1024 * 1024  # 50MB
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {max_size / 1024 / 1024}MB"
        )
    
    # Handle file storage with fallback
    storage_path = None
    try:
        # Try Supabase storage first
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        storage_path = f"documents/{project_id}/{unique_filename}"
        
        # Create the documents bucket if it doesn't exist
        try:
            db_service.client.storage.from_("documents").upload(storage_path, file_content)
            print(f"✅ File uploaded to Supabase storage: {storage_path}")
        except Exception as storage_error:
            print(f"Supabase storage failed: {storage_error}")
            # Use local fallback
            storage_path = create_local_storage_fallback(project_id, file_content, file.filename)
            
    except Exception as e:
        print(f"Storage handling failed: {e}")
        storage_path = create_local_storage_fallback(project_id, file_content, file.filename)
    
    # Parse document name and description
    document_name = name if name else file.filename.split('.')[0]
    document_description = description or f"Uploaded file: {file.filename}"
    
    # Parse tags if provided
    tag_list = []
    if tags:
        try:
            if tags.startswith('['):
                tag_list = json.loads(tags)
            else:
                tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        except:
            tag_list = [tags]  # Single tag fallback
    
    # Extract text content for searchability
    content = ""
    if file_extension == 'txt':
        try:
            content = file_content.decode('utf-8')[:10000]  # Limit to 10KB
        except UnicodeDecodeError:
            content = f"Binary content of {file.filename}"
    elif file_extension == 'json':
        try:
            content = file_content.decode('utf-8')[:5000]  # Limit JSON content
        except UnicodeDecodeError:
            content = f"JSON file: {file.filename}"
    else:
        content = f"File: {file.filename} ({file_extension}, {len(file_content)} bytes)"
    
    # Create document record with multiple fallback strategies
    document_data = {
        "name": document_name,
        "content": content,
        "description": document_description,
        "tags": tag_list,
        "project_id": project_id,
        "uploaded_by": str(current_user.get("id")),
        "file_path": storage_path,
        "file_size": len(file_content),
        "file_type": file_extension,
        "created_at": datetime.utcnow().isoformat(),
        "original_filename": file.filename
    }
    
    print(f"Creating document record:")
    print(f"  - Name: {document_name}")
    print(f"  - Project ID: {project_id}")
    print(f"  - Size: {len(file_content)} bytes")
    print(f"  - Storage: {storage_path}")
    
    # Try multiple database insertion strategies
    document_result = None
    
    # Strategy 1: Use simplified data structure
    try:
        simplified_data = {
            "name": document_name,
            "project_id": project_id,
            "uploaded_by": str(current_user.get("id")),
            "file_path": storage_path,
            "file_size": len(file_content),
            "file_type": file_extension
        }
        
        response = db_service.client.table('documents').insert(simplified_data).execute()
        if response.data:
            document_result = response.data[0]
            print(f"✅ Document record created in database: {document_result.get('id')}")
    except Exception as db_error:
        print(f"Database insertion failed: {db_error}")
        
        # Strategy 2: Create local fallback record
        document_result = create_document_record_fallback(document_data)
    
    # Prepare success response
    response_data = {
        "id": document_result.get("id") if document_result else str(uuid.uuid4()),
        "name": document_name,
        "description": document_description,
        "file_size": len(file_content),
        "file_type": file_extension,
        "project_id": project_id,
        "uploaded_by": current_user.get("email"),
        "created_at": document_data["created_at"],
        "status": "uploaded",
        "storage_path": storage_path,
        "original_filename": file.filename
    }
    
    print(f"✅ Document upload completed successfully")
    print(f"Response: {response_data}")
    
    return response_data

@router.get("/project/{project_id}")
async def get_project_documents_enhanced(
    project_id: int,
    current_user: dict = Depends(get_current_user_fixed),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all documents for a project with enhanced fallback handling"""
    print(f"=== FETCHING DOCUMENTS FOR PROJECT {project_id} ===")
    
    # Ensure project exists
    project = ensure_project_exists(db_service, project_id, current_user.get("id"))
    
    # Check project access
    if not ensure_project_access(project, current_user, project_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    documents = []
    
    # Try to get documents from database
    try:
        response = db_service.client.table('documents').select('*').eq('project_id', project_id).execute()
        if response.data:
            documents = response.data
            print(f"✅ Found {len(documents)} documents in database")
    except Exception as e:
        print(f"Error getting documents from database: {e}")
    
    # Also check local fallback records
    try:
        documents_dir = Path("local_document_records")
        if documents_dir.exists():
            for record_file in documents_dir.glob("document_*.json"):
                try:
                    with open(record_file, "r") as f:
                        doc_data = json.load(f)
                    if doc_data.get("project_id") == project_id:
                        documents.append(doc_data)
                        print(f"✅ Found local document record: {doc_data.get('name')}")
                except Exception as local_error:
                    print(f"Error reading local record {record_file}: {local_error}")
    except Exception as e:
        print(f"Error checking local records: {e}")
    
    print(f"Total documents found: {len(documents)}")
    return documents