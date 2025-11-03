# 🎓 Welcome to Exercise 11: Child Growth Assistant

## 👋 Introduction

Welcome! This exercise is your opportunity to build and harden a **production-ready AI assistant** for parents seeking guidance on child development and growth. You'll transform a basic chat application into a robust, tested, and deployable service.

---

## 🎯 What You'll Build

A **Child Growth Assistant** that:
- 💬 Provides real-time parenting advice via chat
- 🛡️ Has safety guardrails and scope boundaries
- 📚 Uses RAG (Retrieval Augmented Generation) for accurate, cited information
- 🧪 Is thoroughly tested (unit, e2e, load)
- 🐳 Is containerized and ready to deploy
- 📊 Has observability and SLOs
- 💰 Tracks costs and has budget controls

---

## 🚀 Getting Started (5 minutes)

### Step 1: Start the Application

```bash
./start.sh
```

That's it! The script will:
- ✅ Install all dependencies
- ✅ Start backend on http://localhost:8011
- ✅ Start frontend on http://localhost:3082
- ✅ Check everything is working

### Step 2: Try the App

1. Open http://localhost:3082 in your browser
2. Enter your name (e.g., "Sarah")
3. Ask a question like:
   - "How do I help my 5-year-old with bedtime routines?"
   - "My child is struggling with sharing, what should I do?"
   - "What are good screen time limits for a 7-year-old?"

### Step 3: Explore

- **Frontend:** Beautiful, responsive React app
- **Backend API Docs:** http://localhost:8011/docs
- **Real-time Chat:** WebSocket-powered messaging
- **Auto-reload:** Edit code and see changes instantly

---

## 📚 Documentation

We've prepared comprehensive guides for you:

| Document | Purpose |
|----------|---------|
| [README.md](./README.md) | Project overview & Week 8 tasks |
| [QUICKSTART.md](./QUICKSTART.md) | Setup, troubleshooting, manual startup |
| [SCRIPTS.md](./SCRIPTS.md) | Complete scripts reference |
| [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) | Codebase layout & architecture |

**Start with:** [QUICKSTART.md](./QUICKSTART.md) if you run into any issues.

---

## 📋 Week 8 Tasks Overview

You'll complete 12 tasks to harden this MVP for internal alpha launch:

### 🛡️ Core Safety & Quality
1. **Safety & Scope Policy** - Define boundaries, add refusal templates
2. **Curated RAG Pack** - Ground advice in vetted sources with citations
3. **SSE Streaming** - Stream responses for better UX
4. **Playwright E2E Tests** - Cover 10+ realistic scenarios

### 🚀 Infrastructure & DevOps
5. **Docker & Health Checks** - Containerize for deployment
6. **CI/CD Pipelines** - Automated testing and deployment
7. **SLOs & Observability** - Monitor performance and reliability
8. **Guardrails & HITL** - Route complex cases to human mentors

### 💡 Advanced Features
9. **Prompt Versioning** - Track and test prompt changes
10. **Cost Watchdog** - Monitor and control spending
11. **Load Testing** - Validate performance under stress
12. **Accessibility** - Ensure usable by everyone

**See [README.md](./README.md) for detailed requirements and pass/fail criteria.**

---

## 🛠️ Available Tools

### Scripts
```bash
./start.sh    # Start both servers (Mac/Linux)
./start.bat   # Start both servers (Windows)
./stop.sh     # Stop all servers
./test.sh     # Run automated tests
```

### Manual Commands
```bash
# View logs
tail -f backend.log frontend.log

# Test endpoints
curl http://localhost:8011/healthz
curl http://localhost:3082

# Clean restart
./stop.sh && ./start.sh
```

---

## 🎨 The Application

### Frontend (Next.js)
- **Modern UI:** Tailwind CSS with custom animations
- **Real-time Chat:** WebSocket-powered messaging
- **Type-safe:** Full TypeScript coverage
- **Tested:** Playwright e2e tests ready

**Key Files:**
- `frontend/src/app/page.tsx` - Home page
- `frontend/src/app/coach/page.tsx` - Sign-in
- `frontend/src/app/coach/chat/page.tsx` - Chat interface
- `frontend/src/lib/coachApi.ts` - API client

### Backend (FastAPI)
- **Fast:** Async Python with auto-reload
- **WebSocket:** Real-time bidirectional communication
- **Documented:** Auto-generated API docs
- **Extensible:** Ready for RAG, LLM integration

**Key Files:**
- `backend/app/main.py` - FastAPI app
- `backend/app/api/coach.py` - REST endpoints
- `backend/app/api/websocket.py` - WebSocket handler

---

## 🎓 Learning Outcomes

By completing this exercise, you will:

✅ Build production-ready AI applications  
✅ Implement safety guardrails and HITL flows  
✅ Use RAG for grounded, cited responses  
✅ Write comprehensive tests (unit, e2e, load)  
✅ Containerize and deploy services  
✅ Set up CI/CD pipelines  
✅ Monitor performance with SLOs  
✅ Manage costs and budgets  
✅ Design accessible UX  
✅ Version and test prompts  

---

## 🏆 Submission Requirements

By end of Week 8, submit:

1. **3-5 Merged PRs** covering:
   - Safety + RAG
   - Docker + CI/CD
   - E2E + SLOs

2. **2-Minute Demo Video** showing:
   - Refusal flow (out-of-scope question)
   - Normal advice with citations
   - HITL escalation

3. **One-Pager Report** with:
   - Metrics (p95 latency, failure rate, citation rate)
   - Cost per day
   - Key risks
   - Next-week plan

---

## 💡 Development Tips

### Daily Workflow
1. **Morning:** `./start.sh` - servers auto-reload
2. **Code:** Edit files, see changes instantly
3. **Test:** `./test.sh` before committing
4. **Evening:** `Ctrl+C` or `./stop.sh`

### Best Practices
- ✅ Keep `.env` files out of git
- ✅ Write tests for new features
- ✅ Use feature flags for experiments
- ✅ Small, focused PRs
- ✅ Keep CI green

### Debugging
1. Check logs: `tail -f backend.log frontend.log`
2. Test endpoints: `./test.sh`
3. API docs: http://localhost:8011/docs
4. Clean restart: `./stop.sh && ./start.sh`

---

## 🆘 Getting Help

### Resources
- **Quickstart:** [QUICKSTART.md](./QUICKSTART.md)
- **Scripts:** [SCRIPTS.md](./SCRIPTS.md)
- **Structure:** [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)
- **API Docs:** http://localhost:8011/docs

### Common Issues
- **Port in use:** Run `./stop.sh` first
- **Dependencies:** Scripts install automatically
- **Build errors:** Try clean restart
- **WebSocket issues:** Check both servers are running

See [QUICKSTART.md](./QUICKSTART.md) for detailed troubleshooting.

---

## 🎉 Let's Begin!

Ready to build something amazing? Start here:

```bash
# 1. Start the servers
./start.sh

# 2. Open in browser
# http://localhost:3082

# 3. Try the chat!
# Ask a parenting question

# 4. Explore the code
# Read the files mentioned above

# 5. Start building
# Pick a task from README.md
```

**Have fun and happy coding! 🚀**

---

*Exercise 11 - AI Training Class - Week 8*  
*Building Production-Ready AI Assistants*

