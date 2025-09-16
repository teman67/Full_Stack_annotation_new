#!/usr/bin/env python3
"""
Get Supabase project info to determine correct connection string
"""
import os
from dotenv import load_dotenv
from supabase import create_client
import re

def get_project_info():
    """Extract project info from Supabase URL"""
    load_dotenv()
    
    url = os.getenv('SUPABASE_URL')
    print(f"Supabase URL: {url}")
    
    # Extract project reference
    match = re.search(r'https://([^.]+)\.supabase\.co', url)
    if match:
        project_ref = match.group(1)
        print(f"Project Reference: {project_ref}")
        
        # Common connection string formats for different Supabase configurations
        connection_options = [
            # Direct connection (original)
            f"postgresql://postgres:14087AhB%21%40%21@db.{project_ref}.supabase.co:5432/postgres",
            
            # Session pooler (port 5432)
            f"postgresql://postgres:14087AhB%21%40%21@aws-0-us-west-1.pooler.supabase.com:5432/postgres",
            
            # Transaction pooler (port 6543) 
            f"postgresql://postgres:14087AhB%21%40%21@aws-0-us-west-1.pooler.supabase.com:6543/postgres",
            
            # IPv6 alternative using project.supabase.co format
            f"postgresql://postgres:14087AhB%21%40%21@{project_ref}.supabase.co:5432/postgres",
        ]
        
        print("\nPossible connection strings to try:")
        for i, conn_str in enumerate(connection_options, 1):
            print(f"{i}. {conn_str}")
            
        return project_ref, connection_options
    
    return None, []

def test_connection_strings():
    """Test different connection string formats"""
    import psycopg2
    from urllib.parse import quote_plus
    
    project_ref, connection_options = get_project_info()
    
    for i, conn_str in enumerate(connection_options, 1):
        print(f"\n--- Testing connection option {i} ---")
        try:
            conn = psycopg2.connect(conn_str)
            print("✅ SUCCESS! This connection string works!")
            
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"PostgreSQL version: {version[0][:50]}...")
            
            cursor.close()
            conn.close()
            
            print(f"\n🎉 Working connection string:")
            print(f"DATABASE_URL={conn_str}")
            return conn_str
            
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print("\n❌ None of the standard connection formats worked.")
    return None

if __name__ == "__main__":
    print("=== Supabase Connection String Detector ===\n")
    working_connection = test_connection_strings()
    
    if not working_connection:
        print("\n💡 Recommendations:")
        print("1. Check your Supabase dashboard for the exact connection string")
        print("2. Verify your password is correct")
        print("3. Check if Connection Pooling is enabled in your project")
        print("4. Consider using the Supabase client library instead of direct PostgreSQL")
