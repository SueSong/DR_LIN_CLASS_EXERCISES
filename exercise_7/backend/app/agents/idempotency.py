import hashlib


def make_idempotency_key(trace_id: str, node: str, attempt: int) -> str:
    raw = f"{trace_id}:{node}:{attempt}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


