-- Script to check the database schema and fix UUID handling issues

-- First, let's check the data type of the id column in the users table
SELECT column_name, data_type, udt_name
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'id';

-- Create a helper function to verify UUIDs in text form
CREATE OR REPLACE FUNCTION is_valid_uuid(text) RETURNS boolean AS $$
BEGIN
    RETURN $1 ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$';
EXCEPTION WHEN OTHERS THEN
    RETURN false;
END;
$$ LANGUAGE plpgsql;

-- Try to convert any integer user IDs to UUIDs
-- This will only run if the id column is text or UUID type
DO $$
BEGIN
    -- Check if users table exists
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        -- Check if documents table exists
        IF EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'documents'
        ) THEN
            -- Fix documents.uploaded_by column if it's not already UUID
            IF EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'documents' 
                AND column_name = 'uploaded_by' 
                AND data_type NOT IN ('uuid', 'text')
            ) THEN
                -- Modify documents.uploaded_by to use TEXT type
                ALTER TABLE documents 
                DROP CONSTRAINT IF EXISTS documents_uploaded_by_fkey,
                ALTER COLUMN uploaded_by TYPE TEXT;
                
                -- Add foreign key constraint back
                ALTER TABLE documents
                ADD CONSTRAINT documents_uploaded_by_fkey 
                FOREIGN KEY (uploaded_by) 
                REFERENCES auth.users(id);
            END IF;
        END IF;
        
        -- Check if projects table exists
        IF EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'projects'
        ) THEN
            -- Fix projects.owner_id column if it's not already UUID
            IF EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'projects' 
                AND column_name = 'owner_id' 
                AND data_type NOT IN ('uuid', 'text')
            ) THEN
                -- Modify projects.owner_id to use TEXT type
                ALTER TABLE projects 
                DROP CONSTRAINT IF EXISTS projects_owner_id_fkey,
                ALTER COLUMN owner_id TYPE TEXT;
                
                -- Add foreign key constraint back
                ALTER TABLE projects
                ADD CONSTRAINT projects_owner_id_fkey 
                FOREIGN KEY (owner_id) 
                REFERENCES auth.users(id);
            END IF;
        END IF;
        
        -- Check if project_collaborators table exists
        IF EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'project_collaborators'
        ) THEN
            -- Fix project_collaborators.user_id column if it's not already UUID
            IF EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'project_collaborators' 
                AND column_name = 'user_id' 
                AND data_type NOT IN ('uuid', 'text')
            ) THEN
                -- Modify project_collaborators.user_id to use TEXT type
                ALTER TABLE project_collaborators 
                DROP CONSTRAINT IF EXISTS project_collaborators_user_id_fkey,
                ALTER COLUMN user_id TYPE TEXT;
                
                -- Add foreign key constraint back
                ALTER TABLE project_collaborators
                ADD CONSTRAINT project_collaborators_user_id_fkey 
                FOREIGN KEY (user_id) 
                REFERENCES auth.users(id);
            END IF;
        END IF;
    END IF;
END $$;