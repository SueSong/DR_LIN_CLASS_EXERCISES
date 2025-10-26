import os
import json
import requests
import argparse
import shlex
from typing import Optional, List, Dict, Tuple
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()  # load from current working directory if present
# Also attempt to load .env next to this file so it works regardless of CWD
try:
    load_dotenv(dotenv_path=(Path(__file__).parent / ".env"), override=False)
except Exception:
    pass


def require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {var_name}")
    return value


def fetch_stock_price_from_alpha(symbol: str) -> Optional[Dict]:
    """Fetch latest stock price and change percent from Alpha Vantage."""
    try:
        api_key = require_env("ALPHA_VANTAGE_KEY")
    except RuntimeError:
        return None
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": api_key,
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        quote = data.get("Global Quote") or data.get("GlobalQuote")
        if not quote:
            return None
        price = float(quote["05. price"]) if "05. price" in quote else float(quote["price"])  # type: ignore[index]
        change_percent_str = quote.get("10. change percent") or quote.get("change_percent") or "0%"
        change_percent = float(str(change_percent_str).replace("%", ""))
        return {"symbol": symbol, "price": price, "change_percent": change_percent}
    except Exception:
        return None


def fetch_stock_price_from_yahoo(symbol: str) -> Optional[Dict]:
    """Fetch latest stock price and change percent using yfinance (robust to 429)."""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info  # fast endpoint
        price = getattr(info, "last_price", None) or info.get("last_price") if isinstance(info, dict) else None
        if price is None:
            # fallback to regular info
            price = (ticker.info or {}).get("regularMarketPrice")
        # Compute change percent from recent history if not directly available
        change_pct: Optional[float] = None
        try:
            hist = ticker.history(period="2d")
            if not hist.empty and len(hist["Close"]) >= 2:
                today = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                if prev:
                    change_pct = ((today - prev) / prev) * 100.0
        except Exception:
            pass
        if price is None:
            return None
        return {"symbol": symbol, "price": float(price), "change_percent": float(change_pct or 0.0)}
    except Exception:
        return None


def fetch_stock_price(symbol: str) -> Optional[Dict]:
    """Fetch latest stock price; try Alpha Vantage first, then Yahoo as fallback."""
    data = fetch_stock_price_from_alpha(symbol)
    if data is not None:
        return data
    return fetch_stock_price_from_yahoo(symbol)


def fetch_stock_history(symbol: str, days: int = 7) -> Optional[List[Dict]]:
    """Fetch recent daily closes for a symbol (last N trading days).

    Returns a list of dicts sorted descending by date (most recent first):
    [{"date": "YYYY-MM-DD", "close": 123.45, "change_percent": -0.4}, ...]
    """
    api_key = require_env("ALPHA_VANTAGE_KEY")
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "compact",
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    series = data.get("Time Series (Daily)")
    if not series or not isinstance(series, dict):
        return None

    # Sort dates descending (most recent first)
    dates = sorted(series.keys(), reverse=True)
    records: List[Dict] = []
    prev_close: Optional[float] = None
    for date in dates[: max(days + 1, 2)]:  # fetch a bit extra to compute change
        entry = series.get(date, {})
        if not entry:
            continue
        close_str = entry.get("4. close") or entry.get("5. adjusted close")
        if not close_str:
            continue
        try:
            close_val = float(close_str)
        except Exception:
            continue
        change_pct = 0.0
        if prev_close is not None and prev_close != 0:
            change_pct = ((close_val - prev_close) / prev_close) * 100.0
        records.append({"date": date, "close": close_val, "change_percent": round(change_pct, 4)})
        prev_close = close_val

    return records[:days]


