"""
Supabase Database Setup Script

This script creates the necessary tables and RLS policies in your Supabase database.
Run this after setting up your Supabase project and updating the .env file.
"""

import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.models import Base

def create_tables():
    """Create all tables in Supabase database"""
    print("🗄️ Creating database tables...")
    
    # Create engine with Supabase connection
    engine = create_engine(settings.database_url)
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Enable RLS and create policies
        with engine.connect() as connection:
            # Enable RLS on users table
            connection.execute(text("ALTER TABLE users ENABLE ROW LEVEL SECURITY;"))
            
            # Create RLS policy for users
            connection.execute(text("""
                CREATE POLICY "Users can view own data" ON users
                FOR SELECT USING (auth.uid()::text = id::text);
            """))
            
            connection.execute(text("""
                CREATE POLICY "Users can update own data" ON users
                FOR UPDATE USING (auth.uid()::text = id::text);
            """))
            
            # Enable RLS on projects table
            connection.execute(text("ALTER TABLE projects ENABLE ROW LEVEL SECURITY;"))
            
            # Create RLS policy for projects
            connection.execute(text("""
                CREATE POLICY "Users can view own projects" ON projects
                FOR SELECT USING (auth.uid()::text = owner_id::text);
            """))
            
            connection.execute(text("""
                CREATE POLICY "Users can create projects" ON projects
                FOR INSERT WITH CHECK (auth.uid()::text = owner_id::text);
            """))
            
            connection.execute(text("""
                CREATE POLICY "Users can update own projects" ON projects
                FOR UPDATE USING (auth.uid()::text = owner_id::text);
            """))
            
            connection.execute(text("""
                CREATE POLICY "Users can delete own projects" ON projects
                FOR DELETE USING (auth.uid()::text = owner_id::text);
            """))
            
            connection.commit()
            print("✅ RLS policies created successfully!")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

def create_admin_user():
    """Create initial admin user"""
    print("👑 Creating admin user...")
    
    # This would typically be done through Supabase dashboard or auth API
    # For now, we'll just print instructions
    print("""
    ℹ️ To create an admin user:
    1. Go to your Supabase dashboard
    2. Navigate to Authentication > Users
    3. Create a new user with your admin email
    4. Update the users table to set is_admin = true for this user
    
    Or use the Supabase CLI:
    supabase gen types typescript --local > types/supabase.ts
    """)

if __name__ == "__main__":
    print("🚀 Setting up Supabase database...")
    
    # Check if required environment variables are set
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "DATABASE_URL"]
    missing_vars = [var for var in required_vars if not getattr(settings, var.lower(), None)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with Supabase credentials.")
        exit(1)
    
    try:
        create_tables()
        create_admin_user()
        print("✅ Supabase setup complete!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        exit(1)
