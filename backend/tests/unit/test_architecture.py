"""Dependency-rule guard (06 AD-5), scoped to what exists TODAY.

06's target layout (domain/, application/, infrastructure/, app/) does not
exist yet — it lands across Migration Phases 1-3. Writing the full AD-5
import-matrix test now would either trivially pass on directories that don't
exist, or need updating at every phase for no benefit in the meantime.

What DOES exist today and IS worth guarding immediately: the LangGraph-proper
modules — graph.py, nodes.py, state.py, schemas.py, retrieval.py, exactly the
"agents (LangGraph)" box in 06 §2.2's layer diagram — must never import a
concrete infrastructure driver directly (01 B-2 — the retriever node currently
receives a raw `db` handle via partial(), not a port, but it still doesn't
literally `import motor`/`fastapi`/`redis`). This test pins that property so
it cannot regress silently while Phases 1-3 build the real ports.

Deliberately scoped to those five files, NOT every file under backend/agents/:
today's `agents/` directory is a pre-refactor grab-bag that also holds
auth.py, ingest.py, llm.py, company_index.py, notify.py, sample_data.py, and
indian_companies.py — every one of which 06 §2.3/AD-10 classifies as
`infrastructure/` in the target layout, not `agents/`. Applying an
`agents/`-layer rule to auth.py (which legitimately imports
`pymongo.errors.DuplicateKeyError` for exception handling) would be enforcing
the wrong rule against the wrong file — a directory-vs-layer mismatch that
exists only until Phase 3 physically relocates these modules.

    python backend/tests/unit/test_architecture.py
"""
import ast
import os
import sys

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BACKEND_ROOT)

FORBIDDEN_IN_AGENTS = {"motor", "pymongo", "redis", "fastapi", "starlette"}

# The actual LangGraph-layer files — see the module docstring for why this is
# not "every .py under agents/".
LANGGRAPH_LAYER_FILES = ["graph.py", "nodes.py", "state.py", "schemas.py", "retrieval.py"]


def _imported_top_level_modules(filepath: str) -> set[str]:
    with open(filepath, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def _all_agents_py_files() -> list[str]:
    agents_dir = os.path.join(BACKEND_ROOT, "agents")
    return [os.path.join(agents_dir, f) for f in os.listdir(agents_dir) if f.endswith(".py")]


def _langgraph_layer_files() -> list[str]:
    all_files = {os.path.basename(p) for p in _all_agents_py_files()}
    missing = set(LANGGRAPH_LAYER_FILES) - all_files
    assert not missing, f"expected LangGraph-layer files not found in agents/: {missing}"
    return [p for p in _all_agents_py_files() if os.path.basename(p) in LANGGRAPH_LAYER_FILES]


def test_langgraph_layer_never_imports_infrastructure_drivers_directly():
    violations = []
    for path in _langgraph_layer_files():
        hit = _imported_top_level_modules(path) & FORBIDDEN_IN_AGENTS
        if hit:
            violations.append(f"{os.path.relpath(path, BACKEND_ROOT)} imports {sorted(hit)}")
    assert not violations, (
        "the LangGraph layer must depend only on ports once they exist (06 AD-7); "
        "today it must at minimum not import a concrete driver directly:\n" + "\n".join(violations)
    )


def test_agents_never_imports_server():
    # server.py is the legacy composition root being strangled out (06 AD-4);
    # nothing under agents/ may depend on it in either direction — this rule
    # applies to the WHOLE directory (auth.py etc. included), unlike the
    # driver-import rule above.
    violations = [
        os.path.relpath(path, BACKEND_ROOT)
        for path in _all_agents_py_files()
        if "server" in _imported_top_level_modules(path)
    ]
    assert not violations, f"agents/ modules importing server.py: {violations}"


if __name__ == "__main__":
    test_langgraph_layer_never_imports_infrastructure_drivers_directly()
    test_agents_never_imports_server()
    print("ok: LangGraph layer imports no concrete driver; agents/ never imports server.py (dependency-rule seed, 06 AD-5)")
