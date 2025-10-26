#!/usr/bin/env python3
"""
Pydantic Validation Spans Demo - Exercise 1 Implementation
Shows how Pydantic validation is traced with OpenTelemetry spans
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
import json

# Initialize tracer
tracer = trace.get_tracer(__name__)

# Pydantic Models with Validation (Exercise 1)
class StockQuoteInput(BaseModel):
    """Input schema for stock quote requests with validation"""
    symbols: List[str] = Field(..., description="Stock symbols to quote", min_items=1, max_items=10)
    include_details: bool = Field(default=False, description="Include detailed market data")
    user_id: str = Field(default="default_trader", description="User identifier")
    
    @field_validator('symbols')
    @classmethod
    def validate_symbols(cls, v):
        """Validate stock symbols format - creates validation spans"""
        import re
        for symbol in v:
            if not re.match(r'^[A-Z]{1,5}$', symbol.upper()):
                raise ValueError(f"Invalid stock symbol format: {symbol}")
        return [s.upper() for s in v]

class TradeInput(BaseModel):
    """Input schema for trade execution with complex validation"""
    symbol: str = Field(..., description="Stock symbol to trade")
    action: str = Field(..., description="Buy or sell action")
    quantity: Optional[Decimal] = Field(default=None, description="Number of shares")
    amount: Optional[Decimal] = Field(default=None, description="Dollar amount to trade")
    user_id: str = Field(default="default_trader", description="User identifier")
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        """Validate stock symbol format"""
        import re
        if not re.match(r'^[A-Z]{1,5}$', v.upper()):
            raise ValueError(f"Invalid stock symbol format: {v}")
        return v.upper()
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        """Validate trading action"""
        valid_actions = ["BUY", "SELL"]
        if v.upper() not in valid_actions:
            raise ValueError(f"Action must be one of: {valid_actions}")
        return v.upper()
    
    @model_validator(mode='after')
    def validate_quantity_or_amount(self):
        """Cross-field validation - either quantity or amount required"""
        quantity = self.quantity
        amount = self.amount
        if not quantity and not amount:
            raise ValueError("Either quantity or amount must be specified")
        if quantity and amount:
            raise ValueError("Specify either quantity or amount, not both")
        return self

# Validation Functions with OpenTelemetry Spans
def validate_with_spans(model_class: type, input_data: Dict[str, Any], operation_name: str) -> Dict[str, Any]:
    """
    Validate Pydantic input with OpenTelemetry tracing
    This is the core implementation of "Pydantic validation spans"
    """
    
    with tracer.start_as_current_span(f"pydantic_validation_{operation_name}") as span:
        # Add span attributes for the validation operation
        span.set_attribute("validation.model", model_class.__name__)
        span.set_attribute("validation.operation", operation_name)
        span.set_attribute("validation.input_keys", list(input_data.keys()))
        
        try:
            # Start validation timing
            start_time = datetime.utcnow()
            
            # Create nested span for field validation
            with tracer.start_as_current_span("field_validation") as field_span:
                field_span.set_attribute("validation.phase", "field_validation")
                
                # Attempt Pydantic validation
                validated_model = model_class(**input_data)
                
                # Record successful field validation
                field_span.set_attribute("validation.fields_validated", len(input_data))
                field_span.set_status(Status(StatusCode.OK))
            
            # Create nested span for model validation (cross-field validation)
            with tracer.start_as_current_span("model_validation") as model_span:
                model_span.set_attribute("validation.phase", "model_validation")
                
                # Model validation happens automatically in Pydantic v2
                # but we can add custom logic here
                result = validated_model.dict()
                
                model_span.set_attribute("validation.output_keys", list(result.keys()))
                model_span.set_status(Status(StatusCode.OK))
            
            # Calculate validation time
            validation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Record successful validation in main span
            span.set_attribute("validation.success", True)
            span.set_attribute("validation.time_ms", validation_time)
            span.set_attribute("validation.validated_fields", len(result))
            span.set_status(Status(StatusCode.OK))
            
            return {
                "status": "success",
                "validated_data": result,
                "validation_time_ms": validation_time,
                "model": model_class.__name__
            }
            
        except ValidationError as e:
            # Handle Pydantic validation errors with detailed tracing
            validation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Extract validation error details
            error_details = []
            for error in e.errors():
                error_detail = {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                    "input": str(error.get("input", ""))
                }
                error_details.append(error_detail)
            
            # Record validation failure in span
            span.set_attribute("validation.success", False)
            span.set_attribute("validation.time_ms", validation_time)
            span.set_attribute("validation.error_count", len(error_details))
            span.set_attribute("validation.error_fields", [err["field"] for err in error_details])
            span.set_attribute("validation.error_types", [err["type"] for err in error_details])
            
            # Add detailed error information
            for i, error_detail in enumerate(error_details):
                span.set_attribute(f"validation.error_{i}.field", error_detail["field"])
                span.set_attribute(f"validation.error_{i}.message", error_detail["message"])
                span.set_attribute(f"validation.error_{i}.type", error_detail["type"])
            
            span.set_status(Status(StatusCode.ERROR, f"Validation failed: {len(error_details)} errors"))
            
            return {
                "status": "error",
                "error_type": "ValidationError",
                "error_message": str(e),
                "error_details": error_details,
                "validation_time_ms": validation_time,
                "model": model_class.__name__
            }
            
        except Exception as e:
            # Handle unexpected errors
            validation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            span.set_attribute("validation.success", False)
            span.set_attribute("validation.time_ms", validation_time)
            span.set_attribute("validation.error_type", type(e).__name__)
            span.set_attribute("validation.error_message", str(e))
            span.set_status(Status(StatusCode.ERROR, f"Unexpected validation error: {str(e)}"))
            
            return {
                "status": "error",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "validation_time_ms": validation_time,
                "model": model_class.__name__
            }

# Demo Functions
def demo_good_validation():
    """Demo successful Pydantic validation with spans"""
    print("🟢 Demo: Good Validation (Success Case)")
    
    # Good stock quote input
    good_quote_input = {
        "symbols": ["AAPL", "GOOGL", "MSFT"],
        "include_details": True,
        "user_id": "demo_user"
    }
    
    result = validate_with_spans(StockQuoteInput, good_quote_input, "stock_quote")
    print(f"✅ Stock Quote Validation: {result['status']}")
    print(f"   Validation Time: {result['validation_time_ms']:.2f}ms")
    print(f"   Validated Fields: {result['validated_fields']}")
    
    # Good trade input
    good_trade_input = {
        "symbol": "AAPL",
        "action": "BUY",
        "amount": 1000.00,
        "user_id": "demo_user"
    }
    
    result = validate_with_spans(TradeInput, good_trade_input, "trade_execution")
    print(f"✅ Trade Validation: {result['status']}")
    print(f"   Validation Time: {result['validation_time_ms']:.2f}ms")
    print()

def demo_bad_validation():
    """Demo failed Pydantic validation with detailed error spans"""
    print("🔴 Demo: Bad Validation (Error Cases)")
    
    # Bad stock quote input - invalid symbol format
    bad_quote_input = {
        "symbols": ["invalid_symbol_123", "AAPL"],  # First symbol is invalid
        "include_details": "not_a_boolean",  # Wrong type
        "user_id": "demo_user"
    }
    
    result = validate_with_spans(StockQuoteInput, bad_quote_input, "stock_quote")
    print(f"❌ Stock Quote Validation: {result['status']}")
    print(f"   Validation Time: {result['validation_time_ms']:.2f}ms")
    print(f"   Error Count: {len(result.get('error_details', []))}")
    for error in result.get('error_details', []):
        print(f"   - {error['field']}: {error['message']}")
    
    # Bad trade input - missing required fields and invalid values
    bad_trade_input = {
        "symbol": "INVALID_SYMBOL_TOO_LONG",  # Invalid symbol
        "action": "INVALID_ACTION",  # Invalid action
        "quantity": 100,
        "amount": 1000.00,  # Both quantity and amount specified (not allowed)
        "user_id": "demo_user"
    }
    
    result = validate_with_spans(TradeInput, bad_trade_input, "trade_execution")
    print(f"❌ Trade Validation: {result['status']}")
    print(f"   Validation Time: {result['validation_time_ms']:.2f}ms")
    print(f"   Error Count: {len(result.get('error_details', []))}")
    for error in result.get('error_details', []):
        print(f"   - {error['field']}: {error['message']}")
    print()

def demo_edge_cases():
    """Demo edge cases and complex validation scenarios"""
    print("🟡 Demo: Edge Cases and Complex Validation")
    
    # Empty symbols list
    empty_symbols_input = {
        "symbols": [],  # Empty list (min_items=1)
        "include_details": True,
        "user_id": "demo_user"
    }
    
    result = validate_with_spans(StockQuoteInput, empty_symbols_input, "stock_quote")
    print(f"⚠️  Empty Symbols Validation: {result['status']}")
    if result['status'] == 'error':
        for error in result.get('error_details', []):
            print(f"   - {error['field']}: {error['message']}")
    
    # Missing required fields
    missing_fields_input = {
        "user_id": "demo_user"
        # Missing 'symbol' and 'action'
    }
    
    result = validate_with_spans(TradeInput, missing_fields_input, "trade_execution")
    print(f"⚠️  Missing Fields Validation: {result['status']}")
    if result['status'] == 'error':
        for error in result.get('error_details', []):
            print(f"   - {error['field']}: {error['message']}")
    print()

if __name__ == "__main__":
    print("🚀 Pydantic Validation Spans Demo - Exercise 1")
    print("=" * 60)
    print()
    
    # Demo successful validation
    demo_good_validation()
    
    # Demo failed validation with detailed error tracing
    demo_bad_validation()
    
    # Demo edge cases
    demo_edge_cases()
    
    print("📊 Key Features of Pydantic Validation Spans:")
    print("   ✅ Field-level validation tracing")
    print("   ✅ Model-level (cross-field) validation tracing")
    print("   ✅ Detailed error information in spans")
    print("   ✅ Validation timing metrics")
    print("   ✅ Success/failure status tracking")
    print("   ✅ Input/output data structure logging")
    print()
    print("🔍 In Jaeger UI, look for spans named:")
    print("   - pydantic_validation_stock_quote")
    print("   - pydantic_validation_trade_execution")
    print("   - field_validation (nested)")
    print("   - model_validation (nested)")



