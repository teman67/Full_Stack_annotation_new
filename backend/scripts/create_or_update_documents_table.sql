-- Check if documents table exists and create it if it doesn't
DO $$
BEGIN
    -- First check if the documents table exists
    IF NOT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'documents'
    ) THEN
        -- Create documents table if it doesn't exist
        CREATE TABLE documents (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            content TEXT,
            description TEXT,
            tags JSONB DEFAULT '[]'::jsonb,
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
        
        -- Policy to allow users to delete their own documents
        CREATE POLICY "Users can delete their own documents"
            ON documents FOR DELETE
            USING (
                uploaded_by = auth.uid() OR 
                EXISTS (
                    SELECT 1 FROM projects
                    WHERE projects.id = documents.project_id AND projects.owner_id = auth.uid()
                )
            );
            
        -- Create a trigger for updated_at
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER update_documents_updated_at
            BEFORE UPDATE ON documents
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
            
        RAISE NOTICE 'Created documents table with UUID type for uploaded_by';
    ELSE
        -- If the table exists, check if it has the uploaded_by column
        IF EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = 'documents' AND column_name = 'uploaded_by'
        ) THEN
            -- Modify the uploaded_by column to be UUID
            ALTER TABLE documents 
            DROP CONSTRAINT IF EXISTS documents_uploaded_by_fkey,
            ALTER COLUMN uploaded_by TYPE UUID USING uploaded_by::UUID,
            ADD CONSTRAINT documents_uploaded_by_fkey 
                FOREIGN KEY (uploaded_by) 
                REFERENCES auth.users(id);
                
            RAISE NOTICE 'Modified documents.uploaded_by column to UUID type';
        ELSE
            -- Add the uploaded_by column if it doesn't exist
            ALTER TABLE documents
            ADD COLUMN uploaded_by UUID NOT NULL REFERENCES auth.users(id);
            
            RAISE NOTICE 'Added uploaded_by column to documents table';
        END IF;
    END IF;
    
    -- Check if projects table exists and if it has owner_id column
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'projects'
    ) AND EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'projects' AND column_name = 'owner_id'
    ) THEN
        -- Modify the projects.owner_id column to be UUID
        ALTER TABLE projects
        DROP CONSTRAINT IF EXISTS projects_owner_id_fkey,  
        ALTER COLUMN owner_id TYPE UUID USING owner_id::UUID,
        ADD CONSTRAINT projects_owner_id_fkey 
            FOREIGN KEY (owner_id) 
            REFERENCES auth.users(id);
            
        RAISE NOTICE 'Modified projects.owner_id column to UUID type';
    END IF;
    
    -- Check if project_collaborators table exists and if it has user_id column
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'project_collaborators'
    ) AND EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'project_collaborators' AND column_name = 'user_id'
    ) THEN
        -- Modify the project_collaborators.user_id column to be UUID
        ALTER TABLE project_collaborators
        DROP CONSTRAINT IF EXISTS project_collaborators_user_id_fkey,
        ALTER COLUMN user_id TYPE UUID USING user_id::UUID,  
        ADD CONSTRAINT project_collaborators_user_id_fkey
            FOREIGN KEY (user_id)
            REFERENCES auth.users(id);
            
        RAISE NOTICE 'Modified project_collaborators.user_id column to UUID type';
    END IF;
END $$;