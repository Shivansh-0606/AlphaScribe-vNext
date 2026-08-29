# 60 — M13 Filing Content Reading Architecture Decision Pack

**Status:** 🟢 **CTO-RATIFIED / FROZEN (2026-08-27).** Defines the
thin-adapter architecture for exposing already-persisted filing content. The
architecture is aligned with the CTO-resolved Document 59 contract (OD-1
endpoint shape, OD-2 content representation, OD-6/OD-7 semantics) and with
the CTO decision that **no new repository / port / service be introduced for
M13** (OD-A → direct `db` access, §3.1). Ratification **freezes the
architecture**; it does **not** implement it, does **not** modify any
source, schema, index, or frontend file, and does **not** authorize
implementation.
**M13 implementation is NOT AUTHORIZED — a separate, subsequent CTO
implementation-authorization decision is required before any source code may
be changed (§11, §14).**
**Type:** Architecture decision pack (research/design/governance-only — no
code changed, no schema/migration/index file created, no endpoint wired, no
test added, no frontend component created).
**Companion contract:**
[59_M13_Filing_Content_Read_API_Contract.md](59_M13_Filing_Content_Read_API_Contract.md)
(the wire contract, its open decisions, and its exclusions — read first).
**Precedent (cited, unmodified):**
[55_M12_Financial_Research_Data_Completion_Architecture_Decision_Pack.md](55_M12_Financial_Research_Data_Completion_Architecture_Decision_Pack.md)
(the thin-adapter design pattern this mirrors),
[33_M8_Financials_API_Contract_Review.md](33_M8_Financials_API_Contract_Review.md)
(the read-contract precedent),
[56_M12_Governance_Authorization_Reconciliation_Record.md](56_M12_Governance_Authorization_Reconciliation_Record.md)
(the authorization-reconciliation model that would follow implementation),
[57_M12_Post_Implementation_Acceptance_Completion_Record.md](57_M12_Post_Implementation_Acceptance_Completion_Record.md)
(the technical-acceptance model). **None of these is modified by this
document.**
**Roadmap position:**
[58_Post_M12_Backend_AI_Roadmap_Reconciliation.md](58_Post_M12_Backend_AI_Roadmap_Reconciliation.md)
§20–§21. The CTO's ratification of this pack and Document 59 (§14)
constitutes CTO **selection of the M13 direction** from Document 58 §21;
Document 58 §28 to be completed as governance hygiene (Document 58 §14
GH-7 / §26 Decision D — not performed here). **Direction selection and
architecture ratification are not implementation authorization** — that
remains a separate, subsequent CTO decision (§11, §14).
**Date:** 2026-08-27.

---

## 0. What This Document Is and Is Not

**Is:** the architecture decision pack for M13 — the data-access decision,
the handler shape, the content-representation alignment, the MongoDB
posture, and the frontend integration architecture. As of 2026-08-27 the
CTO-resolved items (OD-A data access, OD-C content representation, and —
via Document 59 §16 — OD-1/OD-2/OD-6/OD-7) are folded in; the rest stay
`OPEN` or are explicitly delegated to the separate M13
implementation-authorization phase (§10, §14).

**Is not:** an implementation, an implementation authorization, a Filing
Q&A / RAG / retrieval design, a citation design, an ingestion or data-model
redesign, or an infrastructure expansion. Every still-undecided point is
recorded as `OPEN` / `ARCHITECTURE GAP` / delegated in §10 — none is guessed.

**Governance position.** The CTO's ratification of this pack and Document 59
(§14) selects the M13 direction (Document 58 §21) and freezes the M13
contract + architecture. It does **not** authorize implementation. M13
implementation remains `NOT AUTHORIZED`; a **separate, subsequent** CTO
implementation-authorization decision is required before any source code may
be changed (§11). Document 58's own §28 ratification block should be
completed to record the direction selection — governance hygiene, not
performed here.

## 1. Existing Architecture Dependency (verified this session, direct reads)

Full detail is in Document 59 §1. The load-bearing facts for the
architecture decision:

