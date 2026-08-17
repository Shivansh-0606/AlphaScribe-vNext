# 46 — M10 Phase 4 (Regression / CLI) Pre-Implementation Plan

**Status:** 🟡 PRE-IMPLEMENTATION REVIEW — not an implementation authorization
**Type:** Planning document (no code, no Phase 1–3 change, no Document 45 edit)
**Document 45 status, stated precisely:** 🟡 **PROPOSED — AWAITING CTO APPROVAL** — this is Document 45's own header field, unedited since Revision 3. Prior conversational governance-state banners describing it as "APPROVED / FROZEN" reflect chat-level directives, not an edit to Document 45's own status line; this document does not repeat that overclaim.
**M10 Phase 4 implementation:** 🔴 **NOT AUTHORIZED**
**Supersedes:** an unsaved chat-only Phase 4 readiness assessment from earlier in this session — that assessment was never persisted as a document; this is its first saved form, already incorporating the CTO corrections in §3–§7 below (not a redline against a prior file).

---

## 1. Purpose

A pre-implementation plan for M10 Phase 4 (Regression comparison + baseline handling + CLI/execution interface), built on the frozen Phase 1–3 implementation and Document 45's architecture. Captures five CTO-directed corrections to the baseline/regression rules originally sketched, and the two implementation-detail decisions those corrections resolve. No Phase 4 code exists yet; nothing here authorizes writing any.

---

## 2. Frozen Scope (Document 45, authorized for Phase 4 once implementation is granted)

- Baseline = a stored prior FIXTURE-mode result, subject to the eligibility rule in §4.
- Five-verdict truth table (§5) — no `IMPROVEMENT` (Document 45 §18, reaffirmed twice already).
- `EvaluationResult` persistence at `backend/evaluation/results/`, one JSON file per run, **git-ignored**.
- On-demand CLI script, `argparse`-based, no new dependency, mirroring `backend/scripts/acquire_financials.py`'s existing convention (`argparse` + `asyncio.run(_run(...))` + explicit exit code) — not wired into CI.
- `code_revision` (git commit hash + `-dirty` suffix, stdlib `subprocess`) attached to every result as reproducibility metadata.

## 3. Deferred Scope (stays out of Phase 4)

New metrics, LLM-as-judge, any change to Research/Learning/Comparison Explanation or production citation/scoring, CI integration of any kind, MongoDB/Redis persistence, and Research/Learning's FIXTURE-mode retriever stand-in (Document 45 §11.1's own "implementation-phase detail, not fixed here" — still not Phase 4's job).

---

## 4. Baseline Eligibility Rule (CTO correction — frozen)

A stored result is an eligible baseline **only when all of the following hold**:

- `mode == "fixture"`
- `status == "PASS"` or `status == "FAIL"` (never `"INCONCLUSIVE"`)
- `case_id` matches
- `dataset_version` matches
- `case_version` matches
- `evaluation_version` matches
- `schema_version` matches

**If the most recent compatible FIXTURE-mode result is `INCONCLUSIVE`, it is not an eligible baseline, and the comparison does *not* search backward for an older PASS/FAIL result.** The current comparison result is `INCONCLUSIVE` in that case. Rationale (CTO, verbatim intent preserved): an inconclusive run breaks the continuity of the baseline chain — searching past it to find an older determinate result would silently paper over the fact that the most recent attempt to establish a baseline didn't succeed, and risks comparing against a result that's no longer representative of "the last known state."

This **replaces** this document's prior draft rule (baseline = "the most recent prior FIXTURE-mode result," with no eligibility filter beyond mode and the identity key) — that draft implicitly allowed an INCONCLUSIVE result to sit silently as "the baseline" with undefined comparison behavior. This is now closed.

## 5. Baseline Compatibility Key (CTO correction — frozen)

**Key:** `(case_id, dataset_version, case_version, evaluation_version, schema_version)` — five fields, exact match required on all.

**Explicitly excluded from the identity key:** `provider`, `model`, `code_revision`, `prompt_version`, `prompt_fingerprint`. These remain attached to every result as reproducibility/audit metadata (Document 45 §17) but do not gate baseline eligibility — a baseline recorded under a different provider/model or a different `code_revision` is still comparable, since the whole point of behavioral (not textual) evaluation is that legitimate variation in *how* a surface produces its answer must not itself read as incompatible.

This **replaces** this document's prior draft key, `(case_id, dataset_version, case_version)` — three fields, missing `evaluation_version` and `schema_version`. That gap was a genuine, reported risk: a metric-logic change (bumping `evaluation_version`) could have silently compared a current run against a baseline computed under old metric logic, producing a false REGRESSION or false PASS. Closed by adding both version fields to the key.

## 6. Complete Regression Truth Table (CTO correction — frozen)

