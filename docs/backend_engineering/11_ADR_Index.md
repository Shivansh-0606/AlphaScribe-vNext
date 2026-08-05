# Architecture Decision Record Index

**Status:** 🔒 **FROZEN** — `v1.0`, ratified 2026-08-03
**Milestone:** Backend Engineering M1 · **Baseline:** `main` @ `7404b67`
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main` · commit `7404b67`
**Scope:** the backend architecture set, Documents
[`06`](06_Clean_Architecture_Migration_Plan.md)–[`10`](10_Backend_Security_Architecture.md)

---

## How to read this

Each ADR is a **one-screen summary with a pointer**, not a restatement. The
reasoning, alternatives, risks, and implementation detail live in the source
document — this index exists so a reader can find *which* decision governs a
question without reading five documents, and so a future change knows what it
is amending.

**Amending a decision:** edit the source document as a numbered amendment
(its documents are frozen), then update this row's status to `Superseded by
ADR-0NN` and add the new ADR. Never silently edit a frozen decision.

| Field | Meaning |
|---|---|
| **Status** | `Accepted` · `Accepted (open question)` — ratified but with a tracked follow-up · `Supersedes` — reverses an earlier recommendation |
| **Source** | The authoritative document + ID. Cite *that*, not this index, in code comments. |

---

## Index

| ADR | Title | Status | Source |
|---|---|---|---|
| [001](#adr-001) | Adopt Redis for the job lifecycle | Supersedes | `09` §0 (EQ-1) |
| [002](#adr-002) | Migrate to a layered architecture by strangler fig, not rewrite | Accepted | `06` AD-4 |
| [003](#adr-003) | Application factory with no import-time I/O | Accepted | `06` AD-1 |
| [004](#adr-004) | Ports are Protocols; one composition root; no DI framework | Accepted | `06` AD-2, AD-3 |
| [005](#adr-005) | Enforce the dependency rule by automated test | Accepted | `06` AD-5 |
| [006](#adr-006) | Separate transport DTOs from domain models | Accepted | `06` AD-11 |
| [007](#adr-007) | Two LangGraph graphs sharing one node library | Accepted | `07` LG-1 |
| [008](#adr-008) | Graph node names are a cross-team API contract | Accepted | `07` G-1 |
| [009](#adr-009) | No LangGraph checkpointer; no token-level streaming | Accepted | `07` LG-5, G-4 |
| [010](#adr-010) | No fact-checker in the Learning graph | Accepted | `07` LG-6 |
| [011](#adr-011) | Bound jobs by wall-clock deadline, not per-node timeouts | Accepted | `07` LG-11, LG-12 |
| [012](#adr-012) | MongoDB is the system of record; Redis never is | Accepted | `08` DA-2 · `09` RA-0 |
| [013](#adr-013) | Keep the application `id` as the lookup key | Accepted | `08` DA-1 |
| [014](#adr-014) | Idempotent, order-hardened sequences over transactions | Accepted | `08` DA-4, DA-5 |
| [015](#adr-015) | Output documents embed a source snapshot | Accepted | `08` RI-2 |
| [016](#adr-016) | Forward-only idempotent migrations; additive fields only | Accepted | `08` DA-9, DA-10 |
| [017](#adr-017) | Inline embeddings; no managed vector search in v1 | Accepted (open question) | `08` DA-6, DA-7 |
| [018](#adr-018) | Redis Streams with independent cursors, never consumer groups | Accepted | `09` §4.1 |
| [019](#adr-019) | Every Redis key is bounded; version the keyspace instead of migrating it | Accepted | `09` RA-1, §10.3 |
| [020](#adr-020) | `noeviction`, and a per-concern degradation policy | Accepted | `09` §8, §9.2 |
| [021](#adr-021) | Fail open on rate limiting when Redis is unavailable | Accepted | `09` §8.1 |
| [022](#adr-022) | No Redis HA in v1 | Accepted | `09` §9.7 |
| [023](#adr-023) | Authentication stays stdlib-only | Accepted (standing) | `06` C-3 |
| [024](#adr-024) | Authorization is a property of the repository, not the handler | Accepted | `10` §4.2 (EQ-2, EQ-3) |
| [025](#adr-025) | Cookie sessions require a same-registrable-domain deployment | Accepted | `10` SD-1 |
| [026](#adr-026) | Secrets rotate through an overlap window; revocation is a CLI | Accepted | `10` §8, SD-15 |
| [027](#adr-027) | Prompt injection is a monitored residual risk, not a mitigated one | Accepted (open question) | `10` SR-5, SQ-1 |
| [028](#adr-028) | Reproducible builds via a hash-locked dependency file | Accepted | `10` SD-6 |

---

### ADR-001
**Adopt Redis for the job lifecycle** · *Supersedes the audit recommendation* ·
`09` §0 (EQ-1)

- **Context** — The audit recommended keeping the existing in-process registry +
  Mongo mirror, on the grounds that Redis solves a multi-instance problem a
  single-process deployment does not yet have.
- **Decision** — Redis is adopted, as directed by the platform owner. Redis owns
  live job status, the SSE event transport, cancellation fan-out, rate limits,
  and the active-job set.
- **Consequences** — Resolves `01 D-1` (split SSE streams), `01 D-6` (orphaned
  jobs), and the fragile replay counter using primitives rather than bespoke
  code, and makes multi-instance streaming possible. Adds one runtime service,
  one dependency, and one failure domain — bounded by ADR-020's degradation
  policy.

### ADR-002
**Migrate by strangler fig, not rewrite** · `06` AD-4

- **Context** — `server.py` is 1,208 lines fusing transport, use cases, and
  persistence; a rewrite would produce an unreviewable diff and near-certain
  contract drift.
- **Decision** — Seven phases, each one PR, each leaving `main` green and
  contract-identical. `server.py` shrinks until it is deleted at Phase 6.
- **Consequences** — Value lands early (Phases 0–1 alone make the backend
  testable). Requires discipline against half-finishing: deletion is an exit
  criterion, not a cleanup wish.

### ADR-003
**Application factory with no import-time I/O** · `06` AD-1

- **Context** — `import server` executes `os.environ[...]`, constructs a Mongo
  client, and compiles the graph, so nothing can be imported without a full
  environment. This is the root cause of the testing inversion.
- **Decision** — `create_app()`, one validated `Settings` object, adapters built
  only in the composition root.
- **Consequences** — Unblocks every hermetic test and every subsequent phase.
  Startup hooks move to `lifespan`.

### ADR-004
**Ports are Protocols; one composition root; no DI framework** · `06` AD-2, AD-3

- **Decision** — Seven `typing.Protocol` ports across six concerns; adapters are
  plain classes constructed in `container.py` and nowhere else.
- **Consequences** — The seam costs no runtime machinery and no registration
  ceremony. The adapter set is auditable in one file and swappable per
  environment, which is what makes ADR-001's Redis swap verifiable.

### ADR-005
**Enforce the dependency rule by automated test** · `06` AD-5

- **Context** — Six documented boundary violations all happened *under* code
  review.
- **Decision** — A ~40-line AST walk asserts the allowed-import matrix; no new
  dependency.
- **Consequences** — Layering decay fails CI with a file, line, and offending
  import instead of eroding silently.

### ADR-006
**Separate transport DTOs from domain models** · `06` AD-11

- **Context** — Reports return `{job_id}` and Learning returns `{id}`; the
  frontend validates at the trust boundary, so the difference is load-bearing.
- **Decision** — Frozen wire shapes live in `app/api/dto/`; use cases return
  domain objects and each router serializes to its own envelope.
- **Consequences** — The mechanism that lets both features share one pipeline
  while keeping every approved contract byte-identical.

### ADR-007
**Two graphs sharing one node library** · `07` LG-1, LG-2

- **Context** — Research is up to 6 LLM calls with a retry loop; Learning is
  exactly 1. A parameterized graph would leak fact-check vocabulary into a UI
  state machine that has no stage for it.
- **Decision** — `build_research_graph` and `build_learning_graph`, separate
  state classes, `retriever` shared verbatim (the Learning use case adapts its
  *input*, not the node).
- **Consequences** — No retrieval fork to drift; no cross-feature state
  coupling.

### ADR-008
**Node names are a cross-team API contract** · `07` G-1

- **Context** — The UI derives its loading state from `event.node`; an
  unrecognized name leaves it in "AI Thinking" forever with no error.
- **Decision** — The vocabulary is fixed (`pipeline`, `retriever`, `extractor`,
  `tone`, `synthesizer`, `fact_checker`, `final`, `explainer`). Changing one
  requires frontend sign-off, like any API shape change. An event-envelope test
  enforces it.
- **Consequences** — Constrains graph refactoring; makes the most likely silent
  UI break impossible to ship.

### ADR-009
**No checkpointer, no token streaming** · `07` LG-5, G-4

- **Decision** — Neither is built in v1.
- **Rationale** — Retry issues a *new job id* per the frozen contract, so resume
  has no UI surface; and no delta event type exists in either approved contract,
  so token streaming would require changing both the API and the frontend.
- **Consequences** — Revisit only if a resume affordance or a streaming event
  type is specified.

### ADR-010
**No fact-checker in the Learning graph** · `07` LG-6

- **Context** — The contract carries no `fact_check_status`/`scorecard`, and the
  frozen loading behaviour is exactly two stages. The existing checker verifies
  *numeric* claims only — precisely the class a learner explanation mostly is
  not.
- **Decision** — Grounding by prompt discipline plus deterministic citation
  validation (out-of-range markers stripped; uncited output rejected).
- **Consequences** — Learning stays a single LLM call. If a stronger guarantee
  is later required, the upgrade applies to both features or neither.

### ADR-011
**Bound jobs by wall-clock deadline** · `07` LG-11, LG-12

- **Context** — Every individual limit held; their composition did not. The
  worst case computed to **~57 minutes** for one job holding a concurrency slot,
  and it exceeded the Redis reaper's window, which would have freed the slot of
  a still-running job.
- **Decision** — One budget per job (300 s research / 120 s learning) carried in
  state and checked at node boundaries, with an outer `wait_for` backstop; retry
  attempts 4 → 3 plus a 12-attempt per-job ceiling; `MAX_JOB_LIFETIME` 600 s with
  `MAX_JOB_LIFETIME > max(deadline) + grace` asserted at startup.
- **Consequences** — ⚠️ **User-visible behavior change** on the pathological
  tail: such a job now fails at ~5 min with a retry offered. No contract or
  frontend change. Node-boundary checks degrade rather than hard-cancel, so
  partial results still persist.

### ADR-012
**MongoDB is the system of record; Redis never is** · `08` DA-2 · `09` RA-0

- **Decision** — Redis holds nothing whose loss changes a user-visible outcome
  after a job terminates.
- **Consequences** — Backup and durability reasoning stays trivial: back up
  Mongo, lose nothing that matters. Redis is excluded from the backup policy.
  Losing Redis costs in-flight streams only, which is what makes ADR-020's
  degradation policy and ADR-022's no-HA stance defensible.

### ADR-013
**Keep the application `id` as the lookup key** · `08` DA-1

- **Context** — Every collection carries a uuid4 `id` *and* an unused `_id`
  ObjectId; every query uses `id`, so `_id`'s free unique index is never used.
- **Decision** — Keep `id`; add explicit unique indexes instead of migrating.
- **Consequences** — Five extra indexes versus a repo-wide breaking change that
  would also alter ids returned to clients.

### ADR-014
**Idempotent sequences over transactions** · `08` DA-4, DA-5

- **Decision** — No multi-document transactions. Three non-atomic sequences are
  order-hardened instead — notably account deletion, which deletes the user row
  **last** so any partial failure is re-runnable. Deploy a single-node replica
  set anyway, so transactions and change streams are available later without a
  topology migration.
- **Consequences** — Avoids transaction latency and retry failure modes for
  windows the read paths already tolerate. The account-deletion ordering is
  load-bearing and must be preserved.

### ADR-015
**Output documents embed a source snapshot** · `08` RI-2

- **Context** — Reports and explanations copy their retrieved chunks rather than
  referencing them.
- **Decision** — Keep it. This is deliberate, not denormalization debt.
- **Consequences** — Reports are **immutable historical records**: re-ingesting
  or deleting chunks never invalidates existing citations, and forensics after a
  corpus-poisoning incident remain possible. A future "normalization" would
  silently break both.

### ADR-016
**Forward-only migrations; additive fields only** · `08` DA-9, DA-10

- **Decision** — Numbered, idempotent, forward-only migrations with a ledger;
  no down-migrations. New internal fields are additive and projected out at the
  API boundary.
- **Consequences** — Old and new application versions run against the same
  migrated database, so no phase needs a lockstep deploy. Exactly one
  destructive migration exists (`m0004`), gated on a release soak plus a
  verified backup.

### ADR-017
**Inline embeddings; no managed vector search in v1** · `08` DA-6, DA-7 ·
*open question*

- **Decision** — Keep 384-dim vectors inline in `filing_chunks`; no Atlas
  `$vectorSearch`.
- **Consequences** — ~75 % of each chunk document is the vector, and retrieval
  moves up to ~10 MB per query. Bounded today by the 2,000-chunk cap, the job
  cap, and a new `maxTimeMS`. **Open:** stated triggers (p95 retrieval > 2 s, or
  > ~500k chunks) and a three-step upgrade path.

### ADR-018
**Redis Streams with independent cursors, never consumer groups** · `09` §4.1

- **Context** — `XREADGROUP` *distributes* entries across group members, which
  would faithfully recreate the exact split-stream defect Redis was adopted to
  fix — behind a more authoritative-looking API.
- **Decision** — Plain `XREAD` per connection. A static test bans
  `xreadgroup`/`xgroup_create` from the Redis adapter package.
- **Consequences** — Correct fan-out by construction; exact replay from `0-0`,
  which also deletes the fragile skip-counter.

### ADR-019
**Bound every key; version the keyspace instead of migrating it** · `09` RA-1,
§10.3

- **Decision** — Every key has a TTL or a size cap. An incompatible key-shape
  change bumps `as:v1:` → `as:v2:`; both coexist and old keys expire.
- **Consequences** — There are no Redis data migrations, ever. Unbounded growth
  is impossible by construction.

### ADR-020
**`noeviction`, and a per-concern degradation policy** · `09` §8, §9.2

- **Context** — Under a default eviction policy, Redis would silently evict live
  job event streams under memory pressure, stopping a running pipeline's stream
  with no error anywhere.
- **Decision** — `maxmemory-policy noeviction`, asserted at startup. Redis
  unavailability is handled per concern, not globally: job creation and
  streaming fail closed; report reads, auth, ingest, and search are unaffected.
- **Consequences** — OOM becomes a loud, handled error. A Redis outage refuses
  new analyses instead of producing unobservable ones.

### ADR-021
**Fail open on rate limiting when Redis is unavailable** · `09` §8.1

- **Context** — Fail-closed would turn a cache outage into a total
  authentication outage — a self-inflicted DoS, and the larger real-world risk.
- **Decision** — Allow requests, log WARN, raise a **paging** alert. Bounded by
  scrypt's per-verification cost, which is itself a hard throughput limit on
  online guessing.
- **Consequences** — A brute-force window exists during a Redis outage. This is
  a deliberate, alerted security trade-off, not an oversight.

### ADR-022
**No Redis HA in v1** · `09` §9.7

- **Decision** — Single instance. No Sentinel, no Cluster, no replica.
- **Rationale** — ADR-012 makes a Redis outage survivable, and there is no HA
  story for Mongo either; Sentinel would add failover-correctness concerns to
  protect a component already designed to be lossy.
- **Consequences** — Revisit on multi-region, or on an availability target that
  forbids refusing new jobs during a restart — at which point the answer is
  managed Redis, not self-managed Sentinel.

### ADR-023
**Authentication stays stdlib-only** · `06` C-3 · *standing decision, recorded*

- **Decision** — `hashlib.scrypt` + opaque `secrets` tokens hashed at rest. No
  JWT, no OAuth, no `passlib`/`bcrypt`. Raising the scrypt cost to N=2^16 with
  transparent rehash-on-login stays inside this constraint.
- **Consequences** — Recorded here because it is the constraint most likely to
  be "helpfully" violated by a future contributor reaching for a familiar
  library.

### ADR-024
**Authorization is a property of the repository** · `10` §4.2 (EQ-2, EQ-3)

- **Context** — Authentication is uniform across 29 routes; authorization is
  decided per handler and inconsistently, leaving cross-tenant reads and one
  cross-tenant *write* open.
- **Decision** — Three access classes (owned / shared / admin) enforced as a
  repository-level predicate. The repository exposes no unscoped read, so a new
  handler cannot forget it.
- **Consequences** — ⚠️ **Behavior change** on live endpoints: cross-tenant read
  → 404, non-admin rescore → 403. No path, method, or shape changes, and no
  `web/` call site performs a cross-tenant read.
- **M6 amendment (2026-08-05, no new ADR):** the cache-hit lookup fix this
  decision's own M5 rollout required (`18` §1.2) is promoted to a standing
  Security Invariant — `10` §4.5, `SI-1`: any cache/memoization/dedup lookup
  that can hand back a reference to another request's result is a disguised
  read and inherits this ADR's scoping rule.

### ADR-025
**Cookie sessions require a same-registrable-domain deployment** · `10` SD-1

- **Context** — `SameSite=Lax` is simultaneously the only CSRF control *and* the
  thing that determines whether authentication works cross-origin at all.
- **Decision** — Frontend and backend must share a registrable domain in every
  deployed environment.
- **Consequences** — A split-domain deployment would silently break auth and SSE
  entirely. Moving to `SameSite=None` would remove the CSRF control and mandate
  a CSRF token — a frontend contract change, not an ops-level fix during a
  deploy.

### ADR-026
**Rotate secrets through an overlap window; revocation is a CLI** · `10` §8,
SD-15

- **Decision** — Every rotatable secret has a dual-validity window (two Mongo
  users, two Redis ACL users, dual-pepper OTP verification, two provider keys),
  so rotation is zero-downtime. Bulk session revocation is an operator CLI
  command, not an HTTP endpoint.
- **Consequences** — Rotation stops being an outage. The CLI closes a real gap:
  there is currently **no way to sign everyone out**, which is the primary
  containment lever for a confirmed compromise.

### ADR-027
**Prompt injection is a monitored residual risk** · `10` SR-5, SQ-1 ·
*open question*

- **Context** — Untrusted third-party document text flows verbatim into prompts,
  and any authenticated user can write to the *shared* corpus — so corpus
  poisoning is a same-privilege operation.
- **Decision** — Three deterministic containment layers (delimiting + role
  framing, mandatory citation provenance, ingest-time screening with a metric).
  Explicitly **not** claimed as mitigated.
- **Consequences** — Buys containment (the model has no tools and no side
  effects) and visibility, not prevention. **Open (SQ-1):** per-user corpus
  partitioning is the structural fix and is a product decision — v1 keeps the
  shared corpus.

### ADR-028
**Reproducible builds via a hash-locked dependency file** · `10` SD-6

- **Context** — 12 of 22 backend requirements are unpinned, including every LLM
  SDK — so two builds a week apart can produce materially different agent
  behavior.
- **Decision** — `requirements.txt` stays the human-readable declaration of
  intent; a generated, hash-locked `requirements.lock` is what Docker and CI
  install.
- **Consequences** — Keeps the lean-manifest discipline legible while making
  builds reproducible and CVE blast radius knowable.

---

## Decisions deliberately deferred

Recorded so a future reader knows these were considered, not overlooked. Detail
and revisit-triggers live in the source documents.

| Deferred | Trigger to revisit | Source |
|---|---|---|
| Redis session cache | p95 auth latency, *after* the `users.id` index lands | `09` §14 |
| Redis as a task-queue broker | horizontal scaling where an instance must run jobs it did not accept | `09` §14 |
| Distributed locks | work-stealing across instances | `09` §14 |
| Retrieval-result cache | retrieval reuse across differing queries becomes measurable | `09` §14 |
| Managed vector search | ADR-017's stated thresholds | `08` DR-3 |
| Per-user corpus partitioning | product decision (SQ-1) | `10` §6.4 |
| OpenTelemetry sampling / metrics backend beyond Prometheus | a second instance | `04` §3.3 |
| Async-native LLM client | cancellation latency inside a provider call becomes material | `07` §6.2 |

---

## API-contract impact of the whole set

**Zero approved contracts changed.** The 31 implemented routes and the 4 frozen
Learning routes keep their paths, methods, request shapes, response shapes, and
status semantics; the Phase-0 OpenAPI snapshot is the automated guard.

Three changes are **additive or behavioral** and were ratified explicitly rather
than absorbed silently:

| Change | Nature | ADR |
|---|---|---|
| `GET /api/health/ready` | **Additive** operational probe; no frontend consumer; modifies no existing route | `04` §5.3, `10` §4.4 |
| Job deadlines | Behavioral — a pathological job fails at ~5 min instead of ~57 min | ADR-011 |
| Authorization scoping | Behavioral — cross-tenant read 200 → 404; non-admin rescore 200 → 403 | ADR-024 |

---

*Source documents:* [`06`](06_Clean_Architecture_Migration_Plan.md) ·
[`07`](07_LangGraph_Architecture.md) · [`08`](08_MongoDB_Data_Architecture.md) ·
[`09`](09_Redis_Architecture.md) ·
[`10`](10_Backend_Security_Architecture.md) · index:
[`00_README.md`](00_README.md)
