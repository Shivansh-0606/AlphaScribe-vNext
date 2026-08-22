"""M10 Phase 3 — deterministic evaluators for Document 45 §7's three frozen
ExpectedBehavior rule types, plus Document 47 Phase A's `numeric_consistency`
and Phase C's `model_judged_support` (Document 47 §7.0-§7.3). One small
function per rule, each independently testable, none containing another's
logic (this task's §10).

Four of the five evaluators make no LLM call and return deterministically,
reading only `NormalizedOutput` and (numeric_consistency/model_judged_support)
the case's own `context` dict. `evaluate_model_judged_support` is the one
exception (M11 Phase C, restructured into two calls by M11 Phase E's
structured-applicability architecture) — it makes one or two `chat_json`
calls through `evaluation/core/judge.py`, which is why `evaluate_behavior`
below is `async`. Every judge-execution failure still maps to a
deterministic outcome (INCONCLUSIVE, Document 47 §7.3) — the module's
determinism guarantee is about *failure handling*, not about avoiding the
LLM call Document 47 itself authorizes.

Two rule types (citation_required, limitation_reference) have a reported,
NOT silently resolved, gap against this task's own request — see each
function's own docstring below for the specifics.
"""
from __future__ import annotations

import json
import re

from agents.llm import _active
from evaluation.adapters.types import Citation, NormalizedOutput
from evaluation.core.judge import (
    APPLICABILITY_PROMPT_VERSION,
    JUDGE_ARCHITECTURE_VERSION,
    SUPPORT_PROMPT_VERSION,
    invoke_applicability_judge,
    invoke_support_judge,
)
from evaluation.core.types import BehaviorEvaluation, JudgeDetail, Status
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


# ---------------------------------------------------------------------------
# numeric_consistency (Document 47 §7.0 shared selector + §7.1) — Phase A.
# Research/Learning only; rejected at BenchmarkCase construction time for
# Comparison Explanation (golden_dataset/models.py), never reached here for
# that surface.
# ---------------------------------------------------------------------------

# Document 47 §7.0 step 2: the same sentence-boundary split and [n]-marker
# regex every citation-validation function in this repo already applies.
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.?!])\s+")
_MARKER_RE = re.compile(r"\[(\d+)\]")

# Document 47 §7.1: "reuses the existing numeric-token regex already in this
# codebase" — agents/nodes.py::_extract_candidate_claims's own `number_re`.
# Duplicated, not imported: that regex is a function-local variable, not a
# module constant, and agents/nodes.py is a production pipeline file this
# phase must not touch.
#
# CTO-review fix: the source regex's currency/percentage alternatives carry
# no leading [+-]?, unlike its own bps/pp alternative — a real defect for
# this module's use (exact-value comparison, where "-5%" vs "+5%" is not the
# same claim), even though it doesn't matter for the source function's own
# purpose (flagging *that* a sentence has a number, not its sign). Fixed here
# by extending the existing bps/pp alternative's own [+-]? convention to the
# other two, not by introducing a new grammar.
_NUMERIC_TOKEN_RE = re.compile(r"[+-]?\$[\d,\.]+[MBK]?|[+-]?\d+(?:\.\d+)?\s?%|[+-]?\d+(?:\.\d+)?\s?(?:bps|pp)")

# Document 47 §7.1: a reference path's leading segment, e.g. "source_documents[0]".
_PATH_SEGMENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\[(\d+)\]$")


