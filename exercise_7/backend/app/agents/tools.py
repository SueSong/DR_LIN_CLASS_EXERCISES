import random
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.config import settings


class RateLimitError(Exception):
    def __init__(self, retry_after: float = 0.5):
        super().__init__("429 Too Many Requests")
        self.retry_after = retry_after


class TimeoutErrorTool(Exception):
    pass


@dataclass
class ToolResult:
    ok: bool
    value: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaseTool:
    name: str = "BaseTool"

    async def invoke(self, query: str, context: Dict[str, Any]) -> ToolResult:
        raise NotImplementedError


class SearchTool(BaseTool):
    name = "SearchTool"

    async def invoke(self, query: str, context: Dict[str, Any]) -> ToolResult:
        await asyncio.sleep(0.05)
        results = [
            {"title": "Result A", "score": 0.92},
            {"title": "Result B", "score": 0.88},
            {"title": "Result C", "score": 0.80},
        ]
        return ToolResult(ok=True, value={"candidates": results})


class PriceTool(BaseTool):
    name = "PriceTool"

    async def invoke(self, query: str, context: Dict[str, Any]) -> ToolResult:
        overrides = (context.get("overrides") or {}) if isinstance(context, dict) else {}
        inject_timeout_ms = int(overrides.get("inject_timeout_ms", settings.inject_timeout_ms) or 0)
        fail_rate = float(overrides.get("fail_rate", settings.fail_rate))

        # Inject timeout
        if inject_timeout_ms > 0 and random.random() < 0.05:
            await asyncio.sleep(inject_timeout_ms / 1000.0)
            raise TimeoutErrorTool("simulated timeout")

        # Simulate rate limit
        if random.random() < fail_rate:
            raise RateLimitError(retry_after=random.uniform(0.2, 1.0))

        await asyncio.sleep(0.08)
        price = round(random.uniform(10, 100), 2)
        return ToolResult(ok=True, value={"price": price, "currency": "USD"})


class CacheTool(BaseTool):
    name = "CacheTool"

    async def invoke(self, query: str, context: Dict[str, Any]) -> ToolResult:
        overrides = (context.get("overrides") or {}) if isinstance(context, dict) else {}
        cache_hit_rate = float(overrides.get("cache_hit_rate", settings.cache_hit_rate))
        await asyncio.sleep(0.01)
        # Simulate cache hit rate
        if random.random() < cache_hit_rate:
            return ToolResult(ok=True, value={"price": 42.0, "currency": "USD", "cache": True})
        return ToolResult(ok=False, error="cache_miss")


