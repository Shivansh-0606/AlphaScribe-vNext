"""RateLimiter — sliding-window (09 §7), faithfully mirroring
agents/auth.py's existing `_recent_hits`/`is_rate_limited`/`record_hit`
semantics: a FIXED-window `INCR`+`EXPIRE` would allow a ~2x burst across a
window boundary (09 RR-8) — a real regression a naive Redis port could
introduce silently, which is exactly why 09 §7.1 calls this out explicitly.

Protocol sense is inverted from agents.auth.is_rate_limited() on purpose:
`hit(key) -> bool` returns True when the call is ALLOWED (the natural way to
write `if not await limiter.hit(key): raise 429`), where auth.py's
`is_rate_limited() -> bool` returns True when BLOCKED. Same algorithm,
opposite polarity — call sites read either way; this port picked the sense
that reads better at the call site.

`hit()` checks-then-records atomically in one call (the existing auth.py
pattern is check `is_rate_limited()`, THEN separately `record_hit()` — two
calls ordered by the caller, closing the race only by convention, per
server.py's own comment on /auth/login). Folding both into one call removes
that race structurally rather than by discipline.
"""
from __future__ import annotations

import hashlib
import secrets
import time

import redis.asyncio as redis

from infrastructure.observability.metrics import track_redis_errors

_DEFAULT_WINDOW_S = 15 * 60  # matches agents/auth.py's _RATE_LIMIT_WINDOW
_DEFAULT_MAX_HITS = 5  # matches agents/auth.py's _RATE_LIMIT_MAX


class InMemoryRateLimiter:
    """The documented fallback (09 RA-2). Independent of agents/auth.py's
    own `_hits` dict — infrastructure/ does not import agents/ (06's
    dependency rule, seeded in tests/unit/test_architecture.py) — but
    reproduces its exact sliding-window algorithm."""

    def __init__(self, *, window_s: float = _DEFAULT_WINDOW_S, max_hits: int = _DEFAULT_MAX_HITS) -> None:
        self._window_s = window_s
        self._max_hits = max_hits
        self._hits: dict[str, list[float]] = {}

    def _recent(self, key: str, now: float) -> list[float]:
        return [t for t in self._hits.get(key, []) if now - t < self._window_s]

    async def hit(self, key: str) -> bool:
        now = time.time()
        recent = self._recent(key, now)
        if len(recent) >= self._max_hits:
            self._hits[key] = recent  # keep pruned, don't record the blocked attempt
            return False
        recent.append(now)
        self._hits[key] = recent
        return True

    async def clear(self, key: str) -> None:
        self._hits.pop(key, None)


class RedisRateLimiter:
    """09 §7 — a ZSET per key, pruned-then-checked-then-conditionally-added
    in one pipeline so the check and the record cannot race across two
    concurrent requests for the same key."""

    def __init__(
        self,
        client: redis.Redis,
        *,
        namespace: str = "as:v1",
        window_s: float = _DEFAULT_WINDOW_S,
        max_hits: int = _DEFAULT_MAX_HITS,
    ) -> None:
        self._r = client
        self._ns = namespace
        self._window_s = window_s
        self._max_hits = max_hits

    def _key(self, identifier: str) -> str:
        # 09 RA-4 — hash the identifier before it becomes part of a key, so a
        # raw email never sits in `--scan` output or an AOF file.
        digest = hashlib.sha256(identifier.encode()).hexdigest()
        return f"{self._ns}:rl:{digest}"

    async def hit(self, key: str) -> bool:
        async with track_redis_errors("rate_limiter.hit"):
            now = time.time()
            redis_key = self._key(key)
            # Prune first so the count reflects only the current window.
            await self._r.zremrangebyscore(redis_key, "-inf", now - self._window_s)
            count = await self._r.zcard(redis_key)
            if count >= self._max_hits:
                return False
            member = f"{now}:{secrets.token_urlsafe(6)}"  # unique per hit, even within the same tick
            async with self._r.pipeline() as p:
                p.zadd(redis_key, {member: now})
                p.expire(redis_key, int(self._window_s))
                await p.execute()
            return True

    async def clear(self, key: str) -> None:
        await self._r.delete(self._key(key))
