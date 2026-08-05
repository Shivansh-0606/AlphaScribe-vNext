"""Compile the Learning explain LangGraph (03_Learning_Backend_Design.md §3).

START -> retriever -> explainer -> END. No extractor/tone/fact-checker (see
the design doc §3.1 for why) — one LLM call, matching a learner-facing
feature's latency budget instead of the report pipeline's 4-6 calls.
"""
from __future__ import annotations
from functools import partial
from langgraph.graph import StateGraph, START, END
from infrastructure.observability.tracing import instrument_node
from .learning_state import LearningState
from .learning_nodes import explainer_node
from .nodes import retriever_node

_GRAPH = "learning"


def build_learning_graph(db):
    g = StateGraph(LearningState)

    g.add_node("retriever", instrument_node(_GRAPH, "retriever", partial(retriever_node, db=db)))
    g.add_node("explainer", instrument_node(_GRAPH, "explainer", explainer_node))

    g.add_edge(START, "retriever")
    g.add_edge("retriever", "explainer")
    g.add_edge("explainer", END)

    return g.compile()
