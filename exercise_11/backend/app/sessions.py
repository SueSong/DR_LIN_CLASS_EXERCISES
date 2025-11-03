"""
Simple in-memory session store.
In production, use a proper database or Redis.
"""

from typing import Dict, Optional

# In-memory session store: session_id -> parent_name
SESSIONS: Dict[str, Dict[str, any]] = {}


def create_session(session_id: str, parent_name: str) -> None:
    """Create a new session with parent name."""
    SESSIONS[session_id] = {
        "session_id": session_id,
        "parent_name": parent_name,
        "created_at": None  # Could add timestamp if needed
    }


def get_session(session_id: str) -> Optional[Dict[str, any]]:
    """Get session information."""
    return SESSIONS.get(session_id)


def get_parent_name(session_id: str) -> Optional[str]:
    """Get parent name for a session."""
    session = get_session(session_id)
    return session.get("parent_name") if session else None

