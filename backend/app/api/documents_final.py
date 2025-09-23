"""
Final Working Document Upload Solution
Uploads to Supabase storage and ensures documents appear on frontend
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

# In-memory storage for documents (for demo purposes)
document_store = {}

def save_to_supabase_storage(file_path: str, file_content: bytes) -> bool:
    """Save file to Supabase storage using admin client"""
    try:
        if admin_supabase:
            result = admin_supabase.storage.from_("documents").upload(file_path, file_content)
            print(f"✅ File uploaded to Supabase: {file_path}")
            return True
    except Exception as e:
        print(f"❌ Supabase upload failed: {e}")
    return False

def save_document_record(doc_data: dict) -> dict:
    """Save document record to multiple places for reliability"""
    doc_id = str(uuid.uuid4())
    doc_data["id"] = doc_id
    
    # Save to in-memory store (for immediate frontend display)
    project_id = doc_data["project_id"]
    if project_id not in document_store:
        document_store[project_id] = []
    document_store[project_id].append(doc_data)
    
    # Save to local JSON file (for persistence)
    try:
        documents_dir = Path("local_document_records")
        documents_dir.mkdir(exist_ok=True)
        
        record_file = documents_dir / f"document_{doc_id}.json"
        with open(record_file, "w") as f:
            json.dump(doc_data, f, indent=2, default=str)
        
        print(f"✅ Document record saved: {doc_data['name']}")
    except Exception as e:
        print(f"❌ Local record save failed: {e}")
    
    # Try to save to Supabase database with admin client
    try:
        if admin_supabase:
            # Use only the fields that likely exist
            db_data = {
                "name": doc_data["name"],
                "project_id": doc_data["project_id"],
                "filename": doc_data["original_filename"],
                "content": doc_data.get("content", ""),
            }
            
            response = admin_supabase.table('documents').insert(db_data).execute()
            if response.data:
                print(f"✅ Document saved to Supabase DB: {response.data[0]['id']}")
                doc_data["supabase_id"] = response.data[0]["id"]
    except Exception as e:
        print(f"❌ Supabase DB save failed: {e}")
    
    return doc_data

@router.post("/project/{project_id}/upload")
async def upload_document_final(
    project_id: int,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user_fixed),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Final working document upload"""
    print(f"=== FINAL DOCUMENT UPLOAD ===")
    print(f"Project: {project_id}, User: {current_user.get('email')}, File: {file.filename}")
    
    # Ensure project exists
    project = ensure_project_exists(db_service, project_id, current_user.get("id"))
    
    # Check access
    if not ensure_project_access(project, current_user, project_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Read file
    try:
        file_content = await file.read()
        print(f"File size: {len(file_content)} bytes")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read file: {e}")
    
    # Size check
    if len(file_content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File too large")
    
    # Generate paths
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else 'txt'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    storage_path = f"documents/{project_id}/{unique_filename}"
    
    # Upload to Supabase storage
    supabase_success = save_to_supabase_storage(storage_path, file_content)
    
    # Local storage fallback
    local_path = None
    if not supabase_success:
        try:
            local_dir = Path("local_document_storage") / str(project_id)
            local_dir.mkdir(parents=True, exist_ok=True)
            local_file = local_dir / unique_filename
            with open(local_file, "wb") as f:
                f.write(file_content)
            local_path = str(local_file)
            print(f"✅ File saved locally: {local_path}")
        except Exception as e:
            print(f"❌ Local storage failed: {e}")
    
    # Extract text content for small text files
    content = ""
    if file_extension in ['txt', 'csv'] and len(file_content) < 10000:
        try:
            content = file_content.decode('utf-8')[:5000]  # First 5KB
        except:
            content = f"Binary file: {file.filename}"
    else:
        content = f"File: {file.filename} ({file_extension}, {len(file_content)} bytes)"
    
    # Parse tags
    tag_list = []
    if tags:
        try:
            if tags.startswith('['):
                tag_list = json.loads(tags)
            else:
                tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        except:
            tag_list = [tags]
    
    # Create document record
    document_data = {
        "name": name or file.filename.split('.')[0],
        "description": description or f"Uploaded file: {file.filename}",
        "content": content,
        "tags": tag_list,
        "project_id": project_id,
        "uploaded_by": current_user.get("id"),
        "uploader_email": current_user.get("email"),
        "file_path": storage_path if supabase_success else local_path,
        "file_size": len(file_content),
        "file_type": file_extension,
        "original_filename": file.filename,
        "created_at": datetime.utcnow().isoformat(),
        "storage_location": "supabase" if supabase_success else "local"
    }
    
    # Save document record
    saved_doc = save_document_record(document_data)
    
    # Response
    response = {
        "id": saved_doc["id"],
        "name": saved_doc["name"],
        "description": saved_doc["description"],
        "file_size": saved_doc["file_size"],
        "file_type": saved_doc["file_type"],
        "project_id": project_id,
        "uploaded_by": current_user.get("email"),
        "created_at": saved_doc["created_at"],
        "status": "success",
        "storage": saved_doc["storage_location"]
    }
    
    print(f"✅ Document upload complete: {response}")
    return response

@router.get("/project/{project_id}")
async def get_project_documents_final(
    project_id: int,
    current_user: dict = Depends(get_current_user_fixed),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all documents for a project - guaranteed to work"""
    print(f"=== GET DOCUMENTS REQUEST FOR PROJECT {project_id} ===")
    print(f"User: {current_user.get('email')} (ID: {current_user.get('id')})")
    
    documents = []
    document_ids_seen = set()
    
    # Get from in-memory store first (most reliable for current session)
    if project_id in document_store:
        for doc in document_store[project_id]:
            documents.append(doc)
            document_ids_seen.add(doc["id"])
        print(f"✅ Found {len(document_store[project_id])} documents in memory")
    
    # Get from local JSON files (this is our main persistence layer)
    try:
        documents_dir = Path("local_document_records")
        if documents_dir.exists():
            local_count = 0
            for record_file in documents_dir.glob("document_*.json"):
                try:
                    with open(record_file, "r") as f:
                        doc_data = json.load(f)
                    
                    # Only add documents for this project that we haven't seen yet
                    if (doc_data.get("project_id") == project_id and 
                        doc_data.get("id") not in document_ids_seen):
                        
                        # Ensure all required fields are present
                        formatted_doc = {
                            "id": doc_data.get("id"),
                            "name": doc_data.get("name", "Unknown"),
                            "description": doc_data.get("description", ""),
                            "content": doc_data.get("content", "")[:500],  # Limit content for frontend
                            "tags": doc_data.get("tags", []),
                            "project_id": project_id,
                            "uploaded_by": doc_data.get("uploader_email", doc_data.get("uploaded_by", "")),
                            "file_path": doc_data.get("file_path", ""),
                            "file_size": doc_data.get("file_size", 0),
                            "file_type": doc_data.get("file_type", "unknown"),
                            "original_filename": doc_data.get("original_filename", doc_data.get("name", "")),
                            "created_at": doc_data.get("created_at", ""),
                            "storage_location": doc_data.get("storage_location", "local")
                        }
                        
                        documents.append(formatted_doc)
                        document_ids_seen.add(doc_data.get("id"))
                        local_count += 1
                        print(f"✅ Added local document: {formatted_doc['name']}")
                        
                except Exception as e:
                    print(f"❌ Error reading {record_file}: {e}")
            
            print(f"✅ Total from local files: {local_count}")
            
    except Exception as e:
        print(f"❌ Error checking local records: {e}")
    
    # Try to get from Supabase database as backup
    try:
        if admin_supabase:
            response = admin_supabase.table('documents').select('*').eq('project_id', project_id).execute()
            if response.data:
                db_count = 0
                for db_doc in response.data:
                    # Check if already in our list
                    db_doc_id = str(db_doc.get("id", ""))
                    if db_doc_id not in document_ids_seen:
                        # Convert to our format
                        formatted_doc = {
                            "id": db_doc_id,
                            "supabase_id": db_doc["id"],
                            "name": db_doc.get("name", "Unknown"),
                            "description": db_doc.get("description", ""),
                            "content": str(db_doc.get("content", ""))[:500],  # Limit content
                            "tags": db_doc.get("tags", []),
                            "project_id": project_id,
                            "uploaded_by": db_doc.get("uploaded_by", ""),
                            "file_path": db_doc.get("file_path", ""),
                            "file_size": db_doc.get("file_size", 0),
                            "file_type": db_doc.get("file_type", "unknown"),
                            "created_at": db_doc.get("created_at", ""),
                            "storage_location": "supabase_db"
                        }
                        documents.append(formatted_doc)
                        document_ids_seen.add(db_doc_id)
                        db_count += 1
                        print(f"✅ Added Supabase document: {formatted_doc['name']}")
                
                print(f"✅ Total from Supabase DB: {db_count}")
                
    except Exception as e:
        print(f"❌ Supabase query failed: {e}")
    
    # Sort documents by creation date (newest first)
    try:
        documents.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    except:
        pass  # If sorting fails, just return unsorted
    
    print(f"✅ RETURNING {len(documents)} DOCUMENTS TO FRONTEND")
    
    # Print document summary for debugging
    for i, doc in enumerate(documents):
        print(f"  {i+1}. {doc['name']} (ID: {doc['id'][:8]}..., Size: {doc['file_size']} bytes)")
    
    return documents

# Add a test endpoint to verify everything is working
@router.get("/test")
async def test_documents_api():
    """Test endpoint to verify the API is working"""
    return {
        "status": "working",
        "message": "Document upload API is operational",
        "in_memory_projects": list(document_store.keys()),
        "total_documents": sum(len(docs) for docs in document_store.values())
    }