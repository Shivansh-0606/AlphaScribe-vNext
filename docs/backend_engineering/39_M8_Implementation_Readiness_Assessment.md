# M8 Implementation Readiness Assessment

**Status:** 🔵 **ASSESSMENT — NOT AN APPROVAL.** This document evaluates
whether the M8 Financials-acquisition architecture is ready for
implementation authorization. It does not itself ratify, approve, modify,
or reopen any of Documents 32-38, does not create a schema, repository,
migration, or endpoint, and does not authorize implementation.
**Date:** 2026-08-11

---

## 1. Executive Summary

**Verdict: 🟡 NOT READY — TWO INDEPENDENT GOVERNANCE BLOCKERS REMAIN
(Documents 32 and 35, parallel, no ordering between them). TECHNICAL
ARCHITECTURE SUBSTANTIALLY READY.**

An earlier revision of this assessment found that Document 38's own
status line did not yet reflect CTO ratification. That has since been
resolved directly: Document 38 now carries a "Governance Addendum — CTO
Ratification Record" (added 2026-08-11) recording the CTO's ratification
of the canonical-provider decision, mirroring the same pattern Document
36 already used for its own ratification. Document 38 is therefore
**verifiably** 🟢 CTO RATIFIED as of this document's current revision —
not merely asserted, but recorded in its own text.

| Item | Actual state found in the document itself |
|---|---|
| Document 35 | 🟡 Document 35's **current document text does not contain an explicit CTO ratification record**, despite downstream documents (36, 37, 38, the Document 33 POST amendment) treating it as ratified/binding. Status line still reads "PROPOSED — AWAITING CTO APPROVAL" (line 3), footer still reads "READY FOR CTO RATIFICATION" (line 621). This is evidence of a recording gap, not a claim about what was or wasn't decided outside this repository. |
| Document 36 | 🟢 Confirmed — "CTO RATIFIED — ORCHESTRATION ARCHITECTURE APPROVED (Round 4, 2026-08-10)," with a governance-addendum ratification record. |
| Document 37 | 🟢 Confirmed — CTO APPROVED. |
| Document 33 POST contract | 🟢 Confirmed — frozen and CTO-approved (this session, prior turn). |
| `GET /companies/{ticker}/financials` (same document) | 🟡 CTO approval pending — a **separate, pre-existing, independently-tracked governance item**, not entangled with the POST/acquisition work (see §6). |
| Document 38 | 🟢 Confirmed CTO RATIFIED — ratification record added to the document itself this revision. |
| MongoDB canonical provider | 🟢 Ratified — Document 38's recommendation is now binding, per the above. Not reopened, not reconsidered. |

**Two independent governance blockers remain: Documents 32 and 35.**
Neither is a precondition for the other — no binding document in this
chain establishes that Document 35 must close before Document 32, or
vice versa. Both must close before M8 implementation is authorized; they
can close in either order or in parallel.

- **Document 35** is the foundational acquisition-state architecture
  (AS-0 through AS-5, the terminal-state model) that Documents 36, 37,
  38, and the Document 33 POST-contract amendment all explicitly build on
  and cite as "ratified" / "binding, not reopened." Its own document text
  does not carry the same closure record Documents 36 and 38 now both
  have. This does not assert that no such decision was ever made — only
  that the repository's record of it is incomplete, and this assessment
  can't treat a dependency as closed on the basis of downstream
  documents' assertions alone when the document itself doesn't say so.
- **Document 32**, confirmed by direct inspection of its own text — not
  inferred. Document 32's Summary Table classifies both the
  `financial_statements` collection name (item 2) and the complete field
  set (item 3) as **"REQUIRES FINAL APPROVAL,"** a distinct category from
  "DECIDED" and from "SEPARATE FUTURE GATE" in the same table — Document
  32 itself distinguishes these three categories explicitly and puts
  these two items in the approval-pending one, not the decided one.
  Document 32 also states, unqualified: *"This decision pack itself still
  REQUIRES FINAL APPROVAL as a whole"* (item 12) and *"M8 implementation
  remains unauthorized."* Document 32 does not delegate these two items to
  implementation-time discretion; it names them as awaiting a CTO
  decision.

**Both blockers converge on AS-5, but neither is independently sufficient
to implement it.** AS-5 requires `FinancialStatement` persistence to
happen *before* `acquisition_state = available` is written. That
ordering guarantee needs both halves settled: Document 32's approval
freezes the `FinancialStatement` persistence shape being written first;
Document 35's ratification freezes the acquisition-state architecture
governing the second write. Document 32 approval alone does not make
AS-5 implementable (the acquisition-state side would still be
un-ratified); Document 35 ratification alone does not make it
implementable either (the thing being persisted first would still be
un-approved). Only once both are closed can AS-5's ordering guarantee
safely be wired.

