"""
Exercise 6: API Module
Contains all API route handlers organized by functionality
"""

from .knowledge_base import router as knowledge_base_router
from .documents import router as documents_router  
from .qa_pairs import router as qa_pairs_router
from .chat import router as chat_router
from .prompts import router as prompts_router

# Exercise 7 additions will include an agents router providing plan/execute,
# trace replay, prompt versioning, and cost reporting endpoints. The concrete
# router is added in agents.py (scaffolded for students to complete).
try:
    from .agents import router as agents_router  # type: ignore
except Exception:
    agents_router = None  # Allow app to start even if scaffold incomplete

__all__ = [
    "knowledge_base_router",
    "documents_router", 
    "qa_pairs_router",
    "chat_router",
    "prompts_router",
    "agents_router",
]
