# 📚 Exercise 10: Student Task Plan
## Real-Time AI Call Center Assistant

---

## 🎯 Overview

Students will build upon the provided scaffold to create a **production-grade AI call center assistant** with real-time audio transcription, AI-powered agent suggestions, and customer context retrieval.

**What's Already Built:**
- ✅ Backend API (FastAPI) with WebSocket support
- ✅ Frontend UI (Next.js) for agent and customer
- ✅ Agent-customer matching system
- ✅ Text chat functionality
- ✅ Audio capture and streaming infrastructure
- ✅ Audio level visualization
- ✅ Connection management

**What Students Will Build:**
- 🎯 Real-time speech-to-text transcription
- 🎯 AI agent suggestions based on conversation
- 🎯 Customer information retrieval
- 🎯 Session management and replay
- 🎯 Production optimizations

---

## 📊 Task Levels

### **Level 1: Basic (Core Features) - 4-6 hours**
Essential features that make the system functional.

### **Level 2: Intermediate (Enhanced Features) - 8-10 hours**
Adds polish and production-ready features.

### **Level 3: Advanced (Production Grade) - 12-15 hours**
Full production system with optimizations and advanced features.

---

## 🟢 **LEVEL 1: BASIC TASKS (Must Complete)**

### **Task 1.1: Integrate OpenAI Whisper for Transcription** ⭐⭐⭐
**Difficulty:** Medium  
**Time:** 2-3 hours  
**Priority:** CRITICAL

**Objective:**
Convert audio chunks to text in real-time using OpenAI Whisper API.

**Current State:**
- Audio chunks are captured and sent to backend
- Backend receives chunks but doesn't transcribe them

**What to Implement:**

#### Backend (`backend/app/api/whisper_service.py`):
```python
import openai
from fastapi import HTTPException
import io

class WhisperService:
    def __init__(self, api_key: str):
        openai.api_key = api_key
    
    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio using OpenAI Whisper API
        
        Args:
            audio_bytes: Audio data in WebM format
            
        Returns:
            Transcribed text
        """
        try:
            # Convert audio bytes to file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.webm"
            
            # Call Whisper API
            response = await openai.Audio.atranscribe(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
            
            return response.get("text", "")
            
        except Exception as e:
            print(f"Whisper error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
```

#### Update WebSocket handler (`backend/app/api/websocket.py`):
```python
# Add at top
from .whisper_service import WhisperService
whisper_service = WhisperService(os.getenv("OPENAI_API_KEY"))

# In websocket handler, when receiving audio:
if "bytes" in data:
    audio_chunk = data["bytes"]
    
    # Transcribe audio
    transcript = await whisper_service.transcribe_audio(audio_chunk)
    
    if transcript:
        # Send transcript to sender
        await websocket.send_json({
            "type": "transcript",
            "speaker": "customer",  # or "agent" based on who sent it
            "text": transcript,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Route transcript to partner
        if partner_call_id and partner_call_id in active_connections:
            await active_connections[partner_call_id].send_json({
                "type": "transcript",
                "speaker": "customer",
                "text": transcript,
                "timestamp": datetime.utcnow().isoformat()
            })
```

**Success Criteria:**
- [ ] Audio chunks are transcribed to text
- [ ] Transcripts appear in chat within 2 seconds
- [ ] Both agent and customer see transcripts
- [ ] Handles errors gracefully (API failures, invalid audio)

**Testing:**
1. Start call between agent and customer
2. Enable voice on customer side
3. Speak into microphone
4. Verify text appears in chat
5. Check agent sees the transcription

---

### **Task 1.2: Implement Basic AI Suggestions** ⭐⭐
**Difficulty:** Medium  
**Time:** 2-3 hours  
**Priority:** HIGH

**Objective:**
Generate contextual suggestions for agents based on customer messages.

**What to Implement:**

