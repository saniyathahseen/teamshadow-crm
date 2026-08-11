"""
Automation Service - Smart follow-ups and AI knowledge base.
Handles automated follow-up messages and knowledge-based AI responses.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import re

from app.models import Lead, Conversation, Automation, KnowledgeBase, Business, Task


# ============================================
# Follow-up Automation
# ============================================

def check_follow_ups(db: Session):
    """
    Check all leads for follow-up needs.
    Sends follow-up messages to leads that haven't responded.
    """
    now = datetime.utcnow()
    follow_ups_sent = []

    # Get all active automations for follow-up
    automations = db.query(Automation).filter(
        Automation.trigger == "NO_CUSTOMER_REPLY",
        Automation.active == True  # noqa: E712
    ).all()

    for automation in automations:
        # Find leads for this business that haven't responded
        leads = db.query(Lead).filter(
            Lead.status.in_(["new_lead", "qualified", "contacted"]),
            Lead.updated_at < now - timedelta(hours=automation.delay_hours)
        ).all()

        for lead in leads:
            # Check if last message was from bot/agent (customer hasn't replied)
            last_msg = db.query(Conversation).filter(
                Conversation.lead_id == lead.id
            ).order_by(Conversation.timestamp.desc()).first()

            if last_msg and last_msg.sender != "user":
                # Send follow-up
                message = automation.message_template or (
                    f"Hi {lead.customer_name or 'there'}! Just checking if you'd still like "
                    f"us to share our packages. Let us know if you have any questions! 😊"
                )

                # Save follow-up message
                conv = Conversation(
                    lead_id=lead.id,
                    sender="bot",
                    message=message
                )
                db.add(conv)
                lead.updated_at = now
                db.commit()

                follow_ups_sent.append({
                    "lead_id": lead.id,
                    "customer": lead.customer_name,
                    "message": message
                })

    return follow_ups_sent


# ============================================
# AI Knowledge Base
# ============================================

def answer_from_knowledge_base(db: Session, business_id: int, message: str) -> str | None:
    """
    Try to answer a question using the business's knowledge base.
    Returns None if no match found.
    """
    if not business_id:
        return None

    msg = message.lower()
    knowledge_items = db.query(KnowledgeBase).filter(
        KnowledgeBase.business_id == business_id
    ).all()

    best_match = None
    best_score = 0

    for item in knowledge_items:
        score = 0
        # Check question keywords
        keywords = item.keywords or []
        for kw in keywords:
            if kw.lower() in msg:
                score += 2

        # Check question text
        if item.question.lower() in msg:
            score += 3

        if score > best_score:
            best_score = score
            best_match = item

    if best_match and best_score >= 2:
        return best_match.answer

    return None


def generate_business_reply(db: Session, business: Business, message: str) -> str | None:
    """
    Generate a reply based on business knowledge.
    Handles pricing, services, location, hours questions.
    """
    if not business:
        return None

    msg = message.lower()

    # Pricing questions
    if any(k in msg for k in ['price', 'cost', 'how much', 'rate', 'charge', 'package']):
        if business.starting_price:
            return (
                f"Our packages start from AED {business.starting_price:,.0f}. "
                f"We offer: {', '.join(business.services) if business.services else 'various services'}. "
                f"Would you like to share more details so we can give you an exact quote?"
            )
        return (
            f"We'd love to share our pricing with you! "
            f"Could you tell us more about your requirements?"
        )

    # Services questions
    if any(k in msg for k in ['service', 'offer', 'provide', 'what do you do']):
        if business.services:
            return (
                f"We offer: {', '.join(business.services)}. "
                f"Is there anything specific you're interested in?"
            )
        return "We offer a range of services. What are you looking for?"

    # Location questions
    if any(k in msg for k in ['where', 'location', 'address', 'based']):
        if business.location:
            return f"We're located in {business.location}. Would you like directions?"
        return None

    # Hours questions
    if any(k in msg for k in ['hours', 'open', 'working', 'timing']):
        if business.working_hours:
            return f"Our working hours are: {business.working_hours}. How can we help?"
        return None

    return None


# ============================================
# Lead Scoring
# ============================================

def score_lead(lead: Lead) -> int:
    """Simple lead scoring based on collected information."""
    score = 0
    if lead.customer_name:
        score += 20
    if lead.wedding_date:
        score += 20
    if lead.wedding_location:
        score += 20
    if lead.services and len(lead.services) > 0:
        score += 20
    if lead.budget and lead.budget > 0:
        score += 20
    return score


# ============================================
# Lead Status Transitions
# ============================================

def update_lead_status(db: Session, lead: Lead, new_status: str) -> dict:
    """Update lead status and create task for team if needed."""
    old_status = lead.status
    lead.status = new_status
    lead.updated_at = datetime.utcnow()
    db.commit()

    # Create task for sales team on new lead
    if new_status == "new_lead" and old_status != "new_lead":
        task = Task(
            title=f"New lead: {lead.customer_name or 'Unknown'} ({lead.whatsapp_number})",
            description=f"New lead from {lead.lead_source}. "
                        f"Date: {lead.wedding_date or 'TBD'}, "
                        f"Location: {lead.wedding_location or 'TBD'}, "
                        f"Budget: {lead.budget or 'TBD'}",
            status="pending",
            priority="high",
            related_type="lead",
            related_id=lead.id
        )
        db.add(task)
        db.commit()

    return {
        "lead_id": lead.id,
        "old_status": old_status,
        "new_status": new_status
    }