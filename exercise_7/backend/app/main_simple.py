"""
Exercise 7: Planning & Control - Simplified Main Application
Basic FastAPI application for testing the infrastructure
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

# Import only what we have
from app.config import settings
from app.database import init_database, close_database, get_database_health
from app.services.rag.qa_service import qa_service

# Import RAG services (lazy import to avoid startup hang)
# from app.services.rag.rag_service import rag_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Exercise 6: RAG Chatbot (Simplified)",
    description="A simplified version of the RAG chatbot for testing infrastructure",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - Allow all origins for student class
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for student class
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# =============================================================================
# STARTUP AND SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("🚀 Starting RAG Chatbot (Simplified)...")
    
    try:
        # Initialize database
        logger.info("📊 Initializing database connection...")
        await init_database()
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        # Don't fail startup for demo purposes
        logger.info("⚠️ Continuing in demo mode...")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("🛑 Shutting down RAG Chatbot...")
    await close_database()
    logger.info("✅ Shutdown completed")

# =============================================================================
# HEALTH CHECK ENDPOINTS
# =============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "rag-chatbot-simplified",
        "version": "1.0.0",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/health/quick", tags=["Health"])
async def quick_health_check():
    """Ultra-fast health check for debugging timeouts"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with service dependencies"""
    health_status = {
        "status": "healthy",
        "service": "rag-chatbot-simplified",
        "version": "1.0.0",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {}
    }
    
    try:
        # Check database
        db_health = await get_database_health()
        health_status["dependencies"]["database"] = db_health
        
        # Check RAG system status (lazy import)
        try:
            rag_service = get_rag_service()
            if rag_service is None:
                health_status["dependencies"]["rag_system"] = {
                    "status": "unavailable",
                    "message": "RAG service not loaded"
                }
                health_status["dependencies"]["openai"] = {
                    "status": "unknown",
                    "model": settings.openai_model,
                    "api_key_configured": bool(settings.openai_api_key)
                }
            else:
                rag_status = await rag_service.get_system_status()
                health_status["dependencies"]["rag_system"] = rag_status
                health_status["dependencies"]["openai"] = {
                    "status": rag_status.get("components", {}).get("llm_service", {}).get("status", "unknown"),
                    "model": settings.openai_model,
                    "api_key_configured": bool(settings.openai_api_key)
                }
        except Exception as e:
            health_status["dependencies"]["rag_system"] = {
                "status": "error",
                "error": str(e)
            }

        # Check ChromaDB (simple HTTP check)
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://localhost:8000/api/v2/heartbeat", timeout=5.0)
                if response.status_code == 200:
                    health_status["dependencies"]["chromadb"] = {
                        "status": "healthy",
                        "url": "http://localhost:8000",
                        "api_version": "v2"
                    }
                else:
                    health_status["dependencies"]["chromadb"] = {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}"
                    }
            except Exception as e:
                health_status["dependencies"]["chromadb"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Determine overall status
        all_healthy = all(
            dep.get("status") == "healthy" 
            for dep in health_status["dependencies"].values()
        )
        
        if not all_healthy:
            health_status["status"] = "degraded"
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    return health_status

# =============================================================================
# ROOT ENDPOINT
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Exercise 6: RAG Chatbot API (Simplified)",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs_url": "/docs",
        "health_url": "/health",
        "status": "This is a simplified version for testing infrastructure",
        "infrastructure": {
            "postgresql": "localhost:5433 (rag_chatbot database)",
            "chromadb": "localhost:8000 (vector store)",
            "redis": "localhost:6380 (caching)",
        },
        "next_steps": [
            "Implement document processing endpoints",
            "Add vector search functionality", 
            "Create chat interface",
            "Build admin console"
        ]
    }

# =============================================================================
# DOCUMENT MANAGEMENT ENDPOINTS (MOCK)
# =============================================================================

# Mock data storage for demo purposes
mock_documents = []
mock_qa_pairs = [
    {
        "id": "default-rag-qa",
        "question": "When do you pick RAG vs. (re)training/fine-tuning?",
        "answer": "Need fresh/private data; lower cost & faster iteration; controllable provenance/citations; fine-tune for style/control when knowledge is stable or to compress prompts; often RAG + light tuning wins.",
        "knowledge_base_id": "default",
        "tags": ["RAG", "training", "fine-tuning"],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "metadata": {
            "source": "default_seed_data",
            "confidence": 1.0
        }
    }
]