#### Create AI Service (`backend/app/api/ai_service.py`):
```python
import openai
from typing import List, Dict

class AIAssistantService:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.conversation_history: Dict[str, List[Dict]] = {}
    
    async def generate_suggestion(
        self, 
        call_id: str, 
        customer_message: str,
        conversation_context: List[Dict] = None
    ) -> Dict:
        """
        Generate agent suggestion based on customer message
        
        Returns:
            {
                "suggestion": "Suggest offering a refund",
                "reasoning": "Customer is frustrated about delivery",
                "action": "offer_refund",
                "confidence": 0.85
            }
        """
        # Build conversation history
        if call_id not in self.conversation_history:
            self.conversation_history[call_id] = []
        
        self.conversation_history[call_id].append({
            "role": "user",
            "content": customer_message
        })
        
        # Create prompt
        system_prompt = """You are an AI assistant helping call center agents.
        Analyze the customer's message and provide:
        1. A specific suggestion for what the agent should do
        2. Brief reasoning
        3. Action type (ask_question, offer_solution, escalate, offer_refund, etc.)
        4. Confidence score (0-1)
        
        Respond in JSON format."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            *self.conversation_history[call_id][-5:]  # Last 5 messages
        ]
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )
            
            suggestion_text = response.choices[0].message.content
            
            # Parse JSON response or format nicely
            return {
                "suggestion": suggestion_text,
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": 0.8
            }
            
        except Exception as e:
            print(f"AI suggestion error: {e}")
            return {
                "suggestion": "Listen carefully and ask clarifying questions",
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": 0.5
            }
```

#### Update WebSocket to generate suggestions:
```python
# When customer message arrives
if message["type"] == "transcript" and message.get("speaker") == "customer":
    # Generate AI suggestion for agent
    suggestion = await ai_service.generate_suggestion(
        call_id=call_id,
        customer_message=message["text"]
    )
    
    # Send suggestion only to agent
    if partner_call_id and partner_call_id in active_connections:
        await active_connections[partner_call_id].send_json({
            "type": "ai_suggestion",
            "suggestion": suggestion["suggestion"],
            "confidence": suggestion["confidence"],
            "timestamp": suggestion["timestamp"]
        })
```

#### Frontend - Display suggestions (agent page):
```typescript
// In agent chat page, handle ai_suggestion messages
if (data.type === 'ai_suggestion') {
  setAiSuggestions(prev => [...prev, {
    text: data.suggestion,
    confidence: data.confidence,
    timestamp: data.timestamp
  }]);
}
```

**Success Criteria:**
- [ ] AI suggestions appear for agents within 3 seconds of customer message
- [ ] Suggestions are contextually relevant
- [ ] Suggestions include confidence scores
- [ ] Only agents see suggestions (not customers)

---

### **Task 1.3: Add Customer Information Lookup** ⭐⭐
**Difficulty:** Easy-Medium  
**Time:** 1-2 hours  
**Priority:** MEDIUM

**Objective:**
Retrieve and display customer information when a call starts.

**What to Implement:**

#### Backend - Customer lookup endpoint:
```python
# backend/app/api/customers.py - already exists, enhance it

@router.get("/{customer_id}")
async def get_customer_details(customer_id: str, db: AsyncSession = Depends(get_db)):
    """Get full customer details including orders and tickets"""
    
    # For now, return mock data
    # Students can connect to real database later
    return {
        "customer_id": customer_id,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1-555-0123",
        "account_status": "active",
        "lifetime_value": 1250.00,
        "recent_orders": [
            {
                "order_id": "ORD-12345",
                "date": "2025-10-15",
                "status": "delivered",
                "total": 99.99
            }
        ],
        "open_tickets": [
            {
                "ticket_id": "TKT-789",
                "subject": "Delivery delay",
                "priority": "medium",
                "created": "2025-10-20"
            }
        ]
    }
```

