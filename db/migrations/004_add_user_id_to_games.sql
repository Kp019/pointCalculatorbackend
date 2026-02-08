-- Add user_id column to games table
ALTER TABLE public.games 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES public.users(id) ON DELETE CASCADE;

-- Create index on user_id for faster filtering
CREATE INDEX IF NOT EXISTS idx_games_user_id ON public.games(user_id);

-- Drop existing policy
DROP POLICY IF EXISTS "Enable all operations for all users" ON public.games;

-- Create policy: Users can view their own games
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'games' 
        AND policyname = 'Users can view own games'
    ) THEN
        CREATE POLICY "Users can view own games" ON public.games
            FOR SELECT
            USING (auth.uid() = user_id);
    END IF;
END $$;

-- Create policy: Users can insert their own games
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'games' 
        AND policyname = 'Users can insert own games'
    ) THEN
        CREATE POLICY "Users can insert own games" ON public.games
            FOR INSERT
            WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- Create policy: Users can update their own games
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'games' 
        AND policyname = 'Users can update own games'
    ) THEN
        CREATE POLICY "Users can update own games" ON public.games
            FOR UPDATE
            USING (auth.uid() = user_id)
            WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- Create policy: Users can delete their own games
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'games' 
        AND policyname = 'Users can delete own games'
    ) THEN
        CREATE POLICY "Users can delete own games" ON public.games
            FOR DELETE
            USING (auth.uid() = user_id);
    END IF;
END $$;
