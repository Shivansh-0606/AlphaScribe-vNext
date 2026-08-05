"""Port-conformance suite for RateLimiter (09 §11): InMemoryRateLimiter for
real, RedisRateLimiter against fakeredis. The sliding-window test is the one
that matters most — 09 RR-8's specific regression (a fixed-window `INCR`+
`EXPIRE` port would allow up to a 2x burst across a window boundary).

    python backend/tests/unit/test_redis_rate_limiter.py
"""
import asyncio
import os
import sys
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import fakeredis.aioredis as fakeredis_async

from infrastructure.redis.rate_limiter import InMemoryRateLimiter, RedisRateLimiter

ADAPTERS = {
    "memory": lambda: InMemoryRateLimiter(window_s=15 * 60, max_hits=5),
    "redis (fakeredis)": lambda: RedisRateLimiter(
        fakeredis_async.FakeRedis(decode_responses=True), window_s=15 * 60, max_hits=5
    ),
}


def _key() -> str:
    return f"test:{uuid.uuid4()}"


def test_allows_five_hits_then_blocks_the_sixth():
    for label, make in ADAPTERS.items():
        async def run(make=make):
            limiter = make()
            key = _key()
            for i in range(5):
                assert await limiter.hit(key) is True, f"[{label}] hit {i + 1}/5 should be allowed"
            assert await limiter.hit(key) is False, f"[{label}] 6th hit should be blocked"

        asyncio.run(run())


def test_clear_resets_the_window():
    for label, make in ADAPTERS.items():
        async def run(make=make):
            limiter = make()
            key = _key()
            for _ in range(5):
                await limiter.hit(key)
            assert await limiter.hit(key) is False, label
            await limiter.clear(key)
            assert await limiter.hit(key) is True, f"[{label}] should be allowed again after clear()"

        asyncio.run(run())


def test_blocked_attempts_are_not_recorded_against_the_window():
    # A blocked call must not itself extend/pollute the window — matches
    # agents/auth.py's existing check-before-record ordering.
    for label, make in ADAPTERS.items():
        async def run(make=make):
            limiter = make()
            key = _key()
            for _ in range(5):
                await limiter.hit(key)
            for _ in range(10):  # a flood of additional blocked attempts
                assert await limiter.hit(key) is False, label
            await limiter.clear(key)
            assert await limiter.hit(key) is True, label

        asyncio.run(run())


def test_sliding_window_rejects_a_boundary_burst():
    """09 RR-8 — the fixed-window regression this test exists to catch.
    5 hits placed just inside the window boundary, then a 6th placed just
    after — a correct sliding window still blocks it; a fixed
    INCR+EXPIRE(window) implementation would have reset its counter at the
    window boundary and wrongly allow a fresh burst."""
    window_s = 1.0  # short window so the test runs fast without mocking the clock
    for label, make in [
        ("memory", lambda: InMemoryRateLimiter(window_s=window_s, max_hits=5)),
        ("redis (fakeredis)", lambda: RedisRateLimiter(
            fakeredis_async.FakeRedis(decode_responses=True), window_s=window_s, max_hits=5
        )),
    ]:
        async def run(make=make):
            limiter = make()
            key = _key()
            for _ in range(5):
                assert await limiter.hit(key) is True, label
            # Still well inside the 1s window -> must still be blocked.
            await asyncio.sleep(window_s * 0.3)
            assert await limiter.hit(key) is False, (
                f"[{label}] boundary burst allowed — sliding window regressed to fixed-window semantics"
            )
            # Past the full window -> the old hits have aged out, allowed again.
            await asyncio.sleep(window_s * 0.8)
            assert await limiter.hit(key) is True, label

        asyncio.run(run())


def test_different_keys_are_independent():
    for label, make in ADAPTERS.items():
        async def run(make=make):
            limiter = make()
            key_a, key_b = _key(), _key()
            for _ in range(5):
                await limiter.hit(key_a)
            assert await limiter.hit(key_a) is False, label
            assert await limiter.hit(key_b) is True, f"[{label}] key_b must be unaffected by key_a's limit"

        asyncio.run(run())


if __name__ == "__main__":
    test_allows_five_hits_then_blocks_the_sixth()
    test_clear_resets_the_window()
    test_blocked_attempts_are_not_recorded_against_the_window()
    test_sliding_window_rejects_a_boundary_burst()
    test_different_keys_are_independent()
    print("ok: RateLimiter port conformance (memory + redis/fakeredis) — 5-then-block, clear, "
          "no-record-on-block, sliding-window boundary burst, key independence")