#### Frontend - Fetch and display customer info:
```typescript
// In agent calls page, when call starts:
useEffect(() => {
  if (inCall && customerName) {
    // Fetch customer info
    axios.get(`/api/customers/search?query=${customerName}`)
      .then(res => {
        if (res.data.length > 0) {
          setCustomerInfo(res.data[0]);
        }
      });
  }
}, [inCall, customerName]);

// Display in sidebar
<div className="bg-white rounded-lg shadow p-4">
  <h3 className="font-semibold mb-2">Customer Info</h3>
  {customerInfo ? (
    <>
      <p><strong>Name:</strong> {customerInfo.name}</p>
      <p><strong>Email:</strong> {customerInfo.email}</p>
      <p><strong>Status:</strong> {customerInfo.account_status}</p>
      <p><strong>LTV:</strong> ${customerInfo.lifetime_value}</p>
      
      <h4 className="font-semibold mt-4 mb-2">Recent Orders</h4>
      {customerInfo.recent_orders.map(order => (
        <div key={order.order_id} className="text-sm">
          {order.order_id} - ${order.total}
        </div>
      ))}
    </>
  ) : (
    <p className="text-gray-500">No customer data</p>
  )}
</div>
```

**Success Criteria:**
- [ ] Customer info appears when call starts
- [ ] Shows name, email, phone, account status
- [ ] Displays recent orders and open tickets
- [ ] Updates in real-time

---

## 🟡 **LEVEL 2: INTERMEDIATE TASKS (Should Complete)**

### **Task 2.1: Implement Session Recording** ⭐⭐⭐
**Difficulty:** Medium  
**Time:** 2-3 hours  
**Priority:** HIGH

**Objective:**
Record all call transcripts and enable replay functionality.

**What to Implement:**

#### Create session storage:
```python
# backend/app/api/sessions.py
from sqlalchemy.orm import Session
from datetime import datetime
import json

class SessionManager:
    def __init__(self):
        self.sessions = {}  # In production, use database
    
    def create_session(self, call_id: str, agent_name: str, customer_name: str):
        self.sessions[call_id] = {
            "call_id": call_id,
            "agent_name": agent_name,
            "customer_name": customer_name,
            "started_at": datetime.utcnow().isoformat(),
            "events": []
        }
    
    def add_event(self, call_id: str, event_type: str, data: dict):
        if call_id in self.sessions:
            self.sessions[call_id]["events"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "type": event_type,
                "data": data
            })
    
    def get_session(self, call_id: str):
        return self.sessions.get(call_id)
    
    def list_sessions(self, agent_name: str = None):
        sessions = list(self.sessions.values())
        if agent_name:
            sessions = [s for s in sessions if s["agent_name"] == agent_name]
        return sessions
```

#### Add session recording to WebSocket:
```python
# In websocket handler
session_manager = SessionManager()

# On call start
session_manager.create_session(call_id, agent_name, customer_name)

# On transcript
session_manager.add_event(call_id, "transcript", {
    "speaker": message["speaker"],
    "text": message["text"]
})

# On AI suggestion
session_manager.add_event(call_id, "ai_suggestion", suggestion)
```

#### Frontend - Session replay UI:
```typescript
// New page: /calls/history
export default function CallHistoryPage() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  
  // Fetch sessions
  useEffect(() => {
    axios.get('/api/sessions')
      .then(res => setSessions(res.data));
  }, []);
  
  // Replay session
  const replaySession = (session) => {
    setSelectedSession(session);
    // Display events in order with timing
  };
  
  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="col-span-1">
        <h2>Call History</h2>
        {sessions.map(session => (
          <div key={session.call_id} onClick={() => replaySession(session)}>
            {session.customer_name} - {new Date(session.started_at).toLocaleString()}
          </div>
        ))}
      </div>
      
      <div className="col-span-2">
        {selectedSession && (
          <SessionReplay session={selectedSession} />
        )}
      </div>
    </div>
  );
}
```

