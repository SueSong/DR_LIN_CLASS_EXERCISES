#!/usr/bin/env python3
"""
Actual Pydantic Validation Spans Implementation from Trading Agent
This shows how validation spans are implemented in the real Exercise 5 code
"""

from typing import Dict, Any, Optional, Set
from datetime import datetime
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class ToolRegistry:
    """
    Simplified version of the actual registry showing validation spans
    From: /monorepo/apps/trading-agent/tools/registry.py
    """
    
    async def execute_tool(
        self,
        name: str,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None,
        user_roles: Optional[Set[str]] = None,
        trace_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a registered tool with Pydantic validation spans
        This is where the "Pydantic validation spans" are actually created
        """
        
        # Create main execution span
        with tracer.start_as_current_span(f"tool_execution_{name}") as main_span:
            main_span.set_attribute("tool.name", name)
            main_span.set_attribute("tool.user_id", user_id or "anonymous")
            main_span.set_attribute("tool.input_keys", list(input_data.keys()))
            
            try:
                # Get tool metadata
                tool = self.get_tool(name)
                if not tool:
                    raise ValueError(f"Tool '{name}' not found")
                
                # === PYDANTIC INPUT VALIDATION SPAN ===
                with tracer.start_as_current_span("pydantic_input_validation") as input_span:
                    input_span.set_attribute("validation.phase", "input")
                    input_span.set_attribute("validation.model", tool.metadata.input_schema.__name__)
                    input_span.set_attribute("validation.field_count", len(input_data))
                    
                    validation_start = datetime.utcnow()
                    
                    try:
                        # This is where Pydantic validation happens with tracing
                        validated_input = tool.metadata.input_schema(**input_data)
                        
                        # Record successful validation
                        validation_time = (datetime.utcnow() - validation_start).total_seconds() * 1000
                        input_span.set_attribute("validation.success", True)
                        input_span.set_attribute("validation.time_ms", validation_time)
                        input_span.set_attribute("validation.validated_fields", len(validated_input.dict()))
                        input_span.set_status(Status(StatusCode.OK))
                        
                        # Add field-specific validation details
                        for field_name, field_value in validated_input.dict().items():
                            input_span.set_attribute(f"validation.field.{field_name}", str(type(field_value).__name__))
                        
                    except ValidationError as e:
                        # Record validation failure with detailed error information
                        validation_time = (datetime.utcnow() - validation_start).total_seconds() * 1000
                        
                        # Extract Pydantic error details
                        error_details = []
                        for error in e.errors():
                            error_detail = {
                                "field": ".".join(str(loc) for loc in error["loc"]),
                                "message": error["msg"],
                                "type": error["type"],
                                "input_value": str(error.get("input", ""))
                            }
                            error_details.append(error_detail)
                        
                        # Add detailed error attributes to span
                        input_span.set_attribute("validation.success", False)
                        input_span.set_attribute("validation.time_ms", validation_time)
                        input_span.set_attribute("validation.error_count", len(error_details))
                        input_span.set_attribute("validation.error_fields", [err["field"] for err in error_details])
                        
                        # Add individual error details
                        for i, error_detail in enumerate(error_details[:5]):  # Limit to first 5 errors
                            input_span.set_attribute(f"validation.error_{i}.field", error_detail["field"])
                            input_span.set_attribute(f"validation.error_{i}.message", error_detail["message"])
                            input_span.set_attribute(f"validation.error_{i}.type", error_detail["type"])
                        
                        input_span.set_status(Status(StatusCode.ERROR, f"Input validation failed: {len(error_details)} errors"))
                        
                        # Re-raise with enhanced error message
                        raise ValueError(f"Invalid input for tool '{name}': {e}")
                
                # Execute the actual tool
                with tracer.start_as_current_span("tool_handler_execution") as handler_span:
                    handler_span.set_attribute("tool.handler", tool.handler.__name__)
                    
                    # Execute tool with validated input
                    if tool.metadata.permission.sandbox_enabled:
                        result = await self._execute_sandboxed(tool, validated_input.dict(), trace_context)
                    else:
                        result = await self._execute_direct(tool, validated_input.dict(), trace_context)
                    
                    handler_span.set_attribute("tool.execution.success", True)
                    handler_span.set_status(Status(StatusCode.OK))
                
                # === PYDANTIC OUTPUT VALIDATION SPAN ===
                with tracer.start_as_current_span("pydantic_output_validation") as output_span:
                    output_span.set_attribute("validation.phase", "output")
                    output_span.set_attribute("validation.model", tool.metadata.output_schema.__name__)
                    output_span.set_attribute("validation.result_keys", list(result.keys()) if isinstance(result, dict) else [])
                    
                    validation_start = datetime.utcnow()
                    
                    try:
                        # Validate output with Pydantic
                        validated_output = tool.metadata.output_schema(**result)
                        
                        # Record successful output validation
                        validation_time = (datetime.utcnow() - validation_start).total_seconds() * 1000
                        output_span.set_attribute("validation.success", True)
                        output_span.set_attribute("validation.time_ms", validation_time)
                        output_span.set_attribute("validation.validated_fields", len(validated_output.dict()))
                        output_span.set_status(Status(StatusCode.OK))
                        
                        # Add output field types
                        for field_name, field_value in validated_output.dict().items():
                            output_span.set_attribute(f"validation.output.{field_name}", str(type(field_value).__name__))
                        
                    except ValidationError as e:
                        # Record output validation failure
                        validation_time = (datetime.utcnow() - validation_start).total_seconds() * 1000
                        
                        output_span.set_attribute("validation.success", False)
                        output_span.set_attribute("validation.time_ms", validation_time)
                        output_span.set_attribute("validation.error_message", str(e))
                        output_span.set_status(Status(StatusCode.ERROR, f"Output validation failed: {str(e)}"))
                        
                        logger.error(f"Output validation failed for tool '{name}': {e}")
                        
                        # For output validation failures, we might want to return a generic error
                        # rather than exposing internal validation details
                        validated_output = tool.metadata.output_schema(
                            status="error",
                            error_message="Internal validation error",
                            timestamp=datetime.utcnow()
                        )
                
                # Record successful tool execution
                main_span.set_attribute("tool.execution.success", True)
                main_span.set_attribute("tool.execution.input_valid", True)
                main_span.set_attribute("tool.execution.output_valid", True)
                main_span.set_status(Status(StatusCode.OK))
                
                return validated_output.dict()
                
            except Exception as e:
                # Record tool execution failure
                main_span.set_attribute("tool.execution.success", False)
                main_span.set_attribute("tool.execution.error_type", type(e).__name__)
                main_span.set_attribute("tool.execution.error_message", str(e))
                main_span.set_status(Status(StatusCode.ERROR, f"Tool execution failed: {str(e)}"))
                
                logger.error(f"Tool '{name}' execution failed: {e}")
                raise

# Example of how validation spans appear in the FastAPI endpoints
async def stock_quotes_endpoint_with_validation_spans(request_data: dict):
    """
    Example FastAPI endpoint showing validation spans
    From: /monorepo/apps/trading-agent/app.py
    """
    
    with tracer.start_as_current_span("api_endpoint_stock_quotes") as endpoint_span:
        endpoint_span.set_attribute("api.endpoint", "/quotes")
        endpoint_span.set_attribute("api.method", "POST")
        
        try:
            # === FASTAPI PYDANTIC VALIDATION SPAN ===
            with tracer.start_as_current_span("fastapi_request_validation") as request_span:
                request_span.set_attribute("validation.framework", "fastapi")
                request_span.set_attribute("validation.model", "StockQuoteInput")
                
                # FastAPI automatically validates with Pydantic
                # We can add custom validation spans here
                from tools.schemas import StockQuoteInput
                
                try:
                    validated_request = StockQuoteInput(**request_data)
                    request_span.set_attribute("validation.success", True)
                    request_span.set_status(Status(StatusCode.OK))
                    
                except ValidationError as e:
                    request_span.set_attribute("validation.success", False)
                    request_span.set_attribute("validation.error_count", len(e.errors()))
                    request_span.set_status(Status(StatusCode.ERROR, f"Request validation failed"))
                    raise
            
            # Execute tool through registry (which has its own validation spans)
            registry = ToolRegistry()
            result = await registry.execute_tool(
                "stock_quote",
                validated_request.dict(),
                user_id=validated_request.user_id,
                user_roles={"trader"}
            )
            
            endpoint_span.set_attribute("api.success", True)
            endpoint_span.set_status(Status(StatusCode.OK))
            
            return result
            
        except Exception as e:
            endpoint_span.set_attribute("api.success", False)
            endpoint_span.set_attribute("api.error", str(e))
            endpoint_span.set_status(Status(StatusCode.ERROR, f"API error: {str(e)}"))
            raise

def main():
    """Demo the validation spans concepts"""
    print("🔍 Pydantic Validation Spans in Exercise 5 Trading Agent")
    print("=" * 60)
    print()
    
    print("📋 Key Validation Spans Created:")
    print("   1. 🔸 pydantic_input_validation")
    print("      - Validates incoming tool parameters")
    print("      - Records field validation errors")
    print("      - Measures validation performance")
    print()
    
    print("   2. 🔸 pydantic_output_validation") 
    print("      - Validates tool output format")
    print("      - Ensures response schema compliance")
    print("      - Catches internal validation issues")
    print()
    
    print("   3. 🔸 fastapi_request_validation")
    print("      - Validates HTTP request bodies")
    print("      - Integrates with FastAPI validation")
    print("      - Provides API-level validation tracing")
    print()
    
    print("🎯 Span Attributes Captured:")
    print("   ✅ validation.model - Pydantic model name")
    print("   ✅ validation.success - True/False")
    print("   ✅ validation.time_ms - Validation duration")
    print("   ✅ validation.field_count - Number of fields")
    print("   ✅ validation.error_count - Number of errors")
    print("   ✅ validation.error_fields - Failed field names")
    print("   ✅ validation.field.{name} - Individual field types")
    print()
    
    print("🔍 In Jaeger UI, search for:")
    print("   - Service: 'trading-agent'")
    print("   - Operation: 'pydantic_input_validation'")
    print("   - Operation: 'pydantic_output_validation'")
    print("   - Tags: validation.success=false (for errors)")
    print()
    
    print("📊 This enables you to:")
    print("   🎯 Track validation performance")
    print("   🎯 Identify common validation errors")
    print("   🎯 Monitor schema compliance")
    print("   🎯 Debug input/output issues")
    print("   🎯 Measure validation overhead")

if __name__ == "__main__":
    main()