def _resolve_reference_path(context: dict, reference: str) -> tuple[bool, object]:
    """Document 47 §7.1: `reference` is a dotted/bracket path into
    `case.context`, resolved by plain stdlib dict/list traversal — no
    jsonpath dependency. Returns (resolved, value); (False, None) for any
    missing key/index or a resolved-but-None value — the 'construction
    failure -> INCONCLUSIVE' case §7.1 requires, never raised as an error.

    ponytail: the expected value this resolves is whatever the case author
    wrote into `context` — in LIVE mode (evaluation/adapters/research.py,
    .../learning.py) that is NOT automatically kept in sync with what a real
    retrieval actually returns; nothing in this module reads or verifies
    live retrieval output against it. A stale case-authored figure produces
    a confidently-wrong PASS/FAIL against real (LIVE-mode) generated text,
    not an error — this is a known ceiling of case-authored context, not a
    guarantee of live regression correctness. Upgrade path: bind the
    expected value to the same retrieval the surface itself used for that
    run, which needs adapter-level plumbing this phase does not add
    (Research/Learning FIXTURE mode is the same, already-deferred gap,
    Document 45 §11.1)."""
    current: object = context
    for segment in reference.split("."):
        m = _PATH_SEGMENT_RE.match(segment)
        if m:
            name, idx = m.group(1), int(m.group(2))
            if not isinstance(current, dict) or name not in current:
                return False, None
            current = current[name]
            if not isinstance(current, list) or not (0 <= idx < len(current)):
                return False, None
            current = current[idx]
        else:
            if not isinstance(current, dict) or segment not in current:
                return False, None
            current = current[segment]
    if current is None:
        return False, None
    return True, current


def _normalize_numeric_token(token: str) -> float | None:
    """Document 47 §7.1: '$/%/bps/pp and M/B/K suffixes converted to a
    consistent scale' — standard, unambiguous financial convention only
    (100 bps = 1 percentage point; M/B/K are the literal magnitude), nothing
    invented beyond what §7.1 itself names.

    CTO-review fix: a leading sign is stripped once, up front, and reapplied
    to the final value — every suffix branch below shares it, so "-5%" and
    "+5%" (or "-$95M"/"+$95M") no longer collapse to the same magnitude."""
    t = token.strip()
    sign = 1.0
    if t and t[0] in "+-":
        sign, t = (-1.0 if t[0] == "-" else 1.0), t[1:]
    try:
        if t.startswith("$"):
            body = t[1:]
            suffix = ""
            if body and body[-1] in "MBK":
                suffix, body = body[-1], body[:-1]
            value = float(body.replace(",", ""))
            return sign * value * {"K": 1e3, "M": 1e6, "B": 1e9}.get(suffix, 1.0)
        if t.endswith("%"):
            return sign * float(t[:-1].strip())
        if t.endswith("bps"):
            return sign * float(t[:-3].strip()) / 100.0
        if t.endswith("pp"):
            return sign * float(t[:-2].strip())
        return sign * float(t)
    except ValueError:
        return None


def _coerce_expected_value(raw: object) -> float | None:
    """The fixture value at `reference` may already be a JSON number, or a
    formatted string (e.g. "$94.9B") matching the same convention generated
    text uses — reuses the identical extraction/normalization as the claim
    side, not a second numeric semantic. None (unresolvable) for a bool, a
    non-numeric string, or a string with zero/multiple numeric tokens —
    never guessed."""
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        tokens = _NUMERIC_TOKEN_RE.findall(raw)
        if len(tokens) == 1:
            return _normalize_numeric_token(tokens[0])
    return None


def _leading_source_id(reference: str) -> str | None:
    """Document 47 §7.0 step 1 (Research/Learning only, verified positional
    by direct read of evaluation/adapters/research.py and .../learning.py):
    `reference`'s leading array index k maps to `source_id = str(k + 1)` —
    the exact same 1-based numbering those adapters already build
    Citation.source_id from. None if `reference` has no such leading segment."""
    first_segment = reference.split(".", 1)[0]
    m = _PATH_SEGMENT_RE.match(first_segment)
    if not m:
        return None
    return str(int(m.group(2)) + 1)


