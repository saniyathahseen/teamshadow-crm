"""
Booking routes - manage confirmed bookings and their lifecycle.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import User, Inquiry, Booking, ActivityLog
from app.schemas import BookingCreate
from app.auth import verify_token

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])
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
def list_bookings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()
    return [
        {"id": b.id, "booking_number": b.booking_number,
         "customer": {"id": b.customer.id, "name": b.customer.name, "phone": b.customer.phone}
         if b.customer else None,
         "status": b.status, "total_amount": b.total_amount, "advance_amount": b.advance_amount,
         "balance_amount": b.balance_amount, "payment_status": b.payment_status,
         "event_date": b.event_date.isoformat() if b.event_date else None,
         "event_type": b.event_type, "venue": b.venue,
         "assigned_staff": b.assigned_staff, "agreement_signed": b.agreement_signed,
         "notes": b.notes, "created_at": b.created_at.isoformat() if b.created_at else None}
        for b in bookings
    ]


@router.post("")
def create_booking(data: BookingCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Booking).count() + 1
    booking_number = f"BK-{datetime.now().strftime('%Y%m')}-{count:04d}"
    booking = Booking(
        customer_id=data.customer_id, quotation_id=data.quotation_id, booking_number=booking_number,
        total_amount=data.total_amount, advance_amount=data.advance_amount,
        balance_amount=data.total_amount - data.advance_amount,
        event_date=datetime.strptime(data.event_date, "%Y-%m-%d").date() if data.event_date else None,
        event_type=data.event_type, venue=data.venue, notes=data.notes
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    inquiry = db.query(Inquiry).filter(
        Inquiry.customer_id == data.customer_id, Inquiry.status != "lost"
    ).order_by(Inquiry.created_at.desc()).first()
    if inquiry:
        inquiry.status = "booked"
        db.commit()

    log = ActivityLog(user_id=user.id, action="created", entity_type="booking", entity_id=booking.id,
                     description=f"Booking confirmed: {booking_number}")
    db.add(log)
    db.commit()
    return {"id": booking.id, "booking_number": booking_number, "message": "Booking created successfully"}


@router.put("/{booking_id}/status")
def update_booking_status(booking_id: int, status: str = Query(...),
                          user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = status
    booking.updated_at = datetime.utcnow()
    db.commit()
    log = ActivityLog(user_id=user.id, action="status_changed", entity_type="booking", entity_id=booking.id,
                     description=f"Booking {booking.booking_number} status changed to {status}")
    db.add(log)
    db.commit()
    return {"message": f"Booking status updated to {status}"}