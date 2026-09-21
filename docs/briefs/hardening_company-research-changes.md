# Migrated-Parity Hardening Pass — Company Research Sub-Slice 4: Changes (M15) — Implementation Brief

**Date:** 2026-09-20. **Author:** Docs. **For:** Backend/Frontend Engineer
(via Docs Reviewer). **Governing precedent:** [`docs/briefs/hardening_company-research-filings.md`](hardening_company-research-filings.md)
(Sub-Slice 3) and CTO's six-sub-slice breakdown of Company Research. This
brief covers the Compare Reports / Compare Financial Periods switch
(`ChangeBriefSection.tsx`, `ChangeBriefResult.tsx`) and its two backend
engines: `agents/change_brief_narrative.py` (`report` mode — one bounded
`chat_json` call) and `agents/change_brief_financial.py` (`period` mode —
pure, deterministic, LLM-free).

## 1. Goal

Re-verify Changes' report/period comparison end-to-end against the real
running backend and a real reachable LLM — specifically resolving the open
question the Filings sub-slice pass left unanswered: does report mode's much
smaller, bounded 2-report evidence payload actually avoid the same
output-truncation crash class (Filings brief Finding A) found in Filing
Analysis/Q&A, or is that only a theoretical mitigation?

## 2. Result: report-mode's truncation ceiling was not reached on a real, substantive test case. Period mode's own engine is correct, but live-verifying it surfaced a still-open residual of Sub-Slice 2's Finding A: that fix landed only hours before this pass and was never backfilled, so every previously-acquired ticker's stored data — starting with the exact MSFT dataset that first proved that finding — still exhibits it today.

Two independent things were live-verified: report mode's crash-ceiling
question (resolved, see Finding A below) and period mode's own correctness
(confirmed correct — see §5), which in the process re-surfaced a defect
this project had already recorded as fixed (Finding B).

## 3. Finding A (headline, resolves the inherited open question): report-mode's bounded evidence payload did not reach the truncation ceiling in a real, substantive test

**Method:** two real MSFT Overview reports were generated fresh against the
shared dev stack and a real reachable LLM (NVIDIA-hosted, via
`integrate.api.nvidia.com`), deliberately chosen to be substantive rather
than minimal — one summarizing quarterly results and key risks (job
`42c670b4-e1cc-4558-81b1-e9c6f51b7bee`), one on AI-investment/cloud-growth
outlook (job `6abd64ac-a5a2-4de3-9b1b-0884cff5efbd`) — so that comparing them
would have real, substantive material to generate change items from (a
revenue-guidance shift from none to a full multi-segment guide, a sentiment
flip from Neutral to Bullish), not a thin, easy-to-pass case.

**Observed live:** report-mode Compare (`agents/change_brief_narrative.py`
via job `82d9f435-0f7b-4d30-8f70-6e962b1ae992`) completed cleanly in 40.98s
wall time, with **exactly one** `chat_json` call — confirmed via the
server's own request log, one `POST .../chat/completions` between the job's
start and its `sse stream change_brief ended: ... outcome=completed` line, no
retry, no second completion. It produced 6 discrete, well-formed,
both-sides-grounded change items (revenue guidance introduced, sentiment
Neutral→Bullish, Azure/Intelligent Cloud/Productivity-and-Business-Processes
segment guidance, More Personal Computing revenue range), each correctly
citing one baseline-report source and one current-report source, state
`complete`, zero `coverage_boundaries`, zero dropped candidates.

**What this confirms:** the module's own docstring claim — that bounding the
payload to 2 reports' already-extracted `extracted_data`/
`sentiment_analysis`/`scorecard` (never the full `draft_report`) keeps the
single generation call comfortably inside `DEFAULT_LIGHT_MODEL`'s output
budget — held up on a real case built specifically to be a non-trivial
comparison, not a best-case minimal one. This is the concrete live data
point the outgoing session was about to gather before handoff. It is **not**
an exhaustive guarantee (no adversarial worst-case attempt was made to
maximize item count/explanation length — see §7), but it is real evidence
against the ceiling being reachable in ordinary use, where the Filings
brief's Finding A had none in report mode's favor beyond architectural
reasoning.