def _resolve_eligible_citation(output: NormalizedOutput, source_id: str) -> Citation | None:
    """Document 47 §7.0 step 1's shared eligibility check — used by both
    `numeric_consistency` and `model_judged_support` (M11 Phase C extracted
    this out of what was, in Phase A, inline logic inside
    evaluate_numeric_consistency; that function's own behavior is unchanged,
    only this check's location moved). Returns the matching Citation only if
    it exists AND is eligible; None otherwise — the caller maps None to
    INCONCLUSIVE, never FAIL. The judge, and the numeric comparator, must
    never be handed fabricated or ineligible evidence dressed up as
    legitimate evidence (Document 47 §7.0)."""
    citation = next((c for c in output.citations if c.source_id == source_id), None)
    if citation is None or not citation.eligible:
        return None
    return citation


def _resolve_evidence_text(context: dict, source_id: str) -> str | None:
    """Document 47 §7.2: the evidence text for `model_judged_support` is the
    fixture/live `source_documents` entry at `source_id`'s 1-based index
    (`str(k + 1)` -> `source_documents[k]` — the exact convention Research/
    Learning's adapters already use to build Citation.source_id,
    evaluation/adapters/research.py and .../learning.py). Prefers the `text`
    field production retrieval already populates
    (agents/nodes.py::_format_docs's own `d.get("text", "")` convention),
    falling back to a deterministic JSON dump of the whole entry for fixture
    content that doesn't use that shape — never silently drops information
    by guessing a field. None (-> INCONCLUSIVE, never guessed) if
    `source_documents` is missing/malformed or the index is out of range.

    ponytail: same LIVE-mode ceiling `_resolve_reference_path` already
    documents for numeric_consistency, applying here too — LIVE-mode
    Research/Learning adapters (evaluation/adapters/research.py,
    .../learning.py) never populate `context["source_documents"]` at all
    (that's the case author's fixture data, not live retrieval output), so
    this function's `evidence` is only ever what a case author wrote down,
    never automatically bound to what a real LIVE run actually retrieved.
    Not currently regression-grade against LIVE retrieval for that reason —
    a stale case-authored evidence string produces a confident judge verdict
    against evidence the live pipeline may not have used at all, silently.
    Upgrade path is the same already-deferred one: Research/Learning
    FIXTURE mode (Document 45 §11.1), not solved here."""
    docs = context.get("source_documents")
    if not isinstance(docs, list):
        return None
    try:
        idx = int(source_id) - 1
    except ValueError:
        return None
    if not (0 <= idx < len(docs)):
        return None
    entry = docs[idx]
    if isinstance(entry, str):
        return entry or None
    if isinstance(entry, dict):
        text = entry.get("text")
        if isinstance(text, str) and text.strip():
            return text
        return json.dumps(entry, sort_keys=True)
    return None


_JUDGE_VERDICT_TO_STATUS: dict[str, tuple[Status, str]] = {
    # Document 47 §7.3's frozen table. Judge failure/uncertainty never
    # produces FAIL — NOT_APPLICABLE (a genuine, well-formed verdict) maps to
    # INCONCLUSIVE here; provider/malformed-output/timeout failures never
    # reach this table at all (evaluate_model_judged_support's exception
    # boundary maps those to INCONCLUSIVE directly, before a verdict exists).
    "SUPPORTED": ("PASS", "judge verdict SUPPORTED"),
    "CONTRADICTED": ("FAIL", "judge verdict CONTRADICTED"),
    "UNSUPPORTED": ("FAIL", "judge verdict UNSUPPORTED"),
    "NOT_APPLICABLE": ("INCONCLUSIVE", "judge verdict NOT_APPLICABLE"),
}


