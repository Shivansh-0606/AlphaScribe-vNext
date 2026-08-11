# M8 Canonical Acquisition-State Provider Decision

**Status:** 🟢 **CTO RATIFIED.** See the Governance Addendum near the end
of this document for the ratification record. Ratification covers the
canonical-provider decision in this document only. It does not modify
Documents 33, 35, 36, or 37, and does not authorize implementation.
**Date:** 2026-08-10 · **Ratified:** 2026-08-11
**Builds on (binding, not reopened):** [`35_M8_Acquisition_State_Architecture_Decision.md`](35_M8_Acquisition_State_Architecture_Decision.md),
[`36_M8_Acquisition_Orchestration_Architecture.md`](36_M8_Acquisition_Orchestration_Architecture.md),
[`33_M8_Financials_API_Contract_Review.md`](33_M8_Financials_API_Contract_Review.md)
(including its "Amendment — Financials Acquisition Request Endpoint"),
[`37_Document33_Amendment_Financials_Acquisition_Request_Endpoint.md`](37_Document33_Amendment_Financials_Acquisition_Request_Endpoint.md).
**Does not:** implement anything, create schemas, create repositories,
create provider classes, modify backend/frontend code, implement
orchestration, implement either endpoint, or change any API contract.

**A note on premise, stated upfront rather than glossed over:** Document
35 §8 already selected MongoDB as the acquisition-state store, with a
full evaluation against Redis and a durability requirement (AS-0)
derived independently. This document does not pretend to discover that
decision fresh — it **verifies that Document 35 §8's decision still
holds** against everything ratified *since* Document 35 was written
(Document 36's orchestration/execution model, Document 33's now-frozen
POST wire contract) and against new repository evidence gathered today,
and produces the single, consolidated, full-depth decision record this
task's 16-section structure requires — including security, observability,
and API-implication detail Document 35 §8 did not itself elaborate.
Where this document reaches the same conclusion as Document 35 §8, it
says so and cites the original reasoning rather than re-deriving it from
scratch; where it adds genuinely new evidence, that is flagged
explicitly (§3, §14).

---

## 1. Objective

Determine the authoritative mechanism/provider through which the M8
acquisition orchestration architecture (Document 36) obtains and
persists canonical acquisition state (Document 35), and produce one
consolidated, CTO-reviewable decision record — verifying, not silently
assuming, that the answer holds against every architectural and
repository fact established since Document 35 was ratified.

## 2. Ratified Requirements (extracted from Document 35 — not invented)

| Requirement | Document 35 source | What it demands of a provider |
|---|---|---|
| **Durability** | AS-0 | Indefinite retention, not TTL'd or bounded — the same retention class as `FinancialStatement` itself (ADR-029 §8) |
| **Consistency** | AS-4 | Deterministic outcome under concurrency via monotonic evidence precedence (`available > confirmed_unavailable > no terminal state`); `available` sticky |
| **Authoritative ownership** | AS-0, AS-2 | Exactly one durable store is authoritative; all reads/writes pass through a single boundary — no direct access from multiple code paths |
| **Concurrency** | AS-4 | Two distinct guarantees: idempotency (repeat-same-outcome is safe) and deterministic conflict resolution (different concurrent outcomes never resolve by write-timing alone) |
| **Idempotency** | AS-4 | Writing the same terminal outcome repeatedly changes nothing |
| **Restart recovery** | AS-3 | No terminal state is ever written except on a definitive outcome — a crash mid-attempt leaves nothing to recover, by construction |
| **Worker recovery** | Document 36 §9.3, §14 | Execution is deliberately non-durable (in-process fire-and-forget); *state* recovery is what AS-3 provides, and it requires no reap/sweep mechanism, unlike `Job` |
| **Deployment recovery** | AS-3, Document 36 §15 | Identical to restart recovery — nothing partial is ever persisted |
| **Partial acquisition** | Document 35 §6/§16 (R8) | Statement-type-level granularity — each `(ticker, period_type, statement_type)` identity is independently readable/writable |
| **Terminal states** | Document 35 §2 | Exactly three: `not_yet_acquired`, `available`, `confirmed_unavailable` — no fourth |
| **State transitions** | AS-3, AS-4 | Only a definitive provider outcome may transition state; `available` is sticky and never downgraded by a later `confirmed_unavailable` |
| **Historical correctness** | AS-5 | `FinancialStatement` persistence must precede `acquisition_state = available` — an ordering guarantee, explicitly **not** an atomicity guarantee; a documented, accepted, safe-but-non-converged residual crash window exists |
| **Stale-state handling** | Document 35 §10/§13; ADR-029 §18 item 4 | Explicitly out of scope — no refresh/staleness mechanism is required of the provider |

