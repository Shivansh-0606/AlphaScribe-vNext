# MongoDB Data Architecture

**Status:** 🔒 **FROZEN** — `v1.0`, ratified 2026-08-03 · amendments only (§15)
**Milestone:** Backend Engineering M1 (post-audit) · **Date:** 2026-08-03
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main` · commit `7404b67`
**Depends on:** [`06_Clean_Architecture_Migration_Plan.md`](06_Clean_Architecture_Migration_Plan.md) (AD-3, Ph 3),
[`09_Redis_Architecture.md`](09_Redis_Architecture.md) (ownership split)
**Referenced by:** [`06`](06_Clean_Architecture_Migration_Plan.md) §5.1 · [`07`](07_LangGraph_Architecture.md) §5.2 · [`09`](09_Redis_Architecture.md) §9.3

### Document control

| Version | Date | Change |
|---|---|---|
| **v1.0** | **2026-08-03** | **FROZEN.** Final consistency pass: cross-references, ID uniqueness, inter-document contradictions, ratification/register sync, diagram fidelity, and API-contract invariance all verified. |
| v1.0-rc1 | 2026-08-03 | Added §3 entity-relationship diagrams; added §6 write-path diagram; `maxTimeMS` policy; fixed cross-references; freeze-ready |
| v0.9 | 2026-08-03 | Initial proposal |

> **ID prefixing.** IDs defined here use `I-`, `A-`, `DA-`, `DR-`, `m####`.
> References to IDs owned by another document carry that document's number —
> e.g. `06 C-5`, `01 D-9`.

---

## 0. Scope

Governs collections, document schemas, relationships, indexes, access patterns,
tenancy, lifecycle, migrations, and deployment topology. Does **not** govern
Redis-resident state ([`09`](09_Redis_Architecture.md)) or API shapes (frozen —
`06` C-1).

**Driver:** `motor` 3.3.1 over `pymongo` 4.6.3. **Server:** MongoDB 7.0.

---

## 1. Headline Finding

> **The database has five indexes. All five are on auth collections. Every other
> query in the system is a collection scan.**

`agents/auth.py:111-116` (`ensure_indexes`) is the only place any index is
created. Measured against actual call sites:

| Query | Frequency | Index today | Effect |
|---|---|---|---|
| `users.find_one({"id": session["user_id"]})` (`auth.py:227`) | **every authenticated request** — `current_user` runs on all 29 gated routes | ❌ none (`email` is indexed, `id` is not) | Full `users` COLLSCAN **per API call** |
| `filing_chunks.find({"ticker"}).sort("created_at",-1)` (`retrieval.py:160`) | every report and every explanation | ❌ none | Full COLLSCAN of the largest collection + in-memory sort |
| `reports.find_one({"id"})` (`server.py:1021`) | every report fetch | ❌ none | Full `reports` COLLSCAN |
| `jobs.update_one({"id"}, …)` | **once per pipeline event** (~10–20/run) | ❌ none | COLLSCAN per event |
| `sessions.delete_many({"user_id"})` (`auth.py:172`) | logout-all, password change, account delete | ❌ none | COLLSCAN |

Invisible at demo volume; dominant long before any other bottleneck. **§5 is the
highest-value section of this document**, and its index set (`m0001`) should
land in Migration Phase 3 regardless of what else slips.

---

## 2. Ownership Model

```
┌─────────────────────────────── MongoDB ────────────────────────────────┐
│  SYSTEM OF RECORD — durable, queryable, user-visible                   │
│    Identity     users · sessions · password_resets                     │
│    Corpus       companies · filings · filing_chunks                    │
│    Output       reports · explanations                                 │
│    Job history  jobs · explanation_jobs      (terminal state + summary) │
│    Meta         _migrations                                            │
└────────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────── Redis ─────────────────────────────────┐
│  HOT / EPHEMERAL — reconstructible, TTL'd, never source of truth       │
│    live job status · event streams (SSE replay) · cancel pub/sub ·     │
│    rate-limit counters · active-job ZSET · SEC company-index cache     │
└────────────────────────────────────────────────────────────────────────┘
```

**Invariant DA-0: Redis holds nothing whose loss changes a user-visible outcome
after a job terminates.** Losing Redis loses in-flight streams; it never loses a
report, an explanation, a session, or an account.

### 2.1 Architectural payoff

Today `push()` issues **one Mongo `$push` per pipeline event**
(`server.py:702-705`) purely so a reconnecting client can replay. Once Redis
Streams own replay ([`09`](09_Redis_Architecture.md) §4), that write disappears:
a job becomes **two Mongo writes total** (create + terminal update) instead of
~15–25, and the unbounded `events[]` array (§4.6) goes away rather than being
capped.

---

## 3. Entity Relationships

**No foreign keys exist.** MongoDB enforces no referential integrity, so every
relationship below is an application-level join on an indexed field. The diagram
is therefore a map of *invariants the application must maintain*, not of
constraints the database will enforce.

### 3.1 Full relationship map

