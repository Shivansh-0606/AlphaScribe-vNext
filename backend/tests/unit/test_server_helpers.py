"""Unit check for security-relevant helpers in server.py that need no live
server or DB to exercise directly: the session-cookie policy
(_set_session_cookie), the pydantic `input`-stripping validation-error
handler (10 §6.1 T-14 — a rejected password must never echo back verbatim),
rescore_reports' admin gate (EQ-2, 02 §4.5 — no DB touch happens because
require_admin raises before any db.reports call), and cancel_report's
ownership gate (EQ-3, 01 D-5, M5 — the JobStore is in-memory by default, so
starting then cancelling a job touches no Mongo either).

`import server` is hermetic here (see tests/contract/conftest.py's docstring)
— constructing the app does not touch a real Mongo.

    python backend/tests/unit/test_server_helpers.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

from fastapi import HTTPException, Response  # noqa: E402
from fastapi.exceptions import RequestValidationError  # noqa: E402

from domain.errors import AuthorizationError  # noqa: E402
import server  # noqa: E402


def _cookie_header(remember: bool) -> str:
    response = Response()
    server._set_session_cookie(response, "test-token-value", remember=remember)
    return response.headers["set-cookie"]


def test_cookie_is_httponly_secure_samesite_lax():
    header = _cookie_header(remember=False)
    assert "httponly" in header.lower()
    assert "secure" in header.lower()
    assert "samesite=lax" in header.lower()
    assert "path=/" in header.lower()


def test_cookie_has_no_max_age_when_remember_is_false():
    # No Max-Age -> a session cookie, cleared when the browser closes.
    assert "max-age" not in _cookie_header(remember=False).lower()


def test_cookie_has_max_age_when_remember_is_true():
    header = _cookie_header(remember=True)
    assert "max-age" in header.lower()
    # SESSION_TTL_REMEMBER = 30 days = 2,592,000 seconds.
    import agents.auth as auth
    expected = str(int(auth.SESSION_TTL_REMEMBER.total_seconds()))
    assert expected in header


def test_validation_error_handler_strips_the_raw_input():
    rejected_password = "p4ssXyz9"
    exc = RequestValidationError([
        {"type": "string_too_short", "loc": ("body", "password"),
         "msg": "String should have at least 8 characters",
         "input": rejected_password, "ctx": {"min_length": 8}},
    ])
    response = asyncio.run(server._validation_error_handler(None, exc))
    assert response.status_code == 422
    body = response.body.decode()
    assert rejected_password not in body  # the rejected password itself
    assert '"input"' not in body          # the key that would have carried it
    assert "String should have at least 8 characters" in body  # message kept


def test_rescore_reports_rejects_a_non_admin_before_touching_the_db():
    # Calls the route function directly (no TestClient/lifespan, no Mongo
    # connection needed): require_admin raises before rescore_reports' first
    # db.reports.find() call, so this stays hermetic despite exercising the
    # real route handler, not just infrastructure/security/authorization.py's
    # require_admin in isolation (already covered by test_authorization.py).
    try:
        asyncio.run(server.rescore_reports(user={"email": "nobody@example.com"}))
    except AuthorizationError as e:
        assert e.status_code == 403
        assert e.message == "This action is restricted to admin accounts."
    else:
        raise AssertionError("expected AuthorizationError for a non-admin user")


def test_cancel_report_denies_a_non_owner_before_any_mongo_write():
    # container.job_lifecycle.start() only touches the in-memory JobStore
    # (JOB_BACKEND=memory, the hermetic default) — no Mongo needed to prove
    # the ownership check (M5) fires before cancel_report's first db.jobs
    # write, mirroring the rescore test's same "hermetic despite calling the
    # real route" shape above.
    job_id = f"hermetic-eq3-{id(object())}"
    asyncio.run(server.container.job_lifecycle.start(
        job_id, server.JobKind.RESEARCH, "owner-user-id", ticker="TEST",
    ))
    try:
        asyncio.run(server.cancel_report(job_id, user={"id": "someone-else-id"}))
    except HTTPException as e:
        assert e.status_code == 404
    else:
        raise AssertionError("expected HTTPException(404) for a non-owner")


if __name__ == "__main__":
    test_cookie_is_httponly_secure_samesite_lax()
    test_cookie_has_no_max_age_when_remember_is_false()
    test_cookie_has_max_age_when_remember_is_true()
    test_validation_error_handler_strips_the_raw_input()
    test_rescore_reports_rejects_a_non_admin_before_touching_the_db()
    test_cancel_report_denies_a_non_owner_before_any_mongo_write()
    print("ok: cookie policy (HttpOnly/Secure/SameSite/Max-Age); 422 handler strips raw input app-wide; "
          "rescore admin gate (EQ-2); cancel_report ownership gate (EQ-3)")
