"""M10 Phase 3 — the evaluation core's result shapes (Document 45 §12/§13,
narrowed to a single run — no regression/baseline comparison, that is Phase 4).

Dataclasses, same rationale as evaluation/adapters/types.py: in-process
values passed core -> (future) Phase 4 persistence/CLI, not a JSON-file
boundary like evaluation/golden_dataset/models.py's Pydantic models.
"""
from __future__ import annotations

from dataclasses import dataclass

from evaluation.adapters.types import ExecutionMetadata, ExecutionMode
from evaluation.golden_dataset.models import Surface
from typing import Literal

# Single-run status only (this task's §11) — PASS/WARNING/REGRESSION/
# UNCHANGED_FAILURE/INCONCLUSIVE (Document 45 §18) requires a stored
# baseline to compare against, which does not exist until Phase 4. Nothing
# here is named "verdict" — that word is reserved for §18's later, richer
# concept so the two are never confused.
Status = Literal["PASS", "FAIL", "INCONCLUSIVE"]


@dataclass(frozen=True)
class BehaviorEvaluation:
    """The outcome of evaluating one ExpectedBehavior (Document 45 §7)
    against a NormalizedOutput."""

    behavior_id: str
    match_rule: str
    status: Status
    reason: str


@dataclass(frozen=True)
class MetricResult:
    """One named metric from Document 45 §13's four-metric set. `value` is
    the raw computed number/label for visibility; `status` is that metric's
    own PASS/FAIL/INCONCLUSIVE reading (citation_coverage's is informational
    only — it never gates the case, per §13's own "diagnostic" framing)."""

    name: str
    value: float | bool | str | None
    status: Status
    detail: str


@dataclass(frozen=True)
class CaseEvaluationResult:
    """One benchmark case's full evaluation (Document 45 §12's EvaluationResult,
    narrowed to Phase 3's scope — no `run_id`, `code_revision`, or `verdict`
    5-state enum, all Phase 4/run-level concerns per Document 45 §17/§24)."""

    case_id: str
    surface: Surface
    dataset_version: int
    case_version: int
    mode: ExecutionMode
    evaluation_version: str
    execution: ExecutionMetadata
    behavior_evaluations: list[BehaviorEvaluation]
    metrics: list[MetricResult]
    status: Status
    failure_reasons: list[str]
