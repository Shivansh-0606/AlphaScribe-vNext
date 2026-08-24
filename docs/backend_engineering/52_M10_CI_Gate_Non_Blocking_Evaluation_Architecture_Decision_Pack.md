# 52 — M10 CI-Gate / Non-Blocking Evaluation Architecture Decision Pack

**Status:** 🟢 CTO-RATIFIED (architecture) — Reviewer 3: `PASS`. **Implementation
remains 🔴 NOT AUTHORIZED** — a separate, subsequent CTO decision (§16).
**Type:** Architecture investigation (research/design-only — no code changed, no
workflow modified, no evaluation runner modified)
**Authorization:** CTO Decision B (Candidate 1 selected) — authorizes
production of this architecture decision pack only. **Implementation is not
authorized by this document.**
**Revision 1** — Reviewer 3 architecture-review corrections: (1) replaces the
original blanket "capture the exit code, never propagate it" rule, which
could silently render an infrastructure/execution failure as an apparently
successful job, with an explicit verdict-vs-execution-status contract (§4,
§5.1); (2) makes §8's baseline-compatibility mechanism precise — the CI
artifact-retrieval step stages candidate files only, and never itself
decides compatibility; that decision remains entirely owned by the existing,
unmodified `find_baseline()` (§8); (3) adds explicit concurrent-main-run
semantics (§8.1); (4) makes the Research/Learning FIXTURE-mode gap's CI
classification explicit, distinct from an unexpected adapter failure (§8.2).
No decision from the original document is reversed by this revision.
**Depends on (cited, unmodified):**
[44_Post_M9_Backend_AI_Roadmap_Reconciliation.md](44_Post_M9_Backend_AI_Roadmap_Reconciliation.md) §8,
[45_M10_Pre_Implementation_Architecture_Decision_Pack.md](45_M10_Pre_Implementation_Architecture_Decision_Pack.md) §5/§11.1/§18/§19,
[46_M10_Phase4_Pre_Implementation_Plan.md](46_M10_Phase4_Pre_Implementation_Plan.md),
[47_Hallucination_Detection_Architecture_Decision_Pack.md](47_Hallucination_Detection_Architecture_Decision_Pack.md) §7.4/§9.1/§13,
[10_Backend_Security_Architecture.md](10_Backend_Security_Architecture.md) `SD-12`,
[51_Post_M11_Backend_AI_Roadmap_Reconciliation.md](51_Post_M11_Backend_AI_Roadmap_Reconciliation.md) §21(i).
**Date:** 2026-08-23.

---

## 0. What This Document Is and Is Not

This is the architecture-decision-pack Document 51 §21(i)/§16 identified as
missing: a dedicated design for wiring the existing M10 evaluation harness
into CI, non-blocking, the way every other scope expansion in this series
(Document 41 for M9, Document 45 for M10 itself, Document 47 for
hallucination detection) received its own decision pack before
implementation. It designs; it does not implement. No `.github/workflows/`
file, no `evaluation/` module, and no `agents/` file is modified by this
document.

## 1. Existing Architecture Dependency (verified this session, direct reads)

