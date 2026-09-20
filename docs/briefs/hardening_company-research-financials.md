# Migrated-Parity Hardening Pass — Company Research Sub-Slice 2: Financials — Implementation Brief

**Date:** 2026-09-19. **Author:** Docs. **For:** Frontend Engineer / Backend
(via Docs Reviewer). **Governing precedent:** [`docs/briefs/hardening_company-research-overview.md`](hardening_company-research-overview.md)
(Sub-Slice 1, passed) and CTO's six-sub-slice breakdown of Company Research.
This brief covers `FinancialsSection.tsx` (the single-period "Financial
Metrics" card, sourced from a completed Overview report's `extracted_data`)
and `FinancialStatements` (the M12 multi-period "Financial Statements" card,
`GET/POST .../financials[/acquire]`, `StatementTable.tsx`,
`agents/financials_provider.py`).

## 1. Goal

Re-verify Company Research's Financials section end-to-end against the real
running backend, including the M12 acquisition lifecycle
(not_yet_acquired → requested → available/confirmed_unavailable).

## 2. Result: two real, confirmed, reproducible defects. Not blocking a promotion decision here — that's the reviewer/Engineer's call — but genuinely worth fixing, not cosmetic.

Unlike Sub-Slice 1 (verification-only, zero defects), this sub-slice found
real bugs, both root-caused to a specific line of code, both reproduced
independently on two different tickers.

## 3. Finding A (primary): a naive substring check misformats real financial figures as raw unformatted numbers

**Observed live, twice, on two different tickers (MSFT — data acquired
2026-08-15; IBM — acquired fresh during this pass):** in the multi-period
Financial Statements table, most currency line items render correctly
(`$133.75B`), but a specific, consistent subset renders as raw, unformatted
12-digit floats sitting right next to them — e.g. IBM's Income Statement
shows `Net Income` as `$10.59B` on one row and, two rows below, `Net Income
Continuous Operations` — the **same underlying figure** — as
`10571000000.00`.

**Root cause, isolated precisely:** `agents/financials_provider.py`'s
`_infer_unit()` (line 84-85) does:
```python
if "ratio" in label:
    return MetricUnit.RATIO
```
where `label` is the lowercased `provider_label`. This is a **naive
substring check, not a word-boundary match** — and the English word
**"operation" contains "ratio" as a literal substring** (ope**ratio**n),
as does **"administration"** (administ**ratio**n). Every yfinance line item
whose label contains either word — `Net Income From Continuing Operation
Net Minority Interest`, `Net Income From Continuing And Discontinued
Operation`, `Net Income Continuous Operations`, `Net Income Discontinuous
Operations`, `Net Income From Continuing Operations` (cash flow), `Selling
General And Administration` — is misclassified as `unit: "ratio"` instead
of the correct `unit: "currency"` (which is `_infer_unit`'s own documented
default for everything else, per line 86's comment: "the observed default
for statement line items"). `formatMetricValue`'s `ratio` branch then
applies `value.toFixed(2)` to a raw dollar figure in the tens of billions,
producing exactly the malformed output observed.

**Confirmed not stale/historical:** `git log` shows exactly one commit ever
touched `financials_provider.py` (`881d942`, the original M8
implementation) — `_infer_unit` has never changed. The MSFT data (acquired
2026-08-15) and the IBM data (acquired live, during this pass, minutes ago)
show the **identical** set of mislabeled rows, confirming this is a live,
deterministic, currently-reproducible bug — not something that predates a
since-landed fix.

**Suggested fix direction (not applied here — Docs writes briefs, not
patches):** replace the substring check with a word-boundary match (e.g.
a regex `\bratio\b`, or splitting the label into words and checking
membership), so `"ratio"` matches only the standalone word, not any label
that happens to contain it as a substring.

## 4. Finding B: a failed Overview job shows "Research is still running" on the Financials tab forever, with no way to know it failed or to retry

**Observed live:** generated a real Overview report for `TSLA` under a
fresh account. Its retrieval step took **4 minutes 49 seconds** (664
candidate chunks — far more than IBM's 178 — via the same synchronous
bm25+dense+cross-encoder pipeline discussed in Sub-Slice 1), and the job
was correctly terminated by the platform's own deadline enforcement:
`"Pipeline failed: Analysis exceeded its time budget and was stopped."`
Overview's own UI handles this correctly — a clear failed-state banner with
a working Retry button.

**The Financials tab does not.** `FinancialsSection.tsx`'s gating (`if
(!jobId)`, `report.isPending`, `report.isError`, `if (!report.data)`) never
checks the job's actual terminal status — it only distinguishes "not yet
fetched" from "fetched, got a report" from "fetched, got null." A failed
job's `GET /reports/{id}` legitimately returns `{"status": "failed",
"report": null}` (confirmed directly against the response), which lands in
exactly the same `!report.data` branch as a job that's genuinely still
progressing normally. The user sees: **"Research is still running —
financial metrics will appear here once it completes."** — a promise that
will never be kept, with no error indication and no Retry action. A user
who only ever visits the Financials tab (not Overview) has no way to
discover their research failed at all.

**Compounding effect with §5's finding:** because this same generic banner
also gates the independent M12 "Financial Statements" card (§5), a failed
Overview job blocks access to a completely unrelated data source too.

## 5. Finding C: the M12 "Financial Statements" card's claimed independence from the Overview job doesn't hold in the code

`FinancialsSection.tsx`'s own doc comment (lines 17-25) states the
Statements card is "independent of the report/job above." **The control
flow contradicts this.** All four of the component's early-return branches
(`!jobId`, `report.isPending`, `report.isError`, `!report.data`) return
*before* the final `return` statement that renders both cards — meaning
`<FinancialStatements ticker={ticker} />` is **only ever reached once an
Overview job for that ticker has been run and has completed successfully**
under the current account. Confirmed live, three ways: a ticker with no
`?job=` in the URL shows only the "Run research on the Overview tab..."
banner; a ticker with a `?job=` still in progress shows only "Loading
financial metrics…"/"Research is still running..."; a ticker whose job
failed shows the same "still running" banner (§4) — in every one of these
cases, the Statements card (which needs nothing but the ticker) never
renders, even though its own data source (`GET .../financials`) is
completely unaffected by any of these states.

**Net effect:** a user cannot check a company's multi-period financial
statements — a pure, cheap, LLM-free data lookup — without first paying
for and waiting on an entire AI-generated Overview research run for the
same ticker to succeed. This is a real, live-confirmed product/architecture
mismatch between the documented intent and the shipped behavior, not a
hypothetical.

## 6. What worked correctly, confirmed live

- **The single-period "Financial Metrics" card**, once a completed report
  exists: renders exactly the fields with real values as `MetricStat`s
  (Revenue, Revenue YoY with a correct up/down arrow from a real
  leading `+`/`-` sign, EPS, Net Income), correctly omits fields the LLM
  didn't extract, and correctly shows "No financial metrics were extracted
  for this report" when none exist (observed for one real MSFT run).
- **The acquisition lifecycle, full loop, live**: a genuinely
  `not_yet_acquired` ticker (IBM, confirmed via direct API check before
  triggering) showed the correct "isn't available yet" + "Check for
  financial statements" trigger for all three statement types
  independently; clicking it fired the real `POST .../financials/acquire`
  (confirmed `{"outcome": "requested"}`), all three buttons correctly
  flipped to "Check status" together (shared mutation state, matching the
  backend's per-(ticker, period_type) — not per-statement — request
  shape); after the real background yfinance fetch completed, re-clicking
  correctly refetched and rendered the full multi-period `StatementTable`
  for all three statement types.
- **`StatementTable`'s own gap-flagging**: periods with fewer available
  years correctly show "Not available" per cell (IBM's 2021 column, mostly
  empty) rather than a blank or an error.
- **Data volume/quality note, not a defect**: the rendered tables are raw,
  unfiltered yfinance line items (100+ rows, many near-duplicates — e.g.
  four "Net Income" variants with identical values) — this is the
  documented, already-known "canonical-metric mapping doesn't exist yet"
  gap (Document 32 §3, cited in both `financials_provider.py` and
  `StatementTable.tsx`'s own comments), confirmed live to be exactly as
  severe as those comments imply, not a new finding.

## 7. Acceptance Criteria

- [x] Single-period Financial Metrics card live-verified (real values,
      correct omission of unextracted fields, correct empty state).
- [x] Full acquisition lifecycle live-verified end-to-end: not_yet_acquired
      → trigger → requested → background fetch → available → real
      multi-period table render, on a ticker confirmed not_yet_acquired
      beforehand.
- [x] Finding A (unit-misclassification) root-caused to an exact line and
      confirmed reproducible on two independently-acquired tickers.
- [x] Finding B (misleading "still running" for a failed job) reproduced
      live with a real deadline-exceeded failure.
- [x] Finding C (Statements card's claimed independence not real)
      confirmed via all three gating branches, not just one.
- [ ] Findings A/B/C are Engineer/Backend fixes, not applied here — Docs
      writes briefs, not patches. Recommend Docs Reviewer route A (backend,
      `agents/financials_provider.py`) and B/C (frontend,
      `FinancialsSection.tsx`) as their own small, separate fixes rather
      than blocking this sub-slice's closure — none of the three is a
      security or data-integrity issue, all three are honestly-labeled or
      silently-recoverable-by-navigating-to-Overview-first in the interim.

## 8. Open Questions / Risks

- **Severity/priority call**: is Finding A (data literally misdisplayed for
  ~6 recurring line items on presumably a large fraction of real tickers,
  given how common "operation(s)" and "administration" are in standard
  financial statement vocabulary) worth an expedited fix ahead of the
  remaining Company Research sub-slices, or fine to batch with whatever
  session next touches `financials_provider.py`? Docs Reviewer/CTO's call.
- **Finding B's fix shape**: should `FinancialsSection` check
  `job`/stream-derived stage (would require lifting `useResearchJob`'s
  state up or duplicating a lightweight status check), or is a simpler fix
  (e.g. `GET /reports/{id}`'s `status` field, already returned, just
  currently discarded by `useReport`) enough to distinguish `failed` from
  genuinely `running`? Worth Engineer's judgment, not decided here.
- **Are there other `_infer_unit`-style naive-substring bugs elsewhere in
  this codebase?** Not audited as part of this brief — flagging as a
  pattern worth a quick grep (`"X" in label`-style heuristics) whenever
  Backend next has capacity, not urgent enough to scope its own slice.
- **Sequencing**: per CTO's breakdown, Filings (M13/M14/M16) is next.