def _select_single_claim_sentence(text: str, source_id: str) -> tuple[str | None, str | None]:
    """Document 47 §7.0 steps 2-5, the shared claim selector: the single
    sentence in `text` carrying citation marker [source_id]. Returns
    (sentence, None) on success, or (None, reason) when selection is empty
    or ambiguous — always INCONCLUSIVE at the call site, never guessed.

    §7.0 step 4's own wording covers repetition "whether in one sentence
    repeated or across multiple sentences" — CTO-review fix: the check below
    previously only counted matching *sentences* (membership), so the same
    marker occurring twice inside one otherwise-unambiguous sentence (e.g.
    "$95M [1], confirmed by the same filing [1].") was wrongly accepted as a
    single, unambiguous match. Now counts actual occurrences of `source_id`,
    not just its presence — unrelated markers in the same sentence (e.g. a
    co-occurring [2]) are untouched, since only `source_id`'s own count is
    checked."""
    sentences = _SENTENCE_SPLIT_RE.split(text)
    matches = [s for s in sentences if source_id in _MARKER_RE.findall(s)]
    if not matches:
        return None, f"no sentence in the output carries citation marker [{source_id}]"
    if len(matches) > 1:
        return None, (
            f"citation marker [{source_id}] appears in {len(matches)} sentences — "
            "ambiguous, not evaluated (Document 47 §7.0 step 4)"
        )
    sentence = matches[0]
    occurrences = _MARKER_RE.findall(sentence).count(source_id)
    if occurrences > 1:
        return None, (
            f"citation marker [{source_id}] appears {occurrences} times in the selected "
            "sentence — ambiguous, not evaluated (Document 47 §7.0 step 4)"
        )
    return sentence, None


def evaluate_numeric_consistency(
    behavior: ExpectedBehavior, output: NormalizedOutput, *, surface: Surface, context: dict,
) -> BehaviorEvaluation:
    """Document 47 §7.0 (shared selector) + §7.1 (numeric-specific rules).
    Research/Learning only — BenchmarkCase construction already rejects this
    match_rule for comparison_explanation (golden_dataset/models.py); the
    check below is defense in depth, matching evaluate_limitation_reference's
    own surface-awareness precedent."""
    if surface == "comparison_explanation":
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE",
            "numeric_consistency is not supported for surface='comparison_explanation' (Document 47 §7.0)",
        )

    reason = no_output_reason(output)
    if reason:
        return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE", reason)

    reference = behavior.reference  # non-empty, enforced by ExpectedBehavior._check_combination
    resolved, expected_raw = _resolve_reference_path(context, reference)
    if not resolved:
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE",
            f"reference {reference!r} does not resolve against case.context (missing/None) — "
            "a dataset-authoring problem, not a quality signal",
        )
    expected_value = _coerce_expected_value(expected_raw)
    if expected_value is None:
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE",
            f"reference {reference!r} resolved to a non-numeric value ({expected_raw!r})",
        )

    source_id = _leading_source_id(reference)
    if source_id is None:
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE",
            f"reference {reference!r} has no leading name[index] segment to resolve a citation source_id from",
        )

    citation = _resolve_eligible_citation(output, source_id)
    if citation is None:
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE",
            f"source_id {source_id!r} is not present/eligible in NormalizedOutput.citations",
        )

    sentence, selector_reason = _select_single_claim_sentence(output.text, source_id)
    if sentence is None:
        return BehaviorEvaluation(behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE", selector_reason)

    tokens = _NUMERIC_TOKEN_RE.findall(sentence)
    if len(tokens) > 1:
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE",
            f"selected claim sentence contains {len(tokens)} numeric tokens {tokens} — "
            "ambiguous, not evaluated (Document 47 §7.1)",
        )
    if not tokens:
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "FAIL",
            f"selected claim sentence contains no numeric value: {sentence!r}",
        )

    claim_value = _normalize_numeric_token(tokens[0])
    if claim_value is None:
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "FAIL",
            f"could not parse numeric token {tokens[0]!r} in claim sentence",
        )

    # Document 47 §7.1: zero expected value -> exact equality (relative
    # tolerance is undefined at zero); non-zero -> relative tolerance.
    if expected_value == 0:
        within = claim_value == 0
    else:
        within = abs(claim_value - expected_value) <= behavior.tolerance * abs(expected_value)

    if within:
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "PASS",
            f"claim value {claim_value} matches expected {expected_value} (tolerance={behavior.tolerance})",
        )
    return BehaviorEvaluation(
        behavior.behavior_id, behavior.match_rule, "FAIL",
        f"claim value {claim_value} does not match expected {expected_value} (tolerance={behavior.tolerance})",
    )


