# Exercise 2 — Chat App: Next.js + FastAPI (OpenAI proxy)

This exercise provides:
- a Python FastAPI backend that proxies `/chat` to OpenAI Chat Completions
- a minimal Next.js frontend that calls the backend and renders a chat UI

## Folder structure
- `backend/`: FastAPI app (`/chat`, `/health`)
- `frontend/`: Next.js app with a simple chat interface

## Backend setup

1) Configure env:
```bash
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_2/backend
cp .env.example .env   # then add your OPENAI_API_KEY
```

2) Run the server:
```bash
bash run.sh
# Server starts on http://localhost:8000
```

Health check:
```bash
curl http://localhost:8000/health
```

## Frontend setup

1) Set backend base URL:
```bash
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_2/frontend
echo "NEXT_PUBLIC_BACKEND_BASE=http://localhost:8000" > .env.local
```

2) Start dev server:
```bash
npm install
npm run dev -- --port 4000
```

Open: http://localhost:4000

## Notes
- CORS defaults to `http://localhost:4000`, configure more via `CORS_ORIGINS` in backend `.env`.
- The backend is a thin wrapper; the frontend never uses OpenAI directly.
- Update the model or temperature in the frontend call if desired.