```
                              ┌───────────┐
                              │   users   │
                              │  id (PK)  │
                              │  email ⊙  │
                              └─────┬─────┘
              ┌─────────────────────┼──────────────────────┬────────────────┐
              │ 1:N  user_id        │ 1:N  user_id         │ 1:N  user_id   │
              ▼                     ▼                      ▼                ▼
      ┌───────────────┐    ┌────────────────┐    ┌──────────────┐  ┌───────────────┐
      │   sessions    │    │    reports     │    │ explanations │  │ password_     │
      │  token_hash ⊙ │    │  id (PK)       │    │  id (PK)     │  │ resets        │
      │  user_id      │    │  user_id ∅     │    │  user_id     │  │  email ⚠      │
      │  expires_at ⏱ │    │  ticker        │    │  ticker      │  │  expires_at ⏱ │
      └───────────────┘    │  is_sample ∅   │    │  concept     │  └───────────────┘
                           └───┬────────┬───┘    └──────┬───────┘
                               │        │               │
             ┌─────────────────┘        │ self-ref      │ N:1
             │ 1:1  id ≡ id             │ context_      │ context_report_id
             ▼                          │ report_id     │
      ┌──────────────┐                  └───────────────┴──────► (reports)
      │     jobs     │
      │  id (PK)     │        ┌──────────────────┐  1:1  id ≡ id   ┌──────────────────┐
      │  status      │        │ explanation_jobs │◄────────────────│  explanations    │
      │  created_at ⏱│        │  id (PK)         │                 └──────────────────┘
      └──────────────┘        └──────────────────┘

    ─── corpus (shared across all tenants, no user_id) ─────────────────────────

      ┌──────────────┐  N:1 ticker   ┌──────────────┐  1:N doc_id  ┌────────────────┐
      │  companies   │◄──────────────│   filings    │─────────────►│ filing_chunks  │
      │  ticker ⊙    │               │  doc_id (PK) │              │  doc_id        │
      │  name        │◄──────────────│  ticker      │              │  ticker        │
      └──────────────┘  N:1 ticker   │  num_chunks  │              │  chunk_idx     │
                                     └──────────────┘              │  text          │
                                                                   │  embedding[384]│
                                                                   └────────┬───────┘
                                                                            ┆
                          reports.source_documents[]  ┄┄ SNAPSHOT COPY ┄┄┄┄┄┘
                          explanations.source_documents[]      (not a reference)

  ⊙ unique   ⏱ TTL   ∅ nullable   ⚠ joins on email, not user_id   ┄ denormalized copy
```

### 3.2 Invariants the application must maintain

| # | Invariant | Why it matters |
|---|---|---|
| **RI-1** | **`jobs.id ≡ reports.id`** — the job id *is* the report id (`server.py:919, 730`), and likewise `explanation_jobs.id ≡ explanations.id`. | Non-obvious and load-bearing: `GET /reports/{id}` accepts one id and checks `reports` first, then falls back to the job row (`server.py:1019-1031`). Breaking this breaks the status endpoint. |
| **RI-2** | **`source_documents` is an embedded snapshot, not a reference.** Retrieved chunks are copied into the report/explanation at persist time (embeddings stripped, `retrieval.py:195`). | Makes output documents **immutable historical records**: re-ingesting or deleting chunks never invalidates or silently mutates an existing report's citations. `[n]` markers stay valid forever. This is a deliberate and good property — do not "normalize" it. |
| **RI-3** | **`reports.user_id` is nullable**; `is_sample: true` marks curated public rows with `user_id: null`. | The `$or` in `list_reports` and the ownership predicate both depend on it. Legacy unclaimed rows are claimed on cache hit (`server.py:903-906`). |
| **RI-4** | **`password_resets` joins on `email`, not `user_id`** ⚠️ | An inconsistency with every other user-owned collection. Harmless (the flow verifies the user exists before creating the row) but means an email change would orphan outstanding reset rows. Documented, not changed — it is inside the C-3 stdlib auth surface. |
| **RI-5** | **The corpus has no `user_id`.** `companies`, `filings`, `filing_chunks` are shared by every tenant, by design (`server.py:317-318`). | The basis of the corpus-poisoning risk ([`10`](10_Backend_Security_Architecture.md) §6.4, SQ-1) and of cross-user report reuse. |
| **RI-6** | **`context_report_id` may reference a deleted report.** Follow-up reports and explanations store the id, not a copy. | Dangling references are tolerated: the prior brief is read once at job start; a missing row degrades to no context, never an error. |

### 3.3 Cardinality & growth

| Relationship | Cardinality | Growth driver |
|---|---|---|
| `users → sessions` | 1 : 0–N | ~2/user, TTL-bounded |
| `users → reports` | 1 : 0–N | user activity |
| `users → explanations` | 1 : 0–N | user activity |
| `reports → jobs` | 1 : 1 (RI-1) | — |
| `companies → filings` | 1 : 0–N | ingests per ticker |
| `filings → filing_chunks` | 1 : ~100–2,000 | **document length — the dominant growth axis** |
| `reports → source_documents[]` | 1 : 6–8 embedded | fixed by `top_k` |

