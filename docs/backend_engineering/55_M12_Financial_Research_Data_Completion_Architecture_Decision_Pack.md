# 55 — M12 Financial Research Data Completion Architecture Decision Pack

**Status:** 🟢 CTO-RATIFIED (2026-08-24) — ARCHITECTURE FROZEN.
Implementation NOT AUTHORIZED — see §10.
**Type:** Architecture investigation (research/design-only — no code changed,
no schema/migration file created, no endpoint wired)
**Depends on (cited, unmodified):**
[30_ADR_Proposal_M8_Financial_Statements_Data_Model.md](30_ADR_Proposal_M8_Financial_Statements_Data_Model.md),
[32_M8_Pre_Implementation_Decision_Pack.md](32_M8_Pre_Implementation_Decision_Pack.md),
[33_M8_Financials_API_Contract_Review.md](33_M8_Financials_API_Contract_Review.md) §1-§10,
[35_M8_Acquisition_State_Architecture_Decision.md](35_M8_Acquisition_State_Architecture_Decision.md) (RATIFIED),
[36_M8_Acquisition_Orchestration_Architecture.md](36_M8_Acquisition_Orchestration_Architecture.md) (RATIFIED),
[37_Document33_Amendment_Financials_Acquisition_Request_Endpoint.md](37_Document33_Amendment_Financials_Acquisition_Request_Endpoint.md) (CTO APPROVED),
[38_M8_Canonical_Acquisition_State_Provider_Decision.md](38_M8_Canonical_Acquisition_State_Provider_Decision.md) (RATIFIED),
[docs/governance/Feature_Parity_Tracker.md](../governance/Feature_Parity_Tracker.md) §3 (Phase 4B).
**Date:** 2026-08-24.

---

## 0. What This Document Is and Is Not

This is **not** a from-scratch design. Direct inspection this session found
that the acquisition→persistence half of this workflow is already fully
built, tested, and ratified (§1), and the retrieval contract's wire-level
shape was already fully designed in Document 33 §1-§10 — it has simply
never been ratified or implemented. This document's actual job is narrower
than "design the architecture": identify the one real gap precisely, adopt
the existing design where it already exists, and design only what's
genuinely missing (a thin HTTP read endpoint, a frontend consumer, and a
`StatementTable` render). It designs; it does not implement.

## 1. Existing Architecture Dependency (verified this session, direct reads)

