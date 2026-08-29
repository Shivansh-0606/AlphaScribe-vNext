# 59 — M13 Filing Content Read API Contract

**Status:** 🟢 **CTO-RATIFIED / FROZEN (2026-08-27).** This is a
contract-design artifact. The four decisions the CTO resolved on 2026-08-27
(OD-1 endpoint shape, OD-2 content representation, OD-6 unknown filing, OD-7
filing-without-chunks) are recorded as CTO-resolved in §16 and folded into
§3–§9 below. Ratification of this document **freezes the wire contract**; it
does **not** implement it, does **not** modify any route, schema, index, or
frontend file, and does **not** authorize implementation.
**M13 implementation is NOT AUTHORIZED — a separate, subsequent CTO
implementation-authorization decision is required before any source code may
be changed (§14, §16).**
**Type:** API / contract decision artifact (research/design/governance-only —
no code changed, no schema/migration/index file created, no endpoint wired,
no test added).
**Precedent (cited, unmodified):**
[33_M8_Financials_API_Contract_Review.md](33_M8_Financials_API_Contract_Review.md)
(the CTO-ratified `GET /companies/{ticker}/financials` contract — the
structural precedent for a thin read contract in this repository) and
[55_M12_Financial_Research_Data_Completion_Architecture_Decision_Pack.md](55_M12_Financial_Research_Data_Completion_Architecture_Decision_Pack.md)
(the thin-adapter architecture precedent). **Neither is modified by this
document.**
**Companion:**
[60_M13_Filing_Content_Reading_Architecture_Decision_Pack.md](60_M13_Filing_Content_Reading_Architecture_Decision_Pack.md)
(the architecture decision pack — repository/port, handler shape, frontend
integration, scope). Read both together.
**Roadmap position:**
[58_Post_M12_Backend_AI_Roadmap_Reconciliation.md](58_Post_M12_Backend_AI_Roadmap_Reconciliation.md)
§20–§21 recommends M13 as the next milestone direction. The CTO's
ratification of this document (§16) and Document 60 constitutes CTO
**selection of the M13 direction** from Document 58 §21; Document 58's own
§28 ratification block should be completed to reflect that selection, as a
governance-hygiene follow-up (Document 58 §14 GH-7 / §26 Decision D — not
performed here). **Selection and contract/architecture ratification are not
implementation authorization** — that remains a separate, subsequent CTO
decision (§14, §16).
**Date:** 2026-08-27.

---

## 0. What This Document Is and Is Not

**Is:** a precise, worked wire contract for one new read-only HTTP route
that returns the filing text AlphaScribe already persists at ingest time,
plus the metadata the UI needs to render it. Structured the same way
Document 33 §1–§10 structured the financials read contract.

**Is not:** an implementation, an implementation authorization, an
architecture decision (that is Document 60), a Filing Q&A / retrieval / RAG
design, a citation design, an ingestion change, or a schema/index change.
OD-1 / OD-2 / OD-6 / OD-7 are **CTO-resolved as of 2026-08-27** (§16) and
recorded as such in §13. The remaining register entries (OD-3, OD-4, OD-5,
OD-8, AG-1, AG-2, AG-3) stay `OPEN` or are explicitly **delegated to the
separate M13 implementation-authorization phase** — none is guessed here to
make the document look finished.

## 1. Existing Architecture Dependency (verified this session, direct reads)

