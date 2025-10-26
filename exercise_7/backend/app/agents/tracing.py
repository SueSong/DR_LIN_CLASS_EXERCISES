import time
import uuid
from contextlib import contextmanager
from typing import Dict, Any, Optional, List


class TraceStore:
    def __init__(self) -> None:
        self._traces: Dict[str, Dict[str, Any]] = {}
        self._spans: Dict[str, List[Dict[str, Any]]] = {}

    def new_trace(self, trace_id: Optional[str] = None) -> str:
        tid = trace_id or str(uuid.uuid4())
        self._traces[tid] = {"trace_id": tid, "created_at": time.time()}
        self._spans[tid] = []
        return tid

    def add_span(self, trace_id: str, span: Dict[str, Any]) -> None:
        self._spans.setdefault(trace_id, []).append(span)

    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        return {
            "trace": self._traces.get(trace_id, {"trace_id": trace_id}),
            "spans": self._spans.get(trace_id, []),
        }


trace_store = TraceStore()


@contextmanager
def span(trace_id: str, name: str, parent_span_id: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
    span_id = str(uuid.uuid4())
    start = time.time()
    attrs = dict(attributes or {})
    try:
        yield span_id, attrs
        status = "ok"
        error_code = None
    except Exception as e:
        status = "error"
        error_code = type(e).__name__
        raise
    finally:
        end = time.time()
        trace_store.add_span(
            trace_id,
            {
                "span_id": span_id,
                "parent_span_id": parent_span_id,
                "name": name,
                "start": start,
                "end": end,
                "attributes": {**attrs, "tool_status": status, "error_code": error_code, "latency_ms": int((end - start) * 1000)},
            },
        )


