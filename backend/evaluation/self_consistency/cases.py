"""M11 self-consistency evaluation tooling (Document 47 §9.1) — the held-out
claim/evidence case model and loader.

Deliberately separate from evaluation/golden_dataset/ (M10's frozen
regression dataset, Document 45 §7): these cases are never run through
evaluate_case, never regression-compared, carry no expected_behaviors, and
exist for exactly one purpose — repeated judge invocation to measure verdict
agreement (§9.1 steps 1-3). Same loader discipline as
evaluation/golden_dataset/loader.py (collect every error in one pass, reject
duplicate ids), reused, not reinvented.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

# Document 47 §7.0 Revision 4: model_judged_support is Research/Learning
# only — Comparison Explanation is excluded at the type level here, not
# just by convention, so a case author cannot even construct one.
Surface = Literal["research", "learning"]
ReferenceVerdict = Literal["SUPPORTED", "CONTRADICTED", "UNSUPPORTED", "NOT_APPLICABLE"]


class HeldOutCase(BaseModel):
    """One fixed (claim, evidence) pair for judge self-consistency
    measurement. `reference_verdict`/`reference_rationale` are evaluation
    metadata ONLY (this task's own §1 requirement) — never passed to the
    judge; read only by the aggregation report to characterize agreement
    against a human-authored expectation, after the fact."""

    case_id: str = Field(min_length=1)
    surface: Surface
    provenance: str = Field(
        min_length=1,
        description="Where/how this case was authored, and its independence from judge-prompt tuning",
    )
    claim: str = Field(min_length=1)
    evidence: str = Field(min_length=1)
    reference_verdict: ReferenceVerdict
    reference_rationale: str = Field(min_length=1)


class HeldOutSetIntegrityError(ValueError):
    """One or more held-out case files failed to load or validate — every
    problem collected in one pass (evaluation/golden_dataset/loader.py's
    own DatasetIntegrityError precedent), not fail-fast on the first bad file."""

    def __init__(self, errors: dict[str, str]):
        self.errors = errors
        summary = "\n".join(f"  {path}: {msg}" for path, msg in sorted(errors.items()))
        super().__init__(f"{len(errors)} held-out case file(s) failed to load:\n{summary}")


def load_held_out_set(cases_dir: Path) -> list[HeldOutCase]:
    """Load every `*.json` file in `cases_dir` as a validated HeldOutCase."""
    files = sorted(cases_dir.glob("*.json"))
    if not files:
        raise HeldOutSetIntegrityError({str(cases_dir): "no held-out case files found (*.json)"})

    errors: dict[str, str] = {}
    cases: list[HeldOutCase] = []
    seen_ids: dict[str, str] = {}

    for path in files:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors[str(path)] = f"invalid JSON: {e}"
            continue

        try:
            case = HeldOutCase.model_validate(raw)
        except ValidationError as e:
            errors[str(path)] = f"schema validation failed: {e}"
            continue

        if case.case_id in seen_ids:
            errors[str(path)] = (
                f"duplicate case_id {case.case_id!r} (already declared in {seen_ids[case.case_id]!r})"
            )
            continue

        seen_ids[case.case_id] = str(path)
        cases.append(case)

    if errors:
        raise HeldOutSetIntegrityError(errors)
    return cases
