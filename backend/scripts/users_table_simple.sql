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

-- Drop existing policies if needed (uncomment if you need to recreate policies)
-- DROP POLICY IF EXISTS "Users can view their own data" ON users;
-- DROP POLICY IF EXISTS "Users can update their own data" ON users;

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