`filing_chunks` is the only collection whose growth is superlinear in user
activity, and the only one where document size matters (§4.4).

---

## 4. Document Schemas

Field names are transcribed from the code and are **frozen where they appear in
an API response** (`06` C-1). New fields are additive and marked ✅.

### 4.1 `users`

```jsonc
{ "id": "uuid4-str",            // application id — NOT _id
  "email": "lowercased, unique",
  "password_salt": "hex-32",    // scrypt salt (06 C-3)
  "password_hash": "hex-64",    // scrypt N=2^14 r=8 p=1 dklen=32
  "created_at": "ISO-8601 str", "verified": false, "credits": 0 }
```

> **`_id` vs `id`.** Every collection carries an application-level `id` (uuid4
> string) *and* Mongo's auto `_id` ObjectId, and every query uses `id`. This is
> the established convention and is **not changed** (DA-1) — but it means `id`
> must be explicitly indexed everywhere (§5), because `_id`'s free unique index
> is never used for lookup.

### 4.2 `sessions` · `password_resets`

```jsonc
// sessions
{ "token_hash": "sha256 hex, unique",   // raw token never stored
  "user_id": "users.id", "created_at": "ISO-8601 str", "expires_at": BSON Date }

// password_resets  (RI-4: keyed by email)
{ "email": "...", "otp_hash": "hmac-sha256 hex",   // peppered — auth.py:102-108
  "created_at": "ISO-8601 str", "expires_at": BSON Date, "used": false }
```

### 4.3 `companies` · `filings`

```jsonc
{ "ticker": "AAPL", "name": "Apple Inc.", "updated_at": "ISO-8601 str" }

{ "doc_id": "uuid4", "ticker": "AAPL", "company_name": "Apple Inc.",
  "source": "10-Q 0000320193-24-000081 filed 2024-08-02",
  "num_chunks": 142, "char_count": 187432, "created_at": "ISO-8601 str" }
```

### 4.4 `filing_chunks` — the collection that matters

```jsonc
{ "doc_id": "uuid4", "ticker": "AAPL", "source": "...", "chunk_idx": 17,
  "text": "≤ ~1020 chars", "created_at": "ISO-8601 str",
  "embedding": [384 × double] }     // bge-small-en-v1.5, optional
```

| Component | Bytes | Note |
|---|---|---|
| `text` | ~900–1,020 | `chunk_size=900` + `overlap=120` |
| `embedding` | **~3,900** | 384 × (8-byte double + ~2 B BSON array-index overhead) |
| other fields | ~250 | |
| **total/chunk** | **≈ 5.2 KB** | **~75 % is the vector** |

`retrieve()` fetches up to 2,000 chunks **with embeddings** and re-scores in
Python per query → **up to ~10 MB over the wire per retrieval**. Correct and
fast enough at current volume; the ceiling and its triggers are DR-3 (§13).

### 4.5 `reports`

```jsonc
{ "id": "uuid4 ≡ job_id (RI-1)", "user_id": "users.id | null", "is_sample": bool?,
  "ticker": "AAPL", "query": "...", "company_name": "... | null",
  "created_at": "ISO-8601 str",
  "completed_at": "ISO-8601 str",   // ✅ 01 D-8
  "duration_ms": 38412,             // ✅ 01 D-8 — unlocks the median-report-time gate
  "draft_report": "markdown with [n]",
  "extracted_data": {...}, "sentiment_analysis": {...},
  "source_documents": [SourceDocument],   // snapshot, embeddings stripped (RI-2)
  "fact_check_status": bool, "validation_errors": [str], "verified_claims": [{...}],
  "retry_count": int,
  "scorecard": { faithfulness, context_precision, answer_relevance, overall,
                 cited_sources[], n_claims, n_supported },
  "events": [TraceEvent] }
```

Fields inside `reportDocSchema` are frozen. `completed_at`/`duration_ms` are
additive and projected out of responses (DA-10).

### 4.6 `jobs` · `explanation_jobs`

```jsonc
{ "id": "uuid4", "user_id": "users.id",      // ✅ user_id (absent today)
  "ticker": "AAPL",
  "query": "...",                            // `concept` in explanation_jobs
  "context_report_id": "uuid4 | null",
  "status": "queued|running|completed|failed|cancelled",
  "created_at": "...", "updated_at": "...",
  "completed_at": "...", "duration_ms": int, // ✅
  "error": "safe text | null",
  "report_id": "uuid4 | null",               // `explanation_id` in explanation_jobs
  "events": [TraceEvent] }                   // ⚠️ REMOVED once Redis owns replay (§2.1)
```

> **⚠️ Unbounded array (current).** `events` is `$push`ed per pipeline event
> with no `$slice` cap. At ~200 B × ~20 events it is nowhere near the 16 MB
> document ceiling — but it is unbounded *by construction*. `m0004` removes the
> array rather than capping it, which is the better fix.

### 4.7 `explanations` (new)

