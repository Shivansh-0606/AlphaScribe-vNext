"""Unit check for security-relevant helpers in server.py that need no live
server or DB to exercise directly: the session-cookie policy
(_set_session_cookie), the pydantic `input`-stripping validation-error
handler (10 §6.1 T-14 — a rejected password must never echo back verbatim),
cancel_report's ownership gate (EQ-3, 01 D-5, M5 — the JobStore is in-memory by default, so
starting then cancelling a job touches no Mongo either), and
_track_background_task — the fire-and-forget task-lifetime fix (a task with
no retained reference can be garbage-collected before completion, a
documented asyncio footgun; unrelated to and not a substitute for AS-3's
process-crash trade-off, which concerns durable *state*, not in-memory task
references) — verified at its two call sites (/auth/forgot-password's OTP
email, ensure_company's M8 acquisition scheduling) and directly.

`import server` is hermetic here (see tests/contract/conftest.py's docstring)
— constructing the app does not touch a real Mongo.

    python backend/tests/unit/test_server_helpers.py
"""
import asyncio
import dataclasses
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

from fastapi import HTTPException, Response  # noqa: E402
from fastapi.exceptions import RequestValidationError  # noqa: E402

from agents import company_index  # noqa: E402
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


def test_cancel_report_denies_a_non_owner_before_any_mongo_write():
    # container.job_lifecycle.start() only touches the in-memory JobStore
    # (JOB_BACKEND=memory, the hermetic default) — no Mongo needed to prove
    # the ownership check (M5) fires before cancel_report's first db.jobs
    # write, staying hermetic despite calling the real route handler, not
    # just a mocked one.
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


def test_track_background_task_retains_while_pending_and_discards_when_done():
    # Controllable via asyncio.Event, not a timing sleep — the task only
    # completes when this test says so, so "pending" and "done" are both
    # observed deterministically, not guessed at with a delay.
    async def _body():
        event = asyncio.Event()

        async def _pending():
            await event.wait()

        task = server._track_background_task(asyncio.create_task(_pending()))
        assert task in server._BACKGROUND_TASKS  # A: retained while pending

        event.set()
        await task
        assert task not in server._BACKGROUND_TASKS  # B: removed once done

    asyncio.run(_body())


class _FakeUsersCollection:
    def __init__(self, email: str):
        self._email = email

    async def find_one(self, query):
        return {"id": "u1", "email": self._email}


class _FakeDB:
    """Swaps out server.db's whole surface for forgot_password's own needs
    — safer than monkeypatching Motor collection methods, whose accessors
    (db.users) aren't guaranteed to be stable, reassignable attributes
    (AsyncIOMotorDatabase resolves them dynamically)."""

    def __init__(self, email: str):
        self.users = _FakeUsersCollection(email)


def test_forgot_password_otp_task_is_retained():
    # D: the existing OTP fire-and-forget call site now goes through the
    # same registry. server.db, auth.create_password_reset, and
    # notify.send_otp_email are all stubbed so this stays fully hermetic —
    # only the task-tracking wiring at the OTP call site is under test.
    email = f"otp-track-{id(object())}@example.com"

    original_db = server.db
    original_create_reset = server.auth.create_password_reset
    original_send_otp = server.notify.send_otp_email
    server.db = _FakeDB(email)

    async def _fake_create_password_reset(db, e):
        return "000000"

    async def _fake_send_otp_email(to, otp):
        pass

    server.auth.create_password_reset = _fake_create_password_reset
    server.notify.send_otp_email = _fake_send_otp_email

    async def _body():
        before = set(server._BACKGROUND_TASKS)
        resp = await server.forgot_password(server.ForgotPasswordRequest(email=email))
        assert resp == {"ok": True}
        new_tasks = server._BACKGROUND_TASKS - before
        assert len(new_tasks) == 1  # A, applied to the OTP site specifically
        task = next(iter(new_tasks))
        await task
        assert task not in server._BACKGROUND_TASKS  # B, applied to the OTP site specifically

    try:
        asyncio.run(_body())
    finally:
        server.db = original_db
        server.auth.create_password_reset = original_create_reset
        server.notify.send_otp_email = original_send_otp


def test_ensure_company_retains_the_financials_orchestrator_tasks():
    # C: proves the actual production call site — ensure_company — routes
    # schedule()'s returned tasks through the same registry, without
    # reaching any real Mongo/EDGAR/BSE/yfinance call. lookup_exchange is
    # monkeypatched to raise a sentinel immediately after the tracking
    # loop (the next line in ensure_company after it), which is what keeps
    # this hermetic — schedule() itself is never given a chance to run for
    # real either, since it's replaced by a controllable fake.
    class _StopHere(Exception):
        pass

    class _FakeOrchestrator:
        def schedule(self, ticker, *, trigger):
            async def _pending():
                await asyncio.Event().wait()  # never completes within this test

            return [asyncio.create_task(_pending()) for _ in range(2)]

    original_container = server.container
    original_lookup = company_index.lookup_exchange
    server.container = dataclasses.replace(original_container, financials_orchestrator=_FakeOrchestrator())

    def _raise(*a, **kw):
        raise _StopHere()

    company_index.lookup_exchange = _raise

    async def _body():
        before = set(server._BACKGROUND_TASKS)
        try:
            await server.ensure_company(server.EnsureRequest(ticker="AAPL"), user={"id": "u1"})
        except _StopHere:
            pass
        else:
            raise AssertionError("expected the sentinel to fire before any Mongo/network call")
        new_tasks = server._BACKGROUND_TASKS - before
        assert len(new_tasks) == 2
        for t in new_tasks:
            t.cancel()
        await asyncio.gather(*new_tasks, return_exceptions=True)  # let cancellation finish, not a timing wait

    try:
        asyncio.run(_body())
    finally:
        server.container = original_container
        company_index.lookup_exchange = original_lookup


if __name__ == "__main__":
    test_cookie_is_httponly_secure_samesite_lax()
    test_cookie_has_no_max_age_when_remember_is_false()
    test_cookie_has_max_age_when_remember_is_true()
    test_validation_error_handler_strips_the_raw_input()
    test_cancel_report_denies_a_non_owner_before_any_mongo_write()
    test_track_background_task_retains_while_pending_and_discards_when_done()
    test_forgot_password_otp_task_is_retained()
    test_ensure_company_retains_the_financials_orchestrator_tasks()
    print("ok: cookie policy (HttpOnly/Secure/SameSite/Max-Age); 422 handler strips raw input app-wide; "
          "cancel_report ownership gate (EQ-3); background-task retention "
          "(generic, OTP site, M8 ensure_company site)")
