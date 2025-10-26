# Exercise 10: Architecture Deep Dive 🏗️

## System Architecture

### High-Level Flow

```
Customer (Browser)
    ↓ WebRTC Audio
    ↓
Backend WebRTC Handler
    ↓ Audio Chunks
    ↓
Speech-to-Text Engine (Whisper/Deepgram)
    ↓ Transcription
    ↓
Context Manager
    ├─→ Customer DB Lookup
    ├─→ Conversation History
    └─→ Knowledge Base
    ↓
AI Agent (OpenAI GPT-4 Streaming)
    ↓ Suggestions
    ↓ SSE/WebSocket
    ↓
Agent UI (Next.js)
    ├─ Live Transcript
    ├─ AI Suggestions
    ├─ Customer Info
    └─ Action Buttons
```

---

## Component Details

### 1. WebRTC Layer

**Responsibilities:**
- Establish peer-to-peer audio connection
- Handle ICE negotiation
- Manage audio tracks
- Monitor connection quality

**Tech Stack:**
- **Frontend:** Browser WebRTC API
- **Backend:** `aiortc` (Python) or `node-webrtc` (Node.js)
- **Signaling:** WebSocket for SDP exchange

**Flow:**
```javascript
// 1. Customer requests call
POST /api/calls/start → { call_id, customer_id }

// 2. Get STUN/TURN servers
GET /api/webrtc/ice-servers → { iceServers: [...] }

// 3. Create offer (customer side)
const offer = await peerConnection.createOffer();
POST /api/webrtc/offer → { call_id, offer }

// 4. Get answer (from backend)
← { answer }
await peerConnection.setRemoteDescription(answer);

// 5. Exchange ICE candidates via WebSocket
ws://server/ws/ice-candidates/{call_id}
```

---

### 2. Audio Processing Pipeline

**Steps:**
1. **Capture** - Browser `getUserMedia()` → MediaStream
2. **Encode** - Opus codec (48kHz, 16-bit)
3. **Chunk** - Split into 1-second buffers
4. **Stream** - Send via WebSocket to backend
5. **Decode** - Backend converts to WAV/PCM
6. **Transcribe** - Send to STT engine

**Optimizations:**
- **VAD (Voice Activity Detection)** - Only transcribe when speaking
- **Buffering** - Collect 3-5 seconds before sending
- **Parallel processing** - Transcribe while next chunk is recorded

---

### 3. Speech-to-Text Integration

**Option A: OpenAI Whisper API**
```python
import openai

async def transcribe_audio(audio_chunk: bytes, call_id: str):
    response = await openai.Audio.atranscribe(
        model="whisper-1",
        file=audio_chunk,
        language="en",
        response_format="verbose_json"  # Get timestamps
    )
    
    return {
        "text": response["text"],
        "segments": response["segments"],
        "confidence": response["confidence"]
    }
```

**Option B: Deepgram Streaming** (Recommended for real-time)
```python
from deepgram import Deepgram

dg_client = Deepgram(API_KEY)

async def stream_transcription(call_id: str):
    async with dg_client.transcription.live({
        "punctuate": True,
        "interim_results": True,
        "language": "en-US"
    }) as stream:
        
        async for audio_chunk in audio_queue:
            await stream.send(audio_chunk)
        
        async for result in stream:
            transcript = result.channel.alternatives[0].transcript
            yield {
                "call_id": call_id,
                "text": transcript,
                "is_final": result.is_final
            }
```

---

### 4. Context Manager

**Responsibilities:**
- Maintain conversation state
- Track mentioned entities (names, order IDs)
- Coordinate database lookups
- Build prompt context for AI

**State Structure:**
```python
@dataclass
class ConversationState:
    call_id: str
    customer_id: Optional[int]
    customer_info: Optional[dict]
    transcript: List[TranscriptSegment]
    topics: Set[str]  # ["billing", "refund", "technical_support"]
    entities: Dict[str, Any]  # {"order_id": "78901", "amount": "$129"}
    sentiment: str  # "positive" | "neutral" | "negative"
    suggestions_used: List[str]
    
    def add_transcript(self, speaker: str, text: str):
        self.transcript.append(TranscriptSegment(
            speaker=speaker,
            text=text,
            timestamp=datetime.now()
        ))
        
        # Extract entities
        self._extract_entities(text)
        
        # Update topics
        self._update_topics(text)
        
        # Analyze sentiment
        self._analyze_sentiment(text)
    
    def get_context_for_ai(self) -> str:
        """Build prompt context from conversation state"""
        context_parts = []
        
        if self.customer_info:
            context_parts.append(f"Customer: {self.customer_info['name']}")
            context_parts.append(f"Tier: {self.customer_info['tier']}")
            context_parts.append(f"Account Status: {self.customer_info['status']}")
        
        context_parts.append("\nRecent Conversation:")
        for segment in self.transcript[-10:]:  # Last 10 turns
            context_parts.append(f"{segment.speaker}: {segment.text}")
        
        if self.topics:
            context_parts.append(f"\nTopics Discussed: {', '.join(self.topics)}")
        
        return "\n".join(context_parts)
```

