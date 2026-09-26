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
- [x] **Post-fix (§9):** Finding A's fix (commit `6d65aec`) live re-verified
      against the real backend — 2 of 2 previously-failing no-context cases
      now succeed cleanly, same inputs, real citations. The
      `context_report_id` path was not independently re-run to completion
      this round (unrelated environment instability, not a fix issue — see
      §9) but shares the identical, already-confirmed root cause and the
      identical unconditional fix code path.
- [ ] **Direct `context_report_id` confirmation (§10, 2026-09-24): FAILED,
      2 of 2.** The §9 inference did not hold — a new, context-path-specific
      root cause (Finding C) not covered by `6d65aec`. Not promotable.
- [x] **Direct `context_report_id` confirmation, post-Finding-C-fix (§11,
      2026-09-26): PASSED 4 of 4** — including 2 of 2 against an Overview
      report whose injected brief carried the exact `【n†Lx-Ly】` trigger.
      Direct live evidence, not inference.
- [x] **Cross-tenant fix (`94b01ba`) live-verified (§11):** a second account
      passing the first account's report id gets no injected context,
      confirmed by a canary test against a positive control.

## 7. Tracker correction (§6, `web/features/learning/`)

**As of this brief's original pass (2026-09-22):** correct to reality, not
assumed. Stays In Progress — not promoted to Migrated. The reason had
flipped, not disappeared: previously In Progress because the backend didn't
exist; now In Progress because the backend exists, is correctly wired
end-to-end, and demonstrably did not reliably do the one thing the feature
exists to do. The tracker's own bar ("full functional parity... verified
working end-to-end") was not met at an 80% observed live failure rate, let
alone a 100% failure rate on the entry point the frozen spec names first.

**Updated by §9 (2026-09-23/24), status unchanged — still In Progress:**
Finding A's fix landed and was live re-verified clean on the previously-
failing no-context cases; the `context_report_id` path's confirmation is
still pending (see §9). Per CTO-2's explicit call, the row stays In
Progress until that specific path is directly confirmed, not promoted on
inference alone.

**Updated by §10 (2026-09-24), status unchanged — still In Progress:** the
direct `context_report_id` confirmation was run and failed 2 of 2 on a new
root cause (Finding C). The hold was the right call; the row stays In
Progress pending Finding C's fix and a fresh direct re-run of the same path.

**Updated by §11 (2026-09-26) — promoted to Migrated (CTO-2 sign-off).**
Finding C's fix (`d937e68`) and the cross-tenant fix (`94b01ba`) are both
live-verified by direct evidence on the exact path that failed. CTO-2
signed off; the tracker row is now Migrated.

This correction, plus the stale "doesn't exist" language
in the tracker, the two frontend doc comments named in §0, and the schema
header comment, are not applied in this brief — flagged for whoever owns
each file.

## 8. Open Questions / Risks

- **⚠ SECURITY — cross-tenant read via `context_report_id` (found 2026-09-24,
  routed by CTO-2 to Backend and AI Engineer as its own urgent item).
  ✅ Resolved: fixed in `94b01ba` (owner-or-sample predicate on both
  lookups), live-verified 2026-09-26 (§11).**
  `explain_concept` (`backend/server.py`, the `if req.context_report_id:`
  block in `POST /learning/explain`) loads the context report with
  `db.reports.find_one({"id": req.context_report_id}, ...)` — **no owner
  predicate**. It then injects that report's `draft_report` (first 1,200
  chars) and `extracted_data` into the explainer prompt
  (`learning_nodes.py::_build_user_message`), and appends its `query` to the
  retrieval query. Any
  authenticated user who supplies another tenant's report id gets that
  report's brief fed to the LLM, and the resulting explanation (which the
  caller reads) can restate it — a cross-tenant data disclosure. This is
  inconsistent with EQ-3's read-scoping cutover: `GET /reports/{id}` scopes
  every tier to `{"user_id": user["id"]}` or `{"is_sample": True}` and makes
  a foreign id indistinguishable from a nonexistent one. **The same
  unscoped lookup also exists in `POST /reports/generate`'s follow-up path**
  (the `if req.context_report_id:` block that loads `prior_brief`), so the
  gap is not Learning-only. The context report's ticker is also not checked
  against the request's ticker in either route. **Evidence basis: code
  reading only** — this pass did not attempt a live cross-tenant
  exploitation (that would need two accounts and is the fixing engineer's
  call to reproduce). Obvious shape of a fix: apply `get_report`'s
  owner-or-sample predicate to both lookups and treat a non-match exactly
  like a missing report. Recorded here for the paper trail regardless of
  who fixes it first.
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