## 4. Finding B (headline, higher severity, newly surfaced): Sub-Slice 2's Finding A (unit-misclassification) fix is not retroactive — every ticker acquired before today's fix, including the exact MSFT dataset used as its original proof, still shows it live right now

**Observed live:** while verifying Changes' period mode (MSFT, Income
Statement, FY2023 vs FY2026), 4 of the 47 computed change items rendered as
raw, unformatted 12-digit floats instead of currency — e.g. **Net Income
From Continuing Operation Net Minority Interest**: `72361000000.00 →
133749000000.00` sitting next to correctly-formatted rows like **Net
Income**: `$72.36B → $133.75B` for the *same underlying figure*. This is the
exact malformation Sub-Slice 2's Finding A described.

**Root cause confirmed, and confirmed already fixed in code:**
`agents/financials_provider.py`'s `_infer_unit()` now uses the word-boundary
regex from commit `cdc2914` ("fix(financials): match \"ratio\" as whole
word, not substring", **2026-09-20 13:44:27** — landed the same day as this
pass, hours before it). Running that exact function against all 4 affected
labels confirms it now correctly classifies every one of them as `currency`:

```
Net Income Continuous Operations -> CURRENCY
Net Income From Continuing And Discontinued Operation -> CURRENCY
Net Income From Continuing Operation Net Minority Interest -> CURRENCY
Selling General And Administration -> CURRENCY
```

**But the live, stored data was never recomputed.** A direct read of `GET
/api/companies/MSFT/financials` shows the persisted document still carries
the pre-fix classification:
`{"provider_label":"Net Income From Continuing Operation Net Minority
Interest","value":133749000000,"unit":"ratio"}`, with
`"fetched_at":"2026-08-15T10:30:53"` — over five weeks before the fix
landed. **This is the identical MSFT dataset** (same `fetched_at`
timestamp) that Sub-Slice 2's own Finding A cited as its *first* piece of
evidence ("MSFT — data acquired 2026-08-15"). It was never re-acquired after
the fix, so it never picked the fix up.

**Confirmed not Change-Brief-specific:** navigating to the Financials tab
directly for MSFT shows the identical raw-float rendering, in the identical
4 line items, across all 4 stored annual periods, plus a 5th instance in the
Cash Flow Statement (`Net Income From Continuing Operations`) — the same
"~6 recurring line items" pattern the original Finding A described.

**Mechanism:** `_infer_unit()` runs once, at acquisition time, and its
result is written permanently into the persisted
`FinancialStatement.metrics[].unit`. Nothing re-derives `unit` for an
already-stored document — not the fix itself, not a migration, not a
scheduled job. There is no `ponytail:` marker documenting "already-acquired
tickers keep their stale unit until re-acquired" as a known, deliberate
ceiling; this appears to be an unrecognized gap in what "fixed" meant for
the original finding, not an accepted trade-off.

**Consequence for this sub-slice specifically:** `change_brief_financial.py`
reuses the stored `Metric.unit` verbatim, by design (it is intentionally
dependency-free and never recomputes anything — see its own module
docstring), and `ChangeBriefResult.tsx` reuses `StatementTable`'s
`formatMetricValue` verbatim, also by design. Both are working exactly as
specified; they faithfully **inherit** this defect rather than causing it.
The underlying delta math is unaffected — both sides of each affected metric
share the same stale `unit`, so no false unit-mismatch exclusion is
triggered, and the raw stored numeric value itself is correct — this is a
presentation-only defect, the same severity class as the original Finding A,
now confirmed to reach a second UI surface.

## 5. What worked correctly, confirmed live

- **Report mode**, beyond Finding A's headline result: the account/job
  lifecycle needed to set it up — generating two fresh Overview reports for
  the same ticker (navigating to `/research?ticker=MSFT` without a `?job=`
  param correctly resets the Overview composer to accept a new question even
  after a prior job completed) — worked correctly, and the Changes tab's
  report dropdowns correctly listed both new reports immediately.
