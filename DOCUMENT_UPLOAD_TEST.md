# Document Upload Test Script

This is a quick guide to test if your document upload endpoint is working properly after applying the fixes.

## Prerequisites

1. Backend is running (`python backend/main.py`)
2. User is registered and authenticated
3. At least one project exists

## Step 1: Get an Auth Token

First, you need to log in and get an authentication token. You can do this either:

1. Through the frontend login page (check browser dev tools Network tab to capture the token)
2. Or using a direct API call:

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com", "password": "your-password"}'
```

Save the returned token for the next steps.

## Step 2: Verify Project Exists

Check if you have at least one project:

```bash
curl -X GET "http://localhost:8000/api/projects" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Note the `id` of a project you want to upload a document to.

## Step 3: Test Document Upload

Now test uploading a document:

```bash
curl -X POST "http://localhost:8000/api/documents/project/1/upload" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@./path/to/sample.pdf" \
  -F "name=Test Document" \
  -F "description=This is a test document"
```

Replace:

- `YOUR_TOKEN_HERE` with your authentication token
- `1` with your actual project ID
- `./path/to/sample.pdf` with the path to a test file

## Expected Success Response

```json
{
  "id": 1,
  "name": "Test Document",
  "file_path": "documents/1/some-uuid.pdf",
  "content": "Content of sample.pdf (non-text file)",
  "project_id": 1,
  "user_id": "some-uuid",
  "created_at": "2023-05-10T12:34:56.789Z"
}
```

## Common Errors and Solutions

1. **404 Not Found**: The API endpoint doesn't exist or isn't registered correctly. Check the router registration in main.py.
2. **401 Unauthorized**: Your token is missing, invalid, or expired. Get a new token.
3. **403 Forbidden**: You don't have permission to access this project. Check project ownership.
4. **500 Internal Server Error**: Check the server logs for details. Common issues include:
   - Database table doesn't exist
   - UUID type mismatch
   - Storage bucket not configured properly
   - Environment variables not set correctly

## Monitoring Logs

When running the backend, watch the server logs carefully for any error messages, especially related to:

- Database connection issues
- Supabase storage errors
- Authentication problems
- UUID type conversion issues
