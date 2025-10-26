"""
Exercise 3: Add Reliability (Retry/Timeout)
Comprehensive reliability layer for trading agent tools
"""

import asyncio
import random
import time
import logging
from typing import Any, Callable, Optional, Union, Dict, List, Type
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

class CircuitBreakerState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting calls
    HALF_OPEN = "half_open"  # Testing if service recovered

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
    retryable_exceptions: List[Type[Exception]] = field(default_factory=lambda: [Exception])
    non_retryable_exceptions: List[Type[Exception]] = field(default_factory=list)
    
    # Result-based retry
    retry_on_result: Optional[Callable[[Any], bool]] = None
    
    # Timeout configuration
    timeout_seconds: Optional[float] = None
    
    # Callbacks
    on_retry: Optional[Callable[[int, Exception], None]] = None
    on_failure: Optional[Callable[[int, Exception], None]] = None
    on_success: Optional[Callable[[int, Any], None]] = None

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Number of failures to open circuit
    recovery_timeout: float = 60.0  # Time to wait before trying again
    success_threshold: int = 3  # Successes needed to close circuit
    timeout_seconds: float = 30.0  # Request timeout

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

class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self.next_attempt_time = 0.0
    
    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        current_time = time.time()
        
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        elif self.state == CircuitBreakerState.OPEN:
            if current_time >= self.next_attempt_time:
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                return True
            return False
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    def record_success(self):
        """Record successful execution"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0
    
    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                self.next_attempt_time = time.time() + self.config.recovery_timeout
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.next_attempt_time = time.time() + self.config.recovery_timeout

async def execute_with_retry(
    func: Callable,
    config: Optional[RetryConfig] = None,
    circuit_breaker: Optional[CircuitBreaker] = None,
    *args,
    **kwargs
) -> Any:
    """
    Execute function with retry logic and optional circuit breaker
    
    Args:
        func: Function to execute
        config: Retry configuration
        circuit_breaker: Optional circuit breaker
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
        # Check circuit breaker
        if circuit_breaker and not circuit_breaker.can_execute():
            raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            # Apply timeout if configured
            if config.timeout_seconds:
                if asyncio.iscoroutinefunction(func):
                    result = await asyncio.wait_for(func(*args, **kwargs), timeout=config.timeout_seconds)
                else:
                    # For sync functions, we can't easily apply timeout without threading
                    result = func(*args, **kwargs)
            else:
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
                    if circuit_breaker:
                        circuit_breaker.record_failure()
                    if config.on_failure:
                        config.on_failure(state.attempt, None)
                    return result
            
            # Success
            if circuit_breaker:
                circuit_breaker.record_success()
            if config.on_success:
                config.on_success(state.attempt, result)
            
            return result
            
        except asyncio.TimeoutError as e:
            state.last_exception = e
            logger.warning(f"Timeout on attempt {state.attempt + 1}")
            
            if state.should_retry(exception=e):
                delay = state.get_next_delay()
                state.record_attempt(delay)
                
                if config.on_retry:
                    config.on_retry(state.attempt, e)
                
                await asyncio.sleep(delay)
                continue
            else:
                if circuit_breaker:
                    circuit_breaker.record_failure()
                if config.on_failure:
                    config.on_failure(state.attempt, e)
                raise e
                
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
                if circuit_breaker:
                    circuit_breaker.record_failure()
                if config.on_failure:
                    config.on_failure(state.attempt, e)
                
                logger.error(f"All {state.attempt} attempts failed, giving up")
                raise e

def with_retry(config: RetryConfig, circuit_breaker: Optional[CircuitBreaker] = None):
    """
    Decorator for adding retry logic to functions
    
    Usage:
        @with_retry(RetryConfig(max_attempts=5, base_delay=2.0))
        async def my_function():
            # Function implementation
            pass
    """
    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await execute_with_retry(func, config, circuit_breaker, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return asyncio.run(execute_with_retry(func, config, circuit_breaker, *args, **kwargs))
            return sync_wrapper
    
    return decorator

# Predefined retry configurations for trading operations
class TradingRetryConfigs:
    """Predefined retry configurations for trading operations"""
    
    @staticmethod
    def market_data_fetch() -> RetryConfig:
        """Configuration for market data fetching"""
        return RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=10.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            timeout_seconds=15.0,
            retryable_exceptions=[ConnectionError, TimeoutError, asyncio.TimeoutError],
            non_retryable_exceptions=[ValueError, TypeError]
        )
    
    @staticmethod
    def trade_execution() -> RetryConfig:
        """Configuration for trade execution (more conservative)"""
        return RetryConfig(
            max_attempts=2,  # Fewer retries for trades
            base_delay=0.5,
            max_delay=5.0,
            strategy=RetryStrategy.FIXED_DELAY,
            jitter=False,  # No jitter for trades
            timeout_seconds=10.0,
            retryable_exceptions=[ConnectionError, TimeoutError],
            non_retryable_exceptions=[ValueError, TypeError, PermissionError]
        )
    
    @staticmethod
    def database_operation() -> RetryConfig:
        """Configuration for database operations"""
        return RetryConfig(
            max_attempts=5,
            base_delay=0.1,
            max_delay=2.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            timeout_seconds=30.0,
            retryable_exceptions=[ConnectionError, TimeoutError],
            non_retryable_exceptions=[ValueError, TypeError]
        )
    
    @staticmethod
    def file_operation() -> RetryConfig:
        """Configuration for file operations"""
        return RetryConfig(
            max_attempts=3,
            base_delay=0.1,
            max_delay=1.0,
            strategy=RetryStrategy.LINEAR_BACKOFF,
            jitter=False,
            timeout_seconds=5.0,
            retryable_exceptions=[OSError, IOError],
            non_retryable_exceptions=[PermissionError, FileNotFoundError]
        )
    
    @staticmethod
    def llm_request() -> RetryConfig:
        """Configuration for LLM API requests"""
        return RetryConfig(
            max_attempts=4,
            base_delay=2.0,
            max_delay=30.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            jitter=True,
            timeout_seconds=60.0,
            backoff_multiplier=2.5,
            retryable_exceptions=[ConnectionError, TimeoutError, asyncio.TimeoutError],
            non_retryable_exceptions=[ValueError, TypeError, PermissionError]
        )

# Circuit breaker configurations
class TradingCircuitBreakers:
    """Predefined circuit breaker configurations"""
    
    @staticmethod
    def market_data_api() -> CircuitBreaker:
        """Circuit breaker for market data API"""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=30.0,
            success_threshold=3,
            timeout_seconds=15.0
        )
        return CircuitBreaker(config)
    
    @staticmethod
    def trading_api() -> CircuitBreaker:
        """Circuit breaker for trading API (more sensitive)"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=60.0,
            success_threshold=2,
            timeout_seconds=10.0
        )
        return CircuitBreaker(config)

# Global circuit breakers for the trading system
_market_data_breaker = TradingCircuitBreakers.market_data_api()
_trading_api_breaker = TradingCircuitBreakers.trading_api()

def get_market_data_breaker() -> CircuitBreaker:
    """Get the global market data circuit breaker"""
    return _market_data_breaker

def get_trading_api_breaker() -> CircuitBreaker:
    """Get the global trading API circuit breaker"""
    return _trading_api_breaker
