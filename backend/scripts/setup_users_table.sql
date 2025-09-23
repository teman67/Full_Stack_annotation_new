-- Simple script to create users table with UUID support

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

-- Add RLS policies if they don't exist
-- We need to use a PL/pgSQL block to check if policies exist
DO $$
BEGIN
    -- Policy for viewing own data
    IF NOT EXISTS (
        SELECT FROM pg_policies 
        WHERE tablename = 'users' 
        AND policyname = 'Users can view their own data'
    ) THEN
        BEGIN
            CREATE POLICY "Users can view their own data" 
                ON users FOR SELECT 
                USING (id = auth.uid());
        EXCEPTION WHEN duplicate_object THEN
            -- Policy already exists, ignore
            RAISE NOTICE 'Policy "Users can view their own data" already exists';
        END;
    END IF;
    
    -- Policy for updating own data
    IF NOT EXISTS (
        SELECT FROM pg_policies 
        WHERE tablename = 'users' 
        AND policyname = 'Users can update their own data'
    ) THEN
        BEGIN
            CREATE POLICY "Users can update their own data" 
                ON users FOR UPDATE 
                USING (id = auth.uid());
        EXCEPTION WHEN duplicate_object THEN
            -- Policy already exists, ignore
            RAISE NOTICE 'Policy "Users can update their own data" already exists';
        END;
    END IF;
END $$;