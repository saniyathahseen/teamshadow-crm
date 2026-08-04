"""
Task routes - task assignment and management.
Admin can create/assign tasks. Staff can update their tasks.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import User, Task, ActivityLog
from app.auth import verify_token

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])
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
def list_tasks(
    status: Optional[str] = None,
    assigned_to: Optional[int] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List tasks. Staff see only their tasks, admin sees all."""
    query = db.query(Task)

    # Staff can only see their own tasks
    if user.role != "admin":
        query = query.filter(Task.assigned_to == user.id)

    if status and status != "all":
        query = query.filter(Task.status == status)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    tasks = query.order_by(Task.created_at.desc()).all()
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "assigned_to": {
                "id": t.assignee.id,
                "full_name": t.assignee.full_name
            } if t.assignee else None,
            "created_by": {
                "id": t.creator.id,
                "full_name": t.creator.full_name
            } if t.creator else None,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "related_type": t.related_type,
            "related_id": t.related_id,
            "update_note": t.update_note,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None
        }
        for t in tasks
    ]


@router.post("")
def create_task(data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a task. Only admin can create and assign tasks."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create tasks")

    task = Task(
        title=data.get("title"),
        description=data.get("description"),
        status=data.get("status", "pending"),
        priority=data.get("priority", "medium"),
        assigned_to=data.get("assigned_to"),
        created_by=user.id,
        due_date=datetime.strptime(data["due_date"], "%Y-%m-%d").date() if data.get("due_date") else None,
        related_type=data.get("related_type"),
        related_id=data.get("related_id")
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    log = ActivityLog(
        user_id=user.id,
        action="task_created",
        entity_type="task",
        entity_id=task.id,
        description=f"Task assigned to user #{task.assigned_to}"
    )
    db.add(log)
    db.commit()

    return {"id": task.id, "message": "Task created successfully"}


@router.put("/{task_id}")
def update_task(task_id: int, data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a task. Admin can update any task, staff can update their own."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Staff can only update their own tasks
    if user.role != "admin" and task.assigned_to != user.id:
        raise HTTPException(status_code=403, detail="You can only update your own tasks")

    for key, value in data.items():
        if hasattr(task, key) and value is not None:
            if key == "due_date" and value:
                value = datetime.strptime(value, "%Y-%m-%d").date()
            setattr(task, key, value)

    if data.get("status") == "completed" and not task.completed_at:
        task.completed_at = datetime.utcnow()

    task.updated_at = datetime.utcnow()
    db.commit()

    log = ActivityLog(
        user_id=user.id,
        action="task_updated",
        entity_type="task",
        entity_id=task.id,
        description=f"Task updated: {task.title}"
    )
    db.add(log)
    db.commit()

    return {"message": "Task updated successfully"}


@router.post("/{task_id}/update")
def staff_update_task(task_id: int, data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Staff update their task progress and add notes."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Staff can only update their own tasks
    if task.assigned_to != user.id:
        raise HTTPException(status_code=403, detail="You can only update your own tasks")

    status = data.get("status")
    if status:
        task.status = status
        if status == "completed":
            task.completed_at = datetime.utcnow()
        elif status == "in_progress":
            task.completed_at = None

    note = data.get("update_note")
    if note:
        task.update_note = note

    task.updated_at = datetime.utcnow()
    db.commit()

    log = ActivityLog(
        user_id=user.id,
        action="task_progress",
        entity_type="task",
        entity_id=task.id,
        description=f"{user.full_name} updated task: {task.title} → {task.status}"
    )
    db.add(log)
    db.commit()

    return {"message": "Task updated successfully"}


@router.delete("/{task_id}")
def delete_task(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a task. Only admin can delete."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete tasks")

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}