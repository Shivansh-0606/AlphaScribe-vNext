# Redis Architecture

**Status:** 🔒 **FROZEN** — `v1.0`, ratified 2026-08-03 · amendments only (§16)
**Milestone:** Backend Engineering M1 (post-audit) · **Date:** 2026-08-03
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main` · commit `7404b67`
**Resolves:** EQ-1 ([`01_Backend_Architecture_Review.md`](01_Backend_Architecture_Review.md) §7)
**Depends on:** [`06_Clean_Architecture_Migration_Plan.md`](06_Clean_Architecture_Migration_Plan.md) (AD-8, Ph 4/7),
[`08_MongoDB_Data_Architecture.md`](08_MongoDB_Data_Architecture.md) (DA-0)
**Referenced by:** [`06`](06_Clean_Architecture_Migration_Plan.md) §2.3 · [`07`](07_LangGraph_Architecture.md) §5.4, §6.3 · [`08`](08_MongoDB_Data_Architecture.md) §2.1, §7

### Document control

| Version | Date | Change |
|---|---|---|
| v1.0 | 2026-08-03 | **FROZEN.** Final consistency pass: §9.1 auth changed from bare `requirepass` to scoped ACL users, reconciling with [`10`](10_Backend_Security_Architecture.md) SD-5/§8.2 (rotation needs an overlap window) |
| v1.0-rc1 | 2026-08-03 | Expanded §9 (operational settings: eviction, persistence, restart behavior, connection management, HA stance); added §3.1 key-lifecycle diagram and §9.4 restart-state diagram; `MAX_JOB_LIFETIME` 900 s → **600 s** per `07` §5.3; added §14 deferred items; fixed cross-references |
| v0.9 | 2026-08-03 | Initial proposal |

> **ID prefixing.** IDs defined here use `RA-`, `RR-`. References to IDs owned by
> another document carry that document's number — e.g. `01 D-1`, `06 AD-8`.

---

## 0. Decision Record — EQ-1

**EQ-1 asked:** adopt Redis for the job lifecycle, or keep the in-process
registry + Mongo mirror?

**Ruling: Redis is adopted.** Directed by the platform owner as part of the
approved stack (Redis, OpenTelemetry, Prometheus, Docker, GitHub Actions). The
audit's reservation — that Redis solves a multi-instance problem a
single-process deployment does not yet have — is **recorded and closed**. This
document designs to the ruling and does not re-litigate it.

**What the ruling buys.** Three defects and one documented ceiling are resolved
by Redis primitives rather than bespoke code:

| Existing problem | Redis resolution |
|---|---|
| **`01 D-1`** — a single-consumer `asyncio.Queue` splits the SSE stream between concurrent readers | Redis **Streams** with independent per-connection cursors: every reader gets every event, by construction (§4.2) |
| **`01 D-6`** — jobs orphaned at `running` after a restart, with no producer | Job hash + timestamped active-set ZSET make orphan detection a range query (§6) |
| **Fragile replay** — the `to_skip` counter at `server.py:989-996` | `XRANGE` then `XREAD` from the last id: exact continuation, no counting (§4.3) |
| **`auth.py:45-46` `ponytail:`** — process-local rate-limit dict, "move to Mongo/Redis if it ever scales" | Its stated upgrade path, taken (§7) |

**Cost accepted:** one runtime service, one dependency (`redis>=5`), one new
failure domain. §8 and §9 bound it.

---

## 1. Scope & Invariants

| # | Invariant | Consequence |
|---|---|---|
| **RA-0** | **Redis is never the system of record** (restates `08` DA-0). Nothing whose loss changes a user-visible outcome *after a job terminates* lives only in Redis. | Losing Redis loses in-flight streams. It never loses a report, an explanation, a session, or an account. |
| **RA-1** | **Every key has a TTL or a bounded size.** No unbounded growth, ever. | §3 assigns a bound to every key family. It is also what makes §10.3 keyspace versioning work without data migrations. |
| **RA-2** | **All access goes through ports** (`EventBus`, `JobStore`, `RateLimiter`). No `redis` import outside `infrastructure/redis/`. | Enforced by the `06 AD-5` dependency test. In-process adapters remain as the documented fallback. |
| **RA-3** | **No approved API contract changes.** SSE framing, event shapes, and the `{id}`/`{job_id}` envelopes are untouched. | Redis is an implementation swap behind three ports. |
| **RA-4** | **No secrets, no PII beyond an opaque `user_id`.** | Rate-limit keys hash the identifier (§7.2). |

---

## 2. System Topology

```
                       ┌───────────────────────────────────────────────┐
  browser  ──SSE──►    │  backend instance A         instance B  (…N)  │
  (EventSource)        │   ├─ SSE conn ─┐             ├─ SSE conn      │
                       │   └─ job task  │             └─ job task      │
                       └────────┬───────┴─────────────────┬────────────┘
                                │ XADD / XREAD / PUBLISH  │
                       ┌────────▼─────────────────────────▼────────────┐
                       │                   REDIS 7                     │
                       │  job hashes · event streams · active ZSET ·   │
                       │  cancel pub/sub · rate limits · index cache   │
                       │  AOF everysec · maxmemory-policy noeviction   │
                       └───────────────────┬───────────────────────────┘
                                           │ terminal state + final document
                       ┌───────────────────▼───────────────────────────┐
                       │           MONGODB  (system of record)         │
                       └───────────────────────────────────────────────┘