Beyond governance, the **technical architecture is substantially
complete** — MongoDB infrastructure, the state model, the orchestration
model, security, and observability all have clear, specific answers with
almost nothing invented for this assessment. The blockers below are
governance-status and a small number of concrete implementation-prep
gaps, not open architectural design questions.

## 2. Approved Architecture Baseline (as actually found, not as asserted)

| Document | Subject | Status found in the document itself |
|---|---|---|
| **32** | **Pre-Implementation Decision Pack** | **🔴 GOVERNANCE BLOCKER.** Per Document 32's own Summary Table: collection name (item 2) and complete field set (item 3) are both classified **"REQUIRES FINAL APPROVAL"** — a category Document 32 itself distinguishes from "DECIDED"; item 12, "this decision pack as a whole," carries the same classification. Document 32's own text: *"M8 implementation remains unauthorized."* Not delegated to implementation — an explicit, still-open CTO gate, independent of Document 35 (see §1). |
| 34 | Acquisition-State Risk Review | 🟡 Investigation only, not a decision — its "required decisions" (§7.A) are the ones Document 35 purports to resolve |
| **35** | **Acquisition-State Architecture** | **🔴 GOVERNANCE BLOCKER.** CTO ratification not yet explicitly recorded in the document's own text — governance decision requires explicit closure, independent of Document 32 (see §1) |
| 36 | Acquisition Orchestration Architecture | 🟢 CTO RATIFIED (Round 4, 2026-08-10), with an explicit ratification record |
| 37 | Acquisition Endpoint Proposal | 🟢 CTO APPROVED |
| 33 | `POST .../acquire` API contract | 🟢 CTO APPROVED (this session, prior turn) |
| 33 | `GET /financials` API contract | 🟡 CTO approval pending — separate governance item, tracked independently, not a dependency for POST/acquisition readiness (see §6) |
| 38 | Canonical Acquisition-State Provider (MongoDB) | 🟢 CTO RATIFIED — ratification record added to the document this revision |
| — | M8 implementation | 🔴 BLOCKED |

Also noted, non-blocking but worth flagging as a hygiene gap:
**`docs/backend_engineering/00_README.md`, the doc-index/ratification
register for this entire folder, has no entries at all for Documents
30-38** — its Documents table stops at 29, and its milestone header
still reads "M1 → M2 → M5 → M6" with no mention of M7 or M8. This
assessment does not fix that (out of scope — only this new document may
be created), but a future governance pass should reconcile the register
before it drifts further.

## 3. Implementation Scope

**Required** (explicitly demanded by the ratified/approved parts of the
architecture):
- `POST /companies/{ticker}/financials/acquire` per Document 33's frozen
  contract.
- A canonical acquisition-state persistence mechanism satisfying AS-0
  through AS-5 — required by the downstream architecture and the
  acquisition-state model Document 35 represents. Document 35's
  ratification must be explicitly recorded in its artifact, while
  Document 32's separate approval must settle the `FinancialStatement`
  persistence shape required by AS-5 (see §1). Documents 36, 37, 38, and
  the Document 33 POST amendment already depend on and treat AS-0 through
  AS-5 as binding; this assessment does not redesign them.
- A shared `acquire(identity)` use case invoked by the triggers Document
  36 §4 defines (report/explain ingestion, the new endpoint, manual
  operational trigger).
- MongoDB collection, unique index, and single-document conditional-write
  logic realizing the state model — Document 38's canonical-provider
  decision, 🟢 CTO RATIFIED.

**Existing / Reusable** — confirmed in the repository, not hypothetical:
- `create_mongo_client()` + `_idx()` unique-index helper
  (`backend/infrastructure/mongo/client.py`,
  `backend/infrastructure/mongo/indexes.py`) — the exact mechanism a new
  collection would use.
- `current_user` auth dependency and the Owned/Shared/Admin ownership
  predicate pattern (`backend/server.py:202-208`, Doc 10 §4.2) — this
  endpoint is Shared-class, matching `companies`/`filings`.
- The existing "fetch-and-persist with graceful degradation" shape
  already used by `ensure_company`/`ingest_document`
  (`backend/server.py:670-762`, `backend/agents/ingest.py`) — the closest
  existing analog to an "acquisition" attempt.
