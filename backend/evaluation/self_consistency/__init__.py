"""M11 self-consistency evaluation tooling (Document 47 §9.1).

Produces empirical evidence for a later, separate CTO/reviewer
gate-promotion decision. Deliberately isolated from evaluation/core/,
evaluation/golden_dataset/, and evaluation/regression/ (M10/Phase A-C's
frozen contracts) — this package never imports evaluation.core.case_evaluator
or evaluation.core.judge_gate, and nothing here can influence case-level
PASS/FAIL or the self-consistency gate's version.
"""
