import os
from typing import List, Dict

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

BACKEND_BASE = os.getenv("BACKEND_BASE", "http://localhost:8020").rstrip("/")

st.set_page_config(page_title="Exercise 4 — Routed Chat (Python UI)", page_icon="💬")
st.title("Exercise 4 — Routed Chat (Python UI)")
st.caption("Stock questions route to stock agent; others go to LLM via FastAPI backend.")

if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]


def render_history() -> None:
    for m in st.session_state.messages:
        if m["role"] == "system":
            continue
        with st.chat_message(m["role"]):
            st.markdown(m["content"])  # safe rendering


def send_message(user_text: str) -> None:
    st.session_state.messages.append({"role": "user", "content": user_text})
    try:
        resp = requests.post(
            f"{BACKEND_BASE}/chat",
            json={
                "messages": st.session_state.messages,
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "temperature": 0.3,
            },
            timeout=60,
        )
        if resp.ok:
            data = resp.json()
            reply = data.get("reply", "")
        else:
            reply = f"Error {resp.status_code}: {resp.text}"
    except Exception as e:
        reply = f"Request failed: {e}"
    st.session_state.messages.append({"role": "assistant", "content": reply})


render_history()

if prompt := st.chat_input("Ask about AAPL price or any other question..."):
    with st.spinner("Sending..."):
        send_message(prompt)
        st.rerun()

with st.expander("Settings"):
    st.write(f"Backend: {BACKEND_BASE}")
    st.write("Set BACKEND_BASE env var to change.")