| Component | File | Verified finding |
|---|---|---|
| Domain model | `backend/domain/financials.py` | `FinancialStatement`, `Metric`, `AcquisitionOutcome` (3-state: `NOT_YET_ACQUIRED`/`AVAILABLE`/`CONFIRMED_UNAVAILABLE`) — CTO-approved (Document 32), complete, pure Pydantic, no driver imports. **Module docstring literally anticipates this milestone**: "these do, eventually, via GET /financials." |
| Read port — already exists | `backend/application/ports.py::FinancialStatementRepository` | `.get(ticker, period_type) -> list[FinancialStatement]` **already defined and already implemented** — this is not a new capability. |
| Read adapter — already exists | `backend/infrastructure/mongo/financial_statements.py::MongoFinancialStatementRepository.get` | `db.financial_statements.find({"ticker": ..., "period_type": ...})`, backed by the existing I-26 unique index. Complete, working, unmodified by this document. |
| Acquisition-state port/adapter | `backend/application/ports.py::AcquisitionStateRepository`, `backend/infrastructure/mongo/acquisition_state.py` | `.get(ticker, period_type, statement_type) -> AcquisitionOutcome`, AS-4 monotonic precedence, I-27 unique index. Complete, ratified (Document 35/38), unmodified. |
| Acquisition use case | `backend/application/financials.py::AcquireFinancialsUseCase` | Frozen (Document 39 Step 5). Persists `FinancialStatement`(s) before transitioning acquisition state (AS-5); six typed result kinds; no lock, correctness from AS-4's conditional write. Unmodified. |
| Orchestration | `backend/application/financials_orchestration.py::FinancialsAcquisitionOrchestrator` | Frozen (Document 36 Step 6). Fire-and-forget, `asyncio.Semaphore(3)`-bounded, triggered today by `ensure_company` and the acquire endpoint. Unmodified. |
| Write endpoint | `backend/server.py:808-867`, `POST /companies/{ticker}/financials/acquire` | Frozen wire contract (Document 33 Amendment/Document 37), CTO approved. Reads acquisition state for all 3 `StatementType`s, schedules only the not-yet-acquired ones, returns a 4-outcome rollup (`requested`/`available`/`confirmed_unavailable`/`mixed`). **The endpoint's own docstring names the exact gap this document closes**: "GET /companies/{ticker}/financials is a separate, unbuilt, unrelated governance gate — not touched by this endpoint." |
| Read endpoint | *(does not exist)* | No `GET /companies/{ticker}/financials` route anywhere in `server.py` (confirmed via full-file grep) — the missing piece. |
| Read contract — already designed | `docs/backend_engineering/33_M8_Financials_API_Contract_Review.md` §1-§10 | A complete, worked wire contract already exists: URL shape, full JSON response envelope (`ticker → period_type → statements{income,balance_sheet,cash_flow} → {acquisition_state, periods[]} → metrics[]`), three fully worked example responses (normal success, a confirmed-unavailable statement, a not-yet-acquired ticker), an explicit client-visible-field justification table, an explicit exclusion list, and a resolved error-case table (unknown ticker → 200 not 404, matching `GET /filings`'s own precedent; provider failure is out of this route's lifecycle entirely since it's read-only). **Status: 🟡 "awaiting final CTO approval" — never ratified, never implemented.** |
| Frontend acquisition trigger | `web/features/company-research/application/useFinancialsAcquisition.ts`, `ui/FinancialsSection.tsx` | Already calls `POST .../acquire`, already renders all 4 outcome banners correctly. **The component's own code comments name this exact gap twice**: *"Display in this screen isn't built yet"* (available outcome) and *"this section will show them once structured statement data is added to the backend"* (default state). |
| Frontend render target — already spec'd | `docs/design/09_Component_Inventory.md`, `docs/experience_design/Components/05_Content_Data_Display.md` | `StatementTable` (multi-period Income/Balance/Cash Flow) is a named, frozen component in the design system's Component Inventory — referenced directly in `FinancialsSection.tsx`'s own comments as "the frozen `StatementTable`." Not designed here; already exists as a spec, just never implemented for lack of data. |
| Redis | `backend/infrastructure/redis/` | Confirmed: neither `FinancialStatementRepository` nor `AcquisitionStateRepository`'s Mongo adapters touch Redis at all. Redis today is scoped to `JobStore`/`EventBus`/`RateLimiter` only (`application/ports.py`'s own docstring). No existing precedent for financial-data caching. |

