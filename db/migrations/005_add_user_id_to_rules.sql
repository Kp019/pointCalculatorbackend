-- Add user_id column to rules table
ALTER TABLE public.rules 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES public.users(id) ON DELETE CASCADE;

-- Create index on user_id for faster filtering
CREATE INDEX IF NOT EXISTS idx_rules_user_id ON public.rules(user_id);

-- Drop existing policy
DROP POLICY IF EXISTS "Enable all operations for all users" ON public.rules;

-- Create policy: Users can view their own rules
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'rules' 
        AND policyname = 'Users can view own rules'
    ) THEN
        CREATE POLICY "Users can view own rules" ON public.rules
            FOR SELECT
            USING (auth.uid() = user_id);
    END IF;
END $$;

-- Create policy: Users can insert their own rules
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'rules' 
        AND policyname = 'Users can insert own rules'
    ) THEN
        CREATE POLICY "Users can insert own rules" ON public.rules
            FOR INSERT
            WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- Create policy: Users can update their own rules
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'rules' 
        AND policyname = 'Users can update own rules'
    ) THEN
        CREATE POLICY "Users can update own rules" ON public.rules
            FOR UPDATE
            USING (auth.uid() = user_id)
            WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;

-- Create policy: Users can delete their own rules
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'rules' 
        AND policyname = 'Users can delete own rules'
    ) THEN
        CREATE POLICY "Users can delete own rules" ON public.rules
            FOR DELETE
            USING (auth.uid() = user_id);
    END IF;
END $$;
