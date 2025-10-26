# Exercise 10: Student Tasks Guide 🎯

## Overview

This guide breaks down the exercise into manageable tasks. Follow them sequentially, and you'll have a working real-time AI call assistant by the end!

---

## 📋 Pre-requisites

Before starting, ensure you have:

- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Docker & Docker Compose installed
- [ ] OpenAI API key (for Whisper + GPT-4)
- [ ] Code editor (VS Code recommended)
- [ ] Basic understanding of WebRTC concepts

---

## Phase 1: Setup & Infrastructure (15 min)

### Task 1.1: Initialize Project Structure

Create the basic folder structure:

```bash
cd exercise_10

# Backend
mkdir -p backend/app/api
mkdir -p backend/app/agents
mkdir -p backend/app/streaming
mkdir -p backend/tests

# Frontend
npx create-next-app@latest frontend --typescript --tailwind --app

# Data
mkdir -p data
mkdir -p docs

# Customer simulator
mkdir -p customer-sim
```

### Task 1.2: Set Up Docker Compose

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: callcenter
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://admin:password@postgres:5432/callcenter
      REDIS_URL: redis://redis:6379
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  postgres_data:
```

**Action:** Start services
```bash
docker-compose up -d postgres redis
```

**Checkpoint:** ✅ Postgres and Redis running on localhost

---

### Task 1.3: Create Database Schema

**File:** `backend/app/models.py`

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(50))
    account_number = Column(String(50), unique=True)
    tier = Column(String(20), default="standard")  # standard, gold, platinum
    status = Column(String(20), default="active")
    lifetime_value = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    calls = relationship("Call", back_populates="customer")
    orders = relationship("Order", back_populates="customer")
    tickets = relationship("Ticket", back_populates="customer")

class Call(Base):
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True)
    call_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    agent_name = Column(String(255))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    status = Column(String(20), default="active")  # active, completed, abandoned
    sentiment = Column(String(20), default="neutral")
    summary = Column(Text, nullable=True)
    recording_url = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="calls")
    transcripts = relationship("Transcript", back_populates="call")
    suggestions = relationship("AISuggestion", back_populates="call")

class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.call_id"))
    speaker = Column(String(20))  # customer, agent
    text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    confidence = Column(Float, default=1.0)
    
    call = relationship("Call", back_populates="transcripts")

class AISuggestion(Base):
    __tablename__ = "ai_suggestions"
    
    id = Column(Integer, primary_key=True)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.call_id"))
    suggestion_type = Column(String(50))  # tip, alert, action
    message = Column(Text)
    used = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    call = relationship("Call", back_populates="suggestions")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_number = Column(String(50), unique=True)
    product_name = Column(String(255))
    amount = Column(Float)
    status = Column(String(50))
    order_date = Column(DateTime)
    
    customer = relationship("Customer", back_populates="orders")

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    ticket_number = Column(String(50), unique=True)
    subject = Column(String(255))
    status = Column(String(50))
    priority = Column(String(20))
    created_at = Column(DateTime)
    resolved_at = Column(DateTime, nullable=True)
    
    customer = relationship("Customer", back_populates="tickets")
```

**File:** `backend/app/database.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:password@localhost:5432/callcenter")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

**Action:** Create tables
```bash
cd backend
python -m app.database
```

**Checkpoint:** ✅ Database tables created

---

### Task 1.4: Seed Fake Data

**File:** `data/seed_customers.py`

```python
import asyncio
from faker import Faker
from sqlalchemy import select
from backend.app.database import async_session, init_db
from backend.app.models import Customer, Order, Ticket
from datetime import datetime, timedelta
import random

fake = Faker()

