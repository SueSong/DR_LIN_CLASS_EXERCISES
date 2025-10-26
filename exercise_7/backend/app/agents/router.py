from typing import Literal, Tuple, List
import re


def route(query: str, node: Literal["search", "price"]) -> str:
    """Simple router: if query contains 'price' route to PriceTool, else SearchTool.
    For node sequencing we still respect the plan node type.
    """
    q = (query or "").lower()
    if node == "search":
        return "SearchTool"
    if node == "price":
        if "price" in q:
            return "PriceTool"
        return "SearchTool"
    return "SearchTool"


TICKER_RE = re.compile(r"\b[A-Z]{1,5}\b")
COMMON_WORDS = {"THE","AND","FOR","WITH","THIS","FROM","WILL","HAVE","ARE"}


def detect_stock_intent(query: str) -> Tuple[str, List[str], str | None]:
    q = (query or "").strip()
    ql = q.lower()
    tickers = [t for t in TICKER_RE.findall(q) if t not in COMMON_WORDS]
    if any(w in ql for w in ["buy","sell"]) and tickers:
        return ("trade", tickers, "BUY" if "buy" in ql else "SELL")
    if any(w in ql for w in ["price","quote","quotes"]) and tickers:
        return ("quote", tickers, None)
    return ("none", [], None)



