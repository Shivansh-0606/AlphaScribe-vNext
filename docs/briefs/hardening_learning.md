# Migrated-Parity Hardening Pass — Learning (SCR-08) — Implementation Brief

**Date:** 2026-09-22. **Author:** Docs. **For:** Backend and AI Engineer
(via Docs Reviewer). **Governing precedent:** the six-sub-slice Company
Research hardening pass (`docs/briefs/hardening_company-research-*.md`) and
`docs/briefs/hardening_migrated-parity-pass.md`. This brief is **not** an
Implementation Brief — that was the original assignment, but the premise
turned out to be false (see §0). It is a hardening-pass brief instead,
covering the same ground the six Company Research sub-slices did: live
re-verification of an already-built surface against the real running
backend and a real reachable LLM.

## 0. Premise correction: the Learning backend is not missing

Every piece of documentation touching this feature — the Feature Parity
Tracker's §6 row and freeze note, `LearningScreen.tsx`'s own doc comment
("only the backend behind it doesn't exist yet"), `OverviewSection.tsx`'s
"Explain This" link comment ("the backend capability it calls is a proposed
contract, not live yet"), and `web/features/learning/integration/schemas.ts`'s
header ("NOT YET IMPLEMENTED SERVER-SIDE... every call... will 404") — all
say the backend doesn't exist. **It does, and has since 2026-08-05:**

- `backend/agents/learning_state.py`, `learning_graph.py`, `learning_nodes.py`
  — a complete, compiled 2-node graph (`retriever → explainer`), reusing
  `retriever_node` unchanged and adding a single-call `explainer_node` with
  citation postprocessing and a Law-3 zero-citation reject.
- All four routes live in `backend/server.py`: `POST /learning/explain`
  (line 1622), `POST /learning/{id}/cancel` (1704), `GET /learning/{id}/stream`
  (1735), `GET /learning/{id}` (1743) — full `JobLifecycle`/`EventBus`
  integration (`JobKind.LEARNING`), SSE streaming mirroring the report
  pipeline byte-for-byte, deadline enforcement, `context_report_id` threading
  (`prior_brief`/`prior_financials`), and the same redacted-exception
  discipline every other pipeline in this codebase follows.
- `docs/backend_engineering/03_Learning_Backend_Design.md` (the governing
  design doc, transcribing the frontend's own proposed contract field-for-
  field) and `docs/backend_engineering/15_M2_Phase2_Learning_Implementation_Report.md`
  — **Status: ✅ COMPLETE**, dated 2026-08-05, governed by the frozen
  Backend Architecture v1.0.
- Even already covered by last night's dev-facing-error-leak redaction pass
  — `learning_nodes.py::explainer_node` got the identical `_safe_failure` fix
  applied to every other pipeline node.

This was built and reported complete seven weeks before this pass. Nobody
appears to have live-verified the actual happy path since it landed —
Frontend's own Phase 8 verification (the honest-404 path) predates Phase L
by two days and is now stale. **This brief is that missing live
verification**, not an implementation plan.

## 1. Goal

Live-verify Learning end-to-end against the real running backend and a real
reachable LLM: does asking for a concept explanation actually work, does the
`context_report_id` ("Explain This") entry point actually ground in the
source report, and does the honest-failure path (no filings, cancel) behave
correctly.

## 2. Result: the honest-failure paths and the underlying infrastructure (routes, SSE, job lifecycle, cancel) all work correctly. The actual explanation-grounding mechanism does not — it failed on 4 of 5 real live attempts, including both attempts through the frozen "Explain This" entry point. This is not close to the tracker's own Migrated bar.

## 3. Finding A (headline): the single-call, regex-based citation gate fails to ground a real explanation most of the time — 4 of 5 live attempts, 2 of 2 via `context_report_id`

**Method:** real disposable test account, Managed AI (NVIDIA-hosted, via
`integrate.api.nvidia.com`), ticker NVDA (4 chunks ingested — a real, if
small, corpus; `Retrieved 4/4 chunks` on every run, so retrieval itself was
never the limiting factor).

**Observed live, five real attempts:**

| # | Concept | Context report? | Result |
|---|---|---|---|
| A | "What is operating margin?" (starter chip) | no | **Failed** — "could not be grounded" |
| B | "What was NVIDIA's operating margin, and what does it tell us about the company's profitability?" | no | **Succeeded** |
| C | "What is free cash flow?" (starter chip) | no | **Failed** — "could not be grounded" |
| F | "The report mentioned Blackwell demand is ahead of supply. What does that mean for NVIDIA's revenue, and why would a company want demand to exceed supply?" | yes | **Failed** — "could not be grounded" |
| G | "What is NVIDIA's Data Center segment revenue and why is it growing so fast?" | yes | **Failed** — "could not be grounded" |

Every failure surfaced the same message: *"Pipeline failed: The explanation
could not be grounded in the retrieved filings."* Every failed run's server
log shows **exactly one** LLM call, `200 OK` — this is not a provider error
or a truncation crash (the class Filings/Changes found elsewhere in this
project). The LLM call succeeded; the *response* didn't satisfy the
citation gate.

**Root cause, as far as it's observable from outside the LLM call:**
`explainer_node` (`agents/learning_nodes.py`) uses free-form `chat_text`
(not the schema-validated `chat_json` every structured-extraction node in
this codebase uses), instructs citation via prose ("Cite inline as [1],
[2], ..."), then runs a regex post-processor
(`_postprocess_citations`) that strips any `[n]` marker outside
`[1, num_docs]` and computes the cited-index list. If that list comes back
empty — the model's prose contained zero valid markers — `cited_sources`
comes back empty and `_run_explanation` fails the job outright: *"Law 3: an
explanation with zero grounded citations must not be persisted... the route
layer treats an empty explanation + empty cited_sources as a failed job, not
a success with no sources"* (the module's own docstring). This is a
deliberate design choice, not a bug in the gate itself — but its real-world
trigger rate, live-tested here for the first time, is high: 80% in this
sample, and 100% specifically through the one entry point (`context_report_id`)
the frozen product spec names as a first-class path into this feature.

**What could not be confirmed from outside the system:** whether the model's
raw response actually omitted `[n]` markers entirely, or used a
different-looking citation convention the regex doesn't recognize, or cited
out-of-range indices. Nothing in this pipeline logs or traces the raw
pre-postprocessing model output anywhere — `explainer_node`'s failure trace
event is the same generic `_safe_failure("Explanation", e)` string used for
a genuine LLM exception, with no distinction for "the call succeeded but
grounding failed." Diagnosing the actual mechanism needs that visibility,
which doesn't exist today.

**No retry exists, by explicit design** (`learning_nodes.py`'s own module
docstring: "one call, no retry loop, since the contract has no
verification-stage vocabulary") — this mirrors Filing Q&A's Document-87-
style single-generation discipline. Unlike Filing Analysis's per-output
degrade-to-`insufficient_evidence` containment, Learning has no equivalent
partial-credit path: a citation-gate miss fails the *entire* explanation,
even when — as observed in the failed runs here — the underlying facts
were almost certainly present in the 4-chunk corpus (the same corpus a
follow-up specific question, run B, successfully cited).

## 4. Finding B (minor): no Retry action on a failed or cancelled explanation, unlike every sibling AI surface

**Observed via code and confirmed visually:** `LearningScreen.tsx`'s failed/
cancelled banner (`{(job.stage === "failed" || job.stage === "cancelled") &&
<Banner tone={...}>{...}</Banner>}`) has no `action` prop — no Retry button.
Every other AI surface in this codebase that can fail (Overview, Financials,
Filings, Changes, AI Insights) gives the user a one-click Retry. Here, the
user has to manually retype the same concept into the composer, which is
still visible and usable below the banner — not a dead end, just an
inconsistent, slightly rougher recovery path than the rest of the product,
and one that matters more than it otherwise would given how often Finding A
triggers it.

## 5. What worked correctly, confirmed live

- **A real, successful explanation** (run B): correct Markdown rendering,
  real citations `[1]`–`[4]` into `10-Q FY25 Q1 (excerpt)` sources, a real
  natural-language follow-up-question suggestion (matching the system
  prompt's own instruction), Sources list correctly populated via
  `LearningExplanation`/`SourceReference` — the identical rendering
  convention `AIResponseCard`/`ChangeBriefResult` use elsewhere.
- **The no-context empty state** (`/learning` with no ticker): correct
  "choose an example company" prompt, ticker form submits to
  `/learning?ticker=`.
- **The no-filings honest-failure path**: a genuinely un-ingested ticker
  (COST) correctly surfaced the real backend `400`
  ("No filings ingested for COST...") as a `Banner`, no crash.
- **Cancel, backend-confirmed not just optimistic**: "Stop generating"
  correctly showed the optimistic "Cancelled." banner *and* fired a real
  `POST /learning/{id}/cancel → 200 OK`, confirmed in the network log.
- **The `context_report_id` mechanism threads correctly, mechanically**:
  the "Explain This" link (`/learning?ticker=NVDA&job=<reportId>`) correctly
  carries through to the explain request — confirmed by the fact that runs
  F/G's failure message and job lifecycle were identical in shape to the
  non-context runs, i.e. the context-fetch/injection code path itself
  didn't error or behave differently; the *grounding* failure is downstream
  of that, in the shared `explainer_node`/citation-gate logic.
- **Resilience infrastructure reused correctly from the report pipeline**:
  the context-report source (a real NVDA Overview report, job
  `bb355bde-976e-483f-8866-8db9c1c64985`) itself completed successfully
  despite a real transient LLM `503` mid-run, recovered via the same
  fact-check retry router Overview's own hardening slice first witnessed —
  confirming that shared infrastructure continues to work correctly when
  Learning depends on it.

## 6. Acceptance Criteria

- [x] Premise corrected: Learning's backend exists and is live, not missing
      (§0).
- [x] A real explanation request live-verified end to end against a real
      reachable LLM, with real grounded citations, when the citation gate
      passes.
- [x] The `context_report_id` / "Explain This" entry point live-verified
      mechanically (correct request threading) — and found to fail
      grounding on both live attempts.
- [x] Cancel live-verified backend-confirmed, not just client-optimistic.
- [x] The no-filings and no-context honest-failure paths live-verified.
- [x] Finding A reproduced 4/5 overall, 2/2 via the frozen entry point —
      root-caused to the citation-gate mechanism as far as observable from
      outside the LLM call; the exact trigger inside the model's raw output
      could not be confirmed given no visibility into pre-postprocessing text.
- [ ] Findings A and B are not applied here — Docs writes briefs, not
      patches.

## 7. Tracker correction (§6, `web/features/learning/`)

Per explicit direction: correct to reality, not assumed. **Stays In
Progress — not promoted to Migrated.** The reason has flipped, not
disappeared: previously In Progress because the backend didn't exist; now
In Progress because the backend exists, is correctly wired end-to-end, and
demonstrably does not reliably do the one thing the feature exists to do.
The tracker's own bar ("full functional parity... verified working
end-to-end") is not met at an 80% observed live failure rate, let alone a
100% failure rate on the entry point the frozen spec names first. This
correction, plus the stale "doesn't exist" language in the tracker, the two
frontend doc comments named in §0, and the schema header comment, are not
applied in this brief — flagged for whoever owns each file.

## 8. Open Questions / Risks

- **Fix direction, not decided here.** Candidates, none chosen: (a) add
  visibility into the raw pre-postprocessing model output (even just in the
  trace/log) so the actual failure mechanism can be diagnosed — currently
  the biggest blocker to fixing this correctly rather than guessing; (b) a
  stronger prompt (few-shot citation examples, or restructuring the
  instruction) if raw-output inspection shows the model simply isn't
  complying with the bracket format; (c) move `explainer_node` to
  `chat_json` with a structured schema carrying citation indices explicitly,
  the same discipline every extraction node in the report pipeline already
  uses, instead of a free-form-text-plus-regex gate; (d) a bounded, contained
  retry specifically for a citation-gate miss (distinct from a real LLM
  failure) — this would need its own scoping decision the way Filing
  Analysis/Q&A's retry question did, since Learning's docstring currently
  states no-retry is deliberate, not an oversight.
- **Sample size**: 5 live runs, one ticker (NVDA, a small 4-chunk corpus).
  Not exhaustive — worth confirming whether the failure rate holds on a
  larger corpus or a different ticker before treating 80% as a precise
  number; the *existence* and *severity* of the problem is well-evidenced
  regardless.
- **Every stale "doesn't exist yet" claim found in §0** should be corrected
  wherever it lives (tracker, two frontend comments, schema header) — not
  done here, flagged for the relevant owners.
- **Sequencing**: unlike Company Research's six sub-slices, this wasn't part
  of a planned sequence — it fell out of catching a stale premise. No
  further Learning work is scoped by this brief beyond Finding A's fix,
  which needs a design decision first.
