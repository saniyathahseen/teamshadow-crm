"""
Payment routes - record and track payments.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import User, Booking, Payment, ActivityLog
from app.schemas import PaymentCreate
from app.auth import verify_token

router = APIRouter(prefix="/api/payments", tags=["Payments"])
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
def list_payments(booking_id: Optional[int] = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Payment)
    if booking_id:
        query = query.filter(Payment.booking_id == booking_id)
    payments = query.order_by(Payment.payment_date.desc()).all()
    return [
        {"id": p.id, "booking_id": p.booking_id, "amount": p.amount,
         "payment_type": p.payment_type, "payment_method": p.payment_method,
         "status": p.status, "transaction_id": p.transaction_id, "notes": p.notes,
         "payment_date": p.payment_date.isoformat() if p.payment_date else None}
        for p in payments
    ]


@router.post("")
def create_payment(data: PaymentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payment = Payment(
        booking_id=data.booking_id, amount=data.amount, payment_type=data.payment_type,
        payment_method=data.payment_method, transaction_id=data.transaction_id,
        notes=data.notes, status="completed"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    booking = db.query(Booking).filter(Booking.id == data.booking_id).first()
    if booking:
        total_paid = sum([p.amount for p in booking.payments if p.status == "completed"])
        if total_paid >= booking.total_amount:
            booking.payment_status = "paid"
            booking.balance_amount = 0
        elif total_paid > 0:
            booking.payment_status = "partial"
            booking.balance_amount = booking.total_amount - total_paid
        booking.advance_amount = total_paid
        db.commit()

    log = ActivityLog(user_id=user.id, action="payment_received", entity_type="payment", entity_id=payment.id,
                     description=f"Payment of ₹{data.amount:,.0f} received for booking #{data.booking_id}")
    db.add(log)
    db.commit()
    return {"id": payment.id, "message": "Payment recorded successfully"}