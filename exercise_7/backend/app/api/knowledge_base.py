"""
Exercise 6: Knowledge Base API Routes
Handles document upload, processing, and management
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/knowledge-base", tags=["Knowledge Base"])

# Mock data storage
mock_documents = []

@router.get("/documents")
async def get_documents() -> List[Dict[str, Any]]:
    """Get all documents in the knowledge base"""
    return {
        "status": "success",
        "data": mock_documents,
        "total": len(mock_documents)
    }

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload a document to the knowledge base"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Create mock document entry
    document = {
        "id": str(uuid.uuid4()),
        "filename": file.filename,
        "size": file.size or 0,
        "content_type": file.content_type,
        "status": "processed",
        "chunks_count": 1,
        "uploaded_at": datetime.utcnow().isoformat(),
        "processed_at": datetime.utcnow().isoformat()
    }
    
    mock_documents.append(document)
    
    return {
        "status": "success",
        "message": f"Document {file.filename} uploaded successfully",
        "data": document
    }

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str) -> Dict[str, Any]:
    """Delete a document from the knowledge base"""
    global mock_documents
    
    # Find and remove document
    original_count = len(mock_documents)
    mock_documents = [doc for doc in mock_documents if doc["id"] != document_id]
    
    if len(mock_documents) == original_count:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "status": "success",
        "message": f"Document {document_id} deleted successfully"
    }

@router.get("/stats")
async def get_knowledge_base_stats() -> Dict[str, Any]:
    """Get knowledge base statistics"""
    return {
        "status": "success",
        "data": {
            "total_documents": len(mock_documents),
            "total_chunks": sum(doc.get("chunks_count", 0) for doc in mock_documents),
            "storage_used": sum(doc.get("size", 0) for doc in mock_documents),
            "last_updated": datetime.utcnow().isoformat() if mock_documents else None
        }
    }
