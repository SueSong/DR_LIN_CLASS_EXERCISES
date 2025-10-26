"""
Main RAG Service
Orchestrates document processing, retrieval, and response generation
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .document_processor import document_processor
from .retrieval_service import retrieval_service
from .llm_service import llm_service
from .qa_service import qa_service
from app.config import settings

logger = logging.getLogger(__name__)

class RAGService:
    """Main RAG service that orchestrates the entire pipeline"""
    
    def __init__(self):
        self.document_processor = document_processor
        self.retrieval_service = retrieval_service
        self.llm_service = llm_service
    
    async def process_uploaded_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Process an uploaded document through the RAG pipeline
        
        Args:
            file_path: Path to the uploaded file
            filename: Original filename
            
        Returns:
            Processing results with document metadata
        """
        document_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting RAG processing for document: {filename}")
            
            # Process document (extract text, chunk, embed, store)
            result = await self.document_processor.process_document(
                file_path=file_path,
                filename=filename,
                document_id=document_id
            )
            
            if result.get("processing_status") == "completed":
                logger.info(f"Successfully processed document {filename} with {result.get('chunks_count')} chunks")
            else:
                logger.error(f"Failed to process document {filename}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG document processing: {e}")
            return {
                "document_id": document_id,
                "filename": filename,
                "processing_status": "failed",
                "error": str(e)
            }
    
    async def chat_with_rag(
        self,
        query: str,
        qa_pairs: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_chunks: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process a chat query using the full RAG pipeline
        
        Args:
            query: User's question
            qa_pairs: Available Q&A pairs to search through
            conversation_history: Previous conversation messages
            max_chunks: Maximum number of document chunks to retrieve
            similarity_threshold: Minimum similarity score for retrieval
            
        Returns:
            Complete RAG response with sources and metadata
        """
        try:
            start_time = datetime.now()
            
            logger.info(f"Processing RAG query: '{query[:100]}...'")
            
            # Step 1: Retrieve relevant document chunks
            document_chunks = await self.retrieval_service.search_documents(
                query=query,
                max_results=max_chunks or settings.max_chunks_per_query,
                similarity_threshold=similarity_threshold or settings.similarity_threshold
            )
            
            # Step 2: Search through Q&A pairs if provided
            qa_matches = []
            if qa_pairs:
                qa_matches = await self._search_qa_pairs(query, qa_pairs)
            
            # Step 3: Generate response using LLM with retrieved context
            llm_result = await self.llm_service.generate_response(
                query=query,
                document_chunks=document_chunks,
                qa_matches=qa_matches,
                conversation_history=conversation_history
            )
            
            end_time = datetime.now()
            total_processing_time = (end_time - start_time).total_seconds() * 1000
            
            # Compile complete response
            response = {
                "id": str(uuid.uuid4()),
                "message": query,
                "response": llm_result.get("response", ""),
                "sources": self._format_document_sources(document_chunks),
                "qa_matches": self._format_qa_matches(qa_matches),
                "timestamp": end_time.isoformat(),
                "processing_time_ms": round(total_processing_time, 2),
                "model_used": llm_result.get("model_used", settings.openai_model),
                "retrieval_stats": {
                    "document_chunks_found": len(document_chunks),
                    "qa_matches_found": len(qa_matches),
                    "similarity_threshold": similarity_threshold or settings.similarity_threshold,
                    "max_chunks_requested": max_chunks or settings.max_chunks_per_query
                },
                "llm_processing_time_ms": llm_result.get("processing_time_ms", 0)
            }
            
            logger.info(f"RAG query completed in {total_processing_time:.2f}ms with {len(document_chunks)} document sources and {len(qa_matches)} Q&A matches")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG chat processing: {e}")
            return {
                "id": str(uuid.uuid4()),
                "message": query,
                "response": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "qa_matches": [],
                "timestamp": datetime.now().isoformat(),
                "processing_time_ms": 0,
                "model_used": settings.openai_model,
                "error": str(e)
            }
    
    async def _search_qa_pairs(self, query: str, qa_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search through Q&A pairs using ChromaDB vector similarity"""
        try:
            # Use ChromaDB Q&A service for semantic search
            matches = await qa_service.search_qa_pairs(
                query=query,
                max_results=3,
                similarity_threshold=0.7  # Use higher threshold for embeddings
            )
            
            logger.info(f"Found {len(matches)} Q&A matches using ChromaDB for query: '{query[:50]}...'")
            
            return matches
            
        except Exception as e:
            logger.error(f"Error searching Q&A pairs with ChromaDB: {e}")
            # Fallback to empty list if embedding search fails
            return []
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity calculation based on common words"""
        import re
        
        # Clean and normalize text - remove punctuation and convert to lowercase
        def clean_text(text):
            # Remove punctuation and extra spaces, convert to lowercase
            cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
            return set(cleaned.split())
        
        words1 = clean_text(text1)
        words2 = clean_text(text2)
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _format_document_sources(self, document_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format document chunks for API response"""
        sources = []
        
        for chunk in document_chunks:
            source = {
                "document_id": chunk.get("document_id"),
                "filename": chunk.get("filename"),
                "chunk_text": chunk.get("content", "")[:500],  # Limit to 500 chars for response
                "similarity_score": chunk.get("similarity_score"),
                "chunk_index": chunk.get("chunk_index")
            }
            sources.append(source)
        
        return sources
    
    def _format_qa_matches(self, qa_matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format Q&A matches for API response"""
        formatted_matches = []
        
        for qa in qa_matches:
            match = {
                "question": qa.get("question"),
                "answer": qa.get("answer"),
                "similarity_score": qa.get("similarity_score"),
                "match_type": qa.get("match_type")
            }
            formatted_matches.append(match)
        
        return formatted_matches
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks from the RAG system"""
        try:
            return await self.document_processor.delete_document(document_id)
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the RAG system"""
        try:
            # Check document processor status
            doc_stats = await self.document_processor.get_collection_stats()
            
            # Check retrieval service status
            retrieval_info = await self.retrieval_service.get_collection_info()
            
            # Check LLM service status
            llm_status = await self.llm_service.check_api_connection()
            
            return {
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "document_processor": {
                        "status": "operational",
                        "total_chunks": doc_stats.get("total_chunks", 0)
                    },
                    "retrieval_service": {
                        "status": retrieval_info.get("status", "unknown"),
                        "collection_info": retrieval_info
                    },
                    "llm_service": {
                        "status": llm_status.get("status", "unknown"),
                        "model": llm_status.get("model"),
                        "connection_test": llm_status.get("response", "")[:100] if llm_status.get("response") else None
                    }
                },
                "configuration": {
                    "embedding_model": settings.rag_embedding_model,
                    "llm_model": settings.openai_model,
                    "chunk_size": settings.chunk_size,
                    "max_chunks_per_query": settings.max_chunks_per_query,
                    "similarity_threshold": settings.similarity_threshold
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global instance
rag_service = RAGService()
