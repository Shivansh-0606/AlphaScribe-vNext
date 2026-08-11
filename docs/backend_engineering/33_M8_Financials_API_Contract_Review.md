# M8 Financials API Contract Review

**Status:** 🟡 **API CONTRACT READY — AWAITING FINAL CTO APPROVAL.** This
remains a documentation-only artifact — no backend, frontend, ADR, or
schema/migration file was created or modified to produce it. The API
contract itself is **not yet approved for implementation.**
**Date:** 2026-08-10
**Gate:** the API-contract review Document 32 explicitly carved out as a
separate, later gate (§9/§18 of ADR-029) — Document 32's approval
authorizes the *architecture*, not this contract and not M8
implementation.
**Reviewed/amended contract:** `GET /companies/{ticker}/financials` as
proposed in [`30_ADR_Proposal_M8_Financial_Statements_Data_Model.md`](30_ADR_Proposal_M8_Financial_Statements_Data_Model.md)
§9/§18, read together with the architecture
[`32_M8_Pre_Implementation_Decision_Pack.md`](32_M8_Pre_Implementation_Decision_Pack.md)
subsequently decided (currency/unit model §2.D, acquisition state §4,
canonical metric shape §3) — Document 32 is treated as authoritative
wherever this document and the older ADR-029 §9 text diverge.
**Governance reopening (2026-08-10):** previously frozen; **narrowly
reopened** solely to govern one additional endpoint,
`POST /companies/{ticker}/financials/acquire` — see "Amendment —
Financials Acquisition Request Endpoint" near the end of this document.
This reopening does not change the `GET` contract's own status above,
does not authorize implementation of either endpoint, and does not
touch any other provision of this document.
**`POST .../acquire` contract status:** 🟢 **CTO APPROVED.** The
endpoint's wire-level contract (path, method, parameters, response
envelope, outcome enumeration/precedence, HTTP status, external error
contract) is fully frozen (Amendment §1-§17 below) — no field, status
code, or semantic in that contract remains undesigned, no further,
separate API Contract Review gate follows it, and it has received final
CTO approval (Amendment §17 step 5). This status is distinct from, and
does not alter, the `GET` contract's own status line above. Approval of
this contract does not by itself authorize implementation — see
Amendment §18.

**Governance status ledger:**

| Item | Status |
|---|---|
| Document 35 (M8 Acquisition-State Architecture) | 🟢 RATIFIED |
| Document 36 (M8 Acquisition Orchestration Architecture) | 🟢 RATIFIED |
| Document 37 (Financials Acquisition Request Endpoint Proposal) | 🟢 CTO APPROVED |
| Document 33 narrow reopening | 🟢 COMPLETE |
| Document 33 `POST .../acquire` API contract | 🟢 CTO APPROVED |
| Document 33 `GET /financials` API contract | 🟡 unchanged from Round 4 — awaiting final CTO approval, not resolved by this reopening |
| M8 implementation | 🔴 BLOCKED |

> **Revision, Round 2 — CTO-directed API contract amendment (2026-08-10):**
> the CTO reviewed the initial review (Round 1, same day) and issued
> **🟡 APPROVED WITH CHANGES**, directing this document be turned from a
> review that only *identifies* gaps into a precise contract amendment
> that *resolves* them, using only already-decided architecture. This
> revision: resolves the cold-start question as read-only, no
> synchronous provider call (§4); defines the full client-visible
> response envelope with justification per field (§3); adds three
> concrete example responses (§3); defines the external HTTP error
> contract and documents existing internal mappings where those mappings
> are established (§5); resolves historical-period return policy as
> "no limit, return everything persisted" (§6); resolves
> the "unknown ticker" question using `GET /filings`'s own code behavior
> as direct precedent (§5); and explicitly marks two points — the
> `period_type` omission behavior and numeric-value transmission
> precision — as still requiring final CTO confirmation rather than
> silently deciding them (§10). No new ADR, error model, caching
> strategy, versioning scheme, or acquisition mechanism was introduced.
> Round 1's underlying findings are preserved below where still accurate;
> nothing was silently dropped.
>
> **Revision, Round 3 — CTO final contract micro-revision (2026-08-10):**
> the CTO finalized `period_type` as a required `annual|quarterly`
> parameter with no default; finalized metric `value` as a JSON number
> for v1 (not string-encoded decimal); corrected unknown-ticker
> semantics so acquisition state is never inferred solely from
> `FinancialStatement` absence, but is reported from a canonical
> acquisition-state source instead (§4/§5); and clarified the
> distinction between externally observable HTTP-level contract
> behavior and internal exception-class implementation, so the contract
> no longer asserts an internal class (`AuthorizationError`,
> `ValidationError`) is literally what produces a given status code
> unless that's actually established by existing code (§5). No new
> acquisition mechanism, error class, or architecture was introduced.
> §10's two previously-open items are both resolved; no artificial open
> question is retained merely to keep the document "pending."
>
> **Revision, Round 4 — CTO-directed architecture-boundary clarification
> (2026-08-10):** clarified that the financials API contract is complete
> with respect to acquisition-state semantics, while the canonical
> acquisition-state provider remains a separate architectural dependency
> outside this contract. Document 33 does not define or authorize an
> acquisition mechanism, persistence model, background job, Redis
> behavior, or state-machine implementation. M8 endpoint implementation
> must not invent such a mechanism; a separately approved architecture
> must provide the canonical acquisition-state source before the endpoint
> implementation relies on it.
>
> **Revision, Round 5 — CTO-directed narrow governance reopening
> (2026-08-10):** the CTO ratified [`35_M8_Acquisition_State_Architecture_Decision.md`](35_M8_Acquisition_State_Architecture_Decision.md)
> and [`36_M8_Acquisition_Orchestration_Architecture.md`](36_M8_Acquisition_Orchestration_Architecture.md)
> in full, approved [`37_Document33_Amendment_Financials_Acquisition_Request_Endpoint.md`](37_Document33_Amendment_Financials_Acquisition_Request_Endpoint.md)'s
> governance proposal, and explicitly authorized reopening this document
> **narrowly** to govern exactly one additional endpoint,
> `POST /companies/{ticker}/financials/acquire` — see the "Amendment —
> Financials Acquisition Request Endpoint" section below. **This
> reopening does not touch, reinterpret, or reduce the approval status
> of `GET /companies/{ticker}/financials`'s existing contract** — every
> decision in §1-§10, the Proposed Frozen Contract, and the Final
> Recommendation above remains exactly as Round 4 left it, including its
> own still-open "awaiting final CTO approval" status, which this
> amendment does not resolve one way or the other. This reopening also
> does **not** authorize implementation of either endpoint — the next
> mandatory gate is a separate API Contract Review of the new endpoint's
> wire-level schema.

