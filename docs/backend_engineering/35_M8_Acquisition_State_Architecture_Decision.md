# M8 Acquisition-State Architecture Decision

**Status:** 🟢 **CTO RATIFIED.** See the Governance Addendum near the end
of this document for the ratification record. This document resolves the
seven required decisions Document 34 §7.A identified, at the
architecture level only. No backend, frontend, schema, migration, or
dependency file was created or modified to produce it.

**Architecture:** 🟢 Ratified.
**Implementation:** 🔴 Still blocked — ratifying this document is not
itself an implementation authorization; see the Governance Addendum.

**Date:** 2026-08-10 · **Ratified:** 2026-08-12
**Answers to:** [`34_M8_Acquisition_State_Architecture_Risk_Review.md`](34_M8_Acquisition_State_Architecture_Risk_Review.md)
§7.A's seven required decisions and §9's implementation gate.
**Does not modify:** `32_M8_Pre_Implementation_Decision_Pack.md`,
`33_M8_Financials_API_Contract_Review.md`,
`34_M8_Acquisition_State_Architecture_Risk_Review.md`, any production
code, any test, any schema, any migration.
**Does not:** implement M8, implement the financials endpoint, modify
frontend code, create a MongoDB schema, create Redis keys, implement a
repository, implement acquisition orchestration, or modify Document
33's API contract.

> **Revision, Round 2 — CTO-directed concurrency and persistence
> corrections (2026-08-10):** replaced non-deterministic
> "latest-outcome-wins" concurrency semantics with an explicit
> deterministic outcome-precedence invariant; added the
> FinancialStatement-before-`available` persistence-ordering invariant;
> corrected transient-failure semantics to preserve the previous
> terminal state; and corrected the final document status to indicate
> CTO ratification rather than API contract review.
>
> **Revision, Round 3 — CTO-directed acquisition-state semantic
> clarification (2026-08-10):** clarified that acquisition state
> represents the strongest known durable terminal acquisition outcome,
> not the existence of every acquisition attempt; explicitly documented
> sticky-`available` semantics implied by AS-4's evidence precedence;
> and corrected the orchestration-consumer wording to distinguish
> durable terminal state from transient attempt history.

---

## 1. Problem Statement

Document 33 froze an API contract whose response exposes exactly three
acquisition states (`not_yet_acquired` / `available` /
`confirmed_unavailable`) per statement type. Document 34 confirmed, by
direct repository inspection, that **no mechanism capable of producing
those three states exists anywhere in this codebase** — and registered
twelve risks (R1–R12), five of which (R1, R3, R5, R10, R12) require an
explicit architecture decision before M8 implementation can begin.

This document makes that decision, at the architecture level: what the
acquisition-state concept is, who owns it, at what granularity, under
what failure semantics, and on what store — without writing the
repository, the schema, the orchestration, or the endpoint itself.

## 2. Repository Evidence

Carried forward from Document 34 §3, not re-derived:

- No `acquisition`-related code, no `FinancialStatement` model, and no
  acquisition-state-shaped port exist anywhere in `backend/`.
- The only existing lifecycle/state-machine entity is `Job`/`JobStatus`
  (`backend/domain/models.py`) — Redis-resident, TTL'd, request-scoped,
  with a genuine in-progress state requiring a `reap()`/restart-sweep
  recovery mechanism. Not a fit for a durable, shared-corpus concept
  (§6 below).
- `backend/application/ports.py` establishes the `typing.Protocol`
  port convention this codebase already uses for exactly this kind of
  boundary (`JobStore`, `ChunkRepository`, `ReportLikeRepository`).
- `backend/agents/ingest.py`'s provider-failure handling collapses every
  failure mode into a single `None` return — confirmed evidence of the
  anti-pattern R5 must not repeat, not a precedent to reuse.
- `docs/backend_engineering/09_Redis_Architecture.md` RA-0/RA-1: Redis is
  never the system of record; every key is TTL'd or bounded — a binding
  constraint on §6's store evaluation.
- ADR-029 §6.4/§8: `FinancialStatement`'s own identity
  (`ticker + period_type + period_end + statement_type`), its unique
  index, and its latest-value-wins upsert policy are already decided and
  are reused here as direct precedent, not reinvented.
- No background job runner, worker, scheduler, or queue exists anywhere
  in `backend/`.

## 3. R1 Resolution — Why Acquisition State Is Required

**What state must exist:** **acquisition state is the durable record of
the strongest known terminal acquisition outcome for an acquisition
identity** (§5's granularity decision fixes the identity as
`ticker + period_type + statement_type`). It does not record transient
attempts, in-progress work, or acquisition-attempt history — only which
of the two terminal outcomes (or neither) currently holds, per §4's
invariants. This is not "whether AlphaScribe ever attempted acquisition"
— a transient/inconclusive attempt leaves no trace in this record at all
(AS-3) — it is strictly "what is the strongest durable evidence obtained
so far."

