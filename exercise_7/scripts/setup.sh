#!/bin/bash

# Exercise 6 RAG Chatbot Setup Script
# Comprehensive setup for the entire RAG system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Exercise 6: RAG Chatbot Setup"
echo "================================="
echo "Project Directory: $PROJECT_DIR"
echo ""

# =============================================================================
# PREREQUISITES CHECK
# =============================================================================

echo "📋 Checking Prerequisites..."
echo "----------------------------"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ All prerequisites are installed"
echo ""

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

echo "🌍 Setting up Environment..."
echo "----------------------------"

cd "$PROJECT_DIR"

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Created .env file from env.example"
    else
        echo "⚠️  No env.example found. You'll need to create .env manually."
    fi
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads temp logs data/samples backend/logs
echo "✅ Directories created"

# =============================================================================
# OPTIONAL: START TRADING AGENT (HOST PROCESS)
# =============================================================================

if [ -d "$PROJECT_DIR/../../monorepo/apps/trading-agent" ]; then
  echo "🟢 Starting trading-agent (port 8001) if not already running..."
  pushd "$PROJECT_DIR/../../monorepo/apps/trading-agent" >/dev/null
  if ! nc -z localhost 8001; then
    if [ -f "venv/bin/activate" ]; then
      source venv/bin/activate || true
    fi
    if [ -f requirements.txt ]; then
      pip install -q -r requirements.txt || true
    fi
    nohup python app.py > trading-agent.log 2>&1 &
    echo $! > trading-agent.pid
    echo "✅ trading-agent started (PID $(cat trading-agent.pid))"
  else
    echo "ℹ️  trading-agent already listening on 8001"
  fi
  popd >/dev/null
else
  echo "ℹ️  monorepo trading-agent not found; skipping host start"
fi

# =============================================================================
# DOCKER SERVICES SETUP
# =============================================================================

echo "🐳 Setting up Docker Services..."
echo "--------------------------------"

# Stop any existing services
echo "🛑 Stopping existing services..."
docker-compose down --remove-orphans 2>/dev/null || true

# Pull required images
echo "📦 Pulling Docker images..."
docker-compose pull || true

# Start infrastructure services first (database, chromadb, redis)
echo "🚀 Starting infrastructure services..."
docker-compose up -d postgres-rag chromadb redis-rag

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check service health
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres-rag pg_isready -U rag_user -d rag_chatbot; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
    exit 1
fi

# Check ChromaDB
if curl -s http://localhost:8000/api/v2/heartbeat > /dev/null; then
    echo "✅ ChromaDB is ready"
else
    echo "⚠️  ChromaDB might still be starting..."
fi

# Check Redis
if docker-compose exec -T redis-rag redis-cli --raw incr ping > /dev/null 2>&1; then
    echo "✅ Redis is ready"
else
    echo "⚠️  Redis might still be starting..."
fi

echo ""

# =============================================================================
# BACKEND SETUP
# =============================================================================

echo "🔧 Setting up Backend..."
echo "-----------------------"

cd "$PROJECT_DIR/backend"

# Create Python virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Backend setup completed"
echo ""

# =============================================================================
# FRONTEND SETUP
# =============================================================================

echo "🎨 Setting up Frontend..."
echo "------------------------"

# (monorepo admin/chat not used here)

echo ""

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

echo "📊 Initializing Database..."
echo "---------------------------"

cd "$PROJECT_DIR"

# Verify database tables
echo "🔍 Verifying database tables..."

if docker-compose exec -T postgres-rag psql -U rag_user -d rag_chatbot -c "\dt" > /dev/null 2>&1; then
    echo "✅ Database tables verified"
else
    echo "⚠️  Database tables verification failed"
fi

echo ""

# =============================================================================
# FINAL VERIFICATION
# =============================================================================

echo "🔍 Final Verification..."
echo "-----------------------"

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
sleep 20

# Check backend health
if curl -s http://localhost:8002/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend might still be starting..."
fi

# Check frontend service
if curl -s http://localhost:3002 > /dev/null; then
    echo "✅ Frontend is accessible"
else
    echo "⚠️  Frontend might still be starting..."
fi

echo ""

echo "🎉 Setup Completed Successfully!"
echo "================================"
echo ""

echo "🌐 Access URLs:"
echo "  • Agent Console:     http://localhost:3002/agent-console"
echo "  • Backend API:       http://localhost:8002"
echo "  • Trading Agent API: http://localhost:8001"
echo ""
