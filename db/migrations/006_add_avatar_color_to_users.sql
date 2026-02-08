-- Add avatar_color column to users table
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS avatar_color TEXT;