| Component | File / location | Verified finding |
|---|---|---|
| Ingestion | `backend/agents/ingest.py::ingest_document` | Chunks the raw document (`chunk_text`, `chunk_size=900`, `overlap=120`), then `db.filing_chunks.insert_many(rows)` followed by `db.filings.insert_one({...})`. **No reconstructed full-document text is persisted** — only overlapping chunks + one metadata row. Raw text is truncated at 200,000 chars for EDGAR (`text[:200_000]`) and BSE annual reports before chunking. |
| `filings` collection | `08_MongoDB_Data_Architecture.md` §4.3; `ingest.py:312-320` | `{ "doc_id": "uuid4", "ticker": "AAPL", "company_name": "Apple Inc. | null", "source": "10-Q 0000320193-24-000081 filed 2024-08-02", "num_chunks": 142, "char_count": 187432, "created_at": "ISO-8601 str" }`. One row per ingested document. **`doc_id` is the primary key** (`08` §3 ERD: "`doc_id (PK)`"). |
| `filing_chunks` collection | `08_MongoDB_Data_Architecture.md` §4.4; `ingest.py:298-309` | `{ "doc_id": "uuid4", "ticker": "AAPL", "source": "...", "chunk_idx": 17, "text": "≤ ~1020 chars", "created_at": "ISO-8601 str", "embedding": [384 × double] // optional }`. ~100–2,000 rows per filing (`08` §4.4). `chunk_idx` is a 0-based integer assigned in ingest order (`for i, c in enumerate(chunks)`). `created_at` is one identical value for every chunk of a filing (a single `now` captured once). |
| Filing identity | `ingest.py:287` (`doc_id = str(uuid.uuid4())`) | The only stable machine identifier is `doc_id`. The **accession number and form type exist only inside the free-text `source` string** (e.g. `"10-Q 0000320193-24-000081 filed 2024-08-02"`), never as structured fields. `ticker` is not unique per filing (a ticker has many filings). |
| Existing filing routes | `backend/server.py:929` (`GET /filings`), `:938` (`GET /tickers`) | `GET /filings` (`list_filings`) returns `{"filings": [<metadata rows>]}` — `db.filings.find(q, {"_id": 0}).sort("created_at", -1).to_list(200)`, optional `?ticker=` filter, `current_user` required, projects out `_id`. **Returns 200 with `{"filings": []}` for an unknown ticker — no 404.** `GET /tickers` returns `distinct("ticker")`. **No `GET /filings/{id}` or any per-filing content route exists** (confirmed against `backend/tests/contract/test_route_inventory.py`'s `APPROVED_ROUTES`, 42 entries, no `{id}` filing variant). |
| Read endpoint | *(does not exist)* | The missing piece — exactly as `web/features/company-research/ui/FilingsSection.tsx` says in its own placeholder Banner: *"this section will support it once a per-filing content endpoint exists."* |
| Indexes | `backend/infrastructure/mongo/indexes.py:80-85`; `08` §5 | `filings`: I-10 `{ticker:1, created_at:-1}`, I-11 `{ticker:1, source:1}`. `filing_chunks`: I-12 `{ticker:1, created_at:-1}`, I-13 `{doc_id:1}` (single field, marked "optional" in `08` §5). **There is no compound `{doc_id:1, chunk_idx:1}` index** — see §13 OD-4. |
| Repository / port | `backend/application/ports.py:93` (`ChunkRepository`) | `ChunkRepository` Protocol exists but its docstring reads *"Defined, not implemented, this phase"*; its methods are `chunks_for_ticker(ticker, limit=2000)` and `count_for_ticker(ticker)` — **ticker-scoped, for retrieval**, not `doc_id`-scoped for reading one filing. No concrete adapter exists in `backend/infrastructure/mongo/` and it is not wired in `backend/app/container.py`. **There is no read port that returns one filing's chunks in order plus its metadata** — see §13 AG-1 and Document 60 §3.1. |
| Thin-adapter precedent | `backend/server.py:870-926` (`get_financials`, M12) | `GET /companies/{ticker}/financials` is a thin read: `container.financial_statements.get(...)` + per-`StatementType` `container.acquisition_states.get(...)` via `asyncio.gather`, group, assemble the frozen envelope, `raise InfrastructureError(...)` on a synchronous infra failure, `raise ValidationError(...)` on empty input. **No provider call, no acquisition trigger.** Uses `get_tracer().start_as_current_span("financials.get_endpoint")` and the module `logger`. |
| Error envelope | `backend/domain/errors.py`, `backend/app/api/errors.py` | Every `DomainError` subclass maps to `{"detail": "<message>", "type": "<code>"}` at the HTTP boundary. Relevant kinds: `NotFoundError` (404, `not_found`), `ValidationError` (422, `validation_error`), `InfrastructureError` (502, `infrastructure_error`). `NotFoundError`'s docstring: a resource that "does not exist (or … exists but the caller isn't its owner; those are intentionally indistinguishable)". |
| Auth | `backend/server.py` — `user: dict = Depends(current_user)` on every tool route | One dependency, used identically everywhere. **The corpus (`companies`, `filings`, `filing_chunks`) has no `user_id`** (`08` RI-5: "shared by every tenant, by design"). `GET /filings` today applies no ownership scoping. |
| Observability | `backend/infrastructure/observability/metrics.py:22-27` | Every route already emits `alphascribe_http_requests_total{method,path,status}` and `alphascribe_http_request_duration_seconds{method,path}` via `server.py`'s request-timing middleware. No filing-specific metric exists. |
| Frontend surface | `web/features/company-research/ui/FilingsSection.tsx`; `application/useFilings.ts`; `integration/{api.ts,schemas.ts}` | `FilingsSection` renders the filing list (`useFilings` → `GET /filings`, TanStack Query, `staleTime: 30_000`, `queryKey: ["company-research","filings",ticker]`) and a placeholder Banner for the content pane. `filingSchema` (`schemas.ts:157`) already models a `filings` metadata row (`doc_id, ticker, company_name?, source, num_chunks, char_count, created_at`). `key={f.doc_id}` is already the list React key. |
| Frozen component | `docs/design/09_Component_Inventory.md` §FilingViewer | `FilingViewer` — **Variants: "Filing content", "Filing analysis"**; Properties: filing sections, analysis, source anchors; States: Default/Loading/Empty/Error/AI Thinking-Streaming; Screens: SCR-06, SCR-08. **M13 targets the "Filing content" variant only** — "Filing analysis" (AI-anchored) is out of scope (§12). |

