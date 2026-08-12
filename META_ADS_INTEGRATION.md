# 📱 Meta Ads → WhatsApp Lead Automation

## Overview

This system automatically captures and qualifies leads from **Facebook and Instagram "Send WhatsApp Message" ads**. When a user clicks the ad button, they're redirected to your WhatsApp Business account. The backend receives the message via webhook, runs an AI conversation flow to collect lead details, and stores everything in the CRM.

## How It Works

```
User sees Meta Ad (Facebook/Instagram)
    ↓
Clicks "Send WhatsApp Message"
    ↓
Redirected to WhatsApp Business
    ↓
Sends first message
    ↓
Webhook receives message → Creates Lead
    ↓
AI Bot sends welcome message
    ↓
Collects: Name → Date → Location → Services → Budget
    ↓
Lead stored in CRM with status "new_lead"
    ↓
Sales team notified (task created)
    ↓
Smart follow-up if no response (24h/72h)
    ↓
Human takeover → Quotation → Booking
```

## API Endpoints

### Webhook Endpoints (Public)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/webhooks/whatsapp` | Meta webhook verification |
| POST | `/api/webhooks/whatsapp` | Receive WhatsApp messages |
| POST | `/api/webhooks/instagram` | Receive Instagram DMs |
| POST | `/api/webhooks/facebook` | Receive Facebook messages |
| POST | `/api/webhooks/test` | Simulate a lead message (testing) |

### Lead Management (Admin)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads` | List leads (filter by status/search) |
| GET | `/api/lead/{id}` | Get lead with conversation history |
| PATCH | `/api/lead/{id}` | Update lead status/assignment |
| POST | `/api/send-message` | Send message to lead (human takeover) |
| GET | `/api/lead/{id}/export` | Export lead as CSV |

### Business & Automations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/PUT | `/api/business` | Get/update business profile |
| GET/POST | `/api/knowledge-base` | AI knowledge items |
| GET/POST | `/api/automations` | Follow-up automation rules |
| PATCH | `/api/automations/{id}` | Toggle automation ON/OFF |
| POST | `/api/automations/run-follow-ups` | Run follow-up check |

## AI Conversation Flow

The bot follows a state machine to collect lead information:

```
welcome → collecting_name → collecting_date → collecting_location
  → collecting_services → collecting_budget → complete
```

### Example Conversation
```
User: "Hi! I saw your ad"
Bot: "🎉 Welcome to Team Shadow Weddings! 💍
      What's your name or the couple's name?"

User: "Priya & Rahul"
Bot: "Beautiful name! When is your wedding date?"

User: "December 2026"
Bot: "Perfect! Where is the wedding taking place?"

User: "Goa, Taj Fort Aguada"
Bot: "Wonderful location! Which services are you interested in?
      1️⃣ Photography  2️⃣ Cinematic Video  3️⃣ Event Management
      4️⃣ Decoration  5️⃣ Album"

User: "1,2,5"
Bot: "Great choices! What's your budget range?"

User: "5 lakh"
Bot: "Perfect! Here's your summary:
      Couple: Priya & Rahul
      Date: December 2026
      Location: Goa
      Services: Photography, Cinematic Video, Album
      Budget: ₹500,000
      Our team will contact you shortly!"
```

## AI Features

### Intent Detection
- **Human handoff**: Detects "human", "agent", "call", "talk to someone"
- **Pricing questions**: Detects "price", "cost", "package", "how much"
- **Services questions**: Detects "service", "offer", "what do you do"
- **Portfolio questions**: Detects "work", "portfolio", "sample"
- **Availability questions**: Detects "available", "free", "booked"

### Auto-Detection
- **Budget extraction**: Parses "5 lakh", "500000", "₹5L", "5 lacs"
- **Date extraction**: Parses "December 2026", "15/12/2026", "Dec 2026"
- **Phone extraction**: Parses phone numbers from messages
- **Event type detection**: Detects wedding, engagement, reception, etc.

### Knowledge Base Answers
Business owners configure Q&A pairs in the Settings page:
```
Q: "How much is wedding photography?"
A: "Our packages start from AED 5,000..."
Keywords: price, cost, photography, packages
```

## Smart Follow-ups

Automated follow-up rules fire when customers don't respond:

