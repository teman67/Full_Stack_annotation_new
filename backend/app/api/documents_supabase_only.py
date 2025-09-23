"""
Supabase-Only Document Router
Reads and writes documents exclusively to/from Supabase database and storage
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database_supabase import get_db_service, DatabaseService, admin_supabase
from app.core.config import settings
from app.auth_fix import get_current_user_fixed, ensure_project_exists, ensure_project_access

router = APIRouter()

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

@router.post("/project/{project_id}/upload")
async def upload_document_supabase(
    project_id: int,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user_fixed),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Upload document to Supabase only (no local storage)"""
    print(f"=== SUPABASE DOCUMENT UPLOAD ===")
    print(f"Project: {project_id}, User: {current_user.get('email')}, File: {file.filename}")
    
    # Ensure project exists
    project = ensure_project_exists(db_service, project_id, current_user.get("id"))
    
    # Check access
    if not ensure_project_access(project, current_user, project_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Read file
    try:
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        file_size = len(file_content)
        print(f"File size: {file_size} bytes")
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
    unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
    storage_path = f"documents/{project_id}/{unique_filename}"
    
    # Upload to Supabase storage
    if not save_to_supabase_storage(storage_path, file_content):
        raise HTTPException(status_code=500, detail="Failed to upload to storage")
    
    # Save document record to Supabase database only
    try:
        # Use only essential columns that definitely exist
        doc_data = {
            "name": name or file.filename,
            "file_path": storage_path,
            "owner_id": current_user.get("id"),  # Required field
        }
        
        # Add optional columns that might exist
        if project_id:
            doc_data["project_id"] = project_id
        if description:
            doc_data["description"] = description
        if tags:
            doc_data["tags"] = [tag.strip() for tag in tags.split(",")]
        
        if admin_supabase:
            response = admin_supabase.table('documents').insert(doc_data).execute()
            if response.data:
                document_id = response.data[0]['id']
                print(f"✅ Document saved to Supabase DB with ID: {document_id}")
                
                # Return success response
                return {
                    "id": document_id,
                    "message": "Document uploaded successfully",
                    "name": name or file.filename,
                    "filename": file.filename,
                    "file_path": storage_path,
                    "file_size": file_size,
                    "storage_location": "supabase",
                    "project_id": project_id
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to save document record")
        else:
            raise HTTPException(status_code=500, detail="Supabase admin client not available")
            
    except Exception as e:
        print(f"❌ Error saving to Supabase DB: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save document: {str(e)}")

@router.get("/project/{project_id}")
async def get_project_documents_supabase(
    project_id: int,
    current_user: dict = Depends(get_current_user_fixed),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all documents for a project from Supabase only"""
    print(f"=== GET DOCUMENTS FROM SUPABASE FOR PROJECT {project_id} ===")
    print(f"User: {current_user.get('email')} (ID: {current_user.get('id')})")
    print(f"Current user object: {current_user}")
    
    # Verify user has access to project
    try:
        project = ensure_project_exists(db_service, project_id, current_user.get("id"))
        if not ensure_project_access(project, current_user, project_id):
            print(f"❌ Access denied to project {project_id}")
            raise HTTPException(status_code=403, detail="Access denied to project")
        print(f"✅ User has access to project {project_id}")
    except Exception as e:
        print(f"❌ Project access check failed: {e}")
        raise HTTPException(status_code=403, detail="Cannot access project")
    
    documents = []
    
    try:
        if admin_supabase:
            # Query documents from Supabase database - ONLY for current user
            response = admin_supabase.table('documents').select('*').eq('project_id', project_id).eq('owner_id', current_user.get('id')).execute()
            
            if response.data:
                for db_doc in response.data:
                    # Format document for frontend
                    formatted_doc = {
                        "id": db_doc["id"],
                        "name": db_doc.get("name", "Unknown"),
                        "filename": db_doc.get("filename", ""),
                        "originalName": db_doc.get("filename", "Unknown"),
                        "size": db_doc.get("file_size", 0),
                        "type": db_doc.get("content_type", "unknown"),
                        "uploadedAt": db_doc.get("created_at", ""),
                        "uploadedBy": db_doc.get("uploaded_by", "Unknown user"),
                        "status": "completed",
                        "annotations": 0,
                        "description": db_doc.get("description", ""),
                        "tags": db_doc.get("tags", []),
                        "project_id": project_id,
                        "file_path": db_doc.get("file_path", ""),
                        "storage_location": "supabase"
                    }
                    documents.append(formatted_doc)
                
                print(f"✅ Found {len(documents)} documents for user {current_user.get('email')} in project {project_id}")
            else:
                print(f"📝 No documents found for user {current_user.get('email')} in project {project_id}")
                
        else:
            print("❌ Supabase admin client not available")
            raise HTTPException(status_code=500, detail="Database connection error")
            
    except Exception as e:
        print(f"❌ Error fetching documents from Supabase: {e}")
        # Don't raise error, just return empty list
        print("⚠️ Returning empty list due to database error")
    
    print(f"📋 Returning {len(documents)} documents")
    return documents

@router.get("/{document_id}/content")
async def get_document_content_supabase(
    document_id: int,
    current_user: dict = Depends(get_current_user_fixed),
):
    """Get the content of a document file from Supabase storage"""
    print(f"=== GET DOCUMENT CONTENT {document_id} ===")
    print(f"User: {current_user.get('email')} (ID: {current_user.get('id')})")
    
    try:
        if admin_supabase:
            # Get the document to check ownership and get file path
            response = admin_supabase.table('documents').select('*').eq('id', document_id).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Document not found")
            
            doc = response.data[0]
            
            # Check if user owns this document
            if doc.get('owner_id') != current_user.get('id'):
                raise HTTPException(status_code=403, detail="You can only view your own documents")
            
            file_path = doc.get('file_path')
            if not file_path:
                raise HTTPException(status_code=404, detail="File path not found")
            
            print(f"Getting content for: {doc.get('name')} from {file_path}")
            
            # Get file from Supabase storage
            try:
                file_response = admin_supabase.storage.from_('documents').download(file_path)
                
                if file_response:
                    # Try to decode as text
                    try:
                        content = file_response.decode('utf-8')
                    except UnicodeDecodeError:
                        # If it's not text, return a message
                        content = "[Binary file - cannot display content]"
                    
                    return {
                        "id": document_id,
                        "name": doc.get('name'),
                        "content": content,
                        "file_path": file_path,
                        "description": doc.get('description', ''),
                        "file_size": len(file_response)
                    }
                else:
                    raise HTTPException(status_code=404, detail="File not found in storage")
                    
            except Exception as e:
                print(f"❌ Storage content fetch failed: {e}")
                raise HTTPException(status_code=404, detail="File not found or inaccessible")
        else:
            raise HTTPException(status_code=500, detail="Database connection error")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting document content {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting document content: {str(e)}")

@router.get("/{document_id}/download")
async def download_document_supabase(
    document_id: int,
    current_user: dict = Depends(get_current_user_fixed),
):
    """Download a document file from Supabase storage"""
    print(f"=== DOWNLOAD DOCUMENT {document_id} ===")
    print(f"User: {current_user.get('email')} (ID: {current_user.get('id')})")
    
    try:
        if admin_supabase:
            # Get the document to check ownership and get file path
            response = admin_supabase.table('documents').select('*').eq('id', document_id).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Document not found")
            
            doc = response.data[0]
            
            # Check if user owns this document
            if doc.get('owner_id') != current_user.get('id'):
                raise HTTPException(status_code=403, detail="You can only download your own documents")
            
            file_path = doc.get('file_path')
            if not file_path:
                raise HTTPException(status_code=404, detail="File path not found")
            
            print(f"Downloading: {doc.get('name')} from {file_path}")
            
            # Get file from Supabase storage
            try:
                file_response = admin_supabase.storage.from_('documents').download(file_path)
                
                if file_response:
                    from fastapi.responses import Response
                    
                    # Determine content type
                    content_type = "application/octet-stream"
                    if file_path.endswith('.txt'):
                        content_type = "text/plain"
                    elif file_path.endswith('.pdf'):
                        content_type = "application/pdf"
                    elif file_path.endswith('.json'):
                        content_type = "application/json"
                    
                    # Return file with proper headers
                    return Response(
                        content=file_response,
                        media_type=content_type,
                        headers={
                            "Content-Disposition": f"attachment; filename=\"{doc.get('name', 'document')}\""
                        }
                    )
                else:
                    raise HTTPException(status_code=404, detail="File not found in storage")
                    
            except Exception as e:
                print(f"❌ Storage download failed: {e}")
                raise HTTPException(status_code=404, detail="File not found or inaccessible")
        else:
            raise HTTPException(status_code=500, detail="Database connection error")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error downloading document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")

@router.put("/{document_id}")
async def update_document_supabase(
    document_id: int,
    document_data: dict,
    current_user: dict = Depends(get_current_user_fixed),
):
    """Update a document's metadata"""
    print(f"=== UPDATE DOCUMENT {document_id} ===")
    print(f"User: {current_user.get('email')} (ID: {current_user.get('id')})")
    print(f"Update data: {document_data}")
    
    try:
        if admin_supabase:
            # First, get the document to check ownership
            response = admin_supabase.table('documents').select('*').eq('id', document_id).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Document not found")
            
            doc = response.data[0]
            
            # Check if user owns this document
            if doc.get('owner_id') != current_user.get('id'):
                raise HTTPException(status_code=403, detail="You can only edit your own documents")
            
            # Update the document
            update_data = {}
            if 'name' in document_data:
                update_data['name'] = document_data['name']
            if 'description' in document_data:
                update_data['description'] = document_data['description']
            if 'tags' in document_data:
                update_data['tags'] = document_data['tags']
            
            # Handle content update if provided
            if 'content' in document_data:
                file_path = doc.get('file_path')
                if file_path:
                    try:
                        # Update the file content in Supabase storage
                        content_bytes = document_data['content'].encode('utf-8')
                        upload_response = admin_supabase.storage.from_('documents').update(
                            file_path, 
                            content_bytes,
                            {"content-type": "text/plain"}
                        )
                        print(f"✅ File content updated in storage: {file_path}")
                    except Exception as e:
                        print(f"❌ Error updating file content: {e}")
                        raise HTTPException(status_code=500, detail=f"Failed to update file content: {str(e)}")
            
            if not update_data and 'content' not in document_data:
                raise HTTPException(status_code=400, detail="No valid fields to update")
            
            update_response = admin_supabase.table('documents').update(update_data).eq('id', document_id).execute()
            
            if update_response.data:
                print(f"✅ Document {document_id} updated successfully")
                return update_response.data[0]
            else:
                raise HTTPException(status_code=500, detail="Failed to update document")
        else:
            raise HTTPException(status_code=500, detail="Database connection error")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating document: {str(e)}")

@router.delete("/{document_id}")
async def delete_document_supabase(
    document_id: int,
    current_user: dict = Depends(get_current_user_fixed),
):
    """Delete a document from both Supabase database and storage"""
    print(f"=== DELETE DOCUMENT {document_id} ===")
    print(f"User: {current_user.get('email')} (ID: {current_user.get('id')})")
    
    try:
        if admin_supabase:
            # First, get the document to check ownership and get file path
            response = admin_supabase.table('documents').select('*').eq('id', document_id).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Document not found")
            
            doc = response.data[0]
            
            # Check if user owns this document
            if doc.get('owner_id') != current_user.get('id'):
                raise HTTPException(status_code=403, detail="You can only delete your own documents")
            
            file_path = doc.get('file_path')
            print(f"Document found: {doc.get('name')} at {file_path}")
            
            # Delete from storage first
            if file_path:
                try:
                    admin_supabase.storage.from_('documents').remove([file_path])
                    print(f"✅ File deleted from storage: {file_path}")
                except Exception as e:
                    print(f"⚠️ Storage deletion failed (file may not exist): {e}")
                    # Continue with database deletion even if storage fails
            
            # Delete from database
            delete_response = admin_supabase.table('documents').delete().eq('id', document_id).execute()
            print(f"✅ Document deleted from database: ID {document_id}")
            
            return {
                "message": "Document deleted successfully",
                "id": document_id,
                "file_path": file_path
            }
        else:
            raise HTTPException(status_code=500, detail="Database connection error")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify router is working"""
    return {"status": "working", "message": "Supabase documents router is active"}

@router.get("/{document_id}")
async def get_document_by_id(
    document_id: int,
    current_user: dict = Depends(get_current_user_fixed),
):
    """Get a specific document by ID from Supabase"""
    print(f"=== GET DOCUMENT {document_id} FROM SUPABASE ===")
    
    try:
        if admin_supabase:
            response = admin_supabase.table('documents').select('*').eq('id', document_id).execute()
            
            if response.data:
                doc = response.data[0]
                
                # Verify user has access to the project
                project_id = doc.get("project_id")
                # You could add project access check here if needed
                
                return {
                    "id": doc["id"],
                    "name": doc.get("name", "Unknown"),
                    "filename": doc.get("filename", ""),
                    "content": doc.get("content", ""),
                    "description": doc.get("description", ""),
                    "tags": doc.get("tags", []),
                    "project_id": project_id,
                    "file_path": doc.get("file_path", ""),
                    "file_size": doc.get("file_size", 0),
                    "content_type": doc.get("content_type", "unknown"),
                    "uploaded_by": doc.get("uploaded_by", "Unknown"),
                    "created_at": doc.get("created_at", ""),
                    "storage_location": "supabase"
                }
            else:
                raise HTTPException(status_code=404, detail="Document not found")
        else:
            raise HTTPException(status_code=500, detail="Database connection error")
            
    except Exception as e:
        print(f"❌ Error fetching document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching document: {str(e)}")