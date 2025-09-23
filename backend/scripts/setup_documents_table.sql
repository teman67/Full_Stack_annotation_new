-- Create documents table for Supabase
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    content TEXT,
    description TEXT,
    tags JSONB,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    uploaded_by UUID NOT NULL REFERENCES auth.users(id),
    file_path TEXT,
    file_size INTEGER,
    file_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Add RLS policies for documents table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Policy to allow users to view their own documents
CREATE POLICY "Users can view their own documents"
    ON documents FOR SELECT
    USING (
        uploaded_by = auth.uid() OR 
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = documents.project_id AND projects.owner_id = auth.uid()
        ) OR
        EXISTS (
            SELECT 1 FROM project_collaborators 
            WHERE project_collaborators.project_id = documents.project_id 
            AND project_collaborators.user_id = auth.uid()
        )
    );

-- Policy to allow users to insert their own documents
CREATE POLICY "Users can insert their own documents"
    ON documents FOR INSERT
    WITH CHECK (uploaded_by = auth.uid());

-- Policy to allow users to update their own documents
CREATE POLICY "Users can update their own documents"
    ON documents FOR UPDATE
    USING (
        uploaded_by = auth.uid() OR 
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = documents.project_id AND projects.owner_id = auth.uid()
        ) OR
        EXISTS (
            SELECT 1 FROM project_collaborators 
            WHERE project_collaborators.project_id = documents.project_id 
            AND project_collaborators.user_id = auth.uid()
            AND project_collaborators.can_edit = true
        )
    );

-- Policy to allow users to delete their own documents or documents from projects they own
CREATE POLICY "Users can delete their own documents"
    ON documents FOR DELETE
    USING (
        uploaded_by = auth.uid() OR 
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = documents.project_id AND projects.owner_id = auth.uid()
        )
    );

-- Create a trigger to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();