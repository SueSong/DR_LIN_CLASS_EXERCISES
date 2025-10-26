# Exercise 10: Quick Reference Guide 📋

## Project Overview

**Real-Time AI Call Center Assistant** - A production-grade streaming UI application combining WebRTC, speech-to-text, and AI assistance for live customer support calls.

---

## 📚 Documentation Files

1. **`README.md`** - Main overview, architecture, features, lab flow
2. **`ARCHITECTURE.md`** - Technical deep dive, implementation details
3. **`STUDENT_TASKS.md`** - Step-by-step implementation guide
4. **`ADVANCED_REQUIREMENTS.md`** - Production requirements & acceptance criteria
5. **`QUICK_REFERENCE.md`** - This file

---

## 🎯 Learning Objectives (8 Core Skills)

1. ✅ Real-time audio streaming (WebRTC)
2. ✅ Speech-to-text integration (Whisper/Deepgram)
3. ✅ Streaming AI responses (OpenAI GPT-4)
4. ✅ Server-Sent Events (SSE)
5. ✅ WebSocket bidirectional communication
6. ✅ Optimistic UI updates
7. ✅ Session management & replay
8. ✅ Role-based authentication

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Async Python web framework
- **PostgreSQL** - Relational database
- **Redis** - Session cache
- **OpenAI Whisper** - Speech-to-text
- **OpenAI GPT-4** - AI assistant
- **aiortc** - WebRTC handling

### Frontend
- **Next.js 15** - React framework
- **React 19** - UI library
- **NextAuth** - Authentication
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **WebRTC API** - Browser audio

---

## 📂 Project Structure

```
exercise_10/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app
│   │   ├── api/
│   │   │   ├── websocket.py           # WebSocket handler
│   │   │   ├── streaming.py           # SSE endpoints
│   │   │   ├── chat.py                # Chat API
│   │   │   └── session.py             # Session management
│   │   ├── agents/
│   │   │   ├── transcription.py       # STT engine
│   │   │   ├── assistant.py           # AI agent
│   │   │   └── context_manager.py     # State management
│   │   └── models.py                  # Database models
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── call/[id]/page.tsx     # Call interface
│   │   │   └── admin/page.tsx         # Admin dashboard
│   │   ├── components/
│   │   │   ├── call/
│   │   │   │   ├── AudioStream.tsx    # WebRTC audio
│   │   │   │   ├── Transcription.tsx  # Live transcript
│   │   │   │   └── AISuggestions.tsx  # Streaming hints
│   │   │   └── auth/
│   │   │       └── ProtectedRoute.tsx # Auth guard
│   │   └── lib/
│   │       ├── webrtc.ts              # WebRTC utils
│   │       ├── sse.ts                 # SSE client
│   │       └── session-manager.ts     # Session restore
│   └── package.json
│
├── packages/
│   └── agent-ui/                       # Reusable component library
│       ├── src/
│       │   ├── components/
│       │   └── hooks/
│       └── .storybook/
│
├── data/
│   └── seed_customers.py               # Fake data generator
│
└── docs/
    ├── README.md                       # Overview
    ├── ARCHITECTURE.md                 # Technical details
    ├── STUDENT_TASKS.md                # Implementation guide
    └── ADVANCED_REQUIREMENTS.md        # Production features
```

---

## 🔄 Data Flow

```
1. Customer speaks → Microphone
2. Browser captures audio → getUserMedia()
3. Audio streams → WebSocket → Backend
4. Backend transcribes → Whisper API
5. Transcription streams → SSE → Frontend (displayed live)
6. AI analyzes context → GPT-4 Function Calling
7. AI triggers DB lookup → Customer info loaded
8. AI generates suggestion → Streamed word-by-word → Frontend
9. Agent reads suggestion → Responds to customer
10. Conversation saved → Database (for replay)
```

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
cd exercise_10
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### 2. Start Services
```bash
docker-compose up -d postgres redis
```

