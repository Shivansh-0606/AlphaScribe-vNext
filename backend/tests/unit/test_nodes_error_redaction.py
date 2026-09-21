"""Regression test for the dev-facing error-leak finding (Company Research
Overview hardening-pass brief §3.4): a raw LLM/provider exception message
(e.g. `NonRetryableLLMError`'s "...Raise it in backend/.env and retry.")
must never reach the user-visible SSE trace or the persisted
`validation_errors` field verbatim -- only a generic, redacted message,
with full detail going to the server log (`agents/nodes.py::_safe_failure`).

Hermetic: `chat_json` is monkeypatched, no real LLM/network/DB call.

    python backend/tests/unit/test_nodes_error_redaction.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import agents.learning_nodes as learning_nodes  # noqa: E402
import agents.nodes as nodes  # noqa: E402

_DEV_FACING_MESSAGE = (
    "LLM output was truncated by the max_tokens cap (LLM_MAX_OUTPUT_TOKENS). "
    "Raise it in backend/.env and retry."
)


def test_safe_failure_never_includes_raw_exception_text():
    msg = nodes._safe_failure("Fact-check", RuntimeError(_DEV_FACING_MESSAGE))
    assert "backend/.env" not in msg and "LLM_MAX_OUTPUT_TOKENS" not in msg
    assert msg == "Fact-check failed. See server logs for details."


def test_fact_checker_node_redacts_llm_failure_from_trace_and_validation_errors():
    async def _boom(*_a, **_k):
        raise RuntimeError(_DEV_FACING_MESSAGE)

    original = nodes.chat_json
    nodes.chat_json = _boom
    try:
        state = {
            "draft_report": "Revenue grew 12% year over year.",
            "source_documents": [],
            "retry_count": 0,
        }
        result = asyncio.run(nodes.fact_checker_node(state))
    finally:
        nodes.chat_json = original

    assert result["fact_check_status"] is False
    assert result["retry_count"] == 1
    for err in result["validation_errors"]:
        assert "backend/.env" not in err and "LLM_MAX_OUTPUT_TOKENS" not in err
    for event in result["trace"]:
        assert "backend/.env" not in event["message"] and "LLM_MAX_OUTPUT_TOKENS" not in event["message"]


def test_explainer_node_redacts_llm_failure_from_trace():
    # Backend Reviewer's finding: learning_nodes.py::explainer_node mirrors
    # nodes.py's node-level catch and had the identical leak shape, reachable
    # via server.py's Learning SSE stream -- not caught by the first pass
    # because it lives in a different module.
    async def _boom(*_a, **_k):
        raise RuntimeError(_DEV_FACING_MESSAGE)

    original = learning_nodes.chat_text
    learning_nodes.chat_text = _boom
    try:
        state = {"concept": "gross margin", "ticker": "AAPL", "source_documents": []}
        result = asyncio.run(learning_nodes.explainer_node(state))
    finally:
        learning_nodes.chat_text = original

    assert result["explanation"] == ""
    for event in result["trace"]:
        assert "backend/.env" not in event["message"] and "LLM_MAX_OUTPUT_TOKENS" not in event["message"]


if __name__ == "__main__":
    test_safe_failure_never_includes_raw_exception_text()
    test_fact_checker_node_redacts_llm_failure_from_trace_and_validation_errors()
    test_explainer_node_redacts_llm_failure_from_trace()
    print("ok: nodes.py error redaction — no raw exception text in user-visible trace/validation_errors")
