"""
Intentional buggy snippets for static analysis demo (pylint/pyright).
These functions are not executed at runtime.
"""

from typing import Any, Dict, List
import asyncio


def api_hallucination_wrong_signature() -> None:
    # API hallucination / wrong signatures: wrong attribute, wrong arg order
    from openai import OpenAI  # type: ignore

    client = OpenAI()  # missing api_key on purpose
    # Nonexistent method + wrong params
    client.chat.completions.create_completion(
        "gpt-4o-mini",  # should be model=..., but also wrong method name
        messages="not-a-list",  # wrong type
    )  # type: ignore[attr-defined]


def dependency_version_mismatch() -> None:
    # Dependency mismatch: module name vs package; pretend wrong import
    import pydantics  # type: ignore[import-not-found]
    _ = pydantics  # keep referenced


async def async_await_bug() -> None:
    # Forgotten await
    asyncio.sleep(0.1)  # type: ignore[call-arg]


def boundary_edge_cases(xs: List[int]) -> int:
    # Off-by-one / empty list bug
    return xs[1]  # index error for len<2 not guarded


def data_contract_drift(payload: Dict[str, Any]) -> str:
    # JSON shape mismatch: expect camelCase but backend provides 'reply'
    return str(payload["replyText"])  # KeyError if only 'reply' exists




