# Exercise 10: Real-Time AI Call Center Assistant 🎧

**Class 7: Streaming UI & Real-Time Agentic Systems**

---

## 🎯 Overview

Build a **real-time call center assistance system** where an AI agent listens to live customer conversations via WebRTC and provides **streaming, contextual suggestions** to human agents in real-time. The system combines:

- **WebRTC audio streaming** for live conversation capture
- **Real-time speech-to-text** transcription
- **Streaming AI responses** with live suggestions
- **Database lookups** for customer history and context
- **Live UI updates** showing conversation flow and AI hints

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Call Center Agent UI                       │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │  Live Audio    │  │  Transcription   │  │  AI Suggestions │ │
│  │  Waveform      │  │  (Streaming)     │  │  (Streaming)    │ │
│  └────────────────┘  └──────────────────┘  └─────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         Customer Info Panel (DB Lookup)                    │ │
│  │  Name: John Doe | Account: #12345 | Tier: Gold             │ │
│  │  Last Contact: 2025-10-15 | Issue: Billing                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↕ WebRTC + WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                         Backend Server                          │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │  WebRTC      │→ │  STT Engine  │→ │  AI Agent Router   │   │
│  │  Handler     │  │  (Whisper/   │  │  (Streaming LLM)   │   │
│  │              │  │   Deepgram)  │  └────────────────────┘   │
│  └──────────────┘  └──────────────┘            ↓               │
│                                      ┌────────────────────┐     │
│                                      │  Context Manager   │     │
│                                      │  - Customer DB     │     │
│                                      │  - Conversation    │     │
│                                      │  - Knowledge Base  │     │
│                                      └────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↕ WebRTC
┌─────────────────────────────────────────────────────────────────┐
│                      Customer Simulator                         │
│             (Test UI to simulate customer calls)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎓 Learning Objectives

By completing this exercise, students will:

1. **Implement real-time streaming UI** with Server-Sent Events (SSE) or WebSockets
2. **Handle WebRTC audio streams** for live conversation capture
3. **Build streaming AI pipelines** with incremental LLM responses
4. **Integrate speech-to-text** (STT) for live transcription
5. **Manage stateful conversations** with context preservation
6. **Implement database lookups** triggered by conversation events
7. **Handle concurrent streams** (audio + transcription + AI + UI updates)
8. **Apply real-time agent patterns** (reactive, context-aware, proactive)

---

## 🛠️ Core Features

### 1. **WebRTC Audio Call** 🎤
- Customer-to-agent voice connection
- Browser-based audio capture
- Real-time audio streaming to backend
- Audio level indicators (waveform visualization)

### 2. **Live Transcription** 📝
- Streaming speech-to-text (Whisper API or Deepgram)
- Real-time display of customer words
- Speaker diarization (customer vs. agent)
- Timestamp alignment

### 3. **Streaming AI Assistant** 🤖
- **Real-time suggestions** as customer speaks:
  - "Customer mentions billing → Suggest: Check payment history"
  - "Customer sounds frustrated → Suggest: Offer escalation"
  - "Customer asks about refund → Suggest: Review refund policy"
- **Streaming responses** (word-by-word display)
- **Contextual hints** based on conversation history
- **Proactive alerts** (policy violations, upsell opportunities)

### 4. **Customer Context Panel** 📊
- **Auto-lookup** customer info when call starts
- Display:
  - Customer profile (name, account, tier)
  - Purchase history
  - Previous tickets/issues
  - Preferences and notes
- **Live updates** as conversation reveals context

### 5. **Conversation Memory** 🧠
- Maintain conversation state across turns
- Track topics discussed
- Remember commitments made
- Store call summary for future reference

### 6. **Agent Actions** ⚡
- Quick response templates
- Mark suggestions as used/ignored
- Flag important moments
- End-of-call summary generation

---

## 📂 Project Structure

