#!/bin/bash
# Start the streaming demo

echo "🚀 Starting Streaming Demo..."
echo ""

# Check if running from demo_streaming directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the demo_streaming directory"
    exit 1
fi

# Start backend
echo "📦 Starting backend on port 8100..."
cd backend
pip install -q -r requirements.txt 2>/dev/null
uvicorn app.main:app --reload --port 8100 > /tmp/demo-backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "📦 Starting frontend on port 3100..."
cd frontend
npm install --silent > /dev/null 2>&1
PORT=3100 npm run dev > /tmp/demo-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
cd ..

echo ""
echo "================================"
echo "🎉 Demo is ready!"
echo "================================"
echo ""
echo "📺 Open: http://localhost:3100"
echo "🔧 Backend API: http://localhost:8100"
echo ""
echo "Logs:"
echo "  Backend:  tail -f /tmp/demo-backend.log"
echo "  Frontend: tail -f /tmp/demo-frontend.log"
echo ""
echo "To stop: pkill -f 'uvicorn.*8100' && pkill -f 'next.*3100'"
echo ""

# Open browser (macOS)
sleep 3
open http://localhost:3100 2>/dev/null || echo "Please open http://localhost:3100 in your browser"

