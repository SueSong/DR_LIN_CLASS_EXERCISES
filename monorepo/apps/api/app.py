"""
FastAPI backend for AI Agent Training Class
Main application entry point with tool integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from typing import Dict, Any
import logging

from tools.http_fetch import HTTPFetcher
from tools.db_query import DBQueryTool
from tools.file_ops import FileOperations
from observability.otel import setup_observability, get_tracer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize observability
tracer = get_tracer(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting FastAPI application...")
    setup_observability()
    yield
    # Shutdown
    logger.info("Shutting down FastAPI application...")

app = FastAPI(
    title="AI Agent Training API",
    description="Backend API for AI Agent Training Class",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tools
http_fetcher = HTTPFetcher()
db_query_tool = DBQueryTool()
file_ops = FileOperations()

@app.get("/")
async def root():
    """Health check endpoint"""
    with tracer.start_as_current_span("health_check") as span:
        span.set_attribute("endpoint", "/")
        return {"message": "AI Agent Training API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    with tracer.start_as_current_span("detailed_health_check") as span:
        span.set_attribute("endpoint", "/health")
        return {
            "status": "healthy",
            "services": {
                "http_fetcher": "available",
                "db_query": "available", 
                "file_ops": "available"
            }
        }

@app.post("/tools/http-fetch")
async def fetch_url(request: Dict[str, Any]):
    """HTTP fetch tool endpoint"""
    with tracer.start_as_current_span("http_fetch_tool") as span:
        span.set_attribute("tool.name", "http_fetch")
        try:
            url = request.get("url")
            if not url:
                raise HTTPException(status_code=400, detail="URL is required")
            
            result = await http_fetcher.fetch(url, **request)
            span.set_attribute("status", "success")
            return result
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/db-query")
async def execute_query(request: Dict[str, Any]):
    """Database query tool endpoint"""
    with tracer.start_as_current_span("db_query_tool") as span:
        span.set_attribute("tool.name", "db_query")
        try:
            result = await db_query_tool.execute(request)
            span.set_attribute("status", "success")
            return result
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/file-ops")
async def file_operation(request: Dict[str, Any]):
    """File operations tool endpoint"""
    with tracer.start_as_current_span("file_ops_tool") as span:
        span.set_attribute("tool.name", "file_ops")
        try:
            result = await file_ops.execute(request)
            span.set_attribute("status", "success")
            return result
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