## 9. Post-fix live re-verification (2026-09-23/24)

> **Superseded in part by §10:** the pending direct `context_report_id`
> confirmation below was run on 2026-09-24 and **failed 2 of 2** on a new
> root cause (Finding C). The shared-code-path inference in this section
> did not hold. It is kept as written, for the record.

Finding A's fix landed as commit `6d65aec` (`_normalize_citation_markers()`
— NFKC normalization plus an explicit CJK lenticular-bracket map, run before
the citation gate). Per explicit direction: re-run the same failing cases
against the real backend and confirm the failure rate actually drops in
practice, not just that the new unit tests pass — and only update this
brief/the tracker row if the live evidence actually supports it.

**Confirmed clean, live, same inputs that failed before the fix:** re-ran
both previously-failing no-context starter-concept cases from §3's table
(rows A and C — "What is operating margin?" and "What is free cash flow?",
NVDA, no `context_report_id`) against the real backend and a real reachable
LLM, post-fix. **2 of 2 now succeed cleanly** — real grounded citations
(`[1]`), correct figures matching the source filing, a real follow-up
question suggestion, no gate rejection. Byte-for-byte the same concept
strings that reliably failed pre-fix (confirmed in §3's table and in the
6d65aec raw-log capture for row A specifically).

**The `context_report_id` path has not yet been independently re-run live
to completion post-fix** — not because of a fix problem, but because of
unrelated environment instability the same night: the LLM provider was
unusually flaky (multiple real `503`s, one real fact-check output-truncation
failure), and the Overview report needed to generate a fresh
`context_report_id` twice hit its own real 300-second job deadline before
completing (`agents/graph.py`'s existing, already-documented deadline
enforcement — working exactly as designed, the same mechanism the
Financials/Filings briefs already exercised, not a Learning-specific or
fix-related regression). Rather than force a result out of a visibly
unstable shared LLM provider, this round stopped short of that third
confirmation — it remains outstanding, not abandoned, and is cheap to close
once the provider settles.

**Why the inference is sound, even though it doesn't substitute for that
confirmation:** the fix is not path-conditional. `_normalize_citation_markers()`
runs unconditionally on every `explainer_node` output, before the citation
gate, regardless of whether `prior_brief`/`prior_financials` were injected —
there is no branch in the code that treats a context-seeded call
differently. Finding A's own original diagnosis (§3) already directly
confirmed, via raw log capture, that the *pre-fix* failure mechanism was
byte-for-byte identical on both paths (both cited using 【n】, both
zero-ASCII-marker rejections). A fix applied to the one shared code path
both diagnoses ran through does not have a plausible mechanism to fix one
call site and not the other. **This is a documented inference, not a
substitute for direct evidence on the specific path that had a 100%
pre-fix failure rate and is the frozen primary entry point** — that path's
own track record here earns it a direct confirmation before being called
Migrated, not just general caution extended from a sibling path.