async def seed_data():
    await init_db()
    
    async with async_session() as session:
        # Create 50 customers
        customers = []
        for i in range(50):
            customer = Customer(
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number(),
                account_number=f"ACC{str(i+1).zfill(5)}",
                tier=random.choice(["standard", "gold", "platinum"]),
                status=random.choice(["active", "active", "active", "inactive"]),
                lifetime_value=round(random.uniform(100, 10000), 2)
            )
            customers.append(customer)
        
        session.add_all(customers)
        await session.commit()
        
        # Create orders for each customer
        for customer in customers:
            num_orders = random.randint(1, 10)
            for j in range(num_orders):
                order = Order(
                    customer_id=customer.id,
                    order_number=f"ORD{fake.uuid4()[:8].upper()}",
                    product_name=fake.word().title() + " " + random.choice(["Pro", "Plus", "Premium", "Basic"]),
                    amount=round(random.uniform(10, 500), 2),
                    status=random.choice(["completed", "completed", "shipped", "pending"]),
                    order_date=datetime.now() - timedelta(days=random.randint(1, 365))
                )
                session.add(order)
        
        # Create tickets
        for customer in random.sample(customers, 30):
            num_tickets = random.randint(1, 3)
            for k in range(num_tickets):
                ticket = Ticket(
                    customer_id=customer.id,
                    ticket_number=f"TKT{str(random.randint(10000, 99999))}",
                    subject=random.choice([
                        "Billing inquiry",
                        "Technical support",
                        "Refund request",
                        "Product question",
                        "Account access"
                    ]),
                    status=random.choice(["open", "resolved", "resolved"]),
                    priority=random.choice(["low", "medium", "high"]),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 90))
                )
                session.add(ticket)
        
        await session.commit()
        print("✅ Seeded 50 customers with orders and tickets!")

if __name__ == "__main__":
    asyncio.run(seed_data())
```

**Action:** Run seeder
```bash
python data/seed_customers.py
```

**Checkpoint:** ✅ Database has 50 customers with orders/tickets

---

## Phase 2: WebRTC Audio Streaming (20 min)

### Task 2.1: Backend WebSocket Handler

**File:** `backend/app/api/websocket.py`

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import asyncio
import json

router = APIRouter()

# Active connections
active_connections: Dict[str, WebSocket] = {}
audio_queues: Dict[str, asyncio.Queue] = {}

@router.websocket("/ws/call/{call_id}")
async def websocket_call(websocket: WebSocket, call_id: str):
    await websocket.accept()
    active_connections[call_id] = websocket
    audio_queues[call_id] = asyncio.Queue()
    
    print(f"✅ WebSocket connected: {call_id}")
    
    try:
        while True:
            # Receive audio chunk or text message
            message = await websocket.receive()
            
            if "bytes" in message:
                # Audio data
                audio_chunk = message["bytes"]
                await audio_queues[call_id].put(audio_chunk)
                
            elif "text" in message:
                # Control message
                data = json.loads(message["text"])
                
                if data["type"] == "start_call":
                    await handle_call_start(call_id, data)
                elif data["type"] == "end_call":
                    await handle_call_end(call_id)
                    break
    
    except WebSocketDisconnect:
        print(f"❌ WebSocket disconnected: {call_id}")
    
    finally:
        # Cleanup
        if call_id in active_connections:
            del active_connections[call_id]
        if call_id in audio_queues:
            del audio_queues[call_id]

async def handle_call_start(call_id: str, data: dict):
    print(f"📞 Call started: {call_id}")
    # TODO: Create call record in database
    # TODO: Start transcription task

async def handle_call_end(call_id: str):
    print(f"📴 Call ended: {call_id}")
    # TODO: Update call record
    # TODO: Generate summary
```

**Checkpoint:** ✅ WebSocket endpoint ready

---

### Task 2.2: Frontend WebRTC Component

**File:** `frontend/src/lib/webrtc.ts`

