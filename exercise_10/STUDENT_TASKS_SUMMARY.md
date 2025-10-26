# 📝 Student Tasks - Quick Reference
## Exercise 10: AI Call Center Assistant

---

## 🎯 Task Overview

| Level | Tasks | Time | Difficulty | Priority |
|-------|-------|------|------------|----------|
| **Level 1** | 3 tasks | 4-6 hrs | Basic | **MUST DO** |
| **Level 2** | 3 tasks | 6-8 hrs | Intermediate | **SHOULD DO** |
| **Level 3** | 3 tasks | 8-12 hrs | Advanced | **OPTIONAL** |

---

## 🟢 LEVEL 1: Core Features (Required)

### ✅ Task 1.1: Whisper Transcription
**Time:** 2-3 hours | **Priority:** ⭐⭐⭐ CRITICAL

**What:** Convert audio to text using OpenAI Whisper API

**Files to Create:**
- `backend/app/api/whisper_service.py`

**Files to Modify:**
- `backend/app/api/websocket.py`

**Key Steps:**
1. Install `openai` Python package
2. Create `WhisperService` class
3. Call Whisper API with audio chunks
4. Send transcripts via WebSocket
5. Display in chat UI

**Test:** Speak into mic → See text in chat within 2 seconds

---

### ✅ Task 1.2: AI Agent Suggestions
**Time:** 2-3 hours | **Priority:** ⭐⭐ HIGH

**What:** Generate helpful suggestions for agents based on customer messages

**Files to Create:**
- `backend/app/api/ai_service.py`

**Files to Modify:**
- `backend/app/api/websocket.py`
- `frontend/src/app/calls/page.tsx`

**Key Steps:**
1. Create `AIAssistantService` class
2. Call GPT-4 with customer message
3. Return suggestion + confidence score
4. Send only to agent (not customer)
5. Display in agent sidebar

**Test:** Customer says "I'm frustrated" → Agent sees suggestion "Be empathetic and offer help"

---

### ✅ Task 1.3: Customer Info Lookup
**Time:** 1-2 hours | **Priority:** ⭐⭐ MEDIUM

**What:** Show customer details when call starts

**Files to Modify:**
- `backend/app/api/customers.py` (enhance existing)
- `frontend/src/app/calls/page.tsx`

**Key Steps:**
1. Create customer details endpoint
2. Fetch customer info on call start
3. Display name, email, orders, tickets
4. Update in real-time

**Test:** Start call → See customer info in sidebar

---

## 🟡 LEVEL 2: Enhanced Features (Recommended)

### ✅ Task 2.1: Session Recording
**Time:** 2-3 hours | **Priority:** ⭐⭐⭐ HIGH

**What:** Record calls and enable replay

**Create:** Session storage, replay UI

**Test:** End call → View history → Click to replay

---

### ✅ Task 2.2: Sentiment Analysis
**Time:** 2 hours | **Priority:** ⭐⭐ MEDIUM

**What:** Analyze customer emotions in real-time

**Create:** Sentiment analyzer, visual indicators

**Test:** Customer says "I'm very angry" → See 😟 and warning

---

### ✅ Task 2.3: Metrics Dashboard
**Time:** 2-3 hours | **Priority:** ⭐⭐ MEDIUM

**What:** Track KPIs (avg duration, satisfaction, etc.)

**Create:** Dashboard page with charts

**Test:** View real-time metrics updating

---

## 🔴 LEVEL 3: Advanced Features (Optional)

### ✅ Task 3.1: Optimize Latency
**Time:** 3-4 hours | **Difficulty:** ⭐⭐⭐⭐ HARD

**What:** Reduce transcription latency to < 500ms

**Techniques:** Streaming, VAD, caching

---

### ✅ Task 3.2: NextAuth + Roles
**Time:** 3-4 hours | **Difficulty:** ⭐⭐⭐ MEDIUM-HARD

**What:** Add proper auth with role-based access

**Roles:** agent, supervisor, admin

---

### ✅ Task 3.3: Component Library
**Time:** 4-5 hours | **Difficulty:** ⭐⭐⭐⭐ HARD

**What:** Extract components into `@agent/ui` package

**Deliverable:** Published npm package with Storybook

---

## 📊 Grading Rubric

