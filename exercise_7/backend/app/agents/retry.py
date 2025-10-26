import asyncio
import random
from typing import Callable, Awaitable

from app.config import settings
from .tools import RateLimitError, TimeoutErrorTool


async def execute_with_policies(fn: Callable[[], Awaitable]):
    """Retry policy: ≤2 attempts + jitter on 429/timeouts."""
    max_retries = max(0, settings.max_retries)
    attempt = 0
    while True:
        try:
            return await fn()
        except RateLimitError as e:
            if attempt >= max_retries:
                raise
            attempt += 1
            await asyncio.sleep(_jitter_from_retry_after(e.retry_after))
        except TimeoutErrorTool:
            if attempt >= max_retries:
                raise
            attempt += 1
            await asyncio.sleep(_jitter_backoff(attempt))


def _jitter_from_retry_after(retry_after: float) -> float:
    return max(0.05, retry_after) * (1.0 + random.uniform(0.0, 0.2))


def _jitter_backoff(attempt: int) -> float:
    base = 0.2 * (2 ** (attempt - 1))
    return base * (1.0 + random.uniform(0.0, 0.25))


