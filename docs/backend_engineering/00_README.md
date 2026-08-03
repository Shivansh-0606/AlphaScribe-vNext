# Backend Engineering — Document Index

**Milestone:** Backend Engineering M1
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main` · commit `7404b67`
**Architecture set:** `v1.0` — 🔒 **FROZEN**, ratified 2026-08-03
**Last updated:** 2026-08-03

> Documents 06–10 are frozen. Changes are numbered amendments appended to the
> relevant document, plus a status update in [`11_ADR_Index.md`](11_ADR_Index.md)
> — never silent edits. Start at the [ADR Index](11_ADR_Index.md) to find which
> decision governs a question.

---

## Documents

### Audit phase (complete)

| # | Document | Status | Purpose |
|---|---|---|---|
| [01](01_Backend_Architecture_Review.md) | Backend Architecture Review | audit | Layer boundaries, Clean Architecture compliance, SOLID, coupling, debt register (D-1…D-11) |
| [02](02_API_Coverage_Audit.md) | API Coverage Audit | audit | All 31 routes vs. frontend consumers; API Parity Matrix; contract-fidelity findings (F-1…F-7) |
| [03](03_Learning_Backend_Design.md) | Learning Backend Design | design | The 4 frozen `/api/learning/*` routes: retrieval, graph, prompts, citations, lifecycle, failure recovery |
| [04](04_Observability_Audit.md) | Observability Audit | audit | Logging, metrics, tracing, health (O-1…O-16) |
| [05](05_Testing_Audit.md) | Testing Audit | audit | Unit / integration / contract / streaming coverage (T-1…T-14) |

### Architecture phase (frozen — v1.0)

| # | Document | Status | Purpose |
|---|---|---|---|
| [06](06_Clean_Architecture_Migration_Plan.md) | Clean Architecture Migration Plan | 🔒 v1.0 | Target layering, 6 ports, composition root, 7-phase strangler-fig migration (AD-1…AD-13) |
| [07](07_LangGraph_Architecture.md) | LangGraph Architecture | 🔒 v1.0 | Two graphs, node contract, **execution limits & retry budgets**, streaming, cancellation, instrumentation (LG-1…LG-12) |
| [08](08_MongoDB_Data_Architecture.md) | MongoDB Data Architecture | 🔒 v1.0 | 10 collections, **entity relationships**, 25-index plan, access patterns, migrations, retention (DA-1…DA-10, RI-1…RI-6) |
| [09](09_Redis_Architecture.md) | Redis Architecture | 🔒 v1.0 | Keyspace, Streams event transport, job registry, rate limiting, **operational settings**, degradation policy (RA-0…RA-4) |
| [10](10_Backend_Security_Architecture.md) | Backend Security Architecture | 🔒 v1.0 | Trust boundaries, 25-item threat model, authorization model, **secret rotation**, **incident response**, containers, supply chain, CI gates (SD-1…SD-15) |
| [11](11_ADR_Index.md) | ADR Index | 🔒 v1.0 | 28 architecture decisions summarized with pointers; deferred decisions and their revisit triggers; API-contract impact statement |

### Implementation phase (active)

| # | Document | Status | Purpose |
|---|---|---|---|
| [12](12_M2_Implementation_Charter.md) | M2 Implementation Charter | 🟢 active | Milestone 2 work order: entry conditions, phase checklist, working conventions, coding-session handoff packet, conflict procedure |

---

## Reading order

- **New to this milestone:** 01 → 02 → 06 → then the domain document you need.
- **Implementing:** [06 §7](06_Clean_Architecture_Migration_Plan.md) is the
  authoritative sequence; 07–10 each nest their own ordered steps inside it.
- **Reviewing for freeze:** the consolidated register below, or each document's
  own §Ratification section.

---

## Conventions

- Every finding, decision, requirement, and risk carries a stable ID
  (`D-n`, `F-n`, `O-n`, `T-n`, `AD-n`, `LG-n`, `LR-n`, `DA-n`, `DR-n`, `RI-n`,
  `RA-n`, `RR-n`, `SD-n`, `SR-n`, `EQ-n`, `SQ-n`, `X-n`, `I-n`, `A-n`, `m####`).
  Cite the ID in commits, PRs, and code comments rather than restating the
  reasoning.
- **ID prefixing:** a reference to an ID owned by another document carries that
  document's number — `01 D-1`, `06 C-3`, `10 SD-15`. This matters for two
  colliding series: `C-n` means *coupling* in 01 and *constraints* in 06
  (unqualified `C-n` in 06–10 always means 06's constraints), and `T-n` means
  *testing gap* in 05 and *threat* in 10.
- **ID ownership:** `EQ-n` are owned by [01](01_Backend_Architecture_Review.md) §7
  (the audit raised them); other documents *resolve* them and re-state the ID in
  bold. That is citation, not redefinition — an `EQ-n` always means the same
  question everywhere it appears.
- Status: 🟡 proposed → 🟢 FREEZE-READY → 🔒 **FROZEN**. Documents 06–11 are at
  🔒 v1.0; changes are numbered amendments appended to the document, never
  silent edits.
- Documents 01–05 are audit findings (descriptive, point-in-time). Documents
  06–10 are governance (prescriptive, binding once frozen).

---

## Consolidated ratification register

Every decision ratified at freeze, gathered from the six §Ratification
sections. Recommendations shown were **accepted as written** on 2026-08-03
unless the row says otherwise. Retained as the decision record — reopening any
row requires an amendment plus an ADR status change.

### Resolved at audit

| ID | Question | Ruling |
|---|---|---|
| **EQ-1** | Redis for the job lifecycle, or Mongo-mirrored in-process? | ✅ **Redis adopted** — directed as part of the approved platform stack. Designed in [09](09_Redis_Architecture.md). |

### Ratified — security & authorization

| ID | Question | Recommendation | Doc |
|---|---|---|---|
| **EQ-2** | `POST /reports/rescore`: admin-gate or delete? Today any user rewrites every tenant's scorecards. | Admin-gate (403 for non-admins) | [10 §4.3](10_Backend_Security_Architecture.md) |
| **EQ-3** | Owner-scope report reads? Today any authenticated caller with a UUID reads any tenant's report. | Scope (404 cross-tenant); no frontend path affected | [10 §4.3](10_Backend_Security_Architecture.md) |
| **SD-1** | Frontend + backend on the same registrable domain, or `SameSite=None` + a CSRF token? | Same registrable domain | [10 §5.2](10_Backend_Security_Architecture.md) |
| **SD-3** | Fail startup in production on insecure `OTP_PEPPER` / `RESEND_API_KEY` defaults? | Yes | [10 §7.2](10_Backend_Security_Architecture.md) |
| **SD-5** | Mongo `--auth` + a Redis **ACL user** (not bare `requirepass` — ACL is what gives rotation an overlap window); no in-cluster TLS on a private segment | Approve | [10 §9.2](10_Backend_Security_Architecture.md) |
| **SD-15** | Add a bulk session-revocation CLI. **No lever exists today to sign everyone out** — the most important SEV1 containment action is currently impossible. | **Approve; lands Phase 1** | [10 §8.4](10_Backend_Security_Architecture.md) |
| **§3.1** | Raise scrypt to N=2^16 with transparent rehash-on-login? | Yes (stays stdlib-only) | [10 §3.1](10_Backend_Security_Architecture.md) |
| **§8** | Secret-rotation cadences and procedures (§8.2 matrix, §8.3 `OTP_PEPPER` dual-verify) | Approve | [10 §8](10_Backend_Security_Architecture.md) |
| **SR-5** | Accept prompt injection / corpus poisoning as a **monitored residual risk** rather than claiming mitigation? | Accept, with containment layers | [10 §6.3](10_Backend_Security_Architecture.md) |
| **SQ-1** | Should the filing corpus be per-user partitioned instead of shared? Structural fix for corpus poisoning; changes cost, caching, and cross-user report reuse. | **Product decision — raised, not decided.** v1 keeps the shared corpus. | [10 §6.4](10_Backend_Security_Architecture.md) |
| **§8.1** | Rate limiting when Redis is down: fail open or fail closed? Fail-closed turns a cache outage into a total auth outage. | Fail open + paging alert | [09 §8.1](09_Redis_Architecture.md) |

### Ratified — execution & data

| ID | Question | Recommendation | Doc |
|---|---|---|---|
| **LG-11** | **Job deadlines** (300 s research / 120 s learning). ⚠️ User-visible behavior change: a pathological job now fails at ~5 min instead of running up to ~57 min. No contract or frontend change. | Approve | [07 §5.4, §5.7](07_LangGraph_Architecture.md) |
| **LG-12** | Retry attempts 4 → 3, plus a 12-attempt per-job ceiling | Approve | [07 §5.5](07_LangGraph_Architecture.md) |
| **§6.2** | `MAX_JOB_LIFETIME` **900 s → 600 s**, satisfying `> max(JOB_DEADLINE) + GRACE`. Resolves an inter-document conflict found during this review. | Required for consistency | [09 §6.2](09_Redis_Architecture.md) · [07 §5.3](07_LangGraph_Architecture.md) |
| **LG-6** | No fact-checker in the Learning graph; grounding via prompt + deterministic citation validation | Approve | [07 §9](07_LangGraph_Architecture.md) |
| **LG-5 / AD-12** | No LangGraph checkpointer in v1 | Approve | [07 §9](07_LangGraph_Architecture.md) · [06 §3](06_Clean_Architecture_Migration_Plan.md) |
| **DA-1** | Keep application `id` as the lookup key rather than migrating to `_id` | Approve (the alternative is a repo-wide breaking change) | [08 §10](08_MongoDB_Data_Architecture.md) |
| **DA-4** | Idempotent, order-hardened sequences instead of multi-document transactions | Approve | [08 §8.3](08_MongoDB_Data_Architecture.md) |
| **DA-5** | Single-node replica set in all environments | Approve | [08 §8.1](08_MongoDB_Data_Architecture.md) |
| **DA-7** | No Atlas Vector Search in v1; DR-3 states the trigger to revisit | Approve | [08 §10](08_MongoDB_Data_Architecture.md) |
| **RI-2** | `source_documents` stays an **embedded snapshot** — reports are immutable historical records, and a future "normalization" would silently break historical citations | Binding | [08 §3.2](08_MongoDB_Data_Architecture.md) |
| **§9** | 30-day TTL on job collections; corpus retained indefinitely and **excluded** from account-deletion erasure | Ratify the erasure boundary explicitly | [08 §9](08_MongoDB_Data_Architecture.md) |
| **m0004** | The one destructive migration (drop `jobs.events`), gated on a one-release Redis soak + verified backup | Approve the gate | [08 §11.2](08_MongoDB_Data_Architecture.md) |
| **§7.3** | New per-user job quota (10/hour) — a user-visible 429 that does not exist today | Product call on the number | [09 §7.3](09_Redis_Architecture.md) |
| **§9.7** | No Redis HA (single instance) in v1, with a stated trigger to revisit | Approve | [09 §9.7](09_Redis_Architecture.md) |
| **RR-10** | `scripts/run.py` (the no-Docker developer path) defaults to `JOB_BACKEND=memory`; Redis is used in Docker, CI, and production | Approve | [09 §13](09_Redis_Architecture.md) |
| **§10.2 step 5** | The **one irreversible cutover step** — stop mirroring events to Mongo, then run `m0004`. Paired with the `m0004` row above; gated on a one-release Redis soak **and** a verified backup. | Approve the gate | [09 §10.2](09_Redis_Architecture.md) · [08 §11.2](08_MongoDB_Data_Architecture.md) |

### Ratified — process & binding rules

| ID | Rule | Doc |
|---|---|---|
| **§0.1** | `CLAUDE.md` § Dependencies must be amended for the approved stack (redis, OTel, Prometheus, pydantic-settings, pytest-cov) — otherwise the manifest diff reads as a policy violation | [06 §0.1](06_Clean_Architecture_Migration_Plan.md) |
| **§5.2** | Learning may not start before Migration Phase 4 (else the `01 D-1` SSE defect ships twice) | [06 §5.2](06_Clean_Architecture_Migration_Plan.md) |
| **Ph 6** | `backend/server.py` is **deleted** at Phase 6 — an exit criterion, not an aspiration | [06 §7.1](06_Clean_Architecture_Migration_Plan.md) |
| **G-1** | Graph node names are a cross-team contract; changing one requires frontend sign-off | [07 §13](07_LangGraph_Architecture.md) |
| **§2.3** | Reducer rule — a new parallel branch must write disjoint keys or declare a reducer | [07 §13](07_LangGraph_Architecture.md) |
| **§4.1** | Redis Streams use `XREAD` (independent cursors), **never** `XREADGROUP` — the latter silently recreates `01 D-1` | [09 §4.1](09_Redis_Architecture.md) |
| **§9.2** | `maxmemory-policy noeviction` is a deployment requirement, asserted at startup | [09 §9.2](09_Redis_Architecture.md) |
| **RA-0 / RA-1** | Redis is never the system of record; every key is TTL'd or capped | [09 §1](09_Redis_Architecture.md) |
| **SD-12** | The `live` CI job never runs on fork PRs (it is the only job holding API keys) | [10 §11](10_Backend_Security_Architecture.md) |

---

## Cross-cutting implementation order

Authoritative sequence from [06 §7](06_Clean_Architecture_Migration_Plan.md),
with each domain document's work mapped onto it.

| Phase | Theme | Key deliverables across documents |
|---|---|---|
| **0** | Safety net | Contract tests (`02` F-6) · unit tests for 14 pure functions (`05` §3.2) · **security regression tests (`10` SR-11)** · hermetic CI |
| **1** | App factory | `create_app()` + `Settings` (`06` AD-1/AD-9) · production startup gates (`10` SD-3) · no-body-logging (SD-4) · **bulk session revocation CLI (SD-15)** · `OTP_PEPPER` dual-verify |
| **2** | Domain extraction | Pure logic → `domain/` (`06`, `07` §11) |
| **3** | Ports + Mongo | Repositories (`06` AD-2) · **the 25-index migration `m0001` (`08` §5)** · `maxTimeMS` (`07` X-14) · node port injection (`07` AD-7) |
| **4** | Jobs + EventBus | **`01 D-1` fan-out fix** (`06` AD-8) · restart sweep (D-6) · `completed_at` (D-8) · **job deadlines + retry budget (`07` §5.4–5.5)** |
| **L** | Learning | 4 routes + 2-node graph (`03`, `07` §11 step 7) — **must follow Phase 4** |
| **5** | LLM adapter | Single provider dispatch (`01 D-3`); budget-aware timeouts |
| **6** | Router split | `server.py` deleted · **authorization model (`10` §4)** · EQ-2/EQ-3 · scrypt N=2^16 · PDF timeout |
| **7** | Platform | Redis adapters (`09`) · OTel + Prometheus (`04`, `07` §7) · Docker hardening (`10` §9) · supply chain + CI gates (`10` §10–§11) · log shipping (SR-14) |

---

## What changed in the pre-freeze review (v0.9 → v1.0-rc1)

| # | Change | Where |
|---|---|---|
| 1 | **Execution limits, retry budgets, and timeout policy** — a full inventory (X-1…X-15) plus the worst-case composition analysis that found a **~57-minute** unbounded job, and the deadline policy that fixes it | [07 §5](07_LangGraph_Architecture.md) |
| 2 | **Inter-document conflict found and resolved** — `MAX_JOB_LIFETIME` (900 s) was shorter than the worst-case job, which would have let the reaper free the slot of a still-running job. Now 600 s, with the invariant asserted at startup. | [07 §5.3](07_LangGraph_Architecture.md) · [09 §6.2](09_Redis_Architecture.md) |
| 3 | **Entity-relationship diagram + six invariants** the application must maintain, including `jobs.id ≡ reports.id` and the embedded-snapshot property that makes reports immutable historical records | [08 §3](08_MongoDB_Data_Architecture.md) |
| 4 | **Redis operational settings** — annotated `redis.conf`, eviction rationale, persistence stance, a restart-behavior state diagram covering all four restart permutations, connection management, and an explicit no-HA decision | [09 §9](09_Redis_Architecture.md) |
| 5 | **Secret rotation** — lifecycle diagram, per-secret rotation matrix with overlap windows, `OTP_PEPPER` dual-verify, and the discovery that **bulk session revocation does not exist** (SD-15) | [10 §8](10_Backend_Security_Architecture.md) |
| 6 | **Incident response** — severity model, the containment levers that exist today (`MAX_ACTIVE_JOBS=0` as a kill switch, `OTP_PEPPER` rotation, Redis `FLUSHDB`), six playbooks, evidence preservation, comms | [10 §12](10_Backend_Security_Architecture.md) |
| 7 | **Seven broken section references corrected** in 10, two in 06, one in 08, one in 07; every document now carries a cross-reference index and an ID-prefixing convention | all |
| 8 | New diagrams: before/after module map, port→adapter matrix, execution timeline, key lifecycle, restart states, data classification, secret lifecycle | 06–10 |

**No approved API contract and no frontend behavior was changed.** Two
user-visible *behavior* changes are proposed and flagged for explicit sign-off
rather than treated as fixes: job deadlines (LG-11) and authorization scoping
(EQ-2 / EQ-3).
