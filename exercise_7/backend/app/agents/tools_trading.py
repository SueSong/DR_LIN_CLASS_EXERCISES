import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional, List

import httpx

from app.config import settings
from .tools import ToolResult, BaseTool


async def _post_json(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = settings.trading_agent_url.rstrip("/") + path
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


class TradingQuoteTool(BaseTool):
    name = "TradingQuoteTool"

    async def invoke(self, query: str, context: Dict[str, Any]) -> ToolResult:
        overrides = (context.get("overrides") or {}) if isinstance(context, dict) else {}
        symbols: List[str] = overrides.get("symbols") or context.get("symbols") or []
        if not symbols:
            return ToolResult(ok=False, error="no_symbols")
        payload = {
            "symbols": symbols,
            "include_details": True,
            "user_id": overrides.get("user_id", "default_trader"),
        }
        data = await _post_json("/quotes", payload)
        return ToolResult(ok=True, value=data)


class TradingRecommendTool(BaseTool):
    name = "TradingRecommendTool"

    async def invoke(self, query: str, context: Dict[str, Any]) -> ToolResult:
        overrides = (context.get("overrides") or {}) if isinstance(context, dict) else {}
        market_data = {"quotes": (context.get("trading_quotes") or {}).get("quotes")}
        portfolio_data = overrides.get("portfolio_data") or {}
        payload = {
            "market_data": market_data,
            "portfolio_data": portfolio_data,
            "cash_balance": overrides.get("cash_balance", 10000.0),
            "risk_tolerance": overrides.get("risk_tolerance", "moderate"),
            "user_id": overrides.get("user_id", "default_trader"),
        }
        data = await _post_json("/recommendations", payload)
        return ToolResult(ok=True, value=data)


class TradingTradeTool(BaseTool):
    name = "TradingTradeTool"

    async def invoke(self, query: str, context: Dict[str, Any]) -> ToolResult:
        overrides = (context.get("overrides") or {}) if isinstance(context, dict) else {}
        symbol = overrides.get("symbol") or (context.get("symbols") or [None])[0]
        if not symbol:
            return ToolResult(ok=False, error="no_symbol")
        action = (overrides.get("action") or "BUY").upper()
        amount = float(overrides.get("amount", 1000))
        payload = {
            "symbol": symbol,
            "action": action,
            "amount": amount,
            "user_id": overrides.get("user_id", "default_trader"),
        }
        data = await _post_json("/trade", payload)
        return ToolResult(ok=True, value=data)


