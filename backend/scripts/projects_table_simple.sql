-- Simple script to create projects table with UUID support

-- Create projects table if it doesn't exist
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Enable RLS on the projects table
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Create policies (will error if they already exist, but that's ok)
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
        CREATE POLICY "Users can insert their own projects"
            ON projects FOR INSERT
            WITH CHECK (owner_id::text = auth.uid()::text);
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Insert policy already exists on projects table';
    END;
    
    BEGIN
        CREATE POLICY "Users can update their own projects"
            ON projects FOR UPDATE
            USING (owner_id::text = auth.uid()::text);
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Update policy already exists on projects table';
    END;
    
    BEGIN
        CREATE POLICY "Users can delete their own projects"
            ON projects FOR DELETE
            USING (owner_id::text = auth.uid()::text);
    EXCEPTION WHEN duplicate_object THEN
        RAISE NOTICE 'Delete policy already exists on projects table';
    END;
END $$;