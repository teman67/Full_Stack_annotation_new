#!/usr/bin/env python3
"""
Test Supabase connection using the Supabase client
"""
import os
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from supabase import create_client, Client

async def test_supabase_connection():
    """Test connection using Supabase client"""
    
    print("🔍 Testing Supabase Client Connection...")
    print(f"Supabase URL: {settings.supabase_url}")
    print(f"Using service role key: {settings.supabase_service_role_key[:20]}...")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(
            settings.supabase_url, 
            settings.supabase_service_role_key
        )
        
        # Test connection by checking tables
        response = supabase.table('users').select('*').limit(1).execute()
        
        print("✅ Supabase client connection successful!")
        print(f"📊 Users table query successful, found {len(response.data)} records")
        
        # List all tables
        # Note: This requires a direct SQL query
        sql_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        
        # Try to run SQL query
        try:
            result = supabase.rpc('exec_sql', {'query': sql_query}).execute()
            print("SQL query test:", result)
        except Exception as e:
            print(f"SQL query failed (this is normal): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase client connection failed: {str(e)}")
        return False

def test_database_url():
    """Test and fix the database URL"""
    print("\n🔧 Testing Database URL...")
    
    # Get the raw URL
    db_url = settings.database_url
    print(f"Current DATABASE_URL: {db_url}")
    
    # Check for URL encoding issues
    if '%21' in db_url or '%40' in db_url:
        print("⚠️  Detected URL encoding in password")
        
        # Try to decode the password
        import urllib.parse
        parsed = urllib.parse.urlparse(db_url)
        
        print(f"Host: {parsed.hostname}")
        print(f"Port: {parsed.port}")
        print(f"Database: {parsed.path[1:]}")  # Remove leading /
        print(f"Username: {parsed.username}")
        
        if parsed.password:
            decoded_password = urllib.parse.unquote(parsed.password)
            print(f"Decoded password: {decoded_password}")
            
            # Suggest the corrected URL
            corrected_url = f"postgresql://{parsed.username}:{decoded_password}@{parsed.hostname}:{parsed.port}{parsed.path}"
            print(f"Suggested corrected URL: {corrected_url}")
            
            return corrected_url
    
    return db_url

if __name__ == "__main__":
    import asyncio
    
    # Test database URL
    corrected_url = test_database_url()
    
    # Test Supabase client
    asyncio.run(test_supabase_connection())
