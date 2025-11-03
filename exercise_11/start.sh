#!/bin/bash

# Exercise 11 - Child Growth Assistant Startup Script
# This script starts both backend and frontend servers

set -e  # Exit on error

echo "🚀 Starting Exercise 11 - Child Growth Assistant"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down servers...${NC}"
    # Kill all child processes
    pkill -P $$ 2>/dev/null || true
    exit 0
}

# Register cleanup function
trap cleanup SIGINT SIGTERM EXIT

# Check if ports are already in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}❌ Port $port is already in use!${NC}"
        echo -e "${YELLOW}   Run: lsof -ti:$port | xargs kill -9${NC}"
        return 1
    fi
    return 0
}

echo "📋 Checking ports..."
if ! check_port 8011; then
    echo -e "${RED}Please free port 8011 and try again.${NC}"
    exit 1
fi

if ! check_port 3082; then
    echo -e "${RED}Please free port 3082 and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Ports are available${NC}"
echo ""

# ============================================
# Start Backend
# ============================================
echo -e "${BLUE}📦 Starting Backend Server...${NC}"
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
source venv/bin/activate
pip install -q -r requirements.txt

echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Start backend in background
uvicorn app.main:app --host 0.0.0.0 --port 8011 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo "   URL: http://localhost:8011"
echo "   Logs: $SCRIPT_DIR/backend.log"
echo ""

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8011/healthz > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start. Check backend.log${NC}"
        exit 1
    fi
    sleep 1
done

echo ""

# ============================================
# Start Frontend
# ============================================
echo -e "${BLUE}📦 Starting Frontend Server...${NC}"
cd "$SCRIPT_DIR/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

# Start frontend in background
PORT=3082 npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "   URL: http://localhost:3082"
echo "   Logs: $SCRIPT_DIR/frontend.log"
echo ""

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:3082 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is ready!${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}❌ Frontend failed to start. Check frontend.log${NC}"
        exit 1
    fi
    sleep 1
done

echo ""
echo "================================================"
echo -e "${GREEN}🎉 All servers are running!${NC}"
echo "================================================"
echo ""
echo -e "${BLUE}📱 Open your browser:${NC}"
echo "   👉 http://localhost:3082"
echo ""
echo -e "${BLUE}📊 Backend API:${NC}"
echo "   👉 http://localhost:8011"
echo "   👉 http://localhost:8011/docs (API Documentation)"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo "   Backend:  tail -f $SCRIPT_DIR/backend.log"
echo "   Frontend: tail -f $SCRIPT_DIR/frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Keep script running and show live logs
tail -f frontend.log backend.log &
wait

