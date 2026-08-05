"""Unified error hierarchy (M2 Phase 1 "Error Handling" scope).

Every layer above domain/ catches infrastructure-specific exceptions
(pymongo.errors.*, redis.exceptions.*, httpx.*, openai.*, anthropic.*) at the
boundary and re-raises one of these instead — so `app/api/errors.py`'s single
handler (registered additively in server.py) can map any of them to a
consistent JSON error shape without knowing which driver failed.

Deliberately flat (one file, one hierarchy) rather than a package: there are
nine concrete error kinds today, each a one-line dataclass-shaped exception.
Split it when a kind needs its own logic, not before (YAGNI).

Pure — stdlib only. No pydantic, no driver imports, per 06 AD-6 (domain
imports stdlib + pydantic only; this file doesn't even need pydantic).
"""
from __future__ import annotations


class DomainError(Exception):
    """Base for every error the application layer is allowed to raise across
    a port boundary. Carries an HTTP-shaped `status_code` and a machine-
    readable `code` so `app/api/errors.py` needs no isinstance() chain beyond
    this base class for the common case."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code


class NotFoundError(DomainError):
    """A requested resource does not exist (or — per 10 §4.2's Owned access
    class — exists but the caller isn't its owner; those are intentionally
    indistinguishable at this layer, matching EQ-3's target 404 behavior)."""

    status_code = 404
    code = "not_found"


class ValidationError(DomainError):
    """A domain-level invariant was violated — distinct from Pydantic's
    request-shape validation (already handled at the API boundary before a
    use case ever runs); this is for invariants only the domain knows about."""

    status_code = 422
    code = "validation_error"


class ConflictError(DomainError):
    """The operation conflicts with existing state (e.g. a duplicate email —
    mirrors the existing 409 on POST /auth/register)."""

    status_code = 409
    code = "conflict"


class AuthorizationError(DomainError):
    """Authenticated, but not permitted — the Admin access class in
    10 §4.2/ADR-024. Distinct from authentication failure, which stays a
    401 raised directly by the `current_user` dependency (unchanged)."""

    status_code = 403
    code = "forbidden"


class RateLimitedError(DomainError):
    """A rate limit was hit — mirrors the existing 429s on /auth/login,
    /auth/forgot-password, /auth/reset-password, and MAX_ACTIVE_JOBS."""

    status_code = 429
    code = "rate_limited"


class DeadlineExceededError(DomainError):
    """A job exceeded its wall-clock budget (07 §5.4, ADR-011). Maps to the
    same `pipeline/warn` → UI `cancelled` stage a real cancellation does —
    this exception is how a node signals it, not how the client is told."""

    status_code = 504
    code = "deadline_exceeded"


class InfrastructureError(DomainError):
    """Wraps a failure from a concrete adapter (Mongo, Redis, an LLM
    provider, an external HTTP fetch) that the caller cannot recover from.
    Adapters catch their driver's own exception type and re-raise this with
    the original preserved as `__cause__` — never re-raise the driver
    exception directly across a port boundary, or callers above the port
    would need to know which driver is behind it."""

    status_code = 502
    code = "infrastructure_error"


class LLMProviderError(InfrastructureError):
    """An LLM provider call failed. Kept distinct from a generic
    InfrastructureError because the API boundary's message MUST NEVER echo
    the raw provider exception text — Gemini embeds the API key as a
    `?key=...` URL param (agents/llm.py's existing redact_key_from_error,
    10 T-13). `app/api/errors.py` special-cases this type to always return a
    fixed, safe message regardless of what `message` holds."""

    status_code = 502
    code = "llm_provider_error"


class StreamingError(DomainError):
    """A failure inside an active SSE stream, after headers are already
    sent — cannot become an HTTP error response (10 §6, the stream is
    already 200 OK). infrastructure/streaming/sse.py catches this and emits
    a `{node:"pipeline", status:"error"}` trace event instead of raising."""

    status_code = 500  # meaningless once the stream has started; kept for API symmetry
    code = "streaming_error"
