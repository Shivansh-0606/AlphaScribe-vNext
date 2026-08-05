"""Unit check for the pure/local-state pieces of agents/auth.py: scrypt
hash/verify, the OTP pepper, and the sliding-window rate limiter's pruning
(05 §3.2 — the DoS guard described in auth.py:52-56 had no test). No DB: the
db-touching functions (create_user, authenticate, sessions, ...) are covered
by the existing live suite (test_auth.py et al.) and are out of scope here.

    python backend/tests/unit/test_auth_pure.py
"""
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import agents.auth as auth
from agents.auth import _hash_otp, clear_hits, hash_password, is_rate_limited, record_hit, verify_password


def test_hash_password_roundtrip_and_wrong_password_fails():
    salt_hex, hash_hex = hash_password("correct-horse-battery")
    assert verify_password("correct-horse-battery", salt_hex, hash_hex)
    assert not verify_password("wrong-password", salt_hex, hash_hex)


def test_hash_password_salts_are_unique_per_call():
    salt1, _ = hash_password("same-password")
    salt2, _ = hash_password("same-password")
    assert salt1 != salt2  # secrets.token_bytes(16) per call, not a fixed salt


def test_otp_hash_is_deterministic_for_the_same_pepper():
    assert _hash_otp("123456") == _hash_otp("123456")
    assert _hash_otp("123456") != _hash_otp("654321")


def test_otp_hash_changes_if_the_pepper_changes():
    # 10 §7.2 SD-3: the pepper defaults to a value committed to this repo
    # ("dev-insecure-otp-pepper") when OTP_PEPPER is unset. This test doesn't
    # assert that default is safe (it isn't — that's exactly SD-3's point);
    # it asserts the pepper is actually load-bearing, which is the property
    # SD-3's production startup gate depends on.
    before = _hash_otp("123456")
    real = os.environ.get("OTP_PEPPER")
    os.environ["OTP_PEPPER"] = "a-different-pepper-for-this-test"
    try:
        after = _hash_otp("123456")
    finally:
        if real is None:
            os.environ.pop("OTP_PEPPER", None)
        else:
            os.environ["OTP_PEPPER"] = real
    assert before != after


def test_rate_limit_allows_four_hits_then_blocks_on_the_fifth():
    key = f"test:{uuid.uuid4()}"
    try:
        for _ in range(4):
            assert not is_rate_limited(key)
            record_hit(key)
        assert not is_rate_limited(key)  # still only 4 recorded -> not limited yet
        record_hit(key)                 # 5th hit reaches _RATE_LIMIT_MAX
        assert is_rate_limited(key)
    finally:
        clear_hits(key)


def test_rate_limit_window_prunes_stale_hits():
    # Directly seed hits older than the 15-minute window (auth.py:47) rather
    # than waiting real time — deterministic, no sleep, no clock mocking.
    key = f"test:{uuid.uuid4()}"
    stale = datetime.now(timezone.utc) - timedelta(minutes=20)
    auth._hits[key] = [stale] * 5
    try:
        assert not is_rate_limited(key), "hits outside the window must not count"
        # Pruning to empty must also drop the dict entry (auth.py:52-56 —
        # the unbounded-memory-DoS guard), not leave an empty list behind.
        assert key not in auth._hits
    finally:
        clear_hits(key)


def test_rate_limit_never_creates_an_entry_for_an_unseen_key():
    key = f"test:{uuid.uuid4()}"
    assert not is_rate_limited(key)
    assert key not in auth._hits


def test_clear_hits_is_a_no_op_on_an_unknown_key():
    clear_hits(f"test:{uuid.uuid4()}")  # must not raise


if __name__ == "__main__":
    test_hash_password_roundtrip_and_wrong_password_fails()
    test_hash_password_salts_are_unique_per_call()
    test_otp_hash_is_deterministic_for_the_same_pepper()
    test_otp_hash_changes_if_the_pepper_changes()
    test_rate_limit_allows_four_hits_then_blocks_on_the_fifth()
    test_rate_limit_window_prunes_stale_hits()
    test_rate_limit_never_creates_an_entry_for_an_unseen_key()
    test_clear_hits_is_a_no_op_on_an_unknown_key()
    print("ok: scrypt hash/verify, OTP pepper is load-bearing, sliding-window rate limiter incl. pruning/no-leak")
