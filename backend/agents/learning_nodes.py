"""LangGraph node for the Learning explain pipeline (03_Learning_Backend_Design.md §3-5).

`retriever_node` is reused UNCHANGED from agents/nodes.py (no fork) — this
module only adds `explainer_node`, the single LLM call that replaces the
report pipeline's extractor/tone/synthesizer/fact-checker chain for a
learner-facing explanation (03 §3.1's documented reasoning: one call, no
retry loop, since the contract has no verification-stage vocabulary).
"""
from __future__ import annotations
import logging
import re
import unicodedata
from typing import Match

from .learning_state import LearningState
from .llm import chat_text, _strip_code_fence, DEFAULT_HEAVY_MODEL
from .nodes import _event, _format_docs, _safe_failure

logger = logging.getLogger("alphascribe")

_CITATION_RE = re.compile(r"\[(\d+)\]")

# Learning hardening-pass brief Finding A, root-caused: the model sometimes
# renders an inline citation in a non-ASCII bracket form instead of the
# ASCII `[n]` the prompt asks for and _CITATION_RE matches -- the content is
# correctly grounded, but the marker is invisible to the gate, so Law 3
# discards a genuinely-cited explanation as if it had zero citations.
# Confirmed live: U+3010/U+3011 (CJK "lenticular brackets", 【n】). NFKC
# normalization (applied first, below) already canonicalizes the whole
# "fullwidth ASCII variant" block for free -- ［n］, （n）, fullwidth digits --
# so only the CJK Symbols/Punctuation brackets NFKC does *not* decompose to
# ASCII need an explicit map. U+3014/U+3015 (tortoise shell brackets) share
# the same enumerated-annotation convention as the confirmed lenticular
# pair; not yet observed live, included defensively per the same narrow-
# regex trap that caused this bug in the first place.
_CJK_BRACKET_MAP = str.maketrans({
    "【": "[", "】": "]",  # LEFT/RIGHT BLACK LENTICULAR BRACKET -- confirmed live
    "〔": "[", "〕": "]",  # LEFT/RIGHT TORTOISE SHELL BRACKET -- defensive
})

# Finding C (brief §10): on the context_report_id path, the model copies a
# source-index-plus-line-range convention (`【2†L1-L4】`, or a malformed
# `【1†L1-L4}` with a mismatched closing bracket) from the Overview report's
# own draft_report, which is injected as prior_brief context. The `†Lx-Ly`
# suffix refers to *that report's* source numbering, not Learning's own
# retrieved documents -- kept around, it would let a more tolerant gate
# accept an in-range but mis-grounded citation (§10's "second, latent
# hazard"). Rewritten to canonical `[n]` (suffix dropped) before the plain
# bracket-swap below, which would otherwise leave the suffix intact and
# still fail `_CITATION_RE`.
_SUFFIXED_CITATION_RE = re.compile(
    r"[【〔\[]\s*(\d+)\s*†\s*L\d+-L\d+\s*[】〕\]}]"
)


def _normalize_citation_markers(text: str) -> str:
    """Canonicalize non-ASCII/suffixed citation-bracket forms to the ASCII
    `[n]` _CITATION_RE expects, before the gate ever runs."""
    text = _SUFFIXED_CITATION_RE.sub(lambda m: f"[{m.group(1)}]", text)
    return unicodedata.normalize("NFKC", text).translate(_CJK_BRACKET_MAP)


# Finding C fix direction (b): the actual cause, not just its downstream
# symptom -- strip any citation-shaped marker (Overview's dagger-suffixed
# form or a plain [n]/CJK-bracket one) out of the injected prior_brief
# before it ever reaches the prompt, so the model has no citation convention
# to copy from its own context in the first place. The dagger-suffix half is
# optional so this also catches a plain copied `[n]`/`【n】`.
_ANY_CITATION_MARKER_RE = re.compile(
    r"[【〔\[]\s*\d+(?:\s*†\s*L\d+-L\d+)?\s*[】〕\]}]"
)


def _strip_citation_markers(text: str) -> str:
    """Remove citation-shaped markers from injected context text (never from
    the model's own output -- that's `_normalize_citation_markers`'s job)."""
    stripped = _ANY_CITATION_MARKER_RE.sub("", text)
    stripped = re.sub(r"[ \t]{2,}", " ", stripped)
    return re.sub(r" +([.,;:!?])", r"\1", stripped)


