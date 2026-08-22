"""M10 Phase 4 — live end-to-end evaluation harness test (Document 45 §20/§24
name this category explicitly: "a real benchmark case run against a real
graph/LLM call... the only category needing a live provider/Mongo").

Exercises a genuine LIVE-mode run through the real dataset -> adapter ->
evaluation core -> regression pipeline: real Mongo retrieval (agents/
retrieval.py, unstubbed), real LLM call (agents/llm.py, unstubbed). Also
proves the LIVE-mode result is never usable as a regression comparison
target (the Reviewer-identified fix in evaluation/regression/compare.py).

Skips — does not fail, does not fall back to a fake hermetic substitute —
if this environment has no live LLM key or no reachable Mongo. This
mirrors every other `pytest.mark.live` test in this repo (backend_test_iter2.py
etc.), which assume a running stack (`python scripts/run.py`) rather than
faking one; the explicit prerequisite check here exists only because this
test, unlike the HTTP-based live suite, would otherwise silently "pass" on
an all-degraded, no-real-call run and prove nothing.

    python -m pytest backend/tests/test_m10_evaluation_live.py -v -m live
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

import pytest  # noqa: E402

# 06 §5.1 Ph0 / 05 T-1: needs a live LLM + live Mongo. Excluded from the
# hermetic CI job via `-m "not live"`, same convention every other live
# test file in this repo already uses.
pytestmark = pytest.mark.live


async def _mongo_reachable() -> bool:
    import server
    try:
        await asyncio.wait_for(server.db.command("ping"), timeout=3.0)
        return True
    except Exception:
        return False


def _live_prerequisites_missing_reason() -> str | None:
    """None if the live environment is ready; otherwise the skip reason."""
    from agents.llm import _active
    if not _active().get("api_key"):
        return "no live LLM provider key configured (agents.llm._active() has no api_key)"
    if not asyncio.run(_mongo_reachable()):
        return "no reachable live Mongo instance (server.db.command('ping') failed/timed out)"
    return None


def test_live_mode_evaluation_produces_result_and_is_never_a_comparison_target(tmp_path):
    reason = _live_prerequisites_missing_reason()
    if reason:
        pytest.skip(f"live environment unavailable: {reason}")

    from evaluation.adapters import research
    from evaluation.core.case_evaluator import evaluate_case
    from evaluation.golden_dataset.loader import load_dataset
    from evaluation.regression.compare import compare

    cases_dir = Path(__file__).resolve().parents[1] / "evaluation" / "golden_dataset" / "cases"
    cases = load_dataset(cases_dir)
    case = next(c for c in cases if c.case_id == "research_aapl_revenue_trend")

    async def _go():
        # Real graph.ainvoke, real Mongo retrieval, real chat_text/chat_json
        # calls — nothing stubbed, nothing faked (this task's own §3).
        adapter_result = await research.run(case, mode="live")
        assert adapter_result.mode == "live"

        case_result = await evaluate_case(case, adapter_result)
        # The EvaluationResult contract: a real, three-state status, not a
        # crash and not a silently-invented fourth state.
        assert case_result.status in ("PASS", "FAIL", "INCONCLUSIVE")

        # The fix under review: a LIVE-mode result must never be compared
        # against a stored baseline, regardless of what that baseline says
        # or whether one even exists.
        verdict, comparison_reason = compare(case_result, schema_version=None, results_dir=tmp_path)
        assert verdict == "INCONCLUSIVE"
        assert "LIVE-mode" in comparison_reason
        return case_result

    result = asyncio.run(_go())
    print(f"live evaluation run: status={result.status}, "
          f"metrics={[(m.name, m.value) for m in result.metrics]}")


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v", "-m", "live"]))
