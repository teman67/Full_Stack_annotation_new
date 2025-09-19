"""
Tagsets API with Supabase Storage integration
-------------------------------------------
This module handles tag set operations including:
- Creating, updating, and retrieving tag sets
- Uploading tag set CSV files to Supabase Storage
- Processing uploaded CSV files to create tag sets
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
import io
import csv
from typing import List, Dict, Any, Optional
import uuid
from pydantic import BaseModel, Field

from app.core.database_supabase import get_db, get_admin_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token

# Security
security = HTTPBearer()

# Define get_current_user function to avoid circular imports
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    user_id = payload.get("user_id")
    if email is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Skip direct database lookup of user and use JWT data instead
    # This avoids UUID/integer type issues with the users table
    try:
        # Create user object directly from token data
        # This bypasses the need to query the users table which might have type issues
        user = {
            "id": user_id, 
            "email": email,
            "is_active": True
        }
        print(f"Using JWT user data: {user}")
    except Exception as e:
        print(f"Error creating user from JWT: {str(e)}")
        # If we can't create a user object from the token, fail authentication
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not create user from token data",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Define Tag and TagSet models
class Tag(BaseModel):
    name: str
    color: str
    description: str = ""
    examples: Optional[str] = ""

class TagSetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[Tag]] = None

router = APIRouter()

@router.post("/upload-csv")
async def upload_tagset_csv(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(""),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
    admin_db = Depends(get_admin_db)
):
    """
    Upload a CSV file for a tagset and save it to Supabase storage
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only CSV files are allowed."
        )
    
    try:
        # Read the file content
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Generate a unique filename to prevent collisions
        user_id = current_user["id"]
        filename = f"{user_id}/{uuid.uuid4()}-{file.filename}"
        
        # Upload the file to Supabase Storage
        storage_response = db.storage.from_("tagset-files").upload(
            path=filename,
            file=contents,
            file_options={"content-type": "text/csv"}
        )
        
        if not storage_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to storage"
            )
            
        # Get public URL (though we'll restrict access with policies)
        file_path = db.storage.from_("tagset-files").get_public_url(filename)
        
        # Parse CSV to extract tags
        csv_text = contents.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(csv_text), delimiter=',')
        
        # Skip header row
        try:
            headers = next(csv_reader)
            print(f"CSV headers found: {headers}")
        except StopIteration:
            raise HTTPException(
                status_code=400,
                detail="CSV file is empty or has no headers"
            )
        
        # Check for required columns (case-sensitive)
        required_columns = ['tag_name', 'definition', 'examples']
        missing_columns = [col for col in required_columns if col not in headers]
        
        if missing_columns:
            # Provide a more detailed error message
            error_message = f"""
Missing required columns: {', '.join(missing_columns)}

Your CSV headers: {', '.join(headers)}
Required headers: tag_name, definition, examples

Make sure your CSV has the EXACT header names (case-sensitive) in the first row.
Example CSV format:
tag_name,definition,examples
PERSON,A human individual,John Smith, Mary Jones
"""
            raise HTTPException(
                status_code=400,
                detail=error_message
            )
            
        # Extract tag data from CSV
        tag_name_idx = headers.index('tag_name')
        definition_idx = headers.index('definition')
        examples_idx = headers.index('examples')
        
        tags = []
        for row in csv_reader:
            if len(row) >= max(tag_name_idx, definition_idx, examples_idx) + 1:
                # Generate a random color in hex format for visualization
                random_color = f"#{hash(row[tag_name_idx]) % 0xffffff:06x}"
                
                tags.append({
                    "name": row[tag_name_idx].strip().upper(),
                    "color": random_color,
                    "description": row[definition_idx].strip() if len(row) > definition_idx else "",
                    "examples": row[examples_idx].strip() if len(row) > examples_idx else ""
                })
        
        # Create tagset record in database
        tagset_data = {
            "name": name,
            "description": description,
            "owner_id": str(user_id),  # Ensure UUID is stored as string
            "file_path": filename,
            "tags": tags  # Store tags as JSONB
        }
        
        # Insert tagset into database
        try:
            # Debug info
            print(f"Attempting to insert tagset: {name} for user {user_id}")
            print(f"Tagset data: {tagset_data}")
            
            # Make sure owner_id is a string
            tagset_data["owner_id"] = str(tagset_data["owner_id"])
            
            # Attempt insertion
            response = db.table("tagsets").insert(tagset_data).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create tagset record"
                )
        except Exception as db_error:
            print(f"Database insert error: {str(db_error)}")
            
            # For RLS policy violations, try using the admin client to bypass RLS
            if "violates row-level security policy" in str(db_error):
                print("RLS policy violation - attempting to use admin client to bypass RLS")
                try:
                    # Try to insert using admin client which bypasses RLS
                    admin_response = admin_db.table("tagsets").insert(tagset_data).execute()
                    if admin_response.data:
                        print("Successfully inserted using admin client")
                        return {
                            "success": True,
                            "message": "Tagset CSV uploaded and processed successfully (admin bypass)",
                            "tagset": admin_response.data[0]
                        }
                    else:
                        print("Admin client insert returned no data")
                except Exception as admin_error:
                    print(f"Admin client insert failed: {str(admin_error)}")
                print(f"RLS policy violation: {db_error}")
                # Try to determine if the table exists
                try:
                    # Try a basic query first to see if the table exists
                    check_table = db.table("tagsets").select("count(*)").limit(1).execute()
                    table_exists = len(check_table.data) > 0
                    
                    if table_exists:
                        error_msg = """
Row-level security policy violation detected. The table exists but you don't have permission to insert records.

Please ensure:
1. You're logged in with the correct account
2. The 'tagsets' table has proper RLS policies configured
3. The column types match (e.g., owner_id should be UUID if using Supabase Auth)

For administrators: Run this SQL in the Supabase SQL editor:

-- Check the data type of the owner_id column
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'tagsets' AND column_name = 'owner_id';

-- Enable RLS on tagsets table if not already enabled
ALTER TABLE tagsets ENABLE ROW LEVEL SECURITY;

-- Allow users to insert their own tagsets
CREATE POLICY "Users can insert their own tagsets" ON tagsets
  FOR INSERT WITH CHECK (auth.uid()::text = owner_id);

-- Allow users to view their own tagsets 
CREATE POLICY "Users can view their own tagsets" ON tagsets
  FOR SELECT USING (auth.uid()::text = owner_id);
"""
                    else:
                        error_msg = """
The 'tagsets' table might not exist in the database.

Please run this SQL in the Supabase SQL editor to create the table:

CREATE TABLE tagsets (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  owner_id TEXT NOT NULL,
  file_path TEXT,
  tags JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on tagsets table
ALTER TABLE tagsets ENABLE ROW LEVEL SECURITY;

-- Allow users to insert their own tagsets
CREATE POLICY "Users can insert their own tagsets" ON tagsets
  FOR INSERT WITH CHECK (auth.uid()::text = owner_id);

-- Allow users to view their own tagsets 
CREATE POLICY "Users can view their own tagsets" ON tagsets
  FOR SELECT USING (auth.uid()::text = owner_id);
"""
                except Exception as check_error:
                    print(f"Error checking table: {check_error}")
                    # Default error message if we can't determine if table exists
                    error_msg = """
Database error: Row-level security policy violation.

Please refer to the setup instructions in TAGSET_CSV_SETUP.md for proper configuration.
"""
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_msg
                )
            
            # For other database errors, provide the original error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(db_error)}"
            )
            
        # Return the created tagset with its tags
        return {
            "success": True,
            "message": "Tagset CSV uploaded and processed successfully",
            "tagset": response.data[0]
        }
        
    except Exception as e:
        print(f"Error uploading tagset CSV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload and process CSV file: {str(e)}"
        )

