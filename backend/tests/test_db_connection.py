#!/usr/bin/env python3
"""
Test database connection and verify tables exist
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import async_engine
from sqlalchemy import text
import asyncpg

async def test_database_connection():
    """Test the database connection and check if tables exist"""
    
    print("🔍 Testing Supabase Database Connection...")
    print(f"Database URL: {settings.database_url[:50]}...")
    
    try:
        # Test async connection
        if async_engine:
            async with async_engine.begin() as conn:
                # Test basic connection
                result = await conn.execute(text("SELECT version()"))
                version = result.fetchone()
                print(f"✅ Database connection successful!")
                print(f"📊 PostgreSQL version: {version[0][:50]}...")
                
                # Check if our tables exist
                tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
                """
                
                result = await conn.execute(text(tables_query))
                tables = [row[0] for row in result.fetchall()]
                
                print(f"\n📋 Found {len(tables)} tables in database:")
                for table in tables:
                    print(f"  - {table}")
                
                # Check for our expected tables
                expected_tables = [
                    'users', 'user_profiles', 'teams', 'team_members', 
                    'projects', 'documents', 'annotations', 
                    'auto_detected_entities', 'entity_sources', 
                    'tags', 'tagsets', 'export_records'
                ]
                
                missing_tables = [table for table in expected_tables if table not in tables]
                
                if missing_tables:
                    print(f"\n⚠️  Missing tables: {missing_tables}")
                    print("You may need to run the SQL setup script from MANUAL_SETUP.md")
                else:
                    print(f"\n✅ All expected tables found!")
                
                # Test a simple query on users table if it exists
                if 'users' in tables:
                    users_result = await conn.execute(text("SELECT COUNT(*) FROM users"))
                    user_count = users_result.fetchone()[0]
                    print(f"👥 Users table has {user_count} records")
                
                return True
                
        else:
            print("❌ Database engine not configured")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if your DATABASE_URL in .env is correct")
        print("2. Verify your Supabase database password")
        print("3. Ensure your Supabase project is not paused")
        return False

if __name__ == "__main__":
    asyncio.run(test_database_connection())
