"""Authorization infrastructure (M2 Phase 1 "Authentication & Authorization"
scope; 10 §4.2/ADR-024). `agents/auth.py` is NOT moved here — 06 AD-10
schedules that physical move for Phase 6; this module holds only the NEW
authorization logic Phase 1 adds, and imports `agents.auth.is_admin`
(unchanged) rather than duplicating it.

Two things ship this phase:

  require_admin        — replaces the two duplicated inline
                          `if not auth.is_admin(user): raise HTTPException(403, ...)`
                          checks in server.py (POST /llm/validate,
                          POST /reports/generate's custom-provider gate) with
                          one function. Same condition, same status code,
                          same message — a cutover, not a behavior change
                          (verified in tests/unit/test_authorization.py and
                          by the full contract suite staying green).

  is_owned_or_shared    — the three-access-class predicate from 10 §4.2
                          (Owned / Shared / Admin), built and tested standalone
                          this phase.

M2 Phase (Company Research findings pass, post-Phase L): EQ-2's narrower
cutover (POST /reports/rescore: non-admin -> 403) landed via `require_admin`
here, as its own focused, reviewable change — exactly what this docstring
originally asked for, just not deferred to Phase 6's larger EQ-3 bundle
since EQ-2 touches one route, not 29.

M5 (Report-Read Authorization Cutover): EQ-3 landed too, as its own
dedicated milestone rather than folded into Phase 6's router split — the
same "focused, reviewable PR" reasoning EQ-2 already established, applied
to the larger cutover this docstring originally deferred. `cancel_report`,
`stream_report`, `get_report`, and `compare_reports` (server.py) are now
scoped to owner+sample; `list_reports`/`delete_report` already were.
`is_owned_or_shared` itself is still not the literal call site — each route
applies the same Owned/Shared rule as either a Mongo `$or` query predicate
(for `db.reports`-backed reads, matching `list_reports`' existing shape) or
a direct `Job.user_id` comparison (for `JobStore`-backed reads, which have
no query capability and no shared/sample concept), per this function's own
docstring note below. `is_owned_or_shared` remains available, tested, and
correct for the day a dict-shaped resource is fetched unscoped first and
checked after — none of M5's call sites needed that shape.
"""
from __future__ import annotations

from agents.auth import is_admin
from domain.errors import AuthorizationError
from infrastructure.observability.metrics import authz_denied_total

_ADMIN_ONLY_MESSAGE = "The Custom LLM provider is restricted to admin accounts."


def require_admin(user: dict, *, message: str = _ADMIN_ONLY_MESSAGE) -> None:
    """Raises AuthorizationError (-> 403 via app/api/errors.py's handler)
    unless `user` is an admin. Same condition as the two inline checks it
    replaces (`agents.auth.is_admin`); same status code (403); same default
    message, so the cutover changes zero observable behavior."""
    if not is_admin(user):
        authz_denied_total.labels(endpoint="admin_gate", **{"class": "admin"}).inc()
        raise AuthorizationError(message)


def is_owned_or_shared(resource: dict, user: dict, *, shared_flag: str = "is_sample") -> bool:
    """10 §4.2's Owned/Shared access class as a single predicate: the caller
    owns the resource, or it's explicitly marked shared (e.g. a curated
    sample report, `is_sample: true`). Mirrors the exact `$or` shape already
    used server-side for scoped Mongo queries (e.g. `list_reports`,
    `server.py:1046`) — same rule, reusable, not yet the query itself
    (that's the Phase 6 repository cutover, 10 §4.2's own scope note)."""
    return resource.get("user_id") == user.get("id") or bool(resource.get(shared_flag))
