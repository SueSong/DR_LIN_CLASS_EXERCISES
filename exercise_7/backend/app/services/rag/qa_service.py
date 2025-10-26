"""
Exercise 6: RAG Chatbot - Q&A Embedding Service
Handles Q&A pairs with embeddings stored in ChromaDB for semantic search
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

import chromadb
from chromadb.config import Settings
import openai

from app.config import settings

logger = logging.getLogger(__name__)

class QAEmbeddingService:
    """Service for managing Q&A pairs with embeddings in ChromaDB"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        self.chroma_client = None
        self.qa_collection = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize ChromaDB connection and Q&A collection"""
        if self._initialized:
            return
        
        try:
            # Connect to ChromaDB
            self.chroma_client = chromadb.HttpClient(
                host="localhost",
                port=8000,
                settings=Settings(allow_reset=True)
            )
            
            # Get or create Q&A collection
            try:
                self.qa_collection = self.chroma_client.get_collection(
                    name="qa_pairs",
                    embedding_function=None  # We'll handle embeddings manually
                )
                logger.info("Connected to existing ChromaDB Q&A collection: qa_pairs")
            except Exception:
                # Create new collection if it doesn't exist
                self.qa_collection = self.chroma_client.create_collection(
                    name="qa_pairs",
                    embedding_function=None,
                    metadata={"description": "Q&A pairs with embeddings for semantic search"}
                )
                logger.info("Created new ChromaDB Q&A collection: qa_pairs")
            
            self._initialized = True
            logger.info("Q&A embedding service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Q&A embedding service: {e}")
            raise
    
    async def add_qa_pair(self, question: str, answer: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a Q&A pair with embeddings to ChromaDB"""
        await self.initialize()
        
        try:
            # Generate unique ID
            qa_id = str(uuid.uuid4())
            
            logger.info(f"Generating embeddings for Q&A pair: {qa_id}")
            
            # Generate embeddings for both question and answer with timeout
            question_embedding = await asyncio.wait_for(
                self._generate_embedding(question), 
                timeout=15.0
            )
            answer_embedding = await asyncio.wait_for(
                self._generate_embedding(answer), 
                timeout=15.0
            )
            
            logger.info(f"Embeddings generated successfully for Q&A pair: {qa_id}")
            
            # Prepare metadata (ChromaDB only accepts str, int, float, bool, or None)
            clean_metadata = {}
            if metadata:
                for key, value in metadata.items():
                    if key == "tags" and isinstance(value, list):
                        # Convert tags list to comma-separated string
                        clean_metadata[key] = ",".join(value) if value else ""
                    elif isinstance(value, (str, int, float, bool)) or value is None:
                        clean_metadata[key] = value
                    else:
                        # Convert other types to string
                        clean_metadata[key] = str(value)
            
            qa_metadata = {
                "question": question,
                "answer": answer,
                "created_at": datetime.utcnow().isoformat(),
                "type": "qa_pair",
                **clean_metadata
            }
            
            # Store question embedding
            question_id = f"{qa_id}_question"
            self.qa_collection.add(
                ids=[question_id],
                embeddings=[question_embedding],
                documents=[question],
                metadatas=[{**qa_metadata, "content_type": "question", "qa_id": qa_id}]
            )
            
            # Store answer embedding
            answer_id = f"{qa_id}_answer"
            self.qa_collection.add(
                ids=[answer_id],
                embeddings=[answer_embedding],
                documents=[answer],
                metadatas=[{**qa_metadata, "content_type": "answer", "qa_id": qa_id}]
            )
            
            logger.info(f"Added Q&A pair to ChromaDB: {qa_id}")
            return qa_id
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout generating embeddings for Q&A pair")
            raise Exception("Embedding generation timed out")
        except Exception as e:
            logger.error(f"Failed to add Q&A pair: {e}")
            raise
    
    async def search_qa_pairs(self, query: str, max_results: int = 5, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search Q&A pairs using semantic similarity"""
        await self.initialize()
        
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Search in ChromaDB
            results = self.qa_collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results * 2,  # Get more results to filter and deduplicate
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results and group by Q&A pair
            qa_matches = {}
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0], 
                results["distances"][0]
            )):
                similarity_score = 1 - distance  # Convert distance to similarity
                
                if similarity_score < similarity_threshold:
                    continue
                
                qa_id = metadata.get("qa_id")
                if not qa_id:
                    continue
                
                # Group by Q&A ID and keep the best match
                if qa_id not in qa_matches or similarity_score > qa_matches[qa_id]["similarity_score"]:
                    # Convert tags back to list if it exists
                    tags = metadata.get("tags", "")
                    if isinstance(tags, str) and tags:
                        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                    else:
                        tags_list = []
                    
                    qa_matches[qa_id] = {
                        "id": qa_id,
                        "question": metadata.get("question"),
                        "answer": metadata.get("answer"),
                        "similarity_score": similarity_score,
                        "match_type": metadata.get("content_type", "unknown"),
                        "matched_content": doc,
                        "tags": tags_list,
                        "created_at": metadata.get("created_at"),
                        "metadata": {k: v for k, v in metadata.items() 
                                   if k not in ["question", "answer", "qa_id", "content_type", "created_at", "tags"]}
                    }
            
            # Sort by similarity score and return top results
            sorted_matches = sorted(qa_matches.values(), key=lambda x: x["similarity_score"], reverse=True)
            
            logger.info(f"Found {len(sorted_matches)} Q&A matches for query: '{query[:50]}...'")
            return sorted_matches[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to search Q&A pairs: {e}")
            return []
    
    async def get_all_qa_pairs(self) -> List[Dict[str, Any]]:
        """Get all Q&A pairs from ChromaDB"""
        await self.initialize()
        
        try:
            # Get all documents from the collection
            results = self.qa_collection.get(
                include=["documents", "metadatas"]
            )
            
            # Group by Q&A ID to avoid duplicates
            qa_pairs = {}
            
            for doc, metadata in zip(results["documents"], results["metadatas"]):
                qa_id = metadata.get("qa_id")
                if not qa_id:
                    continue
                
                if qa_id not in qa_pairs:
                    # Convert tags back to list if it exists
                    tags = metadata.get("tags", "")
                    if isinstance(tags, str) and tags:
                        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                    else:
                        tags_list = []
                    
                    qa_pairs[qa_id] = {
                        "id": qa_id,
                        "question": metadata.get("question"),
                        "answer": metadata.get("answer"),
                        "tags": tags_list,
                        "created_at": metadata.get("created_at"),
                        "metadata": {k: v for k, v in metadata.items() 
                                   if k not in ["question", "answer", "qa_id", "content_type", "created_at", "tags"]}
                    }
            
            return list(qa_pairs.values())
            
        except Exception as e:
            logger.error(f"Failed to get Q&A pairs: {e}")
            return []
    
    async def delete_qa_pair(self, qa_id: str) -> bool:
        """Delete a Q&A pair from ChromaDB"""
        await self.initialize()
        
        try:
            # Delete both question and answer embeddings
            question_id = f"{qa_id}_question"
            answer_id = f"{qa_id}_answer"
            
            self.qa_collection.delete(ids=[question_id, answer_id])
            
            logger.info(f"Deleted Q&A pair from ChromaDB: {qa_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Q&A pair {qa_id}: {e}")
            return False
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            # Run in executor to avoid blocking the event loop with timeout
            loop = asyncio.get_event_loop()
            
            def create_embedding():
                return self.openai_client.embeddings.create(
                    model=settings.rag_embedding_model,
                    input=text.strip(),
                    timeout=10.0  # 10 second timeout for OpenAI API
                )
            
            response = await loop.run_in_executor(None, create_embedding)
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get Q&A system status"""
        try:
            await self.initialize()
            
            # Get collection stats
            collection_count = self.qa_collection.count()
            qa_count = collection_count // 2  # Each Q&A pair has 2 embeddings
            
            return {
                "status": "healthy",
                "qa_pairs_count": qa_count,
                "total_embeddings": collection_count,
                "collection_name": "qa_pairs",
                "embedding_model": settings.rag_embedding_model
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "qa_pairs_count": 0,
                "total_embeddings": 0
            }

# Global instance
qa_service = QAEmbeddingService()