def _postprocess_citations(text: str, num_docs: int) -> tuple[str, list[int]]:
    """Pure, stdlib `re` only (03 §5.2, in the spirit of agents/scoring.py).

    Strips any `[n]` marker outside `[1, num_docs]` — an LLM inventing `[9]`
    against 6 sources would otherwise render as a broken citation link — and
    returns the cleaned text plus the 1-based indices actually cited, in
    order of first appearance (Law 3 enforcement: the caller rejects the
    explanation entirely if this list comes back empty)."""
    cited: list[int] = []
    seen: set[int] = set()

    def _replace(m: Match[str]) -> str:
        n = int(m.group(1))
        if 1 <= n <= num_docs:
            if n not in seen:
                seen.add(n)
                cited.append(n)
            return m.group(0)
        return ""  # out-of-range marker — silently dropped, not left dangling

    cleaned = _CITATION_RE.sub(_replace, text)
    return cleaned, cited


_SYSTEM_PROMPT = (
    "You are explaining a finance concept to a learner with no finance "
    "background. Always ground the explanation in this company's actual "
    "figures from the excerpts provided — never state a number that is not "
    "present in the excerpts; say \"not disclosed\" instead. Cite inline as "
    "[1], [2], ... using the excerpt numbers. End by inviting one specific "
    "follow-up question the reader could ask next. Keep the whole "
    "explanation under 400 words."
)


def _build_user_message(state: LearningState, docs: list[dict]) -> str:
    concept = state["concept"]
    ticker = state["ticker"]
    company = state.get("company_name") or ticker
    prior_brief = state.get("prior_brief") or ""
    prior_financials = state.get("prior_financials") or {}

    context_block = ""
    if prior_brief:
        context_block = (
            "\n\n## What this company's latest brief found (context for the explanation)\n"
            f"{_strip_citation_markers(prior_brief)[:1200]}\n"
            f"### Figures already extracted from that brief\n{prior_financials}\n"
        )
    return (
        f"# Concept to explain: {concept}\n"
        f"# Company: {company} ({ticker})\n\n"
        f"## Source excerpts (cite by number)\n{_format_docs(docs, max_chars=6000)}"
        f"{context_block}\n\n"
        f"Explain the concept, then show how it applies to {company} using the "
        "figures above. Close with one follow-up question the reader could ask next."
    )


async def explainer_node(state: LearningState) -> dict:
    docs = state.get("source_documents", [])
    user = _build_user_message(state, docs)
    try:
        raw = await chat_text(_SYSTEM_PROMPT, user, model=DEFAULT_HEAVY_MODEL)
    except Exception as e:  # noqa: BLE001 — mirrors nodes.py's node-level catch
        return {
            "explanation": "",
            "trace": [_event("explainer", "error", _safe_failure("Explanation", e))],
        }
    normalized = _normalize_citation_markers(_strip_code_fence(raw))
    cleaned, cited = _postprocess_citations(normalized, len(docs))
    if not cited:
        # Law 3: an explanation with zero grounded citations must not be
        # persisted (03 §5.2) — the route layer treats an empty `explanation`
        # + empty `cited_sources` as a failed job, not a success with no
        # sources.
        # Learning hardening-pass brief §3/§8(a): nothing previously logged
        # what the model actually returned before this regex ran, so a
        # citation-gate miss (call succeeded, response didn't satisfy the
        # gate) was indistinguishable from any other failure. Server log
        # only -- never returned to the client (same discipline as
        # _safe_failure; the raw response is diagnostic, not user content).
        logger.warning(
            "explainer_node: citation gate rejected the model's response (0 of %d source docs "
            "cited) -- raw pre-postprocessing output:\n%s", len(docs), raw,
        )
        return {
            "explanation": "",
            "cited_sources": [],
            "trace": [_event("explainer", "error",
                              "The explanation had no grounded citations.")],
        }
    return {
        "explanation": cleaned.strip(),
        "cited_sources": cited,
        "trace": [_event("explainer", "ok",
                          f"Explanation written ({len(cleaned)} chars, "
                          f"{len(cited)} sources cited)")],
    }
