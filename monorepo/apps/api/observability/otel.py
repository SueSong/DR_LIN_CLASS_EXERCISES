"""
OpenTelemetry observability setup with Tracer, Metrics, and Exporter initialization
Includes span attributes for tool.name, retries, latency_ms, and status
"""

import os
import logging
from typing import Optional, Dict, Any
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

logger = logging.getLogger(__name__)

# Global observability state
_tracer_provider: Optional[TracerProvider] = None
_meter_provider: Optional[MeterProvider] = None
_is_initialized = False

def setup_observability(
    service_name: str = "ai-agent-training-api",
    service_version: str = "1.0.0",
    jaeger_endpoint: Optional[str] = None,
    enable_console_export: bool = True
) -> None:
    """
    Initialize OpenTelemetry observability stack
    
    Args:
        service_name: Name of the service
        service_version: Version of the service
        jaeger_endpoint: Jaeger collector endpoint (optional)
        enable_console_export: Whether to enable console exporters
    """
    global _tracer_provider, _meter_provider, _is_initialized
    
    if _is_initialized:
        logger.info("Observability already initialized")
        return
    
    logger.info("Initializing OpenTelemetry observability...")
    
    # Create resource with service information
    resource = Resource.create({
        "service.name": service_name,
        "service.version": service_version,
        "service.instance.id": os.getenv("HOSTNAME", "localhost"),
    })
    
    # Setup tracing
    _setup_tracing(resource, jaeger_endpoint, enable_console_export)
    
    # Setup metrics
    _setup_metrics(resource, enable_console_export)
    
    # Setup automatic instrumentation
    _setup_auto_instrumentation()
    
    _is_initialized = True
    logger.info("OpenTelemetry observability initialized successfully")

def _setup_tracing(
    resource: Resource, 
    jaeger_endpoint: Optional[str], 
    enable_console_export: bool
) -> None:
    """Setup tracing with span processors and exporters"""
    global _tracer_provider
    
    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(_tracer_provider)
    
    # Add console exporter for development
    if enable_console_export:
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        _tracer_provider.add_span_processor(console_processor)
    
    # Add OTLP exporter for Jaeger if endpoint provided
    if jaeger_endpoint:
        try:
            otlp_exporter = OTLPSpanExporter(
                endpoint=jaeger_endpoint,
                insecure=True
            )
            otlp_processor = BatchSpanProcessor(otlp_exporter)
            _tracer_provider.add_span_processor(otlp_processor)
            logger.info(f"OTLP exporter configured: {jaeger_endpoint}")
        except Exception as e:
            logger.warning(f"Failed to setup OTLP exporter: {e}")
    
    # Add default OTLP exporter for local development
    try:
        default_otlp_exporter = OTLPSpanExporter(
            endpoint="http://localhost:4317",
            insecure=True
        )
        default_otlp_processor = BatchSpanProcessor(default_otlp_exporter)
        _tracer_provider.add_span_processor(default_otlp_processor)
        logger.info("Default OTLP exporter configured for localhost:4317")
    except Exception as e:
        logger.warning(f"Failed to setup default OTLP exporter: {e}")

def _setup_metrics(resource: Resource, enable_console_export: bool) -> None:
    """Setup metrics with readers and exporters"""
    global _meter_provider
    
    readers = []
    
    # Add console exporter for development
    if enable_console_export:
        console_reader = PeriodicExportingMetricReader(
            exporter=ConsoleMetricExporter(),
            export_interval_millis=30000,  # 30 seconds
        )
        readers.append(console_reader)
    
    # Create meter provider
    _meter_provider = MeterProvider(
        resource=resource,
        metric_readers=readers
    )
    metrics.set_meter_provider(_meter_provider)

def _setup_auto_instrumentation() -> None:
    """Setup automatic instrumentation for common libraries"""
    try:
        # FastAPI instrumentation
        FastAPIInstrumentor().instrument()
        logger.info("FastAPI instrumentation enabled")
        
        # HTTPX instrumentation
        HTTPXClientInstrumentor().instrument()
        logger.info("HTTPX instrumentation enabled")
        
        # SQLAlchemy instrumentation
        SQLAlchemyInstrumentor().instrument()
        logger.info("SQLAlchemy instrumentation enabled")
        
    except Exception as e:
        logger.warning(f"Failed to setup auto instrumentation: {e}")

def get_tracer(name: str) -> trace.Tracer:
    """
    Get a tracer instance
    
    Args:
        name: Name of the tracer (usually module name)
        
    Returns:
        Tracer instance
    """
    if not _is_initialized:
        setup_observability()
    
    return trace.get_tracer(name)