- `Job`/`JobStatus`/`TERMINAL_STATUSES` shape (`backend/domain/models.py`)
  — not reused directly (wrong shape, confirmed below) but the pattern
  template for a new state-machine entity.
- M6 observability: `get_tracer()`, `instrument_node`, the
  `..._total{outcome}` Counter convention, correlation-id middleware —
  all directly reusable with zero new infrastructure.
- `sonner` toast wiring on the frontend (used once, precedent exists).

**New** — genuinely unbuilt:
- The acquisition-state Mongo collection, its unique index, and a
  repository-shaped port (`AcquisitionStateRepository` or similar) behind
  `application/ports.py`'s existing Protocol convention.
- The `acquire(identity)` use case itself and its wiring into the
  orchestration triggers.
- The new POST endpoint handler.
- Provider-outcome classification: today's ingest fetchers
  (`fetch_edgar_latest`, `fetch_yfinance`, `fetch_bse_annual_report`)
  collapse every failure into a bare `None` — they do not yet distinguish
  "provider definitively has no such statement" (→ `confirmed_unavailable`,
  a terminal write) from "transient error" (→ AS-3: no write at all).
  This distinction does not exist in the current adapters and must be
  added.
- `test_route_inventory.py`'s `APPROVED_ROUTES` set and route-count
  assertion (currently pinned to 37) — a hard, pre-existing CI gate that
  will fail the moment new routes are added, until deliberately updated.
- Frontend UI for triggering acquisition and displaying per-statement-type
  state (nothing acquisition-shaped exists in `web/` today — confirmed by
  a zero-match search for "acquire"/"acquisition").

**Explicitly Out of Scope** (per Documents 35/36 themselves, not invented
here):
- A general acquisition-management API (status/history/retry-control
  endpoints) — rejected repeatedly in Document 36.
- A refresh/staleness mechanism for already-`available` data — deferred
  per ADR-029 §18 item 4.
- A scheduler/worker/reap mechanism for acquisition — Document 36 treats
  this as a named, not-yet-built fallback (§4.6), not required for v1.
- Cancellation of an in-flight acquisition attempt — no mechanism exists
  or is planned; only the provider-call timeout bounds it.
- Any change to the `GET /financials` contract's own semantics.

## 4. Component Map

| Component | Existing | Modification needed | New | Dependency |
|---|---|---|---|---|
| API/application layer (routing, auth, error mapping) | `current_user`, `_deny_cross_tenant`, `domain_error_handler` pattern | None | New route + Pydantic request/response models | `test_route_inventory.py` update |
| Acquisition use case | `ensure_company`'s fetch-and-persist shape (analog) | None | New `acquire(identity)` use case | Provider adapters, state repository |
| Acquisition orchestration | Document 36's trigger model (designed, ratified) | None | Wiring triggers → use case | Use case |
| Acquisition-state provider (Mongo) | `create_mongo_client()`, `_idx()` | None | New collection, index, repository port/adapter | Document 38 — 🟢 CTO RATIFIED |
| Provider adapters | `fetch_edgar_latest`/`fetch_yfinance`/`fetch_bse_annual_report` | **Yes** — add definitive-vs-transient outcome classification | Outcome-mapping layer | None |
| Background execution | None (deliberately non-durable per Doc 36 §9.3) | N/A | In-process `asyncio.to_thread` call per attempt | Provider adapters |
| Recovery | AS-3 (nothing to recover, by construction) | None | None | Document 35 ratification |
| Retry/idempotency | AS-4 (monotonic precedence, single-doc conditional write) | None | Conditional-write query implementing AS-4 | State repository |
| Concurrency | AS-4 | None | Same conditional-write logic | State repository |
| Eventing | None planned/needed | N/A | N/A | N/A |
| Observability | `get_tracer()`, metrics catalog convention, correlation middleware | None (reuse as-is) | New metric/span names following existing convention | None |
| Security | `current_user`, Owned/Shared/Admin predicate, SI-1 | None | None (Shared-class, no new trust boundary) | None |
| Frontend integration | `FinancialsSection.tsx` (single-snapshot only), `sonner` toast (one precedent) | Likely — `FinancialsSection` would need to grow multi-statement/acquisition-state awareness | New acquisition-trigger UI + status badge component | Foundation `Badge`/`Table`/`Loader` primitives (all exist, none acquisition-shaped yet) |

## 5. API Implementation Readiness

`POST /companies/{ticker}/financials/acquire` — contract is frozen and
CTO-approved (Document 33 Amendment §1-§17). Verified implementable as
written:
- **Authentication**: `current_user` dependency, same as every other
  tool route — no gap.
