# Post-M6 Engineering Roadmap Reconciliation

**Status:** Research/audit only — no code changed, per this task's own constraint.
**Date:** 2026-08-08
**Governed by:** Backend Architecture v1.0 (`06`–`11`, 🔒 frozen) · Product Roadmap v1.0.0
(`master-plan/03_Feature_Roadmap.md`, 🧊 frozen) · `17_M4_Backend_Capability_Roadmap_Reconciliation.md`
(the current reconciled roadmap this document supersedes for sequencing purposes)
**Predecessor:** M6 Observability Hardening — Base ✅, Doc 26 ✅ Approved with Changes,
Fast-Follow Round 1 ✅, Fast-Follow Round 2 ✅. **Overall M6: APPROVED / CLOSED.** Not
reopened, not modified by this document.

---

## Method

Nine sources reviewed: Backend Architecture v1.0 (`06`–`10`), the M2 Implementation
Charter (`12`), `17`'s Backend Capability & Roadmap Reconciliation and its appended
AI Platform Evolution Roadmap (`17` §7), the ADR Index (`11`), the M5/EQ-3 report
(`18`), M6/Document 26 (`26`) and the fast-follow record (`27`), the current backend
repository (direct read of `server.py`, `app/`, `agents/`, `infrastructure/`,
`application/`, `domain/`, plus a live grep for Docker/CI files), and current frontend
integration (`web/features/*`, `web/lib/api/`, `docs/governance/Feature_Parity_Tracker.md`,
`docs/frontend_architecture/`).

**Key sequencing fact governing this whole document:** `17` already performed the
reconciliation the current brief is asking for once before — it explicitly noted that
the *original* Phase 0–7 migration-phase ordering (from `06 §7`/`12`) does not fully
describe what actually happened, and produced its own **5-milestone roadmap** (M5→M6→M7→M8→M9)
derived from capability gaps rather than phase numbers. M5 and M6 have since executed
and closed. Per this task's own instruction not to assume the original phase ordering
still governs, `17`'s roadmap — not `12`'s Phase 5/6/7 checklist — is treated as the
current source of truth for "what's next." Where the two disagree, that disagreement is
itself reported in §C, not silently resolved in either direction.

---

## A. Completed Work

### Architecture & governance
- Backend Architecture v1.0 frozen (`06`–`10`), ratified 2026-08-03, ADR Index published (`11`, 28 ADRs).
- M2 Implementation Charter's entry conditions (E-1…E-4) satisfied — the architecture package is committed to git (charter-time blocker E-4 resolved; current `git log` head is `6902135`, "backend M2 phase 0-2 + M4-M6: Clean Architecture migration...").

