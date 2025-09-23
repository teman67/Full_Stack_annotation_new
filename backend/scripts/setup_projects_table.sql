-- Create projects table for Supabase
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    owner_id UUID NOT NULL REFERENCES auth.users(id)
);

-- Add RLS policies for projects table
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Policy to allow users to view their own projects
CREATE POLICY "Users can view their own projects"
    ON projects FOR SELECT
    USING (owner_id::text = auth.uid()::text);

-- Policy to allow users to insert their own projects
CREATE POLICY "Users can insert their own projects"
    ON projects FOR INSERT
    WITH CHECK (owner_id::text = auth.uid()::text);

-- Policy to allow users to update their own projects
CREATE POLICY "Users can update their own projects"
    ON projects FOR UPDATE
    USING (owner_id::text = auth.uid()::text);

-- Policy to allow users to delete their own projects
CREATE POLICY "Users can delete their own projects"
    ON projects FOR DELETE
    USING (owner_id::text = auth.uid()::text);

-- Create project_collaborators table
CREATE TABLE IF NOT EXISTS project_collaborators (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    can_edit BOOLEAN DEFAULT false,
    can_annotate BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(project_id, user_id)
);

-- Add RLS policies for project_collaborators table
ALTER TABLE project_collaborators ENABLE ROW LEVEL SECURITY;

-- Policy to allow project owners to manage collaborators
CREATE POLICY "Project owners can manage collaborators"
    ON project_collaborators 
    USING (EXISTS (
        SELECT 1 FROM projects 
        WHERE projects.id = project_collaborators.project_id 
        AND projects.owner_id = auth.uid()
    ));
    
-- Policy to allow users to see if they are collaborators
CREATE POLICY "Users can view their collaborations"
    ON project_collaborators FOR SELECT
    USING (user_id = auth.uid());

-- Create a trigger to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();