### 3. Seed Database
```bash
cd backend
python -m pip install -r requirements.txt
python data/seed_customers.py
```

### 4. Run Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Run Frontend
```bash
cd frontend
npm install
npm run dev
```

### 6. Open App
```
http://localhost:3000
```

---

## 🎯 Student Lab Tasks (90 min)

### Phase 1: Setup (15 min)
- [ ] Create project structure
- [ ] Start Docker services
- [ ] Seed database
- [ ] Verify services running

### Phase 2: Audio Streaming (20 min)
- [ ] Implement WebRTC audio capture
- [ ] Create WebSocket handler
- [ ] Stream audio to backend
- [ ] Display waveform

### Phase 3: Transcription (20 min)
- [ ] Integrate Whisper API
- [ ] Stream transcription via SSE
- [ ] Display live transcript
- [ ] Add speaker labels

### Phase 4: AI Assistant (25 min)
- [ ] Build streaming AI agent
- [ ] Implement context manager
- [ ] Add customer lookup
- [ ] Display suggestions with animation

### Phase 5: Polish (10 min)
- [ ] Add customer info panel
- [ ] Implement quick actions
- [ ] Generate call summary
- [ ] Demo to class

---

## ✅ Acceptance Criteria

### A. Streaming Chat
- [x] **Optimistic echo** - User message appears instantly
- [x] **First token < 1s** - AI response starts within 1 second
- [x] **Graceful abort** - Stop button preserves partial response
- [x] **Smooth rendering** - No UI jank during streaming

### B. Session Restore
- [x] **No dupes after refresh** - Messages appear exactly once
- [x] **Deterministic replay** - Same state after restore
- [x] **IndexedDB backup** - Survives localStorage limits
- [x] **Conflict resolution** - Sync with server correctly

### C. Authentication
- [x] **Role gates** - Admin routes blocked for agents
- [x] **Middleware protection** - Server-side auth checks
- [x] **Session persistence** - Stay logged in after refresh
- [x] **Unauthorized redirect** - Clear error messages

### D. Package Publishing
- [x] **ESM + CJS builds** - Both formats supported
- [x] **TypeScript types** - Full type definitions
- [x] **Storybook docs** - All components documented
- [x] **Unit tests pass** - >80% coverage
- [x] **Peer dependencies** - React not bundled

---

## 🧪 Testing

### Run All Tests
```bash
npm test                    # Unit tests
npm run test:e2e            # End-to-end tests
npm run test:perf           # Performance tests
```

### Test Checklist
```typescript
// Performance
✓ First token arrives < 1s
✓ UI updates at 60fps
✓ WebRTC connection < 2s

// Reliability
✓ No message duplicates
✓ Session restores correctly
✓ Abort preserves partial content

// Security
✓ Unauthorized users redirected
✓ Role gates enforced
✓ Middleware blocks invalid access

// Package
✓ Builds without errors
✓ Types resolve correctly
✓ Storybook renders all stories
```

---

## 📊 Example Conversation Flow

```
[10:23:15] Customer: "Hi, I'm Sarah Johnson. I need help with order 78901"
           ↓
[10:23:16] [AI detects name] → Lookup customer "Sarah Johnson"
           ↓
[10:23:17] [Customer found] → Load account #12345, orders, tickets
           ↓
[10:23:18] [AI generates suggestion]:
           💡 "I found Sarah's order #78901. It shipped yesterday 
               via FedEx. Tracking: 1Z999AA10. ETA: Oct 23."
           ↓
[10:23:22] Agent: "Hi Sarah! I see your order shipped yesterday.
                    It should arrive by Oct 23."
           ↓
[10:23:30] Customer: "Great! Can I change the delivery address?"
           ↓
[10:23:31] [AI checks policy] → "Address changes allowed until day before delivery"
           ↓
[10:23:32] [AI suggests]:
           💡 "Address can still be changed. Use carrier website 
               or offer to handle it for her."
```

---

