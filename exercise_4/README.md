# Exercise 4 — Routed Chat (Stock Agent + LLM)

A Python FastAPI backend with simple web UI. It routes stock-related questions to a stock agent (Alpha Vantage with yfinance fallback) and all other questions to OpenAI Chat.

## Setup

1) Backend env
```bash
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend
cat > .env << 'EOF'
OPENAI_API_KEY=your_openai_key
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
OPENAI_MODEL=gpt-4o-mini
PORT=8020
EOF
```

2) Run backend
```bash
bash run.sh
# open http://localhost:8020
```

3) Web UI options
- Static HTML served by backend at `/` (http://localhost:8020)
- Python Streamlit UI:
```bash
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/frontend_py
# optional: echo "BACKEND_BASE=http://localhost:8020" > .env
bash run.sh
# open http://localhost:4020
```

Try:
- "What is the price of AAPL and MSFT?" → stock agent
- "Explain reinforcement learning" → LLM

Notes:
- Stock agent uses Alpha Vantage first, then Yahoo (yfinance) fallback.
- Adjust routing in `backend/app.py` (`is_stock_question`, `extract_symbols`).