```

**The multi-instance property that matters:** an SSE connection on instance B
can stream a job whose pipeline task runs on instance A, because the event
transport is Redis rather than an in-process queue. That is the point of the
ruling, and it is what the current architecture cannot do at any price.

---

## 3. Keyspace Design

**Namespace:** `as:v{schema}:...` — `as` = AlphaScribe, `v1` = keyspace schema
version. Bumping `v` is the migration mechanism for any incompatible key-shape
change (§10.3): both versions coexist and old keys expire naturally.

| Key | Type | Contents | Bound | RA-1 |
|---|---|---|---|---|
| `as:v1:job:{job_id}` | HASH | `kind`, `status`, `user_id`, `ticker`, `created_at`, `updated_at`, `owner_instance`, `error` | `EXPIRE 24 h`, refreshed on write | ✅ |
| `as:v1:job:{job_id}:events` | **STREAM** | one entry per trace event: `{data: <json TraceEvent>}` | `MAXLEN ~ 1000`; `EXPIRE 1 h` after terminal | ✅ |
| `as:v1:jobs:active` | ZSET | member `job_id`, score = start epoch | pruned by score on every read (§6.2) | ✅ |
| `as:v1:cancel` | PUB/SUB | `{"job_id": "..."}` | transient by nature | ✅ |
| `as:v1:rl:{scope}:{key_hash}` | ZSET | sliding-window hit timestamps | `EXPIRE` = window (15 min) | ✅ |
| `as:v1:cache:secindex` | STRING | SEC company universe JSON | `EXPIRE 24 h` | ✅ |
| `as:v1:lock:{name}` | STRING | `SET NX PX` holder token | `PX` lease | ✅ |

**Why `job_id` is safe as a key component:** it is a server-generated uuid4,
never user-supplied. No key is built from unsanitized client input.

### 3.1 Key lifecycle

```
  admission          running                    terminal              +1 h        +24 h
      │                 │                          │                    │            │
job:{id}  ──HSET queued─┼──HSET running────────────┼──HSET completed────┼────────────┤ EXPIRE
      │                 │                          │                    │            ▼
      │                 │                          │                    │        (gone; Mongo
      │                 │                          │                    │         holds the record)
job:{id}:events ──XADD──┼──XADD ×N────────────────►┼──XADD terminal─────┤ EXPIRE
      │                 │  MAXLEN ~1000            │                    ▼
      │                 │                          │              (replay window closes;
      │                 │                          │               GET /reports/{id} serves
      │                 │                          │               from Mongo thereafter)
      │                 │                          │
