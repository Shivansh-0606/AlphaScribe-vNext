# Clean Architecture Migration Plan

**Status:** 🔒 **FROZEN** — `v1.0`, ratified 2026-08-03 · amendments only (§9)
**Milestone:** Backend Engineering M1 (post-audit) · **Date:** 2026-08-03
**Depends on:** [`01_Backend_Architecture_Review.md`](01_Backend_Architecture_Review.md)
**Referenced by:** [`07`](07_LangGraph_Architecture.md) · [`08`](08_MongoDB_Data_Architecture.md) · [`09`](09_Redis_Architecture.md) · [`10`](10_Backend_Security_Architecture.md)
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main` · commit `7404b67`

### Document control

| Version | Date | Change |
|---|---|---|
| **v1.0** | **2026-08-03** | **FROZEN.** Final consistency pass: cross-references, ID uniqueness, inter-document contradictions, ratification/register sync, diagram fidelity, and API-contract invariance all verified. |
| v1.0-rc1 | 2026-08-03 | Added §2.1 before/after module map and §2.6 port→adapter matrix; corrected two cross-references (`09` §10.1, `10` §4); phase table updated with SD-15, job deadlines, and `m0001`; added §9 cross-reference index; freeze-ready |
| v0.9 | 2026-08-03 | Initial proposal |

> **ID prefixing.** IDs defined here use `C-` (constraints), `OB-`, `AD-`,
> `MR-` (migration risks), `Ph`. References to IDs owned by another document
> carry that document's number
> — e.g. `01 D-1`, `10 SD-3`. Note `01` also defines a `C-` series (coupling);
> unqualified `C-n` in documents `06`–`10` always means **this** document's
> constraints.

---

## 0. Governing Constraints (binding on everything below)

| # | Constraint | Source |
|---|---|---|
| C-1 | **No approved API contract may change.** 31 implemented routes + the 4 frozen Learning routes keep their paths, methods, request shapes, response shapes, and status semantics. | [`02`](02_API_Coverage_Audit.md); `web/features/*/integration/schemas.ts` |
| C-2 | **No frontend behavior may be redesigned.** SSE framing, node vocabulary, and the `id` vs `job_id` envelopes are fixed by shipped, tested UI code. | `web/lib/api/sse-client.ts`, `learning/internal/streamStages.ts` |
| C-3 | **Auth stays stdlib-only.** `hashlib.scrypt` + opaque `secrets` tokens. No JWT, no OAuth, no `passlib`/`bcrypt`. | `CLAUDE.md` § Architecture |
| C-4 | **`pytest.ini` `addopts` is not modified.** | `CLAUDE.md` § Running & testing |
| C-5 | **`ponytail:` markers are preserved**, not silently "fixed". | `CLAUDE.md` § Deliberate shortcuts |
| C-6 | **`backend/tests/backend_test_iter*.py` are kept** — additive suites, not superseded snapshots. | `CLAUDE.md` § Running & testing |
| C-7 | **`agents/scoring.py` stays dependency-free** (stdlib `re` only). | `CLAUDE.md` § Backend specifics |
| C-8 | **External data sources stay best-effort** — BSE/yfinance/EDGAR failures return `None`, never crash a request. | `CLAUDE.md` § Backend specifics |

### 0.1 Governance note — dependency policy

`CLAUDE.md` § Dependencies currently reads *"Keep both dependency manifests
lean… Before adding a dependency, confirm nothing already installed does the
job."* The approved stack for this milestone (Redis, OpenTelemetry, Prometheus,
Docker, GitHub Actions) adds:

```
redis>=5.0                              # 09
pydantic-settings>=2.2                  # AD-9 — replaces 24 scattered os.environ reads
opentelemetry-sdk>=1.25                 # 04, 07 §7
opentelemetry-instrumentation-fastapi
opentelemetry-instrumentation-pymongo
opentelemetry-instrumentation-httpx
opentelemetry-exporter-otlp
prometheus-client>=0.20
# dev / CI only
pytest-cov>=5.0
pytest-asyncio>=0.23                    # hermetic async unit tests
```

A **deliberate, directed expansion**, not drift, recorded here so the manifest
diff is traceable to a decision rather than an unreviewed import.
**`CLAUDE.md` § Dependencies should be amended by its owner** to reflect the
approved platform stack, otherwise the next contributor reads the manifest as a
policy violation. No other dependency is added by this plan.

---

## 1. Objectives & Non-Objectives

### 1.1 Objectives

| ID | Objective | Audit finding addressed |
|---|---|---|
| OB-1 | Make the backend **importable and unit-testable without a live environment** | `01 D-4`, `01 B-6`, `05 T-3` |
| OB-2 | Give Learning a **use-case seam to build on** instead of a 120-line handler to copy | `01 V-1`, `01 D-1` |
| OB-3 | Put **one implementation** behind each infrastructure concern (jobs, events, LLM, persistence) so Redis/OTel/Prometheus can be adopted without touching domain code | `01 D-1`, `D-3`, `D-6`, EQ-1 |
| OB-4 | Establish an **enforced dependency rule** so the layering does not decay | `01 B-1`…`B-6` |
| OB-5 | Preserve every externally observable behavior exactly | C-1, C-2 |

### 1.2 Explicit non-objectives

- **Not** a rewrite. Every phase is a move-and-adapt of working, tested code.
  Zero net-new business logic except the Learning feature itself.
- **Not** a repository per collection. Two are introduced (chunks,
  reports/explanations); `users`/`sessions` stay as `agents/auth.py` plain
  functions — the most-tested module in the codebase.
- **Not** a DI framework. The composition root is one module with explicit
  constructor calls (§2.5).
- **Not** event-sourced, **not** CQRS, **not** a microservice split.

---

## 2. Target Architecture

### 2.1 Before / after

```
  BEFORE (baseline @ 7404b67)                AFTER (Phase 6 exit)

  backend/                                   backend/
   ├── server.py          1208 LOC            ├── app/
   │    routes ×31                            │    ├── main.py       create_app()
   │    request models                        │    ├── settings.py   one typed config
   │    JOBS / JOB_QUEUES globals             │    ├── container.py  composition root
   │    _run_pipeline (7 jobs in one fn)      │    └── api/routes/   6 modules, DTOs
   │    24 direct db.* calls                  ├── domain/            pure, zero deps
   │    CORS, warmup, shutdown                ├── application/       use cases + PORTS
   │    ← import-time env + Mongo + graph     ├── agents/            graphs + nodes
   └── agents/            ~2100 LOC           ├── infrastructure/    mongo · redis · llm
        nodes ← db handle injected            │                      external · obs · sec
        retrieval ← owns a Mongo query        └── tests/ unit · contract · integration
        llm · auth · ingest · scoring
                                              server.py: DELETED
  2 layers, fused                             4 layers, dependency rule enforced (AD-5)
  0 hermetic entry points                     every layer testable in isolation
```

### 2.2 Layer model

```
┌──────────────────────────────────────────────────────────────────────────┐
│  INTERFACE            app/api/                                           │
│  FastAPI routers, transport DTOs, dependencies, exception handlers       │
│  Knows: application ports, domain models.   Never: motor, redis, SDKs.   │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ calls use cases
┌───────────────────────────────▼──────────────────────────────────────────┐
│  APPLICATION          application/                                       │
│  Use cases (run research, run explanation, job lifecycle) + PORTS        │
│  Knows: domain, ports (Protocols).         Never: any concrete adapter.  │
└───────────┬───────────────────────────────────────────┬──────────────────┘
            │ orchestrates                              │ implemented by
┌───────────▼───────────────────────┐   ┌───────────────▼──────────────────┐
│  AGENTS (LangGraph)   agents/     │   │  INFRASTRUCTURE  infrastructure/ │
│  Graphs + nodes. Depends on ports │   │  Mongo, Redis, LLM providers,    │
│  (LLMClient, ChunkRepository).    │   │  EDGAR/BSE/yfinance, OTel/Prom.  │
└───────────┬───────────────────────┘   └───────────────┬──────────────────┘
            │ uses                                      │ depends on
┌───────────▼───────────────────────────────────────────▼──────────────────┐
│  DOMAIN               domain/                                            │
│  Entities, value objects, pure policy (scoring, citations, claims).      │
│  Knows: nothing. Imports stdlib + pydantic only.                         │
└──────────────────────────────────────────────────────────────────────────┘

Dependency rule: arrows point inward. Enforced by test, not review (AD-5).
```

### 2.3 Target package layout

```
backend/
  app/
    main.py                  create_app() factory + lifespan  ← fixes 01 B-6 / D-4
    settings.py              pydantic-settings Settings (AD-9)
    container.py             composition root: builds adapters, wires use cases
    api/
      deps.py                current_user, get_container, require_admin
      errors.py              RequestValidationError handler (moved, unchanged)
      routes/                health · auth · ingest · companies · reports · learning
      dto/                   transport-only request/response models (AD-11)
  domain/
    models.py                SourceDocument, Filing, Report, Explanation, Job
    events.py                TraceEvent — the {node,status,message,ts} contract (C-2)
    scoring.py               ← moved verbatim from agents/scoring.py (C-7)
    citations.py             NEW pure: marker validation/stripping (03 §5.2)
    claims.py                ← from nodes._extract_candidate_claims (C-5 preserved)
    chunking.py              ← from retrieval.chunk_text
    errors.py                DomainError hierarchy
  application/
    ports.py                 Protocols — the seam (§2.4)
    jobs.py                  job lifecycle (create/cancel/subscribe/reap)
    research.py              run-research use case  ← extracted from _run_pipeline (01 V-1)
    learning.py              run-explanation use case
  agents/
    state.py  learning_state.py
    graphs/research.py  graphs/learning.py
    nodes/retriever · extractor · tone · synthesizer · fact_checker · explainer
  infrastructure/
    mongo/client · repositories · indexes · migrations/
    redis/client · job_store · event_bus · rate_limiter
    llm/client · registry · providers/{gemini,openai_compatible,anthropic}
    external/edgar · bse · yfinance · sec_index · resend
    observability/logging · tracing · metrics
    security/passwords · sessions · ssrf
  tests/
    unit/          NEW — hermetic, no server, no network
    contract/      NEW — OpenAPI snapshot + response-shape assertions
    integration/   ← existing backend_test*.py move here unchanged (C-6)
```

**What this is not:** a package per concept. `domain/models.py` is one file for
all entities; `infrastructure/mongo/repositories.py` is one file for both
repositories. Files split when two teams or two lifecycles touch them, not
because a diagram has two boxes.

### 2.4 Ports (`application/ports.py`)

`typing.Protocol`, structural typing — no ABCs, no registration, no inheritance
in adapters.

```python
class ChunkRepository(Protocol):
    async def chunks_for_ticker(self, ticker: str, limit: int = 2000) -> list[Chunk]: ...
    async def count_for_ticker(self, ticker: str) -> int: ...
    async def add_document(self, doc: IngestedDocument) -> IngestResult: ...

class ReportRepository(Protocol):
    async def save(self, report: Report) -> None: ...
    async def get(self, report_id: str, *, owner_id: str) -> Report | None: ...   # 10 §4.2
    async def list_for_user(self, user_id: str, *, ticker: str | None, limit: int) -> list[ReportSummary]: ...
    async def delete(self, report_id: str, *, owner_id: str) -> bool: ...

class ExplanationRepository(Protocol): ...        # same shape, Learning

class JobStore(Protocol):
    async def create(self, job: Job) -> None: ...
    async def get(self, job_id: str) -> Job | None: ...
    async def set_status(self, job_id: str, status: JobStatus, **fields) -> None: ...
    async def active_count(self) -> int: ...
    async def reap(self) -> int: ...

class EventBus(Protocol):
    async def publish(self, job_id: str, event: TraceEvent) -> None: ...
    def subscribe(self, job_id: str) -> AsyncIterator[TraceEvent]: ...   # ← fixes 01 D-1
    async def history(self, job_id: str) -> list[TraceEvent]: ...

class LLMClient(Protocol):
    async def text(self, system: str, user: str, *, tier: ModelTier, budget_s: float) -> str: ...
    async def json(self, system: str, user: str, schema: type[T], *, tier: ModelTier, budget_s: float) -> T: ...

class RateLimiter(Protocol):
    async def hit(self, key: str) -> bool: ...     # True == allowed
    async def clear(self, key: str) -> None: ...
```

> **Anti-YAGNI check.** Seven protocols across six concerns (the two output
> repositories share a shape, so §2.6 lists them on one row) — the minimum
> satisfying OB-1 and OB-3:
> `ChunkRepository` and the two output repositories make retrieval and use cases
> testable without Mongo (`01 B-1`); `JobStore`/`EventBus` are changing
> implementation (EQ-1); `LLMClient` is depended on by every node (`01 V-7`);
> `RateLimiter` is moving to Redis. **No port exists for a concern that is
> neither changing implementation nor blocking a test.**

### 2.5 Composition root (`app/container.py`)

```python
@dataclass(frozen=True)
class Container:
    settings: Settings
    chunks: ChunkRepository;  reports: ReportRepository
    explanations: ExplanationRepository
    jobs: JobStore;  events: EventBus;  llm: LLMClient;  limiter: RateLimiter
    research: ResearchPipeline;  learning: LearningPipeline

def build_container(settings: Settings) -> Container: ...   # the ONLY place adapters are constructed
```

Routers receive it through one dependency
(`container: Container = Depends(get_container)`) read off `app.state`. No
module-level singletons, no import-time I/O. This single change makes
`create_app()` possible and therefore unblocks every hermetic test.

### 2.6 Port → adapter matrix

| Port | Phase 3–4 adapter | Phase 7 adapter | Test double |
|---|---|---|---|
| `ChunkRepository` | `mongo.ChunkRepo` | unchanged | in-memory list |
| `ReportRepository` / `ExplanationRepository` | `mongo.ReportRepo` | unchanged | in-memory dict |
| `JobStore` | `memory.JobStore` | **`redis.JobStore`** ([`09`](09_Redis_Architecture.md) §6) | in-memory dict |
| `EventBus` | `memory.EventBus` (per-subscriber fan-out) | **`redis.EventBus`** (Streams, [`09`](09_Redis_Architecture.md) §4) | in-memory |
| `LLMClient` | `llm.MultiProviderClient` | unchanged | scripted responses |
| `RateLimiter` | `memory.RateLimiter` (ports `auth._hits`) | **`redis.RateLimiter`** ([`09`](09_Redis_Architecture.md) §7) | fake clock |

The Phase-3/4 adapters are **not throwaway**: they remain the documented
fallback ([`09`](09_Redis_Architecture.md) RA-2) and the mechanism that makes
the Phase-7 swap verifiable — one behavioral suite runs against both.

### 2.7 Request flow (after migration)

```
POST /api/reports/generate
  │
  ├─ api/routes/reports.py      validate DTO · current_user · admin/SSRF gate (10 §4.3)
  ├─ application/research.py    ResearchPipeline.start(ticker, query, user, llm_cfg)
  │     ├─ chunks.count_for_ticker()           → ChunkRepository → Mongo
  │     ├─ jobs.active_count() / jobs.create() → JobStore        → Redis
  │     └─ spawn task: _run()  with deadline (07 §5.4)
  │           ├─ agents/graphs/research.astream(state)
  │           │     └─ nodes → LLMClient / ChunkRepository (ports only)
  │           ├─ events.publish(...) per trace event → EventBus → Redis Stream
  │           ├─ domain/scoring.compute_scorecard(report)        (pure)
  │           └─ reports.save(report)          → ReportRepository → Mongo
  └─ 200 {"job_id": ...}                        ← contract unchanged (C-1)
```

Note `{"job_id"}` here and `{"id"}` for Learning (`02 F-1`). That difference
lives in the DTO layer; the use case returns a `Job` and each router serializes
to its own frozen envelope. **This is the structural reason both features share
a pipeline without violating C-1.**

---

## 3. Design Decisions

| ID | Decision | Rationale | Rejected |
|---|---|---|---|
| **AD-1** | **Application factory `create_app()`; no import-time I/O or module-scope `os.environ`.** | Root cause of `01 D-4`/`B-6` and of the entire testing inversion (`05` T-3). Everything else here is cheap once it lands. | Module-level app + env fixtures — leaves `import server` requiring Mongo |
| **AD-2** | Ports are `typing.Protocol`; adapters are plain classes. No ABC, no DI library. | Structural typing gives the seam with zero runtime machinery | `abc.ABC`; `dependency-injector`/`punq` |
| **AD-3** | One composition root; adapters constructed nowhere else | Auditable in one file, swappable per environment | Module-level singletons (`01 V-8`) |
| **AD-4** | **Strangler fig in 7 shippable phases**; `server.py` shrinks until deleted | Every phase leaves `main` green and deployable | Big-bang rewrite on a branch |
| **AD-5** | **The dependency rule is enforced by an automated test**, not review — ~40-line AST walk, no new dependency | `01 B-1`…`B-6` happened *under* review | `import-linter` (a dependency for 40 lines); review only |
| **AD-6** | Domain imports stdlib + pydantic only | Pydantic models LLM-output structure, which is domain policy | Zero third-party in domain — forces duplicating validation |
| **AD-7** | **LangGraph nodes depend on ports, never adapters** — `retriever_node(state, *, chunks)` replaces `db=db` | Makes every node unit-testable with a 10-line fake; removes motor from the domain path (`01 B-2`) | Keep `db` injection — Learning inherits the problem |
| **AD-8** | **`EventBus.subscribe()` returns a per-subscriber iterator** | `01 D-1` is a *contract* defect: the port must forbid the single-consumer shape, so both adapters are obliged to fan out correctly | Fix the queue in `server.py` — fixes reports only |
| **AD-9** | `pydantic-settings`, one `Settings`, validated at startup | 24 scattered `os.environ` reads today, several with silently divergent defaults (the `01 D-3` `base_url` divergence). Fail-fast mirrors the frontend's `env.ts`. | `os.environ.get()` defaults |
| **AD-10** | **`agents/auth.py` is moved, not refactored** → `infrastructure/security/` with signatures intact | The most-tested module (~40 tests), stdlib-only per C-3, no import-time side effects. Refactoring buys nothing and risks the auth surface. | Wrap in a `UserRepository` port |
| **AD-11** | **Transport DTOs separate from domain models** | The mechanism guaranteeing C-1 while internals move; the `id`/`job_id` divergence (`02 F-1`) is a DTO concern and must not leak inward | Return domain objects from routers |
| **AD-12** | **No LangGraph checkpointer in v1** | Retry issues a **new job id** per the frozen contract, so resume has no UI surface. A checkpointer costs a dependency + a write per node for a capability nothing can invoke. | `langgraph-checkpoint-mongodb` now |
| **AD-13** | **Observability wired in the composition root and a decorator**, never inside domain or application code | Keeps OTel/Prometheus out of the AD-5 matrix; domain stays import-clean | Instrument use cases directly |

---

## 4. Dependency Rule Enforcement (AD-5)

`backend/tests/unit/test_architecture.py` — allowed-import matrix:

| Layer | May import |
|---|---|
| `domain/` | stdlib, `pydantic` |
| `application/` | stdlib, `pydantic`, `domain/` |
| `agents/` | stdlib, `pydantic`, `langgraph`, `domain/`, `application/ports` |
| `infrastructure/` | anything, `domain/`, `application/ports` |
| `app/` | anything |

Forbidden and asserted explicitly:

- `domain/` → `application`, `agents`, `infrastructure`, `app`, `motor`,
  `redis`, `fastapi`, `httpx`
- `application/` → `infrastructure`, `app`, `motor`, `redis`, `fastapi`
- `agents/` → `infrastructure`, `app`, `motor`, `redis`
- any module → `server` (the legacy module, during migration)

The test walks `ast.parse` over every `.py` under `backend/`, resolves
`Import`/`ImportFrom` to a layer, and asserts membership. Runs in the hermetic
CI job (< 1 s). Violations name file, line, and offending import.

---

## 5. Migration Strategy

**Strangler fig.** `server.py` remains the running application throughout;
routes are lifted out one group at a time behind an unchanged router prefix.
After each phase `main` is green, deployable, and contract-identical.

### 5.1 Phase table

| Ph | Name | Moves | Net-new | Deletes | Contract risk | Verification gate |
|---|---|---|---|---|---|---|
| **0** | **Safety net** | — | `tests/contract/` OpenAPI snapshot + response-key assertions for all 31 routes; `tests/unit/` for the 14 untested pure functions (`05` §3.2); **security regression tests (`10` SR-11)**; `pytest-cov` baseline; hermetic CI | — | **none** | Snapshot committed; hermetic suite green in CI |
| **1** | **App factory** | `create_app()`, `Settings`, `Container` skeleton; `server.py` becomes `app = create_app()` | `app/main.py`, `settings.py`, `container.py`; **`10` SD-3 startup gates, SD-4 no-body-logging, SD-15 bulk session revocation CLI** | import-time `os.environ` / `build_graph` | none | Imports with **no env vars set**; E2E green; snapshot byte-identical |
| **2** | **Domain extraction** | `scoring.py`, `chunk_text`, `_extract_candidate_claims`, `_format_docs`, `_strip_code_fence` → `domain/` | `citations.py`, `models.py`, `events.py` | — | none (pure moves) | Phase-0 unit tests pass at new import paths |
| **3** | **Ports + Mongo adapters** | Mongo out of `retrieval.py` (`01 B-1`) and route handlers (`01 B-4`) → `infrastructure/mongo/` | `ports.py`; **`08 m0001` — all 25 indexes**; `maxTimeMS` (`07` X-14) | `db.*` calls in `agents/` | low | `explain()` shows `IXSCAN` for `08` A-1…A-8; retrieval testable with a fake repo |
| **4** | **Job lifecycle + EventBus** | `JOBS`/`JOB_QUEUES`/`_reap_jobs`/`push`/SSE generator → `application/jobs.py` + in-process `EventBus` | per-subscriber fan-out (**`01 D-1`**), restart sweep (**D-6**), `completed_at` (**D-8**); **job deadlines + retry budget (`07` §5.4–5.5)** | `server.py:52-53`, `:678-799` | **medium** — SSE is C-2-frozen | Streaming tests `05` T-8/T-9; two-tab manual check; deadline tests |
| **5** | **LLM adapter** | `llm.py` → `infrastructure/llm/`; one provider registry (**`01 D-3`**) | `LLMClient` adapter with budget-aware timeouts | duplicate dispatch at `llm.py:244-252`/`:273-280` | low | `test_llm_*.py` green unmodified |
| **6** | **Router split** | `server.py` routes → `app/api/routes/` (6 modules); DTOs → `app/api/dto/` | `require_admin`; **authorization model (`10` §4)**; scrypt N=2^16 (`10` §3.1); PDF timeout (`10` §6.2) | **`server.py` deleted** | **medium** | Snapshot byte-identical; cross-tenant tests: read → 404, rescore → 403 |
| **7** | **Platform** | `EventBus`/`JobStore`/`RateLimiter` → Redis; OTel + Prometheus; Dockerfile + compose; full CI | per [`09`](09_Redis_Architecture.md), [`10`](10_Backend_Security_Architecture.md) §9–§11 | `auth._hits` | medium | Redis-down drill; `/metrics` scrape; container smoke test |
| **L** | **Learning feature** | — | 4 routes + 2-node graph per [`03`](03_Learning_Backend_Design.md) | — | **none** (new surface) | Contract tests vs. the frozen Zod shapes |

### 5.2 Where the Learning build slots in

**Phase L may start after Phase 4 and must not start before it.** Phases 0–4
deliver exactly what Learning needs and cannot safely proceed without: the
use-case seam (OB-2) and the correct SSE fan-out (`01 D-1` / AD-8). Starting
earlier means writing that defect deliberately — the explicit warning in
[`03`](03_Learning_Backend_Design.md) §6.1.

Phases 5–7 are **independent of L** and may run in parallel or after.

### 5.3 Rules that make every phase safe

1. **The Phase-0 OpenAPI snapshot is the contract oracle.** Any phase that
   changes it fails CI. It is regenerated only by an explicit reviewed commit —
   and only Phase L is expected to change it (4 additive routes).
2. **One phase per PR.** No phase depends on a later phase's code.
3. **Moves are moves.** A phase that relocates code does not also change its
   logic. Behavior changes (`01 D-1`, D-6, D-8, deadlines, scoping) are isolated
   to Phases 4 and 6, each with its test written first.
4. **`git mv` where possible** so review sees a rename, not a rewrite.
5. **Rollback = revert the PR.** No data migration before Phase 7 is destructive
   ([`08`](08_MongoDB_Data_Architecture.md) §11.3), and no phase before 7 adds a
   runtime service.

---

## 6. Risk Register

| ID | Risk | Sev | Likelihood | Mitigation | Gate |
|---|---|---|---|---|---|
| **MR-1** | **SSE behavior regresses in Phase 4**, breaking the shipped UI (C-2). Streaming has 1 test and 7 untested behaviors (`05` T-8…T-14). | **High** | Medium | Write T-8/T-9/T-13/T-14 in Phase 0 **before** touching the generator; preserve replay-then-subscribe ordering; manual two-tab + reconnect check | Ph 4 |
| **MR-2** | **Silent contract drift** — an internal refactor changes a response key nobody notices until the UI fails at the trust boundary | **High** | Medium | Phase-0 snapshot + per-route response-key assertions; a snapshot diff is a blocking CI failure | every phase |
| **MR-3** | **Migration stalls half-done**, leaving two architectures indefinitely — worse than either | **High** | Medium | Phases are ≤ 1 PR each, ordered so value lands early (Ph 0–1 alone fix `01 D-4`/`05` T-3); `server.py` deletion is a Phase-6 **exit criterion**, not a cleanup wish | milestone review |
| **MR-4** | **Dependency-rule decay** after freeze | Medium | High without AD-5 | AD-5 test in the hermetic CI job from Phase 0 | CI |
| **MR-5** | **Auth surface breakage** while moving `agents/auth.py` | **High** | Low | AD-10: move only; ~40 existing auth tests are the gate; no phase changes hashing/session/OTP logic except the explicit `10` §3.1 rehash | Ph 6 |
| **MR-6** | **Redis becomes a new hard dependency** — Redis down = outage where today there is none | Medium | Medium | [`09`](09_Redis_Architecture.md) §8 degradation policy; in-process adapters retained (§2.6); drill on the Phase-7 gate | Ph 7 |
| **MR-7** | **Test-suite non-hermeticity blocks CI** (`05` T-1): E2E needs live SEC/yfinance/LLM | Medium | High | Phase 0 marks network tests `@pytest.mark.live`; CI runs the hermetic subset; live stays manual/nightly. `pytest.ini` `addopts` untouched (C-4) — markers go on tests, not config | Ph 0 |
| **MR-8** | **Scope creep** — "while we're in here" refactors inflate a phase past reviewability | Medium | High | §5.3 rule 3; `ponytail:` markers preserved (C-5), not opportunistically resolved | review |
| **MR-9** | **Learning starts before Phase 4**, shipping `01 D-1` twice | Medium | Medium | §5.2 hard ordering constraint, restated in [`03`](03_Learning_Backend_Design.md) | milestone plan |
| **MR-10** | **`create_app()` changes startup semantics** — warmup, index creation, and company-index load currently run in a deprecated `@app.on_event("startup")` | Low | Medium | Phase 1 moves them to a `lifespan` context manager; warmup stays a background task so startup latency is unchanged | Ph 1 |

---

## 7. Implementation Order (authoritative)

```
Ph0  Safety net ──► Ph1  App factory ──► Ph2  Domain ──► Ph3  Ports + Mongo
                                                              │
                                             ┌────────────────┴────────────────┐
                                             ▼                                 │
                                      Ph4  Jobs + EventBus (01 D-1)            │
                                           + deadlines (07 §5.4)               │
                                             │                                 │
                              ┌──────────────┴──────────────┐                  │
                              ▼                             ▼                  ▼
                        PhL  Learning              Ph5  LLM adapter    (Ph5–7 independent
                              │                             │           of PhL; may run
                              │                             ▼           in parallel)
                              │                      Ph6  Router split
                              │                        + authorization
                              └──────────────┬──────────────┘
                                             ▼
                                Ph7  Redis + OTel/Prom + Docker + CI
```

**Critical path to Learning:** Ph0 → Ph1 → Ph2 → Ph3 → Ph4 → PhL.
**Critical path to production readiness:** … → Ph6 → Ph7.

### 7.1 Per-phase exit criteria

| Ph | Exit criteria |
|---|---|
| 0 | Hermetic suite runs with no server/network/API key; OpenAPI snapshot committed; coverage baseline published; CI green |
| 1 | `from app.main import create_app` succeeds with **no env vars set**; SD-3/SD-4/SD-15 in place; E2E green; snapshot unchanged |
| 2 | `domain/` passes AD-5 with zero non-stdlib/pydantic imports; unit tests moved and green |
| 3 | `retrieve()` callable against a fake `ChunkRepository`; no `db.` reference remains in `agents/`; `08 m0001` applied and `IXSCAN` verified |
| 4 | Two concurrent SSE consumers each receive the **full** stream (`01 D-1`); orphaned `running` jobs swept (D-6); `completed_at` persisted (D-8); job deadline bounds a synthetic slow run |
| 5 | One provider dispatch table; `base_url` resolution identical between validate and generate (`01 D-3`); `test_llm_*.py` green unmodified |
| 6 | **`backend/server.py` deleted**; snapshot byte-identical; all 31 routes served from `app/api/routes/`; authorization matrix (`10` §4.4) enforced at the repository layer |
| 7 | Redis-backed events/jobs/limits; `/metrics` scrapeable; traces emitted; `docker compose up` runs the full stack; CI runs hermetic + contract + lint + audit |
| L | 4 Learning routes validate against the frozen Zod shapes; UI reaches `completed` end-to-end |

---

## 8. Cross-Reference Index

| Referenced here | Target |
|---|---|
| `01 B-1`, `B-2`, `B-4`, `B-6`, `D-1`, `D-3`, `D-4`, `D-6`, `D-8`, `V-1`, `V-7`, `V-8` | [`01_Backend_Architecture_Review.md`](01_Backend_Architecture_Review.md) §2, §4, §6 |
| `02 F-1` | [`02_API_Coverage_Audit.md`](02_API_Coverage_Audit.md) §5 |
| `03` §5.2, §6.1 | [`03_Learning_Backend_Design.md`](03_Learning_Backend_Design.md) |
| `05` T-1, T-3, T-8…T-14, §3.2 | [`05_Testing_Audit.md`](05_Testing_Audit.md) |
| `07` §5.4, §5.5, X-14 | [`07_LangGraph_Architecture.md`](07_LangGraph_Architecture.md) |
| `08` A-1…A-8, `m0001`, §11.3 | [`08_MongoDB_Data_Architecture.md`](08_MongoDB_Data_Architecture.md) |
| `09` RA-2, §4, §6, §7, §8, §10.1 | [`09_Redis_Architecture.md`](09_Redis_Architecture.md) |
| `10` §3.1, §4, §4.2, §4.3, §4.4, §6.2, §9–§11, SD-3, SD-4, SD-15, SR-11 | [`10_Backend_Security_Architecture.md`](10_Backend_Security_Architecture.md) |

---

## 9. Ratification

| # | Item | Position |
|---|---|---|
| 1 | `CLAUDE.md` § Dependencies amendment for the approved stack (§0.1) | Recorded, not applied — `CLAUDE.md` is owner-maintained |
| 2 | **EQ-2** — `POST /reports/rescore`: admin-gate or delete | Plan assumes **admin-gate in Ph 6**; reversible either way |
| 3 | **EQ-3** — report read scoping | Plan assumes **scoped in Ph 6**, matching the Learning default. Cross-tenant 200 → 404; no contract shape changes (C-1 intact) |
| 4 | **§5.2** — Learning cannot precede Phase 4 | Hard ordering constraint |
| 5 | **`server.py` deletion at Phase 6** | Exit criterion, not aspiration |
| 6 | **[`07`](07_LangGraph_Architecture.md) §5.4 job deadlines** land in Phase 4 — a user-visible behavior change on the pathological tail | Recommended; see [`07`](07_LangGraph_Architecture.md) §13 item 5 |
| 7 | **[`10`](10_Backend_Security_Architecture.md) SD-15 bulk session revocation** lands in Phase 1, ahead of the security work it unblocks | Recommended |

**On ratification:** change the status header to 🔒 **FROZEN**, record date and
approver, and treat subsequent changes as numbered amendments.

---

*Companion documents:* [`07`](07_LangGraph_Architecture.md) ·
[`08`](08_MongoDB_Data_Architecture.md) · [`09`](09_Redis_Architecture.md) ·
[`10`](10_Backend_Security_Architecture.md) · index:
[`00_README.md`](00_README.md)