| Fact | Source | Consequence for M13 |
|---|---|---|
| Filing text is persisted **only as overlapping chunks** (`filing_chunks`, `chunk_size=900`, `overlap=120`) + one `filings` metadata row. No reconstructed document is stored. | `agents/ingest.py::ingest_document` | M13 assembles a *read view* from chunks; it does not "fetch a document" |
| Filing identity is `filings.doc_id` (`uuid4`, PK). Accession/form live only in the free-text `source`. | `08` §3, `ingest.py:287` | The endpoint is company-namespaced on `(ticker, doc_id)` per Document 59 §3.1/§16 (OD-1: `GET /companies/{ticker}/filings/{doc_id}/content`); the handler verifies the `filings` row matches both |
| Deterministic order is `filing_chunks.chunk_idx` (0-based, ingest order). `created_at` is one shared value per filing. | `ingest.py:298`, `08` §4.4 | The adapter sorts by `chunk_idx` explicitly; never trusts driver order |
| `ChunkRepository` port exists but is **"Defined, not implemented, this phase"**, is **ticker-scoped** (`chunks_for_ticker`, `count_for_ticker`), has no adapter, and is not in `container.py`. | `application/ports.py:93`, `app/container.py` | Not repurposed for M13. Per OD-A's resolution (§3.1) the handler reads `db` directly — no new port — so `ChunkRepository` is left untouched. |
| Two handler-data-access patterns coexist: `GET /filings` / `GET /tickers` hit `db` directly in the handler; M12's `GET /companies/{ticker}/financials` goes through `container.financial_statements` (a port). | `server.py:929`, `:938`, `:870` | **OD-A resolved to the direct-`db` pattern** (`GET /filings` sibling), per the CTO instruction not to invent a repository/service for M13 — §3.1 |
| M12's `get_financials` is the thin-adapter template: gather → group → assemble frozen envelope → `InfrastructureError` on infra failure → span + logger, no provider call, no side effect. | `server.py:870-926` | M13's handler copies this shape |
| No pagination primitive exists anywhere. Filing text is ≤ ~200 KB (`ingest.py` truncates at `200_000`). Embeddings (75% of chunk bytes) are projected out. | Document 59 §7, `08` §4.4 | Complete content in one response; no pagination — §4 |
| Error envelope: `{"detail","type"}` via `DomainError` → `app/api/errors.py`. `NotFoundError` 404, `ValidationError` 422, `InfrastructureError` 502. | `domain/errors.py`, `app/api/errors.py` | Reuse verbatim — no new error kind |
| Auth: `current_user` everywhere; corpus has **no `user_id`** (`08` RI-5). `GET /filings` applies no ownership scoping. | `server.py`, `08` RI-5 | `current_user` only; no scope parameter — no new authorization concept |
| Observability: every route emits `http_requests_total` / `http_request_duration_seconds` via middleware; M8/M12 paths add a tracer span + `logger`. | `infrastructure/observability/metrics.py:22` | Reuse only; no new metric |
| Frontend: `FilingsSection.tsx` renders the list + a placeholder Banner; `useFilings.ts` is a standard TanStack Query hook; M12 shipped `useFinancialStatements` + `fetchFinancialStatements` + `financialsResponseSchema` + `StatementTable` as the pattern. `FilingViewer` (frozen Component Inventory) has a **"Filing content"** variant. | `web/features/company-research/**`, `docs/design/09_Component_Inventory.md` | Mirror the M12 hook/schema/component wiring; build the "Filing content" variant only |

**No file above is modified by this document.**

## 2. Architectural Objective

```text
PERSISTED FILING CONTENT            (filing_chunks + filings — exists)
        ↓
DIRECT db ACCESS IN THE HANDLER    (OD-A resolved — no new port/repository/service;
                                    the GET /filings sibling pattern)
        ↓
THIN ADAPTER                        (one GET handler, M12 get_financials shape)
        ↓
API CONTRACT                        (Document 59 — 🟢 CTO-RATIFIED / FROZEN)
        ↓
FRONTEND READ SURFACE              (FilingViewer "Filing content" into FilingsSection)
```

A **read** milestone. It must not become Filing Q&A, LLM retrieval, RAG,
agentic reasoning, citation redesign, provider redesign, ingestion
redesign, data-model redesign, or infrastructure expansion (§6, §14).

## 3. Recommended Architecture — Thin Read Adapter

### 3.1 Backend data access — CTO-RESOLVED (OD-A, 2026-08-27): direct `db`, no new port

**CTO decision (§14):** *"Do not invent an additional service or repository
merely for M13."* OD-A is therefore resolved to the **direct-`db`-in-the-handler
pattern** — the same pattern `list_filings` / `list_tickers` already use for
the sibling `GET /filings` / `GET /tickers` routes. **No `FilingContentRepository`,
no new `infrastructure/mongo/` adapter, no new `container.py` field, no new
port.** `ChunkRepository` (`application/ports.py:93`) is **left untouched** —
it is retrieval-shaped and unimplemented; M13 does not repurpose or extend
it (this closes OD-B).

Shape (proposed for the separately-authorized implementation, not written
here):

```
db.filings.find_one({"ticker": <normalised ticker>, "doc_id": <doc_id>}, {"_id": 0})
db.filing_chunks.find({"doc_id": <doc_id>}, {"_id": 0, "embedding": 0}).sort("chunk_idx", 1)
```

- The `filings` lookup filters on **both** `ticker` and `doc_id` so a
  `doc_id` under a different ticker is not found → 404 (Document 59 §8 /
  OD-6).