```
exercise_10/
├── README.md                          # This file
├── ARCHITECTURE.md                    # Detailed architecture guide
├── docker-compose.yml                 # Local dev environment
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── config.py                  # Configuration
│   │   ├── database.py                # DB connection
│   │   ├── models.py                  # SQLAlchemy models
│   │   │
│   │   ├── api/
│   │   │   ├── websocket.py           # WebSocket handler
│   │   │   ├── webrtc.py              # WebRTC signaling
│   │   │   ├── calls.py               # Call management
│   │   │   └── customers.py           # Customer lookup
│   │   │
│   │   ├── agents/
│   │   │   ├── transcription.py       # STT integration
│   │   │   ├── assistant.py           # AI suggestion agent
│   │   │   ├── context_manager.py     # Conversation state
│   │   │   └── knowledge_base.py      # Policy/product lookup
│   │   │
│   │   └── streaming/
│   │       ├── sse.py                 # Server-Sent Events
│   │       └── stream_processor.py    # Stream coordination
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                          # Agent UI (Next.js)
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx               # Dashboard
│   │   │   ├── call/[id]/page.tsx     # Active call interface
│   │   │   └── history/page.tsx       # Call history
│   │   │
│   │   ├── components/
│   │   │   ├── call/
│   │   │   │   ├── AudioStream.tsx    # WebRTC audio
│   │   │   │   ├── Transcription.tsx  # Live transcript
│   │   │   │   ├── AISuggestions.tsx  # Streaming hints
│   │   │   │   └── Waveform.tsx       # Audio visualizer
│   │   │   │
│   │   │   ├── customer/
│   │   │   │   ├── InfoPanel.tsx      # Customer details
│   │   │   │   └── HistoryTimeline.tsx
│   │   │   │
│   │   │   └── streaming/
│   │   │       ├── SSEProvider.tsx    # SSE context
│   │   │       └── StreamText.tsx     # Animated text
│   │   │
│   │   └── lib/
│   │       ├── webrtc.ts              # WebRTC utilities
│   │       ├── sse.ts                 # SSE client
│   │       └── api.ts                 # API client
│   │
│   ├── package.json
│   ├── Dockerfile
│   └── next.config.ts
│
├── customer-sim/                      # Customer Simulator UI
│   ├── index.html                     # Simple test interface
│   └── sim.js                         # WebRTC test caller
│
├── data/
│   ├── seed_customers.py              # Generate fake customers
│   ├── seed_products.py               # Products/services data
│   └── seed_policies.py               # Call center policies
│
└── docs/
    ├── SETUP.md                       # Installation guide
    ├── WEBRTC_GUIDE.md                # WebRTC implementation
    ├── STREAMING_UI.md                # Streaming patterns
    └── STUDENT_TASKS.md               # Step-by-step exercises
```

---

## 🔑 Key Technologies

### Backend
- **FastAPI** - Async API server
- **WebSockets** - Bidirectional real-time communication
- **aiortc** or **Twilio** - WebRTC handling
- **OpenAI Whisper API** or **Deepgram** - Speech-to-text
- **OpenAI GPT-4** - Streaming AI assistance (with function calling)
- **PostgreSQL** - Customer/call database
- **Redis** - Session state management

### Frontend
- **Next.js 15** - React framework
- **WebRTC API** - Browser audio capture
- **Server-Sent Events (SSE)** - Streaming UI updates
- **TanStack Query** - Data fetching
- **Framer Motion** - Smooth animations
- **Tailwind CSS** - Styling

### Streaming Patterns
1. **SSE (Server-Sent Events)** - One-way server→client streaming
2. **WebSockets** - Bidirectional streaming
3. **HTTP Streaming** - Chunked transfer encoding
4. **WebRTC Data Channels** - P2P streaming

---

## 🎯 Student Tasks (90-minute lab)

### Phase 1: Basic Setup (15 min)
1. Set up project structure
2. Run Docker services (Postgres, Redis)
3. Seed fake customer database
4. Test basic WebRTC connection

### Phase 2: Audio Streaming (20 min)
5. Implement WebRTC audio capture in frontend
6. Send audio chunks to backend via WebSocket
7. Display audio waveform visualization
8. Add mute/unmute controls

### Phase 3: Transcription (20 min)
9. Integrate Whisper API or Deepgram
10. Stream transcription results to frontend via SSE
11. Display live transcript with speaker labels
12. Handle transcription errors gracefully

### Phase 4: AI Assistant (25 min)
13. Build streaming AI agent with OpenAI
14. Implement context manager (conversation history)
15. Add customer database lookup (triggered by name mention)
16. Stream AI suggestions to frontend
17. Display suggestions with animations

### Phase 5: Polish & Demo (10 min)
18. Add customer info panel
19. Implement quick action buttons
20. Generate end-of-call summary
21. Demo full flow with team

---

## 🧪 Example User Flow

### Scenario: Customer calls about billing issue

