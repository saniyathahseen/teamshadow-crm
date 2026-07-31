"""
Quotation routes - create, send, and manage quotations.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import User, Inquiry, Quotation, ActivityLog
from app.schemas import QuotationCreate
from app.auth import verify_token

router = APIRouter(prefix="/api/quotations", tags=["Quotations"])
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
def list_quotations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quotations = db.query(Quotation).order_by(Quotation.created_at.desc()).all()
    return [
        {"id": q.id, "quote_number": q.quote_number,
         "customer": {"id": q.customer.id, "name": q.customer.name} if q.customer else None,
         "package_name": q.package_name, "services": q.services,
         "base_amount": q.base_amount, "discount": q.discount, "gst": q.gst,
         "total_amount": q.total_amount, "status": q.status, "notes": q.notes,
         "valid_until": q.valid_until.isoformat() if q.valid_until else None,
         "created_at": q.created_at.isoformat() if q.created_at else None,
         "sent_at": q.sent_at.isoformat() if q.sent_at else None}
        for q in quotations
    ]


@router.post("")
def create_quotation(data: QuotationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Quotation).count() + 1
    quote_number = f"TS-{datetime.now().strftime('%Y%m')}-{count:04d}"
    total = data.base_amount
    if data.discount_type == "percentage" and data.discount > 0:
        total = total - (total * data.discount / 100)
    else:
        total = total - data.discount
    if data.gst > 0:
        total = total + (total * data.gst / 100)

    quotation = Quotation(
        customer_id=data.customer_id, inquiry_id=data.inquiry_id, quote_number=quote_number,
        package_name=data.package_name, services=data.services or [],
        base_amount=data.base_amount, discount=data.discount, discount_type=data.discount_type,
        gst=data.gst, total_amount=max(0, total), notes=data.notes,
        valid_until=datetime.strptime(data.valid_until, "%Y-%m-%d").date() if data.valid_until else None
    )
    db.add(quotation)
    db.commit()
    db.refresh(quotation)

    if data.inquiry_id:
        inquiry = db.query(Inquiry).filter(Inquiry.id == data.inquiry_id).first()
        if inquiry:
            inquiry.status = "quotation_sent"
            db.commit()

    log = ActivityLog(user_id=user.id, action="created", entity_type="quotation", entity_id=quotation.id,
                     description=f"Created quotation {quote_number} for ₹{total:,.0f}")
    db.add(log)
    db.commit()
    return {"id": quotation.id, "quote_number": quote_number, "total_amount": total,
            "message": "Quotation created successfully"}


@router.put("/{quotation_id}/send")
def send_quotation(quotation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="Quotation not found")
    quotation.status = "sent"
    quotation.sent_at = datetime.utcnow()
    db.commit()
    log = ActivityLog(user_id=user.id, action="sent", entity_type="quotation", entity_id=quotation.id,
                     description=f"Sent quotation {quotation.quote_number} to client")
    db.add(log)
    db.commit()
    return {"message": "Quotation sent successfully"}