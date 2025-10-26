"""
LLM Service for RAG System
Handles OpenAI integration for response generation using retrieved context
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

import openai

from app.config import settings

logger = logging.getLogger(__name__)

# Global LLM service instance
llm_service_instance = None

async def init_llm_service() -> bool:
    """Initialize the LLM service"""
    global llm_service_instance
    
    try:
        llm_service_instance = LLMService()
        
        # Test the connection
        test_result = await llm_service_instance.check_api_connection()
        
        if test_result:
            logger.info("✅ LLM service initialized successfully")
            return True
        else:
            logger.error("❌ LLM service initialization failed: API connection test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ LLM service initialization failed: {e}")
        return False

def get_llm_service() -> Optional['LLMService']:
    """Get the global LLM service instance"""
    return llm_service_instance

class LLMService:
    """Handles LLM integration for response generation"""
    
    def __init__(self):
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        
        self.system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from documents and Q&A pairs.

Instructions:
1. Use the provided context to answer the user's question accurately and comprehensively
2. If the context contains relevant information, base your answer primarily on that information
3. If the context doesn't contain enough information to fully answer the question, say so clearly
4. Always be honest about the limitations of the provided context
5. Provide specific references to the source documents when possible
6. Keep your answers clear, concise, and well-structured
7. If multiple sources provide different information, acknowledge the differences

Context will be provided in the following format:
- Document chunks: Relevant excerpts from uploaded documents
- Q&A pairs: Previously answered questions that might be relevant

Always maintain a helpful and professional tone."""
    
    async def generate_response(
        self,
        query: str,
        document_chunks: List[Dict[str, Any]],
        qa_matches: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using OpenAI based on query and retrieved context
        
        Args:
            query: User's question
            document_chunks: Relevant document chunks from vector search
            qa_matches: Matching Q&A pairs
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            start_time = datetime.now()
            
            # Build context from retrieved information
            context = self._build_context(document_chunks, qa_matches)
            
            # Create messages for the conversation
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages for context
                    if msg.get('role') in ['user', 'assistant']:
                        messages.append({
                            "role": msg['role'],
                            "content": msg['content']
                        })
            
            # Add current query with context
            user_message = self._format_user_message(query, context)
            messages.append({"role": "user", "content": user_message})
            
            logger.info(f"Generating response for query: '{query[:100]}...'")
            logger.info(f"Context includes {len(document_chunks)} document chunks and {len(qa_matches)} Q&A matches")
            
            # Generate response with timeout
            def generate_sync():
                return self.openai_client.chat.completions.create(
                    model=settings.openai_model,
                    messages=messages,
                    temperature=settings.openai_temperature,
                    max_tokens=min(settings.openai_max_tokens, 500),  # Limit tokens for faster response
                    timeout=20.0  # 20 second timeout for OpenAI API
                )
            
            response = await asyncio.get_event_loop().run_in_executor(None, generate_sync)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
            
            # Extract response content
            response_text = response.choices[0].message.content
            
            result = {
                "response": response_text,
                "query": query,
                "sources_used": {
                    "document_chunks": len(document_chunks),
                    "qa_matches": len(qa_matches)
                },
                "processing_time_ms": round(processing_time, 2),
                "model_used": settings.openai_model,
                "timestamp": end_time.isoformat(),
                "context_length": len(context)
            }
            
            logger.info(f"Generated response in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return {
                "response": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "query": query,
                "error": str(e),
                "sources_used": {"document_chunks": 0, "qa_matches": 0},
                "processing_time_ms": 0,
                "model_used": settings.openai_model,
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_context(self, document_chunks: List[Dict[str, Any]], qa_matches: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved information"""
        context_parts = []
        
        # Add document chunks
        if document_chunks:
            context_parts.append("=== RELEVANT DOCUMENT EXCERPTS ===")
            for i, chunk in enumerate(document_chunks, 1):
                filename = chunk.get('filename', 'Unknown')
                similarity = chunk.get('similarity_score', 0)
                content = chunk.get('content', '')
                
                context_parts.append(f"\nDocument {i}: {filename} (Relevance: {similarity:.2f})")
                context_parts.append(f"Content: {content}")
        
        # Add Q&A matches
        if qa_matches:
            context_parts.append("\n\n=== RELATED Q&A PAIRS ===")
            for i, qa in enumerate(qa_matches, 1):
                question = qa.get('question', '')
                answer = qa.get('answer', '')
                similarity = qa.get('similarity_score', 0)
                
                context_parts.append(f"\nQ&A {i} (Relevance: {similarity:.2f}):")
                context_parts.append(f"Q: {question}")
                context_parts.append(f"A: {answer}")
        
        return "\n".join(context_parts)
    
    def _format_user_message(self, query: str, context: str) -> str:
        """Format the user message with context"""
        if not context.strip():
            return f"""I have a question but no relevant context was found in the knowledge base.

Question: {query}

Please let me know that you don't have specific information about this topic in the knowledge base, but you can provide general information if helpful."""
        
        return f"""Please answer the following question based on the provided context.

CONTEXT:
{context}

QUESTION: {query}

Please provide a comprehensive answer based on the context above. If the context doesn't fully address the question, please indicate what information is missing."""
    
    async def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate a summary of the given text"""
        try:
            messages = [
                {"role": "system", "content": f"Summarize the following text in no more than {max_length} characters. Be concise but capture the key points."},
                {"role": "user", "content": text}
            ]
            
            def generate_sync():
                return self.openai_client.chat.completions.create(
                    model=settings.openai_model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=100
                )
            
            response = await asyncio.get_event_loop().run_in_executor(None, generate_sync)
            summary = response.choices[0].message.content
            
            # Truncate if still too long
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return text[:max_length-3] + "..." if len(text) > max_length else text
    
    async def check_api_connection(self) -> Dict[str, Any]:
        """Check if OpenAI API is accessible"""
        try:
            test_messages = [
                {"role": "system", "content": "You are a test assistant."},
                {"role": "user", "content": "Say 'API connection successful' if you can read this."}
            ]
            
            def test_sync():
                return self.openai_client.chat.completions.create(
                    model=settings.openai_model,
                    messages=test_messages,
                    temperature=0,
                    max_tokens=50
                )
            
            response = await asyncio.get_event_loop().run_in_executor(None, test_sync)
            
            return {
                "status": "connected",
                "model": settings.openai_model,
                "response": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"OpenAI API connection test failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "model": settings.openai_model
            }

# Global instance
llm_service = LLMService()
