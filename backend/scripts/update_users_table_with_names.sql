-- SQL script to add first_name and last_name columns to users table
-- Run this in Supabase SQL Editor if you want separate name fields

-- Add new columns
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS first_name VARCHAR,
ADD COLUMN IF NOT EXISTS last_name VARCHAR;

-- Update existing records to split the name field
UPDATE users 
SET 
    first_name = SPLIT_PART(name, ' ', 1),
    last_name = CASE 
        WHEN ARRAY_LENGTH(STRING_TO_ARRAY(name, ' '), 1) > 1 
        THEN SUBSTRING(name FROM POSITION(' ' IN name) + 1)
        ELSE ''
    END
WHERE name IS NOT NULL;

-- Optional: You can keep the name field for backward compatibility
-- or drop it if you want to use only first_name and last_name
-- ALTER TABLE users DROP COLUMN name;
