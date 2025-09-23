-- Create a bridge table between users (UUID type) and projects (SERIAL type)
-- These tables would be created when setting up Supabase

-- Modify documents table if needed
ALTER TABLE documents 
DROP CONSTRAINT IF EXISTS documents_uploaded_by_fkey,
ALTER COLUMN uploaded_by TYPE TEXT,  -- or UUID if your Supabase uses UUID type
ADD CONSTRAINT documents_uploaded_by_fkey 
    FOREIGN KEY (uploaded_by) 
    REFERENCES auth.users(id);

-- Check if we need to update any existing user references
UPDATE documents 
SET uploaded_by = CAST(uploaded_by AS TEXT)
WHERE uploaded_by IS NOT NULL;

-- Update project owner_id to use proper UUID type
ALTER TABLE projects
DROP CONSTRAINT IF EXISTS projects_owner_id_fkey,  
ALTER COLUMN owner_id TYPE TEXT,  -- or UUID if your Supabase uses UUID type
ADD CONSTRAINT projects_owner_id_fkey 
    FOREIGN KEY (owner_id) 
    REFERENCES auth.users(id);

-- Update project collaborator user_id to use proper UUID type  
ALTER TABLE project_collaborators
DROP CONSTRAINT IF EXISTS project_collaborators_user_id_fkey,
ALTER COLUMN user_id TYPE TEXT,  -- or UUID if your Supabase uses UUID type  
ADD CONSTRAINT project_collaborators_user_id_fkey
    FOREIGN KEY (user_id)
    REFERENCES auth.users(id);