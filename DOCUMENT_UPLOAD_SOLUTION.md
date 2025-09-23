# Document Upload 404 Issue - Resolution Guide

## Problem Diagnosis

After analyzing the codebase, I've found the likely cause of the 404 error when attempting to upload documents to `/api/documents/project/{project_id}/upload`:

1. The API route is correctly defined in `backend/app/api/documents_supabase.py` and properly registered in `backend/main.py`.
2. The document upload functionality requires proper authentication with a valid JWT token.
3. The Supabase storage bucket for documents must be properly configured with the right policies.
4. The project ID must exist in the database.

## Step-by-Step Solution

### 1. Verify API Server is Running

First, make sure your FastAPI backend is running:

```bash
cd backend
python main.py
```

You should see the server start at http://0.0.0.0:8000.

### 2. Setup Supabase Storage Bucket

Ensure the "documents" storage bucket exists in Supabase with proper policies:

```bash
cd backend/scripts
python setup_storage.py
```

Follow the instructions in the console output to manually set up the storage policies in the Supabase dashboard if needed.

### 3. Test with the Troubleshooter Script

I've created a comprehensive troubleshooting script that will:

- Check if the API server is running
- Authenticate with your credentials
- Get or create a project
- Upload a test document

```bash
cd D:\Full_Stack_annotation_new\Full_Stack_annotation_new
python document_upload_troubleshooter.py
```

Before running, edit the script to include your actual email and password:

```python
# Configuration
API_BASE_URL = "http://localhost:8000"
EMAIL = "your-actual-email@example.com"  # <-- Replace this
PASSWORD = "your-actual-password"        # <-- Replace this
DEBUG = True  # Set to True to see detailed request/response info
```

### 4. Check Authentication

Make sure your authentication token is valid and not expired:

1. The token format should be: `Bearer eyJhbGciOiJ...`
2. The token must be included in the Authorization header
3. The user must be authenticated with Supabase

### 5. Check Request Format

When uploading documents, ensure you're using the correct multipart form format:

```
POST /api/documents/project/1/upload
Authorization: Bearer eyJhbGciOiJ...
Content-Type: multipart/form-data; boundary=---WebKitFormBoundaryXYZ

---WebKitFormBoundaryXYZ
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: text/plain

(file content here)
---WebKitFormBoundaryXYZ
Content-Disposition: form-data; name="name"

Test Document
---WebKitFormBoundaryXYZ
Content-Disposition: form-data; name="description"

This is a test document
---WebKitFormBoundaryXYZ--
```

### 6. Common Issues to Check

If you're still getting a 404 error, check these common issues:

1. **Project ID Doesn't Exist**: Make sure the project ID you're using actually exists in your database.
2. **UUID Type Issues**: Ensure UUIDs are properly handled (the code should already handle this with proper type casting).
3. **Supabase Storage Permissions**: Check that the "documents" bucket has the right policies set.
4. **Database Table Structure**: The documents table should match what's expected in the code.

### 7. Using the Test Script

The `test_document_upload.py` script provides a complete Python implementation for testing the document upload functionality:

```bash
python test_document_upload.py
```

Edit the script to include your actual email and password before running.

## Additional Troubleshooting

If you're still encountering issues, these steps may help:

1. Check the server logs for any error messages
2. Verify the API routes are correctly registered using the `/docs` endpoint (if enabled)
3. Test the authentication endpoint separately to ensure you can get a valid token
4. Examine the database tables to make sure the projects table has entries

If you need additional assistance, please provide:

1. The specific error message from the server logs
2. The response headers from your upload request
3. The exact URL you're using for the upload endpoint
