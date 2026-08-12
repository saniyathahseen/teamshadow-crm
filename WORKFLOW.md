# Team Shadow Weddings - Complete Business Workflow

This document describes the complete end-to-end workflow of the system, from when a customer sees an ad to when they become a confirmed booking.

---

## 📱 Complete Lead Flow: Meta Ad → WhatsApp → AI → Booking

```
1. CUSTOMER SEES AD
   Facebook/Instagram ad shown to potential customer
        ↓
2. CUSTOMER CLICKS "SEND WHATSAPP MESSAGE"
   Meta redirects customer to WhatsApp Business chat
        ↓
3. CUSTOMER SENDS FIRST MESSAGE
   "Hi! I want wedding photography"
        ↓
4. AI WELCOME MESSAGE (automatic)
   "🎉 Welcome to Team Shadow Weddings! 
    What's your name or the couple's name?"
        ↓
5. AI COLLECTS LEAD INFORMATION (step by step)
   Name: "Ahmed & Sara"
   Date: "December 2026"
   Location: "Dubai, Atlantis"
   Services: "1,2,5" → Photography, Video, Album
   Budget: "5 lakh" → ₹500,000
        ↓
6. LEAD SAVED TO CRM (status: new_lead)
   ✓ Conversation history stored
   ✓ Lead details stored
   ✓ Sales team notified via dashboard
        ↓
7. SMART FOLLOW-UP (if no response)
   24h later: "Hi! Just checking if you'd still like our packages..."
   72h later: "We have some great offers this week..."
        ↓
8. HUMAN TAKEOVER (any time)
   Sales agent opens WhatsApp Inbox
   Views full conversation
   Sends personalized reply
   Updates lead status: Qualified / Contacted / Won / Lost
        ↓
9. QUOTATION SENT
   Sales creates quotation from lead details
   Customer receives package proposal
        ↓
10. BOOKING CONFIRMED
    Advance payment recorded
    Wedding date reserved
    Status: Won
```

---

## 🏢 Staff Workflows

### Admin Workflow
1. **Login** with admin credentials
2. **Dashboard** - Monitor Total Leads, New Leads, Follow-ups Pending, Won, Conversion Rate
3. **WhatsApp Inbox** - Review all lead conversations
4. **Assign Tasks** - Create tasks for team members
5. **Manage Staff** - Add team members with username/password
6. **Automations** - Configure follow-up rules
7. **Settings** - Update business profile, services, pricing, AI knowledge base

### Sales Team Workflow
1. **Login** with staff credentials
2. **My Tasks** - View assigned leads/tasks
3. **WhatsApp Inbox** - Take over conversations from AI
4. **Update Lead Status** - Qualify, Contact, Win, or Lose leads
5. **Send Quotations** - Create and send price proposals

### Photographer/Videographer Workflow
1. **Login** with staff credentials
2. **My Tasks** - View assigned shoots
3. **Bookings** - View event schedule
4. **Update Task Status** - Report progress

### Editor Workflow
1. **Login** with editor credentials
2. **Editing Projects** - View projects assigned to you
3. **Update Status** - raw_received → editing_started → review → client_review → approved → delivered

---

## 📊 Lead Status Pipeline

```
NEW_LEAD ──→ QUALIFIED ──→ CONTACTED ──→ WON
    │           │             │           │
    │           │             │           └── Booked, advance received
    │           │             │
    │           │             └── Quotation sent, negotiation
    │           │
    │           └── Details collected, budget known
    │
    └── New WhatsApp message received

LOST ←── Not interested / no response / went elsewhere
```

### Dashboard Stats Explained
| Stat | What it means |
|------|---------------|
| **Total Leads** | All WhatsApp leads captured |
| **New Leads** | Leads needing first contact |
| **Follow-ups Pending** | Leads waiting for follow-up |
| **Won** | Leads converted to bookings |
| **Conversion Rate** | Won ÷ Total × 100% |

---

## 🤖 AI Assistant Behavior

### Conversation Flow (State Machine)
```
welcome → collecting_name → collecting_date → collecting_location
  → collecting_services → collecting_budget → complete
```

### Intent Detection
| User says | AI does |
|-----------|---------|
| "What's your price?" | Answers from business knowledge base |
| "What services do you offer?" | Lists services from business profile |
| "Where are you located?" | Answers location |
| "What are your hours?" | Answers working hours |
| "I want to talk to a human" | Creates task for sales team, transfers to human |
| "5 lakh" | Detects budget → ₹500,000 |
| "December 2026" | Detects wedding date |
| "1,2,5" | Detects services selected |

