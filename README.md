# Team Shadow Weddings CRM

A complete **Unified Order Management System** for Team Shadow Weddings - a wedding photography, videography, and event production company. Manage the full customer journey from lead capture to final delivery in one dashboard.

## ✨ Features

### 📨 Multi-Channel Lead Management
- Capture inquiries from **Instagram, WhatsApp, Website, Facebook, Google, and Referral**
- Unified inbox for all channels
- Quick lead creation with customer auto-registration

### 📄 Quotation Module
- Create quotes with **discount and GST auto-calculation**
- Package selection and custom pricing
- Send quotations to clients with one click

### 📅 Booking & Order Tracking
- Full lifecycle tracking: Booked → Advance Received → Event Scheduled → Event Completed → Editing → Album Designing → Client Approval → Printing → Delivered → Closed
- Advance payment tracking with auto balance calculation

### 💰 Payment Module
- Record payments (Cash, Bank Transfer, UPI, Card)
- Auto-update booking payment status (pending/partial/paid)
- Payment history per booking

### 👥 Staff Management
- Add photographers, videographers, editors, album designers, freelancers
- Track availability and daily rates
- Assign staff to editing projects

### 🎬 Editing Workflow
- Assign editors and designers to projects
- Track progress: Raw Received → Editing Started → Review → Client Review → Approved → Delivered

### 🏠 Customer Portal
- Visual project status tracking for clients
- See payment breakdown (Total vs Paid)
- Track wedding project progress

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm

### 1. Start the Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install "fastapi>=0.110.0" "uvicorn>=0.24.0" "sqlalchemy>=2.0.30" "python-jose[cryptography]" "pydantic>=2.0.0" "python-multipart"
python3 run.py
```
The backend will start at `http://localhost:8000`

### 2. Start the Frontend
```bash
cd frontend
npm install
npm start
```
The frontend will start at `http://localhost:3000`

### 3. Initialize Database (Optional)
```bash
python3 init_db.py
```

## 🔑 Default Login Credentials
| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Sales | `sarah` | `staff123` |
| Photographer | `mike` | `staff123` |
| Editor | `emma` | `staff123` |
| Videographer | `alex` | `staff123` |

## 📁 Project Structure
```
teamshadow-crm/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py           # SQLite database setup
│   │   ├── models.py             # Database models
│   │   ├── schemas.py            # Pydantic schemas
│   │   ├── auth.py               # JWT authentication
│   │   └── routes/               # API route modules
│   │       ├── auth_routes.py
│   │       ├── dashboard_routes.py
│   │       ├── customer_routes.py
│   │       ├── inquiry_routes.py
│   │       ├── quotation_routes.py
│   │       ├── booking_routes.py
│   │       ├── payment_routes.py
│   │       ├── staff_routes.py
│   │       ├── editing_routes.py
│   │       └── extra_routes.py
│   ├── run.py                    # Backend entry point
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── index.js
│       ├── App.js                # React application
│       ├── App.css               # Styles
│       └── api.js                # API service layer
├── init_db.py                    # Database initialization
└── start.sh                      # Quick start script
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Customers
- `GET /api/customers` - List all customers
- `POST /api/customers` - Create customer
- `GET /api/customers/{id}` - Get customer details
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

### Inquiries
- `GET /api/inquiries` - List inquiries (filter by status/source)
- `POST /api/inquiries` - Create inquiry
- `PUT /api/inquiries/{id}` - Update inquiry
- `DELETE /api/inquiries/{id}` - Delete inquiry

### Quotations
- `GET /api/quotations` - List quotations
- `POST /api/quotations` - Create quotation
- `PUT /api/quotations/{id}` - Update quotation
- `DELETE /api/quotations/{id}` - Delete quotation
- `PUT /api/quotations/{id}/send` - Send quotation

### Bookings
- `GET /api/bookings` - List bookings
- `POST /api/bookings` - Create booking
- `PUT /api/bookings/{id}` - Update booking
- `DELETE /api/bookings/{id}` - Delete booking
- `PUT /api/bookings/{id}/status` - Update booking status

### Payments
- `GET /api/payments` - List payments
- `POST /api/payments` - Record payment
- `PUT /api/payments/{id}` - Update payment
- `DELETE /api/payments/{id}` - Delete payment

### Staff
- `GET /api/staff` - List staff
- `POST /api/staff` - Add staff
- `PUT /api/staff/{id}` - Update staff
- `DELETE /api/staff/{id}` - Delete staff

### Editing Projects
- `GET /api/editing-projects` - List editing projects
- `POST /api/editing-projects` - Create project
- `PUT /api/editing-projects/{id}` - Update project
- `DELETE /api/editing-projects/{id}` - Delete project
- `PUT /api/editing-projects/{id}/status` - Update project status

### Admin
- `GET /api/users` - List users (admin only)
- `POST /api/users` - Create user (admin only)

### Other
- `GET /api/activity` - Activity log
- `GET /api/deliverables` - List deliverables
- `POST /api/deliverables` - Create deliverable
- `GET /api/expenses` - List expenses
- `POST /api/expenses` - Create expense

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI, SQLAlchemy, JWT
- **Frontend:** React, JavaScript, CSS
- **Database:** SQLite (zero-config, file-based)
- **Authentication:** JWT with role-based access

## 📋 Business Workflow Covered
```
Customer Inquiry (Instagram/WhatsApp/Website/Facebook)
    ↓
Sales Team Reviews & Contacts
    ↓
Quotation Created & Sent
    ↓
Negotiation
    ↓
Booking Confirmed + Advance Payment
    ↓
Event Scheduled → Event Completed
    ↓
Editing & Album Design
    ↓
Client Approval
    ↓
Printing → Delivery → Closed