| Component | File | Verified finding |
|---|---|---|
| Evaluation CLI | `backend/scripts/run_evaluation.py` | Already exists, works, argparse `--mode fixture\|live`, `--format text\|json`. **Explicitly not wired into CI today** (own docstring: "Deliberately NOT wired into `.github/workflows/backend-ci.yml`"). **Three, not two, distinct exit paths, verified directly (lines 120/128/143):** `SystemExit(2)` for `DatasetIntegrityError` or an unknown `--case-id` — the run never started, a construction/configuration failure; `SystemExit(1)` when `had_error or had_regression` among cases that *did* run and produced a result — the run completed and has content to report; `SystemExit(0)` otherwise. Exit `1` is **content**, not failure — it fires on a legitimate, non-blocking `REGRESSION` verdict exactly as readily as on a per-case `AdapterError`. Load-bearing distinction for §4/§5.1 below. |
| Adapter error hierarchy | `evaluation/adapters/types.py` (full class definitions read) | `AdapterError` has five subclasses: `InvalidBenchmarkInputError`, `AdapterInvocationError`, `ProviderExecutionError`, `MalformedAIOutputError` (four genuine failure categories), and `UnsupportedExecutionModeError` — explicitly documented as "not a case-input problem, not a provider failure — the capability itself is not built," i.e. an intentional, already-known limitation, not a failure. **The type distinction already exists in code.** `run_evaluation.py::run_case`'s `except AdapterError as e: return None, f"{case.case_id}: adapter error — {e}"` catches the common base and stringifies before this JSON reaches `_print_json`/`save_result` — the exception *class* (and therefore the intentional/unexpected distinction) is not currently propagated into the CLI's serialized output. Load-bearing for §8.2 below. |
| Baseline storage | `evaluation/regression/result_store.py` | `RESULTS_DIR = backend/evaluation/results/`, **git-ignored** (module docstring, confirmed). `find_baseline()` looks for the most recent compatible prior FIXTURE-mode result in that directory. **On a fresh, ephemeral CI runner this directory is always empty** — no baseline can ever be found unless something persists it across runs. This is the single largest gap between "the CLI works" and "the CLI works usefully in CI," and is not solved by any existing code. |
| Regression verdict | `evaluation/regression/types.py` | Five-state, already frozen: `PASS \| WARNING \| REGRESSION \| UNCHANGED_FAILURE \| INCONCLUSIVE` (Document 45 §18, Document 46 §6, deliberately no `IMPROVEMENT`). This is an existing, ratified classification — see §7 below. |
| Judge-trust exclusion | `evaluation/core/case_evaluator.py::_counts_toward_aggregation` | Already enforces Document 47 §7.4/§9.1: a `model_judged_support` behavior's status cannot move `CaseEvaluationResult.status` while `JUDGE_SELF_CONSISTENCY_GATE_VERSION == 0`. **This is enforced at the evaluation-logic layer, not the CI layer** — a CI job that simply runs the existing CLI inherits this safety property automatically; it does not need to be re-implemented in CI. |
| FIXTURE-mode coverage | `evaluation/adapters/research.py` (verified directly: raises `UnsupportedExecutionModeError` for `mode="fixture"`) | Confirms Document 47 §7.0's finding in code: **Research and Learning have no FIXTURE mode.** Only Comparison Explanation does. A CI evaluation job today can only produce a regression-eligible (FIXTURE-mode, non-LIVE) result for Comparison Explanation. |
| Even FIXTURE mode needs a live model call | `run_evaluation.py` docstring | "FIXTURE mode needs only a live LLM key (no Mongo)" — FIXTURE fixes *inputs* only; every mode makes a real, non-deterministic LLM call (Document 45 Revision 3's own correction). **This means an evaluation CI job has the same secret-exposure profile as the existing `live` test job — not the `hermetic` job's "no secrets, no network" profile.** |
| CI structure today | `.github/workflows/backend-ci.yml` (full file read) | Two jobs. `hermetic`: every push/PR, `-m "not live"`, dummy env only, no real network/LLM. `live`: gated `github.event_name == 'push' && github.ref == 'refs/heads/main' && github.repository == '<owner-repo>'` — **main-push only, never a PR, fork or otherwise** — and is currently a **documented skeleton**: it skips itself with an `::notice::` if `CI_MONGO_URL`/`CI_GEMINI_API_KEY` secrets aren't configured, which they currently are not. `10 SD-12`: "the only job holding API keys must never run on untrusted PR code," implemented here even more conservatively than the minimum (main-push-only, not just non-fork-PR). |
| Existing artifact-persistence idiom | `.github/workflows/backend-ci.yml`, `hermetic` job | `actions/upload-artifact@v4` already uploads `backend/coverage.xml` with `retention-days: 14`. **A directly reusable, already-in-use pattern** for persisting `evaluation/results/` across runs — no new GitHub Actions primitive is needed. |
| Observability | `infrastructure/observability/metrics.py` (full symbol list read) | `prometheus_client`-based, **pull-based** (`render_latest()` scraped from a live running server's `/metrics` endpoint). Zero evaluation-specific metrics exist. **Architecturally, this stack does not fit an ephemeral CI job** (there is no long-running process for Prometheus to scrape) — CI observability needs a different, CI-native surface (§10). |
| Dataset size today | `evaluation/golden_dataset/cases/*.json` (globbed) | Exactly 4 cases: 1 Research, 1 Learning, 2 Comparison Explanation. Concrete, small, cheap — informs §9's cost estimate. |
| Dataset integrity | `evaluation/golden_dataset/loader.py::DatasetIntegrityError` | Already validates on load: no case files, invalid JSON, schema/invariant failure, or duplicate `case_id` all raise one collected exception. CI does not need to add its own dataset-validation layer — the loader already fails loudly and specifically. |

No file above is modified by this document. Every design choice below is
derived from, and constrained by, this table.

## 2. Architectural Problem — Answered

1. **What evaluation runs in CI?** The existing `run_evaluation.py` CLI,
   unmodified, invoked exactly as a developer would run it locally
   (`python backend/scripts/run_evaluation.py --mode fixture --format json`).
   No new evaluation logic is designed by this document.
2. **What is deterministic?** `numeric_consistency`, `keyword_variant`,
   `citation_required`, `limitation_reference` — the existing Phase 1-3
   behaviors (Document 45 §7, unaffected by this document).
3. **What is LLM-based?** `model_judged_support` — already excluded from
   aggregation while the gate is `0` (§1 above), automatically, with no CI
   involvement required.
4. **What is blocking?** Nothing, by this document's own recommendation
   (§4). No behavior, case, or verdict is authorized to fail a CI job.
5. **What is non-blocking?** Everything the evaluation job produces — see
   §4/§6.
6. **What produces artifacts?** One JSON result file per (case, run)
   already exists (`result_store.py::save_result`); this document adds only
   a CI step that uploads the `results/` directory as a workflow artifact
   (§8) — reusing, not inventing, the pattern already used for
   `backend-coverage`.
7. **What constitutes an evaluation failure?** No verdict is redefined.
   `REGRESSION`/`FAIL`/`INCONCLUSIVE` at the evaluation-result level remain
   exactly what Document 45 §18 already defines. A CI *job* failure is a
   distinct, narrower concept this document deliberately does not conflate
   with them — see §4.
8. **How are historical results protected?** By not touching them: this
   document proposes uploading `results/` as a workflow artifact
   (retained, versioned by GitHub, same as `backend-coverage`), never
   overwriting or deleting a prior artifact. The golden dataset and Run 1
   H-1 artifact conventions (immutable, never regenerated) are the pattern
   this reuses, not a new one.
9. **How is reproducibility handled?** `code_revision` (git commit hash)
   is already stamped on every `EvaluationResult` (§1) — sufficient
   attribution; this document adds nothing new here.
10. **How are costs controlled?** By scope (§9): 4 cases today, one run per
    push to `main` only (never per-PR, never per-push-to-any-branch, matching
    the existing `live` job's own trigger condition exactly) — see §9.
11. **How are flaky LLM evaluations handled?** Not newly solved here — the
    existing `INCONCLUSIVE` verdict and provider-failure-maps-to-
    `INCONCLUSIVE` convention (Document 47 §7.3, applied throughout
    `evaluation/core/`) already absorbs this; a flaky/failed call never
    produces a spurious `REGRESSION`.
12. **How are results surfaced to engineers?** A GitHub Actions job summary
    (`$GITHUB_STEP_SUMMARY`, native, no new dependency) rendering the
    CLI's own `--format text` output, plus the uploaded JSON artifact for
    anyone who wants the full detail. See §8.
13. **How does CI distinguish code failures from evaluation observations?**
    Not by the CLI's raw exit code alone — §1 found that exit `1` already
    conflates a legitimate `REGRESSION` verdict with a per-case
    `AdapterError`, and neither is the same thing as the process never
    completing at all. **Three axes, not one — see §5.1 for the full
    contract:** (a) *did the CLI run to completion and produce a JSON
    result set at all* (job-level execution status — exit `2`, an uncaught
    exception, or no JSON output at all means **no**, and this is
    surfaced distinctly, never silently folded into a green run); (b) *for
    each case that did run, did it produce a verdict or an adapter error*
    (case-level execution status); (c) *for a verdict, which of the five
    existing states does it hold* (the evaluation content itself, always
    non-blocking). This is the specific, concrete mechanism that answers
    §3's "hard boundary" requirement — see §4/§5.1.

## 3. Historical Non-Blocking Precedent

This is not a new pattern for this repository. Document 45 §5/§19 and
Document 46 §2 already establish, for the CLI itself, "no blocking CI gate."
`evaluate_model_judged_support`'s exclusion-until-gate-clears (§1) is the
same discipline applied one layer deeper. This document extends that same
discipline into the CI-wiring layer, rather than introducing a new one.

## 4. Non-Blocking Requirement — Mechanism, Not Just Policy

**Correction (Reviewer 3):** the original version of this section specified
blanket exit-code suppression (`... || true` / `continue-on-error: true`
applied uniformly), on the reasoning that this alone makes the job
non-blocking. That is insufficient and is not this document's design: §1
found the CLI's exit code conflates a legitimate, non-blocking `REGRESSION`
verdict (exit `1`) with process-level failure to even complete (exit `2`, or
an uncaught exception producing no exit code `run_evaluation.py` itself
chose at all). Blanket suppression would make *both* look identical to a
successful, verdict-bearing run — silently converting an infrastructure
failure into an apparently clean evaluation. That is precisely what this
section now forbids.

**Load-bearing rule (frozen, if this document is later ratified), corrected:
evaluation *content* (any of the five verdicts, and any per-case adapter
error) must never fail the CI job or block a merge — but the job must still
distinguish, and visibly surface, whether the CLI executed at all.**
Concretely, the step invoking the CLI is evaluated against exit code and
output presence, not suppressed uniformly:

| Observed outcome | Meaning | CI treatment |
|---|---|---|
| Exit `0`, valid JSON output produced | Every case ran; no `REGRESSION`/error among them | Step succeeds; content reported (§5) |
| Exit `1`, valid JSON output produced | Every case ran; ≥1 has a `REGRESSION` verdict and/or a per-case `AdapterError` | Step succeeds — this is **content**, not job failure (§5) — but each such case is itself surfaced, non-blockingly, in the summary/artifact |
| Exit `2`, or an uncaught exception, or no JSON output produced at all | The run did not complete — dataset-integrity failure, bad CLI invocation, or an unhandled crash | **Step is explicitly flagged as an execution failure** — distinct from any verdict, never silently represented as a successful evaluation run (this task's own required correction) |

This table is the semantic contract; the exact GitHub Actions syntax that
implements it (a post-step check on `${{ steps.<id>.outcome }}` plus
presence of the expected JSON file, or equivalent) is an implementation
detail deferred to §14, not decided here. **What is frozen here is the
distinction itself:** merge-blocking is never triggered by evaluation
*content* (Row 2), and execution failure (Row 3) is never silently absorbed
as success — those are the two halves of Reviewer 3's correction, and
neither reopens whether a future, separately authorized decision may
promote a specific evaluation to a blocking gate (§5's `Gated` class,
untouched, still empty).

No later CI change may reintroduce `had_regression`-driven job failure
without itself being a separately authorized, explicit decision to promote
a named evaluation to a blocking gate — exactly Document 51 §21(i)'s own
boundary and this document's own §6 requirement below, restated as an
implementation-time invariant so it cannot be silently reintroduced by a
future one-line diff. Symmetrically, no later CI change may fold an
execution failure (Row 3) into "success" either — both directions of
silent misrepresentation are equally out of bounds.

## 5. Evaluation Classes

**Reused, not reinvented.** Document 45 §18 already froze a five-state
verdict domain (`PASS`, `WARNING`, `REGRESSION`, `UNCHANGED_FAILURE`,
`INCONCLUSIVE`) that maps directly onto the classes this task's own
framework (§7 of the commissioning task) asks for — inventing a second,
parallel taxonomy would create exactly the kind of "two systems answering
the same question" risk this document exists to avoid:

| This task's requested class | Existing Document 45 mapping | CI treatment |
|---|---|---|
| Deterministic | `numeric_consistency`/`keyword_variant`/etc. contribute to every verdict | Reported, never blocks |
| Statistical / LLM | `model_judged_support` | Reported (disclosed via `judged_by`/`judge_detail`), excluded from status by the gate (§1) — already non-authoritative by construction |
| Diagnostic | Any case/behavior whose result is `INCONCLUSIVE` | Reported as informational, never blocks |
| Advisory | `WARNING`, `REGRESSION`, `UNCHANGED_FAILURE` | Reported prominently (step summary), **never fails the job** — this is the "advisory" tier this document actually implements |
| Gated | *(none exist today)* | **Not created by this document.** Promoting any specific evaluation from advisory to gated requires its own future, explicit, separately-ratified governance decision — this document only ensures the mechanism (§4) exists to make that promotion possible later without redesigning the CI job |

No accidental promotion path exists: nothing in this design reads
`REGRESSION` and fails a step, a job, or a required-status-check. A future
gate would need its own new, explicit CI condition — not a flag flip on
today's job.

### 5.1 Execution Status — an Orthogonal Axis, Not a Sixth Verdict

**The five-state verdict taxonomy above is preserved exactly as Document 45
§18 froze it — nothing is added to it, nothing is removed.** Execution
status is a *separate* axis, one level up, answering a different question
("did the evaluation run?") from the one the verdict answers ("what did it
find?"). Conflating the two — e.g. treating "the CLI crashed" as though it
were a sixth verdict, or silently mapping it onto `INCONCLUSIVE` — is
exactly the ambiguity Reviewer 3's correction removes.

```text
Job-level execution status (new, this section)
  SUCCEEDED  — CLI ran to completion, JSON output present
      → within it, per case:
          Case-level execution status (new, this section)
            RAN        — produced a verdict (one of the five states, §5)
            ERRORED    — produced an AdapterError entry instead (§8.2
                          classifies which kind)
  FAILED     — CLI did not complete (exit 2 / uncaught exception / no
               output) — no verdicts exist to report; surfaced as its own
               distinct condition (§4's table, Row 3), never as a verdict
               and never silently as SUCCEEDED
```

`INCONCLUSIVE` remains exactly what Document 45 §12 already defines: a
*verdict* — the evaluation ran, produced a result, and that result was
inconclusive by the existing regression-comparison rules (e.g. no eligible
baseline, per §8). It is not, and must not become, a stand-in for "the job
failed to execute." Job-level `FAILED` (this subsection) and the verdict
`INCONCLUSIVE` (§5, unchanged) answer different questions and must never be
merged into one signal.

## 6. Preserved Non-Blocking Invariant (restated as acceptance criterion)

> **M10 evaluation must be non-blocking unless a separately ratified
> governance decision later promotes a specific evaluation to a blocking
> gate.**

Satisfied structurally by §4 (exit-code decoupling) and §5 (no `Gated`
class exists yet) — not merely asserted in prose.

## 7. CI Architecture (conceptual flow)

```text
Push to main (same trigger condition as the existing `live` job —
never a PR, fork or same-repo; SD-12's own boundary, applied identically)
        ↓
hermetic job (unchanged, runs as today)
        ↓
evaluation job (new, parallel to `live`, needs `hermetic` — same
`needs:` dependency shape `live` already uses; serialized against
other evaluation-job runs — §8.1)
        ↓
Download the accumulated evaluation-results artifact from the most
recent prior *completed* run of this job on main (via the official
`actions/github-script` action + the REST API — no third-party
marketplace action, no new dependency; §1's existing
`upload-artifact` pattern is the write side of the same idiom) —
merged into, not replacing, `backend/evaluation/results/` (§8)
        ↓
Run `run_evaluation.py --mode fixture --format json`
(exit code AND output presence interpreted per §4's table — content
never blocks; execution failure is surfaced distinctly, never
silently absorbed)
        ↓
Save this run's new results into `evaluation/results/` (existing
mechanism, unmodified — added to, not overwriting, the downloaded
history)
        ↓
Upload the full accumulated `evaluation/results/` as a new workflow
artifact (reuses `actions/upload-artifact@v4`, same as
`backend-coverage`)
        ↓
Write a job summary from the CLI's own `--format text` output,
plus an explicit execution-status line (§4/§5.1) and an explicit
call-out for any `UnsupportedExecutionModeError` case (§8.2)
(`$GITHUB_STEP_SUMMARY`, native GitHub Actions feature, no new tool)
        ↓
Step/job status reflects execution status only (§4) — content
(including REGRESSION and per-case adapter errors) never blocks;
an execution failure (§4 Row 3) is visibly flagged, not hidden
```

**Why main-push-only, not PR-time (a deliberate, evidence-driven choice,
not a default):** §1 established that even FIXTURE mode makes a real LLM
call, giving the evaluation job the exact same secret-exposure profile as
the existing `live` job — which SD-12 and the workflow's own trigger
condition already restrict to `push` to `main` exclusively, never any PR.
Running evaluation at PR time would require either violating that
already-ratified boundary or provisioning a second, lower-privilege secret
scope that does not exist and is not evidenced as needed — out of proportion
per this task's own "smallest coherent" instruction and per Document 44
§4.4's "don't build ahead of evidence" precedent. **Consequence, stated
plainly:** this design gives engineers a post-merge, dashboard/artifact
signal (identical in spirit to how the `live` pytest suite already
surfaces feedback — Document 27/29), not a pre-merge PR comment. A
PR-time-safe variant (e.g. a maintainer-triggered `workflow_dispatch`, or a
separately-provisioned lower-privilege key) is a credible future
enhancement, explicitly not designed here (§11).

## 8. Reproducibility & Baseline Persistence (the load-bearing new mechanism)

This is the one genuinely new piece of plumbing this design requires — §1
identified that `RESULTS_DIR` is git-ignored and CI runners are stateless,
so without this, `find_baseline()` would return "no compatible prior
result" on every single CI run, making `REGRESSION` unreachable in
practice (a silent, misleading gap, not an acceptable one to leave
unaddressed).

**Correction (Reviewer 3):** the original version of this section said only
"download the most recent prior successful run's artifact and use it as the
baseline," which understates who actually decides compatibility and how.
Corrected below.

**Ownership boundary — the CI mechanism does not decide compatibility;
`find_baseline()` already does, unmodified.** The CI-level artifact
retrieval step's only job is to make prior result files present on disk in
`backend/evaluation/results/` before the CLI runs. Which of those files, if
any, is actually usable as a baseline for a given case is decided entirely
by the existing, unmodified `find_baseline()` (`evaluation/regression/
result_store.py`, verified directly this session) using its own frozen
five-field compatibility key — the same one already named in Document 46
§5 and Document 47 §4: **`(case_id, dataset_version, case_version,
evaluation_version, schema_version)`**, plus two further frozen rules
verified directly in `find_baseline()`'s own code: (a) only a result with
`case.mode == "fixture"` is ever eligible — a LIVE-mode result is never a
baseline, matching Document 45 §11.1; (b) if the single most recent
compatible result is itself `INCONCLUSIVE`, it is not eligible and **older
results are not searched** — one inconclusive run breaks the baseline
chain for that case until a new compatible, non-`INCONCLUSIVE` result is
produced (Document 46 §4). **This document invents no new compatibility
dimension and changes none of the above** — it only needs the right files
to be on disk for logic that already exists to run correctly. A prior
result from an incompatible configuration (different dataset/case/
evaluation/schema version, or LIVE mode) is therefore never silently
treated as a baseline: `find_baseline()`'s own filter already excludes it,
exactly as it does for a local developer run today.

**Mechanism, corrected for accumulation:** `_all_results_for_case`
(`result_store.py`, verified directly) globs every `{case_id}__*.json` file
present anywhere in `results_dir` and lets `find_baseline()` sort the
compatible ones by timestamp — i.e. the existing local-usage behavior
already searches *all* historically accumulated results for a case, not
only the single most recent run's own output. For CI to preserve that same
behavior faithfully (rather than silently capping history depth at one
prior run), the evaluation-results artifact must **accumulate** across
runs: each run downloads the full accumulated history via
`actions/github-script`'s REST API (first-party GitHub tooling, no new
dependency), extracts it into `backend/evaluation/results/`, lets the CLI
add *this* run's new result files alongside the existing ones (never
deleting or overwriting a prior file — `save_result`'s own
`{case_id}__{run_id}.json` naming already guarantees distinct filenames per
run), then re-uploads the whole, now-larger directory as the next
artifact. No cache primitive, no external store, no database, no new
service — only `upload-artifact`/`download-artifact`, already present in
this workflow file (§1), used to carry a growing directory forward instead
of a single snapshot.

**Explicit scope limit, reported rather than hidden:** because only
Comparison Explanation has FIXTURE mode today (§1), only its 2 cases can
ever produce a `REGRESSION`-eligible result via this job. Research and
Learning's single case each will run in FIXTURE mode, hit
`UnsupportedExecutionModeError`, and surface as a case-level `ERRORED`
outcome (§5.1) — informative, not broken, and not silently hidden by this
design (the step summary will show it explicitly, per §7/§8.2). This is not
a new gap; it is Document 45 §11.1's already-named, already-deferred
retriever-stand-in gap, now simply visible in a CI-run context rather than
only in a local one.

### 8.1 Concurrent Main-Run Semantics

Multiple pushes to `main` in quick succession could otherwise start
overlapping evaluation-job runs that race on the same accumulated artifact
— two concurrent jobs could each download the same history, run
independently, then race to upload, silently dropping one run's
contribution. **Resolution, using a native GitHub Actions primitive, not
new infrastructure:** a `concurrency:` group on the evaluation job (e.g.
`concurrency: group: evaluation-main, cancel-in-progress: false`) —
already-built-in YAML configuration, not a marketplace action or external
service. `cancel-in-progress: false` is deliberate: a differently-shaped
commit's evaluation run must still complete and contribute its own results,
not be silently discarded because a later push arrived first.

- **Concurrent runs permitted?** No — serialized to exactly one
  evaluation-job run at a time via the `concurrency:` group above.
- **Only completed, successful prior runs qualify as baseline sources?**
  Yes — GitHub's own Artifacts API does not expose an in-progress run's
  artifact for download at all; an artifact only becomes retrievable once
  its uploading job has finished. This is an existing platform guarantee,
  not new design.
- **Can an in-progress run ever be selected as a baseline?** No — for the
  same reason, structurally impossible, not merely policy.
- **Temporal relationship required?** The downloaded artifact must be from
  a run that both started and fully completed strictly before the current
  run's download step executes — guaranteed jointly by serialization
  (no overlap) and the Artifacts API's own completed-only visibility.

### 8.2 Unsupported Execution Mode vs. Unexpected Execution Failure

**Two case-level `ERRORED` outcomes (§5.1) must never be reported
identically, even though today's CLI currently serializes them to the same
untyped string (§1's adapter-error-hierarchy finding).** The semantic
contract this design requires:

- **Intentionally unsupported execution mode** — a case's adapter raises
  `UnsupportedExecutionModeError` (today: any Research or Learning case run
  with `mode="fixture"`). This is a **known, already-documented, permanent-
  until-separately-authorized limitation** (Document 45 §11.1, Document 47
  §7.0) — not a regression, not an infrastructure problem, and not evidence
  anything broke. It must be reported as informational ("not yet
  supported"), visually distinct from both a `REGRESSION` verdict and an
  unexpected-failure flag.
- **Unexpected adapter/execution failure** — any of the other four
  `AdapterError` subclasses (`InvalidBenchmarkInputError`,
  `AdapterInvocationError`, `ProviderExecutionError`,
  `MalformedAIOutputError`, §1). These represent a genuine, unanticipated
  problem worth an engineer's attention, distinct from both an ordinary
  `REGRESSION` and from the known FIXTURE-mode gap above.

**Named dependency, not solved here:** §1 verified that
`run_case`'s `except AdapterError as e: return None, f"...: adapter error —
{e}"` already collapses this type distinction to an untyped string before
it reaches `run_evaluation.py`'s JSON output — the exception *class* that
would make this classification reliable is not currently propagated. This
document does not implement that propagation (no change to
`run_evaluation.py` or `evaluation/adapters/*` is authorized here, §11) —
it names the smallest evidenced gap a future, separately authorized
implementation would need to close (e.g. serializing the exception class
name into the JSON `error` entry) for the CI reporting layer to make this
distinction structurally, rather than by fragile message-text
pattern-matching on today's output.

## 9. Cost / Latency Considerations

- **Dataset size today:** 4 cases (§1) — small and concrete, not an
  estimate.
- **Frequency:** one run per push to `main` (post-merge only, §7) — not
  per-PR, not per-push-to-any-branch. Compare to `live`'s own existing
  frequency, which this job matches exactly.
- **Model tier:** whatever each surface's adapter already calls in FIXTURE
  mode today — no new model, no new provider, no new call path introduced
  by this document.
- **Growth:** cost scales linearly with dataset size, which is
  author-controlled (case files are hand-authored, not auto-generated) —
  the same bound Document 47 §12 already established for
  `model_judged_support` behaviors specifically.
- **No CI-time multiplier:** because the job never blocks (§4/§6), it adds
  zero latency to the developer feedback loop that actually gates merges
  (`hermetic`) — it runs in parallel, post-merge, and its own duration is
  irrelevant to anyone's PR cycle time.

## 10. Observability Considerations

**No Prometheus wiring proposed** — §1 found the existing metrics stack is
pull-based against a live server process, architecturally mismatched to an
ephemeral CI job (nothing to scrape). Instead: the CLI's existing
`--format text`/`--format json` output (§1, already implemented,
unmodified) is surfaced two ways — a GitHub Actions job summary (native,
human-readable, zero new tooling) and the uploaded JSON artifact
(machine-readable, for anyone who wants to script against it later). If
this capability is ever promoted to a blocking gate or a production
signal, *that* promotion is the appropriate trigger to add real
metrics/tracing — consistent with Document 47 §13's own precedent for
exactly this kind of scoping decision, not repeated invention.

## 11. Explicit Non-Goals

- Any blocking CI gate, on any evaluation result, for any surface — not
  authorized now or by any mechanism this design creates (§4/§5/§6).
- PR-time evaluation feedback — explicitly deferred (§7), not designed.
- Research/Learning FIXTURE-mode implementation — remains Document 45
  §11.1's own, separately-deferred gap; not this document's to fix, though
  its absence is now CI-visible (§8).
- Any change to `evaluation/core/*`, `evaluation/regression/*`,
  `evaluation/adapters/*`, `evaluation/golden_dataset/*`, or
  `run_evaluation.py` itself — every one of them is reused exactly as-is.
  This includes the exception-class-propagation gap named in §8.2 — closing
  it is a credible, small, future implementation item, not performed or
  authorized here.
- Any change to `agents/graph.py`, `agents/learning_nodes.py`,
  `agents/comparison_explanation.py`, or any other production pipeline
  file.
- A new secrets-management scheme, a lower-privilege key tier, or a
  `workflow_dispatch`-triggered PR-safe variant — named in §7 as a
  credible future enhancement, not designed or authorized here.
- Wiring `model_judged_support`/the self-consistency gate into this CI
  job's pass/fail semantics in any way — the gate stays at whatever value
  Document 47 §9.1 and Document 50 already established; this document
  does not touch it, reference changing it, or depend on it changing.
- Prometheus/OpenTelemetry instrumentation for evaluation runs (§10).

## 12. Recommended Architecture

**A new, parallel, main-push-only, non-blocking, serialized CI job**
(`evaluation`, alongside `hermetic`/`live`, using `live`'s exact trigger
condition and secret-exposure posture, plus a `concurrency:` group per
§8.1) that: downloads and accumulates the prior evaluation-results artifact
via the official `actions/github-script` REST API idiom (§8), runs the
unmodified `run_evaluation.py --mode fixture --format json` CLI with its
exit code and output presence interpreted per §4's table (content never
blocks; execution failure is surfaced, never absorbed), uploads the
resulting, now-accumulated `evaluation/results/` directory as a new
workflow artifact reusing the existing `upload-artifact` pattern, and
writes a native GitHub Actions job summary from the CLI's own text output
plus an explicit execution-status line and an explicit
unsupported-vs-unexpected classification for any adapter error (§8.2). No
evaluation logic, verdict definition, gate value, prompt, or rubric is
touched. No new dependency, service, database, or observability stack is
introduced.

## 13. Decision Rationale

- **Not "just add it as a step in `hermetic`":** rejected — `hermetic`'s
  own stated design ("no secrets, no live Mongo/LLM/network," §1) would be
  violated by any evaluation mode, including FIXTURE, which needs a live
  LLM key.
- **Not "add it as a PR-time check with a scoped-down key":** rejected as
  disproportionate to current evidence (§7) — no capability gap or
  incident motivates provisioning a new secret tier; the existing
  `live`-job security posture (main-only) already answers the same
  question this job faces, and reusing it is the smaller, more consistent
  diff.
- **Not "block merges on `REGRESSION`":** explicitly rejected by §4/§5/§6,
  and by this document's own commissioning boundary (§6 of the
  commissioning task) — no governance decision anywhere authorizes a
  blocking gate today.
- **Not "invent a new artifact-persistence service (S3/GCS/DB)":**
  rejected — the workflow file already contains a working, in-repo
  precedent (`upload-artifact` for coverage) that solves the identical
  problem shape without any new infrastructure, consistent with
  `CLAUDE.md`'s "keep dependencies lean" and this repo's repeated,
  explicit "don't build ahead of evidence" convention (Document 44 §4.4,
  Document 47 §16).
- **Not "blanket exit-code suppression (`\|\| true` / `continue-on-error`
  applied uniformly)":** rejected on Reviewer 3's own finding (§4) — it
  cannot distinguish "the evaluation ran and found a regression" from "the
  evaluation never ran," silently misrepresenting the latter as success.
  The corrected §4 table achieves non-blocking-for-content without that
  failure mode.
- **Not "let the CI mechanism decide baseline compatibility itself":**
  rejected (§8) — `find_baseline()` already owns this decision correctly;
  reimplementing or second-guessing it in CI YAML would be a second,
  parallel, driftable copy of logic that already exists once, correctly.

## 14. Implementation Boundary

**Not authorized by this document.** If implementation is separately
authorized, the sequence is: (1) add the `evaluation` job to
`backend-ci.yml` with the trigger/concurrency/artifact-accumulation
mechanics in §7-§8.1; (2) implement §4's exit-code/output-presence step
check so an execution failure (Row 3) is visibly distinct from a
successful, content-bearing run (Rows 1-2); (3) verify a first run produces
an `ERRORED`/`UnsupportedExecutionModeError`-classified outcome (§8.2) for
Research/Learning and a real verdict for Comparison Explanation, matching
§8's stated scope limit; (4) verify a second run correctly downloads and
accumulates the first run's artifact and that `find_baseline()` finds a
compatible baseline from it unmodified; (5) verify a deliberately-forced
execution failure (e.g. a malformed dataset file) surfaces as Row 3, not as
a silent success. None of these steps is performed by this document.

## 15. Governance Status

**Architecture:** 🟢 CTO-RATIFIED (§16). Reviewer 3: `PASS`.
**Implementation:** 🔴 NOT AUTHORIZED.

Consistent with this series' own established convention (Document 45 §25,
Document 46 §10, Document 47 §20): this document's approval freezes the
design in §7/§8/§12 as the target architecture. It does not itself authorize
writing the workflow file — that remains a separate, subsequent CTO
decision, exactly as every prior architecture pack in this series required.

## 16. CTO Ratification

Recorded 2026-08-23, under CTO governance authority, following independent
Reviewer 3 review (`PASS — DOCUMENT 52 READY FOR CTO RATIFICATION`).

```text
Document 51:
CTO-RATIFIED

Decision B:
Candidate 1 selected

Document 52:
CTO-RATIFIED (architecture)

Reviewer 3:
PASS

H-1:
CLOSED WITH GOVERNANCE FOLLOW-UP

G7:
NO ARCHITECTURE CHANGE TODAY

G8:
CARRIED FORWARD / BLOCKED

Gate:
0

Implementation:
NOT AUTHORIZED
```

**What ratification does.** Freezes §7/§8/§8.1/§8.2/§12's design — the
existing evaluation harness, unmodified, wired into a new main-push-only,
non-blocking, serialized CI job; cross-run artifact persistence via the
existing `upload-artifact`/`download-artifact` idiom; baseline staging that
defers entirely to the existing, unmodified `find_baseline()`; and
CI-native reporting (job summary + artifact, no Prometheus/OpenTelemetry)
— as the target architecture against which any future implementation is
evaluated. **What it does not do:** authorize any GitHub Actions workflow
change, CI configuration change, evaluation-harness change, artifact-
persistence implementation, baseline implementation, CI-reporting
implementation, backend source change, or deployment change. None of
§4/§5/§5.1/§8/§8.1/§8.2's substantive architecture is reopened, expanded,
or given new infrastructure by this ratification — it is adopted exactly
as revised (Revision 1).

**Frozen scope for any future implementation:** existing evaluation harness
+ GitHub Actions integration + cross-run artifact persistence + baseline
staging (deferring to `find_baseline()`) + CI-native reporting — nothing
beyond what §0–§14 already specify.

M10-CI architecture work stops as of this ratification. A separate,
subsequent CTO decision is required before any implementation begins.
Control returns to the CTO.

---

**NO IMPLEMENTATION PERFORMED. NO WORKFLOW FILE CREATED OR MODIFIED. NO
EVALUATION RUNNER, PROMPT, RUBRIC, OR GATE VALUE CHANGED. NO EXPERIMENT RUN.**
