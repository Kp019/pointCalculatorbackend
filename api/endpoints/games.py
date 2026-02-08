from fastapi import APIRouter, HTTPException, Depends
from schemas.game import GameCreate, GameInDB, GameUpdate
from db.supabase import supabase
from core.auth import get_current_user, AuthUser
from typing import List

router = APIRouter()

@router.post("/", response_model=GameInDB, response_model_by_alias=False)
def create_game(game: GameCreate, current_user: AuthUser = Depends(get_current_user)):
    """Create a new game for the authenticated user."""
    game_data = game.model_dump(by_alias=True)
    game_data["user_id"] = current_user.id
    
    # Use authenticated client from current_user
    response = current_user.client.table("games").insert(game_data).execute()
    if len(response.data) == 0:
        raise HTTPException(status_code=400, detail="Failed to create game")
    return response.data[0]

@router.get("/", response_model=List[GameInDB], response_model_by_alias=False)
def get_games(current_user: AuthUser = Depends(get_current_user)):
    """Get all games for the authenticated user."""
    # Use authenticated client from current_user
    response = current_user.client.table("games").select("*").eq("user_id", current_user.id).order("created_at", desc=True).execute()
    return response.data

@router.get("/{game_id}", response_model=GameInDB, response_model_by_alias=False)
def get_game(game_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Get a specific game owned by the authenticated user."""
    # Use authenticated client from current_user
    response = current_user.client.table("games").select("*").eq("id", game_id).eq("user_id", current_user.id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Game not found")
    return response.data

@router.put("/{game_id}", response_model=GameInDB, response_model_by_alias=False)
def update_game(game_id: str, game: GameUpdate, current_user: AuthUser = Depends(get_current_user)):
    """Update a game owned by the authenticated user."""
    # Use authenticated client from current_user
    response = current_user.client.table("games").update(game.model_dump(exclude_unset=True, by_alias=True)).eq("id", game_id).eq("user_id", current_user.id).execute()
    if len(response.data) == 0:
        raise HTTPException(status_code=404, detail="Game not found")
    return response.data[0]

@router.delete("/{game_id}")
def delete_game(game_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Delete a game owned by the authenticated user."""
    # Use authenticated client from current_user
    response = current_user.client.table("games").delete().eq("id", game_id).eq("user_id", current_user.id).execute()
    if len(response.data) == 0:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"message": "Game deleted successfully"}
