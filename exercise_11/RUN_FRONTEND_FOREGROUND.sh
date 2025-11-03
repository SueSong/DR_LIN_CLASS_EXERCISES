#!/bin/bash

echo "🔥 FINAL FIX - Running in foreground so we can see errors"
echo "=========================================================="

# 1. Kill everything
echo "Step 1: Killing all processes..."
sudo killall -9 node 2>/dev/null || true
sleep 5

# 2. Delete NPX cache
echo "Step 2: Deleting NPX cache..."
rm -rf ~/.npm/_npx
rm -rf /Users/jianlin/.npm/_npx

# 3. Delete frontend
echo "Step 3: Deleting .next..."
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_11/frontend
rm -rf .next

# 4. Verify
echo "Step 4: Verifying cleanup..."
if [ -d ~/.npm/_npx ]; then
    echo "ERROR: NPX cache still exists!"
    exit 1
fi

if [ -d .next ]; then
    echo "ERROR: .next still exists!"
    exit 1
fi

echo "✅ Cleanup complete"
echo ""
echo "Step 5: Starting frontend on port 3082..."
echo "Press Ctrl+C to stop"
echo ""

PORT=3082 npm run dev

