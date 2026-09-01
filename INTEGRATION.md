# 📱 WhatsApp & Instagram Integration Guide

This guide shows how to integrate WhatsApp and Instagram inquiries directly into the Team Shadow CRM.

## 🚀 Quick Integration Options

### Option 1: Manual Entry (Already Working ✅)
The simplest way - just use the **New Inquiry** button in the UI to manually add inquiries from WhatsApp/Instagram. Select the source channel when creating.

### Option 2: WhatsApp Click-to-Chat (Free, No Code)
Add this link to your Instagram bio or website to generate pre-filled WhatsApp messages:

```
https://wa.me/919876543210?text=Hi%20Team%20Shadow%20Weddings%2C%20I%27m%20interested%20in%20your%20services
```

### Option 3: Instagram DM Quick Reply (Free)
1. Go to Instagram → Settings → Business → Quick Replies
2. Create quick replies like:
   - `@pricing` - "Our packages start from ₹XXX. Check our website!"
   - `@book` - "To book, please share your wedding date and venue"
3. When clients DM, one tap sends the auto-response

### Option 4: Meta Ads → WhatsApp Automation (Recommended ✅)
The system has **full WhatsApp webhook automation** built in:

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
Smart follow-up if no response (24h/72h)
    ↓
Human takeover → Quotation → Booking
```

**Webhook endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/webhooks/whatsapp` | Meta webhook verification |
| POST | `/api/webhooks/whatsapp` | Receive WhatsApp messages |
| POST | `/api/webhooks/instagram` | Instagram DM leads |
| POST | `/api/webhooks/facebook` | Facebook Messenger leads |
| POST | `/api/webhooks/test` | Simulate a lead (testing) |

**Test the flow:**
```bash
# Simulate a lead from a Facebook ad
curl -X POST http://localhost:8000/api/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{"from":"97150123456","message":"Hi! I want wedding photography","source":"facebook"}'

# Respond as the customer (AI collects info)
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"97150123456","message":"Ahmed & Sara"}'
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"97150123456","message":"December 2026"}'
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"97150123456","message":"Dubai"}'
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"97150123456","message":"1,2,5"}'
curl -X POST http://localhost:8000/api/webhooks/test -d '{"from":"97150123456","message":"5 lakh"}'
```

### Option 5: API Integration (For Developers)
The CRM has an **Open API endpoint** that can receive inquiries from any platform:

```
POST http://localhost:8000/api/inquiries
Content-Type: application/json
Authorization: Bearer <your_token>
```

```json
{
  "customer_id": 1,
  "source": "whatsapp",
  "message": "Hi! I saw your work on Instagram. Can you share pricing?",
  "event_type": "Wedding",
  "budget_estimate": 500000
}
```

## 🤖 Setting up WhatsApp Business API

1. **Create WhatsApp Business Account** at https://business.whatsapp.com
2. **Get API credentials** from Meta Developer Portal:
   - `WHATSAPP_VERIFY_TOKEN` - You create this yourself
   - `WHATSAPP_API_TOKEN` - From Meta Developer Portal
   - `WHATSAPP_PHONE_ID` - From Meta Developer Portal
3. **Configure webhook URL**: `https://your-domain.com/api/webhooks/whatsapp`
4. **Verify token**: Use the same value as `WHATSAPP_VERIFY_TOKEN`
5. **Subscribe to messages** webhook events

See [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) for detailed credential setup.

## 📸 Setting up Instagram API

1. **Convert to Instagram Business Account**
2. **Get API Access** via Meta Graph API
3. **Create a Webhook** that forwards DMs to `/api/webhooks/instagram`

## 🏷️ Channel Sources Available
| Source | Status | How to Add |
|--------|--------|------------|
| Instagram | ✅ Already supported | Use "New Inquiry" → Select Instagram |
| WhatsApp | ✅ Already supported | Use "New Inquiry" → Select WhatsApp |
| Website | ✅ Already supported | Use "New Inquiry" → Select Website |
| Facebook | ✅ Already supported | Use "New Inquiry" → Select Facebook |
| Google | ✅ Already supported | Use "New Inquiry" → Select Google |
| Referral | ✅ Already supported | Use "New Inquiry" → Select Referral |

## 🆓 Zero-Cost Setup
The CRM already includes:
- ✅ Automatic CRM storage of inquiries
- ✅ Status tracking (New → Contacted → Quoted → Booked)
- ✅ Activity logging
- ✅ Channel-based reporting on the dashboard
- ✅ Customer matching by phone number
- ✅ AI lead qualification (collects name, date, location, services, budget)
- ✅ Smart follow-ups (24h/72h reminders)
- ✅ Human takeover from WhatsApp Inbox
- ✅ Lead export as CSV

No external services required to get started!