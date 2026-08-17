"""M9.1 — Comparison AI Explanation: pure, hermetically-testable grounding logic.

Implements Document 43's frozen contract on top of the existing `chat_json`/
`chat_text` LLM abstraction (agents/llm.py, unmodified) — no second LLM client,
no new provider abstraction, no new retry loop (chat_json already delegates to
chat_text's retry loop; nothing here re-implements it).

Deliberately kept out of server.py (unlike `_run_pipeline`/`_run_explanation`,
which stay there per existing convention) because none of this needs a
LangGraph graph or the job-lifecycle boilerplate — it is pure functions plus
one async LLM call, exactly like `agents/scoring.py`'s `compute_scorecard` is a
separate, independently-testable module server.py calls into.
"""
from __future__ import annotations

import hashlib
import re
from typing import Optional

from agents.llm import chat_json
from agents.schemas import ComparisonExplanationSchema

# Bumped manually if the prompt wording or the output schema shape changes —
# both are explicit components of the explanation-generation identity
# (Document 41 §12.2, Document 43 §14.1/§14.2): a wording/shape change must
# produce a new identity, not silently reuse an artifact generated under the
# old one.
PROMPT_VERSION = "v1"
SCHEMA_VERSION = "v1"

_EVIDENCE_FIELDS = ("extracted_data", "sentiment_analysis", "scorecard")
_VALID_SOURCE_FIELDS = frozenset(_EVIDENCE_FIELDS + ("report",))
_CITATION_RE = re.compile(r"\[(\d+)\]")


class GroundingError(ValueError):
    """Structured LLM output failed citation/grounding validation. Treated as a
    generation failure (never silently published) — Document 42 §7, Document 43 §10."""


def build_evidence_payload(resolved_reports: list[dict]) -> list[dict]:
    """Bounded, structured grounding input — only extracted_data/sentiment_analysis/
    scorecard per report, never draft_report/source_documents/events (Document 41
    §13.1's grounding-input discipline, mirroring financial_extractor_node's existing
    "only what's in the text" rule). `resolved_reports` must already be
    execution-time-authorized (Document 41 §13.2) — this function does no auth."""
    payload = []
    for i, r in enumerate(resolved_reports, start=1):
        payload.append({
            "report_number": i,
            "ticker": r.get("ticker"),
            "company_name": r.get("company_name"),
            "extracted_data": r.get("extracted_data") or {},
            "sentiment_analysis": r.get("sentiment_analysis") or {},
            "scorecard": r.get("scorecard") or {},
        })
    return payload


def build_prompt(evidence: list[dict]) -> tuple[str, str]:
    """(system, user) for chat_json. chat_json's own guardrail already appends the
    JSON-shape instructions (agents/llm.py) — this only carries the product-level
    grounding/behavior rules (Document 42)."""
    system = (
        "You are an equity-research assistant explaining the meaningful differences "
        "between companies a user is comparing, for the AlphaScribe Comparison screen.\n\n"
        "You are given each company's own already-extracted financial data, sentiment "
        "analysis, and scorecard — nothing else. Ground every material claim ONLY in this "
        "data; never invent financial values, percentages, periods, metrics, or trends.\n\n"
        "Explain what the differences MEAN in research context (not just restating the "
        "numbers) — semantic interpretation, not a bare data dump. Never issue a buy/sell "
        "recommendation, investment advice, or a verdict on which company is 'better'.\n\n"
        "Only state a cause for a difference if the provided sentiment_analysis or "
        "extracted_data (e.g. guidance) for that company itself already states it — never "
        "infer or guess a cause. If you cannot find a supporting cause in the given data, "
        "describe the difference without explaining why it happened.\n\n"
        "Cite every material claim with an inline [n] marker, where n is the 1-based index "
        "of an entry you list under `sources`. Each source's `report_number` must be one of "
        "the report_number values given below (never invent a report_number) and `field` "
        "must be exactly one of: extracted_data, sentiment_analysis, scorecard, report.\n\n"
        "If a company is missing a metric other companies have (the field is null, empty, or "
        "absent), do NOT estimate, interpolate, or guess a value for it — list it under "
        "`limitations` with the affected report_number and metric name instead, and do not "
        "make any claim in narrative that would require that missing value."
    )
    import json
    user = (
        "Compared companies (in this order — cite by report_number, not by name):\n\n"
        + json.dumps(evidence, default=str, indent=2)
        + "\n\nExplain the meaningful differences between these companies."
    )
    return system, user


def compute_identity_key(resolved_report_ids: list[str], *, provider: str, model: str) -> str:
    """Explanation-generation identity (Document 41 §12.2, Document 43 §14.1's
    canonical-identity stage): resolved report IDs + prompt version + schema version +
    provider + model. Order-independent in report_ids (a comparison of [A,B] and [B,A]
    is the same comparison identity)."""
    parts = "|".join(sorted(resolved_report_ids))
    key = f"{parts}::{PROMPT_VERSION}::{SCHEMA_VERSION}::{provider}::{model}"
    return hashlib.sha256(key.encode()).hexdigest()


