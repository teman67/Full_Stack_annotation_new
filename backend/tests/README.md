# Tests Directory

This directory contains test files for the backend application.

## Files

### Database Tests

- **`test_comprehensive_db.py`**: Comprehensive database connectivity and functionality test
- **`test_db_connection.py`**: Basic database connection test using SQLAlchemy
- **`test_supabase_client.py`**: Supabase client connection test and URL validation

## Usage

Run tests from the backend directory:

```bash
# From backend directory
python tests/test_comprehensive_db.py
python tests/test_db_connection.py
python tests/test_supabase_client.py
```

## Test Descriptions

### `test_comprehensive_db.py`

- Tests Supabase client connection
- Verifies all database tables exist
- Tests basic CRUD operations
- Provides summary of database setup status

### `test_db_connection.py`

- Tests direct PostgreSQL connection via SQLAlchemy
- Checks database version and connectivity
- Lists available tables

### `test_supabase_client.py`

- Tests Supabase client connectivity
- Validates database URL format
- Checks for URL encoding issues
