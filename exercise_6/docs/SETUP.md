# 🚀 Exercise 6 Setup Guide

Complete setup instructions for the RAG-Enhanced Chatbot system.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

### Required Software
- **Docker Desktop** 4.0+ - [Download](https://www.docker.com/products/docker-desktop/)
- **Node.js** 18+ - [Download](https://nodejs.org/)
- **Python** 3.8+ - [Download](https://www.python.org/)
- **Git** - [Download](https://git-scm.com/)

### Optional (Recommended)
- **VS Code** with Python and Docker extensions
- **Postman** or similar API testing tool
- **pgAdmin** for database management

## 🎯 Quick Start (5 Minutes)

### 1. Clone and Navigate
```bash
cd exercise_6
```

### 2. Environment Setup
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your API keys (optional for basic functionality)
nano .env
```

### 3. Run Setup Script
```bash
# Make script executable
chmod +x scripts/setup.sh

# Run complete setup
./scripts/setup.sh
```

### 4. Access Applications
- **Admin Console**: http://localhost:3002
- **Chat Interface**: http://localhost:3003
- **API Documentation**: http://localhost:8002/docs

## 🔧 Manual Setup (Step by Step)

If you prefer manual setup or encounter issues with the automated script:

### Step 1: Environment Configuration

1. **Copy Environment File**:
   ```bash
   cp env.example .env
   ```

2. **Edit Configuration** (optional):
   ```bash
   # Add your API keys for enhanced functionality
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ```

### Step 2: Infrastructure Services

1. **Start Database Services**:
   ```bash
   docker-compose up -d postgres-rag chromadb redis-rag
   ```

2. **Verify Services**:
   ```bash
   # Check PostgreSQL
   docker-compose exec postgres-rag pg_isready -U rag_user -d rag_chatbot
   
   # Check ChromaDB
   curl http://localhost:8000/api/v1/heartbeat
   
   # Check Redis
   docker-compose exec redis-rag redis-cli ping
   ```

### Step 3: Backend Setup

1. **Navigate to Backend**:
   ```bash
   cd backend
   ```

2. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Start Backend**:
   ```bash
   # Option 1: Direct run
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Option 2: Docker
   cd ..
   docker-compose up -d backend
   ```

### Step 4: Frontend Setup

1. **Admin Console**:
   ```bash
   cd frontend/admin
   npm install
   npm start  # Runs on port 3000, mapped to 3002 in Docker
   ```

2. **Chat Interface**:
   ```bash
   cd frontend/chat
   npm install
   npm start  # Runs on port 3000, mapped to 3003 in Docker
   ```

3. **Docker Alternative**:
   ```bash
   # Start both frontends with Docker
   docker-compose up -d admin-frontend chat-frontend
   ```

### Step 5: Verification

1. **Health Checks**:
   ```bash
   # Backend health
   curl http://localhost:8002/health
   
   # Detailed health with dependencies
   curl http://localhost:8002/health/detailed
   ```

2. **Test API**:
   ```bash
   # List knowledge bases
   curl http://localhost:8002/api/v1/knowledge-bases
   
   # API documentation
   open http://localhost:8002/docs
   ```

## 🐳 Docker Commands Reference

### Basic Operations
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend

# Rebuild and start
docker-compose up -d --build
```

### Development Commands
```bash
# Start with file watching (development)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Run backend in development mode
docker-compose exec backend uvicorn app.main:app --reload

# Access database
docker-compose exec postgres-rag psql -U rag_user -d rag_chatbot
```

### Cleanup Commands
```bash
# Remove all containers and volumes
docker-compose down -v --remove-orphans

# Remove all images
docker-compose down --rmi all

# Full cleanup (careful!)
docker system prune -a --volumes
```

## 🔧 Port Configuration

The system uses the following ports (configured to avoid conflicts):

| Service | Internal Port | External Port | Description |
|---------|---------------|---------------|-------------|
| PostgreSQL | 5432 | 5433 | Database with pgvector |
| ChromaDB | 8000 | 8000 | Vector similarity search |
| Redis | 6379 | 6380 | Caching layer |
| Backend API | 8000 | 8002 | FastAPI application |
| Admin Console | 3000 | 3002 | React admin interface |
| Chat Interface | 3000 | 3003 | React chat interface |

### Changing Ports

Edit `docker-compose.yml` to change port mappings:

```yaml
services:
  postgres-rag:
    ports:
      - "5434:5432"  # Change external port to 5434
```

## 🌍 Environment Variables

### Required Variables
```bash
# Database
DATABASE_URL=postgresql://rag_user:rag_password_2024@localhost:5433/rag_chatbot

# Vector Database
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
```

### Optional Variables
```bash
# LLM APIs (for enhanced functionality)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Performance Tuning
CHUNK_SIZE=1000
MAX_RETRIEVED_CHUNKS=5
SIMILARITY_THRESHOLD=0.7
```

### Development Variables
```bash
# Development settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
ENABLE_API_DOCS=true
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port
lsof -i :5432  # or netstat -tulpn | grep 5432

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

#### 2. Docker Permission Issues
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker-compose up -d
```

#### 3. Database Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose ps postgres-rag

# Check logs
docker-compose logs postgres-rag

# Restart database
docker-compose restart postgres-rag
```

#### 4. ChromaDB Not Responding
```bash
# Check ChromaDB status
curl http://localhost:8000/api/v1/heartbeat

# Restart ChromaDB
docker-compose restart chromadb

# Check logs
docker-compose logs chromadb
```

#### 5. Frontend Build Failures
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+
```

### Performance Issues

#### 1. Slow Database Queries
```bash
# Check database performance
docker-compose exec postgres-rag psql -U rag_user -d rag_chatbot -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;"
```

#### 2. High Memory Usage
```bash
# Check container resource usage
docker stats

# Limit container memory
# Add to docker-compose.yml:
# mem_limit: 1g
```

#### 3. Slow Vector Search
```bash
# Check ChromaDB collection size
curl http://localhost:8000/api/v1/collections/rag_documents

# Consider increasing similarity threshold
# Edit .env: SIMILARITY_THRESHOLD=0.8
```

### Logs and Debugging

#### 1. View All Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

#### 2. Backend Debugging
```bash
# Enable debug mode
# Edit .env: DEBUG=true, LOG_LEVEL=DEBUG

# Access backend container
docker-compose exec backend bash

# Run backend manually
docker-compose exec backend python -m app.main
```

#### 3. Database Debugging
```bash
# Access PostgreSQL
docker-compose exec postgres-rag psql -U rag_user -d rag_chatbot

# Check tables
\dt

# Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## 🔒 Security Considerations

### Development Environment
- Default passwords are used for convenience
- API documentation is enabled
- CORS is permissive
- Debug mode is enabled

### Production Deployment
Before deploying to production:

1. **Change Default Passwords**:
   ```bash
   # Generate secure passwords
   openssl rand -base64 32
   ```

2. **Disable Debug Features**:
   ```bash
   ENVIRONMENT=production
   DEBUG=false
   ENABLE_API_DOCS=false
   ```

3. **Configure CORS Properly**:
   ```bash
   CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
   ```

4. **Use HTTPS**:
   - Configure SSL certificates
   - Use reverse proxy (nginx)
   - Enable HTTPS redirects

5. **Secure Database Access**:
   - Use strong passwords
   - Limit network access
   - Enable SSL connections

## 📚 Additional Resources

### Documentation
- [API Documentation](API.md)
- [Architecture Overview](ARCHITECTURE.md)
- [Development Guide](DEVELOPMENT.md)

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [PostgreSQL + pgvector](https://github.com/pgvector/pgvector)
- [Docker Compose Reference](https://docs.docker.com/compose/)

### Community
- [GitHub Issues](https://github.com/your-repo/issues)
- [Discord Community](https://discord.gg/your-server)
- [Stack Overflow Tag](https://stackoverflow.com/questions/tagged/rag-chatbot)

## 🆘 Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs** first using the commands above
2. **Search existing issues** in the GitHub repository
3. **Create a new issue** with:
   - Your operating system
   - Docker version
   - Error messages and logs
   - Steps to reproduce

Happy building! 🚀
