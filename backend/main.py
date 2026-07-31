from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import Optional
from pydantic import BaseModel
import secrets

from database import (
    init_db, SessionLocal,
    User, Customer, Inquiry, Quotation, Booking, Payment,
    Staff, EditingProject, Deliverable, Expense, ActivityLog,
    hash_password, verify_password
)

app = FastAPI(title="Team Shadow Weddings - CRM API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

from jose import jwt, JWTError

SECRET_KEY = "teamshadow-wedding-crm-secret-key-2024-very-secure"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(days=7)})
    # Ensure sub is a string
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ============================================
# Pydantic Schemas (v2 compatible)
# ============================================

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    bride_name: Optional[str] = None
    groom_name: Optional[str] = None
    wedding_date: Optional[str] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class InquiryCreate(BaseModel):
    customer_id: int
    source: str
    message: Optional[str] = None
    status: str = "new"
    assigned_to: Optional[int] = None
    event_type: Optional[str] = None
    event_date: Optional[str] = None
    guest_count: Optional[int] = None
    budget_estimate: Optional[float] = None
    notes: Optional[str] = None

class QuotationCreate(BaseModel):
    customer_id: int
    inquiry_id: Optional[int] = None
    package_name: Optional[str] = None
    services: Optional[list] = None
    base_amount: float = 0
    discount: float = 0
    discount_type: str = "percentage"
    gst: float = 0
    notes: Optional[str] = None
    valid_until: Optional[str] = None

class BookingCreate(BaseModel):
    customer_id: int
    quotation_id: Optional[int] = None
    total_amount: float = 0
    advance_amount: float = 0
    event_date: Optional[str] = None
    event_type: Optional[str] = None
    venue: Optional[str] = None
    notes: Optional[str] = None

class PaymentCreate(BaseModel):
    booking_id: int
    amount: float
    payment_type: str
    payment_method: str = "cash"
    transaction_id: Optional[str] = None
    notes: Optional[str] = None

class StaffCreate(BaseModel):
    user_id: int
    role: str
    specialization: Optional[str] = None
    phone: Optional[str] = None
    daily_rate: float = 0

class EditingProjectCreate(BaseModel):
    booking_id: int
    editor_id: Optional[int] = None
    designer_id: Optional[int] = None
    reviewer_id: Optional[int] = None
    editing_notes: Optional[str] = None

class DeliverableCreate(BaseModel):
    booking_id: int
    deliverable_type: str
    description: Optional[str] = None
    notes: Optional[str] = None

class ExpenseCreate(BaseModel):
    booking_id: Optional[int] = None
    category: str
    description: str
    amount: float
    vendor_name: Optional[str] = None
    payment_method: Optional[str] = None

# ============================================
# Auth Routes
# ============================================

