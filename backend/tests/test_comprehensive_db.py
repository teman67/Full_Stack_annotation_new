#!/usr/bin/env python3
"""
Comprehensive database test using Supabase client
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.supabase_db import supabase_db

async def comprehensive_db_test():
    """Run comprehensive database tests"""
    
    print("🔍 Comprehensive Database Test")
    print("=" * 50)
    
    # Test 1: Basic connection
    print("\n1️⃣ Testing basic connection...")
    connection_result = await supabase_db.test_connection()
    
    if connection_result['success']:
        print(f"✅ Connection successful!")
        print(f"📊 Current user count: {connection_result.get('user_count', 0)}")
    else:
        print(f"❌ Connection failed: {connection_result['message']}")
        return False
    
    # Test 2: Check tables
    print("\n2️⃣ Checking database tables...")
    tables = await supabase_db.get_tables()
    
    print(f"📋 Found {len(tables)} tables:")
    for table in tables:
        print(f"  ✅ {table}")
    
    # Expected tables
    expected_tables = [
        'users', 'user_profiles', 'teams', 'team_members',
        'projects', 'documents', 'annotations', 'annotation_history',
        'validation_results', 'admin_accounts', 'tags', 'tag_sets'
    ]
    
    missing_tables = [table for table in expected_tables if table not in tables]
    
    if missing_tables:
        print(f"\n⚠️  Missing tables: {missing_tables}")
        print("💡 You may need to run the SQL setup script from MANUAL_SETUP.md")
    else:
        print(f"\n✅ All expected tables found!")
    
    # Test 3: Test users table operations
    print("\n3️⃣ Testing users table operations...")
    
    # Get current users
    users_result = await supabase_db.get_users()
    
    if users_result['success']:
        print(f"✅ Users query successful, found {users_result['count']} users")
        
        if users_result['data']:
            print("👥 Sample user data:")
            for user in users_result['data'][:2]:  # Show first 2 users
                print(f"  - ID: {user.get('id')}, Email: {user.get('email')}")
    else:
        print(f"❌ Users query failed: {users_result['error']}")
    
    # Test 4: Create a test user (optional)
    print("\n4️⃣ Testing user creation...")
    
    test_user_data = {
        'email': 'test@example.com',
        'name': 'Test User',
        'is_active': True,
        'is_admin': False
    }
    
    create_result = await supabase_db.create_user(test_user_data)
    
    if create_result['success']:
        print(f"✅ Test user created successfully!")
        print(f"📋 User ID: {create_result['data'].get('id')}")
    else:
        if 'duplicate key' in create_result['error'].lower():
            print(f"ℹ️  Test user already exists (this is fine)")
        else:
            print(f"❌ User creation failed: {create_result['error']}")
    
    # Final summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if connection_result['success'] and len(tables) > 0:
        print("✅ Database is properly connected and configured!")
        print("🚀 Ready to start the FastAPI server!")
        print("\nNext steps:")
        print("1. Run: python -m uvicorn main:app --reload")
        print("2. Open: http://localhost:8000/docs")
        print("3. Test API endpoints")
        return True
    else:
        print("❌ Database setup incomplete")
        print("📋 Please check the MANUAL_SETUP.md guide")
        return False

if __name__ == "__main__":
    success = asyncio.run(comprehensive_db_test())
