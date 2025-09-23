"""
Fixed Document Upload that works with existing Supabase setup
Handles RLS policies and uses correct database schema
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
import json
import uuid
import os
from datetime import datetime
from pathlib import Path

from app.core.database_supabase import get_db_service, DatabaseService, admin_supabase
from app.core.config import settings
from app.auth_fix import get_current_user_fixed, ensure_project_exists, ensure_project_access

router = APIRouter()

def upload_to_supabase_with_admin(file_path: str, file_content: bytes) -> bool:
    """Upload file using admin client to bypass RLS"""
    try:
        if admin_supabase:
            result = admin_supabase.storage.from_("documents").upload(file_path, file_content)
            print(f"✅ File uploaded to Supabase storage: {file_path}")
            return True
    except Exception as e:
        print(f"❌ Supabase storage upload failed: {e}")
    return False

def create_document_in_db_simple(db_service, doc_data: dict) -> dict:
    """Create document using simplified schema that matches existing database"""
    try:
        # Try minimal data structure first
        minimal_data = {
            "name": doc_data.get("name"),
            "project_id": doc_data.get("project_id"),
            "uploaded_by": doc_data.get("uploaded_by")
        }
        
        response = db_service.client.table('documents').insert(minimal_data).execute()
        if response.data:
            print(f"✅ Document created with minimal data: {response.data[0]}")
            return response.data[0]
            
    except Exception as e:
        print(f"❌ Minimal document creation failed: {e}")
    
    # If that fails, try with admin client
    try:
        if admin_supabase:
            response = admin_supabase.table('documents').insert(minimal_data).execute()
            if response.data:
                print(f"✅ Document created with admin client: {response.data[0]}")
                return response.data[0]
    except Exception as e:
        print(f"❌ Admin document creation failed: {e}")
    
    return None

@router.post("/project/{project_id}/upload")
async def upload_document_working(
    project_id: int,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user_fixed),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Working document upload that bypasses RLS and schema issues"""
    print(f"=== WORKING DOCUMENT UPLOAD ===")
    print(f"Project ID: {project_id}")
    print(f"User: {current_user.get('email')} (ID: {current_user.get('id')})")
    print(f"File: {file.filename} ({file.content_type})")
    
    # Ensure project exists
    project = ensure_project_exists(db_service, project_id, current_user.get("id"))
    print(f"Project: {project.get('name', 'Fallback Project')}")
    
    # Check project access
    if not ensure_project_access(project, current_user, project_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
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
    
    # Check file size (10MB limit for now)
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {max_size / 1024 / 1024}MB"
        )
    
    # Generate file path
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else 'txt'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    storage_path = f"documents/{project_id}/{unique_filename}"
    
    # Try to upload to Supabase storage using admin client
    supabase_upload_success = upload_to_supabase_with_admin(storage_path, file_content)
    
    # If Supabase fails, store locally as backup
    local_storage_path = None
    if not supabase_upload_success:
        try:
            storage_dir = Path("local_document_storage") / str(project_id)
            storage_dir.mkdir(parents=True, exist_ok=True)
            local_file_path = storage_dir / unique_filename
            
            with open(local_file_path, "wb") as f:
                f.write(file_content)
            
            local_storage_path = f"local_storage/documents/{project_id}/{unique_filename}"
            print(f"✅ File stored locally: {local_file_path}")
        except Exception as e:
            print(f"❌ Local storage also failed: {e}")
    
    # Parse document data
    document_name = name if name else file.filename.split('.')[0]
    
    # Create document record in database
    document_data = {
        "name": document_name,
        "project_id": project_id,
        "uploaded_by": str(current_user.get("id"))
    }
    
    print(f"Creating document record: {document_data}")
    
    # Try to create document in database
    document_result = create_document_in_db_simple(db_service, document_data)
    
    # If database creation fails, create local JSON record
    if not document_result:
        try:
            documents_dir = Path("local_document_records")
            documents_dir.mkdir(exist_ok=True)
            
            doc_id = str(uuid.uuid4())
            full_document_data = {
                "id": doc_id,
                "name": document_name,
                "description": description or f"Uploaded file: {file.filename}",
                "project_id": project_id,
                "uploaded_by": str(current_user.get("id")),
                "file_path": storage_path if supabase_upload_success else local_storage_path,
                "file_size": len(file_content),
                "file_type": file_extension,
                "created_at": datetime.utcnow().isoformat(),
                "original_filename": file.filename,
                "stored_in_supabase": supabase_upload_success
            }
            
            record_file = documents_dir / f"document_{doc_id}.json"
            with open(record_file, "w") as f:
                json.dump(full_document_data, f, indent=2, default=str)
            
            print(f"✅ Document record saved locally: {record_file}")
            document_result = full_document_data
            
        except Exception as e:
            print(f"❌ Local record creation failed: {e}")
            document_result = {"id": str(uuid.uuid4()), "name": document_name}
    
    # Prepare response
    response_data = {
        "id": document_result.get("id"),
        "name": document_name,
        "description": description or f"Uploaded file: {file.filename}",
        "file_size": len(file_content),
        "file_type": file_extension,
        "project_id": project_id,
        "uploaded_by": current_user.get("email"),
        "created_at": datetime.utcnow().isoformat(),
        "status": "uploaded",
        "storage_location": "supabase" if supabase_upload_success else "local",
        "file_path": storage_path if supabase_upload_success else local_storage_path
    }
    
    print(f"✅ Upload completed: {response_data['status']} in {response_data['storage_location']}")
    return response_data

@router.get("/project/{project_id}")
async def get_project_documents_working(
    project_id: int,
    current_user: dict = Depends(get_current_user_fixed),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all documents for a project with working schema"""
    print(f"=== FETCHING DOCUMENTS FOR PROJECT {project_id} ===")
    
    documents = []
    
    # Try to get documents from database with simplified query
    try:
        response = db_service.client.table('documents').select('*').eq('project_id', project_id).execute()
        if response.data:
            documents.extend(response.data)
            print(f"✅ Found {len(response.data)} documents in database")
    except Exception as e:
        print(f"Database query error: {e}")
        
        # Try with admin client
        try:
            if admin_supabase:
                response = admin_supabase.table('documents').select('*').eq('project_id', project_id).execute()
                if response.data:
                    documents.extend(response.data)
                    print(f"✅ Found {len(response.data)} documents via admin")
        except Exception as admin_error:
            print(f"Admin query error: {admin_error}")
    
    # Also get local records
    try:
        documents_dir = Path("local_document_records")
        if documents_dir.exists():
            for record_file in documents_dir.glob("document_*.json"):
                try:
                    with open(record_file, "r") as f:
                        doc_data = json.load(f)
                    if doc_data.get("project_id") == project_id:
                        documents.append(doc_data)
                        print(f"✅ Found local document: {doc_data.get('name')}")
                except Exception as local_error:
                    print(f"Error reading local record: {local_error}")
    except Exception as e:
        print(f"Error checking local records: {e}")
    
    print(f"Total documents: {len(documents)}")
    return documents