---

## 1. Contract Under Review

Verbatim from ADR-029 §9 (the starting point — this document supersedes
it as the operative contract text pending final CTO approval, without
modifying the ADR file itself):

```
GET /companies/{ticker}/financials?period_type=annual|quarterly
```

The ADR-029 §9 text is a one-sentence sketch that predates Document 32's
later-decided `unit` field and acquisition-state model. Round 1 of this
review catalogued exactly what was missing; this Round 2 revision fills
those gaps using only decisions Document 32 already made.

## 2. Repository Evidence (unchanged from Round 1 — still accurate)

- `backend/server.py:765-771` — `GET /filings`: `current_user`-gated,
  `ticker.upper()` normalization, `db.filings.find({"ticker": ...}, {"_id":
  0}).sort("created_at",-1).to_list(200)`, returns `{"filings": rows}`
  with **no ticker-existence check and no 404 for zero results** — the
  query runs regardless of whether the ticker is real, and an empty list
  is a valid 200 response. This is the direct precedent §5 below relies on.
- `backend/domain/errors.py` — the existing, only error hierarchy:
  `NotFoundError`(404)/`ValidationError`(422)/`ConflictError`(409)/
  `AuthorizationError`(403)/`RateLimitedError`(429)/
  `DeadlineExceededError`(504)/`InfrastructureError`(502)/
  `LLMProviderError`(502)/`StreamingError`.
- `backend/tests/contract/test_route_inventory.py` — frozen-route
  exact-set assertion; adding this route requires updating
  `APPROVED_ROUTES` at implementation time (downstream consequence, not
  this task).
- `docs/backend_engineering/10_Backend_Security_Architecture.md` §4.5
  (`SI-1`) — shared-corpus caches (`filings`, `chunks`, `companies`)
  carry no owner scoping and are unaffected by SI-1. `financial_statements`
  is the same ownership class (ADR-029 §8, no `user_id`).
- `web/features/company-research/integration/api.ts` /
  `FinancialsSection.tsx` — zero existing frontend integration code for
  this endpoint; unchanged since Round 1.
- ADR-029 §8 / Document 32 §4 — acquisition state is decided as a
  *concept*, conceptually separate from `FinancialStatement` persistence,
  with the acquisition *mechanism* intentionally left unspecified. §4
  below resolves what this endpoint's own behavior is without inventing
  that mechanism.

## 3. Response Contract (resolved — Decisions 2 & 3)

### 3.1 Client-visible fields, with justification (not a Mongo dump)

Per Document 32's decided `FinancialStatement` model. Every field below
is included **because** it serves a stated client need — nothing is
exposed merely because it exists in persistence:

**Document/period-level:**

| Field | Why it's client-visible |
|---|---|
| `period_type` | Echoes back which of the two required values (`annual`/`quarterly`, §6.1) the response corresponds to — self-describing even though the caller already supplied it in the request |
| `statement_type` | The primary grouping key — required to distinguish income/balance_sheet/cash_flow |
| `period_end` | The historical period identity — required for any time-series rendering (the X-axis of every Data Visualization roadmap chart) |
| `fiscal_year` | Human-readable period labeling for the frozen `StatementTable`'s annual/quarterly columns |
| `currency` | Without it a numeric `value` is financially meaningless — this is the entire reason Document 32 §2.D exists |
| `source` | AlphaScribe's trust-first/source-attribution posture — every other data surface (`source_documents`, `filings.source`) exposes this |
| `fetched_at` | Lets the frontend signal data recency to the user — a trust signal (matches the frozen "Trusted AI" / Source Traceability roadmap category) |

