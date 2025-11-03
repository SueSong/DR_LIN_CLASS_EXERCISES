#!/bin/bash
set -x  # Show each command as it executes

echo "=================================="
echo "COMPLETE DELETE AND REINSTALL"
echo "=================================="
echo ""

# Step 1: Kill processes
echo ">>> Step 1: Killing processes..."
sudo killall -9 node 2>/dev/null || true
pkill -9 -f next 2>/dev/null || true
pkill -9 -f uvicorn 2>/dev/null || true
sleep 5

# Step 2: Delete NPX cache
echo ">>> Step 2: Deleting NPX cache..."
rm -rf ~/.npm/_npx
rm -rf /Users/jianlin/.npm/_npx

# Step 3: Delete frontend completely
echo ">>> Step 3: Deleting frontend..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/frontend
rm -rf .next
rm -rf node_modules
rm -rf package-lock.json
rm -rf .turbo
rm -rf .swc

# Step 4: Clean npm cache
echo ">>> Step 4: Cleaning npm cache..."
npm cache clean --force

# Step 5: Install
echo ">>> Step 5: Installing dependencies..."
npm install

# Step 6: Verify no npx cache
echo ">>> Step 6: Verifying..."
if [ -d ~/.npm/_npx ]; then
    echo "ERROR: NPX cache still exists!"
    exit 1
fi

if [ ! -d node_modules/next ]; then
    echo "ERROR: Next.js not installed!"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ REINSTALL COMPLETE"
echo "=================================="
echo ""
echo "Now starting servers..."
echo ""

# Step 7: Start backend
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/backend
if [ ! -d venv ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload > /tmp/ex11_backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Step 8: Start frontend
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/frontend
PORT=3082 npm run dev > /tmp/ex11_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "Waiting 20 seconds for servers to start..."
sleep 20

echo ""
echo "Testing..."
curl -s http://localhost:8011/healthz && echo " ✅ Backend OK"
curl -s -I http://localhost:3082 2>&1 | head -1
echo ""
echo "=================================="
echo "✅ SERVERS RUNNING"
echo ""
echo "Frontend: http://localhost:3082"
echo "Backend:  http://localhost:8011"
echo ""
echo "Logs:"
echo "  tail -f /tmp/ex11_backend.log"
echo "  tail -f /tmp/ex11_frontend.log"
echo ""
echo "Stop: kill $BACKEND_PID $FRONTEND_PID"
echo "=================================="

