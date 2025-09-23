-- Simple script to create documents table with UUID support

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