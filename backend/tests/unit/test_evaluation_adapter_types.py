"""Unit check for evaluation/adapters/types.py — the common adapter contract
(M10 Phase 2, Document 45 §11). Pure, dependency-free.

    python backend/tests/unit/test_evaluation_adapter_types.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from evaluation.adapters.types import (
    AdapterError,
    AdapterInvocationError,
    AdapterResult,
    Citation,
    ExecutionMetadata,
    InvalidBenchmarkInputError,
    MalformedAIOutputError,
    NormalizedOutput,
    ProviderExecutionError,
    UnsupportedExecutionModeError,
    fingerprint,
)


def test_normalized_output_has_expected_fields():
    out = NormalizedOutput(
        text="hello",
        citations=[Citation(source_id="1", eligible=True, referenced=True, valid=True)],
        grounding_verdict="grounded",
        limitations_stated=[],
    )
    assert out.text == "hello"
    assert out.citations[0].valid is True
    assert out.raw == {}  # default_factory


def test_adapter_result_carries_case_surface_mode():
    result = AdapterResult(
        case_id="c1", surface="research", mode="live",
        output=NormalizedOutput(text="x", citations=[], grounding_verdict="error", limitations_stated=[]),
        execution=ExecutionMetadata(provider="gemini", model="gemini-flash"),
    )
    assert result.case_id == "c1"
    assert result.surface == "research"
    assert result.mode == "live"
    assert result.execution.provider == "gemini"


def test_execution_metadata_never_carries_api_key_field():
    # No `api_key` field exists on the dataclass at all — a structural
    # guarantee, not just a convention, that a secret can't be attached.
    assert "api_key" not in ExecutionMetadata.__dataclass_fields__


def test_error_hierarchy():
    for exc_cls in (
        InvalidBenchmarkInputError, AdapterInvocationError,
        ProviderExecutionError, MalformedAIOutputError, UnsupportedExecutionModeError,
    ):
        assert issubclass(exc_cls, AdapterError)
        try:
            raise exc_cls("x")
        except AdapterError:
            pass
        else:
            raise AssertionError(f"{exc_cls} should be catchable as AdapterError")


def test_fingerprint_is_deterministic_and_content_sensitive():
    a = fingerprint("system prompt", "user template")
    b = fingerprint("system prompt", "user template")
    c = fingerprint("system prompt", "different template")
    assert a == b
    assert a != c
    assert isinstance(a, str) and len(a) == 16


if __name__ == "__main__":
    test_normalized_output_has_expected_fields()
    test_adapter_result_carries_case_surface_mode()
    test_execution_metadata_never_carries_api_key_field()
    test_error_hierarchy()
    test_fingerprint_is_deterministic_and_content_sensitive()
    print("ok: NormalizedOutput/AdapterResult/ExecutionMetadata shape; AdapterError hierarchy; fingerprint()")
