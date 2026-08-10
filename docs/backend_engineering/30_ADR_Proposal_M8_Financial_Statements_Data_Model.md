# ADR-029 (Ratified) — M8 Financial Statements & Data Visualization: Data Model, Provider, and Persistence Architecture

**Status:** 🟢 **RATIFIED** (architecture only) — 2026-08-10.
**What ratification covers:** the architectural model in this document —
document granularity (one document per statement per reporting period),
statement-document identity, the canonical financial-concept layer, the
`FinancialStatementRepository` boundary, period/units semantics, the
restatement policy direction, and the serve-then-refresh-async +
controlled-cold-start-acquisition freshness direction.
**What ratification does NOT cover** (still open, listed in full in §18):
- **M8 implementation is not automatically complete or authorized by this
  ratification.** Nothing in this document creates code, a collection, an
  index, a route, or a dependency.
- **The proposed `GET /companies/{ticker}/financials` route (§9) still
  requires its own, separate API-contract approval** — ratifying the
  architecture does not ratify the contract.
- **Implementation-time provider verification remains required** before
  any of this can be built (§17/§18's verification list; see also `31`,
  the verification spike this ratification authorizes as the next step).
- Final collection name, final literal field names, freshness threshold,
  BSE/NSE coverage strategy, restatement-policy ratification, and
  migration numbering all remain explicit follow-up decisions, not
  silently resolved by this ratification.
**Date:** 2026-08-10
**Scope of this task:** Architecture preparation only, per Document 28 §D
("Financial Statements / Data Visualization... blocked on a new ADR before
scoping") and `17`'s Milestone 8 definition (§ below). This document
proposes the ADR M8 needs before implementation can be scoped — it does not
implement M8.
**Predecessor:**
[`17_M4_Backend_Capability_Roadmap_Reconciliation.md`](17_M4_Backend_Capability_Roadmap_Reconciliation.md)
§1/§6 (Milestone 8 definition) ·
[`28_Post_M6_Roadmap_Reconciliation.md`](28_Post_M6_Roadmap_Reconciliation.md)
§C (confirms M8 still open, still blocked on this ADR).
**Does not modify:** Document 28's roadmap conclusions, M7, M6, any frozen
document (`06`–`10`), any API contract, any production code.

> **Revision note (2026-08-10):** the CTO reviewed the original proposal and
> issued **🟡 APPROVED WITH CHANGES** — this document incorporates that
> review's mandatory architectural corrections (unique index, canonical
> financial-concept layer, repository boundary, period/units semantics,
> restatement policy, async-refresh freshness direction, revised §18). The
> document remains **PROPOSED, not ratified** — the CTO's "approved with
> changes" verdict applies to the *findings*, not to this revised text,
> which itself now awaits a fresh CTO read before ratification. No
> implementation occurred as part of this revision.
>
> **Revision note, Round 2 (2026-08-10):** a second CTO review again issued
> **🟡 APPROVED WITH CHANGES**, identifying one remaining ambiguity: the
> proposed unique index implied line-level document uniqueness while §6
> left document granularity (statement-level vs. metric-level) undecided.
> This revision resolves it: **M8 v1 commits to one document per financial
> statement per reporting period** (§6.5), with the statement document's
> identity fixed as `ticker + period_type + period_end + statement_type`
> and `canonical_metric`/`provider_label` living inside each document's
> `metrics[]` array, never in its identity or index (§8). §18 is updated
> accordingly. The document remains **PROPOSED, not ratified**; no
> implementation occurred as part of this revision either.
>
> **Revision note, Round 3 — Ratification (2026-08-10):** a third CTO
> review confirmed the repository-wording fix from Round 2's follow-up
> cleanup was applied consistently, and issued **🟢 APPROVED FOR
> RATIFICATION**. The architectural model in this document is now
> **RATIFIED** — see the Status block above for exactly what that does and
> does not cover. No item in §18's "Still requiring CTO approval" or
> "Implementation-time verification" lists was silently resolved by this
> ratification; they remain open and are carried forward unchanged. The
> ratified architecture's next step is a read-only provider verification
> spike (documented separately in
> [`31_M8_Provider_Verification_Spike_yfinance.md`](31_M8_Provider_Verification_Spike_yfinance.md)),
> not implementation.

---

## 1. Problem

Two frozen MVP roadmap sections are unimplemented on the backend, and the
frontend has already built honest placeholders waiting for them:

- **Financial Statements** (`docs/master-plan/03_Feature_Roadmap.md:119-126`):
  Income Statement, Balance Sheet, Cash Flow, Quarterly Results, Annual
  Results.
- **Data Visualization** (`03_Feature_Roadmap.md:191-197`): Revenue, Profit,
  Margin, Growth, and Financial Ratio charts.