**Recommendation (CTO-2's call, 2026-09-24): stays In Progress, not
promoted yet.** The 2-of-2 no-context confirmation and the shared-code-path
inference are real, meaningful progress — but `context_report_id` is the
one path that had a *100%* pre-fix failure rate and is the frozen primary
entry point (`OverviewSection`'s "Explain This"), and that specific track
record earns a direct confirmation rather than an inference extended from
its sibling path, however sound that inference is. This is not a structural
blocker — it's one pending live run, not yet done, cheap to close once the
shared LLM provider stops being flaky. No further design or code work is
implied; this is purely "run the same case a third time and confirm," the
same bar every other live-verification in this hardening pass has held
itself to before a row gets called Migrated.

## 10. Finding C: direct `context_report_id` confirmation FAILED — a new, context-path-specific root cause (2026-09-24)

> **Resolved by §11:** Finding C was fixed in `d937e68` and live-verified
> on 2026-09-26 against the exact dagger-style trigger (2/2 pass).

**Result: 2 of 2 failed through the frozen "Explain This" entry point. The
same question with no context succeeded (1 of 1).** This is the direct
confirmation §9 said was owed. It came back negative, so §9's
shared-code-path inference is falsified for this path.

**Method:** a fresh disposable account on the real running stack (Managed AI,
NVIDIA-hosted). A fresh NVDA Overview report (`no_cache`, job
`f275ed54-af57-48c8-bdee-35014f4cc373`) completed in ~2.5 minutes with
`fact_check_status: true`. There were no provider `503`s and no deadline hit
this time, so provider flakiness is excluded. Learning was then run with
§3 row G's question verbatim, "What is NVIDIA's Data Center segment revenue
and why is it growing so fast?", ticker NVDA. The account was deleted
afterwards (`DELETE /auth/me → 200`, then `/auth/me → 401`).

| Run | `context_report_id` | Result |
|---|---|---|
| C1 (`343cce7c…`) | `f275ed54…` | **Failed** — "could not be grounded in the retrieved filings" |
| C2 (`43121d04…`) | `f275ed54…` | **Failed** — same |
| C3 (`655ccbbc…`) | none (control) | **Succeeded** — 4 of 4 sources cited, $22.6B / +427% YoY, correct |

Each run retrieved `4/4 chunks` and made exactly one LLM call, which
succeeded. The failure is the citation gate again, not the provider.

**Root cause (directly observed, not inferred):** `6d65aec`'s gate-miss
logging captured both failed runs' raw model output. In both, the
explanation is **correctly grounded**: the figures are right, and every
claim carries a citation to one of the 4 retrieved sources. The model wrote
those citations in the form **`【2†L1-L4】`** (source index plus a `†L…`
line-range suffix), and once in a malformed form, `【1†L1-L4}`.

It copied this convention from the prompt. On this path,
`_build_user_message` injects the context report's `draft_report` (first
1,200 characters) under a "What this company's latest brief found" heading.
The Overview synthesizer's own persisted output uses exactly this style:
report `f275ed54…`'s `draft_report` contains 17 such markers
(`【1†L1-L4】`, `【3†L5-L6】`, ...). The no-context control never sees that
text, and it cites in plain `[n]`.

`6d65aec`'s fix maps the brackets, but the suffix still breaks the gate.
`_normalize_citation_markers()` maps `【】` to `[]`, turning `【2†L1-L4】` into
`[2†L1-L4]`. `_CITATION_RE = \[(\d+)\]` requires `]` immediately after the
digits, so it matches zero markers. The result is 0 of 4 cited, a Law-3
reject, and a failed job. The fix is not wrong for what it covers, and it
does run unconditionally on this path. The model's *input* differs by path,
though, and so does the citation form it produces. §9 reasoned only about
the code path, and that is the gap this finding exposes.

**A second, latent hazard on the same path:** the `【n†…】` markers inside
the injected brief refer to *the Overview report's* source numbering, not
to the Learning retrieval's 4 documents. Even with a more tolerant gate, a
model echoing the brief's markers could produce in-range indices that point
at the wrong Learning source. The gate would count these as grounded when
they are mis-grounded.

**Fix direction (not decided here; for Backend and AI Engineer via CTO-2):**
- (a) Widen the normalization or gate to accept an optional
  `†…` suffix, and a tolerant close, inside a numeric citation. Rewrite each
  match to canonical `[n]` before `_postprocess_citations`, so the
  persisted/rendered text uses the one convention every other surface
  expects.
- (b) Strip citation markers from `prior_brief` before injecting it into the
  explainer prompt. This removes the style the model copies and closes the
  index-collision hazard above.

(b) addresses the cause and (a) is defense in depth; doing both is likely
right. Any fix needs a unit test built from the logged C1/C2 raw outputs,
plus a fresh direct live re-run of this path. An inference will not do.

**Side observation, out of scope for this brief:** the Overview synthesizer
itself persists `【n†Lx-Ly】` markers in `draft_report`. Whether Company
Research's Overview renders these correctly as citations has not been
checked in this pass. It is flagged for whoever owns that surface.

**Recommendation: stays In Progress, not promoted.** This is a real,
reproducible defect on the frozen primary entry point, and its failure rate
(2/2 here, 2/2 pre-`6d65aec` in §3) is unchanged. The no-context path stays
confirmed clean (§9, plus control run C3 here). CTO-2's decision to require
direct confirmation instead of promoting on inference is what caught this.

## 11. Post-Finding-C live re-verification — `context_report_id` path PASSES, cross-tenant fix confirmed (2026-09-26)

Both fixes routed out of §8/§10 landed and were reviewed PASS:
- `94b01ba` applies the owner-or-sample predicate to both `context_report_id`
  lookups.
- `d937e68` (Finding C) does two things. It normalizes dagger-suffixed
  citation markers in the model's output, and it strips citation markers
  from the injected `prior_brief`.

This section is the direct live evidence CTO-2 required before promotion.
It is not an inference.

**Method:** the real running stack with Managed AI (NVIDIA-hosted). Two
fresh disposable accounts, A and B. Account A generated two fresh NVDA
Overview reports (`no_cache`), and both completed with
`fact_check_status: true`. Every Learning run used
§3 row G's question verbatim unless noted. Both accounts were deleted
afterwards (`DELETE /auth/me → 200`, then `/auth/me → 401`, for each).

**The Overview synthesizer's citation style is nondeterministic, so the
trigger input was confirmed deliberately.** Report 1
(`89814216-ba0d-4e4b-93d3-7693bf5b75dd`) cited in plain `[n]`, with zero
`†` markers, so it exercises the context path but not Finding C's actual
trigger. Report 2 (`2bd3c690-fc4c-4077-8047-b265077cdf3c`) cited in the
`【n†Lx-Ly】` style: 14 markers, 8 inside the 1,200 characters that
`_build_user_message` injects. That is the exact input that produced
§10's 2/2 failure. Both reports were tested.

| Run | Account | `context_report_id` | Result |
|---|---|---|---|
| R1, R2 | A | report 2 (**dagger-style**, the Finding C trigger) | **Succeeded 2/2**: `[1]`–`[4]` cited, 4 sources, no `†` in output |
| R3, R4 | A | report 1 (plain `[n]` style) | **Succeeded 2/2**: `[1]`–`[4]` cited, 4 sources |
| R5 | A | none (control) | **Succeeded**: `[1]`–`[4]` cited, 4 sources |
| R6 | A | report 1 (own), canary prompt | Positive control: the model **listed the brief's `###` headings verbatim** ("Snapshot", "Financial Highlights"), so the context *was* injected |
| R7 | **B** | report 1 (**A's**), same canary prompt | **"NO CONTEXT BRIEF"**, so A's report was *not* injected into B's job |

Every run produced a figure-correct, cited explanation ($22.6B, +427% YoY),
and the backend log contains **zero** citation-gate-miss warnings for the
whole session.

**How the cross-tenant check works:** the fixed route ignores a foreign id
silently, exactly as it treats a nonexistent one. That matches EQ-3's
"indistinguishable from nonexistent" invariant, but it means there is no
error response to observe. The check is behavioral instead. The canary
prompt asks the model to quote the `###` headings of any context brief in
its input, or to say "NO CONTEXT BRIEF". The retrieved filing excerpts
don't carry those headings, so only an injected Overview brief can supply
them. The same prompt yields the headings for A's own report (R6) and
"NO CONTEXT BRIEF" for B passing A's id (R7). That is a controlled, direct
demonstration that `94b01ba` closes the gap on `POST /learning/explain`.
`POST /reports/generate`'s follow-up path received the identical predicate.
It was not separately live-probed here: a full report run is a
harder-to-observe signal. It is covered by `94b01ba`'s hermetic regression
tests and Backend Reviewer's sweep of every `db.reports` lookup in
`server.py`.

**Residual gap (minor, non-blocking; for Backend and AI Engineer):**
both of `d937e68`'s new patterns (`_SUFFIXED_CITATION_RE` and
`_ANY_CITATION_MARKER_RE`) require the range form `†Lx-Ly`. A single-line
marker such as `【3†L7】`, which appeared in §10's Overview draft, matches
neither: it is not stripped from `prior_brief` and not normalized in the
output. Checked directly against the committed regexes. If the model copies
that form, a citation in that exact form is still rejected. Neither brief
tested here contained a single-line marker, so this was not triggered live.
The fix is small: make `-L\d+` optional in both patterns (`L\d+(?:-L\d+)?`).
It is flagged, not blocking. §10's failures, and every dagger marker
observed across all reports in this pass, used the range form, which is
now covered.

**Recommendation: promote Learning (SCR-08) to Migrated.**
- Every path the brief set out to verify has now been verified live by
  direct evidence: no-context (§9, plus R5), the frozen "Explain This"
  `context_report_id` entry point against its actual failure trigger (R1/R2)
  and a plain brief (R3/R4), cancel, and the no-filings and no-context
  honest-failure paths (§5).
- The security issue this pass surfaced is fixed and live-confirmed.
- What remains is non-blocking: Finding B (no Retry button on
  failed/cancelled, §4), the single-line-marker residual above, and the
  stale doc comments flagged in §0/§7.
- **CTO-2 signed off (2026-09-26): promoted to Migrated.** The
  single-line-marker residual is routed to Backend and AI Engineer as a
  separate non-blocking follow-up.
