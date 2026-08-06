"""
WhatsApp/Instagram/Facebook Webhook Routes - Meta Ads Lead Automation.
Receives incoming WhatsApp messages from Meta ads, runs AI conversation flow,
and stores qualified leads in the CRM.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import re
import os
import requests

from app.database import get_db
from app.models import User, Customer, Inquiry, ActivityLog, Lead, Conversation, Task
from app.auth import verify_token

router = APIRouter(prefix="/api", tags=["Webhooks"])
security = HTTPBearer()

# ============================================
# Configuration (from env vars, not hardcoded)
# ============================================
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "teamshadow-webhook-verify-2024")
WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
META_API_URL = "https://graph.facebook.com/v19.0"

# ============================================
# Conversation State Machine
# ============================================
CONVERSATION_STATES = [
    "welcome",
    "collecting_name",
    "collecting_date",
    "collecting_location",
    "collecting_services",
    "collecting_budget",
    "complete",
    "human",
]

SERVICES_OPTIONS = {
    "photography": "Photography",
    "cinematic_video": "Cinematic Video",
    "event_management": "Event Management",
    "decoration": "Decoration",
    "album": "Album",
}


def detect_intent(message: str) -> str:
    """Detect user intent from message."""
    msg = message.lower()

    # Human handoff detection
    if any(k in msg for k in ['human', 'agent', 'person', 'call', 'talk to someone', 'speak to']):
        return "human_handoff"

    # Question detection
    if any(k in msg for k in ['price', 'cost', 'package', 'rate', 'charge', 'how much']):
        return "pricing_question"

    if any(k in msg for k in ['service', 'offer', 'provide', 'what do you do']):
        return "services_question"

    if any(k in msg for k in ['work', 'portfolio', 'sample', 'example', 'see your']):
        return "portfolio_question"

    if any(k in msg for k in ['available', 'free', 'booked', 'date available']):
        return "availability_question"

    return "answer"


def generate_reply(message: str, state: str, lead_data: dict) -> dict:
    """
    Generate a natural response based on conversation state.
    Returns (reply_text, new_state)
    """
    msg = message.lower()
    intent = detect_intent(message)

    # Handle human handoff at any point
    if intent == "human_handoff":
        return {
            "reply": "Of course! I'll connect you with one of our wedding specialists right away. A human agent will take over this chat shortly. Meanwhile, can you share your phone number so they can reach you faster if needed?",
            "state": "human",
            "needs_human": True
        }

    if state == "welcome":
        return {
            "reply": "🎉 Welcome to Team Shadow Weddings! 💍\n\nWe're excited to help you create memories that last forever.\n\nTo understand your requirements better, could you tell me:\n\n👰 **What's your name or the couple's name?** (e.g., Priya & Rahul)",
            "state": "collecting_name"
        }

    if state == "collecting_name":
        # Validate: should be a name (2+ words or contains &/and)
        if len(message.strip().split()) >= 2 or '&' in message or 'and' in message.lower():
            return {
                "reply": f"Beautiful name, {message.strip()}! 🥰\n\nNow, when is your wedding date? (e.g., December 2026 or 15/12/2026)",
                "state": "collecting_date"
            }
        return {
            "reply": "That's lovely! Could you share your full name or the couple's names? (e.g., Priya & Rahul)",
            "state": "collecting_name"
        }

    if state == "collecting_date":
        # Validate: contains a date pattern
        date_patterns = [
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b',
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{1,2}(st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b',
            r'\b(next\s+(year|month|december|january))\b',
        ]
        if any(re.search(p, msg) for p in date_patterns):
            return {
                "reply": "Perfect! 📅\n\nWhere is the wedding/event taking place? (City & Venue name if known)",
                "state": "collecting_location"
            }
        return {
            "reply": "Could you clarify the wedding date? (e.g., Dec 2026, or a specific date like 15/12/2026)",
            "state": "collecting_date"
        }

    if state == "collecting_location":
        return {
            "reply": "Wonderful location! 📍\n\nWhich services are you interested in? Reply with numbers:\n\n1️⃣ Photography\n2️⃣ Cinematic Video\n3️⃣ Event Management\n4️⃣ Decoration\n5️⃣ Album\n\n(e.g., \"1,2,5\" or \"photography, video, album\")",
            "state": "collecting_services"
        }

    if state == "collecting_services":
        # Parse selected services
        selected = []
        if any(d in msg for d in ['1', 'photography', 'photo']):
            selected.append("Photography")
        if any(d in msg for d in ['2', 'cinematic', 'video', 'videography']):
            selected.append("Cinematic Video")
        if any(d in msg for d in ['3', 'event management', 'management']):
            selected.append("Event Management")
        if any(d in msg for d in ['4', 'decoration', 'decor']):
            selected.append("Decoration")
        if any(d in msg for d in ['5', 'album']):
            selected.append("Album")

        if selected:
            return {
                "reply": f"Great choices! ✨\n\nSelected services: {', '.join(selected)}\n\nWhat's your approximate budget range? (e.g., 5 lakh, 500000, or 5L)",
                "state": "collecting_budget",
                "services": selected
            }
        return {
            "reply": "Could you tell me which services you're interested in? Reply with numbers:\n\n1️⃣ Photography\n2️⃣ Cinematic Video\n3️⃣ Event Management\n4️⃣ Decoration\n5️⃣ Album\n\n(e.g., \"1,2,5\")",
            "state": "collecting_services"
        }

    if state == "collecting_budget":
        # Extract budget
        budget = extract_budget(message)
        if budget:
            return {
                "reply": f"Perfect! Thank you for sharing your budget of approximately ₹{budget:,.0f}. 💰\n\nAll the details I've collected:\n\n👰 Couple: {lead_data.get('customer_name', '-')}\n📅 Date: {lead_data.get('wedding_date', '-')}\n📍 Location: {lead_data.get('wedding_location', '-')}\n✨ Services: {', '.join(lead_data.get('services', [])) if lead_data.get('services') else '-'}\n💰 Budget: ₹{budget:,.0f}\n\nOur team will review your details and send you our best packages shortly! 🚀\n\nIs there anything else you'd like to know while you wait?",
                "state": "complete",
                "budget": budget,
                "complete": True
            }
        return {
            "reply": "Could you share your approximate budget? (e.g., 5 lakh, 500000, or 5L)",
            "state": "collecting_budget"
        }

    if state == "complete":
        return {
            "reply": "Is there anything else I can help you with? You can ask about our packages, services, or type 'human' to talk to our team. 😊",
            "state": "complete"
        }

    if state == "human":
        return {
            "reply": "Our team member will reply to you shortly. Feel free to share any additional details while you wait! 📱",
            "state": "human",
            "needs_human": True
        }

    # Fallback - should not reach here
    return {
        "reply": "Thanks for your message! Let me note that down. Our team will respond shortly.",
        "state": "complete"
    }


def extract_budget(message: str) -> float | None:
    """Extract budget from message."""
    msg = message.lower()
    patterns = [
        r'(\d+)\s*(?:lakh|lac|lakhs|lacs)\b',
        r'₹\s*(\d+[,\d]*)',
        r'rs\.?\s*(\d+[,\d]*)',
        r'budget[:\s]+(\d+[,\d]*)',
        r'(\d+[,\d]*)\s*rupees',
    ]
    for pattern in patterns:
        match = re.search(pattern, msg)
        if match:
            amount = match.group(1).replace(',', '')
            if 'lakh' in pattern or 'lac' in pattern:
                return float(amount) * 100000
            return float(amount)
    return None


# ============================================
# WhatsApp Cloud API Integration
# ============================================
def send_whatsapp_message(to_number: str, message: str) -> bool:
    """Send a WhatsApp message via Meta Cloud API."""
    if not WHATSAPP_API_TOKEN or not WHATSAPP_PHONE_ID:
        print(f"[WhatsApp] Skipped sending (not configured): {message[:50]}...")
        return True  # Simulate success for local testing

    url = f"{META_API_URL}/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.status_code in (200, 201)
    except Exception as e:
        print(f"[WhatsApp] Error sending message: {e}")
        return False


# ============================================
# Webhook Verification (Meta)
# ============================================
@router.get("/webhooks/whatsapp")
def verify_webhook(
    hub_mode: str = Query(...),
    hub_verify_token: str = Query(...),
    hub_challenge: str = Query(...)
):
    """Verify the webhook with Meta's verification request."""
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        return { "hub.challenge": hub_challenge }
    raise HTTPException(status_code=403, detail="Verification failed")


