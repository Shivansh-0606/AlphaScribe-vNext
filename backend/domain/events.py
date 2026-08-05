"""TraceEvent — the frozen `{node, status, message, ts, ...extra}` contract
(07 G-2) that every SSE stream emits. One shared shape for both the existing
report pipeline and any future graph (Learning included, once built) — this
is exactly the "reusable SSE infrastructure" this phase asks for at the
domain level; infrastructure/streaming/sse.py builds the transport on top.

TypedDict, not a dataclass: TraceEvent is serialized straight to JSON on the
wire (`json.dumps(event)` in the existing SSE generator) and constructed as
plain dict literals throughout agents/nodes.py — a TypedDict lets both sides
treat it as "a dict with a known shape" with no construction/serialization
boilerplate, matching the existing `_event()` helper's own return type.
"""
from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

EventStatus = Literal["start", "ok", "warn", "error"]


class TraceEvent(TypedDict):
    node: str
    status: EventStatus
    message: NotRequired[str]
    ts: NotRequired[str]
    # `extra` fields (count, stages, retry_count, ...) are added ad hoc by
    # callers via **extra, exactly as agents/nodes.py's `_event()` does today
    # — TypedDict permits extra keys are NOT type-checked here on purpose;
    # each node's payload shape is that node's concern, not this contract's.


def is_terminal_event(event: dict) -> bool:
    """The `pipeline` wrapper's closing event (07 §4.2) — both EventBus
    adapters need to recognize it identically: the Redis Streams adapter
    stops iterating and lets the key's TTL take over (09 §4.4), and the
    in-memory adapter stops the subscriber's async generator. Shared here so
    the two adapters can't silently disagree on what "done" means."""
    return event.get("node") == "pipeline" and event.get("status") in ("ok", "error", "warn")