```
┌─────────────────────────────────────────────────────────────────┐
│ Call Center Agent View                                          │
├─────────────────────────────────────────────────────────────────┤
│ [●] Recording   [🎤] Mute   [📞] End Call                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 📝 LIVE TRANSCRIPT                                              │
│ ────────────────────────────────────────────────────────────    │
│ [10:23:15] Customer: "Hi, I'm John Doe, and I have a question  │
│                       about my last bill..."                     │
│ [10:23:22] Agent:    "Hi John! Let me pull up your account."   │
│                                                                  │
│ 🤖 AI SUGGESTIONS (streaming...)                                │
│ ────────────────────────────────────────────────────────────    │
│ ✨ Customer identified: John Doe (Account #12345)               │
│    → Pulling account details...                                 │
│                                                                  │
│ 💡 Suggestion: "I see you were billed $129.99 on Oct 15.       │
│    This includes your premium plan ($99) + overage charges      │
│    ($30.99). Would you like me to explain the charges?"         │
│                                                                  │
│ ⚠️  Alert: Customer is Gold tier - prioritize satisfaction      │
│                                                                  │
│ 📊 CUSTOMER INFO                                                │
│ ────────────────────────────────────────────────────────────    │
│ Name: John Doe                  Tier: 🥇 Gold                   │
│ Account: #12345                 Since: Jan 2023                 │
│ Last Contact: Oct 10, 2025      Issue: Feature Request          │
│ Lifetime Value: $2,340          Status: Active                  │
│                                                                  │
│ Recent Orders:                                                   │
│ • Premium Plan Renewal - $99.00 (Oct 1)                         │
│ • Data Overage - $30.99 (Oct 15) ← Related to current call      │
│                                                                  │
│ 🏷️ Quick Actions:                                               │
│ [Apply 10% Discount] [Waive Fee] [Escalate] [Schedule Callback]│
└─────────────────────────────────────────────────────────────────┘
```

**What happens behind the scenes:**

1. **Audio flows** → WebRTC → Backend
2. **STT processes** → Whisper API → "Hi, I'm John Doe..."
3. **AI detects name** → Triggers DB lookup → Loads customer #12345
4. **AI analyzes** → Context (billing issue) + History (previous complaints) + Tier (Gold)
5. **AI generates** → Streaming suggestion appears word-by-word
6. **Agent sees** → Real-time hint, customer info, and suggested actions
7. **Agent responds** → Confidently with full context

---

## 🎨 UI Components Breakdown

### 1. **AudioStream Component** (WebRTC)
```typescript
// Real-time audio capture & streaming
- Microphone permission
- Audio level visualization
- Mute/unmute toggle
- Connection status indicator
```

### 2. **Transcription Component** (SSE)
```typescript
// Live speech-to-text display
- Streaming text append
- Speaker labels (Customer/Agent)
- Auto-scroll to latest
- Timestamps
- Search/highlight keywords
```

### 3. **AISuggestions Component** (SSE)
```typescript
// Streaming AI hints
- Animated text appearance (typewriter effect)
- Suggestion cards with context
- Action buttons (Use, Dismiss)
- Priority indicators (🔥 urgent, 💡 tip, ⚠️ warning)
```

### 4. **CustomerInfoPanel Component**
```typescript
// Database-driven customer context
- Profile summary
- Purchase history
- Previous tickets
- Preferences/notes
- Quick facts
```

### 5. **Waveform Component**
```typescript
// Audio visualization
- Real-time frequency bars
- Volume indicator
- Silence detection
```

---

## 🧠 AI Agent Capabilities

### **Assistant Agent** (Streaming)
**Responsibilities:**
- Listen to live transcription
- Analyze customer intent
- Generate contextual suggestions
- Provide policy guidance
- Detect emotions/sentiment
- Flag upsell opportunities

**Example Prompts:**
```python
SYSTEM_PROMPT = """
You are an AI assistant helping a call center agent in real-time.
Analyze the customer conversation and provide:
1. Immediate suggestions (what to say next)
2. Relevant customer information (from context)
3. Policy guidance (return policy, SLA, etc.)
4. Risk alerts (angry customer, churn risk)
5. Upsell opportunities (relevant products)

Respond in short, actionable suggestions that appear in real-time.
Format: JSON with type (suggestion|alert|info) and message.
"""
```

**Function Calling:**
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "lookup_customer",
            "description": "Search customer by name, email, or phone",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "search_type": {"enum": ["name", "email", "phone"]}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Check order status by order ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_return_policy",
            "description": "Get return policy for a product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"}
                }
            }
        }
    }
]
```

---

## 🔄 Streaming Patterns Explained

### **Pattern 1: Server-Sent Events (SSE)**
**Use for:** Transcription, AI suggestions (one-way server→client)

```python
# Backend (FastAPI)
@app.get("/api/stream/suggestions/{call_id}")
async def stream_suggestions(call_id: str):
    async def generate():
        async for chunk in ai_agent.stream_suggestions(call_id):
            yield f"data: {json.dumps(chunk)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

