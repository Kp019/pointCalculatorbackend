from fastapi import APIRouter, HTTPException, Depends
from schemas.rule import SavedRuleCreate, SavedRuleInDB, SavedRuleUpdate
from db.supabase import supabase
from core.auth import get_current_user, AuthUser
from typing import List

router = APIRouter()

@router.post("/", response_model=SavedRuleInDB)
def create_rule(rule: SavedRuleCreate, current_user: AuthUser = Depends(get_current_user)):
    """Create a new rule for the authenticated user."""
    rule_data = rule.model_dump()
    rule_data["user_id"] = current_user.id
    
    # Use authenticated client from current_user
    response = current_user.client.table("rules").insert(rule_data).execute()
    if len(response.data) == 0:
        raise HTTPException(status_code=400, detail="Failed to create rule")
    return response.data[0]

@router.get("/", response_model=List[SavedRuleInDB])
def get_rules(current_user: AuthUser = Depends(get_current_user)):
    """Get all rules for the authenticated user."""
    # Use authenticated client from current_user
    response = current_user.client.table("rules").select("*").eq("user_id", current_user.id).execute()
    return response.data

@router.put("/{rule_id}", response_model=SavedRuleInDB)
def update_rule(rule_id: str, rule: SavedRuleUpdate, current_user: AuthUser = Depends(get_current_user)):
    """Update a rule owned by the authenticated user."""
    # Use authenticated client from current_user
    response = current_user.client.table("rules").update(rule.model_dump(exclude_unset=True)).eq("id", rule_id).eq("user_id", current_user.id).execute()
    if len(response.data) == 0:
        raise HTTPException(status_code=404, detail="Rule not found")
    return response.data[0]

@router.delete("/{rule_id}")
def delete_rule(rule_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Delete a rule owned by the authenticated user."""
    # Use authenticated client from current_user
    response = current_user.client.table("rules").delete().eq("id", rule_id).eq("user_id", current_user.id).execute()
    if len(response.data) == 0:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted successfully"}