def compute_evidence_fingerprint(resolved_reports: list[dict]) -> str:
    """'Materially equivalent evidence state' for partial-result reuse (Document 43
    §15.1) — a presence-only fingerprint of which grounding fields each resolved report
    actually has data in.

    ponytail: reports are immutable after creation in this codebase (Document 41 §2) —
    nothing currently re-extracts extracted_data/sentiment_analysis/scorecard for an
    existing report, so this fingerprint cannot actually change for a fixed report set
    today. Recomputed fresh (not cached) so it stays correct if a future feature ever
    makes report content mutable; upgrade path then would be hashing field *content*,
    not just presence.
    """
    parts = []
    for r in sorted(resolved_reports, key=lambda r: r["id"]):
        present = sorted(f for f in _EVIDENCE_FIELDS if r.get(f))
        parts.append(f"{r['id']}:{','.join(present)}")
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def validate_and_map_citations(result: ComparisonExplanationSchema, resolved_reports: list[dict]) -> dict:
    """Mechanically validates the LLM's structured output against Document 43 §10's
    invariants and maps each source's model-supplied `report_number` to the real,
    server-known `report_id` — the model's own output never determines a real id.

    Raises GroundingError (never silently publishes) when:
      - a citation marker or index is inconsistent (duplicate/undeclared/unused index);
      - a source or limitation references a report_number out of range;
      - a source has an invalid `field`;
      - there are zero grounded citations (Document 42 §7 — zero-citation reject).

    Returns a dict matching Document 43 §9-§11's ExplanationResult shape (minus id/
    comparison_report_ids/generated_at, which the caller attaches)."""
    n = len(resolved_reports)

    declared_indices = [s.index for s in result.sources]
    if len(declared_indices) != len(set(declared_indices)):
        raise GroundingError("duplicate citation indices declared in sources")
    declared = set(declared_indices)

    used = {int(m) for m in _CITATION_RE.findall(result.narrative)}
    if not used:
        raise GroundingError("narrative contains no [n] citation markers")
    if not used <= declared:
        raise GroundingError(f"narrative cites indices not declared in sources: {sorted(used - declared)}")

    cited = set(result.cited_source_indices)
    if not cited:
        raise GroundingError("zero grounded citations")
    if not cited <= declared:
        raise GroundingError("cited_source_indices references an index not declared in sources")
    if not used <= cited:
        # Document 43 §10's invariant: every [n] marker actually present in the
        # narrative must itself be confirmed as grounded via cited_source_indices
        # — a marker that's merely *declared* in sources but never listed as
        # cited is not proof the claim is grounded (a model could declare a
        # source for one claim and silently attach the same marker to an
        # uncited one). used ⊆ declared alone is not sufficient.
        raise GroundingError(
            f"narrative cites indices not confirmed in cited_source_indices: {sorted(used - cited)}"
        )

    mapped_sources = []
    for s in result.sources:
        if not (1 <= s.report_number <= n):
            raise GroundingError(f"source {s.index} references report_number {s.report_number}, out of range 1..{n}")
        if s.field not in _VALID_SOURCE_FIELDS:
            raise GroundingError(f"source {s.index} has invalid field {s.field!r}")
        mapped_sources.append({
            "index": s.index,
            "report_id": resolved_reports[s.report_number - 1]["id"],
            "field": s.field,
        })

    limitations = []
    for lim in result.limitations:
        if lim.report_number is not None and not (1 <= lim.report_number <= n):
            raise GroundingError(f"limitation references report_number {lim.report_number}, out of range 1..{n}")
        limitations.append({
            "report_id": resolved_reports[lim.report_number - 1]["id"] if lim.report_number else None,
            "metric": lim.metric,
            "reason": lim.reason,
        })

    return {
        "narrative": result.narrative,
        "sources": mapped_sources,
        "cited_source_indices": sorted(cited),
        "limitations": limitations,
        "evidence_completeness": "partial" if limitations else "complete",
    }


async def generate_explanation(resolved_reports: list[dict]) -> dict:
    """The one LLM call (chat_json → chat_text, agents/llm.py, unmodified) plus
    validation. Raises GroundingError on any grounding-integrity failure, or
    propagates whatever chat_json itself raises (NonRetryableLLMError, ValueError on
    malformed JSON, a provider exception after chat_text's own retry loop is
    exhausted) — the caller (server.py's job wrapper) maps all of these to the
    existing redacted-failure-message convention, exactly like every other AI node
    in this codebase."""
    from agents.llm import DEFAULT_LIGHT_MODEL

    evidence = build_evidence_payload(resolved_reports)
    system, user = build_prompt(evidence)
    result = await chat_json(system, user, ComparisonExplanationSchema, model=DEFAULT_LIGHT_MODEL)
    return validate_and_map_citations(result, resolved_reports)
