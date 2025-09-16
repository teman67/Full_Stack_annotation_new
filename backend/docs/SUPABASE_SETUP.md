# 🚀 Supabase Setup Guide

This guide will help you set up Supabase for the Scientific Text Annotator backend.

## Step 1: Create Supabase Project

1. **Go to [Supabase](https://supabase.com)**
2. **Sign up/Sign in** to your account
3. **Create a new project:**
   - Click "New Project"
   - Choose your organization
   - Name your project (e.g., "scientific-annotator")
   - Set a database password (save this!)
   - Choose a region closest to you
   - Click "Create new project"

## Step 2: Get Your Credentials

1. **Go to Project Settings:**

   - Click the gear icon (⚙️) in the sidebar
   - Go to "API" section

2. **Copy these values:**

   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)
   - **service_role key** (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

3. **Get Database URL:**
   - Go to "Database" section in settings
   - Copy the connection string
   - It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

## Step 3: Update Your Environment File

Update your `.env` file with the Supabase credentials:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database URL
DATABASE_URL=postgresql://postgres:your_password@db.your-project-ref.supabase.co:5432/postgres

# JWT Settings (use a secure secret key)
SECRET_KEY=your-very-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Environment
ENVIRONMENT=development
```

## Step 4: Install Additional Dependencies

Install the Supabase client:

```bash
pip install supabase==2.7.4 postgrest==0.16.8
```

## Step 5: Set Up Database Tables

Run the database setup script:

```bash
python setup_supabase.py
```

This will:

- Create all necessary tables
- Set up Row Level Security (RLS) policies
- Configure proper permissions

## Step 6: Enable Authentication

1. **Go to Authentication in Supabase Dashboard:**

   - Navigate to Authentication > Settings
   - Enable "Enable email confirmations" if you want email verification
   - Configure your email templates

2. **Set up OAuth (Optional):**
   - Go to Authentication > Providers
   - Enable Google, GitHub, LinkedIn as needed
   - Add redirect URLs:
     - Development: `http://localhost:3000/auth/callback`
     - Production: `https://your-domain.com/auth/callback`

## Step 7: Test the Setup

1. **Start the backend server:**

   ```bash
   uvicorn main:app --reload
   ```

2. **Test the API:**
   - Go to http://localhost:8000/docs
   - Try the health check endpoint
   - Test user registration

## Step 8: Create Admin User

1. **Register a user through the API or Supabase dashboard**

2. **Make the user an admin:**
   - Go to Supabase dashboard > Database > Table Editor
   - Find the `users` table
   - Edit your user record and set `is_admin = true`

## Troubleshooting

### Common Issues:

1. **Database connection errors:**

   ```
   Check your DATABASE_URL format
   Ensure your database password is correct
   Verify your project reference ID
   ```

2. **Authentication errors:**

   ```
   Verify SUPABASE_URL and SUPABASE_ANON_KEY
   Check if JWT tokens are properly configured
   Ensure RLS policies are set up correctly
   ```

3. **Table creation errors:**
   ```
   Check if you have proper database permissions
   Verify the database connection string
   Make sure Supabase project is active
   ```

### Useful Supabase SQL Queries:

```sql
-- Check if tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';

-- Make a user admin
UPDATE users
SET is_admin = true
WHERE email = 'your-email@example.com';

-- Check RLS policies
SELECT * FROM pg_policies WHERE tablename = 'users';
```

## Next Steps

Once Supabase is set up:

1. **Test all API endpoints**
2. **Create some sample data**
3. **Set up the frontend**
4. **Configure file storage (if needed)**
5. **Set up production deployment**

## Production Considerations

For production deployment:

1. **Enable SSL/TLS**
2. **Set up proper backup policies**
3. **Configure monitoring and alerts**
4. **Set up API rate limiting**
5. **Review and tighten RLS policies**
6. **Enable audit logging**

---

**Need Help?**

- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI + Supabase Guide](https://supabase.com/docs/guides/getting-started/tutorials/with-fastapi)
- [Authentication Guide](https://supabase.com/docs/guides/auth)
