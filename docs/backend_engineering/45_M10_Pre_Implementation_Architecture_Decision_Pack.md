# 45 — M10 Pre-Implementation Architecture Decision Pack

**Status:** 🟡 PROPOSED — AWAITING CTO APPROVAL
**Type:** Architecture investigation (research/design-only, no code changed, no pipeline modified)
**Revision 3** — direction approved in principle, not yet frozen. Applies four CTO-requested precision fixes to Revision 2 (which itself resolved nine earlier findings, summarized below): (1) FIXTURE MODE terminology corrected — it fixes *inputs* only; Research/Learning/Comparison Explanation all still make a real, nondeterministic LLM call in fixture mode, and regression stays behavioral/metric-based, never a text snapshot (§11.1); (2) the regression-verdict rule set closed to cover every baseline/current pass-fail combination, adding an explicit `UNCHANGED_FAILURE` state and a full truth table, without reintroducing `IMPROVEMENT` (§18); (3) citation coverage's zero-denominator case defined explicitly — `null`/not-applicable when no evidence was eligible, `0.0` only when evidence existed and none was validly cited, with `citation_expectation` (not `citation_coverage`) as the actual pass/fail gate (§13); (4) `ExpectedBehavior`'s `type`/`match_rule`/`variants`/`reference` combinations made explicit via a constraint table, to be enforced as a Pydantic cross-field validator at implementation time (§7). No other section changed in substance.
**Revision 2 (superseded by the above, kept for record):** `expected_behaviors` made an executable structured record (§7); the generic unsupported-claim-rate metric removed in favor of a case-level `limitation_reference` behavior (§13); the binary grounding metric renamed from "grounded-claim rate" to "grounding status" (§13); citation coverage redefined against an explicit eligible/referenced/valid `Citation` record instead of an assumed-uniform denominator (§11); local result-baseline persistence made explicit — `backend/evaluation/results/`, git-ignored (§12, §18); FIXTURE vs. LIVE execution modes defined, with LIVE never eligible as a baseline (§11.1); `prompt_fingerprint` introduced as a distinct field from `prompt_version` for the two surfaces with no explicit version constant (§12, §17); the `IMPROVEMENT` verdict removed as unjustifiable at v1 scale (§18); `code_revision` added to `EvaluationResult` (§12, §17).
**Depends on (frozen, unmodified):** [17_M4_Backend_Capability_Roadmap_Reconciliation.md](17_M4_Backend_Capability_Roadmap_Reconciliation.md) §7.1, [44_Post_M9_Backend_AI_Roadmap_Reconciliation.md](44_Post_M9_Backend_AI_Roadmap_Reconciliation.md) §7 (Milestone 10 recommendation)
**Does not reopen:** M9 architecture (Documents 41/42/43) — cited for pattern precedent only, not modified or re-ratified here.

---

## 1. Purpose

Document 44 recommended Milestone 10 — AI Evaluation & Regression Foundation as the next Backend & AI milestone and was CTO-approved as the milestone identity. That approval named *what* comes next; it did not design *how*. This document is that design: the architecture for a shared evaluation foundation across AlphaScribe's three AI-generating surfaces. It follows the same two-stage pattern M9 used (Document 41 = architecture, before Document 43 = contract) — this is the architecture stage. No dataset, no harness code, and no pipeline change is created here.

---

## 2. Problem Statement

Three independent LLM-generating surfaces exist today — Research (`agents/graph.py`), Learning (`agents/learning_nodes.py`), Comparison Explanation (`agents/comparison_explanation.py`) — each with its own prompt, its own citation-validation logic, and no shared way to answer "did a prompt/model/schema change make any of these worse?" The only existing quality signal, `agents/scoring.py`'s `compute_scorecard`, is computed per-report, never compared against a baseline, and is structurally coupled to the Report document shape (`draft_report`, `source_documents`, `verified_claims`) — it cannot evaluate Learning or Comparison Explanation's differently-shaped outputs without a fake-report adapter. `01 D-10`'s already-documented blind spot (qualitative fabrication passing faithfulness scoring undetected) remains unmitigated for all three surfaces.

---

## 3. Current Repository State (verified this session, direct reads)

| Component | File | Verified finding |
|---|---|---|
| Citation/quality scoring | `agents/scoring.py` | `compute_scorecard(report: dict)` — stdlib `re` only, no deps. Reads `draft_report`, `source_documents`, `query`, `verified_claims` from a report-shaped dict. Report-shape-coupled, not surface-generic. |
| Research pipeline | `agents/graph.py`, `agents/nodes.py`, `agents/state.py` | 5-node LangGraph (`retriever → extractor‖tone → synthesizer → fact_checker`), compiled once at module load (`graph = build_graph(db)` in `server.py`). State (`AgentState`) is a `TypedDict`: `ticker`, `query`, `source_documents`, `extracted_data`, `sentiment_analysis`, `draft_report`, `fact_check_status`, `verified_claims`, `trace`. |
| Learning pipeline | `agents/learning_nodes.py`, `agents/learning_state.py`, `agents/learning_graph.py` | 2-node graph (`retriever → explainer`), separate `LearningState` TypedDict: `ticker`, `concept`, `query`, `company_name`, `source_documents`, `explanation`, `cited_sources` (1-based indices). Citation post-processing (`_postprocess_citations`) is a pure, importable, stdlib-`re` function already isolated from the node itself. |
| Comparison Explanation | `agents/comparison_explanation.py` | Pure functions + one `chat_json` call (`generate_explanation`). Already versions itself explicitly: `PROMPT_VERSION = "v1"`, `SCHEMA_VERSION = "v1"` (module-level constants, bumped manually on prompt/schema change). `validate_and_map_citations` is a pure, importable function that raises `GroundingError` on any grounding-integrity failure — the exact "did it behave correctly" signal this milestone needs, already built. |
| LLM abstraction | `agents/llm.py` | `chat_text`/`chat_json`, multi-provider, per-request context via `_LLM_CTX`. Provider/model resolvable read-only via `_active()`. No client changes needed for evaluation — the harness is just another caller. |
| Existing repo-native dataset convention | `agents/sample_data.py` | `SAMPLES: list[dict]` — a plain, version-controlled, code-reviewable Python data structure, no database, no external file format. Precedent this document draws on directly (§9). |
| Job/DB/SSE wrapper layer | `server.py:889` (`_run_pipeline`), `:1325` (`_run_explanation`), `:1814` (`_run_comparison_explanation`) | Each wraps its graph/function call with job-lifecycle state (`db.jobs`, `container.job_lifecycle`), SSE publish, and a job-level tracing span. **Not a clean evaluation entry point** — calling these directly would create real job records and SSE traffic for what should be a side-effect-free benchmark run. |
| Test conventions | `pytest.ini`, `.github/workflows/backend-ci.yml` | Fixed `-n 2 --dist loadscope`; `live` marker separates hermetic (`-m "not live"`, every push/PR) from live (`-m live`, needs real Mongo/LLM, main-only). No lint/format/type-check job exists. |
| On-demand script precedent | `backend/scripts/load_test.py` | Plain `argparse` CLI, no new dependency, explicitly manual/opt-in ("`python backend/scripts/load_test.py --concurrency 20`"), never wired into CI. Precedent for this milestone's execution model (§19). |

