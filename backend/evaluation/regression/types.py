"""M10 Phase 4 — regression/persistence result shapes (Document 45 §12/§18,
Document 46 §4-§7's frozen corrections).

Dataclass, same rationale as evaluation/core/types.py and evaluation/adapters/
types.py: an in-process/local-file-artifact shape, not a Pydantic JSON-schema
boundary. Wraps Phase 3's frozen CaseEvaluationResult rather than duplicating
its fields (case_id/surface/dataset_version/case_version/mode/
evaluation_version/execution/metrics/status/failure_reasons all already live
there, unmodified) — this module only adds the run-level fields Document 45
§12 assigns to EvaluationResult that Phase 3 explicitly did not build
(run_id, timestamp, code_revision) plus the regression verdict (§18) and
schema_version (Document 46 §7 — populated at this boundary, not on Phase 2's
frozen ExecutionMetadata).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from evaluation.core.types import CaseEvaluationResult

# Document 45 §18, Document 46 §6 — five states, no IMPROVEMENT (reaffirmed
# twice already in Document 45's own revision history).
Verdict = Literal["PASS", "WARNING", "REGRESSION", "UNCHANGED_FAILURE", "INCONCLUSIVE"]


@dataclass(frozen=True)
class EvaluationResult:
    """One persisted record for (case, run) — Document 45 §12."""

    run_id: str            # shared across every case in one harness invocation
    timestamp: str          # ISO 8601 — stamped by the caller (the CLI), never computed in this module
    code_revision: str       # git commit hash (+"-dirty"), stdlib subprocess — Document 45 §17
    schema_version: str | None  # Document 46 §7 — the evaluated surface's explicit schema version, or null
    case: CaseEvaluationResult   # Phase 3's unmodified result — never duplicated, only wrapped
    verdict: Verdict
    verdict_reason: str
