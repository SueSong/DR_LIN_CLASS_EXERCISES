#!/bin/bash

# Start Trading Agent Script
echo "🚀 Starting AI Trading Agent..."

# Navigate to trading agent directory
cd "$(dirname "$0")/apps/trading-agent"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements_simple.txt
    pip install jinja2
else
    echo "✅ Virtual environment found"
    source venv/bin/activate
fi

# Start the server
echo "🌐 Starting server on http://localhost:8001"
echo "💬 Chat UI will be available at: http://localhost:8001/"
echo "📚 API docs available at: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload
