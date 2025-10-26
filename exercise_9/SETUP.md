# Setup Guide - Exercise 9

## Prerequisites

### Required
- **Docker Desktop** (recommended) OR
- **Python 3.11+** and **Node.js 18+**

### Optional
- Git for version control
- Postman for API testing

## Installation Methods

### Method 1: Docker (Recommended for Quick Start)

**Advantages**: No need to manage dependencies, works across all platforms

```bash
# 1. Navigate to exercise directory
cd /path/to/exercise_9

# 2. Start services
docker-compose up --build

# 3. Wait for services to start (30-60 seconds)
# Backend will be at: http://localhost:8000
# Frontend will be at: http://localhost:3000

# 4. Stop services when done
docker-compose down
```

**Verify Setup:**
- Backend health check: http://localhost:8000/health
- API documentation: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Method 2: Manual Setup (For Development)

**Advantages**: Better for debugging and development

#### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment (recommended)
python -m venv venv

# 3. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start backend server
uvicorn app.main:app --reload --port 8000

# Server will start at: http://localhost:8000
```

#### Frontend Setup

```bash
# 1. Open a new terminal
# 2. Navigate to frontend directory
cd frontend

# 3. Install dependencies
npm install

# 4. Start development server
npm run dev

# Server will start at: http://localhost:3000
```

## Post-Installation

### 1. Verify Backend

Open browser to http://localhost:8000/health

Expected response:
```json
{
  "status": "healthy",
  "service": "legal-document-review",
  "version": "1.0.0",
  "agents": ["classifier", "extractor", "reviewer", "drafter"]
}
```

### 2. Verify Frontend

Open browser to http://localhost:3000

You should see the home page with:
- Navigation bar
- Feature cards (PII Protection, Policy Enforcement, HITL, Red Team)
- Quick Start buttons

### 3. Test with Sample Document

```bash
# 1. Go to Documents page
# 2. Upload: data/sample_documents/nda_with_pii.md
# 3. Click "Start Review Process"
# 4. View multi-agent results
```

## Configuration

### Backend Configuration

Create `.env` file in backend directory (optional):
```bash
# API Configuration
PORT=8000
HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO
```

### Frontend Configuration

Create `.env.local` file in frontend directory:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Common Issues & Solutions

### Issue: Port Already in Use

**Error**: `Address already in use: 8000` or `3000`

**Solution**:
```bash
# Find process using port
# macOS/Linux:
lsof -i :8000
kill -9 <PID>

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different ports:
# Backend: uvicorn app.main:app --port 8001
# Frontend: npm run dev -- -p 3001
```

### Issue: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt

# Or reinstall:
pip install --force-reinstall -r requirements.txt
```

### Issue: React/Next.js Errors

**Error**: Various npm/node errors

**Solution**:
```bash
# Clear node_modules and cache
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Issue: CORS Errors in Browser

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
- Ensure backend is running
- Check frontend `NEXT_PUBLIC_API_URL` points to correct backend URL
- Backend already has CORS enabled for all origins (development only)

### Issue: Docker Build Fails

**Error**: Docker build or compose errors

**Solution**:
```bash
# Clean Docker cache
docker-compose down -v
docker system prune -a

# Rebuild
docker-compose up --build
```

## Development Workflow

### Making Changes to Backend

```bash
# 1. Backend runs with --reload flag, changes auto-reload
# 2. Edit files in backend/app/
# 3. Check terminal for reload confirmation
# 4. Test changes at http://localhost:8000/docs
```

### Making Changes to Frontend

```bash
# 1. Frontend has hot reload enabled
# 2. Edit files in frontend/src/
# 3. Changes appear immediately in browser
# 4. Check browser console for errors
```

### Testing API Endpoints

Use the interactive API documentation:
http://localhost:8000/docs

Or use curl:
```bash
# Health check
curl http://localhost:8000/health

# List documents
curl http://localhost:8000/api/documents

# Get policies
curl http://localhost:8000/api/policies
```

## Running Red Team Tests

```bash
# 1. Start both backend and frontend
# 2. Navigate to http://localhost:3000/redteam
# 3. Click "Run Test" on any predefined scenario
# 4. View results

# Or use API directly:
curl -X POST http://localhost:8000/api/redteam/test \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test SSN Reconstruction",
    "description": "Test PII reconstruction",
    "attack_type": "reconstruction",
    "payload": {
      "redacted_value": "***-**-1234",
      "reconstruction_attempt": "123-45-1234"
    }
  }'
```

## Monitoring & Debugging

### Backend Logs

```bash
# Manual setup: Check terminal running uvicorn
# Docker: docker-compose logs -f backend
```

### Frontend Logs

```bash
# Manual setup: Check terminal running npm
# Docker: docker-compose logs -f frontend
# Browser: Open Developer Tools → Console
```

### Database/Storage

Current implementation uses in-memory storage (resets on restart).

To persist data across restarts, you would need to:
1. Add a database (PostgreSQL, MongoDB, etc.)
2. Update backend to use database instead of `STORE` dict
3. Add database service to docker-compose.yml

## Performance Tuning

### Backend
- Increase worker processes for production:
  ```bash
  uvicorn app.main:app --workers 4 --port 8000
  ```

### Frontend
- Build optimized version:
  ```bash
  npm run build
  npm start  # Production server
  ```

## Security Hardening

For production deployment:

1. **Enable Authentication**
   - Add JWT tokens
   - Implement user management
   - Protect sensitive endpoints

2. **Use HTTPS**
   - Set up SSL certificates
   - Redirect HTTP to HTTPS

3. **Environment Variables**
   - Never commit `.env` files
   - Use secret management (AWS Secrets Manager, etc.)

4. **Rate Limiting**
   - Implement API rate limiting
   - Prevent abuse and DDoS

5. **Database Security**
   - Use proper database instead of in-memory
   - Encrypt sensitive data at rest
   - Use connection pooling

## Next Steps

1. Upload sample documents
2. Run a document review
3. Try red team tests
4. Check audit logs
5. Monitor KPIs in reports

For more details, see [README.md](README.md)

