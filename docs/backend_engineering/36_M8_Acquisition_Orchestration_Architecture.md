# M8 Acquisition Orchestration Architecture

**Status:** 🟢 **CTO RATIFIED — ORCHESTRATION ARCHITECTURE APPROVED**
(Round 4, 2026-08-10). Ratification covers the orchestration
architecture only — see the Governance Addendum near the end of this
document for the exact scope and the governance sequence still
required before implementation.

**Architecture:** 🟢 Ratified (Round 4, 2026-08-10).
**Implementation:** 🔴 Still blocked — ratifying this document does not
authorize implementation; see the Governance Addendum.

**Date:** 2026-08-10
**Builds on:** [`35_M8_Acquisition_State_Architecture_Decision.md`](35_M8_Acquisition_State_Architecture_Decision.md)
(binding — not reopened), [`34_M8_Acquisition_State_Architecture_Risk_Review.md`](34_M8_Acquisition_State_Architecture_Risk_Review.md),
[`32_M8_Pre_Implementation_Decision_Pack.md`](32_M8_Pre_Implementation_Decision_Pack.md).
**Does not modify:** Document 32, Document 33, Document 34, Document 35,
any production code, any test, any schema, any migration, any endpoint,
any repository, any provider adapter, any worker, `server.py`, LangGraph,
or the frontend.

> **Revision, Round 2 — CTO-directed rejection and redesign
> (2026-08-10):** Round 1 proposed that `GET /companies/{ticker}/financials`,
> upon finding an identity `not_yet_acquired`, would schedule an
> `asyncio.create_task` acquisition attempt before returning its
> (unaffected) read response. **The CTO rejected this outright** — an
> asynchronous, non-blocking trigger is still a trigger, and Documents 33
> and 35 establish `GET /financials` as strictly read-only, not merely
> "not synchronously blocking." Round 2 redesigned the trigger as a side
> step inside the existing `POST /report`/`POST /explain` ingestion
> pipeline instead, keeping `GET` a pure read.
>
> **Revision, Round 3 — CTO-directed trigger-ownership and
> execution-durability correction (2026-08-10):** the CTO approved
> Round 2's read-only correction (`GET /financials` remains strictly
> read-only — **not regressed here**) but identified two deeper problems
> Round 2 did not resolve: (1) Round 2 made acquisition a conceptual
> side effect of report generation, leaving any user who only ever uses
> the Financials feature with a permanently `not_yet_acquired` result
> and no path to change that — a product/architecture ownership gap,
> not a mere technical edge case; (2) Round 2 asserted in-process,
> non-durable execution was acceptable by citing precedent
> (`company_index`, OTP email) without separately analyzing *safety*
> (does AS-3/AS-4/AS-5 prevent corruption — yes, unchanged) versus
> *liveness* (will acquisition ever actually happen — Round 2 left this
> weak and did not say so plainly). This round re-evaluates trigger
> ownership from first principles (§5), reframes acquisition as a shared
> capability with multiple peer triggers rather than a report-generation
> side effect (§4, §6), and adds an explicit safety-vs-liveness analysis
> (§9) the prior rounds lacked. Round 1's and Round 2's content is
> superseded where restated below, not silently deleted — this note and
> Round 2's note above it are the audit trail.
>
> **Revision, Round 4 — CTO-directed finalization corrections
> (2026-08-10):** the CTO approved Round 3's trigger-ownership and
> safety/liveness model and requested nine precision corrections before
> ratification: (1) clarified that the Financials trigger endpoint is an
> explicit acquisition *request*, not a retry engine, and that the
> frontend must never own provider retry/backoff/rate-limit/timeout
> policy — client polling is a UX observation mechanism only; (2) added
> an explicit durable-state-vs-non-durable-execution invariant, stated
> as a deliberate v1 decision, not an oversight; (3) corrected the AS-5
> crash-window explanation to state precisely that AS-5 orders the two
> writes, it does not make them atomic, and that a resulting
> non-converged window is possible (safe, not designed away here); (4)
> made the governance sequence for the recommended trigger endpoint
> fully explicit — Document 36 approval, then a separate CTO approval to
> reopen Document 33's governance, then a Document 33 amendment, then an
> API contract review, only then implementation; (5) clarified the
> endpoint's meaning as "request acquisition for this ticker's
> identities," explicitly not a retry/force-refresh/status/management
> API, with no wire schema defined here; (6) sharpened liveness wording
> to "trigger-driven, not globally guaranteed"; (7) confirmed the
> read/acquisition diagram implies no trigger owns the capability; (8)
> updated the risk table; (9) reconfirmed the implementation block.
> Round 1/2/3's content is superseded where restated below, not silently
> deleted.
>
> **Governance Record Update — CTO Ratification (2026-08-10):** the CTO
> formally ratified the Round 4 orchestration architecture as written.
> **No architectural content was changed, reopened, rewritten, or
> reinterpreted in this governance-record update.** This entry and the
> Governance Addendum near the end of the document record the
> ratification and the governance sequence still required before
> implementation. Round 1-4's content is unchanged; the architecture
> remains Round 4.

---

## 1. Objective

Define how AlphaScribe triggers, executes, retries, and recovers
financial-statement acquisition as an **independently owned, shared
application capability** — not a side effect of any single feature —
while (a) treating every acquisition-state decision Document 35
ratified as fixed, and (b) preserving `GET /companies/{ticker}/financials`
as strictly read-only, with no side effects of any kind.

## 2. Frozen Constraints (Document 35 — not reopened)

Unchanged from Round 2:

- Three public acquisition states; no fourth. Identity =
  `(ticker, period_type, statement_type)`.
- **AS-0–AS-2:** single durable source of truth, never inferred from
  `FinancialStatement` absence, single repository-shaped boundary.
- **AS-3:** terminal-write-only — a transient/inconclusive attempt
  writes nothing and preserves whatever durable state already existed.
