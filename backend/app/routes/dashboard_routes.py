"""
Dashboard routes - aggregated business overview.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models import User, Inquiry, Quotation, Booking, Payment, Staff, ActivityLog, Lead
from app.auth import verify_token

router = APIRouter(prefix="/api", tags=["Dashboard"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/dashboard")
def get_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_inquiries = db.query(Inquiry).count()
    active_leads = db.query(Inquiry).filter(Inquiry.status.in_(["new", "contacted", "qualified", "follow_up", "quotation_sent"])).count()
    total_quotations = db.query(Quotation).count()
    confirmed_bookings = db.query(Booking).filter(Booking.status == "booked").count()

    total_revenue = db.query(Payment).filter(Payment.status == "completed").with_entities(Payment.amount).all()
    total_revenue = sum([r[0] for r in total_revenue]) if total_revenue else 0
    pending_payments = db.query(Booking).filter(Booking.payment_status.in_(["pending", "partial"])).count()

    channels = {}
    for source in ["instagram", "whatsapp", "website", "facebook", "google", "referral"]:
        count = db.query(Inquiry).filter(Inquiry.source == source).count()
        if count > 0:
            channels[source] = count

    recent_activity = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(10).all()

    today = date.today()
    upcoming = db.query(Booking).filter(
        Booking.event_date >= today,
        Booking.status.in_(["booked", "advance_received", "event_scheduled"])
    ).order_by(Booking.event_date).limit(5).all()

    team_stats = []
    staff_members = db.query(Staff).all()
    for s in staff_members:
        count = db.query(Inquiry).filter(Inquiry.assigned_to == s.user_id).count()
        team_stats.append({
            "name": s.user.full_name if s.user else "Unknown",
            "initials": "".join([w[0] for w in (s.user.full_name or "").split()[:2]]),
            "role": s.role,
            "inquiry_count": count
        })

    # LeadFlow AI stats
    total_leads = db.query(Lead).count()
    new_leads = db.query(Lead).filter(Lead.status == "new_lead").count()
    qualified_leads = db.query(Lead).filter(Lead.status == "qualified").count()
    won_leads = db.query(Lead).filter(Lead.status == "booked").count()
    lost_leads = db.query(Lead).filter(Lead.status == "lost").count()
    follow_ups = db.query(Lead).filter(
        Lead.status.in_(["new_lead", "qualified", "contacted"])
    ).count()
    conversion_rate = round((won_leads / total_leads * 100), 1) if total_leads > 0 else 0

    return {
        "total_inquiries": total_inquiries,
        "active_leads": active_leads,
        "total_quotations": total_quotations,
        "confirmed_bookings": confirmed_bookings,
        "total_revenue": total_revenue,
        "pending_payments": pending_payments,
        "total_leads": total_leads,
        "new_leads": new_leads,
        "qualified_leads": qualified_leads,
        "won_leads": won_leads,
        "lost_leads": lost_leads,
        "follow_ups_pending": follow_ups,
        "conversion_rate": conversion_rate,
        "channels": channels,
        "recent_activity": [
            {"id": a.id, "action": a.action, "entity_type": a.entity_type,
             "description": a.description, "created_at": a.created_at.isoformat() if a.created_at else None}
            for a in recent_activity
        ],
        "upcoming_events": [
            {"id": b.id, "customer_name": b.customer.name if b.customer else "Unknown",
             "event_type": b.event_type, "event_date": b.event_date.isoformat() if b.event_date else None,
             "venue": b.venue, "status": b.status}
            for b in upcoming
        ],
        "team_stats": team_stats
    }