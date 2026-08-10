"""Port-conformance suite for EventBus (09 §11): the SAME behavioral checks
run against BOTH adapters — InMemoryEventBus for real, RedisEventBus against
fakeredis (a real Redis-protocol server, not a mock of this module's own
code — XADD/XREAD/EXPIRE all execute for real; see the module docstring on
why this environment has no real `redis-server`/Docker available, and why
fakeredis is a materially stronger check than mocking `redis.asyncio.Redis`
directly would be).

The fan-out test is the one that must never be deleted: it is the literal
regression test for 01 D-1 (the defect Redis Streams were adopted to fix,
09 §0) and for 09 RR-1 (the risk that a future edit reaches for XREADGROUP,
which would silently recreate D-1 behind a more "correct"-looking API).

    python backend/tests/unit/test_redis_event_bus.py
"""
import ast
import asyncio
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import fakeredis.aioredis as fakeredis_async

from infrastructure.redis import event_bus as event_bus_module
from infrastructure.redis.event_bus import InMemoryEventBus, RedisEventBus


def _new_redis_bus() -> RedisEventBus:
    return RedisEventBus(fakeredis_async.FakeRedis(decode_responses=True))


ADAPTERS = {
    "memory": lambda: InMemoryEventBus(),
    "redis (fakeredis)": _new_redis_bus,
}

TERMINAL = {"node": "pipeline", "status": "ok"}


async def _drain(bus, job_id: str, limit: int = 50) -> list[dict]:
    out = []
    async for ev in bus.subscribe(job_id):
        out.append(ev)
        if len(out) >= limit:
            break
    return out


def test_static_ban_on_xreadgroup():
    """09 §4.1's binding rule, enforced mechanically: xreadgroup/
    xgroup_create must appear NOWHERE in this module's source."""
    src = inspect.getsource(event_bus_module)
    tree = ast.parse(src)
    banned = {"xreadgroup", "xgroup_create"}
    calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr in banned
    }
    assert not calls, f"09 §4.1 violation — banned Redis Stream call(s) used: {calls}"


def test_fan_out_two_concurrent_subscribers_each_get_every_event():
    """THE regression test for 01 D-1. Must never be deleted (09 §11)."""
    for label, make_bus in ADAPTERS.items():
        async def run(make_bus=make_bus):
            bus = make_bus()
            job_id = "job-fanout"
            events = [
                {"node": "pipeline", "status": "start"},
                {"node": "retriever", "status": "ok", "count": 5},
                {"node": "explainer", "status": "ok"},
                TERMINAL,
            ]

            async def subscriber():
                return await _drain(bus, job_id)

            sub_a = asyncio.ensure_future(subscriber())
            sub_b = asyncio.ensure_future(subscriber())
            await asyncio.sleep(0.05)  # let both subscribers register before publishing
            for ev in events:
                await bus.publish(job_id, ev)
            got_a = await asyncio.wait_for(sub_a, timeout=5)
            got_b = await asyncio.wait_for(sub_b, timeout=5)
            assert got_a == events, f"[{label}] subscriber A missed events: got {got_a}"
            assert got_b == events, f"[{label}] subscriber B missed events: got {got_b}"

        asyncio.run(run())


def test_replay_then_live_no_duplicates():
    for label, make_bus in ADAPTERS.items():
        async def run(make_bus=make_bus):
            bus = make_bus()
            job_id = "job-replay"
            await bus.publish(job_id, {"node": "pipeline", "status": "start"})
            await bus.publish(job_id, {"node": "retriever", "status": "ok"})

            # Connect AFTER two events already happened -> must replay them,
            # then continue live with no gap and no duplicate.
            sub = asyncio.ensure_future(_drain(bus, job_id))
            await asyncio.sleep(0.05)
            await bus.publish(job_id, TERMINAL)
            got = await asyncio.wait_for(sub, timeout=5)
            assert got == [
                {"node": "pipeline", "status": "start"},
                {"node": "retriever", "status": "ok"},
                TERMINAL,
            ], f"[{label}] replay+live mismatch: {got}"

        asyncio.run(run())


def test_history_returns_everything_published():
    for label, make_bus in ADAPTERS.items():
        async def run(make_bus=make_bus):
            bus = make_bus()
            job_id = "job-history"
            events = [{"node": "pipeline", "status": "start"}, TERMINAL]
            for ev in events:
                await bus.publish(job_id, ev)
            assert await bus.history(job_id) == events, f"[{label}] history mismatch"

        asyncio.run(run())


def test_subscribe_stops_at_the_terminal_event():
    for label, make_bus in ADAPTERS.items():
        async def run(make_bus=make_bus):
            bus = make_bus()
            job_id = "job-terminal"
            await bus.publish(job_id, {"node": "pipeline", "status": "start"})
            await bus.publish(job_id, TERMINAL)
            got = await asyncio.wait_for(_drain(bus, job_id, limit=10), timeout=5)
            assert got == [{"node": "pipeline", "status": "start"}, TERMINAL], (
                f"[{label}] subscriber did not stop cleanly at the terminal event: {got}"
            )

        asyncio.run(run())


def test_redis_subscribe_yields_keepalive_after_the_configured_idle_window():
    """T-10 (M7, Doc 28 B-5): the InMemory adapter has no idle timeout at all
    (`await q.get()` blocks forever) — keepalive is a Redis Streams-only
    behavior, `subscribe()`'s own XREAD `block=_XREAD_BLOCK_MS` timing out
    with no new entries (infrastructure/redis/event_bus.py:98-105). Exercises
    the real method against fakeredis (a real Redis-protocol implementation,
    not a mock of this module — see the module docstring), with the module's
    `_XREAD_BLOCK_MS` constant monkeypatched down for a fast test — the
    production value (15s) is unchanged, only this test's view of it during
    the call is, since `subscribe()` reads the module global at call time."""
    async def run():
        real_block_ms = event_bus_module._XREAD_BLOCK_MS
        event_bus_module._XREAD_BLOCK_MS = 200
        try:
            bus = _new_redis_bus()
            job_id = "job-keepalive"
            gen = bus.subscribe(job_id)

            first = await asyncio.wait_for(gen.__anext__(), timeout=5)
            assert first == event_bus_module._KEEPALIVE, (
                f"expected a keepalive after the idle window with nothing published, got {first}"
            )

            # A real event published after the keepalive must still arrive —
            # keepalive is a "nothing happened yet" signal, not a stream end.
            await bus.publish(job_id, TERMINAL)
            second = await asyncio.wait_for(gen.__anext__(), timeout=5)
            assert second == TERMINAL
        finally:
            event_bus_module._XREAD_BLOCK_MS = real_block_ms

    asyncio.run(run())


if __name__ == "__main__":
    test_static_ban_on_xreadgroup()
    test_fan_out_two_concurrent_subscribers_each_get_every_event()
    test_replay_then_live_no_duplicates()
    test_history_returns_everything_published()
    test_subscribe_stops_at_the_terminal_event()
    test_redis_subscribe_yields_keepalive_after_the_configured_idle_window()
    print("ok: EventBus port conformance (memory + redis/fakeredis) — fan-out, replay, history, "
          "terminal-stop, XREADGROUP ban, keepalive-after-idle")