- **AS-4:** deterministic concurrency via monotonic evidence precedence
  (`available > confirmed_unavailable > no terminal state`); `available`
  is sticky. **AS-4 is the system's only correctness guarantee under
  concurrency** — nothing in this document substitutes for it.
- **AS-5:** `FinancialStatement` persistence precedes
  `acquisition_state = available`; if it fails, `available` is never
  written.
- MongoDB is the selected acquisition-state store;
  `AcquisitionStateRepository` remains separate from
  `FinancialStatementRepository`. Redis is never the system of record.
- **`GET /companies/{ticker}/financials` is strictly read-only.** It
  must not call the provider, schedule acquisition, create an
  acquisition task, write acquisition state, write `FinancialStatement`,
  trigger a retry, or perform any hidden background mutation. Document
  33's API contract is frozen and is not touched here.

## 3. Repository Evidence

Carried forward from Round 2 (§3 there), unchanged, plus nothing new
required for this round's questions — the ownership/durability analysis
below reasons from the same evidence already gathered, not new code
inspection:

- `agents/company_index.py`'s lazy-populate pattern (`_LOAD_LOCK`,
  `is_loaded()`/`load_index()`) and `server.py:634-637`, `:360`'s
  fire-and-forget `asyncio.create_task` usage — an execution-mechanism
  precedent, re-examined rigorously in §9, not cited as proof by itself
  this round.
- `server.py:1085`, `:1418` — `RUNNING_TASKS[job_id]`-tracked `Job`
  triggers for `POST /report`/`POST /explain`; the existing ingestion
  step (`agents/ingest.py:97-149`) these already run.
- `server.py:1645-1649` — `_warmup`'s one-time startup precedent.
- `application/ports.py:49`, `jobs.py:115-134` — `JobStore.reap()` /
  `JobLifecycle.reap_stale()` exist but are never called from
  `server.py` in production — no working scheduler precedent exists in
  this codebase today (reconfirmed, unchanged from Round 2).
- No dedicated acquisition endpoint exists; this document chain has
  repeatedly excluded creating one — **re-evaluated explicitly this
  round (§4.4), not assumed excluded.**
- No background job runner, worker, scheduler, or queue exists anywhere
  in `backend/`.

## 4. Trigger Alternatives (re-evaluated)

Each candidate judged on user/product behavior, architectural ownership,
lifecycle, failure behavior, retry behavior, crash/restart behavior,
operational complexity, whether `GET` stays read-only, interaction with
Documents 33/35, repository evidence, and v1 appropriateness.

### 4.1 `POST /report` / `POST /explain` (Round 2's selection)

- **User/product behavior:** acquisition happens as a consequence of a
  user researching a ticker — a real, common path, but not the only one
  the Financials feature needs.
- **Ownership:** correctly reframed this round (§6) as *one legitimate
  trigger of the shared use case*, not the owner of it — Round 2's
  phrasing ("a side step inside ingestion") is corrected here.
- **Lifecycle/failure/retry/crash:** unchanged from Round 2 §7-§14 —
  fire-and-forget, non-blocking to report generation, safe under AS-3.
- **`GET` stays read-only:** yes — untouched, this trigger lives entirely
  inside a different endpoint.
- **Document 33/35 interaction:** none — orthogonal to both.
- **Repository evidence:** strong — `agents/ingest.py` already does this
  class of work today for `.info`.
- **v1 appropriateness:** retained as one peer trigger, **not sufficient
  alone** — this is precisely the gap the CTO identified. A user who
  only opens the Financials tab never causes this trigger to fire.

### 4.2 A dedicated internal application command

Not itself a trigger source — it *is* the shared `acquire(identity)` use
case (§6) every other candidate invokes. Restated, not redecided.

### 4.3 An internal/admin operational trigger

A manually-invoked command/script that calls `acquire()` directly (e.g.
to pre-seed demo data, or to force-retry a specific identity). **Retained
as a legitimate, always-available secondary trigger** — useful
operationally, but it requires a human to act, so it does not by itself
solve organic user liveness (§9). Not rejected; not sufficient alone.

### 4.4 A dedicated acquisition-trigger endpoint (re-evaluated, not assumed excluded)

