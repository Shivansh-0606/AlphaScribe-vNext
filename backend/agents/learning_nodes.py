"""LangGraph node for the Learning explain pipeline (03_Learning_Backend_Design.md §3-5).

`retriever_node` is reused UNCHANGED from agents/nodes.py (no fork) — this
module only adds `explainer_node`, the single LLM call that replaces the
report pipeline's extractor/tone/synthesizer/fact-checker chain for a
learner-facing explanation (03 §3.1's documented reasoning: one call, no
retry loop, since the contract has no verification-stage vocabulary).
"""
from __future__ import annotations
import re
from typing import Match

from .learning_state import LearningState
from .llm import chat_text, _strip_code_fence, DEFAULT_HEAVY_MODEL
from .nodes import _event, _format_docs

_CITATION_RE = re.compile(r"\[(\d+)\]")


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
            f"{prior_brief[:1200]}\n"
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
            "trace": [_event("explainer", "error", f"Explanation failed: {e}")],
        }
    cleaned, cited = _postprocess_citations(_strip_code_fence(raw), len(docs))
    if not cited:
        # Law 3: an explanation with zero grounded citations must not be
        # persisted (03 §5.2) — the route layer treats an empty `explanation`
        # + empty `cited_sources` as a failed job, not a success with no
        # sources.
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