**Governance discrepancy found, reported rather than resolved (per this
document's own scope):** Document 33's governance ledger (dated
2026-08-10) states **"M8 implementation: 🔴 BLOCKED."** Direct code
inspection this session shows the acquisition state repository, financial
statement repository, acquisition use case, orchestrator, and the `POST
.../acquire` endpoint are all real, complete, and live in the working
tree — not blocked, not stubbed. This is the same shape of discrepancy
Document 47 §0 already found and disclosed for Document 45/M10 ("chat-level
directives describing governance state the repository's own documents of
record do not support") — this document does not resolve it, silently
adopt the stronger claim, or edit Document 33. It is named here because
§10's CTO decision list depends on it: ratifying Document 33's `GET`
contract is the one governance action this whole gap is actually waiting
on, independent of whatever "M8 implementation: BLOCKED" was originally
about.

## 2. Problem Definition

| Stage | State | Evidence |
|---|---|---|
| Acquisition | **Existing and sufficient** | `AcquireFinancialsUseCase` + orchestrator, frozen, live, tested |
| Persistence | **Existing and sufficient** | `MongoFinancialStatementRepository`, I-26 unique index, restatement policy decided (latest-wins upsert, ADR-029 §6.4) |
| Retrieval (repository layer) | **Existing and sufficient** | `.get(ticker, period_type)` already implemented |
| Retrieval (HTTP layer) | **Missing** | No route exists; contract fully designed (Document 33) but unratified |
| Frontend consumption | **Missing** | No hook, no API client call, no data-fetching code for the read side (acquisition-trigger side already exists) |
| User-visible financial statements | **Missing** | `StatementTable` is spec'd, never implemented — `FinancialsSection.tsx` explicitly reserves and labels the gap |

**What cannot currently be retrieved:** any persisted `FinancialStatement`,
by any client, ever — the data physically exists in MongoDB once
acquisition succeeds, but no code path reads it back out to a user.
**What the frontend expects:** exactly Document 33 §3.2's envelope shape —
confirmed by cross-referencing `FinancialsSection.tsx`'s existing
outcome-banner logic (which already understands the 3-state
`acquisition_state` vocabulary) against that document's response examples;
no divergence found. **Whether existing data is sufficient:** yes, for the
milestone as scoped — `canonical_metric`/`provider_label`/`value`/`unit`
already carry everything `StatementTable` needs; the still-open
canonical-metric mapping gap (Document 32 §3, `_infer_unit`'s
`ponytail:`-marked heuristic) is a data-*quality* concern, not a
blocking gap for rendering — `provider_label` is always present as a
fallback display value. **Whether normalization is already adequate:**
adequate for display; not adequate for cross-provider metric comparison
(out of scope, unchanged by this document).

## 3. Recommended Architecture

**Adopt Document 33 §3.2's response envelope verbatim** — do not redesign
it. Add exactly one new HTTP route, one new frontend data-fetching hook,
and wire the already-frozen `StatementTable` component. Nothing else in
the stack changes.

### 3.1 Backend: `GET /companies/{ticker}/financials`

- **Handler shape**: a thin adapter, mirroring `acquire_financials`'s own
  existing structure (`server.py:808-867`) — call
  `container.financial_statements.get(ticker, period_type)` (already
  exists) and `container.acquisition_states.get(ticker, period_type, st)`
  for each `StatementType` (same `asyncio.gather` pattern the acquire
  endpoint already uses), group the returned `FinancialStatement` list by
  `statement_type` into `periods[]`, and assemble Document 33 §3.2's exact
  envelope. No new repository method, no new use case, no new domain
  field.
- **Query params**: `period_type: annual|quarterly`, required (Document 33
  §6.1) — no default, matching the acquire endpoint's own existing
  parameter shape exactly.
- **Auth**: `current_user`, identical to every other route (Document 33
  §8's own resolved decision) — no new authorization concept.
- **Errors**: read-only, so provider failure is categorically out of this
  route's lifecycle (Document 33 §4). Ticker semantics are taken verbatim
  from Document 33's own error-case table (row 5), which names this exact
  case **"Unknown/unseen ticker (never seen by AlphaScribe at all)"** and
  resolves it to **200**, not a 404, "not... solely because the ticker is
  absent" — the response reports `not_yet_acquired` for all three
  statement types, since that is what `AcquisitionStateRepository` itself
  returns for an identity with no document (Document 32 §4's own
  read-time default). This document introduces no new ticker-validation
  rule and no new terminology — "unknown/unseen ticker" is Document 33's
  own paired term, reused exactly, not coined here.
- **Route inventory**: `tests/contract/test_route_inventory.py`'s frozen
  `APPROVED_ROUTES` set needs exactly one new entry — a known, already-named
  downstream consequence (Document 33 §2), not a design question.

### 3.2 Frontend: data-fetching + render

- **New hook**, mirroring `useReport`'s existing pattern (same feature
  module, same `@tanstack/react-query` convention already used by
  `useFinancialsAcquisition`): `useFinancialStatements(ticker, periodType)`
  calling a new `getFinancialStatements` function in
  `company-research/integration/api.ts`, alongside the existing
  `acquireFinancials` call there.
- **Render**: wire the already-frozen `StatementTable` component
  (`docs/design/09_Component_Inventory.md`) into `FinancialsSection.tsx`'s
  reserved "Financial Statements" card, replacing `StatementsBanner`'s
  current terminal "available" message (*"Display in this screen isn't
  built yet"*) with the real table once `acquisition_state === "available"`
  for a given statement type; the existing banner logic is otherwise
  preserved unchanged for `requested`/`confirmed_unavailable`/`mixed`/idle.
- **No new state management, no new design tokens, no new component
  library primitive** — `StatementTable` is already in the frozen
  inventory; this milestone only gives it real data to render.

**Acceptance matrix (frozen, if this document is ratified) — every state
`FinancialsSection.tsx` must handle once wired to the new hook:**

| Frontend state | Backend contract producing it | User-visible result |
|---|---|---|
| Loading | Request in flight (React Query `isPending`) | `Loader` — no assumption about eventual outcome |
| `NOT_YET_ACQUIRED` (per statement type) | `acquisition_state: "not_yet_acquired"`, `periods: []` (Document 33 §3.2 Example 3) | Existing idle banner — "not available yet," with the existing "Check for financial statements" acquisition-trigger action retained (§3.2's `StatementsBanner`, unchanged) |
| `AVAILABLE` + populated `periods[]` | `acquisition_state: "available"`, `periods` non-empty (Document 33 §3.2 Example 1) | `StatementTable` renders real multi-period data |
| `AVAILABLE` + empty `periods[]`, if it occurs | `acquisition_state: "available"` with `periods: []` — AS-5's persist-then-transition ordering (`application/financials.py::_acquire`) means state only becomes `AVAILABLE` after `FinancialStatement` upsert already succeeded, so this combination should not occur via the normal acquisition path; not claimed impossible outright (e.g. an out-of-band data change is not something this document's repository-layer analysis can rule out) | Treated the same as `NOT_YET_ACQUIRED`'s empty-state rendering — an honest "no data to show" state, never a fabricated table; **not** the same as `CONFIRMED_UNAVAILABLE`'s messaging, since the acquisition layer's own state says `available`, not confirmed-absent |
| `CONFIRMED_UNAVAILABLE` (per statement type) | `acquisition_state: "confirmed_unavailable"`, `periods: []` (Document 33 §3.2 Example 2) | Existing "provider has no financial statements" banner (§3.2's `StatementsBanner`, unchanged) — distinct copy from the `NOT_YET_ACQUIRED` case per §3.5's invariant |
| Request error (network/5xx/auth) | HTTP-layer failure, no valid envelope returned | Existing error-banner-with-retry pattern already used elsewhere in this feature (matching `report.isError`'s existing handling in the same file) |

This matrix is normative for implementation, not implemented here.

### 3.3 Redis — explicitly not introduced

Per §1's finding (no existing precedent, no current participation) and
this document's own instruction not to add Redis merely for this
milestone: **no caching layer is proposed.** The read query is a single,
indexed, per-`(ticker, period_type)` Mongo lookup — the same shape and
cost class as `GET /filings`, which has no cache either. If read volume or
latency ever becomes evidenced as a problem, that is a separately
justified, future decision (the same "don't build ahead of evidence"
discipline this repository's own governance record already applies
repeatedly — Document 44 §4.4, Document 47 §16, Document 52 §13).

### 3.4 MongoDB — no schema or index change

`financial_statements`' existing I-26 unique index
(`ticker+period_type+period_end+statement_type`) already supports this
read pattern (`{ticker, period_type}` is a prefix of the indexed fields).
No new collection, no new index, no versioning/retention change — Document
32 §6.4's latest-wins upsert policy is unaffected by adding a reader.

### 3.5 Architectural Invariants (frozen, if this document is ratified)

**`period_type` invariant.** The requested `period_type` is authoritative
for the complete request lifecycle. It must remain the single, consistent
identity key through every stage: HTTP request → repository query →
response envelope → frontend query identity → rendered data. The handler
(§3.1) queries `FinancialStatementRepository.get(ticker, period_type)`
with exactly the requested `period_type`, never a default or a merge of
both values; the frontend hook (§3.2) keys its query identity
(`@tanstack/react-query`'s cache key) on `(ticker, periodType)` together,
never `ticker` alone. **Annual and quarterly financial records must never
be silently mixed** — at no stage does this design combine, average, or
fall back between the two.

**`acquisition_state` invariant.** `acquisition_state` is authoritative
and is obtained from `AcquisitionStateRepository` — never inferred from
`FinancialStatement` presence or absence. `periods[]` represents persisted
financial statement data and must never be used to infer acquisition
state; the handler queries both repositories independently (§3.1) and
reports each one's own answer. This preserves the distinction between
`NOT_YET_ACQUIRED` and `CONFIRMED_UNAVAILABLE` even when both produce
`periods: []` in the response — the two states mean structurally different
things (no attempt yet, vs. an attempt that definitively found nothing,
Document 32 §4's three-state model) and collapsing them because their
`periods[]` arrays look identical would silently destroy information the
acquisition-state layer was specifically built to preserve.

## 4. Decision Rationale

- **Not "redesign the read contract":** rejected — Document 33 §1-§10
  already did this work in detail, worked examples included; redesigning
  it would be pure duplication of existing, already-written design work.
  **Document 33 contains the existing proposed retrieval contract and
  remains unratified until explicit CTO approval** — reusing its text is
  a drafting efficiency, not a claim that the contract carries any
  governance weight beyond its own recorded status. Redesigning it would
  also violate this repository's own repeated "reuse, don't reinvent"
  discipline.
- **Not "add a cache/Redis layer proactively":** rejected (§3.3) — no
  evidenced need, explicit instruction not to add one "merely for this
  milestone."
- **Not "also fix `FilingViewer`'s content-reading gap":** rejected as
  out of scope — Feature Parity Tracker names it as a *separate*,
  similarly-shaped Phase 4B placeholder, but this milestone's title and
  objective are specifically financial *statements*; bundling it would be
  scope creep beyond what was authorized.
- **Not "resolve the canonical-metric-mapping gap first" (Document 32
  §3):** rejected — `provider_label` is already a safe, always-present
  fallback per §2's finding; gating this milestone on that separate,
  larger governance process (a "five-step canonical-vocabulary governance
  process" per `financials_provider.py`'s own docstring) would block a
  now-ready milestone on an unrelated, larger one.

## 5. Explicit Non-Goals

- Any change to `AcquireFinancialsUseCase`, `FinancialsAcquisitionOrchestrator`,
  the acquisition-state repository, or the `POST .../acquire` endpoint —
  all frozen, all reused exactly as-is.
- Any change to the canonical-metric mapping process (Document 32 §3) or
  the unit-inference heuristic (`financials_provider.py::_infer_unit`).
- `FilingViewer`'s content-reading pane (a separate Phase 4B placeholder).
- Multi-provider redundancy for structured financials (still yfinance-only
  — a real, separately-scoped resilience question, not this milestone's).
- Real-time market data, any export/PDF capability, any multi-turn
  conversation feature — unrelated to financial-statement retrieval.
- Redis/caching (§3.3).
- Resolving Document 33's "M8 implementation: BLOCKED" ledger line's
  original meaning — surfaced for CTO awareness (§1), not adjudicated
  here.
- **Citation-model divergence across Research/Learning/Comparison
  Explanation** (each surface represents source attribution differently —
  a separate, previously-identified architecture-quality finding,
  unrelated to `FinancialStatement`'s own `source`/`fetched_at` fields).
  This is recorded here only as separately-tracked architecture debt.
  **Resolution is neither required for M12 architecture ratification nor
  authorized by this document.** Document 33 is not rewritten and no
  citation-system redesign is proposed by this document.

## 6. Cost / Latency / Observability

- **Cost:** zero new LLM calls, zero new provider calls — this is a pure
  Mongo read behind existing auth, same cost class as `GET /filings`.
- **Latency:** one indexed query plus up to 3 acquisition-state lookups
  (parallel via `asyncio.gather`, matching the acquire endpoint's own
  existing pattern) — no external network call in the request path.
- **Observability:** reuse existing HTTP metrics, tracing, and logging
  conventions only. Every FastAPI route already gets `http_requests_total`/
  `http_request_duration_seconds` for free (`infrastructure/observability/
  metrics.py`'s existing middleware); the handler additionally uses the
  existing tracing span convention (`get_tracer().start_as_current_span`,
  matching every other financials code path) and the existing `logger`
  pattern. **No new financial-specific metric is proposed** — existing
  observability is not demonstrably insufficient for a single, low-volume,
  read-only, indexed-query endpoint, and this document does not invent a
  new counter merely because a similar-shaped one exists elsewhere
  (`acquisition_request_total`). If a gap is later evidenced in practice,
  that is a separate, future decision, not this milestone's.

## 7. Implementation Boundary

**Not authorized by this document.** If implementation is separately
authorized, the sequence is: (1) CTO ratifies Document 33's `GET` contract
(§9 below — a governance action, not new design work); (2) add the route
handler per §3.1; (3) update `test_route_inventory.py`'s `APPROVED_ROUTES`;
(4) add the frontend hook + wire `StatementTable` per §3.2. None of these
steps is performed by this document.

### 7.1 Authorization Chain (frozen sequence)

```text
CTO ratifies Document 33
        ↓
CTO ratifies Document 55
        ↓
SEPARATE CTO implementation authorization
        ↓
Engineering
```

**Approval of Document 33 and Document 55 does NOT constitute
implementation authorization.** Each arrow above is a distinct, separate
governance act — ratifying the retrieval contract (Document 33) and
ratifying this architecture (Document 55) both remain purely
design/governance decisions; neither one, alone or together, authorizes
writing the route handler, the frontend hook, or any other code. A third,
separate, subsequent CTO decision is required before engineering begins,
exactly as this series' own established two-stage convention (§7 above)
already requires for every prior architecture pack.

## 8. Governance Status

**Architecture:** 🟢 CTO-RATIFIED (2026-08-24) — FROZEN.
**Implementation:** 🔴 NOT AUTHORIZED — a separate, subsequent CTO
implementation-authorization decision remains required (§10).

## 9. CTO Decisions Required

1. **Ratify Document 33's `GET /companies/{ticker}/financials` contract**
   (§1-§10 of that document) — the design already exists in full; this is
   a sign-off decision, not a request for new design work. **✅ RATIFIED
   2026-08-24 (§10).**
2. **Approve this document's thin-adapter architecture** (§3.1-§3.4) for
   the route handler, frontend hook, and `StatementTable` wiring. **✅
   RATIFIED 2026-08-24 (§10).**
3. **Optionally address** the Document 33 ledger discrepancy named in §1
   (whether "M8 implementation: BLOCKED" should be corrected against
   current repository evidence) — independent of, and not a prerequisite
   for, decisions 1-2. **Not addressed by the §10 ratification — remains
   open, at CTO discretion.**
4. **Separately, subsequently** authorize implementation — not granted by
   this document, per this series' own established two-stage convention.
   **Still not granted — remains the one outstanding decision (§10).**

## 10. Governance Ratification (2026-08-24)

**CTO Decision — M12 Financial Research Data Completion.** The CTO
ratified Document 33 and this document (Document 55) together, as a
single M12 governance ratification. This section is the canonical record
of that decision; §1-§9 above are unmodified by it.

**Document 33 ratified with:** annual/quarterly separation preserved;
`acquisition_state` authoritative; `periods[]` ordered by `period_end`
descending, most recent period first (Document 33 Round 6/§6.2); existing
response/error semantics preserved.

**Document 55 ratified as:** the authoritative M12 architecture — the
thin-adapter design of §3.1-§3.4 (backend route handler, frontend hook,
`StatementTable` wiring), unchanged from how it was proposed.

**M12 scope, as ratified — limited to:** existing financial persistence +
existing acquisition-state infrastructure + `GET /companies/{ticker}/
financials` + existing frontend financial-statement consumption +
existing `StatementTable`. Nothing beyond this combination is ratified.

**M12 explicit exclusions, as ratified — this ratification does NOT
authorize:** Redis; new financial-data infrastructure; provider
redesign; acquisition rewrite; citation-architecture changes (§5's
citation-model-divergence item remains separately-tracked debt,
unchanged); G8 remediation; H-1 work; generalized financial analytics;
unrelated roadmap work.

**Authorization boundary (unchanged from §7/§7.1):** this ratification
approves the contract and architecture only. It does **not** authorize
implementation. A separate, subsequent CTO implementation-authorization
decision remains required before Backend Engineering begins.

**Governance state of record, as of this ratification:**

| Item | Status |
|---|---|
| Document 33 | 🟢 CTO-RATIFIED |
| Document 55 | 🟢 CTO-RATIFIED |
| M12 Architecture | 🟢 FROZEN |
| Implementation | 🔴 NOT AUTHORIZED |
| G8 | 🔴 BLOCKED |
| H-1 | 🟡 CLOSED WITH GOVERNANCE FOLLOW-UP |
| Gate | 0 |

---

**NO IMPLEMENTATION PERFORMED. NO ENDPOINT CREATED. NO SCHEMA OR INDEX
CHANGED. NO FRONTEND CODE WRITTEN. NO EXPERIMENT RUN. This §10 addendum
is the only edit made to this document by the ratification recording —
§0-§9 are otherwise exactly as originally authored.**