No requirement above is invented — each traces to a specific,
already-ratified clause.

## 3. Repository Evidence

Reconfirmed from Document 34/35/36's own evidence, plus new evidence
gathered specifically for this decision:

- **No acquisition-state code exists anywhere in `backend/`** — no
  `FinancialStatementRepository`, no `AcquisitionStateRepository`, no
  acquisition-shaped port in `application/ports.py` (reconfirmed,
  unchanged since Document 34 §3).
- **`Job`/`JobStore`** (`domain/models.py`, `infrastructure/redis/job_store.py`)
  remains the only existing lifecycle/state-machine entity — Redis-
  resident, TTL'd, user-scoped, with a genuine in-progress state
  requiring `reap()`. Wrong shape for this role (Document 35 §2,
  Document 36 §4.3, unchanged) — not re-litigated here.
- **`backend/infrastructure/mongo/client.py`** (read directly, new for
  this decision): `create_mongo_client()` constructs a plain
  `AsyncIOMotorClient(mongo_url)` with **no explicit write-concern
  override** — meaning the driver default (acknowledged, `w:1`) applies.
  This is a concrete, previously-unstated fact relevant to §9's
  durability discussion (§14).
- **`backend/infrastructure/mongo/indexes.py`** (read directly, new):
  an existing, proven `_idx(collection, keys, unique=True, name=...)`
  helper already creates unique indexes for `users`, `sessions`,
  `companies`, `reports`, `jobs`, and others — the exact mechanism
  Document 35 §8 already cited as the pattern a future acquisition-state
  unique key would reuse. This is not a hypothetical pattern; it is
  live, working code exercised today.
