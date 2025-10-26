"""
Retry Logic with Exponential Backoff and Jitter
Implements robust retry mechanisms for tool execution
"""

import asyncio
import random
import time
import logging
from typing import Any, Callable, Optional, Union, Dict, List
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import inspect

logger = logging.getLogger(__name__)

class RetryStrategy(str, Enum):
    """Retry strategy enumeration"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    FIBONACCI_BACKOFF = "fibonacci_backoff"

class RetryCondition(str, Enum):
    """Retry condition enumeration"""
    ON_EXCEPTION = "on_exception"
    ON_RESULT = "on_result"
    ON_BOTH = "on_both"

@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay: float = 1.0  # Base delay in seconds
    max_delay: float = 60.0  # Maximum delay in seconds
    backoff_multiplier: float = 2.0  # Multiplier for exponential backoff
    jitter: bool = True  # Add random jitter to delays
    jitter_range: float = 0.1  # Jitter range (0.0 to 1.0)
    
    # Exception handling
    retryable_exceptions: List[type] = field(default_factory=lambda: [Exception])
    non_retryable_exceptions: List[type] = field(default_factory=list)
    
    # Result-based retry
    retry_on_result: Optional[Callable[[Any], bool]] = None
    
    # Callbacks
    on_retry: Optional[Callable[[int, Exception], None]] = None
    on_failure: Optional[Callable[[int, Exception], None]] = None
    on_success: Optional[Callable[[int, Any], None]] = None

class RetryState:
    """State tracking for retry operations"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.attempt = 0
        self.total_delay = 0.0
        self.start_time = time.time()
        self.last_exception: Optional[Exception] = None
        self.delays: List[float] = []
    
    def should_retry(self, exception: Optional[Exception] = None, result: Any = None) -> bool:
        """Determine if operation should be retried"""
        
        # Check attempt limit
        if self.attempt >= self.config.max_attempts:
            return False
        
        # Check exception-based retry conditions
        if exception:
            # Check non-retryable exceptions first
            if any(isinstance(exception, exc_type) for exc_type in self.config.non_retryable_exceptions):
                return False
            
            # Check retryable exceptions
            if not any(isinstance(exception, exc_type) for exc_type in self.config.retryable_exceptions):
                return False
        
        # Check result-based retry conditions
        if result is not None and self.config.retry_on_result:
            return self.config.retry_on_result(result)
        
        return True
    
    def get_next_delay(self) -> float:
        """Calculate next delay based on strategy"""
        
        if self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
            
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * (self.attempt + 1)
            
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** self.attempt)
            
        elif self.config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            delay = self.config.base_delay * self._fibonacci(self.attempt + 1)
            
        else:
            delay = self.config.base_delay
        
        # Apply maximum delay limit
        delay = min(delay, self.config.max_delay)
        
        # Add jitter if enabled
        if self.config.jitter:
            jitter_amount = delay * self.config.jitter_range
            jitter = random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay + jitter)
        
        return delay
    
    def _fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    def record_attempt(self, delay: float):
        """Record attempt and delay"""
        self.attempt += 1
        self.delays.append(delay)
        self.total_delay += delay
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retry statistics"""
        return {
            "total_attempts": self.attempt,
            "total_delay": self.total_delay,
            "average_delay": self.total_delay / len(self.delays) if self.delays else 0,
            "delays": self.delays,
            "duration": time.time() - self.start_time,
            "last_exception": str(self.last_exception) if self.last_exception else None
        }

async def exponential_backoff_with_jitter(
    func: Callable,
    config: Optional[RetryConfig] = None,
    *args,
    **kwargs
) -> Any:
    """
    Execute function with exponential backoff and jitter
    
    Args:
        func: Function to execute
        config: Retry configuration
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries failed
    """
    
    if config is None:
        config = RetryConfig()
    
    state = RetryState(config)
    
    while True:
        try:
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Check if result indicates retry needed
            if config.retry_on_result and config.retry_on_result(result):
                if state.should_retry(result=result):
                    delay = state.get_next_delay()
                    state.record_attempt(delay)
                    
                    logger.info(f"Retrying due to result condition, attempt {state.attempt}, delay {delay:.2f}s")
                    
                    if config.on_retry:
                        config.on_retry(state.attempt, None)
                    
                    await asyncio.sleep(delay)
                    continue
                else:
                    # Max attempts reached
                    if config.on_failure:
                        config.on_failure(state.attempt, None)
                    return result
            
            # Success
            if config.on_success:
                config.on_success(state.attempt, result)
            
            return result
            
        except Exception as e:
            state.last_exception = e
            
            if state.should_retry(exception=e):
                delay = state.get_next_delay()
                state.record_attempt(delay)
                
                logger.warning(f"Attempt {state.attempt} failed: {e}, retrying in {delay:.2f}s")
                
                if config.on_retry:
                    config.on_retry(state.attempt, e)
                
                await asyncio.sleep(delay)
                continue
            else:
                # No more retries
                if config.on_failure:
                    config.on_failure(state.attempt, e)
                
                logger.error(f"All {state.attempt} attempts failed, giving up")
                raise e

def retry_with_config(config: RetryConfig):
    """
    Decorator for adding retry logic to functions
    
    Usage:
        @retry_with_config(RetryConfig(max_attempts=5, base_delay=2.0))
        async def my_function():
            # Function implementation
            pass
    """
    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await exponential_backoff_with_jitter(func, config, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return asyncio.run(exponential_backoff_with_jitter(func, config, *args, **kwargs))
            return sync_wrapper
    
    return decorator

def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    jitter: bool = True,
    retryable_exceptions: Optional[List[type]] = None,
    non_retryable_exceptions: Optional[List[type]] = None
):
    """
    Simple retry decorator with common parameters
    
    Usage:
        @retry(max_attempts=5, base_delay=2.0, strategy=RetryStrategy.EXPONENTIAL_BACKOFF)
        async def my_function():
            # Function implementation
            pass
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        strategy=strategy,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions or [Exception],
        non_retryable_exceptions=non_retryable_exceptions or []
    )
    
    return retry_with_config(config)

