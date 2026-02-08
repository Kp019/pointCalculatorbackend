from pydantic import BaseModel
from typing import Optional
from schemas.game import GameConfig

class SavedRuleBase(BaseModel):
    name: str
    config: GameConfig

class SavedRuleCreate(SavedRuleBase):
    pass

class SavedRuleUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[GameConfig] = None

class SavedRuleInDB(SavedRuleBase):
    id: str
