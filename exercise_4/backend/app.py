import os
from typing import List, Optional, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from agents.stock_agent import screen_symbols


load_dotenv()

OPENAI_MODEL_DEFAULT = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def require_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing env: {name}")
    return val


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    temperature: Optional[float] = 0.3


class ChatResponse(BaseModel):
    reply: str


app = FastAPI(title="Exercise 4 Router Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="static")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
@app.get("/")
def root_redirect():
    return RedirectResponse(url="/ui")


def is_stock_question(text: str) -> bool:
    keywords = ["stock", "stocks", "ticker", "price", "quote", "invest", "buy", "sell"]
    has_keyword = any(k in text.lower() for k in keywords)
    looks_like_symbol = text.strip().upper().replace("$", "").isalpha() and 1 <= len(text.strip()) <= 5
    return has_keyword or looks_like_symbol


def extract_symbols(text: str) -> List[str]:
    # naive: split on spaces, pick uppercase tokens of len 1..5 or prefixed with $
    syms: List[str] = []
    for tok in text.replace(",", " ").split():
        t = tok.upper().strip()
        if t.startswith("$"):
            t = t[1:]
        if t.isalpha() and 1 <= len(t) <= 5:
            syms.append(t)
    # de-dup keep order
    seen = set()
    out: List[str] = []
    for s in syms:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out[:5]


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages required")
    last = req.messages[-1]
    user_text = last.content

    if is_stock_question(user_text):
        symbols = extract_symbols(user_text) or ["AAPL", "MSFT"]
        quotes = screen_symbols(symbols)
        if not quotes:
            return ChatResponse(reply="Sorry, I couldn't fetch any quotes right now.")
        lines = [f"{q['symbol']}: price={q['price']}, change%={q['change_percent']:.2f}" for q in quotes]
        reply = "\n".join(lines)
        return ChatResponse(reply=reply)

    # otherwise route to LLM
    try:
        from openai import OpenAI
        client = OpenAI(api_key=require_env("OPENAI_API_KEY"))
        completion = client.chat.completions.create(
            model=req.model or OPENAI_MODEL_DEFAULT,
            messages=[m.dict() for m in req.messages],
            temperature=req.temperature or 0.3,
        )
        content = completion.choices[0].message.content or ""
        return ChatResponse(reply=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")


