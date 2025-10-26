"""
Exercise 6: Q&A Pairs API Routes
Handles question-answer pair management
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/v1/qa-pairs", tags=["Q&A Pairs"])

# Mock data storage (will be replaced with database in production)
mock_qa_pairs = []

@router.get("/")
async def list_qa_pairs(
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    tag: Optional[str] = None
) -> Dict[str, Any]:
    """List all Q&A pairs with optional filtering"""
    filtered_pairs = mock_qa_pairs
    
    if tag:
        filtered_pairs = [
            pair for pair in filtered_pairs 
            if tag in pair.get("tags", [])
        ]
    
    # Apply pagination
    paginated_pairs = filtered_pairs[offset:offset + limit]
    
    return {
        "status": "success",
        "data": paginated_pairs,
        "total": len(filtered_pairs),
        "limit": limit,
        "offset": offset
    }

@router.post("/")
async def create_qa_pair(qa_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new Q&A pair"""
    if not qa_data.get("question") or not qa_data.get("answer"):
        raise HTTPException(status_code=400, detail="Question and answer are required")
    
    qa_pair = {
        "id": str(uuid.uuid4()),
        "question": qa_data["question"],
        "answer": qa_data["answer"],
        "tags": qa_data.get("tags", []),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "usage_count": 0,
        "last_used": None
    }
    
    mock_qa_pairs.append(qa_pair)
    
    return {
        "status": "success",
        "message": "Q&A pair created successfully",
        "data": qa_pair
    }

@router.get("/{qa_id}")
async def get_qa_pair(qa_id: str) -> Dict[str, Any]:
    """Get a specific Q&A pair by ID"""
    qa_pair = next((pair for pair in mock_qa_pairs if pair["id"] == qa_id), None)
    
    if not qa_pair:
        raise HTTPException(status_code=404, detail="Q&A pair not found")
    
    return {
        "status": "success",
        "data": qa_pair
    }

@router.put("/{qa_id}")
async def update_qa_pair(qa_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update a Q&A pair"""
    qa_pair = next((pair for pair in mock_qa_pairs if pair["id"] == qa_id), None)
    
    if not qa_pair:
        raise HTTPException(status_code=404, detail="Q&A pair not found")
    
    # Update allowed fields
    allowed_fields = ["question", "answer", "tags"]
    for field in allowed_fields:
        if field in update_data:
            qa_pair[field] = update_data[field]
    
    qa_pair["updated_at"] = datetime.utcnow().isoformat()
    
    return {
        "status": "success",
        "message": "Q&A pair updated successfully",
        "data": qa_pair
    }

@router.delete("/{qa_id}")
async def delete_qa_pair(qa_id: str) -> Dict[str, Any]:
    """Delete a Q&A pair"""
    global mock_qa_pairs
    
    original_count = len(mock_qa_pairs)
    mock_qa_pairs = [pair for pair in mock_qa_pairs if pair["id"] != qa_id]
    
    if len(mock_qa_pairs) == original_count:
        raise HTTPException(status_code=404, detail="Q&A pair not found")
    
    return {
        "status": "success",
        "message": f"Q&A pair {qa_id} deleted successfully"
    }

@router.post("/{qa_id}/usage")
async def record_qa_usage(qa_id: str) -> Dict[str, Any]:
    """Record usage of a Q&A pair"""
    qa_pair = next((pair for pair in mock_qa_pairs if pair["id"] == qa_id), None)
    
    if not qa_pair:
        raise HTTPException(status_code=404, detail="Q&A pair not found")
    
    qa_pair["usage_count"] = qa_pair.get("usage_count", 0) + 1
    qa_pair["last_used"] = datetime.utcnow().isoformat()
    
    return {
        "status": "success",
        "message": "Usage recorded successfully",
        "data": {
            "qa_id": qa_id,
            "usage_count": qa_pair["usage_count"],
            "last_used": qa_pair["last_used"]
        }
    }