| Baseline | Current | Verdict |
|---|---|---|
| No eligible baseline | PASS | INCONCLUSIVE |
| No eligible baseline | FAIL | INCONCLUSIVE |
| No eligible baseline | INCONCLUSIVE | INCONCLUSIVE |
| Eligible, baseline PASS | PASS, no soft-metric drop | PASS |
| Eligible, baseline PASS | PASS, soft metric drops without crossing its required floor | WARNING |
| Eligible, baseline PASS | FAIL | REGRESSION |
| Eligible, baseline FAIL | PASS | PASS |
| Eligible, baseline FAIL | FAIL | UNCHANGED_FAILURE |
| Eligible (any) | INCONCLUSIVE | INCONCLUSIVE |
| Most recent compatible result is INCONCLUSIVE | *(any)* | Not eligible — do not search older results. Current comparison = INCONCLUSIVE |

Every baseline/current combination now has exactly one defined outcome — no case falls through undefined. `PASS`/`FAIL`/`INCONCLUSIVE` here are `CaseEvaluationResult.status` (Phase 3, frozen) for the run in question; `WARNING`'s "soft metric" reads `citation_coverage`/`expected_characteristic_coverage`'s `MetricResult.value` directly (both already exist, unmodified, Phase 3).

## 7. `schema_version` (CTO correction — clarified, one gap identified and resolved without touching Phase 2)

**Rule:** `EvaluationResult.schema_version` is populated from the evaluated surface's explicit schema version when one exists; `null` otherwise. Today, only Comparison Explanation has one (`agents.comparison_explanation.SCHEMA_VERSION`) — Research and Learning have no equivalent constant (the same finding already recorded in Document 45 §17 for `prompt_version`/`prompt_fingerprint`), so `schema_version` is `null` for those two surfaces, not fabricated.

**Gap found, per this task's own instruction to report rather than silently patch:** the frozen Phase 2 `ExecutionMetadata` dataclass (`evaluation/adapters/types.py`) has **no `schema_version` field at all**. The Comparison Explanation adapter (`evaluation/adapters/comparison_explanation.py:116`) already imports `SCHEMA_VERSION` but never attaches it anywhere — it is read and discarded. Document 45 §12 names `schema_version` as a distinct `EvaluationResult` field; Phase 2's frozen contract has no slot for it.

**Resolution — does not require modifying the frozen Phase 2 contract:** Phase 4, when constructing the persisted `EvaluationResult` from a `CaseEvaluationResult`, reads `agents.comparison_explanation.SCHEMA_VERSION` **independently** for `surface == "comparison_explanation"` results — the same already-existing, versioned production constant the adapter itself already imports, just read a second time at the Phase 4 boundary instead of being threaded through `ExecutionMetadata`. This is additive (a new read in a new Phase 4 module), not a change to `evaluation/adapters/types.py`, `comparison_explanation.py`, or any other frozen Phase 1–3 file. For Research/Learning, `schema_version` stays `null` — no equivalent constant exists to read.

This resolves within Phase 4's own authority; it does **not** rise to the "STOP and report a Phase 2 conflict" condition, because no Phase 2 edit is needed.

## 8. Real Fixture-Capable Seed Case (CTO directive — scoped)

Phase 4 must add `fixture_reports` content to **at least one** Comparison Explanation golden case (Comparison Explanation is the only surface with a working FIXTURE mode today — Phase 2's own finding) so the regression machinery has something real to demonstrate against, not only synthetic unit-test fixtures. Confirmed by direct inspection this session: **none of the three current seed cases carries `fixture_reports`** — without this addition, Phase 4 would ship with zero regression-eligible dataset content.

This is dataset **content** authorship (a new/updated JSON case file under `backend/evaluation/golden_dataset/cases/`), explicitly named as Phase 4's own responsibility by Document 45 §24's sequencing ("first authored golden-dataset cases"), not a reopening of Phase 1's schema or loader code. Research/Learning FIXTURE mode remains deferred — no retriever stand-in, no production AI pipeline change, matching Document 45 §11.1's own deferral and Phase 2's already-accepted gap.

## 9. Preserved Decisions (unchanged from the prior draft)

Local JSON result artifacts; git-ignored `backend/evaluation/results/`; FIXTURE vs. LIVE distinction with LIVE never eligible as a baseline; stdlib `json`/`pathlib` only; `argparse` CLI, no new CLI framework; no CI wiring; no MongoDB; no Redis; no new metrics; no LLM-as-judge; no production pipeline changes; `code_revision` metadata; behavioral (never textual) regression evaluation; the five verdicts PASS / WARNING / REGRESSION / UNCHANGED_FAILURE / INCONCLUSIVE (no `IMPROVEMENT`).

---

## 10. Governance Status

**Document 45:**
🟡 PROPOSED — AWAITING CTO APPROVAL (its own header, unedited)

**M10 Phase 4 implementation:**
🔴 NOT AUTHORIZED

This document is a planning correction only. It does not authorize starting Phase 4, does not modify Document 45, and does not modify any Phase 1–3 file.
