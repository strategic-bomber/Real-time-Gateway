from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
import uuid
from python_api.db import SessionLocal, DealMember

router = APIRouter()

# In-memory token store for demo (Use JWT/Redis in production)
active_tokens = {}

class DemoLogin(BaseModel):
    username: str
    deal_id: str

class TokenResponse(BaseModel):
    token: str
    role: str

@router.post("/api/demo/sessions", response_model=TokenResponse)
def demo_login(data: DemoLogin):
    db = SessionLocal()
    member = db.query(DealMember).filter_by(deal_id=data.deal_id, user_id=data.username).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this deal")
    
    token = str(uuid.uuid4())
    active_tokens[token] = {
        "subject": data.username,
        "role": member.role,
        "deal_id": data.deal_id
    }
    return {"token": token, "role": member.role}

@router.post("/internal/auth/validate")
def internal_validate(authorization: str = Header(...)):
    """Called by Go Gateway to verify WSS/SSE subscriptions and publishing rights."""
    token = authorization.replace("Bearer ", "")
    if token not in active_tokens:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    user = active_tokens[token]
    return {
        "subject": user["subject"],
        "expires_at": "2099-01-01T00:00:00Z", # Mock
        "subscribe_rooms": [user["deal_id"]],
        "publish_rooms": [user["deal_id"]],
        "allow_broadcast": False
    }