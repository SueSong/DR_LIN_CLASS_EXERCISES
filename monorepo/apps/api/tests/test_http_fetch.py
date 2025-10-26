"""
Tests for HTTP fetch tool with timeout, retry, rate limiting, and UA identification
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from hypothesis import given, strategies as st, settings

from tools.http_fetch import HTTPFetcher, RateLimiter

class TestRateLimiter:
    """Test rate limiter functionality"""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_allows_requests_within_limit(self):
        """Test that rate limiter allows requests within the limit"""
        limiter = RateLimiter(requests_per_second=10.0)
        
        # Should allow 5 requests quickly
        for _ in range(5):
            await limiter.acquire()
        
        # All requests should complete quickly
        assert len(limiter._requests) == 5
    
    @pytest.mark.asyncio
    async def test_rate_limiter_delays_excess_requests(self):
        """Test that rate limiter delays requests exceeding the limit"""
        limiter = RateLimiter(requests_per_second=2.0)  # Very low limit
        
        start_time = time.time()
        
        # Make 3 requests (should delay the 3rd)
        for _ in range(3):
            await limiter.acquire()
        
        elapsed = time.time() - start_time
        
        # Should have taken some time due to rate limiting
        assert elapsed > 0.4  # At least 400ms delay

class TestHTTPFetcher:
    """Test HTTP fetcher functionality"""
    
    @pytest.fixture
    def http_fetcher(self):
        """Create HTTP fetcher instance for testing"""
        return HTTPFetcher(
            timeout=5.0,
            max_retries=2,
            rate_limit_rps=100.0,  # High limit for tests
            user_agent="Test-Agent/1.0"
        )
    
    @pytest.mark.asyncio
    async def test_successful_get_request(self, http_fetcher):
        """Test successful GET request"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"test": "data"}
        mock_response.url = "https://api.example.com/test"
        
        with patch.object(http_fetcher.client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await http_fetcher.fetch("https://api.example.com/test")
            
            assert result["success"] is True
            assert result["status_code"] == 200
            assert result["data"] == {"test": "data"}
            assert "latency_ms" in result
            
            # Verify request was made with correct parameters
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert kwargs["method"] == "GET"
            assert kwargs["url"] == "https://api.example.com/test"
            assert kwargs["headers"]["User-Agent"] == "Test-Agent/1.0"
    
    @pytest.mark.asyncio
    async def test_post_request_with_data(self, http_fetcher):
        """Test POST request with JSON data"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"id": 123, "created": True}
        mock_response.url = "https://api.example.com/create"
        
        with patch.object(http_fetcher.client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            test_data = {"name": "Test Item", "value": 42}
            result = await http_fetcher.fetch(
                "https://api.example.com/create",
                method="POST",
                data=test_data
            )
            
            assert result["success"] is True
            assert result["status_code"] == 201
            assert result["data"] == {"id": 123, "created": True}
            
            # Verify POST data was sent
            args, kwargs = mock_request.call_args
            assert kwargs["method"] == "POST"
            assert kwargs["json"] == test_data
    
    @pytest.mark.asyncio
    async def test_retry_on_server_error(self, http_fetcher):
        """Test retry logic on server errors"""
        # First two calls return 500, third succeeds
        responses = [
            MagicMock(status_code=500, headers={}, text="Server Error"),
            MagicMock(status_code=500, headers={}, text="Server Error"),
            MagicMock(status_code=200, headers={"content-type": "text/plain"}, text="Success", url="https://api.example.com/test")
        ]
        
        with patch.object(http_fetcher.client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = responses
            
            result = await http_fetcher.fetch("https://api.example.com/test")
            
            assert result["success"] is True
            assert result["status_code"] == 200
            assert result["attempt"] == 3  # Third attempt succeeded
            assert mock_request.call_count == 3
    
    @pytest.mark.asyncio
    async def test_max_retries_exhausted(self, http_fetcher):
        """Test behavior when max retries are exhausted"""
        # All calls return 500
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.headers = {}
        mock_response.text = "Server Error"
        
        with patch.object(http_fetcher.client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await http_fetcher.fetch("https://api.example.com/test")
            
            assert result["success"] is False
            assert "error" in result
            assert mock_request.call_count == http_fetcher.max_retries + 1
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, http_fetcher):
        """Test timeout handling with retry"""
        with patch.object(http_fetcher.client, 'request', new_callable=AsyncMock) as mock_request:
            # First call times out, second succeeds
            mock_request.side_effect = [
                httpx.TimeoutException("Request timed out"),
                MagicMock(status_code=200, headers={}, text="Success", url="https://api.example.com/test")
            ]
            
            result = await http_fetcher.fetch("https://api.example.com/test")
            
            assert result["success"] is True
            assert result["attempt"] == 2
            assert mock_request.call_count == 2
    
    @pytest.mark.asyncio
    async def test_invalid_url_rejection(self, http_fetcher):
        """Test rejection of invalid URLs"""
        with pytest.raises(ValueError, match="Invalid URL"):
            await http_fetcher.fetch("not-a-url")
    
    @pytest.mark.asyncio
    async def test_private_url_rejection(self, http_fetcher):
        """Test rejection of private/local URLs"""
        private_urls = [
            "http://localhost:8080/test",
            "http://127.0.0.1/test",
            "http://192.168.1.1/test",
            "http://10.0.0.1/test",
        ]
        
        for url in private_urls:
            with pytest.raises(ValueError, match="Access to private/local URLs is not allowed"):
                await http_fetcher.fetch(url)
    
    @pytest.mark.asyncio
    async def test_custom_headers(self, http_fetcher):
        """Test custom headers are included"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "Success"
        mock_response.url = "https://api.example.com/test"
        
        with patch.object(http_fetcher.client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            custom_headers = {"Authorization": "Bearer token123", "X-Custom": "value"}
            await http_fetcher.fetch("https://api.example.com/test", headers=custom_headers)
            
            args, kwargs = mock_request.call_args
            headers = kwargs["headers"]
            assert headers["Authorization"] == "Bearer token123"
            assert headers["X-Custom"] == "value"
            assert headers["User-Agent"] == "Test-Agent/1.0"  # Default UA preserved
    
    @pytest.mark.asyncio
    async def test_query_parameters(self, http_fetcher):
        """Test query parameters are included"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "Success"
        mock_response.url = "https://api.example.com/test"
        
        with patch.object(http_fetcher.client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            params = {"page": "1", "limit": "10", "filter": "active"}
            await http_fetcher.fetch("https://api.example.com/test", params=params)
            
            args, kwargs = mock_request.call_args
            assert kwargs["params"] == params
    
    @pytest.mark.asyncio
    async def test_content_type_handling(self, http_fetcher):
        """Test different content types are handled correctly"""
        # Test JSON response
        json_response = MagicMock()
        json_response.status_code = 200
        json_response.headers = {"content-type": "application/json"}
        json_response.json.return_value = {"key": "value"}
        json_response.url = "https://api.example.com/json"
        
        # Test text response
        text_response = MagicMock()
        text_response.status_code = 200
        text_response.headers = {"content-type": "text/plain"}
        text_response.text = "Plain text content"
        text_response.content = b"Plain text content"
        text_response.url = "https://api.example.com/text"
        
        with patch.object(http_fetcher.client, 'request', new_callable=AsyncMock) as mock_request:
            # Test JSON
            mock_request.return_value = json_response
            result = await http_fetcher.fetch("https://api.example.com/json")
            assert "data" in result
            assert result["data"] == {"key": "value"}
            
            # Test text
            mock_request.return_value = text_response
            result = await http_fetcher.fetch("https://api.example.com/text")
            assert "text" in result
            assert result["text"] == "Plain text content"

class TestHTTPFetcherPropertyBased:
    """Property-based tests using Hypothesis"""
    
    @pytest.fixture
    def http_fetcher(self):
        return HTTPFetcher(timeout=1.0, max_retries=1, rate_limit_rps=1000.0)
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=10, deadline=5000)
    @pytest.mark.asyncio
    async def test_user_agent_is_always_set(self, http_fetcher, user_agent):
        """Property: User-Agent header is always set in requests"""
        http_fetcher.user_agent = user_agent
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "OK"
        mock_response.url = "https://example.com"
        
        with patch.object(http_fetcher.client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            await http_fetcher.fetch("https://example.com")
            
            args, kwargs = mock_request.call_args
            assert "User-Agent" in kwargs["headers"]
            assert kwargs["headers"]["User-Agent"] == user_agent
    
    @given(st.integers(min_value=100, max_value=599))
    @settings(max_examples=10, deadline=5000)
    @pytest.mark.asyncio
    async def test_status_code_handling(self, http_fetcher, status_code):
        """Property: All HTTP status codes are handled appropriately"""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.headers = {}
        mock_response.text = f"Response {status_code}"
        mock_response.url = "https://example.com"
        
        with patch.object(http_fetcher.client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await http_fetcher.fetch("https://example.com")
            
            assert "status_code" in result
            assert result["status_code"] == status_code
            assert "success" in result
            
            # Success should be True for 2xx and 3xx, False for 4xx and 5xx
            if status_code < 400:
                assert result["success"] is True
            else:
                assert result["success"] is False