**No file above is modified by this document.** Every contract choice below
is derived from, and constrained by, this table.

## 2. Problem Definition

| Stage | State | Evidence |
|---|---|---|
| Ingestion of filing text | **Existing and sufficient** | `ingest_document`, `chunk_text`, live, tested |
| Persistence of filing text (chunked) | **Existing and sufficient** | `filing_chunks` rows with `chunk_idx`; `filings` metadata row |
| Retrieval-layer read (ticker-scoped, for RAG) | **Existing** | `retrieval.py` `filing_chunks.find({ticker}).sort(created_at,-1).limit(2000)` — but this is for the research pipeline, not for reading one filing in order |
| Per-filing content read (HTTP) | **Missing** | No route; no contract; no repository method scoped to one `doc_id` returning ordered chunks + metadata |
| Frontend filing-content surface | **Missing** | `FilingsSection.tsx` renders a placeholder Banner where the content pane belongs |

**What cannot currently be retrieved:** the text of any single ingested
filing, in reading order, by any client. The chunks physically exist in
MongoDB; no code path returns one filing's chunks (ordered, without
embeddings) to a user.

## 3. Endpoint and Resource Identity

### 3.1 Resource identity — CTO-RESOLVED (company-scoped `(ticker, doc_id)`)

Per OD-1's resolution (§3.2, §16), a filing is addressed by **`ticker` +
`doc_id` together** — company-namespaced, matching M12's own
`GET /companies/{ticker}/financials` shape. `doc_id` (the `uuid4` string
assigned at ingest, `filings.doc_id`, `08` §3 "`doc_id (PK)`") remains the
per-filing machine identifier; `ticker` is the required namespacing segment
in the path. This is:

- the only stable per-filing machine identifier (`doc_id`), now qualified by
  the company namespace the rest of the research surface already uses;
- already returned by `GET /filings` in every row (both `doc_id` and
  `ticker`);
- already the React list key in `FilingsSection.tsx` (`key={f.doc_id}`),
  rendered inside a `ticker`-scoped screen;
- already indexed on `filing_chunks` (I-13 `{doc_id:1}`) and on `filings`
  (I-10 `{ticker:1, created_at:-1}`).

**The handler MUST verify the `filings` row matches BOTH the path `ticker`
and the path `doc_id`.** A `doc_id` that exists under a different `ticker`
"does not exist for the requested company" and returns 404 (§8, OD-6).

**Not used, and why:**

- **Accession number** — not a stored field; only embedded in the free-text
  `source` string, and only for EDGAR filings (BSE annual reports and
  `POST /ingest/text` produce a differently-shaped `source`). Parsing it out
  would be fragile and incomplete.
- **`ticker` + form type** — form type is not a structured field; not
  unique.
- **A new identifier minted for M13** — explicitly rejected. Document 60 §7
  (architectural principle) and this document both forbid introducing an
  identifier solely for M13. `(ticker, doc_id)` is sufficient.

### 3.2 Endpoint shape — CTO-RESOLVED (OD-1, 2026-08-27)

**Decision (§16):**

```
GET /companies/{ticker}/filings/{doc_id}/content
```

Served under the existing `/api` router prefix as
`GET /api/companies/{ticker}/filings/{doc_id}/content`, exactly as M12's
`@api.get("/companies/{ticker}/financials")` is served at
`/api/companies/{ticker}/financials`. This is a company-namespaced
sub-resource read: "the content of this filing, for this company".

**Supersedes** the two candidate shapes previously offered for review
(`GET /api/filings/{doc_id}/content` and `GET /api/filings/{doc_id}`) — both
are withdrawn; the CTO chose the company-scoped form for consistency with
the rest of the `/companies/{ticker}/…` research surface.

`test_route_inventory.py`'s `APPROVED_ROUTES` gains exactly one entry —
`("GET", "/api/companies/{ticker}/filings/{doc_id}/content")` — a known
downstream consequence, not a design question (Document 33 §2's own
precedent). Adding that entry is part of the separately-authorized
implementation, not this contract.

## 4. Request Identity and Parameters

