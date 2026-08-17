"""M10 Phase 4 — code_revision (Document 45 §17): the git commit hash of the
working tree at run time. Stdlib `subprocess` only — no new dependency, no
network call, exactly as Document 45 §17 specifies."""
from __future__ import annotations

import subprocess
from pathlib import Path

_CWD = Path(__file__).resolve().parents[2]  # backend/ — inside the repo working tree
_TIMEOUT_S = 10


def get_code_revision() -> str:
    """`git rev-parse HEAD`, suffixed "-dirty" if `git status --porcelain` is
    non-empty. Returns "unknown" if git itself is unavailable — this must
    never raise and block a run over missing tooling."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=_CWD, capture_output=True, text=True,
            check=True, timeout=_TIMEOUT_S,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return "unknown"

    try:
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=_CWD, capture_output=True, text=True,
            check=True, timeout=_TIMEOUT_S,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        status = ""

    return f"{commit}-dirty" if status.strip() else commit
