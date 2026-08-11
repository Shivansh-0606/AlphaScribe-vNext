# Document 33 Amendment — Financials Acquisition Request Endpoint

**Status:** 🟡 **PROPOSED — AWAITING CTO APPROVAL.** This is a
**governance amendment proposal**, not an amendment itself. It does not
modify Document 33, Document 35, or Document 36. If approved, Document
33 would be updated separately, narrowly, to incorporate the contract
proposed here — that update is not performed by this document.
**Date:** 2026-08-10
**Proposed following:** the CTO's recommendation to reopen Document 33's
governance scope, as contemplated by Document 36 §4.4 step 2. **Formal
reopening remains subject to explicit CTO approval recorded
separately** — this document does not claim that reopening has already
occurred.
**Builds on (binding, not reopened):** [`33_M8_Financials_API_Contract_Review.md`](33_M8_Financials_API_Contract_Review.md),
[`35_M8_Acquisition_State_Architecture_Decision.md`](35_M8_Acquisition_State_Architecture_Decision.md),
[`36_M8_Acquisition_Orchestration_Architecture.md`](36_M8_Acquisition_Orchestration_Architecture.md),
[`32_M8_Pre_Implementation_Decision_Pack.md`](32_M8_Pre_Implementation_Decision_Pack.md).
**Does not:** implement the endpoint, modify production code, modify
frontend code, modify Documents 33/35/36, create schemas, create
repositories, implement orchestration, freeze a contract without further
CTO approval, or authorize M8 implementation. Production implementation
remains **BLOCKED** regardless of this proposal's outcome.

---

## 1. Purpose

**Why the endpoint exists.** Document 36 §9.2 (ratified) establishes
that v1 acquisition liveness is trigger-driven, not globally guaranteed
— an identity only gets another chance to reach a terminal state when a
legitimate trigger fires (§5 there). The existing triggers
(`POST /report`/`POST /explain`'s ingestion step, an internal/ops
command) all require the user to have taken an *unrelated* action
(generating a report) before financial-statement acquisition is ever
attempted for their ticker. This endpoint closes that gap by giving the
Financials feature its own, directly-owned trigger.

