# Exercise 11 - Scripts & Tools Reference

This document describes all the helper scripts available for Exercise 11.

## 📁 Scripts Overview

```
exercise_11/
├── start.sh          # 🚀 Start all servers (Mac/Linux)
├── start.bat         # 🚀 Start all servers (Windows)
├── stop.sh           # 🛑 Stop all servers (Mac/Linux)
├── stop.bat          # 🛑 Stop all servers (Windows)
├── test.sh           # 🧪 Test all endpoints (Mac/Linux)
├── QUICKSTART.md     # 📖 Quick start guide
└── README.md         # 📚 Main documentation
```

---

## 🚀 Starting the Application

### Automatic Start (Recommended)

**Mac/Linux:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

**What it does:**
- ✅ Checks if ports 8011 and 3082 are available
- ✅ Creates Python virtual environment (if needed)
- ✅ Installs all dependencies
- ✅ Starts backend on http://localhost:8011
- ✅ Starts frontend on http://localhost:3082
- ✅ Waits for both servers to be ready
- ✅ Shows live logs from both servers

**Output:**
- Backend logs: `backend.log`
- Frontend logs: `frontend.log`

**To stop:** Press `Ctrl+C`

---

## 🛑 Stopping the Application

### Quick Stop

**Mac/Linux:**
```bash
./stop.sh
```

**Windows:**
```cmd
stop.bat
```

**What it does:**
- Finds and kills processes on port 8011 (backend)
- Finds and kills processes on port 3082 (frontend)
- Cleans up any remaining related processes

### Manual Stop

**Mac/Linux:**
```bash
# Kill specific ports
lsof -ti:8011 | xargs kill -9
lsof -ti:3082 | xargs kill -9

# Or kill all node/python processes
pkill -9 node
pkill -9 python
```

**Windows:**
```cmd
# Find and kill by port
netstat -ano | findstr :8011
taskkill /PID <PID> /F

netstat -ano | findstr :3082
taskkill /PID <PID> /F
```

---

## 🧪 Testing the Application

### Automated Tests

```bash
./test.sh
```

**What it tests:**
1. ✅ Backend health endpoint (`/healthz`)
2. ✅ Backend readiness endpoint (`/readyz`)
3. ✅ Backend CORS configuration
4. ✅ Coach API endpoint (`/api/coach/start`)
5. ✅ Frontend home page
6. ✅ Frontend coach page
7. ✅ Frontend static assets
8. ✅ WebSocket connectivity

**Exit codes:**
- `0` - All tests passed ✅
- `1` - Some tests failed ❌

### Manual Testing

```bash
# Test backend
curl http://localhost:8011/healthz
# Expected: {"status":"healthy"}

curl http://localhost:8011/readyz
# Expected: {"status":"ready"}

curl -X POST http://localhost:8011/api/coach/start \
  -H "Content-Type: application/json" \
  -d '{"parent_name":"Test"}'
# Expected: {"session_id":"..."}

# Test frontend
curl http://localhost:3082
# Expected: HTML with "Child Growth Assistant"

# Open in browser
open http://localhost:3082  # Mac
start http://localhost:3082  # Windows
xdg-open http://localhost:3082  # Linux
```

---

## 📊 Viewing Logs

### Real-time Logs

**Mac/Linux:**
```bash
# Both servers
tail -f backend.log frontend.log

# Backend only
tail -f backend.log

# Frontend only
tail -f frontend.log
```

**Windows:**
```cmd
REM View in separate command windows (opened by start.bat)
REM Or use PowerShell:
Get-Content backend.log -Wait -Tail 50
Get-Content frontend.log -Wait -Tail 50
```

### Search Logs

```bash
# Find errors
grep -i error backend.log frontend.log

# Find specific pattern
grep "session_id" backend.log

# Count occurrences
grep -c "WebSocket" backend.log
```

---

## 🔧 Common Troubleshooting

### Port Already in Use

```bash
# Mac/Linux
./stop.sh
./start.sh

# Or manually:
lsof -ti:8011 | xargs kill -9
lsof -ti:3082 | xargs kill -9
```

### Frontend Won't Start

```bash
cd frontend
rm -rf .next node_modules
npm install
PORT=3082 npm run dev
```

### Backend Won't Start

```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload
```

### Connection Refused

1. Check if servers are running:
   ```bash
   lsof -i:8011  # Backend
   lsof -i:3082  # Frontend
   ```

2. Check logs:
   ```bash
   tail -50 backend.log
   tail -50 frontend.log
   ```

3. Restart everything:
   ```bash
   ./stop.sh
   ./start.sh
   ```

---

## 📝 Development Workflow

### Typical Day

```bash
# Morning - Start servers
./start.sh

# Make changes to code (auto-reload enabled)
# Backend: Edit Python files → auto-reloads
# Frontend: Edit React/TS files → hot-reloads in browser

# Test your changes
./test.sh

# Check logs if needed
tail -f backend.log frontend.log

# Evening - Stop servers
# Press Ctrl+C in terminal with start.sh
# Or run: ./stop.sh
```

### Before Committing

```bash
# Run tests
./test.sh

# Check code quality
cd backend && python -m pytest
cd frontend && npm run lint
cd frontend && npm run type-check

# Run e2e tests
cd frontend && npm run test:e2e
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Start everything | `./start.sh` |
| Stop everything | `./stop.sh` or `Ctrl+C` |
| Test everything | `./test.sh` |
| View logs | `tail -f backend.log frontend.log` |
| Clean restart | `./stop.sh && rm *.log && ./start.sh` |
| Check ports | `lsof -i:8011 -i:3082` |
| API docs | http://localhost:8011/docs |
| Frontend | http://localhost:3082 |

---

## 📚 Additional Resources

- **[QUICKSTART.md](./QUICKSTART.md)** - Detailed setup guide
- **[README.md](./README.md)** - Project overview and student tasks
- **Backend API Docs:** http://localhost:8011/docs
- **Frontend Dev Docs:** https://nextjs.org/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com/

---

## 💡 Tips

1. **Always use `./start.sh`** - It handles dependencies and checks
2. **Check logs first** when debugging - `tail -f *.log`
3. **Use `./test.sh`** before committing - Catches issues early
4. **Keep servers running** - Auto-reload works for most changes
5. **Clean restart** if weird issues - `./stop.sh && ./start.sh`

---

## 🆘 Getting Help

If you encounter issues:

1. ✅ Check this document first
2. ✅ Read the logs: `tail -50 backend.log frontend.log`
3. ✅ Run tests: `./test.sh`
4. ✅ Try clean restart: `./stop.sh && ./start.sh`
5. ✅ Check [QUICKSTART.md](./QUICKSTART.md) troubleshooting section
6. ✅ Ask for help with logs and error messages

