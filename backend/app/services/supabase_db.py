"""
Alternative database service using Supabase client directly
This bypasses the direct PostgreSQL connection issues
"""
from typing import List, Dict, Any, Optional
from supabase import Client
from app.core.config import settings
from app.core.database import get_supabase_client

class SupabaseDBService:
    """Database service using Supabase client"""
    
    def __init__(self):
        self.client: Client = get_supabase_client()
    
    async def get_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        try:
            # Query information_schema to get table names
            # Since we can't run raw SQL, we'll check for specific tables
            tables_to_check = [
                'users', 'user_profiles', 'teams', 'team_members',
                'projects', 'documents', 'annotations', 'annotation_history',
                'validation_results', 'admin_accounts', 'tags', 'tag_sets'
            ]
            
            existing_tables = []
            
            for table in tables_to_check:
                try:
                    # Try to query the table (with limit 0 to avoid data)
                    response = self.client.table(table).select('*').limit(0).execute()
                    existing_tables.append(table)
                except Exception:
                    # Table doesn't exist or no access
                    pass
            
            return existing_tables
            
        except Exception as e:
            print(f"Error checking tables: {e}")
            return []
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the database connection"""
        try:
            # Try to access the users table
            response = self.client.table('users').select('id').limit(1).execute()
            
            return {
                'success': True,
                'message': 'Connection successful',
                'user_count': len(response.data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'error': str(e)
            }
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        try:
            response = self.client.table('users').insert(user_data).execute()
            return {
                'success': True,
                'data': response.data[0] if response.data else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_users(self, limit: int = 10) -> Dict[str, Any]:
        """Get list of users"""
        try:
            response = self.client.table('users').select('*').limit(limit).execute()
            return {
                'success': True,
                'data': response.data,
                'count': len(response.data)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
supabase_db = SupabaseDBService()