```typescript
// Frontend (React)
const eventSource = new EventSource(`/api/stream/suggestions/${callId}`);
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    setSuggestions(prev => [...prev, data]);
};
```

### **Pattern 2: WebSocket (Bidirectional)**
**Use for:** Audio streaming, real-time commands

```python
# Backend
@app.websocket("/ws/call/{call_id}")
async def websocket_call(websocket: WebSocket, call_id: str):
    await websocket.accept()
    try:
        while True:
            audio_chunk = await websocket.receive_bytes()
            transcription = await stt_engine.transcribe(audio_chunk)
            await websocket.send_json({"type": "transcript", "text": transcription})
    except WebSocketDisconnect:
        pass
```

```typescript
// Frontend
const ws = new WebSocket(`ws://localhost:8000/ws/call/${callId}`);
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'transcript') {
        setTranscript(prev => prev + data.text);
    }
};
```

### **Pattern 3: WebRTC (Peer-to-Peer)**
**Use for:** High-quality audio streaming

```javascript
// Frontend - Customer side
const pc = new RTCPeerConnection(config);
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
stream.getTracks().forEach(track => pc.addTrack(track, stream));

// Create offer
const offer = await pc.createOffer();
await pc.setLocalDescription(offer);

// Send offer to signaling server
await fetch('/api/webrtc/offer', {
    method: 'POST',
    body: JSON.stringify({ offer, callId })
});
```

---

## 📊 Database Schema

```sql
-- Customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    account_number VARCHAR(50) UNIQUE,
    tier VARCHAR(20) DEFAULT 'standard', -- standard, gold, platinum
    status VARCHAR(20) DEFAULT 'active',
    lifetime_value DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Calls table
CREATE TABLE calls (
    id SERIAL PRIMARY KEY,
    call_id UUID UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    agent_name VARCHAR(255),
    start_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    status VARCHAR(20), -- active, completed, abandoned
    sentiment VARCHAR(20), -- positive, neutral, negative
    summary TEXT,
    recording_url TEXT
);

-- Transcripts table
CREATE TABLE transcripts (
    id SERIAL PRIMARY KEY,
    call_id UUID REFERENCES calls(call_id),
    speaker VARCHAR(20), -- customer, agent
    text TEXT,
    timestamp TIMESTAMP,
    confidence FLOAT
);

-- AI Suggestions table
CREATE TABLE ai_suggestions (
    id SERIAL PRIMARY KEY,
    call_id UUID REFERENCES calls(call_id),
    suggestion_type VARCHAR(50), -- tip, alert, action
    message TEXT,
    used BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_number VARCHAR(50) UNIQUE,
    product_name VARCHAR(255),
    amount DECIMAL(10, 2),
    status VARCHAR(50),
    order_date TIMESTAMP
);

