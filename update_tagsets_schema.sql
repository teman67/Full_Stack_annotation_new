-- Update the tagsets table to better accommodate the new tag structure
-- This script preserves your existing table but ensures it can handle the new columns

-- First, check if the tagsets table exists
SELECT EXISTS (
   SELECT FROM information_schema.tables 
   WHERE table_name = 'tagsets'
);

-- If you need to drop and recreate the tagsets table (only do this if you don't have important data)
-- DROP TABLE IF EXISTS tagsets;

-- Create or update the tagsets table
CREATE TABLE IF NOT EXISTS tagsets (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  owner_id TEXT NOT NULL, -- Using TEXT instead of UUID for simpler compatibility
  file_path TEXT,
  tags JSONB DEFAULT '[]'::jsonb, -- Will store definition and examples in this JSONB field
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Make sure RLS is enabled
ALTER TABLE tagsets ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own tagsets" ON tagsets;
DROP POLICY IF EXISTS "Users can insert their own tagsets" ON tagsets;
DROP POLICY IF EXISTS "Users can update their own tagsets" ON tagsets;
DROP POLICY IF EXISTS "Users can delete their own tagsets" ON tagsets;

-- Create policies with explicit text casting of auth.uid()
CREATE POLICY "Users can view their own tagsets" ON tagsets
  FOR SELECT USING (auth.uid()::text = owner_id);
  
CREATE POLICY "Users can insert their own tagsets" ON tagsets
  FOR INSERT WITH CHECK (auth.uid()::text = owner_id);
  
CREATE POLICY "Users can update their own tagsets" ON tagsets
  FOR UPDATE USING (auth.uid()::text = owner_id);
  
CREATE POLICY "Users can delete their own tagsets" ON tagsets
  FOR DELETE USING (auth.uid()::text = owner_id);

-- Optional: Add example record to test the structure
-- INSERT INTO tagsets (name, description, owner_id, tags)
-- VALUES (
--   'Sample Tagset', 
--   'Created from updated schema', 
--   'your-auth-uid-here',
--   '[
--     {"name": "PERSON", "color": "#FF5733", "description": "A human individual", "examples": "John Smith, Mary Jones"},
--     {"name": "ORGANIZATION", "color": "#33FF57", "description": "A company or institution", "examples": "Google Inc., United Nations"},
--     {"name": "LOCATION", "color": "#5733FF", "description": "A physical place or area", "examples": "New York, Mount Everest"}
--   ]'::jsonb
-- );

-- Check the current structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'tagsets';

-- Check policies
SELECT * FROM pg_policies WHERE tablename = 'tagsets';