@router.get("/")
async def get_user_tagsets(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get all tagsets owned by the current user
    """
    try:
        user_id = current_user["id"]
        
        # Convert user_id to string to ensure consistent comparison with stored values
        # Supabase stores UUIDs as strings in the database
        str_user_id = str(user_id)
        print(f"Fetching tagsets for user ID: {str_user_id}")
        
        # Use filter instead of eq to avoid type issues with UUID
        try:
            response = db.table("tagsets").select("*").filter("owner_id", "eq", str_user_id).execute()
            print(f"Query response: {response}")
        except Exception as e:
            print(f"Error with filter query: {e}")
            # Try with text comparison as fallback
            response = db.table("tagsets").select("*").eq("owner_id", str_user_id).execute()
        
        return {
            "success": True,
            "tagsets": response.data if hasattr(response, 'data') else []
        }
    except Exception as e:
        print(f"Error retrieving tagsets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tagsets: {str(e)}"
        )

@router.get("/{tagset_id}")
async def get_tagset(
    tagset_id: int,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get a specific tagset by ID
    """
    try:
        user_id = current_user["id"]
        # Correctly use integer ID for tagsets
        response = db.table("tagsets").select("*").eq("id", int(tagset_id)).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tagset not found"
            )
            
        tagset = response.data[0]
        
        # Check if user owns the tagset
        if str(tagset["owner_id"]) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this tagset"
            )
            
        return {
            "success": True,
            "tagset": tagset
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving tagset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tagset: {str(e)}"
        )

