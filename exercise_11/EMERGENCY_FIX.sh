#!/bin/bash

echo "🚨 EMERGENCY FIX - Exercise 11"
echo "=============================="
echo ""
echo "This will:"
echo "1. Kill ALL node processes"
echo "2. Delete NPX cache completely"  
echo "3. Delete .next build cache"
echo "4. Fresh npm install"
echo "5. Start servers"
echo ""
read -p "Press ENTER to continue or Ctrl+C to cancel..."

# 1. Kill everything
echo ""
echo "1️⃣  Killing all Node and Python processes..."
killall -9 node 2>/dev/null || true
killall -9 Python 2>/dev/null || true
pkill -9 -f uvicorn 2>/dev/null || true
sleep 3
echo "✅ All processes killed"

# 2. Remove NPX cache (THE KEY FIX)
echo ""
echo "2️⃣  Removing NPX cache..."
if [ -d ~/.npm/_npx ]; then
    rm -rf ~/.npm/_npx
    echo "✅ NPX cache removed"
else
    echo "⚠️  No NPX cache found (this is good)"
fi

# 3. Clean frontend
echo ""
echo "3️⃣  Cleaning frontend..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/frontend
if [ -d .next ]; then
    rm -rf .next
    echo "✅ .next deleted"
fi
if [ -d node_modules ]; then
    rm -rf node_modules
    echo "✅ node_modules deleted"
fi
if [ -f package-lock.json ]; then
    rm -f package-lock.json
    echo "✅ package-lock.json deleted"
fi

# 4. Install
echo ""
echo "4️⃣  Installing dependencies (this may take a minute)..."
npm install > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ npm install successful"
else
    echo "❌ npm install failed"
    exit 1
fi

# 5. Start backend
echo ""
echo "5️⃣  Starting backend..."
cd ../backend
if [ ! -d venv ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

nohup uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload > /tmp/ex11_backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# 6. Start frontend
echo ""
echo "6️⃣  Starting frontend..."
cd ../frontend
nohup npm run dev > /tmp/ex11_frontend_$(date +%s).log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend starting (PID: $FRONTEND_PID)"

# Wait
echo ""
echo "⏳ Waiting 20 seconds for servers to start..."
sleep 20

# Test
echo ""
echo "7️⃣  Testing endpoints..."
echo ""

# Test backend
if curl -s http://localhost:8011/healthz | grep -q "ok"; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

# Test frontend
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3082 2>&1)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Frontend home page OK (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "❌ Frontend not responding (check if port 3082 is blocked)"
else
    echo "⚠️  Frontend returned HTTP $HTTP_CODE"
fi

echo ""
echo "=============================="
echo "📍 URLs:"
echo "   Frontend: http://localhost:3082"
echo "   Backend:  http://localhost:8011"
echo ""
echo "📊 Check logs:"
echo "   tail -f /tmp/ex11_backend.log"
echo "   tail -f /tmp/ex11_frontend_*.log"
echo ""
echo "🛑 Stop servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""

