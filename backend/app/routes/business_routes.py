"""
Business Routes - business profiles, knowledge base, and automation settings.
Multi-business architecture for LeadFlow AI SaaS.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import User, Business, KnowledgeBase, Automation, Lead, Conversation, ActivityLog
from app.auth import verify_token

router = APIRouter(prefix="/api", tags=["Business"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ============================================
# Business Profile
# ============================================

@router.get("/business")
def get_business(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's business profile."""
    business = db.query(Business).first()  # Single business for now
    if not business:
        # Create default business
        business = Business(
            name="Team Shadow Weddings",
            industry="wedding",
            timezone="Asia/Dubai",
            whatsapp_number="+971501234567",
            services=["Wedding Photography", "Wedding Videography", "Event Decoration", "Albums"],
            starting_price=8000,
            working_hours="10 AM - 7 PM",
            location="Dubai"
        )
        db.add(business)
        db.commit()
        db.refresh(business)

    return {
        "id": business.id,
        "name": business.name,
        "email": business.email,
        "phone": business.phone,
        "industry": business.industry,
        "timezone": business.timezone,
        "whatsapp_number": business.whatsapp_number,
        "services": business.services,
        "starting_price": business.starting_price,
        "working_hours": business.working_hours,
        "location": business.location
    }


@router.put("/business")
def update_business(data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update business profile."""
    business = db.query(Business).first()
    if not business:
        business = Business(name="Team Shadow Weddings")
        db.add(business)
        db.commit()
        db.refresh(business)

    for key, value in data.items():
        if hasattr(business, key) and value is not None:
            setattr(business, key, value)

    db.commit()
    return {"message": "Business updated successfully", "business": business.name}


# ============================================
# Knowledge Base (AI answers)
# ============================================

@router.get("/knowledge-base")
def list_knowledge(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all knowledge base items."""
    business = db.query(Business).first()
    if not business:
        return []
    items = db.query(KnowledgeBase).filter(KnowledgeBase.business_id == business.id).all()
    return [
        {
            "id": k.id,
            "question": k.question,
            "answer": k.answer,
            "keywords": k.keywords
        }
        for k in items
    ]


@router.post("/knowledge-base")
def create_knowledge(data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add a knowledge base item for AI answers."""
    business = db.query(Business).first()
    if not business:
        raise HTTPException(status_code=400, detail="Business profile not found")

    item = KnowledgeBase(
        business_id=business.id,
        question=data.get("question", ""),
        answer=data.get("answer", ""),
        keywords=data.get("keywords", [])
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "message": "Knowledge added successfully"}


@router.delete("/knowledge-base/{item_id}")
def delete_knowledge(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a knowledge base item."""
    item = db.query(KnowledgeBase).filter(KnowledgeBase.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")
    db.delete(item)
    db.commit()
    return {"message": "Knowledge deleted successfully"}


# ============================================
# Automations (Follow-ups)
# ============================================

@router.get("/automations")
def list_automations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all automation rules."""
    business = db.query(Business).first()
    if not business:
        return []
    automations = db.query(Automation).filter(Automation.business_id == business.id).all()
    return [
        {
            "id": a.id,
            "name": a.name,
            "trigger": a.trigger,
            "action": a.action,
            "delay_hours": a.delay_hours,
            "message_template": a.message_template,
            "active": a.active
        }
        for a in automations
    ]


@router.post("/automations")
def create_automation(data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create an automation rule."""
    business = db.query(Business).first()
    if not business:
        raise HTTPException(status_code=400, detail="Business profile not found")

    automation = Automation(
        business_id=business.id,
        name=data.get("name", "Follow-up"),
        trigger=data.get("trigger", "NO_CUSTOMER_REPLY"),
        action=data.get("action", "SEND_FOLLOWUP"),
        delay_hours=data.get("delay_hours", 24),
        message_template=data.get("message_template"),
        active=data.get("active", True)
    )
    db.add(automation)
    db.commit()
    db.refresh(automation)
    return {"id": automation.id, "message": "Automation created successfully"}


@router.patch("/automations/{automation_id}")
def toggle_automation(automation_id: int, data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Toggle automation on/off or update settings."""
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")

    for key, value in data.items():
        if hasattr(automation, key) and value is not None:
            setattr(automation, key, value)

    db.commit()
    return {"message": "Automation updated successfully"}


@router.delete("/automations/{automation_id}")
def delete_automation(automation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete an automation rule."""
    automation = db.query(Automation).filter(Automation.id == automation_id).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    db.delete(automation)
    db.commit()
    return {"message": "Automation deleted successfully"}


@router.post("/automations/run-follow-ups")
def run_follow_ups(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Manually trigger follow-up check for testing."""
    from app.services.automation_service import check_follow_ups
    results = check_follow_ups(db)
    return {
        "follow_ups_sent": len(results),
        "results": results
    }