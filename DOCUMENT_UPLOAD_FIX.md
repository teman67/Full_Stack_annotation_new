# Document Upload Functionality Fix

This guide provides a step-by-step approach to fix the document upload functionality in the application.

## Step 1: Fix Database Schema

### 1.1 Set Up Users Table

Run the following SQL script in your Supabase SQL Editor:

```sql
-- From users_table_simple.sql
-- Check if users table exists, if not create it
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Enable RLS on the users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policies (will error if they already exist, but that's ok)
DO $$
BEGIN
    BEGIN
        CREATE POLICY "Users can view their own data"
            ON users FOR SELECT
            USING (id::text = auth.uid()::text);
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Select policy already exists on users table';
    END;

    BEGIN
        CREATE POLICY "Users can update their own data"
            ON users FOR UPDATE
            USING (id::text = auth.uid()::text);
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Update policy already exists on users table';
    END;
END $$;
```

### 1.2 Set Up Projects Table (if not already created)

Make sure you have a projects table. If not, create it with:

```sql
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    -- Add additional columns if needed after confirming they exist in your schema
);

-- Create project_collaborators table if needed for collaboration features
CREATE TABLE IF NOT EXISTS project_collaborators (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    can_edit BOOLEAN DEFAULT false,
    can_annotate BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(project_id, user_id)
);

ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    BEGIN
        CREATE POLICY "Users can view their own projects"
            ON projects FOR SELECT
            USING (owner_id::text = auth.uid()::text);
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Select policy already exists on projects table';
    END;

    BEGIN
        CREATE POLICY "Users can update their own projects"
            ON projects FOR UPDATE
            USING (owner_id::text = auth.uid()::text);
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Update policy already exists on projects table';
    END;
END $$;
```

### 1.3 Set Up Documents Table

Run the following SQL script in your Supabase SQL Editor:

```sql
-- From documents_table_simple.sql
-- Create documents table if it doesn't exist
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    file_path TEXT,
    content TEXT,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    uploaded_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Enable RLS on the documents table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create policies (will error if they already exist, but that's ok)
DO $$
BEGIN
    BEGIN
        CREATE POLICY "Users can view their own documents"
            ON documents FOR SELECT
            USING (uploaded_by::text = auth.uid()::text);
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Select policy already exists on documents table';
    END;

    BEGIN
        CREATE POLICY "Users can insert their own documents"
            ON documents FOR INSERT
            WITH CHECK (uploaded_by::text = auth.uid()::text);
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Insert policy already exists on documents table';
    END;

    BEGIN
        CREATE POLICY "Users can update their own documents"
            ON documents FOR UPDATE
            USING (uploaded_by::text = auth.uid()::text);
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Update policy already exists on documents table';
    END;
END $$;
```

## Step 2: Set Up Supabase Storage

### 2.1 Create a .env file (if not already exists)

Create a `.env` file in the backend directory with your Supabase credentials:

```
SUPABASE_URL=https://your-project-url.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

### 2.2 Run the Storage Setup Script

Run the Python script to create the storage bucket and policies:

```
python scripts/setup_storage_simple.py
```

## Step 3: Check API Implementation

Ensure your FastAPI endpoints for document upload are correctly implemented in `backend/app/api/documents_supabase.py` with:

1. Upload endpoint: `POST /api/documents/project/{project_id}/upload`
2. Document handling functionality
3. Proper Supabase storage integration

## Step 4: Test Document Upload

1. Start your backend server:

   ```
   cd backend
   python main.py
   ```

2. Test the API using a tool like Postman or curl:
   ```
   curl -X POST "http://localhost:8000/api/documents/project/1/upload" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -F "file=@path/to/your/document.pdf"
   ```

## Troubleshooting

If you encounter issues:

1. Check the backend logs for errors
2. Verify that the SQL scripts executed successfully
3. Ensure your Supabase credentials are correct
4. Confirm that the storage bucket was created
5. Verify user authentication is working correctly

For UUID errors, ensure:

- The users table has an `id` column of type UUID
- Any foreign keys referencing the user ID are also of type UUID
- The document table's `user_id` field is of type UUID
