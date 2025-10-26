from typing import List, Dict, Any


def rerank_top_one(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Deterministic top-1: sort by score desc then title asc and pick first."""
    if not candidates:
        return {"title": "", "score": 0.0}
    sorted_candidates = sorted(candidates, key=lambda x: (-float(x.get("score", 0)), str(x.get("title", ""))))
    return sorted_candidates[0]