---

### 5. AI Assistant Agent

**Architecture:**
```python
class StreamingAssistant:
    def __init__(self):
        self.client = openai.AsyncOpenAI()
        self.system_prompt = self._load_system_prompt()
        self.tools = self._define_tools()
    
    async def stream_suggestions(
        self, 
        call_id: str, 
        context: ConversationState
    ):
        """Generate streaming suggestions based on conversation"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context.get_context_for_ai()}
        ]
        
        stream = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            tools=self.tools,
            stream=True,
            temperature=0.7
        )
        
        current_suggestion = ""
        current_tool_call = None
        
        async for chunk in stream:
            delta = chunk.choices[0].delta
            
            # Handle text content
            if delta.content:
                current_suggestion += delta.content
                yield {
                    "type": "text",
                    "content": delta.content,
                    "is_complete": False
                }
            
            # Handle tool calls
            if delta.tool_calls:
                tool_call = delta.tool_calls[0]
                if tool_call.function.name:
                    current_tool_call = tool_call.function.name
                    
                    # Execute tool
                    result = await self._execute_tool(
                        tool_call.function.name,
                        tool_call.function.arguments
                    )
                    
                    yield {
                        "type": "tool_result",
                        "tool": current_tool_call,
                        "result": result
                    }
            
            # End of message
            if chunk.choices[0].finish_reason:
                yield {
                    "type": "complete",
                    "suggestion": current_suggestion
                }
    
    def _define_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "lookup_customer",
                    "description": "Search for customer by name, email, or phone",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (name/email/phone)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_order_details",
                    "description": "Get order information by order number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_number": {"type": "string"}
                        },
                        "required": ["order_number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_policy",
                    "description": "Look up company policy on returns, refunds, SLA",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "policy_type": {
                                "type": "string",
                                "enum": ["return", "refund", "warranty", "sla"]
                            }
                        },
                        "required": ["policy_type"]
                    }
                }
            }
        ]
    
    async def _execute_tool(self, tool_name: str, arguments: str):
        """Execute tool call and return result"""
        args = json.loads(arguments)
        
        if tool_name == "lookup_customer":
            return await db.search_customer(args["query"])
        elif tool_name == "get_order_details":
            return await db.get_order(args["order_number"])
        elif tool_name == "check_policy":
            return await kb.get_policy(args["policy_type"])
        
        return None
```

---

### 6. Streaming Endpoints

**SSE for AI Suggestions:**
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/api/stream/suggestions/{call_id}")
async def stream_suggestions(call_id: str):
    async def generate():
        context = await context_manager.get_state(call_id)
        
        async for chunk in assistant.stream_suggestions(call_id, context):
            # Format as SSE
            data = json.dumps(chunk)
            yield f"data: {data}\n\n"
            
            # Keep connection alive
            await asyncio.sleep(0)
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

**WebSocket for Audio:**
```python
@app.websocket("/ws/call/{call_id}")
async def websocket_call(websocket: WebSocket, call_id: str):
    await websocket.accept()
    
    try:
        # Start transcription stream
        transcription_task = asyncio.create_task(
            stream_transcription(call_id, websocket)
        )
        
        # Receive audio
        while True:
            audio_chunk = await websocket.receive_bytes()
            
            # Queue for transcription
            await audio_queue.put({
                "call_id": call_id,
                "audio": audio_chunk,
                "timestamp": time.time()
            })
    
    except WebSocketDisconnect:
        transcription_task.cancel()
        await cleanup_call(call_id)
```

---

### 7. Frontend Streaming Components

**SSE Hook:**
```typescript
// hooks/useSSE.ts
import { useEffect, useState } from 'react';

export function useSSE<T>(url: string) {
  const [data, setData] = useState<T[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const eventSource = new EventSource(url);

    eventSource.onopen = () => setIsConnected(true);
    
    eventSource.onmessage = (event) => {
      try {
        const newData = JSON.parse(event.data);
        setData(prev => [...prev, newData]);
      } catch (e) {
        setError(e as Error);
      }
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      eventSource.close();
    };

    return () => eventSource.close();
  }, [url]);

  return { data, isConnected, error };
}
```