**What the endpoint means, precisely:** *"request acquisition for the
relevant financial identities for this ticker."* Nothing more. It is
**not** a retry endpoint, a force-refresh endpoint, a provider-retry
API, an acquisition-status endpoint, or a general acquisition-management
API — those framings are explicitly rejected (§23). It invokes the same
shared `acquire()` use case every other trigger invokes (§6); repeated
calls are safe because correctness comes entirely from Document 35's
AS-4, not from anything the endpoint itself does. No wire-level
request/response schema is defined here — that belongs to the later API
contract document (§4.4's governance sequence, below).

- **User/product behavior:** the Financials feature's own frontend,
  upon observing `not_yet_acquired` from the (still-read-only) `GET`
  response, calls this endpoint to request acquisition for that
  ticker's identities. This directly answers the CTO's central
  question — a financials-only user gets an immediate, feature-owned
  path to *request* acquisition, not a hope that they'll also generate
  a report.
- **Architectural ownership:** clean — this endpoint does nothing but
  invoke the same shared `acquire()` use case §4.1's trigger already
  calls (§6's "shared capability" model, not report-subordinate).
- **Lifecycle:** request → identity check → `asyncio.create_task(acquire(identity))`
  → immediate response (e.g. "acquisition requested") → the underlying
  attempt proceeds exactly as §7-§14 describe, unchanged in mechanism
  from the existing trigger.
- **Failure/retry behavior:** identical to §4.1's — AS-3-safe, no
  terminal write on transient failure. **The meaningful difference is
  liveness, not safety** (§9). The frontend *may* observe
  `not_yet_acquired`, request acquisition, and poll `GET /financials`
  for UX/status purposes — but **client polling is a user-experience
  observation mechanism, not the backend's retry policy.** The frontend
  must not become the architectural owner of: provider retry policy,
  exponential backoff, rate-limit handling, provider timeout policy,
  attempt counters, or any other backend lifecycle policy — all of
  those remain entirely server-side concerns (§12, §13), undecided
  Engineering Questions where not yet designed, never delegated to the
  client by virtue of it being allowed to poll. If a second acquisition
  request is explicitly issued after observing the current state (or
  through any other legitimate trigger), it simply invokes the same
  idempotent acquisition use case again (§10) — the endpoint has no
  memory of "this is attempt number N" and does not need one.
- **Crash/restart behavior:** identical to every other trigger — AS-3
  guarantees safety; nothing new to recover.
- **Operational complexity:** low — one more authenticated route calling
  an already-designed use case, using the same `current_user`
  authentication `GET /financials` already requires. No new
  infrastructure class.
- **Does `GET` stay read-only:** **yes, unconditionally** — this is a
  *different* endpoint. `GET /financials` itself gains no new behavior.
- **Interaction with Document 35:** none — same use case, same
  invariants, same repositories.
- **Interaction with Document 33:** **Document 33 governs only
  `GET /financials`, is frozen, and does not currently authorize a
  second, acquisition-triggering endpoint.** Document 36 does not
  change that. Introducing the endpoint requires the following
  sequence, none of which this document performs:

  1. The CTO ratifies this document's orchestration architecture.
  2. The CTO explicitly approves reopening the narrow API-governance
     question of whether a second, acquisition-triggering endpoint may
     exist.
  3. Document 33 receives a narrow amendment/addendum covering the new
     endpoint specifically — Document 33's existing frozen contract for
     `GET /financials` is not otherwise reopened.
  4. An API contract review approves the new endpoint's own contract
     (request/response shape, auth, error behavior) — not defined here.
  5. Only then may implementation begin.

  **Document 36 itself authorizes none of these steps** — it recommends
  step 2 be taken, and stops there.
- **v1 appropriateness:** **recommended (§5)**, conditional on the
  five-step sequence above. If step 2 is declined, §4.6 (scheduler) is
  the named fallback.

### 4.5 A dedicated acquisition endpoint — reused as a general-purpose write surface

Not evaluated separately from §4.4 — the CTO's candidate D and this
document's recommendation are the same narrow proposal: one route, one
purpose (request acquisition for a specific identity/ticker), not a
general acquisition-management API.

### 4.6 A scheduler

- **User/product behavior:** invisible to any specific user — a periodic
  sweep attempts `not_yet_acquired` identities in the background,
  independent of anyone looking at anything.
- **Ownership:** clean — calls the same shared `acquire()` use case.
- **Lifecycle:** a periodic `asyncio` loop, same shape `_warmup` already
  starts at `@app.on_event("startup")`, but recurring rather than
  one-shot.
- **Failure/retry/crash:** AS-3-safe like every other trigger; a missed
  cycle (crash) simply means the next cycle, once the process restarts,
  resumes coverage — no state to recover.
- **Operational complexity:** low-to-moderate — genuinely new (no
  working precedent exists in this codebase, §3), but not a new
  infrastructure *class* (no queue, no worker process, no external
  scheduler service) — an in-process loop, the same shape `reap_stale()`
  conceptually needs but doesn't have (§3).
- **`GET` stays read-only:** yes — completely orthogonal.
- **Document 33/35 interaction:** none.
- **v1 appropriateness:** **not selected as primary** — it provides
  guaranteed eventual liveness for *every* ticker AlphaScribe knows
  about, whether or not anyone has asked about it via any feature,
  which is broader coverage than current evidence justifies (no product
  requirement asks for financials on tickers nobody has looked at).
  **Named explicitly as the fallback if §4.4 is not approved**, since it
  closes the same organic-liveness gap without touching API governance
  at all — and as a plausible *future* backstop even if §4.4 is
  approved, for the narrower case of a ticker nobody currently views but
  someone will later (§20).

### 4.7 A queue/worker

**Rejected, unchanged from Round 2 (§4.7 there) — not reflexively, on
the same evidentiary basis.** ADR-029 §11's "small, bounded, infrequent"
characterization and this backend's single-instance operation don't
currently justify a queue's distinguishing properties (cross-restart
durability, horizontal scaling) over §4.4/§4.6's lighter mechanisms.
Re-affirmed here, not re-argued from scratch, since neither this round's
new evidence nor its new questions change the underlying scale
assessment.

### 4.8 Another existing controlled application trigger

No candidate beyond §4.1 surfaces on renewed inspection — `company_index`'s
trigger (ticker search) has no relationship to financial-statement
identities.

### 4.9 No automatic trigger in v1

**Rejected as the primary answer**, unchanged reasoning from Round 2
§4.9 — leaves `FinancialsSection.tsx` effectively permanently
unpopulated without manual intervention, which does not serve M8's
product intent. Retained only as what §4.3 already provides (a manual
operational escape hatch), not as the organic-user answer.

## 5. Selected Trigger Architecture

**Acquisition is triggered by multiple legitimate, peer entry points
into one shared use case — not owned by any single one of them:**

1. **`POST /report` / `POST /explain`'s existing ingestion step** (§4.1)
   — unconditional, already exists conceptually, retained.
2. **A dedicated Financials-feature acquisition-trigger endpoint**
   (§4.4) — **recommended**, closes the organic financials-only-user
   gap the CTO identified, **conditional on explicit CTO approval to
   reopen the narrow "does a second, acquisition-triggering endpoint
   exist" governance question** Document 33's original review closed.
   This document does not build it; it recommends approving its
   existence.
3. **An internal/operational manual trigger** (§4.3) — always available,
   not a solution to organic liveness by itself.
4. **A scheduler** (§4.6) — **named fallback** if (2) is not approved,
   and a plausible future backstop regardless.

```
READ PATH  (GET /companies/{ticker}/financials — Document 33, unchanged):

    GET /companies/{ticker}/financials
            │
            ▼
    read FinancialStatementRepository
            +
    read AcquisitionStateRepository
            │
            ▼
    response

    — no arrow leaves this box, under any of the trigger options above.


ACQUISITION CAPABILITY  (independently owned, multiple legitimate entry points):

    Trigger(s)
    ┌─────────────────────────────────────────────────────┐
    │  POST /report / POST /explain   (existing ingestion) │
    │  Financials acquisition-trigger endpoint  (§4.4, new,│
    │    pending governance approval)                      │
    │  Internal/operational command   (§4.3)                │
    │  Scheduler   (§4.6, fallback / future)                │
    └─────────────────────────────────────────────────────┘
            │
            ▼
    Acquisition Use Case  (application layer, §6 — shared,
    independently owned; no trigger is its "parent")
            │
            ▼
        provider (yfinance)
            │
            ▼
    FinancialStatementRepository persistence      (AS-5: first)
            │
            ▼
    AcquisitionStateRepository persistence        (AS-5: then, on success)
```

**There is no arrow from `GET /financials` into the acquisition
capability**, under any trigger. `GET` and the acquisition capability
share only the two repository boundaries — never a direct call.

## 6. Ownership Model — Acquisition as a Shared Application Capability

**Corrected framing, per the CTO's explicit instruction:** the
acquisition use case is not, and must not be described as, a side effect
of report generation. The correct shape is:

```
Application
      ↓
Acquisition Use Case   (independently owned, application layer)
      ↓
Provider + persistence
```

with `POST /report`, the Financials trigger (§4.4), operational commands
(§4.3), and a future scheduler (§4.6) all calling *into* it as peers —
none of them owns it, none of them is a prerequisite for the others to
function, and the use case itself has no knowledge of which trigger
invoked it (consistent with §19's security boundary — it does not carry
the triggering context's identity forward regardless of which trigger
fired). This corrects Round 2's language ("financial acquisition is a
side effect of report generation") throughout the rest of this document.

## 7. Provider Invocation

Unchanged from Round 2: one `acquire(identity)` call maps to one
provider call, matching the real yfinance call boundary Document 35 §6
already used. `asyncio.to_thread`, same as `_fetch_yfinance_sync`. A
bounded timeout wraps every call — **duration remains an Engineering
Question** (§25).

## 8. Provider Outcome Semantics

Unchanged from Round 2 — reapplies Document 35 §5 without redeciding
any outcome:

| Outcome | Acquisition state (Doc 35, unchanged) | Terminal? |
|---|---|---|
| Success, statement data returned | `available`, only after `FinancialStatement` persists (AS-5) | Yes |
| Success, provider explicitly empty | `confirmed_unavailable`, unless already `available` (AS-4 sticky) | Yes |
| Partial data | `available` (not distinct, Document 35 §5) | Yes |
| Timeout / failure / malformed response / rate limiting | No terminal write (AS-3) | No |
| Stale data | Not a new outcome — out of scope (ADR-029 §18 item 4) | N/A |

## 9. Safety vs. Liveness — First-Class Analysis

**These are different properties and must not be conflated, per the
CTO's explicit correction of Round 2's reasoning.**

### 9.1 Safety (unchanged, strong)

No invalid terminal state is ever written, regardless of how many
triggers fire, how they race, or how the process fails mid-attempt.
Guaranteed entirely by Document 35's AS-3/AS-4/AS-5 — this document adds
nothing to and removes nothing from that guarantee. Safety holds
identically for every trigger in §5, because they all funnel through the
same use case and the same repository boundaries.

### 9.2 Liveness (the property Round 2 left weak, addressed here)

**Definition used here:** for a given acquisition identity that is
currently `not_yet_acquired`, will it eventually get another opportunity
to reach a terminal state?

- **Under Round 2's design (trigger §4.1 only):** weak. Liveness
  depended entirely on someone eventually re-running research on the
  ticker — plausible, but not tied to the Financials feature at all,
  and completely absent for a user who only ever opens the Financials
  tab.
- **Under this round's design (§5, with §4.4 approved):** substantially
  stronger for the case that matters most — an active user waiting on
  financials. **Observation and request are distinct:** that user's
  client may poll `GET /financials` to *observe* current state, and,
  informed by that observation, *explicitly issue another acquisition
  request* through §4.4 — a legitimate trigger in its own right (§5).
  Polling itself performs no retry and mutates nothing; the **request**
  is what gives the identity another opportunity to reach a terminal
  state, **without any new server-side durable execution** (§9.3's
  mechanism is unchanged — still in-process, fire-and-forget). Liveness
  here comes from the user's decision to ask again, which polling merely
  helps them time — not from polling as a mechanism.
- **Residual liveness gap (named, not hidden):** an identity whose only
  trigger was §4.1 (research) or §4.3 (a one-off manual command), that
  failed, and for which **no one is currently viewing the Financials tab
  for that ticker**, has no guaranteed future retry. This is the same
  fundamental gap Round 2 had, narrowed but not eliminated by §4.4 — it
  is eliminated only if §4.6's scheduler is ever added. **Explicitly not
  claimed acceptable by default** — see §20 (Acceptance Test Scenario 8)
  and §25 for the CTO decision this depends on.
- **Precise statement of what v1 provides:** the Financials trigger
  (§4.4) gives the active Financials user a direct, feature-owned way to
  *explicitly request* acquisition again. **Client polling of
  `GET /financials` is a user-experience observation mechanism — it
  informs the user (or their client) when it might be worth issuing
  another request; it is not itself a backend liveness mechanism and
  performs no retry on its own.** Liveness in this case comes from the
  explicit request the user's activity leads to, not from the act of
  polling. **"V1 provides trigger-driven liveness, not globally
  guaranteed eventual acquisition."** A future scheduler or durable
  worker (§4.6, §4.7) may strengthen this later; neither is built here.

### 9.3 Why in-process fire-and-forget execution remains selected despite the liveness gap

**Explicit architectural invariant:**

```
DURABLE:                              NON-DURABLE:
  AcquisitionState                      the in-flight acquisition
  FinancialStatement                    task itself
```

**"V1 guarantees durable acquisition OUTCOME state, but does not
guarantee durable acquisition EXECUTION."** A process crash may lose an
in-flight acquisition attempt entirely — no record of it having started
survives. This is safe because: AS-3 prevents any invalid terminal state
from resulting; AS-4 preserves concurrency correctness regardless; AS-5
preserves write ordering between `FinancialStatement` and acquisition
state. When execution is lost, another legitimate trigger (§5) may
create another attempt — that is the entirety of v1's recovery story,
and §9.2 already states plainly where it is and isn't strong. A future
scheduler or durable worker (§4.6, §4.7) could provide durable execution
if scale or reliability requirements ever justify it — not built
speculatively here.

**This is a deliberate v1 architectural decision, not an accidental
limitation.** It follows from the ten-dimension analysis below, not from
convenience or precedent alone.

Answering the CTO's explicit question — why durable *state* but not
durable *execution* — against the ten requested dimensions:

1. **Correctness requirements:** fully satisfied by durable state
   (AS-3/AS-4/AS-5) independent of execution durability — a lost attempt
   is never a *wrong* answer, only a *missing* one.
2. **User expectations:** the real risk is a user perceiving the product
   as stuck. §4.4 + client polling directly addresses this for the
   active-user case; the residual gap (§9.2) is the honest remainder.
3. **Provider cost:** yfinance is free/unmetered in evidence gathered so
   far (Document 31) — repeated attempts carry no direct cost, only
   rate-limit risk (§8, unchanged Engineering Question).
4. **Acquisition frequency:** low — ADR-029 §11's "small, bounded,
   infrequent... not a hot path" — the population of in-flight attempts
   at any moment is small, so the *volume* lost to a rare crash is
   inherently small.
5. **Acceptable delay:** for the §4.4 active-user path, the time until
   another explicit acquisition request is user/client-action dependent.
   Client polling may inform that decision but does not itself initiate
   another attempt. The exact request cadence is a frontend/UX decision,
   not designed here. For the residual gap, delay is currently
   unbounded — named, not resolved, in §9.2/§20.
6. **Crash behavior:** AS-3-safe by construction — an in-flight attempt
   simply vanishes with no trace, never corrupting state.
7. **Process restart:** identical to crash — nothing to recover.
8. **Horizontal scaling:** not currently relevant — this backend is
   single-instance today (CLAUDE.md); durable execution's main benefit
   here (coordinating work across multiple workers) has no current
   evidence of need.
9. **Observability:** an in-flight attempt lost to a crash does lose its
   `acquisition_completed`/`acquisition_failed` log/span (§17) — a real,
   named observability gap on crash specifically, distinct from the
   correctness question and not previously called out this precisely.
10. **Retry opportunities:** v1 does not provide a durable backend retry
    mechanism. A subsequent acquisition attempt occurs only when another
    legitimate trigger fires, including a later explicit acquisition
    request from an active Financials user. Client polling may inform
    when the client chooses to issue another request, but polling itself
    is not a retry mechanism and does not guarantee eventual
    acquisition — this is a deliberate design choice, not an oversight.

**Selected: in-process fire-and-forget remains the execution mechanism**
(unchanged from Round 2), **not because it was already used elsewhere in
this codebase, but because the ten dimensions above — taken together —
show safety is fully decoupled from execution durability, volume is low,
and the strongest liveness need (an active user) is served by §4.4
giving that user a direct way to issue another explicit acquisition
request, rather than requiring the server to remember anything about
in-flight work.** Client polling only informs *when* that request is
made — it is not itself the retry mechanism. The residual gap (§9.2) is
real and is carried into §20/§25 as an explicit decision point, not
dismissed.

## 10. Idempotency

Unchanged from Round 2 — two distinct concerns (Document 35 AS-4
correctness vs. this document's efficiency concern), same identity,
same reasoning. §4.4's trigger inherits this unchanged — a duplicate
call to it (e.g. a user clicking "retry" twice) is exactly as safe and
exactly as bounded-wasteful as any other duplicate trigger.

## 11. Concurrency

Unchanged from Round 2 §10 — restated once more since this round adds a
new trigger source: **AS-4 is correctness, full stop, regardless of how
many trigger types exist or how many of them fire concurrently for the
same identity.** An in-process per-identity lock remains optional,
efficiency-only, same-process-scoped, and provides zero correctness
guarantee across multiple processes — AS-4 covers that case
unconditionally. Adding §4.4 as a new trigger source does not change any
of this; it only adds one more caller into the same lock/AS-4 story.

## 12. Retry Semantics

- **Retry trigger:** any of §5's triggers firing again for a still-
  `not_yet_acquired` identity. `GET /financials` is never a retry
  trigger — unchanged, unconditional.
- **What actually causes a retry to happen now:** primarily a user
  re-invoking §4.4's request endpoint (possibly prompted by their own
  client polling `GET /financials` for status, §9.2); secondarily a
  future research request (§4.1); occasionally a manual command (§4.3).
  **The client polling loop, if a frontend implements one, only decides
  *when to ask again* — it never decides backoff, timeout, or
  rate-limit behavior, all of which remain entirely server-side (§4.4).**
- **Retry/request frequency:** for §4.4, the frequency of subsequent
  acquisition requests is determined by explicit client/user requests,
  subject to whatever UX/request cadence the frontend eventually adopts.
  Client polling may inform when another request is appropriate, but the
  polling interval itself is not a retry interval and does not cause an
  acquisition attempt. This cadence is a UX decision, not a backend
  retry policy. For §4.1/§4.3, unbounded and undefined, unchanged from
  Round 2.
- **Backoff/cooldown, rate-limit handling:** still explicitly undecided
  — an Engineering Question (§25), not silently resolved, and **not a
  responsibility this document delegates to the frontend.** No evidence
  (Document 31) currently shows rate-limit pressure.

## 13. Timeout Semantics

Unchanged from Round 2 §12: mechanism precedent exists
(`agents/ingest.py`'s `httpx.AsyncClient(timeout=25.0, ...)`), exact
duration for yfinance's call shape is undecided (§25).

## 14. Cancellation

Unchanged from Round 2 §13, generalized to any trigger: the triggering
request's cancellation/disconnect does not cancel an already-fired
acquisition task, for any of §5's trigger types — acquisition serves the
shared corpus, not the specific requester. No explicit cancellation
affordance exists for acquisition itself at v1; §13's bounded timeout is
the only cap.

## 15. Crash/Restart Recovery

Unchanged in substance from Round 2 §14, with the overclaim already
corrected there (Round 2 had already walked back "fully self-healing" to
"safe but not guaranteed-to-retry") — this round's contribution is §9's
formal safety/liveness split, which supersedes Round 2's informal
version of the same idea. Nothing new to state here beyond §9.

## 16. Partial Acquisition

Unchanged from Round 2 §15 — reuses Document 35's ratified granularity,
no competing granularity introduced.

## 17. Eventing

Unchanged from Round 2 §16, with one addition: `acquisition_requested`
is no longer purely implicit for the §4.4 path — an explicit trigger
call *is* this event for that path (still implicit for §4.1/§4.3/§4.6).
`acquisition_started`/`provider_started`/`provider_completed`/
`provider_failed`/`acquisition_completed`/`acquisition_failed` are
unchanged. `retry_scheduled` still does not apply (no server-side
scheduler exists unless §4.6 is later adopted). `acquisition_cancelled`
still does not apply (§14).

## 18. Observability

Unchanged from Round 2 §17 in mechanism (M6 reuse — `get_tracer()`,
`llm_calls_total`-style `Counter`). One addition per §9.3 point 9: the
observability gap where a crash mid-attempt loses that attempt's
completion event should be named explicitly in any future
implementation-level design as a known limitation, not silently absent
— flagged here at the architecture level, not solved.

## 19. Security

Unchanged from Round 2 §18: `acquire()` carries no user context forward
regardless of which trigger invoked it (§6) — restated because §4.4
means acquisition can now be triggered by an authenticated,
feature-specific user action, making it *more* important, not less, that
the use case itself remains user-agnostic (Document 33 §7 shared-corpus
model, unchanged). §4.4's endpoint (if approved) would require
`current_user`, same as `GET /financials` — no weaker authentication
boundary than the read path it's paired with.

## 20. Acceptance Test Scenarios

Verification against the eight required scenarios before treating this
architecture as complete:

1. **User generates a report for AAPL — how does acquisition happen?**
   §4.1's existing ingestion step fires `acquire()` for each
   `not_yet_acquired` identity implied by the ticker, independent of the
   report's own success/failure (§7).
2. **User opens Financials for AAPL, never generates a report — how does
   acquisition happen?** Via §4.4 (recommended, pending governance
   approval): the frontend, seeing `not_yet_acquired`, calls the
   dedicated trigger endpoint. If §4.4 is not approved, the honest
   answer is §4.6 (scheduler, if later built) or, absent both,
   **it does not happen** — named explicitly, not hidden, and the
   central reason this round exists.
3. **Acquisition fails transiently — what causes another attempt?** No
   terminal write (AS-3); a future firing of any §5 trigger — most
   plausibly a subsequent explicit acquisition request through §4.4, a
   future research-trigger invocation, or an operational trigger. Client
   polling may inform the user's decision to issue another request but
   does not itself constitute backend retry (§9.2, §12).
4. **Acquisition is running and the process crashes — what survives?**
   Nothing in-flight; AS-3 guarantees no corrupt state; a future trigger
   re-attempts. If the trigger was §4.1, `Job`-level `reap()` separately
   marks that job failed — unrelated to acquisition-state recovery
   (§15).
5. **Two users trigger acquisition for AAPL simultaneously — what
   prevents an incorrect final state?** AS-4 (Document 35) alone,
   unconditionally — an in-process lock only reduces wasted duplicate
   provider calls, never substitutes for AS-4 (§11).
6. **Provider is rate-limited — what happens?** Falls under §8's
   non-terminal outcomes — no state written, safely retryable later; no
   dedicated backoff policy exists (§12, §25, Engineering Question, not
   silently assumed handled).
7. **`FinancialStatement` persists but the acquisition-state write
   fails — how does AS-5 protect correctness?** **AS-5 prevents the
   system from publishing `available` before the `FinancialStatement`
   exists. It does not make the two writes atomic.** If the
   `FinancialStatement` write succeeds and the subsequent
   acquisition-state write then fails, the result is: the
   `FinancialStatement` exists, and acquisition state remains at its
   previous value. This is **safe, conservative, and never a false
   `available`** — but it is a real, potentially **temporarily
   non-converged** state (data exists; the record of that fact does
   not, yet). This is the same crash window Document 35 already names,
   restated precisely here: ordering, not atomicity. **Future
   acquisition or reconciliation work may be required to converge the
   durable state** — no reconciliation mechanism is designed or invented
   in this document; only the property itself is recorded accurately.
8. **A ticker is never researched again after an acquisition failure —
   does acquisition eventually retry? Is that acceptable?** Under §4.1
   alone: no guaranteed retry. Under this round's full design: a retry
   occurs only if someone issues an explicit acquisition request via
   §4.4 (merely viewing the Financials tab — a `GET`, an observation —
   does not by itself retry anything) or re-researches the ticker
   (§4.1), but there is **no guarantee** absent one of those. **Explicitly
   determined here: this residual gap is not
   automatically acceptable** — it is a named decision point for the
   CTO (§9.2, §25), not something this document unilaterally declares
   fine because AS-3 makes it safe. Safety and liveness are different
   properties (§9), and this scenario is precisely where that
   distinction matters.

## 21. Failure Matrix

| Failure/Event | Acquisition State | Retry | Recovery | User Visible |
|---|---|---|---|---|
| Successful acquisition (any trigger) | `available` (after `FinancialStatement` persists, AS-5) | None needed | N/A | Yes, next `GET` |
| Provider timeout | Unchanged — no terminal write (AS-3) | Only if a subsequent acquisition request is explicitly issued through §4.4 or another legitimate trigger fires; client polling alone does not retry acquisition | Identity unchanged; safe | No new signal |
| Provider failure (exception) | Unchanged | Same as timeout | Same | No new signal |
| No data (provider-confirmed empty) | `confirmed_unavailable`, unless already `available` (AS-4 sticky) | Not automatic — refresh policy, out of scope | N/A — terminal | Yes, next `GET` |
| Partial data | `available` (§8) | None needed | N/A | Yes, next `GET` |
| Duplicate trigger calls (any combination of §5's triggers, same identity) | Unaffected — AS-4 deterministic regardless | N/A — dedup concern (§10/§11) | In-process lock reduces waste; AS-4 guarantees correctness even without it | No — each `GET` reads current state independently |
| Worker/process crash | Unchanged — nothing persisted (AS-3) | Same as timeout | None needed (§15) | No |
| Process/deployment restart | Unchanged | Same as timeout | Same as crash | No |
| Cancellation (client disconnect from triggering request) | Unaffected | N/A — task continues to conclusion | N/A | No |
| **Ticker only ever `GET`-queried, and §4.4 is not approved / user never revisits** | Stays `not_yet_acquired` indefinitely | **None** | None — the named, undecided residual gap (§9.2, §20 scenario 8) | Yes — client sees `not_yet_acquired` on every request |

## 22. Architecture Boundaries (conceptual only)

- **Acquisition capability:** the shared `acquire(identity)` use case
  (§6) — application layer, owned by none of its callers.
- **Triggers:** §5's four peer entry points, each calling into the
  capability, none subordinate to another.
- **Acquisition state:** unchanged from Document 35 §9.
- **Provider abstraction / persistence:** unchanged from Round 2.
- **Eventing:** structured logs + trace spans, not a new pub/sub system.
- **API/application layer:** `GET /financials` — pure read, permanently
  unaffected by this document. §4.4 (if approved) — a second, narrow,
  authenticated write route whose only job is invoking the shared use
  case.
- **Background execution:** in-process `asyncio.create_task`,
  non-durable, untracked — selected deliberately per §9.3, not by
  default.

## 23. Rejected Alternatives

- **`GET /financials` as trigger (Round 1)** — rejected by CTO review;
  remains rejected.
- **Acquisition as an implicit side effect of report generation only
  (Round 2's framing)** — corrected this round (§6); §4.1 is retained as
  a trigger but no longer described as acquisition's owner.
- **Direct reuse of the `Job` mechanism** — rejected, unchanged (wrong
  shape: user-scoped, streamed, has a genuine in-progress state).
- **Startup/prewarming of all tickers** — rejected, unchanged.
- **Queue/worker infrastructure** — rejected, unchanged evidentiary
  basis (§4.7).
- **Redis-based distributed lock** — rejected; AS-4 makes correctness
  independent of coordination (§11).
- **Treating a scheduler as unconditionally unnecessary** — **not
  rejected outright this round** — named as the explicit fallback if
  §4.4 is declined (§4.6, §20).
- **Declaring the financials-only-user gap acceptable by default because
  AS-3 makes it safe** — explicitly rejected as reasoning; safety and
  liveness are different properties (§9), and this document does not
  make that determination unilaterally (§20).

## 24. Risks

| Risk | Assessment |
|---|---|
| **The recommended dedicated endpoint (§4.4) requires separate API-governance approval** it does not itself grant | Blocked on the explicit five-step sequence in §4.4 — CTO ratification of this document, then explicit approval to reopen Document 33's governance, then a Document 33 amendment, then an API contract review, only then implementation. If declined, §4.6 (scheduler) is the named fallback, or the residual gap (§9.2, §21) stands |
| **Client polling is a UX observation mechanism, not backend retry ownership** — a future implementer could mistakenly build backoff/rate-limit/timeout logic into the frontend | Explicitly forbidden (§4.4, §12) — those remain server-side concerns; named here so the distinction survives into implementation planning |
| **V1 execution is intentionally non-durable** — an in-flight acquisition attempt is lost on process crash or restart | Deliberate, not accidental (§9.3's explicit invariant) — safe under AS-3, but real; a future scheduler/worker (§4.6/§4.7) is the evidence-driven remedy if this proves insufficient |
| **AS-5 leaves a safe but potentially non-converged two-write window** (`FinancialStatement` exists, acquisition state stays previous) if the second write fails after the first succeeds | Named precisely in §20 Scenario 7 — AS-5 is ordering, not atomicity; no reconciliation mechanism is designed here |
| **V1 provides trigger-driven liveness, not globally guaranteed eventual acquisition** — an identity whose only trigger ever fired is §4.1/§4.3 and then never fires again has no guaranteed retry | The core residual liveness gap this round surfaces explicitly (§9.2) rather than hiding behind AS-3's safety guarantee |
| **A future scheduler/worker remains an evidence-driven scaling option**, not a v1 requirement | Named as the fallback/backstop (§4.6, §4.7); not built without evidence of need, per standing "smallest architecture" discipline |
| Crash mid-attempt loses that attempt's completion observability event | Named in §9.3 point 9 — a real, minor observability gap |
| `reap_stale()` still not wired to run periodically anywhere | Pre-existing `Job`-system gap, unrelated to this document's own scope, flagged for awareness (§3, §25) |
| No backoff policy exists for rate-limit handling | Unchanged Engineering Question (§12, §25) |

## 25. Remaining Open Questions

**Engineering Questions (genuinely undecided):**

- Exact provider-call timeout duration (§7, §13).
- Whether rate-limit pressure ever justifies a backoff/cooldown policy
  (§12).
- The exact client-side polling interval/cap for §4.4 (a frontend/UX
  decision, not this document's to make).
- Whether §4.6's scheduler is ever built as a backstop, and under what
  evidence threshold (§4.6, §20 scenario 2).
- Whether `reap_stale()` should be wired to a periodic caller in
  production — a pre-existing, adjacent `Job`-system gap (§3), not
  created by or the responsibility of this document.
- The exact mechanism for threading a correlation identifier from any
  trigger into an `acquire()` task that outlives it.

**A governance decision this document depends on, named explicitly, not
silently assumed:**

- Whether the CTO approves reopening the narrow question of whether a
  second, dedicated, acquisition-triggering endpoint may exist alongside
  `GET /financials` (§4.4). This document recommends approval; it does
  not treat approval as already granted. §20's scenario 2 and 8 are the
  concrete cases this decision resolves.

## 26. Implementation Prerequisites

1. Orchestration ownership — **resolved, corrected to a shared-capability
   model** (§6).
2. Trigger(s) — **resolved as multiple peers; the primary recommended
   trigger for organic financials-only users (§4.4) depends on an
   explicit, named governance approval this document does not itself
   grant** (§4.4, §25).
3. Execution durability — **resolved (in-process fire-and-forget
   retained), justified against ten explicit dimensions rather than by
   precedent citation alone** (§9.3).
4. Safety — **unchanged, fully guaranteed by Document 35** (§9.1).
5. Liveness — **explicitly analyzed as a distinct property; strong for
   the active-user case if §4.4 is approved, honestly weak otherwise**
   (§9.2).
6. Provider invocation, outcomes, idempotency, concurrency, cancellation,
   crash recovery, partial acquisition, eventing, observability,
   security, API boundary — **all resolved, carried forward from Round
   2 with corrections noted above** (§7-§19, §22).

**What remains before M8 endpoint implementation can begin:** the
separate CTO governance decision on whether to reopen Document 33's
API-governance scope; the resulting narrow Document 33 amendment if
approved; the API contract review for the new endpoint; Document 35's
own still-open items; and this document's Engineering Questions (§25).

**M8 implementation remains BLOCKED. Document 36 alone authorizes
none of the following:** an endpoint, a schema, a repository, a
provider adapter, a worker, a scheduler, production code, or test
changes.

## Governance Addendum — CTO Ratification Record

- **Date:** 2026-08-10
- **Round:** 4
- **Decision:** CTO RATIFIED
- **Scope:** the orchestration architecture in this document only —
  trigger model (§4-§6), execution model (§9.3), safety/liveness
  analysis (§9), and all downstream sections (§7-§22) as written in
  Round 4. Nothing about this ratification reopens, rewrites, or
  reinterprets that content.
- **Implementation:** remains 🔴 **BLOCKED.** Ratifying this document is
  not itself an implementation authorization.
- **`GET /companies/{ticker}/financials` remains strictly read-only** —
  unaffected by this ratification, exactly as §2 and §5 already
  establish.
- **The dedicated Financials acquisition-request endpoint (§4.4) remains
  conditional** on the governance step below — ratifying this document
  does **not** approve the endpoint's existence.
- **This ratification does not itself amend Document 33.** Document 33
  remains frozen and untouched. The next required decision is a
  **separate, explicit CTO decision** on whether to reopen Document 33's
  API-governance scope to permit a second, acquisition-triggering
  endpoint.

**Governance sequence (unchanged from §4.4, restated here as the
authoritative record of where this document's approval sits within
it):**

1. **Document 36 CTO ratification — NOW COMPLETE** (this addendum).
2. A separate, explicit CTO decision to reopen the narrow
   API-governance question in Document 33 — **not yet made.**
3. If approved, a narrow amendment to Document 33 covering only the new
   acquisition-request endpoint — Document 33's existing `GET`
   contract is not otherwise reopened.
4. An API contract review of the new endpoint's own contract (request/
   response shape, auth, error behavior — not defined in this
   document).
5. Only after step 4's approval may implementation begin.

Steps 2-5 remain outstanding. Nothing in this addendum performs any of
them.

---

*Companion documents:
[`35_M8_Acquisition_State_Architecture_Decision.md`](35_M8_Acquisition_State_Architecture_Decision.md) (binding, unmodified) ·
[`34_M8_Acquisition_State_Architecture_Risk_Review.md`](34_M8_Acquisition_State_Architecture_Risk_Review.md) (unmodified) ·
[`32_M8_Pre_Implementation_Decision_Pack.md`](32_M8_Pre_Implementation_Decision_Pack.md) (unmodified) ·
[`33_M8_Financials_API_Contract_Review.md`](33_M8_Financials_API_Contract_Review.md) (frozen; §4.4 recommends, but does not itself make, a narrow proposal to extend its governance scope) ·
`backend/agents/company_index.py`, `backend/agents/ingest.py`,
`backend/server.py:634-637,360,1085,1418,1645-1649`, `backend/application/jobs.py`.*

*This document records the CTO-ratified M8 acquisition orchestration
architecture. It does not authorize implementation and does not amend
Document 33 or authorize the proposed acquisition-trigger endpoint.*

---

## Orchestration architecture: CTO RATIFIED (Round 4). M8 implementation remains BLOCKED pending the governance sequence recorded above.
