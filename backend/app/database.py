"""
Database configuration and initialization.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{os.path.join(BASE_DIR, 'teamshadow.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables and default data."""
    import os
    import app.models  # noqa: F401 - Import models to register them
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        from app.models import User, Staff
        from app.auth import hash_password

        admin_username = os.getenv("TEAMSHADOW_ADMIN_USERNAME")
        admin_password = os.getenv("TEAMSHADOW_ADMIN_PASSWORD")
        staff_password = os.getenv("TEAMSHADOW_STAFF_PASSWORD")

        if admin_username and admin_password:
            if not db.query(User).filter(User.username == admin_username).first():
                admin = User(
                    username=admin_username,
                    email="admin@teamshadow.com",
                    hashed_password=hash_password(admin_password),
                    full_name="Team Shadow Admin",
                    role="admin",
                    is_active=True
                )
                db.add(admin)
                db.commit()

        if staff_password:
            sample_staff = [
                {"username": "sarah", "password": staff_password, "full_name": "Sarah Johnson", "role": "sales"},
                {"username": "mike", "password": staff_password, "full_name": "Mike Chen", "role": "photographer"},
                {"username": "emma", "password": staff_password, "full_name": "Emma Wilson", "role": "editor"},
                {"username": "alex", "password": staff_password, "full_name": "Alex Rivera", "role": "videographer"},
            ]
            for s in sample_staff:
                if not db.query(User).filter(User.username == s["username"]).first():
                    user = User(
                        username=s["username"],
                        email=f"{s['username']}@teamshadow.com",
                        hashed_password=hash_password(s["password"]),
                        full_name=s["full_name"],
                        role=s["role"]
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                    staff = Staff(user_id=user.id, role=s["role"])
                    db.add(staff)
                    db.commit()
    finally:
        db.close()