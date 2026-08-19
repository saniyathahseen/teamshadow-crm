# Team Shadow Weddings CRM - LeadFlow AI Edition

**Turn WhatsApp conversations into customers - automatically.**

A complete wedding business management system that captures WhatsApp/Instagram/Facebook ads leads, responds with AI, organizes leads in one inbox, and automatically follows up with potential customers.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Node.js 18+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Run with Docker (Recommended)
```bash
# Clone the repo
git clone https://github.com/saniyathahseen/teamshadow-crm.git
cd teamshadow-crm

# Start all services
docker compose up -d --build

# Access the app
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

### Run locally (Development)
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm install
npm start
```

## 👤 Default Login
| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Sales | `sarah` | `staff123` |
| Photographer | `mike` | `staff123` |
| Editor | `emma` | `staff123` |
| Videographer | `alex` | `staff123` |

## 📱 What This System Does

### 1. Meta Ads → WhatsApp Lead Automation
```
User sees Facebook/Instagram ad
    ↓
Clicks "Send WhatsApp Message"
    ↓
Messages your WhatsApp Business
    ↓
Webhook captures the message automatically
    ↓
AI bot responds with welcome message
    ↓
AI collects: Name → Date → Location → Services → Budget
    ↓
Lead stored in CRM as "new_lead"
    ↓
Sales team notified
```

### 2. AI Assistant
- **Automated welcome**: Instantly responds to every WhatsApp enquiry
- **Lead qualification**: Collects name, wedding date, location, services, budget step-by-step
- **Smart answers**: Answers pricing, services, location, and hours questions from your knowledge base
- **Human handoff**: Detects when customer wants to talk to a person and creates a task for your team

### 3. WhatsApp Inbox
- All leads in one dashboard
- View full conversation history
- Chat bubbles (user=green, bot=gray)
- Send replies directly (human takeover)
- Quick status buttons: Qualify, Contacted, Won, Lost
- Export lead as CSV

### 4. Smart Follow-ups
- Automated reminders for customers who don't respond
- Configurable: "Follow-up after 24 hours", "Follow-up after 72 hours"
- Custom message templates
- ON/OFF toggle for each automation rule

### 5. Lead Management
- Track leads through: **New → Qualified → Contacted → Won → Lost**
- Dashboard shows: Total Leads, New Leads, Follow-ups Pending, Won, Conversion Rate
- Filter by status
- Search by name, phone, or location

## 🗂️ Dashboard Screens

| Screen | What it does |
|--------|-------------|
| **Dashboard** | Overview: Total Leads, New Leads, Follow-ups Pending, Won, Conversion Rate |
| **WhatsApp Inbox** | Lead conversations, human takeover, export |
| **Inquiries** | Full CRM inquiry management (create/edit/update status/delete) |
| **Customers** | Customer database (view/edit/delete) |
| **Quotations** | Create/send quotations to clients |
| **Bookings** | Confirmed wedding bookings, payments |
| **Payments** | Record payments against bookings |
| **Editing** | Post-wedding editing project tracking |
| **Tasks** | Assign tasks to team members |
| **Automations** | Follow-up automation rules |
| **Settings** | Business profile + AI knowledge base |

## 🔌 API Endpoints

### Webhooks (Public)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/webhooks/whatsapp` | Meta webhook verification |
| POST | `/api/webhooks/whatsapp` | Receive WhatsApp messages |
| POST | `/api/webhooks/instagram` | Instagram DM leads |
| POST | `/api/webhooks/facebook` | Facebook Messenger leads |
| POST | `/api/webhooks/test` | Simulate a lead (testing) |

