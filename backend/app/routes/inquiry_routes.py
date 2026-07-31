"""
Inquiry routes - manage leads from all channels.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import User, Customer, Inquiry, ActivityLog
from app.schemas import InquiryCreate
from app.auth import verify_token

router = APIRouter(prefix="/api/inquiries", tags=["Inquiries"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("")
def list_inquiries(
    status: Optional[str] = None, source: Optional[str] = None,
    assigned_to: Optional[str] = None, search: Optional[str] = None,
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    query = db.query(Inquiry)
    if status and status != "all":
        query = query.filter(Inquiry.status == status)
    if source and source != "all":
        query = query.filter(Inquiry.source == source)
    if assigned_to and assigned_to != "all":
        if assigned_to == "unassigned":
            query = query.filter(Inquiry.assigned_to.is_(None))
        else:
            query = query.filter(Inquiry.assigned_to == int(assigned_to))
    if search:
        query = query.join(Customer).filter(
            Customer.name.ilike(f"%{search}%") | Customer.phone.ilike(f"%{search}%")
        )
    inquiries = query.order_by(Inquiry.created_at.desc()).all()
    return [
        {"id": i.id, "customer": {"id": i.customer.id, "name": i.customer.name, "phone": i.customer.phone}
         if i.customer else None,
         "source": i.source, "message": i.message, "status": i.status, "event_type": i.event_type,
         "event_date": i.event_date.isoformat() if i.event_date else None,
         "guest_count": i.guest_count, "budget_estimate": i.budget_estimate,
         "assigned_to": {"id": i.assignee.id, "full_name": i.assignee.full_name,
                        "initials": "".join([w[0] for w in (i.assignee.full_name or "").split()[:2]])}
         if i.assignee else None,
         "notes": i.notes, "last_contacted": i.last_contacted.isoformat() if i.last_contacted else None,
         "created_at": i.created_at.isoformat() if i.created_at else None}
        for i in inquiries
    ]


@router.post("")
def create_inquiry(data: InquiryCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    inquiry = Inquiry(
        customer_id=data.customer_id, source=data.source, message=data.message,
        status=data.status, assigned_to=data.assigned_to, event_type=data.event_type,
        event_date=datetime.strptime(data.event_date, "%Y-%m-%d").date() if data.event_date else None,
        guest_count=data.guest_count, budget_estimate=data.budget_estimate, notes=data.notes
    )
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    log = ActivityLog(user_id=user.id, action="created", entity_type="inquiry", entity_id=inquiry.id,
                     description=f"New inquiry from {customer.name if customer else 'Unknown'} via {data.source}")
    db.add(log)
    db.commit()
    return {"id": inquiry.id, "message": "Inquiry created successfully"}


@router.put("/{inquiry_id}")
def update_inquiry(inquiry_id: int, data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    for key, value in data.items():
        if hasattr(inquiry, key) and value is not None:
            if key == "event_date" and value:
                value = datetime.strptime(value, "%Y-%m-%d").date()
            setattr(inquiry, key, value)
    inquiry.updated_at = datetime.utcnow()
    db.commit()
    log = ActivityLog(user_id=user.id, action="updated", entity_type="inquiry", entity_id=inquiry.id,
                     description=f"Updated inquiry #{inquiry.id}")
    db.add(log)
    db.commit()
    return {"message": "Inquiry updated successfully"}


@router.delete("/{inquiry_id}")
def delete_inquiry(inquiry_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    db.delete(inquiry)
    db.commit()
    return {"message": "Inquiry deleted successfully"}