### Knowledge Base
Business owners add Q&A pairs in Settings → AI Knowledge Base:
```
Q: "How much is wedding photography?"
A: "Our wedding photography packages start from AED 5,000..."
Keywords: price, cost, photography, packages
```

---

## ⚙️ Automation Rules

### Available Triggers
| Trigger | Fires when |
|---------|-----------|
| `NO_CUSTOMER_REPLY` | Customer hasn't replied after X hours |
| `LEAD_CREATED` | New lead arrives |
| `STATUS_CHANGED` | Lead status changes |

### Available Actions
| Action | What it does |
|--------|-------------|
| `SEND_FOLLOWUP` | Sends follow-up message |
| `SEND_AI_REPLY` | Sends AI-generated response |
| `NOTIFY_TEAM` | Creates task for sales team |

### Example Rules
```
Name: "24h Follow-up"
Trigger: NO_CUSTOMER_REPLY
Action: SEND_FOLLOWUP
Delay: 24 hours
Message: "Hi {name}! Just checking if you'd still like our packages. Let us know! 😊"

Name: "72h Follow-up"  
Trigger: NO_CUSTOMER_REPLY
Action: SEND_FOLLOWUP
Delay: 72 hours
Message: "We have some great offers this week. Would you like to see them?"
```

---

## 📋 CRM Module Workflows

### Customer Management
1. Customer created from WhatsApp lead or manually
2. Add: name, phone, email, wedding date, bride/groom names, venue
3. View customer detail with all inquiries and bookings

### Quotation Workflow
1. Create quotation for a customer
2. Add package name, base amount, discount %, GST %
3. System calculates total amount
4. Send quotation to client
5. Track status: draft → sent → accepted/rejected

### Booking Workflow
1. Convert won lead/customer to booking
2. Add: event type, event date, total amount, advance amount, venue
3. Record advance payment
4. Track status: booked → advance_received → event_scheduled → event_completed
5. Post-event: editing → album_designing → client_approval → printing → delivered → closed

### Payment Workflow
1. Record payment against a booking
2. Type: advance, milestone, or final
3. Method: cash, bank transfer, UPI, or card
4. Track payment status: pending → completed

### Editing Workflow
1. Create editing project for completed event
2. Assign editor and album designer
3. Track: raw_received → editing_started → review → client_review → approved → delivered

### Task Management
1. Admin creates task and assigns to staff
2. Set priority: low, medium, high, urgent
3. Staff updates status: pending → in_progress → completed
4. Staff adds update notes

---

## 🔐 Roles & Permissions

| Feature | Admin | Sales | Photographer | Editor |
|---------|-------|-------|--------------|--------|
| Dashboard | ✅ | ✅ | ✅ | ✅ |
| My Tasks | ✅ | ✅ | ✅ | ✅ |
| WhatsApp Inbox | ✅ | ✅ | ❌ | ❌ |
| Inquiries | ✅ | ✅ | ❌ | ❌ |
| Customers | ✅ | ✅ | ❌ | ❌ |
| Quotations | ✅ | ✅ | ❌ | ❌ |
| Bookings | ✅ | ✅ | ✅ | ❌ |
| Payments | ✅ | ✅ | ❌ | ❌ |
| Staff | ✅ | ❌ | ❌ | ❌ |
| Editing | ✅ | ❌ | ❌ | ✅ |
| Automations | ✅ | ❌ | ❌ | ❌ |
| Settings | ✅ | ❌ | ❌ | ❌ |

---

## 🚀 Deployment Workflow

### First Time
```bash
git clone https://github.com/saniyathahseen/teamshadow-crm.git
cd teamshadow-crm
docker compose up -d --build
```

### After Code Changes
```bash
docker compose up -d --build
```

### Reset Database
```bash
docker compose down
docker volume rm teamshadow-crm_teamshadow_data
docker compose up -d --build
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend not starting | Check logs: `docker logs teamshadow-backend` |
| Frontend not loading | Check: `docker logs teamshadow-frontend` |
| Login fails | DB was reset, use default admin/admin123 |
| WhatsApp not sending | Set WHATSAPP_API_TOKEN and WHATSAPP_PHONE_ID env vars |
| Leads not showing | Create test lead: `POST /api/webhooks/test` |
| Dashboard shows 0 | No data yet - create leads/customers first |