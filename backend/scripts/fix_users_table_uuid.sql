-- Script to check and fix the users table with UUID issues

DO $$
DECLARE
    user_id_type TEXT;
BEGIN
    -- Check if users table exists
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        -- Check the data type of the id column
        SELECT data_type INTO user_id_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'id';
        
        -- If id column is integer, update it to UUID
        IF user_id_type = 'integer' THEN
            -- Drop all foreign keys referencing users.id first
            -- NOTE: This part is complex and potentially risky. We should identify all FKs first.
            
            -- For now, we'll create a new users_uuid table with correct structure
            -- This is safer than trying to alter the existing table with references
            CREATE TABLE users_uuid (
                id UUID PRIMARY KEY REFERENCES auth.users(id),
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                first_name TEXT,
                last_name TEXT, 
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                email_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            );
            
            -- Enable RLS on the new table
            ALTER TABLE users_uuid ENABLE ROW LEVEL SECURITY;
            
            -- Add RLS policies
            CREATE POLICY "Users can view their own data" 
                ON users_uuid FOR SELECT 
                USING (id = auth.uid());
                
            CREATE POLICY "Users can update their own data" 
                ON users_uuid FOR UPDATE 
                USING (id = auth.uid());
            
            RAISE NOTICE 'Created new users_uuid table with proper UUID structure.';
            RAISE NOTICE 'IMPORTANT: You need to manually migrate data and update references!';
        ELSE
            RAISE NOTICE 'Users table id column is already type: %', user_id_type;
        END IF;
    ELSE
        -- Create users table if it doesn't exist
        CREATE TABLE users (
            id UUID PRIMARY KEY REFERENCES auth.users(id),
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            first_name TEXT,
            last_name TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            is_admin BOOLEAN DEFAULT FALSE,
            email_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );
        
        -- Enable RLS on the users table
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        
        -- Add RLS policies
        CREATE POLICY "Users can view their own data" 
            ON users FOR SELECT 
            USING (id = auth.uid());
            
        CREATE POLICY "Users can update their own data" 
            ON users FOR UPDATE 
            USING (id = auth.uid());
            
        RAISE NOTICE 'Created users table with UUID type for id';
    END IF;
END $$;