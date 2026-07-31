"""
Pydantic schemas for request/response validation.
"""
from typing import Optional
from pydantic import BaseModel


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