No evaluation-like utility, benchmark dataset, or fixture-based golden-output pattern exists anywhere in the repository today beyond `sample_data.py`'s ingest-demo data (a different purpose — seed content, not expected-behavior assertions).

---

## 4. M10 Goals

- One versioned golden dataset spanning all three AI-generating surfaces.
- One evaluation harness that runs a dataset case against a surface and produces a normalized result, without embedding surface-specific logic in the core evaluator.
- Behavioral, not textual, correctness checks — the harness answers "did the AI behave correctly," never "did it produce the same words."
- A simple regression signal (PASS/WARNING/REGRESSION/UNCHANGED_FAILURE/INCONCLUSIVE, §18) comparing a new FIXTURE-mode run (§11) against the last recorded FIXTURE-mode run for the same case.
- On-demand, developer-invoked execution only.

---

## 5. Non-Goals (this milestone)

Per the task's explicit boundary — CI blocking gates, deployment gates, provider failover/routing, cost optimization, Redis migration, production capacity planning, SLO/alerting platforms, frontend UX, new production API endpoints, any runtime change to Research/Learning/Comparison Explanation, and production hallucination-detection systems are all out of scope. Also out of scope for *this specific document*: the dataset content itself, the harness code, and any evaluation script — this is architecture only.

---

## 6. Architecture Principles

