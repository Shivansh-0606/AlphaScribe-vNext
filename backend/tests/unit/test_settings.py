"""Unit check for app/settings.py — 06 AD-9, resolving 10 SD-2/SD-3.

No DB, no network: Settings only reads os.environ. Each test sets exactly the
env vars it needs and restores the environment afterward so tests don't leak
into each other or into later test files in the same worker (the class of bug
found in M2 Phase 0, docs/backend_engineering/13 §1.5).

    python backend/tests/unit/test_settings.py
"""
import contextlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.settings import Environment, load_settings

_SETTINGS_KEYS = [
    "MONGO_URL", "DB_NAME", "REDIS_URL", "CORS_ORIGINS", "OTP_PEPPER",
    "RESEND_API_KEY", "ADMIN_EMAILS", "MAX_ACTIVE_JOBS",
    "JOB_DEADLINE_RESEARCH_S", "JOB_DEADLINE_LEARNING_S",
    "JOB_DEADLINE_GRACE_S", "MAX_JOB_LIFETIME_S", "LLM_PROVIDER",
    "LLM_ALLOW_PRIVATE_BASE_URL", "LOG_LEVEL", "OTEL_EXPORTER_OTLP_ENDPOINT",
    "PROMETHEUS_ENABLED", "ENVIRONMENT",
]


@contextlib.contextmanager
def _clean_env(**kv):
    """Clears every Settings-relevant env var, sets exactly `kv`, then
    restores the original environment on exit — so a developer's real
    backend/.env (loaded once at process start by server.py) never leaks
    into, or gets clobbered by, these tests. Snapshot-and-clear happens
    BEFORE any value is set (unlike a chained `.set()` builder, which would
    set values first and then wipe them — the ordering bug this was written
    to avoid)."""
    saved = {k: os.environ.get(k) for k in _SETTINGS_KEYS}
    for k in _SETTINGS_KEYS:
        os.environ.pop(k, None)
    os.environ.update(kv)
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_required_fields_must_be_set():
    with _clean_env():
        try:
            load_settings()
        except Exception:
            pass
        else:
            raise AssertionError("MONGO_URL/DB_NAME are required; expected a validation error")


def test_defaults_apply_when_optional_fields_are_unset():
    with _clean_env(MONGO_URL="mongodb://x", DB_NAME="x"):
        s = load_settings()
        assert s.environment is Environment.DEVELOPMENT
        assert s.max_active_jobs == 8
        assert s.otp_pepper == "dev-insecure-otp-pepper"
        assert s.cors_origin_list == ["http://localhost:3001"]


def test_job_deadline_dict_matches_07_5_4():
    with _clean_env(MONGO_URL="mongodb://x", DB_NAME="x"):
        s = load_settings()
        assert s.job_deadline_s == {
            "research": 300.0, "learning": 120.0, "comparison_explanation": 60.0,
            "filing_analysis": 180.0,  # M14 — additive (Document 65 §11/§19; operational, retunable)
        }
        # 09 §6.2 / 07 LR-9's binding invariant: the reaper window must
        # exceed the longest job deadline plus grace, or the reaper could
        # free the slot of a still-running job.
        assert s.max_job_lifetime_s > max(s.job_deadline_s.values()) + s.job_deadline_grace_s


def test_admin_email_set_parses_and_lowercases():
    with _clean_env(MONGO_URL="mongodb://x", DB_NAME="x",
                    ADMIN_EMAILS="Admin@Example.com, second@x.com"):
        s = load_settings()
        assert s.admin_email_set == {"admin@example.com", "second@x.com"}


def test_cors_wildcard_is_rejected():
    with _clean_env(MONGO_URL="mongodb://x", DB_NAME="x", CORS_ORIGINS="*"):
        try:
            load_settings()
        except Exception as e:
            assert "SD-2" in str(e) or "explicit origin list" in str(e)
        else:
            raise AssertionError("wildcard CORS_ORIGINS must be rejected (10 SD-2)")


def test_production_requires_a_real_otp_pepper_and_resend_key():
    with _clean_env(MONGO_URL="mongodb://x", DB_NAME="x", ENVIRONMENT="production"):
        try:
            load_settings()
        except Exception as e:
            msg = str(e)
            assert "OTP_PEPPER" in msg
            assert "RESEND_API_KEY" in msg
        else:
            raise AssertionError("production with insecure defaults must fail startup (10 SD-3)")


def test_production_with_secure_config_succeeds():
    with _clean_env(MONGO_URL="mongodb://x", DB_NAME="x", ENVIRONMENT="production",
                    OTP_PEPPER="a-real-random-pepper", RESEND_API_KEY="re_live_x"):
        s = load_settings()
        assert s.environment is Environment.PRODUCTION


def test_development_ignores_the_production_gate():
    with _clean_env(MONGO_URL="mongodb://x", DB_NAME="x"):
        # Uses the insecure default pepper, no RESEND_API_KEY — must NOT raise
        # outside production (this is exactly local dev's normal shape).
        s = load_settings()
        assert s.environment is Environment.DEVELOPMENT


if __name__ == "__main__":
    test_required_fields_must_be_set()
    test_defaults_apply_when_optional_fields_are_unset()
    test_job_deadline_dict_matches_07_5_4()
    test_admin_email_set_parses_and_lowercases()
    test_cors_wildcard_is_rejected()
    test_production_requires_a_real_otp_pepper_and_resend_key()
    test_production_with_secure_config_succeeds()
    test_development_ignores_the_production_gate()
    print("ok: Settings — required fields, defaults, job-deadline invariant, CORS gate, production SD-3 gate")
