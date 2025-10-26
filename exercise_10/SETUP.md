# Exercise 10: Real-Time AI Call Center Assistant - Setup Guide

## 🚀 Quick Start

This guide will help you set up the complete Exercise 10 project.

---

## 📋 Prerequisites

- **Docker & Docker Compose** (for easy setup)
- **Node.js 18+** (if running without Docker)
- **Python 3.11+** (if running without Docker)
- **PostgreSQL 15** (if running without Docker)
- **Redis 7** (if running without Docker)
- **OpenAI API Key** (required for AI features)

---

## 🏃 Running with Docker (Recommended)

### 1. Clone and Navigate
```bash
cd exercise_10
```

### 2. Set Up Environment Variables
```bash
# Copy example env file
cp backend/env.example backend/.env

# Edit .env and add your OpenAI API key
nano backend/.env  # or use your preferred editor
```

### 3. Start All Services
```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Wait for services to be healthy (about 10 seconds)
docker-compose ps

# Start backend and frontend
docker-compose up backend frontend
```

### 4. Seed the Database (in a new terminal)
```bash
# Enter backend container
docker-compose exec backend bash

# Run seeder
python -m data.seed_data

# Exit container
exit
```

### 5. Access the Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### 6. Login Credentials
Use these default accounts:

| Username   | Password   | Role       |
|-----------|-----------|------------|
| admin     | admin123  | Admin      |
| supervisor | super123  | Supervisor |
| agent1    | agent123  | Agent      |
| agent2    | agent123  | Agent      |

---

## 🛠️ Running Without Docker

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
nano .env  # Add your API keys

# Start PostgreSQL and Redis (must be running)
# PostgreSQL on port 5432
# Redis on port 6379

# Initialize database
python -c "
import asyncio
from app.database import init_db
asyncio.run(init_db())
"

# Seed data
python -m data.seed_data

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000" >> .env.local

# Run development server
npm run dev
```

---

## 📚 Project Structure

```
exercise_10/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Main FastAPI app
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database setup
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── auth.py            # Authentication
│   │   └── api/               # API endpoints
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile
│
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # Next.js app directory
│   │   ├── components/        # React components
│   │   └── lib/               # Utilities
│   ├── package.json           # Node dependencies
│   └── Dockerfile
│
├── data/                       # Database seeding
│   └── seed_data.py           # Fake data generator
│
├── docker-compose.yml          # Docker orchestration
└── README.md                   # This file
```

---

## 🧪 Testing the API

### Using cURL

```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User",
    "role": "agent"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=agent1&password=agent123"

# Search for a customer (with token)
TOKEN="your-jwt-token-here"
curl -X GET "http://localhost:8000/api/customers/search?q=John" \
  -H "Authorization: Bearer $TOKEN"
```

### Using the API Documentation

Visit http://localhost:8000/docs for interactive API documentation powered by Swagger UI.

---

## 🎯 Next Steps

### For Students

1. **Explore the codebase:**
   - Read `backend/app/models.py` - Database schema
   - Read `backend/app/api/websocket.py` - WebSocket handler
   - Read `frontend/src/app/page.tsx` - Home page

2. **Implement missing features:**
   - WebRTC audio streaming
   - Speech-to-text integration
   - AI suggestion engine
   - Live UI components

3. **Follow the task guide:**
   - See `STUDENT_TASKS.md` for step-by-step instructions
   - Complete each phase sequentially
   - Test as you go

### For Instructors

1. **Review the architecture:**
   - See `ARCHITECTURE.md` for technical details
   - Understand data flow and components

2. **Customize for your class:**
   - Adjust difficulty by hiding/showing code
   - Add or remove features based on time
   - Create additional exercises

3. **Prepare demo:**
   - Run through the entire flow
   - Test with real OpenAI API calls
   - Prepare backup plan if API is down

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs backend

# Restart services
docker-compose restart postgres backend
```

### Frontend won't start
```bash
# Check logs
docker-compose logs frontend

# Rebuild
docker-compose build --no-cache frontend
docker-compose up frontend
```

### Database connection error
```bash
# Ensure DATABASE_URL in .env matches your setup
# Default: postgresql+asyncpg://admin:password@postgres:5432/callcenter

# Test connection
docker-compose exec backend python -c "
import asyncio
from app.database import engine
async def test():
    async with engine.begin() as conn:
        print('✅ Connected!')
asyncio.run(test())
"
```

### WebSocket not connecting
```bash
# Check CORS settings in backend/.env
# Ensure frontend URL is in CORS_ORIGINS

# Check browser console for errors
# Open DevTools → Console → Network → WS
```

---

## 📝 Environment Variables Reference

### Backend (.env)
| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://admin:password@localhost:5432/callcenter` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `SECRET_KEY` | JWT secret key | `your-secret-key` |
| `CORS_ORIGINS` | Allowed origins | `["http://localhost:3000"]` |

### Frontend (.env.local)
| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:8000` |
| `NEXTAUTH_SECRET` | NextAuth secret | `random-string` |
| `NEXTAUTH_URL` | Frontend URL | `http://localhost:3000` |

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [WebRTC Guide](https://webrtc.org/getting-started/overview)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

## 📧 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs: `docker-compose logs`
3. Ask your instructor or TA
4. Post in the class Slack/Discord channel

---

## 🎉 Success!

If you see:
- ✅ Backend running on port 8000
- ✅ Frontend running on port 3000
- ✅ Can login with agent1/agent123
- ✅ Can search for customers

**Congratulations!** You're ready to start building the AI Call Center Assistant! 🚀

---

**Next:** Read `STUDENT_TASKS.md` to begin implementing features.

