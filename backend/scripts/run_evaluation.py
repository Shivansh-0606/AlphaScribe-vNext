"""M10 Phase 4 — on-demand evaluation/regression CLI (Document 45 §19,
Document 46). Mirrors backend/scripts/acquire_financials.py's exact
convention (argparse + asyncio.run + explicit exit code) — no new CLI
framework. Deliberately NOT wired into .github/workflows/backend-ci.yml
(Document 45 §5/§19, Document 46 §2 — no blocking CI gate).

FIXTURE mode needs only a live LLM key (no Mongo). LIVE mode additionally
needs a live Mongo, matching the `pytest -m live` suite's own requirement.

Usage:
    python backend/scripts/run_evaluation.py
    python backend/scripts/run_evaluation.py --mode live
    python backend/scripts/run_evaluation.py --case-id comparison_explanation_aapl_msft --format json
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.adapters import comparison_explanation, learning, research  # noqa: E402
from evaluation.adapters.types import AdapterError  # noqa: E402
from evaluation.core.case_evaluator import evaluate_case  # noqa: E402
from evaluation.golden_dataset.loader import DatasetIntegrityError, load_dataset  # noqa: E402
from evaluation.golden_dataset.models import BenchmarkCase  # noqa: E402
from evaluation.regression.compare import compare  # noqa: E402
from evaluation.regression.git_info import get_code_revision  # noqa: E402
from evaluation.regression.result_store import RESULTS_DIR, result_to_dict, save_result  # noqa: E402
from evaluation.regression.types import EvaluationResult  # noqa: E402

_DEFAULT_CASES_DIR = Path(__file__).resolve().parents[1] / "evaluation" / "golden_dataset" / "cases"

_ADAPTERS = {
    "research": research.run,
    "learning": learning.run,
    "comparison_explanation": comparison_explanation.run,
}

Outcome = tuple[EvaluationResult | None, str | None]  # (result, error) — exactly one is non-None


def _schema_version_for(surface: str) -> str | None:
    # Document 46 §7: read the surface's own explicit schema-version constant
    # independently at this Phase 4 boundary. Phase 2's frozen ExecutionMetadata
    # has no schema_version slot — a reported, not silently patched, gap.
    if surface == "comparison_explanation":
        from agents.comparison_explanation import SCHEMA_VERSION
        return SCHEMA_VERSION
    return None


async def run_case(
    case: BenchmarkCase, mode: str, run_id: str, code_revision: str, *, results_dir: Path = RESULTS_DIR,
) -> Outcome:
    adapter_fn = _ADAPTERS[case.surface]
    try:
        adapter_result = await adapter_fn(case, mode=mode)
    except AdapterError as e:
        return None, f"{case.case_id}: adapter error — {e}"

    case_result = evaluate_case(case, adapter_result)
    schema_version = _schema_version_for(case.surface)
    verdict, reason = compare(case_result, schema_version=schema_version, results_dir=results_dir)

    result = EvaluationResult(
        run_id=run_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        code_revision=code_revision,
        schema_version=schema_version,
        case=case_result,
        verdict=verdict,
        verdict_reason=reason,
    )
    return result, None


async def run_all(cases: list[BenchmarkCase], mode: str, *, results_dir: Path = RESULTS_DIR) -> list[Outcome]:
    run_id = str(uuid.uuid4())
    code_revision = get_code_revision()
    return [await run_case(case, mode, run_id, code_revision, results_dir=results_dir) for case in cases]


def _print_text(outcomes: list[Outcome]) -> None:
    for result, error in outcomes:
        if error:
            print(f"ERROR            {error}")
            continue
        print(f"{result.verdict:16s} {result.case.case_id} "
              f"({result.case.surface}, {result.case.mode}) — {result.verdict_reason}")


def _print_json(outcomes: list[Outcome]) -> None:
    payload = [{"error": error} if error else result_to_dict(result) for result, error in outcomes]
    print(json.dumps(payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=["fixture", "live"], default="fixture")
    parser.add_argument("--case-id", action="append", dest="case_ids",
                         help="repeatable; defaults to every case in the dataset")
    parser.add_argument("--dataset-dir", type=Path, default=_DEFAULT_CASES_DIR)
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR,
                         help="where results are read from (baselines) and written to; "
                              "defaults to the real, git-ignored backend/evaluation/results/")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    try:
        cases = load_dataset(args.dataset_dir)
    except DatasetIntegrityError as e:
        print(f"dataset error: {e}", file=sys.stderr)
        raise SystemExit(2)

    if args.case_ids:
        wanted = set(args.case_ids)
        cases = [c for c in cases if c.case_id in wanted]
        missing = wanted - {c.case_id for c in cases}
        if missing:
            print(f"unknown case_id(s): {sorted(missing)}", file=sys.stderr)
            raise SystemExit(2)

    outcomes = asyncio.run(run_all(cases, args.mode, results_dir=args.results_dir))

    for result, _error in outcomes:
        if result is not None:
            save_result(result, results_dir=args.results_dir)

    if args.format == "json":
        _print_json(outcomes)
    else:
        _print_text(outcomes)

    had_error = any(error for _, error in outcomes)
    had_regression = any(result is not None and result.verdict == "REGRESSION" for result, _ in outcomes)
    raise SystemExit(1 if (had_error or had_regression) else 0)


if __name__ == "__main__":
    main()
