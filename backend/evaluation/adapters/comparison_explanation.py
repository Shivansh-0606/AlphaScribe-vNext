"""M10 Phase 2 — Comparison Explanation surface adapter (Document 45 §11).

Reuses `agents.comparison_explanation.generate_explanation` directly — the
same pure function `server.py:1814`'s `_run_comparison_explanation` calls —
no second LLM invocation path, no re-implemented grounding/citation logic.

Unlike Research/Learning's nodes (which never raise — failures are absorbed
into empty in-state fields), `generate_explanation` itself raises on failure
(its own docstring: "propagates whatever chat_json itself raises"). This
adapter mirrors that shape at its own boundary: `GroundingError` is caught
and mapped to `grounding_verdict="ungrounded"` (a real, meaningful AI-quality
result, not an adapter failure); any other exception is wrapped and re-raised
as `ProviderExecutionError`.

Two execution modes, both implemented (unlike Research/Learning, where only
LIVE mode is built this phase — see Document 45 §11.1's own deferral for
why): LIVE resolves real reports via the existing, unmodified
`server._resolve_authorized_reports` (EQ-3 owner-or-sample authorization,
reused exactly — no second resolution query); FIXTURE reads inline report
dicts straight from `case.context["fixture_reports"]` — no Mongo, no stand-in
needed, since `generate_explanation` already takes plain dicts as its input.
"""
from __future__ import annotations

from evaluation.golden_dataset.models import BenchmarkCase

from .types import (
    AdapterInvocationError,
    AdapterResult,
    Citation,
    ExecutionMetadata,
    ExecutionMode,
    InvalidBenchmarkInputError,
    MalformedAIOutputError,
    NormalizedOutput,
    ProviderExecutionError,
)

SURFACE = "comparison_explanation"

# A placeholder identity for the required user_id argument of
# server._resolve_authorized_reports — that query's own predicate is
# `{"user_id": user_id} OR {"is_sample": True}` (server.py's own EQ-3
# resolution), so any non-empty placeholder resolves is_sample=true reports
# correctly regardless of its value. Benchmark cases referencing real report
# ids should reference sample reports for this reason, documented in
# evaluation/golden_dataset/models.py's context-key requirement (§7).
_EVALUATION_USER_ID = "m10-evaluation-harness"


async def _resolve_reports_live(report_ids: list[str], case_id: str) -> list[dict]:
    from server import _resolve_authorized_reports

    try:
        resolved = await _resolve_authorized_reports(report_ids, _EVALUATION_USER_ID)
    except Exception as e:  # noqa: BLE001 — see AdapterInvocationError's own docstring
        raise AdapterInvocationError(
            f"case {case_id!r}: _resolve_authorized_reports failed: {e}"
        ) from e
    if len(resolved) < 2:
        raise InvalidBenchmarkInputError(
            f"case {case_id!r}: fewer than 2 of {report_ids!r} resolved (LIVE mode; "
            f"report ids must reference is_sample=true reports for evaluation access)"
        )
    return resolved


def _resolve_reports_fixture(case: BenchmarkCase) -> list[dict]:
    fixture_reports = case.context.get("fixture_reports")
    if not isinstance(fixture_reports, list) or len(fixture_reports) < 2:
        raise InvalidBenchmarkInputError(
            f"case {case.case_id!r}: FIXTURE mode requires >=2 entries in "
            f"context['fixture_reports'] (Document 45 §11.1); none/insufficient supplied"
        )
    return fixture_reports


def _eligible_source_ids(resolved_reports: list[dict]) -> set[str]:
    from agents.comparison_explanation import _EVIDENCE_FIELDS

    ids = set()
    for report in resolved_reports:
        report_id = report["id"]
        ids.add(f"{report_id}:report")  # the report itself is always citable as a whole
        for field_name in _EVIDENCE_FIELDS:
            if report.get(field_name):
                ids.add(f"{report_id}:{field_name}")
    return ids


