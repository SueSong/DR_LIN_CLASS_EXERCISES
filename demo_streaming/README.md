# 🎬 Streaming UI Demo - Class 7

This demo showcases different streaming patterns for AI applications:
- **Server-Sent Events (SSE)** - One-way streaming from server
- **WebSockets** - Bidirectional real-time communication
- **Session Restoration** - Deterministic replay
- **Role-Based Actions** - Different capabilities per role

## 🚀 Quick Start

```bash
# Backend
cd demo_streaming/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8100

# Frontend
cd demo_streaming/frontend
npm install
PORT=3100 npm run dev
```

Then open: `http://localhost:3100`

## 📊 Features Demonstrated

### 1. **SSE Mode**
- Server pushes updates to client
- No client → server messages during stream
- Automatic reconnection
- Perfect for AI completions

### 2. **WebSocket Mode**
- Bidirectional communication
- Real-time updates both ways
- Perfect for interactive chat

### 3. **Session Restoration**
- All messages stored
- Click "Restore Session" to replay
- Deterministic - same order every time

### 4. **Role-Based Actions**
- **User Role**: Can chat, view history
- **Agent Role**: Can chat, interrupt, prioritize
- **Admin Role**: All features + session management

## 🎯 Demo Script

1. Start in SSE mode → Send a message → Watch streaming
2. Switch to WebSocket mode → Send message → See difference
3. Add more messages in both modes
4. Click "Restore Session" → Watch replay
5. Switch roles → See different actions available

