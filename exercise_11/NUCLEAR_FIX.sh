#!/bin/bash

echo "🔥 NUCLEAR OPTION - Complete Reset"
echo "=================================="
echo ""
echo "This will FORCEFULLY:"
echo "  1. Kill ALL Node processes"
echo "  2. Delete NPX cache"
echo "  3. Delete EVERYTHING in frontend"
echo "  4. Reinstall from scratch"
echo ""

# 1. KILL EVERYTHING
echo "1️⃣  Killing all Node/Python processes..."
sudo killall -9 node 2>/dev/null || true
sudo killall -9 Python 2>/dev/null || true
sudo pkill -9 -f next 2>/dev/null || true
sudo pkill -9 -f uvicorn 2>/dev/null || true
sleep 5
echo "✅ All processes killed"

# 2. DELETE NPX CACHE
echo ""
echo "2️⃣  Deleting NPX cache..."
if [ -d ~/.npm/_npx ]; then
    rm -rf ~/.npm/_npx
    echo "✅ Deleted ~/.npm/_npx"
else
    echo "⚠️  No NPX cache found"
fi

# Also clear npm cache
npm cache clean --force 2>/dev/null || true
echo "✅ NPM cache cleared"

# 3. NUCLEAR DELETE FRONTEND
echo ""
echo "3️⃣  NUCLEAR DELETE of frontend..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/frontend
rm -rf .next
rm -rf node_modules
rm -rf package-lock.json
rm -rf .turbo
rm -rf .swc
echo "✅ Frontend completely cleaned"

# 4. FRESH INSTALL
echo ""
echo "4️⃣  Fresh install..."
npm install
echo "✅ Dependencies installed"

# 5. VERIFY NO NPX CACHE
echo ""
echo "5️⃣  Verifying npx cache is gone..."
if [ -d ~/.npm/_npx ]; then
    echo "❌ NPX CACHE STILL EXISTS! Deleting again..."
    rm -rf ~/.npm/_npx
else
    echo "✅ NPX cache confirmed gone"
fi

# 6. START BACKEND
echo ""
echo "6️⃣  Starting backend..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/backend

if [ ! -d venv ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload > /tmp/ex11_backend_$(date +%s).log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# 7. START FRONTEND (with explicit port to avoid conflicts)
echo ""
echo "7️⃣  Starting frontend on port 3082..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/frontend

# Use PORT environment variable to override package.json
PORT=3082 npm run dev > /tmp/ex11_frontend_$(date +%s).log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

# 8. WAIT AND TEST
echo ""
echo "⏳ Waiting 25 seconds for servers to fully start..."
for i in {25..1}; do
    printf "\r   %02d seconds remaining..." $i
    sleep 1
done
echo ""

# 9. TEST EVERYTHING
echo ""
echo "8️⃣  Testing..."
echo ""

# Test backend
echo -n "Backend health: "
if curl -s http://localhost:8011/healthz 2>&1 | grep -q "ok"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# Test frontend with actual content
echo -n "Frontend home: "
HTTP_HOME=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3082 2>&1)
if [ "$HTTP_HOME" = "200" ]; then
    echo "✅ OK (HTTP $HTTP_HOME)"
    
    # Check for webpack error in actual response
    RESPONSE=$(curl -s http://localhost:3082 2>&1 | head -100)
    if echo "$RESPONSE" | grep -q "webpack_modules"; then
        echo "⚠️  WARNING: Response contains webpack error!"
        echo ""
        echo "Checking for NPX path in logs..."
        LATEST_LOG=$(ls -t /tmp/ex11_frontend_*.log 2>/dev/null | head -1)
        if [ -n "$LATEST_LOG" ]; then
            if grep -q "jianlin/.npm/_npx" "$LATEST_LOG"; then
                echo "❌ NPX PATH STILL IN LOGS!"
                echo ""
                echo "Last 30 lines of log:"
                tail -30 "$LATEST_LOG"
            else
                echo "✅ No NPX path in logs"
            fi
        fi
    else
        echo "✅ No webpack errors detected"
    fi
else
    echo "❌ HTTP $HTTP_HOME"
fi

echo ""
echo "=================================="
echo "📍 URLs:"
echo "   Frontend: http://localhost:3082"
echo "   Backend:  http://localhost:8011"
echo ""
echo "📊 Latest logs:"
BACKEND_LOG=$(ls -t /tmp/ex11_backend_*.log 2>/dev/null | head -1)
FRONTEND_LOG=$(ls -t /tmp/ex11_frontend_*.log 2>/dev/null | head -1)
echo "   Backend:  tail -f $BACKEND_LOG"
echo "   Frontend: tail -f $FRONTEND_LOG"
echo ""
echo "🛑 Stop servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "$BACKEND_PID $FRONTEND_PID" > /tmp/ex11_pids.txt

# 10. FINAL CHECK
echo "🔍 Final NPX cache check..."
if [ -d ~/.npm/_npx ]; then
    echo "❌ WARNING: NPX cache recreated!"
    ls -la ~/.npm/_npx/
else
    echo "✅ NPX cache remains deleted"
fi

echo ""
echo "✨ Done! Open http://localhost:3082 in your browser"
echo ""