def _normalize(case: BenchmarkCase, mode: ExecutionMode, result: dict, resolved_reports: list[dict]) -> AdapterResult:
    mapped_ids = {f"{s['report_id']}:{s['field']}" for s in result["sources"]}
    eligible_ids = _eligible_source_ids(resolved_reports)
    # eligible and mapped/cited are distinct concepts (Document 45 §13):
    # eligible = actually available as citable evidence (report field
    # presence, independent of the model's behavior); referenced/valid = what
    # the model cited and validate_and_map_citations accepted. A source can be
    # cited without being eligible (the model cited an empty/absent field —
    # structurally valid per validate_and_map_citations, since that function
    # only checks report_number range + field name, not field content) — such
    # a citation must report eligible=False, not be conflated with eligibility.
    citations = [
        Citation(
            source_id=sid,
            eligible=(sid in eligible_ids),
            referenced=(sid in mapped_ids),
            valid=(sid in mapped_ids),
        )
        for sid in sorted(eligible_ids | mapped_ids)
    ]

    limitations_stated = [
        f"{lim['metric']}: {lim['reason']}" for lim in result.get("limitations", [])
    ]

    from agents.comparison_explanation import PROMPT_VERSION, SCHEMA_VERSION
    from agents.llm import _active

    cfg = _active()
    output = NormalizedOutput(
        text=result["narrative"],
        citations=citations,
        grounding_verdict="grounded",
        limitations_stated=limitations_stated,
        raw=dict(result),
    )
    execution = ExecutionMetadata(
        provider=cfg.get("provider"),
        model=cfg.get("light"),  # generate_explanation calls chat_json with DEFAULT_LIGHT_MODEL
        prompt_version=PROMPT_VERSION,
        prompt_fingerprint=None,  # explicit version exists for this surface — no hash proxy needed
    )
    return AdapterResult(case_id=case.case_id, surface=SURFACE, mode=mode, output=output, execution=execution)


def _ungrounded_result(case: BenchmarkCase, mode: ExecutionMode, reason: str) -> AdapterResult:
    from agents.llm import _active

    cfg = _active()
    output = NormalizedOutput(
        text="",
        citations=[],
        grounding_verdict="ungrounded",
        limitations_stated=[],
        raw={"grounding_error": reason},
    )
    execution = ExecutionMetadata(provider=cfg.get("provider"), model=cfg.get("light"))
    return AdapterResult(case_id=case.case_id, surface=SURFACE, mode=mode, output=output, execution=execution)


async def run(case: BenchmarkCase, mode: ExecutionMode = "live") -> AdapterResult:
    """Run the Comparison Explanation surface for one benchmark case and
    return its normalized result. Raises AdapterError subclasses on failure."""
    if case.surface != SURFACE:
        raise ValueError(f"comparison_explanation adapter called with surface={case.surface!r}")

    report_ids = case.context.get("report_ids")
    if not isinstance(report_ids, list) or len(report_ids) < 2:
        raise InvalidBenchmarkInputError(
            f"case {case.case_id!r}: context['report_ids'] must have >=2 entries"
        )

    if mode == "fixture":
        resolved_reports = _resolve_reports_fixture(case)
    else:
        resolved_reports = await _resolve_reports_live(report_ids, case.case_id)

    from agents.comparison_explanation import GroundingError, generate_explanation

    try:
        result = await generate_explanation(resolved_reports)
    except GroundingError as e:
        return _ungrounded_result(case, mode, str(e))
    except Exception as e:  # noqa: BLE001 — see ProviderExecutionError's own docstring
        raise ProviderExecutionError(
            f"case {case.case_id!r}: generate_explanation failed: {e}"
        ) from e

    if not isinstance(result, dict) or not result.get("narrative"):
        raise MalformedAIOutputError(
            f"case {case.case_id!r}: generate_explanation returned an unexpected/empty result shape"
        )
    return _normalize(case, mode, result, resolved_reports)