# ============================================
# Main Webhook Handler
# ============================================
@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receive WhatsApp messages from Meta ads.
    Creates a Lead and runs the conversation flow.
    """
    try:
        data = await request.json()
        print(f"[Webhook] Received: {data}")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Parse Meta payload
    entries = data.get("entry", [])
    if not entries:
        return {"status": "ok"}

    results = []
    for entry in entries:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])

            for msg in messages:
                if msg.get("type") != "text":
                    continue

                from_number = msg.get("from", "")
                text = msg.get("text", {}).get("body", "")
                msg_id = msg.get("id", "")

                result = process_message(db, from_number, text, "whatsapp")
                results.append(result)

    return {"status": "ok", "results": results}


@router.post("/webhooks/instagram")
async def instagram_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Instagram DM leads."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    from_number = data.get("from") or data.get("sender_id", "")
    text = data.get("message", "")

    result = process_message(db, from_number, text, "instagram")
    return {"status": "ok", "result": result}


@router.post("/webhooks/facebook")
async def facebook_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Facebook Messenger leads."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    from_number = data.get("from") or data.get("sender_id", "")
    text = data.get("message", "")

    result = process_message(db, from_number, text, "facebook")
    return {"status": "ok", "result": result}


def process_message(db: Session, whatsapp_number: str, message: str, source: str) -> dict:
    """Process an incoming message and run the conversation flow."""
    if not whatsapp_number:
        raise HTTPException(status_code=400, detail="WhatsApp number is required")

    # Find or create lead
    lead = db.query(Lead).filter(Lead.whatsapp_number == whatsapp_number).first()

    if not lead:
        lead = Lead(
            whatsapp_number=whatsapp_number,
            lead_source=source,
            conversation_state="welcome",
            status="new_lead"
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

    # Save user message to conversation
    conversation = Conversation(
        lead_id=lead.id,
        sender="user",
        message=message
    )
    db.add(conversation)
    db.commit()

    # Generate bot reply based on state
    lead_data = {
        "customer_name": lead.customer_name,
        "wedding_date": lead.wedding_date,
        "wedding_location": lead.wedding_location,
        "services": lead.services,
    }

    response = generate_reply(message, lead.conversation_state, lead_data)

    # Update lead based on response
    if lead.conversation_state == "welcome":
        lead.conversation_state = "collecting_name"

    elif lead.conversation_state == "collecting_name":
        lead.customer_name = message.strip()
        lead.conversation_state = "collecting_date"

    elif lead.conversation_state == "collecting_date":
        # Extract date
        lead.wedding_date = extract_date(message)
        lead.conversation_state = "collecting_location"

    elif lead.conversation_state == "collecting_location":
        lead.wedding_location = message.strip()
        lead.conversation_state = "collecting_services"

    elif lead.conversation_state == "collecting_services":
        lead.services = response.get("services", [])
        lead.conversation_state = "collecting_budget"

    elif lead.conversation_state == "collecting_budget":
        lead.budget = response.get("budget")
        if response.get("complete"):
            lead.conversation_state = "complete"
            lead.status = "new_lead"

    elif lead.conversation_state == "human":
        if response.get("needs_human"):
            # Create a task for the sales team
            task = Task(
                title=f"Follow up with {lead.customer_name or 'lead'} ({whatsapp_number})",
                description=f"Lead from {source} requested human agent. Full details: {lead.customer_name}, {lead.wedding_date}, {lead.wedding_location}, Budget: {lead.budget}",
                status="pending",
                priority="high",
                related_type="lead",
                related_id=lead.id
            )
            db.add(task)

    lead.updated_at = datetime.utcnow()
    db.commit()

    # Save bot reply
    bot_conversation = Conversation(
        lead_id=lead.id,
        sender="bot",
        message=response["reply"]
    )
    db.add(bot_conversation)
    db.commit()

    # Send via WhatsApp API (if configured)
    send_whatsapp_message(whatsapp_number, response["reply"])

    return {
        "lead_id": lead.id,
        "status": lead.status,
        "conversation_state": lead.conversation_state,
        "reply": response["reply"]
    }


def extract_date(message: str) -> str | None:
    """Extract date string from message."""
    msg = message.lower()
    patterns = [
        r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)(?:\.)?\s+\d{4}\b',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, msg, re.IGNORECASE)
        if match:
            return match.group(0)
    return message.strip()


# ============================================
# Test Endpoint - Simulate a lead message
# ============================================
@router.post("/webhooks/test")
def test_webhook(data: dict, db: Session = Depends(get_db)):
    """Test endpoint to simulate a WhatsApp message (for local testing)."""
    phone = data.get("from") or data.get("phone", "919876543210")
    message = data.get("message", "")
    source = data.get("source", "whatsapp")

    result = process_message(db, phone, message, source)
    return result


# ============================================
# Lead Management APIs
# ============================================
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/leads")
def list_leads(
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all leads. Filter by status or search by name/phone."""
    query = db.query(Lead)

    if status and status != "all":
        query = query.filter(Lead.status == status)
    if search:
        query = query.filter(
            Lead.customer_name.ilike(f"%{search}%") |
            Lead.whatsapp_number.ilike(f"%{search}%") |
            Lead.wedding_location.ilike(f"%{search}%")
        )

    leads = query.order_by(Lead.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "whatsapp_number": l.whatsapp_number,
            "customer_name": l.customer_name,
            "wedding_date": l.wedding_date,
            "wedding_location": l.wedding_location,
            "services": l.services,
            "budget": l.budget,
            "lead_source": l.lead_source,
            "conversation_state": l.conversation_state,
            "assigned_to": {
                "id": l.assignee.id,
                "full_name": l.assignee.full_name
            } if l.assignee else None,
            "status": l.status,
            "conversation_count": len(l.conversations),
            "created_at": l.created_at.isoformat() if l.created_at else None,
            "updated_at": l.updated_at.isoformat() if l.updated_at else None
        }
        for l in leads
    ]


