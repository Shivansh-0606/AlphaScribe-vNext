"""ensure_indexes — the full 25-index set from
docs/backend_engineering/08_MongoDB_Data_Architecture.md §5.1.

Supersedes agents/auth.py's ensure_indexes (which only covers I-1/I-3/I-4/
I-6/I-7 — the 5 auth-collection indexes that existed before this phase).
This module is the complete set across every collection; server.py's startup
hook is updated to call THIS function instead (server.py's own change is
additive-only — see the "Additive server.py integration" section of the
Phase 1 report).

Every index name is prefixed with its 08 §5.1 row id (I-2, I-9, ...) so a
slow-query log or `explain()` output is traceable straight back to the
architecture doc that specified it.

`create_index` is idempotent for a NEW index (08 DA-8) — but running this for
real against this repo's actual dev database (Phase 1's Test Report) surfaced
a real edge case DA-8 didn't anticipate: the 5 indexes agents/auth.py's
*existing* `ensure_indexes()` already created (I-1/I-3/I-4/I-6/I-7) were
created WITHOUT an explicit name, so MongoDB auto-named them (`email_1`,
`token_hash_1`, ...). Asking to create the *same key spec* under a *different*
explicit name raises `OperationFailure` code 85 (`IndexOptionsConflict`) — the
key spec already satisfies the index; only the label differs. `_idx()` below
treats that specific, narrow case as success (the index exists and does its
job; the human-readable name is a nice-to-have this repo's pre-existing
indexes predate) rather than a startup failure — anything else still raises.

New collections (explanations, explanation_jobs — 08 §4.7/§4.6) are NOT
created here as documents; `create_index` on a not-yet-existing collection
creates the collection implicitly, which is intentional and harmless (Mongo
does this for any first write too).
"""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import OperationFailure

_INDEX_OPTIONS_CONFLICT = 85


async def ensure_indexes(db: AsyncIOMotorDatabase) -> dict[str, list[str]]:
    """Idempotently create every index in the 08 §5.1 set. Returns
    {collection: [index_names_created_or_confirmed]} for startup logging."""
    created: dict[str, list[str]] = {}

    async def _idx(collection: str, keys, **kwargs) -> None:
        try:
            name = await db[collection].create_index(keys, **kwargs)
        except OperationFailure as e:
            if e.code != _INDEX_OPTIONS_CONFLICT:
                raise
            # Same key spec already indexed under a different (usually
            # auto-generated, pre-08-§5.1) name — functionally satisfied.
            name = f"{kwargs.get('name', '?')} (pre-existing under a different name)"
        created.setdefault(collection, []).append(name)

    # --- users --------------------------------------------------------
    await _idx("users", "email", unique=True, name="I-1_email_unique")
    await _idx("users", "id", unique=True, name="I-2_id_unique")

    # --- sessions -------------------------------------------------------
    await _idx("sessions", "token_hash", unique=True, name="I-3_token_hash_unique")
    await _idx("sessions", "expires_at", expireAfterSeconds=0, name="I-4_expires_at_ttl")
    await _idx("sessions", "user_id", name="I-5_user_id")

    # --- password_resets --------------------------------------------------
    await _idx("password_resets", "email", name="I-6_email")
    await _idx("password_resets", "expires_at", expireAfterSeconds=0, name="I-7_expires_at_ttl")
    await _idx(
        "password_resets",
        [("email", 1), ("used", 1), ("created_at", -1)],
        name="I-8_email_used_created",
    )

    # --- companies (shared corpus) -----------------------------------------
    await _idx("companies", "ticker", unique=True, name="I-9_ticker_unique")

    # --- filings ----------------------------------------------------------
    await _idx("filings", [("ticker", 1), ("created_at", -1)], name="I-10_ticker_created")
    await _idx("filings", [("ticker", 1), ("source", 1)], name="I-11_ticker_source")

    # --- filing_chunks (the hot path — 08 §1's headline finding) -----------
    await _idx("filing_chunks", [("ticker", 1), ("created_at", -1)], name="I-12_ticker_created")
    await _idx("filing_chunks", "doc_id", name="I-13_doc_id")

    # --- reports ------------------------------------------------------------
    await _idx("reports", "id", unique=True, name="I-14_id_unique")
    await _idx("reports", [("user_id", 1), ("created_at", -1)], name="I-15_user_created")
    await _idx(
        "reports", [("is_sample", 1), ("created_at", -1)],
        name="I-16_is_sample_created", sparse=True,
    )
    await _idx(
        "reports", [("ticker", 1), ("query", 1), ("created_at", -1)],
        name="I-17_ticker_query_created",
    )

    # --- jobs -----------------------------------------------------------
    await _idx("jobs", "id", unique=True, name="I-18_id_unique")
    await _idx("jobs", [("status", 1), ("created_at", -1)], name="I-19_status_created")
    await _idx("jobs", "created_at", expireAfterSeconds=30 * 24 * 3600, name="I-20_created_at_ttl_30d")

    # --- explanations (M2 Phase 1 — infra only; the collection itself is
    # populated by the Learning feature, not built in this phase) -----------
    await _idx("explanations", "id", unique=True, name="I-21_id_unique")
    await _idx("explanations", [("user_id", 1), ("created_at", -1)], name="I-22_user_created")

    # --- explanation_jobs ----------------------------------------------------
    await _idx("explanation_jobs", "id", unique=True, name="I-23_id_unique")
    await _idx("explanation_jobs", [("status", 1), ("created_at", -1)], name="I-24_status_created")
    await _idx(
        "explanation_jobs", "created_at",
        expireAfterSeconds=30 * 24 * 3600, name="I-25_created_at_ttl_30d",
    )

    return created
