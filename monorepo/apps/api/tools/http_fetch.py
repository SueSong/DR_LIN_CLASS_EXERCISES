"""
HTTP Fetch Tool with timeout, retry, rate limiting, and UA identification
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from urllib.parse import urlparse
import httpx
import logging
from observability.otel import get_tracer

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)

@dataclass
class RateLimiter:
    """Simple rate limiter implementation"""
    requests_per_second: float = 10.0
    _requests: List[float] = field(default_factory=list)
    
    async def acquire(self):
        """Acquire permission to make a request"""
        now = time.time()
        # Remove old requests outside the window
        self._requests = [req_time for req_time in self._requests if now - req_time < 1.0]
        
        if len(self._requests) >= self.requests_per_second:
            sleep_time = 1.0 - (now - self._requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self._requests.append(now)

class HTTPFetcher:
    """HTTP fetcher with advanced features"""
    
    def __init__(self, 
                 timeout: float = 30.0,
                 max_retries: int = 3,
                 rate_limit_rps: float = 10.0,
                 user_agent: str = "AI-Agent-Training-Class/1.0"):
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent
        self.rate_limiter = RateLimiter(rate_limit_rps)
        
        # Create HTTP client with default settings
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={"User-Agent": user_agent},
            follow_redirects=True
        )
    
    async def fetch(self, 
                   url: str,
                   method: str = "GET",
                   headers: Optional[Dict[str, str]] = None,
                   data: Optional[Dict[str, Any]] = None,
                   params: Optional[Dict[str, str]] = None,
                   **kwargs) -> Dict[str, Any]:
        """
        Fetch URL with retry logic and rate limiting
        
        Args:
            url: Target URL
            method: HTTP method (GET, POST, etc.)
            headers: Additional headers
            data: Request body data
            params: Query parameters
            **kwargs: Additional httpx client options
            
        Returns:
            Dict containing response data and metadata
        """
        
        with tracer.start_as_current_span("http_fetch") as span:
            span.set_attribute("http.url", url)
            span.set_attribute("http.method", method)
            span.set_attribute("tool.name", "http_fetch")
            
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError(f"Invalid URL: {url}")
            
            # Security check - block local/private IPs
            if self._is_private_url(parsed_url):
                raise ValueError(f"Access to private/local URLs is not allowed: {url}")
            
            # Prepare request
            request_headers = {"User-Agent": self.user_agent}
            if headers:
                request_headers.update(headers)
            
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    # Apply rate limiting
                    await self.rate_limiter.acquire()
                    
                    span.set_attribute("retries", attempt)
                    start_time = time.time()
                    
                    # Make the request
                    response = await self.client.request(
                        method=method,
                        url=url,
                        headers=request_headers,
                        json=data if data else None,
                        params=params,
                        **kwargs
                    )
                    
                    latency_ms = (time.time() - start_time) * 1000
                    span.set_attribute("latency_ms", latency_ms)
                    span.set_attribute("http.status_code", response.status_code)
                    
                    # Handle response
                    result = {
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "url": str(response.url),
                        "latency_ms": latency_ms,
                        "attempt": attempt + 1,
                        "success": True
                    }
                    
                    # Try to parse response content
                    try:
                        content_type = response.headers.get("content-type", "").lower()
                        if "application/json" in content_type:
                            result["data"] = response.json()
                        else:
                            result["text"] = response.text
                            result["content_length"] = len(response.content)
                    except Exception as e:
                        logger.warning(f"Failed to parse response content: {e}")
                        result["text"] = response.text
                    
                    # Check if response indicates success
                    if response.status_code < 400:
                        span.set_attribute("status", "success")
                        return result
                    else:
                        # HTTP error - might be retryable
                        if response.status_code >= 500 and attempt < self.max_retries:
                            logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}, retrying...")
                            await self._wait_for_retry(attempt)
                            continue
                        else:
                            result["success"] = False
                            result["error"] = f"HTTP {response.status_code}"
                            span.set_attribute("status", "error")
                            return result
                            
                except httpx.TimeoutException as e:
                    last_exception = e
                    logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                    if attempt < self.max_retries:
                        await self._wait_for_retry(attempt)
                        continue
                        
                except httpx.RequestError as e:
                    last_exception = e
                    logger.warning(f"Request error on attempt {attempt + 1}: {e}")
                    if attempt < self.max_retries:
                        await self._wait_for_retry(attempt)
                        continue
                        
                except Exception as e:
                    last_exception = e
                    logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                    break
            
            # All retries exhausted
            span.set_attribute("status", "error")
            span.set_attribute("retries", self.max_retries)
            
            return {
                "success": False,
                "error": f"Failed after {self.max_retries + 1} attempts: {str(last_exception)}",
                "attempts": self.max_retries + 1,
                "last_exception": str(last_exception)
            }
    
    def _is_private_url(self, parsed_url) -> bool:
        """Check if URL points to private/local network"""
        hostname = parsed_url.hostname
        if not hostname:
            return True
            
        # Block localhost and private IP ranges
        private_patterns = [
            "localhost", "127.", "10.", "172.16.", "172.17.", "172.18.", 
            "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
            "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.",
            "172.31.", "192.168.", "169.254."
        ]
        
        return any(hostname.startswith(pattern) for pattern in private_patterns)
    
    async def _wait_for_retry(self, attempt: int):
        """Exponential backoff with jitter"""
        import random
        base_delay = 2 ** attempt
        jitter = random.uniform(0.1, 0.5)
        delay = base_delay + jitter
        await asyncio.sleep(min(delay, 30))  # Cap at 30 seconds
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

# Global instance for the API
_global_fetcher = None

def get_http_fetcher() -> HTTPFetcher:
    """Get global HTTP fetcher instance"""
    global _global_fetcher
    if _global_fetcher is None:
        _global_fetcher = HTTPFetcher()
    return _global_fetcher
