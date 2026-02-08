from supabase import create_client, Client, ClientOptions
from core.config import settings

def create_supabase_client(token: str = None) -> Client:
    """
    Create a new Supabase client instance.
    
    Args:
        token: Optional JWT token to authenticate the client with.
        
    Returns:
        Client: Supabase client instance.
    """
    options = ClientOptions(persist_session=False)
    if token:
        options.headers.update({"Authorization": f"Bearer {token}"})
            
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY, options=options)

# Global anonymous client for generic access
# Note: Do not use this for user-specific operations that require RLS
supabase: Client = create_client(
    settings.SUPABASE_URL, 
    settings.SUPABASE_KEY,
    options=ClientOptions(persist_session=False)
)