- **Path parameters (both required):**
  - `ticker: str` — normalised `.strip().upper()` in the handler, matching
    `list_filings` (`ticker.upper()`) and `get_financials`
    (`ticker.strip().upper()`). Empty after normalisation → `ValidationError`
    (422), matching `get_financials`.
  - `doc_id: str` — the `filings.doc_id` value. No format validation beyond
    "non-empty string" (it is an opaque `uuid4`; a value that matches no
    `(ticker, doc_id)` row → §8's 404 path, OD-6).
- **Query parameters:** none required for the current scope. Pagination
  parameters are **not** part of this contract — see §7.
- **Body:** none (GET).
- **Auth:** `current_user` dependency, identical to every other route
  (§10). `ticker` in the path is a **namespacing / validation** segment,
  not an authorization scope — the corpus has no `user_id` (§10).

## 5. Response Envelope

### 5.1 Shape — CTO-RESOLVED (OD-2, 2026-08-27)

The envelope carries **filing identity + UI metadata + content**.

**Metadata fields (from the `filings` row, verbatim — no new derivation):**

```jsonc
{
  "doc_id": "b1f2…",                // filings.doc_id (echoes the path doc_id)
  "ticker": "AAPL",                 // filings.ticker — equals the normalised path ticker (else 404, §8/OD-6)
  "company_name": "Apple Inc.",     // filings.company_name — nullable (ingest.py allows None)
  "source": "10-Q 0000320193-24-000081 filed 2024-08-02",  // filings.source — free text, as stored
  "created_at": "2026-08-02T14:11:03.221+00:00",           // filings.created_at — ISO-8601 str, as stored
  "num_chunks": 142,               // filings.num_chunks
  "char_count": 187432,            // filings.char_count
  "content": { "chunks": [ /* see below */ ] }
}
```

**Content — CTO decision (§16):** return the **already-persisted filing
content chunks using the existing persisted representation**. Each chunk
**retains its deterministic `chunk_idx` identity and its stored content
representation** (`text`). The adapter does **not** reconstruct, summarize,
transform, embed, rerank, or otherwise reinterpret the stored content.

```jsonc
"content": {
  "chunks": [
    { "chunk_idx": 0, "text": "…" },   // filing_chunks.chunk_idx + filing_chunks.text, verbatim
    { "chunk_idx": 1, "text": "…" },
    …                                   // ordered by chunk_idx ascending (§6)
  ]
}
```

- **Ordered `chunk_idx` ascending** (§6) — the reading order of the original
  document.
- **Verbatim `text`** — exactly the string persisted at ingest. No
  overlap-trimming in the adapter (that would be a transformation the CTO
  decision forbids — see §13 OD-3); any display-side handling of the
  `overlap=120` shared tail is a UI concern, outside this contract.
- **No reassembled single string, no summary, no derived field** — the
  reassembled-string and "both" representations previously offered for
  review are withdrawn.
- Faithful to `08` RI-2's "immutable historical record" discipline —
  nothing about the persisted chunk is reinterpreted.

### 5.2 What is NOT in the envelope

- **`embedding`** — the 384-dim vector on every `filing_chunks` row
  (`08` §4.4: "~75% of each chunk is the vector"). Projected out
  unconditionally. The vector is a derived retrieval artifact, not the
  filing's *content representation* — OD-2's "existing persisted
  representation" means the persisted `chunk_idx` + `text`, and the CTO
  decision's "do not … embed … or otherwise reinterpret" plus the frozen
  "no RAG" exclusion (§12) both keep it out. This also keeps the response
  small (§7), the same discipline `08` DA-10 applies to `reports` internal
  fields.
- **`_id`** — projected out, matching `GET /filings` (`{"_id": 0}`).
- **Any structured form-type / accession / filing-date field** — not stored
  (§3.1); not synthesised here. §13 AG-2.
- **Any AI analysis, summary, citation, or anchor** — out of scope (§12).
- **Any acquisition-state field** — there is no acquisition-state store for
  filings (§8; unlike M12's `AcquisitionStateRepository`).

## 6. Content Ordering

**Authoritative order: `chunk_idx` ascending.** This is deterministic,
assigned once at ingest (`ingest_document`: `for i, c in enumerate(chunks)`),
and is the reading order of the original document.

- **`created_at` must NOT be used as the sort key or a tiebreak** — every
  chunk of one filing carries the same `created_at` (a single `now` value
  captured once in `ingest_document`). It carries no intra-filing ordering
  information.
- **Incidental MongoDB return order must NOT be relied on.** The query must
  carry an explicit `.sort("chunk_idx", 1)` (or the repository method must
  guarantee it) — see Document 60 §3.2.
- `chunk_idx` is contiguous `0 … num_chunks-1` for a normally-ingested
  filing. A gap would indicate a partial/failed ingest — §8's
  malformed-content path.

## 7. Pagination Decision — NOT REQUIRED FOR M13 SCOPE

**Decision: return the complete filing content in one response. No
pagination in this contract.** Rationale, from measured repository facts:

- **Bounded input.** `ingest.py` truncates raw text at `200_000` chars
  before chunking (`text[:200_000]`, both EDGAR and BSE paths).
  `filings.char_count` is therefore ≤ ~200 KB of UTF-8 text per filing
  today.
- **Bounded chunk count.** `08` §4.4 sizes a filing at ~100–2,000 chunks;
  each chunk `text` is ~900–1,020 chars.
- **The 10 MB figure in `08` §4.4 is the *embedding* payload**, not the
  text. With `embedding` projected out (§5.2), a full filing's text is
  ≈ its `char_count` (~200 KB worst case) plus JSON framing — a single
  ordinary response, same order of magnitude as a large `GET /reports/{id}`
  (`draft_report` markdown + `source_documents`).
- **No pagination primitive exists anywhere in the codebase** to reuse
  (`GET /filings` caps at `.to_list(200)`; retrieval caps at `.limit(2000)`;
  no cursor/offset pattern; the frontend has no infinite-scroll pattern).
  Adding one would be net-new infrastructure for a payload that does not
  need it — against Document 60 §7 and `CLAUDE.md`'s "don't build ahead of
  evidence".

**Ceiling / revisit trigger (recorded, not built):** if the ingest
`200_000`-char truncation is ever raised, or a provider that returns
un-truncated multi-hundred-page filings is added, or measured
`char_count` / response latency shows a real problem, **that** is the
trigger to design chunk pagination (`chunk_idx`-range windows are the
natural cursor — stable, contiguous, already the sort key). Not before.
`OPEN DECISION` **OD-5** in §13 records the pagination parameter shape to
use *if and when* that trigger fires; it is not part of this contract.

## 8. Empty / Not-Found / Malformed Semantics

There is **no acquisition-state store for filings** (unlike M12, where
`AcquisitionStateRepository` gave `not_yet_acquired` / `available` /
`confirmed_unavailable`). A filing either has rows or it does not.
Acquisition state must **not** be inferred from an empty array — there is
nothing to infer it from, and this contract must not invent one.

The three cases below are **CTO-resolved (§16)** and carry an explicit,
frozen semantic distinction:

```
Unknown filing            → 404
Known filing + zero chunks → 200 + content.chunks: []
Known filing + content     → 200 + ordered chunks
```

| Case | Repository reality | HTTP behaviour | Status |
|---|---|---|---|
| `(ticker, doc_id)` matches a `filings` row **and** `filing_chunks` has its rows | Normal — the overwhelmingly common path | **200** with the full envelope (§5) — ordered chunks | CTO-RESOLVED (§16) |
| `doc_id` does not match any `filings` row **for the requested `ticker`** (no row at all, or a row under a different ticker) | The filing does not exist for the requested company | **404 `NotFoundError`** (`{"detail": "...", "type": "not_found"}`). `NotFoundError`'s existing semantics (resource absent / not visible) apply unchanged. | **CTO-RESOLVED (OD-6, §16)** |
| `(ticker, doc_id)` matches a `filings` row but `filing_chunks` returns **zero** rows | Should not occur via `ingest_document` (it inserts chunks *then* the filing row), but a crashed/partial ingest could leave it; a re-ingest cleanup path (`01 D-9`) could in principle remove chunks | **200 OK** with the filing metadata (§5.1) and **`content.chunks: []`** (an empty array). Never a fabricated body. Distinct from the 404 case above by status code and by the presence of the metadata envelope. | **CTO-RESOLVED (OD-7, §16)** |
| `filing_chunks` rows exist but are malformed (missing `chunk_idx`, missing/empty `text`, or a gap in the `0..n-1` sequence) | A data-integrity fault, not a normal state | **OD-8 — NOT resolved by this ratification; DELEGATED to the separate M13 implementation-authorization phase.** Non-binding candidate (recorded, not decided): serve the well-formed chunks in `chunk_idx` order and `logger.warning` the anomaly; do not 500 the whole read for one bad chunk; do not silently renumber. Whether to surface a machine-readable `"partial": true` is part of what the implementation-authorization decision settles. | OPEN — delegated to implementation |
| `(ticker, doc_id)` present but the `filings` row itself is malformed (missing `ticker` / `num_chunks` / etc.) | Data-integrity fault | Candidate (recorded, not decided): `InfrastructureError` (502) with a safe message + `logger.exception`, matching M12's `get_financials` behaviour for a read it cannot assemble. Settled at implementation-authorization alongside OD-8. | OPEN — delegated to implementation |

**Not inferred:** "content not yet available" as a *lifecycle state*. There
is no pending/acquiring concept for filings and this contract does not
invent one. The metadata-without-chunks case (OD-7) is a **data condition**
carried by the empty `content.chunks: []` array plus the 200 status; the
ratified decision mandates the empty array, not any additional flag field.

## 9. Error Semantics

Reuse the existing envelope with no additions:

- **Shape:** `{"detail": "<message>", "type": "<code>"}` via
  `backend/app/api/errors.py`'s single `DomainError` handler.
- **422 `validation_error`** (`ValidationError`) — only if a
  future parameter (e.g. an eventual pagination cursor, §7) needs domain
  validation. Not used by the current no-parameter contract.
- **404 `not_found`** (`NotFoundError`) — **CTO-RESOLVED (OD-6, §16):**
  returned when `(ticker, doc_id)` matches no `filings` row for the
  requested company.
- **502 `infrastructure_error`** (`InfrastructureError`) — a synchronous
  Mongo failure while reading, message safe ("Failed to read filing
  content. See server logs for details."), `logger.exception` first —
  identical pattern to M12's `get_financials` (`server.py:895-899`).
- **401** — unauthenticated, raised by `current_user` itself, unchanged.
- **No 5xx from a provider path** — this route makes no external call
  (§12).

## 10. Authorization

- **`current_user` dependency, unchanged.** Identical to every other tool
  route; no new authorization concept, no new decorator, no scope
  parameter.
- **No ownership scoping.** The corpus (`companies`, `filings`,
  `filing_chunks`) has no `user_id` (`08` RI-5 — shared across all tenants
  by design; the basis of the documented, accepted corpus-reuse and
  corpus-poisoning trade-offs in `10` §6.4 / SQ-1). `GET /filings` today
  applies no per-user filter, and this contract does not add one. Any
  authenticated user can read any ingested filing's content — the same
  visibility the filing *list* already has.
- **`10 SD-12` etc. unaffected** — this is a read route, no secrets, no
  fork/PR CI implications.

## 11. Observability

- **Reuse only.** Every FastAPI route already emits
  `alphascribe_http_requests_total{method,path,status}` and
  `alphascribe_http_request_duration_seconds{method,path}` via the
  request-timing middleware (`infrastructure/observability/metrics.py`).
- The handler additionally uses the existing tracing convention
  (`get_tracer().start_as_current_span("filings.get_content_endpoint")` or
  similar) and the module `logger`, matching every M8/M12 financials code
  path.
- **No new filing-specific metric is proposed.** A single, low-volume,
  read-only, indexed query does not evidence a need for a dedicated
  counter; inventing one merely because `acquisition_request_total` exists
  elsewhere is the pattern Document 55 §6 already declined. If a gap is
  later evidenced in practice, that is a separate, future decision.

## 12. Explicit Exclusions (this contract does NOT define, and M13 must NOT add)

- LLM calls of any kind in the read path.
- Filing Q&A, conversational filing interaction, or any generative feature.
- RAG / hybrid retrieval / reranking / embeddings work / a new embedding
  pipeline.
- The `FilingViewer` "Filing analysis" variant, AI-anchored analysis, or
  source anchors tied to analysis.
- Citation representation or any change to the `[n]` citation system.
- Structured filing-section extraction (Risk Factors / MD&A / Important
  Changes as distinct fields) — a separate, `DEFERRED` roadmap item
  (Document 58 §9).
- Parsing the `source` string into structured form-type / accession /
  filing-date fields (§13 AG-2).
- Any change to ingestion, `chunk_text`, chunk size/overlap, or the
  embedding step.
- Redis, any caching layer, or cache-invalidation.
- A new MongoDB collection.
- A schema migration. A new index is a separate `OPEN DECISION` (OD-4) for
  the implementation phase, not part of this contract, and not added here.
- Provider dependency, provider redesign, or multi-provider redundancy for
  filing acquisition.
- Pagination (§7) — deferred with a recorded trigger, not designed.
- G8, H-1, the self-consistency gate, generalized analytics, durable
  research sessions.

## 13. Open Decisions / Architecture Gaps Register

**OD-1, OD-2, OD-6, OD-7 are CTO-RESOLVED (2026-08-27, §16).** The rest stay
`OPEN` or are explicitly delegated to the separate M13
implementation-authorization phase — none is guessed here.

| ID | Kind | Question | Resolution / disposition |
|---|---|---|---|
| **OD-1** | ✅ CTO-RESOLVED (2026-08-27) | Endpoint shape — §3.2, §16 | **`GET /companies/{ticker}/filings/{doc_id}/content`** (served at `/api/companies/{ticker}/filings/{doc_id}/content`). Company-namespaced sub-resource. Both earlier candidate shapes withdrawn. |
| **OD-2** | ✅ CTO-RESOLVED (2026-08-27) | `content` representation — §5.1, §16 | **Ordered `content.chunks: [{chunk_idx, text}]`, using the existing persisted representation.** Each chunk retains its deterministic `chunk_idx` identity and its stored `text`. No reconstruct / summarize / transform / embed / rerank / reinterpret. Reassembled-string and "both" options withdrawn. |
| **OD-3** | RESOLVED-BY-CONSEQUENCE | Chunk `overlap` (~120 chars) handling — §5.1 | OD-2's decision forecloses **in-adapter** overlap trimming (it is a transformation). No contract change. Any display-side handling of the overlap is a UI concern, outside this contract. |
| **OD-4** | OPEN — delegated to implementation | No `{doc_id:1, chunk_idx:1}` compound index on `filing_chunks` (only I-13 `{doc_id:1}`). Sorting ≤2,000 small docs in memory is acceptable — §6, Document 60 §3.4 | **Not decided here; not added here** (schema/index changes are out of scope). The separate M13 implementation-authorization decision weighs it against measured latency. |
| **OD-5** | OPEN — deferred (trigger-gated) | If/when the §7 pagination trigger fires: parameter shape | `chunk_idx`-range window (`?from_idx=&limit=`). Not part of this contract; not triggered. |
| **OD-6** | ✅ CTO-RESOLVED (2026-08-27) | Unknown filing — §8, §16 | **404 `NotFoundError`** when `(ticker, doc_id)` matches no `filings` row for the requested company (including a `doc_id` that exists under a different ticker). |
| **OD-7** | ✅ CTO-RESOLVED (2026-08-27) | Filing exists, zero `filing_chunks` — §8, §16 | **200 OK** with the filing metadata (§5.1) and **`content.chunks: []`**. The semantic distinction unknown→404 / zero-chunks→200-empty / content→200-ordered is frozen. No additional flag field is mandated by the decision. |
| **OD-8** | OPEN — delegated to implementation | Malformed/gapped chunk sequence: serve-well-formed-and-warn vs fail; whether to surface `partial: true` — §8 | **NOT resolved by this ratification.** Delegated to the separate M13 implementation-authorization phase. Non-binding candidate recorded in §8. No behaviour invented here. |
| **AG-1** | ARCHITECTURE GAP — addressed in Document 60 | No `doc_id`-scoped filing-content read port/adapter exists — §8; Document 60 §3.1 | Document 60 §3.1 (OD-A) is **CTO-resolved to direct `db` access in the handler** (the `GET /filings` pattern) — **no new repository, port, or service for M13**. |
| **AG-2** | ARCHITECTURE GAP | No structured form-type / accession / filing-date fields exist; they live only in the free-text `source`. If the UI needs them structured, that is an ingestion-schema change (out of scope) or a parse step (fragile) — record, do not solve | Out of scope for M13; UI renders `source` as-is |
| **AG-3** | ARCHITECTURE GAP | `docs/backend_engineering/00_README.md` index and `11_ADR_Index.md` do not cover M8–M12 (Document 58 §14 GH-1/GH-2). This M13 contract, when ratified, will also need an index row — a numbered-amendment requirement, not this document's to perform | Bundle into Document 58 §26 Decision D |

## 14. Governance Status and Authorization Sequence

**M13:** direction `SELECTED` by the CTO (Document 58 §21) via this
ratification and Document 60's; Document 58 §28 to be completed as
governance hygiene.
**This contract (Document 59):** 🟢 `CTO-RATIFIED / FROZEN` (2026-08-27, §16).
**M13 architecture (Document 60):** 🟢 `CTO-RATIFIED / FROZEN` (2026-08-27).
**M13 implementation:** 🔴 `NOT AUTHORIZED`.

```text
Post-M12 roadmap reconciliation (Document 58)
        ↓  CTO ratification / M13 direction selection
M13 contract (Document 59) + M13 architecture decision pack (Document 60)
        ↓  CTO ratification — 🟢 DONE (2026-08-27, §16)  [freezes contract + architecture; authorizes NO code]
Separate, subsequent M13 implementation authorization   ← 🔴 NOT GRANTED — required next
        ↓
Engineering implementation
        ↓
Technical review
        ↓
Commit / push governance
```

**No stage is collapsible.** This ratification freezes the wire contract
(and, in Document 60, the thin-adapter architecture); it does **not**
authorize writing the route, the handler, the frontend hook, the schema, or
any other code, and it does **not** authorize adding the `APPROVED_ROUTES`
entry or the OD-4 index. A separate, subsequent CTO
implementation-authorization decision is required before any source code may
be changed — the same two-stage convention Documents 33+55 provided for M12,
Document 52 for the M10 CI-gate, and Document 47 for hallucination
detection.

The terms `APPROVED TO BUILD`, `IMPLEMENTATION READY`, and `AUTHORIZED` are
**not** applied to M13 implementation anywhere in this document. "Frozen"
here describes the **contract**, not a licence to build it.

## 15. CTO Decisions — Status

1. **Settled contract core** — resource identity (`(ticker, doc_id)`, §3.1),
   ordering (`chunk_idx`, §6), no-pagination (§7), error envelope reuse
   (§9), `current_user` + no ownership scoping (§10), observability reuse
   (§11), exclusions (§12): **RATIFIED (§16).**
2. **OD-1** — endpoint shape: **RESOLVED (§16).**
3. **OD-2** (and OD-3 by consequence) — content representation:
   **RESOLVED (§16).**
4. **OD-6 and OD-7** — not-found and metadata-without-chunks semantics:
   **RESOLVED (§16).**
5. **OD-4 / OD-5 / OD-8 / AG-1 / AG-2 / AG-3** — recorded in §13 as
   `OPEN`/deferred/delegated; **not resolved by this ratification** and not
   blockers for it. OD-4 and OD-8 are delegated to the separate M13
   implementation-authorization phase.
6. **Implementation authorization** — **NOT granted** by this ratification;
   remains a separate, subsequent CTO decision (§14).

## 16. CTO Ratification (2026-08-27)

**CTO Decision — M13 Filing Content Read API Contract.** The CTO ratified
this document (Document 59) together with Document 60 as a single M13
contract-and-architecture ratification. This section is the canonical record
of that decision; §0–§15 above are folded to match it and are otherwise
unmodified in substance.

**Four open decisions, resolved verbatim as issued:**

- **OD-1 — Endpoint shape.**
  `GET /companies/{ticker}/filings/{doc_id}/content`.

- **OD-2 — Content representation.**
  Return the already-persisted filing content chunks using the existing
  persisted representation. Each chunk must retain its deterministic
  `chunk_idx` identity and content representation. Do not reconstruct,
  summarize, transform, embed, rerank, or otherwise reinterpret the stored
  content.

- **OD-6 — Unknown `doc_id`.**
  Return HTTP 404 Not Found when the requested filing / `doc_id` does not
  exist for the requested company.

- **OD-7 — Filing exists but has no chunks.**
  Return HTTP 200 OK with the filing metadata and an empty chunks array
  when the filing exists but contains zero persisted content chunks.

  Frozen semantic distinction:
  ```
  Unknown filing              → 404
  Known filing + zero chunks  → 200 + chunks: []
  Known filing + content      → 200 + ordered chunks
  ```

**Ratified scope, as frozen — limited to:** the company-namespaced
read-only route above; the existing `filings` / `filing_chunks` persistence,
read verbatim; deterministic `chunk_idx` ordering; the `{detail,type}` error
envelope; `current_user` auth with no ownership scoping; existing HTTP
metrics + tracing + logging. Nothing beyond this combination is ratified.

**Explicit exclusions, as frozen — this ratification does NOT authorize:**
LLM calls; Filing Q&A; RAG / retrieval / reranking / embeddings work;
citation redesign; ingestion / `chunk_text` redesign; Redis; caching; a new
MongoDB collection; a schema migration; the OD-4 index (delegated); provider
dependency or redesign; premature pagination; a new repository / port /
service for M13 (Document 60 §3.1 / OD-A resolved to direct `db` access);
structured filing-section extraction; G8; H-1; generalized analytics;
durable research sessions.

**Delegated to the separate M13 implementation-authorization phase (not
resolved here):** OD-4 (compound index), OD-8 (malformed/gapped chunk
handling), the malformed-`filings`-row 502 case, OD-E (frontend surface
shape, Document 60).

**Authorization boundary (unchanged from §14):** this ratification freezes
the contract and the architecture only. It does **not** authorize
implementation. A separate, subsequent CTO implementation-authorization
decision remains required before Backend Engineering begins.

**Governance state of record, as of this ratification:**

| Item | Status |
|---|---|
| Document 59 | 🟢 CTO-RATIFIED / FROZEN |
| Document 60 | 🟢 CTO-RATIFIED / FROZEN |
| M13 contract + architecture | 🟢 FROZEN |
| M13 implementation | 🔴 NOT AUTHORIZED |
| G8 | 🔴 BLOCKED |
| H-1 | 🟡 CLOSED WITH GOVERNANCE FOLLOW-UP |
| Gate (`JUDGE_SELF_CONSISTENCY_GATE_VERSION`) | 0 |
| M12 | COMPLETE / TECHNICALLY ACCEPTED / COMMITTED (b4e90a0) / PUSHED — not reopened |

---

**NO IMPLEMENTATION PERFORMED. NO ROUTE, SCHEMA, INDEX, TEST, OR FRONTEND
FILE CREATED OR MODIFIED. NO EXTERNAL CALL. THIS RATIFICATION RECORDS CTO
DECISIONS ONLY. M13 IMPLEMENTATION REMAINS NOT AUTHORIZED. GATE REMAINS 0.
G8 AND H-1 UNCHANGED. M12 NOT REOPENED. DOCUMENTS 33 / 55 / 56 / 57 NOT
MODIFIED.**
