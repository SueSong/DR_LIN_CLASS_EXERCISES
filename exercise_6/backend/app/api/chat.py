"""
Exercise 6: Chat API Routes
Handles chat interactions and conversation management
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

# Mock conversation storage
mock_conversations = {}
mock_messages = []

@router.post("/")
async def send_message(chat_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send a message and get AI response"""
    message = chat_data.get("message", "")
    session_id = chat_data.get("session_id", str(uuid.uuid4()))
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Create user message
    user_message = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "type": "user",
        "content": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Create AI response (mock)
    ai_response = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "type": "assistant",
        "content": f"This is a mock response to: {message}",
        "timestamp": datetime.utcnow().isoformat(),
        "sources": {
            "knowledge_base_hits": [],
            "qa_hits": []
        },
        "processing_time_ms": 1500,
        "model_used": "gpt-3.5-turbo"
    }
    
    # Store messages
    mock_messages.extend([user_message, ai_response])
    
    # Update conversation
    if session_id not in mock_conversations:
        mock_conversations[session_id] = {
            "id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "message_count": 0
        }
    
    mock_conversations[session_id]["message_count"] += 2
    mock_conversations[session_id]["updated_at"] = datetime.utcnow().isoformat()
    
    return {
        "status": "success",
        "data": {
            "id": ai_response["id"],
            "message": message,
            "response": ai_response["content"],
            "sources": [],
            "qa_matches": [],
            "timestamp": ai_response["timestamp"],
            "processing_time_ms": ai_response["processing_time_ms"],
            "model_used": ai_response["model_used"],
            "session_id": session_id
        }
    }

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0
) -> Dict[str, Any]:
    """Get chat history for a session"""
    if session_id not in mock_conversations:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get messages for this session
    session_messages = [
        msg for msg in mock_messages 
        if msg.get("session_id") == session_id
    ]
    
    # Apply pagination
    paginated_messages = session_messages[offset:offset + limit]
    
    return {
        "status": "success",
        "data": {
            "session_id": session_id,
            "messages": paginated_messages,
            "total_messages": len(session_messages),
            "conversation": mock_conversations[session_id]
        }
    }

@router.get("/sessions")
async def list_chat_sessions(
    limit: Optional[int] = 20,
    offset: Optional[int] = 0
) -> Dict[str, Any]:
    """List all chat sessions"""
    sessions = list(mock_conversations.values())
    
    # Sort by updated_at descending
    sessions.sort(key=lambda x: x["updated_at"], reverse=True)
    
    # Apply pagination
    paginated_sessions = sessions[offset:offset + limit]
    
    return {
        "status": "success",
        "data": paginated_sessions,
        "total": len(sessions),
        "limit": limit,
        "offset": offset
    }

@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str) -> Dict[str, Any]:
    """Delete a chat session and all its messages"""
    if session_id not in mock_conversations:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Remove session
    del mock_conversations[session_id]
    
    # Remove all messages for this session
    global mock_messages
    mock_messages = [
        msg for msg in mock_messages 
        if msg.get("session_id") != session_id
    ]
    
    return {
        "status": "success",
        "message": f"Session {session_id} deleted successfully"
    }

@router.post("/feedback")
async def submit_chat_feedback(feedback_data: Dict[str, Any]) -> Dict[str, Any]:
    """Submit feedback for a chat response"""
    message_id = feedback_data.get("message_id")
    rating = feedback_data.get("rating")  # 1-5 stars
    comment = feedback_data.get("comment", "")
    
    if not message_id or not rating:
        raise HTTPException(status_code=400, detail="Message ID and rating are required")
    
    # In a real implementation, this would be stored in a database
    feedback = {
        "id": str(uuid.uuid4()),
        "message_id": message_id,
        "rating": rating,
        "comment": comment,
        "submitted_at": datetime.utcnow().isoformat()
    }
    
    return {
        "status": "success",
        "message": "Feedback submitted successfully",
        "data": feedback
    }