# Predefined retry configurations for common scenarios
class CommonRetryConfigs:
    """Common retry configurations"""
    
    @staticmethod
    def network_request() -> RetryConfig:
        """Configuration for network requests"""
        return RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=30.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            retryable_exceptions=[ConnectionError, TimeoutError],
            non_retryable_exceptions=[ValueError, TypeError]
        )
    
    @staticmethod
    def database_operation() -> RetryConfig:
        """Configuration for database operations"""
        return RetryConfig(
            max_attempts=5,
            base_delay=0.5,
            max_delay=10.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            retryable_exceptions=[ConnectionError, TimeoutError],
            non_retryable_exceptions=[ValueError, TypeError]
        )
    
    @staticmethod
    def file_operation() -> RetryConfig:
        """Configuration for file operations"""
        return RetryConfig(
            max_attempts=3,
            base_delay=0.1,
            max_delay=5.0,
            strategy=RetryStrategy.LINEAR_BACKOFF,
            jitter=False,
            retryable_exceptions=[OSError, IOError],
            non_retryable_exceptions=[PermissionError, FileNotFoundError]
        )
    
    @staticmethod
    def api_call() -> RetryConfig:
        """Configuration for API calls"""
        return RetryConfig(
            max_attempts=4,
            base_delay=2.0,
            max_delay=60.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            backoff_multiplier=2.5,
            retryable_exceptions=[ConnectionError, TimeoutError],
            non_retryable_exceptions=[ValueError, TypeError, PermissionError]
        )

# Utility functions for retry logic
def create_result_retry_condition(expected_values: List[Any]) -> Callable[[Any], bool]:
    """Create a retry condition based on expected result values"""
    def condition(result: Any) -> bool:
        return result not in expected_values
    return condition

def create_status_code_retry_condition(retryable_codes: List[int]) -> Callable[[Dict[str, Any]], bool]:
    """Create a retry condition based on HTTP status codes"""
    def condition(result: Dict[str, Any]) -> bool:
        status_code = result.get('status_code')
        return status_code in retryable_codes
    return condition

class RetryMetrics:
    """Metrics collection for retry operations"""
    
    def __init__(self):
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0
        self.total_attempts = 0
        self.total_delay = 0.0
        self.retry_counts = {}  # attempt_count -> frequency
    
    def record_operation(self, state: RetryState, success: bool):
        """Record operation metrics"""
        self.total_operations += 1
        self.total_attempts += state.attempt
        self.total_delay += state.total_delay
        
        if success:
            self.successful_operations += 1
        else:
            self.failed_operations += 1
        
        # Track retry count distribution
        retry_count = state.attempt - 1  # First attempt is not a retry
        self.retry_counts[retry_count] = self.retry_counts.get(retry_count, 0) + 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get retry statistics"""
        return {
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": self.successful_operations / self.total_operations if self.total_operations > 0 else 0,
            "average_attempts": self.total_attempts / self.total_operations if self.total_operations > 0 else 0,
            "average_delay": self.total_delay / self.total_operations if self.total_operations > 0 else 0,
            "retry_distribution": self.retry_counts
        }

# Global metrics instance
_global_metrics = RetryMetrics()

def get_retry_metrics() -> RetryMetrics:
    """Get global retry metrics instance"""
    return _global_metrics