- **`scripts/run.py`** (read directly, new): the local `mongod` process
  is launched as `mongod --dbpath ... --port ... --bind_ip 127.0.0.1` —
  **no `--replSet` flag anywhere.** This is a **standalone MongoDB
  instance**, not a replica set. This matters directly: MongoDB
  multi-document transactions require a replica set (or sharded
  cluster) and are **structurally unavailable** in this deployment
  topology today — not merely "not needed" (Document 35's conclusion)
  but currently **impossible** to use even if desired. This
  independently reinforces Document 35 AS-2/AS-4's single-document-only
  design from a different angle than Document 35 itself argued.
- **`docs/backend_engineering/09_Redis_Architecture.md` RA-0/RA-1**
  (cited, unchanged): Redis is never the system of record; every key is
  TTL'd or bounded — binding, disqualifying Redis from this role
  independent of any other consideration.
- **ADR-029 §8**: `FinancialStatement`'s own already-decided identity
  (`ticker + period_type + period_end + statement_type`), unique index,
  and upsert policy — the direct, already-ratified precedent for
  applying the same pattern to acquisition state.

## 4. Current-State Assessment

**No existing mechanism in this repository already serves as the
canonical acquisition-state provider.** The closest structural analog
(`Job`/`JobStore`) is the wrong shape for reasons already established
(user-scoped, streamed, genuine in-progress state) and is not proposed
for reuse. Of the two persistence *technologies* already present in
this codebase, only one (MongoDB) is even eligible against AS-0's
durability requirement — Redis is independently barred by RA-0/RA-1.
No third persistence technology exists in this repository (reconfirmed,
`backend/infrastructure/` contains only `mongo/` and `redis/`).

## 5. Candidate Providers

Exactly the technologies actually present in this codebase — no new
technology is considered, per the explicit constraint against inventing
one:

1. **MongoDB** — already used for `companies`, `filings`,
   `financial_statements` (to be), `users`, `sessions`, `reports`,
   `jobs`, and every other durable, indefinite-retention concept in this
   backend.
2. **Redis** — already used for `Job`/`EventBus`/rate-limiting — all
   explicitly TTL'd/bounded, ephemeral-by-design use cases (RA-0/RA-1).
3. **Existing persistence mechanism(s) beyond these two** — none exist
   (§3, §4).

## 6. Evaluation Matrix

| Dimension | MongoDB | Redis |
|---|---|---|
| **Durability** | Indefinite retention, matches AS-0 exactly; already the durability class for every comparable concept in this codebase | Disqualified — RA-1: every key is TTL'd or bounded, structurally incompatible with AS-0's indefinite-retention requirement |
| **Consistency** | Single-document reads/writes are strongly consistent on the primary; sufficient for AS-4's per-identity precedence rule (each identity is one document) | N/A — disqualified above |
| **Atomicity** | Single-document operations are atomic natively (no transaction needed, and — per §3's new finding — multi-document transactions are structurally unavailable in this standalone deployment anyway); AS-2/AS-4's design requires only single-document atomicity, which this provides | N/A |
| **Concurrency** | A single-document conditional update (e.g. an update-if-precedence-not-lower filter) natively expresses AS-4's monotonic precedence rule with no lock, no transaction | N/A |
| **Recovery** | Nothing to recover — AS-3 means no partial write ever exists; a crash mid-attempt simply leaves the prior document state (or its absence) untouched | Disqualified — even if durability were acceptable, RA-0 (never the system of record) independently bars this role |
| **Existing infrastructure fit** | Reuses the existing Mongo client (`infrastructure/mongo/client.py`), the existing `_idx()` unique-index pattern, and the existing repository-port convention (`application/ports.py`) — zero new infrastructure | Would require treating Redis as a system of record, directly contradicting RA-0, a binding invariant this decision does not reopen |
| **Operational complexity** | None beyond what already exists for every other collection in this database | N/A — disqualified |

## 7. Canonical Provider Recommendation

**MongoDB is the canonical acquisition-state provider.** This confirms
Document 35 §8's decision; it is not reopened or changed. The
recommendation, restated with the evidence gathered specifically for
this document:

- **Why it satisfies the ratified requirements:** every requirement in
  §2 maps directly onto a native MongoDB capability already exercised
  elsewhere in this codebase — indefinite retention (no TTL index, same
  as `companies`/`filings`), a unique compound index for identity/
  idempotency (the existing `_idx()` pattern), single-document atomic
  conditional writes for AS-4's precedence rule (no transaction needed,
  and — newly confirmed — none available in this deployment topology
  regardless), and zero recovery machinery required because AS-3 never
  produces a partial write to recover from.
- **Why Redis is rejected:** RA-0/RA-1 (binding, unchanged) — Redis is
  never the system of record and every key must be bounded/TTL'd,
  directly incompatible with AS-0's indefinite-retention requirement.
  This is not a preference; it is a standing architectural invariant
  this decision does not have authority to override.
- **Why no other technology was considered:** none exists in this
  repository, and no evidence gathered — old or new — shows a gap
  MongoDB cannot close. Introducing a new persistence technology
  (e.g. a dedicated key-value store, a separate database) would be
  solving a problem this evidence does not show exists.
- **Operational implications:** zero new infrastructure to operate —
  the same MongoDB instance, the same client construction, the same
  index-creation pattern already in production use for this codebase's
  existing collections.
- **Failure/recovery implications:** unchanged from Document 35 §7/AS-3
  and Document 36 §15 — a crash, timeout, process restart, or
  deployment restart during an in-flight acquisition attempt leaves the
  identity exactly as it was, because nothing partial is ever written.
  No reap/sweep mechanism is required, unlike `Job`.
- **Migration implications:** none — this is a net-new collection/store
  (exact name not decided here, §15), not a migration of existing data.
  No existing collection changes shape as a result of this decision.
- **Remaining risks:** §14.

## 8. Consistency/Concurrency Implications

Restated against each scenario this task names, all already resolved by
Document 35/36 and unaffected by confirming MongoDB as the provider:

| Scenario | Behavior |
|---|---|
| Duplicate acquisition requests (via the frozen `POST .../acquire`) | Idempotent — repeating a request for an already-terminal identity is a no-op read; for a `not_yet_acquired` identity, safe regardless of how many times it's requested (AS-4) |
| Concurrent requests, same identity | AS-4's monotonic precedence resolves the final state deterministically, expressible as a single-document conditional write — no lock, no transaction required, and (§3) none available in this deployment even if desired |
| Worker restart | Nothing to restart — execution is in-process/non-durable by design (Document 36 §9.3); state recovery is AS-3's job, unaffected |
| Process restart | Identical to worker restart — AS-3 |
| Deployment restart | Identical — AS-3, Document 36 §15 |
| Partial acquisition | Statement-type-level granularity (§2) means each identity's document is independent — a partial outcome across a ticker's three statement types is just three independent, individually-correct documents |
| Retry | Demand-driven via any legitimate trigger (Document 36 §5, §12) — a retry is simply another read-then-conditionally-write cycle against the same document |
| Cancellation | No cancellation mechanism exists for acquisition (Document 36 §14) — irrelevant to the provider, which only ever sees complete, definitive writes or none at all |

This is fully consistent with Document 36; nothing above introduces a
new mechanism.

## 9. Recovery Implications

Stated once, precisely: **there is nothing to recover, ever, at the
provider level.** AS-3 guarantees that a terminal state is written only
upon a fully definitive outcome — a crash, timeout, or restart at any
point before that write completes simply means the write never
happened, and the document remains exactly as it was. This is
categorically different from `Job`'s recovery story
(`JobStore.reap()`), which exists specifically because `Job` *does*
have a genuine in-progress state that can be orphaned. The
acquisition-state provider has no analogous state to orphan, so it
needs no analogous recovery mechanism — confirmed, not newly designed,
by this document.

## 10. Security Implications

- **Resource ownership:** unaffected — acquisition state is shared-
  corpus data with no per-user ownership dimension, identical
  classification to `companies`/`filings`/`financial_statements`
  (`08` RI-5, `10` SI-1, unchanged).
- **Authorization boundaries:** the provider is accessed only through
  the application-layer boundary (AS-2) — never directly from an
  endpoint handler. Neither `GET /financials` nor
  `POST .../acquire` can use this provider to bypass the other's
  authorization, because neither endpoint talks to the provider
  directly; both go through the same shared use case (Document 36 §6).
- **Cache-ownership invariant (SI-1):** unaffected — this provider adds
  no new caching layer and does not touch Redis.
- **Tenant/user isolation:** not applicable — there is no tenant
  dimension on this data (Document 33 §7, unchanged).

## 11. Observability Implications

Reuses M6 exactly, per Document 36 §17-18 — not modified here:

- **State-transition metrics:** the acquisition-attempt outcome counter
  Document 36 §18 already specifies (`acquisition_request_total{outcome}`-
  style, following the `llm_calls_total` labeled-`Counter` convention)
  covers this; no separate provider-specific metric is introduced.
- **Tracing:** the existing `get_tracer()` helper, wrapping the
  provider's read/write calls exactly as it already wraps other Mongo
  operations elsewhere in this codebase — no new tracing mechanism.
- **Structured logging:** server-side only, correlated by the
  acquisition identity itself (Document 36 §17 — no new ID scheme).
- **Correlation/job identifiers:** unchanged — acquisition state is
  explicitly not a `Job`, carries no `job_id`, and none is introduced by
  this decision.
- **Failure visibility:** a failed provider write (e.g. a transient
  Mongo error) is itself covered by the existing `InfrastructureError`
  → 502 convention at the application layer (Document 33 §5/§8,
  unchanged) — no new failure-visibility mechanism is required.

## 12. API Implications

- **`POST /companies/{ticker}/financials/acquire`** (Document 33
  Amendment, frozen): the endpoint's response (§5 there — `requested`/
  `available`/`confirmed_unavailable`/`mixed`) is computed by a
  **synchronous point-read** of this provider, by unique identity key,
  for the ≤3 relevant statement-type identities — a trivial, already-
  supported MongoDB operation requiring no schema beyond the identity
  key and the state field. The endpoint's response contract does not
  require or imply any change to this provider's design.
