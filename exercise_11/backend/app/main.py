from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import coach, websocket, sse, hitl, billing
from .observability import setup_observability

app = FastAPI(title="Child Growth Assistant", version="0.1.0")

# Initialize observability
setup_observability(
    service_name="child-growth-assistant",
    service_version="0.1.0",
    enable_console_export=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3080",
        "http://localhost:3081",
        "http://localhost:3082",
        "http://localhost:3083",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/readyz")
async def readyz():
    # TODO: check RAG index and model key here later
    return {"ready": True}


app.include_router(coach.router)
app.include_router(websocket.router)
app.include_router(sse.router)
app.include_router(hitl.router)
app.include_router(billing.router)


