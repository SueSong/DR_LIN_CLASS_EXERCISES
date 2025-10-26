"""
Stock Trading Tools - Implementing all Exercise 1-6 skills
Comprehensive trading tools with reliability, observability, and permissions
"""

import asyncio
import httpx
import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
import json
from datetime import datetime

# OpenTelemetry imports (Exercise 4)
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from .schemas import (
    StockQuoteInput, StockQuoteOutput, StockQuote,
    TradeInput, TradeOutput, PortfolioInput, PortfolioOutput,
    RecommendationInput, RecommendationOutput, TradingRecommendation,
    ToolStatus, TransactionType
)
from .registry import (
    register_trading_tool, ToolCategory, ToolPermission, PermissionLevel
)
from .reliability import (
    with_retry, TradingRetryConfigs, get_market_data_breaker
)

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

# Database connection (will be injected)
_db_connection = None

def set_database_connection(db_conn):
    """Set the database connection for tools"""
    global _db_connection
    _db_connection = db_conn

# Exercise 1: Typed Tool with Pydantic + Exercise 3: Reliability + Exercise 4: Observability
@register_trading_tool(
    name="stock_quote",
    description="Get real-time stock quotes with market data",
    category=ToolCategory.MARKET_DATA,
    input_schema=StockQuoteInput,
    output_schema=StockQuoteOutput,
    permission=ToolPermission(
        level=PermissionLevel.PUBLIC,
        rate_limit_per_minute=60,
        sandbox_enabled=True
    ),
    tags=["stocks", "quotes", "market-data"],
    version="1.0.0"
)
@with_retry(TradingRetryConfigs.market_data_fetch(), get_market_data_breaker())
async def get_stock_quotes(input_data: Dict[str, Any], trace_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get stock quotes from market data API
    Demonstrates Exercise 1 (Pydantic), Exercise 3 (Retry), Exercise 4 (Observability)
    """
    
    with tracer.start_as_current_span("stock_quote_tool") as span:
        span.set_attribute("tool.name", "stock_quote")
        span.set_attribute("symbols.count", len(input_data.get("symbols", [])))
        
        try:
            symbols = input_data["symbols"]
            include_details = input_data.get("include_details", False)
            
            quotes = []
            
            # For demo purposes, we'll use a mock API or Alpha Vantage
            # In production, you'd use your preferred stock data provider
            
            async with httpx.AsyncClient() as client:
                for symbol in symbols:
                    span.set_attribute(f"symbol.{symbol}", "fetching")
                    
                    try:
                        # Mock stock data for demo (replace with real API)
                        quote_data = await _fetch_stock_data(client, symbol, include_details)
                        
                        quote = StockQuote(
                            symbol=symbol,
                            price=Decimal(str(quote_data.get("price", 100.0))),
                            change=Decimal(str(quote_data.get("change", 0.0))),
                            change_percent=Decimal(str(quote_data.get("change_percent", 0.0))),
                            volume=quote_data.get("volume"),
                            market_cap=quote_data.get("market_cap"),
                            pe_ratio=Decimal(str(quote_data.get("pe_ratio", 0.0))) if quote_data.get("pe_ratio") else None,
                            day_high=Decimal(str(quote_data.get("day_high", 0.0))) if quote_data.get("day_high") else None,
                            day_low=Decimal(str(quote_data.get("day_low", 0.0))) if quote_data.get("day_low") else None,
                        )
                        
                        quotes.append(quote)
                        span.set_attribute(f"symbol.{symbol}", "success")
                        
                        # Cache quote in database
                        if _db_connection:
                            await _cache_stock_quote(_db_connection, symbol, quote_data)
                        
                    except Exception as e:
                        logger.warning(f"Failed to fetch quote for {symbol}: {e}")
                        span.set_attribute(f"symbol.{symbol}", "error")
                        # Continue with other symbols
            
            span.set_attribute("quotes.fetched", len(quotes))
            span.set_attribute("status", "success")
            
            return {
                "status": ToolStatus.SUCCESS,
                "quotes": [quote.dict() for quote in quotes],
                "market_status": "OPEN",  # Mock status
                "data_source": "demo_api",
                "timestamp": datetime.utcnow(),
                "execution_time_ms": 0  # Will be set by retry wrapper
            }
            
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            span.set_status(Status(StatusCode.ERROR, str(e)))
            
            logger.error(f"Stock quote tool failed: {e}")
            return {
                "status": ToolStatus.ERROR,
                "error_message": str(e),
                "quotes": [],
                "timestamp": datetime.utcnow()
            }

async def _fetch_stock_data(client: httpx.AsyncClient, symbol: str, include_details: bool) -> Dict[str, Any]:
    """Fetch stock data from API (mock implementation)"""
    
    # Mock data for demo - replace with real API calls
    import random
    
    base_price = {"AAPL": 175.0, "GOOGL": 135.0, "MSFT": 340.0, "TSLA": 245.0, "AMZN": 145.0}.get(symbol, 100.0)
    change = random.uniform(-5.0, 5.0)
    
    data = {
        "symbol": symbol,
        "price": base_price + change,
        "change": change,
        "change_percent": (change / base_price) * 100,
        "volume": random.randint(1000000, 50000000),
    }
    
    if include_details:
        data.update({
            "market_cap": random.randint(100000000000, 3000000000000),
            "pe_ratio": random.uniform(10.0, 50.0),
            "day_high": data["price"] + random.uniform(0, 5),
            "day_low": data["price"] - random.uniform(0, 5),
        })
    
    return data

async def _cache_stock_quote(db_conn, symbol: str, quote_data: Dict[str, Any]):
    """Cache stock quote in database"""
    try:
        query = """
        INSERT INTO stock_quotes (symbol, price, change_percent, volume, market_cap, quote_data, last_updated)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (symbol) DO UPDATE SET
            price = EXCLUDED.price,
            change_percent = EXCLUDED.change_percent,
            volume = EXCLUDED.volume,
            market_cap = EXCLUDED.market_cap,
            quote_data = EXCLUDED.quote_data,
            last_updated = EXCLUDED.last_updated
        """
        
        await db_conn.execute(
            query,
            symbol,
            quote_data.get("price"),
            quote_data.get("change_percent"),
            quote_data.get("volume"),
            quote_data.get("market_cap"),
            json.dumps(quote_data),
            datetime.utcnow()
        )
    except Exception as e:
        logger.warning(f"Failed to cache quote for {symbol}: {e}")

# Exercise 5: Permission & Sandboxing - Trading tool with restricted access
@register_trading_tool(
    name="execute_trade",
    description="Execute buy/sell trades with portfolio management",
    category=ToolCategory.TRADING,
    input_schema=TradeInput,
    output_schema=TradeOutput,
    permission=ToolPermission(
        level=PermissionLevel.TRADER,  # Requires trader permission
        allowed_operations=["BUY", "SELL"],
        rate_limit_per_minute=10,  # Limited trading frequency
        sandbox_enabled=True,
        max_concurrent_calls=1  # One trade at a time
    ),
    tags=["trading", "execution", "portfolio"],
    version="1.0.0"
)
@with_retry(TradingRetryConfigs.trade_execution())
async def execute_trade(input_data: Dict[str, Any], trace_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute a stock trade with full validation and portfolio management
    Demonstrates Exercise 5 (Permissions & Sandboxing)
    """
    
    with tracer.start_as_current_span("execute_trade_tool") as span:
        span.set_attribute("tool.name", "execute_trade")
        span.set_attribute("symbol", input_data.get("symbol"))
        span.set_attribute("action", input_data.get("action"))
        
        try:
            # For demo purposes, allow mock trading even without database
            mock_mode = not _db_connection
            if mock_mode:
                logger.info("🎭 Running in DEMO MODE - simulating trades without database")
            
            symbol = input_data["symbol"]
            action = TransactionType(input_data["action"])
            quantity = input_data.get("quantity")
            amount = input_data.get("amount")
            user_id = input_data.get("user_id", "default_trader")
            
            span.set_attribute("user_id", user_id)
            
            # Get current stock price
            current_price = await _get_current_stock_price(symbol)
            span.set_attribute("current_price", float(current_price))
            
            # Calculate trade details
            if quantity:
                shares = Decimal(str(quantity))
                total_amount = shares * current_price
            else:
                total_amount = Decimal(str(amount))
                shares = total_amount / current_price
            
            # Validate trade
            await _validate_trade(user_id, symbol, action, shares, total_amount, current_price)
            
            # Execute trade in database
            transaction_id = await _execute_trade_in_db(
                user_id, symbol, action, shares, current_price, total_amount
            )
            
            # Get updated cash balance
            remaining_cash = await _get_cash_balance(user_id)
            
            span.set_attribute("transaction_id", transaction_id)
            span.set_attribute("shares", float(shares))
            span.set_attribute("total_amount", float(total_amount))
            span.set_attribute("status", "success")
            
            return {
                "status": ToolStatus.SUCCESS,
                "transaction_id": transaction_id,
                "symbol": symbol,
                "action": action.value,
                "shares": shares,
                "price": current_price,
                "total_amount": total_amount,
                "fees": Decimal("0"),  # Mock fees
                "remaining_cash": remaining_cash,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            span.set_status(Status(StatusCode.ERROR, str(e)))
            
            logger.error(f"Trade execution failed: {e}")
            return {
                "status": ToolStatus.ERROR,
                "error_message": str(e),
                "symbol": input_data.get("symbol"),
                "action": input_data.get("action"),
                "timestamp": datetime.utcnow()
            }

async def _get_current_stock_price(symbol: str) -> Decimal:
    """Get current stock price from cache or API"""
    if _db_connection:
        result = await _db_connection.fetchrow(
            "SELECT price FROM stock_quotes WHERE symbol = $1 ORDER BY last_updated DESC LIMIT 1",
            symbol
        )
        if result:
            return Decimal(str(result["price"]))
    
    # Fallback to API call
    mock_prices = {"AAPL": 175.0, "GOOGL": 135.0, "MSFT": 340.0, "TSLA": 245.0, "AMZN": 145.0}
    return Decimal(str(mock_prices.get(symbol, 100.0)))

async def _validate_trade(user_id: str, symbol: str, action: TransactionType, shares: Decimal, total_amount: Decimal, price: Decimal):
    """Validate trade against portfolio and cash balance"""
    
    if action == TransactionType.BUY:
        # Check cash balance
        cash_balance = await _get_cash_balance(user_id)
        if total_amount > cash_balance:
            raise ValueError(f"Insufficient cash: need ${total_amount}, have ${cash_balance}")
    
    elif action == TransactionType.SELL:
        # Check stock holdings
        holdings = await _get_stock_holdings(user_id, symbol)
        if shares > holdings:
            raise ValueError(f"Insufficient shares: need {shares}, have {holdings}")

async def _get_cash_balance(user_id: str) -> Decimal:
    """Get current cash balance"""
    if not _db_connection:
        return Decimal("950000")  # Mock balance for demo
    
    result = await _db_connection.fetchrow(
        "SELECT balance FROM cash_balance WHERE user_id = $1",
        user_id
    )
    return Decimal(str(result["balance"])) if result else Decimal("0")

async def _get_stock_holdings(user_id: str, symbol: str) -> Decimal:
    """Get current stock holdings"""
    if not _db_connection:
        return Decimal("0")  # Mock holdings
    
    result = await _db_connection.fetchrow(
        "SELECT shares FROM portfolio WHERE user_id = $1 AND symbol = $2",
        user_id, symbol
    )
    return Decimal(str(result["shares"])) if result else Decimal("0")

async def _execute_trade_in_db(user_id: str, symbol: str, action: TransactionType, shares: Decimal, price: Decimal, total_amount: Decimal) -> str:
    """Execute trade in database with transaction"""
    
    if not _db_connection:
        return "mock_transaction_id"
    
    async with _db_connection.transaction():
        # Insert transaction record
        transaction_id = await _db_connection.fetchval(
            """
            INSERT INTO transactions (user_id, symbol, transaction_type, shares, price, total_amount, agent_reasoning)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
            """,
            user_id, symbol, action.value, shares, price, total_amount, "Automated trade execution"
        )
        
        if action == TransactionType.BUY:
            # Update cash balance
            await _db_connection.execute(
                "UPDATE cash_balance SET balance = balance - $1 WHERE user_id = $2",
                total_amount, user_id
            )
            
            # Update portfolio
            await _db_connection.execute(
                """
                INSERT INTO portfolio (user_id, symbol, shares, avg_cost)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id, symbol) DO UPDATE SET
                    shares = portfolio.shares + EXCLUDED.shares,
                    avg_cost = ((portfolio.shares * portfolio.avg_cost) + (EXCLUDED.shares * EXCLUDED.avg_cost)) / (portfolio.shares + EXCLUDED.shares),
                    last_updated = CURRENT_TIMESTAMP
                """,
                user_id, symbol, shares, price
            )
        
        elif action == TransactionType.SELL:
            # Update cash balance
            await _db_connection.execute(
                "UPDATE cash_balance SET balance = balance + $1 WHERE user_id = $2",
                total_amount, user_id
            )
            
            # Update portfolio
            await _db_connection.execute(
                """
                UPDATE portfolio 
                SET shares = shares - $3, last_updated = CURRENT_TIMESTAMP
                WHERE user_id = $1 AND symbol = $2
                """,
                user_id, symbol, shares
            )
        
        return str(transaction_id)

# Portfolio management tool
@register_trading_tool(
    name="get_portfolio",
    description="Get current portfolio positions and performance",
    category=ToolCategory.PORTFOLIO,
    input_schema=PortfolioInput,
    output_schema=PortfolioOutput,
    permission=ToolPermission(
        level=PermissionLevel.AUTHENTICATED,
        sandbox_enabled=True
    ),
    tags=["portfolio", "positions", "performance"],
    version="1.0.0"
)
async def get_portfolio(input_data: Dict[str, Any], trace_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get portfolio positions and performance metrics"""
    
    with tracer.start_as_current_span("get_portfolio_tool") as span:
        span.set_attribute("tool.name", "get_portfolio")
        
        try:
            user_id = input_data.get("user_id", "default_trader")
            include_performance = input_data.get("include_performance", True)
            
            if not _db_connection:
                # Mock portfolio data
                return {
                    "status": ToolStatus.SUCCESS,
                    "positions": [],
                    "cash_balance": Decimal("1000000"),
                    "total_value": Decimal("1000000"),
                    "total_return": Decimal("0"),
                    "total_return_percent": Decimal("0"),
                    "timestamp": datetime.utcnow()
                }
            
            # Get portfolio positions
            positions_data = await _db_connection.fetch(
                """
                SELECT p.symbol, p.shares, p.avg_cost, sq.price as current_price,
                       (p.shares * sq.price) as market_value,
                       (p.shares * sq.price) - (p.shares * p.avg_cost) as unrealized_pnl,
                       CASE WHEN p.avg_cost > 0 THEN ((sq.price - p.avg_cost) / p.avg_cost * 100) ELSE 0 END as return_percent
                FROM portfolio p
                LEFT JOIN stock_quotes sq ON p.symbol = sq.symbol
                WHERE p.user_id = $1 AND p.shares > 0
                """,
                user_id
            )
            
            positions = []
            for row in positions_data:
                positions.append({
                    "symbol": row["symbol"],
                    "shares": Decimal(str(row["shares"])),
                    "avg_cost": Decimal(str(row["avg_cost"])),
                    "current_price": Decimal(str(row["current_price"] or 0)),
                    "market_value": Decimal(str(row["market_value"] or 0)),
                    "unrealized_pnl": Decimal(str(row["unrealized_pnl"] or 0)),
                    "return_percent": Decimal(str(row["return_percent"] or 0))
                })
            
            # Get cash balance
            cash_balance = await _get_cash_balance(user_id)
            
            # Calculate totals
            total_portfolio_value = sum(pos["market_value"] for pos in positions)
            total_value = cash_balance + total_portfolio_value
            
            span.set_attribute("positions.count", len(positions))
            span.set_attribute("total_value", float(total_value))
            span.set_attribute("status", "success")
            
            return {
                "status": ToolStatus.SUCCESS,
                "positions": positions,
                "cash_balance": cash_balance,
                "total_value": total_value,
                "total_return": sum(pos["unrealized_pnl"] for pos in positions),
                "total_return_percent": Decimal("0"),  # Would calculate based on initial investment
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            span.set_status(Status(StatusCode.ERROR, str(e)))
            
            logger.error(f"Portfolio tool failed: {e}")
            return {
                "status": ToolStatus.ERROR,
                "error_message": str(e),
                "timestamp": datetime.utcnow()
            }
