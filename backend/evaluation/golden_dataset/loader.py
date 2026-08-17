"""M10 Phase 1 — golden benchmark dataset loader (Document 45 §7, §9).

Discovers, parses, and validates `*.json` benchmark case files. Nothing here
touches an AI provider, Mongo, or evaluation/scoring logic (Document 45 §21's
loader-boundary separation) — dataset loading and validation only.
"""
from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .models import BenchmarkCase


class DatasetIntegrityError(ValueError):
    """One or more benchmark case files failed to load or validate.

    `errors` maps the offending file path to its specific problem — collected
    across the whole directory in one pass (not fail-fast on the first bad
    file), so a dataset author sees every problem in one loader run.
    """

    def __init__(self, errors: dict[str, str]):
        self.errors = errors
        summary = "\n".join(f"  {path}: {msg}" for path, msg in sorted(errors.items()))
        super().__init__(f"{len(errors)} benchmark case file(s) failed to load:\n{summary}")


def load_dataset(cases_dir: Path) -> list[BenchmarkCase]:
    """Load every `*.json` case file in `cases_dir` as a validated `BenchmarkCase`.

    Raises `DatasetIntegrityError` (a single exception, every problem collected)
    when: the directory has no case files; a file is not valid JSON; a file
    fails `BenchmarkCase` schema/invariant validation; or two files declare
    the same `case_id`.
    """
    files = sorted(cases_dir.glob("*.json"))
    if not files:
        raise DatasetIntegrityError({str(cases_dir): "no benchmark case files found (*.json)"})

    errors: dict[str, str] = {}
    cases: list[BenchmarkCase] = []
    seen_ids: dict[str, str] = {}  # case_id -> first file path that declared it

    for path in files:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors[str(path)] = f"invalid JSON: {e}"
            continue

        try:
            case = BenchmarkCase.model_validate(raw)
        except ValidationError as e:
            errors[str(path)] = f"schema validation failed: {e}"
            continue

        if case.case_id in seen_ids:
            errors[str(path)] = (
                f"duplicate case_id {case.case_id!r} (already declared in {seen_ids[case.case_id]!r})"
            )
            continue

        seen_ids[case.case_id] = str(path)
        cases.append(case)

    if errors:
        raise DatasetIntegrityError(errors)
    return cases