**Who consumes it:**
1. `GET /companies/{ticker}/financials` (Document 33) — the primary,
   explicit consumer; it must report `acquisition_state` without
   inferring it from anything else.
2. A future acquisition-orchestration component (not designed here) —
   may use acquisition state to determine which acquisition identities
   already have a durable terminal outcome, so it can avoid redundant
   acquisition where appropriate. It cannot use acquisition state to
   learn whether a transient attempt was ever made, or how many times —
   that information does not exist in this record by design (§4, AS-3);
   retry/backoff decision-making is a separate future orchestration
   concern (§13), not something this record supports.
3. No other consumer is currently evidenced. An internal ops/observability
   view is plausible future value, not a current requirement — not
   designed here.

**What decisions depend on it:** the entire `acquisition_state` field in
Document 33's response envelope has no legitimate source without this;
and any future orchestrator's "does a durable terminal outcome already
exist for this identity" check depends on reading it first.

**What failures become ambiguous without it:** exactly the collapse
Document 32 §4 and Document 33 §4/§5 already forbid — "never attempted"
and "attempted, provider confirmed nothing" (`confirmed_unavailable`)
become indistinguishable from a missing `FinancialStatement` document,
and from each other, without a durable record of the strongest known
terminal outcome. A transient, inconclusive attempt is a separate
matter: by design it never becomes part of that record at all (AS-3),
so there is nothing about it to keep from being ambiguous — it simply
leaves whatever durable state already existed unchanged. Without an
explicit, separately-owned record, the read endpoint cannot honor its
own frozen contract without either violating it (inferring from
absence) or permanently returning `not_yet_acquired` for every ticker
(functionally not a working endpoint).

No storage technology is selected in this section — that is §6, after
the invariant (§4) and granularity (§5) are settled, per the same
ordering this task specified.

## 4. R3 — The Canonical Acquisition-State Invariant

Stated as a numbered invariant set, in the same style as this
codebase's existing binding invariants (e.g. `09` RA-0/RA-1), so it is
independently checkable rather than a prose aspiration:

- **AS-0 (Single source of truth).** Acquisition state for a given
  identity is held authoritatively by exactly one durable store. No
  other system — a cache, an in-memory structure, Redis, or the
  `FinancialStatement` collection itself — may be treated as
  authoritative for it.
- **AS-1 (Never inferred from `FinancialStatement`).** Carried forward
  unchanged from Document 32 §4 / Document 33 §4-§5: absence of a
  `FinancialStatement` document never determines acquisition state, in
  either direction.
- **AS-2 (Single boundary).** All reads and writes of acquisition state
  pass through one repository-shaped boundary. No code path queries or
  mutates the underlying store directly — this is what prevents
  competing representations, not a locking mechanism.
- **AS-3 (Terminal-write only).** A terminal state (`available` or
  `confirmed_unavailable`) is written only upon a definitive provider
  outcome (§5). A transient or inconclusive attempt writes nothing.
  This resolves Document 34 R12: since no in-progress state is ever
  externally observable and no terminal state is ever written
  prematurely, an interrupted attempt (crash, timeout, restart) simply
  leaves the identity as it was — safely re-attemptable, never stuck,
  never wrong. This applies identically regardless of what the identity
  previously held — no state, `available`, or `confirmed_unavailable` —
  a transient failure never downgrades or erases an existing terminal
  state (§5).