- **`GET /companies/{ticker}/financials`** (Document 33 §1-§10, frozen,
  eventual): identical read pattern — `acquisition_state` per
  `statement_type` is a direct read from this provider, keyed the same
  way.
- **Neither contract is modified by this decision.** Both were already
  designed against exactly this provider shape (Document 33 §4's
  "Contract Dependency — Acquisition-State Provider" section
  anticipated precisely this).

## 13. Rejected Alternatives

- **Redis as the canonical provider** — rejected; RA-0/RA-1, unchanged,
  disqualify it independent of any other factor (§6, §7).
- **A new/different persistence technology** (a dedicated KV store, a
  separate database, an external service) — rejected; no evidence from
  either the original Document 35 review or this document's fresh
  repository inspection shows a gap MongoDB cannot close, and
  introducing one would contradict this whole document chain's
  "smallest architecture that remains correct" discipline.
- **Multi-document Mongo transactions** — rejected; not required by
  AS-2/AS-4's single-document design, and — newly confirmed here (§3) —
  **structurally unavailable** in this deployment's standalone `mongod`
  topology regardless of preference.
- **Reusing `Job`/`JobStore` as the provider** — rejected, unchanged
  from Document 35 §2 / Document 36 §4.3: wrong shape (user-scoped,
  streamed, has a genuine in-progress state this model deliberately
  lacks).

