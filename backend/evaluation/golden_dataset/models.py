"""M10 Phase 1 — golden benchmark dataset models (Document 45 §7).

Pydantic, not a dataclass (unlike domain/models.py's pure in-process state) —
these cross a JSON-file boundary, the same rationale agents/schemas.py's
LLM-JSON-boundary models already follow in this repository.

This module defines the dataset *shape* only. Surface adapters, AI execution,
evaluation, and regression comparison are later M10 phases (Document 45 §11+)
and are deliberately not implemented here (Document 45 §21's own separation:
the dataset schema imports nothing from `agents/`).
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

Surface = Literal["research", "learning", "comparison_explanation"]
BehaviorType = Literal["presence", "absence", "acknowledgment"]
# Document 47 §7 adds "numeric_consistency" (Phase A) and "model_judged_support"
# (Phase C) to Document 45 §7's original three — additive schema extensions,
# not a redesign; the three original rules' validation is unchanged (see
# _check_combination below).
MatchRule = Literal[
    "keyword_variant", "citation_required", "limitation_reference",
    "numeric_consistency", "model_judged_support",
]

# Document 45 §7's constraint table, extended by Document 47 §7 with two more
# rows (numeric_consistency, model_judged_support -> both presence only).
_ALLOWED_TYPES_BY_RULE: dict[str, tuple[str, ...]] = {
    "keyword_variant": ("presence", "absence"),
    "citation_required": ("presence",),
    "limitation_reference": ("acknowledgment",),
    "numeric_consistency": ("presence",),
    "model_judged_support": ("presence",),
}

# Document 47 §7.0: match_rules whose source_id resolution is verified
# positional/direct only for Research/Learning (evaluation/adapters/
# research.py, .../learning.py) — Comparison Explanation's Citation.source_id
# is f"{report_id}:{field_name}", decoupled from both fixture array order and
# the narrative's own [n] marker numbers. Shared by numeric_consistency
# (Phase A) and model_judged_support (Phase C) — one set, not two checks.
_RESEARCH_LEARNING_ONLY_RULES: frozenset[str] = frozenset({"numeric_consistency", "model_judged_support"})

# Document 45 §7/§11: the surface-appropriate context keys named by the
# architecture (Research: ticker+query; Learning: ticker+concept; Comparison
# Explanation: a list of report references). Adapter-level interpretation of
# these values belongs to Phase 2 — this only checks the keys exist.
_CONTEXT_KEYS_BY_SURFACE: dict[str, tuple[str, ...]] = {
    "research": ("ticker", "query"),
    "learning": ("ticker", "concept"),
    "comparison_explanation": ("report_ids",),
}


class ExpectedBehavior(BaseModel):
    """One executable behavioral assertion (Document 45 §7's structured
    representation — never a free-form string). `description` documents
    intent for a human reviewer only; the check always executes against
    `match_rule` + `variants`/`reference`, never against `description` itself."""

    behavior_id: str = Field(min_length=1, description="Unique within the case")
    type: BehaviorType
    description: str = Field(min_length=1, description="Human-readable only — never parsed or matched")
    match_rule: MatchRule
    variants: list[str] | None = Field(
        default=None,
        description="Required (non-empty) only for match_rule='keyword_variant'; forbidden otherwise",
    )
    reference: str | None = Field(
        default=None,
        description="Required only for match_rule in ('citation_required', 'limitation_reference', "
                    "'numeric_consistency', 'model_judged_support'); forbidden for 'keyword_variant'",
    )
    tolerance: float | None = Field(
        default=None,
        description="Required (non-negative relative fraction, e.g. 0.01 = 1%) only for "
                    "match_rule='numeric_consistency' (Document 47 §7.1); forbidden otherwise",
    )

    @model_validator(mode="after")
    def _check_combination(self) -> "ExpectedBehavior":
        # Document 45 §7's constraint table, enforced — not documentation-only.
        # Document 47 §7 adds one more row (numeric_consistency) below.
        allowed_types = _ALLOWED_TYPES_BY_RULE[self.match_rule]
        if self.type not in allowed_types:
            raise ValueError(
                f"behavior {self.behavior_id!r}: match_rule={self.match_rule!r} requires "
                f"type in {allowed_types}, got type={self.type!r}"
            )
        if self.match_rule == "keyword_variant":
            if not self.variants or not all(v.strip() for v in self.variants):
                raise ValueError(
                    f"behavior {self.behavior_id!r}: match_rule='keyword_variant' requires "
                    f"a non-empty 'variants' list of non-blank strings"
                )
            if self.reference is not None:
                raise ValueError(
                    f"behavior {self.behavior_id!r}: match_rule='keyword_variant' forbids 'reference'"
                )
            if self.tolerance is not None:
                raise ValueError(
                    f"behavior {self.behavior_id!r}: match_rule='keyword_variant' forbids 'tolerance'"
                )
        elif self.match_rule == "numeric_consistency":
            # Document 47 §7.1: reference is required (the fixture-evidence
            # path that resolves both the expected value and, via its leading
            # index, the citation source_id — §7.0 step 1); variants forbidden
            # (this rule matches numbers, not phrases); tolerance required and
            # non-negative — never a hidden repository-wide default.
            if not self.reference or not self.reference.strip():
                raise ValueError(
                    f"behavior {self.behavior_id!r}: match_rule='numeric_consistency' requires "
                    f"a non-empty 'reference'"
                )
            if self.variants is not None:
                raise ValueError(
                    f"behavior {self.behavior_id!r}: match_rule='numeric_consistency' forbids 'variants'"
                )
            if self.tolerance is None:
                raise ValueError(
                    f"behavior {self.behavior_id!r}: match_rule='numeric_consistency' requires "
                    f"'tolerance' (a non-negative relative fraction)"
                )
            if self.tolerance < 0:
                raise ValueError(
                    f"behavior {self.behavior_id!r}: 'tolerance' must be >= 0, got {self.tolerance!r}"
                )
        elif self.match_rule == "model_judged_support":
            # Document 47 §7.2: reference IS the source_id directly (unlike
            # numeric_consistency, no fixture path — the judge's evidence/claim
            # selector resolves everything else from it, §7.0). variants and
            # tolerance are both meaningless for a judge-adjudicated rule.
            if not self.reference or not self.reference.strip():
                raise ValueError(
                    f"behavior {self.behavior_id!r}: match_rule='model_judged_support' requires "
                    f"a non-empty 'reference' (a source_id)"
                )
            if self.variants is not None:
                raise ValueError(
                    f"behavior {self.behavior_id!r}: match_rule='model_judged_support' forbids 'variants'"
                )
            if self.tolerance is not None:
                raise ValueError(
                    f"behavior {self.behavior_id!r}: match_rule='model_judged_support' forbids 'tolerance'"
                )
        else:  # citation_required, limitation_reference
            if not self.reference or not self.reference.strip():
                raise ValueError(
                    f"behavior {self.behavior_id!r}: match_rule={self.match_rule!r} requires "
                    f"a non-empty 'reference'"
                )
            if self.variants is not None:
                raise ValueError(
                    f"behavior {self.behavior_id!r}: match_rule={self.match_rule!r} forbids 'variants'"
                )
            if self.tolerance is not None:
                raise ValueError(
                    f"behavior {self.behavior_id!r}: match_rule={self.match_rule!r} forbids 'tolerance'"
                )
        return self


class CitationExpectation(BaseModel):
    """Minimum grounding bar for a case (Document 45 §7) — the universal floor
    every surface already enforces in production (>=1 valid citation), with an
    optional, case-specific raised bar (e.g. a named source that must be cited)."""

    min_valid_citations: int = Field(default=1, ge=1)
    required_source_ids: list[str] = Field(default_factory=list)


class BenchmarkCase(BaseModel):
    """One golden-dataset case (Document 45 §7). Validates only the shape a
    case must have to exist at all — surface-specific interpretation of
    `context` (e.g. actually invoking Research/Learning/Comparison Explanation)
    belongs to the Phase 2 surface adapters, not this model."""

    case_id: str = Field(min_length=1)
    surface: Surface
    dataset_version: int = Field(ge=1)
    case_version: int = Field(ge=1)
    context: dict[str, object]
    expected_behaviors: list[ExpectedBehavior] = Field(min_length=1)
    expected_evidence: dict[str, object] | None = None
    citation_expectation: CitationExpectation
    known_limitations: list[str] | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _check_context_matches_surface(self) -> "BenchmarkCase":
        required = _CONTEXT_KEYS_BY_SURFACE[self.surface]
        missing = [k for k in required if not self.context.get(k)]
        if missing:
            raise ValueError(
                f"case {self.case_id!r}: surface={self.surface!r} requires non-empty "
                f"context key(s) {missing}"
            )
        return self

    @model_validator(mode="after")
    def _check_behavior_ids_unique(self) -> "BenchmarkCase":
        ids = [b.behavior_id for b in self.expected_behaviors]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise ValueError(f"case {self.case_id!r}: duplicate behavior_id(s) {sorted(dupes)}")
        return self

    @model_validator(mode="after")
    def _check_limitation_references_resolve(self) -> "BenchmarkCase":
        known = set(self.known_limitations or [])
        for b in self.expected_behaviors:
            if b.match_rule == "limitation_reference" and b.reference not in known:
                raise ValueError(
                    f"case {self.case_id!r}: behavior {b.behavior_id!r} references limitation "
                    f"{b.reference!r}, not present in known_limitations {sorted(known)}"
                )
        return self

    @model_validator(mode="after")
    def _check_research_learning_only_rules_surface(self) -> "BenchmarkCase":
        # Document 47 §7.0 (generalized for Phase C, Phase A behavior
        # unchanged): Citation.source_id for Comparison Explanation is
        # f"{report_id}:{field_name}" (evaluation/adapters/comparison_explanation.py)
        # — decoupled from fixture array order and from the narrative's own
        # [n] marker numbers, which the model assigns via its own declared
        # report_number mapping. Both numeric_consistency's positional
        # source_id resolution AND model_judged_support's reference-as-
        # source_id resolution are verified facts only for Research/Learning
        # (evaluation/adapters/research.py, .../learning.py). Rejected here,
        # at construction, not silently mis-evaluated later — one shared
        # check (_RESEARCH_LEARNING_ONLY_RULES), not two separate ones.
        if self.surface == "comparison_explanation":
            offenders = [
                b.behavior_id for b in self.expected_behaviors
                if b.match_rule in _RESEARCH_LEARNING_ONLY_RULES
            ]
            if offenders:
                offending_rules = sorted({
                    b.match_rule for b in self.expected_behaviors if b.behavior_id in offenders
                })
                raise ValueError(
                    f"case {self.case_id!r}: match_rule(s) {offending_rules} are not supported for "
                    f"surface='comparison_explanation' (Document 47 §7.0) — behavior(s) {offenders}"
                )
        return self
