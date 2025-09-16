#!/usr/bin/env python3
"""
Test Supabase client connectivity
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

def test_supabase_client():
    """Test Supabase client connection"""
    load_dotenv()
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"Testing Supabase client connection...")
    print(f"URL: {url}")
    print(f"Key: {key[:20]}...")
    
    try:
        supabase: Client = create_client(url, key)
        
        # Test connection with a simple query to existing tables
        response = supabase.table('annotation_history').select('*').limit(1).execute()
        print("✅ Supabase client connection successful!")
        print(f"Tables accessible: annotation_history")
        return True
        
    except Exception as e:
        print(f"❌ Supabase client connection failed: {e}")
        return False

if __name__ == "__main__":
    test_supabase_client()
