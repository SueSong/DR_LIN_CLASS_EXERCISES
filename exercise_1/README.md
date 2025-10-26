# Exercise 1 — Hello Agent: Stock Screener

This exercise builds a simple agentic CLI that:

- fetches real-time quotes from Alpha Vantage
- sends a concise stock summary (with optional 7-day history) to an LLM
- returns BUY and SELL lists with short reasons

Students can extend it with commands, memory, and visualization.

## Prerequisites

- Python 3.10+
- An Alpha Vantage API key
- An OpenAI API key

## Setup

1) Navigate to this folder:
```bash
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_1
```

2) Create virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3) Install dependencies:
```bash
pip install -r requirements.txt
```

4) Configure environment variables:

- Copy `.env.example` to `.env` and fill in your keys
- Or export variables directly in your shell

`.env.example`:
```env
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
OPENAI_API_KEY=your_openai_api_key
# Optional: comma-separated list
STOCK_SYMBOLS=AAPL,TSLA,AMZN,NVDA,MSFT
```

Load `.env` automatically by using `setup.sh` (recommended):
```bash
bash setup.sh
```

## Run

Quick start (one-liner):
```bash
bash run.sh
```

Or run manually:
```bash
python hello_agent.py
```

Example output:
```text
Fetched Stock Data:
{'symbol': 'AAPL', 'price': 172.33, 'change_percent': -0.54}
{'symbol': 'TSLA', 'price': 238.44, 'change_percent': 2.31}

LLM Recommendation:
{
  "buy_list": ["TSLA (upward momentum)", "NVDA (positive growth)"],
  "sell_list": ["AAPL (declining trend)", "AMZN (flat performance)"]
}
```

## Notes

- Alpha Vantage free tier has rate limits. If requests return `None`, try fewer symbols, wait a minute, or reduce history days.
- Change tracked symbols via env var: `STOCK_SYMBOLS="AAPL,MSFT"`.
- The script prints JSON if the model returns valid JSON; otherwise prints raw text.

## Interactive mode

Start interactive:
```bash
python hello_agent.py --interactive
# or
INTERACTIVE=1 python hello_agent.py
```

Commands:
- `help`: show commands
- `list`: show tracked tickers
- `add NVDA AAPL`: track new symbols
- `remove TSLA`: untrack symbols
- `price NFLX`: fetch current quote
- `history NVDA [7]`: show last N days (default 7) of daily closes
- `screen [7]`: fetch all tracked with N-day history and get LLM buy/sell
- `ask What do you think about GOOGL?`: free-form question with recent context

## Extensions (for class discussion)

- Add a CLI command loop to add/remove symbols during runtime
- Persist last decisions to a local JSON file
- Plot change% trend using `matplotlib`
- Add function-calling to force consistent JSON schema

## Troubleshooting

- If you see `Missing required environment variable`, check `.env` or exported vars
- If you see HTTP 200 with empty `Global Quote`, you might be rate-limited or symbol is invalid
- If LLM output isn’t JSON, reduce temperature or add a JSON schema/system prompt