Both are blocked on the same root gap: **no structured, multi-period
financial-statement data exists anywhere in this system.** `17`'s own
Capability Matrix (§ "Financial Statements" row) confirms this by direct
code read: `agents/ingest.py` never calls yfinance's `.financials`,
`.balance_sheet`, or `.cashflow` — only `.info`, a single-period snapshot.

This is a genuinely new architectural decision (new data modeling, not a
bug fix), which is why `17` and `28` both gate M8 on an ADR before
implementation.

## 2. Current Architecture (evidence)

- **`agents/ingest.py:97-149` (`_fetch_yfinance_sync`)**: calls
  `yf.Ticker(sym).info` only — a flat dict of point-in-time metrics
  (market cap, ttm revenue, EBITDA, margins, P/E, etc.), converted to a
  narrative text block and ingested as unstructured `filing_chunks` text.
  No structured/numeric persistence at all.
- **Backend extraction (`agents/schemas.py:7-14`, `FinancialsSchema`)**: an
  LLM-populated, single-period, 7-field, all-`Optional[str]` shape
  (`revenue`, `revenue_yoy`, `eps`, `net_income`, `operating_margin`,
  `free_cash_flow`, `guidance`) extracted from whatever text the retriever
  found for one report — not a structured statement, not multi-period, not
  typed numerics.
- **Frontend (`web/features/company-research/ui/FinancialsSection.tsx:13-20,
  111-120`)**: already renders the 7-field snapshot as `MetricStat` tiles,
  and explicitly reserves a "Financial Statements" card with a placeholder
  banner: *"Multi-period Income Statement / Balance Sheet / Cash Flow
  Statement data isn't available yet — this section will show them once
  structured statement data is added to the backend."* The component's own
  docstring records this as a CTO decision from "Phase 4B" — progressive
  enhancement with an honest placeholder rather than fabricating data.
