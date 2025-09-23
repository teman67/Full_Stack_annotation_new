# Document Upload Functionality - Complete Fix

This guide consolidates all the fixes required to resolve the document upload functionality issues in the application.

## Issue Summary

The application was experiencing two main issues:

1. The document upload endpoint (`POST /api/documents/project/1/upload`) was returning a 404 Not Found error
2. After fixing the endpoint, a UUID type mismatch error occurred during authentication

## Fix Summary

We've created several files to address these issues:

1. **Simplified SQL Scripts**:

   - `users_table_simple.sql`: Creates users table with proper UUID type for user IDs
   - `documents_table_simple.sql`: Creates documents table with proper UUID reference to users

2. **Storage Setup Script**:

   - `setup_storage_simple.py`: Sets up Supabase storage bucket with proper permissions

3. **Guidance Documents**:
   - `DOCUMENT_UPLOAD_FIX.md`: Step-by-step guide to fix the document upload functionality
   - `DOCUMENT_UPLOAD_TEST.md`: How to test if the document upload works properly

## Root Cause Analysis

1. **404 Error (Endpoint Not Found)**:

   - The document upload endpoint was correctly implemented in `documents_supabase.py`
   - The router was correctly registered in `main.py`
   - The issue was likely due to database schema problems preventing the endpoint from working correctly

2. **UUID Type Mismatch**:
   - Supabase authentication uses UUID format for user IDs
   - Some database tables were using integer type for user IDs instead of UUID
   - This caused type mismatches when joining tables or validating relationships

## Complete Fix Implementation

### 1. Database Schema Fixes

The most critical fix is ensuring all user ID references use UUID type consistently:

```sql
-- Users Table (using UUID type)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    -- other fields
);

-- Documents Table (using UUID for user_id)
CREATE TABLE IF NOT EXISTS documents (
    -- other fields
    user_id UUID REFERENCES auth.users(id),
    -- other fields
);
```

### 2. Policy Type Casting

When creating RLS policies, you must explicitly cast `auth.uid()` to UUID:

```sql
-- For users table
CREATE POLICY "Users can view their own data"
    ON users FOR SELECT
    USING (id = auth.uid()::uuid);

-- For documents table
CREATE POLICY "Users can view their own documents"
    ON documents FOR SELECT
    USING (user_id = auth.uid()::uuid);
```

This explicit casting resolves the "operator does not exist: integer = uuid" error.

### 2. Code Improvements

In `database_supabase.py`, we improved UUID handling:

```python
# Ensure uploaded_by is stored as string to handle UUID correctly
if "uploaded_by" in document_data:
    document_data["uploaded_by"] = str(document_data["uploaded_by"])
```

### 3. Storage Configuration

Set up proper Supabase storage with correct RLS policies:

```python
# Create bucket for documents
create_storage_bucket()
create_storage_policies()
```

## Validation Steps

After implementing these fixes:

1. Check that the database tables are created with correct UUID types
2. Verify that the storage bucket exists with proper permissions
3. Test document upload using the API endpoint
4. Monitor logs for any UUID type mismatch errors

## Preventive Measures

To avoid similar issues in the future:

1. Always use UUID type for user references when working with Supabase Auth
2. Implement proper error handling and validation for type mismatches
3. Use explicit type casting when needed to handle UUID conversions
4. Add more detailed logging for authentication and database operations

## Next Steps

If these fixes don't resolve the issues completely:

1. Check for other tables that might have inconsistent ID types
2. Verify the Supabase RLS policies are correctly implemented
3. Test the authentication flow end-to-end
4. Consider a database migration to standardize all UUID fields
