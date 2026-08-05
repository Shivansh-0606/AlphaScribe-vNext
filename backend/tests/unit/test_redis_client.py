"""Unit check for infrastructure/redis/client.py — ping and the 09 §9.2
noeviction startup assertion. Against fakeredis (real command execution).

    python backend/tests/unit/test_redis_client.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import fakeredis.aioredis as fakeredis_async

from domain.errors import InfrastructureError
from infrastructure.redis.client import assert_noeviction_policy, ping


def test_ping_true_on_a_live_connection():
    r = fakeredis_async.FakeRedis(decode_responses=True)
    assert asyncio.run(ping(r)) is True


def test_ping_raises_infrastructure_error_when_unreachable():
    class _BrokenClient:
        async def ping(self):
            raise ConnectionError("connection refused")

    try:
        asyncio.run(ping(_BrokenClient()))
    except InfrastructureError as e:
        assert e.code == "redis_unreachable"
    else:
        raise AssertionError("expected InfrastructureError")


def test_noeviction_check_returns_false_and_does_not_raise_when_config_get_unsupported():
    # fakeredis doesn't implement CONFIG GET — this is also the real-world
    # shape of a managed Redis tier with CONFIG disabled (09's own note).
    r = fakeredis_async.FakeRedis(decode_responses=True)
    assert asyncio.run(assert_noeviction_policy(r)) is False


def test_noeviction_check_true_when_policy_is_correct():
    class _FakeClient:
        async def config_get(self, name):
            return {"maxmemory-policy": "noeviction"}

    assert asyncio.run(assert_noeviction_policy(_FakeClient())) is True


def test_noeviction_check_false_when_policy_is_wrong():
    class _FakeClient:
        async def config_get(self, name):
            return {"maxmemory-policy": "allkeys-lru"}

    assert asyncio.run(assert_noeviction_policy(_FakeClient())) is False


if __name__ == "__main__":
    test_ping_true_on_a_live_connection()
    test_ping_raises_infrastructure_error_when_unreachable()
    test_noeviction_check_returns_false_and_does_not_raise_when_config_get_unsupported()
    test_noeviction_check_true_when_policy_is_correct()
    test_noeviction_check_false_when_policy_is_wrong()
    print("ok: Redis client ping + noeviction-policy assertion (09 §9.2)")