Mirrors the frozen `ExplanationDoc` ([`03`](03_Learning_Backend_Design.md) §1.3)
plus internal fields **stripped from the API response** (DA-10):

```jsonc
{ "id": "uuid4", "ticker": "...", "concept": "user's verbatim words",
  "explanation": "markdown with [n]", "source_documents": [SourceDocument],
  "company_name": "... | null", "created_at": "ISO-8601 str",
  // ── internal, never serialized ──
  "user_id": "users.id", "context_report_id": "uuid4 | null",
  "cited_sources": [1,3,4], "retrieval_meta": {...},
  "completed_at": "...", "duration_ms": int }
```

### 4.8 `_migrations` (new)

```jsonc
{ "_id": "0003_learning", "applied_at": BSON Date, "duration_ms": int }
```

---

## 5. Index Architecture

Every index is derived from an actual query. Nothing is speculative.

### 5.1 Index set

| # | Collection | Index | Type | Serves | Status |
|---|---|---|---|---|---|
| I-1 | `users` | `{email: 1}` | unique | login, forgot/reset | ✅ exists |
| **I-2** | `users` | `{id: 1}` | **unique** | `get_current_user` — **every authenticated request** | 🔴 **MISSING — highest impact** |
| I-3 | `sessions` | `{token_hash: 1}` | unique | session lookup, every request | ✅ exists |
| I-4 | `sessions` | `{expires_at: 1}` | TTL(0) | auto-expiry | ✅ exists |
| **I-5** | `sessions` | `{user_id: 1}` | — | `delete_other_sessions`, `delete_all_sessions` | 🔴 missing |
| I-6 | `password_resets` | `{email: 1}` | — | reset lookup | ✅ exists |
| I-7 | `password_resets` | `{expires_at: 1}` | TTL(0) | auto-expiry | ✅ exists |
| **I-8** | `password_resets` | `{email:1, used:1, created_at:-1}` | — | `verify_password_reset` exact query — supersedes I-6 | 🔴 missing |
| **I-9** | `companies` | `{ticker: 1}` | **unique** | lookup **and upsert race-safety** (`ingest.py:319-323`) | 🔴 missing |
| **I-10** | `filings` | `{ticker:1, created_at:-1}` | — | `list_filings`, `ensure_company` latest, `distinct("ticker")` | 🔴 missing |
| **I-11** | `filings` | `{ticker:1, source:1}` | — | sample-dedupe `find_one` (`server.py:366`) | 🔴 missing |
| **I-12** | `filing_chunks` | `{ticker:1, created_at:-1}` | — | **every retrieval** + pre-flight count | 🔴 **MISSING — 2nd highest** |
| I-13 | `filing_chunks` | `{doc_id: 1}` | — | re-ingest cleanup (`01 D-9` upgrade path) | ⚪ optional |
| **I-14** | `reports` | `{id: 1}` | **unique** | get, compare `$in`, delete, RI-1 join | 🔴 missing |
| **I-15** | `reports` | `{user_id:1, created_at:-1}` | — | `list_reports` `$or` branch 1, delete cascade | 🔴 missing |
| **I-16** | `reports` | `{is_sample:1, created_at:-1}` | sparse | `list_reports` `$or` branch 2 | 🔴 missing |
| **I-17** | `reports` | `{ticker:1, query:1, created_at:-1}` | — | the cache probe (`server.py:889-893`) | 🔴 missing |
| **I-18** | `jobs` | `{id: 1}` | **unique** | every status write | 🔴 missing |
| I-19 | `jobs` | `{status:1, created_at:-1}` | — | restart sweep (`01 D-6`), reaper | ✅ new |
| I-20 | `jobs` | `{created_at: 1}` | TTL(30 d) | retention (§9) | ✅ new |
| I-21 | `explanations` | `{id: 1}` | unique | fetch | ✅ new |
| I-22 | `explanations` | `{user_id:1, created_at:-1}` | — | scoped fetch, future history | ✅ new |
| I-23 | `explanation_jobs` | `{id: 1}` | unique | status | ✅ new |
| I-24 | `explanation_jobs` | `{status:1, created_at:-1}` | — | restart sweep | ✅ new |
| I-25 | `explanation_jobs` | `{created_at: 1}` | TTL(30 d) | retention | ✅ new |

**11 missing indexes on existing hot paths.** I-2 and I-12 alone account for the
two most frequent scans in the system.

### 5.2 `$or` and the reports list

`list_reports` queries `{"$or": [{"user_id": uid}, {"is_sample": true}]}` sorted
by `created_at`. MongoDB satisfies `$or` by **index union** — one index per
branch (I-15, I-16), merged and de-duplicated. Both carry `created_at: -1` so
the sort is index-provided rather than an in-memory `SORT` stage. I-16 is
**sparse**: `is_sample` is absent on most documents, so it holds only the
handful of curated samples.

### 5.3 Query timeouts

