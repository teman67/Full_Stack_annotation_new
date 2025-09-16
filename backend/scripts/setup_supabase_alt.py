"""
Alternative Supabase Database Setup Script

This script uses Supabase SQL execution instead of direct PostgreSQL connection.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import get_supabase_client
from app.core.config import settings

def create_tables_via_supabase():
    """Create tables using Supabase SQL execution"""
    print("🗄️ Creating database tables via Supabase...")
    
    client = get_supabase_client()
    
    # SQL to create all tables
    create_tables_sql = """
    -- Create users table
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR UNIQUE NOT NULL,
        name VARCHAR NOT NULL,
        hashed_password VARCHAR,
        is_active BOOLEAN DEFAULT TRUE,
        is_admin BOOLEAN DEFAULT FALSE,
        email_verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create user_profiles table
    CREATE TABLE IF NOT EXISTS user_profiles (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        avatar_url VARCHAR,
        preferences JSONB DEFAULT '{}',
        subscription_tier VARCHAR DEFAULT 'free',
        oauth_provider VARCHAR,
        oauth_id VARCHAR,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create teams table
    CREATE TABLE IF NOT EXISTS teams (
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        description TEXT,
        owner_id INTEGER REFERENCES users(id),
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create team_members table
    CREATE TABLE IF NOT EXISTS team_members (
        id SERIAL PRIMARY KEY,
        team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        role VARCHAR DEFAULT 'member',
        joined_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create projects table
    CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        description TEXT,
        owner_id INTEGER REFERENCES users(id),
        team_id INTEGER REFERENCES teams(id),
        settings JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create documents table
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
        name VARCHAR NOT NULL,
        content TEXT NOT NULL,
        file_path VARCHAR,
        uploaded_by INTEGER REFERENCES users(id),
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create tag_sets table
    CREATE TABLE IF NOT EXISTS tag_sets (
        id SERIAL PRIMARY KEY,
        project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
        name VARCHAR NOT NULL,
        tags_json JSONB NOT NULL,
        created_by INTEGER REFERENCES users(id),
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create tags table
    CREATE TABLE IF NOT EXISTS tags (
        id SERIAL PRIMARY KEY,
        tag_set_id INTEGER REFERENCES tag_sets(id) ON DELETE CASCADE,
        name VARCHAR NOT NULL,
        definition TEXT,
        examples TEXT,
        color VARCHAR
    );

    -- Create annotations table
    CREATE TABLE IF NOT EXISTS annotations (
        id SERIAL PRIMARY KEY,
        document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users(id),
        tag_id INTEGER REFERENCES tags(id),
        text TEXT NOT NULL,
        start_pos INTEGER NOT NULL,
        end_pos INTEGER NOT NULL,
        confidence REAL,
        source VARCHAR DEFAULT 'manual',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create annotation_history table
    CREATE TABLE IF NOT EXISTS annotation_history (
        id SERIAL PRIMARY KEY,
        annotation_id INTEGER REFERENCES annotations(id) ON DELETE CASCADE,
        field_changed VARCHAR NOT NULL,
        old_value TEXT,
        new_value TEXT,
        changed_by INTEGER REFERENCES users(id),
        changed_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create validation_results table
    CREATE TABLE IF NOT EXISTS validation_results (
        id SERIAL PRIMARY KEY,
        annotation_id INTEGER REFERENCES annotations(id) ON DELETE CASCADE,
        status VARCHAR NOT NULL,
        error_message TEXT,
        fixed_automatically BOOLEAN DEFAULT FALSE,
        validated_at TIMESTAMPTZ DEFAULT NOW()
    );

    -- Create admin_accounts table
    CREATE TABLE IF NOT EXISTS admin_accounts (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        permissions JSONB DEFAULT '{}',
        created_by INTEGER REFERENCES users(id),
        created_at TIMESTAMPTZ DEFAULT NOW(),
        last_login TIMESTAMPTZ
    );
    """
    
    try:
        # Execute the SQL
        result = client.rpc('exec_sql', {'sql': create_tables_sql}).execute()
        print("✅ Database tables created successfully via Supabase!")
        
    except Exception as e:
        print(f"❌ Error creating tables via Supabase: {e}")
        print("Let's try a different approach - creating tables one by one...")
        
        # Try creating tables individually
        tables = [
            ("users", """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR UNIQUE NOT NULL,
                    name VARCHAR NOT NULL,
                    hashed_password VARCHAR,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    email_verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """),
            ("user_profiles", """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                    avatar_url VARCHAR,
                    preferences JSONB DEFAULT '{}',
                    subscription_tier VARCHAR DEFAULT 'free',
                    oauth_provider VARCHAR,
                    oauth_id VARCHAR,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
        ]
        
        for table_name, sql in tables:
            try:
                print(f"Creating {table_name} table...")
                result = client.rpc('exec_sql', {'sql': sql}).execute()
                print(f"✅ {table_name} table created")
            except Exception as table_error:
                print(f"❌ Error creating {table_name}: {table_error}")

def setup_rls_policies():
    """Set up Row Level Security policies"""
    print("🔐 Setting up RLS policies...")
    
    client = get_supabase_client()
    
    rls_sql = """
    -- Enable RLS on users table
    ALTER TABLE users ENABLE ROW LEVEL SECURITY;
    
    -- Enable RLS on projects table  
    ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
    
    -- Enable RLS on documents table
    ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
    
    -- Enable RLS on annotations table
    ALTER TABLE annotations ENABLE ROW LEVEL SECURITY;
    """
    
    try:
        result = client.rpc('exec_sql', {'sql': rls_sql}).execute()
        print("✅ RLS policies enabled!")
    except Exception as e:
        print(f"⚠️ RLS setup warning: {e}")
        print("You may need to set up RLS policies manually in the Supabase dashboard")

def create_admin_user():
    """Instructions to create admin user"""
    print("👑 Admin user setup:")
    print("""
    To create an admin user:
    1. Register a user through the API (once server is running)
    2. Go to Supabase dashboard → Database → Table Editor
    3. Find the 'users' table
    4. Edit your user record and set 'is_admin' = true
    
    Or you can do this via SQL in the Supabase SQL Editor:
    UPDATE users SET is_admin = true WHERE email = 'your-email@example.com';
    """)

if __name__ == "__main__":
    print("🚀 Setting up Supabase database (alternative method)...")
    
    # Check if Supabase is configured
    if not settings.supabase_url or not settings.supabase_anon_key:
        print("❌ Supabase URL and keys not configured in .env file")
        exit(1)
    
    try:
        create_tables_via_supabase()
        setup_rls_policies()
        create_admin_user()
        print("✅ Supabase setup complete!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\n💡 Alternative approach:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Create tables manually using the SQL from this script")
        exit(1)