async def evaluate_model_judged_support(
    behavior: ExpectedBehavior, output: NormalizedOutput, *, surface: Surface, context: dict,
) -> BehaviorEvaluation:
    """Document 47 §7.0 (shared selector) + §7.2 (model_judged_support) +
    §7.3 (frozen verdict->status mapping) — M11 Phase C, restructured by M11
    Phase E's structured-applicability architecture (Document 47 Phase D
    architecture review's Option B).

    Research/Learning only — BenchmarkCase construction already rejects this
    match_rule for comparison_explanation
    (golden_dataset/models.py::_check_research_learning_only_rules_surface);
    the check below is defense in depth, matching
    evaluate_numeric_consistency's own precedent.

    The judge never selects the claim or the evidence — both come from the
    same deterministic §7.0 selector numeric_consistency already uses,
    computed before either judge stage is ever called (§7's load-bearing
    rule: the judge only adjudicates).

    Control flow (Phase E's genuine boundary, not merely an added field):
    Stage 1 (applicability) always runs first. Any Stage 1 failure (provider
    error, timeout, retry exhaustion, malformed/schema-invalid output — an
    unknown applicability value included, since chat_json's own schema
    validation already rejects it before this function could ever see one)
    maps to INCONCLUSIVE and Stage 2 never runs. A well-formed NOT_APPLICABLE
    from Stage 1 is terminal — INCONCLUSIVE per §7.3's table, Stage 2 never
    runs. Only a well-formed APPLICABLE invokes Stage 2 (support
    classification), whose own failure likewise maps to INCONCLUSIVE, never
    to any of SUPPORTED/UNSUPPORTED/CONTRADICTED/NOT_APPLICABLE — Document
    47 §7.3's frozen rule, unchanged by the staging, via two narrow exception
    boundaries instead of one, not a new exception taxonomy."""
    if surface == "comparison_explanation":
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE",
            "model_judged_support is not supported for surface='comparison_explanation' (Document 47 §7.0)",
            judged_by="model",
        )

    reason = no_output_reason(output)
    if reason:
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE", reason, judged_by="model",
        )

    source_id = behavior.reference  # IS the source_id directly (§7.2) — non-empty, enforced by ExpectedBehavior
    citation = _resolve_eligible_citation(output, source_id)
    if citation is None:
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE",
            f"source_id {source_id!r} is not present/eligible in NormalizedOutput.citations",
            judged_by="model",
        )

    sentence, selector_reason = _select_single_claim_sentence(output.text, source_id)
    if sentence is None:
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE", selector_reason, judged_by="model",
        )

    evidence = _resolve_evidence_text(context, source_id)
    if evidence is None:
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE",
            f"source_id {source_id!r}'s evidence content could not be resolved from case.context",
            judged_by="model",
        )

    try:
        applicability_result = await invoke_applicability_judge(sentence, evidence)
    except Exception as e:  # noqa: BLE001 — Stage 1 failure: INCONCLUSIVE, Stage 2 never runs.
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE",
            f"applicability judge invocation failed: {e}",
            judged_by="model",
        )

    judge_model = _active().get("light")  # DEFAULT_LIGHT_MODEL tier resolved, same convention as ExecutionMetadata.model

    if applicability_result.applicability == "NOT_APPLICABLE":
        status, verdict_reason = _JUDGE_VERDICT_TO_STATUS["NOT_APPLICABLE"]
        detail = JudgeDetail(
            judge_model=judge_model,
            judge_prompt_version=JUDGE_ARCHITECTURE_VERSION,
            verdict="NOT_APPLICABLE",
            rationale=applicability_result.rationale,
            applicability="NOT_APPLICABLE",
            applicability_rationale=applicability_result.rationale,
            applicability_prompt_version=APPLICABILITY_PROMPT_VERSION,
        )
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, status,
            f"{verdict_reason}: {applicability_result.rationale}",
            judged_by="model", judge_detail=detail,
        )

    try:
        support_result = await invoke_support_judge(sentence, evidence)
    except Exception as e:  # noqa: BLE001 — Stage 2 failure: INCONCLUSIVE, same as Stage 1's.
        return BehaviorEvaluation(
            behavior.behavior_id, behavior.match_rule, "INCONCLUSIVE",
            f"support judge invocation failed: {e}",
            judged_by="model",
        )

    status, verdict_reason = _JUDGE_VERDICT_TO_STATUS[support_result.verdict]
    detail = JudgeDetail(
        judge_model=judge_model,
        judge_prompt_version=JUDGE_ARCHITECTURE_VERSION,
        verdict=support_result.verdict,
        rationale=support_result.rationale,
        applicability="APPLICABLE",
        applicability_rationale=applicability_result.rationale,
        applicability_prompt_version=APPLICABILITY_PROMPT_VERSION,
        support_prompt_version=SUPPORT_PROMPT_VERSION,
    )
    return BehaviorEvaluation(
        behavior.behavior_id, behavior.match_rule, status,
        f"{verdict_reason}: {support_result.rationale}",
        judged_by="model", judge_detail=detail,
    )


