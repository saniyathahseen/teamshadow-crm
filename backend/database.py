from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Date
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os
import hashlib
import secrets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'teamshadow.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================
# ENUMS as constants
# ============================================
LEAD_SOURCES = ['instagram', 'whatsapp', 'website', 'facebook', 'google', 'referral', 'manual']
INQUIRY_STATUS = ['new', 'contacted', 'qualified', 'quotation_sent', 'follow_up', 'negotiation', 'booked', 'lost']
BOOKING_STATUS = ['booked', 'advance_received', 'event_scheduled', 'event_completed', 'editing', 'album_designing', 'client_approval', 'printing', 'delivered', 'closed']
PAYMENT_STATUS = ['pending', 'partial', 'paid']
STAFF_ROLES = ['admin', 'sales', 'photographer', 'videographer', 'drone_operator', 'editor', 'album_designer', 'freelancer']
EDITING_STATUS = ['raw_received', 'editing_started', 'review', 'client_review', 'approved', 'delivered']

# ============================================
# Password hashing helper (no passlib dependency)
# ============================================

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    if '$' not in hashed:
        return False
    salt, pwd_hash = hashed.split('$', 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == pwd_hash

# ============================================
# Models
# ============================================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default='sales')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, index=True)
    email = Column(String, nullable=True)
    bride_name = Column(String, nullable=True)
    groom_name = Column(String, nullable=True)
    wedding_date = Column(Date, nullable=True)
    venue = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    inquiries = relationship("Inquiry", back_populates="customer")
    bookings = relationship("Booking", back_populates="customer")
    quotations = relationship("Quotation", back_populates="customer")

class Inquiry(Base):
    __tablename__ = "inquiries"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    source = Column(String)
    message = Column(Text, nullable=True)
    status = Column(String, default='new')
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String, nullable=True)
    event_date = Column(Date, nullable=True)
    guest_count = Column(Integer, nullable=True)
    budget_estimate = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contacted = Column(DateTime, nullable=True)
    
    customer = relationship("Customer", back_populates="inquiries")
    assignee = relationship("User", foreign_keys=[assigned_to])
    quotations = relationship("Quotation", back_populates="inquiry")

class Quotation(Base):
    __tablename__ = "quotations"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    inquiry_id = Column(Integer, ForeignKey("inquiries.id"), nullable=True)
    quote_number = Column(String, unique=True)
    package_name = Column(String, nullable=True)
    services = Column(JSON, nullable=True)
    base_amount = Column(Float, default=0)
    discount = Column(Float, default=0)
    discount_type = Column(String, default='percentage')
    gst = Column(Float, default=0)
    total_amount = Column(Float, default=0)
    status = Column(String, default='draft')
    notes = Column(Text, nullable=True)
    valid_until = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    
    customer = relationship("Customer", back_populates="quotations")
    inquiry = relationship("Inquiry", back_populates="quotations")
    booking = relationship("Booking", back_populates="quotation", uselist=False)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    quotation_id = Column(Integer, ForeignKey("quotations.id"), nullable=True)
    booking_number = Column(String, unique=True)
    status = Column(String, default='booked')
    total_amount = Column(Float, default=0)
    advance_amount = Column(Float, default=0)
    balance_amount = Column(Float, default=0)
    payment_status = Column(String, default='pending')
    event_date = Column(Date, nullable=True)
    event_type = Column(String, nullable=True)
    venue = Column(String, nullable=True)
    assigned_staff = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    agreement_signed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="bookings")
    quotation = relationship("Quotation", back_populates="booking")
    payments = relationship("Payment", back_populates="booking")
    editing_projects = relationship("EditingProject", back_populates="booking")
    deliverables = relationship("Deliverable", back_populates="booking")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    amount = Column(Float)
    payment_type = Column(String)
    payment_method = Column(String)
    status = Column(String, default='pending')
    transaction_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    payment_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    booking = relationship("Booking", back_populates="payments")

class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    role = Column(String)
    specialization = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    daily_rate = Column(Float, default=0)
    joined_at = Column(Date, nullable=True)
    
    user = relationship("User")

class EditingProject(Base):
    __tablename__ = "editing_projects"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    editor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    designer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default='raw_received')
    raw_files_received = Column(Boolean, default=False)
    editing_notes = Column(Text, nullable=True)
    client_feedback = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    booking = relationship("Booking", back_populates="editing_projects")

class Deliverable(Base):
    __tablename__ = "deliverables"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    deliverable_type = Column(String)
    description = Column(String, nullable=True)
    status = Column(String, default='pending')
    delivery_date = Column(DateTime, nullable=True)
    client_approved = Column(Boolean, default=False)
    file_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    booking = relationship("Booking", back_populates="deliverables")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    category = Column(String)
    description = Column(String)
    amount = Column(Float)
    vendor_name = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    expense_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@teamshadow.com",
            hashed_password=hash_password("admin123"),
            full_name="Team Shadow Admin",
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")