### M2 (implementation)
- **Phase 0** (safety net: contract tests, unit tests, hermetic CI) — ✅ complete (`13`).
- **Phase 1** (app factory scaffolding, `Settings`, `Container`, 7 ports, correlation-id + Prometheus middleware, OTel built) — ✅ complete (`14`). Note: "app factory scaffolding" landed, but `server.py` itself was never refactored into `create_app()` — see D-4 in §B.
- **Phase L** (Learning: 4 routes, 2-node graph, citation post-processing, job lifecycle) — ✅ complete (`15`), confirmed still live and consumed by the frontend (all 4 Learning routes have a frontend caller).
- **Phase 5 substance** (single-provider LLM dispatch, `01 D-3` fix) — ✅ done in substance: `infrastructure/llm/registry.py`'s `dispatch()` is the one dispatch table both `_generate_sync` and `validate_key` share, confirmed by direct read this session. **Not formally closed as a numbered phase** — no `M2_Phase5_*` report exists in the doc index the way Phase 0/1/L each got one. Cosmetic gap, not a functional one.
- **Phase 3/4 substance** (Mongo 25-index migration, Redis EventBus/JobStore/RateLimiter, `01 D-1` fan-out fix) — ✅ done, confirmed live (`app/container.py`'s adapter switch, `infrastructure/mongo/indexes.py`, `infrastructure/redis/*`).
- Company Research backend (M3-track, doc `16`) — ✅ confirmed already-existing + EQ-2 admin-gate closure.
- **M4** — Backend Capability & Roadmap Reconciliation (`17`) — ✅ complete, research-only, produced the current 5-milestone roadmap.
- **M5** — Report-Read Authorization Cutover (EQ-3, `18`) — ✅ complete, **CTO-approved** (confirmed this session).
- **M6** — Observability Hardening (`19`–`27`) — ✅ complete, **CTO-approved through Fast-Follow Round 2** (confirmed this session). Closed items include: OTel tracing activation + LangGraph/SSE/LLM-retry/job-level spans, 11 active Prometheus metrics, correlation-id plumbing (see nuance in §B), `/health` O-12/O-13 fixes, conditional Redis readiness (A2), two corrected stale docstrings (A3), job-span ERROR-status correctness, retrieval-duration exception-path recording, SSE outcome-classification correctness with regression coverage.

### Security
- EQ-2 (`POST /reports/rescore` admin-gated) — ✅ closed (M3).
- EQ-3 (report reads owner-scoped) — ✅ closed (M5). `D-5`, tabled as "❌ Open" in `17` (written *before* M5 executed), is now closed — verified via `18` and this session's own earlier confirmation of M5's CTO approval.
- `SI-1` (cache-hit-is-a-disguised-read invariant) — ✅ promoted into frozen `10` §4.5 as a permanent amendment (v1.0→v1.1), during M6.

### Frontend
- 6 feature domains (`account-setup`, `workspace-home`, `company-research`, `comparison`, `research-library`, `learning`) are all structurally complete (full ui/application/integration/internal/index.ts scaffold) and consume 25 of the 37 backend routes. `Feature_Parity_Tracker.md` is stale on one specific point (still describes Learning's backend as absent) — corrected by `17`'s own cross-reference; Learning's backend has been live since M2 Phase L.

---

## B. Remaining Work

### B-1. Google Social Authentication vs. `CLAUDE.md` — unresolved document conflict

- **Identifier:** Critical finding, `17` §4 (no ID prefix assigned — a document-conflict, not an engineering finding).
- **Original source:** Frozen Product Roadmap `master-plan/03_Feature_Roadmap.md` (line 87, lists "Social Authentication (Google)" as MVP scope) vs. `CLAUDE.md` ("do not add JWT, OAuth, or cloud-SDK auth dependencies").
- **Current repository evidence:** Confirmed this session — zero OAuth code anywhere in `agents/auth.py` or `requirements.txt`; zero OAuth UI/route/client code anywhere in `web/`.
- **Business/user impact:** A frozen MVP feature is permanently unbuilt until resolved.
- **Technical impact:** None if left as-is — the auth system works correctly without it. The risk is entirely in the two frozen documents contradicting each other, not in running code.
- **Dependencies:** None technical. Requires a product/CTO ruling: amend the roadmap (drop it) or amend `CLAUDE.md` (permit one OAuth dependency).
- **Priority:** High-visibility, zero engineering effort until decided.
- **Still required?** Cannot be answered by engineering — this is the one item in this whole reconciliation that is **not a milestone candidate**, by design (per `17`'s own conclusion, reaffirmed here after independent verification).

### B-2. Correlation ID still does not appear in emitted logs — despite A1 being "fixed"

- **Identifier:** Not previously tracked as a distinct ID — a residual piece of `04` O-1 / doc 26 A1.
- **Original source:** `04` O-1 ("no correlation identifier... unattributable with concurrent jobs"); doc 26 A1 fixed the *filter attachment* bug.
- **Current repository evidence (verified this session, not carried forward from a prior claim):** `server.py`'s `logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s")` — confirmed via direct grep just now — **still does not reference `%(correlation_id)s`**. A1's fix made the filter correctly reach every `LogRecord`, but nothing in the active format string prints the field, so **no emitted log line shows a correlation id today**, identical to the situation before A1 was "fixed" — just for a different underlying reason now (format string omission, not filter mis-attachment).
- **Business/user impact:** None directly user-visible; blocks real incident correlation across concurrent jobs.
- **Technical impact:** One-line fix (`format="...%(correlation_id)s: %(message)s"`) — the plumbing (A1) is already correct and tested; only the format string needs the field added.
- **Dependencies:** None.
- **Priority:** **Medium — low implementation effort, meaningful operational value.** The fix itself is trivial (one format-string edit), but correlation IDs are a real incident-response primitive — they're what lets an operator connect a request, a job, a log line, and a trace span into one investigable thread. Trivial-to-implement is not the same as low-value; the low-effort classification this item had before undersold that. Still not a milestone by itself, and still outside M7's mandatory acceptance criteria (see §D and the CTO Recommendation).
- **Still required?** Yes.

### B-3. Pipeline trace events never reach structured logs (`04`/`17` O-2)

- **Identifier:** `O-2`.
- **Original source:** `04` §2.4; carried forward as open in `17` §4 (Medium); scoped into `17`'s original Milestone 6 description ("pipeline-trace-to-log bridge").
- **Current repository evidence:** `server.py`'s `push()` (both research and Learning) — confirmed via direct grep this session — calls `container.job_lifecycle.publish()` and a Mongo `$push`, never `logger.info`. Unchanged by M6's actual execution.
- **Business/user impact:** None directly.
- **Technical impact:** The richest per-job signal in the system stays invisible to any log-based tool. One `logger.info` call inside `push()`.
- **Dependencies:** None.
- **Priority:** Low effort, real value.
- **Still required?** Yes — genuinely not done, despite being named in `17`'s original scope for "Milestone 6." **M6 as actually executed was narrower than `17` originally scoped it** (M6 focused on tracing/metrics/health/readiness correctness rather than the log-format items) — noted here as a scope-drift fact, not a criticism; M6 is closed and not being reopened.

### B-4. JSON structured logging (`04`/`17` O-3)

- **Identifier:** `O-3`.
- **Current repository evidence:** Format string (above) is still the original human-readable string, not JSON.
- **Business/user impact:** None locally; blocking for any hosted log-aggregation deployment.
- **Technical impact:** Deliberately deferred since the original audit ("acceptable for local dev, blocking for any hosted deployment") — no hosted deployment exists yet.
- **Dependencies:** None technical; benefits from B-2/B-3 landing in the same pass (same file, same area).
- **Priority:** Low — no current trigger (no hosted deployment).
- **Still required?** Not yet — genuinely deferrable, consistent with the original audit's own framing, not a gap being ignored.

### B-5. Streaming/Lifecycle test gaps (T-6, T-7, T-10, T-11, T-13, T-14)

- **Identifier:** `T-6` (restart-recovery), `T-7` (`/ingest/pdf` untested), `T-10` (keepalive-after-idle), `T-11` (stream-of-finished-job), `T-13` (cancel-mid-stream event assertion), `T-14` (strict event-ordering assertion).
- **Original source:** `05_Testing_Audit.md`; consolidated and still open per `17` §4.
- **Current repository evidence:** None of these were touched by M6's test additions (M6 added tests for span status, retrieval-duration, and SSE *metric outcome* classification — a different concern from T-13's event-framing assertion). Confirmed by reviewing this session's own test-file diff.
- **Business/user impact:** None currently — these guard against regression, they don't fix a live bug.
- **Technical impact:** Low today, grows over time as the streaming/job-lifecycle code changes without these guards.
- **Dependencies:** None — pure test-writing, no architecture decisions.
- **Priority:** Small effort, real regression protection.
- **Still required?** Yes, and this is the largest fully-ready item in this reconciliation — see §D.

### B-6. Real-Redis verification (`JOB_BACKEND=redis`)

- **Identifier:** Inherited condition from `14`/`15`, restated open in `17` §5.
- **Current repository evidence:** `RedisJobStore`/`RedisEventBus`/`RedisRateLimiter` are built and unit-tested against a real Redis client interface, but the M6 session's own live-suite runs all used the `JOB_BACKEND=memory` default — no run this session exercised the Redis-backed path.
- **Business/user impact:** None today (memory backend is the shipped default).
- **Technical impact:** Unverified-against-real-Redis code path; low risk while `memory` stays the default.
- **Dependencies:** A running Redis instance for a 30-minute smoke test.
- **Priority:** Small, contained.
- **Still required?** Yes, but not urgent — no trigger (single-instance deployment) has fired.

### B-7. `POST /reports/rescore` — unbounded, zero-consumer surface

- **Identifier:** `01 D-2` (original finding), reaffirmed as a deprecation candidate in `17` §1.
- **Current repository evidence:** Still present in the 37-route contract; admin-gated since M3 but not deleted.
- **Business/user impact:** None (admin-gated, no frontend consumer).
- **Technical impact:** Dead surface area.
- **Dependencies:** A route removal is an API-contract change — needs an Engineering Question / explicit sign-off before touching the frozen route inventory, not a unilateral deletion.
- **Priority:** Trivial effort, low value — cosmetic.
- **Still required?** Marginal — safe to leave, safe to remove; not a blocker either way.

---

## C. Stale Work — not resurrected

| Item | Original source | Why it's stale now |
|---|---|---|
| **Phase 6** (router split, `server.py` deletion, M2-2 DoD) | `06 §7`, `12` §3/§7 | **Confirmed still open by direct evidence** (`server.py` is 1,709 lines, still monolithic, 37 routes all in one file) — but per this task's own instruction not to assume the original phase ordering still governs, and per `17`'s own reconciliation (which superseded the Phase 5/6/7 checklist with the M5–M9 roadmap and did **not** carry "finish Phase 6" forward as a named milestone), this is deliberately **not** being proposed as the next milestone. The security-relevant slice of Phase 6 (authorization model) already shipped as M5. The remainder (pure code reorganization, D-4's "no unit-testable seam" symptom) is tracked as low-risk technical debt in `17` §5, not resurrected here. |
| **Phase 7 — Docker hardening** | `06 §7`, `12` §3, M2-6 DoD | **Confirmed still open** — no `Dockerfile` or `docker-compose*` exists anywhere in the repo (verified by direct search this session). Same reasoning as Phase 6: `17`'s reconciled roadmap did not carry this forward as a named milestone; the OTel/Prometheus slice of Phase 7 shipped as M6. No current trigger (no hosted deployment) makes this urgent. |
| **Phase 7 — CI security/supply-chain gates (`10` §10–§11)** | `10` §10–§11 | Only one real backend CI workflow exists (`backend-ci.yml`); full supply-chain gating status not independently re-verified this pass (out of this reconciliation's evidence-gathering scope) — flagged as unverified, not claimed complete or incomplete. Not proposed as next milestone for the same reason as the two rows above. |
| Managed vector search (`ADR-017`) | `08` DA-6/DA-7 | Explicitly deferred with a stated trigger (p95 retrieval > 2s or > ~500k chunks) — trigger not met. Correctly still deferred, not stale-and-forgotten. |
| Per-user corpus partitioning (`SQ-1`) | `10` §6.4 | Blocked on a product decision, same class as B-1. Not an engineering item. |
| The 8 items in `11`'s "Decisions deliberately deferred" table (Redis session cache, Redis-as-broker, distributed locks, retrieval-result cache, async-native LLM client, etc.) | `11`, `09` §14 | Every one has a stated revisit trigger; none has fired. Correctly not resurrected. |
| `17` §7's entire AI Platform Evolution Roadmap (evaluation/regression, provider governance, cost optimization, capacity planning, production operations) | `17` §7 | Explicitly self-described as "documents, does not implement... no new ADR, no architecture change" — every item's own "trigger to build" (second AI feature shipping, real production traffic, a provider outage, etc.) is unmet at current single-instance, pre-launch scale. Confirmed still unmet by this session's own evidence-gathering (no production traffic exists). Correctly excluded from milestone candidacy. |
| Financial Statements & Data Visualization (`17`'s proposed "Milestone 8") | `17` §1, §6 | **Not stale — genuinely still open** (confirmed: `agents/ingest.py` still only calls yfinance's `.info`; `recharts` still not installed in `web/`) but **not ready**: needs a new ADR before scoping (new data model, `17`'s own stated precondition). Not proposed as the immediate next milestone because it is blocked on a decision this reconciliation cannot make unilaterally — listed for completeness, not dismissed. |
| AI Comparison explanation + rescore deletion (`17`'s proposed "Milestone 9") | `17` §1, §6 | Still open, still small, still valid — just lower-priority than B-5's test-hardening cluster per `17`'s own explicit dependency-ordering (5→6→7→8→9). Not stale, simply not next. |

---

## D. Next Milestone

### Milestone name
**Milestone 7 — Streaming/Lifecycle Test Hardening**

*(Verbatim name from `17` §6, the current ratified roadmap — not a new name invented by this reconciliation.)*

### Objective
Close the remaining Low-risk-but-real automated-test gaps in the streaming/job-lifecycle
surface (`T-6`, `T-7`, `T-10`, `T-11`, `T-13`, `T-14`) — regression protection for
correctly-working code that is currently unguarded, not a bug fix.

### Scope
1. Automated restart-recovery test (`T-6`) — verify the startup sweep actually marks orphaned jobs `failed` (previously confirmed manually in M2, never automated).
2. `POST /ingest/pdf` test coverage (`T-7`) — currently zero automated coverage.
3. Keepalive-after-120s-idle test (`T-10`).
4. Streaming an already-finished job (`T-11`) — reconnect behavior.
5. Cancel-mid-stream event assertion (`T-13`) — verify the `pipeline/warn` event's actual presence in the SSE stream, not just the terminal status via `GET`.
6. Strict event-ordering assertion (`T-14`) — today's live tests check the *set* of required node events, not their order.

**Optional, low-cost bundling candidates already scoped and verified-open by this
reconciliation** (not required for M7's own acceptance, but same-area, same-file,
trivial to fold in if the CTO wants them together): B-2 (add `%(correlation_id)s` to
the log format string) and B-3 (one `logger.info` inside `push()`). Listed separately
so M7's own scope isn't silently inflated — the CTO Recommendation below treats them
as optional, not required. **Optional B-2/B-3 bundling requires explicit CTO approval
and must not alter M7's acceptance criteria (§D, below) unless those items are
formally added to the milestone** — "optional" is a standing state here, not a default
path into committed implementation scope.

**Deployment boundary (B-2, B-3):** neither is a blocker for M7, and neither requires
reopening M6. Both should be completed before any hosted/customer-facing deployment —
correlation IDs and pipeline-trace-to-log visibility materially improve incident
correlation and log-based diagnosis, and that need becomes real the moment traffic is
real. `O-3` (JSON structured logging) stays trigger-dependent exactly as already
documented in B-4 — this boundary does not extend to it.

### Explicit non-scope
- Phase 6 (router split, `server.py` deletion) — deliberately not resurrected, §C.
- Phase 7 (Docker, CI supply-chain gates) — deliberately not resurrected, §C.
- Google Social Authentication (B-1) — blocked on a product/CTO decision, not engineering.
- Financial Statements / Data Visualization ("Milestone 8") — blocked on a new ADR.
- Real-Redis verification (B-6) — a separate small item, not part of this test-hardening cluster (different subsystem: infra verification, not test authorship).
- Any change to `POST /reports/rescore` (B-7) — a contract-touching decision, out of scope for a pure-test milestone.
- Any change to API contracts, frozen architecture, or frontend code.

### Dependencies
None. Pure test-writing against already-shipped, already-working code paths.

### Relevant ADRs
None directly govern test authorship; the tests verify behavior already ratified by
**ADR-011** (job deadlines/lifecycle) and **ADR-001/ADR-018** (Redis job/event backend,
`XREAD`-only Streams semantics) without changing either.

### Expected files/modules affected
`backend/tests/` only — new test files/cases under `backend/tests/unit/` and
`backend/tests/` (live-marked where a running server is required, e.g. restart-recovery
and keepalive). No production code under `backend/agents/`, `backend/server.py`,
`backend/app/`, `backend/infrastructure/`, or `backend/application/` is expected to
change. **No production-code changes are permitted within M7 without first raising an
Engineering Question and obtaining explicit approval** (per the M2 charter's own
conflict procedure, `12` §6). If a test exposes a legitimate production-code
testability defect, that defect must be separately assessed through that process
before any implementation — this preserves M7's test-only scope while leaving room
for the governance process, not this document, to judge whether a real testability
problem justifies a change, rather than foreclosing that question by assumption.

### Testing requirements
Each of the 6 items becomes at least one new test, hermetic where possible (`T-7`
almost certainly can be; `T-6`/`T-10`/`T-11`/`T-13` likely need `@pytest.mark.live`
per the existing convention). All new tests must pass in the same hermetic/live split
this repo already enforces (`pytest.ini`'s `-n 2 --dist loadscope`, unmodified per
the standing `W-6` rule). No existing test may be weakened to make a new one pass.

### Acceptance criteria
- All 6 named gaps (`T-6/7/10/11/13/14`) have at least one new, real test exercising the actual code path (not a helper in isolation) — consistent with the standard this session's M6 fast-follow round already established for span-status/SSE-cancellation tests.
- Full hermetic + contract suite still green.
- Full live suite run and reported — new failures (beyond the pre-existing, already-documented baseline of 6) block sign-off; the pre-existing baseline itself is not this milestone's concern to fix.
- No API contract change (route inventory unchanged).
- A short implementation report, matching this repo's established pattern (what was tested, files changed, before/after coverage).

---

## CTO Recommendation

**NEXT MILESTONE:**
Milestone 7 — Streaming/Lifecycle Test Hardening

**STATUS:**
READY FOR CTO APPROVAL

**RATIONALE:**
This is the highest-priority item that is simultaneously (a) still genuinely required —
verified against current repository evidence, not assumed from the original roadmap,
(b) already ratified as next-in-sequence by `17`'s own current reconciled roadmap
(M5→M6→**M7**→M8→M9), with M5 and M6 now closed, and (c) blocked by nothing — no ADR,
no product decision, no architecture change, no dependency on any other open item.
Every other candidate this reconciliation found is either not a milestone (B-1's Google
OAuth conflict needs a product ruling, not code), not ready (Financial Statements/"M8"
needs a new ADR first), explicitly deprioritized by the current roadmap's own ordering
(Phase 6/7's remaining architectural items, per §C), or small enough to be an optional
same-pass addendum rather than its own milestone (B-2, B-3).

**DEPENDENCIES:**
None.

**NON-SCOPE:**
Phase 6 (router split / `server.py` deletion) · Phase 7 (Docker, CI supply-chain gates)
· Google Social Authentication · Financial Statements & Data Visualization ("Milestone 8")
· Real-Redis verification (B-6) · `POST /reports/rescore` deletion (B-7) · any API
contract, frozen architecture, or frontend change.

---

*Do not start implementation until this milestone has been reviewed and approved by the CTO.*

*Companion documents: [`11_ADR_Index.md`](11_ADR_Index.md) · [`12_M2_Implementation_Charter.md`](12_M2_Implementation_Charter.md) · [`17_M4_Backend_Capability_Roadmap_Reconciliation.md`](17_M4_Backend_Capability_Roadmap_Reconciliation.md) · [`18_M5_EQ3_Authorization_Cutover_Report.md`](18_M5_EQ3_Authorization_Cutover_Report.md) · [`26_M6_Observability_Architecture_Review.md`](26_M6_Observability_Architecture_Review.md) · [`27_M6_Fast_Follow_Execution_Review.md`](27_M6_Fast_Follow_Execution_Review.md) · [`Feature_Parity_Tracker.md`](../governance/Feature_Parity_Tracker.md)*
