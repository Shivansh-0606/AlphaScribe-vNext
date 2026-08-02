"""Unit check for validate_key/redact_key_from_error in agents/llm.py.

validate_key must reject an empty key and an unknown provider without ever
calling a provider, must call the right provider function with the resolved
model/base_url on success, and must propagate a provider failure so the
caller (server.py's /llm/validate) can redact and report it. No network:
the provider-calling functions are stubbed with a call recorder.
redact_key_from_error must never let the raw key — or a Gemini-style
`?key=...` URL param — survive into the returned string.

    python backend/tests/test_llm_validate.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agents.llm as llm


def test_redact_key_from_error_strips_literal_key_and_url_param():
    key = "sk-supersecret123"
    err = Exception(f"request to https://api.example.com/v1?key={key}&x=1 failed: {key}")
    redacted = llm.redact_key_from_error(err, key)
    assert key not in redacted
    assert "***REDACTED***" in redacted


def test_validate_key_rejects_empty_key():
    try:
        asyncio.run(llm.validate_key("gemini", "   "))
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for an empty key")


def test_validate_key_rejects_unknown_provider():
    try:
        asyncio.run(llm.validate_key("not-a-real-provider", "some-key"))
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for an unknown provider")


def test_validate_key_success_calls_the_resolved_provider_fn():
    calls = []

    def stub(system, user, model, key, base_url):
        calls.append({"model": model, "key": key, "base_url": base_url})
        return "OK"

    real = llm._gen_openai_compatible
    llm._gen_openai_compatible = stub
    try:
        asyncio.run(llm.validate_key("groq", "gsk-test"))
    finally:
        llm._gen_openai_compatible = real

    assert len(calls) == 1, f"expected exactly one provider call, got {len(calls)}"
    assert calls[0]["key"] == "gsk-test"
    assert calls[0]["model"] == llm.PROVIDER_DEFAULTS["groq"][0]  # light model default
    assert calls[0]["base_url"] == llm.PROVIDER_BASE_URL["groq"]  # built-in base URL


def test_validate_key_propagates_provider_failure():
    def boom(*a, **k):
        raise RuntimeError("invalid_api_key")

    real = llm._gen_gemini
    llm._gen_gemini = boom
    try:
        try:
            asyncio.run(llm.validate_key("gemini", "bad-key"))
        except RuntimeError:
            pass
        else:
            raise AssertionError("expected the provider failure to propagate")
    finally:
        llm._gen_gemini = real


if __name__ == "__main__":
    test_redact_key_from_error_strips_literal_key_and_url_param()
    test_validate_key_rejects_empty_key()
    test_validate_key_rejects_unknown_provider()
    test_validate_key_success_calls_the_resolved_provider_fn()
    test_validate_key_propagates_provider_failure()
    print("ok: validate_key rejects bad input, calls the right provider, propagates failure; redaction strips the key")
