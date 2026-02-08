"""Authentication utilities and dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from core.config import settings
from db.supabase import supabase, create_supabase_client
from supabase import Client
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

class AuthUser:
    """Authenticated user from Supabase."""
    def __init__(self, user_id: str, email: str, client: Client):
        self.id = user_id
        self.email = email
        self.client = client  # Authenticated Supabase client

def verify_token(token: str) -> Optional[AuthUser]:
    """
    Verify JWT token using Supabase Auth API and return authenticated user with client.
    
    Args:
        token: JWT token string
        
    Returns:
        AuthUser if valid, None otherwise
    """
    try:
        # Verify token using Supabase Auth (using global client is fine for verification)
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            return None
            
        user = user_response.user
        
        # Create an authenticated client for this user
        client = create_supabase_client(token)
        
        return AuthUser(user_id=user.id, email=user.email, client=client)
        
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthUser:
    """
    FastAPI dependency to get current authenticated user.
    """
    token = credentials.credentials
    user = verify_token(token)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[AuthUser]:
    """
    FastAPI dependency to get current user if authenticated, None otherwise.
    """
    if credentials is None:
        return None
        
    token = credentials.credentials
    return verify_token(token)
