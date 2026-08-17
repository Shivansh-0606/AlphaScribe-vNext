"""M10 Phase 2 — Learning surface adapter (Document 45 §11).

Invokes the existing, already-compiled Learning graph — the same module-
level singleton (`server.learning_graph`) `server.py:1325`'s `_run_explanation`
calls — directly via `.ainvoke()`, bypassing job/DB/SSE entirely. No second
Learning implementation: no LLM call, no prompt, no retrieval logic here.

Learning's own grounding model is binary by construction — `explainer_node`
(agents/learning_nodes.py) either returns a non-empty `explanation` with a
non-empty `cited_sources` list, or returns both empty (LLM failure, or
Law 3's zero-citation-reject) — there is no partial/ungrounded-but-non-empty
state to observe, unlike Research's fact-checker gradation. `grounding_verdict`
below reflects that: only "grounded" or "error" are ever produced.
"""
from __future__ import annotations

import inspect

from evaluation.golden_dataset.models import BenchmarkCase

from .types import (
    AdapterInvocationError,
    AdapterResult,
    Citation,
    ExecutionMetadata,
    ExecutionMode,
    MalformedAIOutputError,
    NormalizedOutput,
    UnsupportedExecutionModeError,
    fingerprint,
)

SURFACE = "learning"


def _prompt_fingerprint() -> str:
    from agents import learning_nodes

    return fingerprint(
        learning_nodes._SYSTEM_PROMPT,
        inspect.getsource(learning_nodes._build_user_message),
    )


def _build_initial_state(case: BenchmarkCase) -> dict:
    # Mirrors server.py:1355's own `initial` dict construction for
    # _run_explanation — same required LearningState keys.
    state: dict = {
        "ticker": str(case.context["ticker"]).upper(),
        "concept": str(case.context["concept"]),
        "query": str(case.context.get("query") or case.context["concept"]),
        "trace": [],
    }
    if case.context.get("company_name"):
        state["company_name"] = str(case.context["company_name"])
    return state


def _normalize(case: BenchmarkCase, mode: ExecutionMode, final_state: dict) -> AdapterResult:
    docs = final_state.get("source_documents") or []
    explanation = final_state.get("explanation") or ""
    cited_sources = final_state.get("cited_sources") or []

    # _postprocess_citations (agents/learning_nodes.py) already strips any
    # out-of-range [n] marker before returning — cited_sources IS the valid
    # set. We have no visibility into markers that were silently dropped,
    # so referenced == valid here, not a limitation of this adapter but of
    # what explainer_node's own return value exposes (Document 45 §11's
    # per-adapter Citation population, done from what's actually available).
    cited_set = set(cited_sources)
    citations = [
        Citation(source_id=str(i), eligible=True, referenced=i in cited_set, valid=i in cited_set)
        for i in range(1, len(docs) + 1)
    ]

    grounding_verdict = "grounded" if explanation and cited_sources else "error"

    from agents.llm import _active

    cfg = _active()
    output = NormalizedOutput(
        text=explanation,
        citations=citations,
        grounding_verdict=grounding_verdict,
        limitations_stated=[],  # Learning has no structured limitations field today
        raw=dict(final_state),
    )
    execution = ExecutionMetadata(
        provider=cfg.get("provider"),
        model=cfg.get("heavy"),  # explainer_node's one LLM call uses the heavy tier
        prompt_fingerprint=_prompt_fingerprint(),
    )
    return AdapterResult(case_id=case.case_id, surface=SURFACE, mode=mode, output=output, execution=execution)


async def run(case: BenchmarkCase, mode: ExecutionMode = "live") -> AdapterResult:
    """Run the Learning surface for one benchmark case and return its
    normalized result. Raises AdapterError subclasses on failure."""
    if case.surface != SURFACE:
        raise ValueError(f"learning adapter called with surface={case.surface!r}")

    if mode == "fixture":
        raise UnsupportedExecutionModeError(
            f"case {case.case_id!r}: Learning FIXTURE mode is not implemented in M10 Phase 2 "
            "(Document 45 §11.1's retriever stand-in is deliberately deferred, not built here)"
        )

    from server import learning_graph  # existing compiled singleton

    initial_state = _build_initial_state(case)
    try:
        final_state = await learning_graph.ainvoke(initial_state, {"recursion_limit": 10})
    except Exception as e:  # noqa: BLE001 — see AdapterInvocationError's own docstring
        raise AdapterInvocationError(f"case {case.case_id!r}: Learning graph.ainvoke failed: {e}") from e

    if not isinstance(final_state, dict) or not final_state:
        raise MalformedAIOutputError(
            f"case {case.case_id!r}: Learning graph.ainvoke returned an empty/non-dict final state"
        )
    return _normalize(case, mode, final_state)
