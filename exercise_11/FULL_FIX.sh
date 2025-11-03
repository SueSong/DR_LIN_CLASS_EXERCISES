#!/bin/bash
set -e

echo "🔧 COMPLETE FIX SCRIPT FOR EXERCISE 11"
echo "======================================"

# Step 1: Clean npx cache
echo ""
echo "1️⃣  Removing npx cache..."
rm -rf ~/.npm/_npx
echo "✅ NPX cache cleared"

# Step 2: Kill all node processes
echo ""
echo "2️⃣  Killing all Node.js processes..."
killall -9 node 2>/dev/null || true
sleep 3
echo "✅ All Node processes killed"

# Step 3: Clean frontend
echo ""
echo "3️⃣  Cleaning frontend build artifacts..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/frontend
rm -rf .next node_modules package-lock.json
echo "✅ Frontend cleaned"

# Step 4: Install frontend dependencies
echo ""
echo "4️⃣  Installing frontend dependencies..."
npm install
echo "✅ Dependencies installed"

# Step 5: Start backend
echo ""
echo "5️⃣  Starting backend server..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/backend

# Create venv if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Start backend in background
uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload > /tmp/ex11_backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID, Port: 8011)"

# Step 6: Start frontend
echo ""
echo "6️⃣  Starting frontend server..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/frontend
PORT=3083 npm run dev > /tmp/ex11_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend starting (PID: $FRONTEND_PID, Port: 3083)"

# Wait for servers to start
echo ""
echo "⏳ Waiting 15 seconds for servers to initialize..."
sleep 15

# Test the servers
echo ""
echo "7️⃣  Testing servers..."
echo ""
echo "Testing backend health..."
curl -s http://localhost:8011/healthz && echo " ✅" || echo " ❌"

echo ""
echo "Testing frontend..."
curl -s -I http://localhost:3083 | head -1

echo ""
echo "Testing problem endpoint /coach/chat..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3083/coach/chat)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ /coach/chat returned HTTP 200"
else
    echo "❌ /coach/chat returned HTTP $HTTP_CODE"
    echo ""
    echo "Last 30 lines of frontend log:"
    tail -30 /tmp/ex11_frontend.log
fi

echo ""
echo "======================================"
echo "🎉 SETUP COMPLETE!"
echo ""
echo "📍 Frontend: http://localhost:3083"
echo "📍 Backend:  http://localhost:8011"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f /tmp/ex11_backend.log"
echo "   Frontend: tail -f /tmp/ex11_frontend.log"
echo ""
echo "🛑 To stop servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""