@router.get("/lead/{lead_id}")
def get_lead(lead_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get lead details with conversation history."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return {
        "id": lead.id,
        "whatsapp_number": lead.whatsapp_number,
        "customer_name": lead.customer_name,
        "wedding_date": lead.wedding_date,
        "wedding_location": lead.wedding_location,
        "services": lead.services,
        "budget": lead.budget,
        "lead_source": lead.lead_source,
        "conversation_state": lead.conversation_state,
        "assigned_to": {
            "id": lead.assignee.id,
            "full_name": lead.assignee.full_name
        } if lead.assignee else None,
        "status": lead.status,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
        "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
        "conversations": [
            {
                "id": c.id,
                "sender": c.sender,
                "message": c.message,
                "timestamp": c.timestamp.isoformat() if c.timestamp else None
            }
            for c in lead.conversations
        ]
    }


@router.patch("/lead/{lead_id}")
def update_lead(lead_id: int, data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update lead status, assignment, or details."""
    payload = verify_token(user.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    current_user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    for key, value in data.items():
        if hasattr(lead, key) and value is not None:
            setattr(lead, key, value)

    lead.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Lead updated successfully"}


@router.post("/send-message")
def send_message(data: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Send a message to a lead (human agent takeover)."""
    payload = verify_token(user.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    current_user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")

    lead_id = data.get("lead_id")
    message = data.get("message", "")

    if not lead_id or not message:
        raise HTTPException(status_code=400, detail="lead_id and message are required")

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Save agent message
    conversation = Conversation(
        lead_id=lead.id,
        sender="agent",
        message=message
    )
    db.add(conversation)

    # Set lead to human state
    lead.conversation_state = "human"
    lead.status = "contacted"
    lead.updated_at = datetime.utcnow()
    db.commit()

    # Send via WhatsApp API
    sent = send_whatsapp_message(lead.whatsapp_number, message)

    return {
        "message": "Message sent successfully",
        "sent": sent
    }


@router.get("/lead/{lead_id}/export")
def export_lead(lead_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Export a single lead's full conversation history (for CSV download)."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Return data formatted for CSV export
    lines = [
        "Lead Export - Team Shadow CRM",
        f"ID,{lead.id}",
        f"Customer,{lead.customer_name or ''}",
        f"WhatsApp,{lead.whatsapp_number}",
        f"Wedding Date,{lead.wedding_date or ''}",
        f"Location,{lead.wedding_location or ''}",
        f"Services,{', '.join(lead.services) if lead.services else ''}",
        f"Budget,{lead.budget or ''}",
        f"Source,{lead.lead_source}",
        f"Status,{lead.status}",
        f"State,{lead.conversation_state}",
        f"Created,{lead.created_at}",
        "",
        "Conversation History",
        "Sender,Message,Timestamp",
    ]
    for c in lead.conversations:
        lines.append(f"{c.sender},{c.message.replace(',', ';')},{c.timestamp}")

    return {"csv": "\n".join(lines)}