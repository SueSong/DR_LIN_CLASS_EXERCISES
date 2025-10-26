"""
Exercise 1: Typed Tools with Pydantic
Comprehensive schemas for all trading agent tools
"""

from typing import Dict, Any, List, Optional, Union, Literal
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
import re

# Base schemas
class ToolStatus(str, Enum):
    """Tool execution status"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    TIMEOUT = "timeout"

class BaseToolInput(BaseModel):
    """Base input schema for all tools"""
    request_id: Optional[str] = Field(default=None, description="Unique request identifier")
    user_id: str = Field(default="default_trader", description="User identifier")
    
    class Config:
        extra = "forbid"

class BaseToolOutput(BaseModel):
    """Base output schema for all tools"""
    status: ToolStatus = Field(..., description="Execution status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Execution timestamp")
    execution_time_ms: Optional[float] = Field(default=None, description="Execution time in milliseconds")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

# Stock Quote Tool (Exercise 1 integration)
class StockQuoteInput(BaseToolInput):
    """Input schema for stock quote requests"""
    symbols: List[str] = Field(..., description="Stock symbols to quote", min_items=1, max_items=10)
    include_details: bool = Field(default=False, description="Include detailed market data")
    
    @field_validator('symbols')
    @classmethod
    def validate_symbols(cls, v):
        """Validate stock symbols format"""
        for symbol in v:
            if not re.match(r'^[A-Z]{1,5}$', symbol.upper()):
                raise ValueError(f"Invalid stock symbol format: {symbol}")
        return [s.upper() for s in v]

class StockQuote(BaseModel):
    """Individual stock quote data"""
    symbol: str = Field(..., description="Stock symbol")
    price: Decimal = Field(..., description="Current price")
    change: Optional[Decimal] = Field(default=None, description="Price change")
    change_percent: Optional[Decimal] = Field(default=None, description="Percentage change")
    volume: Optional[int] = Field(default=None, description="Trading volume")
    market_cap: Optional[int] = Field(default=None, description="Market capitalization")
    pe_ratio: Optional[Decimal] = Field(default=None, description="P/E ratio")
    day_high: Optional[Decimal] = Field(default=None, description="Day high")
    day_low: Optional[Decimal] = Field(default=None, description="Day low")
    year_high: Optional[Decimal] = Field(default=None, description="52-week high")
    year_low: Optional[Decimal] = Field(default=None, description="52-week low")

class StockQuoteOutput(BaseToolOutput):
    """Output schema for stock quotes"""
    quotes: List[StockQuote] = Field(default_factory=list, description="Stock quotes")
    market_status: Optional[str] = Field(default=None, description="Market status")
    data_source: Optional[str] = Field(default=None, description="Data source")

# Portfolio Management Tools
class TransactionType(str, Enum):
    """Transaction types"""
    BUY = "BUY"
    SELL = "SELL"

class TradeInput(BaseToolInput):
    """Input schema for trade execution"""
    symbol: str = Field(..., description="Stock symbol to trade")
    action: TransactionType = Field(..., description="Buy or sell action")
    quantity: Optional[Decimal] = Field(default=None, description="Number of shares")
    amount: Optional[Decimal] = Field(default=None, description="Dollar amount to trade")
    price_limit: Optional[Decimal] = Field(default=None, description="Maximum price for buy, minimum for sell")
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z]{1,5}$', v.upper()):
            raise ValueError(f"Invalid stock symbol format: {v}")
        return v.upper()
    
    @model_validator(mode='after')
    def validate_quantity_or_amount(self):
        quantity = self.quantity
        amount = self.amount
        if not quantity and not amount:
            raise ValueError("Either quantity or amount must be specified")
        if quantity and amount:
            raise ValueError("Specify either quantity or amount, not both")
        return self

class TradeOutput(BaseToolOutput):
    """Output schema for trade execution"""
    transaction_id: Optional[str] = Field(default=None, description="Transaction ID")
    symbol: Optional[str] = Field(default=None, description="Stock symbol")
    action: Optional[TransactionType] = Field(default=None, description="Executed action")
    shares: Optional[Decimal] = Field(default=None, description="Number of shares traded")
    price: Optional[Decimal] = Field(default=None, description="Execution price")
    total_amount: Optional[Decimal] = Field(default=None, description="Total transaction amount")
    fees: Optional[Decimal] = Field(default=Decimal('0'), description="Transaction fees")
    remaining_cash: Optional[Decimal] = Field(default=None, description="Remaining cash balance")

# Portfolio Query Tools
class PortfolioInput(BaseToolInput):
    """Input schema for portfolio queries"""
    include_performance: bool = Field(default=True, description="Include performance metrics")
    include_unrealized_pnl: bool = Field(default=True, description="Include unrealized P&L")

class PortfolioPosition(BaseModel):
    """Individual portfolio position"""
    symbol: str = Field(..., description="Stock symbol")
    shares: Decimal = Field(..., description="Number of shares")
    avg_cost: Decimal = Field(..., description="Average cost per share")
    current_price: Decimal = Field(..., description="Current market price")
    market_value: Decimal = Field(..., description="Current market value")
    unrealized_pnl: Decimal = Field(..., description="Unrealized profit/loss")
    return_percent: Decimal = Field(..., description="Return percentage")

class PortfolioOutput(BaseToolOutput):
    """Output schema for portfolio data"""
    positions: List[PortfolioPosition] = Field(default_factory=list, description="Portfolio positions")
    cash_balance: Decimal = Field(..., description="Available cash")
    total_value: Decimal = Field(..., description="Total portfolio value")
    total_return: Decimal = Field(default=Decimal('0'), description="Total return")
    total_return_percent: Decimal = Field(default=Decimal('0'), description="Total return percentage")

# LLM Recommendation Tools
class RecommendationInput(BaseToolInput):
    """Input schema for LLM trading recommendations"""
    market_data: Dict[str, Any] = Field(..., description="Current market data")
    portfolio_data: Dict[str, Any] = Field(..., description="Current portfolio state")
    cash_balance: Decimal = Field(..., description="Available cash")
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance level")
    investment_goals: List[str] = Field(default_factory=list, description="Investment objectives")
    
    @field_validator('risk_tolerance')
    @classmethod
    def validate_risk_tolerance(cls, v):
        valid_levels = ["conservative", "moderate", "aggressive"]
        if v.lower() not in valid_levels:
            raise ValueError(f"Risk tolerance must be one of: {valid_levels}")
        return v.lower()

class TradingRecommendation(BaseModel):
    """Individual trading recommendation"""
    symbol: str = Field(..., description="Stock symbol")
    action: TransactionType = Field(..., description="Recommended action")
    quantity: Optional[Decimal] = Field(default=None, description="Recommended quantity")
    amount: Optional[Decimal] = Field(default=None, description="Recommended dollar amount")
    reasoning: str = Field(..., description="LLM reasoning for recommendation")
    confidence: Decimal = Field(..., description="Confidence score 0-1")
    priority: int = Field(..., description="Priority ranking")

class RecommendationOutput(BaseToolOutput):
    """Output schema for trading recommendations"""
    recommendations: List[TradingRecommendation] = Field(default_factory=list, description="Trading recommendations")
    market_analysis: str = Field(..., description="Overall market analysis")
    portfolio_analysis: str = Field(..., description="Portfolio analysis")
    risk_assessment: str = Field(..., description="Risk assessment")
    cash_allocation: Decimal = Field(..., description="Recommended cash allocation percentage")

# Report Generation Tools
class ReportInput(BaseToolInput):
    """Input schema for report generation"""
    report_date: date = Field(default_factory=date.today, description="Report date")
    report_type: str = Field(default="daily", description="Report type")
    include_charts: bool = Field(default=False, description="Include performance charts")
    
    @field_validator('report_type')
    @classmethod
    def validate_report_type(cls, v):
        valid_types = ["daily", "weekly", "monthly", "custom"]
        if v.lower() not in valid_types:
            raise ValueError(f"Report type must be one of: {valid_types}")
        return v.lower()

class ReportOutput(BaseToolOutput):
    """Output schema for generated reports"""
    report_id: str = Field(..., description="Generated report ID")
    file_path: str = Field(..., description="Path to generated report file")
    report_summary: Dict[str, Any] = Field(..., description="Report summary data")
    performance_metrics: Dict[str, Decimal] = Field(..., description="Performance metrics")

# Database Tools
class DatabaseQueryInput(BaseToolInput):
    """Input schema for database queries"""
    query_type: str = Field(..., description="Type of query")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    
    @field_validator('query_type')
    @classmethod
    def validate_query_type(cls, v):
        valid_types = ["portfolio", "transactions", "quotes", "reports", "balance"]
        if v.lower() not in valid_types:
            raise ValueError(f"Query type must be one of: {valid_types}")
        return v.lower()

class DatabaseQueryOutput(BaseToolOutput):
    """Output schema for database queries"""
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Query results")
    row_count: int = Field(default=0, description="Number of rows returned")

# File Operations (from Exercise 2)
class FileOperation(str, Enum):
    """File operation types"""
    READ = "read"
    WRITE = "write"
    APPEND = "append"
    DELETE = "delete"

class FileOperationInput(BaseToolInput):
    """Input schema for file operations"""
    operation: FileOperation = Field(..., description="File operation to perform")
    file_path: str = Field(..., description="File path")
    content: Optional[str] = Field(default=None, description="Content for write/append operations")
    encoding: str = Field(default="utf-8", description="File encoding")
    
    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v):
        # Basic path validation - no traversal attacks
        if '..' in v or v.startswith('/'):
            raise ValueError("Invalid file path - path traversal not allowed")
        return v

class FileOperationOutput(BaseToolOutput):
    """Output schema for file operations"""
    operation: FileOperation = Field(..., description="Performed operation")
    file_path: str = Field(..., description="File path")
    content: Optional[str] = Field(default=None, description="File content for read operations")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")

# Validation functions for good vs bad inputs (Exercise 1 demo)
def validate_stock_quote_input(data: Dict[str, Any]) -> StockQuoteInput:
    """Validate stock quote input - demo for Exercise 1"""
    try:
        return StockQuoteInput(**data)
    except Exception as e:
        raise ValueError(f"Invalid stock quote input: {e}")

def validate_trade_input(data: Dict[str, Any]) -> TradeInput:
    """Validate trade input - demo for Exercise 1"""
    try:
        return TradeInput(**data)
    except Exception as e:
        raise ValueError(f"Invalid trade input: {e}")

# Example usage for Exercise 1 demo
EXAMPLE_GOOD_INPUTS = {
    "stock_quote": {
        "symbols": ["AAPL", "GOOGL", "MSFT"],
        "include_details": True
    },
    "trade": {
        "symbol": "AAPL",
        "action": "BUY",
        "amount": 1000.00
    }
}

EXAMPLE_BAD_INPUTS = {
    "stock_quote": {
        "symbols": ["invalid_symbol_123"],  # Invalid format
        "include_details": "not_a_boolean"  # Wrong type
    },
    "trade": {
        "symbol": "INVALID",
        "action": "INVALID_ACTION",  # Invalid enum
        # Missing quantity or amount
    }
}