@app.post("/api/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    )

@app.get("/api/auth/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role
    }

# ============================================
# Dashboard
# ============================================

@app.get("/api/dashboard")
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
    
    return {
        "total_inquiries": total_inquiries,
        "active_leads": active_leads,
        "total_quotations": total_quotations,
        "confirmed_bookings": confirmed_bookings,
        "total_revenue": total_revenue,
        "pending_payments": pending_payments,
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

# ============================================
# Customers
# ============================================

@app.get("/api/customers")
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

@app.post("/api/customers")
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
    log = ActivityLog(user_id=user.id, action="created", entity_type="customer", entity_id=customer.id, description=f"Created customer: {customer.name}")
    db.add(log)
    db.commit()
    return {"id": customer.id, "name": customer.name, "message": "Customer created successfully"}

@app.get("/api/customers/{customer_id}")
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
        "inquiries": [{"id": i.id, "source": i.source, "status": i.status, "event_type": i.event_type, "created_at": i.created_at.isoformat() if i.created_at else None} for i in customer.inquiries],
        "bookings": [{"id": b.id, "booking_number": b.booking_number, "status": b.status, "total_amount": b.total_amount, "event_date": b.event_date.isoformat() if b.event_date else None} for b in customer.bookings],
        "quotations": [{"id": q.id, "quote_number": q.quote_number, "total_amount": q.total_amount, "status": q.status, "created_at": q.created_at.isoformat() if q.created_at else None} for q in customer.quotations]
    }

# ============================================
# Inquiries
# ============================================

@app.get("/api/inquiries")
def list_inquiries(status: Optional[str] = None, source: Optional[str] = None, assigned_to: Optional[str] = None, search: Optional[str] = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
        {"id": i.id, "customer": {"id": i.customer.id, "name": i.customer.name, "phone": i.customer.phone} if i.customer else None,
         "source": i.source, "message": i.message, "status": i.status, "event_type": i.event_type,
         "event_date": i.event_date.isoformat() if i.event_date else None,
         "guest_count": i.guest_count, "budget_estimate": i.budget_estimate,
         "assigned_to": {"id": i.assignee.id, "full_name": i.assignee.full_name, "initials": "".join([w[0] for w in (i.assignee.full_name or "").split()[:2]])} if i.assignee else None,
         "notes": i.notes, "last_contacted": i.last_contacted.isoformat() if i.last_contacted else None,
         "created_at": i.created_at.isoformat() if i.created_at else None}
        for i in inquiries
    ]

@app.post("/api/inquiries")
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

@app.put("/api/inquiries/{inquiry_id}")
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
    log = ActivityLog(user_id=user.id, action="updated", entity_type="inquiry", entity_id=inquiry.id, description=f"Updated inquiry #{inquiry.id}")
    db.add(log)
    db.commit()
    return {"message": "Inquiry updated successfully"}

@app.delete("/api/inquiries/{inquiry_id}")
def delete_inquiry(inquiry_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    db.delete(inquiry)
    db.commit()
    return {"message": "Inquiry deleted successfully"}

# ============================================
# Quotations
# ============================================

@app.get("/api/quotations")
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

@app.post("/api/quotations")
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
    return {"id": quotation.id, "quote_number": quote_number, "total_amount": total, "message": "Quotation created successfully"}

@app.put("/api/quotations/{quotation_id}/send")
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

# ============================================
# Bookings
# ============================================

@app.get("/api/bookings")
def list_bookings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()
    return [
        {"id": b.id, "booking_number": b.booking_number,
         "customer": {"id": b.customer.id, "name": b.customer.name, "phone": b.customer.phone} if b.customer else None,
         "status": b.status, "total_amount": b.total_amount, "advance_amount": b.advance_amount,
         "balance_amount": b.balance_amount, "payment_status": b.payment_status,
         "event_date": b.event_date.isoformat() if b.event_date else None,
         "event_type": b.event_type, "venue": b.venue,
         "assigned_staff": b.assigned_staff, "agreement_signed": b.agreement_signed,
         "notes": b.notes, "created_at": b.created_at.isoformat() if b.created_at else None}
        for b in bookings
    ]

@app.post("/api/bookings")
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
    
    inquiry = db.query(Inquiry).filter(Inquiry.customer_id == data.customer_id, Inquiry.status != "lost").order_by(Inquiry.created_at.desc()).first()
    if inquiry:
        inquiry.status = "booked"
        db.commit()
    
    log = ActivityLog(user_id=user.id, action="created", entity_type="booking", entity_id=booking.id,
                     description=f"Booking confirmed: {booking_number}")
    db.add(log)
    db.commit()
    return {"id": booking.id, "booking_number": booking_number, "message": "Booking created successfully"}

@app.put("/api/bookings/{booking_id}/status")
def update_booking_status(booking_id: int, status: str = Query(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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

# ============================================
# Payments
# ============================================

@app.get("/api/payments")
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

@app.post("/api/payments")
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

# ============================================
# Staff
# ============================================

@app.get("/api/staff")
def list_staff(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    staff_list = db.query(Staff).all()
    return [
        {"id": s.id, "user_id": s.user_id,
         "name": s.user.full_name if s.user else "Unknown",
         "initials": "".join([w[0] for w in (s.user.full_name or "").split()[:2]]),
         "role": s.role, "specialization": s.specialization,
         "phone": s.phone, "is_available": s.is_available, "daily_rate": s.daily_rate}
        for s in staff_list
    ]

@app.post("/api/staff")
def create_staff(data: StaffCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    staff = Staff(user_id=data.user_id, role=data.role, specialization=data.specialization, phone=data.phone, daily_rate=data.daily_rate)
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return {"id": staff.id, "message": "Staff added successfully"}

# ============================================
# Editing Projects
# ============================================

@app.get("/api/editing-projects")
def list_editing_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.query(EditingProject).order_by(EditingProject.created_at.desc()).all()
    return [
        {"id": p.id, "booking_id": p.booking_id,
         "booking_number": p.booking.booking_number if p.booking else None,
         "customer_name": p.booking.customer.name if p.booking and p.booking.customer else None,
         "editor": {"id": p.editor.id, "full_name": p.editor.full_name} if p.editor else None,
         "designer": {"id": p.designer.id, "full_name": p.designer.full_name} if p.designer else None,
         "status": p.status, "raw_files_received": p.raw_files_received,
         "editing_notes": p.editing_notes, "client_feedback": p.client_feedback,
         "started_at": p.started_at.isoformat() if p.started_at else None,
         "completed_at": p.completed_at.isoformat() if p.completed_at else None,
         "created_at": p.created_at.isoformat() if p.created_at else None}
        for p in projects
    ]

@app.post("/api/editing-projects")
def create_editing_project(data: EditingProjectCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = EditingProject(
        booking_id=data.booking_id, editor_id=data.editor_id, designer_id=data.designer_id,
        reviewer_id=data.reviewer_id, editing_notes=data.editing_notes
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    booking = db.query(Booking).filter(Booking.id == data.booking_id).first()
    if booking:
        booking.status = "editing"
        db.commit()
    return {"id": project.id, "message": "Editing project created successfully"}

@app.put("/api/editing-projects/{project_id}/status")
def update_editing_status(project_id: int, status: str = Query(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(EditingProject).filter(EditingProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.status = status
    if status == "editing_started" and not project.started_at:
        project.started_at = datetime.utcnow()
    if status == "delivered":
        project.completed_at = datetime.utcnow()
    db.commit()
    return {"message": f"Editing status updated to {status}"}

# ============================================
# Deliverables
# ============================================

@app.get("/api/deliverables")
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

@app.post("/api/deliverables")
def create_deliverable(data: DeliverableCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    deliverable = Deliverable(booking_id=data.booking_id, deliverable_type=data.deliverable_type, description=data.description, notes=data.notes)
    db.add(deliverable)
    db.commit()
    db.refresh(deliverable)
    return {"id": deliverable.id, "message": "Deliverable added successfully"}

# ============================================
# Expenses
# ============================================

@app.get("/api/expenses")
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

@app.post("/api/expenses")
def create_expense(data: ExpenseCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expense = Expense(booking_id=data.booking_id, category=data.category, description=data.description, amount=data.amount, vendor_name=data.vendor_name, payment_method=data.payment_method)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return {"id": expense.id, "message": "Expense recorded successfully"}

# ============================================
# Activity
# ============================================

@app.get("/api/activity")
def list_activity(limit: int = 20, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit).all()
    return [
        {"id": l.id, "user_id": l.user_id, "action": l.action, "entity_type": l.entity_type,
         "entity_id": l.entity_id, "description": l.description,
         "created_at": l.created_at.isoformat() if l.created_at else None}
        for l in logs
    ]

# ============================================
# Users (Admin)
# ============================================

@app.get("/api/users")
def list_users(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    users = db.query(User).all()
    return [
        {"id": u.id, "username": u.username, "email": u.email,
         "full_name": u.full_name, "role": u.role, "is_active": u.is_active}
        for u in users
    ]

@app.post("/api/users")
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
# Initialize & Run
# ============================================

@app.on_event("startup")
def startup():
    init_db()
    db = SessionLocal()
    sample_staff = [
        {"username": "sarah", "password": "staff123", "full_name": "Sarah Johnson", "role": "sales"},
        {"username": "mike", "password": "staff123", "full_name": "Mike Chen", "role": "photographer"},
        {"username": "emma", "password": "staff123", "full_name": "Emma Wilson", "role": "editor"},
        {"username": "alex", "password": "staff123", "full_name": "Alex Rivera", "role": "videographer"},
    ]
    for s in sample_staff:
        existing = db.query(User).filter(User.username == s["username"]).first()
        if not existing:
            user = User(
                username=s["username"], email=f"{s['username']}@teamshadow.com",
                hashed_password=hash_password(s["password"]),
                full_name=s["full_name"], role=s["role"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            staff = Staff(user_id=user.id, role=s["role"])
            db.add(staff)
            db.commit()
    db.close()

@app.get("/")
def root():
    return {"message": "Team Shadow Weddings CRM API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)