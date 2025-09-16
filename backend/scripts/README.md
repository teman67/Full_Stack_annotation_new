# Scripts Directory

This directory contains setup and utility scripts for the backend.

## Files

### Database Setup Scripts

- **`setup_supabase.py`**: Main database setup script using direct PostgreSQL connection
- **`setup_supabase_alt.py`**: Alternative setup script using Supabase client (recommended if direct connection fails)

### Platform Scripts

- **`setup.bat`**: Windows setup script
- **`setup.sh`**: Unix/Linux setup script

## Usage

To set up the database, run one of the setup scripts from the backend directory:

```bash
# From backend directory
python scripts/setup_supabase.py
# OR
python scripts/setup_supabase_alt.py
```

For platform setup:

```bash
# Windows
./scripts/setup.bat

# Unix/Linux/Mac
./scripts/setup.sh
```