## 14. Risks

| Risk | Assessment |
|---|---|
| **Default Mongo write concern is acknowledged (`w:1`), not majority** — newly observed (§3), not previously stated anywhere in this document chain | `create_mongo_client()` sets no explicit write concern. At `w:1`, a write acknowledged by the primary could theoretically be lost in a narrow primary-failover window before replication catches up. This is a pre-existing characteristic of *every* collection in this database today (`companies`, `filings`, `financial_statements`, `jobs`, etc.) — not something unique to acquisition state, and not something this decision introduces. Flagged as an implementation-time configuration question (whether to request a stronger write concern for this specific collection), not decided here |
| Standalone (non-replica-set) MongoDB in the current deployment (§3) | Confirms transactions aren't available, reinforcing rather than weakening the single-document design (§13). Also means there is currently no replica-set-based failover at all for *any* collection — a pre-existing operational characteristic of this deployment, not a new risk this decision creates |
| Exact collection name, field names, and index definition remain undecided | Correctly deferred to implementation, per Document 35 §8's own conclusion — not an architecture ambiguity |
| AS-5's enforcement mechanism (how the two writes are sequenced in code) remains undecided | Unchanged Engineering Question, Document 35 §13 |

**On `w:1` and the standalone topology, stated plainly so neither finding
is misread as a provider-selection problem:** the current MongoDB client
uses the existing acknowledged write concern configuration (`w:1`), and
the current local deployment is a standalone MongoDB topology. These are
pre-existing infrastructure characteristics, not properties introduced
by the acquisition-state provider decision. The provider decision
therefore does not prescribe a stronger write concern or a replica-set
topology. Whether production hardening requires stronger
acknowledgement/failover guarantees is an operational/infrastructure
decision that must be resolved before production hardening, but it does
not invalidate MongoDB as the canonical acquisition-state provider, does
not require MongoDB transactions, and does not change AS-2/AS-4. No
majority write concern is currently configured, and no replica set
currently exists — this table does not claim otherwise.

## 15. Remaining Dependencies

- This document's own CTO approval.
- Document 35's own still-open implementation-time items (exact schema/
  index naming, AS-5's write-sequencing mechanism) — unchanged, not
  resolved here since they are implementation detail, not architecture.
- Document 36's own remaining Engineering Questions (timeout duration,
  backoff policy, client-polling cadence, whether a scheduler is ever
  built) — unchanged, orthogonal to the provider decision.
- Whether a stronger write concern is warranted for this specific
  collection (§14) — an implementation-time operational decision, not
  an architecture blocker.

