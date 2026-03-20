"""Authentication utilities and dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy.orm import Session
from core.config import settings
from core.security import decode_access_token
from db.base import get_db
from db.models import User
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

class AuthUser:
    """Authenticated user information."""
    def __init__(self, user_id: str, email: str):
        self.id = user_id
        self.email = email

def verify_token(token: str, db: Session) -> Optional[AuthUser]:
    """
    Verify JWT token and return authenticated user from database.
    
    Args:
        token: JWT token string
        db: Database session
        
    Returns:
        AuthUser if valid, None otherwise
    """
    try:
        payload = decode_access_token(token)
        if not payload:
            return None
            
        user_id = payload.get("sub")
        if not user_id:
            return None
            
        # Fetch user from database to ensure they still exist
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
            
        return AuthUser(user_id=str(user.id), email=user.email)
        
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AuthUser:
    """
    FastAPI dependency to get current authenticated user.
    """
    token = credentials.credentials
    user = verify_token(token, db)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[AuthUser]:
    """
    FastAPI dependency to get current user if authenticated, None otherwise.
    """
    if credentials is None:
        return None
        
    token = credentials.credentials
    return verify_token(token, db)
