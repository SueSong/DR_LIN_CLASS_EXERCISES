#!/bin/bash

# Complete Server Startup Script for Exercise 5 (Unix/Linux/macOS)
# Starts all servers in the correct order with proper error handling

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "🚀 Complete Server Startup for Exercise 5"
echo "=========================================="
echo "Project Directory: $PROJECT_DIR"
echo ""

# =============================================================================
# PREREQUISITES CHECK
# =============================================================================

echo "📋 Prerequisites Check"
echo "====================="

# Check if we're in the monorepo directory
if [ ! -f "package.json" ]; then
    echo "❌ Not in monorepo directory. Please run this from the monorepo root."
    echo "Current directory: $(pwd)"
    echo "Expected files: package.json, docker-compose.yml"
    exit 1
fi

echo "✅ In monorepo directory: $(pwd)"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js is available ($(node --version))"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python is available ($(python3 --version))"
echo ""

# =============================================================================
# STOP EXISTING SERVERS
# =============================================================================

echo "🛑 Stopping any existing servers..."
echo "==================================="

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        echo "🔪 Killing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Kill processes on our target ports
for port in 8000 8001 3000 16686 9090 5432 6379; do
    kill_port $port
done

# Stop docker-compose services (if any)
docker-compose down --remove-orphans 2>/dev/null || true

echo "✅ Existing servers stopped"
echo ""

# =============================================================================
# START OBSERVABILITY STACK
# =============================================================================

echo "🔭 1. Starting Observability Stack (Jaeger, Prometheus, Grafana)"
echo "================================================================"

if [ -f "setup-observability.sh" ]; then
    chmod +x setup-observability.sh
    if ./setup-observability.sh; then
        echo "✅ Observability stack started successfully"
        OBSERVABILITY_FAILED=0
    else
        echo "❌ Failed to start observability stack"
        echo "⚠️  Continuing without observability..."
        OBSERVABILITY_FAILED=1
    fi
else
    echo "⚠️  setup-observability.sh not found, starting Docker services directly..."
    docker-compose up -d jaeger prometheus grafana 2>/dev/null || true
    OBSERVABILITY_FAILED=1
fi

echo ""
echo "⏳ Waiting 10 seconds for observability services to stabilize..."
sleep 10
echo ""

# =============================================================================
# START TRADING AGENT SERVER
# =============================================================================

echo "🎯 2. Starting Trading Agent Server (Exercise 5)"
echo "==============================================="

# Check if trading agent directory exists
if [ ! -d "apps/trading-agent" ]; then
    echo "❌ Trading agent directory not found: apps/trading-agent"
    exit 1
fi

# Start trading agent in background
echo "🚀 Starting Trading Agent..."
if [ -f "start-trading.sh" ]; then
    chmod +x start-trading.sh
    nohup ./start-trading.sh > /tmp/trading-agent.log 2>&1 &
    TRADING_PID=$!
    echo "📝 Trading Agent started with PID: $TRADING_PID (logs: /tmp/trading-agent.log)"
else
    # Fallback to npm script
    nohup npm run start:trading > /tmp/trading-agent.log 2>&1 &
    TRADING_PID=$!
    echo "📝 Trading Agent started with PID: $TRADING_PID (logs: /tmp/trading-agent.log)"
fi

# Wait for trading agent to start
echo "⏳ Waiting for Trading Agent to start..."
sleep 15

# Check if trading agent is running
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Trading Agent is running at http://localhost:8001"
    TRADING_STATUS="✅ Running"
else
    echo "⚠️  Trading Agent might still be starting... (check logs: tail -f /tmp/trading-agent.log)"
    TRADING_STATUS="⚠️ Starting"
fi

echo ""

# =============================================================================
# START ORIGINAL API SERVER (OPTIONAL)
# =============================================================================

echo "🔧 3. Starting Original API Server (Exercise 1-4) - Optional"
echo "==========================================================="

read -p "Start Original API Server? (y/n): " -n 1 -r START_API
echo ""

if [[ $START_API =~ ^[Yy]$ ]]; then
    echo "🚀 Starting Original API..."
    
    # Check if API directory exists
    if [ -d "apps/api" ]; then
        cd apps/api
        
        # Check if virtual environment exists
        if [ ! -d "venv" ]; then
            echo "📦 Creating virtual environment for API..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment and start server
        source venv/bin/activate
        
        # Install dependencies if needed
        if [ ! -f "venv/installed" ]; then
            echo "📚 Installing API dependencies..."
            pip install --upgrade pip
            pip install -r requirements.txt 2>/dev/null || echo "⚠️ Some dependencies might be missing"
            touch venv/installed
        fi
        
        # Start API server in background
        nohup python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload > /tmp/api-server.log 2>&1 &
        API_PID=$!
        echo "📝 Original API started with PID: $API_PID (logs: /tmp/api-server.log)"
        
        cd "$PROJECT_DIR"
        
        # Wait for API to start
        echo "⏳ Waiting for Original API to start..."
        sleep 10
        
        # Check if API is running
        if curl -s http://localhost:8000/health > /dev/null; then
            echo "✅ Original API is running at http://localhost:8000"
            API_STATUS="✅ Running"
        else
            echo "⚠️  Original API might still be starting... (check logs: tail -f /tmp/api-server.log)"
            API_STATUS="⚠️ Starting"
        fi
    else
        echo "❌ API directory not found: apps/api"
        API_STATUS="❌ Not found"
    fi
