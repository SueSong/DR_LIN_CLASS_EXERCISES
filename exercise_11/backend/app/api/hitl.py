"""
HITL (Human-in-the-Loop) API endpoints
Handles mentor queue and replies for crisis situations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from ..guardrails import (
    get_hitl_queue,
    get_hitl_item,
    update_hitl_item,
    get_session_hitl_replies,
    HITL_QUEUE  # Import the queue directly for debugging
)

router = APIRouter(prefix="/api/hitl", tags=["hitl"])


class MentorReplyRequest(BaseModel):
    """Request to add mentor reply to HITL item"""
    mentor_reply: str


@router.get("/queue")
async def get_queue(status: Optional[str] = "pending"):
    """
    Get HITL queue items.
    
    Query params:
        status: Filter by status (default: "pending")
    """
    try:
        items = get_hitl_queue(status=status)
        # Debug: Also return all items for troubleshooting
        all_items = list(HITL_QUEUE.values())
        return {
            "items": items,
            "count": len(items),
            "debug": {
                "total_items_in_queue": len(HITL_QUEUE),
                "all_statuses": [item.get("status") for item in all_items]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{hitl_id}")
async def get_item_details(hitl_id: str):
    """Get details of a specific HITL item."""
    item = get_hitl_item(hitl_id)
    if not item:
        raise HTTPException(status_code=404, detail="HITL item not found")
    return item


@router.post("/{hitl_id}/reply")
async def submit_mentor_reply(hitl_id: str, request: MentorReplyRequest):
    """
    Submit mentor reply to a HITL item.
    The reply will be sent to the parent's chat session.
    """
    if not request.mentor_reply or not request.mentor_reply.strip():
        raise HTTPException(status_code=400, detail="mentor_reply is required")
    
    success = update_hitl_item(hitl_id, request.mentor_reply.strip())
    if not success:
        raise HTTPException(status_code=404, detail="HITL item not found")
    
    item = get_hitl_item(hitl_id)
    return {
        "success": True,
        "hitl_id": hitl_id,
        "mentor_reply": item["mentor_reply"],
        "session_id": item["session_id"]
    }


@router.get("/session/{session_id}/replies")
async def get_session_replies(session_id: str):
    """Get all mentor replies for a specific session."""
    replies = get_session_hitl_replies(session_id)
    return {
        "session_id": session_id,
        "replies": replies,
        "count": len(replies)
    }
