"""
Main FastAPI Application for Truck Monitoring System
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db
from .api import auth_routes, trucks, statistics
from .seed_data import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events - startup and shutdown"""
    # Startup
    print("🚀 Starting Truck Monitoring System...")
    init_db()
    seed_database()
    print("✅ Server ready at http://localhost:8095")
    yield
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title="Truck Monitoring System",
    description="Backend portal for monitoring truck traffic with user authentication",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(trucks.router)
app.include_router(statistics.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Truck Monitoring System API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "truck-monitoring"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8095,
        reload=True
    )

