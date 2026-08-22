"""M11 self-consistency evaluation tooling (Document 47 §9.1) — repeated
judge invocation over a fixed held-out claim/evidence set. Produces
EMPIRICAL EVIDENCE ONLY: this script never reads or writes
JUDGE_SELF_CONSISTENCY_GATE_VERSION (evaluation/core/judge_gate.py) and
never touches case-level PASS/FAIL — gate promotion is a separate, human
CTO/reviewer decision (§9.1 step 6), not something this script performs or
recommends.

Mirrors run_evaluation.py's own argparse + asyncio.run + explicit exit code
convention — no new CLI framework. Needs only a live LLM key (same
requirement as run_evaluation.py --mode live), no Mongo.

Usage:
    python backend/scripts/run_judge_self_consistency.py
    python backend/scripts/run_judge_self_consistency.py --repeats 10 --output results.json
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from dataclasses import asdict
from pathlib import Path

_BACKEND_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(_BACKEND_ROOT))

# server.py's own convention (ROOT_DIR / ".env") — this script deliberately
# bypasses the surface-adapter layer (evaluation/adapters/*), which is what
# other CLIs (run_evaluation.py) rely on to transitively `import server` and
# load .env as a side effect. Reused here explicitly instead, via the
# already-required python-dotenv dependency (requirements.txt) — not a new one.
from dotenv import load_dotenv  # noqa: E402
load_dotenv(_BACKEND_ROOT / ".env")

from evaluation.self_consistency.cases import HeldOutSetIntegrityError, load_held_out_set  # noqa: E402
from evaluation.self_consistency.runner import aggregate, run_case_repeats  # noqa: E402

_DEFAULT_CASES_DIR = Path(__file__).resolve().parents[1] / "evaluation" / "self_consistency" / "cases"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _run_all(cases, repeats: int):
    measurements = []
    for case in cases:
        measurements.extend(await run_case_repeats(case, repeats=repeats, timestamp_fn=_now))
    return measurements


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cases-dir", type=Path, default=_DEFAULT_CASES_DIR)
    parser.add_argument("--repeats", type=int, default=5, help="independent judge calls per held-out case")
    parser.add_argument("--output", type=Path, default=None, help="write raw measurements + aggregate report as JSON (default: stdout)")
    args = parser.parse_args()

    try:
        cases = load_held_out_set(args.cases_dir)
    except HeldOutSetIntegrityError as e:
        print(f"held-out set error: {e}", file=sys.stderr)
        raise SystemExit(2)

    measurements = asyncio.run(_run_all(cases, args.repeats))
    report = aggregate(cases, measurements)

    payload = {
        "generated_at": _now(),
        "repeats_per_case": args.repeats,
        "held_out_case_count": len(cases),
        "note": (
            "EVIDENCE ONLY (Document 47 Sec9.1) -- does not authorize gate promotion. "
            "JUDGE_SELF_CONSISTENCY_GATE_VERSION is not read or written by this script; "
            "promoting the gate is a separate, explicit CTO/reviewer decision (Sec9.1 step 6)."
        ),
        "measurements": [asdict(m) for m in measurements],
        "report": asdict(report),
    }

    text = json.dumps(payload, indent=2)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