**Metric-level (inside each period's `metrics[]`):**

| Field | Why it's client-visible |
|---|---|
| `canonical_metric` | The normalized concept identity charts/ratios key off (nullable — unmapped rows still carry `provider_label`/`value`/`unit`, Document 32 §3) |
| `provider_label` | Preserves the raw label for unmapped rows and for transparency/debugging — matches the "preserve unknown rows" invariant (Document 32 §3) |
| `value` | The data itself |
| `unit` | Disambiguates currency vs. per-share vs. share-count vs. ratio/percentage/count (Document 32 §2.D — this is the field that made the original triple insufficient) |

**Acquisition-level:** see §4.

**Explicitly excluded / not client-visible** (do not expose merely
because it exists in persistence): any internal Mongo identifier (`_id` —
already excluded everywhere else in this codebase via projection); any
internal refresh/acquisition-job bookkeeping (`refresh_triggered`,
`refresh_started`, `refresh_job_id`, or similar) — **explicitly
prohibited** by the CTO's direction; internal repository/provider
implementation details beyond `source`/`fetched_at`. `ticker` itself is
**not repeated per-entry** — it is already the response's top-level
field (§3.2), so repeating it inside every statement/period would be
redundant, not client value.

### 3.2 JSON envelope

Shape: `ticker → period_type → statements (keyed by statement_type) →
acquisition_state + periods[] → metrics[]`. No pagination, no API
version field, no unrelated metadata, no deeper nesting than the data
itself requires.

**Example 1 — normal successful response** (values illustrative, shaped
after Document 31's actual observed AAPL data):

```json
{
  "ticker": "AAPL",
  "period_type": "annual",
  "statements": {
    "income": {
      "acquisition_state": "available",
      "periods": [
        {
          "period_end": "2025-09-30",
          "fiscal_year": "2025",
          "currency": "USD",
          "source": "yfinance",
          "fetched_at": "2026-08-10T09:00:00Z",
          "metrics": [
            {
              "canonical_metric": "total_revenue",
              "provider_label": "Total Revenue",
              "value": 416161000000,
              "unit": "currency"
            },
            {
              "canonical_metric": null,
              "provider_label": "Tax Rate For Calcs",
              "value": 0.156,
              "unit": "ratio"
            }
          ]
        }
      ]
    },
    "balance_sheet": {
      "acquisition_state": "available",
      "periods": [
        {
          "period_end": "2025-09-30",
          "fiscal_year": "2025",
          "currency": "USD",
          "source": "yfinance",
          "fetched_at": "2026-08-10T09:00:00Z",
          "metrics": [
            {
              "canonical_metric": "shares_outstanding",
              "provider_label": "Ordinary Shares Number",
              "value": 14773260000,
              "unit": "shares"
            }
          ]
        }
      ]
    },
    "cash_flow": {
      "acquisition_state": "available",
      "periods": [
        {
          "period_end": "2025-09-30",
          "fiscal_year": "2025",
          "currency": "USD",
          "source": "yfinance",
          "fetched_at": "2026-08-10T09:00:00Z",
          "metrics": [
            {
              "canonical_metric": "free_cash_flow",
              "provider_label": "Free Cash Flow",
              "value": 98767000000,
              "unit": "currency"
            }
          ]
        }
      ]
    }
  }
}
```

**Example 2 — a response containing a confirmed-unavailable statement**
(shaped after Document 31's own RELIANCE.NS `.quarterly_cashflow`
finding — real evidence, not a hypothetical):

```json
{
  "ticker": "RELIANCE",
  "period_type": "quarterly",
  "statements": {
    "income": {
      "acquisition_state": "available",
      "periods": [ "... populated, omitted here for brevity ..." ]
    },
    "balance_sheet": {
      "acquisition_state": "available",
      "periods": [ "... populated, omitted here for brevity ..." ]
    },
    "cash_flow": {
      "acquisition_state": "confirmed_unavailable",
      "periods": []
    }
  }
}
```

**Example 3 — a statement that has not yet been acquired.** `NEWTICKER`
is used here as an example of a ticker for which the **canonical
acquisition-state source reports `not_yet_acquired`** for all three
statement types — this is what that source's state produces for a
ticker with no acquisition history, not a status this endpoint infers
merely because the ticker is unfamiliar or `FinancialStatement` documents
happen to be absent (§4/§5, row 5-6):

```json
{
  "ticker": "NEWTICKER",
  "period_type": "annual",
  "statements": {
    "income": { "acquisition_state": "not_yet_acquired", "periods": [] },
    "balance_sheet": { "acquisition_state": "not_yet_acquired", "periods": [] },
    "cash_flow": { "acquisition_state": "not_yet_acquired", "periods": [] }
  }
}
```

These are **contract examples**, not implementation code — field names
and shape are fixed by this document; nothing here is executable.

## 4. Acquisition-State Semantics (resolved — Decision 1, the sole architectural blocker)

**Final direction: `GET /companies/{ticker}/financials` is, and remains,
a read-oriented endpoint.**

- **It MUST NOT synchronously call yfinance** when persisted financial
  statements do not exist. The request path is never `HTTP request →
  yfinance → transformation → Mongo write → response` — that shape is
  explicitly rejected.
- **A missing `FinancialStatement` does not automatically mean
  `confirmed_unavailable`.** The endpoint distinguishes `not_yet_acquired`
  (no fetch attempted) from `confirmed_unavailable` (a fetch was
  attempted and the provider explicitly returned nothing — Document 31
  §9's RELIANCE.NS finding) from `available`. This is Document 32 §4's
  three-state model, carried through unchanged into the response (§3.2).
- **Acquisition lifecycle is represented separately from
  `FinancialStatement` persistence**, exactly as Document 32 §4 already
  decided — `acquisition_state` in the response is not derived by
  merely checking "does a document exist," it is a first-class piece of
  information this endpoint reports, sourced from whatever canonical
  acquisition-state source exists (its storage mechanism is not
  specified by this document — see the next bullet). Precisely:
  - `not_yet_acquired` — reported when the canonical acquisition-state
    source indicates no acquisition attempt has been made.
  - `available` — reported when the canonical acquisition-state source
    indicates a successful acquisition, together with the persisted
    `FinancialStatement` data that acquisition produced.
  - `confirmed_unavailable` — reported when the canonical
    acquisition-state source indicates an acquisition was **actually
    attempted** and the provider's result established unavailability
    (Document 31's RELIANCE.NS `.quarterly_cashflow` case — an empty
    DataFrame, no exception — is the concrete precedent this state
    exists to represent).
  - **The absence of a `FinancialStatement` document, by itself, proves
    neither `not_yet_acquired` nor `confirmed_unavailable`.** Both states
    are determined by the canonical acquisition-state source, never
    inferred from document absence alone.
- **The acquisition mechanism itself — including the canonical
  acquisition-state source's own storage — is explicitly out of scope
  for this contract.** Document 32 intentionally left it unspecified, and
  this amendment does not invent one: no acquisition endpoint, no
  background job, no state-machine implementation, no Mongo collection
  for the acquisition-state source, and no Redis behavior for acquisition
  is defined here. Some other, separately-designed controlled acquisition
  path is responsible for ever moving a combination out of
  `not_yet_acquired` — this contract only guarantees that `GET .../
  financials` will faithfully report whatever state that other mechanism
  has left behind, without triggering it itself.
- **Freshness/refresh internals stay behind the API boundary.** Per
  explicit CTO direction, no `refresh_triggered`, `refresh_started`,
  `refresh_job_id`, or comparable internal-lifecycle field is added to
  the response. The endpoint exposes persisted data and acquisition
  state — nothing about *how* or *when* a refresh might happen.

This resolves Round 1's single blocking issue without designing the
acquisition mechanism the CTO explicitly said stays out of this task.

## Contract Dependency — Acquisition-State Provider

**API contract:** the financials API contract is now frozen with respect
to acquisition-state semantics. The endpoint exposes exactly three
states — `not_yet_acquired`, `available`, `confirmed_unavailable` — and
reports whichever of them the canonical acquisition-state source
currently holds for a given ticker/statement combination (§4). The API
contract requires a canonical acquisition-state source, but Document 33
does not define that source. The contract is therefore complete as an
API contract, while the acquisition-state provider remains a separately
governed architectural dependency.

**Separate architectural dependency:** the system still requires a
canonical acquisition-state source capable of supplying those states.
The following are intentionally **out of scope for Document 33** and are
not invented here: how acquisition is triggered; where acquisition state
is persisted; the Mongo collection/schema (if any) for acquisition
state; background job architecture; Redis usage; the acquisition
state-machine implementation; provider orchestration; retry policy;
refresh scheduling; and acquisition-endpoint design.

**Implementation gate:** M8 financials endpoint implementation must not
begin by inventing an acquisition-state mechanism. Before implementation
of the endpoint begins, one of the following must be true: (1) an
already-approved architecture provides the canonical acquisition-state
source, or (2) a separate architecture decision is reviewed and approved
defining that acquisition-state provider. The implementation engineer
must not infer acquisition state from `FinancialStatement` absence as a
substitute for that source (§4/§5), and must not create an implicit
acquisition-state store merely to satisfy the API contract. This is a
governance dependency, not a reason to redesign the API — the
acquisition-state *semantics* are resolved; only the *mechanism/provider*
remains outside this document.

## 5. Error Contract (resolved — Decision 4, corrected per Round 3)

No new error type is introduced. This section states the **externally
observable HTTP contract** — the response status/shape a client actually
sees — separately from internal implementation, since the two are not
always the same mechanism even where they happen to produce the same
status code (corrected this round; Round 2 conflated them in places).

| # | Case | External HTTP contract | Internal implementation note |
|---|---|---|---|
| 1 | Missing `period_type` | **422** | Existing FastAPI/Pydantic automatic request-validation behavior (a required-parameter check), not a deliberately-raised application exception |
| 2 | Invalid `period_type` value (not `annual`/`quarterly`) | **422** | Same — existing FastAPI/Pydantic automatic enum-validation behavior |
| 3 | Authentication failure | **401** | Handled by the existing `current_user` dependency, following its existing authentication behavior — this document does not assert that this dependency raises the application's `AuthorizationError` class (that class is 403, "authenticated but forbidden," a distinct case — see `domain/errors.py`); no such equivalence is claimed |
| 4 | Database/infrastructure failure | **502** | Follows the existing `InfrastructureError` → 502 application convention, per `domain/errors.py` and `app/api/errors.py`'s handler |
| 5 | Unknown/unseen ticker (never seen by AlphaScribe at all) | **200** — not a 404 solely because the ticker is absent | `GET /filings`'s existing code is the precedent for *not requiring a ticker-existence lookup to avoid a 404* (it never checks `companies` before querying and returns 200+empty regardless). **This precedent establishes only that a successful empty/shared-corpus response is acceptable — it does not, by itself, establish what `acquisition_state` the response reports.** That is determined by whatever canonical acquisition-state source exists (§4) — for a ticker AlphaScribe has genuinely never attempted, that source would report `not_yet_acquired`, but this is the acquisition-state source's answer, not an inference this endpoint makes merely from `FinancialStatement` absence |
| 6 | Known ticker, no acquired financial data | **200** | `acquisition_state` reported exactly as the canonical acquisition-state source states it (§4) — not inferred from document absence |
| 7 | Statement confirmed unavailable | **200**, `acquisition_state: "confirmed_unavailable"` in the response body — **not an error** | Reported from the canonical acquisition-state source, which records that a fetch was attempted and the provider explicitly returned nothing (Document 31's RELIANCE.NS `.quarterly_cashflow` case is the concrete precedent this state exists to represent) |
| 8 | Provider (yfinance) failure | **Outside this route's request lifecycle** | Since `GET .../financials` never calls yfinance synchronously (§4), no provider-failure case belongs to this route at all — it belongs to whatever separate, not-designed-here acquisition mechanism eventually calls yfinance |

**Explicit reiteration:** `not_yet_acquired` and `confirmed_unavailable`
are **valid acquisition states inside a successful 200 response**, never
HTTP errors. **No new HTTP status is introduced anywhere in this table.**

## 6. Request Parameter, Historical, and Numeric Semantics (all resolved per Round 3)

### 6.1 `period_type` (request parameter — finalized)

**`period_type` is REQUIRED. Accepted values: `annual`, `quarterly`.
There is no default.**

```
VALID:    GET /companies/AAPL/financials?period_type=annual
VALID:    GET /companies/AAPL/financials?period_type=quarterly
INVALID:  GET /companies/AAPL/financials
```

A missing or invalid value both produce **422**, via the existing
FastAPI/Pydantic automatic request-validation behavior (§5, rows 1-2) —
no bespoke validation logic is introduced. This closes the omission
question Round 2 had left open.

### 6.2 Historical periods

**Return all persisted periods matching the requested ticker and
`period_type`, with no pagination or artificial limit.** Document 32 §8
already decided indefinite retention; Document 31's own evidence shows
current response sizes are small (39-77 metrics per statement document,
5-7 periods per combination — "a few hundred to low-thousands of metric
entries" at present scale, Round 1 §9). No repository or product evidence
justifies pagination today. If a future scale requirement changes this,
that is a **separately reviewed contract evolution**, not something to
pre-build speculatively here.

### 6.3 Freshness

Covered by §4 — the endpoint serves persisted data and reports
acquisition state; it does not expose refresh mechanics.

### 6.4 Numeric value representation (finalized)

**`value` is transmitted as a JSON number for v1.** Not a
string-encoded decimal, not a custom numeric wrapper. This follows the
existing API's numeric-JSON convention (e.g. `scorecard`'s
`faithfulness`/`overall` floats are already transmitted this way). This
is **not** a claim that the API provides arbitrary accounting-grade
decimal precision — it is a v1 transmission-format decision. Document 31
observed values (up to ~4 trillion) remain exactly representable within
IEEE-754 double's safe-integer range at current scale. If exact
decimal/accounting semantics are ever required, that is a **separately
reviewed API evolution** — not something this v1 contract commits to or
precludes. No `Decimal` serialization, custom numeric type, backend
serialization change, or frontend schema change is introduced by this
decision — it is a contract-text decision only.

## 7. Security (unchanged conclusion from Round 1 — still accurate)

- **Authentication:** the endpoint requires the existing `current_user`
  dependency, following its existing authentication behavior (§5, row 3).
- **Authorization/ownership:** none required — shared corpus, confirmed
  via `08` RI-5 and `10` SI-1. No cross-tenant risk exists because there
  is no tenant dimension on this data.
- **Data exposure:** public company financial data, same classification
  as `filings`/`companies` (`08` §9). No PII risk.
- **Sensitive provider metadata:** none identified — `provider_label` is
  a plain row-label string, not a credential.
- **No `user_id` filtering, tenant ownership, per-user authorization, or
  new security middleware is introduced** — the shared-corpus model is
  preserved exactly as decided.

**No security issue identified.**

## 8. Frontend Compatibility (resolved — the §4/§3 gap Round 1 identified)

The frozen `StatementTable` design (`05_Content_Data_Display.md`
§"States") requires the frontend to distinguish Loading / Available /
**Partial Failure**. Round 1 found the response schema couldn't support
this because acquisition state wasn't represented. **§3/§4 above resolve
this**: `acquisition_state` per `statement_type` (`not_yet_acquired` /
`available` / `confirmed_unavailable`) is now an explicit, first-class
part of the response, giving the frontend exactly the three signals the
frozen design already requires — no frontend component, schema, or
architecture is created or modified by this document; this section only
confirms the contract is now *capable* of supporting the already-frozen
state model.

## 9. Required Implementation Constraints (preserved conclusions, unchanged)

These conclusions from Round 1 stand and are not reopened:

- **Versioning:** the existing unversioned `/api/...` convention is
  preserved. No `/api/v1`, `Accept-Version` header, or version field is
  introduced.
- **Observability:** M6's existing infrastructure (tracing via
  `get_tracer()`, Prometheus metrics following the `llm_calls_total`
  convention, automatic correlation-ID/structured-logging middleware)
  covers this endpoint without redesign. Specific metric names remain an
  implementation detail, not a contract term.
- **Caching:** SI-1 does not bind this endpoint (shared corpus, no owner
  scoping to leak). No Redis caching is introduced (Document 32 §8,
  unchanged).
- **Financial statement types / extensibility:** `statement_type` grouping
  (`income`/`balance_sheet`/`cash_flow`) is unambiguous and appropriately
  extensible without structural change. No issue.
- **Route-inventory contract test:** adding this route requires updating
  `test_route_inventory.py`'s `APPROVED_ROUTES` set at implementation
  time — a known, expected downstream consequence, not a contract defect.

## 10. Remaining CTO Decisions

**None.** Both points left open after Round 2 (`period_type` omission
behavior, numeric value transmission precision) were resolved by the
CTO's Round 3 direction and are reflected throughout this document (§6.1,
§6.4). No other genuine unresolved API-contract decision remains — no
artificial open question is retained merely to keep this document
"pending." (The acquisition mechanism itself, per §4, remains a
deliberately separate, not-yet-designed piece of work — that is a
statement of scope, not an unresolved *contract* question: this contract
only needs to say the endpoint reports whatever that mechanism produces,
which it does.)

---

## Proposed Frozen Contract (summary)

```
METHOD:              GET
PATH:                /companies/{ticker}/financials
AUTH:                current_user (existing authentication pattern)
TICKER:              normalized to uppercase server-side
PERIOD TYPE:         annual | quarterly
                     REQUIRED, NO DEFAULT
ACQUISITION:         read-oriented endpoint
                     NO synchronous provider acquisition
STATEMENT TYPES:     income | balance_sheet | cash_flow
HISTORICAL PERIODS:  all persisted periods matching the requested
                     ticker/period_type; no pagination, no artificial limit
VALUE:               JSON number
ACQUISITION STATES:  not_yet_acquired | available | confirmed_unavailable
                     (reported from the canonical acquisition-state
                     source — NEVER inferred solely from
                     FinancialStatement absence, §4/§5)
                     These states are part of the API contract; their
                     canonical source/provider is a separate
                     architectural dependency not defined by this
                     contract (see "Contract Dependency —
                     Acquisition-State Provider" above §5).
ERRORS:              existing application/API error behavior;
                     no new error hierarchy; acquisition states are
                     NOT errors (§5)
VERSIONING:          existing unversioned /api/... convention (§9)
STATUS:              ready for final CTO review
```

---

## Final Recommendation

## 🟡 API CONTRACT READY — AWAITING FINAL CTO APPROVAL

This document is not itself an approval. Every gap Round 1 identified,
and both points Round 2 left open, have been resolved using only
already-decided architecture (Document 32) and existing codebase
precedent (`GET /filings`, `domain/errors.py`, FastAPI/Pydantic's
existing validation behavior) — with the internal-vs-external error
distinction and acquisition-state sourcing corrected per the CTO's Round
3 direction. No unresolved contract decision remains. The API contract
itself is complete and ready for final CTO approval; the canonical
acquisition-state provider is a separate architectural dependency
("Contract Dependency — Acquisition-State Provider" above) that must be
approved — via already-approved architecture or a separate architecture
decision — before endpoint implementation begins. This is a governance
dependency on implementation, not a new unresolved API-contract
decision. The CTO's final review determines whether this contract is
approved for implementation.

---

## Amendment — Financials Acquisition Request Endpoint

### 1. Governance status

**Document 33 — previous status:** frozen, governing exactly one
endpoint (`GET /companies/{ticker}/financials`, §1-§10 above,
unchanged by this amendment).

**Document 33 — new status:** **narrowly reopened**, solely to govern
one additional endpoint: `POST /companies/{ticker}/financials/acquire`.
No other provision of this document is reopened, reworded, or
reinterpreted by this amendment. That endpoint's wire-level contract is
now **complete** (§17) and 🟢 **CTO APPROVED** (§17 step 5).

**This narrow reopening does not authorize implementation.** Document
35 (M8 Acquisition-State Architecture) and Document 36 (M8 Acquisition
Orchestration Architecture) remain ratified and unchanged. Document 37
(the governance proposal this amendment formalizes) remains approved
and unchanged. `GET /financials`'s existing contract remains frozen
exactly as Round 4 left it. Only this one additive endpoint is being
introduced into Document 33's governance scope.

### 2. Purpose

`POST /companies/{ticker}/financials/acquire` is **an explicit request
to initiate or ensure acquisition of the financial data implied by the
requested company and period type.** It is not a retry API, a
force-refresh API, a provider-selection API, a status API, an
acquisition-history API, a job-management API, a general
acquisition-management API, or a direct provider API. Internal
orchestration — who actually calls the provider, when, and how failures
are retried — remains entirely governed by Document 36 and is not
redefined here.

### 3. Endpoint definition

```
METHOD:            POST
PATH:              /companies/{ticker}/financials/acquire
AUTHENTICATION:    current_user (identical to GET /financials)
AUTHORIZATION:     same resource-ownership/access boundary as
                   GET /financials — none beyond authentication;
                   shared corpus, no per-user ownership dimension
QUERY:             period_type = annual | quarterly - REQUIRED, no default
BODY:              none
VERSIONING:        existing unversioned /api/... convention (unchanged)
```

### 4. Request semantics

For `(ticker, period_type)`, the request concerns the three statement
identities `income`, `balance_sheet`, `cash_flow` implied by that pair
— the same batch scope Document 36 §5 already established for this
trigger. **`statement_type` is not exposed as a request parameter** —
doing so would expose internal acquisition granularity beyond what this
governance amendment authorizes. Only identities currently
`not_yet_acquired` are submitted to the shared acquisition use case
(Document 35/36, unchanged): an identity already `available` is not
reacquired; an identity already `confirmed_unavailable` is not
refreshed (a deliberate re-check remains a separate, out-of-scope
refresh-policy question, ADR-029 §18 item 4). No new acquisition state
is introduced, and the three-state model ratified by Document 35 is not
altered in any way.

### 5. Response semantics — frozen wire-level envelope

**The response body is frozen as exactly these three fields, no more:**

```json
{
  "ticker": "AAPL",
  "period_type": "annual",
  "outcome": "requested"
}
```

| Field | Contract |
|---|---|
| `ticker` | Normalized uppercase ticker, echoing the requested path parameter. Contains no new state information — a pure echo |
| `period_type` | Echoes the required request parameter — exactly one of `annual`, `quarterly` |
| `outcome` | Exactly one of `requested` \| `available` \| `confirmed_unavailable` \| `mixed` (§6) |

**No other response field is introduced.** This response body explicitly
does **not** expose: `acquisition_state` as a top-level response field;
task IDs; job IDs; attempt IDs; retry counts; provider names; lock
state; worker state; timestamps; provider errors; or internal
persistence details of any kind.

**`requested` means only that the acquisition request was accepted for
processing.** It does **not** imply that a new task was definitely
created, that acquisition definitely started, that acquisition
succeeded, that no other acquisition attempt was already running, or
that eventual availability is guaranteed. The response does not expose
internal task/lock state — the endpoint remains a request trigger, not
a status endpoint.

### 6. Response precedence

Evaluated in this exact deterministic order over the relevant
identities implied by `(ticker, period_type)`:

1. **If any relevant identity is `not_yet_acquired` then outcome =
   `requested`.** Takes precedence over every other case.
2. **Else if all relevant identities are `available` then outcome =
   `available`.**
3. **Else if all relevant identities are `confirmed_unavailable` then
   outcome = `confirmed_unavailable`.**
4. **Otherwise outcome = `mixed`.**

No alternative precedence rule and no additional public state are
introduced.

**Example A — rule 1 applies (`requested`):**

```
Request:  POST /companies/AAPL/financials/acquire?period_type=annual

Response: HTTP 200
{
  "ticker": "AAPL",
  "period_type": "annual",
  "outcome": "requested"
}
```

Underlying state: `income = available, balance_sheet = not_yet_acquired,
cash_flow = confirmed_unavailable`. Meaning: at least one relevant
identity was `not_yet_acquired` and the request was accepted for
processing. **This does NOT guarantee that a new task was created or
that acquisition has started** (§5).

**Example B — rule 2 applies (`available`):**

```
Response: HTTP 200
{
  "ticker": "AAPL",
  "period_type": "annual",
  "outcome": "available"
}
```

Underlying state: all relevant identities are already `available`.
Meaning: all relevant identities are already `available` — nothing was
scheduled.

**Example C — rule 4 applies (`mixed`):**

```
Response: HTTP 200
{
  "ticker": "AAPL",
  "period_type": "annual",
  "outcome": "mixed"
}
```

Underlying state: `income = available, balance_sheet = available,
cash_flow = confirmed_unavailable`. Meaning: no identity remains
`not_yet_acquired`, but the terminal states present contain a
combination of `available` and `confirmed_unavailable`.

### 7. HTTP status — frozen

**Success status: 200.** No `202 Accepted` pattern exists anywhere in
this codebase today, and every existing fire-and-forget `POST` in this
backend (`/reports/generate`, `/learning/explain`) already returns 200
with a small acknowledgment body — 200 matches existing convention and
does not imply a trackable resource this endpoint deliberately doesn't
expose. This is the frozen wire-level HTTP contract for this endpoint's
success case — not subject to a further, separate contract review (§17).

### 8. Error semantics — frozen external error contract

Reuses the existing `domain/errors.py` error hierarchy exactly (§5
above, unchanged) — no new public error class is introduced:

| Status | Case |
|---|---|
| **401** | Authentication failure |
| **422** | Malformed ticker, missing `period_type`, invalid `period_type`, or otherwise malformed request |
| **429** | Rate limited |
| **502** | Synchronous infrastructure failure encountered while processing the request |

**Explicit asynchronous-provider-failure boundary:** provider failures
occurring *after* the acquisition request has been accepted are **not**
part of this POST response contract. The request is answered
synchronously, before any provider call runs (Document 36 §9.3's
fire-and-forget model, unchanged) — a timeout, exception, malformed
response, or rate limit encountered by the *asynchronous* acquisition
attempt is never surfaced through this endpoint's response. Such
outcomes are observed later, exclusively through
`GET /companies/{ticker}/financials` (§3/§4 above, unchanged). This
endpoint's error contract governs only failures in *accepting* the
request, never failures in the acquisition attempt itself.

This is the frozen external error contract for this endpoint.

### 9. Unknown ticker behavior

A malformed ticker produces **422**. A syntactically valid ticker that
is unknown to AlphaScribe **may be accepted** — the request is not
rejected merely because the ticker has never been seen before; the
eventual acquisition processing (Document 36) determines the outcome.
**Ticker existence is intentionally not validated as a prerequisite to
accepting the acquisition request.** No mandatory preliminary
company-existence lookup is introduced merely to validate the request —
this mirrors §5 row 5's existing `GET /filings` precedent exactly.

### 10. Idempotency / deduplication

Repeated requests for the same acquisition target must not create
uncontrolled duplicate acquisition work. The endpoint may fold into the
existing shared acquisition mechanism and its in-process deduplication
(Document 36 §9-§11, unchanged) — but **"accepted for processing" is an
acknowledgment of the request only and does not guarantee that a new
internal task was created.** No internal lock/task state is exposed
through the API. No second idempotency system is introduced — Document
35's AS-4 remains the sole correctness guarantee under concurrency,
unchanged.

### 11. Rate limiting

Proposed protection: key by `user + ticker + period` (e.g.
`acquire:{user_id}:{ticker}:{period_type}`), reusing the existing
in-memory rate-limiter pattern (`agents/auth.py`'s
`is_rate_limited`/`record_hit`) — no new infrastructure, no Redis. **This
is explicitly not a global acquisition budget** — it does not by itself
prevent a user from requesting acquisition across many unrelated
tickers in quick succession; a global budget, if ever needed, is a
separate implementation/operational question not designed by this
amendment. Rate limiting itself is not implemented by this task — the
existing backend security/rate-limit architecture is referenced only as
the future implementation basis.

### 12. Authentication / authorization

Identical to `GET /financials`: `current_user` required; no additional
authorization dimension exists because this data has no per-user
ownership boundary (shared corpus, `08` RI-5 / `10` SI-1, unchanged). No
new authorization model is introduced.

### 13. Security invariants

- Authentication required, identical to `GET /financials`.
- Authorization follows the same existing resource-access boundary —
  none beyond authentication.
- Acquisition cannot be triggered for an "unauthorized" resource because
  no per-user resource-ownership dimension exists on this data.
- Provider credentials remain internal — not applicable today (yfinance
  and the BSE fetch path remain credential-free, Document 36 §3/§19,
  unchanged); forward-looking guidance only if a future provider ever
  requires one.
- Orchestration internals (provider selection, retry/backoff, worker/
  lock state, attempt history) remain private — never exposed through
  this endpoint's response.
- The cache-ownership invariant (SI-1) is unaffected — unchanged.
- `GET /financials` cannot bypass this endpoint's authorization, and
  this endpoint cannot bypass `GET /financials`'s — the two are
  independent, identically-authenticated endpoints with no shared
  bypass surface.

### 14. Observability

References the already-approved M6 observability architecture — not
modified by this amendment. A future implementation would be observable
through the existing infrastructure: the existing correlation-ID/
structured-logging middleware; a request-outcome metric (following the
existing `llm_calls_total`-style labeled-counter convention); tracing
via the existing `get_tracer()` helper; structured logging, server-side
only. **No acquisition/job identifier or other internal telemetry is
exposed through the public response** (§5, §10 above) — consistent with
this endpoint remaining a request trigger, not a status endpoint.

### 15. GET /financials preservation

`GET /companies/{ticker}/financials`'s existing contract (§1-§10 above)
is **entirely unchanged** by this amendment. It remains:

- strictly read-only;
- never triggering acquisition, synchronously or asynchronously;
- never scheduling acquisition;
- never mutating acquisition state;
- never invoking a provider;
- governed by its existing authentication (`current_user`) and
  authorization (none beyond authentication) exactly as §7 above states;
- governed by its existing response contract (§3 above) exactly as
  written;
- governed by its existing error semantics (§5 above) exactly as
  written.

This amendment introduces an additive endpoint alongside `GET
/financials`; it does not modify, reinterpret, or weaken `GET
/financials`'s contract in any respect.

### 16. Rejected alternatives

Carried forward from Document 37's approved evaluation:

- **GET-triggered acquisition** — rejected. This is what Document 36
  Round 1 proposed and the CTO rejected outright; `GET /financials`
  remains strictly read-only, unconditionally, under this amendment.
- **Frontend-only retry** — rejected as a complete solution. Client
  polling with no backend endpoint to call has nothing to invoke;
  Document 36 §9.2/§12 establish polling as observation, not retry —
  this endpoint is the explicit request polling alone cannot provide.
- **Automatic background acquisition without explicit request** (a
  scheduler, Document 36 §4.6) — not rejected outright; named as the
  fallback if this endpoint proves insufficient, and a plausible future
  backstop regardless. Not proposed here because it requires new
  infrastructure (a periodic loop) not currently justified by evidence
  — the dedicated endpoint is the narrower, already-precedented option.
- **General acquisition-management API** (status, history, retry-control,
  provider-selection endpoints) — rejected explicitly and repeatedly
  throughout this amendment (§2, §5, §10 above) — directly contrary to
  the narrow scope this governance reopening authorizes.

### 17. Governance sequence — this document is the API Contract Review

**This amendment section is itself the API Contract Review artifact for
`POST /companies/{ticker}/financials/acquire`.** No further, separate
"API Contract Review" gate follows it. The governance sequence, updated
to reflect that:

1. Document 36 CTO ratification — **COMPLETE.**
2. Document 37 CTO approval — **COMPLETE.**
3. Document 33 narrow governance reopening — **COMPLETE.**
4. Document 33 API contract (this section, §1-§16 above) — **COMPLETE**
   after this final freeze: exact path, method, request parameter,
   request-body rule, authentication rule, response JSON schema (§5),
   outcome enumeration and precedence (§6), concrete response examples
   (§6), HTTP status (§7), and external error contract (§8) are all
   frozen.
5. CTO final approval of this contract — **COMPLETE.**
6. Implementation may be **separately** authorized — subject to the
   acquisition-state-provider dependency (§18 below, unchanged from
   §4's "Contract Dependency — Acquisition-State Provider").

**Step 5 is granted. Until step 6's dependency is satisfied and
implementation is separately authorized, M8 implementation remains
BLOCKED.**

### 18. Implementation authorization boundary

This amendment is a **governance/documentation artifact only.** It does
not authorize: production implementation; backend code changes;
frontend changes; tests; MongoDB schema changes; Redis changes;
repository implementation; provider implementation; acquisition-worker
implementation; orchestration implementation; or API deployment. No
endpoint was implemented, no route was registered, and
`test_route_inventory.py`'s frozen `APPROVED_ROUTES` set was not
touched to produce this amendment.

**Even with this contract now complete and CTO-approved (§17),
implementation requires all of:**

1. **Final CTO approval of this contract** (§17 step 5 — complete).
2. **The canonical acquisition-state-provider dependency satisfied** —
   unchanged from §4's "Contract Dependency — Acquisition-State
   Provider," which this endpoint relies on exactly as `GET /financials`
   already does: either an already-approved architecture provides the
   canonical acquisition-state source, or a separate architecture
   decision defines it. This dependency is **not removed or weakened**
   by completing this endpoint's wire contract — a complete API contract
   is not a substitute for the underlying state source existing.
3. **Explicit implementation authorization**, granted separately from
   both of the above.

Absent all three, M8 implementation remains **BLOCKED.**

### 19. Amendment history

| Round | Date | Action |
|---|---|---|
| - | 2026-08-10 | Document 37 (governance proposal) drafted, reviewed through four correction rounds, and CTO-approved |
| 1 | 2026-08-10 | This amendment added to Document 33, narrowly reopening governance for `POST /companies/{ticker}/financials/acquire` only. `GET /financials`'s existing contract (§1-§10 above) left entirely unchanged |
| 2 | 2026-08-10 | Final freeze: response envelope (§5), response examples (§6), HTTP status (§7), and external error contract (§8) all frozen; the "API Contract Review" gate folded into this document itself (§17); acquisition-state-provider dependency explicitly restated (§18) |

---

*Companion documents:
[`30_ADR_Proposal_M8_Financial_Statements_Data_Model.md`](30_ADR_Proposal_M8_Financial_Statements_Data_Model.md) §9/§18 ·
[`32_M8_Pre_Implementation_Decision_Pack.md`](32_M8_Pre_Implementation_Decision_Pack.md) (CTO-approved architecture this amendment builds on, unmodified) ·
[`10_Backend_Security_Architecture.md`](10_Backend_Security_Architecture.md) §4.5 (SI-1) ·
[`35_M8_Acquisition_State_Architecture_Decision.md`](35_M8_Acquisition_State_Architecture_Decision.md) (ratified, unmodified — governs the "Amendment" section above) ·
[`36_M8_Acquisition_Orchestration_Architecture.md`](36_M8_Acquisition_Orchestration_Architecture.md) (ratified, unmodified — the "Amendment" section above operationalizes its §4.4) ·
[`37_Document33_Amendment_Financials_Acquisition_Request_Endpoint.md`](37_Document33_Amendment_Financials_Acquisition_Request_Endpoint.md) (CTO-approved governance proposal this "Amendment" section formalizes, unmodified).*

*This is a documentation-only amendment. No endpoint, repository, schema,
migration, or frontend code was implemented. The `POST .../acquire`
contract has received final CTO approval (§17 step 5); M8 implementation
and implementation planning remain gated on the acquisition-state-
provider dependency (§18) and a separate implementation authorization.
The "Amendment — Financials Acquisition Request Endpoint" section above
narrowly reopens this document's governance for exactly one additional
endpoint and completes and CTO-approves that endpoint's wire-level API
contract (§17) — it does not itself authorize implementation of either
endpoint. No further, separate "API Contract Review" gate follows this
document; the remaining steps are the acquisition-state-provider
dependency (§18) and a separate implementation authorization.*