| Score | Requirements |
|-------|-------------|
| **60% (Pass)** | Complete all Level 1 tasks |
| **75% (Good)** | Level 1 + any 2 Level 2 tasks |
| **90% (Excellent)** | Level 1 + all Level 2 tasks |
| **100% (Perfect)** | All tasks + at least 1 Level 3 |

---

## 🚦 Getting Started

### Step 1: Environment Setup (30 min)
```bash
# Get OpenAI API key
export OPENAI_API_KEY="sk-..."

# Backend
cd exercise_10/backend
source venv/bin/activate
pip install openai

# Frontend  
cd exercise_10/frontend
npm install
```

### Step 2: Test Current System (15 min)
1. Start backend: `uvicorn app.main_simple:app --reload --port 8000`
2. Start frontend: `PORT=3080 npm run dev`
3. Open agent at `localhost:3080/auth/signin`
4. Open customer at `localhost:3080/customer`
5. Test text chat works

### Step 3: Start Task 1.1 (2-3 hours)
1. Create `whisper_service.py`
2. Integrate with WebSocket
3. Test transcription
4. Fix any bugs

### Step 4: Continue Tasks (1-2 hours each)
Complete tasks in order, test each thoroughly

---

## 📚 Quick Links

**API Documentation:**
- [OpenAI Whisper](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI Chat](https://platform.openai.com/docs/guides/chat)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)

**Code Examples:**
- See `STUDENT_TASKS_DETAILED.md` for full code samples
- Check existing code in `backend/app/api/` for patterns
- Look at `frontend/src/lib/` for utilities

**Testing:**
- Use browser DevTools (F12) for debugging
- Check backend logs: `tail -f /tmp/backend.log`
- Use `curl` to test API endpoints

---

## 💡 Pro Tips

1. **One Task at a Time** - Don't start Task 2 until Task 1 works
2. **Test Early, Test Often** - Test after every major change
3. **Read Error Messages** - They usually tell you what's wrong
4. **Use Console Logging** - `console.log()` and `print()` are your friends
5. **Git Commit Often** - Commit after each task completion
6. **Ask for Help** - Don't spend more than 30 min stuck on one issue

---

## ⚠️ Common Issues

| Problem | Solution |
|---------|----------|
| Whisper API error | Check API key is set correctly |
| Audio not transcribing | Check audio format is WebM/Opus |
| WebSocket disconnects | Add reconnection logic |
| Messages not routing | Check call_id matching in backend |
| CORS errors | Add frontend URL to CORS origins |
| Out of tokens | OpenAI free tier has limits, upgrade or use smaller model |

---

## 🎓 What You'll Learn

✅ **Real-time Systems** - WebSockets, audio streaming, low latency  
✅ **AI Integration** - Whisper API, GPT-4, prompt engineering  
✅ **Full-Stack Dev** - React hooks, FastAPI async, state management  
✅ **Production Skills** - Error handling, auth, performance optimization  
✅ **Best Practices** - Testing, documentation, code organization  

---

## 🏆 Bonus Points

Extra credit for:
- **Clean Code** - Well-documented, follows conventions
- **Error Handling** - Graceful failures, user-friendly messages
- **Testing** - Unit tests or E2E tests
- **UI Polish** - Beautiful, responsive design
- **Innovation** - Add creative features beyond requirements
- **Documentation** - Write usage guide for your features

---

## 📞 Support

- **Office Hours:** TBD
- **Discussion Forum:** [Link]
- **Sample Code:** See `STUDENT_TASKS_DETAILED.md`
- **Video Walkthrough:** [Link to recording]

---

## ✅ Task Completion Checklist

### Level 1 (Required)
- [ ] Task 1.1: Whisper transcription working
- [ ] Task 1.2: AI suggestions displaying
- [ ] Task 1.3: Customer info loading

### Level 2 (Recommended)
- [ ] Task 2.1: Session recording implemented
- [ ] Task 2.2: Sentiment analysis showing
- [ ] Task 2.3: Metrics dashboard functional

### Level 3 (Optional)
- [ ] Task 3.1: Latency optimized
- [ ] Task 3.2: Auth with roles working
- [ ] Task 3.3: Component library published

### Submission
- [ ] Code committed to Git
- [ ] README updated with features
- [ ] Demo video recorded (optional)
- [ ] Deployed to cloud (optional)

---

**Let's build something awesome! 🚀**

Questions? Check the detailed guide or ask in office hours!

