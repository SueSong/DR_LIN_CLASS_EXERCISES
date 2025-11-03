from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import time
from ..guards import check_message_safety, SafetyClassification
from ..guardrails import check_and_queue_crisis, get_session_hitl_replies
from ..sessions import get_parent_name
from ..rag_retrieval import retrieve_knowledge
from ..observability import get_tracer
import sys
from pathlib import Path
billing_dir = Path(__file__).parent.parent.parent.parent / "billing"
sys.path.insert(0, str(billing_dir.parent))
from billing.ledger import get_ledger
from billing.lite_mode import generate_lite_mode_response, get_lite_mode_notice

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/coach/{session_id}")
async def coach_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        await websocket.send_json({
            "type": "session_started",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Check for any pending mentor replies when session starts
        pending_replies = get_session_hitl_replies(session_id)
        for reply in pending_replies:
            if reply.get("mentor_reply"):
                await websocket.send_json({
                    "type": "mentor_reply",
                    "text": reply["mentor_reply"],
                    "original_message": reply.get("message", ""),
                    "timestamp": reply.get("mentor_replied_at", datetime.utcnow().isoformat()),
                })
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except Exception:
                msg = {"type": "text", "text": data}

            if msg.get("type") == "text":
                user_text = msg.get("text", "").strip()
                
                print(f"[WEBSOCKET] Received message from session {session_id}: '{user_text[:100]}...'")
                
                tracer = get_tracer()
                start_time = time.time()
                
                with tracer.start_as_current_span("model.generate_advice") as span:
                    span.set_attribute("model.user_text_length", len(user_text))
                    span.set_attribute("model.session_id", session_id)
                    
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
                    
                    if classification == SafetyClassification.SAFE:
                        # Check budget before generating advice
                        ledger = get_ledger()
                        is_over_budget, current_cost, budget_limit = ledger.is_over_budget()
                        use_lite_mode = is_over_budget
                        
                        # Retrieve relevant knowledge from RAG
                        retrieved_knowledge = retrieve_knowledge(user_text, max_results=2)
                        
                        # Generate advice incorporating retrieved knowledge
                        if retrieved_knowledge:
                            top_entry = retrieved_knowledge[0]
                            relevance_score = top_entry.get("relevance_score", 0)
                            
                            # Check if we found a good match (relevance_score > 0)
                            # Score of 0 means it's the fallback entry (not a real match)
                            if relevance_score > 0:
                                if use_lite_mode:
                                    # Use lite mode response
                                    advice_text = generate_lite_mode_response(user_text, retrieved_knowledge)
                                else:
                                    # Good match found - use the content
                                    advice = top_entry.get("content", "")
                                    
                                    # Include a brief summary
                                    advice_parts = [advice]
                                    if len(retrieved_knowledge) > 1:
                                        # Mention additional relevant topics
                                        additional = retrieved_knowledge[1]
                                        advice_parts.append(f"\n\nYou might also find helpful: {additional.get('title', '')}")
                                    
                                    advice_text = "\n".join(advice_parts)
                                
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
                                
                                # Record turn in billing ledger
                                turn_record = ledger.record_turn(
                                    session_id=session_id,
                                    input_text=user_text,
                                    output_text=advice_text,
                                    model_mode="lite" if use_lite_mode else "full",
                                    was_over_budget=is_over_budget
                                )
                            else:
                                # No good match found - use lite mode if over budget
                                if use_lite_mode:
                                    advice_text = generate_lite_mode_response(user_text, retrieved_knowledge)
                                else:
                                    advice_text = (
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
                                citations = []
                                
                                # Record turn
                                turn_record = ledger.record_turn(
                                    session_id=session_id,
                                    input_text=user_text,
                                    output_text=advice_text,
                                    model_mode="lite" if use_lite_mode else "full",
                                    was_over_budget=is_over_budget
                                )
                            
                            # Set model span attributes
                            latency_ms = (time.time() - start_time) * 1000
                            span.set_attribute("model.latency_ms", latency_ms)
                            span.set_attribute("model.advice_length", len(advice_text))
                            span.set_attribute("model.citations_count", len(citations))
                            span.set_attribute("model.has_citations", len(citations) > 0)
                            span.set_attribute("model.relevance_score", top_entry.get("relevance_score", 0) if retrieved_knowledge else 0)
                            span.set_attribute("model.mode", "lite" if use_lite_mode else "full")
                            span.set_attribute("billing.cost_usd", turn_record.cost_usd)
                            span.set_attribute("billing.was_over_budget", is_over_budget)
                            
                            response_data = {
                                "type": "advice",
                                "text": advice_text,
                                "echo": user_text,
                                "citations": citations,
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                            
                            # Add budget notice if in lite mode
                            if use_lite_mode:
                                notice = get_lite_mode_notice()
                                response_data["budget_notice"] = notice
                            
                            await websocket.send_json(response_data)
                        else:
                            # Fallback if no knowledge retrieved at all
                            if use_lite_mode:
                                advice_text = generate_lite_mode_response(user_text, None)
                            else:
                                advice_text = (
                                    "I hear you. Here are a few ideas you might try: "
                                    "1) Acknowledge feelings, 2) Offer a simple choice, 3) Keep routines consistent."
                                )
                            citations = []
                            
                            # Record turn
                            turn_record = ledger.record_turn(
                                session_id=session_id,
                                input_text=user_text,
                                output_text=advice_text,
                                model_mode="lite" if use_lite_mode else "full",
                                was_over_budget=is_over_budget
                            )
                            
                            # Set model span attributes
                            latency_ms = (time.time() - start_time) * 1000
                            span.set_attribute("model.latency_ms", latency_ms)
                            span.set_attribute("model.advice_length", len(advice_text))
                            span.set_attribute("model.citations_count", len(citations))
                            span.set_attribute("model.has_citations", len(citations) > 0)
                            span.set_attribute("model.relevance_score", 0)
                            span.set_attribute("model.mode", "lite" if use_lite_mode else "full")
                            span.set_attribute("billing.cost_usd", turn_record.cost_usd)
                            span.set_attribute("billing.was_over_budget", is_over_budget)
                            
                            response_data = {
                                "type": "advice",
                                "text": advice_text,
                                "echo": user_text,
                                "citations": citations,
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                            
                            if use_lite_mode:
                                notice = get_lite_mode_notice()
                                response_data["budget_notice"] = notice
                            
                            await websocket.send_json(response_data)
                    elif classification == SafetyClassification.BLOCKED:
                        # Record turn for blocked
                        ledger = get_ledger()
                        turn_record = ledger.record_turn(
                            session_id=session_id,
                            input_text=user_text,
                            output_text=refusal_message or "",
                            model_mode="full",
                            was_over_budget=False
                        )
                        
                        # Set model span attributes for blocked
                        latency_ms = (time.time() - start_time) * 1000
                        span.set_attribute("model.latency_ms", latency_ms)
                        span.set_attribute("model.classification", "BLOCKED")
                        span.set_attribute("billing.cost_usd", turn_record.cost_usd)
                        
                        # Send refusal message
                        await websocket.send_json({
                            "type": "refusal",
                            "text": refusal_message,
                            "echo": user_text,
                            "reason": "out_of_scope",
                            "timestamp": datetime.utcnow().isoformat(),
                            "metadata": safety_metadata,
                        })
                    elif classification == SafetyClassification.ESCALATE:
                        # Create crisis message
                        crisis_message = (
                            "I understand this is a serious situation that requires immediate professional support. "
                            "Your message has been flagged for review by our mentor team. "
                            "For immediate crisis support, please contact:\n\n"
                            "• National Suicide & Crisis Lifeline: 988\n"
                            "• Crisis Text Line: Text HOME to 741741\n"
                            "• National Child Abuse Hotline: 1-800-4-A-CHILD\n\n"
                            "A mentor will review your message and respond as soon as possible."
                        )
                        
                        # Record turn for escalate
                        ledger = get_ledger()
                        turn_record = ledger.record_turn(
                            session_id=session_id,
                            input_text=user_text,
                            output_text=crisis_message,
                            model_mode="full",
                            was_over_budget=False
                        )
                        
                        # Set model span attributes for escalate
                        latency_ms = (time.time() - start_time) * 1000
                        span.set_attribute("model.latency_ms", latency_ms)
                        span.set_attribute("model.classification", "ESCALATE")
                        span.set_attribute("billing.cost_usd", turn_record.cost_usd)
                        if hitl_id:
                            span.set_attribute("model.hitl_id", hitl_id)
                        
                        # Send crisis redirect message
                        await websocket.send_json({
                            "type": "crisis_redirect",
                            "text": crisis_message,
                            "echo": user_text,
                            "reason": "crisis_situation",
                            "hitl_id": hitl_id,
                            "timestamp": datetime.utcnow().isoformat(),
                            "metadata": safety_metadata,
                        })
                        # Crisis message has been queued to HITL for mentor review
            else:
                await websocket.send_json({"type": "noop"})

    except WebSocketDisconnect:
        pass


