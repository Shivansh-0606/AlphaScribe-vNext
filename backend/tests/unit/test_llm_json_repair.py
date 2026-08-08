"""Unit check for agents/llm.py's chat_json JSON-repair ladder — flagged in
05 §3.2 as the highest-complexity code in the backend with zero direct tests:
every structured LLM output in the product passes through it, and each
fallback branch exists because a real model produced that exact malformation.

Also covers _strip_code_fence, _retry_after_seconds, and _schema_hint (05
§3.2). No network: _generate_sync is stubbed to return a fixed raw string,
exactly like test_llm_retry.py / test_llm_validate.py.

    python backend/tests/unit/test_llm_json_repair.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pydantic import BaseModel, Field, ValidationError

import agents.llm as llm
from agents.llm import _retry_after_seconds, _schema_hint, _strip_code_fence, chat_json


class _Simple(BaseModel):
    name: str
    value: int


class _ListWrapper(BaseModel):
    items: list[str] = Field(default_factory=list)


class _Inner(BaseModel):
    label: str = Field(description="a label")


class _Nested(BaseModel):
    tag: str
    inner: _Inner
    inners: list[_Inner]


def _chat_json_with_raw(raw: str, schema=_Simple):
    """Drive chat_json end-to-end through its real parsing logic by stubbing
    the one point that would otherwise touch a network."""
    real = llm._generate_sync
    # M6: chat_text now calls _generate_sync(..., usage_sink=...) to collect
    # token-usage metrics — the stub's signature must accept (and ignore)
    # that keyword-only arg, same as the real function does when a provider
    # doesn't report usage.
    llm._generate_sync = lambda system, user, model, *, usage_sink=None: raw
    try:
        return asyncio.run(chat_json("sys", "user", schema))
    finally:
        llm._generate_sync = real


def test_clean_json_no_fence():
    result = _chat_json_with_raw('{"name": "x", "value": 1}')
    assert result == _Simple(name="x", value=1)


def test_json_wrapped_in_markdown_fence():
    result = _chat_json_with_raw('```json\n{"name": "x", "value": 1}\n```')
    assert result == _Simple(name="x", value=1)


def test_json_embedded_in_surrounding_prose():
    raw = 'Here is the result: {"name": "x", "value": 1} — hope that helps!'
    result = _chat_json_with_raw(raw)
    assert result == _Simple(name="x", value=1)


def test_bare_key_value_pairs_missing_outer_braces():
    # llm.py:401-405 — the model sometimes drops the outer {}.
    result = _chat_json_with_raw('"name": "x", "value": 1')
    assert result == _Simple(name="x", value=1)


def test_json_schema_envelope_is_unwrapped():
    # llm.py:406-415 — the model echoes {"properties": {...}, "type": "object"}
    # instead of a plain instance.
    raw = '{"properties": {"name": "x", "value": 1}, "type": "object"}'
    result = _chat_json_with_raw(raw)
    assert result == _Simple(name="x", value=1)


def test_bare_array_wraps_into_the_single_list_field():
    # llm.py:417-423 — a schema with exactly one list field accepts a bare array.
    result = _chat_json_with_raw('["a", "b", "c"]', schema=_ListWrapper)
    assert result == _ListWrapper(items=["a", "b", "c"])


def test_non_json_garbage_raises_with_a_readable_message():
    try:
        _chat_json_with_raw("the model just refused to answer")
    except ValueError as e:
        assert "did not return JSON" in str(e)
    else:
        raise AssertionError("expected ValueError for unparseable output")


def test_schema_validation_failure_is_wrapped_with_context():
    try:
        _chat_json_with_raw('{"name": "x"}')  # missing required "value"
    except ValueError as e:
        assert "Pydantic validation failed" in str(e)
    else:
        raise AssertionError("expected ValueError for a schema mismatch")


def test_strip_code_fence_variants():
    assert _strip_code_fence('{"a": 1}') == '{"a": 1}'
    assert _strip_code_fence('```json\n{"a": 1}\n```') == '{"a": 1}'
    assert _strip_code_fence('```\n{"a": 1}\n```') == '{"a": 1}'
    # Not a full wrap (fence only at the start) -> left alone, per the $ anchor.
    unwrapped = '```json\n{"a": 1}'
    assert _strip_code_fence(unwrapped) == unwrapped


def test_retry_after_seconds_parses_gemini_and_generic_shapes():
    assert _retry_after_seconds(Exception("retry_delay { seconds: 5 }")) == 5.0
    assert _retry_after_seconds(Exception("rate limited, try again in 3.5s")) == 3.5
    assert _retry_after_seconds(Exception("no timing info here")) is None


def test_schema_hint_recurses_into_nested_and_list_of_models():
    hint = _schema_hint(_Nested)
    assert '"tag": str (required)' in hint
    assert '"inner": object (required), with fields:' in hint
    assert '"inners": array (required), each item an object with fields:' in hint
    assert '"label": str (required) - a label' in hint


if __name__ == "__main__":
    test_clean_json_no_fence()
    test_json_wrapped_in_markdown_fence()
    test_json_embedded_in_surrounding_prose()
    test_bare_key_value_pairs_missing_outer_braces()
    test_json_schema_envelope_is_unwrapped()
    test_bare_array_wraps_into_the_single_list_field()
    test_non_json_garbage_raises_with_a_readable_message()
    test_schema_validation_failure_is_wrapped_with_context()
    test_strip_code_fence_variants()
    test_retry_after_seconds_parses_gemini_and_generic_shapes()
    test_schema_hint_recurses_into_nested_and_list_of_models()
    print("ok: chat_json repair ladder (all branches), _strip_code_fence, _retry_after_seconds, _schema_hint")