### Leads
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads` | List leads (filter by status/search) |
| GET | `/api/lead/{id}` | Get lead with conversation history |
| PATCH | `/api/lead/{id}` | Update lead status/details |
| POST | `/api/send-message` | Send message to lead (human takeover) |
| GET | `/api/lead/{id}/export` | Export lead as CSV |

### Business & Automations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/PUT | `/api/business` | Get/update business profile |
| GET/POST | `/api/knowledge-base` | AI knowledge items |
| GET/POST | `/api/automations` | Follow-up automation rules |
| PATCH | `/api/automations/{id}` | Toggle automation ON/OFF |
| POST | `/api/automations/run-follow-ups` | Run follow-up check now |

### CRM
| Resource | Endpoints |
|----------|-----------|
| Customers | GET/POST `/api/customers`, GET/PUT/DELETE `/api/customers/{id}` |
| Inquiries | GET/POST `/api/inquiries`, PUT/DELETE `/api/inquiries/{id}` |
| Quotations | GET/POST `/api/quotations`, PUT/DELETE `/api/quotations/{id}` |
| Bookings | GET/POST `/api/bookings`, PUT/DELETE `/api/bookings/{id}` |
| Payments | GET/POST `/api/payments`, PUT/DELETE `/api/payments/{id}` |
| Staff | GET/POST `/api/staff`, PUT/DELETE `/api/staff/{id}` |
| Tasks | GET/POST `/api/tasks`, PUT/DELETE `/api/tasks/{id}` |
| Users | GET/POST `/api/users` |

## 📊 Database Models

| Model | Purpose |
|-------|---------|
| `User` | System users (admin/staff) with login credentials |
| `Business` | Business profile (services, pricing, location, hours) |
| `Customer` | Client information |
| `Inquiry` | Initial enquiries from all channels |
| `Lead` | WhatsApp leads with qualification status |
| `Conversation` | WhatsApp conversation history |
| `Quotation` | Price quotes sent to clients |
| `Booking` | Confirmed events |
| `Payment` | Payment records |
| `Staff` | Team members |
| `EditingProject` | Post-event editing tracking |
| `Deliverable` | Final deliverables |
| `Task` | Team task management |
| `Automation` | Follow-up rules (trigger/action/delay) |
| `KnowledgeBase` | AI answers for common questions |
| `ActivityLog` | Audit trail |

## 📁 Project Structure
```
teamshadow-crm/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── auth.py          # JWT authentication
│   │   ├── database.py      # Database setup
│   │   ├── routes/          # API endpoints
│   │   │   ├── webhook_routes.py     # WhatsApp lead capture
│   │   │   ├── business_routes.py    # Profile + automations
│   │   │   ├── dashboard_routes.py   # Stats overview
│   │   │   └── ... (all CRM routes)
│   │   └── services/
│   │       └── automation_service.py  # Follow-ups + AI knowledge
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── App.js           # All UI screens
│   │   ├── App.css          # Styles
│   │   └── api.js           # API client
│   └── package.json
├── docker-compose.yml       # Backend + frontend orchestration
├── META_ADS_INTEGRATION.md  # Meta ads → WhatsApp guide
├── WHATSAPP_SETUP.md        # How to get WhatsApp credentials
└── WORKFLOW.md              # Business workflow
```

## 🚀 Deployment

### GitHub Pages (Free - Frontend)
The site is **automatically deployed** to GitHub Pages using GitHub Actions on every push to `main`.

**Live URL:** `https://saniyathahseen.github.io/teamshadow-crm/`

The workflow (`.github/workflows/deploy.yml`):
1. Installs frontend dependencies
2. Builds the React app (`npm run build`)
3. Uploads the `frontend/build` folder to GitHub Pages

**To enable:** Go to repo → Settings → Pages → Source: "GitHub Actions"

### Docker (Full Stack - Backend + Frontend)
```bash
# Deploy on any VPS/cloud server
git clone https://github.com/saniyathahseen/teamshadow-crm.git
cd teamshadow-crm
docker compose up -d --build

# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Render.com / Railway (Free Tier)
1. Connect your GitHub repo
2. Select "Docker" as the runtime
3. Deploy the two services (backend on port 8000, frontend on port 3000)

## 💰 How to Set Up WhatsApp (Meta) Integration

See [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) for a complete step-by-step guide to get:
- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_API_TOKEN`
- `WHATSAPP_PHONE_ID`

## 🔧 Configuration

Set these environment variables:
```bash
# Meta WhatsApp API credentials
WHATSAPP_VERIFY_TOKEN=your-verify-token
WHATSAPP_API_TOKEN=your-api-token
WHATSAPP_PHONE_ID=your-phone-id

# Frontend API URL (default: /api which proxies to backend)
REACT_APP_API_URL=/api
```

## 🧪 Testing the System

### Test WhatsApp lead flow
```bash
# 1. Simulate a lead from a Facebook ad
curl -X POST http://localhost:8000/api/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"from":"97150123456","message":"Hi! I want wedding photography","source":"facebook"}'

# 2. Respond as the customer (AI collects info)
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"97150123456","message":"Ahmed & Sara"}'
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"97150123456","message":"December 2026"}'
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"97150123456","message":"Dubai"}'
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"97150123456","message":"1,2,5"}'
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"97150123456","message":"5 lakh"}'

# 3. View captured leads
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

curl -s http://localhost:8000/api/leads -H "Authorization: Bearer $TOKEN"

# 4. Export a lead as CSV
curl -s http://localhost:8000/api/lead/1/export -H "Authorization: Bearer $TOKEN"
```

## 📚 More Documentation
- **[META_ADS_INTEGRATION.md](META_ADS_INTEGRATION.md)** - Complete Meta Ads → WhatsApp automation guide
- **[WHATSAPP_SETUP.md](WHATSAPP_SETUP.md)** - How to get WhatsApp API credentials
- **[WORKFLOW.md](WORKFLOW.md)** - Business workflow documentation
- **[SECURITY.md](SECURITY.md)** - Security & deployment guide
- **[INTEGRATION.md](INTEGRATION.md)** - Integration guide

## 🛠️ Tech Stack
- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, JWT
- **Frontend**: React 18, Axios
- **Deployment**: Docker, Docker Compose, Nginx
- **AI**: Rule-based intent detection + knowledge base (no external API needed)
- **WhatsApp**: Meta WhatsApp Cloud API