- **Authorization**: Shared-class resource (no per-user ownership
  dimension, Document 33 §7) — the existing predicate pattern covers
  this with no new logic.
- **Ticker/period_type handling, body, response schema, outcome
  semantics/precedence, HTTP status, error semantics**: all fully
  specified in Document 33 §1-§16 with concrete worked examples; nothing
  ambiguous found.
- **Rate limiting**: Document 33 §7 defers to implementation-time choice
  between the legacy in-memory `is_rate_limited`/`record_hit` pattern and
  the newer `RateLimiter` Protocol port (`application/ports.py:69-79`,
  explicitly intended to replace the legacy dict per its own module
  docstring). Not a blocker — an implementation-time choice with a stated
  preferred direction (use the port).
- **Idempotency/deduplication**: covered by AS-4 at the state-provider
  level, not by anything new at the endpoint.

**No blocker found here.** The one hard mechanical requirement:
`backend/tests/contract/test_route_inventory.py`'s `APPROVED_ROUTES` set
and its `== 37` count assertion must be updated as part of the same PR
that adds the route, or CI fails by design.

## 6. GET /financials Compatibility

The existing `GET /companies/{ticker}/financials` contract (Document 33
§1-§10) is unaffected by any M8 acquisition work — the POST amendment
explicitly does not touch it, and this assessment does not either. Its
status line is unchanged from Round 4: "awaiting final CTO approval, not
resolved by this reopening."

**This is a separate governance item, tracked independently, and it is
not a dependency for backend acquisition-capability readiness.** No
binding document (32, 33, 35, 36, 37, or 38) states that `GET
/financials`'s own approval is a prerequisite for implementing the POST
acquisition endpoint or the acquisition-state provider — the two
contracts are independently frozen/pending in Document 33, and nothing
here reopens, redesigns, or waits on the `GET` contract. It must not be
reopened merely because the POST acquisition endpoint is being
implemented. The backend M8 acquisition foundation (state provider,
orchestration, POST endpoint) can proceed on its own governance timeline,
provided the frozen POST contract is respected; `GET /financials`'s
approval is tracked separately and does not appear in this document's
blocker list (§17, §19).

## 7. MongoDB Implementation Readiness

Conceptually implementable today, with the canonical provider decision
already ratified by Document 38. Remaining work is implementation detail,
subject to closure of Document 35's governance record and the separate
Document 32 approval governing the `FinancialStatement` persistence shape
required by AS-5 (§1/§2). What it requires:
- **Collection**: new, name not yet finalized (Document 35 §13 defers
  this explicitly).
- **Document structure**: per-identity (`ticker + period_type +
  statement_type`) document carrying at minimum a terminal-state field
  (`not_yet_acquired | available | confirmed_unavailable`) — shape not
  yet fixed, deliberately deferred to implementation per Document 35 §8.
- **Indexes**: a unique compound index on the identity tuple, following
  the exact `_idx()` pattern already used for 25 existing indexes across
  9 collections (`backend/infrastructure/mongo/indexes.py`) — mechanically
  identical to existing work, no new pattern needed.
- **Uniqueness constraints**: the unique index above is sufficient; no
  additional constraint identified.
- **Atomic transitions**: a single-document conditional update (e.g.
  update-if-new-precedence-not-lower) — native Mongo capability, no
  transaction needed (AS-4, reinforced by the standalone-topology finding
  in Document 38 §3/§13/§14).
- **Concurrency control**: same conditional write — no lock needed.
- **Recovery queries**: none required — AS-3 means there is nothing
  partial to query for.
- **Migration requirements**: none — net-new collection, not a migration
  of existing data (Document 38 §7).
- **Retention requirements**: indefinite, no TTL index (AS-0) — opposite
  of every existing Redis-resident TTL'd structure, consistent with every
  other Mongo-resident durable collection in this codebase.

One documented, non-blocking risk carried forward unchanged from Document
38 §14 (this assessment does not re-litigate it, per this task's explicit
"do not reopen" instruction): the Mongo client sets no explicit write
concern (`w:1` driver default applies), and Document 08's own stated
convention (`w:1, j:true` under a replica set) presumes a replica-set
topology this deployment does not currently have (`scripts/run.py` starts
`mongod` with no `--replSet` flag). This is a pre-existing characteristic
of every collection in this database, not something M8 introduces, and
Document 38 already classifies it as an operational/infrastructure
consideration for production hardening, not a provider-selection or
architecture blocker.