def get_meter(name: str) -> metrics.Meter:
    """
    Get a meter instance
    
    Args:
        name: Name of the meter (usually module name)
        
    Returns:
        Meter instance
    """
    if not _is_initialized:
        setup_observability()
    
    return metrics.get_meter(name)

class ToolSpan:
    """
    Context manager for tool execution spans with standard attributes
    """
    
    def __init__(self, 
                 tracer: trace.Tracer,
                 tool_name: str,
                 operation: Optional[str] = None,
                 **attributes):
        self.tracer = tracer
        self.tool_name = tool_name
        self.operation = operation
        self.attributes = attributes
        self.span = None
        self.start_time = None
    
    def __enter__(self):
        import time
        
        span_name = f"{self.tool_name}"
        if self.operation:
            span_name += f".{self.operation}"
        
        self.span = self.tracer.start_span(span_name)
        self.start_time = time.time()
        
        # Set standard attributes
        self.span.set_attribute("tool.name", self.tool_name)
        if self.operation:
            self.span.set_attribute("tool.operation", self.operation)
        
        # Set custom attributes
        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)
        
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span and self.start_time:
            import time
            
            # Calculate and set latency
            latency_ms = (time.time() - self.start_time) * 1000
            self.span.set_attribute("latency_ms", latency_ms)
            
            # Set status based on exception
            if exc_type is None:
                self.span.set_attribute("status", "success")
            else:
                self.span.set_attribute("status", "error")
                self.span.set_attribute("error.type", exc_type.__name__)
                self.span.set_attribute("error.message", str(exc_val))
            
            self.span.end()

class MetricsCollector:
    """
    Collector for custom metrics with standard tool metrics
    """
    
    def __init__(self, meter_name: str):
        self.meter = get_meter(meter_name)
        
        # Create standard counters and histograms
        self.tool_requests_counter = self.meter.create_counter(
            name="tool_requests_total",
            description="Total number of tool requests",
            unit="1"
        )
        
        self.tool_duration_histogram = self.meter.create_histogram(
            name="tool_duration_ms",
            description="Tool execution duration in milliseconds",
            unit="ms"
        )
        
        self.tool_errors_counter = self.meter.create_counter(
            name="tool_errors_total",
            description="Total number of tool errors",
            unit="1"
        )
        
        self.tool_retries_counter = self.meter.create_counter(
            name="tool_retries_total",
            description="Total number of tool retries",
            unit="1"
        )
    
    def record_tool_request(self, tool_name: str, status: str = "success"):
        """Record a tool request"""
        self.tool_requests_counter.add(1, {
            "tool_name": tool_name,
            "status": status
        })
    
    def record_tool_duration(self, tool_name: str, duration_ms: float, status: str = "success"):
        """Record tool execution duration"""
        self.tool_duration_histogram.record(duration_ms, {
            "tool_name": tool_name,
            "status": status
        })
    
    def record_tool_error(self, tool_name: str, error_type: str):
        """Record a tool error"""
        self.tool_errors_counter.add(1, {
            "tool_name": tool_name,
            "error_type": error_type
        })
    
    def record_tool_retry(self, tool_name: str, attempt: int):
        """Record a tool retry"""
        self.tool_retries_counter.add(1, {
            "tool_name": tool_name,
            "attempt": str(attempt)
        })

# Global metrics collector
_global_metrics: Optional[MetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = MetricsCollector("ai_agent_tools")
    return _global_metrics

def create_tool_span(tracer: trace.Tracer, tool_name: str, **attributes) -> ToolSpan:
    """
    Create a tool execution span with standard attributes
    
    Args:
        tracer: Tracer instance
        tool_name: Name of the tool
        **attributes: Additional span attributes
        
    Returns:
        ToolSpan context manager
    """
    return ToolSpan(tracer, tool_name, **attributes)

def shutdown_observability():
    """Shutdown observability providers"""
    global _tracer_provider, _meter_provider, _is_initialized
    
    if _tracer_provider:
        _tracer_provider.shutdown()
    
    if _meter_provider:
        _meter_provider.shutdown()
    
    _is_initialized = False
    logger.info("Observability shutdown complete")

# Environment-based configuration
def get_observability_config() -> Dict[str, Any]:
    """Get observability configuration from environment variables"""
    return {
        "service_name": os.getenv("OTEL_SERVICE_NAME", "ai-agent-training-api"),
        "service_version": os.getenv("OTEL_SERVICE_VERSION", "1.0.0"),
        "jaeger_endpoint": os.getenv("JAEGER_ENDPOINT"),
        "enable_console_export": os.getenv("OTEL_CONSOLE_EXPORT", "true").lower() == "true",
    }