**Success Criteria:**
- [ ] All transcripts are recorded
- [ ] Sessions can be listed
- [ ] Sessions can be replayed with correct timing
- [ ] Replay shows AI suggestions
- [ ] Replay is deterministic (same each time)

---

### **Task 2.2: Add Sentiment Analysis** ⭐⭐
**Difficulty:** Medium  
**Time:** 2 hours  
**Priority:** MEDIUM

**Objective:**
Analyze customer sentiment in real-time and alert agents.

**What to Implement:**

```python
# backend/app/api/sentiment_service.py
from textblob import TextBlob
# or use OpenAI for better results

class SentimentAnalyzer:
    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of text
        Returns: {
            "score": -1 to 1 (negative to positive),
            "label": "negative" | "neutral" | "positive",
            "confidence": 0-1
        }
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity < -0.3:
            label = "negative"
        elif polarity > 0.3:
            label = "positive"
        else:
            label = "neutral"
        
        return {
            "score": polarity,
            "label": label,
            "confidence": abs(polarity)
        }
```

#### Display sentiment in UI:
```typescript
// Show sentiment indicator next to customer messages
{message.speaker === 'customer' && message.sentiment && (
  <div className={`sentiment-indicator ${message.sentiment.label}`}>
    {message.sentiment.label === 'negative' ? '😟' : 
     message.sentiment.label === 'positive' ? '😊' : '😐'}
  </div>
)}

// Alert agent if sentiment is very negative
{sentiment.label === 'negative' && sentiment.score < -0.5 && (
  <div className="alert alert-warning">
    ⚠️ Customer sentiment is negative - be empathetic
  </div>
)}
```

**Success Criteria:**
- [ ] Sentiment analyzed for each message
- [ ] Visual indicator for positive/negative/neutral
- [ ] Alerts shown for very negative sentiment
- [ ] Sentiment trends visualized

---

### **Task 2.3: Implement Call Metrics Dashboard** ⭐⭐
**Difficulty:** Medium  
**Time:** 2-3 hours  
**Priority:** MEDIUM

**Objective:**
Track and display key call center metrics.

**Metrics to Track:**
- Average call duration
- Customer satisfaction (based on sentiment)
- First response time
- Resolution rate
- Agent utilization

**What to Implement:**

```typescript
// New page: /dashboard
export default function MetricsDashboard() {
  const [metrics, setMetrics] = useState({
    avgCallDuration: 0,
    totalCalls: 0,
    activeAgents: 0,
    waitingCustomers: 0,
    avgSentiment: 0,
    resolutionRate: 0
  });
  
  // Fetch metrics every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      axios.get('/api/metrics').then(res => setMetrics(res.data));
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="grid grid-cols-4 gap-4">
      <MetricCard 
        title="Total Calls" 
        value={metrics.totalCalls} 
        icon={<Phone />}
      />
      <MetricCard 
        title="Avg Duration" 
        value={`${Math.round(metrics.avgCallDuration / 60)}min`}
        icon={<Clock />}
      />
      <MetricCard 
        title="Active Agents" 
        value={metrics.activeAgents}
        icon={<User />}
      />
      <MetricCard 
        title="Waiting" 
        value={metrics.waitingCustomers}
        icon={<MessageSquare />}
      />
    </div>
  );
}
```

**Success Criteria:**
- [ ] Real-time metrics displayed
- [ ] Charts for trends over time
- [ ] Exportable reports
- [ ] Alerts for anomalies

---

## 🔴 **LEVEL 3: ADVANCED TASKS (Challenge)**

### **Task 3.1: Optimize Audio Latency** ⭐⭐⭐⭐
**Difficulty:** Hard  
**Time:** 3-4 hours  
**Priority:** LOW

**Objective:**
Reduce end-to-end latency for audio transcription to < 500ms.