## 8. Acquisition Orchestration Readiness

Document 36 is ratified and resolves lifecycle transitions, provider
invocation, retry, cancellation, concurrency, idempotency, partial
acquisition, and recovery with concrete, specific answers (§4-§16,
summarized in §8 of this assessment's component map). **Six items are
explicitly left open as implementation-time "Engineering Questions"
(Document 36 §25)** — none of them architecture ambiguity, all
engineering-level:

1. Exact provider-call timeout duration.
2. Whether rate-limit pressure ever justifies a backoff/cooldown policy.
3. Exact client-side polling interval/cap (frontend/UX decision).
4. Whether §4.6's scheduler fallback is ever built, and under what
   evidence threshold.
5. Whether the pre-existing `reap_stale()` should be wired to a periodic
   caller in production (adjacent gap, not new).
6. Exact mechanism for threading a correlation identifier into an
   outliving `acquire()` task.

None of these block starting implementation — they're engineering
decisions to make during implementation, not CTO gates (see §16).

**Separately, Document 36 documents an accepted residual risk** (§9.2,
§20 scenario 8, §21): the "liveness gap" — an identity may have no
guaranteed future retry if no trigger ever fires again for it. This is
recorded as a known, reviewed trade-off within the ratified document, not
an unresolved question this assessment is raising fresh.

## 9. Provider Integration Readiness

`backend/agents/ingest.py`'s three fetchers (`fetch_edgar_latest`,
`fetch_yfinance`, `fetch_bse_annual_report`) already follow the
try/except-to-`None` graceful-degradation shape CLAUDE.md requires, and
their orchestrating caller (`ensure_company`) is structurally the closest
existing analog to what an `acquire()` use case would do. One concrete
gap, classified as an **IMPLEMENTATION PREREQUISITE** (not a redesign of
provider architecture, not a governance blocker — a piece of work that
must land before the acquisition-state write path can be built):

- **Outcome classification is missing.** All fetchers currently return
  `None` on any failure — network error, rate limit, or "this ticker
  genuinely has no such statement" are indistinguishable today. AS-3/AS-4
  require this distinguished: a **definitive unavailable** outcome must
  map to `confirmed_unavailable` (a terminal write), while a **transient
  failure** must map to no terminal-state write at all. This is new
  classification logic layered on the existing fetchers, not a redesign
  of them, and it must be resolved before — not after — the
  acquisition-state repository's write path is implemented (see §18,
  step 5).
- **Latency**: Document 36 §7 assumes a bounded, `asyncio.to_thread`-wrapped
  single provider call per attempt with a timeout (duration TBD, §25 item
  1) — consistent with the existing `httpx.AsyncClient(timeout=25.0)`
  precedent already in the codebase. No incompatibility found.

No new provider and no provider-selection change is implied or needed.

## 10. Recovery Readiness

AS-3 (Document 35 — governance recording gap, but internally consistent
— see §1) means there is nothing to recover at the state-provider level
by construction:
a crash before a definitive write leaves the prior state untouched.
Combined with Document 36's deliberately non-durable execution model
(§9.3), the accepted trade-off is that an in-flight *attempt* itself can
be silently lost on crash with no trace — recoverable only by a future
trigger firing again (§8 above). This matches the "no reap/sweep/worker
recovery" prohibition already established for this feature. No new
recovery mechanism is required or should be built.

## 11. Security Readiness

- **Authentication**: `current_user`, unchanged, no new mechanism.
- **Authorization/ownership**: Shared-class resource, existing predicate
  pattern (Document 10 §4.2), no per-user dimension.
- **Acquisition-trigger authorization**: same as the endpoint's own auth
  — no separate trigger-authorization concept exists or is needed.
- **Provider credential isolation**: unchanged — existing provider
  fetchers already isolate credentials/config the same way this feature
  would.
- **Cache-ownership invariant (SI-1)**: not implicated — this feature
  introduces no caching/memoization/dedup layer that could leak another
  user's data, since the resource is Shared-class to begin with.
- **Secret handling**: no new secrets introduced.
- **Abuse/rate limiting**: covered in §5 — implementation-time choice of
  mechanism, not an open design question.

No new security model is introduced or required.

## 12. Observability Readiness

M6 infrastructure is directly reusable with zero new infrastructure:
`get_tracer()` + `instrument_node` for spans, the established
`alphascribe_<name>_total{outcome}` Counter convention for state
transitions/retries/failures, and the existing correlation-id middleware
for structured logging. Document 36 §17-18 already specifies exactly
which metric/span names this feature should add, following the existing
catalog pattern — this is additive cataloguing work, not new design.

