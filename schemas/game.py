from pydantic import BaseModel, Field, ConfigDict, AliasChoices
from typing import Optional, List, Dict
from enum import Enum

class WinMetric(str, Enum):
    ROUNDS = "rounds"
    POINTS = "points"
    BOTH = "both"

class WinCondition(str, Enum):
    HIGHEST = "highest"
    LOWEST = "lowest"

class GameMode(str, Enum):
    SUDDEN_DEATH = "sudden-death"
    ELIMINATION = "elimination"

class GameConfig(BaseModel):
    winMetric: WinMetric
    targetRounds: int
    targetPoints: int
    winCondition: WinCondition
    gameMode: GameMode

class Player(BaseModel):
    id: str
    name: str
    scores: List[int]
    totalScore: int

class Round(BaseModel):
    roundNumber: int
    scores: Dict[str, int]

class GameBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    name: str
    config: GameConfig
    players: List[Player]
    rounds: List[Round]
    currentRound: int = Field(validation_alias=AliasChoices("currentRound", "current_round"), serialization_alias="current_round")
    winner: Optional[str] = None

class GameCreate(GameBase):
    pass

class GameUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    players: Optional[List[Player]] = None
    rounds: Optional[List[Round]] = None
    currentRound: Optional[int] = Field(default=None, validation_alias=AliasChoices("currentRound", "current_round"), serialization_alias="current_round")
    winner: Optional[str] = None
    name: Optional[str] = None

class GameInDB(GameBase):
    id: str
    user_id: str
    created_at: str
    updated_at: str