Per [`07`](07_LangGraph_Architecture.md) §5.5 (X-14), **every Mongo operation
carries a `maxTimeMS`**: 10 s on the retrieval query (the only one that can scan
a large collection), 5 s elsewhere. Enforced in the repository adapters, not at
call sites, so a new query cannot forget it.

### 5.4 Deliberately *not* indexed

| Query | Why |
|---|---|
| `reports.aggregate` group-by-ticker (trending) | An index cannot serve a full group-by. If it becomes hot the answer is a materialized counter or a cached result. Currently unconsumed by the frontend. |
| `reports.find({})` (rescore) | Deliberately full-collection; EQ-2 recommends admin-gating or deleting it. |
| `companies.find({})` | ~12k small docs, read whole by design. |
| `filings.count_documents({})` / `filing_chunks.count_documents({})` (health) | Replaced by `estimated_document_count()` — an O(1) metadata read ([`04`](04_Observability_Audit.md) O-12) — not by an index. |
| Text index on `filing_chunks.text` | BM25 is computed in-process by `rank_bm25`; a Mongo `$text` index would be a second, divergent ranking. Retrieval quality is owned by `agents/retrieval.py`. |

### 5.5 Where indexes are created

`ensure_indexes(db)` moves from `agents/auth.py` to
`infrastructure/mongo/indexes.py`, covers all collections, and runs from the
`lifespan` startup hook. `createIndex` is idempotent, so it is safe every boot.
MongoDB 7 builds in the background.

---

## 6. Write Paths

```
INGEST  (POST /ingest/*)                     3 writes, not atomic — §8.3
   chunk_text() ──► embed_texts() ──► filing_chunks.insert_many()  [N docs]
                                  └─► filings.insert_one()          [1 doc]
                                  └─► companies.update_one(upsert)  [I-9 required]

REPORT JOB
   admission ──► jobs.insert_one({status:"queued"})                 [write 1]
        │
        ▼   (pipeline runs; events → Redis Streams, NOT Mongo — §2.1)
   terminal ──► reports.insert_one(doc + scorecard)                 [write 2]
            └─► jobs.update_one({status:"completed", duration_ms})   [write 3]
                     ▲
                     └─ RI-1: same id. GET checks `reports` first, so a crash
                        between writes 2 and 3 is invisible to the user.

DELETE ACCOUNT   ordered so `users` is deleted LAST — §8.3
   reports.find({user_id}) → reports.delete_many({user_id})
        → jobs.delete_many({id:{$in}}) → sessions.delete_many({user_id})
        → users.delete_one({id})
   (corpus deliberately untouched — RI-5)
```

---

## 7. Access-Pattern Map

| # | Operation | Query | Index | Notes |
|---|---|---|---|---|
| A-1 | Authenticate | `sessions.find_one({token_hash})` → `users.find_one({id})` | I-3, **I-2** | 2 round-trips per request. A Redis session cache is the documented optimization ([`09`](09_Redis_Architecture.md) §14), not adopted in v1. |
| A-2 | Retrieve chunks | `filing_chunks.find({ticker}).sort(created_at,-1).limit(2000)` | **I-12** | The hot path; §4.4 sizing, §5.3 timeout. |
| A-3 | Pre-flight "has data" | `filing_chunks.count_documents({ticker})` | **I-12** | Index-covered count. |
| A-4 | Cache probe | `reports.find_one({ticker, query}).sort(created_at,-1)` | **I-17** | Compared against `filings` latest `created_at` (I-10). |
| A-5 | Fetch report | `reports.find_one({id})` | **I-14** | + ownership predicate after EQ-3. |
| A-6 | List reports | `reports.find({$or:[…]}).sort(created_at,-1).limit(n)` | I-15 ∪ I-16 | §5.2. |
| A-7 | Compare | `reports.find({id: {$in: [2..4]}})` | **I-14** | |
| A-8 | Job status write | `jobs.update_one({id}, {$set})` | **I-18** | ~15–25 writes/job → 2 once Redis owns events. |
| A-9 | Ingest | see §6 | I-9 for upsert safety | not atomic — §8.3 |
| A-10 | Account delete cascade | see §6 | I-15, I-18, **I-5**, **I-2** | not atomic — §8.3 |

---

## 8. Consistency, Atomicity, Concurrency

### 8.1 Deployment topology

```
docker compose:
  mongo:  mongo:7.0  --replSet rs0  --auth  --bind_ip_all
          + one-shot init container: rs.initiate()   → single-node replica set
```

**Single-node replica set, not standalone** (DA-5). Cost: one init container.
Benefit: transactions, change streams, and causal consistency become
*available* without a later topology migration. v1 uses none of them.

### 8.2 Read/write concerns

| Setting | Value | Rationale |
|---|---|---|
| Write concern | `w:1, j:true` (RS default) | Single node; journaling protects against process crash |
| Read concern | `local` | Single node — no staleness window exists |
| Read preference | `primary` | Only one node |
| `maxTimeMS` | 10 s retrieval / 5 s other | §5.3 |

### 8.3 Non-atomic sequences (accepted, with compensations)

