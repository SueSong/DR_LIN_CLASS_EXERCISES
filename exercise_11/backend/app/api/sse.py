"""
SSE (Server-Sent Events) Streaming API
Streams advice chunks in real-time for better UX.
"""

import asyncio
import json
import time
from typing import List
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..guards import check_message_safety, SafetyClassification
from ..guardrails import check_and_queue_crisis
from ..sessions import get_parent_name
from ..rag_retrieval import retrieve_knowledge
from ..observability import get_tracer
import sys
from pathlib import Path
billing_dir = Path(__file__).parent.parent.parent.parent / "billing"
sys.path.insert(0, str(billing_dir.parent))
from billing.ledger import get_ledger
from billing.lite_mode import generate_lite_mode_response, get_lite_mode_notice

router = APIRouter(prefix="/api/coach", tags=["SSE"])


class StreamAdviceRequest(BaseModel):
    """Request model for streaming advice"""
    message: str
    session_id: str


def chunk_text(text: str, chunk_size: int = 5) -> List[str]:
    """
    Split text into chunks (words) for streaming.
    
    Args:
        text: Text to chunk
        chunk_size: Number of words per chunk
    
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if i + chunk_size < len(words):
            chunk += " "  # Add space between chunks
        chunks.append(chunk)
    return chunks


async def stream_advice_generator(
    user_text: str,
    session_id: str,
    request: Request
):
    print(f"[SSE] Received message from session {session_id}: '{user_text[:100]}...'")
    """
    Generator function that streams advice chunks as SSE events.
    
    Args:
        user_text: User's message
        session_id: Session identifier
        request: FastAPI request object for disconnect detection
    """
    tracer = get_tracer()
    start_time = time.time()
    
    try:
        with tracer.start_as_current_span("model.generate_advice_stream") as span:
            span.set_attribute("model.user_text_length", len(user_text))
            span.set_attribute("model.session_id", session_id)
            span.set_attribute("model.streaming", True)
            
            # Safety guard check with HITL queuing for crisis
            # Use guardrails for crisis detection and HITL queuing (<500ms requirement)
            parent_name = get_parent_name(session_id)
            classification, refusal_message, hitl_id = check_and_queue_crisis(
                user_text,
                session_id,
                parent_name=parent_name
            )
            # Get safety metadata for backward compatibility
            _, _, safety_metadata = check_message_safety(user_text, session_id)
            
            # Send classification event
            yield f"event: classification\n"
            yield f"data: {json.dumps({'classification': classification.value})}\n\n"
            
            if classification == SafetyClassification.SAFE:
                # Check budget before generating advice
                ledger = get_ledger()
                is_over_budget, current_cost, budget_limit = ledger.is_over_budget()
                
                # Debug logging for budget check
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"[BUDGET CHECK] is_over_budget={is_over_budget}, current_cost=${current_cost:.6f}, budget_limit=${budget_limit:.6f}")
                
                # Retrieve knowledge from RAG
                retrieved_knowledge = retrieve_knowledge(user_text, max_results=2)
                
                # Determine mode based on budget
                use_lite_mode = is_over_budget
                
                if use_lite_mode:
                    logger.info(f"[LITE MODE] Budget exceeded, using lite mode for session {session_id}")
                
                # Prepare advice content
                if retrieved_knowledge:
                    top_entry = retrieved_knowledge[0]
                    relevance_score = top_entry.get("relevance_score", 0)
                    
                    if relevance_score > 0:
                        if use_lite_mode:
                            # Use lite mode response
                            advice_content = generate_lite_mode_response(user_text, retrieved_knowledge)
                            # Send budget notice
                            notice = get_lite_mode_notice()
                            yield f"event: notice\n"
                            yield f"data: {json.dumps(notice)}\n\n"
                        else:
                            # Good match - stream the full content
                            advice_content = top_entry.get("content", "")
                        
                        # Prepare citations
                        citations = [
                            {
                                "id": entry.get("citation", {}).get("id"),
                                "title": entry.get("citation", {}).get("title"),
                                "source": entry.get("citation", {}).get("source"),
                                "source_url": entry.get("citation", {}).get("source_url"),
                            }
                            for entry in retrieved_knowledge
                        ]
                        
                        # Send citations event first
                        yield f"event: citations\n"
                        yield f"data: {json.dumps({'citations': citations})}\n\n"
                        
                        # Stream advice content chunk by chunk
                        chunks = chunk_text(advice_content)
                        
                        # Send start event
                        yield f"event: start\n"
                        yield f"data: {json.dumps({'type': 'advice', 'echo': user_text})}\n\n"
                        
                        # Stream chunks with small delay for visible streaming effect
                        for chunk in chunks:
                            # Check if client disconnected
                            if await request.is_disconnected():
                                break
                            
                            yield f"event: chunk\n"
                            yield f"data: {json.dumps({'content': chunk})}\n\n"
                            
                            # Small delay to make streaming visible (but still fast)
                            await asyncio.sleep(0.05)  # 50ms between chunks
                        
                        # Send end event
                        yield f"event: end\n"
                        yield f"data: {json.dumps({'done': True})}\n\n"
                        
                        # Record turn in billing ledger
                        turn_record = ledger.record_turn(
                            session_id=session_id,
                            input_text=user_text,
                            output_text=advice_content,
                            model_mode="lite" if use_lite_mode else "full",
                            was_over_budget=is_over_budget
                        )
                        
                        # Set model span attributes
                        latency_ms = (time.time() - start_time) * 1000
                        span.set_attribute("model.latency_ms", latency_ms)
                        span.set_attribute("model.advice_length", len(advice_content))
                        span.set_attribute("model.citations_count", len(citations))
                        span.set_attribute("model.has_citations", len(citations) > 0)
                        span.set_attribute("model.relevance_score", relevance_score)
                        span.set_attribute("model.classification", "SAFE")
                        span.set_attribute("model.mode", "lite" if use_lite_mode else "full")
                        span.set_attribute("billing.cost_usd", turn_record.cost_usd)
                        span.set_attribute("billing.was_over_budget", is_over_budget)
                    else:
                        # No good match - use lite mode if over budget, otherwise fallback
                        if use_lite_mode:
                            fallback_message = generate_lite_mode_response(user_text, retrieved_knowledge)
                            notice = get_lite_mode_notice()
                            yield f"event: notice\n"
                            yield f"data: {json.dumps(notice)}\n\n"
                        else:
                            fallback_message = (
                                f"I understand you're asking about '{user_text}'. "
                                "I don't have specific information on that topic in my knowledge base. "
                                "However, I can help you with general parenting topics like:\n\n"
                                "• Behavior management and positive reinforcement\n"
                                "• Sleep routines and bedtime strategies\n"
                                "• Managing screen time and technology use\n"
                                "• Handling sibling conflicts\n"
                                "• Mealtime strategies for picky eaters\n"
                                "• Building emotional intelligence\n"
                                "• Encouraging independence\n"
                                "• Managing tantrums\n"
                                "• Homework and learning support\n"
                                "• Building self-esteem\n\n"
                                "Would you like guidance on any of these topics instead?"
                            )
                        
                        yield f"event: start\n"
                        yield f"data: {json.dumps({'type': 'advice', 'echo': user_text})}\n\n"
                        
                        chunks = chunk_text(fallback_message)
                        for chunk in chunks:
                            if await request.is_disconnected():
                                break
                            yield f"event: chunk\n"
                            yield f"data: {json.dumps({'content': chunk})}\n\n"
                            await asyncio.sleep(0.05)
                        
                        yield f"event: end\n"
                        yield f"data: {json.dumps({'done': True})}\n\n"
                        
                        # Record turn for fallback
                        turn_record = ledger.record_turn(
                            session_id=session_id,
                            input_text=user_text,
                            output_text=fallback_message,
                            model_mode="lite" if use_lite_mode else "full",
                            was_over_budget=is_over_budget
                        )
                        
                        # Set model span attributes for fallback
                        latency_ms = (time.time() - start_time) * 1000
                        span.set_attribute("model.latency_ms", latency_ms)
                        span.set_attribute("model.classification", "SAFE_FALLBACK")
                        span.set_attribute("model.advice_length", len(fallback_message))
                        span.set_attribute("model.mode", "lite" if use_lite_mode else "full")
                        span.set_attribute("billing.cost_usd", turn_record.cost_usd)
                        span.set_attribute("billing.was_over_budget", is_over_budget)
                else:
                    # Fallback if no knowledge retrieved
                    if use_lite_mode:
                        fallback = generate_lite_mode_response(user_text, None)
                        notice = get_lite_mode_notice()
                        yield f"event: notice\n"
                        yield f"data: {json.dumps(notice)}\n\n"
                    else:
                        fallback = (
                            "I hear you. Here are a few ideas you might try: "
                            "1) Acknowledge feelings, 2) Offer a simple choice, 3) Keep routines consistent."
                        )
                    
                    yield f"event: start\n"
                    yield f"data: {json.dumps({'type': 'advice', 'echo': user_text})}\n\n"
                    
                    chunks = chunk_text(fallback)
                    for chunk in chunks:
                        if await request.is_disconnected():
                            break
                        yield f"event: chunk\n"
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                        await asyncio.sleep(0.05)
                    
                    yield f"event: end\n"
                    yield f"data: {json.dumps({'done': True})}\n\n"
                    
                    # Record turn for fallback
                    turn_record = ledger.record_turn(
                        session_id=session_id,
                        input_text=user_text,
                        output_text=fallback,
                        model_mode="lite" if use_lite_mode else "full",
                        was_over_budget=is_over_budget
                    )
                    
                    # Set model span attributes for fallback
                    latency_ms = (time.time() - start_time) * 1000
                    span.set_attribute("model.latency_ms", latency_ms)
                    span.set_attribute("model.classification", "SAFE_FALLBACK")
                    span.set_attribute("model.advice_length", len(fallback))
                    span.set_attribute("model.mode", "lite" if use_lite_mode else "full")
                    span.set_attribute("billing.cost_usd", turn_record.cost_usd)
                    span.set_attribute("billing.was_over_budget", is_over_budget)
            
            elif classification == SafetyClassification.BLOCKED:
                # Stream refusal message
                yield f"event: start\n"
                yield f"data: {json.dumps({'type': 'refusal', 'echo': user_text})}\n\n"
                
                chunks = chunk_text(refusal_message)
                for chunk in chunks:
                    if await request.is_disconnected():
                        break
                    yield f"event: chunk\n"
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                    await asyncio.sleep(0.05)
                
                yield f"event: end\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
                
                # Record turn for blocked (minimal cost - just refusal message)
                ledger = get_ledger()
                turn_record = ledger.record_turn(
                    session_id=session_id,
                    input_text=user_text,
                    output_text=refusal_message,
                    model_mode="full",  # Refusal messages are always full
                    was_over_budget=False
                )
                
                # Set model span attributes for blocked
                latency_ms = (time.time() - start_time) * 1000
                span.set_attribute("model.latency_ms", latency_ms)
                span.set_attribute("model.classification", "BLOCKED")
                span.set_attribute("model.advice_length", len(refusal_message))
                span.set_attribute("billing.cost_usd", turn_record.cost_usd)
            
            elif classification == SafetyClassification.ESCALATE:
                # Stream crisis redirect
                crisis_message = (
                    "I understand this is a serious situation that requires immediate professional support. "
                    "Your message has been flagged for review by our mentor team. "
                    "For immediate crisis support, please contact:\n\n"
                    "• National Suicide & Crisis Lifeline: 988\n"
                    "• Crisis Text Line: Text HOME to 741741\n"
                    "• National Child Abuse Hotline: 1-800-4-A-CHILD\n\n"
                    "A mentor will review your message and respond as soon as possible."
                )
                
                yield f"event: start\n"
                yield f"data: {json.dumps({'type': 'crisis_redirect', 'echo': user_text})}\n\n"
                
                chunks = chunk_text(crisis_message)
                for chunk in chunks:
                    if await request.is_disconnected():
                        break
                    yield f"event: chunk\n"
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                    await asyncio.sleep(0.05)
                
                yield f"event: end\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
                
                # Record turn for escalate (minimal cost - just redirect message)
                ledger = get_ledger()
                turn_record = ledger.record_turn(
                    session_id=session_id,
                    input_text=user_text,
                    output_text=crisis_message,
                    model_mode="full",  # Crisis messages are always full
                    was_over_budget=False
                )
                
                # Set model span attributes for escalate
                latency_ms = (time.time() - start_time) * 1000
                span.set_attribute("model.latency_ms", latency_ms)
                span.set_attribute("model.classification", "ESCALATE")
                span.set_attribute("model.advice_length", len(crisis_message))
                span.set_attribute("billing.cost_usd", turn_record.cost_usd)
            
    except Exception as e:
        # Send error event
        yield f"event: error\n"
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@router.post("/stream")
async def stream_advice(request_body: StreamAdviceRequest, request: Request):
    print(f"[SSE POST] /api/coach/stream called for session {request_body.session_id}")
    """
    SSE endpoint for streaming advice.
    
    Usage:
        POST /api/coach/stream
        Body: {"message": "user question", "session_id": "session_123"}
    
    Returns:
        StreamingResponse with SSE events
    """
    return StreamingResponse(
        stream_advice_generator(
            request_body.message,
            request_body.session_id,
            request
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )

