"""Structured logging + correlation IDs (M2 Phase 1 "Logging & Observability"
scope). Fixes 04 O-1 ("no correlation identifier... a stack trace in the log
is unattributable with concurrent jobs") without changing server.py's
existing `logging.basicConfig` call site's behavior for anyone not yet
opted in — this module is additive: a contextvar + a logging.Filter that
injects it into every LogRecord, activated by attaching the filter to the
root logger (server.py's own change, kept minimal and reversible).

JSON formatting (04 O-3) is NOT built this phase — deferred deliberately;
see the Phase 1 report's Technical Debt section. Human-readable output stays
the default until a hosted deployment needs log aggregation to parse it; the
correlation id is the piece that matters for local/dev debugging today and
composes with either format later.
"""
from __future__ import annotations

import logging
from contextvars import ContextVar

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def set_correlation_id(value: str | None) -> None:
    _correlation_id.set(value)


def get_correlation_id() -> str | None:
    return _correlation_id.get()


class CorrelationIdFilter(logging.Filter):
    """Injects `%(correlation_id)s` into every LogRecord — "-" when unset, so
    existing format strings that don't reference it are unaffected, and ones
    that do (a new one this phase can add) never KeyError on a record
    produced before any job/request set the contextvar."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id() or "-"
        return True


def install_correlation_filter(logger: logging.Logger | None = None) -> CorrelationIdFilter:
    """Idempotent-ish: attaches one filter instance. Calling this twice on
    the same logger with two different CorrelationIdFilter instances would
    inject the field twice (harmless — both write the same value — but
    wasteful); callers should call this once, at startup, which is the only
    place server.py's own change does."""
    target = logger or logging.getLogger()
    f = CorrelationIdFilter()
    target.addFilter(f)
    return f
