"""Unified error handling (M2 Phase 1 "Error Handling" scope). One handler
maps every domain.errors.DomainError subclass to a consistent JSON shape —
`{"detail": "<message>", "type": "<code>"}` — instead of each new use case
hand-rolling its own HTTPException.

Registered ADDITIVELY in server.py alongside the existing
`RequestValidationError` handler (server.py:1157-1165, unchanged, still
strips pydantic's `input` field — 10 T-14). Nothing in the 31 existing routes
currently raises a DomainError, so registering this handler changes no
existing response for any of them; it is pure new capability for new code
(starting with infrastructure/security/authorization.py's `require_admin`).

LLMProviderError gets its own branch: the message on that exception type must
NEVER reach a client verbatim — provider SDK exceptions can embed the raw API
key (Gemini's `?key=...` URL param, 10 T-13) — so this handler always
substitutes a fixed, safe string for it, mirroring server.py's own existing
pipeline-error handling (`server.py:779-795`) rather than trusting every
future LLMProviderError raiser to redact correctly.
"""
from __future__ import annotations

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from domain.errors import DomainError, LLMProviderError

logger = logging.getLogger("alphascribe")


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    if isinstance(exc, LLMProviderError):
        logger.exception("LLM provider error", exc_info=exc)
        message = "The AI provider request failed. See server logs for details."
    else:
        message = exc.message
    return JSONResponse(status_code=exc.status_code, content={"detail": message, "type": exc.code})