```typescript
export class AudioStreamer {
  private mediaStream: MediaStream | null = null;
  private websocket: WebSocket | null = null;
  private audioContext: AudioContext | null = null;
  private processor: ScriptProcessorNode | null = null;

  async start(callId: string, wsUrl: string): Promise<void> {
    // Get microphone permission
    this.mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000,
      },
    });

    // Connect WebSocket
    this.websocket = new WebSocket(`${wsUrl}/ws/call/${callId}`);
    
    this.websocket.onopen = () => {
      console.log('✅ WebSocket connected');
      this.startStreaming();
    };

    this.websocket.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
    };
  }

  private startStreaming() {
    if (!this.mediaStream || !this.websocket) return;

    this.audioContext = new AudioContext({ sampleRate: 16000 });
    const source = this.audioContext.createMediaStreamSource(this.mediaStream);
    
    // Create processor for raw audio
    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
    
    this.processor.onaudioprocess = (event) => {
      if (this.websocket?.readyState === WebSocket.OPEN) {
        const audioData = event.inputBuffer.getChannelData(0);
        
        // Convert Float32Array to Int16Array
        const int16Array = new Int16Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
          int16Array[i] = Math.max(-32768, Math.min(32767, audioData[i] * 32768));
        }
        
        // Send to server
        this.websocket.send(int16Array.buffer);
      }
    };

    source.connect(this.processor);
    this.processor.connect(this.audioContext.destination);
  }

  stop() {
    this.processor?.disconnect();
    this.audioContext?.close();
    this.mediaStream?.getTracks().forEach(track => track.stop());
    this.websocket?.close();
  }

  getAudioLevel(): number {
    // Return current volume level for visualization
    return 0.5; // Placeholder
  }
}
```

**File:** `frontend/src/components/call/AudioStream.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { AudioStreamer } from '@/lib/webrtc';

interface Props {
  callId: string;
  onStreamReady?: () => void;
}

export function AudioStream({ callId, onStreamReady }: Props) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [streamer] = useState(() => new AudioStreamer());

  const startCall = async () => {
    try {
      await streamer.start(callId, 'ws://localhost:8000');
      setIsStreaming(true);
      onStreamReady?.();
      
      // Update audio level indicator
      const interval = setInterval(() => {
        setAudioLevel(streamer.getAudioLevel());
      }, 100);
      
      return () => clearInterval(interval);
    } catch (error) {
      console.error('Failed to start audio stream:', error);
    }
  };

  const endCall = () => {
    streamer.stop();
    setIsStreaming(false);
  };

  return (
    <div className="audio-stream-panel">
      <div className="flex items-center gap-4">
        {!isStreaming ? (
          <button
            onClick={startCall}
            className="btn btn-primary"
          >
            🎤 Start Call
          </button>
        ) : (
          <button
            onClick={endCall}
            className="btn btn-danger"
          >
            📞 End Call
          </button>
        )}
        
        {isStreaming && (
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-sm text-gray-600">Recording</span>
          </div>
        )}
      </div>
      
      {/* Audio level indicator */}
      {isStreaming && (
        <div className="mt-4">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 transition-all duration-100"
              style={{ width: `${audioLevel * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
```

**Checkpoint:** ✅ Audio streaming from browser to backend

---

## Phase 3: Speech-to-Text Integration (20 min)

### Task 3.1: Whisper Integration

**File:** `backend/app/agents/transcription.py`

```python
import openai
import asyncio
from typing import AsyncGenerator
import io
import wave

class TranscriptionEngine:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.buffer_size = 16000 * 5  # 5 seconds at 16kHz
    
    async def transcribe_stream(
        self, 
        call_id: str, 
        audio_queue: asyncio.Queue
    ) -> AsyncGenerator[dict, None]:
        """Transcribe audio chunks as they arrive"""
        
        buffer = bytearray()
        
        while True:
            try:
                # Get audio chunk
                chunk = await asyncio.wait_for(audio_queue.get(), timeout=30)
                buffer.extend(chunk)
                
                # Process when buffer is full
                if len(buffer) >= self.buffer_size:
                    audio_data = bytes(buffer)
                    buffer.clear()
                    
                    # Convert to WAV format
                    wav_buffer = self._to_wav(audio_data)
                    
                    # Transcribe
                    result = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=("audio.wav", wav_buffer, "audio/wav"),
                        language="en"
                    )
                    
                    yield {
                        "call_id": call_id,
                        "text": result.text,
                        "timestamp": asyncio.get_event_loop().time()
                    }
            
            except asyncio.TimeoutError:
                # No audio received, end stream
                break
            except Exception as e:
                print(f"Transcription error: {e}")
                continue
    
    def _to_wav(self, audio_data: bytes) -> io.BytesIO:
        """Convert raw PCM to WAV format"""
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_data)
        wav_buffer.seek(0)
        return wav_buffer
