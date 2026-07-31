"""
Extra routes - users, activity, deliverables, expenses, and utility endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import User, Deliverable, Expense, ActivityLog
from app.schemas import DeliverableCreate, ExpenseCreate
from app.auth import verify_token, hash_password

router = APIRouter(tags=["Extra"])
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
# Users (Admin only)
# ============================================

@router.get("/api/users")
def list_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    users = db.query(User).all()
    return [
        {"id": u.id, "username": u.username, "email": u.email,
         "full_name": u.full_name, "role": u.role, "is_active": u.is_active}
        for u in users
    ]


@router.post("/api/users")
def create_user(data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    new_user = User(
        username=data["username"], email=data.get("email", ""),
        hashed_password=hash_password(data["password"]),
        full_name=data["full_name"], role=data.get("role", "sales")
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "message": "User created successfully"}


# ============================================
# Activity Log
# ============================================

@router.get("/api/activity")
def list_activity(limit: int = 20, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit).all()
    return [
        {"id": l.id, "user_id": l.user_id, "action": l.action, "entity_type": l.entity_type,
         "entity_id": l.entity_id, "description": l.description,
         "created_at": l.created_at.isoformat() if l.created_at else None}
        for l in logs
    ]


# ============================================
# Deliverables
# ============================================

@router.get("/api/deliverables")
def list_deliverables(booking_id: Optional[int] = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Deliverable)
    if booking_id:
        query = query.filter(Deliverable.booking_id == booking_id)
    deliverables = query.order_by(Deliverable.created_at.desc()).all()
    return [
        {"id": d.id, "booking_id": d.booking_id, "deliverable_type": d.deliverable_type,
         "description": d.description, "status": d.status,
         "delivery_date": d.delivery_date.isoformat() if d.delivery_date else None,
         "client_approved": d.client_approved, "notes": d.notes}
        for d in deliverables
    ]


@router.post("/api/deliverables")
def create_deliverable(data: DeliverableCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deliverable = Deliverable(
        booking_id=data.booking_id, deliverable_type=data.deliverable_type,
        description=data.description, notes=data.notes
    )
    db.add(deliverable)
    db.commit()
    db.refresh(deliverable)
    return {"id": deliverable.id, "message": "Deliverable added successfully"}


# ============================================
# Expenses
# ============================================

@router.get("/api/expenses")
def list_expenses(booking_id: Optional[int] = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Expense)
    if booking_id:
        query = query.filter(Expense.booking_id == booking_id)
    expenses = query.order_by(Expense.expense_date.desc()).all()
    return [
        {"id": e.id, "booking_id": e.booking_id, "category": e.category,
         "description": e.description, "amount": e.amount, "vendor_name": e.vendor_name,
         "payment_method": e.payment_method, "expense_date": e.expense_date.isoformat() if e.expense_date else None}
        for e in expenses
    ]


@router.post("/api/expenses")
def create_expense(data: ExpenseCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expense = Expense(
        booking_id=data.booking_id, category=data.category, description=data.description,
        amount=data.amount, vendor_name=data.vendor_name, payment_method=data.payment_method
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return {"id": expense.id, "message": "Expense recorded successfully"}