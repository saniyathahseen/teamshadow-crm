"""
Team Shadow Weddings CRM - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes.auth_routes import router as auth_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.customer_routes import router as customer_router
from app.routes.inquiry_routes import router as inquiry_router
from app.routes.quotation_routes import router as quotation_router
from app.routes.booking_routes import router as booking_router
from app.routes.payment_routes import router as payment_router
from app.routes.staff_routes import router as staff_router
from app.routes.editing_routes import router as editing_router
from app.routes.extra_routes import router as extra_router
from app.routes.task_routes import router as task_router

app = FastAPI(
    title="Team Shadow Weddings CRM",
    version="1.0.0",
    description="Unified Order Management System for Team Shadow Weddings"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(customer_router)
app.include_router(inquiry_router)
app.include_router(quotation_router)
app.include_router(booking_router)
app.include_router(payment_router)
app.include_router(staff_router)
app.include_router(editing_router)
app.include_router(extra_router)
app.include_router(task_router)


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()


@app.get("/")
def root():
    return {
        "message": "Team Shadow Weddings CRM API",
        "version": "1.0.0",
        "docs": "/docs"
    }