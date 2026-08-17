"""M10 Phase 2 — Research surface adapter (Document 45 §11).

Invokes the existing, already-compiled Research graph — the same module-
level singleton (`server.graph`) `server.py:889`'s `_run_pipeline` calls —
directly via `.ainvoke()`, bypassing job/DB/SSE entirely (Document 45 §11's
adapter table). No second Research implementation: this module contains no
LLM call, no prompt, and no retrieval logic of its own; it only translates
a `BenchmarkCase` into `AgentState` and normalizes the graph's own final
state back out.

Production drives this same compiled graph via `.astream()` (for SSE/trace
push and job-deadline checks — irrelevant to an evaluation run that has no
job/SSE at all). `.ainvoke()` returns the identical merged final state for
the identical compiled graph object; Document 45 §11 chose it deliberately
for exactly this reason.
"""
from __future__ import annotations

import inspect
import re

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

SURFACE = "research"

_CITATION_RE = re.compile(r"\[(\d+)\]")


def _prompt_fingerprint() -> str:
    # Research's system/user prompts are inline string literals inside each
    # LLM-calling node (agents/nodes.py), not module-level constants — so the
    # node functions' own source is the closest available "prompt template"
    # to fingerprint (Document 45 §17), via read-only introspection. No
    # pipeline file is imported for its behavior here, only its source text.
    from agents import nodes

    return fingerprint(
        inspect.getsource(nodes.financial_extractor_node),
        inspect.getsource(nodes.tone_risk_node),
        inspect.getsource(nodes.synthesizer_node),
        inspect.getsource(nodes.fact_checker_node),
    )


def _build_initial_state(case: BenchmarkCase) -> dict:
    # Mirrors server.py:928's own `initial` dict construction for
    # _run_pipeline — same required AgentState keys, no job-specific fields.
    return {
        "ticker": str(case.context["ticker"]).upper(),
        "query": str(case.context["query"]),
        "retry_count": 0,
        "trace": [],
    }


def _normalize(case: BenchmarkCase, mode: ExecutionMode, final_state: dict) -> AdapterResult:
    docs = final_state.get("source_documents") or []
    draft = final_state.get("draft_report") or ""
    verified_claims = final_state.get("verified_claims") or []
    fact_check_status = final_state.get("fact_check_status")

    cited_markers = {int(m) for m in _CITATION_RE.findall(draft)}
    citations = [
        Citation(
            source_id=str(i),
            eligible=True,
            referenced=i in cited_markers,
            valid=i in cited_markers,  # in-range by construction (1..len(docs))
        )
        for i in range(1, len(docs) + 1)
    ]

    if not draft:
        # synthesizer_node/fact_checker_node's own failure path (LLM error,
        # or fact_check_router's "give_up" after 2 failed retries with an
        # empty rewrite) — a completed-but-failed run, not an adapter error.
        grounding_verdict = "error"
    elif fact_check_status is False:
        # Fact-checker gave up: at least one claim remained unsupported
        # after the retry budget (agents/nodes.py's own fact_check_router).
        grounding_verdict = "ungrounded"
    elif not cited_markers:
        grounding_verdict = "ungrounded"
    else:
        grounding_verdict = "grounded"

    limitations_stated = [
        c["claim"] for c in verified_claims
        if isinstance(c, dict) and c.get("supported") is False
    ]

    from agents.llm import _active

    cfg = _active()
    output = NormalizedOutput(
        text=draft,
        citations=citations,
        grounding_verdict=grounding_verdict,
        limitations_stated=limitations_stated,
        raw=dict(final_state),
    )
    execution = ExecutionMetadata(
        provider=cfg.get("provider"),
        model=cfg.get("heavy"),  # synthesizer/fact_checker (the grounding-relevant calls) use the heavy tier
        prompt_fingerprint=_prompt_fingerprint(),
    )
    return AdapterResult(case_id=case.case_id, surface=SURFACE, mode=mode, output=output, execution=execution)


async def run(case: BenchmarkCase, mode: ExecutionMode = "live") -> AdapterResult:
    """Run the Research surface for one benchmark case and return its
    normalized result. Raises AdapterError subclasses (evaluation/adapters/
    types.py) on failure — never returns a partially-normalized result."""
    if case.surface != SURFACE:
        raise ValueError(f"research adapter called with surface={case.surface!r}")

    if mode == "fixture":
        raise UnsupportedExecutionModeError(
            f"case {case.case_id!r}: Research FIXTURE mode is not implemented in M10 Phase 2 "
            "(Document 45 §11.1's retriever stand-in is deliberately deferred, not built here)"
        )

    from server import graph  # existing compiled singleton — no second Research implementation

    initial_state = _build_initial_state(case)
    try:
        final_state = await graph.ainvoke(initial_state, {"recursion_limit": 10})
    except Exception as e:  # noqa: BLE001 — see AdapterInvocationError's own docstring
        raise AdapterInvocationError(f"case {case.case_id!r}: Research graph.ainvoke failed: {e}") from e

    if not isinstance(final_state, dict) or not final_state:
        raise MalformedAIOutputError(
            f"case {case.case_id!r}: Research graph.ainvoke returned an empty/non-dict final state"
        )
    return _normalize(case, mode, final_state)