1. **Behavioral, not snapshot.** No case ever asserts `actual_output == expected_output`. Every case asserts characteristics: a concept is present, a claim is grounded, a citation resolves, a known limitation is acknowledged. This is the load-bearing principle of the whole design — every schema and metric decision below exists to serve it, not the reverse.
2. **Zero pipeline coupling.** The three graphs/functions are called exactly as they exist today (`graph.ainvoke`, `learning_graph.ainvoke`, `generate_explanation`) — never modified to become "more evaluatable."
3. **Normalize at the edge, evaluate in the core.** Surface-specific shape differences (Research's `verified_claims`, Learning's `cited_sources`, Comparison's `sources`/`limitations`) are resolved once, in a thin adapter, into one common shape. The evaluator and metrics never see a surface-specific field.
4. **Reuse production grounding logic where it already exists; do not reimplement it.** `validate_and_map_citations` and `_postprocess_citations` already encode the exact pass/fail grounding rules each surface's real users depend on — wrapping them (read-only, catching their exceptions as signal) keeps the evaluator honest to production behavior instead of drifting from it over time.
5. **Deterministic first.** Every metric in this milestone is rule-based and reproducible. Model-assisted ("LLM-as-judge") evaluation is named and deliberately deferred (§15, §23) — not built casually per the task's own instruction.

---

## 7. Golden Dataset Design

### Schema (per case)

| Field | Required? | Purpose |
|---|---|---|
| `case_id` | Required | Stable, unique identifier. Never reused after removal (a removed case's id retires, per §8). |
| `surface` | Required | One of `research`, `learning`, `comparison_explanation` — routes to the matching adapter (§11). |
| `dataset_version` | Required | The dataset release this case belongs to (§8). |
| `case_version` | Required | Increments only when *this case's* inputs/expectations change, independent of the dataset-wide version (§8). |
| `context` | Required | Surface-appropriate input: `ticker` (+`query`) for Research; `ticker`+`concept`(+`query`) for Learning; a list of report references for Comparison Explanation. |
| `expected_behaviors` | Required | List of structured `ExpectedBehavior` records to check (defined below; §15 evaluates them) — never a bare free-form string. At least one entry required; a case with none is malformed. |
| `expected_evidence` | Optional | Expected grounding characteristics — e.g. a metric that must be cited, a source field expected to be referenced. Optional because not every case needs to pin the evidence shape, only the behavior. |
| `citation_expectation` | Required | Minimum grounding bar for this case: at minimum, "must produce ≥1 valid citation" (the universal floor every surface already enforces in production — `GroundingError`/zero-citation-reject). Cases may raise this bar (e.g. "must cite the guidance figure specifically"). |
| `known_limitations` | Optional | Expected gaps the AI should *acknowledge*, not silently ignore (Comparison Explanation's `limitations` field, Learning/Research's "not disclosed" convention) — optional because most cases have no deliberate data gap. |
| `notes` | Optional | Free-text rationale for why this case exists — human-readable audit trail, not machine-evaluated. |

**Why this shape and no more:** every required field is required because a case cannot be routed (`surface`), replayed reproducibly (`dataset_version`/`case_version`), constructed (`context`), or scored (`expected_behaviors`, `citation_expectation`) without it. Every optional field is optional because a valid, useful case can omit it (not every case needs a named limitation or a pinned evidence characteristic) — making them required would force fabricated content into cases that don't need it, which is exactly the "enormous manually maintained specification" failure mode this question warns against.

**How cases evolve:** adding a case is additive (new `case_id`, current `dataset_version`). Changing a case's expectations bumps only that case's `case_version` (§8) — it does not require re-versioning every other case in the dataset.

### Structured `expected_behaviors` representation

A behavioral assertion must be executable, not prose that only a human can interpret. Each `expected_behaviors` entry is a small structured record:

```
ExpectedBehavior:
  behavior_id   : str    # unique within the case
  type          : "presence" | "absence" | "acknowledgment"   # the three deterministic check strategies §15 already defines
  description   : str    # human-readable, e.g. "identifies revenue decline" — documentation and failure_reasons text only, never itself parsed or matched
  match_rule    : "keyword_variant" | "citation_required" | "limitation_reference"   # which deterministic check §15 runs
  variants      : list[str]   # required when match_rule == "keyword_variant" — acceptable phrase variants, e.g. ["revenue decline", "revenue fell", "lower revenue", "decreased revenue"]
  reference     : str | None   # required when match_rule == "limitation_reference" — the `known_limitations` entry this behavior confirms was acknowledged (this is also where a case's known-unsupported-claim expectation lives, §13's revised metric set)
```

`description` documents intent for a human reviewer; the check itself always executes against `match_rule` + `variants`/`reference`, never against natural-language parsing of `description`. This makes concrete what §15 relies on: a "case-authored acceptable-variant list" is now the required `variants` field on a typed, minimal record, not an implied convention layered on top of a plain string.

**Valid field combinations (Revision 3 — closes an ambiguity Revision 2 left implicit):** `type` and `match_rule` are not independently free — each `match_rule` fixes which `type`(s) it can pair with and which of `variants`/`reference` is required vs. forbidden:

| `match_rule` | Allowed `type` | `variants` | `reference` |
|---|---|---|---|
| `keyword_variant` | `presence` or `absence` | **Required** — ≥1 entry | **Forbidden** — must be absent/null |
| `citation_required` | `presence` only | **Forbidden** — must be absent/null | **Required** — names the citation target the behavior checks for (§15's citation-based presence check) |
| `limitation_reference` | `acknowledgment` only | **Forbidden** — must be absent/null | **Required** — the `known_limitations` entry this behavior confirms was acknowledged |

No other `(match_rule, type)` pairing is valid, and no `match_rule` accepts both `variants` and `reference` populated at once. This table is the full set — no fourth deterministic strategy is introduced (§15's three checks, unchanged). The implementation's Pydantic model for `ExpectedBehavior` should enforce this as a cross-field validator (e.g. a `model_validator` rejecting `variants` set when `match_rule != "keyword_variant"`, and equivalently for `reference`), not leave it as documentation-only convention — the same discipline `agents/schemas.py`'s existing Pydantic models already apply to their own fields (implementation detail, not built by this document).

---

## 8. Dataset Versioning

- **`dataset_version`**: a plain incrementing integer (`1`, `2`, ...), not semantic versioning — there is no meaningfully different "major vs. minor" dataset change at this scale, and `Documentation_Governance.md`'s MAJOR/MINOR/PATCH scheme is for prose documents with reader-facing meaning, not a machine-read case list. Over-engineering this was explicitly out of scope per the task's own instruction.
- **`case_version`**: a plain incrementing integer, scoped to one `case_id`. Bumped only when that case's `context` or `expected_*` fields change.
- **Compatibility:** a case is compatible with a harness run if the harness's evaluator understands its `dataset_version`'s schema shape (in practice: always, until a future dataset schema change — out of scope to design for preemptively).
- **Additions/removals:** additions are free (new `case_id`, no version bump required dataset-wide). Removal retires a `case_id` permanently — it is never reassigned, so a historical evaluation run referencing it stays interpretable (it names a case that once existed, not an unrelated one that exists now).
- **Historical reproducibility:** an evaluation result record (§17) captures the exact `dataset_version` + `case_version` of every case it ran, so a past run remains interpretable even after the dataset file changes later — the result doesn't need the dataset to still look the same, it carries the version it ran against.

---

## 9. Dataset Storage Decision

| Option | Simplicity | Version control | Reviewability | Reproducibility | Dev workflow | Scalability | Maintenance |
|---|---|---|---|---|---|---|---|
| **A. Repo-tracked JSON, one file per case** | High — `json.load`, stdlib only | Native git, full history per case | High — a PR touching one case shows a one-file diff | High — pinned to a commit like any other code | Edit a file, run the harness | Fine to thousands of small files; each stays independently reviewable | Low — no schema-migration tooling needed, Pydantic validates on load |
| **B. Structured fixture files (pytest fixtures / conftest-style)** | Same mechanics as A, framed as test fixtures instead of data files | Same as A | Same as A | Same as A | Same as A, but conflates "test fixture" (pytest-only) with "dataset" (also read by the standalone run script) | Same as A | Same as A |
| **C. Database-backed benchmark dataset** | Low — needs a Mongo collection, a seed/migration step, a query path | Weak — no git diff/blame on a document without extra tooling | Low — a PR cannot show "what changed in this case" without a separate export step | Lower — a query result can silently reflect an in-place edit with no audit trail unless versioning is built on top | Requires the harness to talk to Mongo just to read static data | Unnecessary — dataset size here is dozens to low hundreds of cases, not a scale problem | Higher — now an operational dependency (a running Mongo) for what is otherwise pure data |

**Recommendation: A — repo-tracked JSON, one file per case**, not a database. B is functionally the same storage as A described in test-fixture language — adopting A already gets B's benefits without introducing a second name for the same mechanism, so B is not a distinct choice here. C is explicitly rejected, and not merely because "AlphaScribe uses MongoDB elsewhere" (the task's own warning) — it is rejected on its own merits: a benchmark case is authored and reviewed by a human once, then read many times unchanged; that is exactly what a file in git is for, and a database adds an operational dependency and loses free code-review diffing for a data shape that doesn't need query flexibility, indexing, or concurrent writers. This also matches `agents/sample_data.py`'s own precedent of keeping static, reviewed content in the repository rather than a database — the same instinct, expressed as JSON here since the content is declarative structured data (case fields, list-of-strings), not Python logic, and Pydantic validates it on load regardless of which format it started in.

Concretely: `backend/evaluation/golden_dataset/cases/<case_id>.json`, one JSON object per file, loaded and validated (§7's schema, as a Pydantic model) at harness start.

---

## 10. Evaluation Harness Architecture

```
Golden Dataset (JSON files, §9)
        │
        ▼
  Benchmark Case (validated Pydantic model, §7)
        │
        ▼
  Surface Adapter (§11) ── selects by `case.surface`
        │
        ▼
  AI Execution (the real graph/function — graph.ainvoke /
                learning_graph.ainvoke / generate_explanation,
                UNCHANGED, called exactly as production calls it)
        │
        ▼
  Normalized Output (§11 — adapter's own translation step)
        │
        ▼
  Evaluation (§13–§15 — metrics + behavioral checks, surface-blind)
        │
        ▼
  Evaluation Result (§12 — one record per case, per run)
```

The core evaluator (the box that computes metrics and behavioral verdicts) depends only on the **Normalized Output** shape (§12) and the **Benchmark Case** shape (§7). It imports no surface-specific module (`agents/graph.py`, `agents/learning_nodes.py`, `agents/comparison_explanation.py`) directly — only the three adapters do, each in its own file, each importable independently. This is what makes §21 (a fourth surface needs only a new adapter) true rather than aspirational.

---

## 11. Surface Adapter Architecture

One adapter per surface, each a single function `run(case: BenchmarkCase, mode: "fixture" | "live") -> RawSurfaceOutput`, calling the real pipeline exactly as it exists today — no wrapper class hierarchy, no plugin registry (explicitly avoided per the task's "over-generalized plugin systems" constraint; three concrete functions and a `dict`/`match` dispatch by `case.surface` string is sufficient at this scale, and adding a fourth is one more `elif`/dict entry, not a new abstraction). `mode` selects only *where the evidence comes from* (§11.1 below) — it does not change which function is called or add a fourth adapter.

| Surface | Adapter calls | Inputs built from `case.context` | Raw output read |
|---|---|---|---|
| Research | `graph.ainvoke(initial_state)` — the same compiled graph `server.py:889`'s `_run_pipeline` calls, invoked directly, bypassing job/DB/SSE entirely | `ticker`, `query` → `AgentState`'s `ticker`/`query`/`retry_count`/`trace` (mirrors `_run_pipeline`'s own `initial` dict construction, `server.py:928`) | `draft_report`, `source_documents`, `verified_claims`, `fact_check_status` |
| Learning | `learning_graph.ainvoke(initial_state)` | `ticker`, `concept`, `query` → `LearningState` | `explanation`, `cited_sources`, `source_documents` |
| Comparison Explanation | `generate_explanation(resolved_reports)` (`agents/comparison_explanation.py:197`, already a pure, directly-callable async function — no adapter translation needed on the input side beyond loading the referenced reports) | A list of report IDs → the corresponding report documents, resolved per `mode` — real Mongo lookup (live) or a versioned fixture-report shape (fixture) — see §11.1 | `narrative`, `sources`, `cited_source_indices`, `limitations` |

### 11.1 Execution Modes: Fixture vs. Live

Every adapter call is explicitly mode-scoped — the same three functions, same call pattern above, just a second, mode-dependent source for the evidence each surface's real retrieval step would otherwise fetch live. **Precision required here (Revision 3):** FIXTURE MODE fixes the *input* side only — `case.context`'s evidence is versioned and reproducible — it does **not** fix the *output* side. Research, Learning, and Comparison Explanation all still execute a real `chat_text`/`chat_json` call against a real LLM provider in both modes; nothing about FIXTURE MODE stubs, mocks, or removes the need for a live LLM provider. Reproducibility here means "the same evidence is offered on every run," not "the same output is produced on every run" — output nondeterminism is exactly why §6 principle 1 and §16 require regression to be judged behaviorally/metric-based (grounding status, citation coverage, expected-characteristic coverage), never by comparing generated text across runs. This is the same non-determinism §16 already describes for LIVE mode; FIXTURE mode narrows *which* variable can explain a result change (only the model's response, since the input is now held fixed) — it does not add determinism the LLM call itself doesn't have.

- **FIXTURE MODE — reproducible inputs, live (nondeterministic) model execution.** Comparison Explanation: `case.context` supplies report *content* directly, as a versioned fixture-report shape stored alongside the dataset (§9's same repo-tracked-JSON convention, not read from Mongo) — `generate_explanation(resolved_reports)` is called with that fixture data verbatim, then makes its own real `chat_json` call exactly as production does. Research/Learning: `case.context` supplies fixture `source_documents` directly; the adapter compiles a fixture-scoped graph instance (reusing `build_graph`'s/the Learning graph's own existing `db` parameter — already a dependency-injection seam, not a new one — against a minimal in-memory stand-in satisfying only the read calls `retriever_node` makes) rather than modifying `retriever_node` itself, and the graph's LLM-calling nodes (extractor/tone/synthesizer/fact_checker or explainer) still run for real. The exact stand-in shape is an implementation-phase detail, not fixed here. **FIXTURE MODE is the only mode eligible as a regression baseline or comparison target (§18)** — a baseline's *inputs* must hold still between runs (its outputs are still allowed, and expected, to vary within what the behavioral checks accept).
- **LIVE MODE — real Mongo retrieval, real report resolution, real environment integration** (evidence side; model execution is real LLM in both modes, see above). Confirms the adapter's real integration path still works end-to-end against production data. Recorded in `EvaluationResult` (§12) with `mode: "live"`, but **never used as the reproducibility baseline** — a live run's retrieval/report inputs can themselves change between runs (corpus updates, ranking changes) *in addition to* the model's own output variance, which would make an input change indistinguishable from a genuine model/prompt regression if it were allowed into §18's comparison.

This gives every surface — including Comparison Explanation's Mongo-dependent report resolution — a reproducible fixture path, without a second adapter, a plugin hook, or any change to the three graphs/functions themselves.

Each adapter's own small, private normalization step then maps its raw output into the one shared **Normalized Output** shape consumed by evaluation (§12/§13), built on one explicitly-defined citation record:

```
Citation:
  source_id     : str    # the surface's own identifier for one unit of citable evidence — a 1-based source_documents index (Research/Learning) or a report_number-mapped source entry (Comparison Explanation)
  eligible      : bool   # was this source available to the model as citable evidence at all, independent of whether the model used it
  referenced    : bool   # did the model's raw output name/declare this source, even if the reference later fails validation
  valid         : bool   # did this reference pass the surface's own wrapped production validator (§14) — a real, resolvable citation

NormalizedOutput:
  text                : str            # the generated narrative/explanation/brief
  citations           : list[Citation] # every surface's citation shape normalized to one record — never a raw marker count
  grounding_verdict    : "grounded" | "ungrounded" | "error"  # from §14's wrapped validators
  limitations_stated   : list[str]      # explicit gaps the AI named, if any
  raw                  : dict            # the untouched surface-specific output, kept for debugging only — never read by the evaluator core
```

Per surface, `eligible` is the full evidence set actually offered to the model (Research/Learning: every entry in `source_documents`; Comparison Explanation: every `(report, field)` pair in `build_evidence_payload`'s output); `referenced` is whatever the raw output named at all; `valid` is whatever survived §14's wrapped validator (`compute_scorecard`'s in-range cited-marker set, `_postprocess_citations`'s returned indices, or `validate_and_map_citations`'s `cited_source_indices`, respectively). This population happens entirely inside each adapter's own normalization step — the core evaluator only ever sees the finished `Citation` list, never a surface's raw citation representation.

No production file in `agents/` is edited to produce this — the translation lives entirely in the (new, not-yet-created) adapter module.

---

## 12. Evaluation Result Model

One record per (case, run):

```
EvaluationResult:
  run_id                : str   # generated per harness invocation, groups all cases in one run
  case_id                : str
  dataset_version        : int
  case_version            : int
  surface                : str
  mode                    : "fixture" | "live"   # §11.1 — which evidence source produced this result
  timestamp               : str   # ISO 8601, stamped by the caller at run time (not inside harness code — Workflow/tooling-agnostic; mirrors this repository's own constraint on scripts that must not call datetime.now() inside deterministic logic)
  provider                : str | None   # from agents.llm._active(), read-only
  model                   : str | None
  prompt_version          : str | None   # ONLY populated where a surface exposes an explicit version constant — Comparison Explanation's PROMPT_VERSION today (§17); null for Research/Learning
  prompt_fingerprint       : str | None   # content hash of the prompt template actually used — the only reproducibility signal available for Research/Learning today (§17); never conflated with prompt_version
  schema_version           : str | None
  code_revision            : str          # git commit hash of the working tree at run time (§17), suffixed "-dirty" if uncommitted changes are present
  evaluation_version        : str        # version of the harness/metrics logic itself, so a metric-definition change is distinguishable from a model/prompt change
  metrics                 : dict[str, float | bool | str]   # §13 — grounding status is a string, not a rate
  verdict                 : "PASS" | "WARNING" | "REGRESSION" | "UNCHANGED_FAILURE" | "INCONCLUSIVE"   # §18 — see §18's truth table; IMPROVEMENT is deliberately not a v1 state
  failure_reasons          : list[str]    # human-readable, e.g. "expected_behavior 'acknowledges missing segment data' not satisfied"
```

Stored at `backend/evaluation/results/`, one flat JSON result-artifact file per run — **git-ignored**, exactly like `backend/coverage.xml` (a local/CI run artifact, never committed dataset content). The **local baseline** for a given `(case_id, dataset_version, case_version)` is simply the most recent FIXTURE-mode result file on disk carrying that exact key (§18); if none exists, the comparison returns INCONCLUSIVE by definition, not an error. No persistent database, and no remote/shared result store, is introduced at this milestone's scale (dozens of cases, developer-invoked, local runs) — if evaluation ever needs cross-run trend queries at volume or across machines, that is itself a future-triggered capacity concern (Document 17 §7.4's own pattern: build the store when evidence demands it, not ahead of it).

---

## 13. Metrics

| Metric | Input | Calculation | Interpretation | Limitations |
|---|---|---|---|---|
| **Citation coverage** | `NormalizedOutput.citations` (the normalized `Citation` list, §11) | Let `E = len([c for c in citations if c.eligible])`, `V = len([c for c in citations if c.valid])`. **If `E == 0`: `citation_coverage = null` (not applicable — never a divide-by-zero, never silently reported as `0.0`).** If `E > 0`: `citation_coverage = V / E`, which is `0.0` when `E > 0` and `V == 0` (evidence was offered, nothing valid cited) — a genuinely different, worse case than "no evidence existed to cite," and the two must not collapse to the same number. | Higher = more of the evidence actually offered to the model was validly used; `null` = the case offered no citable evidence at all, a dataset-authoring signal, not a model-quality one | A high score doesn't prove the citations are *correct* beyond what §14's wrapped validator already checks — it measures coverage of validated citations, not independent fact-correctness. Whether an `E == 0` case (or a `V == 0` case) makes the case *fail* is entirely governed by `case.citation_expectation` (§7) — a case whose own `citation_expectation` requires ≥1 valid citation fails on `V == 0` regardless of what `citation_coverage` reports; `citation_coverage` is a diagnostic metric, `citation_expectation` is the pass/fail gate (§13's Case pass/fail row) |
| **Grounding status** | `NormalizedOutput.grounding_verdict` (from the wrapped production validator, §14) | Direct pass-through of the surface's own binary verdict — `"grounded"` or `"ungrounded"`/`"error"` — reported as a status string, never averaged or rated | Whether the surface's own production grounding rule was satisfied for this one case | Not a rate — this design has no per-claim extraction to compute a genuine claim-level rate from. Renamed from an earlier draft's "grounded-claim rate," which implied a granularity this design doesn't have |
| **Expected-characteristic coverage** | `case.expected_behaviors` (structured, §7), `NormalizedOutput.text` (+ `limitations_stated`) | Fraction of `expected_behaviors` entries satisfied (§15's rule-based check per `match_rule`) — a case's known-unsupported-claim expectations are checked here too, via a `match_rule: "limitation_reference"` entry, not a separate metric | Whether the AI did what the case actually asked it to do, including correctly naming its own limitations — the metric closest to "behaved correctly" | Deterministic keyword/phrase matching (§15) — the known false-negative risk of legitimate paraphrase is accepted for v1, not solved. Only catches limitations a case author explicitly anticipated and encoded as a behavior — generic, un-anticipated hallucination detection stays deferred (§23) |
| **Case pass/fail** | All of the above + `case.citation_expectation` | Boolean AND of: citation floor met, grounding status = grounded, all required `expected_behaviors` satisfied | The single verdict rolled into `EvaluationResult.metrics["pass"]` before §18's regression comparison | Only as good as the case's own authored expectations — garbage-in/garbage-out is a dataset-authoring risk, not a harness defect |

No metric beyond these four is defined for M10 — each earns its place by mapping directly to one of the task's own listed examples (grounding, citation, characteristic coverage, pass/fail); nothing was added purely for apparent comprehensiveness. A generic, claim-level unsupported-claim *rate* was deliberately removed from Revision 1 of this design (see the header's Revision 2 note) — this design has no claim-level extraction from plain output text to compute one honestly; what a case can assert instead is a specific, case-authored expectation that a *named* limitation gets acknowledged (an `expected_behaviors` entry, above), never a repository-wide hallucination statistic. Generic adversarial hallucination detection remains explicitly deferred (§23), not attempted by approximation here.

---

## 14. Citation Evaluation

Per-surface, reusing what already exists in production rather than reimplementing citation logic a fourth time (three call sites — `scoring.py`, `comparison_explanation.py`, `learning_nodes.py` — already independently implement the same `[n]`-marker convention; the evaluator does not add a fifth from scratch):

- **Comparison Explanation → wrap.** `validate_and_map_citations` (`agents/comparison_explanation.py:124`) already *is* the production grounding check. The adapter calls it exactly as `agents/comparison_explanation.py:210`'s own `generate_explanation` does; a raised `GroundingError` maps directly to `grounding_verdict = "ungrounded"`, success maps to `"grounded"`. This is the strongest case for wrapping: the function already returns exactly the pass/fail signal needed, with zero adaptation.
- **Learning → wrap.** `_postprocess_citations` (`agents/learning_nodes.py:20`) is already a pure, side-effect-free, importable function returning `(cleaned_text, cited_indices)`. The adapter calls it on the raw `explanation` text; an empty `cited_indices` list maps to `"ungrounded"` (mirroring `explainer_node`'s own zero-citation-reject rule at `agents/learning_nodes.py:90`), non-empty maps to `"grounded"`.
- **Research → wrap.** `compute_scorecard` (`agents/scoring.py:28`) already reads exactly the fields `AgentState`'s final value carries (`draft_report`, `source_documents`, `verified_claims`, `fact_check_status`) — no fake-report translation is needed, since the raw graph output *is* report-shaped. The adapter calls `compute_scorecard` directly on the graph's final state dict; `faithfulness < 1.0` or `context_precision == 0.0` maps to `"ungrounded"`.

**Why wrap instead of independently reimplementing or extending:** an independent reimplementation (a fourth citation-regex implementation) would drift from whatever the production functions actually enforce the moment either side changes — exactly the kind of duplicated-logic risk `01 D-3`'s LLM-dispatch consolidation was fixed to prevent, generalized here to citation logic. Wrapping means the evaluator is *by construction* honest to what production actually does today, and a future change to any of these three functions is automatically picked up by evaluation without a second edit. **Why not "extend"** (adding new shared parameters/hooks to the production functions themselves): that would touch `agents/comparison_explanation.py`, `agents/learning_nodes.py`, and `agents/scoring.py` — explicitly prohibited ("do not modify existing AI pipelines," and `compute_scorecard`/`validate_and_map_citations` are pipeline-adjacent scoring/grounding logic, not evaluation infrastructure). This design calls all three exactly as they exist, read-only.

---

## 15. Behavioral Evaluation

`expected_behaviors` entries are short, human-authored strings (e.g. *"identifies revenue decline," "acknowledges missing segment data," "does not claim an unsupported causal explanation"*). Each is evaluated by a small, deterministic, rule-based checker — **not** exact-text matching:

- **Presence-style behaviors** ("identifies revenue decline"): matched against a case-authored list of acceptable keyword/phrase variants (e.g. `["revenue decline", "revenue fell", "lower revenue", "decreased revenue"]`), case-insensitive substring/token check. The case author supplies the variant list as part of authoring the case (an addition to `expected_behaviors`'s representation, not a new top-level dataset field) — this keeps the check deterministic while tolerating legitimate paraphrase within an author-approved set, rather than requiring the model's exact wording.
- **Absence-style behaviors** ("does not claim an unsupported causal explanation"): checked as the *negative* of the grounding metric (§13) plus, where the case names a specific forbidden claim shape, a keyword-absence check mirroring the presence check above.
- **Acknowledgment-style behaviors** ("acknowledges missing segment data"): checked against `NormalizedOutput.limitations_stated` (populated from `limitations`/`known-gap` fields each surface's real output already carries — Comparison Explanation's `limitations`, or a "not disclosed" phrase match for Research/Learning, which don't have a structured limitations field today).

**Is this deterministic, rule-based, structured, or model-assisted?** Deterministic and rule-based, by design — keyword/phrase-variant matching against author-supplied acceptable-variant lists, no LLM call in the evaluation path itself.

**Why deterministic evaluation is judged sufficient for M10, and LLM-as-judge is not introduced:** the task's own instruction requires justifying this explicitly, so: (1) deterministic checks are reproducible — the same case run twice against the same output gives the same verdict, which a model-assisted judge cannot guarantee without its own drift/versioning problem layered on top of the one this milestone is trying to solve; (2) every metric this milestone needs (grounding, citation coverage, characteristic presence/absence) is already expressible as a rule against structured or lightly-parsed text, per §13 — there is no case in this design where only a second LLM call could answer the question; (3) a model-assisted judge would itself need its own evaluation (is the judge reliable? does it drift when *its* model changes?) — a second, nested version of exactly the problem `01 D-10` names, not a solution to it. **This belongs deferred, not built here** — named explicitly in §23 as a future extension once the deterministic layer proves where its false-negative rate (accepted-paraphrase misses) is actually too high in practice, which is itself evidence this milestone's own regression tracking (§18) would surface over time.

---

## 16. Non-Determinism

Correct variation and actual regression are distinguished by evaluating **characteristics, never text**: two runs producing differently-worded narratives that both satisfy the same `expected_behaviors`, `citation_expectation`, and grounding verdict are both `PASS` — no output-equality check exists anywhere in this design (§6 principle 1). A regression is a *verdict* change (§18) — a case that previously satisfied its behavioral/grounding checks now fails them, or a metric crosses below its case-defined floor — never a diff against previous wording. This is what makes the architecture immune to legitimate LLM output variance by construction, not by a tolerance threshold bolted on afterward.

---

## 17. Reproducibility

Recorded per `EvaluationResult` (§12): `dataset_version`, `case_version`, `mode`, `provider`, `model` (both read from `agents.llm._active()`, read-only), `evaluation_version` (the harness/metric-logic version, incremented independently of dataset/case versions), `run_id`, `timestamp`.

**`prompt_version` vs. `prompt_fingerprint` — a genuine gap, named precisely rather than worked around or blurred:** Comparison Explanation already exposes `PROMPT_VERSION`/`SCHEMA_VERSION` (`agents/comparison_explanation.py:28-29`) — the harness records these directly into `prompt_version`/`schema_version` for that surface. Research and Learning have **no equivalent version constant today** (verified by direct read of `agents/nodes.py`'s and `agents/learning_nodes.py`'s prompt strings — no version marker exists), so `prompt_version` stays `null` for them. For those two, the harness instead records **`prompt_fingerprint`** — a content hash of the prompt template string actually used — as their only available reproducibility signal. This is a distinct, separately-named field, not `prompt_version` repurposed: a hash proves *that* the prompt text changed, but carries none of the deliberate, human-assigned meaning an explicitly-bumped version string does, and reusing one name for both would misrepresent a mechanical byproduct as an intentional versioning decision. Adopting explicit `PROMPT_VERSION` constants on those two surfaces (mirroring M9.1's own precedent) is named here as a natural, tiny follow-up for whoever authorizes M10 implementation — not built now.

**`code_revision`:** the git commit hash of the working tree at the moment a run executes (`git rev-parse HEAD`, stdlib `subprocess` — no new dependency, no production runtime change), suffixed `-dirty` if uncommitted changes are present. This ties a result to the exact code that produced it, independent of whether that code was ever captured by a milestone document — directly relevant given Comparison Explanation itself is, as of this writing, an uncommitted working-tree state (Document 44 §2C): an honest `-dirty` suffix reflects that instead of implying a false pin to a specific, merged commit.

No secrets (API keys, provider credentials) are ever part of an `EvaluationResult` — only `provider`/`model` *names*, exactly as `llm_calls_total`'s existing Prometheus labels already do (`agents/llm.py:367`), never the key itself.

---

## 18. Regression Semantics

Five verdicts, deliberately simple — no statistical framework, confidence interval, or trend model, since nothing in this repository's current evaluation volume (dozens of cases, developer-invoked runs) justifies one. Revision 3 closes a gap in Revision 2's rule set: every baseline/current pass-fail combination now has a defined outcome, not only the two Revision 2 named.

| Verdict | Precise rule |
|---|---|
| **PASS** | Current FIXTURE-mode run's `case.metrics["pass"]` is `true`, and either no baseline exists, the baseline was also `true`, **or the baseline was `false`** (a previously-failing case that now passes is `PASS`, not a restored `IMPROVEMENT` state — §18 Revision 2 already rejected reintroducing that verdict, and this rule doesn't reopen it). |
| **WARNING** | Current run's `case.metrics["pass"]` is `true`, but `citation_coverage` or `expected_characteristic_coverage` is strictly lower than the baseline run's value for the same metric, without crossing below the case's own required floor (`citation_expectation` / all-required-behaviors-satisfied still holds). |
| **REGRESSION** | Baseline `case.metrics["pass"]` was `true`; current run's is `false`. |
| **UNCHANGED_FAILURE** | Baseline `case.metrics["pass"]` was `false`; current run's is also `false`. Distinct from REGRESSION (nothing newly broke) and distinct from PASS (the case still doesn't meet its own bar) — a still-broken case must not silently read as either "just regressed" or "fine." |
| **INCONCLUSIVE** | No prior FIXTURE-mode result exists for this exact `case_id` + `dataset_version` + `case_version` key (nothing to regress against yet), or the AI call itself errored (a provider/network failure, not a quality signal — must not be misreported as REGRESSION or UNCHANGED_FAILURE). |

**Truth table** (baseline pass/fail × current pass/fail, both from FIXTURE-mode runs only):

| Baseline | Current | Verdict |
|---|---|---|
| *(none)* | pass or fail | INCONCLUSIVE |
| pass | pass, no soft-metric drop | PASS |
| pass | pass, soft-metric drop within floor | WARNING |
| pass | fail | REGRESSION |
| fail | pass | PASS |
| fail | fail | UNCHANGED_FAILURE |
| *(any)* | AI execution errored | INCONCLUSIVE |

**No `IMPROVEMENT` state — unchanged from Revision 2, reaffirmed here.** A newly-passing case is `PASS` (table above), not a distinct "it got better" state: this design's single-most-recent-baseline model (below) can't reliably distinguish a genuine fix from a single flaky pass without more run history than a v1 local result store retains, and unlike REGRESSION/UNCHANGED_FAILURE (both real, current problems worth surfacing even imperfectly), an "IMPROVEMENT" that turns out to be flaky costs nothing to instead just report as PASS.

**Baseline = the most recent prior FIXTURE-mode `EvaluationResult` file in `backend/evaluation/results/` for the exact same `(case_id, dataset_version, case_version)` key** (§12) — not a statistical aggregate, not a rolling average, and never a LIVE-mode run (§11.1 — LIVE-mode results are recorded but never eligible as a baseline or comparison target, since their own inputs can vary run to run). This is the simplest baseline definition that still answers "did this get worse since last time," matching the task's own instruction not to build a complex statistical framework the repository doesn't yet need.

---

## 19. Execution Model

Developer/on-demand only, mirroring `backend/scripts/load_test.py`'s exact convention (§3): a plain script (`python backend/scripts/run_evaluation.py --mode fixture|live`, not created by this document — see §24), explicit invocation, no new dependency. **FIXTURE mode** (§11.1, the default and the one used for regression tracking) needs only a live LLM key — no Mongo, since fixture inputs bypass retrieval entirely. **LIVE mode** additionally needs a live Mongo, matching the `pytest -m live` suite's existing requirement — not a new operational dependency, just a new consumer of one that already exists. **Not wired into `.github/workflows/backend-ci.yml`** — no blocking gate, no automatic trigger, per the explicit non-goal (§5) and Document 17 §7.1's own "once golden datasets + regression evaluation exist to run" framing for the (separately scoped, not-in-M10) CI job.

---

## 20. Testing Strategy

Two categories, matching this repository's existing hermetic/live split (§3):

**Hermetic (default suite, no live provider/Mongo):**
- Dataset schema validation — a case missing a required field (§7) is rejected with a clear error, not silently accepted.
- Malformed benchmark cases — duplicate `case_id`, `expected_behaviors` empty, `surface` not one of the three known values.
- Deterministic scoring — each metric (§13) computed against a fixed, hand-constructed `NormalizedOutput` fixture, asserting the exact expected number/verdict (no AI call).
- Citation evaluation — the three wrapped functions (§14) exercised against fixed inputs known to trigger both their grounded and ungrounded paths, using the same fixtures those functions' own existing test files already use (`tests/unit/test_comparison_explanation_*.py`, `tests/unit/test_scoring.py` precedent) rather than inventing new fixtures that could drift from production's own test data.
- Behavioral characteristic evaluation — fixed text fixtures against fixed `expected_behaviors` lists, covering presence/absence/acknowledgment cases.
- Result normalization — each adapter's translation step, tested against a fixed raw-output fixture per surface (no real `graph.ainvoke`/`chat_json` call).
- Fixture-mode adapter paths — each adapter's FIXTURE-mode branch (§11.1) exercised against a fixed fixture report/source-document set, confirming it never attempts a live Mongo or LLM call in this test category.
- Regression comparison — fixed pairs of prior/current `EvaluationResult` fixtures, asserting each of the five verdicts and every cell of §18's truth table is produced correctly, including the no-prior-baseline → INCONCLUSIVE case and the LIVE-mode-never-a-baseline rule.
- Version compatibility — a case at an old `dataset_version`/`case_version` still loads and evaluates correctly.
- Adapter contract — each adapter, given a fixed case, returns a `NormalizedOutput` with all required fields populated (structure check, not a real AI call).
- Failure handling — a simulated AI-call exception surfaces as INCONCLUSIVE (§18), never crashes the harness or mis-reports as REGRESSION.

**Live (separate, explicitly marked, not run by default — mirrors `pytest.mark.live`):**
- End-to-end: a real benchmark case run against a real graph/LLM call, confirming the adapter's real (not fixture) output normalizes correctly. This is the only category needing a live provider/Mongo, and it is the harness's actual purpose (§19) — kept separate from the hermetic suite exactly as `backend_test_iter2.py` etc. already are, not blended into it.

---

## 21. Extensibility

A fourth AI-generating surface requires exactly: (1) a new adapter function (`run(case) -> NormalizedOutput`, §11's pattern) and (2) new benchmark cases with `surface = "<new_surface>"` (§7). It requires **no** change to the core evaluator, the `EvaluationResult` schema (§12), or any metric definition (§13) — every one of those already operates only on the surface-blind `NormalizedOutput` shape (§6 principle 3). This is verified structurally by this design, not assumed: nothing in §12–§18 references a surface-specific field name anywhere.

---

## 22. Risks

- **Dataset maintenance burden.** A golden dataset needs periodic human curation as the product evolves (new metrics, new expected behaviors as features change) — an ongoing cost this document does not eliminate, only bounds (§9's one-file-per-case keeps each update small and reviewable).
- **Deterministic behavioral checks are false-negative-prone on legitimate paraphrase outside a case's authored variant list** (§15) — accepted for v1; the mitigation is widening variant lists over time, not switching to LLM-as-judge prematurely (§23).
- **Citation-metric reuse couples evaluation to three production functions' current signatures** (§14) — a future refactor of `compute_scorecard`, `validate_and_map_citations`, or `_postprocess_citations` could silently break the evaluation adapters if their call signature changes without the adapter being updated in the same change. Mitigated by the adapter-contract tests (§20), which would fail loudly, not silently.
- **No `PROMPT_VERSION` on Research/Learning today** (§17) — the content-hash proxy is a real workaround, not the clean solution; if those two surfaces' prompts change materially and often, the case for adding explicit version constants (a tiny, separately-authorized pipeline change) strengthens.
- **M9's own unmerged/governance-unresolved state** (Document 44 §2) — Comparison Explanation, one of the three surfaces this design evaluates, exists only in the working tree as of this writing. If M9 changes materially before merge, the Comparison Explanation adapter (§11) may need revisiting before implementation — flagged, not resolved here, consistent with Document 44's own finding that this is M9's unfinished business, not M10's to fix. `code_revision`'s `-dirty` suffix (§17) makes this state visible in every result record rather than silently assumed away.
- **Fixture reports/documents (§11.1) can drift from what a live Mongo-resolved report would actually contain** as the product evolves (a real report's `extracted_data`/`scorecard` shape changing). Accepted for v1 since fixture content is versioned and human-curated alongside the dataset (§9) — LIVE-mode runs (§11.1) exist specifically to catch this drift, even though they deliberately never feed the regression baseline.

---

## 23. Alternatives Considered

| Alternative | Rejected because |
|---|---|
| LLM-as-judge behavioral evaluation | Introduces a second, unversioned quality-drift problem on top of the one being solved (§15); every M10-scope metric is already expressible deterministically. Deferred as a named future extension once deterministic false-negative rate is evidenced as a real problem, not assumed one. |
| Database-backed golden dataset (MongoDB) | Rejected on its own merits, not merely "avoid Mongo by reflex" (§9) — loses git-native reviewability for authored, rarely-changing data; adds an operational dependency the repository's own `CLAUDE.md` "keep dependencies lean" convention argues against for what a directory of JSON files already solves. |
| Single giant JSON dataset file | Rejected in favor of one-file-per-case (§9) — a monolithic file makes every PR touching any case show a large, hard-to-review diff; one file per case keeps every dataset change small and independently reviewable, matching this repository's own preference for small, attributable diffs (established across every milestone report in this index). |
| Calling `_run_pipeline`/`_run_explanation`/`_run_comparison_explanation` directly (server.py) | Rejected (§3, §11) — these wrap job-lifecycle/DB/SSE side effects inappropriate for a benchmark run; the compiled graphs and pure functions underneath them are the correct, already-existing integration seam. |
| A generalized plugin/registry system for surface adapters | Rejected as premature (§11, architectural constraints) — three concrete adapter functions dispatched by a `surface` string field is sufficient at three (soon four) surfaces; a plugin architecture solves a scaling problem this repository doesn't have yet, the same reasoning Document 17 §7.4 already applies to infrastructure capacity. |
| Wiring evaluation into CI as a blocking gate now | Explicitly out of scope (§5, §19) — Document 17 §7.1's own trigger for this ("once golden datasets + regression evaluation exist to run") is itself downstream of this milestone, not concurrent with it. |

---

## 24. Implementation Sequencing (informational — not authorized by this document)

Sketched for whoever eventually receives implementation authorization; sequencing here does not itself authorize anything (§25):

1. Dataset schema (Pydantic model, §7) + JSON loader/validator + hermetic validation tests (§20).
2. Three surface adapters (§11), each independently testable against fixed fixtures, no live calls required for their unit tests.
3. Metrics (§13) + citation-evaluation wrapping (§14) + `EvaluationResult` model (§12) — all hermetic.
4. Regression comparison (§18) + the on-demand run script (§19, mirroring `load_test.py`) + first authored golden-dataset cases (a small seed set, not exhaustive coverage on day one) + the live end-to-end test category (§20).

Each phase is independently reviewable and independently revertible; nothing in this sequencing requires phases 2-4 to land in a single change.

---

## 25. CTO Decision Required

**M10 Architecture:**
🟡 PROPOSED / AWAITING CTO APPROVAL

**M10 Implementation:**
🔴 NOT AUTHORIZED

This document proposes an architecture only. No dataset, harness, adapter, metric, or script exists yet, and no existing AI pipeline file was modified to produce this design. Implementation authorization is a separate, subsequent CTO decision.
