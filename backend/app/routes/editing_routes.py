"""
Editing project routes - manage editing workflow.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import User, Booking, EditingProject, ActivityLog
from app.schemas import EditingProjectCreate
from app.auth import verify_token

router = APIRouter(prefix="/api/editing-projects", tags=["Editing"])
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


@router.post("")
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


@router.put("/{project_id}/status")
def update_editing_status(project_id: int, status: str = Query(...),
                          user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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