## 16. Implementation Prerequisites

1. Canonical acquisition-state provider — **resolved: MongoDB**,
   confirming Document 35 §8 against the complete ratified stack and
   fresh repository evidence (§3, §7).
2. Consistency/concurrency behavior — **resolved**, unchanged from
   Document 35 AS-4 (§8).
3. Recovery behavior — **resolved**, unchanged from Document 35 AS-3
   (§9).
4. Security — **resolved**, no new trust boundary (§10).
5. Observability — **resolved**, reuses M6 unchanged (§11).
6. API compatibility — **resolved**, both `GET` and the frozen `POST`
   contract already anticipate exactly this provider shape (§12).

**Governance status at time of writing:**

| Document | Status |
|---|---|
| Document 35 (Acquisition-State Architecture Decision) | 🟢 RATIFIED |
| Document 36 (Acquisition Orchestration Architecture) | 🟢 RATIFIED |
| Document 37 (Financials Acquisition Request Endpoint Proposal) | 🟢 CTO APPROVED |
| Document 33 `POST .../acquire` API contract | 🟢 CTO APPROVED |
| Document 38 (this document) | 🟢 CTO RATIFIED (see Governance Addendum) |
| M8 implementation | 🔴 BLOCKED |

The POST API contract (Document 33) is tracked independently and has
already received final CTO approval. This document does not modify that
contract or authorize its implementation. **What remains before M8
implementation can begin** is completion of any explicitly retained
implementation-time questions from Documents 35 and 36 (§15),
confirmation that the canonical provider dependency is available to the
implementation, and separate implementation authorization. Ratifying
this document is not itself an implementation authorization. Nothing in
this document authorizes implementation.

## Governance Addendum — CTO Ratification Record

- **Date:** 2026-08-11
- **Decision:** CTO RATIFIED
- **Scope:** the canonical acquisition-state provider decision in this
  document only — MongoDB as canonical provider (§7), Redis rejection
  (§7, §13), the `w:1`/standalone-topology clarification (§14), and all
  other sections as written. Nothing about this ratification reopens,
  rewrites, or reinterprets that content, and it does not itself amend
  Documents 33, 35, 36, or 37.
- **Implementation:** remains 🔴 **BLOCKED.** Ratifying this document is
  not itself an implementation authorization.
- **Dependency, not superseded by this ratification:** this document's
  own conclusion (§7) rests on Document 35 §8's acquisition-state model
  (AS-0 through AS-5). Document 35's own text does not yet contain an
  explicit CTO ratification record of its own — this addendum ratifies
  *this document's provider recommendation*, not Document 35 itself. See
  [`39_M8_Implementation_Readiness_Assessment.md`](39_M8_Implementation_Readiness_Assessment.md)
  for the current governance-readiness picture across all M8 documents.

---

*Companion documents:
[`35_M8_Acquisition_State_Architecture_Decision.md`](35_M8_Acquisition_State_Architecture_Decision.md) §8 (the original provider decision this document confirms, unmodified) ·
[`36_M8_Acquisition_Orchestration_Architecture.md`](36_M8_Acquisition_Orchestration_Architecture.md) (ratified, unmodified) ·
[`33_M8_Financials_API_Contract_Review.md`](33_M8_Financials_API_Contract_Review.md) (frozen `GET` contract + complete `POST` amendment, unmodified) ·
[`37_Document33_Amendment_Financials_Acquisition_Request_Endpoint.md`](37_Document33_Amendment_Financials_Acquisition_Request_Endpoint.md) (unmodified) ·
`backend/infrastructure/mongo/client.py`, `backend/infrastructure/mongo/indexes.py`,
`scripts/run.py`, `docs/backend_engineering/09_Redis_Architecture.md` RA-0/RA-1
(repository evidence cited above, unmodified).*

*This is a CTO-ratified architecture-decision artifact (see Governance
Addendum). It does not itself authorize implementation, does not create
a schema, repository, or provider class, and does not modify any API
contract.*

---

## CANONICAL PROVIDER DECISION: CTO RATIFIED. M8 implementation remains BLOCKED pending the governance sequence recorded above.
