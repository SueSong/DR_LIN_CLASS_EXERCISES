from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import json
import time
from datetime import datetime
import uuid

app = FastAPI(title="Streaming Demo API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3100", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
sessions: Dict[str, List[Dict]] = {}
active_websockets: Dict[str, WebSocket] = {}

# Models
class ChatMessage(BaseModel):
    role: str  # user, agent, admin
    content: str
    session_id: Optional[str] = None

class SessionRestore(BaseModel):
    session_id: str

# Simulated AI response generator
async def generate_ai_response(prompt: str, mode: str = "sse"):
    """Simulate streaming AI response"""
    responses = [
        f"I understand you said: '{prompt[:50]}...'",
        "Let me think about that...",
        "Based on my analysis, ",
        "I would recommend ",
        f"that you consider {'using SSE for one-way streaming' if mode == 'sse' else 'using WebSockets for bidirectional communication'}.",
        " This approach offers better performance and user experience.",
        " Would you like me to elaborate on this?"
    ]
    
    for chunk in responses:
        await asyncio.sleep(0.3)  # Simulate processing time
        yield chunk

# SSE Endpoint
@app.post("/api/chat/sse")
async def chat_sse(message: ChatMessage, request: Request):
    """Server-Sent Events endpoint for streaming responses"""
    
    # Create or get session
    session_id = message.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = []
    
    # Store user message
    sessions[session_id].append({
        "id": str(uuid.uuid4()),
        "role": message.role,
        "content": message.content,
        "timestamp": datetime.now().isoformat(),
        "mode": "sse"
    })
    
    async def event_generator():
        """Generate SSE events"""
        # Send session ID first
        yield {
            "event": "session",
            "data": json.dumps({"session_id": session_id})
        }
        
        # Send start event
        response_id = str(uuid.uuid4())
        yield {
            "event": "start",
            "data": json.dumps({
                "id": response_id,
                "role": "assistant",
                "timestamp": datetime.now().isoformat()
            })
        }
        
        # Stream response chunks
        full_response = ""
        async for chunk in generate_ai_response(message.content, "sse"):
            full_response += chunk
            yield {
                "event": "chunk",
                "data": json.dumps({
                    "id": response_id,
                    "content": chunk
                })
            }
            
            # Check if client disconnected
            if await request.is_disconnected():
                print(f"Client disconnected during SSE stream")
                break
        
        # Store AI response
        sessions[session_id].append({
            "id": response_id,
            "role": "assistant",
            "content": full_response,
            "timestamp": datetime.now().isoformat(),
            "mode": "sse"
        })
        
        # Send end event
        yield {
            "event": "end",
            "data": json.dumps({
                "id": response_id,
                "done": True
            })
        }
    
    return EventSourceResponse(event_generator())

# WebSocket Endpoint
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for bidirectional streaming"""
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    active_websockets[connection_id] = websocket
    
    print(f"✅ WebSocket connected: {connection_id}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "chat":
                # Handle chat message
                session_id = message_data.get("session_id") or str(uuid.uuid4())
                role = message_data.get("role", "user")
                content = message_data.get("content", "")
                
                if session_id not in sessions:
                    sessions[session_id] = []
                
                # Store user message
                user_msg_id = str(uuid.uuid4())
                sessions[session_id].append({
                    "id": user_msg_id,
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                    "mode": "websocket"
                })
                
                # Send acknowledgment
                await websocket.send_json({
                    "type": "ack",
                    "message_id": user_msg_id,
                    "session_id": session_id
                })
                
                # Stream AI response
                response_id = str(uuid.uuid4())
                await websocket.send_json({
                    "type": "start",
                    "id": response_id,
                    "role": "assistant",
                    "timestamp": datetime.now().isoformat()
                })
                
                full_response = ""
                async for chunk in generate_ai_response(content, "websocket"):
                    full_response += chunk
                    await websocket.send_json({
                        "type": "chunk",
                        "id": response_id,
                        "content": chunk
                    })
                
                # Store AI response
                sessions[session_id].append({
                    "id": response_id,
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": datetime.now().isoformat(),
                    "mode": "websocket"
                })
                
                # Send end
                await websocket.send_json({
                    "type": "end",
                    "id": response_id,
                    "done": True
                })
            
            elif message_type == "ping":
                # Heartbeat
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "abort":
                # Client wants to abort current stream
                await websocket.send_json({
                    "type": "aborted",
                    "message": "Stream aborted by client"
                })
    
    except WebSocketDisconnect:
        print(f"❌ WebSocket disconnected: {connection_id}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        if connection_id in active_websockets:
            del active_websockets[connection_id]

# Session Management Endpoints
@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session history"""
    if session_id not in sessions:
        return {"error": "Session not found", "session_id": session_id, "messages": []}
    
    return {
        "session_id": session_id,
        "messages": sessions[session_id],
        "message_count": len(sessions[session_id])
    }

@app.post("/api/sessions/{session_id}/restore")
async def restore_session(session_id: str, request: Request):
    """Restore session with deterministic replay (SSE)"""
    if session_id not in sessions:
        return {"error": "Session not found"}
    
    async def replay_generator():
        """Replay session messages with timing"""
        messages = sessions[session_id]
        
        yield {
            "event": "session",
            "data": json.dumps({
                "session_id": session_id,
                "total_messages": len(messages)
            })
        }
        
        for i, msg in enumerate(messages):
            # Simulate original timing (faster for demo)
            await asyncio.sleep(0.2)
            
            yield {
                "event": "message",
                "data": json.dumps({
                    "index": i,
                    "message": msg
                })
            }
            
            if await request.is_disconnected():
                break
        
        yield {
            "event": "complete",
            "data": json.dumps({"restored": True})
        }
    
    return EventSourceResponse(replay_generator())

@app.get("/api/sessions")
async def list_sessions():
    """List all sessions"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "message_count": len(messages),
                "last_activity": messages[-1]["timestamp"] if messages else None
            }
            for sid, messages in sessions.items()
        ]
    }

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session (admin only)"""
    if session_id in sessions:
        del sessions[session_id]
        return {"deleted": True, "session_id": session_id}
    return {"error": "Session not found"}

# Role capabilities endpoint
@app.get("/api/capabilities/{role}")
async def get_capabilities(role: str):
    """Get capabilities for a role"""
    capabilities = {
        "user": {
            "can_chat": True,
            "can_view_history": True,
            "can_restore": False,
            "can_delete": False,
            "can_interrupt": False,
            "can_prioritize": False
        },
        "agent": {
            "can_chat": True,
            "can_view_history": True,
            "can_restore": True,
            "can_delete": False,
            "can_interrupt": True,
            "can_prioritize": True
        },
        "admin": {
            "can_chat": True,
            "can_view_history": True,
            "can_restore": True,
            "can_delete": True,
            "can_interrupt": True,
            "can_prioritize": True
        }
    }
    
    return capabilities.get(role, capabilities["user"])

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "active_websockets": len(active_websockets),
        "active_sessions": len(sessions)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)

