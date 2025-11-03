"""
Guardrails Module
Extends safety guards with PII detection and HITL queue integration.
Routes crisis prompts to HITL for human review.
"""

import re
import time
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .guards import SafetyGuard, SafetyClassification, check_message_safety

# In-memory HITL queue (in production, use a database)
HITL_QUEUE: Dict[str, Dict] = {}

# PII patterns for detection
PII_PATTERNS = {
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "phone": re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
    "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    "credit_card": re.compile(r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b'),
    "address": re.compile(r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)'),
    "ip_address": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
}


def detect_pii(message: str) -> List[Dict[str, any]]:
    """
    Detect PII (Personally Identifiable Information) in a message.
    
    Args:
        message: User message to scan
        
    Returns:
        List of detected PII entities with type and text
    """
    detected_pii = []
    message_lower = message.lower()
    
    for pii_type, pattern in PII_PATTERNS.items():
        matches = pattern.finditer(message)
        for match in matches:
            detected_pii.append({
                "type": pii_type,
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "context": message[max(0, match.start()-20):min(len(message), match.end()+20)]
            })
    
    # Remove duplicates
    seen = set()
    unique_pii = []
    for item in detected_pii:
        key = (item["type"], item["text"])
        if key not in seen:
            seen.add(key)
            unique_pii.append(item)
    
    return unique_pii


def check_and_queue_crisis(
    message: str,
    session_id: str,
    parent_name: Optional[str] = None
) -> Tuple[SafetyClassification, Optional[str], Optional[str]]:
    """
    Check message for crisis situations and queue to HITL if needed.
    
    This function must complete in <500ms to meet SLO requirements.
    
    Args:
        message: User message to check
        session_id: Current session ID
        parent_name: Parent's name (if available)
        
    Returns:
        Tuple of (classification, refusal_message, hitl_id)
        - classification: SAFE, BLOCKED, or ESCALATE
        - refusal_message: Template response if blocked/escalated
        - hitl_id: ID of HITL queue item if queued, None otherwise
    """
    start_time = time.time()
    
    # Use existing safety guard for classification
    classification, refusal_message, safety_metadata = check_message_safety(message, session_id)
    
    print(f"[HITL DEBUG] Message: '{message[:50]}...', Classification: {classification.value}, Session: {session_id}")
    
    # If crisis detected, queue to HITL
    hitl_id = None
    if classification == SafetyClassification.ESCALATE:
        print(f"[HITL DEBUG] ESCALATE detected! Queuing to HITL...")
        hitl_id = queue_to_hitl(
            message=message,
            session_id=session_id,
            parent_name=parent_name,
            classification=classification.value,
            safety_metadata=safety_metadata
        )
        print(f"[HITL DEBUG] Queued successfully! hitl_id: {hitl_id}")
    else:
        print(f"[HITL DEBUG] Not ESCALATE (was {classification.value}), skipping HITL queue")
    
    # Ensure we meet <500ms requirement
    elapsed_ms = (time.time() - start_time) * 1000
    if elapsed_ms > 500:
        # Log warning but don't fail - HITL queuing is already done
        print(f"Warning: Crisis routing took {elapsed_ms:.2f}ms (target: <500ms)")
    
    return classification, refusal_message, hitl_id


def queue_to_hitl(
    message: str,
    session_id: str,
    parent_name: Optional[str] = None,
    classification: str = "escalate",
    safety_metadata: Optional[Dict] = None
) -> str:
    """
    Queue a crisis message to HITL (Human-in-the-Loop) for mentor review.
    
    Args:
        message: Original user message
        session_id: Session ID
        parent_name: Parent's name
        classification: Safety classification
        safety_metadata: Additional safety metadata
        
    Returns:
        HITL queue item ID
    """
    hitl_id = str(uuid.uuid4())
    
    # Detect PII in message
    detected_pii = detect_pii(message)
    
    # Create HITL queue item
    hitl_item = {
        "hitl_id": hitl_id,
        "session_id": session_id,
        "parent_name": parent_name or "Unknown",
        "message": message,
        "classification": classification,
        "primary_category": safety_metadata.get("primary_category") if safety_metadata else None,
        "detected_pii": detected_pii,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "mentor_reply": None,
        "mentor_replied_at": None,
    }
    
    # Store in queue
    HITL_QUEUE[hitl_id] = hitl_item
    
    # Debug logging
    print(f"[HITL] Queued item {hitl_id} for session {session_id}, status: {hitl_item['status']}, queue size: {len(HITL_QUEUE)}")
    
    return hitl_id


def get_hitl_queue(status: Optional[str] = "pending") -> List[Dict]:
    """
    Get HITL queue items, optionally filtered by status.
    
    Args:
        status: Filter by status ("pending", "reviewed", "replied", etc.)
        
    Returns:
        List of HITL queue items
    """
    if status:
        return [
            {
                "hitl_id": item["hitl_id"],
                "session_id": item["session_id"],
                "parent_name": item["parent_name"],
                "message": item["message"],
                "classification": item["classification"],
                "primary_category": item["primary_category"],
                "detected_pii": item["detected_pii"],
                "status": item["status"],
                "created_at": item["created_at"],
                "mentor_reply": item.get("mentor_reply"),
                "mentor_replied_at": item.get("mentor_replied_at"),
            }
            for item in HITL_QUEUE.values()
            if item["status"] == status
        ]
    else:
        return list(HITL_QUEUE.values())


def get_hitl_item(hitl_id: str) -> Optional[Dict]:
    """Get a specific HITL item by ID."""
    return HITL_QUEUE.get(hitl_id)


def update_hitl_item(hitl_id: str, mentor_reply: str) -> bool:
    """
    Update HITL item with mentor reply.
    
    Args:
        hitl_id: HITL item ID
        mentor_reply: Mentor's response message
        
    Returns:
        True if updated successfully, False if item not found
    """
    if hitl_id not in HITL_QUEUE:
        return False
    
    HITL_QUEUE[hitl_id]["mentor_reply"] = mentor_reply
    HITL_QUEUE[hitl_id]["mentor_replied_at"] = datetime.utcnow().isoformat()
    HITL_QUEUE[hitl_id]["status"] = "replied"
    
    return True


def get_session_hitl_replies(session_id: str) -> List[Dict]:
    """
    Get all mentor replies for a session.
    
    Args:
        session_id: Session ID
        
    Returns:
        List of HITL items with mentor replies for this session
    """
    return [
        {
            "hitl_id": item["hitl_id"],
            "message": item["message"],
            "mentor_reply": item.get("mentor_reply"),
            "mentor_replied_at": item.get("mentor_replied_at"),
        }
        for item in HITL_QUEUE.values()
        if item["session_id"] == session_id and item.get("mentor_reply")
    ]

