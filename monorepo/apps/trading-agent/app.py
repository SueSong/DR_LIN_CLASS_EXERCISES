"""
Exercise 5: Stock Trading Agent - Main FastAPI Application
Demonstrates all Exercise 1-6 skills in a comprehensive trading system
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
import os
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# Database imports
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# OpenTelemetry imports (Exercise 4)
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource

# Optional AsyncPG instrumentation (if available)
try:
    from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
    ASYNCPG_INSTRUMENTATION_AVAILABLE = True
except ImportError:
    ASYNCPG_INSTRUMENTATION_AVAILABLE = False

# Trading agent imports
from tools.registry import get_trading_registry, TradingToolRegistry
from tools.schemas import *
from tools import stock_tools, reporting
from agents.llm_agent import get_llm_agent
from tools.stock_tools import set_database_connection
from tools.reporting import set_database_connection as set_reporting_db_connection

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
db_pool: Optional[asyncpg.Pool] = None
registry: TradingToolRegistry = get_trading_registry()

def setup_observability():
    """Setup OpenTelemetry observability (Exercise 4)"""
    
    # Create resource
    resource = Resource.create({
        "service.name": "trading-agent",
        "service.version": "1.0.0",
        "deployment.environment": "development"
    })
    
    # Setup tracing
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    
    # Add OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",
        insecure=True
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Setup automatic instrumentation
    FastAPIInstrumentor().instrument()
    
    # Optional AsyncPG instrumentation
    if ASYNCPG_INSTRUMENTATION_AVAILABLE:
        AsyncPGInstrumentor().instrument()
        logger.info("AsyncPG instrumentation enabled")
    else:
        logger.info("AsyncPG instrumentation not available")
    
    logger.info("OpenTelemetry observability configured")

async def setup_database():
    """Setup database connection pool"""
    global db_pool
    
    database_url = os.getenv(
        "DATABASE_URL", 
        "postgresql://trader:trading123@localhost:5432/trading_db"
    )
    
    try:
        db_pool = await asyncpg.create_pool(
            database_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        
        # Set database connection for tools
        async with db_pool.acquire() as conn:
            set_database_connection(conn)
            set_reporting_db_connection(conn)
        
        logger.info("Database connection pool created")
        
    except Exception as e:
        logger.error(f"Failed to setup database: {e}")
        # Continue without database for demo purposes
        db_pool = None

async def cleanup_database():
    """Cleanup database connections"""
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("Database connection pool closed")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Trading Agent...")
    setup_observability()
    await setup_database()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Trading Agent...")
    await cleanup_database()

# Create FastAPI app
app = FastAPI(
    title="AI Trading Agent",
    description="Exercise 5: Comprehensive Stock Trading Agent with AI-powered decisions",
    version="1.0.0",
    lifespan=lifespan
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database connection
async def get_db_connection():
    """Get database connection from pool"""
    if db_pool:
        async with db_pool.acquire() as conn:
            yield conn
    else:
        yield None

# Web UI endpoints
@app.get("/", response_class=HTMLResponse)
async def chat_ui(request: Request):
    """Chat UI for the trading agent"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Alternative chat UI endpoint"""
    return templates.TemplateResponse("chat.html", {"request": request})

# API endpoints
@app.get("/api")
async def root():
    """Root API endpoint"""
    return {
        "message": "AI Trading Agent API is running",
        "version": "1.0.0",
        "exercises": ["1: Typed Tools", "2: Tool Registry", "3: Reliability", 
                     "4: Observability", "5: Permissions", "6: Full Agent Flow"],
        "chat_ui": "http://localhost:8001/",
        "api_docs": "http://localhost:8001/docs"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected" if db_pool else "disconnected",
        "tools_registered": len(registry._tools),
        "llm_available": get_llm_agent().client is not None
    }