**Optimizations:**
1. **Streaming Transcription** - Don't wait for full audio chunk
2. **Batch Processing** - Process multiple chunks together
3. **Caching** - Cache common phrases
4. **WebSocket Compression** - Reduce payload size
5. **Voice Activity Detection** - Only transcribe when speaking

**What to Implement:**

```python
# Streaming Whisper (use faster-whisper library)
from faster_whisper import WhisperModel

class OptimizedWhisperService:
    def __init__(self):
        self.model = WhisperModel("base", device="cpu", compute_type="int8")
    
    async def transcribe_stream(self, audio_stream):
        """Transcribe audio in streaming mode"""
        segments, info = self.model.transcribe(
            audio_stream, 
            beam_size=5,
            vad_filter=True,  # Voice Activity Detection
            without_timestamps=False
        )
        
        for segment in segments:
            yield segment.text
```

**Success Criteria:**
- [ ] First token latency < 500ms
- [ ] Streaming transcription implemented
- [ ] VAD reduces unnecessary processing
- [ ] Handles network issues gracefully

---

### **Task 3.2: Implement NextAuth with Role-Based Access** ⭐⭐⭐
**Difficulty:** Medium-Hard  
**Time:** 3-4 hours  
**Priority:** MEDIUM

**Objective:**
Add proper authentication with role-based access control.

**Roles:**
- `agent` - Can take calls, see AI suggestions
- `supervisor` - Can see all calls, view metrics
- `admin` - Full access, manage users

**What to Implement:**

```typescript
// pages/api/auth/[...nextauth].ts
import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

export default NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        // Verify with backend
        const res = await fetch(`${process.env.API_URL}/auth/login`, {
          method: 'POST',
          body: JSON.stringify(credentials),
          headers: { "Content-Type": "application/json" }
        });
        
        const user = await res.json();
        
        if (res.ok && user) {
          return user;  // includes role
        }
        return null;
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = user.role;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.role = token.role;
      return session;
    }
  },
  pages: {
    signIn: '/auth/signin',
  }
});

// Protect routes
import { useSession } from "next-auth/react";

export default function AgentPage() {
  const { data: session, status } = useSession({
    required: true,
    onUnauthenticated() {
      router.push('/auth/signin');
    }
  });
  
  if (session.user.role !== 'agent' && session.user.role !== 'supervisor') {
    return <div>Access Denied</div>;
  }
  
  // Rest of component...
}
```

**Success Criteria:**
- [ ] Users must authenticate to access agent pages
- [ ] Roles properly enforced
- [ ] Session persists across page reloads
- [ ] Protected API routes check roles

---

### **Task 3.3: Create @agent/ui Package with Storybook** ⭐⭐⭐⭐
**Difficulty:** Hard  
**Time:** 4-5 hours  
**Priority:** LOW

**Objective:**
Extract reusable components into a publishable npm package.

**Components to Extract:**
- `AudioLevelMeter`
- `ChatMessage`
- `CallControls`
- `CustomerInfoCard`
- `AISuggestionPanel`

**Structure:**
```
packages/agent-ui/
├── src/
│   ├── components/
│   │   ├── AudioLevelMeter.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── CallControls.tsx
│   │   └── index.ts
│   ├── hooks/
│   │   ├── useAudioCall.ts
│   │   └── index.ts
│   └── index.ts
├── .storybook/
│   └── main.js
├── stories/
│   ├── AudioLevelMeter.stories.tsx
│   └── ChatMessage.stories.tsx
├── tests/
│   └── AudioLevelMeter.test.tsx
├── package.json
└── tsconfig.json
```

**Storybook Stories:**
```typescript
// stories/AudioLevelMeter.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { AudioLevelMeter } from '../src/components/AudioLevelMeter';

const meta: Meta<typeof AudioLevelMeter> = {
  title: 'Components/AudioLevelMeter',
  component: AudioLevelMeter,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof AudioLevelMeter>;

export const Default: Story = {
  args: {
    level: 0.5,
    color: 'blue'
  }
};

export const High: Story = {
  args: {
    level: 0.9,
    color: 'red'
  }
};
```

