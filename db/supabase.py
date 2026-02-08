from supabase import create_client, Client, ClientOptions
from core.config import settings

def create_supabase_client(token: str = None) -> Client:
    """
    Create a new Supabase client instance.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("Supabase credentials missing. Check environment variables.")
        
    options = ClientOptions(persist_session=False)
    if token:
        options.headers.update({"Authorization": f"Bearer {token}"})
            
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY, options=options)

# Global anonymous client for generic access
supabase: Client = None
if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    supabase = create_client(
        settings.SUPABASE_URL, 
        settings.SUPABASE_KEY,
        options=ClientOptions(persist_session=False)
    )
