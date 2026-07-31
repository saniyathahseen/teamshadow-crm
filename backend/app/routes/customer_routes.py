"""
Customer routes - CRUD operations.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import User, Customer, ActivityLog
from app.schemas import CustomerCreate
from app.auth import verify_token

router = APIRouter(prefix="/api/customers", tags=["Customers"])
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
def list_customers(search: Optional[str] = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Customer)
    if search:
        query = query.filter(
            Customer.name.ilike(f"%{search}%") |
            Customer.phone.ilike(f"%{search}%") |
            Customer.email.ilike(f"%{search}%")
        )
    customers = query.order_by(Customer.created_at.desc()).all()
    return [
        {"id": c.id, "name": c.name, "phone": c.phone, "email": c.email,
         "bride_name": c.bride_name, "groom_name": c.groom_name,
         "wedding_date": c.wedding_date.isoformat() if c.wedding_date else None,
         "venue": c.venue, "notes": c.notes,
         "created_at": c.created_at.isoformat() if c.created_at else None}
        for c in customers
    ]


@router.post("")
def create_customer(data: CustomerCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    customer = Customer(
        name=data.name, phone=data.phone, email=data.email,
        bride_name=data.bride_name, groom_name=data.groom_name,
        wedding_date=datetime.strptime(data.wedding_date, "%Y-%m-%d").date() if data.wedding_date else None,
        venue=data.venue, address=data.address, notes=data.notes
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    log = ActivityLog(user_id=user.id, action="created", entity_type="customer", entity_id=customer.id,
                     description=f"Created customer: {customer.name}")
    db.add(log)
    db.commit()
    return {"id": customer.id, "name": customer.name, "message": "Customer created successfully"}


@router.get("/{customer_id}")
def get_customer(customer_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {
        "id": customer.id, "name": customer.name, "phone": customer.phone, "email": customer.email,
        "bride_name": customer.bride_name, "groom_name": customer.groom_name,
        "wedding_date": customer.wedding_date.isoformat() if customer.wedding_date else None,
        "venue": customer.venue, "address": customer.address, "notes": customer.notes,
        "created_at": customer.created_at.isoformat() if customer.created_at else None,
        "inquiries": [{"id": i.id, "source": i.source, "status": i.status, "event_type": i.event_type,
                      "created_at": i.created_at.isoformat() if i.created_at else None} for i in customer.inquiries],
        "bookings": [{"id": b.id, "booking_number": b.booking_number, "status": b.status,
                     "total_amount": b.total_amount, "event_date": b.event_date.isoformat() if b.event_date else None}
                     for b in customer.bookings],
        "quotations": [{"id": q.id, "quote_number": q.quote_number, "total_amount": q.total_amount,
                       "status": q.status, "created_at": q.created_at.isoformat() if q.created_at else None}
                       for q in customer.quotations]
    }