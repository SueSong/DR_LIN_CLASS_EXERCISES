# Quick Start Guide - Exercise 11

## 🚀 Easy Startup (Recommended)

### Mac/Linux:
```bash
./start.sh
```

### Windows:
```cmd
start.bat
```

The script will automatically:
- ✅ Check if ports are available
- ✅ Set up Python virtual environment
- ✅ Install all dependencies
- ✅ Start backend on port 8011
- ✅ Start frontend on port 3082
- ✅ Open logs in real-time

**Then open:** http://localhost:3082

Press `Ctrl+C` to stop all servers.

---

## 📋 Manual Startup

If you prefer to start servers manually:

### Terminal 1 - Backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm install
PORT=3082 npm run dev  # On Windows: set PORT=3082 && npm run dev
```

### Then open:
- **Frontend:** http://localhost:3082
- **Backend API Docs:** http://localhost:8011/docs

---

## 🔧 Troubleshooting

### Port Already in Use?

**Mac/Linux:**
```bash
# Check what's using the port
lsof -ti:8011   # or :3082

# Kill the process
lsof -ti:8011 | xargs kill -9
lsof -ti:3082 | xargs kill -9
```

**Windows:**
```cmd
# Check what's using the port
netstat -ano | findstr :8011

# Kill the process (replace PID with the number from above)
taskkill /PID <PID> /F
```

### Frontend Build Errors?

```bash
cd frontend
rm -rf .next node_modules
npm install
PORT=3082 npm run dev
```

### Backend Import Errors?

```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload
```

---

## 📊 Verify Everything is Working

```bash
# Test backend
curl http://localhost:8011/healthz
# Should return: {"status":"healthy"}

# Test frontend
curl http://localhost:3082
# Should return HTML content

# Test WebSocket
# Open http://localhost:3082/coach in your browser and try chatting
```

---

## 🎯 What to Do Next

1. **Try the app:** Go to http://localhost:3082
2. **Enter a parent name** (e.g., "Sarah")
3. **Ask a question** about child development
4. **Get AI coaching advice** in real-time

Example questions:
- "How do I help my 5-year-old with bedtime routines?"
- "My child is struggling with sharing toys, what should I do?"
- "What are good screen time limits for a 7-year-old?"

---

## 📝 Development Tips

### Watch Logs in Real-Time

**Mac/Linux:**
```bash
# Backend logs
tail -f backend.log

# Frontend logs  
tail -f frontend.log
```

**Windows:**
The servers run in separate command windows, so you can see logs directly there.

### Auto-Reload

Both servers have auto-reload enabled:
- **Backend:** Edit Python files → auto-reloads
- **Frontend:** Edit React/TypeScript files → hot-reloads in browser

### Test API Endpoints

Visit http://localhost:8011/docs for interactive API documentation (Swagger UI).

---

## 🎓 Week 8 Exercises

See the main [README.md](./README.md) for the full list of Week 8 tasks including:
- Safety & scope boundaries
- RAG implementation
- E2E tests with Playwright
- Docker & CI/CD
- SLOs & observability
- And more!

