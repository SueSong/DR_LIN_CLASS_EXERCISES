from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db, close_db
from .api import auth_routes, customers, websocket, calls

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting AI Call Center Assistant...")
    # await init_db()  # Temporarily disabled - audio doesn't need database
    print("Backend ready (database disabled)")
    yield
    # Shutdown
    print("Shutting down...")
    # await close_db()
    print("Backend shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Real-Time AI Call Center Assistant API",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(customers.router)
app.include_router(calls.router)
app.include_router(websocket.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Call Center Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

