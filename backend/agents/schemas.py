"""Pydantic schemas used by extractor, tone, and fact-checker nodes.

JudgeVerdictSchema (bottom of file) is the one exception — Document 47 §9
names `agents/schemas.py`'s existing convention as where the M11 Phase C
judge's structured-output schema belongs, even though the judge is
evaluation infrastructure, not a production pipeline node. Purely additive;
no schema above it is touched."""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


class FinancialsSchema(BaseModel):
    revenue: Optional[str] = Field(default=None, description="Total revenue (with unit, e.g. '$94.9B')")
    revenue_yoy: Optional[str] = Field(default=None, description="Year-over-year revenue growth, e.g. '+6%'")
    eps: Optional[str] = Field(default=None, description="Diluted EPS, e.g. '$1.64'")
    net_income: Optional[str] = Field(default=None, description="Net income, e.g. '$25.0B'")
    operating_margin: Optional[str] = Field(default=None, description="Operating margin %, e.g. '30.2%'")
    free_cash_flow: Optional[str] = Field(default=None, description="Free cash flow, e.g. '$25.9B'")
    guidance: Optional[str] = Field(default=None, description="Forward guidance quoted or summarized")


class ToneSchema(BaseModel):
    sentiment: str = Field(description="One of: Bullish, Bearish, Neutral")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence 0..1")
    summary: str = Field(description="Two-to-three sentence summary of management tone")
    key_risks: list[str] = Field(default_factory=list, description="Top 3-5 risk factors")
    key_positives: list[str] = Field(default_factory=list, description="Top 3-5 positive drivers")


class ClaimCheck(BaseModel):
    claim: str = Field(default="", description="A specific factual/numeric claim from the draft")
    claim_id: Optional[int] = Field(default=None, description="1-based index of the checked claim, if the model references it by number")
    supported: bool = Field(description="Whether the claim is directly supported by source docs")
    evidence: Optional[str] = Field(default=None, description="Quoted supporting text, if any")
    reason: Optional[str] = Field(default=None, description="Explanation when not supported")


class FactCheckSchema(BaseModel):
    claims: list[ClaimCheck] = Field(default_factory=list)


class ComparisonSourceSchema(BaseModel):
    """One entry in a comparison explanation's citation list (M9.1, Document 43 §10).
    `report_number` is a 1-based index into the reports supplied in the prompt, NOT a
    real database id — the server maps it to the actual `report_id` after validation
    (agents/comparison_explanation.py), so the model is never trusted to emit a real id."""
    index: int = Field(description="1-based citation index; matches an [n] marker in narrative")
    report_number: int = Field(description="1-based index into the provided reports list this claim is grounded in")
    field: str = Field(description="One of: extracted_data, sentiment_analysis, scorecard, report")


class ComparisonLimitationSchema(BaseModel):
    report_number: Optional[int] = Field(
        default=None, description="1-based index of the report with missing/non-comparable data, if attributable to one specific report"
    )
    metric: str = Field(description="The metric or field that is missing or non-comparable")
    reason: str = Field(description="Short, plain-language reason the data is unavailable — never a fabricated value")


class ComparisonExplanationSchema(BaseModel):
    """Structured output for M9.1 comparison explanation (Level 2 — Semantic
    Interpretation, Document 42). `narrative` must cite every material claim via
    inline [n] markers resolved against `sources`; `limitations` names evidence gaps
    explicitly rather than inferring/estimating them (Document 42 §11)."""
    narrative: str = Field(description="Plain-language explanation of the meaningful differences, with inline [n] citation markers for every material claim")
    sources: list[ComparisonSourceSchema] = Field(default_factory=list)
    cited_source_indices: list[int] = Field(
        default_factory=list, description="1-based indices into sources that are actually referenced by [n] markers in narrative"
    )
    limitations: list[ComparisonLimitationSchema] = Field(
        default_factory=list, description="Explicit evidence gaps for data that is missing or non-comparable — never invent a value to fill these"
    )


class ChangeBriefNarrativeSourceSchema(BaseModel):
    """One citation entry for a single `report`-mode change item (M15 / C-4,
    Document 70 R4 §11.3). `report_number` is a 1-based index into the two
    reports supplied in the prompt (1 = baseline, 2 = current), NOT a real
    database id — the server maps it to the actual `report_id` after
    per-item validation (agents/change_brief_narrative.py), so the model is
    never trusted to emit a real id (identical discipline to
    ComparisonSourceSchema)."""
    index: int = Field(description="1-based citation index; matches an [n] marker in explanation")
    report_number: int = Field(description="1-based: 1 = baseline report, 2 = current report")
    field: str = Field(description="One of: extracted_data, sentiment_analysis, scorecard, report")


class ChangeBriefNarrativeItemSchema(BaseModel):
    """One discrete narrative change claim (Document 70 R4 §8.3 / §11.3). Each
    item is independently cited; every emitted item must cite at least one
    source from the baseline report AND at least one from the current report
    (the both-sides rule, enforced deterministically after generation)."""
    summary: str = Field(description="One short sentence naming the single discrete change")
    explanation: str = Field(description="Plain-language explanation with inline [n] citation markers for every claim")
    sources: list[ChangeBriefNarrativeSourceSchema] = Field(default_factory=list)
    cited_source_indices: list[int] = Field(
        default_factory=list, description="1-based indices into sources actually referenced by [n] markers in explanation"
    )


