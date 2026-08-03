"""
Staff routes - manage team members.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Staff
from app.schemas import StaffCreate
from app.auth import verify_token

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
         "initials": "".join([w[0] for w in (s.user.full_name or "").split()[:2]]),
         "role": s.role, "specialization": s.specialization,
         "phone": s.phone, "is_available": s.is_available, "daily_rate": s.daily_rate}
        for s in staff_list
    ]


@router.put("/{staff_id}")
def update_staff(staff_id: int, data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    for key, value in data.items():
        if hasattr(staff, key) and value is not None:
            setattr(staff, key, value)
    db.commit()
    return {"message": "Staff updated successfully"}


@router.delete("/{staff_id}")
def delete_staff(staff_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    db.delete(staff)
    db.commit()
    return {"message": "Staff deleted successfully"}


@router.post("")
def create_staff(data: StaffCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    staff = Staff(
        user_id=data.user_id, role=data.role, specialization=data.specialization,
        phone=data.phone, daily_rate=data.daily_rate
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return {"id": staff.id, "message": "Staff added successfully"}
