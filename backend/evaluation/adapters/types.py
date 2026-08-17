"""M10 Phase 2 — the common adapter contract (Document 45 §11).

Dataclasses, not Pydantic (unlike evaluation/golden_dataset/models.py's
JSON-file-boundary models): these are in-process return values passed
adapter -> future evaluation core, never serialized to/from a file — the
same rationale domain/models.py already uses for its own in-process state.

Nothing here imports agents/graph.py, agents/learning_nodes.py, or
agents/comparison_explanation.py — the three surface-specific adapter
modules are the only importers of those, keeping this module (and any
future evaluation core built on it) surface-blind (Document 45 §6
principle 3, §21).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Literal

from evaluation.golden_dataset.models import Surface

ExecutionMode = Literal["fixture", "live"]
GroundingVerdict = Literal["grounded", "ungrounded", "error"]


def fingerprint(*parts: str) -> str:
    """Deterministic content hash of one or more prompt-template source
    strings (Document 45 §17's `prompt_fingerprint` — never called
    `prompt_version`, which only applies where a surface has an explicit
    version constant, Comparison Explanation today). Stdlib only."""
    return hashlib.sha256("\x00".join(parts).encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class Citation:
    """Document 45 §11's normalized citation record — eligible/referenced/
    valid, not a raw marker count (Revision 2's fix to an assumed-uniform
    denominator)."""

    source_id: str
    eligible: bool
    referenced: bool
    valid: bool


@dataclass(frozen=True)
class NormalizedOutput:
    """Document 45 §11's NormalizedOutput — the one shape every surface's
    raw output is translated into before evaluation. `raw` is kept for
    debugging only; the (future) evaluator core must never read it."""

    text: str
    citations: list[Citation]
    grounding_verdict: GroundingVerdict
    limitations_stated: list[str]
    raw: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionMetadata:
    """Execution metadata necessary for evaluation (this task's §7) — never
    a secret. `api_key` is deliberately absent; only provider/model *names*
    are carried, exactly as agents/llm.py's own llm_calls_total metric
    labels already do."""

    provider: str | None
    model: str | None
    prompt_version: str | None = None
    prompt_fingerprint: str | None = None


@dataclass(frozen=True)
class AdapterResult:
    """What a surface adapter returns for one benchmark case (Document 45
    §11, extended with case_id/surface/mode per this task's §7 — Document 45
    itself places those at the EvaluationResult/run level, Phase 3; Phase 2
    attaches them here since the adapter is what actually knows them)."""

    case_id: str
    surface: Surface
    mode: ExecutionMode
    output: NormalizedOutput
    execution: ExecutionMetadata


# ---------------------------------------------------------------------------
# Error boundary (this task's §8) — four categories the task names, plus one
# adapter-capability gap the frozen architecture itself already deferred
# (Document 45 §11.1: "the exact stand-in shape is an implementation-phase
# detail, not fixed here").
# ---------------------------------------------------------------------------

class AdapterError(Exception):
    """Base for every M10 adapter-boundary failure. Never carries a raw
    provider exception's message unmodified if it might contain a key —
    callers should prefer the existing redaction agents/llm.py's own
    error path already applies over re-exposing a raw exception string."""


class InvalidBenchmarkInputError(AdapterError):
    """The benchmark case (or the combination of case + mode) is not usable
    by this adapter as given — e.g. FIXTURE mode requested for Comparison
    Explanation with no `fixture_reports` in `case.context`. Not a provider
    or framework failure; the input itself is the problem."""


class AdapterInvocationError(AdapterError):
    """The adapter's own call into the existing surface failed to run at
    all — a framework/plumbing failure (e.g. `graph.ainvoke` raising an
    unexpected exception), distinct from a provider/LLM failure and from a
    benchmark-input problem."""


class ProviderExecutionError(AdapterError):
    """The underlying AI/provider genuinely failed to produce output —
    mirrors each surface's own production failure path for exceptions that
    are NOT absorbed into a soft in-state signal (Comparison Explanation's
    `generate_explanation` docstring: "propagates whatever chat_json itself
    raises"). Distinct from a completed-but-low-quality result, which is
    `NormalizedOutput.grounding_verdict == "error"`, not a raised exception."""


class MalformedAIOutputError(AdapterError):
    """The AI capability completed and returned *something*, but its shape
    is not what the adapter expects to normalize (e.g. the graph's final
    state came back empty/non-dict) — distinct from a provider/network
    failure and from the surface's own documented soft-failure end-state."""


class UnsupportedExecutionModeError(AdapterError):
    """This adapter does not implement the requested `mode` for this surface
    yet. Not a case-input problem, not a provider failure — the capability
    itself is not built. Document 45 §11.1 explicitly left the Research/
    Learning FIXTURE-mode stand-in mechanism as "an implementation-phase
    detail, not fixed" by the frozen architecture; this phase implements
    LIVE mode for all three surfaces and FIXTURE mode for Comparison
    Explanation only (no stand-in needed there — fixture_reports are
    supplied inline). Raised, not silently faked, for the deferred case."""
