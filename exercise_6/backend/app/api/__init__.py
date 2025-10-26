"""
Exercise 6: API Module
Contains all API route handlers organized by functionality
"""

from .knowledge_base import router as knowledge_base_router
from .documents import router as documents_router  
from .qa_pairs import router as qa_pairs_router
from .chat import router as chat_router

__all__ = [
    "knowledge_base_router",
    "documents_router", 
    "qa_pairs_router",
    "chat_router"
]
