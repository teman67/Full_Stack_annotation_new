# 📋 Manual Database Setup Guide

Since the automated setup scripts can't connect to your Supabase database directly, let's set up the tables manually through the Supabase dashboard.

## 🎯 Step 1: Access Supabase SQL Editor

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `toyattjeguduxpiwpzrl`
3. Click on **"SQL Editor"** in the left sidebar
4. Click **"New Query"**

## 🗄️ Step 2: Create Database Tables

Copy and paste this SQL script into the SQL Editor and click **"Run"**:

```sql
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
```

## 🔐 Step 3: Enable Row Level Security (Optional)

Run this SQL to enable RLS policies:

```sql
-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE annotations ENABLE ROW LEVEL SECURITY;

-- Create basic RLS policies (you can customize these later)
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Users can view own projects" ON projects
    FOR SELECT USING (auth.uid()::text = owner_id::text);

CREATE POLICY "Users can create projects" ON projects
    FOR INSERT WITH CHECK (auth.uid()::text = owner_id::text);

CREATE POLICY "Users can update own projects" ON projects
    FOR UPDATE USING (auth.uid()::text = owner_id::text);

CREATE POLICY "Users can delete own projects" ON projects
    FOR DELETE USING (auth.uid()::text = owner_id::text);
```

## ✅ Step 4: Verify Tables Created

1. Go to **"Table Editor"** in the left sidebar
2. You should see all the tables listed:
   - users
   - user_profiles
   - teams
   - team_members
   - projects
   - documents
   - tag_sets
   - tags
   - annotations
   - annotation_history
   - validation_results
   - admin_accounts

## 🚀 Step 5: Test the Backend

Now you can start the FastAPI server:

```bash
uvicorn main:app --reload
```

The server should start on `http://localhost:8000`

You can access:

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 👑 Step 6: Create Admin User (After Server is Running)

1. **Register a user** through the API:

   - Go to http://localhost:8000/docs
   - Find the `/auth/register` endpoint
   - Register with your email and password

2. **Make the user admin**:
   - Go back to Supabase SQL Editor
   - Run this SQL (replace with your email):
   ```sql
   UPDATE users SET is_admin = true WHERE email = 'your-email@example.com';
   ```

## 🔧 Troubleshooting

If you get any errors:

1. **Table creation errors**: Check if the SQL ran successfully in the SQL Editor
2. **Connection errors**: Verify your DATABASE_URL in the .env file
3. **Permission errors**: Make sure RLS policies are set up correctly

## 🎉 What's Next?

Once the database is set up and the server is running:

1. **Test API endpoints** through the Swagger UI
2. **Create some sample data**
3. **Start working on the frontend**
4. **Migrate your existing Streamlit app logic**

---

**Need help?** Check the Supabase documentation or the FastAPI docs for more details.
