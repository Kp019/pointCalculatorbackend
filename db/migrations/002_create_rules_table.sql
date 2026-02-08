-- Create rules table
CREATE TABLE IF NOT EXISTS public.rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    config JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create index on created_at for faster ordering
CREATE INDEX IF NOT EXISTS idx_rules_created_at ON public.rules(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.rules ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations for now (you can restrict this later)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'rules' 
        AND policyname = 'Enable all operations for all users'
    ) THEN
        CREATE POLICY "Enable all operations for all users" ON public.rules
            FOR ALL
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_rules_updated_at ON public.rules;
CREATE TRIGGER update_rules_updated_at BEFORE UPDATE ON public.rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
