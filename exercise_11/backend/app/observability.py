"""
OpenTelemetry Observability Setup
Provides tracing spans for retrieval, guard, and model operations.
"""

import os
import logging
from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Configure logger with handler if not already configured
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Global tracer provider
_tracer_provider: Optional[TracerProvider] = None
_is_initialized = False


def setup_observability(
    service_name: str = "child-growth-assistant",
    service_version: str = "1.0.0",
    jaeger_endpoint: Optional[str] = None,
    enable_console_export: bool = True
) -> None:
    """
    Initialize OpenTelemetry observability stack.
    
    Args:
        service_name: Name of the service
        service_version: Version of the service
        jaeger_endpoint: Jaeger collector endpoint (optional, default: localhost:4317)
        enable_console_export: Whether to enable console exporters for debugging
    """
    global _tracer_provider, _is_initialized
    
    if _is_initialized:
        logger.info("Observability already initialized")
        return
    
    logger.info("Initializing OpenTelemetry observability...")
    
    # Create resource with service information
    resource = Resource.create({
        "service.name": service_name,
        "service.version": service_version,
        "service.instance.id": os.getenv("HOSTNAME", "localhost"),
        "deployment.environment": os.getenv("ENVIRONMENT", "development"),
    })
    
    # Setup tracing
    _tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(_tracer_provider)
    
    # Add console exporter for development (shows spans in console)
    if enable_console_export:
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        _tracer_provider.add_span_processor(console_processor)
        logger.info("Console span exporter enabled")
    
    # Add OTLP exporter for Jaeger (if endpoint provided or default)
    otlp_endpoint = jaeger_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    try:
        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=True  # Use insecure for local development
        )
        otlp_processor = BatchSpanProcessor(otlp_exporter)
        _tracer_provider.add_span_processor(otlp_processor)
        logger.info(f"OTLP exporter configured: {otlp_endpoint}")
    except Exception as e:
        logger.warning(f"Failed to setup OTLP exporter (Jaeger may not be running): {e}")
    
    # Setup automatic FastAPI instrumentation
    try:
        FastAPIInstrumentor().instrument()
        logger.info("FastAPI instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to setup FastAPI instrumentation: {e}")
    
    _is_initialized = True
    logger.info("OpenTelemetry observability initialized successfully")


def get_tracer(name: str = "child-growth-assistant"):
    """Get a tracer for creating spans"""
    return trace.get_tracer(name)


def create_span(span_name: str, attributes: Optional[dict] = None):
    """
    Context manager for creating a span.
    
    Usage:
        with create_span("retrieval.retrieve", {"query": query}):
            # do work
            pass
    """
    tracer = get_tracer()
    span = tracer.start_as_current_span(span_name)
    
    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)
    
    return span

