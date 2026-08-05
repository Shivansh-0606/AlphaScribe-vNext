"""MongoDB connection lifecycle (M2 Phase 1 "Database Layer" scope; 08 §8).

Deliberately thin: `motor`/`pymongo` clients connect lazily (confirmed
empirically in Phase 0 — `import server` never touches the network), so
"connection lifecycle" here means constructing the client once and closing it
once, not managing a pool by hand. The real work is `ping()` (a true
liveness/readiness check, unlike `server.py`'s existing `/health`, which
counts documents — 04 O-12) and `ensure_indexes()` (08 §5 — the 25-index set;
the single highest-value fix identified in the whole architecture set, per
08 §1's headline finding: "the database has five indexes, all on auth
collections").
"""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from domain.errors import InfrastructureError


def create_mongo_client(mongo_url: str) -> AsyncIOMotorClient:
    """One call site for client construction (mirrors app/settings.py's
    load_settings() — one place a future connection-pool/TLS option gets
    added, not scattered across every module that needs `db`)."""
    return AsyncIOMotorClient(mongo_url)


async def ping(db: AsyncIOMotorDatabase) -> bool:
    """True liveness check — `{"ping": 1}` is a metadata round-trip, not a
    collection scan (unlike the existing /health's count_documents calls,
    04 O-12). Raises InfrastructureError instead of letting a raw
    pymongo/motor exception cross the port boundary (domain/errors.py)."""
    try:
        await db.command("ping")
        return True
    except Exception as e:  # noqa: BLE001 — any driver failure means "not live"
        raise InfrastructureError(f"MongoDB ping failed: {e}", code="mongo_unreachable") from e