**What user/product problem it solves.** A user whose only interest is
a ticker's financial statements has, under the existing trigger set, no
way to cause acquisition to happen at all — they would see
`not_yet_acquired` indefinitely (Document 36 §21's named residual risk).
This endpoint gives that user's client an explicit, idempotent way to
ask AlphaScribe to attempt acquisition for the ticker they are actually
looking at.

**Why `GET /financials` cannot perform this mutation.** Document 33 §4
and Document 35's AS-0-AS-5 establish `GET /financials` as strictly
read-only by design — not merely "not synchronously blocking," per
Document 36 Round 2's explicit correction. A read endpoint that silently
mutates state (even asynchronously) conflates two different HTTP
semantics and was rejected outright in Document 36's own revision
history. A **separate** endpoint is the only way to request a mutation
without compromising that boundary.

**Why the endpoint belongs within the approved architecture.** It
invokes exactly the same shared `acquire(identity)` use case Document 36
§6 already defines as an independently-owned application capability with
multiple peer triggers — this endpoint is simply one more peer, not a
new concept. It introduces no new acquisition-state semantics (Document
35 is unchanged), no new orchestration mechanism (Document 36's
in-process fire-and-forget execution model, §9.3, is reused unchanged),
and no new infrastructure.

**A grounding fact from the current repository, not previously part of
this record:** `web/features/company-research/ui/FinancialsSection.tsx`
is the only existing Financials UI surface today, and it is a **pre-M8
interim placeholder** — its own code comment states "the frozen
`StatementTable` (multi-period Income/Balance/Cash Flow) has no backend
data source at all... No backend scope was added for this phase." It
renders only a single-period LLM-extracted snapshot tied to an existing
report (`useReport(jobId)`, gated on a `?job=` query param) and shows a
static "isn't available yet" banner where multi-period statement data
would go. **As shipped today, there is no reachable UI path to a
financials-only view that bypasses report generation** — but this is
because the M8 integration doesn't exist yet, not because the intended
design forecloses it: Document 33 §8 already cites the *frozen*
`StatementTable` design (`05_Content_Data_Display.md` §"States",
Loading/Available/Partial-Failure) as the target UI, and that design is
independent of any report. This amendment evaluates the endpoint against
that frozen target design, not against today's interim placeholder —
the organic-user gap Document 36 identifies is a property of the
*intended* product surface, confirmed by the already-frozen design doc,
not an assumption this review invents. This is noted for completeness,
not as a reason to delay: it does not weaken the case for the endpoint,
but it does mean the endpoint's practical value is realized once the
`StatementTable`/`GET /financials` integration is actually built —
itself still gated behind this whole governance sequence.

## 2. HTTP Semantics

| Aspect | Determination | Evidence |
|---|---|---|
| **Method** | `POST` | Mutating/triggering action; matches this codebase's existing convention for action endpoints (`POST /reports/{job_id}/cancel`, `POST /learning/{id}/cancel` — both action-suffixed `POST`s on an existing resource path) |
| **Path** | `POST /companies/{ticker}/financials/acquire` | Verb-suffix convention, matching `/cancel`'s existing shape, and matching the shared use-case's own name (`acquire()`, Document 36 §4.1). Prefer the verb `acquire` over the noun `acquisition` in the governance-scope sketch — reduces conceptual drift from Document 36's own vocabulary. Unversioned `/api/...` prefix, matching Document 33 §9 (unchanged) |
| **Idempotency (HTTP sense)** | Not idempotent by HTTP's strict definition (each call may schedule work), but **safe to call repeatedly without corrupting state** — correctness comes entirely from Document 35 AS-4, exactly as Document 36 §10 already establishes. No second idempotency model is introduced |
| **Success status** | **Proposed success status: 200, subject to the later API contract review** — not 202 | No `202 Accepted` pattern exists anywhere in this codebase today (`server.py` — confirmed by direct inspection); every existing fire-and-forget `POST` (`/reports/generate`, `/learning/explain`) returns **200 with a small acknowledgment body** (`{"job_id": ...}`). A 202 would also imply a trackable resource this endpoint deliberately does not expose (Document 36 §4.4 — not a status endpoint). 200 matches existing convention and doesn't overclaim. **This document does not freeze the final wire-level HTTP contract** — 200 is this proposal's recommendation, not a decided outcome; the API contract review (§ Required Governance Decision, step 4) makes the final call |
| **Failure statuses** | 401, 422, 429, 502 — see §9 | Reuses `domain/errors.py`'s existing hierarchy exactly, no new status code introduced |

## 3. Request Contract

**Minimum required information — mirrors `GET /financials` exactly,
adds nothing:**

```
POST /companies/{ticker}/financials/acquire?period_type=annual|quarterly
```

- `ticker` — path parameter, same normalization as `GET` (uppercase,
  server-side).
- `period_type` — **required** query parameter, `annual` or `quarterly`,
  no default — identical rule to Document 33 §6.1's already-frozen `GET`
  parameter, reused rather than reinvented.
- **No request body.** No `statement_type` selector, no force-refresh
  flag, no provider hint, no scope override. One call requests
  acquisition for whichever of the three statement types (income,
  balance_sheet, cash_flow) implied by `(ticker, period_type)` are
  currently `not_yet_acquired` — the same batch scope Document 36 §5's
  diagram already establishes for this trigger. Exposing `statement_type`
  as a separate, callable parameter would leak internal acquisition
  granularity the Critical Boundary explicitly prohibits ("arbitrary
  acquisition scopes") — rejected on that basis, not merely omitted.

## 4. Response Contract

**What the caller actually needs to know, nothing more:**

| Signal | Meaning | Why it's included / excluded |
|---|---|---|
| `requested` | One or more relevant identities are currently eligible for acquisition and the acquisition request has been **accepted for processing**. The response does **not** expose whether a new task was created, whether an existing in-flight attempt already covers the identity, or whether an efficiency lock suppressed duplicate work | The caller's actionable signal — "check back later." **`requested` does not mean a new task was definitely created, does not mean acquisition has started, does not mean acquisition succeeded, and does not expose any internal in-flight state.** The endpoint remains a request trigger, not a status endpoint |
| `available` | All relevant identities are already `available` — nothing was scheduled | Lets the client skip triggering and read immediately via `GET`; echoes information `GET` already exposes, nothing new |
| `confirmed_unavailable` | All relevant identities are already `confirmed_unavailable` — nothing was scheduled (refresh is explicitly out of scope, ADR-029 §18 item 4) | Same reasoning as `available` — an echo, not new information |
| `mixed` | No relevant identity is `not_yet_acquired`, and the terminal states present are a combination of `available` and `confirmed_unavailable` — nothing was scheduled | Reuses Document 33 §3.2's existing per-statement-type response shape — the caller should simply re-read via `GET`, which already reports each statement type independently (R8, unchanged) |

**Deterministic response precedence** (evaluated in this exact order
over the relevant identities implied by `(ticker, period_type)`):

1. **If any relevant identity is `not_yet_acquired` → outcome =
   `requested`.** This takes precedence over every other case,
   regardless of what the other identities' states are.
2. **Else if all relevant identities are `available` → outcome =
   `available`.**
3. **Else if all relevant identities are `confirmed_unavailable` →
   outcome = `confirmed_unavailable`.**
4. **Otherwise → outcome = `mixed`.** Reached only when no identity is
   `not_yet_acquired` and the terminal states present are a genuine
   combination of `available` and `confirmed_unavailable`.

No fifth or additional public state is introduced — this is a
precedence rule over the same four signals already defined above, not a
new concept.

**Example (precedence rule 1 applies):**
```
income        = available
balance_sheet = not_yet_acquired
cash_flow     = confirmed_unavailable
→ outcome = requested
```

**Example (precedence rule 4 applies):**
```
income        = available
balance_sheet = confirmed_unavailable
cash_flow     = available
→ outcome = mixed
```

**Deliberately excluded — per the Critical Boundary:**
- **"Already acquiring"** as a distinct signal. Distinguishing "just
  scheduled" from "someone else's attempt is already in flight" would
  require exposing the in-process lock/task state Document 36 §9-§11
  frame as an internal efficiency optimization only — not a public
  concept. Both cases are correctly served by the same `requested`
  response; the caller's next action (poll `GET`) is identical either
  way.
- Any acquisition/job identifier, attempt count, provider name, or
  timestamp of the eventual outcome — all internal (Document 36 §17-§19,
  unchanged).
- The eventual provider outcome itself. This endpoint's response is
  computed **synchronously from state visible at request time only** —
  it never blocks on or reports the asynchronous attempt's result
  (Document 36 §9.3's fire-and-forget model, unchanged). A provider
  failure, timeout, or rate limit that occurs *after* the response is
  sent is invisible to this response by construction, exactly as
  Document 36 §8/§21 already establish for every other trigger.

**No wire-level schema (field names, exact JSON shape) is finalized
here** — per this task's explicit instruction, that belongs to the later
API contract review (§ Required Governance Decision, below).

## 5. Authorization

- **Authentication:** `current_user`, identical to `GET /financials` —
  no weaker, no stronger.
- **Authorization:** none beyond authentication — this endpoint acts on
  the same shared-corpus data as `GET /financials` (Document 33 §7,
  unchanged: no per-user ownership dimension on `companies`, `filings`,
  `financial_statements`, or acquisition state). Any authenticated user
  may request acquisition for any ticker, exactly mirroring who may
  `GET` any ticker's financials — the endpoint introduces no new
  authorization decision to make.
- **Ownership boundary:** identical to `GET /financials` — none exists,
  none is introduced.
- **Abuse prevention:** see §7 (Rate Limiting).

## 6. Idempotency

**Aligned exactly with Document 36 — no second acquisition model is
introduced.** The endpoint's own idempotency behavior, per repeat-call
scenario:

| Scenario | Behavior |
|---|---|
| Repeated while an identity is `not_yet_acquired` (whether or not an attempt happens to already be in flight) | Each call is safe; may schedule another attempt or fold into the in-process lock's dedup (Document 36 §9, efficiency-only) — response is `requested` either way. Correctness is AS-4's job, not this endpoint's |
| After successful acquisition (`available`) | **No new attempt is scheduled.** The endpoint short-circuits and returns `available` — re-attempting could not change a sticky `available` result (AS-4) and would only waste a provider call |
| After `confirmed_unavailable` | **No new attempt is scheduled.** A deliberate re-check is explicitly a refresh-policy question, out of scope (ADR-029 §18 item 4, unchanged) — this endpoint does not reopen that question through the back door. Returns `confirmed_unavailable` |
| From concurrent users, same ticker | Handled identically to any other concurrent trigger — AS-4 for correctness, the in-process lock for efficiency (Document 36 §9-§11, unchanged) |

This means the endpoint only ever actually schedules work for
identities still `not_yet_acquired` — it is not a generic "re-run
acquisition" or force-refresh action, consistent with the Critical
Boundary and with §1's stated purpose.

## 7. Rate Limiting / Abuse

**Reuses the existing in-memory rate-limiter exactly — no new
infrastructure.** `agents/auth.py`'s `is_rate_limited`/`record_hit`
pattern (already used for login and password-reset OTP, keyed by a
string, process-local, 429 on limit) is directly applicable here: key by
something like `f"acquire:{user_id}:{ticker}:{period_type}"` (exact key
shape is an implementation detail, not decided here) without introducing
Redis, a distributed limiter, or any new dependency — matching this
codebase's own documented posture that the existing limiter is "fine
for the single-instance backend" (CLAUDE.md). No speculative
infrastructure is introduced.

**Scope of this protection, stated precisely:** the proposed per-user/
per-ticker/per-period key protects against repeated request
amplification for the *same* acquisition target. **It does not by
itself establish a global per-user acquisition budget across arbitrary
tickers** — a user requesting acquisition for many different tickers in
quick succession would not be throttled by this key alone. A global
budget remains an implementation/operational question and is not
designed by this governance proposal; this document proposes a single,
narrowly-scoped limiter as the minimum precedent-consistent protection,
not a complete abuse-prevention system.

## 8. Observability

**Reuses M6 exactly — no redesign,** consistent with Document 36 §17-§18:

- **Correlation ID:** inherited from the existing automatic
  correlation-ID/structured-logging middleware on the incoming request
  — no new scheme.
- **Acquisition/job identifier exposure:** **none.** This endpoint does
  not expose an identifier for the triggered attempt, consistent with
  Document 36 §4.4's "not a status endpoint" boundary and with the
  Critical Boundary's explicit exclusion of "acquisition history
  management."
- **Metrics:** one new labeled counter (e.g.
  `acquisition_request_total{outcome}`), following the existing
  `llm_calls_total`-style family (Document 36 §18) — outcome labels
  matching §4's response signals (`requested`/`available`/
  `confirmed_unavailable`/`mixed`).
- **Tracing/structured logging:** server-side only, via the same
  `get_tracer()` convention already used elsewhere — never surfaced
  through the public response body.

## 9. Error Semantics

| Case | External behavior | Why |
|---|---|---|
| Unauthenticated request | **401** | Existing `current_user` dependency behavior, unchanged from `GET` |
| Unauthorized request | **N/A — not a distinct case** | No ownership dimension exists on this data (§5); nothing to be unauthorized *for* beyond authentication |
| Missing/invalid `period_type` | **422** | Identical to Document 33 §5 rows 1-2 (existing FastAPI/Pydantic automatic validation, no bespoke logic) |
| Invalid ticker (malformed, not "doesn't exist") | **422**, matching the `period_type` case — basic format validation only | No stronger validation is introduced than what already governs the path |
| Company/ticker not found (unknown to AlphaScribe) | **Not a rejection case — request is accepted (200, `requested`)** | Mirrors Document 33 §5 row 5's precedent exactly (`GET /filings` never gates on ticker existence); rejecting genuinely new tickers would defeat this endpoint's own purpose — a new-to-AlphaScribe ticker is exactly the case that should be attempted. **Ticker existence is intentionally not validated as a prerequisite to accepting the acquisition request; eventual provider/application outcome determines whether the identity becomes terminal.** No new ticker-existence lookup is introduced |
| Acquisition already in progress | **Not distinguished — 200, `requested`** | §4/§6 — no internal in-flight state is exposed; idempotent regardless |
| Data already available | **200, `available`** | §4 — a useful, non-leaking echo of existing public state |
| Provider unavailable (during the async attempt) | **Not visible to this endpoint's response at all** | The response is computed before the async attempt runs (§4, §9.3 of Document 36); this case only ever becomes visible via a later `GET` |
| Rate-limited | **429** | Reuses the existing `RateLimitedError` → 429 convention (Document 33 §5 row 4's sibling pattern; §7 above) |
| Unexpected internal failure (e.g. the synchronous state read fails) | **502** | Matches the existing `InfrastructureError` → 502 convention (Document 33 §5 row 4, unchanged) — internal failure detail stays server-side, never leaked in the response body |

## 10. Frontend Compatibility

**No frontend code is modified by this proposal.** Findings from
inspecting the existing frontend (§1, repeated here for this section's
own record):

- `FinancialsSection.tsx` today has zero integration with
  `GET /companies/{ticker}/financials` or any acquisition-triggering
  endpoint — it is a pre-M8 placeholder built around a single-period
  LLM-extracted snapshot tied to an existing report.
- The **frozen** target design (`05_Content_Data_Display.md`
  `StatementTable`, cited by Document 33 §8) already anticipates a
  Loading/Available/Partial-Failure UI independent of any report — this
  endpoint is designed to fit that already-frozen target, not to invent
  a new workflow.
- The natural integration point (not built here, not designed in
  wire-level detail): the frozen `StatementTable`, upon rendering
  `not_yet_acquired` from `GET /financials`, would call this endpoint
  once, then continue polling `GET /financials` per Document 36 §4.4's
  already-ratified observation model — polling informs the UI when to
  re-render, it does not itself retry anything.
- This proposal **does not require or imply any change to the currently
  approved experience** — the existing `StatementTable` design already
  anticipated exactly this need; this endpoint is what makes that design
  implementable, not a redesign of it.

## 11. Security

Verified against each required property:

- **Cannot bypass `GET` authorization** — identical `current_user`
  dependency, no alternate auth path.
- **Cannot expose acquisition internals** — §4 deliberately excludes
  in-progress state, attempt identifiers, and provider outcome details.
- **Cannot trigger acquisition for unauthorized resources** — no
  resource-ownership dimension exists to bypass (§5); every
  authenticated user has identical access, mirroring `GET`.
- **Cannot leak provider credentials** — not applicable; yfinance and
  the BSE fetch path remain credential-free (reconfirmed, Document 36
  §3/§19).
- **Cannot bypass cache ownership rules** — SI-1's no-owner-scoping
  classification for shared-corpus data (`10` §4.5) is unaffected; this
  endpoint writes through the same two repository boundaries Document 35
  already scoped, nothing new.

---

## Required Governance Decision

**Governance sequence (unchanged from Document 36 §4.4; restated here as
the authoritative record of where this proposal sits within it):**

1. **Document 36 CTO ratification — COMPLETE.**
2. A separate, explicit CTO decision to reopen the narrow
   API-governance question in Document 33 — **not yet made. This
   proposal does not perform or claim step 2.**
3. If approved, a narrow amendment to Document 33 covering only the new
   acquisition-request endpoint — Document 33's existing `GET` contract
   is not otherwise reopened.
4. An API contract review of the new endpoint's own contract (request/
   response shape, auth, error behavior — proposed here, not frozen).
5. Only after step 4's approval may implementation begin.

**This document is a recommendation submitted for step 2 — it is not
itself step 2.** Steps 2-5 all remain outstanding.

### Existing frozen rule

Document 33 currently defines `GET /companies/{ticker}/financials` as
the **sole, read-oriented, strictly read-only** endpoint for this
feature — "MUST NOT synchronously call yfinance," "no provider
acquisition during the request lifecycle." Document 33 does not
authorize any second endpoint; its frozen contract makes no provision
for a client to request acquisition at all. This is what currently
prevents the endpoint proposed here from existing.

### Narrow exception / amendment

Reopen Document 33 **only** to authorize the existence of one
additional endpoint — `POST /companies/{ticker}/financials/acquire`
(§2-§4 above) — whose sole function is to invoke the shared
`acquire(identity)` use case (Document 36 §6) for the caller's
requested `(ticker, period_type)`. **`GET /financials`'s existing frozen
contract is not reopened, reworded, or reinterpreted in any respect.**
No other Document 33 provision changes.

### Proposed endpoint

```
METHOD:           POST
PATH:             /companies/{ticker}/financials/acquire
AUTH:             current_user (identical to GET)
QUERY PARAM:      period_type = annual | quarterly, REQUIRED, no default
REQUEST BODY:     none
SUCCESS:          200 (proposed, subject to the later API contract
                  review — not frozen by this document), body
                  communicates one of:
                    requested | available | confirmed_unavailable | mixed
ERRORS:           401 (unauthenticated) · 422 (missing/invalid period_type
                  or malformed ticker) · 429 (rate-limited) ·
                  502 (unexpected internal failure)
NOT EXPOSED:      acquisition/job identifiers, in-progress state,
                  attempt history, provider outcome details, provider
                  selection, retry/backoff controls, internal
                  persistence details
VERSIONING:       existing unversioned /api/... convention (unchanged)
```

Exact JSON field names are explicitly **not** frozen by this proposal —
left to the API contract review named in the sequence below.

### Scope boundary

**May:** accept a request for one `(ticker, period_type)`; read current
acquisition state for the implied identities; schedule acquisition
attempts for whichever are `not_yet_acquired`, via the existing shared
use case; respond with one of the four signals in §4.

**May not:** accept a `statement_type` or any other scope-narrowing/
widening parameter; expose, accept, or mutate any internal acquisition
mechanism (provider choice, retry policy, worker/lock state, attempt
counters); serve as a status/history endpoint; trigger a re-check of an
already-terminal identity (no refresh); become a general
acquisition-management surface of any kind.

### Architectural alignment

- **Document 35:** consumes the identity model, the three public
  states, and AS-0-AS-5 exactly as ratified — introduces no new state,
  no new invariant, no reinterpretation.
- **Document 36:** this endpoint **is** the §4.4 trigger Document 36
  already recommended and reasoned through in full (ownership model
  §6, execution model §9.3, idempotency §10, concurrency §11, retry/
  polling boundary §12, error mapping §8). Nothing in this proposal
  adds a decision Document 36 didn't already make — it operationalizes
  §4.4 into a concrete wire contract, consistent with the governance
  sequence Document 36 itself specified.

### Security model

Detailed in §5 and §11 above: identical authentication to `GET`, no
authorization dimension (shared corpus, unchanged), no credential
exposure, no cache-ownership impact, no internal-state leak.

### Compatibility

`GET /financials`'s existing contract, response shape, and error
behavior are **entirely unchanged** — this is an additive endpoint, not
a modification to any existing one. No frontend code changes are
required by this proposal to remain consistent (§10) — the endpoint is
designed to fit the already-frozen `StatementTable` target design, not
to require a new one.

### Rejected alternatives

- **GET-triggered acquisition** — rejected. This is precisely what
  Document 36 Round 1 proposed and the CTO rejected outright; reopening
  it here would contradict a already-ratified decision. `GET` remains
  strictly read-only under this proposal, unconditionally.
- **Frontend-only retry** — rejected as a complete solution. A frontend
  polling loop with no backend trigger to call has nothing to invoke —
  Document 36 §9.2/§12 already establish that polling is an observation
  mechanism, not a retry engine; it requires *something* to explicitly
  request against. This endpoint is that something; a frontend-only
  approach without it cannot close the organic-user gap at all.
- **Automatic background acquisition without explicit request** — i.e.
  a scheduler (Document 36 §4.6). Not rejected outright — Document 36
  already names this as the fallback if this endpoint is declined, and
  a plausible future backstop regardless. Not proposed here because it
  requires new infrastructure (a periodic loop) this codebase doesn't
  currently have, on evidence that doesn't yet justify it (Document 36
  §4.6, unchanged) — the dedicated endpoint is the narrower, cheaper,
  already-evidenced-as-precedented option and is preferred for that
  reason, not because the scheduler is architecturally wrong.
- **General acquisition-management API** (status endpoint, history
  endpoint, retry-control endpoint, provider-selection endpoint) —
  rejected explicitly and repeatedly throughout this proposal (§4, §9,
  Scope boundary above) — directly contrary to the Critical Boundary
  this task itself specified, and to Document 36 §4.4/§4.5's own framing
  of the endpoint as a narrow request trigger only.

---

## Recommendation

### APPROVE NARROW API-GOVERNANCE AMENDMENT

The endpoint is narrowly scoped, introduces no new architecture beyond
what Documents 35 and 36 already ratified, reuses existing patterns
end-to-end (authentication, rate limiting, error conventions, the
fire-and-forget execution model), and closes a real, already-identified
gap without expanding into a general acquisition-management surface.
**This document recommends that the CTO approve reopening Document 33
narrowly for this one endpoint's contract (governance step 2, above). It
does not itself grant that approval, does not freeze the endpoint's
wire-level schema, and does not authorize implementation.** Steps 2-5 of
the governance sequence above all remain outstanding.

---

*Companion documents:
[`33_M8_Financials_API_Contract_Review.md`](33_M8_Financials_API_Contract_Review.md) (frozen; the narrow amendment this proposal recommends targets it, but does not itself modify it) ·
[`35_M8_Acquisition_State_Architecture_Decision.md`](35_M8_Acquisition_State_Architecture_Decision.md) (binding, unmodified) ·
[`36_M8_Acquisition_Orchestration_Architecture.md`](36_M8_Acquisition_Orchestration_Architecture.md) (ratified, unmodified — this proposal operationalizes its §4.4) ·
`web/features/company-research/ui/FinancialsSection.tsx` (frontend evidence, unmodified) ·
`backend/agents/auth.py` (rate-limiter precedent, unmodified) ·
`backend/server.py:979-1110,1347-1425` (existing POST/action-endpoint conventions, unmodified).*

*This proposal does not itself amend Document 33, does not authorize
implementation, and does not freeze any wire-level contract. M8
implementation remains BLOCKED.*