- `filing_chunks` is filtered on `doc_id` (I-13) with `embedding` projected
  out (Document 59 §5.2) and an **explicit `.sort("chunk_idx", 1)`**
  (Document 59 §6).

**Trade-off accepted, as the CTO directed:** the alternative — a new
`FilingContentRepository` port + Mongo adapter + container wiring, matching
M12 — was declined for M13. `server.py` gains one more direct-`db` read
site (as `GET /filings` already is); Clean-Architecture purity is traded for
not adding a repository/service for a single read, per the explicit
instruction. If a future milestone consolidates filing data access behind a
port, that is its decision, not M13's.

### 3.2 Backend handler shape (mirrors M12 `get_financials`, `server.py:870-926`)

Proposed structure — **not written, not authorized**:

- One `@api.get("/companies/{ticker}/filings/{doc_id}/content")` handler
  (Document 59 §3.2 / §16), `user: dict = Depends(current_user)`.
- Normalise `ticker` (`.strip().upper()`); empty → `ValidationError` (422),
  matching `get_financials`.
- `with get_tracer().start_as_current_span("filings.get_content_endpoint"):`
  set `ticker` and `doc_id` span attributes.
- Read the `filings` row on `{ticker, doc_id}` and the ordered,
  embedding-stripped `filing_chunks` on `{doc_id}` — **direct `db`**
  (OD-A, §3.1), no port. **Explicit `.sort("chunk_idx", 1)`** — never
  incidental order (Document 59 §6).
- `except` a synchronous Mongo failure → `logger.exception(...)` then
  `raise InfrastructureError("Failed to read filing content. See server
  logs for details.")` — identical to `get_financials`.
- Not-found / zero-chunks handling per Document 59 §8 / §16
  (**OD-6: 404**; **OD-7: 200 + `content.chunks: []`**). Malformed-chunk
  handling (OD-8) and the malformed-`filings`-row 502 case are **delegated
  to the separate M13 implementation-authorization phase** — not decided
  here.
- Assemble the Document 59 §5 envelope: metadata fields verbatim +
  `content.chunks: [{chunk_idx, text}]` ordered ascending, `text` verbatim,
  **no transform** (Document 59 §5.1 / OD-2). **No provider call, no
  acquisition trigger, no side effect, no write.**
- Add exactly one entry to `tests/contract/test_route_inventory.py`'s
  `APPROVED_ROUTES` — `("GET", "/api/companies/{ticker}/filings/{doc_id}/content")`
  — a known downstream consequence (Document 33 §2), performed only under
  the separate implementation authorization.

### 3.3 Content representation — CTO-RESOLVED (Document 59 OD-2, 2026-08-27)

Aligned with the ratified contract (Document 59 §5.1 / §16): the adapter
returns the **already-persisted chunks in the existing persisted
representation** — an ordered list of `{chunk_idx, text}`, `embedding`
projected out. Each chunk keeps its deterministic `chunk_idx` identity and
its stored `text`.

- **No reconstruction, no reassembled string, no summary, no derived
  field.** No **in-adapter** overlap trimming — that is a transformation the
  CTO decision forbids ("do not … transform … or otherwise reinterpret").
  This closes OD-C.
- The `overlap=120` shared tail between consecutive chunks is left intact in
  the payload; any display-side handling is a **UI concern**, outside this
  architecture and outside the contract (Document 59 §13 OD-3).
- Faithful to `08` RI-2's "immutable historical record" discipline —
  nothing about the persisted chunk is reinterpreted.

### 3.4 MongoDB — no schema change; index is an OPEN DECISION, not made here

- **No new collection.** `filings` + `filing_chunks` are sufficient.
- **No schema migration.** No field is added, removed, or reshaped on
  either collection.
- **Index — OD-D: DELEGATED to the separate M13 implementation-authorization
  phase.** Today `filing_chunks` has I-13 `{doc_id:1}` (single field) and
  I-12 `{ticker:1, created_at:-1}`; `filings` has I-10 `{ticker:1,
  created_at:-1}`. The `filings` `find_one` on `{ticker, doc_id}` is a
  point lookup (well served by I-10 / a `doc_id` scan of one ticker's
  rows). The `filing_chunks` `doc_id`-scoped query with a `chunk_idx` sort
  uses I-13 for the match and sorts ≤2,000 small (embedding-stripped) docs
  in memory — acceptable at current volume. A compound `{doc_id:1,
  chunk_idx:1}` index would make the sort index-covered. **This document
  does not decide it and does not add it** (schema/index changes are out of
  scope). The separate implementation-authorization decision weighs it
  against measured latency. Recorded, not resolved.

### 3.5 Frontend integration architecture (description only — no UI built)

