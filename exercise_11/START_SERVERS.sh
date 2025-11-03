#!/bin/bash
set -e

echo "🚀 Starting Exercise 11 Servers"
echo "================================"

# Kill existing processes
echo "Stopping any existing servers..."
killall -9 node 2>/dev/null || true
pkill -9 -f "uvicorn.*8011" 2>/dev/null || true
sleep 2

# Start Backend
echo ""
echo "📦 Starting Backend (port 8011)..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload > /tmp/ex11_backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Start Frontend
echo ""
echo "🎨 Starting Frontend (port 3082)..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/frontend

PORT=3082 npm run dev > /tmp/ex11_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

# Wait and test
echo ""
echo "⏳ Waiting 10 seconds for servers to start..."
sleep 10

echo ""
echo "🧪 Testing servers..."
echo ""
echo -n "Backend health: "
curl -s http://localhost:8011/healthz | grep -q "ok" && echo "✅ OK" || echo "❌ FAILED"

echo -n "Frontend home: "
curl -s -I http://localhost:3082 2>&1 | head -1 | grep -q "200" && echo "✅ OK" || echo "❌ FAILED"

echo -n "Frontend /coach/chat: "
curl -s -I http://localhost:3082/coach/chat 2>&1 | head -1 | grep -q "200" && echo "✅ OK" || echo "⚠️  Check logs"

echo ""
echo "================================"
echo "✨ Servers are running!"
echo ""
echo "🌐 URLs:"
echo "   Frontend: http://localhost:3082"
echo "   Backend:  http://localhost:8011"
echo ""
echo "📊 Monitor logs:"
echo "   tail -f /tmp/ex11_backend.log"
echo "   tail -f /tmp/ex11_frontend.log"
echo ""
echo "🛑 Stop servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "PIDs saved to /tmp/ex11_pids.txt"
echo "$BACKEND_PID $FRONTEND_PID" > /tmp/ex11_pids.txt

