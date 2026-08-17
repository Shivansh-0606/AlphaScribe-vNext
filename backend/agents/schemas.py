"""Pydantic schemas used by extractor, tone, and fact-checker nodes."""
from __future__ import annotations
from typing import Optional
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
