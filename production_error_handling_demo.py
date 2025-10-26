#!/usr/bin/env python3
"""
Production-Ready Error Handling in Exercise 5 Trading Agent
Comprehensive demonstration of error handling patterns and implementations
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Type
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from fastapi import HTTPException
from pydantic import ValidationError

# Configure logging for demonstration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorCategory(str, Enum):
    """Error categories for systematic handling"""
    VALIDATION_ERROR = "validation_error"
    PERMISSION_ERROR = "permission_error"
    NETWORK_ERROR = "network_error"
    DATABASE_ERROR = "database_error"
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    SYSTEM_ERROR = "system_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"

@dataclass
class ErrorContext:
    """Comprehensive error context for debugging and monitoring"""
    error_id: str
    category: ErrorCategory
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    tool_name: Optional[str] = None
    trace_id: Optional[str] = None
    retry_count: int = 0
    is_recoverable: bool = True

class ProductionErrorHandler:
    """
    Production-ready error handling system from Exercise 5
    Demonstrates comprehensive error management patterns
    """
    
    def __init__(self):
        self.error_history: List[ErrorContext] = []
        self.error_counts: Dict[ErrorCategory, int] = {}
    
    def handle_validation_error(self, error: ValidationError, context: Dict[str, Any]) -> ErrorContext:
        """
        Handle Pydantic validation errors with detailed context
        From: tools/registry.py execute_tool() method
        """
        
        # Extract detailed validation error information
        error_details = []
        for pydantic_error in error.errors():
            error_detail = {
                "field": ".".join(str(loc) for loc in pydantic_error["loc"]),
                "message": pydantic_error["msg"],
                "type": pydantic_error["type"],
                "input_value": str(pydantic_error.get("input", "")),
                "context": pydantic_error.get("ctx", {})
            }
            error_details.append(error_detail)
        
        error_context = ErrorContext(
            error_id=f"VAL_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            category=ErrorCategory.VALIDATION_ERROR,
            message=f"Input validation failed: {len(error_details)} field errors",
            details={
                "validation_errors": error_details,
                "input_data": context.get("input_data", {}),
                "model_name": context.get("model_name", "Unknown"),
                "field_count": len(error_details),
                "error_summary": [err["field"] for err in error_details]
            },
            timestamp=datetime.utcnow(),
            user_id=context.get("user_id"),
            tool_name=context.get("tool_name"),
            is_recoverable=True  # Validation errors are usually fixable
        )
        
        self._record_error(error_context)
        
        # Log structured error information
        logger.error(f"Validation Error [{error_context.error_id}]: {error_context.message}")
        for detail in error_details:
            logger.error(f"  Field '{detail['field']}': {detail['message']}")
        
        return error_context
    
    def handle_permission_error(self, error: PermissionError, context: Dict[str, Any]) -> ErrorContext:
        """
        Handle permission and authorization errors
        From: tools/registry.py _check_permissions() method
        """
        
        error_context = ErrorContext(
            error_id=f"PERM_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            category=ErrorCategory.PERMISSION_ERROR,
            message=str(error),
            details={
                "required_permissions": context.get("required_permissions", []),
                "user_roles": context.get("user_roles", []),
                "tool_name": context.get("tool_name"),
                "permission_level": context.get("permission_level"),
                "sandbox_enabled": context.get("sandbox_enabled", False),
                "rate_limit_exceeded": context.get("rate_limit_exceeded", False)
            },
            timestamp=datetime.utcnow(),
            user_id=context.get("user_id"),
            tool_name=context.get("tool_name"),
            is_recoverable=False  # Permission errors require admin intervention
        )
        
        self._record_error(error_context)
        
        # Log security-related error
        logger.warning(f"Permission Error [{error_context.error_id}]: {error_context.message}")
        logger.warning(f"  User: {context.get('user_id')} | Tool: {context.get('tool_name')}")
        
        return error_context
    
    def handle_network_error(self, error: Exception, context: Dict[str, Any]) -> ErrorContext:
        """
        Handle network and connectivity errors with retry logic
        From: tools/reliability.py execute_with_retry() function
        """
        
        # Determine if error is retryable
        retryable_types = [ConnectionError, TimeoutError, asyncio.TimeoutError]
        is_retryable = any(isinstance(error, exc_type) for exc_type in retryable_types)
        
        error_context = ErrorContext(
            error_id=f"NET_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            category=ErrorCategory.NETWORK_ERROR,
            message=f"Network error: {str(error)}",
            details={
                "error_type": type(error).__name__,
                "is_retryable": is_retryable,
                "endpoint": context.get("endpoint"),
                "timeout_seconds": context.get("timeout_seconds"),
                "retry_attempt": context.get("retry_attempt", 0),
                "max_retries": context.get("max_retries", 3),
                "circuit_breaker_state": context.get("circuit_breaker_state", "unknown")
            },
            timestamp=datetime.utcnow(),
            user_id=context.get("user_id"),
            tool_name=context.get("tool_name"),
            retry_count=context.get("retry_attempt", 0),
            is_recoverable=is_retryable
        )
        
        self._record_error(error_context)
        
        # Log with appropriate level based on retry status
        if is_retryable and error_context.retry_count < context.get("max_retries", 3):
            logger.warning(f"Network Error [{error_context.error_id}]: {error_context.message} (will retry)")
        else:
            logger.error(f"Network Error [{error_context.error_id}]: {error_context.message} (giving up)")
        
        return error_context
    
    def handle_database_error(self, error: Exception, context: Dict[str, Any]) -> ErrorContext:
        """
        Handle database connection and query errors
        From: app.py database connection handling
        """
        
        error_context = ErrorContext(
            error_id=f"DB_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            category=ErrorCategory.DATABASE_ERROR,
            message=f"Database error: {str(error)}",
            details={
                "error_type": type(error).__name__,
                "query": context.get("query", "Unknown"),
                "database_url": context.get("database_url", "").split("@")[-1] if context.get("database_url") else "Unknown",
                "connection_available": context.get("connection_available", False),
                "transaction_active": context.get("transaction_active", False),
                "retry_count": context.get("retry_count", 0)
            },
            timestamp=datetime.utcnow(),
            user_id=context.get("user_id"),
            tool_name=context.get("tool_name"),
            is_recoverable=True  # Most DB errors are recoverable
        )
        
        self._record_error(error_context)
        
        logger.error(f"Database Error [{error_context.error_id}]: {error_context.message}")
        
        return error_context
    
    def handle_business_logic_error(self, error: Exception, context: Dict[str, Any]) -> ErrorContext:
        """
        Handle business logic and trading-specific errors
        From: tools/stock_tools.py trading validation
        """
        
        error_context = ErrorContext(
            error_id=f"BIZ_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            category=ErrorCategory.BUSINESS_LOGIC_ERROR,
            message=f"Business logic error: {str(error)}",
            details={
                "error_type": type(error).__name__,
                "operation": context.get("operation"),
                "symbol": context.get("symbol"),
                "amount": context.get("amount"),
                "cash_balance": context.get("cash_balance"),
                "market_hours": context.get("market_hours", "unknown"),
                "validation_rules": context.get("validation_rules", [])
            },
            timestamp=datetime.utcnow(),
            user_id=context.get("user_id"),
            tool_name=context.get("tool_name"),
            is_recoverable=False  # Business logic errors usually need user correction
        )
        
        self._record_error(error_context)
        
        logger.warning(f"Business Logic Error [{error_context.error_id}]: {error_context.message}")
        
        return error_context
    
    def handle_system_error(self, error: Exception, context: Dict[str, Any]) -> ErrorContext:
        """
        Handle unexpected system errors and exceptions
        From: app.py global exception handlers
        """
        
        error_context = ErrorContext(
            error_id=f"SYS_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            category=ErrorCategory.SYSTEM_ERROR,
            message=f"System error: {str(error)}",
            details={
                "error_type": type(error).__name__,
                "stack_trace": str(error.__traceback__) if error.__traceback__ else None,
                "module": context.get("module"),
                "function": context.get("function"),
                "line_number": context.get("line_number"),
                "system_state": context.get("system_state", {})
            },
            timestamp=datetime.utcnow(),
            user_id=context.get("user_id"),
            tool_name=context.get("tool_name"),
            is_recoverable=False  # System errors usually require investigation
        )
        
        self._record_error(error_context)
        
        logger.critical(f"System Error [{error_context.error_id}]: {error_context.message}")
        
        return error_context
    
    def _record_error(self, error_context: ErrorContext):
        """Record error for monitoring and analysis"""
        self.error_history.append(error_context)
        
        # Update error counts
        if error_context.category in self.error_counts:
            self.error_counts[error_context.category] += 1
        else:
            self.error_counts[error_context.category] = 1
        
        # Trigger alerts for critical errors
        if error_context.category in [ErrorCategory.SYSTEM_ERROR, ErrorCategory.PERMISSION_ERROR]:
            self._trigger_alert(error_context)
    
    def _trigger_alert(self, error_context: ErrorContext):
        """Trigger monitoring alerts for critical errors"""
        logger.critical(f"🚨 ALERT: Critical error detected - {error_context.error_id}")
        # In production, this would integrate with monitoring systems like PagerDuty, Slack, etc.
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get comprehensive error summary for monitoring"""
        recent_errors = [err for err in self.error_history if 
                        (datetime.utcnow() - err.timestamp).total_seconds() < 3600]  # Last hour
        
        return {
            "total_errors": len(self.error_history),
            "recent_errors": len(recent_errors),
            "error_counts_by_category": self.error_counts,
            "recent_error_rate": len(recent_errors) / 60,  # Errors per minute
            "most_common_errors": sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "recoverable_errors": len([err for err in recent_errors if err.is_recoverable]),
            "critical_errors": len([err for err in recent_errors if not err.is_recoverable])
        }