def compute_history_features(history: List[Dict]) -> Dict:
    """Compute simple features from history: n-day return, avg change, last close."""
    if not history:
        return {"n_day_return_pct": 0.0, "avg_daily_change_pct": 0.0, "last_close": None}
    closes = [h["close"] for h in history]
    last_close = closes[0]
    end_close = closes[-1]
    n_day_return = 0.0
    if end_close:
        n_day_return = ((last_close - end_close) / end_close) * 100.0
    daily_changes = [h.get("change_percent", 0.0) for h in history]
    avg_daily_change = sum(daily_changes) / len(daily_changes) if daily_changes else 0.0
    return {
        "n_day_return_pct": round(n_day_return, 4),
        "avg_daily_change_pct": round(avg_daily_change, 4),
        "last_close": last_close,
    }


def get_openai_client():
    from openai import OpenAI
    api_key = require_env("OPENAI_API_KEY")
    return OpenAI(api_key=api_key)


def analyze_with_llm(stocks: List[Dict]) -> str:
    """Call OpenAI Chat Completions to classify stocks into buy/sell, returning JSON string."""
    client = get_openai_client()

    stock_lines = [
        f"{s['symbol']}: Price={s['price']}, Change%={s['change_percent']}" for s in stocks
    ]
    stock_summary = "\n".join(stock_lines)

    prompt = (
        "You are a stock screening assistant.\n"
        "Here is the stock data:\n\n"
        f"{stock_summary}\n\n"
        "Task:\n"
        "- Decide if each stock goes into BUY or SELL list.\n"
        "- SELL list should be ordered by priority (biggest negative change first).\n"
        "- Give short reasons for each.\n"
        "Return result in JSON with keys: buy_list, sell_list.\n"
        "Ensure JSON is valid and parsable."
    )

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    content = completion.choices[0].message.content or "{}"
    return content