class ChangeBriefNarrativeLimitationSchema(BaseModel):
    """An evidence-coverage gap: a topic evidenced on only one side, so whether
    it genuinely changed cannot be confirmed (Document 70 R4 §14.2). One input
    signal to the `partial` determination — never the sole authority
    (Document 73 R1 §10)."""
    topic: str = Field(description="The specific topic/metric evidenced on only one side")
    missing_side: str = Field(description="Which side lacks corroborating evidence: 'baseline' or 'current'")


class ChangeBriefNarrativeSchema(BaseModel):
    """Structured output for M15 / C-4 `report`-mode narrative comparison
    (Document 73 R1 §10/§11 — a structured schema extension, not a
    post-generation text decomposition). A bounded list of discrete,
    individually-cited change claims plus explicit one-sided-evidence
    limitations."""
    items: list[ChangeBriefNarrativeItemSchema] = Field(default_factory=list)
    limitations: list[ChangeBriefNarrativeLimitationSchema] = Field(
        default_factory=list, description="Topics evidenced on only one side — never invent the missing side's content"
    )


class JudgeVerdictSchema(BaseModel):
    """M11 Phase C — Document 47 §7.2/§7.3/§9's model-judged-support judge.
    Evaluates ONLY whether the supplied evidence supports the supplied claim
    — the judge never selects which claim or evidence to look at (§7.0's own
    load-bearing rule; that selection is done deterministically before this
    schema is ever populated), and is never asked for investment advice,
    general fact-checking, or open-ended quality scoring."""
    verdict: Literal["SUPPORTED", "CONTRADICTED", "UNSUPPORTED", "NOT_APPLICABLE"] = Field(
        description="SUPPORTED: the evidence directly supports the claim. CONTRADICTED: the evidence "
                    "itself states a fact or substantive position incompatible with the claim. Mere "
                    "absence of information, guidance, disclosure, or a stated position is UNSUPPORTED, "
                    "not CONTRADICTED. A substantive negation of the claim's proposition may still be "
                    "CONTRADICTED. UNSUPPORTED: the evidence neither supports nor contradicts the claim. "
                    "NOT_APPLICABLE: the evidence concerns a different entity, or a genuinely different "
                    "underlying quantity or business fact than the claim asserts — not merely similar "
                    "wording, topic, or numbers, and not merely a difference in tense, modality, or "
                    "polarity — including a reported level versus that same quantity's change or "
                    "expected change over time, or a statement of fact versus an expectation, plan, "
                    "or disclosure-existence statement about that same fact, all of which remain the "
                    "same underlying quantity. Evidence "
                    "about the same underlying quantity or business fact remains "
                    "applicable even when it differs from the claim in those ways. Evidence that is "
                    "relevant in that sense but simply fails to confirm the claim is UNSUPPORTED, not "
                    "NOT_APPLICABLE."
    )
    rationale: str = Field(
        description="One or two sentences explaining the verdict — documentation only, never re-parsed "
                    "or matched as structured truth (Document 47 §7.3)"
    )


class ApplicabilityVerdictSchema(BaseModel):
    """M11 Phase E — Document 47 §7.3.1's relevance-first applicability
    decision as its own, structurally separate output (Phase D's Option B:
    a genuine control-flow boundary, not a field added to JudgeVerdictSchema).
    Evaluates ONLY whether EVIDENCE is genuinely relevant to CLAIM — never
    whether it supports, contradicts, or fails to confirm CLAIM; that
    decision belongs to SupportVerdictSchema, reached only when applicability
    is APPLICABLE."""
    applicability: Literal["APPLICABLE", "NOT_APPLICABLE"] = Field(
        description="APPLICABLE: EVIDENCE concerns the same underlying entity/subject and the same "
                    "underlying quantity or business fact CLAIM asserts something about — even when it "
                    "differs from CLAIM in tense, time period, modality, or polarity (a reported level vs. "
                    "that quantity's change, or a statement of fact vs. an expectation, plan, or "
                    "disclosure-existence statement about the same fact, are the same underlying quantity, "
                    "not different ones). Evidence that is applicable in this sense but simply fails to "
                    "confirm CLAIM is still APPLICABLE. NOT_APPLICABLE: EVIDENCE concerns a different "
                    "entity, or a genuinely different underlying quantity or business fact than CLAIM "
                    "asserts — not merely similar wording, topic, or numbers."
    )
    rationale: str = Field(
        description="One or two sentences explaining the applicability decision — documentation only, "
                    "never re-parsed or matched as structured truth (Document 47 §7.3)"
    )


class SupportVerdictSchema(BaseModel):
    """M11 Phase E — the support-classification stage, invoked only after
    ApplicabilityVerdictSchema has already determined EVIDENCE is APPLICABLE.
    Never outputs NOT_APPLICABLE: that decision has already been made by a
    separate, prior call and is structurally unreachable here."""
    verdict: Literal["SUPPORTED", "UNSUPPORTED", "CONTRADICTED"] = Field(
        description="SUPPORTED: the evidence directly supports the claim. CONTRADICTED: the evidence "
                    "itself states a fact or substantive position incompatible with the claim. Mere "
                    "absence of information, guidance, disclosure, or a stated position is UNSUPPORTED, "
                    "not CONTRADICTED. A substantive negation of the claim's proposition may still be "
                    "CONTRADICTED. UNSUPPORTED: the evidence neither supports nor contradicts the claim."
    )
    rationale: str = Field(
        description="One or two sentences explaining the verdict — documentation only, never re-parsed "
                    "or matched as structured truth (Document 47 §7.3)"
    )
