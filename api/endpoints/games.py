from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.game import GameCreate, GameInDB, GameUpdate
from core.auth import get_current_user, AuthUser
from db.base import get_db
from db.models import Game
from typing import List
import uuid

router = APIRouter()

@router.post("/", response_model=GameInDB, response_model_by_alias=False)
def create_game(
    game: GameCreate, 
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new game for the authenticated user."""
    try:
        game_data = game.model_dump(by_alias=True)
        
        new_game = Game(
            user_id=uuid.UUID(current_user.id),
            name=game_data["name"],
            config=game_data["config"],
            players=game_data["players"],
            rounds=game_data["rounds"],
            current_round=str(game_data.get("current_round", "1")),
            winner=game_data.get("winner")
        )
        
        db.add(new_game)
        db.commit()
        db.refresh(new_game)
        
        return new_game
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create game: {str(e)}")

@router.get("/", response_model=List[GameInDB], response_model_by_alias=False)
def get_games(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all games for the authenticated user."""
    games = db.query(Game).filter(Game.user_id == uuid.UUID(current_user.id)).order_by(Game.created_at.desc()).all()
    return games

@router.get("/{game_id}/", response_model=GameInDB, response_model_by_alias=False)
def get_game(
    game_id: str, 
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific game owned by the authenticated user."""
    game = db.query(Game).filter(
        Game.id == uuid.UUID(game_id), 
        Game.user_id == uuid.UUID(current_user.id)
    ).first()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@router.put("/{game_id}/", response_model=GameInDB, response_model_by_alias=False)
def update_game(
    game_id: str, 
    game_update: GameUpdate, 
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a game owned by the authenticated user."""
    game = db.query(Game).filter(
        Game.id == uuid.UUID(game_id), 
        Game.user_id == uuid.UUID(current_user.id)
    ).first()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    update_data = game_update.model_dump(exclude_unset=True, by_alias=True)
    
    if "name" in update_data:
        game.name = update_data["name"]
    if "config" in update_data:
        game.config = update_data["config"]
    if "players" in update_data:
        game.players = update_data["players"]
    if "rounds" in update_data:
        game.rounds = update_data["rounds"]
    if "current_round" in update_data:
        game.current_round = str(update_data["current_round"])
    if "winner" in update_data:
        game.winner = update_data["winner"]
        
    db.commit()
    db.refresh(game)
    return game

@router.delete("/{game_id}/")
def delete_game(
    game_id: str, 
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a game owned by the authenticated user."""
    game = db.query(Game).filter(
        Game.id == uuid.UUID(game_id), 
        Game.user_id == uuid.UUID(current_user.id)
    ).first()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    db.delete(game)
    db.commit()
    return {"message": "Game deleted successfully"}