## 13. Test Strategy

**Unit**: state-transition/precedence logic (AS-4's conditional-write
outcome for every input combination), outcome-mapping (provider result →
terminal-state or no-write), idempotency (repeat-write is a no-op).

**Integration**: Mongo persistence (unique index + conditional write
against a real/test Mongo instance, following the existing `_idx()` test
pattern if one exists), orchestration (trigger → use case → provider →
state write, end to end), provider boundary (mocked provider outcomes),
recovery (simulated crash mid-attempt leaves state untouched).

**Contract**: `POST .../acquire` against Document 33's frozen response
examples (§6) — closest existing model is
`backend/tests/backend_test_iter6.py` (`POST /companies/ensure`
structure). `GET /financials` contract tests are blocked on that
contract's own approval (§6 above) — not in scope to write yet.

**Failure**: timeout, provider failure (both transient and definitive),
partial acquisition (one of three statement types succeeds), duplicate
concurrent request, restart-recovery (kill process mid-attempt, verify
untouched state), cancellation (verify: none exists, so nothing to test
beyond "disconnect doesn't cancel").

**Security**: unauthorized request (no session), unauthorized resource
access pattern consistent with existing Shared-class tests, rate-limit
enforcement, ownership-boundary regression (should be a no-op given
Shared classification, but worth an explicit negative test).

`test_route_inventory.py` must be updated in the same change that adds
the route — this is a hard CI gate, not optional.

## 14. Migration & Deployment Readiness

- **MongoDB migration**: none required — net-new collection (§7).
- **Indexes**: created idempotently at startup via the existing
  `indexes.py` mechanism — no separate migration script.
- **Backfill**: none — no prior data to backfill; the collection starts
  empty and is populated lazily on first acquisition.
- **Feature flag / staged rollout / rollback strategy / compatibility
  window**: none of the existing infrastructure in this codebase uses
  feature flags or a staged-rollout mechanism (confirmed absent). The
  closed route inventory (`test_route_inventory.py`) is a **CI contract
  gate, not a production rollout mechanism** — it prevents an
  undeclared route from merging, it does not stage or gate a deploy.
  Route inventory must be updated in the same PR that adds the route.
  Rollback does not require a database migration, since this is a
  net-new collection with no prior data. No migration script or
  deployment-config change is proposed or needed here.

## 15. Frontend Impact

`web/features/company-research/` exists and is fully built, but has
**zero** references to "acquire"/"acquisition" and its `FinancialsSection.tsx`
renders only a single-period, 7-field LLM-extracted snapshot sourced from
`/reports/{id}` — explicitly not the multi-period statement table this
endpoint would eventually feed. **This is not "no changes needed" — the
existing frontend cannot consume this capability without new work.**
Concretely missing: any API client call to
`/companies/{ticker}/financials/acquire`, any acquisition-state-aware UI
(no acquisition-status-badge-shaped component exists in
`web/components/foundation/`), and any trigger-then-poll/toast pattern
reusable as-is (the closest precedent, `useResearchJob.ts`, is
SSE-based, not poll-based, and would need adaptation, not reuse).

**This is real, new frontend work — and it is classified as a separate
implementation slice/follow-on, not an architectural blocker for backend
acquisition implementation.** The backend M8 acquisition foundation
(state provider, orchestration, POST endpoint) can be implemented
independently of the eventual frontend acquisition UX, provided the
frozen API contract (Document 33) remains respected. No frontend design
is proposed here — this section only records that the gap exists and its
scope, per §18 step 13.

## 16. Open Questions

| # | Question | Affected architecture | Why it matters | CTO decision required? |
|---|---|---|---|---|
| 1 | Is Document 32's final approval granted (collection name, field set, pack as a whole)? | `FinancialStatement` persistence, which AS-5 requires to precede `acquisition_state = available` | Document 32's own Summary Table classifies these items "REQUIRES FINAL APPROVAL," distinct from "DECIDED," and states M8 implementation "remains unauthorized" | **YES/NO — governance closure required; independent blocker, parallel to #2** |
| 2 | Is Document 35's ratification explicitly recorded in its own artifact? | Everything downstream (36, 37, 38, 33 amendment) | The entire acquisition-state model's authority currently rests on a document that still reads "PROPOSED — AWAITING CTO APPROVAL" in its own text | **YES/NO — governance closure required; independent blocker, parallel to #1** |
| 3 | Provider-outcome classification (transient vs. definitive) | Orchestration, AS-3/AS-4 | Current ingest fetchers don't distinguish these; needed before `confirmed_unavailable` can be written correctly | No — engineering-level implementation prerequisite, must be resolved *before* the write path is built, not after |
| 4 | Timeout duration, backoff policy, polling cadence, scheduler-or-not (Doc 36 §25 items 1-4) | Orchestration | Concrete values needed before code ships, but the *mechanism* for each is already decided | No — engineering-level |
| 5 | `00_README.md`'s stale ratification register (no M7/M8 entries) | Documentation hygiene only | Doesn't block implementation, but the register is no longer trustworthy for this milestone | No — documentation housekeeping |