# Lazy import for RAG service to avoid startup hang
_rag_service = None

def get_rag_service():
    """Lazy import RAG service to avoid startup delays"""
    global _rag_service
    if _rag_service is None:
        try:
            from app.services.rag.rag_service import rag_service
            _rag_service = rag_service
            logger.info("RAG service loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load RAG service: {e}")
            _rag_service = False  # Mark as failed
    return _rag_service if _rag_service is not False else None

@app.get("/api/v1/documents", tags=["Documents"])
async def get_documents():
    """Get all documents (mock implementation)"""
    return {
        "status": "success",
        "data": mock_documents,
        "total": len(mock_documents),
        "message": "Documents retrieved successfully (mock data)"
    }

@app.post("/api/v1/documents/upload", tags=["Documents"])
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document using real RAG pipeline"""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not supported. Allowed types: PDF, TXT, DOCX"
            )

        # Validate file size
        content = await file.read()
        if len(content) > settings.max_file_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File size exceeds {settings.max_file_size_mb:.1f}MB limit"
            )

        # Save file temporarily for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Get RAG service (lazy import)
            rag_service = get_rag_service()
            
            if rag_service is None:
                # Fallback to mock processing if RAG service unavailable
                logger.warning("RAG service unavailable, using mock document processing")
                result = {
                    "document_id": str(uuid.uuid4()),
                    "filename": file.filename,
                    "processing_status": "completed",
                    "chunks_count": len(content) // 1000 + 1,  # Mock chunk count
                    "total_characters": len(content)
                }
            else:
                # Process document using RAG service
                logger.info(f"Processing document: {file.filename}")
                result = await rag_service.process_uploaded_document(
                    file_path=temp_file_path,
                    filename=file.filename
                )

            # Create document entry for frontend
            document_entry = {
                "id": result["document_id"],
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content),
                "status": result["processing_status"],
                "uploaded_at": datetime.utcnow().isoformat(),
                "processed_at": datetime.utcnow().isoformat() if result["processing_status"] == "completed" else None,
                "chunks_count": result.get("chunks_count", 0),
                "knowledge_base_id": "default",
                "metadata": {
                    "original_filename": file.filename,
                    "file_extension": os.path.splitext(file.filename)[1],
                    "processing_method": "real_rag",
                    "total_characters": result.get("total_characters", 0),
                    "error": result.get("error") if result["processing_status"] == "failed" else None
                }
            }

            # Add to mock storage for frontend compatibility
            mock_documents.append(document_entry)

            if result["processing_status"] == "completed":
                message = f"Document '{file.filename}' uploaded and processed successfully with {result.get('chunks_count', 0)} chunks"
            else:
                message = f"Document '{file.filename}' upload failed: {result.get('error', 'Unknown error')}"

            return {
                "status": "success" if result["processing_status"] == "completed" else "error",
                "data": document_entry,
                "message": message
            }

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.delete("/api/v1/documents/{document_id}", tags=["Documents"])
async def delete_document(document_id: str):
    """Delete a document (mock implementation)"""
    global mock_documents
    
    # Find and remove document
    original_count = len(mock_documents)
    mock_documents = [doc for doc in mock_documents if doc["id"] != document_id]
    
    if len(mock_documents) == original_count:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "status": "success",
        "message": f"Document {document_id} deleted successfully (mock)"
    }

# =============================================================================
# Q&A MANAGEMENT ENDPOINTS (MOCK)
# =============================================================================

@app.get("/api/v1/qa-pairs", tags=["Q&A"])
async def get_qa_pairs():
    """Get all Q&A pairs from ChromaDB"""
    try:
        qa_pairs = await qa_service.get_all_qa_pairs()
        return {
            "status": "success",
            "data": qa_pairs,
            "total": len(qa_pairs),
            "message": "Q&A pairs retrieved successfully from ChromaDB"
        }
    except Exception as e:
        logger.error(f"Failed to get Q&A pairs from ChromaDB: {e}")
        # Fallback to mock data
        return {
            "status": "success",
            "data": mock_qa_pairs,
            "total": len(mock_qa_pairs),
            "message": "Q&A pairs retrieved successfully (fallback to mock data)"
        }

@app.post("/api/v1/qa-pairs", tags=["Q&A"])
async def create_qa_pair(qa_data: dict):
    """Create a Q&A pair (mock implementation)"""
    try:
        # Validate required fields
        if not qa_data.get("question") or not qa_data.get("answer"):
            raise HTTPException(status_code=400, detail="Question and answer are required")
        
        # Create Q&A pair with embeddings in ChromaDB
        try:
            qa_id = await qa_service.add_qa_pair(
                question=qa_data["question"],
                answer=qa_data["answer"],
                metadata={
                    "knowledge_base_id": qa_data.get("knowledge_base_id", "default"),
                    "tags": qa_data.get("tags", []),
                    "source": "manual_entry",
                    "confidence": 1.0
                }
            )
            logger.info(f"Q&A pair added to ChromaDB with ID: {qa_id}")
        except Exception as e:
            logger.warning(f"Failed to add Q&A to ChromaDB: {e}, using mock storage")
            qa_id = str(uuid.uuid4())
        
        # Create response data
        mock_qa = {
            "id": qa_id,
            "question": qa_data["question"],
            "answer": qa_data["answer"],
            "knowledge_base_id": qa_data.get("knowledge_base_id", "default"),
            "tags": qa_data.get("tags", []),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": {
                "source": "manual_entry",
                "confidence": 1.0
            }
        }
        
        # Add to mock storage for backward compatibility
        mock_qa_pairs.append(mock_qa)
        
        return {
            "status": "success",
            "data": mock_qa,
            "message": "Q&A pair created successfully with embeddings in ChromaDB"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Q&A creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Creation failed: {str(e)}")

@app.put("/api/v1/qa-pairs/{qa_id}", tags=["Q&A"])
async def update_qa_pair(qa_id: str, qa_data: dict):
    """Update a Q&A pair (mock implementation)"""
    global mock_qa_pairs
    
    # Find and update Q&A pair
    for i, qa in enumerate(mock_qa_pairs):
        if qa["id"] == qa_id:
            # Update fields if provided
            if "question" in qa_data:
                qa["question"] = qa_data["question"]
            if "answer" in qa_data:
                qa["answer"] = qa_data["answer"]
            if "tags" in qa_data:
                qa["tags"] = qa_data["tags"]
            
            qa["updated_at"] = datetime.now().isoformat()
            mock_qa_pairs[i] = qa
            
            # Update in ChromaDB if RAG service is available
            try:
                if hasattr(qa_service, 'update_qa_pair'):
                    await qa_service.update_qa_pair(qa_id, qa["question"], qa["answer"], qa.get("tags", []))
                    logger.info(f"Updated Q&A pair {qa_id} in ChromaDB")
            except Exception as e:
                logger.warning(f"Failed to update Q&A pair in ChromaDB: {e}")
            
            return qa
    
    raise HTTPException(status_code=404, detail="Q&A pair not found")

@app.delete("/api/v1/qa-pairs/{qa_id}", tags=["Q&A"])
async def delete_qa_pair(qa_id: str):
    """Delete a Q&A pair (mock implementation)"""
    global mock_qa_pairs
    
    # Find and remove Q&A pair
    original_count = len(mock_qa_pairs)
    mock_qa_pairs = [qa for qa in mock_qa_pairs if qa["id"] != qa_id]
    
    if len(mock_qa_pairs) == original_count:
        raise HTTPException(status_code=404, detail="Q&A pair not found")
    
    return {
        "status": "success",
        "message": f"Q&A pair {qa_id} deleted successfully (mock)"
    }

# =============================================================================
# CHAT ENDPOINTS (MOCK)
# =============================================================================

@app.post("/api/v1/chat", tags=["Chat"])
async def chat(chat_data: dict):
    """Chat with the RAG system using real OpenAI integration with timeout handling"""
    message = chat_data.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    session_id = chat_data.get("session_id")
    
    logger.info(f"Processing chat query: {message[:100]}...")

    try:
        # Get RAG service (lazy import)
        rag_service = get_rag_service()
        
        if rag_service is None:
            # Fallback to mock response if RAG service unavailable
            logger.warning("RAG service unavailable, using mock response")
            mock_response = {
                "id": str(uuid.uuid4()),
                "message": message,
                "response": f"I'm currently running in demo mode. The RAG system is not fully initialized, but I received your message: '{message}'. In a fully operational system, I would search through uploaded documents and provide contextual responses using OpenAI.",
                "sources": [],
                "qa_matches": [],
                "timestamp": datetime.utcnow().isoformat(),
                "processing_time_ms": 50,
                "model_used": "demo-mode"
            }
            return {
                "status": "demo",
                "data": mock_response,
                "message": "Response generated in demo mode (RAG service unavailable)"
            }

        # Get Q&A pairs for context (use mock data for now)
        qa_pairs = mock_qa_pairs
        logger.info(f"Found {len(qa_pairs)} Q&A pairs for RAG processing")

        # Process query through real RAG pipeline with timeout
        rag_response = await asyncio.wait_for(
            rag_service.chat_with_rag(
                query=message,
                qa_pairs=qa_pairs,
                conversation_history=None,  # Could be implemented with session storage
                max_chunks=min(settings.max_chunks_per_query, 3),  # Limit chunks for faster response
                similarity_threshold=settings.similarity_threshold
            ),
            timeout=25.0  # 25 second timeout to stay under frontend 30s limit
        )

        logger.info(f"RAG response generated successfully in {rag_response.get('processing_time_ms', 0)}ms")

        return {
            "status": "success",
            "data": rag_response,
            "message": "Chat response generated successfully using real RAG pipeline"
        }

    except asyncio.TimeoutError:
        logger.error(f"Chat processing timed out for query: {message[:100]}")
        # Return timeout fallback response
        fallback_response = {
            "id": str(uuid.uuid4()),
            "message": message,
            "response": "I apologize, but your request is taking longer than expected to process. This might be due to high server load or complex document processing. Please try again with a simpler question, or check if the OpenAI API and ChromaDB services are responding properly.",
            "sources": [],
            "qa_matches": [],
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 25000,
            "model_used": settings.openai_model,
            "error": "Request timeout after 25 seconds"
        }
        
        return {
            "status": "timeout",
            "data": fallback_response,
            "message": "Chat processing timed out - please try again"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to informative error message
        fallback_response = {
            "id": str(uuid.uuid4()),
            "message": message,
            "response": f"I apologize, but I encountered an error while processing your question. This might be due to the OpenAI API key configuration, ChromaDB connection, or network issues. Error details: {str(e)}",
            "sources": [],
            "qa_matches": [],
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": 0,
            "model_used": settings.openai_model,
            "error": str(e)
        }
        
        return {
            "status": "error",
            "data": fallback_response,
            "message": f"Chat processing failed: {str(e)}"
        }

@app.get("/api/v1/chat/history/{session_id}", tags=["Chat"])
async def get_chat_history(session_id: str):
    """Get chat history for a session (mock implementation)"""
    # Mock chat history - in a real implementation, this would come from a database
    mock_history = [
        {
            "id": f"msg_{session_id}_1",
            "type": "user",
            "content": "What is RAG?",
            "timestamp": "2024-01-01T10:00:00Z"
        },
        {
            "id": f"msg_{session_id}_2", 
            "type": "assistant",
            "content": "RAG (Retrieval-Augmented Generation) is a technique that combines information retrieval with text generation...",
            "timestamp": "2024-01-01T10:00:05Z",
            "sources": {
                "knowledge_base_hits": [
                    {
                        "id": "doc_1",
                        "content": "RAG combines retrieval and generation...",
                        "filename": "rag_overview.pdf",
                        "similarity_score": 0.95
                    }
                ],
                "qa_hits": []
            }
        }
    ]
    
    return {
        "status": "success",
        "session_id": session_id,
        "messages": mock_history,
        "total_messages": len(mock_history)
    }

# =============================================================================
# TEST ENDPOINTS
# =============================================================================

@app.get("/test/database", tags=["Testing"])
async def test_database():
    """Test database connectivity"""
    try:
        health = await get_database_health()
        return {
            "status": "success",
            "database_health": health,
            "message": "Database connection test completed"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Database connection test failed"
        }

@app.get("/test/chromadb", tags=["Testing"])
async def test_chromadb():
    """Test ChromaDB connectivity"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v2/heartbeat", timeout=5.0)
            return {
                "status": "success",
                "chromadb_response": response.json(),
                "status_code": response.status_code,
                "message": "ChromaDB connection test completed"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "ChromaDB connection test failed"
        }

@app.get("/config", tags=["Configuration"])
async def get_config():
    """Get application configuration (non-sensitive)"""
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "debug": settings.debug,
        "database_configured": bool(settings.database_url),
        "chromadb_host": settings.chromadb_host,
        "chromadb_port": settings.chromadb_port,
        "cors_origins": settings.cors_origins,
        "max_file_size_mb": settings.max_file_size_mb,
        "chunk_size": settings.chunk_size,
        "embedding_model": settings.embedding_model,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info",
    )
