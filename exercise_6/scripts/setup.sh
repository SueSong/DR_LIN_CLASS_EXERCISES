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
# DOCKER SERVICES SETUP
# =============================================================================

echo "🐳 Setting up Docker Services..."
echo "--------------------------------"

# Stop any existing services
echo "🛑 Stopping existing services..."
docker-compose down --remove-orphans 2>/dev/null || true

# Pull required images
echo "📦 Pulling Docker images..."
docker-compose pull

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
if curl -s http://localhost:8000/api/v1/heartbeat > /dev/null; then
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

# Setup Admin Console
if [ -d "$PROJECT_DIR/frontend/admin" ]; then
    echo "📱 Setting up Admin Console..."
    cd "$PROJECT_DIR/frontend/admin"
    
    if [ -f "package.json" ]; then
        npm install
        echo "✅ Admin Console dependencies installed"
    else
        echo "⚠️  Admin Console package.json not found"
    fi
fi

# Setup Chat Interface
if [ -d "$PROJECT_DIR/frontend/chat" ]; then
    echo "💬 Setting up Chat Interface..."
    cd "$PROJECT_DIR/frontend/chat"
    
    if [ -f "package.json" ]; then
        npm install
        echo "✅ Chat Interface dependencies installed"
    else
        echo "⚠️  Chat Interface package.json not found"
    fi
fi

echo ""

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

echo "📊 Initializing Database..."
echo "---------------------------"

cd "$PROJECT_DIR"

# The database should already be initialized by the init.sql script
# Let's verify the tables exist
echo "🔍 Verifying database tables..."

if docker-compose exec -T postgres-rag psql -U rag_user -d rag_chatbot -c "\dt" > /dev/null 2>&1; then
    echo "✅ Database tables verified"
else
    echo "⚠️  Database tables verification failed"
fi

echo ""

# =============================================================================
# SAMPLE DATA LOADING (Optional)
# =============================================================================

echo "📄 Loading Sample Data..."
echo "------------------------"

# Check if sample data should be loaded
if [ "${LOAD_SAMPLE_DATA:-true}" = "true" ]; then
    if [ -f "$PROJECT_DIR/data/samples/load_samples.py" ]; then
        cd "$PROJECT_DIR/backend"
        source venv/bin/activate
        python "$PROJECT_DIR/data/samples/load_samples.py"
        echo "✅ Sample data loaded"
    else
        echo "⚠️  Sample data script not found"
    fi
else
    echo "⏭️  Skipping sample data loading"
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

# Check frontend services
if curl -s http://localhost:3002 > /dev/null; then
    echo "✅ Admin Console is accessible"
else
    echo "⚠️  Admin Console might still be starting..."
fi

if curl -s http://localhost:3003 > /dev/null; then
    echo "✅ Chat Interface is accessible"
else
    echo "⚠️  Chat Interface might still be starting..."
fi

echo ""

# =============================================================================
# SUCCESS MESSAGE
# =============================================================================

echo "🎉 Setup Completed Successfully!"
echo "================================"
echo ""
echo "🌐 Access URLs:"
echo "  • Admin Console:     http://localhost:3002"
echo "  • Chat Interface:    http://localhost:3003"
echo "  • Backend API:       http://localhost:8002"
echo "  • API Documentation: http://localhost:8002/docs"
echo "  • ChromaDB:          http://localhost:8000"
echo ""
echo "📊 Database Access:"
echo "  • Host: localhost"
echo "  • Port: 5433"
echo "  • Database: rag_chatbot"
echo "  • User: rag_user"
echo "  • Password: rag_password_2024"
echo ""
echo "🚀 Next Steps:"
echo "  1. Open http://localhost:3002 to access the Admin Console"
echo "  2. Upload some documents to create your knowledge base"
echo "  3. Add Q&A pairs for direct question matching"
echo "  4. Test the chat interface at http://localhost:3003"
echo "  5. Explore the API documentation at http://localhost:8002/docs"
echo ""
echo "🛑 To stop all services: docker-compose down"
echo "🔄 To restart services: docker-compose up -d"
echo ""
echo "Happy chatting! 🤖"
