"""EventBus — the AD-8 fix for 01 D-1 (09 §4).

Two adapters implementing application.ports.EventBus:

  InMemoryEventBus  — per-subscriber asyncio.Queue fan-out. This is not a
                      test double bolted on afterward; it IS the fix for
                      01 D-1 in pure Python, and it is the documented
                      fallback (09 RA-2) when Redis is unavailable.
  RedisEventBus     — Redis Streams, independent cursors per subscriber via
                      plain XREAD.

09 §4.1's single most important rule: XREAD, NEVER XREADGROUP. A consumer
group DISTRIBUTES entries across group members — using one here would
silently recreate 01 D-1 (two subscribers splitting one event stream) behind
an API that looks more "correct." Nothing in this file calls xreadgroup or
xgroup_create; tests/unit/test_redis_event_bus.py statically asserts that.
"""
from __future__ import annotations

import asyncio
import contextlib
import json
from typing import AsyncIterator

import redis.asyncio as redis

from domain.events import TraceEvent, is_terminal_event
from infrastructure.observability.metrics import track_redis_errors

_KEEPALIVE: TraceEvent = {"node": "_keepalive", "status": "ok"}  # never sent to a client (07 §4.4's SSE
# layer maps this internally to `: keepalive\n\n`; not part of the frozen event envelope itself, G-2)

_STREAM_MAXLEN = 1000
_STREAM_TTL_S = 3600  # 09 §4.4 — grace window for a reconnect after the job finished
_XREAD_BLOCK_MS = 15_000
_XREAD_COUNT = 100


class InMemoryEventBus:
    """The documented fallback (09 RA-2) and the actual 01 D-1 fix: every
    call to subscribe() gets its own queue, so N concurrent subscribers to
    one job each receive every event — the property the single shared
    `asyncio.Queue` in server.py's current SSE generator does not have."""

    def __init__(self) -> None:
        self._history: dict[str, list[TraceEvent]] = {}
        self._subscribers: dict[str, list[asyncio.Queue]] = {}

    async def publish(self, job_id: str, event: TraceEvent) -> None:
        self._history.setdefault(job_id, []).append(event)
        for q in self._subscribers.get(job_id, []):
            await q.put(event)

    async def subscribe(self, job_id: str) -> AsyncIterator[TraceEvent]:
        q: asyncio.Queue = asyncio.Queue()
        # Replay first, THEN register — matches 09 §4.3's exact-replay
        # property: nothing published between "read history" and "start
        # listening" can be missed or double-delivered, because there is no
        # gap (registration happens before we ever await on the queue).
        replay = list(self._history.get(job_id, []))
        self._subscribers.setdefault(job_id, []).append(q)
        try:
            for ev in replay:
                yield ev
                if is_terminal_event(ev):
                    return
            while True:
                ev = await q.get()
                yield ev
                if is_terminal_event(ev):
                    return
        finally:
            subs = self._subscribers.get(job_id)
            if subs and q in subs:
                subs.remove(q)

    async def history(self, job_id: str) -> list[TraceEvent]:
        return list(self._history.get(job_id, []))


class RedisEventBus:
    """09 §4 — Streams with independent cursors (XREAD only, never
    XREADGROUP — see the module docstring)."""

    def __init__(self, client: redis.Redis, *, namespace: str = "as:v1") -> None:
        self._r = client
        self._ns = namespace

    def _key(self, job_id: str) -> str:
        return f"{self._ns}:job:{job_id}:events"

    async def publish(self, job_id: str, event: TraceEvent) -> None:
        async with track_redis_errors("event_bus.publish"):
            key = self._key(job_id)
            await self._r.xadd(key, {"data": json.dumps(event)}, maxlen=_STREAM_MAXLEN, approximate=True)
            await self._r.expire(key, _STREAM_TTL_S)

    async def subscribe(self, job_id: str) -> AsyncIterator[TraceEvent]:
        key = self._key(job_id)
        last = "0-0"
        while True:
            resp = await self._r.xread({key: last}, block=_XREAD_BLOCK_MS, count=_XREAD_COUNT)
            if not resp:
                yield _KEEPALIVE
                continue
            for _stream_key, entries in resp:
                for entry_id, fields in entries:
                    last = entry_id
                    ev = json.loads(fields["data"])
                    yield ev
                    if is_terminal_event(ev):
                        return

    async def history(self, job_id: str) -> list[TraceEvent]:
        entries = await self._r.xrange(self._key(job_id))
        return [json.loads(fields["data"]) for _entry_id, fields in entries]