## 17. Implementation Risks

| Risk | Category | Severity |
|---|---|---|
| Document 32's collection name, field set, and the pack as a whole still require final CTO approval per Document 32's own Summary Table | Governance | **BLOCKER — independent, parallel to Document 35** |
| Document 35's CTO ratification is not explicitly recorded in its own text | Governance | **BLOCKER — independent, parallel to Document 32** |
| Provider adapters conflate transient and definitive failure | Data consistency | MEDIUM — **implementation prerequisite**, must be closed before the acquisition-state write path is built (§9, §18 step 5), not a blocker to starting other prep work |
| `test_route_inventory.py`'s closed route set will fail CI until updated | Technical | LOW — mechanical, well-understood |
| Mongo default write concern (`w:1`) / standalone topology vs. Document 08's stated `w:1, j:true` RS convention | Data consistency / operational | LOW — pre-existing across the whole database, already accepted in Document 38, not new to M8 |
| Frontend has no consumer for this endpoint yet | Technical / scope | LOW-MEDIUM — separate implementation slice/follow-on (§15), explicitly not a backend architectural blocker |
| Liveness gap: an identity can go unretried indefinitely if no trigger ever fires | Data consistency | MEDIUM — accepted trade-off already documented in ratified Document 36, not new |
| `GET /financials` contract itself still unapproved | Governance | LOW for M8 acquisition purposes — separate, independently-tracked item (§6), not a dependency for POST/backend readiness |
| Migration/rollback | Migration | LOW — none required, net-new collection |
| Security | Security | LOW — no new trust boundary, existing patterns fully cover this feature |

## 18. Implementation Checklist (dependency order)

Steps 1 and 2 are a **parallel governance gate** — both must close, in
either order or simultaneously, before step 3 onward:

1. **Resolve Document 32 final approval** — collection name, complete
   `FinancialStatement` field set, and decision-pack approval (Document
   32's Summary Table items 2, 3, 12).
2. **Resolve Document 35 governance** — obtain and record explicit CTO
   ratification of the acquisition-state architecture.
3. **Synchronize Document 32 and Document 35's governance records** after
   their respective CTO closures — record the appropriate approval or
   ratification directly in each document of record, using the same
   governance-addendum pattern already demonstrated by Documents 36 and
   38 (Document 32 → a CTO approval record; Document 35 → a CTO
   ratification record), so each decision is recorded where a future
   reader will actually find it, not just asserted elsewhere.
4. Document 38 synchronization — **DONE.** Document 38 was CTO-ratified
   and its own Governance Addendum (2026-08-11) has been recorded; its
   status line reads 🟢 CTO RATIFIED. No further approval gate applies
   to Document 38.
5. **Confirm both `FinancialStatement` and acquisition-state shapes are
   frozen** (steps 1-3 complete), then finalize the implementation-level
   schema/index details each governing document explicitly deferred: the
   *acquisition-state* Mongo collection name/document shape/index
   (Document 35 §13's deferred implementation detail) — distinct from
   Document 32's `financial_statements` collection, which requires CTO
   approval (step 1) rather than being an implementation-time choice.
6. Resolve provider outcome classification (transient vs. definitive) —
   **implementation prerequisite**, must land before step 7.
7. Build the acquisition-state repository port + Mongo adapter
   (single-document conditional write implementing AS-4).
8. Build the `acquire(identity)` use case.
9. Wire the use case into Document 36's existing, ratified triggers
   (report/explain ingestion, the new endpoint, manual operational
   trigger).
10. Implement the `POST /companies/{ticker}/financials/acquire` endpoint
    against Document 33's frozen, CTO-approved contract.
11. Add observability (metrics/spans) following the existing M6 catalog
    convention.
12. Update `test_route_inventory.py`'s `APPROVED_ROUTES` set and count.
13. Write the backend test suite (§13 above).
14. Frontend acquisition UX as a **separate implementation slice** (§15)
    — not sequenced ahead of or blocking steps 1-13, and not designed
    here.

Also, separately and not gating the above: update
`docs/backend_engineering/00_README.md`'s ratification register to
include Documents 30-39 (low-effort governance hygiene, §2).

## 19. Final Readiness Decision

## 🟡 NOT READY

**Two independent governance blockers remain: Documents 32 and 35.** No
binding document establishes that either must close before the other —
they are parallel, not sequential:

- **Document 32** — its own Summary Table requires explicit CTO sign-off
  on the `financial_statements` collection name, the complete field set,
  and the decision pack as a whole — all three classified "REQUIRES FINAL
  APPROVAL," a category Document 32 itself distinguishes from "DECIDED."
  Document 32's own text states "M8 implementation remains unauthorized."
  This is not delegated to implementation and is not resolved by anything
  in Documents 35-38.
- **Document 35** — CTO ratification is not explicitly recorded in its
  own governance artifact; its status line still reads 🟡 PROPOSED —
  AWAITING CTO APPROVAL, despite being treated as ratified and binding by
  every document built on top of it (36, 37, 38, the Document 33 POST
  amendment). This assessment does not assert that the underlying
  decision was never made — only that the repository's record of it is
  incomplete, which is sufficient reason not to treat it as closed.

Both must close before implementation readiness is reached; from there,
explicit implementation authorization is a separate, later step.

**Document 38 is fully resolved, not a blocker** — its repository status
banner has been synchronized with its CTO ratification this revision (a
Governance Addendum was added directly to Document 38, mirroring
Document 36's pattern), so Document 38 is verifiably 🟢 CTO RATIFIED as
of this document. It is unrelated to the two open blockers above.

**TECHNICAL ARCHITECTURE:** substantially ready — MongoDB approach,
orchestration design, security, and observability all have specific,
implementable answers with no open architectural design questions. The
blockers above are governance authorization/recording gaps, not
technical-architecture gaps — the technical design itself is not blocked
by either document.

**IMPLEMENTATION PREREQUISITES:** must be completed per §18 — Documents
32 and 35's governance closure (parallel, no required order between
them), then provider-outcome classification before the state-write path
is built, then the remaining build-out steps. `GET /financials`'s pending
approval and the frontend acquisition UX are both tracked separately and
are not part of this blocker list.

---

## M8 IMPLEMENTATION READINESS

**STATUS:** 🟡 NOT READY

**TWO INDEPENDENT GOVERNANCE BLOCKERS (parallel, no ordering between
them):**
1. Document 32 — its own Summary Table requires final CTO approval on
   the `financial_statements` collection name, the complete field set,
   and the decision pack as a whole (items 2, 3, 12); Document 32's own
   text states M8 implementation "remains unauthorized."
2. Document 35 — its own artifact does not yet contain an explicit CTO
   ratification record (status line still reads 🟡 PROPOSED — AWAITING
   CTO APPROVAL).

**RESOLVED GOVERNANCE ITEMS:**
- Document 36 — 🟢 CTO RATIFIED
- Document 37 — 🟢 CTO APPROVED
- Document 33 POST `.../acquire` — 🟢 CTO APPROVED
- Document 38 — 🟢 CTO RATIFIED
- MongoDB canonical acquisition-state provider — 🟢 FROZEN

**IMPLEMENTATION PREREQUISITES** (§18):
- Document 32 final approval (collection name, field set, pack as a
  whole) — parallel to Document 35, no required order
- Document 35 governance recording and status synchronization — parallel
  to Document 32, no required order
- Provider-outcome classification (transient vs. definitive)
- Schema/index finalization (acquisition-state collection — distinct from
  Document 32's `financial_statements` collection above)
- Remaining implementation-level engineering decisions (Doc 36 §25)
- Repository/use-case/orchestration implementation
- Route-inventory update
- Backend tests
- Frontend acquisition UX as a separate implementation slice

**`GET /companies/{ticker}/financials`:** 🟡 CTO approval pending,
tracked separately — **not** an M8 acquisition backend blocker.

**NEXT GOVERNANCE ACTION:** Obtain and record explicit CTO decisions for
both remaining blockers — Document 35's ratification and Document 32's
final approval — then add a Governance Addendum to each (mirroring the
pattern now present in both Documents 36 and 38) so the decisions are
captured in the documents of record, not only asserted elsewhere. Once
both addenda exist, this readiness
verdict should be re-evaluated — at that point the remaining items are
implementation prerequisites (§18), not governance blockers.

STOP. No implementation performed.
