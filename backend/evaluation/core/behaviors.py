"""M10 Phase 3 — deterministic evaluators for Document 45 §7's three frozen
ExpectedBehavior rule types. One small function per rule, each independently
testable, none containing another's logic (this task's §10).

No LLM call anywhere in this module (this task's §7/§13) — every evaluator
reads only `NormalizedOutput` (evaluation/adapters/types.py) and the
`ExpectedBehavior` being checked, and returns deterministically.

Two rule types (citation_required, limitation_reference) have a reported,
NOT silently resolved, gap against this task's own request — see each
function's own docstring below for the specifics.
"""
from __future__ import annotations

from evaluation.adapters.types import NormalizedOutput
from evaluation.core.types import BehaviorEvaluation
from evaluation.golden_dataset.models import ExpectedBehavior, Surface


def no_output_reason(output: NormalizedOutput) -> str | None:
    """Shared precondition every evaluator below needs: there is nothing to
    evaluate when the surface produced no text at all (grounding_verdict
    'error', or an ungrounded Comparison Explanation result — Document 45
    §11's own soft-failure/GroundingError mapping). Not "one metric's logic
    living in another's" — a data-availability guard every metric needs
    identically, kept in one place so it can't drift between them."""
    if not output.text:
        return f"adapter produced no generated text (grounding_verdict={output.grounding_verdict!r})"
    return None


def _normalize_text(text: str) -> str:
    # Document 45 §15: "case-insensitive substring/token check" — the one
    # tolerance for "reasonable textual variation" this task asks for,
    # nothing fuzzier (deterministic, no NLP dependency).
    return " ".join(text.lower().split())


def evaluate_keyword_variant(behavior: ExpectedBehavior, output: NormalizedOutput) -> BehaviorEvaluation:
    """Document 45 §15's presence/absence check: case-insensitive substring
    match against `behavior.variants`. `type='presence'` passes when at
    least one variant is found; `type='absence'` passes when none are."""
    reason = no_output_reason(output)
    if reason:
        return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE", reason)

    haystack = _normalize_text(output.text)
    matched = [v for v in (behavior.variants or []) if _normalize_text(v) in haystack]

    if behavior.type == "presence":
        if matched:
            return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "PASS",
                                       f"matched variant(s): {matched}")
        return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "FAIL",
                                   f"none of {behavior.variants} found in output text")
    # type == "absence" — the only other type Document 45 §7 allows for this rule
    if not matched:
        return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "PASS",
                                   "none of the forbidden variants were found")
    return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "FAIL",
                               f"forbidden variant(s) found: {matched}")


_CITATION_GAP_NOTE = (
    "evaluates citation presence in aggregate, not whether reference {reference!r} "
    "specifically was cited — no structural mapping from a human-authored reference "
    "label to a Citation.source_id exists anywhere in Document 45 or NormalizedOutput "
    "(reported gap, not silently resolved by fuzzy matching)"
)


def evaluate_citation_required(behavior: ExpectedBehavior, output: NormalizedOutput) -> BehaviorEvaluation:
    """REPORTED GAP: `behavior.reference` (Document 45 §7) is a free-text,
    human-authored label (e.g. "revenue_figure") with no structural mapping
    to any `Citation.source_id` in `NormalizedOutput` (source ids look like
    "1" or "r1:extracted_data" — a case author's `reference` value never
    matches these). Matching `reference` to a *specific* citation would
    require semantic/NLP matching — explicitly out of scope (this task's §7:
    "free from LLM judgment"; §8: "report the limitation rather than
    manufacturing a heuristic"). This evaluator therefore checks citation
    PRESENCE IN AGGREGATE — did the surface produce >=1 valid citation at
    all — which is the coarsest interpretation the frozen architecture
    actually supports deterministically.

    Document 45 §7's constraint table restricts this rule to `type='presence'`
    only (no 'forbidden citation' state is constructible via
    `BenchmarkCase.model_validate`). The `type='absence'` branch below is
    implemented defensively, symmetric with keyword_variant, per this task's
    own test-matrix request — reachable only via a hand-constructed
    ExpectedBehavior that bypasses Pydantic validation, not through the
    frozen, validated case-authoring path."""
    reason = no_output_reason(output)
    if reason:
        return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE", reason)

    has_valid_citation = any(c.valid for c in output.citations)
    note = _CITATION_GAP_NOTE.format(reference=behavior.reference)

    if behavior.type == "presence":
        if has_valid_citation:
            return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "PASS",
                                       f"at least one valid citation present ({note})")
        return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "FAIL",
                                   f"no valid citation found ({note})")
    # type == "absence" — see docstring: not constructible via the frozen schema today
    if not has_valid_citation:
        return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "PASS",
                                   f"no citation present, as required ({note})")
    return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "FAIL",
                               f"a citation was present though forbidden ({note})")


