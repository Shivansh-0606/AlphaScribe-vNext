"""LangGraph state for the Learning explain pipeline (03_Learning_Backend_Design.md §3).

Deliberately separate from agents/state.py's AgentState: Learning is a
2-node graph (retriever -> explainer) with different inputs (concept,
company_name, prior_financials) and no extractor/tone/fact-checker fields —
sharing one TypedDict would just carry unused keys across both pipelines.
"""
from __future__ import annotations
from typing import Annotated
from operator import add
from typing import TypedDict

from .state import SourceDocument


class LearningState(TypedDict, total=False):
    # inputs
    ticker: str
    query: str              # expanded retrieval query (R-1) — what retriever_node reads
    concept: str             # verbatim user input — what the prompt and doc use
    company_name: str
    prior_brief: str         # from context_report_id, capped at prompt-assembly time
    prior_financials: dict   # from context_report_id's extracted_data

    # retrieval (retriever_node, reused unchanged from agents/nodes.py)
    source_documents: list[SourceDocument]

    # explanation
    explanation: str
    cited_sources: list[int]  # 1-based indices into source_documents actually cited (03 §5.2)

    # observability trace (list of pipeline events, appended by each node)
    trace: Annotated[list[dict], add]
