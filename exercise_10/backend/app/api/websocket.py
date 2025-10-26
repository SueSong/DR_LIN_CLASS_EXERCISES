from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json
from datetime import datetime
import os
import asyncio
import io
import wave

# Import transcription services
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ..agents.transcription import TranscriptionEngine
    from ..agents.context_manager import get_state
except:
    TranscriptionEngine = None
    get_state = None

try:
    from .ai_service import AIAssistantService
except:
    AIAssistantService = None

router = APIRouter(tags=["WebSocket"])

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Audio buffers for transcription (call_id -> bytearray)
audio_buffers: Dict[str, bytearray] = {}

# Transcription service instance
transcription_engine = None
if os.getenv("OPENAI_API_KEY") and TranscriptionEngine:
    try:
        transcription_engine = TranscriptionEngine(os.getenv("OPENAI_API_KEY"))
        print("Transcription engine initialized")
    except Exception as e:
        print(f"WARNING: Could not initialize transcription: {e}")

# AI Assistant service instance
ai_assistant = None
if os.getenv("OPENAI_API_KEY") and AIAssistantService:
    try:
        ai_assistant = AIAssistantService(os.getenv("OPENAI_API_KEY"))
        print("✅ AI Assistant service initialized")
    except Exception as e:
        print(f"❌ WARNING: Could not initialize AI Assistant: {e}")
else:
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ WARNING: OPENAI_API_KEY not found in environment")
    if not AIAssistantService:
        print("❌ WARNING: AIAssistantService not imported")

# Buffer size: 5 seconds of audio at 16kHz, 16-bit
BUFFER_SIZE_SECONDS = 5
BUFFER_SIZE_BYTES = 16000 * 2 * BUFFER_SIZE_SECONDS  # 160,000 bytes

async def transcribe_audio_buffer(call_id: str, audio_data: bytes, speaker: str) -> str:
    """Transcribe audio buffer using Whisper API"""
    if not os.getenv("OPENAI_API_KEY"):
        return None
    
    try:
        # Convert raw PCM to WAV format
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            wav_file.writeframes(audio_data)
        
        wav_buffer.seek(0)
        
        # Call Whisper API
        import openai
        response = await openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY")).audio.transcriptions.create(
            model="whisper-1",
            file=("audio.wav", wav_buffer, "audio/wav"),
            language="en"
        )
        
        text = response.text.strip()
        
        # Update conversation state
        if get_state and text:
            state = get_state(call_id)
            state.add_transcript(speaker, text)
        
        print(f"📝 Transcribed ({speaker}): {text[:50]}...")
        return text
        
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None