def evaluate_limitation_reference(
    behavior: ExpectedBehavior, output: NormalizedOutput, *, surface: Surface,
) -> BehaviorEvaluation:
    """REPORTED GAP (same shape as evaluate_citation_required, and same
    reason): `behavior.reference` names a `known_limitations` entry — a
    short, case-author-defined id (e.g. "figure_not_disclosed") — but
    `NormalizedOutput.limitations_stated` holds free-text sentences
    (Comparison Explanation: "metric: reason"; Research: the flagged claim
    text) with no structural mapping back to that id. This evaluator checks
    acknowledgment PRESENCE IN AGGREGATE, not reference-specific matching,
    for the same reasons evaluate_citation_required does.

    SURFACE-SPECIFIC GAP, found during Phase 3 implementation: Learning's
    adapter (evaluation/adapters/learning.py) always returns
    `limitations_stated=[]` — Learning has no structured limitations field
    in production at all (a Phase 2 finding, not new here). An empty list
    from Learning therefore does NOT mean "no limitation was acknowledged"
    the way it does for Research/Comparison Explanation — it means "this
    surface cannot report the answer." Returns INCONCLUSIVE for Learning
    unconditionally, rather than a misleading FAIL.

    Document 45 §7's `BehaviorType` enum (presence|absence|acknowledgment)
    has no fourth value meaning "forbidden acknowledgment," and this rule's
    constraint table restricts it to `type='acknowledgment'` only — unlike
    citation_required, there is no existing sibling type value to reuse
    defensively for a "forbidden" case. This task's test-matrix request for
    a forbidden-acknowledgment case cannot be fulfilled without adding a
    fourth type value to the frozen schema — not done here; only the one
    type value Document 45 actually defines is implemented."""
    reason = no_output_reason(output)
    if reason:
        return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE", reason)

    if surface == "learning":
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE",
            "Learning's adapter does not populate limitations_stated (no structured "
            "limitations field exists for this surface); cannot determine acknowledgment "
            "deterministically",
        )

    has_limitation = bool(output.limitations_stated)
    note = (
        f"evaluates acknowledgment presence in aggregate, not whether reference "
        f"{behavior.reference!r} specifically was acknowledged — no structural mapping from "
        f"a known_limitations id to limitations_stated content exists (reported gap)"
    )
    if has_limitation:
        return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "PASS",
                                   f"at least one limitation acknowledged ({note})")
    return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "FAIL",
                               f"no limitation acknowledged ({note})")


_EVALUATORS = {
    "keyword_variant": lambda behavior, output, surface: evaluate_keyword_variant(behavior, output),
    "citation_required": lambda behavior, output, surface: evaluate_citation_required(behavior, output),
    "limitation_reference": lambda behavior, output, surface: evaluate_limitation_reference(
        behavior, output, surface=surface
    ),
}


def evaluate_behavior(behavior: ExpectedBehavior, output: NormalizedOutput, *, surface: Surface) -> BehaviorEvaluation:
    """Dispatch by `behavior.match_rule` to the one matching evaluator above.
    `match_rule` is a Pydantic Literal (evaluation/golden_dataset/models.py)
    — the KeyError branch below is unreachable through any validated
    BenchmarkCase, kept only as a defensive guard."""
    try:
        fn = _EVALUATORS[behavior.match_rule]
    except KeyError:
        raise ValueError(f"unsupported match_rule {behavior.match_rule!r}") from None
    return fn(behavior, output, surface)