- **Frozen design spec** (`docs/experience_design/Components/05_Content_Data_Display.md:71-108`):
  a `StatementTable` component variant already exists in the frozen design
  system — "Financial statement (Income/Balance/Cash Flow; annual/quarterly)"
  — with defined states (Default/Loading/Empty/**Partial Failure** — failed
  cells flagged explicitly, never silently blank) and accessibility rules
  (proper `<table>` semantics, `aria-sort`, decimal-aligned numerics). This
  is UI-ready and waiting on real data, not something this ADR needs to design.
- **MongoDB (`08_MongoDB_Data_Architecture.md` §4.3)**: `companies` is
  `{ticker, name, updated_at}` only — no currency, country, or exchange
  field persisted anywhere today (yfinance's `.info` *does* return
  `currency`/`country`, per `ingest.py:123`, but only embedded in narrative
  text, never persisted structurally). `filings` is ingestion metadata only
  (`doc_id, ticker, company_name, source, num_chunks, char_count,
  created_at`) — no numeric/statement data.
- **No domain model layer for companies/filings.** `domain/models.py` only
  defines job-related dataclasses; company/filing access is direct
  `db.companies`/`db.filings` dict access in `server.py`/`ingest.py`, unlike
  the ports-based Clean Architecture layer built for jobs (`06` AD-2).
- **No chart library installed.** Confirmed no `recharts` (or any chart
  lib) in `web/package.json`. `CLAUDE.md` already documents this as
  deliberate — "neither is installed... add them when one is [built]."
- **Existing freshness-caching precedent** (`08` §"Cache probe" A-4):
  `reports.find_one({ticker, query}).sort(created_at,-1)` is compared
  against the ticker's latest `filings.created_at` (index I-10/I-17) — a
  **Mongo-side freshness comparison**, not a Redis cache. This is the only
  existing precedent for "is this externally-sourced data still fresh
  enough to reuse."

## 3. Evidence from Repository (summary table)

| Question | Evidence | Conclusion |
|---|---|---|
| Does a financial-statement data source exist? | `ingest.py` never calls `.financials`/`.balance_sheet`/`.cashflow` | No — confirmed absent, not merely undocumented |
| Does yfinance (already a dependency) expose statement data? | `17` §"Milestone 8" names these three properties explicitly as the integration point | Very likely yes — but the exact DataFrame shape/period coverage must be verified against the installed `yfinance` version at implementation time, not assumed here (see §17, Explicit Non-Scope) |
| Does the frontend need this now? | `FinancialsSection.tsx`'s own placeholder banner + `StatementTable` frozen design spec | Yes — UI is built and waiting |
| Is there a precedent for company currency/fiscal-period modeling? | `companies` collection has no such fields today | No — this ADR proposes the first such fields; flagged, not fabricated |
| Is there a caching precedent for external financial data? | `08` A-4 freshness comparison (Mongo-side, not Redis) | Yes — reuse this pattern, don't invent Redis caching |

## 4. Decision Options

**Option A — Extend the existing `companies`/`filings` pattern** (raw dict
access, new fields on existing or sibling collections, no ports layer).
**Option B — New Clean-Architecture domain concept** (a `FinancialStatement`
port/repository, matching the jobs pattern (`06` AD-2), fully ports-mediated.
**Option C — Do not persist structured statements at all**; fetch
on-demand from yfinance per request, no new collection.

## 5. Recommended Decision

**Revised per CTO review: Option B, kept intentionally small.** Persist
structured statement data in Mongo (matching the existing `companies`/
`filings` ownership model — shared corpus, not user-scoped, per `08` RI-5)
rather than fetching on-demand every request (Option C would repeatedly hit
yfinance's rate limits and add request latency for data that changes at
most quarterly) — that part of the original recommendation is unchanged.

What changes: the original proposal recommended Option A (extending the
un-ported `companies`/`filings` direct-dict-access pattern) on the grounds
that it matched existing precedent. The CTO's review rejected that
reasoning — new M8 architecture should not perpetuate the legacy coupling
`companies`/`filings` already carry, even though that coupling is tolerated
as-is for the corpus collections themselves (this ADR does not propose
retrofitting `companies`/`filings` with a ports layer — that would be
out-of-scope legacy rework, not part of M8).

The revised recommendation is a **narrow, forward-looking repository
boundary** for this one new capability:

```
FinancialStatementRepository (port, application layer)
        ↓
MongoFinancialStatementRepository (adapter, infrastructure layer)
```

Scoped deliberately small — a **minimum v1 repository surface**, not a
general-purpose repository framework:
- `get(ticker, period_type) -> list[StatementDocument]`
- `upsert(statement: StatementDocument) -> None`
- `freshness(ticker, period_type) -> datetime | None`

This is a floor, not a ceiling: implementation may reveal a legitimate need
for additional operations (e.g. a latest-period lookup, or a bulk upsert
for ingesting all three statement types in one pass) — those are not added
by this ADR, but the Protocol is expected to grow only as real call sites
demand it, not speculatively.

This mirrors the shape (not the full weight) of ports already defined in
`application/ports.py` (06 AD-2) — which already includes not just job
infrastructure (`JobStore`, `EventBus`) but repository-shaped Protocols
(`ChunkRepository`, `ReportLikeRepository`) for exactly this kind of
persistence boundary. `FinancialStatementRepository` would be a new
Protocol in that same file, following the same `typing.Protocol`
structural-typing convention already established there — this is
*consistent* with an existing, already-used pattern in this codebase, not a
new architectural style being invented for M8. It is explicitly
**not** an excessive abstraction hierarchy: no repository-of-repositories,
no generic CRUD interface, no dependency-injection framework beyond what
`app/container.py` already does for the jobs ports.

## 6. Data Model

**What repository evidence supports:** a new collection (working name
`financial_statements`, final name subject to CTO approval), holding
statement data from yfinance's `.financials`/`.quarterly_financials`
(income statement), `.balance_sheet`/`.quarterly_balance_sheet`, and
`.cashflow`/`.quarterly_cashflow` (or `.cash_flow`/`.quarterly_cash_flow`
depending on the installed version — **must be verified against the
pinned yfinance version before implementation**, not assumed here).

**What this ADR does NOT invent:** the exact set of line items (e.g.
"Total Revenue", "Cost of Revenue", "Operating Income" — yfinance's
DataFrame row labels vary by ticker and aren't enumerable from this
session's evidence alone), the exact fiscal-year-end representation for
non-US tickers, and the exact scale/unit convention yfinance returns values
in (BSE/NSE tickers already have special handling in `ingest.py:105-107`;
whether yfinance returns statement data at all for Indian exchange
suffixes, and what unit convention it uses per-market, is unverified in
this session — flagged, not assumed).

### 6.1 Canonical financial concept layer (revised per CTO review)

The original proposal's `line_items: {label: value}` map was rejected by
CTO review as insufficient: a purely schemaless blob cannot reliably power
cross-ticker revenue/profit/margin/growth charts or ratio calculations,
since two tickers' yfinance DataFrames may use different row labels for the
economically-equivalent concept (e.g. "Total Revenue" vs. "Revenue"). At
the same time, hardcoding every yfinance row into a rigid Pydantic model
per line item is rejected too — the row-label set is not verified in this
session and likely isn't stable across tickers/exchanges.

The revised design introduces a **canonical financial concept layer** that
sits between the provider's raw row and any consumer (statement tables,
charts, ratio math) — **as a `metrics[]` array inside one statement
document** (§6.5/§8 — document granularity is decided, not left open).
Each entry in `metrics[]` is a triple of **AlphaScribe canonical concept**,
**provider-specific label**, and **numeric value**:

```
metrics[]
├── canonical_metric   e.g. "total_revenue" | "net_income" | "operating_income"
├── provider_label     the exact yfinance DataFrame row label, verbatim
└── value               numeric
```

`canonical_metric` and `provider_label` live **inside** `metrics[]` — they
are never part of the statement document's own identity (§6.5/§8 fixes
this explicitly: the identity is `ticker + period_type + period_end +
statement_type` only).

**Unknown rows are preserved, not dropped.** Any yfinance row that doesn't
map to a known canonical concept is still added to `metrics[]` with
`canonical_metric: null` (or another clearly documented unmapped
representation) and its `provider_label`/`value` intact — ingestion never
breaks or silently discards data because a label wasn't anticipated. This
is the mechanism that satisfies "preserve unknown provider-specific rows
without breaking ingestion."

**The canonical vocabulary itself (the finite list of `canonical_metric`
values — `total_revenue`, `net_income`, etc. — and the label-to-concept
mapping table) is explicitly NOT finalized by this ADR.** It requires
verifying actual yfinance row labels across a representative sample of
tickers/exchanges against the pinned version — an implementation-time
verification task (§17), not something to guess here. This ADR decides the
*shape* of the canonical layer, not its *contents*.

### 6.2 Period semantics (added per CTO review)

The original single `fiscal_period` field is ambiguous between annual and
quarterly periods and doesn't support growth/ratio calculations that need
to know a period's actual span. The architectural discussion should
distinguish (final field names are an implementation-time naming decision,
not fixed here without more evidence than this session gathered):

- **period type** — annual vs. quarterly (already proposed as `period_type`)
- **period end** — the specific date yfinance's DataFrame column label
  represents
- **fiscal year** — which fiscal year the period belongs to (distinct from
  calendar year for companies with non-calendar fiscal years — unverified
  whether yfinance exposes this directly or it must be derived)
- **reporting period duration** — needed to distinguish, e.g., a quarterly
  figure from a trailing-twelve-month figure when computing YoY growth;
  whether yfinance's raw output already disambiguates this or requires
  derivation is unverified

This is an architectural requirement (the model must be able to represent
these distinctly), not a final schema — the exact field set is deferred to
implementation, informed by what yfinance's actual output distinguishes.

### 6.3 Units and scale semantics (added per CTO review)

Currency alone (`currency` from `.info.currency`, already fetched today per
`ingest.py:123` but not persisted — still proposed as new, per the original
ADR) is insufficient: a numeric value's meaning also depends on its scale
(whether yfinance returns raw units, thousands, or millions — this varies
by provider and sometimes by statement line). **This ADR does not fabricate
yfinance's scale convention** — it states only that the persisted model
must carry currency and a scale/unit indicator alongside every numeric
value, and that the actual convention yfinance uses (and whether it's
consistent across statement types and exchanges) must be verified during
the implementation-time provider verification spike (§17), not assumed.

### 6.4 Restatement policy (added per CTO review)

Providers occasionally revise previously-reported figures (restatements).
**v1 policy, proposed for CTO ratification, is deliberately simple — no
historical versioning:**
- The statement document identified by `(ticker, period_type, period_end,
  statement_type)` (§6.5/§8) is upserted as a whole on each fetch — its
  `metrics[]` array reflects the provider's latest-returned values, not
  appended to. A restated figure simply overwrites the prior value for
  that `canonical_metric` within the document; it is not versioned.
- Provenance/fetch metadata (`source`, `fetched_at`) is retained so a
  consumer can see *when* the document was last confirmed.
- Full historical provider-version tracking (retaining every value a
  metric ever held across re-fetches) is explicitly **out of scope** for
  v1 — a possible future capability, not a v1 requirement, and not
  something this ADR designs.

### 6.5 Document Granularity — Decided (one document per statement per period)

**M8 v1 commits to one MongoDB document per financial statement per
reporting period** — not a decision left open. Conceptually, for one
ticker/period, three separate documents exist:

```
AAPL / annual / 2025 / income
AAPL / annual / 2025 / balance_sheet
AAPL / annual / 2025 / cash_flow
```

**Why three distinct documents, not one document covering all three
statement types:** each statement type (income, balance sheet, cash flow)
is fetched, refreshed, and can fail independently — the frozen
`StatementTable` design spec's own "Partial Failure" state (§2, `05
_Content_Data_Display.md:94-95`) requires that one statement type being
unavailable never blocks the other two from rendering. A single combined
document per ticker/period would couple three independently-fetchable,
independently-failable concerns into one write/read unit; three documents
keep that failure isolation at the storage layer, not just the UI layer.

**Conceptual shape** (architectural, not yet an implemented schema — no
collection or index is created by this ADR):

```
FinancialStatement
├── ticker
├── period_type       ("annual" | "quarterly", §6.2)
├── period_end         (§6.2 — the statement document's identity field)
├── fiscal_year        (§6.2 — shape required, exact representation deferred)
├── period_duration    (§6.2 — shape required, exact representation deferred)
├── statement_type     ("income" | "balance_sheet" | "cash_flow")
├── currency           (§6.3)
├── scale/unit          (§6.3 — exact representation deferred)
├── source             ("yfinance")
├── fetched_at          (ISO-8601 — freshness §8, restatement provenance §6.4)
└── metrics[]           (§6.1 — the canonical-concept layer)
    ├── canonical_metric   (nullable/unmapped for unrecognized rows)
    ├── provider_label
    └── value
```

`canonical_metric` and `provider_label` are fields **inside** `metrics[]`
only — they are not part of the statement document's identity (§8's
index). No final field names beyond what's listed here are fabricated;
exact yfinance-derived values (row labels, scale convention, fiscal-year
representation) remain implementation-time verification (§17).

## 7. Provider Architecture

**No new provider is required or recommended.** yfinance is already a
runtime dependency (`ingest.py:103`), and `17`'s own Milestone 8 scoping
already names the exact properties (`.financials`/`.balance_sheet`/
`.cashflow`) as the integration point — extending the existing
`_fetch_yfinance_sync`-adjacent code path, not adding a new external
dependency or provider abstraction. This satisfies CLAUDE.md's "before
adding a dependency, confirm nothing already installed... does the job" —
yfinance already does. BSE/Indian-exchange coverage for statement data is
unverified (see §6) and may need the existing BSE annual-report PDF path
(`fetch_bse_annual_report`) as a documented fallback rather than a second
provider — flagged for implementation-time verification, not decided here.

## 8. Persistence Strategy

- **Collection:** new `financial_statements` (or CTO-preferred name),
  following the existing shared-corpus ownership model (`08` §2, RI-5) —
  no `user_id`, same as `companies`/`filings`.
- **Document granularity and indexing (decided, corrected per CTO
  review):** the collection stores **one document per financial statement
  per reporting period** (§6.5) — one income-statement document, one
  balance-sheet document, and one cash-flow document per ticker/period,
  each independently fetchable and independently failable. The original
  proposal's `{ticker: 1, period_type: 1, fiscal_period: -1}` unique index
  was identified as incorrect for this reason: all three statement types
  share the same ticker, period type, and period, so that key would
  collide across statement types. The **statement document's identity is
  `ticker + period_type + period_end + statement_type`**, and the unique
  compound index is:

  ```
  { ticker: 1, period_type: 1, period_end: 1, statement_type: 1 }
  ```

  This gives exactly one income statement, one balance sheet, and one
  cash-flow statement per ticker per reporting period, while letting all
  three share the same `ticker`/`period_type`/`period_end`. `canonical_metric`
  and `provider_label` are **not** part of this index — they live inside
  each document's `metrics[]` array (§6.1/§6.5), not in the document's
  identity. There is no alternative line-level document model in this
  proposal — document granularity is a single, decided architecture, not
  a choice deferred to implementation. This is documented here as a
  *proposed* schema/index decision, not implemented — no index is created
  by this ADR.
- **Repository boundary (added per CTO review):** persistence is proposed
  behind a small `FinancialStatementRepository` port (§5) with the minimum
  v1 surface of `get`, `upsert`, and `freshness` — implemented by a
  `MongoFinancialStatementRepository` adapter. This is a forward-looking
  Clean Architecture boundary for this one new capability, not a
  retroactive rewrite of the existing `companies`/`filings` direct-access
  pattern, which this ADR leaves untouched.
- **Freshness strategy (revised direction per CTO review):** the exact
  staleness threshold remains explicitly undecided (§18) — that's a product
  judgment call, not an engineering default. What changes is the *shape* of
  the strategy: the original proposal implied a request could synchronously
  call yfinance when data was stale. CTO review redirects this toward
  **serve-then-refresh-async**: `request → serve persisted data (via
  `FinancialStatementRepository.get`) → if `freshness()` indicates
  staleness, trigger a refresh that does not block the response`, rather
  than `request → synchronously call yfinance`. This ADR does **not**
  design the refresh mechanism itself (a background task, a queue, a
  next-request trigger — all unimplemented, all deferred) — it only
  establishes the architectural direction that user-facing reads should not
  block on a live provider call.

  **Cold start (added per CTO review):** the serve-then-refresh-async
  direction above describes the *existing-data* case only. When no
  statement document exists yet for a ticker/period (`get()` returns
  nothing), that is architecturally distinct and must be acknowledged
  rather than left undefined: it requires a **controlled initial
  acquisition path**, not the same "serve stale, refresh in background"
  flow (there is nothing to serve). This ADR does **not** design or
  implement that acquisition path — whether it blocks the request,
  queues, or uses a background worker is an implementation-time decision,
  not fixed here without more evidence than this session gathered. The
  point of this paragraph is only to prevent the architecture from having
  an undefined cold-start state, not to resolve it.

  **No Redis caching is proposed** —
  RA-0/RA-1 (`09` — Redis is never system of record, everything
  TTL'd/bounded) argue against it, and this data is exactly the kind of
  "reconstructible from a public source" content `08` §9 already classifies
  `companies`/`filings`/`filing_chunks` as (no backup required,
  re-ingestible).
- **Historical retention:** indefinite, matching `companies`/`filings`
  retention (`08` §9) — statement history has ongoing analytical value
  (multi-period charts, per the Data Visualization roadmap section) and
  costs are bounded (a handful of periods × 3 statement types per ticker,
  not per-chunk volume like `filing_chunks`). Restatement handling (what
  happens when a provider revises a prior figure) is addressed separately
  in §6.4 — retention here is about how many periods are kept, not about
  versioning a single period's value over time.
- **Migration:** additive only — a new collection needs no migration of
  existing data, consistent with `08`'s migration numbering (`m0001`
  precedent) if the CTO wants this tracked as a numbered migration.

## 9. API Implications (proposed only — not implemented, not approved)

**No existing API contract is touched.** The 37-route inventory
(`17` — "0 divergent") is frozen; this ADR does not modify it.

**If approved**, the minimal new surface needed is a single additive route,
proposed for separate CTO sign-off:

```
GET /companies/{ticker}/financials?period_type=annual|quarterly
```

returning the persisted `financial_statements` rows for that ticker (read
via `FinancialStatementRepository.get`, §8), grouped by `statement_type`,
each line carrying its `canonical_metric`/`provider_label`/`value` triple
(§6.1) rather than an opaque blob. This mirrors the existing `GET /filings`
pattern (metadata-only read, no mutation) rather than inventing a new
route shape. **This is a proposed contract, explicitly flagged for CTO
approval — not created or modified by this task.**

## 10. Frontend Data Contract Implications

Evidence from `FinancialsSection.tsx` and the frozen `StatementTable` spec
gives a precise target shape without redesigning anything: the frontend
needs, per ticker, statement-type-grouped rows carrying `period_type`,
period semantics (§6.2), and each metric's `canonical_metric`/`value`
(§6.1) it can group into the three statement tables the design system
already specifies, with **partial-failure
semantics** (per §"States" in `05_Content_Data_Display.md:94-95`) — if one
statement type fails to fetch/parse, that section shows "unavailable," not
a blank or a crash. The §9 proposed response shape is structured to make
this direct (group-by-`statement_type` is a client-side operation on the
proposed shape, not a new backend requirement).

## 11. Performance Considerations

- yfinance calls are synchronous, blocking I/O today (`_fetch_yfinance_sync`
  runs via `asyncio.to_thread`, per `agents/ingest.py:152-155`'s async
  wrapper) — the same pattern should extend to statement fetches, no new
  concurrency model needed.
- Fetching three DataFrames (`.financials`, `.balance_sheet`, `.cashflow`)
  per ticker is a small, bounded, infrequent cost (quarterly-reporting
  cadence) — not a hot path like `filing_chunks` retrieval (`09` §4.4's
  "up to 2,000 chunks" concern does not apply here).
- No new N+1 risk identified — a single ticker's three statements fetch
  together in one provider call sequence.

## 12. Security Considerations

- No new trust boundary: yfinance is already an allowed external
  dependency; no new hostname allowlist is needed (unlike the BSE PDF path,
  which required one per `10`'s TB-3/T-19 finding — statement data comes
  from the same yfinance SDK already vetted for the `.info` call).
- No PII: statement data is public company financial data, same
  classification as `companies`/`filings` (`08` §9 — "not personal data").
- No new authorization model needed: statement data is shared-corpus, read
  via the same `current_user`-gated pattern every other tool route already
  uses (`agents/auth.py`) — no ownership scoping question like EQ-2/EQ-3
  arises here, since there's no per-user data.

## 13. Observability

Reuse M6's already-approved infrastructure, not a redesign:
- Wrap the new fetch path the same way `_run_pipeline`'s nodes are wrapped
  today (`instrument_node()` pattern, `19` §"node instrumentation") if this
  becomes a graph node, or a comparable span if it's a plain ingest-time
  call — either way, the existing `get_tracer()` helper
  (`infrastructure/observability/tracing.py`), not a new tracing mechanism.
- A new Prometheus counter for statement-fetch outcomes (success/failure/
  stale-serve), following the existing `llm_calls_total`-style
  labeled-counter convention (`infrastructure/observability/metrics.py`) —
  no new metrics *system*, just one more instrumented call site, consistent
  with M6's own scope discipline (`19`'s "closed the gap between what was
  defined and what had a call site," not a new observability architecture).
- Correlation-id propagation is automatic (request-scoped middleware,
  already applies to any route handler) — no additional work.

## 14. Migration Strategy

Purely additive: one new collection, one new compound index, no changes to
`companies`/`filings`/`filing_chunks`/`reports`/`jobs` schemas. If the CTO
wants this numbered as a formal migration (matching `08`'s `m0001`
precedent), it would be `m0002` — flagged as a naming question for CTO
preference, not decided here.

## 15. Risks

| Risk | Likelihood | Impact | Notes |
|---|---|---|---|
| yfinance's exact statement DataFrame shape/coverage is unverified in this session | Medium | Medium | Must be confirmed against the pinned version before implementation — explicitly flagged, not guessed |
| Non-US (BSE/NSE) tickers may have sparse or absent statement data via yfinance | Medium | Medium | `ingest.py`'s existing BSE PDF fallback path may need to cover this gap — flagged, not designed here |
| Canonical-metric vocabulary (§6.1) isn't finalized by this ADR | Medium | Low | Deliberate — finalizing it now without verifying real yfinance labels would mean guessing; explicitly deferred to implementation-time verification (§17), not a gap in this revision |
| `FinancialStatementRepository`'s three-operation surface may prove too narrow once implementation starts (e.g. deletion, partial-statement upsert) | Low | Low | Kept intentionally minimal per CTO direction; extending a small Protocol later is cheap, over-designing it now is the larger risk |
| Async-refresh freshness direction (§8) implies *some* background-refresh mechanism will eventually be needed | Medium | Low (deferred, not decided) | This ADR sets direction only — no background job, queue, or scheduler is designed or implemented here (§17) |

## 16. Alternatives Rejected

- **Original Option A — extend the un-ported `companies`/`filings` direct-
  dict-access pattern (this ADR's original recommendation):** superseded by
  CTO review — new M8 architecture should not perpetuate legacy coupling,
  even though that coupling is tolerated as-is for `companies`/`filings`
  themselves. Replaced by the small `FinancialStatementRepository` boundary
  in §5/§8.
- **A fully schemaless `{label: value}` line-items blob (original §6):**
  rejected by CTO review as insufficient for cross-ticker analytical
  queries (charts, ratios, growth calculations need a stable concept
  identity, not raw provider labels). Replaced by the canonical-concept
  layer (§6.1).
- **A fully rigid Pydantic model with one typed field per yfinance row:**
  also rejected — the row-label set isn't verified as stable across
  tickers/exchanges in this session, and hardcoding it risks silent data
  loss for any label variance. The canonical-concept layer (§6.1) is the
  middle path between this and full schemalessness.
- **On-demand fetch, no persistence (Option C):** rejected — repeated
  yfinance calls per page view risk rate-limiting and add latency for data
  that changes at most quarterly; §8's freshness-compare pattern already
  has Mongo-side precedent for exactly this kind of external-data caching
  question.
- **A new charting/data provider instead of yfinance:** rejected per the
  task's own constraint ("do not select a new provider merely for
  convenience") and CLAUDE.md's dependency-lean stance — yfinance already
  does the job per `17`'s own scoping.
- **Redis-backed caching of statement data:** rejected — `09`'s RA-0/RA-1
  invariants (Redis never system of record, always bounded/TTL'd) and the
  existing Mongo-side freshness-compare precedent (§2, A-4) both argue
  against introducing a new caching layer for data that's cheap to persist
  durably and doesn't need sub-second reads.

## 17. Explicit Non-Scope

- Implementing any part of M8 (this is architecture preparation only).
- Modifying `agents/ingest.py`, `server.py`, `domain/models.py`, or any
  other production file.
- Modifying any existing API contract or the 37-route inventory.
- Adding a MongoDB collection or Redis infrastructure (this ADR *proposes*
  a collection; it does not add one).
- Designing or modifying frontend code (the frozen `StatementTable` spec
  and `FinancialsSection.tsx` are treated as evidence, not redesigned).
- Verifying yfinance's exact DataFrame shape/row-label stability, scale/
  unit convention, and exchange coverage — flagged as an implementation-
  time task (§17.1).
- Finalizing the canonical-metric vocabulary (§6.1) or writing the
  `FinancialStatementRepository`/`MongoFinancialStatementRepository` code
  (§5/§8) — this ADR proposes their shape, not their implementation.
- Designing or building any background-refresh mechanism implied by the
  serve-then-refresh-async direction (§8) — no job, queue, or scheduler is
  specified here.
- Reopening M6 or M7.
- Creating a second ADR, a new milestone document, or another roadmap
  reconciliation.

## 18. Decisions Requiring CTO Approval (revised)

### Decided by this revision (incorporating both CTO review rounds)

- **Canonical financial concept strategy** (§6.1) — the *shape* is settled:
  a `metrics[]` array holding `canonical_metric` / `provider_label` /
  `value` triples, unknown rows preserved with a null/unmapped concept
  rather than dropped. The *vocabulary itself* is not decided here — see
  Implementation-time verification, below.
- **Lightweight repository boundary** (§5/§8) — settled: a small
  `FinancialStatementRepository` Protocol (minimum v1 surface: `get`/
  `upsert`/`freshness`) with a `MongoFinancialStatementRepository`
  adapter, following the existing `application/ports.py` convention, in
  place of the original proposal's recommendation to extend the un-ported
  `companies`/`filings` pattern.
- **One document per statement per reporting period** (§6.5) — settled,
  not left open. Three documents exist per ticker/period (income, balance
  sheet, cash flow), each independently fetchable/failable, matching the
  frozen `StatementTable` spec's Partial Failure semantics.
- **Statement document identity: `ticker + period_type + period_end +
  statement_type`** (§8) — settled. `canonical_metric` and
  `provider_label` are fields inside `metrics[]`, never part of the
  document's identity or its unique index.

### Still requiring CTO approval

1. **Final collection name** (§8) — `financial_statements` is a working
   name only.
2. **Final exact field naming** (§6.2/§6.3/§6.5) — `period_end`,
   `fiscal_year`, `period_duration`, the scale/unit field's exact name —
   the *shape* is decided, the literal field names are not.
3. **The proposed `GET /companies/{ticker}/financials` route** (§9) —
   explicitly not created by this task; needs its own sign-off as an API
   contract change, separate from ADR ratification.
4. **Freshness/staleness threshold** for triggering an async refresh (§8)
   — a product judgment call (e.g., 24h vs. 7d vs. "always re-fetch if the
   fiscal period is missing"), not an engineering default this ADR should
   set unilaterally. (The *direction* — serve-then-refresh-async, with a
   distinct cold-start acquisition path — is now decided; the *threshold*
   and both mechanisms are not.)
5. **BSE/NSE statement-data coverage strategy** (§6/§15) — whether
   yfinance suffices, needs the existing BSE PDF fallback, or is
   explicitly out of scope for M8's first cut.
6. **Restatement policy ratification** (§6.4) — the proposed v1 policy
   (latest-value-wins, no historical versioning) is a product-visible
   behavior decision, offered as a recommendation, not assumed approved.
7. **Migration numbering** (`m0002` or otherwise, §14) — naming
   preference only.

### Implementation-time verification (not CTO decisions — engineering tasks)

- yfinance's exact DataFrame shape for `.financials`/`.balance_sheet`/
  `.cashflow` (and their `.quarterly_*` counterparts) against the pinned
  version (§6, §17).
- Actual row labels per statement type, across a representative
  ticker/exchange sample (§6.1, §17).
- The canonical mapping vocabulary itself — the finite `canonical_metric`
  list and its label-to-concept mapping table (§6.1) — deliberately not
  finalized by this ADR.
- Actual currency/scale (unit) convention, and whether it's consistent
  across statement types and exchanges (§6.3, §17).
- Fiscal-period metadata — whether yfinance exposes fiscal-year/period-
  duration data directly or it must be derived (§6.2).
- Exchange coverage — whether yfinance returns statement data at all for
  BSE/NSE-suffixed tickers (feeds "still requiring CTO approval" item 5,
  above, but is itself a verification task, not a judgment call).

---

*Companion documents:
[`17_M4_Backend_Capability_Roadmap_Reconciliation.md`](17_M4_Backend_Capability_Roadmap_Reconciliation.md) ·
[`28_Post_M6_Roadmap_Reconciliation.md`](28_Post_M6_Roadmap_Reconciliation.md) ·
[`08_MongoDB_Data_Architecture.md`](08_MongoDB_Data_Architecture.md) ·
[`09_Redis_Architecture.md`](09_Redis_Architecture.md) ·
[`11_ADR_Index.md`](11_ADR_Index.md) (a frozen document — formal
registration of ADR-029 there is a separate, later action, not made by
this ratification) ·
`docs/experience_design/Components/05_Content_Data_Display.md` (frozen
`StatementTable` spec) ·
`web/features/company-research/ui/FinancialsSection.tsx` (frontend
placeholder evidence).*

*Architecture ratified 2026-08-10. Implementation is still gated on (a) the
provider verification spike (`31`) and (b) separate approval of the
proposed API contract (§9) and the remaining §18 open items — do not
implement any part of this ADR until those are satisfied.*