async def transcribe_and_broadcast(
    call_id: str,
    audio_data: bytes,
    speaker: str,
    sender_ws: WebSocket,
    partner_call_id: str = None
):
    """Transcribe audio and send to both sender and partner"""
    try:
        # Transcribe the audio
        text = await transcribe_audio_buffer(call_id, audio_data, speaker)
        
        if not text:
            return
        
        # Create transcript message
        transcript_msg = {
            "type": "transcript",
            "speaker": speaker,
            "text": text,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to sender
        try:
            await sender_ws.send_json(transcript_msg)
            print(f"📤 Sent transcript to sender ({speaker}): {text[:30]}...")
        except Exception as e:
            print(f"❌ Error sending to sender: {e}")
        
        # Send to partner
        if partner_call_id and partner_call_id in active_connections:
            try:
                await active_connections[partner_call_id].send_json(transcript_msg)
                print(f"📤 Sent transcript to partner: {text[:30]}...")
            except Exception as e:
                print(f"❌ Error sending to partner: {e}")
                # Remove dead connection
                if partner_call_id in active_connections:
                    del active_connections[partner_call_id]
        
        # Generate AI suggestion for agent when customer speaks
        if speaker == "customer" and partner_call_id and partner_call_id in active_connections and ai_assistant:
            try:
                # Generate suggestion based on customer message
                suggestion = await ai_assistant.generate_suggestion(
                    call_id=call_id,
                    customer_message=text
                )
                
                # Send suggestion only to agent (partner)
                suggestion_msg = {
                    "type": "ai_suggestion",
                    "suggestion": suggestion["suggestion"],
                    "reasoning": suggestion.get("reasoning", ""),
                    "action": suggestion.get("action", ""),
                    "confidence": suggestion["confidence"],
                    "timestamp": suggestion["timestamp"]
                }
                
                # Check if partner connection is still active
                if partner_call_id in active_connections:
                    try:
                        await active_connections[partner_call_id].send_json(suggestion_msg)
                        print(f"🤖 Sent AI suggestion to agent: {suggestion['suggestion'][:50]}... (confidence: {suggestion['confidence']})")
                    except Exception as send_error:
                        print(f"❌ Error sending AI suggestion to agent: {send_error}")
                        # Remove dead connection
                        if partner_call_id in active_connections:
                            del active_connections[partner_call_id]
                else:
                    print(f"❌ Partner connection {partner_call_id} not found for AI suggestion")
                
            except Exception as e:
                print(f"❌ Error generating AI suggestion: {e}")
                
    except Exception as e:
        print(f"❌ Error in transcribe_and_broadcast: {e}")

@router.websocket("/ws/call/{call_id}")
async def websocket_call_endpoint(websocket: WebSocket, call_id: str):
    """
    WebSocket endpoint for real-time call handling
    
    Receives:
    - Audio chunks (bytes)
    - Control messages (JSON)
    
    Sends:
    - Transcription updates
    - AI suggestions
    - Status updates
    """
    await websocket.accept()
    active_connections[call_id] = websocket
    audio_buffers[call_id] = bytearray()
    
    print(f"✅ WebSocket connected: {call_id}")
    
    try:
        while True:
            # Receive data from client
            data = await websocket.receive()
            
            if "bytes" in data:
                # Audio data received
                audio_chunk = data["bytes"]
                
                # Route audio to partner (for real-time audio streaming)
                from .calls import active_calls
                partner_call_id = None
                speaker = "customer"  # Default
                
                # Find partner and determine speaker
                for active_call_id, call_info in active_calls.items():
                    if call_id == call_info.get("agent_call_id"):
                        partner_call_id = call_info.get("customer_call_id")
                        speaker = "agent"
                        break
                    elif call_id == call_info.get("customer_call_id"):
                        partner_call_id = call_info.get("agent_call_id")
                        speaker = "customer"
                        break
                
                # Forward audio to partner if connected
                if partner_call_id and partner_call_id in active_connections:
                    try:
                        await active_connections[partner_call_id].send_bytes(audio_chunk)
                    except Exception as e:
                        print(f"Error forwarding audio: {e}")
                
                # Buffer audio for transcription
                if call_id in audio_buffers:
                    audio_buffers[call_id].extend(audio_chunk)
                    
                    # Check if buffer is full (5 seconds of audio)
                    if len(audio_buffers[call_id]) >= BUFFER_SIZE_BYTES:
                        # Transcribe the buffered audio
                        audio_data = bytes(audio_buffers[call_id])
                        audio_buffers[call_id].clear()
                        
                        # Transcribe in background to avoid blocking
                        asyncio.create_task(
                            transcribe_and_broadcast(
                                call_id, 
                                audio_data, 
                                speaker, 
                                websocket, 
                                partner_call_id
                            )
                        )
                
            elif "text" in data:
                # Control message received
                message = json.loads(data["text"])
                
                if message["type"] == "start_call":
                    print(f"📞 Call started: {call_id}")
                    await handle_start_call(call_id, message, websocket)
                    
                elif message["type"] == "end_call":
                    print(f"📴 Call ended: {call_id}")
                    await handle_end_call(call_id, message, websocket)
                    break
                    
                elif message["type"] == "transcript":
                    # Manual transcript entry (for testing) or real transcription
                    await handle_transcript(call_id, message, websocket)
    
    except WebSocketDisconnect:
        print(f"❌ WebSocket disconnected: {call_id}")
    
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    
    finally:
        # Cleanup
        if call_id in active_connections:
            del active_connections[call_id]
        if call_id in audio_buffers:
            del audio_buffers[call_id]
        if ai_assistant:
            ai_assistant.clear_history(call_id)
        
        # Clear conversation state from context manager
        try:
            from ..agents.context_manager import conversation_states
            if call_id in conversation_states:
                del conversation_states[call_id]
                print(f"🧹 Cleared conversation state for {call_id}")
        except:
            pass
            
        print(f"🧹 Cleaned up resources for {call_id}")

async def handle_start_call(call_id: str, message: dict, websocket: WebSocket):
    """Handle call start"""
    # Clear any existing conversation state for this call
    try:
        from ..agents.context_manager import conversation_states
        if call_id in conversation_states:
            del conversation_states[call_id]
            print(f"🧹 Cleared existing conversation state for {call_id}")
    except:
        pass
    
    await websocket.send_json({
        "type": "call_started",
        "call_id": call_id,
        "timestamp": datetime.utcnow().isoformat()
    })

async def handle_end_call(call_id: str, message: dict, websocket: WebSocket):
    """Handle call end"""
    await websocket.send_json({
        "type": "call_ended",
        "call_id": call_id,
        "timestamp": datetime.utcnow().isoformat()
    })

async def handle_transcript(call_id: str, message: dict, websocket: WebSocket):
    """Handle transcript segment and route to partner"""
    speaker = message.get("speaker", "customer")
    text = message.get("text", "")
    
    transcript_msg = {
        "type": "transcript",
        "speaker": speaker,
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Echo back to sender (for confirmation)
    await websocket.send_json(transcript_msg)
    
    # Route to partner (agent or customer)
    # Import from calls.py to check active connections
    from .calls import active_calls
    
    # Find partner's call_id
    partner_call_id = None
    for active_call_id, call_info in active_calls.items():
        if call_id == call_info.get("agent_call_id"):
            partner_call_id = call_info.get("customer_call_id")
            break
        elif call_id == call_info.get("customer_call_id"):
            partner_call_id = call_info.get("agent_call_id")
            break
    
    # Send to partner if connected
    if partner_call_id and partner_call_id in active_connections:
        try:
            await active_connections[partner_call_id].send_json(transcript_msg)
            print(f"📤 Routed message from {call_id} to {partner_call_id}")
        except Exception as e:
            print(f"Error routing message: {e}")

async def broadcast_to_call(call_id: str, message: dict):
    """Broadcast a message to a specific call's WebSocket"""
    if call_id in active_connections:
        try:
            await active_connections[call_id].send_json(message)
        except Exception as e:
            print(f"Error broadcasting to {call_id}: {e}")

