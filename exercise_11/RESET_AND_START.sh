#!/bin/bash
set -e

echo "🧹 COMPLETE RESET - Exercise 11"
echo "==============================="

# Step 1: Kill everything
echo ""
echo "Step 1: Stopping all servers..."
killall -9 node 2>/dev/null || true
pkill -9 -f "uvicorn.*8011" 2>/dev/null || true
sleep 3
echo "✅ Servers stopped"

# Step 2: Remove npx cache
echo ""
echo "Step 2: Removing NPX cache..."
rm -rf ~/.npm/_npx
echo "✅ NPX cache cleared"

# Step 3: Clean frontend
echo ""
echo "Step 3: Cleaning frontend..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/frontend
rm -rf .next node_modules package-lock.json
echo "✅ Frontend cleaned"

# Step 4: Fresh install
echo ""
echo "Step 4: Installing dependencies..."
npm install
echo "✅ Dependencies installed"

# Step 5: Start backend
echo ""
echo "Step 5: Starting backend (port 8011)..."
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

# Step 6: Start frontend
echo ""
echo "Step 6: Starting frontend (port 3082)..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/frontend
PORT=3082 npm run dev > /tmp/ex11_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

# Wait
echo ""
echo "⏳ Waiting 15 seconds for servers to initialize..."
for i in {15..1}; do
    echo -n "$i... "
    sleep 1
done
echo ""

# Test
echo ""
echo "Step 7: Testing servers..."
echo ""

echo -n "Backend health check: "
if curl -s http://localhost:8011/healthz | grep -q "ok"; then
    echo "✅ PASS"
else
    echo "❌ FAIL"
    echo "Backend log:"
    tail -20 /tmp/ex11_backend.log
fi

echo -n "Frontend home page: "
HTTP_HOME=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3082 2>&1)
if [ "$HTTP_HOME" = "200" ]; then
    echo "✅ PASS (HTTP $HTTP_HOME)"
else
    echo "❌ FAIL (HTTP $HTTP_HOME)"
fi

echo -n "Frontend /coach page: "
HTTP_COACH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3082/coach 2>&1)
if [ "$HTTP_COACH" = "200" ]; then
    echo "✅ PASS (HTTP $HTTP_COACH)"
else
    echo "❌ FAIL (HTTP $HTTP_COACH)"
fi

echo -n "Frontend /coach/chat page: "
HTTP_CHAT=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3082/coach/chat 2>&1)
if [ "$HTTP_CHAT" = "200" ]; then
    echo "✅ PASS (HTTP $HTTP_CHAT)"
else
    echo "⚠️  HTTP $HTTP_CHAT"
    echo ""
    echo "Last 30 lines of frontend log:"
    tail -30 /tmp/ex11_frontend.log
fi

echo ""
echo "==============================="
echo "🎉 SETUP COMPLETE!"
echo ""
echo "🌐 Open in browser:"
echo "   http://localhost:3082"
echo ""
echo "📊 Monitor logs:"
echo "   Backend:  tail -f /tmp/ex11_backend.log"
echo "   Frontend: tail -f /tmp/ex11_frontend.log"
echo ""
echo "🛑 Stop servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "PIDs: $BACKEND_PID (backend) $FRONTEND_PID (frontend)" > /tmp/ex11_pids.txt

