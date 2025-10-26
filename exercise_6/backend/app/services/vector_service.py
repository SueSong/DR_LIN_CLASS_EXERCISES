"""
Exercise 6: RAG Chatbot - PostgreSQL Vector Service
Handles document and Q&A embeddings using PostgreSQL + pgvector
"""

import logging
import hashlib
import uuid
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio

import asyncpg
import openai
import numpy as np

from app.config import settings
from app.database import get_connection

logger = logging.getLogger(__name__)

class PostgreSQLVectorService:
    """Service for managing embeddings in PostgreSQL with pgvector"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the vector service"""
        if self._initialized:
            return
        
        try:
            # Test database connection
            conn = await get_connection()
            try:
                # Verify pgvector extension is available
                result = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                )
                if not result:
                    raise Exception("pgvector extension is not installed")
                
                logger.info("PostgreSQL vector service initialized successfully")
                self._initialized = True
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL vector service: {e}")
            raise
    
    # =============================================================================
    # DOCUMENT EMBEDDING METHODS
    # =============================================================================
    
    async def add_document_chunks(
        self, 
        document_id: str, 
        chunks: List[Dict[str, Any]]
    ) -> List[str]:
        """Add document chunks with embeddings to PostgreSQL"""
        await self.initialize()
        
        try:
            chunk_ids = []
            
            conn = await get_connection()
            try:
                for i, chunk in enumerate(chunks):
                    content = chunk.get('content', '').strip()
                    if not content:
                        continue
                    
                    # Generate content hash for deduplication
                    content_hash = hashlib.sha256(content.encode()).hexdigest()
                    
                    # Generate embedding
                    embedding = await self._generate_embedding(content)
                    
                    # Insert chunk with embedding (convert to pgvector format)
                    embedding_str = '[' + ','.join(map(str, embedding)) + ']'
                    metadata_json = json.dumps(chunk.get('metadata', {}))
                    chunk_id = await conn.fetchval("""
                        INSERT INTO document_chunks (
                            document_id, chunk_index, content, content_hash,
                            token_count, char_count, embedding, metadata
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7::vector, $8::jsonb)
                        ON CONFLICT (document_id, chunk_index) 
                        DO UPDATE SET 
                            content = EXCLUDED.content,
                            content_hash = EXCLUDED.content_hash,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata
                        RETURNING id
                    """, 
                        document_id, i, content, content_hash,
                        chunk.get('token_count'), len(content), 
                        embedding_str, metadata_json
                    )
                    
                    chunk_ids.append(str(chunk_id))
                
                logger.info(f"Added {len(chunk_ids)} document chunks with embeddings for document {document_id}")
                return chunk_ids
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Failed to add document chunks: {e}")
            raise
    
    async def search_document_chunks(
        self, 
        query: str, 
        knowledge_base_id: Optional[str] = None,
        max_results: int = 5, 
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search document chunks using vector similarity"""
        await self.initialize()
        
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Build SQL query (convert query embedding to pgvector format)
            query_embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            sql = """
                SELECT 
                    dc.id,
                    dc.document_id,
                    dc.content,
                    dc.chunk_index,
                    dc.metadata,
                    (dc.metadata->>'filename') as filename,
                    (dc.metadata->>'title') as title,
                    1 - (dc.embedding <=> $1::vector) as similarity_score
                FROM document_chunks dc
                WHERE 1 - (dc.embedding <=> $1::vector) >= $2
            """
            
            params = [query_embedding_str, similarity_threshold]
            
            if knowledge_base_id:
                sql += " AND (dc.metadata->>'knowledge_base_id') = $3"
                params.append(knowledge_base_id)
            
            sql += " ORDER BY dc.embedding <=> $1::vector LIMIT $" + str(len(params) + 1)
            params.append(max_results)
            
            conn = await get_connection()
            try:
                rows = await conn.fetch(sql, *params)
                
                results = []
                for row in rows:
                    results.append({
                        "id": str(row["id"]),
                        "document_id": str(row["document_id"]),
                        "content": row["content"],
                        "chunk_index": row["chunk_index"],
                        "filename": row["filename"],
                        "title": row["title"],
                        "similarity_score": float(row["similarity_score"]),
                        "metadata": row["metadata"] or {}
                    })
                
                logger.info(f"Found {len(results)} document chunks for query: '{query[:50]}...'")
                return results
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Failed to search document chunks: {e}")
            return []
    
    # =============================================================================
    # Q&A EMBEDDING METHODS
    # =============================================================================
    
    async def add_qa_pair(
        self, 
        question: str, 
        answer: str, 
        knowledge_base_id: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add Q&A pair with embeddings to PostgreSQL"""
        await self.initialize()
        
        try:
            # Generate embeddings for both question and answer
            question_embedding = await self._generate_embedding(question)
            answer_embedding = await self._generate_embedding(answer)
            
            conn = await get_connection()
            try:
                # Get or create knowledge base
                kb_id = await self._ensure_knowledge_base(conn, knowledge_base_id)
                
                # Insert Q&A pair with embeddings
                qa_id = await conn.fetchval("""
                    INSERT INTO qa_pairs (
                        knowledge_base_id, question, answer, 
                        question_embedding, answer_embedding,
                        tags, metadata, status
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'active')
                    RETURNING id
                """, 
                    kb_id, question, answer,
                    question_embedding, answer_embedding,
                    metadata.get('tags', []) if metadata else [],
                    metadata or {}
                )
                
                logger.info(f"Added Q&A pair with embeddings: {qa_id}")
                return str(qa_id)
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Failed to add Q&A pair: {e}")
            raise
    
    async def search_qa_pairs(
        self, 
        query: str, 
        knowledge_base_id: Optional[str] = None,
        max_results: int = 5, 
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search Q&A pairs using vector similarity"""
        await self.initialize()
        
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Search both question and answer embeddings
            sql = """
                WITH question_matches AS (
                    SELECT 
                        id, question, answer, tags, metadata, created_at,
                        1 - (question_embedding <=> $1) as similarity_score,
                        'question' as match_type
                    FROM qa_pairs
                    WHERE status = 'active' 
                    AND 1 - (question_embedding <=> $1) >= $2
                ),
                answer_matches AS (
                    SELECT 
                        id, question, answer, tags, metadata, created_at,
                        1 - (answer_embedding <=> $1) as similarity_score,
                        'answer' as match_type
                    FROM qa_pairs
                    WHERE status = 'active' 
                    AND 1 - (answer_embedding <=> $1) >= $2
                ),
                all_matches AS (
                    SELECT * FROM question_matches
                    UNION ALL
                    SELECT * FROM answer_matches
                )
                SELECT DISTINCT ON (id)
                    id, question, answer, tags, metadata, created_at,
                    similarity_score, match_type
                FROM all_matches
            """
            
            params = [query_embedding, similarity_threshold]
            
            if knowledge_base_id:
                # Add knowledge base filter (need to join with knowledge_bases table)
                sql = sql.replace(
                    "FROM qa_pairs",
                    "FROM qa_pairs qa JOIN knowledge_bases kb ON qa.knowledge_base_id = kb.id"
                ).replace(
                    "WHERE status = 'active'",
                    "WHERE qa.status = 'active' AND kb.name = $3"
                )
                params.append(knowledge_base_id)
            
            sql += " ORDER BY id, similarity_score DESC LIMIT $" + str(len(params) + 1)
            params.append(max_results)
            
            conn = await get_connection()
            try:
                rows = await conn.fetch(sql, *params)
                
                results = []
                for row in rows:
                    results.append({
                        "id": str(row["id"]),
                        "question": row["question"],
                        "answer": row["answer"],
                        "similarity_score": float(row["similarity_score"]),
                        "match_type": row["match_type"],
                        "tags": row["tags"] or [],
                        "metadata": row["metadata"] or {},
                        "created_at": row["created_at"].isoformat() if row["created_at"] else None
                    })
                
                logger.info(f"Found {len(results)} Q&A matches for query: '{query[:50]}...'")
                return results
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Failed to search Q&A pairs: {e}")
            return []
    
    async def get_all_qa_pairs(self, knowledge_base_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all Q&A pairs from PostgreSQL"""
        await self.initialize()
        
        try:
            sql = """
                SELECT qa.id, qa.question, qa.answer, qa.tags, qa.metadata, 
                       qa.created_at, qa.updated_at, kb.name as knowledge_base_name
                FROM qa_pairs qa
                JOIN knowledge_bases kb ON qa.knowledge_base_id = kb.id
                WHERE qa.status = 'active'
            """
            
            params = []
            if knowledge_base_id:
                sql += " AND kb.name = $1"
                params.append(knowledge_base_id)
            
            sql += " ORDER BY qa.created_at DESC"
            
            conn = await get_connection()
            try:
                rows = await conn.fetch(sql, *params)
                
                results = []
                for row in rows:
                    results.append({
                        "id": str(row["id"]),
                        "question": row["question"],
                        "answer": row["answer"],
                        "knowledge_base_id": row["knowledge_base_name"],
                        "tags": row["tags"] or [],
                        "metadata": row["metadata"] or {},
                        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
                    })
                
                return results
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Failed to get Q&A pairs: {e}")
            return []
    
    async def delete_qa_pair(self, qa_id: str) -> bool:
        """Delete Q&A pair from PostgreSQL"""
        await self.initialize()
        
        try:
            conn = await get_connection()
            try:
                result = await conn.execute(
                    "UPDATE qa_pairs SET status = 'archived' WHERE id = $1",
                    qa_id
                )
                
                success = result == "UPDATE 1"
                if success:
                    logger.info(f"Archived Q&A pair: {qa_id}")
                
                return success
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Failed to delete Q&A pair {qa_id}: {e}")
            return False
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.openai_client.embeddings.create(
                    model=settings.rag_embedding_model,
                    input=text.strip()
                )
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def _ensure_knowledge_base(self, conn: asyncpg.Connection, name: str) -> str:
        """Ensure knowledge base exists and return its ID"""
        try:
            # Try to get existing knowledge base
            kb_id = await conn.fetchval(
                "SELECT id FROM knowledge_bases WHERE name = $1",
                name
            )
            
            if kb_id:
                return str(kb_id)
            
            # Create new knowledge base
            kb_id = await conn.fetchval("""
                INSERT INTO knowledge_bases (name, description, metadata)
                VALUES ($1, $2, $3)
                RETURNING id
            """, 
                name, 
                f"Auto-created knowledge base: {name}",
                {"created_by": "system", "auto_created": True}
            )
            
            logger.info(f"Created new knowledge base: {name} ({kb_id})")
            return str(kb_id)
            
        except Exception as e:
            logger.error(f"Failed to ensure knowledge base {name}: {e}")
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get vector system status"""
        try:
            await self.initialize()
            
            conn = await get_connection()
            try:
                # Get document chunks count
                doc_chunks_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL"
                )
                
                # Get Q&A pairs count
                qa_pairs_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM qa_pairs WHERE status = 'active'"
                )
                
                # Get knowledge bases count
                kb_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM knowledge_bases WHERE is_active = true"
                )
                
                return {
                    "status": "healthy",
                    "database": "postgresql_pgvector",
                    "embedding_model": settings.rag_embedding_model,
                    "embedding_dimension": 1536,
                    "document_chunks": doc_chunks_count,
                    "qa_pairs": qa_pairs_count,
                    "knowledge_bases": kb_count
                }
            finally:
                await conn.close()
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "document_chunks": 0,
                "qa_pairs": 0,
                "knowledge_bases": 0
            }

# Global instance
vector_service = PostgreSQLVectorService()
