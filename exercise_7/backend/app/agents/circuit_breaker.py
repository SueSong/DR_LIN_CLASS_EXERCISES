import time
from dataclasses import dataclass, field
from typing import Dict, Deque
from collections import deque

from app.config import settings


@dataclass
class CircuitState:
    failures: Deque[float] = field(default_factory=deque)
    opened_at: float | None = None


class CircuitBreaker:
    def __init__(self) -> None:
        self._per_tool: Dict[str, CircuitState] = {}

    def record_failure(self, tool_name: str) -> None:
        state = self._per_tool.setdefault(tool_name, CircuitState())
        now = time.time()
        state.failures.append(now)
        self._trim(state, now)
        if len(state.failures) >= settings.circuit_failures_threshold and not state.opened_at:
            state.opened_at = now

    def record_success(self, tool_name: str) -> None:
        state = self._per_tool.setdefault(tool_name, CircuitState())
        now = time.time()
        self._trim(state, now)
        if state.opened_at and (now - state.opened_at) >= settings.circuit_cooldown_seconds:
            # Close after cooldown if we observe a success
            state.opened_at = None
            state.failures.clear()

    def is_open(self, tool_name: str) -> bool:
        state = self._per_tool.setdefault(tool_name, CircuitState())
        now = time.time()
        self._trim(state, now)
        if state.opened_at is None:
            return False
        # circuit remains open during cooldown window
        return (now - state.opened_at) < settings.circuit_cooldown_seconds

    def _trim(self, state: CircuitState, now: float) -> None:
        window = settings.circuit_window_seconds
        while state.failures and (now - state.failures[0]) > window:
            state.failures.popleft()


circuit_breaker = CircuitBreaker()


