# Migrated-Parity Hardening Pass — Company Research Sub-Slice 5: AI Insights — Implementation Brief

**Date:** 2026-09-21. **Author:** Docs. **For:** Frontend Engineer (via Docs
Reviewer). **Governing precedent:** [`docs/briefs/hardening_company-research-changes.md`](hardening_company-research-changes.md)
(Sub-Slice 4) and CTO's six-sub-slice breakdown of Company Research. This
brief covers the "AI Insights" tab (`AIInsightsSection.tsx`) — the Copilot
follow-up surface (`CopilotPanel.tsx`) that reruns the full Overview
pipeline (retriever → extractor ‖ tone → synthesizer → fact_checker) seeded
with `context_report_id`, not a lightweight incremental chat completion.
"Explain a concept from this report" is a separate Learning-domain feature
(`web/features/learning`) — out of scope here.

## 1. Goal

Re-verify AI Insights end-to-end against the real running backend and a
real reachable LLM: does a follow-up question genuinely build on the prior
report's content (not just generate a fresh, context-blind brief), and does
the tab's job-state gating handle a terminal-but-not-completed job correctly?

## 2. Result: the happy path works correctly and is genuinely context-aware, confirmed live. But the tab's gating for a job that ends without completing reproduces Financials Sub-Slice 2's Finding B exactly — because that fix was deliberately scoped to one consumer and was never applied here, despite AI Insights sharing the identical anti-pattern.

## 3. Finding A (headline): a cancelled/failed Overview job shows "Research is still running" on AI Insights forever, with no error indication and no Retry — the same defect class as Financials Sub-Slice 2's Finding B, confirmed live, in code never touched by that fix

**Observed live:** started a real Overview job for MSFT
(`d7397a3a-af8e-4e7e-93bf-bb3f8ca4d2d8`) and cancelled it mid-retrieval via
"Stop generating." `GET /api/reports/{id}` correctly returns
`{"status": "cancelled", "id": "...", "events": [...]}` — no `report` key
at all. **Overview's own UI handles this correctly**: "Analysis was
cancelled." with a working Retry button. **The AI Insights tab, for the
identical job id, shows: "Research is still running — AI Insights will be
available once it completes."** — a promise this terminal job will never
keep, with no error indication and no way to retry from this tab. (Tested
via cancellation rather than a deadline-exceeded failure for speed; the code
path is identical for both — see root cause below — so the result
generalizes to a true `failed` status as well.)

**Root cause, precisely isolated:** `AIInsightsSection.tsx` gates on
`useReport(jobId)` alone. `useReport` (`application/useReport.ts`) calls
`fetchCompletedReport`, which does `res.report ?? null` — **discarding the
job's own `status` field** — so a cancelled or failed job's `report: null`
lands in exactly the same branch as a job that's genuinely still running.
This is the identical shape as Financials Sub-Slice 2's Finding B.

**What makes this a real, newly-confirmed gap rather than a duplicate of an
already-fixed issue:** that finding *was* fixed — but narrowly.
`useReport.ts` now also exports `useReportStatus`, a **separate, opt-in**
hook added specifically for this problem, whose own doc comment says so
explicitly: *"a need only one caller (`FinancialsSection`, distinguishing a
failed job from a genuinely still-running one) actually has."*
`AIInsightsSection.tsx` never adopted it — it still only imports `useReport`.
The fix closed the finding for one consumer and left the shared root cause
(`useReport` discarding `status`) live everywhere else that gates on it the
same way.

**Confirmed at the test level too:** `AIInsightsSection.test.tsx` has a test
titled *"shows a non-error message while the Overview run is still in
progress,"* which mocks `status: "running"` — there is no test anywhere in
that file for `status: "failed"` or `status: "cancelled"`. This is the exact
same blind spot that let the original Financials finding ship unnoticed.

## 4. What worked correctly, confirmed live

- **Context actually carries forward, not just architecturally but in the
  model's actual output.** Generated a real MSFT Overview report
  (`9f6f6571-96a0-4d59-aba1-44d1cb1d9fc3`, "Summarize the latest quarterly
  results and key risks"), which surfaced a Q4/multi-year-contract
  seasonality point. Asked a real follow-up on the AI Insights tab
  specifically about that point ("Why is that specifically, and does that
  pattern create any risk?"). The follow-up
  (`ab0c0fcb-afcd-4457-a23a-d86cc250fdfd`) came back as a genuinely
  elaborated, on-topic answer with a dedicated "Seasonality / contract
  timing" risk item — not a generic restatement of the first report. This is
  real evidence `prior_brief` (the capped 1200-char excerpt injected into
  `synthesizer_node`) is doing its job, not just present in the code.
- **The rerun is a genuine full pipeline pass, not an echo**: the follow-up
  cited a source (`10-Q FY24 Q4 (excerpt)`) that report 1 never cited — i.e.
  retrieval genuinely ran fresh rather than reusing report 1's evidence set,
  matching the module's own stated design (full rerun, not incremental
  chat).
- **Cache bypass for follow-ups confirmed**: the follow-up got a brand-new
  `job_id`, distinct from the context report's id — consistent with
  `server.py`'s cache short-circuit being conditioned on
  `not req.context_report_id`.
- **Resilience to a real transient provider error**: mid-run, one LLM call
  returned a genuine `503 Service Unavailable` from the provider; the next
  call succeeded and the job completed normally end to end — the follow-up
  job was not failed by a single transient provider hiccup.
- **The "no research yet" gate** (`!jobId`): correctly shows "Run research
  on the Overview tab first — AI Insights lets you ask follow-up questions
  once you have a research brief for {ticker}," confirmed live.

## 5. Acceptance Criteria

- [x] A real follow-up question live-verified end to end against a real
      reachable LLM, confirmed to genuinely incorporate prior-report context
      (not just architecturally capable of it).
- [x] Cache-bypass and fresh-full-pipeline-rerun behavior for follow-ups
      confirmed live.
- [x] Finding A reproduced live (cancelled job), root-caused to the exact
      shared hook and exact prior fix's scoping decision, corroborated by
      the test suite's own coverage gap.
- [x] The "no job yet" gate confirmed live.
- [ ] Finding A is a small, targeted fix (adopt `useReportStatus` in
      `AIInsightsSection.tsx`, mirroring `FinancialsSection`'s own fix) —
      not applied here.

## 6. Open Questions / Risks

- **Finding A's fix is likely a one-line-of-reasoning change**: since
  `useReportStatus` already exists and already solves exactly this problem
  for `FinancialsSection`, the natural fix is for `AIInsightsSection` to
  check it too (distinguish `failed`/`cancelled` from a still-running job
  and show an honest error + retry) — no new hook needed. Not applied here;
  Docs writes briefs, not patches.
- **Likely not isolated to these two consumers**: `useReport`'s
  `status`-discarding shape is the shared root cause, and it's plausible
  other Company Research surfaces gate on `useReport` the same
  `!report.data`-means-still-running way. Not audited here — worth a quick
  grep (`useReport(` call sites, checking which ones also import
  `useReportStatus`) whenever Frontend next has capacity, similar in spirit
  to the Financials brief's own open question about other `_infer_unit`
  -style bugs.
- **A deadline-exceeded failure wasn't separately reproduced** for AI
  Insights (cancellation was used instead, for speed) — the code path is
  identical (`GET /reports/{id}` returns `report: null` either way), so this
  isn't expected to change the finding, but it wasn't independently
  confirmed with a true `failed` status the way Financials' Finding B was.
- **Sequencing**: per CTO's breakdown, Export is next.