**Streaming Suggestions Component:**
```typescript
// components/AISuggestions.tsx
'use client';

import { useSSE } from '@/hooks/useSSE';
import { motion, AnimatePresence } from 'framer-motion';

interface Suggestion {
  type: 'text' | 'tool_result' | 'complete';
  content?: string;
  tool?: string;
  result?: any;
}

export function AISuggestions({ callId }: { callId: string }) {
  const { data: suggestions, isConnected } = useSSE<Suggestion>(
    `/api/stream/suggestions/${callId}`
  );

  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    // Animate text appearance
    const textChunks = suggestions.filter(s => s.type === 'text');
    const fullText = textChunks.map(s => s.content).join('');
    
    let currentIndex = displayedText.length;
    if (currentIndex < fullText.length) {
      const timer = setTimeout(() => {
        setDisplayedText(fullText.slice(0, currentIndex + 1));
      }, 20); // Typewriter effect
      
      return () => clearTimeout(timer);
    }
  }, [suggestions]);

  return (
    <div className="suggestions-panel">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xl">🤖</span>
        <h3 className="font-semibold">AI Assistant</h3>
        {isConnected && (
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
        )}
      </div>

      <AnimatePresence>
        {displayedText && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="suggestion-card"
          >
            <p className="text-gray-800">{displayedText}</p>
            <span className="typing-cursor">|</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tool results */}
      {suggestions
        .filter(s => s.type === 'tool_result')
        .map((s, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="tool-result"
          >
            <div className="font-medium">📊 {s.tool}</div>
            <pre className="text-sm">{JSON.stringify(s.result, null, 2)}</pre>
          </motion.div>
        ))}
    </div>
  );
}
```

---

### 8. Database Access Layer

**Repository Pattern:**
```python
from sqlalchemy.ext.asyncio import AsyncSession

class CustomerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def search(self, query: str) -> Optional[Customer]:
        """Search by name, email, or phone"""
        result = await self.session.execute(
            select(Customer).where(
                or_(
                    Customer.name.ilike(f"%{query}%"),
                    Customer.email.ilike(f"%{query}%"),
                    Customer.phone.ilike(f"%{query}%")
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_with_history(self, customer_id: int) -> dict:
        """Get customer with orders, tickets, and call history"""
        customer = await self.session.get(Customer, customer_id)
        
        orders = await self.session.execute(
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.order_date.desc())
            .limit(10)
        )
        
        tickets = await self.session.execute(
            select(Ticket)
            .where(Ticket.customer_id == customer_id)
            .order_by(Ticket.created_at.desc())
            .limit(5)
        )
        
        return {
            "customer": customer,
            "orders": orders.scalars().all(),
            "tickets": tickets.scalars().all()
        }
```

---

## Deployment Architecture

### Development
```
Docker Compose:
├── backend (FastAPI)
├── frontend (Next.js)
├── postgres (Database)
├── redis (Session cache)
└── coturn (STUN/TURN server)
```

### Production
```
Cloud Architecture:
├── CDN (Frontend)
├── Load Balancer
│   ├── API Server 1 (Fargate)
│   ├── API Server 2 (Fargate)
│   └── API Server N
├── RDS (PostgreSQL)
├── ElastiCache (Redis)
├── S3 (Call recordings)
└── Twilio (WebRTC infrastructure)
```

---

## Performance Considerations

### Latency Optimization
1. **Edge deployment** - Deploy close to users
2. **Connection pooling** - Reuse database connections
3. **Caching** - Redis for customer lookup
4. **Prefetching** - Load customer info on call start
5. **Batch transcription** - 3-5 second chunks

### Scalability
1. **Horizontal scaling** - Stateless API servers
2. **WebSocket sharding** - Route by call_id
3. **Queue-based processing** - SQS for async tasks
4. **Database read replicas** - Separate read/write
5. **CDN** - Static assets at edge

### Cost Optimization
1. **Deepgram vs Whisper** - Deepgram cheaper for streaming
2. **GPT-4 vs GPT-3.5** - Use 3.5 for simple suggestions
3. **Audio compression** - Opus at 24kbps
4. **Serverless** - Lambda for infrequent tasks
5. **Auto-scaling** - Scale down during off-hours

---

This architecture is production-ready and can scale to thousands of concurrent calls!

