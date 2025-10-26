"""
Exercise 6: Logging Utilities
Provides centralized logging configuration for the application
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import os

def setup_app_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup application-wide logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        format_string: Custom format string for log messages
    
    Returns:
        Configured logger instance
    """
    
    # Default format string
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(filename)s:%(lineno)d] - %(message)s"
        )
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Create application logger
    app_logger = logging.getLogger("app")
    
    # Log initialization
    app_logger.info(f"✅ Logging initialized - Level: {level}")
    if log_file:
        app_logger.info(f"📝 Log file: {log_file}")
    
    return app_logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def log_request(logger: logging.Logger, method: str, path: str, status_code: int, duration_ms: float):
    """
    Log HTTP request information
    
    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
    """
    level = logging.INFO
    if status_code >= 400:
        level = logging.WARNING
    if status_code >= 500:
        level = logging.ERROR
    
    logger.log(
        level,
        f"{method} {path} - {status_code} - {duration_ms:.2f}ms"
    )

def log_error(logger: logging.Logger, error: Exception, context: Optional[str] = None):
    """
    Log error information with context
    
    Args:
        logger: Logger instance
        error: Exception instance
        context: Optional context information
    """
    error_msg = f"❌ Error: {str(error)}"
    if context:
        error_msg = f"❌ Error in {context}: {str(error)}"
    
    logger.error(error_msg, exc_info=True)

def log_performance(logger: logging.Logger, operation: str, duration_ms: float, details: Optional[dict] = None):
    """
    Log performance metrics
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration_ms: Duration in milliseconds
        details: Optional additional details
    """
    msg = f"⏱️ {operation} completed in {duration_ms:.2f}ms"
    
    if details:
        detail_str = ", ".join([f"{k}={v}" for k, v in details.items()])
        msg += f" ({detail_str})"
    
    logger.info(msg)

class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return logging.getLogger(self.__class__.__name__)
    
    def log_info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def log_error(self, message: str, error: Optional[Exception] = None):
        """Log error message"""
        if error:
            self.logger.error(f"{message}: {str(error)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def log_debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