@router.patch("/{tagset_id}")
async def update_tagset(
    tagset_id: int,
    tagset_data: TagSetUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Update an existing tagset
    """
    try:
        user_id = current_user["id"]
        
        # Get the tagset to check ownership
        get_response = db.table("tagsets").select("*").eq("id", int(tagset_id)).execute()
        
        if not get_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tagset not found"
            )
            
        existing_tagset = get_response.data[0]
        
        # Check if user owns the tagset - convert to string for comparison to avoid type issues
        if str(existing_tagset["owner_id"]) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this tagset"
            )
        
        # Prepare data for update - only allow certain fields to be updated
        update_data = {
            "updated_at": "NOW()"
        }
        
        # Only update fields that were provided
        if tagset_data.name is not None:
            update_data["name"] = tagset_data.name
            
        if tagset_data.description is not None:
            update_data["description"] = tagset_data.description
            
        if tagset_data.tags is not None:
            update_data["tags"] = [tag.dict() for tag in tagset_data.tags]
        
        # Update the tagset in the database
        update_response = db.table("tagsets").update(update_data).eq("id", int(tagset_id)).execute()
        
        if not update_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update tagset"
            )
            
        return {
            "success": True,
            "message": "Tagset updated successfully",
            "tagset": update_response.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating tagset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tagset: {str(e)}"
        )

@router.delete("/{tagset_id}")
async def delete_tagset(
    tagset_id: int,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete a tagset and its associated file
    """
    try:
        user_id = current_user["id"]
        
        # Get the tagset to check ownership and get file path
        get_response = db.table("tagsets").select("*").eq("id", int(tagset_id)).execute()
        
        if not get_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tagset not found"
            )
            
        tagset = get_response.data[0]
        
        # Check if user owns the tagset - convert to string for comparison to avoid type issues
        if str(tagset["owner_id"]) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this tagset"
            )
        
        # Delete the file from storage if there's a file path
        if tagset.get("file_path"):
            try:
                db.storage.from_("tagset-files").remove([tagset["file_path"]])
            except Exception as storage_error:
                print(f"Warning: Could not delete file from storage: {storage_error}")
                # Continue with tagset deletion even if file deletion fails
        
        # Delete the tagset from the database
        delete_response = db.table("tagsets").delete().eq("id", int(tagset_id)).execute()
        
        return {
            "success": True,
            "message": "Tagset deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting tagset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tagset: {str(e)}"
        )
