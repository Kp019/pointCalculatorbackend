"""Authentication endpoints."""
from fastapi import APIRouter, HTTPException, status, Depends
from schemas.user import UserCreate, UserResponse, Token, LoginRequest, UserUpdate
from core.auth import get_current_user, AuthUser
from db.supabase import supabase, create_supabase_client
from gotrue.errors import AuthApiError
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate):
    """
    Create a new user account.
    
    The user profile will be automatically created via database trigger.
    """
    try:
        # Use a fresh client for auth operations to avoid global state issues
        auth_client = create_supabase_client()
        
        # Sign up user with Supabase Auth
        response = auth_client.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "username": user_data.username
                }
            }
        })
        
        # Check if email verification is enabled (user created but no session)
        if response.user and not response.session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account created successfully! Please verify your email to log in."
            )
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account"
            )
        
        # Return token and user info
        return Token(
            access_token=response.session.access_token,
            token_type="bearer",
            user=UserResponse(
                id=response.user.id,
                email=response.user.email,
                username=user_data.username
            )
        )
        
    except Exception as e:
        logger.error(f"Signup failed: {e}")
        error_msg = str(e)
        if "User already registered" in error_msg:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

@router.post("/login", response_model=Token)
def login(credentials: LoginRequest):
    """Login with email and password."""
    try:
        # Use a fresh client for auth operations to avoid global state issues
        auth_client = create_supabase_client()
        
        # Sign in with Supabase Auth
        response = auth_client.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not response.user or not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Use authenticated client to fetch user profile
        user_client = create_supabase_client(response.session.access_token)
        user_profile = user_client.table("users").select("*").eq("id", response.user.id).single().execute()
        
        return Token(
            access_token=response.session.access_token,
            token_type="bearer",
            user=UserResponse(
                id=response.user.id,
                email=response.user.email,
                username=user_profile.data.get("username") if user_profile.data else None,
                avatar_url=user_profile.data.get("avatar_url") if user_profile.data else None,
                avatar_color=user_profile.data.get("avatar_color") if user_profile.data else None
            )
        )
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

@router.post("/logout")
def logout(current_user: AuthUser = Depends(get_current_user)):
    """Logout current user."""
    try:
        # Sign out from the current user's client session
        current_user.client.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: AuthUser = Depends(get_current_user)):
    """Get current user's profile."""
    try:
        # Use authenticated client from current_user
        response = current_user.client.table("users").select("*").eq("id", current_user.id).single().execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return UserResponse(
            id=response.data["id"],
            email=response.data["email"],
            username=response.data.get("username"),
            avatar_url=response.data.get("avatar_url"),
            avatar_color=response.data.get("avatar_color")
        )
        
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: AuthUser = Depends(get_current_user)
):
    """Update current user's profile."""
    try:
        # Build update data
        update_data = {}
        if user_update.username is not None:
            update_data["username"] = user_update.username
        if user_update.avatar_url is not None:
            update_data["avatar_url"] = user_update.avatar_url
        if user_update.avatar_color is not None:
            update_data["avatar_color"] = user_update.avatar_color
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Use authenticated client from current_user
        response = current_user.client.table("users").update(update_data).eq("id", current_user.id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return UserResponse(
            id=response.data[0]["id"],
            email=response.data[0]["email"],
            username=response.data[0].get("username"),
            avatar_url=response.data[0].get("avatar_url"),
            avatar_color=response.data[0].get("avatar_color")
        )
        
    except Exception as e:
        logger.error(f"Failed to update user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
