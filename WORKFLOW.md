# 📋 Team Shadow CRM - Complete Workflow Documentation

This document explains the complete business workflow from lead capture to final delivery, and how each step maps to the CRM system.

---

## 🔄 Complete Business Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CUSTOMER DISCOVERY                            │
│  Instagram │ WhatsApp │ Website │ Facebook │ Google │ Referral  │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    1. INQUIRY RECEIVED                          │
│  • Customer sends message/contact form                          │
│  • CRM: Create Inquiry (source: instagram/whatsapp/etc)         │
│  • Status: "new"                                                │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    2. SALES CONTACT                             │
│  • Sales team contacts customer                                 │
│  • Discuss requirements, date, venue, budget                    │
│  • CRM: Update Inquiry status → "contacted"                     │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    3. QUALIFICATION                             │
│  • Assess if customer is serious and fits budget                │
│  • CRM: Update Inquiry status → "qualified"                     │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    4. QUOTATION CREATED                         │
│  • Create quotation with package, discount, GST                 │
│  • CRM: Create Quotation (auto-calculates total)                │
│  • CRM: Inquiry status → "quotation_sent"                       │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    5. NEGOTIATION                               │
│  • Customer may negotiate price/package                         │
│  • CRM: Update Inquiry status → "negotiation"                   │
│  • Update quotation if needed                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    6. BOOKING CONFIRMED                         │
│  • Customer agrees to proceed                                  │
│  • CRM: Create Booking (with total & advance amount)            │
│  • CRM: Inquiry status → "booked"                               │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    7. ADVANCE PAYMENT                           │
│  • Customer pays advance (cash/UPI/bank transfer)               │
│  • CRM: Record Payment (type: advance)                          │
│  • CRM: Booking status → "advance_received"                     │
│  • CRM: Payment status auto-updates (pending/partial/paid)      │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    8. EVENT SCHEDULED                           │
│  • Confirm event date and venue                                 │
│  • CRM: Booking status → "event_scheduled"                      │
│  • Assign photographers/videographers                           │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    9. EVENT COMPLETED                           │
│  • Wedding/event covered by team                                │
│  • CRM: Booking status → "event_completed"                      │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    10. EDITING WORKFLOW                         │
│  • Create Editing Project                                       │
│  • Assign editor and designer                                   │
│  • Track: raw_received → editing_started → review               │
│  • CRM: Booking status → "editing"                              │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    11. ALBUM DESIGNING                          │
│  • Designer creates album layout                                │
│  • CRM: Booking status → "album_designing"                      │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    12. CLIENT APPROVAL                          │
│  • Client reviews photos/videos/album                           │
│  • CRM: Booking status → "client_approval"                      │
│  • Editing status → "client_review"                             │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    13. PRINTING                                 │
│  • Print albums, frames, canvases                               │
│  • CRM: Booking status → "printing"                             │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    14. FINAL PAYMENT                            │
│  • Customer pays remaining balance                              │
│  • CRM: Record Payment (type: final)                            │
│  • CRM: Payment status → "paid"                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    15. DELIVERY                                 │
│  • Deliver albums, videos, photos                               │
│  • CRM: Booking status → "delivered"                            │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    16. CLOSED                                   │
│  • Project complete, after-sales support                        │
│  • CRM: Booking status → "closed"                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 👥 Role-Based Workflow

### Admin Workflow
```
1. Login as admin
2. View Dashboard → see all business stats
3. Manage Inquiries → assign to staff, update status
4. Create Quotations → send to clients
5. Confirm Bookings → track payments
6. Assign Tasks → create tasks for staff
7. Manage Staff → add/edit/remove team members
8. Track Editing → monitor project progress
```

### Staff Workflow
```
1. Login with staff credentials (created by admin)
2. View Dashboard → see business overview
3. View "My Tasks" → see only tasks assigned to them
4. Update Task Status:
   - Pending → In Progress → Completed
5. Add Progress Notes → document what they did
6. Cannot see other staff tasks or customer data
```

---

## 📊 Status Flow Diagrams

### Inquiry Status Flow
```
new → contacted → qualified → quotation_sent → negotiation → booked
  ↘ lost (at any stage)
```

### Booking Status Flow
```
booked → advance_received → event_scheduled → event_completed
  → editing → album_designing → client_approval → printing
  → delivered → closed
```

### Payment Status Flow
```
pending → partial → paid
(advance payment = partial, full payment = paid)
```

### Editing Status Flow
```
raw_received → editing_started → review → client_review → approved → delivered
```

### Task Status Flow
```
pending → in_progress → completed
```

---

## 🎯 Key Business Rules

1. **Inquiry → Booking**: An inquiry becomes a booking when customer confirms
2. **Advance Payment**: Required to confirm booking (typically 30-50%)
3. **Payment Tracking**: System auto-calculates balance = total - paid
4. **Task Assignment**: Only admin can create/assign tasks
5. **Staff Visibility**: Staff only see their own tasks
6. **Activity Logging**: All actions are logged for audit trail

---

## 🛠️ Daily Usage Guide

### Morning Routine (Admin)
1. Check Dashboard for new inquiries
2. Review pending quotations
3. Check upcoming events
4. Assign new tasks to staff

### During Day (Staff)
1. Check "My Tasks"
2. Update task progress as you work
3. Add notes about completed work

### Evening Routine (Admin)
1. Review task updates from staff
2. Record any payments received
3. Update booking statuses
4. Plan next day's tasks

---

## 📁 Database Tables & Relationships

```
users ────┬─── staff (user_id)
          ├─── inquiries.assigned_to
          ├─── tasks.assigned_to
          └─── tasks.created_by

customers ────┬─── inquiries (customer_id)
              ├─── quotations (customer_id)
              └─── bookings (customer_id)

bookings ────┬─── payments (booking_id)
             ├─── editing_projects (booking_id)
             └─── deliverables (booking_id)

quotations ──── bookings (quotation_id)
```

---

## 🚀 Quick Start Commands

```bash
# Start backend
cd backend && source venv/bin/activate && python3 run.py

# Start frontend
cd frontend && npm start

# Check database
python3 query_db.py

# Reset database
python3 init_db.py
```

---

## 🔑 Default Accounts

| Role | Username | Password | Access |
|------|----------|----------|--------|
| Admin | `admin` | `admin123` | Full access |
| Sales | `sarah` | `staff123` | Tasks only |
| Photographer | `mike` | `staff123` | Tasks only |
| Editor | `emma` | `staff123` | Tasks only |
| Videographer | `alex` | `staff123` | Tasks only |