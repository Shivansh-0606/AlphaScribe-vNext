"""Unit check for app/container.py — the composition root (06 AD-3/ADR-004).

    python backend/tests/unit/test_container.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _settings(**overrides):
    from app.settings import Settings

    defaults = dict(MONGO_URL="mongodb://localhost:27017", DB_NAME="x")
    defaults.update(overrides)
    real = {k: os.environ.get(k) for k in defaults}
    os.environ.update(defaults)
    try:
        return Settings()
    finally:
        for k, v in real.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_default_backend_is_memory_and_needs_no_running_redis():
    real = os.environ.pop("JOB_BACKEND", None)
    try:
        from app.container import build_container
        from infrastructure.redis.event_bus import InMemoryEventBus
        from infrastructure.redis.job_store import InMemoryJobStore

        c = build_container(_settings())
        assert isinstance(c.jobs, InMemoryJobStore)
        assert isinstance(c.events, InMemoryEventBus)
    finally:
        if real is not None:
            os.environ["JOB_BACKEND"] = real


def test_container_job_lifecycle_works_end_to_end():
    real = os.environ.pop("JOB_BACKEND", None)
    try:
        from app.container import build_container
        from domain.models import JobKind

        async def run():
            c = build_container(_settings(MAX_ACTIVE_JOBS="8"))
            job = await c.job_lifecycle.start("j1", JobKind.RESEARCH, "u1", ticker="AAPL")
            assert job.ticker == "AAPL"
            await c.job_lifecycle.complete("j1")
            assert (await c.job_lifecycle.get("j1")).status.value == "completed"

        asyncio.run(run())
    finally:
        if real is not None:
            os.environ["JOB_BACKEND"] = real


def test_redis_backend_constructs_without_a_reachable_redis():
    # redis.asyncio.Redis.from_url() is lazy (confirmed for real elsewhere in
    # this test suite) — selecting the redis backend must not require a live
    # server just to build the container.
    real = os.environ.get("JOB_BACKEND")
    os.environ["JOB_BACKEND"] = "redis"
    try:
        from app.container import build_container
        from infrastructure.redis.event_bus import RedisEventBus
        from infrastructure.redis.job_store import RedisJobStore

        c = build_container(_settings())
        assert isinstance(c.jobs, RedisJobStore)
        assert isinstance(c.events, RedisEventBus)
    finally:
        if real is None:
            os.environ.pop("JOB_BACKEND", None)
        else:
            os.environ["JOB_BACKEND"] = real


def test_unknown_backend_raises_a_readable_error():
    real = os.environ.get("JOB_BACKEND")
    os.environ["JOB_BACKEND"] = "not-a-real-backend"
    try:
        from app.container import build_container

        try:
            build_container(_settings())
        except ValueError as e:
            assert "not-a-real-backend" in str(e)
        else:
            raise AssertionError("expected ValueError for an unknown JOB_BACKEND")
    finally:
        if real is None:
            os.environ.pop("JOB_BACKEND", None)
        else:
            os.environ["JOB_BACKEND"] = real


if __name__ == "__main__":
    test_default_backend_is_memory_and_needs_no_running_redis()
    test_container_job_lifecycle_works_end_to_end()
    test_redis_backend_constructs_without_a_reachable_redis()
    test_unknown_backend_raises_a_readable_error()
    print("ok: Container — default memory backend, end-to-end job lifecycle, redis backend construction, "
          "unknown-backend error")