Mirror the M12 wiring, one-for-one:

| M12 artifact | M13 analogue (proposed, not built) |
|---|---|
| `integration/schemas.ts::financialsResponseSchema` (Zod) | a `filingContentResponseSchema` matching the ratified Document 59 §5.1 shape — metadata fields + `content.chunks: [{chunk_idx, text}]` |
| `integration/api.ts::fetchFinancialStatements(...)` via `apiFetch` + schema | a `fetchFilingContent(ticker, docId)` in the same file — the only place `company-research` touches `apiFetch` for this route (02.2 AD-1); builds the path `/api/companies/{ticker}/filings/{docId}/content` |
| `application/useFinancialStatements.ts` (keyed hook + exported query-key fn) | a `useFilingContent(ticker, docId)` hook, `queryKey: ["company-research","filing-content",ticker,docId]`, `staleTime: 30_000` — same shape as the existing `useFilings` |
| `web/components/research/StatementTable.tsx` (first build of a frozen Component-Inventory component) | the `FilingViewer` **"Filing content" variant** (frozen Component Inventory §FilingViewer) — a scrollable, section-navigable content panel; **no "Filing analysis" half**, no AI, no source anchors-to-analysis |
| `FinancialsSection.tsx` rewired to render `StatementTable` when data is present, keeping the existing banner logic for other states | `FilingsSection.tsx` rewired to render the content panel for a selected filing, **replacing the placeholder Banner** ("this section will support it once a per-filing content endpoint exists"), keeping the existing list, loading `Skeleton`, error `Banner`/Retry, and empty `Banner` exactly as they are |

**Constraints (from the commissioning instruction, §5):**

- Reuse existing `@tanstack/react-query` patterns, loading/error/empty
  states (`Skeleton`, `Banner`), foundation components (`Card`, `Text`,
  `Button`), accessibility patterns (navigable sections, per the frozen
  `FilingViewer` spec), and responsive layout conventions.
- **Do NOT** redesign the application shell, add a new state-management
  system, or introduce a new component-library primitive.
- **Do NOT** implement the UI in this milestone's governance phase — this
  pack describes the intended integration only.
- **OPEN DECISION OD-E:** whether M13 delivers the full `FilingViewer`
  split-pane shell (content pane populated, analysis pane visibly
  "not available yet") or a simpler scrollable content panel inside the
  existing `FilingsSection` list flow. Architecture artifact describes both;
  the CTO / a later implementation-authorization picks.

## 4. Pagination Architecture Decision — NOT REQUIRED FOR M13

Restated from Document 59 §7 (it is an architecture decision, not only a
contract one): **complete content in one response; no pagination.**

- Filing text is bounded (`ingest.py` truncates at `200_000` chars);
  chunk count ~100–2,000; embeddings projected out. Worst-case payload
  ≈ 200 KB of text + framing — one ordinary response.
- No cursor/offset/infinite-scroll primitive exists anywhere to reuse.
  Building one is net-new infrastructure for a payload that does not need
  it — against §7 and `CLAUDE.md`.
- **Recorded revisit trigger (not built):** raise the `200_000` truncation,
  add a provider that returns un-truncated multi-hundred-page filings, or
  observe a real latency/size problem → then design `chunk_idx`-range
  windowing (`?from_idx=&limit=`; stable, contiguous, already the sort
  key). `OD-5` in Document 59 §13 holds the parameter shape for that future
  case.

## 5. Frontend Architecture (existing surface, no redesign)

- **The placeholder already exists.** `FilingsSection.tsx` reserves the
  content pane with an honest Banner. M13 replaces that Banner with the
  real content panel and adds nothing to the surrounding list/loading/
  error/empty flow.
- **Server-state ownership** stays in the feature's `application/` layer
  (a new `useFilingContent` hook), consistent with
  `03_Data_and_State_Architecture.md` and how `useFilings` /
  `useFinancialStatements` already work. No `web/lib/state/` addition, no
  global store, no context.
- **Component home:** the `FilingViewer` "Filing content" view is a
  research component — `web/components/research/` (the same home as
  `StatementTable`, `MetricStat`, `SourceReference`), imported through the
  feature, never `components/ui` directly (per `CLAUDE.md` / frontend
  architecture).
