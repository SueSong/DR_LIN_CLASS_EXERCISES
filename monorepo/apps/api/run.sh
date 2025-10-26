#!/bin/bash

# AI Agent Training API - Development Server
# Run script for FastAPI backend with hot reload

set -e

echo "🚀 Starting AI Agent Training API..."

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

# Create data directory if it doesn't exist
mkdir -p data

# Set environment variables for development
export OTEL_SERVICE_NAME="ai-agent-training-api-dev"
export OTEL_SERVICE_VERSION="1.0.0"
export OTEL_CONSOLE_EXPORT="true"

# Start the server with hot reload
echo "🌟 Starting FastAPI server on http://localhost:8000"
echo "📊 API documentation available at http://localhost:8000/docs"
echo "🔍 Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
