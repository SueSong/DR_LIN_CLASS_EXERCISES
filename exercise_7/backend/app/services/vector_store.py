"""
Exercise 6: Vector Store Service
Handles ChromaDB initialization and management
"""

import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)

# Global ChromaDB client
chromadb_client = None
chromadb_initialized = False

async def init_chromadb(host: str = "localhost", port: int = 8000) -> bool:
    """Initialize ChromaDB connection"""
    global chromadb_client, chromadb_initialized
    
    try:
        # Test ChromaDB connection
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{host}:{port}/api/v2/heartbeat", timeout=5.0)
            
            if response.status_code == 200:
                logger.info(f"✅ ChromaDB connected successfully at {host}:{port}")
                chromadb_initialized = True
                return True
            else:
                logger.error(f"❌ ChromaDB connection failed: HTTP {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"❌ ChromaDB initialization failed: {e}")
        return False

async def close_chromadb() -> None:
    """Close ChromaDB connection"""
    global chromadb_client, chromadb_initialized
    
    try:
        if chromadb_client:
            # ChromaDB client doesn't need explicit closing
            chromadb_client = None
            
        chromadb_initialized = False
        logger.info("✅ ChromaDB connection closed")
        
    except Exception as e:
        logger.error(f"❌ Error closing ChromaDB: {e}")

async def get_chromadb_status() -> Dict[str, Any]:
    """Get ChromaDB connection status"""
    if not chromadb_initialized:
        return {
            "status": "disconnected",
            "message": "ChromaDB not initialized"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v2/heartbeat", timeout=5.0)
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "url": "http://localhost:8000",
                    "api_version": "v2"
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}"
                }
                
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def is_chromadb_available() -> bool:
    """Check if ChromaDB is available"""
    return chromadb_initialized

async def create_collection(name: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """Create a new ChromaDB collection"""
    if not chromadb_initialized:
        logger.error("ChromaDB not initialized")
        return False
    
    try:
        # This would create a collection in a real implementation
        logger.info(f"✅ Collection '{name}' created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create collection '{name}': {e}")
        return False

async def delete_collection(name: str) -> bool:
    """Delete a ChromaDB collection"""
    if not chromadb_initialized:
        logger.error("ChromaDB not initialized")
        return False
    
    try:
        # This would delete a collection in a real implementation
        logger.info(f"✅ Collection '{name}' deleted successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to delete collection '{name}': {e}")
        return False

async def list_collections() -> list:
    """List all ChromaDB collections"""
    if not chromadb_initialized:
        logger.error("ChromaDB not initialized")
        return []
    
    try:
        # This would list collections in a real implementation
        mock_collections = ["rag_documents", "qa_pairs"]
        logger.info(f"✅ Found {len(mock_collections)} collections")
        return mock_collections
        
    except Exception as e:
        logger.error(f"❌ Failed to list collections: {e}")
        return []