## 🎨 UI Components

### 1. AudioStream
```tsx
<AudioStream
  callId="call-123"
  wsUrl="ws://localhost:8000"
  onStreamStart={() => console.log('Started')}
/>
```
**Features:** Mic permission, waveform, mute/unmute

### 2. Transcription
```tsx
<Transcription
  callId="call-123"
  sseUrl="http://localhost:8000"
/>
```
**Features:** Live text, speaker labels, timestamps

### 3. AISuggestions
```tsx
<AISuggestions
  callId="call-123"
  sseUrl="http://localhost:8000"
/>
```
**Features:** Streaming text, animations, action buttons

### 4. CustomerInfo
```tsx
<CustomerInfo customerId={123} />
```
**Features:** Profile, orders, tickets, quick facts

---

## 🔧 Configuration

### Environment Variables

**Backend** (`.env`)
```bash
DATABASE_URL=postgresql://admin:password@localhost:5432/callcenter
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key
```

**Frontend** (`.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

---

## 📈 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| First token latency | < 1s | `performance.now()` |
| Audio → Transcript | < 3s | Whisper API + network |
| UI render time | 60fps | Chrome DevTools |
| WebRTC connection | < 2s | ICE gathering time |
| Session restore | < 500ms | IndexedDB read time |

---

## 🐛 Common Issues

### Issue 1: WebRTC not connecting
**Solution:** Check STUN/TURN server config, verify firewall allows UDP

### Issue 2: Audio crackling
**Solution:** Adjust buffer size, check sample rate (16kHz)

### Issue 3: Transcription delayed
**Solution:** Switch to Deepgram streaming, reduce chunk size

### Issue 4: AI suggestions slow
**Solution:** Enable streaming, optimize prompt, cache customer data

### Issue 5: Duplicate messages after refresh
**Solution:** Implement turn-based commits, use deterministic IDs

---

## 📚 Additional Resources

- [WebRTC Samples](https://webrtc.github.io/samples/)
- [OpenAI Whisper Docs](https://platform.openai.com/docs/guides/speech-to-text)
- [Server-Sent Events Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [NextAuth.js Docs](https://next-auth.js.org/)
- [Storybook Docs](https://storybook.js.org/)

---

## 🎓 Grading Rubric

| Category | Weight | Criteria |
|----------|--------|----------|
| **Functionality** | 40% | All features working, proper error handling |
| **Performance** | 20% | Meets latency targets, smooth UI |
| **Code Quality** | 20% | Clean code, TypeScript, tests |
| **UX** | 10% | Responsive, accessible, intuitive |
| **Documentation** | 10% | README, code comments, stories |

**Total: 100 points**

---

## 🎉 Success Criteria

A successful implementation demonstrates:

✅ **Real-time streaming** - Audio, transcription, AI all working together  
✅ **Low latency** - First token < 1s, smooth interactions  
✅ **Reliability** - No duplicates, graceful errors, session restore  
✅ **Security** - Authentication, role-based access, protected routes  
✅ **Quality** - Tests passing, Storybook documented, TypeScript types  
✅ **Polish** - Beautiful UI, smooth animations, professional UX  

---

## 💡 Next Steps (Beyond Lab)

### Intermediate
- Add multi-language support
- Implement emotion detection
- Create analytics dashboard
- Add voice commands for agent

### Advanced
- Scale to 1000 concurrent calls
- Deploy to production (AWS/GCP)
- Add co-browsing feature
- Implement call recording storage
- Build supervisor monitoring view

---

## 🤝 Getting Help

- **Instructor office hours:** Check schedule
- **GitHub Issues:** Report bugs in exercise repo
- **Slack channel:** `#exercise-10-help`
- **Pair programming:** Find a classmate!

---

Good luck with your real-time AI call assistant! 🚀

**Remember:** The goal is to learn streaming patterns, not perfection. Focus on understanding the flow of data from audio → AI → UI. Everything else is just details! 💪