# FastAPI Error Handlers (from app.py)
class FastAPIErrorHandlers:
    """
    FastAPI-specific error handling patterns from Exercise 5
    Demonstrates HTTP error response handling
    """
    
    @staticmethod
    def validation_error_handler(error: ValidationError) -> HTTPException:
        """Convert Pydantic validation errors to HTTP 400 responses"""
        error_details = []
        for pydantic_error in error.errors():
            error_details.append({
                "field": ".".join(str(loc) for loc in pydantic_error["loc"]),
                "message": pydantic_error["msg"],
                "type": pydantic_error["type"]
            })
        
        return HTTPException(
            status_code=400,
            detail={
                "error": "Validation Error",
                "message": "Input validation failed",
                "errors": error_details,
                "error_count": len(error_details)
            }
        )
    
    @staticmethod
    def permission_error_handler(error: PermissionError) -> HTTPException:
        """Convert permission errors to HTTP 403 responses"""
        return HTTPException(
            status_code=403,
            detail={
                "error": "Permission Denied",
                "message": str(error),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def database_error_handler(error: Exception) -> HTTPException:
        """Convert database errors to HTTP 503 responses"""
        return HTTPException(
            status_code=503,
            detail={
                "error": "Service Unavailable",
                "message": "Database service temporarily unavailable",
                "retry_after": 30,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def generic_error_handler(error: Exception) -> HTTPException:
        """Convert generic errors to HTTP 500 responses"""
        return HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "error_type": type(error).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Circuit Breaker Error Handling (from tools/reliability.py)
class CircuitBreakerErrorHandling:
    """
    Circuit breaker error handling patterns
    Demonstrates fault tolerance and service protection
    """
    
    @staticmethod
    def handle_circuit_open_error(service_name: str, failure_count: int) -> Exception:
        """Handle circuit breaker open state"""
        error_msg = f"Circuit breaker OPEN for {service_name} (failures: {failure_count})"
        logger.error(error_msg)
        return Exception(f"Service {service_name} temporarily unavailable - circuit breaker activated")
    
    @staticmethod
    def handle_timeout_error(service_name: str, timeout_seconds: float) -> Exception:
        """Handle service timeout errors"""
        error_msg = f"Service {service_name} timeout after {timeout_seconds}s"
        logger.warning(error_msg)
        return TimeoutError(error_msg)

def demo_production_error_handling():
    """Demonstrate production-ready error handling patterns"""
    
    print("🔧 Production-Ready Error Handling in Exercise 5")
    print("=" * 60)
    print()
    
    error_handler = ProductionErrorHandler()
    
    # Demo 1: Validation Error Handling
    print("📋 1. Validation Error Handling")
    try:
        # Simulate Pydantic validation error
        from pydantic import BaseModel, Field
        
        class TradeInput(BaseModel):
            symbol: str = Field(..., min_length=1, max_length=5)
            amount: float = Field(..., gt=0)
        
        # This will cause validation errors
        TradeInput(symbol="", amount=-100)
        
    except ValidationError as e:
        context = {
            "input_data": {"symbol": "", "amount": -100},
            "model_name": "TradeInput",
            "user_id": "demo_user",
            "tool_name": "execute_trade"
        }
        error_ctx = error_handler.handle_validation_error(e, context)
        print(f"   ✅ Handled validation error: {error_ctx.error_id}")
        print(f"   📊 Error details: {len(error_ctx.details['validation_errors'])} field errors")
    
    # Demo 2: Permission Error Handling
    print("\n🔒 2. Permission Error Handling")
    perm_error = PermissionError("User 'guest' lacks 'trader' role for tool 'execute_trade'")
    context = {
        "user_id": "guest",
        "tool_name": "execute_trade",
        "required_permissions": ["trader"],
        "user_roles": ["guest"],
        "permission_level": "AUTHENTICATED"
    }
    error_ctx = error_handler.handle_permission_error(perm_error, context)
    print(f"   ✅ Handled permission error: {error_ctx.error_id}")
    print(f"   🚫 Recoverable: {error_ctx.is_recoverable}")
    
    # Demo 3: Network Error Handling
    print("\n🌐 3. Network Error Handling")
    network_error = ConnectionError("Failed to connect to market data API")
    context = {
        "endpoint": "https://api.marketdata.com/quotes",
        "timeout_seconds": 15.0,
        "retry_attempt": 1,
        "max_retries": 3,
        "user_id": "trader_001",
        "tool_name": "stock_quote"
    }
    error_ctx = error_handler.handle_network_error(network_error, context)
    print(f"   ✅ Handled network error: {error_ctx.error_id}")
    print(f"   🔄 Retryable: {error_ctx.is_recoverable}")
    
    # Demo 4: Database Error Handling
    print("\n💾 4. Database Error Handling")
    db_error = Exception("role 'trader' does not exist")
    context = {
        "query": "SELECT * FROM portfolio WHERE user_id = $1",
        "database_url": "postgresql://trader:***@localhost:5432/trading_db",
        "connection_available": False,
        "user_id": "trader_001",
        "tool_name": "get_portfolio"
    }
    error_ctx = error_handler.handle_database_error(db_error, context)
    print(f"   ✅ Handled database error: {error_ctx.error_id}")
    
    # Demo 5: Business Logic Error Handling
    print("\n💼 5. Business Logic Error Handling")
    biz_error = ValueError("Insufficient cash balance for trade: required $1000, available $500")
    context = {
        "operation": "BUY",
        "symbol": "AAPL",
        "amount": 1000,
        "cash_balance": 500,
        "user_id": "trader_001",
        "tool_name": "execute_trade"
    }
    error_ctx = error_handler.handle_business_logic_error(biz_error, context)
    print(f"   ✅ Handled business logic error: {error_ctx.error_id}")
    
    # Demo 6: Error Summary and Monitoring
    print("\n📊 6. Error Summary and Monitoring")
    summary = error_handler.get_error_summary()
    print(f"   📈 Total errors recorded: {summary['total_errors']}")
    print(f"   ⏰ Recent errors (last hour): {summary['recent_errors']}")
    print(f"   📊 Error rate: {summary['recent_error_rate']:.2f} errors/minute")
    print(f"   🔄 Recoverable errors: {summary['recoverable_errors']}")
    print(f"   🚨 Critical errors: {summary['critical_errors']}")
    
    print("\n🎯 Key Production Error Handling Features:")
    print("   ✅ Structured error categorization")
    print("   ✅ Comprehensive error context capture")
    print("   ✅ Automatic error logging and monitoring")
    print("   ✅ Retry logic with exponential backoff")
    print("   ✅ Circuit breaker fault tolerance")
    print("   ✅ HTTP error response standardization")
    print("   ✅ Security-aware permission error handling")
    print("   ✅ Business logic validation with user feedback")
    print("   ✅ Real-time error rate monitoring")
    print("   ✅ Alert triggering for critical errors")

if __name__ == "__main__":
    demo_production_error_handling()