- **Period mode's deterministic computation**: of the 47 computed items, 43
  were correct end to end — accurate absolute/percent deltas (e.g. Diluted
  EPS `$9.68 → $17.95`, `+85.4%`; Basic Average Shares `7.45B → 7.43B`,
  `-0.2%`), correct alphabetical-by-metric sort, correct per-item citations
  (`statement_type` + `period_end`), and correct `complete` state (no
  coverage boundaries, since baseline/current shared units throughout, stale
  or not).
- **Mode switch** (`Compare Reports` / `Compare Financial Periods`): the two
  modes are correctly mutually exclusive and each correctly gates on its own
  prerequisite (≥2 reports; ≥2 periods for the selected statement/period
  type), matching `ChangeBriefSection.tsx`'s own stated design.
- **Failure-path rendering** (read from source, not exercised live since no
  crash occurred — see Finding A): `job.stage === "failed"` renders a
  `Banner` with a Retry button and the redacted error message, the same
  honest-failure pattern as Filing Analysis/Q&A, confirming report mode
  would degrade the same way if the ceiling were ever reached in practice.

## 6. Acceptance Criteria

- [x] Report mode live-verified end to end against a real reachable LLM on a
      substantive real case, resolving the Filings-brief-inherited open
      question about whether its bounded payload reaches the shared
      truncation ceiling.
- [x] Period mode live-verified end to end; deterministic computation
      confirmed correct.
- [x] Finding B root-caused precisely (exact function, exact fixing commit
      and timestamp, exact stale `fetched_at`), confirmed live on two
      independent UI surfaces (Financials tab and Changes), confirmed to be
      inherited stale data rather than new code in this sub-slice.
- [ ] Findings A (resolved question, not a defect) and B are not applied
      here — Docs writes briefs, not patches.

## 7. Open Questions / Risks

- **Finding A's result is real but not exhaustive**: only one substantive
  real case was tried, not an adversarial attempt to maximize item count or
  per-item explanation length. If Backend/CTO want a harder guarantee before
  fully closing this question, a deliberately maximal synthetic case could
  be constructed — not attempted here, consistent with confirming what a
  real pair of reports produces rather than manufacturing an artificial
  edge case no real user report would resemble.
- **Finding B's actual blast radius**: confirmed live for MSFT specifically;
  not enumerated across the rest of the corpus (e.g. IBM, TSLA from earlier
  sub-slices). Since the fix landed today with no backfill step, every
  ticker whose financials were acquired before 2026-09-20 13:44:27 IST is
  presumptively still affected — worth a quick direct query against the
  `financial_statements` (or equivalent) collection to confirm the full
  scope before deciding urgency.
- **Finding B's fix direction, not decided here**: (a) a one-time backfill
  re-running `_infer_unit()` over every stored `metrics[]` entry and
  rewriting `unit` in place — cheap, since the raw values are already
  correct and no re-fetch from yfinance is needed, only reclassification;
  (b) treat already-acquired data as intentionally frozen and require a
  user-triggered re-acquisition (the existing "Check for financial
  statements" flow) to pick up the fix. CTO/Backend's call.
- **Finding A's closure status needs a caveat**: Sub-Slice 2's Finding A was
  recorded as fixed and committed; this pass is the first live confirmation
  that "fixed" needs to read "fixed prospectively, not backfilled." Worth
  relaying to whoever tracks that finding's closure so the record reflects
  it's not fully resolved for existing data.
- **Noted, not treated as a finding**: one of the two report-mode test
  reports' stored `query` field shows garbled, duplicated text (`"...
  cloudWhat is the outlook ... growth? growth?"`). Most likely attributable
  to this session's own browser-automation tooling (a stray keystroke event
  surviving a failed-click-then-retry sequence during input), not a product
  defect — `change_brief_narrative.py` never reads `query`, only
  `extracted_data`/`sentiment_analysis`/`scorecard`, so it had zero effect
  on Finding A's test, and a second, deliberate retype in the same session
  produced no repeat. Flagged only for completeness.
- **Sequencing**: per CTO's breakdown, AI Insights is next.
