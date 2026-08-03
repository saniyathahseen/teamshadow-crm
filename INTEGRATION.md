# 📱 WhatsApp & Instagram Inquiry Integration Guide

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

### Option 4: API Integration (For Developers)
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
2. **Get API Access** using Twilio, Meta Cloud API, or WATI
3. **Create a Webhook** that receives new messages and calls our API:

```python
# webhook_example.py
import requests

def whatsapp_webhook(message_data):
    """Forward WhatsApp messages to Team Shadow CRM"""
    response = requests.post(
        "http://localhost:8000/api/inquiries",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        json={
            "source": "whatsapp",
            "customer_name": message_data.get("customer_name", "WhatsApp Lead"),
            "phone": message_data.get("phone"),
            "message": message_data.get("text", "")
        }
    )
    return response.json()
```

## 📸 Setting up Instagram API

1. **Convert to Instagram Business Account**
2. **Get API Access** via Meta Graph API
3. **Create a Webhook** that forwards DMs:

```python
# instagram_webhook.py
import requests

def instagram_webhook(dm_data):
    """Forward Instagram DMs to Team Shadow CRM"""
    response = requests.post(
        "http://localhost:8000/api/inquiries",
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        json={
            "source": "instagram",
            "customer_name": dm_data.get("sender_name", "Instagram Lead"),
            "message": dm_data.get("message", "")
        }
    )
    return response.json()
```

## 📧 Email Integration (Simple)

Set up a **Gmail filter** that forwards inquiries from your contact form to:
- Your email: `inquiries@teamshadow.com`
- The team quickly adds them via the CRM interface

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

No external services required to get started!