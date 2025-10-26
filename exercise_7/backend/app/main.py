"""
Exercise 6: RAG Chatbot - Complete Main Application
Full-featured FastAPI application with all expected imports and modules
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import os
import tempfile
import asyncio

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configuration and database
from app.config import settings
from app.database import init_database, close_database, get_database_health

# API routes - all the modules students expect
from app.api import knowledge_base, documents, qa_pairs, chat
from app.api import agents as agents_module
from app.api import prompts as prompts_module

# Services - vector store and LLM service initialization
from app.services.vector_store import init_chromadb, close_chromadb
from app.services.rag.llm_service import init_llm_service

# Utilities - logging setup
from app.utils.logging import setup_app_logging

# RAG services
from app.services.rag.qa_service import qa_service

# Setup application logging
app_logger = setup_app_logging(level=settings.log_level)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Exercise 6: RAG Chatbot",
    description="Complete RAG (Retrieval-Augmented Generation) Chatbot with PostgreSQL + pgvector and ChromaDB",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,  # Set to False for student class
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
rag_service = None
services_initialized = False

@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup"""
    global services_initialized
    
    logger.info("🚀 Starting RAG Chatbot (Complete Version)...")
    
    try:
        # Initialize database
        logger.info("📊 Initializing database connection...")
        await init_database()
        
        # Initialize ChromaDB
        logger.info("🔗 Initializing ChromaDB...")
        chromadb_success = await init_chromadb(
            host=settings.chromadb_host, 
            port=settings.chromadb_port
        )
        
        # Initialize LLM service
        logger.info("🤖 Initializing LLM service...")
        llm_success = await init_llm_service()
        
        # Initialize RAG service (lazy import to avoid startup hang)
        try:
            from app.services.rag.rag_service import rag_service as rag_svc
            global rag_service
            rag_service = rag_svc
            logger.info("✅ RAG service loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load RAG service: {e}")
            rag_service = None
        
        services_initialized = True
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        logger.info("⚠️ Continuing in demo mode...")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("🛑 Shutting down RAG Chatbot...")
    
    try:
        # Close ChromaDB
        await close_chromadb()
        
        # Close database
        await close_database()
        
        logger.info("✅ Shutdown completed")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

# Include API routers
app.include_router(knowledge_base.router)
app.include_router(documents.router)
app.include_router(qa_pairs.router)
app.include_router(chat.router)
app.include_router(prompts_module.router)
if getattr(agents_module, "agents_router", None):
    app.include_router(agents_module.agents_router)
else:
    # Fallback: directly import router from agents module we created
    try:
        from app.api.agents import router as agents_router
        app.include_router(agents_router)
    except Exception:
        pass

# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "rag-chatbot",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with service status"""
    health_status = {
        "status": "healthy",
        "service": "rag-chatbot",
        "version": "1.0.0",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "services_initialized": services_initialized,
        "dependencies": {}
    }
    
    # Check database health
    try:
        db_health = await get_database_health()
        health_status["dependencies"]["database"] = {
            "status": "healthy" if db_health else "unhealthy",
            "details": db_health
        }
    except Exception as e:
        health_status["dependencies"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Check ChromaDB health
    try:
        from app.services.vector_store import get_chromadb_status
        chromadb_status = await get_chromadb_status()
        health_status["dependencies"]["chromadb"] = chromadb_status
    except Exception as e:
        health_status["dependencies"]["chromadb"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check LLM service health
    try:
        from app.services.rag.llm_service import get_llm_service
        llm_service = get_llm_service()
        if llm_service:
            llm_healthy = await llm_service.check_api_connection()
            health_status["dependencies"]["llm"] = {
                "status": "healthy" if llm_healthy else "unhealthy",
                "model": settings.openai_model
            }
        else:
            health_status["dependencies"]["llm"] = {
                "status": "not_initialized"
            }
    except Exception as e:
        health_status["dependencies"]["llm"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Determine overall status
    all_healthy = all(
        dep.get("status") == "healthy" 
        for dep in health_status["dependencies"].values()
    )
    
    if not all_healthy:
        health_status["status"] = "degraded"
    
    return health_status

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Exercise 6: RAG Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "knowledge_base": "/api/v1/knowledge-base",
            "documents": "/api/v1/documents", 
            "qa_pairs": "/api/v1/qa-pairs",
            "chat": "/api/v1/chat"
        },
        "features": [
            "Document upload and processing",
            "Q&A pair management",
            "RAG-powered chat",
            "PostgreSQL + pgvector for document storage",
            "ChromaDB for Q&A pairs",
            "OpenAI integration",
            "Complete REST API"
        ]
    }

# Configuration endpoint
@app.get("/config", tags=["Configuration"])
async def get_configuration():
    """Get current application configuration (non-sensitive)"""
    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "openai_model": settings.openai_model,
        "rag_embedding_model": settings.rag_embedding_model,
        "similarity_threshold": settings.similarity_threshold,
        "max_file_size": settings.max_file_size,
        "allowed_file_types": settings.allowed_file_types,
        "chromadb_host": settings.chromadb_host,
        "chromadb_port": settings.chromadb_port,
        "cors_origins": settings.cors_origins
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )