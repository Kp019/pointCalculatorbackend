from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.rule import SavedRuleCreate, SavedRuleInDB, SavedRuleUpdate
from core.auth import get_current_user, AuthUser
from db.base import get_db
from db.models import SavedRule
from typing import List
import uuid

router = APIRouter()

@router.post("/", response_model=SavedRuleInDB)
def create_rule(
    rule: SavedRuleCreate, 
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new rule for the authenticated user."""
    try:
        new_rule = SavedRule(
            user_id=uuid.UUID(current_user.id),
            name=rule.name,
            config=rule.config.model_dump()
        )
        
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        
        return new_rule
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create rule: {str(e)}")

@router.get("/", response_model=List[SavedRuleInDB])
def get_rules(
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all rules for the authenticated user."""
    rules = db.query(SavedRule).filter(SavedRule.user_id == uuid.UUID(current_user.id)).all()
    return rules

@router.put("/{rule_id}/", response_model=SavedRuleInDB)
def update_rule(
    rule_id: str, 
    rule_update: SavedRuleUpdate, 
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a rule owned by the authenticated user."""
    rule = db.query(SavedRule).filter(
        SavedRule.id == uuid.UUID(rule_id), 
        SavedRule.user_id == uuid.UUID(current_user.id)
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    if rule_update.name is not None:
        rule.name = rule_update.name
    if rule_update.config is not None:
        rule.config = rule_update.config.model_dump()
        
    db.commit()
    db.refresh(rule)
    return rule

@router.delete("/{rule_id}/")
def delete_rule(
    rule_id: str, 
    current_user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a rule owned by the authenticated user."""
    rule = db.query(SavedRule).filter(
        SavedRule.id == uuid.UUID(rule_id), 
        SavedRule.user_id == uuid.UUID(current_user.id)
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted successfully"}
