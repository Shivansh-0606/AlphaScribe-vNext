"""Unit check for infrastructure/security/authorization.py (10 §4.2/ADR-024).

No DB, no server: `is_admin` reads only ADMIN_EMAILS from the environment
(agents/auth.py, unchanged).

    python backend/tests/unit/test_authorization.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from domain.errors import AuthorizationError
from infrastructure.security.authorization import is_owned_or_shared, require_admin


def _with_admin_emails(value: str):
    real = os.environ.get("ADMIN_EMAILS")
    os.environ["ADMIN_EMAILS"] = value
    return real


def _restore_admin_emails(real: str | None) -> None:
    if real is None:
        os.environ.pop("ADMIN_EMAILS", None)
    else:
        os.environ["ADMIN_EMAILS"] = real


def test_require_admin_allows_an_admin_user():
    real = _with_admin_emails("admin@example.com")
    try:
        require_admin({"email": "admin@example.com"})  # must not raise
    finally:
        _restore_admin_emails(real)


def test_require_admin_raises_authorization_error_for_a_non_admin():
    real = _with_admin_emails("admin@example.com")
    try:
        try:
            require_admin({"email": "someone-else@example.com"})
        except AuthorizationError as e:
            assert e.status_code == 403
            assert e.code == "forbidden"
        else:
            raise AssertionError("expected AuthorizationError for a non-admin user")
    finally:
        _restore_admin_emails(real)


def test_require_admin_default_message_matches_the_existing_inline_checks():
    # The two server.py call sites being replaced both use this exact
    # message (server.py:822, :852) — the cutover must not change it.
    real = _with_admin_emails("")
    try:
        try:
            require_admin({"email": "x@example.com"})
        except AuthorizationError as e:
            assert e.message == "The Custom LLM provider is restricted to admin accounts."
    finally:
        _restore_admin_emails(real)


def test_is_owned_or_shared_true_for_the_owner():
    assert is_owned_or_shared({"user_id": "u1"}, {"id": "u1"}) is True


def test_is_owned_or_shared_true_for_a_shared_sample():
    assert is_owned_or_shared({"user_id": None, "is_sample": True}, {"id": "u1"}) is True


def test_is_owned_or_shared_false_for_a_stranger():
    assert is_owned_or_shared({"user_id": "u2"}, {"id": "u1"}) is False


if __name__ == "__main__":
    test_require_admin_allows_an_admin_user()
    test_require_admin_raises_authorization_error_for_a_non_admin()
    test_require_admin_default_message_matches_the_existing_inline_checks()
    test_is_owned_or_shared_true_for_the_owner()
    test_is_owned_or_shared_true_for_a_shared_sample()
    test_is_owned_or_shared_false_for_a_stranger()
    print("ok: require_admin (matches the inline checks it replaces), is_owned_or_shared (10 §4.2 access class)")