else
    echo "⏭️  Skipping Original API Server"
    API_STATUS="⏭️ Skipped"
fi

echo ""

# =============================================================================
# DISPLAY ACCESS INFORMATION
# =============================================================================

echo "🎮 Server Access Information"
echo "============================"

echo ""
echo "🎯 Main Services:"
echo "  • Trading Agent Chat UI:    http://localhost:8001"
echo "  • Trading Agent API Docs:   http://localhost:8001/docs"
echo "  • Trading Agent Health:     http://localhost:8001/health"

if [[ $START_API =~ ^[Yy]$ ]]; then
    echo "  • Original API Docs:        http://localhost:8000/docs"
    echo "  • Original API Health:      http://localhost:8000/health"
fi

if [ $OBSERVABILITY_FAILED -eq 0 ]; then
    echo ""
    echo "📊 Observability Services:"
    echo "  • Jaeger Tracing UI:        http://localhost:16686"
    echo "  • Prometheus Metrics:       http://localhost:9090"
    echo "  • Grafana Dashboards:       http://localhost:3001 (admin/admin)"
fi

echo ""
echo "📊 Service Status:"
echo "  • Trading Agent:            $TRADING_STATUS"
if [[ $START_API =~ ^[Yy]$ ]]; then
    echo "  • Original API:             $API_STATUS"
fi
if [ $OBSERVABILITY_FAILED -eq 0 ]; then
    echo "  • Observability Stack:      ✅ Running"
else
    echo "  • Observability Stack:      ⚠️ Issues detected"
fi

echo ""
echo "🧪 Quick Test Commands:"
echo "  # Test Trading Agent"
echo "  curl http://localhost:8001/health"
echo ""
echo "  # Get Stock Quote"
echo "  curl -X POST http://localhost:8001/quotes \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"symbols\":[\"AAPL\"],\"user_id\":\"test\"}'"
echo ""
echo "  # Execute Trade"
echo "  curl -X POST http://localhost:8001/trades \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"symbol\":\"AAPL\",\"action\":\"BUY\",\"amount\":1000,\"user_id\":\"test\"}'"

echo ""
echo "📝 Log Files:"
echo "  • Trading Agent logs:       tail -f /tmp/trading-agent.log"
if [[ $START_API =~ ^[Yy]$ ]]; then
    echo "  • Original API logs:        tail -f /tmp/api-server.log"
fi

echo ""
echo "🎉 Exercise 5 Setup Complete!"
echo "============================="
echo ""
echo "🚀 Ready to demo:"
echo "  1. Open http://localhost:8001 for the Trading Agent Chat UI"
echo "  2. Try stock quotes, trading, and AI recommendations"
if [ $OBSERVABILITY_FAILED -eq 0 ]; then
    echo "  3. View traces at http://localhost:16686 (search for 'trading-agent' service)"
fi
echo "  4. All 6 exercises are implemented and ready for demonstration"

echo ""
echo "🛑 To stop all servers:"
echo "  • Press Ctrl+C in this terminal"
echo "  • Or run: ./stop-all-servers.sh"
echo "  • Or run: docker-compose down"

# =============================================================================
# CLEANUP FUNCTION
# =============================================================================

cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    
    # Kill background processes
    if [ -n "$TRADING_PID" ]; then
        kill $TRADING_PID 2>/dev/null || true
    fi
    
    if [ -n "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    
    # Kill processes on ports
    for port in 8000 8001; do
        kill_port $port
    done
    
    # Stop Docker services
    docker-compose down --remove-orphans 2>/dev/null || true
    
    echo "✅ All servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo ""
echo "🌐 Opening Trading Agent Chat UI in browser..."
sleep 2

# Open browser (works on macOS and most Linux distributions)
if command -v open &> /dev/null; then
    open http://localhost:8001
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8001
else
    echo "💡 Please open http://localhost:8001 in your browser"
fi

echo ""
echo "🎯 Trading Agent Chat UI should open in your browser!"
echo "Keep this terminal open to monitor server status."
echo "Press Ctrl+C to stop all servers."
echo ""

# Keep script running to maintain background processes
while true; do
    sleep 10
    
    # Check if services are still running
    if ! curl -s http://localhost:8001/health > /dev/null; then
        echo "⚠️  Trading Agent appears to be down"
    fi
    
    if [[ $START_API =~ ^[Yy]$ ]] && ! curl -s http://localhost:8000/health > /dev/null; then
        echo "⚠️  Original API appears to be down"
    fi
done