- **AS-4 (Idempotency and deterministic concurrency).** Two distinct
  guarantees, not one:
  - *Idempotency:* writing the same valid outcome for an identity that
    already holds it is safe — repeating a write changes nothing.
  - *Concurrency correctness:* idempotency alone does not make
    concurrent writes safe. Two individually-valid, *different*
    definitive outcomes can race for the same identity — for example,
    one call returns usable statement data while a second, concurrent
    call for the same identity returns an explicitly-empty result (a
    plausible provider inconsistency, not a hypothetical — Document 31
    §9 already documents that yfinance can return an empty result for a
    combination without that being a permanent fact). **Concurrent
    definitive acquisition outcomes for the same acquisition identity
    MUST NOT resolve solely according to database write timing.**

  **v1 conflict-resolution rule — monotonic evidence precedence:**
  ```
  available  >  confirmed_unavailable  >  no terminal state
  ```
  applied as:
  - existing `available` + concurrent `confirmed_unavailable` → `available`
  - existing `confirmed_unavailable` + concurrent `available` → `available`
  - no existing state + concurrent `available` → `available`
  - no existing state + concurrent `confirmed_unavailable` → `confirmed_unavailable`

  **`available` is intentionally sticky once established.** A later or
  concurrent `confirmed_unavailable` outcome does not downgrade an
  identity that already has `available` state. This reflects the
  architecture's interpretation of acquisition state as the strongest
  durable evidence obtained for the identity, rather than the latest
  provider observation:

  - **Case A:** `available` + later `confirmed_unavailable` → `available`.
  - **Case B:** `confirmed_unavailable` + later `available` → `available`.
  - **Case C:** no terminal state + `available` → `available`.
  - **Case D:** no terminal state + `confirmed_unavailable` → `confirmed_unavailable`.

  This behavior is intentional architecture — it is **not** an accidental
  consequence of MongoDB update ordering. Acquisition state represents
  *strongest known durable acquisition evidence*, not *latest provider
  observation*; that distinction is what makes `available` sticky and
  `confirmed_unavailable` upgradeable, rather than the two simply
  overwriting each other on whichever call happens to land last. This
  correction does not introduce refresh/staleness architecture, provider
  freshness semantics, timestamps, or new states — refresh/staleness
  remains outside this decision's scope, unchanged from §10/§13.

  **Why this ordering, and not the reverse:** `available` is positive
  evidence — the provider actually returned usable statement data, which
  is not something a transient glitch can fabricate. `confirmed_unavailable`
  is weaker evidence — it establishes only that *one particular call*
  returned nothing; Document 31 §9's RELIANCE.NS finding is itself
  evidence that an empty result can be a per-call provider quirk rather
  than a permanent fact about the ticker, and nothing in Document 31 or
  Document 32 §4 rules out a second call to the *same* identity later
  succeeding. Letting a later or concurrent empty response overwrite
  already-observed successful data would silently regress a client from
  seeing real financial data to seeing none — a strictly worse failure
  mode than the reverse (briefly under-reporting a negative result is
  safe; erasing known-good data is not). This rule also makes the final
  state independent of write order by construction: whichever write
  physically lands first, the same precedence comparison always produces
  the same result — this is what "deterministic," not merely
  "idempotent," means here (resolves R6).

  **This is consistent with, and does not contradict, Document 33's
  contract, Document 34's risk analysis, or §5's outcome semantics
  below** — none of them specify a resolution for this specific race;
  this rule fills a genuine gap, it does not override a prior decision.

  **No distributed lock, worker coordination system, or multi-document
  Mongo transaction is required or introduced.** The rule above is a
  value-comparison applied at write time; a single-document conditional
  write (an update that only proceeds when the new outcome's precedence
  is not lower than the identity's current state) is sufficient to
  enforce it using ordinary single-document Mongo semantics — no new
  infrastructure class. The exact update mechanics are an
  implementation-level decision; what this document fixes is the
  *outcome* the mechanism must produce, which is what makes the final
  state deterministic regardless of implementation.
- **AS-5 (Available-state persistence ordering).** `available` MUST NOT
  become the canonical acquisition state until the corresponding
  `FinancialStatement` persistence operation has successfully completed.
  Required sequence: provider success → persist `FinancialStatement` →
  `FinancialStatement` persistence succeeds → persist
  `acquisition_state = available`. If `FinancialStatement` persistence
  fails, `acquisition_state = available` MUST NOT be persisted — the
  acquisition state remains at its previous value (an application of
  AS-3: nothing less than a fully definitive, fully persisted success
  qualifies as the terminal outcome).

  **Why this is needed:** `AcquisitionStateRepository` and
  `FinancialStatementRepository` are deliberately separate boundaries
  (§9; Document 32 §4). Without an explicit ordering, the sequence
  "persist `available` → `FinancialStatement` persistence fails" is
  possible, producing a false positive: the frozen API contract would
  report `available` for data that doesn't actually exist. AS-5 rules
  this out by fixing the order, not by merging the two boundaries.

  **Residual crash window — explicitly acknowledged, not ignored:** if
  `FinancialStatement` persistence succeeds but the process crashes
  before the subsequent `acquisition_state = available` write occurs,
  the resulting state is temporarily: the `FinancialStatement` document
  exists, but the acquisition state remains absent or at its previous
  value (e.g. still `not_yet_acquired`). **This is acceptable for v1
  specifically because it produces a conservative state, never a false
  `available`** — the read endpoint under-reports (shows
  `not_yet_acquired` for data that, in fact, already exists) rather than
  over-reports. Under-reporting is the safe direction; AS-5 exists
  precisely to prevent the opposite. Reconciling this residual window
  (e.g. a future check that finds an orphaned `FinancialStatement` with
  no matching terminal state) is left to future orchestration/
  reconciliation work — not designed here, consistent with orchestration
  remaining out of scope (§7). No Mongo multi-document transaction,
  two-phase commit, saga, or event-sourcing mechanism is introduced to
  close this window — no repository evidence shows atomicity across the
  two persistence operations is mandatory for v1, only that the
  *ordering* is.

**How consumers determine current state:** by reading through AS-2's
boundary only. This closes R3 and R1 together — the invariant set
defines what the concept *is* independent of which store implements it.

## 5. R5 — Provider Outcome Semantics

Each outcome maps to exactly one row. "No terminal write" means AS-3
applies: nothing is persisted, and the identity remains whatever it was
before the attempt (typically `not_yet_acquired`).

| Outcome | Acquisition state written | Persistence allowed | Retry allowed | User-visible | Terminal? |
|---|---|---|---|---|---|
| Success, statement data returned | `available` — written only *after* `FinancialStatement` persistence succeeds (AS-5) | Yes — `FinancialStatement` first, then state; if `FinancialStatement` persistence fails, no state write occurs and the identity remains at its previous value (AS-5) | No (done) | Yes | Yes |
| Success, provider explicitly returned no data (empty result, no exception — the RELIANCE.NS `.quarterly_cashflow` precedent, Document 31 §9) | `confirmed_unavailable` — **unless the identity already holds `available`, in which case AS-4's sticky-`available` rule means this outcome never overwrites it** (Case A) | Yes — state only, and only when not superseded by an existing `available` (AS-4) | Not automatically; a deliberate re-check is a refresh-policy question, out of scope (ADR-029 §18 item 4) | Yes | Yes |
| Partial data (fewer periods returned than might exist) | `available` (same AS-5 ordering as the first row) | Yes | No | Yes — whatever was returned | Yes |
| Provider timeout | *(none — previous state, if any, preserved, AS-3)* | No terminal write (AS-3) | Yes | No new signal — see corrected transient-failure semantics below | No |
| Network failure | *(none — previous state, if any, preserved)* | No terminal write | Yes | No new signal — see below | No |
| Provider rate limiting | *(none — previous state, if any, preserved)* | No terminal write | Yes, after backoff (backoff mechanism is orchestration, out of scope) | No new signal — see below | No |
| Provider exception (unclassified) | *(none — previous state, if any, preserved)* | No terminal write | Yes | No new signal — see below | No |
| Invalid/malformed provider response | *(none — previous state, if any, preserved)* | No terminal write | Yes | No new signal — see below | No |
| Stale (already-`available` data whose freshness is in question) | *(not a new outcome — `available` unchanged)* | N/A | N/A | Refresh/staleness signaling explicitly out of scope (ADR-029 §18 item 4), unchanged here | N/A |
| "Retryable failure" | *(category, not a distinct outcome — covers every row above with no terminal write)* | | | | |
| "Non-retryable failure" | **No repository evidence supports a distinct non-retryable-failure state beyond `confirmed_unavailable`.** Stated explicitly per this task's instruction not to invent an answer: nothing in Document 31's provider evidence distinguishes "provider says this ticker categorically doesn't exist" from "provider returned empty for this statement/period combination." Until such evidence exists, both collapse to the rows above (`confirmed_unavailable` for a definitive empty result; no terminal write for anything else). | | | | |

**Transient-failure semantics (corrected).** A transient or inconclusive
acquisition attempt performs no terminal-state write and therefore
**preserves the identity's previous acquisition state, if one exists** —
it does not universally become `not_yet_acquired`:

- *No previous state* + timeout → no state / `not_yet_acquired`.
- *Previous state = `available`* + a later refresh attempt times out →
  `available` remains.
- *Previous state = `confirmed_unavailable`* + a retry times out →
  `confirmed_unavailable` remains.

This applies to every "no terminal write" row above (timeout, network
failure, rate limiting, exception, malformed response): none of them
ever downgrades or erases an existing terminal state. "Indistinguishable
from never attempted" is only true in the specific case where no prior
state existed. No fourth public `acquisition_state` is introduced by
this clarification, and Document 33 is unchanged.

**"Partial data within one statement-type fetch" is not a distinct
outcome** given §5's (below) statement-type-level granularity decision:
a fetch returns whatever periods the provider returns in one call, and
that is simply `available` — there is no independently-known "expected
period count" to compare against, so nothing can be flagged as
incomplete relative to it.

**Fourth public state rejected.** No outcome above requires a fourth
client-visible `acquisition_state` value — Document 33's three-state
contract is sufficient and is not reopened.

**Internal attempt history (§7.A.7 of Document 34) — resolved as not
required for v1.** The only functional need for a richer internal
history (e.g. "attempted 3 times, last failure was a timeout") is
retry/backoff decision-making by a future orchestrator — which is
itself out of scope (§7 below). The terminal-state record alone (AS-0
through AS-4) is sufficient for everything the acquisition-state
architecture itself needs to do. If a future orchestration design
requires attempt history for backoff purposes, that is that design's
own decision to make, not a prerequisite of this one.

## 6. R10 — Granularity Decision

**Recommended and adopted for this proposal: statement-type-level** —
identity = `(ticker, period_type, statement_type)`.

| Criterion | Company-level | Period-level | **Statement-type-level (recommended)** |
|---|---|---|---|
| Correctness vs. Document 33's frozen response shape | Wrong — collapses independently-failable statement types into one flag, contradicting §3.2 Example 2 (income available, cash flow confirmed-unavailable) | Requires an aggregation rule to collapse multiple periods into Document 33's single per-statement-type field — **that rule does not exist and this document does not invent it** | Matches exactly — no aggregation, no contract change |
| Matches a real, independently-triggerable unit of provider work | No | No — yfinance exposes no way to fetch "just one period" independently of the rest; one `.financials`-style call returns all periods for a statement type atomically (ADR-029 §6) | Yes — one call boundary = one acquisition attempt = one state |
| Partial acquisition (R8) | Cannot represent | Representable but with no defined aggregation rule to surface it | Representable directly, already demonstrated in Document 33 §3.2 |
| Provider failures | N/A (too coarse to matter) | Ambiguous — does one period's failure block the others? Undefined | Unambiguous — the call either succeeds or it doesn't, for the whole statement type |
| Historical data | N/A | Naturally fits period identity, but at the cost above | Naturally fits — a successful call populates however many periods the provider returns, in one write |
| Concurrency | Trivially small (1/ticker) but wrong grain | Larger surface (periods × statement types × period types) | Small, bounded: 3 statement types × 2 period types = 6 identities per ticker |
| Recovery (AS-3) | N/A | Same invariant applies, more records to reason about | Same invariant applies, fewer records — simpler to verify |
| Frontend requirements | Fails the frozen `StatementTable` Partial Failure state | Satisfies it, at added cost | Satisfies it directly, matching what's already shipped in the design spec |
| Storage complexity | Minimal but wrong | Higher (up to 5-7× more records per ticker, per Document 31's observed period counts) | Minimal — 6 records per ticker |
| Future extensibility | N/A | Extends by period, which isn't how the provider or the API vary | Extends cleanly — a new statement type is one more identity, matching how ADR-029 §6.5 already scopes statement types |

**Company-level is rejected outright** — it structurally cannot satisfy
Document 33's already-frozen partial-failure behavior. **Period-level is
rejected** — not because it is impossible, but because it requires
inventing an aggregation rule this document has no evidence to define,
and it doesn't correspond to any real, independently-executable
provider operation. **Statement-type-level is adopted** — it requires no
aggregation rule, matches the real provider call boundary, and requires
no change to Document 33.

This resolves R10 definitively: the granularity mismatch Document 34
flagged between Document 32 §4's wording and Document 33's response
shape is closed by choosing the grain Document 33 already assumes.

## 7. R12 — Persistence & Recovery Invariant

Restated from §4's AS-3/AS-4, applied explicitly to each failure
scenario this task asked to be addressed:

| Scenario | What must survive | Guarantee |
|---|---|---|
| Process restart (mid-attempt) | Nothing needs to survive — AS-3 means nothing was written yet | Identity remains at its pre-attempt state; safely re-attemptable |
| Worker/orchestrator restart | Same as above | Same guarantee — no orchestrator-specific recovery logic is required by the *state* architecture itself |
| Provider failure (any kind, §5) | Nothing | No terminal write occurs (AS-3) |
| Partial acquisition (one statement type succeeds, a concurrent one for the same ticker fails) | Each identity's own terminal write, independently | Statement-type-level granularity (§6) means these are already independent identities — no cross-identity coordination is needed |
| Retry | The prior state, if any | A retry after a non-terminal outcome finds the identity unchanged and may safely attempt again; a retry after a terminal outcome is a refresh question, out of scope |
| Duplicate concurrent requests for the same identity, same outcome | The repeated outcome | AS-4's idempotency guarantee — no corruption, no lock required |
| Concurrent requests for the same identity, *different* outcomes (e.g. one succeeds, one returns empty) | Deterministically the higher-precedence outcome, regardless of write order | AS-4's concurrency-correctness guarantee (monotonic evidence precedence: `available` > `confirmed_unavailable` > no terminal state) — not decided by write timing, no lock required |
| Concurrent acquisition (two different identities, same ticker) | Independent per-identity writes | No shared mutable state between them at this grain (§6) |
| Deployment restart | Nothing in-flight | Same as process restart — AS-3 means there is never partial/corrupt state to recover from |
| Stale/incomplete state | N/A | "Incomplete" is not a representable state under this model (AS-3) — an identity is either untouched or holds a complete, valid terminal outcome; there is no third, partially-written condition to recover from |

**What must survive process failure, stated once:** nothing beyond the
last successfully-written terminal state, because AS-3 guarantees
nothing else is ever written. This is a deliberately weaker (and
cheaper) guarantee than the `Job`/`JobStore` `reap()` pattern provides —
and correctly so, because that pattern exists only to recover a genuine
in-progress state, which this model does not have (§4, AS-3).

## 8. Storage Evaluation

Evaluated only now, after §4–§7 fixed what is required of a store — not
before, per this task's explicit ordering.

**Requirements derived from §4–§7:** durable (indefinite retention, not
TTL'd — AS-0, matching ADR-029 §8's retention policy for
`FinancialStatement` itself); supports a single-document conditional
write expressing AS-4's precedence rule (not merely an unconditional
idempotent upsert — idempotency alone does not give deterministic
concurrency, §4); requires no distributed lock or coordination primitive
(AS-4); requires no in-progress-state recovery machinery (AS-3); and,
separately, supports the write-ordering AS-5 requires between
`FinancialStatement` and acquisition-state persistence.

| Store | Durability | Recovery | Consistency | Concurrency | Operational complexity | Verdict |
|---|---|---|---|---|---|---|
| **Redis** | **Disqualified.** `09` RA-0/RA-1 (binding, already cited in Document 34): Redis is never the system of record; every key is TTL'd or bounded. Acquisition state must be indefinite, per AS-0 — a bounded/TTL'd store cannot serve as the sole authoritative source for it | N/A — disqualified above | N/A | N/A | N/A | **Rejected on an existing, binding architectural invariant — not by default preference against Redis** |
| **MongoDB** | Already the durable, indefinite-retention store for every comparable shared-corpus concept in this codebase (`companies`, `filings`, and `financial_statements` itself, per ADR-029 §8) | A single-document conditional write on a unique key is a native, already-used Mongo pattern (identical in shape to ADR-029 §8's `FinancialStatement` unique index) — no additional recovery mechanism needed, consistent with §7's finding that none is required | Single-document conditional writes give exactly the single-writer-per-identity guarantee AS-2 requires, with no multi-document transaction needed (each identity is independent, §6) | AS-4's precedence rule is expressible as an ordinary single-document conditional update — no lock, no transaction; a losing concurrent write is simply rejected or overwritten deterministically, never merged or corrupted | Zero new infrastructure — reuses the existing Mongo client, existing repository-port convention (`application/ports.py`) | **Selected.** The only currently approved persistence mechanism in this stack that satisfies the identified v1 requirements — the requirement itself, not habit, is what selects it |
| **Other existing persistence mechanisms** | None exist beyond Mongo and Redis (`backend/infrastructure/` confirmed in Document 34 §3 — no third persistent store anywhere in this codebase) | — | — | — | — | No third option to evaluate |

**Mongo is not assumed because it is already part of the stack** — it
is selected because AS-0 (durability) is a hard requirement this
document derived independently in §4, and Mongo is the only store in
this codebase's approved architecture that satisfies it; Redis is
independently disqualified by a pre-existing, binding invariant (RA-0),
not by elimination of convenience.

No collection name, field name, or index is specified — §4's invariants
and §6's granularity are sufficient to constrain an implementation
without naming one.

## 9. Recommended Architecture Boundaries (conceptual only)

Matching the level of detail ADR-029 §5 already used for
`FinancialStatementRepository` (shape, not code):

- **Domain concept:** an acquisition-state value with the three states
  Document 32 §4 already named, keyed by the §6 identity. Not a class,
  not a file — a concept.
- **Application responsibility:** a repository-shaped boundary (AS-2),
  separate from `FinancialStatementRepository`, following the existing
  `typing.Protocol` convention in `application/ports.py`. Minimum
  conceptual surface, mirroring ADR-029 §5's "minimum v1 repository
  surface" discipline: read one identity's state; write a terminal
  state for one identity (idempotently and deterministically, AS-4).
  Nothing beyond that is justified by §3-§7's decisions.
- **Persistence responsibility:** a Mongo-backed adapter behind that
  boundary (§8) — not designed here beyond "Mongo, unique-key upsert."
- **Provider boundary:** unchanged. Wherever a future orchestrator calls
  yfinance, that call site is unaffected by this document and is not
  designed here.
- **Acquisition-state boundary:** deliberately separate from
  `FinancialStatementRepository` (Document 32 §4's `FinancialStatement
  data ≠ Acquisition lifecycle state`), even though both may share the
  same Mongo database and the same general repository convention.

No concrete interface, method signature, or schema is finalized — the
above is a boundary description, consistent with this task's
constraint.

## 10. API Implications

`GET /companies/{ticker}/financials` (Document 33) is **not modified**
by this decision:

- **What the API needs to know:** exactly the three states, at
  statement-type granularity (§6) — which is precisely the shape
  Document 33's `statements.<type>.acquisition_state` field already
  has. No new field, no schema change.
- **Can it distinguish unavailable vs. not-yet-acquired?** Yes — that is
  the entire purpose of AS-0–AS-4; this was previously impossible only
  because no source existed to answer it (R1), not because Document
  33's contract was incapable of expressing it.
- **Is partial data representable?** Yes, at the statement-type grain,
  exactly as Document 33 §3.2 Example 2 already demonstrates. Within one
  statement type, whatever periods were returned are returned — there is
  no separate "partial" signal (§5).
- **Is freshness observable?** Only via the already-existing `fetched_at`
  field (Document 33 §3.1) — unchanged. Refresh/staleness remains out of
  scope (ADR-029 §18 item 4), untouched by this decision.
- **Are provider failures exposed or normalized?** Normalized. A
  transient provider failure (§5) never overwrites an existing terminal
  state and is invisible to the API consumer either way: if the identity
  previously held no state, it remains `not_yet_acquired`; if it
  previously held `available` or `confirmed_unavailable` (e.g. during a
  future refresh attempt, out of scope here), that state remains visible
  unchanged. This matches Document 33's already-frozen contract exactly,
  which has no error state for this case.

**No change to Document 33 is required or proposed.**

## 11. Rejected Alternatives

- **Company-level granularity** — rejected; contradicts Document 33's
  already-frozen partial-failure support (§6, R8).
- **Period-level granularity** — rejected; requires an undefined
  aggregation rule and doesn't correspond to a real provider call
  boundary (§6).
- **Redis as the acquisition-state store** — rejected; violates the
  binding RA-0/RA-1 invariant (§8).
- **A fourth public acquisition state** for transient/inconclusive
  attempts — rejected; would reopen Document 33's frozen contract, and
  no product requirement demands it (§5).
- **Internal acquisition-attempt history/log** — rejected for v1;
  serves only a not-yet-designed orchestrator's retry/backoff logic,
  which is a separate future decision (§5).
- **A distinct "non-retryable failure" state** beyond
  `confirmed_unavailable` — rejected for lack of evidence; stated
  explicitly per this task's instruction not to invent an answer where
  evidence is insufficient (§5).

## 12. Risks

| Risk | Status after this decision |
|---|---|
| R1 — no source exists | Resolved at the architecture level (§3, §4); implementation still required and still gated |
| R3 — inference-from-absence regression | Resolved as AS-1, carried forward unchanged and restated as binding |
| R5 — undefined failure semantics | Resolved (§5's outcome table), including the corrected transient-failure rule that a non-terminal outcome preserves the identity's prior state rather than universally resetting to `not_yet_acquired` |
| R6 — concurrent acquisition attempts could race | Resolved at architecture level by deterministic concurrent-outcome precedence (AS-4); implementation must enforce this invariant |
| R10 — granularity mismatch | Resolved (§6 — statement-type-level, adopted) |
| R12 — crash/stuck-state risk | Resolved at architecture level by AS-3 + AS-5; implementation must preserve the persistence ordering invariant |
| Acquisition **orchestration** (who triggers, retry backoff, worker/queue design) | **Not resolved — explicitly out of scope of this decision**, as it was of Document 34 §7.C. This document defines the state architecture an orchestrator would read/write against; it does not design the orchestrator |
| Refresh/staleness policy | Unchanged, still deferred per ADR-029 §18 item 4 — does not block v1 read correctness (§10) |
| The "no distinct non-retryable-failure state" conclusion (§5) | Low risk of being wrong given current evidence; explicitly flagged as revisitable if future evidence (e.g. a provider response distinguishing "ticker doesn't exist" from "no data for this combination") emerges |

## 13. Remaining Open Questions

- Exact Mongo collection name, field names, and index definition — an
  implementation detail correctly left to implementation, not an
  architecture ambiguity (§8, §9).
- Acquisition orchestration in full: trigger mechanism, worker/queue
  design (if any), retry/backoff policy, and how a cold-start attempt is
  actually initiated. Explicitly out of scope here, as it was in
  Document 34 §7.C — this is the next architecture gap, not resolved by
  this document.
- Refresh/staleness mechanism and threshold — unchanged, deferred per
  ADR-029 §18 item 4.
- Whether a `test_route_inventory.py`-style regression guard should
  enforce AS-1 in code once a source exists — an implementation-time
  engineering choice, not an architecture blocker.
- **How AS-5's ordering guarantee is mechanically enforced** (e.g. write
  sequencing in application code, a conditional/compare-and-swap update,
  or something else) is an implementation-level decision. This is *not*
  an open architecture question: **what** must be guaranteed —
  `FinancialStatement` persistence completes before `acquisition_state =
  available` is written — is already decided (§4, AS-5). Only the *how*
  is left to implementation.

## 14. Implementation Prerequisites

Mapped against Document 34 §9's seven-item implementation gate:

1. Canonical acquisition-state source of truth — **resolved** (§8:
   MongoDB, CTO RATIFIED).
2. State ownership — **resolved** (§9: separate boundary from
   `FinancialStatementRepository`).
3. State granularity — **resolved** (§6: statement-type-level).
4. Terminal/lifecycle semantics — **resolved** (§4: AS-0, AS-1, AS-3,
   AS-5), including the `FinancialStatement`-before-`available`
   persistence-ordering invariant (AS-5).
5. Transient failure semantics — **resolved** (§5) — corrected to
   preserve the identity's prior terminal state rather than universally
   resetting to `not_yet_acquired`.
6. Idempotency/concurrency behavior — **resolved by AS-4's deterministic
   conflict semantics** (monotonic evidence precedence: `available` >
   `confirmed_unavailable` > no terminal state) — not by idempotency
   alone (§4, §8).
7. Internal acquisition-attempt history — **remains resolved**: not
   required for v1, with rationale stated (§5).

All seven of Document 34 §7.A's required decisions are addressed at the
architecture level. What remains before M8 endpoint implementation can
begin: **this document's own CTO approval**, and separately, an
acquisition-orchestration design (§13) — the latter is a new,
independent architecture task this document does not attempt, and its
absence does not reopen anything decided above, because the read-only
`GET` endpoint (Document 33) never triggers acquisition itself.

---

*Companion documents:
[`32_M8_Pre_Implementation_Decision_Pack.md`](32_M8_Pre_Implementation_Decision_Pack.md) §4 (unmodified) ·
[`33_M8_Financials_API_Contract_Review.md`](33_M8_Financials_API_Contract_Review.md) (unmodified, not reopened) ·
[`34_M8_Acquisition_State_Architecture_Risk_Review.md`](34_M8_Acquisition_State_Architecture_Risk_Review.md) (the risk register this document resolves) ·
[`09_Redis_Architecture.md`](09_Redis_Architecture.md) RA-0/RA-1 (cited, unmodified).*

*This is a CTO-ratified architecture-decision artifact (see Governance
Addendum near the end of this document). It does not itself authorize
implementation, schema changes, migrations, dependency changes, provider
integration, or endpoint implementation.*

**Self-assessment against this task's own test:** R1, R3, R5, R6, R10,
and R12 each received a concrete, evidence-based resolution in §3–§8
(not a restatement of the question) — a source of truth, a numbered
invariant set (including the deterministic concurrency rule, AS-4, and
the persistence-ordering rule, AS-5), a complete outcome table with
corrected transient-failure semantics, an adopted granularity with
rejected alternatives, and a crash-recovery guarantee, respectively —
with no open sub-question left dangling within any of them. The two
items left genuinely open (acquisition **orchestration**, §13, and the
narrow non-retryable-failure question, §5/§12) are both explicitly
separate architectural concerns this task scoped out, not unresolved
ambiguity within the risks resolved above.

**This does not mean M8 implementation is unblocked.** Architecture is
now 🟢 ratified (see Governance Addendum below); M8 implementation
remains 🔴 blocked regardless — Document 34's implementation gate (§9
there) is answered only at the architecture level here, not executed,
and nothing in this document authorizes writing code, a schema, an
index, or an endpoint.

## Governance Addendum — CTO Ratification Record

- **Date:** 2026-08-12
- **Decision:** CTO RATIFIED
- **Scope:** the acquisition-state architecture in this document only —
  the three-state model (§2), the identity/granularity decision (§6:
  `(ticker, period_type, statement_type)`, `period_end` excluded), the
  invariant set AS-0 through AS-5 (§4), the outcome table (§5), and the
  recovery guarantees (§7). Nothing about this ratification reopens,
  rewrites, or reinterprets that content.
- **Consistency confirmed against the current state of Documents 32, 33,
  36, 37, 38, and 39** at time of ratification: `FinancialStatement`'s
  own identity (`ticker + period_type + period_end + statement_type`,
  ADR-029 §8) remains unaffected and separate, per the
  `FinancialStatement data ≠ Acquisition lifecycle state` boundary this
  document establishes; Document 38's canonical-provider decision
  (MongoDB) builds on this document's identity/state model without
  altering it; Document 36's orchestration architecture treats
  acquisition orchestration as explicitly out of scope here, per §13;
  Document 33's `GET`/`POST` contracts are unaffected and not reopened.
- **Implementation:** remains 🔴 **BLOCKED.** Ratifying this document is
  not itself an implementation authorization. Implementation remains
  subject to the implementation-readiness/authorization gate (see
  [`39_M8_Implementation_Readiness_Assessment.md`](39_M8_Implementation_Readiness_Assessment.md)).

---

## M8 ACQUISITION-STATE ARCHITECTURE: CTO RATIFIED. M8 implementation remains BLOCKED pending the governance sequence recorded above.