| Sequence | Failure window | Compensation |
|---|---|---|
| **Ingest** (A-9) | Chunks written, `filings` row missing | Retrieval reads `filing_chunks` directly, so the corpus stays usable; `filings` is metadata. |
| **Job completion** | Report saved, job still `running` | `GET /reports/{id}` checks `reports` **first** (RI-1), so the user sees the completed report regardless. The restart sweep reconciles the job row. |
| **Account delete** (A-10) | Partial cascade | Ordered so the **user document is deleted last**: any partial failure leaves the account intact and re-runnable, never a dangling session with no user. **This ordering is load-bearing and must be preserved.** |

**DA-4: prefer idempotent, order-hardened sequences over transactions.**
Transactions on a single-node RS add latency and a new failure mode
(`TransientTransactionError` retry loops) to close windows the read paths
already tolerate. Revisit only if a genuinely destructive interleaving is found.

### 8.4 Concurrency hazards

| Hazard | Status |
|---|---|
| **`companies` upsert race** — concurrent ingests of one ticker can both insert without a unique index | 🔴 Fixed by **I-9**. A correctness fix, not just performance. |
| Duplicate report for the same `(ticker, query)` under concurrent generate | Accepted — the cache probe is best-effort; worst case is a wasted run. |
| `jobs.update_one(upsert=True)` racing the initial `insert_one` | Safe: upsert on a unique indexed `id` (I-18) collapses to an update. |

---

## 9. Data Lifecycle & Retention

| Collection | Retention | Mechanism |
|---|---|---|
| `sessions` | until `expires_at` (24 h / 30 d) | TTL I-4 ✅ |
| `password_resets` | 10 min | TTL I-7 ✅ |
| `jobs`, `explanation_jobs` | **30 days** | TTL I-20 / I-25 ✅ new |
| `reports`, `explanations` | until user delete or account deletion | cascade (§6) |
| `companies`, `filings`, `filing_chunks` | indefinite — **shared corpus, deliberately not user-scoped** (RI-5) | none |
| `_migrations` | indefinite | — |

**Why `jobs` gets a TTL and `reports` does not:** a job row is an execution
record whose user-visible value is superseded by the report it produced. Thirty
days covers debugging and support without one row per run forever.

**Erasure boundary.** Account deletion removes `users`, `sessions`, `reports`,
`explanations`, and job rows. It deliberately does **not** remove ingested
filings/chunks — a shared corpus sourced from public filings, not personal data
(existing commented behavior, `server.py:317-318`). Restated here so the
boundary is explicit rather than incidental; ratification item §15 row 4.

---

## 10. Design Decisions