# Tool registry endpoints (Exercise 2)
@app.get("/tools")
async def list_tools(category: Optional[str] = None):
    """List available tools in registry"""
    
    from tools.registry import ToolCategory
    
    filter_category = None
    if category:
        try:
            filter_category = ToolCategory(category.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    tools = registry.list_tools(category=filter_category)
    
    return {
        "tools": [
            {
                "name": tool.metadata.name,
                "description": tool.metadata.description,
                "category": tool.metadata.category.value,
                "permission_level": tool.metadata.permission.level.value,
                "enabled": tool.metadata.enabled,
                "call_count": tool.call_count,
                "success_rate": tool.success_count / tool.call_count if tool.call_count > 0 else 0
            }
            for tool in tools
        ],
        "total_count": len(tools)
    }

@app.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get detailed information about a specific tool"""
    
    tool = registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    return {
        "name": tool.metadata.name,
        "description": tool.metadata.description,
        "category": tool.metadata.category.value,
        "version": tool.metadata.version,
        "permission": {
            "level": tool.metadata.permission.level.value,
            "sandbox_enabled": tool.metadata.permission.sandbox_enabled,
            "rate_limit_per_minute": tool.metadata.permission.rate_limit_per_minute
        },
        "statistics": {
            "call_count": tool.call_count,
            "success_count": tool.success_count,
            "error_count": tool.error_count,
            "avg_execution_time": tool.avg_execution_time,
            "last_called": tool.last_called.isoformat() if tool.last_called else None
        },
        "input_schema": tool.metadata.input_schema.schema(),
        "output_schema": tool.metadata.output_schema.schema()
    }

# Stock quote endpoint (Exercise 1: Typed Tools)
@app.post("/quotes")
async def get_stock_quotes(request: StockQuoteInput, db: Optional[asyncpg.Connection] = Depends(get_db_connection)):
    """Get stock quotes - demonstrates Exercise 1 (Typed Tools with Pydantic)"""
    
    try:
        if db:
            set_database_connection(db)
        
        result = await registry.execute_tool(
            "stock_quote",
            request.dict(),
            user_id=request.user_id,
            user_roles={"trader"}
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Stock quotes failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Trading endpoint (Exercise 5: Permissions & Sandboxing)
@app.post("/trade")
async def execute_trade(request: TradeInput, db: Optional[asyncpg.Connection] = Depends(get_db_connection)):
    """Execute trade - demonstrates Exercise 5 (Permissions & Sandboxing)"""
    
    try:
        if db:
            set_database_connection(db)
        
        result = await registry.execute_tool(
            "execute_trade",
            request.dict(),
            user_id=request.user_id,
            user_roles={"trader", "authenticated"}
        )
        
        return result
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Trade execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trades")
async def execute_trades(request: dict, db: Optional[asyncpg.Connection] = Depends(get_db_connection)):
    """Execute trade (plural endpoint for chat UI compatibility)"""
    
    try:
        # Convert dict to TradeInput for validation
        trade_input = TradeInput(**request)
        
        if db:
            set_database_connection(db)
        
        result = await registry.execute_tool(
            "execute_trade",
            trade_input.dict(),
            user_id=trade_input.user_id,
            user_roles={"trader", "authenticated"}
        )
        
        return result
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Trade execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Portfolio endpoint
@app.get("/portfolio")
async def get_portfolio(user_id: str = "default_trader", db: Optional[asyncpg.Connection] = Depends(get_db_connection)):
    """Get portfolio positions"""
    
    try:
        if db:
            set_database_connection(db)
        
        result = await registry.execute_tool(
            "get_portfolio",
            {"user_id": user_id},
            user_id=user_id,
            user_roles={"authenticated"}
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Portfolio retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI recommendations endpoint (Exercise 6: Full Agent Flow)
@app.post("/recommendations")
async def get_trading_recommendations(
    request: RecommendationInput, 
    db: Optional[asyncpg.Connection] = Depends(get_db_connection)
):
    """Get AI-powered trading recommendations - demonstrates Exercise 6 (Full Agent Flow)"""
    
    try:
        if db:
            set_database_connection(db)
        
        result = await registry.execute_tool(
            "get_trading_recommendations",
            request.dict(),
            user_id=request.user_id,
            user_roles={"trader", "authenticated"}
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Trading recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Reporting endpoint (Exercise 2: File Operations)
@app.post("/reports/daily")
async def generate_daily_report(
    request: ReportInput,
    background_tasks: BackgroundTasks,
    db: Optional[asyncpg.Connection] = Depends(get_db_connection)
):
    """Generate daily trading report - demonstrates Exercise 2 (File Operations)"""
    
    try:
        if db:
            set_reporting_db_connection(db)
        
        result = await registry.execute_tool(
            "generate_daily_report",
            request.dict(),
            user_id=request.user_id,
            user_roles={"authenticated"}
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File operations endpoint
@app.post("/files")
async def file_operations(request: FileOperationInput):
    """Perform file operations - demonstrates sandboxed file access"""
    
    try:
        result = await registry.execute_tool(
            "file_operations",
            request.dict(),
            user_id=request.user_id,
            user_roles={"authenticated"}
        )
        
        return result
        
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"File operations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent orchestration endpoint (Exercise 6: Full Agent Flow)
@app.post("/agent/auto-trade")
async def auto_trade_agent(
    user_id: str = "default_trader",
    risk_tolerance: str = "moderate",
    db: Optional[asyncpg.Connection] = Depends(get_db_connection)
):
    """
    Full agent flow: Get quotes → Analyze → Recommend → Execute → Report
    Demonstrates Exercise 6 (Full Agent Flow)
    """
    
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("auto_trade_agent_flow") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("risk_tolerance", risk_tolerance)
        
        try:
            if db:
                set_database_connection(db)
                set_reporting_db_connection(db)
            
            # Step 1: Get current portfolio
            portfolio_result = await registry.execute_tool(
                "get_portfolio",
                {"user_id": user_id},
                user_id=user_id,
                user_roles={"authenticated"}
            )
            
            if portfolio_result["status"] != "success":
                raise Exception("Failed to get portfolio")
            
            # Step 2: Get market quotes for major stocks
            quotes_result = await registry.execute_tool(
                "stock_quote",
                {"symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"], "include_details": True},
                user_id=user_id,
                user_roles={"trader"}
            )
            
            if quotes_result["status"] != "success":
                raise Exception("Failed to get stock quotes")
            
            # Step 3: Get AI recommendations
            recommendations_result = await registry.execute_tool(
                "get_trading_recommendations",
                {
                    "market_data": {"quotes": quotes_result["quotes"]},
                    "portfolio_data": portfolio_result,
                    "cash_balance": portfolio_result["cash_balance"],
                    "risk_tolerance": risk_tolerance,
                    "user_id": user_id
                },
                user_id=user_id,
                user_roles={"trader", "authenticated"}
            )
            
            if recommendations_result["status"] != "success":
                raise Exception("Failed to get recommendations")
            
            # Step 4: Execute top recommendation (if any)
            executed_trades = []
            recommendations = recommendations_result.get("recommendations", [])
            
            if recommendations:
                top_recommendation = recommendations[0]  # Highest priority
                
                if top_recommendation["confidence"] > 0.6:  # Only execute high-confidence trades
                    trade_result = await registry.execute_tool(
                        "execute_trade",
                        {
                            "symbol": top_recommendation["symbol"],
                            "action": top_recommendation["action"],
                            "amount": float(top_recommendation.get("amount", 1000)),
                            "user_id": user_id
                        },
                        user_id=user_id,
                        user_roles={"trader", "authenticated"}
                    )
                    
                    if trade_result["status"] == "success":
                        executed_trades.append(trade_result)
            
            # Step 5: Generate daily report
            from datetime import date
            report_result = await registry.execute_tool(
                "generate_daily_report",
                {
                    "user_id": user_id,
                    "report_date": date.today().isoformat(),
                    "report_type": "daily"
                },
                user_id=user_id,
                user_roles={"authenticated"}
            )
            
            span.set_attribute("executed_trades", len(executed_trades))
            span.set_attribute("recommendations_count", len(recommendations))
            span.set_attribute("status", "success")
            
            return {
                "status": "success",
                "portfolio": portfolio_result,
                "market_quotes": quotes_result,
                "recommendations": recommendations_result,
                "executed_trades": executed_trades,
                "daily_report": report_result,
                "agent_summary": {
                    "recommendations_generated": len(recommendations),
                    "trades_executed": len(executed_trades),
                    "total_portfolio_value": portfolio_result.get("total_value", 0)
                }
            }
            
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            
            logger.error(f"Auto-trade agent flow failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Registry statistics endpoint
@app.get("/stats")
async def get_registry_stats():
    """Get tool registry statistics"""
    return registry.get_registry_stats()

# Demo endpoints for Exercise 1 (Good vs Bad Input)
@app.post("/demo/validate-input")
async def demo_input_validation(request: Dict[str, Any]):
    """Demonstrate good vs bad input validation (Exercise 1)"""
    
    results = {}
    
    # Test stock quote validation
    try:
        good_quote_input = StockQuoteInput(**{
            "symbols": ["AAPL", "GOOGL"],
            "include_details": True
        })
        results["stock_quote_good"] = {"status": "valid", "data": good_quote_input.dict()}
    except Exception as e:
        results["stock_quote_good"] = {"status": "error", "error": str(e)}
    
    try:
        bad_quote_input = StockQuoteInput(**{
            "symbols": ["invalid_symbol_123"],
            "include_details": "not_a_boolean"
        })
        results["stock_quote_bad"] = {"status": "valid", "data": bad_quote_input.dict()}
    except Exception as e:
        results["stock_quote_bad"] = {"status": "error", "error": str(e)}
    
    # Test trade validation
    try:
        good_trade_input = TradeInput(**{
            "symbol": "AAPL",
            "action": "BUY",
            "amount": 1000.00
        })
        results["trade_good"] = {"status": "valid", "data": good_trade_input.dict()}
    except Exception as e:
        results["trade_good"] = {"status": "error", "error": str(e)}
    
    try:
        bad_trade_input = TradeInput(**{
            "symbol": "INVALID",
            "action": "INVALID_ACTION"
            # Missing amount or quantity
        })
        results["trade_bad"] = {"status": "valid", "data": bad_trade_input.dict()}
    except Exception as e:
        results["trade_bad"] = {"status": "error", "error": str(e)}
    
    return {
        "demonstration": "Exercise 1: Typed Tools with Pydantic",
        "results": results,
        "explanation": "Good inputs pass validation, bad inputs show clear error messages"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8001,  # Different port from the original API
        reload=True,
        log_level="info"
    )
