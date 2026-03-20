from pydantic import BaseModel, ConfigDict
from typing import Optional
from schemas.game import GameConfig
import uuid

class SavedRuleBase(BaseModel):
    name: str
    config: GameConfig

class SavedRuleCreate(SavedRuleBase):
    pass

class SavedRuleUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[GameConfig] = None

class SavedRuleInDB(SavedRuleBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)