| Rule | Trigger | Delay | Message |
|------|---------|-------|---------|
| 24h Follow-up | NO_CUSTOMER_REPLY | 24 hours | "Hi! Just checking if you'd still like our packages..." |
| 72h Follow-up | NO_CUSTOMER_REPLY | 72 hours | "We have some great offers this week..." |

## Lead Management

Track leads through the pipeline:
```
New Lead → Qualified → Contacted → Won → Lost
```

Dashboard displays:
- Total Leads
- New Leads
- Follow-ups Pending
- Won
- Conversion Rate

## Configuration

Set these environment variables in your deployment:

```bash
# Meta WhatsApp Cloud API credentials
WHATSAPP_VERIFY_TOKEN=your-verify-token
WHATSAPP_API_TOKEN=your-api-token
WHATSAPP_PHONE_ID=your-phone-id
```

## Testing Guide

### 1. Test the webhook flow
```bash
# Simulate a lead from Facebook ad
curl -X POST http://localhost:8000/api/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"from":"919555111222","message":"Hi! I saw your ad","source":"facebook"}'
```

### 2. Test the full conversation
```bash
# Send sequential messages to simulate conversation
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"919555111222","message":"Priya & Rahul"}'
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"919555111222","message":"December 2026"}'
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"919555111222","message":"Goa"}'
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"919555111222","message":"1,2,5"}'
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"919555111222","message":"5 lakh"}'
```

### 3. View captured leads
```bash
# Login to get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

# List all leads
curl -s http://localhost:8000/api/leads -H "Authorization: Bearer $TOKEN"

# Get lead with conversation history
curl -s http://localhost:8000/api/lead/1 -H "Authorization: Bearer $TOKEN"

# Export lead as CSV
curl -s http://localhost:8000/api/lead/1/export -H "Authorization: Bearer $TOKEN"
```

### 4. Update lead status
```bash
curl -s -X PATCH http://localhost:8000/api/lead/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"qualified"}'
```

### 5. Send message (human takeover)
```bash
curl -s -X POST http://localhost:8000/api/send-message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lead_id":1,"message":"Hi! Thanks for your enquiry. Here are our packages..."}'
```

### 6. Test follow-up automation
```bash
# Create a follow-up rule
curl -s -X POST http://localhost:8000/api/automations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"24h Follow-up","trigger":"NO_CUSTOMER_REPLY","action":"SEND_FOLLOWUP","delay_hours":24,"message_template":"Hi! Just checking if you would still like our packages."}'

# Run follow-up check
curl -s -X POST http://localhost:8000/api/automations/run-follow-ups \
  -H "Authorization: Bearer $TOKEN"
```

## Meta Webhook Setup

1. **Create WhatsApp Business Account** at https://business.whatsapp.com
2. **Get API credentials** from Meta Developer Portal
3. **Configure webhook URL**: `https://your-domain.com/api/webhooks/whatsapp`
4. **Verify token**: Use the same value as `WHATSAPP_VERIFY_TOKEN`
5. **Subscribe to messages** webhook events

See [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) for detailed credential setup.

## Database Schema

### Lead Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| whatsapp_number | String | Lead's WhatsApp number |
| customer_name | String | Couple's name |
| wedding_date | String | Wedding date |
| wedding_location | String | Venue/city |
| services | JSON | Selected services |
| budget | Float | Budget amount |
| lead_source | String | facebook/instagram/whatsapp |
| conversation_state | String | Current bot state |
| assigned_to | Integer | Sales team member |
| status | String | new_lead/qualified/contacted/won/lost |
| created_at | DateTime | Lead created |
| updated_at | DateTime | Last update |

### Conversation Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| lead_id | Integer | FK to leads |
| sender | String | user/bot/agent |
| message | Text | Message content |
| timestamp | DateTime | When sent |

### Automation Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| business_id | Integer | FK to businesses |
| name | String | Rule name |
| trigger | String | LEAD_CREATED / NO_CUSTOMER_REPLY / STATUS_CHANGED |
| action | String | SEND_FOLLOWUP / SEND_AI_REPLY / NOTIFY_TEAM |
| delay_hours | Integer | Delay before firing |
| message_template | Text | Follow-up message |
| active | Boolean | ON/OFF toggle |

### KnowledgeBase Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| business_id | Integer | FK to businesses |
| question | String | Common question |
| answer | Text | AI response |
| keywords | JSON | Related keywords for matching |