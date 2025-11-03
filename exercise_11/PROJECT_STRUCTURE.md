# Exercise 11 - Project Structure

```
exercise_11/
│
├── 📜 Scripts & Documentation
│   ├── start.sh                    # 🚀 Start all servers (Mac/Linux)
│   ├── start.bat                   # 🚀 Start all servers (Windows)
│   ├── stop.sh                     # 🛑 Stop all servers (Mac/Linux)
│   ├── stop.bat                    # 🛑 Stop all servers (Windows)
│   ├── test.sh                     # 🧪 Test suite
│   ├── README.md                   # 📚 Main documentation
│   ├── QUICKSTART.md              # 🏃 Quick start guide
│   └── SCRIPTS.md                  # 📖 Scripts reference
│
├── 🔧 Backend (FastAPI - Port 8011)
│   ├── app/
│   │   ├── main.py                # Main FastAPI app
│   │   ├── api/
│   │   │   ├── coach.py          # Coach endpoints
│   │   │   └── websocket.py      # WebSocket handler
│   │   └── __init__.py
│   ├── requirements.txt           # Python dependencies
│   └── venv/                      # Virtual environment (auto-created)
│
├── 🎨 Frontend (Next.js - Port 3082)
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # Home page
│   │   │   ├── layout.tsx        # Root layout
│   │   │   ├── globals.css       # Global styles
│   │   │   └── coach/
│   │   │       ├── page.tsx      # Parent sign-in
│   │   │       └── chat/
│   │   │           └── page.tsx  # Chat interface
│   │   └── lib/
│   │       └── coachApi.ts       # API client
│   ├── e2e/
│   │   └── assistant.spec.ts     # Playwright tests
│   ├── package.json               # Node dependencies
│   ├── tailwind.config.ts        # Tailwind config
│   ├── postcss.config.js         # PostCSS config
│   ├── tsconfig.json             # TypeScript config
│   ├── next.config.js            # Next.js config
│   ├── playwright.config.ts      # Playwright config
│   ├── node_modules/             # Dependencies (auto-created)
│   └── .next/                    # Build output (auto-created)
│
├── 🧪 Load Testing
│   ├── k6/
│   │   └── coach_scenario.js     # K6 load test
│   └── locust/
│       ├── locustfile.py         # Locust load test
│       └── requirements.txt      # Python dependencies
│
└── 📝 Generated Files (auto-created by scripts)
    ├── backend.log               # Backend logs
    └── frontend.log              # Frontend logs
```

---

## 📦 Key Components

### Backend (`/backend`)
- **FastAPI** framework for REST API and WebSocket
- **Health checks** at `/healthz` and `/readyz`
- **Coach API** at `/api/coach/start`
- **WebSocket** at `/ws/coach/{session_id}`
- **Auto-reload** enabled for development

### Frontend (`/frontend`)
- **Next.js 14** with App Router
- **React 18** for UI components
- **Tailwind CSS** for styling
- **TypeScript** for type safety
- **WebSocket** for real-time chat
- **Hot-reload** enabled for development

### Testing
- **Playwright** for end-to-end tests
- **K6** for load testing (HTTP & WebSocket)
- **Locust** for load testing (HTTP)
- **Manual test script** (`test.sh`)

---

## 🔄 Data Flow

```
┌─────────────┐         HTTP/WS          ┌─────────────┐
│             │ ───────────────────────> │             │
│  Browser    │   POST /api/coach/start  │   Backend   │
│ (Port 3082) │ <─────────────────────── │ (Port 8011) │
│             │   WebSocket /ws/coach    │             │
└─────────────┘                          └─────────────┘
      │                                         │
      │                                         │
      v                                         v
┌─────────────┐                          ┌─────────────┐
│   React     │                          │   FastAPI   │
│   Pages     │                          │   Routes    │
└─────────────┘                          └─────────────┘
```

### Request Flow

1. **User visits** http://localhost:3082
2. **Next.js serves** React app
3. **User enters name** → POST to `/api/coach/start`
4. **Backend returns** `session_id`
5. **Frontend connects** to WebSocket `/ws/coach/{session_id}`
6. **User sends message** → WebSocket
7. **Backend processes** and sends advice
8. **Frontend displays** advice in real-time

---

## 🎯 Development Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3082 | http://localhost:3082 |
| Backend API | 8011 | http://localhost:8011 |
| API Docs | 8011 | http://localhost:8011/docs |
| WebSocket | 8011 | ws://localhost:8011/ws/coach/{id} |

---

## 📁 File Purposes

### Startup Scripts
- `start.sh` - Automated startup for Mac/Linux
- `start.bat` - Automated startup for Windows
- Handles dependencies, health checks, logging

### Stop Scripts
- `stop.sh` - Kill all servers on Mac/Linux
- `stop.bat` - Kill all servers on Windows
- Cleans up ports 8011 and 3082

### Test Script
- `test.sh` - Automated testing
- Validates backend, frontend, WebSocket
- Returns 0 if all pass, 1 if any fail

### Documentation
- `README.md` - Project overview, Week 8 tasks
- `QUICKSTART.md` - Setup guide, troubleshooting
- `SCRIPTS.md` - Scripts reference (this file)
- `ARCHITECTURE.md` - (for students to create)

---

## 🔨 Build Artifacts

### Backend
```
backend/
├── venv/              # Python virtual environment
│   ├── bin/           # Python, pip, uvicorn
│   └── lib/           # Installed packages
└── __pycache__/       # Compiled Python files
```

### Frontend
```
frontend/
├── node_modules/      # npm packages
├── .next/             # Next.js build output
│   ├── cache/         # Build cache
│   ├── server/        # Server bundles
│   └── static/        # Static assets
└── playwright-report/ # Test reports
```

### Logs
```
exercise_11/
├── backend.log        # Backend stdout/stderr
└── frontend.log       # Frontend stdout/stderr
```

---

## 🧹 Cleaning Up

### Full Clean
```bash
# Stop servers
./stop.sh

# Remove all build artifacts
rm -rf backend/venv backend/__pycache__
rm -rf frontend/.next frontend/node_modules
rm -rf *.log

# Fresh install
./start.sh
```

### Partial Clean
```bash
# Frontend only
cd frontend
rm -rf .next
npm install
cd ..

# Backend only
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

---

## 📚 Dependencies

### Backend Python Packages
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
websockets==12.0
pydantic==2.5.0
```

### Frontend npm Packages
```
next@14.1.0
react@18.2.0
react-dom@18.2.0
typescript@5.3.3
tailwindcss@3.4.1
@playwright/test@1.40.1
axios@1.6.2
lucide-react@0.292.0
```

### Load Testing
```
k6 (binary download)
locust==2.29.1 (Python)
```

---

## 🎓 Week 8 Tasks Location

Students will create these files:

```
exercise_11/
├── docs/
│   └── safety_scope.md           # Task 1: Safety policy
├── config/
│   └── safety_policy.json        # Task 1: Safety config
├── rag/
│   ├── ingest.py                 # Task 2: RAG ingestion
│   └── index.json                # Task 2: RAG index
├── observability/
│   └── dashboards/               # Task 7: Observability
├── .github/
│   └── workflows/
│       ├── ci.yml                # Task 6: CI pipeline
│       └── cd.yml                # Task 6: CD pipeline
├── Dockerfile                    # Task 5: Backend container
├── Dockerfile.web                # Task 5: Frontend container
├── docker-compose.yml            # Task 5: Orchestration
└── prompts/
    └── child_coach_v1.json       # Task 9: Prompt versioning
```

See [README.md](./README.md) for complete task descriptions.

