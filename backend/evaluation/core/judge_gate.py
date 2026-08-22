"""Document 47 §7.4/§9.1 — the self-consistency gate's runtime representation.

Resolves the implementation-readiness review's second blocker: Document 47
freezes that a `model_judged_support` behavior's status must be excluded from
a case's PASS/FAIL aggregation until an empirical self-consistency evaluation
(§9.1) has run and a CTO/reviewer has reviewed it (§9.1 step 6) — but the
architecture never specified how code represents "has that happened yet."

This module answers only that question. It is a versioned constant, not a
feature flag: no environment variable, no runtime mutability, no automatic
promotion on any condition this codebase can observe. Bumping it is a human,
reviewed act — the same discipline `evaluation_version` (evaluation/core/
case_evaluator.py) already applies to metric-logic changes, applied here to a
judge-trust decision instead.

Not wired into `evaluation/core/case_evaluator.py`'s aggregation functions by
this module — that wiring is part of implementing `model_judged_support`
itself (Document 47 §19 step 3/6), out of scope for this change. This module
only makes the gate's state inspectable and importable ahead of that work.
"""
from __future__ import annotations

JUDGE_SELF_CONSISTENCY_GATE_VERSION = 0
"""
0   — model-judged results are not yet trusted for PASS/FAIL aggregation.
      `model_judged_support` behaviors may be built, called, and their
      results recorded and disclosed (`judged_by`/`judge_detail`,
      Document 47 §8), but must be excluded from
      `_characteristic_coverage_metric`/`_overall_status`'s aggregation
      (Document 47 §7.4) whenever this constant is `0`.

Any value greater than 0 means a specific, CTO/reviewer-approved
self-consistency evaluation round (Document 47 §9.1) has cleared for that
version — assigned only by a future, explicit code change, never inferred at
runtime from test results, environment state, or elapsed time.
"""
