"""Redis connection management (M2 Phase 1 "Redis Layer" scope; 09 §9).

`redis.asyncio.Redis.from_url()` connects lazily, same as motor (confirmed in
Phase 0 for Mongo; true of redis-py too) — constructing the client here does
not touch the network.
"""
from __future__ import annotations

import logging

import redis.asyncio as redis

from domain.errors import InfrastructureError

logger = logging.getLogger("alphascribe.redis")

# 09 §4.5/§9.5: sized for concurrent SSE readers (each blocking XREAD holds a
# connection for the block duration) + headroom for command traffic.
DEFAULT_MAX_CONNECTIONS = 100
DEFAULT_SOCKET_TIMEOUT_S = 20  # > the 15s XREAD block, so a normal block never trips it
DEFAULT_CONNECT_TIMEOUT_S = 3  # fail fast into the degradation path (09 §8)


def create_redis_client(redis_url: str, *, max_connections: int = DEFAULT_MAX_CONNECTIONS) -> redis.Redis:
    return redis.Redis.from_url(
        redis_url,
        decode_responses=True,
        max_connections=max_connections,
        socket_timeout=DEFAULT_SOCKET_TIMEOUT_S,
        socket_connect_timeout=DEFAULT_CONNECT_TIMEOUT_S,
    )


async def ping(client: redis.Redis) -> bool:
    try:
        return bool(await client.ping())
    except Exception as e:  # noqa: BLE001
        raise InfrastructureError(f"Redis ping failed: {e}", code="redis_unreachable") from e


async def assert_noeviction_policy(client: redis.Redis) -> bool:
    """09 §9.2 — the binding startup assertion. `maxmemory-policy` must be
    `noeviction`, or a managed Redis's default eviction policy could silently
    truncate a LIVE job's event stream under memory pressure — turning a
    running pipeline's SSE stream into one that just stops, with no error
    anywhere in the system (09 §9.2's own words).

    Logs ERROR and returns False rather than raising: this is a loud warning
    a deployment must not ignore, not a reason to refuse every request (that
    would be a self-inflicted outage over a config that is *usually* fine in
    dev — fail loud, not fail closed, for this one specific check).
    """
    try:
        cfg = await client.config_get("maxmemory-policy")
    except Exception as e:  # noqa: BLE001
        # CONFIG GET can be disabled on some managed Redis tiers; that's a
        # deployment fact to log, not a reason to crash startup either.
        logger.warning("could not read Redis maxmemory-policy (%s) — skipping the noeviction check", e)
        return False
    policy = cfg.get("maxmemory-policy") if cfg else None
    if policy != "noeviction":
        logger.error(
            "REDIS MISCONFIGURED: maxmemory-policy=%s (require noeviction, 09 §9.2) — "
            "a live job's SSE stream can be silently evicted under memory pressure",
            policy,
        )
        return False
    return True
