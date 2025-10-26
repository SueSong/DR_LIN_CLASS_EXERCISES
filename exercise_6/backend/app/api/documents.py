"""
Exercise 6: Documents API Routes
Handles individual document operations and metadata
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

# Mock data storage (will be replaced with database in production)
mock_documents = []

@router.get("/")
async def list_documents(
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """List all documents with optional filtering"""
    filtered_docs = mock_documents
    
    if status:
        filtered_docs = [doc for doc in filtered_docs if doc.get("status") == status]
    
    # Apply pagination
    paginated_docs = filtered_docs[offset:offset + limit]
    
    return {
        "status": "success",
        "data": paginated_docs,
        "total": len(filtered_docs),
        "limit": limit,
        "offset": offset
    }

@router.get("/{document_id}")
async def get_document(document_id: str) -> Dict[str, Any]:
    """Get a specific document by ID"""
    document = next((doc for doc in mock_documents if doc["id"] == document_id), None)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "status": "success",
        "data": document
    }

@router.put("/{document_id}")
async def update_document(document_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update document metadata"""
    document = next((doc for doc in mock_documents if doc["id"] == document_id), None)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update allowed fields
    allowed_fields = ["filename", "tags", "description"]
    for field in allowed_fields:
        if field in update_data:
            document[field] = update_data[field]
    
    document["updated_at"] = datetime.utcnow().isoformat()
    
    return {
        "status": "success",
        "message": "Document updated successfully",
        "data": document
    }

@router.get("/{document_id}/chunks")
async def get_document_chunks(document_id: str) -> Dict[str, Any]:
    """Get all chunks for a specific document"""
    document = next((doc for doc in mock_documents if doc["id"] == document_id), None)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Mock chunks data
    mock_chunks = [
        {
            "id": f"chunk_{i}",
            "document_id": document_id,
            "content": f"This is chunk {i} of document {document['filename']}",
            "chunk_index": i,
            "start_char": i * 500,
            "end_char": (i + 1) * 500,
            "embedding_vector": [0.1] * 1536  # Mock embedding
        }
        for i in range(document.get("chunks_count", 1))
    ]
    
    return {
        "status": "success",
        "data": mock_chunks,
        "total": len(mock_chunks)
    }