def analyze_with_llm_with_history(stocks: List[Dict], histories: Dict[str, List[Dict]], features: Dict[str, Dict], days: int) -> str:
    """LLM call that includes N-day history and simple features per symbol."""
    client = get_openai_client()

    lines: List[str] = []
    for s in stocks:
        sym = s["symbol"]
        feat = features.get(sym, {})
        hist = histories.get(sym, [])
        hist_str = "; ".join([f"{h['date']}: {h['close']} ({h['change_percent']}%)" for h in hist])
        lines.append(
            (
                f"{sym}: Price={s['price']}, 1d%={s['change_percent']}; "
                f"{days}d_return%={feat.get('n_day_return_pct')}, avg_daily%={feat.get('avg_daily_change_pct')}\n"
                f"  history: {hist_str}"
            )
        )
    summary = "\n".join(lines)

    prompt = (
        "You are a stock screening assistant.\n"
        f"Use each symbol's last {days} trading days to decide BUY or SELL.\n\n"
        f"Data:\n{summary}\n\n"
        "Task:\n"
        "- Create BUY and SELL lists with short reasons.\n"
        "- Consider both short-term momentum and recent trend.\n"
        "- SELL should be ordered by biggest downside risk first.\n"
        "Return valid JSON with keys: buy_list, sell_list."
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return completion.choices[0].message.content or "{}"


def answer_question_with_llm(question: str, stocks: List[Dict]) -> str:
    """Answer an arbitrary question with optional stock context."""
    client = get_openai_client()

    stock_lines = [
        f"{s['symbol']}: Price={s['price']}, Change%={s['change_percent']}" for s in stocks
    ]
    stock_summary = "\n".join(stock_lines) if stocks else "(no context)"

    prompt = (
        "You are a helpful stock assistant.\n"
        "If stock context is provided, use it. Otherwise, answer generally.\n\n"
        f"Context:\n{stock_summary}\n\n"
        f"Question: {question}\n"
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return completion.choices[0].message.content or ""


def interactive_loop(initial_symbols: List[str]) -> None:
    tracked: List[str] = list(dict.fromkeys([s.upper() for s in initial_symbols]))

    def print_help() -> None:
        print(
            "Commands:\n"
            "  help                 Show this help\n"
            "  list                 Show tracked symbols\n"
            "  add TICKER [..]      Add one or more tickers\n"
            "  remove TICKER [..]   Remove one or more tickers\n"
            "  price TICKER         Fetch latest price for one\n"
            "  screen [days]        Fetch all + LLM buy/sell with N-day history (default 7)\n"
            "  history TICKER [d]   Show last d days history (default 7)\n"
            "  ask QUESTION         Ask any question\n"
            "  exit                 Quit\n"
        )

    print("Interactive mode. Type 'help' for commands. Ctrl+C to exit.")
    while True:
        try:
            line = input("agent> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        try:
            parts = shlex.split(line)
        except ValueError:
            print("Could not parse input")
            continue
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in {"exit", "quit", "q"}:
            break
        if cmd == "help":
            print_help()
            continue
        if cmd == "list":
            print(", ".join(tracked) if tracked else "(none)")
            continue
        if cmd == "add" and args:
            for sym in args:
                symu = sym.upper()
                if symu not in tracked:
                    tracked.append(symu)
            print("Tracked:", ", ".join(tracked))
            continue
        if cmd in {"remove", "rm"} and args:
            remove_set = {a.upper() for a in args}
            tracked[:] = [s for s in tracked if s not in remove_set]
            print("Tracked:", ", ".join(tracked) if tracked else "(none)")
            continue
        if cmd == "price" and args:
            sym = args[0].upper()
            data = fetch_stock_price(sym)
            if data:
                print(data)
            else:
                print(f"No data for {sym}")
            continue
        if cmd == "screen":
            # optional arg: days
            days = 7
            if args:
                try:
                    days = max(2, int(args[0]))
                except Exception:
                    pass
            stock_data: List[Dict] = []
            for sym in tracked:
                data = fetch_stock_price(sym)
                if data:
                    stock_data.append(data)
            if not stock_data:
                print("No stock data; check API key or rate limits.")
                continue
            # histories + features
            histories: Dict[str, List[Dict]] = {}
            feats: Dict[str, Dict] = {}
            for s in stock_data:
                sym = s["symbol"]
                hist = fetch_stock_history(sym, days=days) or []
                histories[sym] = hist
                feats[sym] = compute_history_features(hist)
            print("Fetched Stock Data:")
            for s in stock_data:
                print(s)
            print("\nLLM Recommendation (with history):")
            print(analyze_with_llm_with_history(stock_data, histories, feats, days))
            continue
        if cmd == "history" and args:
            sym = args[0].upper()
            days = 7
            if len(args) > 1:
                try:
                    days = max(2, int(args[1]))
                except Exception:
                    pass
            hist = fetch_stock_history(sym, days=days)
            if not hist:
                print(f"No history for {sym}")
                continue
            for h in hist:
                print(h)
            continue
        if cmd == "ask":
            question = line.partition(" ")[2].strip()
            if not question:
                print("Usage: ask QUESTION")
                continue
            # Provide current context
            context_data: List[Dict] = []
            for sym in tracked[:5]:  # limit to reduce rate-limit impact
                data = fetch_stock_price(sym)
                if data:
                    context_data.append(data)
            print(answer_question_with_llm(question, context_data))
            continue

        print("Unknown command. Type 'help'.")


def main() -> None:
    symbols_env = os.getenv("STOCK_SYMBOLS", "AAPL,TSLA,AMZN,NVDA,MSFT")
    symbols = [s.strip().upper() for s in symbols_env.split(",") if s.strip()]

    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--interactive", "-i", action="store_true")
    args = parser.parse_args()

    if args.interactive or os.getenv("INTERACTIVE", "0") == "1":
        interactive_loop(symbols)
        return

    stock_data: List[Dict] = []
    for sym in symbols:
        data = fetch_stock_price(sym)
        if data:
            stock_data.append(data)

    print("Fetched Stock Data:")
    for s in stock_data:
        print(s)

    if not stock_data:
        print("No stock data fetched; check your ALPHA_VANTAGE_KEY or API limits.")
        return

    print("\nLLM Recommendation:")
    result_text = analyze_with_llm(stock_data)
    try:
        result_json = json.loads(result_text)
        print(json.dumps(result_json, indent=2))
    except Exception:
        print(result_text)


if __name__ == "__main__":
    main()


