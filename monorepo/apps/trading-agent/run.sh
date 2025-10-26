#!/bin/bash

# AI Trading Agent - Development Server
# Exercise 5: Stock Trading Agent with all Exercise 1-6 skills

set -e

echo "🤖 Starting AI Trading Agent (Exercise 5)..."
echo "Features: Typed Tools, Registry, Reliability, Observability, Permissions, Full Agent Flow"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create directories
mkdir -p reports data

# Set environment variables for development
export OTEL_SERVICE_NAME="trading-agent"
export OTEL_SERVICE_VERSION="1.0.0"
export OTEL_CONSOLE_EXPORT="true"
export DATABASE_URL="postgresql://trader:trading123@localhost:5432/trading_db"
export LLM_PROVIDER="openai"  # or "anthropic" or leave empty for mock
export REPORTS_DIR="reports"

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL connection..."
if ! python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('$DATABASE_URL'))" 2>/dev/null; then
    echo "⚠️  PostgreSQL not available - running with mock data"
    echo "   To use full database features:"
    echo "   1. Start observability stack: npm run observability:start"
    echo "   2. Wait for PostgreSQL to be ready"
else
    echo "✅ PostgreSQL connection successful"
fi

# Start the server
echo ""
echo "🌟 Starting Trading Agent API on http://localhost:8001"
echo "📊 API documentation: http://localhost:8001/docs"
echo "🔍 Health check: http://localhost:8001/health"
echo "🔧 Tools registry: http://localhost:8001/tools"
echo ""
echo "🎯 Exercise Demonstrations:"
echo "  1. Typed Tools: http://localhost:8001/demo/validate-input"
echo "  2. Tool Registry: http://localhost:8001/tools"
echo "  3. Reliability: Built into all tool calls"
echo "  4. Observability: http://localhost:16686 (Jaeger)"
echo "  5. Permissions: Enforced on all trading operations"
echo "  6. Full Agent Flow: http://localhost:8001/agent/auto-trade"
echo ""
echo "🚀 Run complete demo: python demo_all_exercises.py"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