jobs:active ──ZADD──────┼──────────────────────────┼──ZREM
      │                 │                          │
      └── ZREMRANGEBYSCORE prunes anything older than MAX_JOB_LIFETIME (600 s) ──────►
          (self-healing: a crashed worker's slot expires by time, never leaks)
```

---

## 4. Event Transport (Streams) — the `01 D-1` fix

### 4.1 Why Streams, and why **not** consumer groups

| Option | Behavior | Verdict |
|---|---|---|
| Pub/Sub | fire-and-forget; a late or blipped subscriber loses events | ❌ breaks replay-on-reconnect, which the UI relies on |
| Stream + **consumer group** (`XREADGROUP`) | entries are **distributed** across group members | ❌ **this is `01 D-1` again, in a new colour** — two SSE connections in one group would split the stream |
| **Stream + independent cursors** (`XREAD`) | every reader has its own cursor and sees **every** entry | ✅ **chosen** |

> **The single most important implementation note in this document.**
> `XREADGROUP` looks like the "proper" Streams API and would faithfully
> reproduce the exact defect Redis was adopted to fix. The `EventBus` port
> (`06 AD-8`) forbids the shape; §11 enforces it with a static ban test.

### 4.2 Publish path

```python
# infrastructure/redis/event_bus.py
async def publish(self, job_id: str, event: TraceEvent) -> None:
    key = f"as:v1:job:{job_id}:events"
    await self.r.xadd(key, {"data": json.dumps(event)}, maxlen=1000, approximate=True)
    await self.r.expire(key, 3600)
```

One `XADD` per trace event replaces the current dual write (in-memory list +
`asyncio.Queue`) **and** the Mongo `$push` (`08` DA-3) — ~15–25 Mongo writes per
job become zero.

### 4.3 Subscribe path (replaces `server.py:978-1006` wholesale)

```python
async def subscribe(self, job_id: str) -> AsyncIterator[TraceEvent]:
    key, last = f"as:v1:job:{job_id}:events", "0-0"     # "0-0" = from the beginning
    while True:
        resp = await self.r.xread({key: last}, block=15_000, count=100)
        if not resp:
            yield KEEPALIVE                              # → `: keepalive\n\n`
            continue
        for _, entries in resp:
            for entry_id, fields in entries:
                last = entry_id
                ev = json.loads(fields["data"])
                yield ev
                if is_terminal(ev):
                    return                               # → `event: end\ndata: {}\n\n`
```

Three defects disappear at once:

1. **Replay is exact.** Starting at `0-0` reads full history, then the cursor
   continues live. No snapshot, no `to_skip` counter, no assumption that the
   queue is unconsumed.
2. **Fan-out is correct.** Each connection owns its `last`. Two tabs, a
   reconnect, and a mid-job connect all receive the complete stream.
3. **Keepalives are free.** `block=15000` returning empty *is* the keepalive
   tick. The SSE framing the frontend sees is unchanged (RA-3).

### 4.4 Terminal semantics

The use case writes the terminal event (`{node:"pipeline", status:"ok"|"error"|
"warn"}`) to the stream, then sets `EXPIRE 3600` as a hard grace window. A
reconnect within the hour replays the whole run including its ending; after
that, `GET /reports/{id}` / `GET /learning/{id}` serves the durable Mongo record
— the correct source for a finished job anyway.

### 4.5 Connection-pool sizing ⚠️

A blocking `XREAD` **holds a connection from the pool for the block duration**.
With `max_connections` too low, concurrent SSE viewers starve every other Redis
call — including job creation.

**Rule: `max_connections ≥ (expected concurrent SSE connections) + 20`.**
Default **100**. `block=15000` (not 120 s) keeps connections cycling. A
`alphascribe_redis_pool_exhausted_total` counter alerts before it bites. See
also §9.5.

---

## 5. Cancellation (Pub/Sub)

Cancellation must reach the instance that **owns the asyncio task** — which,
multi-instance, is not necessarily the one receiving the HTTP request.

```
POST /learning/{id}/cancel   (instance B)
  ├─ HSET as:v1:job:{id} status=cancelled     # authoritative regardless of delivery
  ├─ PUBLISH as:v1:cancel {"job_id": id}
  └─ 200 {"id": id, "status": "cancelled"}    # frozen shape (02 F-1) — no `note` field

every instance subscribes to as:v1:cancel:
  └─ if job_id in local task registry: task.cancel()
       └─ CancelledError → use case emits {node:"pipeline", status:"warn"}
            → XADD to the stream → every SSE reader sees it → `event: end`
```

**Status is set before the publish**, so a dropped Pub/Sub message still leaves
the job correctly marked cancelled; worst case a pipeline runs to completion and
finds itself already cancelled at persistence time (checked before the Mongo
write). Cancellation is therefore **idempotent and delivery-tolerant** — which
the frontend requires, since it fires the call fire-and-forget and never reads
the response (`useExplanationJob.ts:107-112`).

[`07`](07_LangGraph_Architecture.md) §6.2 still applies: an in-flight provider
call inside `asyncio.to_thread` cannot be interrupted, so cancellation lands at
the next await point. The job deadline ([`07`](07_LangGraph_Architecture.md)
§5.4) is the independent backstop.

---

## 6. Job Registry & Concurrency Cap

### 6.1 Job hash

`HSET as:v1:job:{id}` carries live status; Mongo carries the durable record.
Reads prefer Mongo for terminal jobs (RA-0) and Redis for in-flight ones —
matching the existing precedence at `server.py:1019-1031`, where `reports` is
checked before the job registry (`08` RI-1).

### 6.2 Active set — ZSET, not a counter

```python
# start
await r.zadd("as:v1:jobs:active", {job_id: now_epoch})
# finish / cancel / fail
await r.zrem("as:v1:jobs:active", job_id)
# admission control
await r.zremrangebyscore("as:v1:jobs:active", "-inf", now - MAX_JOB_LIFETIME)  # self-healing
if await r.zcard("as:v1:jobs:active") >= MAX_ACTIVE_JOBS:
    raise TooManyJobs                                   # → 429, existing contract
```

**A ZSET, not `INCR`/`DECR`.** An `INCR` counter **leaks a slot permanently**
every time a worker crashes mid-job; after N crashes the system refuses all work
with a 429 and only a manual reset recovers it. Scored membership makes stale
entries expire by *time*, so the cap is self-healing.

**`MAX_JOB_LIFETIME = 600 s`** (amended in v1.0-rc1 from 900 s). The binding
invariant, asserted at startup per [`07`](07_LangGraph_Architecture.md) LR-9:

```
MAX_JOB_LIFETIME  >  max(JOB_DEADLINE) + GRACE
      600 s        >        300 s      +  30 s     ✅
```

Without this the reaper could free the slot of a still-running job and allow
over-admission beyond `MAX_ACTIVE_JOBS`.

### 6.3 Restart recovery (`01 D-6`)

On startup each instance:

1. `ZREMRANGEBYSCORE` prunes expired active entries;
2. queries Mongo for `jobs`/`explanation_jobs` with `status ∈ {queued, running}`
   (indexes `08` I-19/I-24) whose `id` is **not** in the active ZSET;
3. marks each `failed` with "server restarted", and appends a terminal event to
   its stream if the stream still exists.

An in-flight job at restart becomes a *failed* job the UI can retry, instead of
a permanent spinner.

---

## 7. Rate Limiting

### 7.1 Faithful port of the existing semantics

`agents/auth.py`'s `_recent_hits` prunes hits outside a 15-minute window and
caps at 5 — a **sliding** window. A fixed-window `INCR`+`EXPIRE` would allow a
2× burst across a boundary (10 attempts in ~1 s), silently weakening a
brute-force control during a "pure infrastructure" migration.

```python
key = f"as:v1:rl:{scope}:{sha256(identifier)}"
async with r.pipeline() as p:
    p.zremrangebyscore(key, "-inf", now - WINDOW)
    p.zcard(key)
    p.zadd(key, {f"{now}:{token_urlsafe(6)}": now})   # unique member per hit
    p.expire(key, WINDOW)
    _, count, _, _ = await p.execute()
allowed = count < MAX_HITS
```

Preserved: keyed by email only, not IP (the reasoning at `server.py:217-222`
still holds — IP-keying would self-DoS shared NATs). Preserved: the hit is
recorded **before** the DB await, with `clear_hits` on success — the temporal
coupling documented at `server.py:226` / `:263`.

### 7.2 Privacy (RA-4)

The identifier is **SHA-256 hashed** before it becomes part of a key. Today's
in-process dict holds raw emails in memory; a shared Redis with operator access
and on-disk persistence should not. Hashing costs nothing and keeps account
identifiers out of `--scan` output and AOF files.

### 7.3 Limits

| Scope | Key | Limit | Rationale |
|---|---|---|---|
| `login` | email hash | 5 / 15 min | existing |
| `reset-req` | email hash | 5 / 15 min | existing |
| `reset-verify` | email hash | 5 / 15 min | existing |
| `jobs` | `user_id` | **10 / hour** ✅ new | `MAX_ACTIVE_JOBS` bounds *concurrency*, not *volume*: one user can serially burn unlimited LLM quota today |

---

## 8. Failure & Degradation Policy

**The central question Redis adoption forces.** Answered per concern, not
globally.

| Concern | Redis unavailable | Policy | Rationale |
|---|---|---|---|
| **Start a job** (`POST /reports/generate`, `/learning/explain`) | 503, retryable message | 🔒 **fail closed** | Starting a pipeline nobody can observe burns real LLM spend for an unobservable result |
| **Stream an in-flight job** | SSE emits `{node:"pipeline", status:"error"}` → UI shows failed + retry | 🔒 fail closed | Correct per SCR-08 error behaviour |
| **Fetch a finished report/explanation** | ✅ unaffected | — | Served from Mongo (RA-0) |
| **Auth, account, ingest, search, list** | ✅ unaffected | — | No Redis dependency |
| **Rate limiting** | requests **allowed**, WARN log + `alphascribe_ratelimit_degraded` | 🔓 **fail open** ⚠️ | §8.1 |
| **Cancellation** | falls back to the local task registry (works single-instance) | 🔓 degrade | Job deadline is the backstop |
| **SEC index cache** | falls back to the in-process 24 h cache | 🔓 degrade | Already current behavior |

### 8.1 ⚠️ Fail-open rate limiting — an explicit trade-off

Fail-**closed** means *Redis down ⇒ nobody can log in*: a cache outage becomes a
total authentication outage, a self-inflicted DoS and the larger real-world
risk.

Fail-**open** leaves a brute-force window while Redis is down, bounded by two
things already in place:

- **`hashlib.scrypt`** costs ~50–100 ms per verification today and ~200 ms at
  the proposed N=2^16 ([`10`](10_Backend_Security_Architecture.md) §3.1) — a
  hard natural throughput limit on online guessing;
- the outage is loud: WARN logs + a Prometheus gauge + a **paging** alert.

**Recommendation: fail open, with alerting.** A genuine security decision, not
an implementation detail — §16 lists it for explicit sign-off. If the ruling is
fail-closed, one setting flips, but the outage characteristic must be accepted
knowingly.

---

## 9. Operational Settings

### 9.1 Server configuration

```conf
# ── network ────────────────────────────────────────────────────────────────
bind 0.0.0.0                    # container-internal network only (10 SD-5)
protected-mode yes
port 6379
timeout 0                       # blocking XREAD holds idle-looking connections;
                                # a non-zero idle timeout would kill live SSE readers
tcp-keepalive 300

# ── auth: an ACL user, NOT bare `requirepass` ──────────────────────────────
# `requirepass` has no rotation overlap window; two ACL users do (10 §8.2).
# The app user is scoped to the as:v1: keyspace and the cancel channel, and is
# denied @admin/@dangerous — so FLUSHDB (an incident lever, 10 §12.3) requires
# the separate operator credential, not the application's.
user default off
user alphascribe on >${REDIS_PASSWORD} ~as:v1:* &as:v1:cancel +@all -@admin -@dangerous
user operator   on >${REDIS_ADMIN_PASSWORD} ~* &* +@all

# ── memory ─────────────────────────────────────────────────────────────────
maxmemory 256mb
maxmemory-policy noeviction     # ⚠️ CRITICAL — §9.2

# ── persistence ────────────────────────────────────────────────────────────
appendonly yes
appendfsync everysec            # ≤1 s loss window; RA-0 makes loss survivable
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
save 900 1                      # RDB as a coarse secondary snapshot
stop-writes-on-bgsave-error no  # a failed snapshot must not halt job intake;
                                # RA-0 means the snapshot is not load-bearing

# ── client buffers ─────────────────────────────────────────────────────────
client-output-buffer-limit pubsub 32mb 8mb 60   # a wedged cancel-subscriber is
                                                # disconnected, not left to grow
# ── diagnostics ────────────────────────────────────────────────────────────
slowlog-log-slower-than 10000   # 10 ms — every op here should be sub-millisecond
slowlog-max-len 256
latency-monitor-threshold 100

# ── deliberately off ───────────────────────────────────────────────────────
notify-keyspace-events ""       # nothing subscribes to expiry events
databases 1                     # db 0 only; namespacing is by key prefix (§3)
```

### 9.2 Eviction — `noeviction` is mandatory, not a preference

> Under `allkeys-lru` (a common default in managed Redis) the server would
> silently evict **live job event streams** under memory pressure. A running
> pipeline's SSE stream would simply stop mid-run, with no error anywhere in the
> system.

`noeviction` converts that into a loud `OOM command not allowed when used
memory > 'maxmemory'` error, which the §8 fail-closed policy already handles
correctly: job creation 503s, existing reports keep serving, and an alert fires.

**A managed-Redis deployment must have this verified, not assumed.** The
application asserts it at startup:

```python
policy = (await r.config_get("maxmemory-policy"))["maxmemory-policy"]
if policy != "noeviction":
    logger.error("REDIS MISCONFIGURED: maxmemory-policy=%s (require noeviction)", policy)
    # ERROR + metric; startup continues so a misconfiguration is loud, not fatal
```

### 9.3 Persistence — what it is and is not for

AOF `everysec` is enabled so a Redis **restart is continuous for in-flight
jobs**, not because durability is required. Per RA-0, total Redis data loss
costs in-flight streams only.

| Property | Setting | Consequence |
|---|---|---|
| Loss window | `appendfsync everysec` | ≤1 s of events on an unclean stop |
| Rewrite | 100 % growth, min 64 MB | With a ~5 MB working set (§9.6), rewrites are effectively never triggered |
| RDB | `save 900 1` | Coarse secondary snapshot; not relied upon |
| Backup | **none** | Redis is explicitly **excluded** from the backup policy; [`08`](08_MongoDB_Data_Architecture.md) §12.2 backs up Mongo |

### 9.4 Restart behavior

```
                         ┌──────────────────────────────────────────────┐
                         │  Which process restarted?                    │
                         └───────┬──────────────────────┬───────────────┘
                                 │                      │
              ┌──────────────────▼─────────┐  ┌─────────▼──────────────────┐
              │  BACKEND restarts           │  │  REDIS restarts            │
              │  (Redis alive)              │  │  (backend alive)           │
              └──────────────┬──────────────┘  └─────────┬──────────────────┘
                             │                            │
     job tasks die with the process        ┌──────────────┴──────────────┐
     streams + hashes survive in Redis      │  AOF intact?               │
                             │              └───┬─────────────────┬──────┘
                             ▼                 YES               NO / flushed
              startup sweep (§6.3):             │                 │
              running/queued ∉ active-ZSET      │                 │
                    → mark failed               ▼                 ▼
                    → terminal event      ≤1 s of events    ALL job state gone
                    → UI shows retry       lost; cursors     ├─ live tasks still
                                           resume; ZSET      │  running, publishing
                                           may hold stale    │  into a void
                                           entries →         ├─ SSE readers error →
                                           self-heal by      │  UI failed + retry
                                           score             └─ on reconnect the
                                                                backend re-registers
                                                                its live jobs:
                                                                ZADD (idempotent)
                                                                + HSET status
```

**Reconnect re-registration** is the one piece of recovery logic Redis does not
give for free: on a successful reconnect the backend walks its **local** task
registry and idempotently re-`ZADD`s each live job into `as:v1:jobs:active` and
re-`HSET`s its status. Without it, a Redis wipe resets the concurrency cap to
zero while N jobs are still running, allowing over-admission.

| Scenario | Reports/explanations | In-flight jobs | Concurrency cap | User impact |
|---|---|---|---|---|
| Backend restart | ✅ safe (Mongo) | marked `failed` by the sweep | recomputed from the ZSET | retry offered |
| Redis restart, AOF intact | ✅ safe | continue; streams resume | ≤1 s of drift, self-heals | brief SSE reconnect |
| Redis restart, data lost | ✅ safe | continue; re-registered on reconnect | rebuilt from local registries | SSE error → retry |
| Both restart | ✅ safe | swept to `failed` | empty, correct | retry offered |
| Redis OOM (§9.2) | ✅ safe | existing streams keep reading; new `XADD` fails | intake 503s | fail-closed, alerted |

**Docker:** `restart: unless-stopped`, `healthcheck: redis-cli --user alphascribe
--pass $REDIS_PASSWORD ping`
(10 s interval, 3 retries). The backend does **not** hard-depend on Redis at
startup — it starts, logs the connection failure, and serves the §8 degraded
matrix until Redis returns.

### 9.5 Connection management

| Setting | Value | Rationale |
|---|---|---|
| `max_connections` | **100** | §4.5: concurrent SSE readers + 20 headroom |
| `socket_timeout` | 20 s | > the 15 s `XREAD block`, so a normal block never trips it |
| `socket_connect_timeout` | 3 s | fail fast into the §8 degradation path |
| `health_check_interval` | 30 s | reaps half-open connections behind a NAT/proxy |
| `retry_on_timeout` | `True` | for non-blocking ops only |
| Client name | `alphascribe:{instance_id}` | makes `CLIENT LIST` diagnosable |
| **Separate pool for Pub/Sub** | yes | a subscriber connection is long-lived and must never contend with the command pool |

### 9.6 Memory budget

| Family | Per unit | At 1,000 jobs/day | Steady state |
|---|---|---|---|
| Event streams | ~20 events × ~300 B ≈ 6 KB/job | 6 MB/day | ~1 MB (1 h TTL) |
| Job hashes | ~400 B | 400 KB/day | ~400 KB (24 h TTL) |
| Active ZSET | ~60 B × ≤8 | — | negligible |
| Rate-limit ZSETs | ~100 B × active users | — | < 1 MB (15 min TTL) |
| SEC index cache | ~1.5 MB | — | 1.5 MB |
| **Total** | | | **≈ 5 MB steady · 256 MB cap ≈ 50× headroom** |

The cap exists to make runaway growth fail loudly (§9.2), not because the
workload approaches it.

### 9.7 High availability — explicitly out of scope

**v1 runs a single Redis instance.** No Sentinel, no Cluster, no replica.

Justification: RA-0 means a Redis outage degrades to §8's matrix — reports and
accounts keep working, new jobs are refused — and the deployment is
single-region with no HA story for Mongo either. Adding Sentinel would introduce
failover-correctness concerns (split-brain, stale primary) to protect a
component whose loss is already designed to be survivable.

**Trigger to revisit:** a multi-region deployment, or an availability target that
makes "new analyses refused during a Redis restart" unacceptable. At that point
the answer is a managed Redis with automatic failover, not self-managed
Sentinel.

---

## 10. Migration Strategy

### 10.1 Port-first sequencing

Redis lands **after** the ports exist, never as a direct swap of `server.py`
internals:

```
Ph 4 : application/jobs.py + IN-PROCESS EventBus/JobStore adapters
          └─ 01 D-1 fixed here, in Python, with tests   ← Learning may start
Ph 7 : REDIS adapters implementing the same ports
          └─ swap in container.py; the Ph-4 tests must pass unchanged
```

The Phase-4 in-process adapters are not throwaway: they remain the **test double
and the documented fallback** (RA-2), and they are what makes the Phase-7 swap
verifiable — one behavioral suite runs against both implementations.

### 10.2 Cutover

| Step | Action | Rollback |
|---|---|---|
| 1 | Add `redis` service to compose + CI; health-gate | remove service |
| 2 | Ship Redis adapters **disabled**, behind `JOB_BACKEND=memory\|redis` (default `memory`) | — |
| 3 | Flip to `redis` in dev; run the §11 conformance suite against both | flip back |
| 4 | Flip in production; soak one release | flip back — Mongo still holds every durable record |
| 5 | After soak: drop the Mongo `events` `$push` (`08` DA-3) and run `08 m0004` | **point of no return** |

Steps 1–4 are fully reversible because Mongo remains the system of record. Step
5 is the one irreversible action, gated on a verified backup plus a full release
of soak.

### 10.3 Keyspace versioning

An incompatible key-shape change bumps `as:v1:` → `as:v2:`. Both coexist; v1
keys expire by their own TTLs (RA-1 guarantees every key has one). **There are
no Redis data migrations** — that is the entire benefit of the TTL invariant.

---

## 11. Testing Strategy

| Layer | What |
|---|---|
| **Port conformance** | One behavioral suite run against **both** `EventBus` adapters (in-process, Redis), parametrized |
| **Fan-out (`01 D-1` regression)** | Two concurrent subscribers each receive **all N** events, in order — the test that must never be deleted |
| **Replay** | Subscribe after k events → receive all k then live ones, **no duplicates** |
| **Consumer-group ban** | Static assertion that `xreadgroup`/`xgroup_create` appear **nowhere** in `infrastructure/redis/` (§4.1) |
| **Cancellation** | Publish cancel → owning instance cancels → terminal `warn` on the stream |
| **Active-set self-healing** | Stale entries > `MAX_JOB_LIFETIME` pruned; cap recovers after a simulated crash |
| **Deadline/reaper invariant** | Startup assertion `MAX_JOB_LIFETIME > max(JOB_DEADLINE) + GRACE` fails on a bad config (§6.2, `07` LR-9) |
| **Rate-limit window** | 5 allowed, 6th denied; **sliding-boundary burst rejected** (the fixed-window regression) |
| **Degradation** | Redis unreachable → job creation 503; report fetch 200; login allowed + metric (§8) |
| **Restart recovery** | Redis flushed mid-job → reconnect re-registers live jobs; cap is correct (§9.4) |
| **Pool exhaustion** | N+1 concurrent SSE connections against a pool of N → bounded failure, not deadlock (§4.5) |
| **`noeviction` assertion** | Startup logs ERROR + metric when the policy is wrong (§9.2) |

CI runs these against `redis:7-alpine` as a GitHub Actions **service container**
— hermetic, no network egress, no API key. They belong to the fast CI job.

---

## 12. Observability

| Metric | Type | Labels | Signal |
|---|---|---|---|
| `alphascribe_redis_operation_duration_seconds` | Histogram | `op` | latency of `XADD`/`XREAD`/ZSET ops |
| `alphascribe_redis_errors_total` | Counter | `op`, `kind` | connectivity, **`oom`** (§9.2) |
| `alphascribe_redis_pool_exhausted_total` | Counter | — | §4.5 early warning |
| `alphascribe_redis_reconnects_total` | Counter | — | §9.4 restart detection |
| `alphascribe_stream_subscribers` | Gauge | — | live SSE connections |
| `alphascribe_jobs_active` | Gauge | `kind` | ZCARD vs `MAX_ACTIVE_JOBS` |
| `alphascribe_jobs_rejected_total` | Counter | `reason` (`cap`, `rate`, `redis_down`) | 429/503 attribution |
| `alphascribe_ratelimit_hits_total` | Counter | `scope`, `outcome` | brute-force visibility |
| `alphascribe_ratelimit_degraded` | Gauge | — | **§8.1 fail-open alarm — must page** |
| `alphascribe_stream_events_total` | Counter | `kind` | throughput |

OpenTelemetry: Redis calls are spans nested under the pipeline/node spans of
[`07`](07_LangGraph_Architecture.md) §7.1, so a slow `XADD` appears in the same
trace as the node that emitted it.

**Alerting minimum (both page):** `alphascribe_ratelimit_degraded > 0` (a
security control is disabled) and `alphascribe_redis_errors_total{kind="oom"} >
0` (the `noeviction` tripwire). Neither is a metric anyone will think to check
unprompted.

---

## 13. Risks

| ID | Risk | Sev | Likelihood | Mitigation |
|---|---|---|---|---|
| **RR-1** | **`XREADGROUP` used instead of `XREAD`**, silently recreating `01 D-1` behind a more authoritative-looking API | **High** | Medium | §4.1 binding rule; §11 static ban test; fan-out regression test |
| **RR-2** | **Redis becomes a hard single point of failure** — an outage stops report generation entirely, where today no such dependency exists | **High** | Medium | §8 per-concern policy; in-process adapters retained (RA-2); §10.2 flag rollback; degradation drill on the Phase-7 gate |
| **RR-3** | **`maxmemory-policy` defaults to an eviction policy** in managed Redis, silently truncating live streams | **High** | Medium | §9.2 startup assertion + OOM alert |
| **RR-4** | **Connection-pool exhaustion** from blocking `XREAD` starves non-streaming calls | Medium | Medium | §4.5 sizing rule; §9.5 separate Pub/Sub pool; 15 s block; counter + test |
| **RR-5** | **Fail-open rate limiting** leaves a brute-force window during a Redis outage | Medium | Low | §8.1 — deliberate, scrypt-bounded, alerted, listed for sign-off |
| **RR-6** | **`INCR`-style concurrency counting reintroduced**, leaking slots on crash until the system 429s permanently | Medium | Medium | §6.2 ZSET design; self-healing test with a simulated crash |
| **RR-7** | **Split-brain between Redis and Mongo status** — `completed` in one, `running` in the other | Medium | Medium | Mongo wins for terminal states (RA-0); Mongo-first read precedence (`08` RI-1); restart sweep reconciles (§6.3) |
| **RR-8** | **Sliding→fixed window regression** during the rate-limiter port silently halves brute-force protection | Medium | Medium | §7.1 faithful port + the boundary-burst test |
| **RR-9** | **PII in Redis** — emails as key components, visible to `--scan` and persisted in AOF | Low | Medium | RA-4 / §7.2 hashing |
| **RR-10** | **Dev/CI/prod drift** — `scripts/run.py` (portable Mongo, no Redis) vs Docker compose | Medium | Medium | `run.py` defaults to `JOB_BACKEND=memory`; Redis in Docker/CI/prod |
| **RR-11** | **Reconnect re-registration omitted** (§9.4), letting a Redis wipe reset the concurrency cap while jobs still run | Medium | Medium | Explicit restart-recovery test in §11 |

---

## 14. Deferred — Considered and Not Adopted

Recorded so a future reader knows these were decided, not overlooked.

| Item | Why not in v1 | Trigger to revisit |
|---|---|---|
| **Session cache in Redis** | Would remove one of the two Mongo round-trips per authenticated request (`08` A-1). But once `08` I-2 exists, that lookup is an indexed point read — and caching sessions adds a revocation-correctness problem (a cached session must not outlive `delete_all_sessions`, the primary containment lever in [`10`](10_Backend_Security_Architecture.md) §12). | p95 auth latency becomes material **after** I-2 lands |
| **Redis Sentinel / Cluster** | §9.7 | Multi-region, or an availability target that forbids refusing new jobs during a restart |
| **Distributed locks for pipeline work** | No work is currently duplicated across instances; jobs are owned by the instance that created them | Work-stealing or a job queue consumed by many instances |
| **Redis as a task queue (e.g. RQ/Celery broker)** | Jobs are in-process `asyncio.Task`s owned by the accepting instance. A broker would let any instance run any job — a bigger change than this milestone, and it needs the deadline/cancellation model to be broker-aware. | Horizontal scaling where an instance must run jobs it did not accept |
| **Caching retrieval results** | Retrieval is deterministic per `(ticker, query)`, so it is cacheable — but the report-level cache (`server.py:885-907`) already short-circuits the whole pipeline for the same key, making a retrieval cache redundant | Retrieval reused across differing queries (e.g. Learning + research on one ticker) becomes measurable |
| **Keyspace notifications** | Nothing subscribes to expiry events; TTL semantics are sufficient | A feature needs to react to a key expiring |

---

## 15. Implementation Order

| Step | Work | Phase | Gate |
|---|---|---|---|
| 1 | `EventBus`/`JobStore`/`RateLimiter` ports + **in-process** adapters; `01 D-1` fixed | Ph 4 | Fan-out + replay tests green |
| 2 | Learning built on the ports | Ph L | Contract tests green |
| 3 | `redis` service in compose + GH Actions service container | Ph 7 | CI runs against `redis:7-alpine` |
| 4 | Redis `EventBus` (Streams, `XREAD` — §4) | Ph 7 | Same conformance suite passes unchanged |
| 5 | Redis `JobStore` (hash + ZSET — §6) incl. restart sweep and reconnect re-registration (§9.4) | Ph 7 | Crash- and wipe-recovery tests green |
| 6 | Redis `RateLimiter` (§7); `auth._hits` deleted; per-user job quota | Ph 7 | Sliding-window boundary test green |
| 7 | Cancel Pub/Sub (§5), separate subscriber pool (§9.5) | Ph 7 | Two-instance cancel drill |
| 8 | Config hardening (§9.1), `noeviction` + deadline-invariant assertions, metrics + alerts (§12) | Ph 7 | Alerts fire in a drill |
| 9 | Degradation drill; flip `JOB_BACKEND=redis` | Ph 7 | §8 matrix verified behavior-by-behavior |
| 10 | Drop Mongo `$push`; run `08 m0004` | Ph 7 + 1 release | Backup verified |

**Ordering constraint:** steps 4–6 must not precede step 1. Writing Redis
adapters before the ports exist means writing them against `server.py`
internals, which is the swap this plan exists to avoid.

---

## 16. Ratification

| # | Item | Position |
|---|---|---|
| 1 | **§8.1 — fail-OPEN rate limiting when Redis is down.** Fail-closed converts a cache outage into a total auth outage. | **Recommended: fail open + paging alert.** Explicit sign-off required either way |
| 2 | **§4.1 — `XREAD`, never `XREADGROUP`** | Binding (RR-1) |
| 3 | **§9.2 — `maxmemory-policy noeviction`** as a deployment requirement, asserted at startup | Binding (RR-3) |
| 4 | **RA-0 / RA-1** — Redis is never the system of record; every key is TTL'd or capped | Binding |
| 5 | **§9.7 — no HA (single instance) in v1** | Proposed, with a stated trigger |
| 6 | **§7.3 — new per-user job quota (10/hour).** A user-visible 429 that does not exist today. | Proposed; product call on the number |
| 7 | **§6.2 — `MAX_JOB_LIFETIME = 600 s`**, satisfying `> max(JOB_DEADLINE) + GRACE` (amends v0.9's 900 s; resolves the conflict found in [`07`](07_LangGraph_Architecture.md) §5.3) | Required for consistency |
| 8 | **RR-10 — `scripts/run.py` defaults to `JOB_BACKEND=memory`** for the no-Docker developer path | Proposed |
| 9 | **§10.2 step 5** — the one irreversible step, gated on a one-release soak + verified backup | Proposed |

**On ratification:** change the status header to 🔒 **FROZEN**, record date and
approver, and treat subsequent changes as numbered amendments.

---

## 17. Cross-Reference Index

| Referenced here | Target |
|---|---|
| `01 D-1`, `01 D-6`, EQ-1 §7 | [`01_Backend_Architecture_Review.md`](01_Backend_Architecture_Review.md) |
| `02 F-1` | [`02_API_Coverage_Audit.md`](02_API_Coverage_Audit.md) §5 |
| `06 AD-5`, `06 AD-8`; Ph 4/7/L | [`06_Clean_Architecture_Migration_Plan.md`](06_Clean_Architecture_Migration_Plan.md) |
| `07` §5.3, §5.4, §6.2, §7.1, LR-9 | [`07_LangGraph_Architecture.md`](07_LangGraph_Architecture.md) |
| `08` DA-0, DA-3, RI-1, I-19/I-24, `m0004`, §12.2 | [`08_MongoDB_Data_Architecture.md`](08_MongoDB_Data_Architecture.md) |
| `10` §3.1, §12, SD-5 | [`10_Backend_Security_Architecture.md`](10_Backend_Security_Architecture.md) |

---

*Companion documents:* [`06`](06_Clean_Architecture_Migration_Plan.md) ·
[`07`](07_LangGraph_Architecture.md) · [`08`](08_MongoDB_Data_Architecture.md) ·
[`10`](10_Backend_Security_Architecture.md) · index:
[`00_README.md`](00_README.md)