async def _dispatch_keyword_variant(behavior, output, surface, context) -> BehaviorEvaluation:
    return evaluate_keyword_variant(behavior, output)


async def _dispatch_citation_required(behavior, output, surface, context) -> BehaviorEvaluation:
    return evaluate_citation_required(behavior, output)


async def _dispatch_limitation_reference(behavior, output, surface, context) -> BehaviorEvaluation:
    return evaluate_limitation_reference(behavior, output, surface=surface)


async def _dispatch_numeric_consistency(behavior, output, surface, context) -> BehaviorEvaluation:
    return evaluate_numeric_consistency(behavior, output, surface=surface, context=context)


async def _dispatch_model_judged_support(behavior, output, surface, context) -> BehaviorEvaluation:
    return await evaluate_model_judged_support(behavior, output, surface=surface, context=context)


# M11 Phase C: evaluate_behavior became async (below) because this one entry
# makes a real chat_json call; the other four are still purely synchronous
# under the hood — each dispatch wrapper is `async def` only because Python
# lambdas can't be, not because the four deterministic evaluators changed.
_EVALUATORS = {
    "keyword_variant": _dispatch_keyword_variant,
    "citation_required": _dispatch_citation_required,
    "limitation_reference": _dispatch_limitation_reference,
    "numeric_consistency": _dispatch_numeric_consistency,
    "model_judged_support": _dispatch_model_judged_support,
}


async def evaluate_behavior(
    behavior: ExpectedBehavior, output: NormalizedOutput, *, surface: Surface, context: dict,
) -> BehaviorEvaluation:
    """Dispatch by `behavior.match_rule` to the one matching evaluator above.
    `match_rule` is a Pydantic Literal (evaluation/golden_dataset/models.py)
    — the KeyError branch below is unreachable through any validated
    BenchmarkCase, kept only as a defensive guard.

    Async (M11 Phase C) because `model_judged_support` makes a real
    `chat_json` call — the four deterministic evaluators' own logic is
    unchanged; only this dispatch function and its caller
    (evaluation/core/case_evaluator.py::evaluate_case) needed one `await`
    added each."""
    try:
        fn = _EVALUATORS[behavior.match_rule]
    except KeyError:
        raise ValueError(f"unsupported match_rule {behavior.match_rule!r}") from None
    return await fn(behavior, output, surface, context)