| ID | Decision | Rationale | Rejected |
|---|---|---|---|
| **DA-1** | Application `id` (uuid4 string) stays the lookup key; `_id` remains an unused ObjectId | Changing to `_id` touches every collection, every query, and the API surface (ids are returned to clients). Cost is one explicit unique index per collection. | Migrate `id` → `_id` |
| **DA-2** | Mongo is the system of record; Redis is cache/transport (DA-0) | Keeps durability trivial: back up Mongo, lose nothing that matters | Redis as job SoR |
| **DA-3** | Drop the per-event `jobs.$push` once Redis Streams own replay (§2.1) | ~15–25 writes/job → 2; removes the unbounded array instead of capping it | `$push` with `$slice:-100` |
| **DA-4** | Idempotent, order-hardened sequences over transactions (§8.3) | Read paths already tolerate every window | `start_transaction()` around ingest and completion |
| **DA-5** | Single-node replica set in all environments (§8.1) | Transactions/change streams available later at zero migration cost | Standalone `mongod` |
| **DA-6** | Embeddings stay inline as BSON double arrays | Retrieval needs vector + text together; a separate collection means a join per query. The 75 % overhead is a stated ceiling (DR-3), not a surprise. | Separate `chunk_vectors`; `BinData` float32 (halves size — revisit at DR-3's trigger) |
| **DA-7** | No Atlas Vector Search / `$vectorSearch` in v1 | Requires Atlas (this deploys self-hosted) and would replace the tuned hybrid fusion with a different ranker | Adopt Atlas now |
| **DA-8** | Indexes created from `infrastructure/mongo/indexes.py` at startup, idempotently, for all collections | Startup is the one place guaranteed to run in every environment including tests and CI | A manual DBA runbook — guarantees drift |
| **DA-9** | Forward-only, numbered, idempotent migrations with a `_migrations` ledger; **no down-migrations** | Down-migrations are written, never tested, never run. Forward-fix is the honest model. | Alembic-style up/down |
| **DA-10** | New internal fields are additive and projected out at the API boundary | The mechanism that lets persistence evolve under a frozen contract (`06` C-1); already the established pattern (`server.py:1050`) | Match the API shape in storage |

---

## 11. Migration Strategy

### 11.1 Mechanism

```
infrastructure/mongo/migrations/
  __init__.py            ordered registry of (id, coroutine)
  m0001_indexes.py       create the §5 index set               (idempotent)
  m0002_job_user_id.py   backfill jobs.user_id from reports    (idempotent)
  m0003_learning.py      create explanations / explanation_jobs + I-21…I-25
  m0004_job_events_drop.py  ⚠️ destructive — gated
  m0005_report_timing.py    additive fields on new docs only
```

Runner: `python -m app.cli migrate` **and** an automatic pass in `lifespan`.

```python
if await db._migrations.find_one({"_id": mid}): return    # already applied
await migration(db)                                        # must be idempotent anyway
await db._migrations.insert_one({"_id": mid, "applied_at": now, "duration_ms": …})
```

**Every migration must be safe to run twice**, ledger or not. The ledger is an
optimization and an audit trail, not the correctness mechanism.

### 11.2 Inventory

| ID | Change | Destructive | Backfill | Downtime |
|---|---|---|---|---|
| `m0001_indexes` | All 25 indexes (§5) | No | none | **none** (background builds) |
| `m0002_job_user_id` | `jobs.user_id` from the matching report | No | one pass over `jobs` | none |
| `m0003_learning` | New collections + I-21…I-25 | No | none | none |
| `m0004_job_events_drop` | `$unset` `events` from job collections | ⚠️ **Yes** | none | none |
| `m0005_report_timing` | `completed_at`/`duration_ms` on **new** documents only | No | **none — deliberately** (the data does not exist historically) | none |

**`m0004` is the only destructive migration.** Gate: Redis Streams must have
served SSE replay in production for one full release cycle, **and** a verified
Mongo backup must exist. Until then the `events` array stays as a redundant
safety net.

### 11.3 Rollback

- `m0001`, `m0003`: dropping the new indexes/collections restores the prior
  state exactly. The application tolerates missing indexes (it did for months).
- `m0002`, `m0005`: additive; older code ignores them.
- `m0004`: **not reversible** — hence the gate. Recovery is a restore.

### 11.4 Zero-downtime property

No migration renames a field, changes a type, or requires a code/schema lockstep
deploy. Old and new application versions can both run against a migrated
database — a direct consequence of DA-10.

---

## 12. Operations

### 12.1 Docker topology

```
┌── compose network: alphascribe ─────────────────────────────────┐
│  backend ──────► mongo:7.0 (replSet rs0, --auth) ──► vol mongo-data
│    │             healthcheck: mongosh --eval 'db.adminCommand("ping")'
│    └───────────► redis:7-alpine                  ──► vol redis-data
│  mongo-init (one-shot): rs.initiate()
│  prometheus ──scrape──► backend:8001/metrics
│  otel-collector ◄──OTLP── backend
└──────────────────────────────────────────────────────────────────┘
```

`scripts/run.py`'s portable-MongoDB bootstrap (`.mongo/`, ~250 MB) is
**retained** as the zero-Docker developer path. Docker is the CI and deployment
path. Both produce the same schema, guaranteed because indexes and migrations
run from application startup (DA-8), not from an image-build step.

### 12.2 Backup

| Item | Approach |
|---|---|
| What | `mongodump` of the whole database; `users`, `reports`, `explanations` are the irreplaceable parts |
| Cadence | Daily; **and immediately before `m0004`** |
| Reconstructible without backup | `companies`, `filings`, `filing_chunks` (re-ingestible from public sources); `jobs` (execution history only) |
| Restore drill | Phase-7 exit criterion, alongside the Redis-down drill |

### 12.3 Monitoring

| Metric | Purpose |
|---|---|
| `alphascribe_mongo_operation_duration_seconds{collection,op}` | slow-query detection — would have surfaced §1 immediately |
| `alphascribe_mongo_errors_total{collection,op,kind}` | connectivity, write failures, **`maxTimeMS` expiries** |
| `alphascribe_corpus_chunks` (gauge) | corpus growth → the DR-3 trigger |
| `alphascribe_collection_documents{collection}` (gauge, `estimated_document_count`) | cheap growth tracking; replaces the O-12 health counts |

OpenTelemetry `pymongo` auto-instrumentation provides per-query spans nested
under the node spans in [`07`](07_LangGraph_Architecture.md) §7.1.

---

## 13. Risks

| ID | Risk | Sev | Likelihood | Mitigation |
|---|---|---|---|---|
| **DR-1** | **Missing indexes (§1) degrade non-linearly.** A `users` COLLSCAN per request and a `filing_chunks` COLLSCAN per retrieval are invisible at demo scale and dominant at production scale. | **High** | **High** | `m0001` in Phase 3, ahead of every other data change; slow-query metric as the standing guard |
| **DR-2** | **`companies` upsert without a unique index creates duplicate ticker rows** under concurrent ingest — a correctness bug | Medium | Medium | I-9; a pre-flight dedupe pass inside `m0001` in case duplicates already exist |
| **DR-3** | **Retrieval memory/bandwidth ceiling.** 2,000 chunks × ~5.2 KB ≈ 10 MB/query, re-scored in Python, multiplied by `MAX_ACTIVE_JOBS`. | Medium | Medium | Bounded today by the 2,000 cap, the job cap, and (new) `maxTimeMS`. **Triggers:** p95 retrieval > 2 s, or `alphascribe_corpus_chunks` > ~500k. **Upgrade order:** (a) project out `embedding` when the embedder is unavailable, (b) `BinData` float32 (~2× smaller), (c) `$vectorSearch` on Atlas (DA-7). |
| **DR-4** | **`m0004` deletes job event history**, irreversibly | Medium | Low | One-release soak of Redis Streams + verified backup as a hard gate |
| **DR-5** | **Non-atomic account deletion** leaves orphans on mid-cascade failure | Medium | Low | Ordering makes it re-runnable (§8.3); user row last. A periodic orphan sweep is the follow-up if it ever fires. |
| **DR-6** | **Stale chunks accumulate on re-ingest** (`01 D-9`) — old and new chunks coexist and compete in retrieval | Low | Medium | Preserved deliberately (`06` C-5 — it is a `ponytail:` marker with a stated trigger). I-13 exists to make the `doc_id` cleanup cheap when that trigger fires. |
| **DR-7** | **Dev (portable Mongo) and prod (Docker RS) diverge** | Low | Low | DA-5 makes both replica sets; DA-4 means no code depends on transactions |
| **DR-8** | **Index build on a large populated collection degrades writes** | Low | Low | MongoDB 7 builds in background; `m0001` runs while the corpus is small — another reason to sequence it early |

---

## 14. Implementation Order

| Step | Work | Migration phase | Gate |
|---|---|---|---|
| 1 | `infrastructure/mongo/indexes.py` + `m0001_indexes` (all 25) | **Ph 3 — first** | `explain()` shows `IXSCAN` (not `COLLSCAN`) for A-1…A-8 |
| 2 | Repositories behind ports; `db.*` removed from `agents/` and route handlers; `maxTimeMS` (§5.3) | Ph 3 | `06 AD-5` dependency test green |
| 3 | `m0002_job_user_id`; `completed_at`/`duration_ms` (`m0005`) | Ph 4 | Median report time computable from Mongo |
| 4 | `m0003_learning` collections + indexes | Ph L | Learning contract tests green |
| 5 | Redis Streams own replay; stop `$push`ing to Mongo | Ph 7 | Writes/job = 2, verified by the op-duration metric |
| 6 | `m0004_job_events_drop` | **Ph 7 + one release** | Backup verified |
| 7 | Docker compose (RS + init + `--auth`), backup/restore drill, Mongo metrics | Ph 7 | Restore drill passes |

---

## 15. Ratification

| # | Item | Position |
|---|---|---|
| 1 | **DA-1** — keep application `id` as the lookup key rather than migrating to `_id` | Proposed; the alternative is a repo-wide breaking change |
| 2 | **DA-4** — no multi-document transactions | Proposed |
| 3 | **DA-5** — single-node replica set in all environments | Proposed |
| 4 | **§9 retention & erasure boundary** — 30-day TTL on job collections; corpus retained indefinitely and **excluded from account-deletion erasure** | Proposed; the erasure boundary deserves an explicit ruling |
| 5 | **`m0004`** — the one destructive migration, and its two-part gate | Proposed |
| 6 | **DA-7** — no Atlas Vector Search in v1; DR-3 states the trigger to revisit | Proposed |
| 7 | **RI-2** — `source_documents` stays an embedded snapshot (reports are immutable historical records) | Proposed as binding — a future "normalization" would silently break historical citations |

**On ratification:** change the status header to 🔒 **FROZEN**, record date and
approver, and treat subsequent changes as numbered amendments.

---

## 16. Cross-Reference Index

| Referenced here | Target |
|---|---|
| `01 D-6`, `01 D-8`, `01 D-9` | [`01_Backend_Architecture_Review.md`](01_Backend_Architecture_Review.md) §6 |
| `03` §1.3 | [`03_Learning_Backend_Design.md`](03_Learning_Backend_Design.md) |
| `04` O-12, §3.2 | [`04_Observability_Audit.md`](04_Observability_Audit.md) |
| `06` C-1, C-3, C-5; Ph 3/4/7/L; AD-3, AD-5 | [`06_Clean_Architecture_Migration_Plan.md`](06_Clean_Architecture_Migration_Plan.md) |
| `07` §5.5 (X-14), §7.1 | [`07_LangGraph_Architecture.md`](07_LangGraph_Architecture.md) |
| `09` §4, §6.2, §14 | [`09_Redis_Architecture.md`](09_Redis_Architecture.md) |
| `10` §6.4, SQ-1, EQ-2, EQ-3 | [`10_Backend_Security_Architecture.md`](10_Backend_Security_Architecture.md) |

---

*Companion documents:* [`06`](06_Clean_Architecture_Migration_Plan.md) ·
[`07`](07_LangGraph_Architecture.md) · [`09`](09_Redis_Architecture.md) ·
[`10`](10_Backend_Security_Architecture.md) · index:
[`00_README.md`](00_README.md)
