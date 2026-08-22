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
class JudgeDetail:
    """Document 47 §8 — reproducibility/disclosure metadata for a
    model-judged BehaviorEvaluation. Populated only when
    BehaviorEvaluation.judged_by == "model". `rationale` is the judge's own
    explanation — documentation only, never re-parsed or matched, the same
    discipline ExpectedBehavior.description already follows.

    M11 Phase E: `applicability`/`applicability_rationale` are additive,
    defaulted (None) fields for the structured-applicability architecture
    (Document 47 Phase D's Option B) — None for every v3-naN single-call
    result and for any record persisted before Phase E, so old result files
    keep loading unchanged. When populated: `applicability`/
    `applicability_rationale` are Stage 1's own decision/rationale;
    `verdict`/`rationale` remain the terminal decision as before — Stage 1's
    when NOT_APPLICABLE (Stage 2 never ran), Stage 2's otherwise.
    `judge_prompt_version` then carries JUDGE_ARCHITECTURE_VERSION rather
    than a v3-naN prompt-text version — same field, a version identity
    either way.

    M11 Phase H governance correction (Document 47 §9.1 step 4):
    `applicability_prompt_version`/`support_prompt_version` are additive,
    defaulted (None) fields carrying `evaluation.core.judge.
    APPLICABILITY_PROMPT_VERSION`/`SUPPORT_PROMPT_VERSION` — None for every
    v3-naN single-call result and for any record persisted before this
    change (including every Phase E/G/H self-consistency artifact already on
    disk), so old result files keep loading unchanged, the same discipline
    `applicability`/`applicability_rationale` already established one phase
    earlier. They exist because `judge_prompt_version` (carrying
    JUDGE_ARCHITECTURE_VERSION) does not, and structurally cannot, reflect a
    Stage 1- or Stage 2-only wording change — these two fields are what does.
    `support_prompt_version` is populated only when Stage 2 actually ran
    (mirroring `verdict`/`rationale`'s own Stage-1-vs-Stage-2 split above);
    it stays None on a NOT_APPLICABLE (Stage 1 terminal) result."""

    judge_model: str | None
    judge_prompt_version: str
    verdict: Literal["SUPPORTED", "CONTRADICTED", "UNSUPPORTED", "NOT_APPLICABLE"]
    rationale: str
    applicability: Literal["APPLICABLE", "NOT_APPLICABLE"] | None = None
    applicability_rationale: str | None = None
    applicability_prompt_version: str | None = None
    support_prompt_version: str | None = None


@dataclass(frozen=True)
class BehaviorEvaluation:
    """The outcome of evaluating one ExpectedBehavior (Document 45 §7)
    against a NormalizedOutput.

    `judged_by`/`judge_detail` (Document 47 §8, M11 Phase C): additive,
    defaulted fields — every existing deterministic evaluator's construction
    call is unaffected (`judged_by` defaults to "deterministic",
    `judge_detail` to None). They exist purely for disclosure/audit; a
    model-judged result must never render or persist indistinguishably from
    a deterministic one (Document 47 §10's non-negotiable requirement)."""

    behavior_id: str
    match_rule: str
    status: Status
    reason: str
    judged_by: Literal["deterministic", "model"] = "deterministic"
    judge_detail: JudgeDetail | None = None


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