```

**Checkpoint:** ✅ Audio transcription working

---

### Task 3.2: Stream Transcription to Frontend

**File:** `backend/app/api/streaming.py`

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import asyncio

router = APIRouter()

# Store transcription streams
transcription_streams: dict = {}

@router.get("/api/stream/transcript/{call_id}")
async def stream_transcript(call_id: str):
    async def generate():
        queue = asyncio.Queue()
        transcription_streams[call_id] = queue
        
        try:
            while True:
                # Wait for transcript
                transcript = await queue.get()
                
                # Send as SSE
                data = json.dumps(transcript)
                yield f"data: {data}\n\n"
        
        finally:
            del transcription_streams[call_id]
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

**Checkpoint:** ✅ Transcripts streaming to frontend

---

## Phase 4: AI Assistant Integration (25 min)

### Task 4.1: Context Manager

**File:** `backend/app/agents/context_manager.py`

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from datetime import datetime

@dataclass
class TranscriptSegment:
    speaker: str  # "customer" or "agent"
    text: str
    timestamp: datetime

@dataclass
class ConversationState:
    call_id: str
    customer_id: Optional[int] = None
    customer_info: Optional[dict] = None
    transcript: List[TranscriptSegment] = field(default_factory=list)
    topics: Set[str] = field(default_factory=set)
    entities: Dict[str, any] = field(default_factory=dict)
    sentiment: str = "neutral"
    
    def add_transcript(self, speaker: str, text: str):
        """Add new transcript segment"""
        self.transcript.append(TranscriptSegment(
            speaker=speaker,
            text=text,
            timestamp=datetime.now()
        ))
    
    def get_context_for_ai(self) -> str:
        """Build prompt context"""
        parts = []
        
        if self.customer_info:
            parts.append(f"**Customer:** {self.customer_info['name']}")
            parts.append(f"**Tier:** {self.customer_info['tier']}")
            parts.append(f"**Account:** {self.customer_info['account_number']}")
            parts.append("")
        
        parts.append("**Recent Conversation:**")
        for seg in self.transcript[-10:]:
            parts.append(f"{seg.speaker.title()}: {seg.text}")
        
        return "\n".join(parts)

# Global state manager
conversation_states: Dict[str, ConversationState] = {}

def get_state(call_id: str) -> ConversationState:
    if call_id not in conversation_states:
        conversation_states[call_id] = ConversationState(call_id=call_id)
    return conversation_states[call_id]
```

**Checkpoint:** ✅ Conversation state tracked

---

### Task 4.2: Streaming AI Assistant

**File:** `backend/app/agents/assistant.py`

```python
import openai
import json
from typing import AsyncGenerator

class StreamingAssistant:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.system_prompt = """You are an AI assistant helping a call center agent in real-time.

Analyze the conversation and provide:
1. **Immediate suggestions** - What the agent should say next
2. **Customer insights** - Important facts about the customer
3. **Policy guidance** - Relevant company policies
4. **Risk alerts** - If customer is frustrated or at risk of churning

Respond in short, actionable bullet points. Be concise and helpful."""
    
    async def stream_suggestions(
        self,
        context: str
    ) -> AsyncGenerator[dict, None]:
        """Generate streaming suggestions"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context}
        ]
        
        stream = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            stream=True,
            temperature=0.7
        )
        
        async for chunk in stream:
            delta = chunk.choices[0].delta
            
            if delta.content:
                yield {
                    "type": "text",
                    "content": delta.content
                }
            
            if chunk.choices[0].finish_reason:
                yield {"type": "complete"}
```

**Checkpoint:** ✅ AI suggestions generating

---

*Continue with remaining tasks...*

## Summary Checklist

At the end of all phases, you should have:

- [ ] WebRTC audio streaming working
- [ ] Live transcription appearing in UI
- [ ] AI suggestions streaming word-by-word
- [ ] Customer info panel loading automatically
- [ ] Database lookups triggered by AI
- [ ] Clean, responsive UI
- [ ] Proper error handling
- [ ] Code documented

---

Good luck! 🚀