-- Tickets table
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    ticket_number VARCHAR(50) UNIQUE,
    subject VARCHAR(255),
    status VARCHAR(50),
    priority VARCHAR(20),
    created_at TIMESTAMP,
    resolved_at TIMESTAMP
);
```

---

## 🎯 Evaluation Criteria

### **Functionality (40%)**
- ✅ WebRTC audio connection works
- ✅ Live transcription appears in real-time
- ✅ AI suggestions stream word-by-word
- ✅ Customer info loads automatically
- ✅ Conversation state maintained

### **Streaming UI (30%)**
- ✅ SSE implementation correct
- ✅ No UI freezing during streams
- ✅ Smooth animations
- ✅ Proper error handling
- ✅ Connection recovery

### **AI Integration (20%)**
- ✅ Context-aware suggestions
- ✅ Timely database lookups
- ✅ Function calling works
- ✅ Relevant recommendations

### **Code Quality (10%)**
- ✅ Clean separation of concerns
- ✅ Proper typing (TypeScript/Python)
- ✅ Error boundaries
- ✅ Resource cleanup

---

## 🚀 Bonus Challenges

### **Advanced Features:**
1. **Multi-language support** - Auto-detect customer language, translate suggestions
2. **Emotion detection** - Analyze voice tone, flag angry customers
3. **Smart routing** - Route high-value customers to senior agents
4. **Call analytics dashboard** - Real-time metrics, sentiment trends
5. **Offline mode** - Queue suggestions when connection drops
6. **Voice commands** - Agent can control UI with voice
7. **Co-browsing** - Share screen with customer during call
8. **Auto-summarization** - Generate call summary with action items

### **Performance Optimizations:**
1. **Audio compression** - Opus codec for lower bandwidth
2. **Transcription batching** - Buffer 3-5 seconds before sending
3. **Suggestion debouncing** - Don't spam agent with suggestions
4. **WebSocket pooling** - Reuse connections
5. **Edge caching** - CDN for static assets

---

## 📚 Learning Resources

### **WebRTC**
- [WebRTC.org Official Guide](https://webrtc.org/)
- [MDN WebRTC API](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)
- [Simple Peer (library)](https://github.com/feross/simple-peer)

### **Streaming UI**
- [Server-Sent Events Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [Vercel AI SDK](https://sdk.vercel.ai/docs) - Streaming helpers
- [React Suspense for Streaming](https://react.dev/reference/react/Suspense)

### **Speech-to-Text**
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [Deepgram Streaming API](https://developers.deepgram.com/)
- [AssemblyAI Real-Time](https://www.assemblyai.com/docs/audio-intelligence)

### **AI Agents**
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [LangChain Streaming](https://python.langchain.com/docs/expression_language/streaming)

---

## 🎓 Pedagogical Notes (for Instructors)

### **Why this exercise?**
1. **Real-world relevance** - Call centers are ubiquitous, students see immediate value
2. **Multiple streaming patterns** - Audio, text, AI all streaming simultaneously
3. **Complexity** - Requires coordinating many moving parts (great for debugging skills)
4. **Impressive demo** - Visually engaging, easy to show parents/employers
5. **Career relevant** - Many companies building similar systems (customer support, sales)

### **Common student struggles:**
1. **WebRTC setup** - Signaling server confusion → Provide working template
2. **Audio permissions** - Browser blocks mic → Add clear UX prompts
3. **Stream coordination** - Multiple SSE connections → Use React Context
4. **Latency** - Suggestions too slow → Optimize prompt, use streaming
5. **State management** - Lost messages → Implement message queue

### **Teaching tips:**
1. **Start simple** - Get audio working first, add AI later
2. **Provide scaffolding** - Pre-built WebRTC and SSE helpers
3. **Live demo** - Show working version before lab
4. **Pair programming** - One student handles backend, one frontend
5. **Celebrate progress** - Even basic transcription is impressive!

### **Time allocation:**
- 10 min: Lecture on streaming patterns + WebRTC basics
- 10 min: Live demo of finished product
- 60 min: Hands-on lab (guided tasks)
- 10 min: Team demos + Q&A

---

## 🎬 Demo Script

**Instructor demonstrates:**

1. **Open customer simulator** → Start fake call
2. **Customer speaks:** "Hi, I'm Sarah Johnson, I need help with order #78901"
3. **Show agent UI:**
   - Audio waveform animates
   - Transcription appears word-by-word
   - AI detects name → Customer panel populates instantly
   - AI suggestion streams in: "I found Sarah's order #78901. It shipped yesterday via FedEx. ETA: Oct 23."
4. **Agent responds:** Uses suggestion, customer happy
5. **Show database** → Prove data was looked up in real-time
6. **End call** → Show auto-generated summary

**Students react:** "Wow! 🤯"

---

## 📦 Deliverables

Students submit:

1. **GitHub repository** with:
   - Complete source code
   - Docker Compose setup
   - README with setup instructions
   - `.env.example` with required keys

2. **2-minute demo video** showing:
   - Starting a call
   - Live transcription working
   - AI suggestions appearing
   - Customer info loading
   - Call summary generation

3. **Written reflection** (1 page):
   - What streaming pattern did you use and why?
   - What was the hardest part?
   - How would you scale this to 1000 concurrent calls?
   - What's one feature you'd add next?

---

## 🏆 Success Metrics

A great implementation should:

- ✅ **Low latency** - Suggestions appear within 2-3 seconds of customer speaking
- ✅ **High accuracy** - Transcription >90% accurate
- ✅ **Smooth UX** - No janky animations, clean transitions
- ✅ **Reliable** - Handles network hiccups gracefully
- ✅ **Contextual** - AI suggestions actually help the agent
- ✅ **Scalable** - Architecture supports multiple concurrent calls

---

## 🎉 Conclusion

This exercise combines cutting-edge technologies (WebRTC, streaming AI, real-time UI) in a practical, impressive demo. Students gain hands-on experience with patterns they'll use in production systems at top tech companies.

**Key takeaway:** Real-time agentic systems require careful coordination of multiple streaming data sources, but when done right, they create magical user experiences.

Good luck! 🚀

---

**Questions?** Reach out to the instructor or check `/docs` folder for detailed guides.