**Success Criteria:**
- [ ] Package builds successfully (ESM + types)
- [ ] Storybook runs and displays all components
- [ ] Basic tests pass (Vitest)
- [ ] Package published to npm (or private registry)
- [ ] Can be imported in another project

---

## 📋 **Task Checklist & Grading**

### **Minimum Passing (60%)**
- [ ] Task 1.1: Whisper integration (20%)
- [ ] Task 1.2: AI suggestions (20%)
- [ ] Task 1.3: Customer lookup (20%)

### **Good Score (75%)**
All Level 1 tasks + any 2 Level 2 tasks

### **Excellent Score (90%)**
All Level 1 and Level 2 tasks

### **Perfect Score (100%)**
All tasks including at least 1 Level 3 task

---

## 🎓 **Learning Objectives**

By completing these tasks, students will learn:

1. **Real-time Systems**
   - WebSocket bidirectional communication
   - Audio streaming and processing
   - Low-latency optimizations

2. **AI Integration**
   - OpenAI Whisper API
   - GPT-4 for contextual suggestions
   - Prompt engineering

3. **Frontend Architecture**
   - React hooks for complex state
   - Real-time UI updates
   - Component library development

4. **Backend Development**
   - FastAPI async patterns
   - WebSocket handling
   - Session management

5. **Production Engineering**
   - Error handling and resilience
   - Performance optimization
   - Authentication and authorization

---

## 🚀 **Getting Started**

1. **Read the Code**
   - Explore existing scaffold
   - Understand data flow
   - Run the app and test it

2. **Set Up Environment**
   - Get OpenAI API key
   - Install dependencies
   - Configure environment variables

3. **Start with Task 1.1**
   - Implement Whisper integration
   - Test thoroughly
   - Move to next task

4. **Iterate and Test**
   - Complete one task at a time
   - Test each feature
   - Fix bugs before moving on

5. **Optional: Deploy**
   - Deploy to Vercel (frontend)
   - Deploy to Railway/Render (backend)
   - Share demo with classmates

---

## 📚 **Resources**

- [OpenAI Whisper API Docs](https://platform.openai.com/docs/guides/speech-to-text)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Next.js Real-time Features](https://nextjs.org/docs)
- [Storybook Documentation](https://storybook.js.org/)
- [WebRTC Fundamentals](https://webrtc.org/)

---

## 💡 **Tips for Success**

1. **Start Small** - Get one feature working end-to-end before moving on
2. **Test Often** - Use the browser DevTools console
3. **Read Errors** - Error messages usually tell you what's wrong
4. **Ask for Help** - Use office hours or discussion board
5. **Document** - Write comments explaining your code
6. **Version Control** - Commit after each task completion

---

## 🏆 **Bonus Challenges**

For students who finish early:

1. **Multi-language Support** - Support transcription in multiple languages
2. **Call Recording** - Save audio files for later playback
3. **Custom AI Models** - Train custom model for domain-specific terms
4. **Mobile App** - Create React Native version
5. **Analytics Dashboard** - Advanced metrics and visualizations
6. **Integration Tests** - E2E tests with Playwright
7. **Load Testing** - Test with 100+ concurrent users

---

## ⚠️ **Common Pitfalls**

1. **Audio Format Issues** - Ensure WebM/Opus is properly encoded
2. **API Rate Limits** - Handle OpenAI rate limiting
3. **WebSocket Reconnection** - Implement reconnection logic
4. **Memory Leaks** - Clean up audio streams properly
5. **CORS Issues** - Configure CORS headers correctly
6. **State Management** - Don't forget to clean up on unmount

---

**Good luck! 🚀**

Remember: The goal is to learn, not just to finish. Take your time, understand each concept, and build something you're proud of!

