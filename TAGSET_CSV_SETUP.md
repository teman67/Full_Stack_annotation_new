# Tagset CSV File Upload - Manual Setup Instructions

## 1. Create the Supabase Storage Bucket

Run the setup script to create the storage bucket:

```bash
cd backend
python scripts/setup_storage.py
```

## 2. Set Up Storage Policies Manually

Since the automatic policy creation might fail, follow these steps to set up policies manually:

1. Go to your [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Navigate to **Storage** in the left sidebar
4. Click on the **tagset-files** bucket
5. Go to the **Policies** tab
6. For each operation (INSERT, SELECT, UPDATE, DELETE):
   - Click **Add Policies**
   - Select the operation type
   - Choose **Policies using custom SQL**
   - Enter the policy name (e.g., "Allow users to upload their own files")
   - Enter the SQL expression: `uid() = auth.uid()`
   - Click **Save Policy**

## 3. Create the Tagsets Table (REQUIRED STEP)

**Important**: Before the CSV upload functionality will work properly, you MUST create the `tagsets` table in your Supabase database. This is a critical prerequisite step.

To create the table:

1. Go to your Supabase project dashboard
2. Navigate to "SQL Editor" (under "Database" in the left sidebar)
3. Create a new query
4. Paste the SQL below
5. Click "Run" to execute

Execute this SQL in the Supabase SQL Editor:

```sql
-- First check that users table exists and has proper ID type
SELECT data_type
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name = 'id';

-- Important: UUID type handling for Supabase Auth
--
-- Supabase Auth always uses UUID for user IDs
-- Our app handles this by converting IDs to strings for database operations
-- You have two options:
--
-- OPTION 1 (RECOMMENDED): Use TEXT type for owner_id column
-- This allows the backend to store the UUID as a string
-- and avoids type conversion issues
--
-- OPTION 2: Use UUID type and ensure proper type casting in your policies
-- This requires using explicit type casting in RLS policies (see below)

CREATE TABLE tagsets (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  owner_id TEXT NOT NULL, -- Using TEXT instead of UUID for simpler compatibility
  file_path TEXT,
  tags JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add RLS policies for tagsets table
ALTER TABLE tagsets ENABLE ROW LEVEL SECURITY;

-- Policy to allow users to view their own tagsets
-- Note the cast of auth.uid() to text for proper comparison
CREATE POLICY "Users can view their own tagsets" ON tagsets
  FOR SELECT USING (auth.uid()::text = owner_id);

-- Policy to allow users to insert their own tagsets
CREATE POLICY "Users can insert their own tagsets" ON tagsets
  FOR INSERT WITH CHECK (auth.uid()::text = owner_id);

-- Policy to allow users to update their own tagsets
CREATE POLICY "Users can update their own tagsets" ON tagsets
  FOR UPDATE USING (auth.uid()::text = owner_id);

-- Policy to allow users to delete their own tagsets
CREATE POLICY "Users can delete their own tagsets" ON tagsets
  FOR DELETE USING (auth.uid()::text = owner_id);
```

> **Important UUID Type Note**: If you choose to use UUID type for the owner_id column, make sure to modify the policies accordingly:
>
> ```sql
> -- If using UUID type for owner_id:
> CREATE POLICY "Users can view their own tagsets" ON tagsets
>   FOR SELECT USING (auth.uid() = owner_id);
> ```

## 4. Start the Backend Server

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 5. Start the Frontend Server

```bash
cd frontend
npm run dev
```

## 6. Usage

1. Navigate to the tagsets page in your application
2. Click the **Import CSV** button
3. Enter a name for the tagset
4. Select a CSV file that follows the **EXACT** required format:
   - **MUST** have these exact headers: `tag_name`, `definition`, `examples`
   - Headers are case-sensitive and must match exactly
   - Each row represents one tag

Example CSV content (copy and paste this format):

```csv
tag_name,definition,examples
PERSON,A human individual,John Smith, Mary Jones
ORGANIZATION,A company or institution,Google Inc., United Nations
LOCATION,A physical place or area,New York, Mount Everest
```

> ⚠️ **COMMON ERROR**: If you see "Missing required columns", check that your CSV headers match exactly as shown above.

## 7. Troubleshooting

### Row-level Security Policy Violations

If you see an error about "violating row-level security policy":

1. Verify the SQL setup in step 3 was completed
2. Check that RLS is enabled on the tagsets table
3. Confirm the RLS policies are correctly set up
4. Ensure you're logged in with a valid user account

### UUID Type Issues

If you encounter type compatibility errors:

1. Check the data type of the `owner_id` column in the `tagsets` table:

   ```sql
   SELECT column_name, data_type FROM information_schema.columns
   WHERE table_name = 'tagsets' AND column_name = 'owner_id';
   ```

2. If using TEXT type (recommended):
   - Make sure all RLS policies use the cast `auth.uid()::text` for comparison
3. If using UUID type:
   - Ensure proper reference to auth.users(id)
   - Make sure RLS policies use auth.uid() without casting

### CSV Format Issues

If your CSV file is not being processed correctly:

1. Check that your CSV has the required headers: `tag_name`, `definition`, `examples`
2. Verify there are no extra quotes or special characters
3. Make sure each tag name is unique within the CSV file
4. Fill in the name and description for your tagset
5. Select a CSV file with the format: `tag_name,definition,examples`
6. Click Upload

Your CSV file will be stored in Supabase storage with proper user-based access controls, ensuring only the user who uploaded the file can access it later.

## Troubleshooting

If you encounter issues:

1. Check the browser console for any error messages
2. Verify that all storage policies are correctly set up in the Supabase dashboard
3. Make sure the tagsets table exists and has the proper RLS policies
4. Confirm that your backend API is running and accessible

### Fixing Backend Start Issues

If you get an import error when starting the backend:

1. Make sure the tagsets table is created first (Step 3)
2. Try restarting the server

If you get specific errors about imports or dependencies:

```
# Fix circular import issues (if any)
cd backend
python -c "from app.api.tagsets_supabase import router"
```

If there are issues with the `get_current_user` function, you can update the import in `tagsets_supabase.py` to use the function from the main.py file directly.

### API Path Issues

If you see 404 errors like `GET /api/api/tagsets HTTP/1.1 404 Not Found` in your backend terminal:

1. Check the frontend API client (`src/lib/api/tagsets.ts`) to ensure it's not adding an extra `/api` prefix
2. The correct paths should be:
   - `/tagsets` (not `/api/tagsets`)
   - `/tagsets/upload-csv` (not `/api/tagsets/upload-csv`)

This happens because the `client.ts` file already sets the baseURL to include `/api`.

### Database Type Errors

If you see errors like `invalid input syntax for type integer: "uuid-string"`:

This means there's a type mismatch between your database columns and the data you're trying to store. The Supabase Auth user IDs are UUIDs (strings like "5adb01e4-e12a-4b90-8830-7ce4e0ed69d8"), but your database table might be expecting integers.

**You MUST fix this before the application will work correctly!**

Execute this SQL in the Supabase SQL Editor:

```sql
-- RECOMMENDED SOLUTION:
-- Instead of modifying the users table (which can cause errors),
-- we'll create the tagsets table to work with TEXT owner_id
-- This approach avoids UUID casting issues completely

-- If the tagsets table already exists with the wrong type, drop it
-- (only if you don't have important data in it)
DROP TABLE IF EXISTS tagsets;

-- Create the tagsets table with TEXT owner_id
CREATE TABLE tagsets (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  owner_id TEXT NOT NULL, -- Using TEXT instead of UUID for compatibility
  file_path TEXT,
  tags JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Check the structure to confirm
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'tagsets'
AND column_name = 'owner_id';

-- Add RLS policies for the tagsets table with proper type casting:
ALTER TABLE tagsets ENABLE ROW LEVEL SECURITY;

-- First remove any existing policies if they exist:
DROP POLICY IF EXISTS "Users can view their own tagsets" ON tagsets;
DROP POLICY IF EXISTS "Users can insert their own tagsets" ON tagsets;
DROP POLICY IF EXISTS "Users can update their own tagsets" ON tagsets;
DROP POLICY IF EXISTS "Users can delete their own tagsets" ON tagsets;

-- Create policies with explicit text casting of auth.uid()
-- This is CRITICAL for proper functioning with UUID user IDs
CREATE POLICY "Users can view their own tagsets" ON tagsets
  FOR SELECT USING (auth.uid()::text = owner_id);

CREATE POLICY "Users can insert their own tagsets" ON tagsets
  FOR INSERT WITH CHECK (auth.uid()::text = owner_id);

CREATE POLICY "Users can update their own tagsets" ON tagsets
  FOR UPDATE USING (auth.uid()::text = owner_id);

CREATE POLICY "Users can delete their own tagsets" ON tagsets
  FOR DELETE USING (auth.uid()::text = owner_id);
```

> ⚠️ **IMPORTANT**: The error message `"invalid input syntax for type integer: "5adb01e4-e12a-4b90-8830-7ce4e0ed69d8"` means your users table has the wrong ID type. The solution above avoids modifying the users table directly (which can cause errors like `cannot cast type integer to uuid`) and instead adapts the tagsets table to work with the existing users table.
>
> If you encounter the error `ERROR: 42846: cannot cast type integer to uuid`, this means PostgreSQL cannot directly convert integers to UUIDs. The solution is to use TEXT type for owner_id and cast auth.uid() to text in policies.