- **Accessibility:** the frozen `FilingViewer` spec requires "Navigable
  sections"; what that requires for M13 is fixed solely by the canonical
  record in §16 (Addendum — Finding #7 CTO Interpretation) — not restated
  here. The content panel honours the existing `jest-axe` discipline the
  feature already uses.
- **No shell change, no route change** — the content lives inside the
  existing `/research?ticker=` → Filings section; no new Next.js route,
  no `(group)` change.

## 6. Strict M13 Scope

**IN SCOPE (architecture/contract level only — nothing built):**

- A read contract for existing persisted filing content (Document 59).
- A thin backend read adapter (§3.2) over existing `filings` /
  `filing_chunks` persistence.
- Deterministic content ordering by `chunk_idx` (§3.2, Document 59 §6).
- API error semantics reusing the existing `{detail,type}` envelope
  (Document 59 §9).
- Authentication/authorization using the existing `current_user`
  dependency, no ownership scoping (Document 59 §10).
- Observability reusing existing middleware + tracer + logger (Document 59
  §11).
- Frontend consumption architecture: a TanStack Query hook + api client
  fn + Zod schema + the `FilingViewer` "Filing content" variant wired into
  `FilingsSection.tsx` (§3.5, §5).
- The filing-content reading surface architecture (§5) — described, not
  implemented.

**OUT OF SCOPE (must not appear in M13, at any layer):**

- LLM calls; Filing Q&A; RAG; hybrid retrieval; reranking; agents;
  LangGraph workflows; new embedding pipelines.
- Citation-system redesign or any `[n]`-citation change.
- The `FilingViewer` "Filing analysis" variant / AI-anchored analysis /
  analysis-to-source anchors.
- Filing ingestion redesign; `chunk_text` / chunk-size / overlap changes.
- Structured filing-section extraction (Risk Factors / MD&A / Important
  Changes as fields) — separate `DEFERRED` item (Document 58 §9).
- Parsing `source` into structured fields (AG-2).
- Provider redesign; provider redundancy; a new provider dependency.
- Redis; caching; a new database/collection; new persistence infrastructure.
- Schema migration. (A new index is `OD-D` — an implementation-phase call,
  not made or applied here.)
- G8; H-1 Run 2; self-consistency gate work; generalized analytics;
  durable research sessions.
- Unrelated frontend work — no shell redesign, no state-management system,
  no changes outside the reserved content pane and its hook/schema/client.

## 7. Architectural Principle

```text
PERSISTED FILING CONTENT
        ↓
DIRECT db ACCESS IN THE HANDLER   (OD-A resolved — no new port; GET /filings pattern)
        ↓
THIN ADAPTER
        ↓
API CONTRACT   (Document 59 — 🟢 CTO-RATIFIED / FROZEN)
        ↓
FRONTEND READ SURFACE
```

- **Do not introduce a new application architecture** merely because M13
  adds an endpoint. No new layer, no new cross-cutting concern, no new
  framework.
- **No new repository / port / service for M13** (CTO decision, §3.1 /
  OD-A). `ChunkRepository` is left untouched. The handler reads `db`
  directly, exactly as the sibling `GET /filings` / `GET /tickers` routes
  already do.
- **Reuse** the M12 handler shape, the `{detail,type}` error envelope,
  `current_user`, the observability middleware, the TanStack Query hook
  pattern, the `web/components/research/` home, and the frozen `FilingViewer`
  spec. Add only the one route, the one hook, the one schema, and the one
  component the milestone genuinely requires.

## 8. Decision Rationale

- **Not "redesign filing storage / add a reconstructed-document field":**
  rejected — `08` RI-2's immutable-snapshot discipline and the "no
  ingestion redesign" scope line both forbid it; chunks + `chunk_idx` are a
  sufficient read source.
- **Not "reuse or extend `ChunkRepository`":** rejected — it is
  retrieval-shaped (ticker-scoped, `limit`-bounded, unimplemented).
  Repurposing it would couple a reading feature to the RAG port. Left
  untouched.
- **Not "add a `FilingContentRepository` port + adapter + container
  wiring":** rejected for M13 by explicit CTO instruction — *"do not invent
  an additional service or repository merely for M13."* The handler reads
  `db` directly, as `GET /filings` does (§3.1 / OD-A).
- **Not "paginate":** rejected for M13 — no evidenced need, no primitive to
  reuse, bounded payload (§4).
- **Not "add a caching layer":** rejected — single indexed Mongo read
  behind existing auth, same cost class as `GET /filings`; `CLAUDE.md` +
  Document 55 §3.3's own precedent.
- **Not "build the `FilingViewer` analysis half too":** rejected — that is
  Filing Q&A / AI analysis, an explicit exclusion and a potential future
  4th AI surface with its own separate governance (Document 58 §20.4).
- **Not "bundle structured section extraction":** rejected — a separate
  `DEFERRED` roadmap item (Document 58 §9) requiring a schema + graph-node
  ADR; M13 serves the raw text and stops there.
- **Not "scope filing content per-user":** rejected — the corpus has no
  `user_id` by design (`08` RI-5) and `GET /filings` already applies no
  scoping; adding it for the content read alone would be inconsistent and
  is not a documented requirement.

## 9. Cost / Latency / Observability

- **Cost:** zero LLM calls, zero provider calls. One `filings` `find_one`
  + one `filing_chunks` range read (embeddings projected out). Same cost
  class as `GET /filings`.
- **Latency:** one indexed match + an in-memory sort of ≤2,000
  embedding-stripped docs (or index-covered if OD-D adds the compound
  index). No external network call in the request path.
- **Observability:** `http_requests_total` / `http_request_duration_seconds`
  for free from the middleware; a tracer span and `logger` lines matching
  M8/M12. **No new metric proposed** (Document 55 §6 precedent). If a real
  gap is later evidenced, that is a separate decision.

## 10. Open Architecture Decisions / Gaps (register)

**OD-A, OD-B, OD-C are CTO-RESOLVED (2026-08-27, §14); OD-6/OD-7 resolved in
Document 59 §16.** The rest stay `OPEN` or are delegated to the separate M13
implementation-authorization phase. Cross-references Document 59 §13.

| ID | Kind | Question | Resolution / disposition |
|---|---|---|---|
| **AG-1** | ARCHITECTURE GAP — addressed | No `doc_id`-scoped filing-content read port/adapter; `ChunkRepository` is ticker-scoped + unimplemented + unwired (§1, §3.1) | **Addressed by OD-A's resolution:** the handler reads `db` directly (the `GET /filings` pattern); no port is needed, so the "gap" is not filled — it is bypassed by design, per CTO instruction. `ChunkRepository` left untouched. |
| **OD-A** | ✅ CTO-RESOLVED (2026-08-27) | Data access: new read port vs direct `db` in handler — §3.1 | **Direct `db` in the handler** (`GET /filings` pattern). No `FilingContentRepository`, no new adapter, no `container.py` change, no new port. |
| **OD-B** | ✅ CTO-RESOLVED (2026-08-27) | `ChunkRepository` disposition — §3.1 | **Leave `ChunkRepository` untouched.** Not extended, not replaced, not repurposed. (Moot given OD-A → direct `db`.) |
| **OD-C** | ✅ CTO-RESOLVED (2026-08-27) | Content representation (= Document 59 OD-2); overlap handling (= Document 59 OD-3) — §3.3 | **Ordered `content.chunks: [{chunk_idx, text}]`, existing persisted representation, verbatim, no transform.** No in-adapter overlap trimming. Overlap display handling is a UI concern, outside this architecture. |
| **OD-D** | OPEN — delegated to implementation | Add a `{doc_id:1, chunk_idx:1}` compound index on `filing_chunks`? Not decided here; not added here — §3.4 | **DELEGATED** to the separate M13 implementation-authorization phase; add only if measured latency warrants. |
| **OD-E** | OPEN — delegated to implementation | Frontend surface: full `FilingViewer` split-pane shell vs a scrollable content panel inside `FilingsSection` — §3.5 | **DELEGATED** to the separate M13 implementation-authorization phase; both shapes described in §3.5/§5. |
| **OD-6 / OD-7** | ✅ CTO-RESOLVED (2026-08-27) | Not-found / metadata-without-chunks semantics — Document 59 §8 / §16 | **OD-6: 404** when `(ticker, doc_id)` not found for the company. **OD-7: 200 + `content.chunks: []`.** |
| **OD-8** | OPEN — delegated to implementation | Malformed/gapped chunk sequence; the malformed-`filings`-row 502 case — Document 59 §8 | **NOT resolved by this ratification. DELEGATED** to the separate M13 implementation-authorization phase. No behaviour invented here. |
| **AG-2** | ARCHITECTURE GAP | No structured form-type / accession / filing-date fields (only free-text `source`). Out of scope to solve; UI renders `source` as-is — Document 59 §13 | Out of scope for M13 |
| **AG-3** | ARCHITECTURE GAP | `00_README.md` / `11_ADR_Index.md` do not cover M8–M12 or these M13 docs (Document 58 §14 GH-1/GH-2) | Bundle into Document 58 §26 Decision D — not this pack's to perform |

## 11. Document Relationships and Governance Sequence

```text
Post-M12 roadmap reconciliation        Document 58
        ↓  CTO ratification / M13 direction selection (Document 58 §28 to be completed — hygiene)
M13 contract + architecture            Documents 59 + 60 — 🟢 CTO-RATIFIED / FROZEN (2026-08-27, §14 / Doc 59 §16)
        ↓  ← DONE. Freezes the contract + thin-adapter architecture. Authorizes NO code.
Separate M13 implementation authorization   ← 🔴 NOT GRANTED — its own distinct CTO governance act, required next
        ↓
Engineering implementation             — route + handler (direct db) + hook + schema + FilingViewer "Filing content"
        ↓
Technical review                       — model per Document 57 (M12 acceptance record)
        ↓
Commit / push governance               — model per Document 56 (M12 authorization reconciliation)
```

- **Document 58 → 59 + 60:** Document 58 §20–§21 recommends the M13
  direction; ratifying Documents 59 + 60 (§14) is the "M13 contract +
  architecture" step §21's sequence names and constitutes CTO selection of
  the direction. Document 58 §28 to be completed to record that selection
  (governance hygiene — not performed here).
- **59 + 60 → implementation authorization:** ratification freezes the
  design surface. It does **not** authorize implementation. A separate,
  subsequent CTO decision is required — the same non-collapsible two-stage
  convention Documents 33 + 55 used for M12 (Document 55 §7.1), Document 52
  for the M10 CI-gate, Document 47 for hallucination detection.
- **implementation → technical acceptance → commit/push:** after
  (separately authorized) engineering, a technical-acceptance record
  modelled on Document 57 and an authorization-reconciliation record
  modelled on Document 56 would follow — each its own governance act.
- **M12 completion, Document 33 (contract precedent), Document 55
  (thin-adapter precedent), Document 56 (authorization model), Document 57
  (acceptance model), Document 58 (roadmap position)** are all
  **referenced, not modified**, by Documents 59 and 60.

## 12. Governance Status

```text
M13 direction                    SELECTED by the CTO (Document 58 §21; §28 to be completed — hygiene)
M13 API contract (Document 59)   🟢 CTO-RATIFIED / FROZEN (2026-08-27)
M13 architecture (Document 60)   🟢 CTO-RATIFIED / FROZEN (2026-08-27)
M13 implementation               🔴 NOT AUTHORIZED
Gate (JUDGE_SELF_CONSISTENCY_GATE_VERSION)   0  (unchanged — untouched by M13)
G8                               BLOCKED / CARRIED FORWARD  (unchanged — untouched by M13)
H-1                              CLOSED WITH GOVERNANCE FOLLOW-UP  (unchanged — untouched by M13)
M12                              COMPLETE / TECHNICALLY ACCEPTED / COMMITTED (b4e90a0) / PUSHED  (not reopened)
```

The terms `APPROVED TO BUILD`, `IMPLEMENTATION READY`, and `AUTHORIZED` are
**not** applied to M13 implementation anywhere in this document. "Frozen" /
"CTO-RATIFIED" here describe the **contract and architecture**, not a licence
to build them. Ratifying Documents 59 and 60 does **not** authorize
implementation (§11).

## 13. CTO Decisions — Status

1. **Thin-adapter architecture** (§3.2) and principle (§7) — a thin `GET`
   handler over existing persistence, M12 `get_financials` shape, no side
   effects, no provider/LLM call: **RATIFIED (§14).**
2. **OD-A / OD-B** — data access and `ChunkRepository` disposition:
   **RESOLVED (§14)** — direct `db` in the handler; no new port/repository/
   service; `ChunkRepository` left untouched.
3. **OD-C** — content representation + overlap handling (with Document 59
   OD-2/OD-3): **RESOLVED (§14)** — ordered persisted `{chunk_idx, text}`,
   verbatim, no transform.
4. **OD-D (index), OD-E (frontend surface shape), OD-8 (malformed chunks),
   AG-2, AG-3** — recorded in §10; **not resolved by this ratification.**
   OD-D, OD-E, OD-8 are **delegated to the separate M13
   implementation-authorization phase.**
5. **Frontend integration architecture** (§3.5, §5) — hook + api client +
   Zod schema + `FilingViewer` "Filing content" variant into
   `FilingsSection.tsx`, no shell/state-management change: **RATIFIED (§14).**
6. **Implementation authorization** — **NOT granted** by this ratification;
   remains a separate, subsequent CTO decision (§11).

## 14. CTO Ratification (2026-08-27)

**CTO Decision — M13 Filing Content Reading Architecture.** The CTO ratified
this document (Document 60) together with Document 59 as a single M13
contract-and-architecture ratification. §0–§13 above are folded to match it
and are otherwise unmodified in substance.

**Architecture ratified as:**

- **Thin read adapter** — one `GET /companies/{ticker}/filings/{doc_id}/content`
  handler in the M12 `get_financials` shape (§3.2).
- **Authenticated request** — `current_user` dependency, unchanged; no
  ownership scoping (`ticker` is a namespacing segment, not a scope).
- **Existing persistence, read verbatim** — `filings` + `filing_chunks`;
  no new collection, no schema migration.
- **Direct `db` access in the handler** (OD-A) — **no new repository, port,
  or service for M13** (explicit CTO instruction); `ChunkRepository` left
  untouched (OD-B).
- **Deterministic `chunk_idx` ordering** — explicit `.sort("chunk_idx", 1)`;
  driver order never trusted (§3.2, Document 59 §6).
- **Content representation** (OD-C) — ordered `content.chunks:
  [{chunk_idx, text}]` in the existing persisted representation; verbatim;
  no reconstruct / summarize / transform / embed / rerank / reinterpret;
  `embedding` projected out.
- **Read-only** — no acquisition trigger, no provider call, no external
  call, no write, no side effect.
- **Existing observability** — `http_requests_total` /
  `http_request_duration_seconds` from the middleware + a tracer span +
  `logger`; no new metric.
- **Not-found / zero-chunks** — OD-6: 404; OD-7: 200 + `content.chunks: []`
  (Document 59 §8 / §16).
- **Frontend integration** — a `useFilingContent(ticker, docId)` TanStack
  Query hook + a `fetchFilingContent` api-client fn + a
  `filingContentResponseSchema` Zod schema + the `FilingViewer` "Filing
  content" variant wired into `FilingsSection.tsx`; no shell redesign, no
  new state-management system, no new `components/ui` primitive.

**Explicitly NOT authorized by this ratification:** LLM calls; Filing Q&A;
RAG / retrieval / reranking / embeddings work; the `FilingViewer` "Filing
analysis" variant; citation redesign; ingestion / `chunk_text` redesign;
Redis; caching; a new collection; a schema migration; the OD-4/OD-D index;
provider dependency or redesign; premature pagination; a new
repository/port/service; structured filing-section extraction; G8; H-1;
generalized analytics; durable research sessions; any source, test, schema,
or infrastructure change.

**Delegated to the separate M13 implementation-authorization phase (not
resolved here):** OD-D (compound index), OD-E (frontend surface shape),
OD-8 (malformed/gapped chunk handling + the malformed-`filings`-row 502
case).

**Authorization boundary (unchanged from §11):** this ratification freezes
the architecture only. It does **not** authorize implementation. A separate,
subsequent CTO implementation-authorization decision remains required before
Backend Engineering begins.

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

## 15. Non-Goals / DO-NOT List (M13 must not start any of these)

- Implement M13 (route, port, hook, schema, component, test).
- Add an LLM call, provider call, RAG/retrieval/reranking, or an embedding
  pipeline anywhere in the read path.
- Build the `FilingViewer` "Filing analysis" variant or any AI-anchored
  analysis.
- Redesign filing ingestion, `chunk_text`, chunk size, or overlap.
- Add Redis, a cache, a new collection, or a schema migration.
- Add or modify a MongoDB index (OD-D is a recorded implementation-phase
  decision, not an action here).
- Parse `source` into structured fields, or add structured filing metadata
  (AG-2).
- Touch G8, H-1, the self-consistency gate, or `JUDGE_SELF_CONSISTENCY_GATE_VERSION`.
- Reopen M12 or modify Documents 33 / 55 / 56 / 57.
- Modify the frozen product roadmap.
- Redesign the frontend shell or introduce a new state-management system.
- Stage, commit, push, merge, rebase, or clean unrelated working-tree
  changes.

## 16. Addendum — Finding #7 CTO Interpretation (2026-08-28)

Recorded post-ratification. §0–§15 above are unchanged. Implementation-review
Finding #7 asked what "navigable sections" / "section-navigable content
panel" (§3.5, §5; frozen Component Inventory §FilingViewer) requires for
M13. **CTO interpretation (verbatim, review Pass 4, 2026-08-28):**

> For M13, "navigable sections" means deterministic navigation/reading
> across the persisted filing-content chunks rendered by FilingViewer.
> M13 does not introduce semantic section extraction, heading inference,
> or Risk Factors/MD&A segmentation. Structured filing-section extraction
> remains separately deferred.

**Consequence.** The shipped `FilingViewer` "Filing content" variant —
persisted chunks rendered as an ordered list of `<li>` sections inside a
labelled, keyboard-focusable (`tabIndex=0`) scroll region — already
satisfies this interpretation. **No `FilingViewer` redesign and no
semantic heading-extraction work is authorized or performed by this
addendum.** Semantic section navigation remains a separate, future,
out-of-M13-scope item. This addendum records the interpretation only; it
changes no architecture, no contract, and no code.

---

**NO IMPLEMENTATION PERFORMED. NO SOURCE, SCHEMA, INDEX, TEST, OR FRONTEND
FILE CREATED OR MODIFIED. NO EXTERNAL CALL. NO NEW APPLICATION ARCHITECTURE
INTRODUCED. M13 IMPLEMENTATION REMAINS NOT AUTHORIZED. GATE REMAINS 0. G8
AND H-1 UNCHANGED. M12 NOT REOPENED. DOCUMENTS 33 / 55 / 56 / 57 NOT
MODIFIED. NOTHING STAGED, COMMITTED, OR PUSHED.**
