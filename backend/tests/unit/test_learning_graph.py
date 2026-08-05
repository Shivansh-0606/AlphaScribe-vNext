"""Unit check for agents/learning_graph.py's compiled node vocabulary.

03_Learning_Backend_Design.md §3: "any node name outside {pipeline,
retriever, explainer, final} leaves the UI stuck in the AI Thinking state
forever" — the graph's own node names are part of the frozen frontend
contract (streamStages.ts:25-36), so a rename here is a silent breaking
change this test exists to catch. No LLM, no DB (db=None — the graph is only
compiled, never run).

    python backend/tests/unit/test_learning_graph.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.learning_graph import build_learning_graph


def test_graph_has_exactly_the_frozen_node_names():
    graph = build_learning_graph(db=None)
    nodes = set(graph.get_graph().nodes.keys()) - {"__start__", "__end__"}
    assert nodes == {"retriever", "explainer"}


def test_graph_edges_form_a_straight_line_retriever_then_explainer():
    graph = build_learning_graph(db=None)
    edges = {(e.source, e.target) for e in graph.get_graph().edges}
    assert ("__start__", "retriever") in edges
    assert ("retriever", "explainer") in edges
    assert ("explainer", "__end__") in edges
    # No extractor/tone/fact-checker fan-out (03 §3.1) — exactly 3 edges.
    assert len(edges) == 3


if __name__ == "__main__":
    test_graph_has_exactly_the_frozen_node_names()
    test_graph_edges_form_a_straight_line_retriever_then_explainer()
    print("ok: Learning graph node vocabulary matches the frozen frontend contract; "
          "no extractor/tone/fact-checker fan-out")
