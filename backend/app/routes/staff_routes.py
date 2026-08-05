"""
Staff routes - manage team members.
Admin can create staff with username/password, edit, and delete.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Staff, ActivityLog
from app.schemas import StaffCreate
from app.auth import verify_token, hash_password

router = APIRouter(prefix="/api/staff", tags=["Staff"])
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
def list_staff(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    staff_list = db.query(Staff).all()
    return [
        {"id": s.id, "user_id": s.user_id,
         "name": s.user.full_name if s.user else "Unknown",
         "username": s.user.username if s.user else "",
         "initials": "".join([w[0] for w in (s.user.full_name or "").split()[:2]]),
         "role": s.role, "specialization": s.specialization,
         "phone": s.phone, "is_available": s.is_available, "daily_rate": s.daily_rate}
        for s in staff_list
    ]


@router.post("")
def create_staff(data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new staff member with username/password.
    Admin only. Creates both a User account and Staff record.
    """
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add staff")

    # Check if username already exists
    username = data.get("username", "").strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Username '{username}' already exists")

    password = data.get("password", "")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    full_name = data.get("full_name", "").strip()
    if not full_name:
        raise HTTPException(status_code=400, detail="Full name is required")

    # Create user account
    new_user = User(
        username=username,
        email=data.get("email", f"{username}@teamshadow.com"),
        hashed_password=hash_password(password),
        full_name=full_name,
        role=data.get("role", "photographer")
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create staff record
    staff = Staff(
        user_id=new_user.id,
        role=data.get("role", "photographer"),
        specialization=data.get("specialization"),
        phone=data.get("phone"),
        daily_rate=data.get("daily_rate", 0)
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)

    log = ActivityLog(
        user_id=user.id,
        action="staff_created",
        entity_type="staff",
        entity_id=staff.id,
        description=f"Created staff: {full_name} ({username})"
    )
    db.add(log)
    db.commit()

    return {
        "id": staff.id,
        "user_id": new_user.id,
        "username": username,
        "message": f"Staff '{full_name}' created successfully. They can login with username '{username}'"
    }


@router.put("/{staff_id}")
def update_staff(staff_id: int, data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update staff details. Admin only."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update staff")

    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    # Update staff fields
    for key in ['role', 'specialization', 'phone', 'is_available', 'daily_rate']:
        if key in data and data[key] is not None:
            setattr(staff, key, data[key])

    # Update linked user if provided
    if staff.user:
        if data.get("full_name"):
            staff.user.full_name = data["full_name"]
        if data.get("email"):
            staff.user.email = data["email"]
        if data.get("password"):
            staff.user.hashed_password = hash_password(data["password"])
        if data.get("role"):
            staff.user.role = data["role"]

    db.commit()

    log = ActivityLog(
        user_id=user.id,
        action="staff_updated",
        entity_type="staff",
        entity_id=staff.id,
        description=f"Updated staff: {staff.user.full_name if staff.user else staff_id}"
    )
    db.add(log)
    db.commit()

    return {"message": "Staff updated successfully"}


@router.delete("/{staff_id}")
def delete_staff(staff_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete staff. Admin only."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete staff")

    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    # Delete the linked user account too
    if staff.user:
        db.delete(staff.user)

    db.delete(staff)
    db.commit()
    return {"message": "Staff deleted successfully"}