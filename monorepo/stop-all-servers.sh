#!/bin/bash

# Stop All Servers Script for Exercise 5
# Gracefully stops all running services

echo "🛑 Stopping All Servers"
echo "======================="

# Function to kill process on port
kill_port() {
    local port=$1
    local service_name=$2
    local pid=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        echo "🔪 Stopping $service_name on port $port (PID: $pid)"
        kill -TERM $pid 2>/dev/null || true
        sleep 2
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            echo "🔨 Force stopping $service_name (PID: $pid)"
            kill -9 $pid 2>/dev/null || true
        fi
        echo "✅ $service_name stopped"
    else
        echo "ℹ️  No process found on port $port ($service_name)"
    fi
}

# Stop services by port
echo "🔍 Stopping services by port..."
kill_port 8001 "Trading Agent"
kill_port 8000 "Original API"
kill_port 3000 "Frontend"
kill_port 16686 "Jaeger"
kill_port 9090 "Prometheus"
kill_port 3001 "Grafana"

echo ""
echo "🐳 Stopping Docker services..."
docker-compose down --remove-orphans 2>/dev/null || echo "ℹ️  No Docker Compose services to stop"

echo ""
echo "🧹 Cleaning up log files..."
rm -f /tmp/trading-agent.log /tmp/api-server.log 2>/dev/null || true

echo ""
echo "✅ All servers stopped successfully!"
echo ""
echo "🚀 To start servers again:"
echo "  • Run: ./start-all-servers.sh"
echo "  • Or: npm run start:all"
