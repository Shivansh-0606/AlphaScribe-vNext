# 62 — Post-M13 Backend & AI Roadmap Reconciliation

**Status:** 🟢 **CTO-RATIFIED (2026-08-30) — AUTHORITATIVE POST-M13 BACKEND &
AI ROADMAP POSITION.** This document is a roadmap reconciliation. It records
the actual post-M13 repository and governance state, classifies every known
remaining Backend & AI candidate against that state, and recommends **one**
preferred roadmap direction. The CTO ratified it as the authoritative
Post-M13 position on 2026-08-30 (§16). **Ratification adopts its findings; it
authorizes no implementation, freezes no architecture, creates no contract,
does not formally select the M14 milestone, and grants no commit or push
authorization** — see §11, §13, §14, §16. C-1 Filing Analysis is the
ratified **preferred roadmap direction**; formal M14 milestone selection
remains a separate, subsequent CTO decision.
**Type:** Roadmap reconciliation (research / governance only — no source
code changed, no test changed, no schema / index / configuration /
infrastructure changed, no architecture decided, no milestone authorized,
no frozen document edited). The only file this task creates is this
document.
**Pattern / genre:** same as
[17_M4_Backend_Capability_Roadmap_Reconciliation.md](17_M4_Backend_Capability_Roadmap_Reconciliation.md),
[28_Post_M6_Roadmap_Reconciliation.md](28_Post_M6_Roadmap_Reconciliation.md),
[44_Post_M9_Backend_AI_Roadmap_Reconciliation.md](44_Post_M9_Backend_AI_Roadmap_Reconciliation.md),
[51_Post_M11_Backend_AI_Roadmap_Reconciliation.md](51_Post_M11_Backend_AI_Roadmap_Reconciliation.md),
and
[58_Post_M12_Backend_AI_Roadmap_Reconciliation.md](58_Post_M12_Backend_AI_Roadmap_Reconciliation.md).
Reconciles current repository / governance state and recommends what comes
next. Does not itself ratify anything.
**Relationship to Document 58.** Document 58 describes the **Post-M12**
decision context. This document describes the **Post-M13** decision
context. Document 58 is **not modified** by this document (see §3 for its
precise current status). Document 58's still-live registers — its deferred
(§9), blocked (§10), and governance-hygiene (§14) tables — are carried
forward and updated here, not deleted there.
**Date:** 2026-08-30.

---

## 0. What This Document Is and Is Not

**Is:** a factual reconstruction of the post-M13 baseline, a status pass
over the governance record, an evidence-based classification of remaining
Backend & AI candidates, one recommended next direction, and a statement of
the governance gates that must be cleared before that direction could enter
implementation.

**Is not:** an implementation, an implementation authorization, a contract,
an architecture decision pack, a scope freeze, a milestone selection, an
amendment to any frozen document, a reopening of M13, or a reopening of
H-1 / G8. It creates no `window.claude`-style runtime, no endpoint, no
schema, no test. It resolves no open architectural question — where one
exists (notably the Filing Analysis chunk-vs-section question, §7), it
**surfaces** the question for the contract / architecture phase rather than
answering it.

---

## 1. Post-M13 Baseline

Reconstructed this session by direct inspection of `git` (`rev-parse`,
`rev-list`, `log`, `show`, `diff`, `diff-tree`, `ls-tree`, `ls-remote`,
`branch`, `cat-file`) and read-only reads of source, tests, and governance
documents. No mutation performed.

### 1.1 M13 status

| Fact | Value |
|---|---|
| M13 — Filing Content Reading | **COMPLETE** |
| M13 technical review | **PASS** — recorded in Document 61 §7 (targeted M13 backend 13/13; M13 contract guard 3/3 at route count 43; broader hermetic backend 594/594; frontend `tsc` clean, `eslint` clean, `FilingViewer` 3/3, `FilingsSection` 7/7). The full live backend HTTP suite (running server + MongoDB) was not run in the verification passes; the hermetic subset stood in for it, as at pre-commit review. |
| M13 implementation commit | `244ca5cba77791ab49d705db2d3fda99150e46b6` — subject `feat(m13): add filing content reading`, parent `b4e90a0` (M12), single-parent / non-merge, **12 files** (6 modified, 6 added) |
| M13 governance reconciliation commit | `f1c18c37f0650b4f66f1ad4b8b6a6e0579f67e09` — subject `docs(m13): record governance authorization reconciliation`, parent `244ca5c`, single-parent / non-merge, **1 file** (adds `docs/backend_engineering/61_...md`) |
| Publication state | **PUBLISHED.** `HEAD` = `origin/main` = `origin/HEAD` = `f1c18c3`; `git ls-remote origin refs/heads/main` = `f1c18c3` (true remote confirmed); ahead/behind = `0 / 0`. History `f1c18c3 → 244ca5c → b4e90a0` is linear. `244ca5c` was **not** amended or rebased (full SHA intact, still parented on `b4e90a0`; reflog shows a single plain `commit:` entry). |
| Documents 59 & 60 | Byte-identical across `244ca5c..HEAD` (`git diff 244ca5c HEAD -- 59 60` empty) — unchanged since publication. |
| Document 61 | Tracked in `HEAD`; added by `f1c18c3`. |

### 1.2 M13 committed file boundary (from the commit object, not the working tree)

```
M  backend/server.py
M  backend/tests/contract/test_route_inventory.py
A  backend/tests/unit/test_filing_content_get_endpoint.py
A  docs/backend_engineering/59_M13_Filing_Content_Read_API_Contract.md
A  docs/backend_engineering/60_M13_Filing_Content_Reading_Architecture_Decision_Pack.md
A  web/components/research/FilingViewer.tsx
A  web/components/research/FilingViewer.test.tsx
A  web/features/company-research/application/useFilingContent.ts
M  web/features/company-research/integration/api.ts
M  web/features/company-research/integration/schemas.ts
M  web/features/company-research/ui/FilingsSection.test.tsx
M  web/features/company-research/ui/FilingsSection.tsx
```

### 1.3 Current architectural capabilities (post-M13)

- **Backend API surface: 43 approved routes** (`backend/tests/contract/test_route_inventory.py`
  exact-set guard, `assert len(APPROVED_ROUTES) == 43`). Auth ×13; `POST /llm/validate`;
  ingest ×5 (`text` / `edgar` / `samples` / `audio` / `pdf`); companies
  (`list` / `search` / `ensure` / `trending`); `GET /filings`; `GET /tickers`;
  reports (`generate` / `{id}/stream` / `{id}` / `{id}/cancel` / `list` /
  `{id}` DELETE / `compare`); compare-explain ×4 (M9.1); learning ×4;
  `POST /companies/{ticker}/financials/acquire` (M8);
  `GET /companies/{ticker}/financials` (M12);
  **`GET /companies/{ticker}/filings/{doc_id}/content` (M13)**;
  `/`, `/health`, `/health/ready`, `/metrics`.
- **Research pipeline (unchanged by M13):** `POST /reports/generate` →
  LangGraph `retriever → (extractor ‖ tone) → synthesizer → fact_checker`
  with a conditional `fact_check_router` (retry synthesizer or end) →
  SSE stream → `GET /reports/{id}`.
- **Persistence:** MongoDB via `motor` (async). Collections in play:
  `sessions`, `companies` (+ company index), `filings`, `filing_chunks`,
  `reports`, `financial_statements`, `acquisition_states`, learning jobs.
  Repositories in `backend/infrastructure/mongo/`. **M13 added no
  collection, no index, no migration.**

### 1.4 Backend capabilities

- Stdlib-only login wall (`agents/auth.py`): `hashlib.scrypt`,
  `secrets.token_urlsafe` opaque session tokens hashed at rest, in-memory
  per-email rate limiter. Every tool endpoint behind `current_user`.
- Multi-provider LLM access **only** through `agents/llm.py`
  (`chat_text` / `chat_json`); Gemini / OpenAI-compatible / Groq; per-request
  key + base_url via `contextvar`; provider→model mapping in
  `infrastructure/llm/registry.py`.
- Hybrid retrieval (`agents/retrieval.py`): BM25 (`rank-bm25`) + dense
  (`fastembed`) + cross-encoder rerank, degrades to BM25-only offline.
  **Consumed only by the report pipeline's `retriever` node.**
- Dependency-free RAGAS-lite scoring (`agents/scoring.py`, stdlib `re`).
- Best-effort external acquisition (`agents/ingest.py`): SEC EDGAR,
  yfinance (NSE `.NS` / BSE `.BO`), BSE annual-report PDF. All failures
  return `None` and fall back; never crash a request. Raw text truncated at
  200 000 chars; chunking size 900 / overlap 120.
- Observability: `infrastructure/observability/` (logging, Prometheus
  `/metrics`, OpenTelemetry tracing); HTTP middleware + per-endpoint spans
  in `server.py` (M13 added `filings.get_content_endpoint`).
- Job / streaming infra: `infrastructure/redis/` (client, `event_bus`,
  `job_store`, `rate_limiter`); `JOB_BACKEND=memory` is the default —
  Redis is optional and used only when configured.

### 1.5 Frontend capabilities

- Next.js 15 App Router, React 19, TS strict. Route groups
  `(public)/(setup)/(workspace)/(research)/(document)`. Six features —
  `account-setup`, `company-research`, `comparison`, `learning`,
  `research-library`, `workspace-home` — each `ui/application/integration/internal`
  with an `index.ts` public surface.
- `components/foundation` (design-system wrappers) + `components/research`
  (`StatementTable`, `MetricStat`, `SourceReference`, `ConfidenceIndicator`,
  **`FilingViewer`**) + `components/ui` (shadcn primitives, foundation-only).
- Single warm-light theme (`styles/tokens.css`, no toggle).
- Data layer: TanStack Query hooks in each feature's `application/`; Zod
  schemas + `apiFetch` in `integration/`; errors normalised to `AppError`.
- Legacy CRA `frontend/` remains frozen read-only.

### 1.6 Filing / content capabilities (M13 delivered)

- Ingest persists chunked filing text + metadata to `filings` +
  `filing_chunks` (`chunk_idx` + `text`, no section identity, no headings —
  each chunk is a ~900-char slice with 120-char overlap).
- **`GET /companies/{ticker}/filings/{doc_id}/content`** — a thin,
  read-only HTTP adapter: direct `db` access (Document 60 §3.1 / OD-A — no
  new repository / port / service), `filings.find_one({ticker, doc_id})` +
  `filing_chunks.find({doc_id}, {_id:0, embedding:0}).sort("chunk_idx", 1)`
  + a Python re-sort, the frozen Document 59 §5.1 envelope. OD-6 unknown
  `(ticker, doc_id)` → 404; OD-7 known filing / zero chunks → 200 +
  `content.chunks: []`; OD-8 malformed chunk → omit + `logger.warning`;
  unassemblable `filings` row → 502. No provider call, no acquisition
  trigger, no write.
- Frontend: `useFilingContent(ticker, docId)` query hook →
  `FilingViewer` **"Filing content" variant** (ordered `<li data-chunk-idx>`
  list inside a labelled, `tabIndex=0` scroll region; verbatim chunk text;
  honest "no readable content" empty state), wired into `FilingsSection`
  replacing the prior placeholder Banner. Loading `Skeleton`, error
  `Banner` + Retry, `jest-axe` discipline preserved.
- **Not built (deliberately deferred by M13 — Document 60 §16):** the
  `FilingViewer` **"Filing analysis" variant** (AI analysis, source anchors,
  AI Thinking / Streaming states), Filing Q&A, and any semantic section
  extraction / heading inference / Risk-Factors–MD&A segmentation.

### 1.7 Repository / working-tree state

**The M13 publication state is synchronized** (`HEAD` = `origin/main` =
`f1c18c3`, `0 / 0`). **The working tree is NOT Git-clean** — it contains
known unrelated, pre-existing changes and artifacts that are outside M13
and outside this document's scope, and that this document does not stage,
modify, delete, or clean:

```
 M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated test-flake hardening)
?? docs/backend_engineering/58_Post_M12_Backend_AI_Roadmap_Reconciliation.md   (untracked governance proposal — §3)
?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/          (untracked — M11 Phase H-1 evidence)
?? FROZEN
?? Semantic
?? _)
?? or
?? structured                                                  (five untracked zero-byte editor/hook artifacts)
```

Nothing is staged. This document adds one further untracked file — itself.

---

## 2. Governance State

Recorded, not decided. Every line below is a statement of the current
record, not a new authorization.

```text
M12 (Financial Research Data Completion)   COMPLETE / TECHNICALLY ACCEPTED / COMMITTED (b4e90a0) / PUSHED
M13 (Filing Content Reading)               COMPLETE / TECHNICALLY REVIEWED PASS (Doc 61 §7) /
                                            COMMITTED (244ca5c) / GOVERNANCE-RECONCILED (Doc 61, f1c18c3) / PUSHED
Document 33  (M8/M12 Financials API Contract)          CTO-RATIFIED (2026-08-24, Round 7) / implemented / published
Document 55  (M12 Architecture Decision Pack)          CTO-RATIFIED / ARCHITECTURE FROZEN (2026-08-24) / implemented / published
Document 56  (M12 Governance Authorization Reconc.)    INFORMATIONAL audit/reconciliation record / published
Document 57  (M12 Post-Implementation Acceptance)      IMPLEMENTATION TECHNICALLY ACCEPTED / published
Document 58  (Post-M12 Roadmap Reconciliation)         PROPOSED — CTO DECISION REQUIRED / §28 pending / UNTRACKED — see §3
Document 59  (M13 API Contract)                        CTO-RATIFIED / FROZEN (2026-08-27) / implemented / published (244ca5c) / unchanged since
Document 60  (M13 Architecture Decision Pack)          CTO-RATIFIED / FROZEN (2026-08-27) / implemented / published (244ca5c) / unchanged since
Document 61  (M13 Governance Authorization Reconc.)    INFORMATIONAL audit/reconciliation record / VERSION-CONTROLLED / PUBLISHED (f1c18c3)

M13 implementation authorization   HISTORICALLY OCCURRED as a separate CTO governance act, before implementation,
                                    and is RECONCILED (not issued, not created) by Document 61 §5 / §12.5.
                                    Document 61 is the durable repository-resident attestation; it is NOT the
                                    original authorization and does not re-issue it. No standalone dated,
                                    numbered authorization artifact exists (Document 61 §5.1 / §12.5.2) — an
                                    accepted, disclosed provenance limit, not a defect this document corrects.
M13 commit                          244ca5c   (operational repository fact)
M13 governance commit               f1c18c3   (operational repository fact)
Branch synchronization              main = origin/main = origin/HEAD = f1c18c3 ; ahead/behind 0/0
Gate (JUDGE_SELF_CONSISTENCY_GATE_VERSION)   0   (unchanged — untouched by M13)
G7                                 NO ARCHITECTURE CHANGE TODAY (unchanged)
G8                                 BLOCKED / CARRIED FORWARD (unchanged — §4)
H-1                                CLOSED WITH GOVERNANCE FOLLOW-UP (unchanged — §4)

NEXT MILESTONE                     NONE currently implementation-authorized.
```

### 2.1 The authorization ladder is preserved and not collapsed

The following are **distinct governance acts**; none substitutes for
another, and this document conflates none of them:

```
implementation authorization   (a scope-bound CTO act, before code)
        ≠
technical acceptance / review PASS   (a validation fact — tests / typecheck / lint)
        ≠
commit authorization   (a CTO act permitting a commit) — for M13: NOT ON RECORD (Doc 61 §9 / §12.2 / §12.5)
        ≠
push authorization   (a CTO act permitting a push) — for M13: NOT ON RECORD (Doc 61 §12.2 / §12.5)
```

For M13: implementation authorization **occurred** (reconciled by Document
61); technical review **PASSED**; the commit `244ca5c` and its publication
are **operational facts** with no explicit commit- or push-authorization
decision on record (Document 61 records this plainly and infers no
authorization from commit existence, push completion, or technical PASS).
This document does not re-adjudicate that history and does not imply
Document 61 was the original authorization.

---

## 3. Document 58 Status

### 3.1 Evidence

- **Document 58's own header:** `🟡 PROPOSED — CTO DECISION REQUIRED`.
  Its §28 "CTO Ratification" block is **entirely `(pending)`** — no
  ratification event is recorded in the document.
- **Document 58 is untracked** in the working tree. It is **not part of the
  published governance history**; no commit contains it.
- **Document 58's recommended direction — M13 — Filing Content Reading —
  has been fully executed and published:** Documents 59 and 60 were
  CTO-ratified and frozen (2026-08-27), M13 was implemented (`244ca5c`),
  Document 61 reconciled its authorization provenance (`f1c18c3`), and all
  are on `origin/main`.
- **The M13 direction selection ran through Documents 59/60, not through
  Document 58.** Document 59 §14 states that "The CTO's ratification of this
  document … and Document 60 constitutes CTO **selection of the M13
  direction** from Document 58 §21", and that "Document 58's own §28
  ratification block should be completed to reflect that selection, as a
  governance-hygiene follow-up". Document 60 carries the same note. So the
  frozen documents themselves treat Document 58 §28 as **unfinished
  hygiene**, and the direction was adopted via 59/60's ratification rather
  than 58's.
- **Genre precedent (Document 58 header):** each roadmap reconciliation
  "becomes the authoritative current position" when ratified, while the
  prior one "remains on record as prior-generation" (Document 51 was
  ratified 2026-08-23 and kept Document 44 on record). Document 58 was
  **never ratified**, so it never formally became the "authoritative
  current position" — yet its substance (the M13 recommendation) was acted
  on anyway.

### 3.2 Determination

**Document 58 is an UNRATIFIED PROPOSAL whose recommended direction (M13)
was independently pursued and completed. Its Post-M12 decision context and
its M13 recommendation are now HISTORICAL and CONSUMED. It is neither
formally ratified nor formally superseded through the
`Documentation_Governance.md` change-request chain.** Its non-M13 content —
the deferred-work register (§9), blocked-work register (§10), and
governance-hygiene table (§14), plus the G7 / G8 / H-1 treatments (§15–§17)
— remains **accurate and unconsumed**, and is carried forward into this
document (§4, §6, §10 below).

### 3.3 Residual ambiguity (stated, not invented away)

Whether Document 58 §28 should now be **completed as a historical-record
ratification** (adopting its Post-M12 findings retroactively, the
governance-hygiene follow-up that Documents 59 §14 and 60 explicitly call
for), or **left as a permanently unratified historical proposal** whose
substantive value has been transferred into this document, is a **CTO
governance-hygiene decision**. The evidence supports either handling; it
does not conclusively mandate one. This document surfaces the choice
(§13 / §14) and does not make it. **Document 58 is not modified here.**

### 3.4 A minor internal-consistency note on Document 58 (recorded, not fixed)

Document 58's Executive Summary (§1) cross-references "§17 … §18 … §19 …
§20 … §21's options", but its actual section numbering places the M13
recommendation at §20, its scope at §20.3, its exclusions at §20.4, its
frozen authorization sequence at §21, and its "CTO Decisions Required" at
§26. This internal cross-reference drift is a pre-existing hygiene item in
an unratified document; it is **noted, not corrected** (silent edits to
governance documents are prohibited; Document 58 is out of scope for this
task).

---

## 4. H-1 / G8

Inspected for governance status only. **No evaluation run was executed.**
**No status was changed.**

### 4.1 H-1

**What it is:** the M11 **Phase H-1 self-consistency generalization
diagnostic probe** — a case-matrix experiment probing the Document 47
SS7.3.1 component/aggregate granularity rule for the Stage-1 *applicability*
judge, run independently of and subsequent to the M-04/M-05 experiments.
It is **evidence only** — it does not promote the judge, validate or
promote the gate, or authorize production readiness.

**Status:** **CLOSED WITH GOVERNANCE FOLLOW-UP** — unchanged from Document
49 §21 and carried by Documents 50 / 51 / 55 / 56 / 57 and Document 58 §17.
Not reopened by M13 and not reopened here. Any Run 2 requires a fresh
experiment identity **and** a separate CTO authorization. The untracked
`backend/evaluation/self_consistency/phase_h1_generalization_matrix/`
directory is pre-existing evidence, unrelated to M13, on the must-not-touch
list — not staged, not modified, not deleted.

**Blocks the next product milestone?** **No.** H-1 is closed, non-production,
and explicitly out of scope for every candidate in §6.

**Requires governance follow-up?** The follow-up is already the recorded
state ("CLOSED **WITH GOVERNANCE FOLLOW-UP**"). No new follow-up is created
here; none is required for milestone selection.

### 4.2 G8

**What it is:** a documented, **accepted** architectural finding — a narrow
explicit-vs-inferred precision gap in the Stage-1 applicability-judge
*prompt*. Fully contained today by `JUDGE_SELF_CONSISTENCY_GATE_VERSION = 0`
and by the judge's **total absence from any production code path**.

**Status:** **BLOCKED / CARRIED FORWARD** — unchanged from Document 50 §16,
Document 51 §15, Document 55 §10, Document 56 §10, and Document 58 §16. No
CTO authorization exists for any step of its named future pathway (bounded
prompt/rubric revision → diagnostic experiment → independent review →
evidence → separate gate decision). A G8 bounded-revision governance
package is `PROPOSED / BLOCKED` (Document 58 §11). This document does not
touch G8: it proposes no revision, authors no diagnostic, changes no prompt
or rubric, and does not change `JUDGE_SELF_CONSISTENCY_GATE_VERSION`.

**Blocks the next product milestone?** **No.** G8 is non-production and
explicitly excluded from every candidate's scope in §6.

**Requires governance follow-up?** Only if the CTO independently elects to
authorize a pathway step — which is a separate decision, not a dependency
of next-milestone selection.

### 4.3 Effect on milestone selection

**Neither H-1 nor G8 blocks, gates, or should drive next-milestone
selection.** Both remain standing debt the CTO may separately choose to
address. Any candidate in §6 whose architecture would touch the judge, the
gate, H-1, or G7 is out of scope by that fact alone.

---

## 5. Current Technical Baseline

A description of the architecture as it stands after M13. **Not an
implementation proposal.** Nothing below authorizes a change.

### 5.1 Backend

- **FastAPI routes:** 43 approved (§1.3). Additive-only discipline enforced
  by the exact-set route-inventory contract test.
- **Company-research APIs:** `companies` search / ensure / trending / list;
  `tickers`; `reports/generate` + SSE + `reports/{id}` + `reports` list +
  `reports/{id}` DELETE; `reports/compare` + compare-explain ×4;
  `companies/{ticker}/financials` (read, M12) +
  `companies/{ticker}/financials/acquire` (M8).
- **Filing APIs:** `GET /filings` (metadata list) +
  `GET /companies/{ticker}/filings/{doc_id}/content` (M13, chunked text
  read).
- **Persistence:** MongoDB via `motor`; repositories in
  `infrastructure/mongo/` for financial statements and acquisition state;
  filings / filing_chunks read via **direct `db`** in the handler (the M12
  `get_financials` shape, and the M13 pattern that Document 60 OD-A froze).
  `infrastructure/mongo/indexes.py` holds the index set.
- **MongoDB usage:** read-heavy; the M13 read path issues one `find_one`
  and one `find().sort().to_list()`; no write, no upsert, no aggregation
  pipeline.
- **Acquisition boundary:** `agents/ingest.py` only. Best-effort; `None` +
  fallback on any failure; 200 000-char truncation. **No read endpoint
  triggers acquisition.**
- **Provider boundary:** `agents/llm.py` only (`chat_text` / `chat_json`);
  `agents/financials_provider.py` for financial data. **No read endpoint
  calls a provider.** M13's read path calls neither.
- **Redis / cache boundary:** `infrastructure/redis/` (job store, SSE event
  bus, rate limiter); `JOB_BACKEND=memory` default. **No caching layer for
  API responses; M13 added none.**
- **Observability:** structured logging, Prometheus `/metrics`,
  OpenTelemetry tracing; per-endpoint spans; `/health` + `/health/ready`.
- **Testing:** `backend/tests/unit/` (53 files, hermetic TestClient +
  fake-Mongo), `backend/tests/contract/` (5, incl. the 43-route exact-set
  guard), plus live HTTP suites (`backend_test.py`, `backend_test_iter2-7.py`
  — additive per feature); pytest-xdist `-n 2 --dist loadscope` (fixed).

### 5.2 Frontend

- **Company-research flow:** `CompanyResearchScreen` composes
  Overview / Financials / Filings / AIInsights / Copilot / Export /
  SectionNav; server state in the feature's `application/` layer.
- **Filings flow:** `useFilings` (metadata list) + `useFilingContent`
  (M13 content read) → `FilingsSection` renders the list with a per-filing
  "Read content" toggle → `FilingViewer` "Filing content" variant.
- **API client:** `integration/api.ts` — one `apiFetch` call site per
  route; `fetchFilingContent(ticker, docId)` builds
  `/api/companies/{ticker}/filings/{docId}/content` with `encodeURIComponent`.
- **Zod validation:** `integration/schemas.ts` — `filingContentResponseSchema`
  (metadata fields + `content.chunks: [{ chunk_idx, text }]`), validated by
  `apiFetch`; failures normalise to `AppError`.
- **TanStack Query:** `useFilingContent` — `queryKey ["company-research",
  "filing-content", ticker, docId]`, `staleTime 30_000`, `enabled` gated on
  a selected `docId`, **no feature-local `retry`** (global `retry: false`).
- **`FilingViewer`:** presentational; caller owns loading / error / retry;
  renders ordered chunks verbatim in a labelled `tabIndex=0` scroll region;
  honest zero-chunk empty state; no fabricated text.
- **`FilingsSection`:** list + `Skeleton` loading + `Banner` + Retry error
  + honest empty state, all preserved; only the content pane is new.
- **Error handling / accessibility:** `apiFetch` trust boundary +
  `AppError` normalisation; `jest-axe` on `FilingViewer` and `FilingsSection`;
  `role="region"` + `aria-label` + keyboard focus on the reading pane.

### 5.3 AI

- **RAG / LLM boundaries today:** the hybrid retriever + the four-node
  LangGraph pipeline serve **report generation**; `comparison_explanation`
  and the `learning_graph` are the other two LLM surfaces. Retrieval is
  **not** wired to any filing-scoped surface. The M13 read path is
  **RAG-free and LLM-free** by design.
- **Intentionally NOT implemented:** any AI on a specific filing (the
  `FilingViewer` "Filing analysis" variant), Filing Q&A, semantic filing
  section extraction (Risk Factors / MD&A / Important Changes as structured
  outputs), cross-filing analytics, filing-scoped citations.
- **What future work would require architectural decisions:** a new
  filing-scoped AI surface would be a **fourth** LLM surface and would touch
  the frozen LangGraph architecture (the §2.3 reducer rule and the `G-1`
  node-name contract, per Document 58 §9); it would require its own API
  contract and its own architecture decision pack, and it would have to
  resolve whether it operates over the current unstructured chunk
  representation or requires structured section boundaries first (§7).

---

## 6. Product Capability Gaps

Scoped to AlphaScribe's equity-research mission ("reduce hours of manual
equity research into minutes"), measured against the frozen product roadmap
(`docs/master-plan/03_Feature_Roadmap.md`, V1.0 MVP) and the current
implementation. **Maximum 5 candidates. This is not a backlog and not a
selection.**

### C-1 — Filing Analysis (grounded AI over the filing content M13 now serves)

1. **User problem.** The app now serves the raw 10-K/10-Q text (M13) and a
   whole-company AI brief, but there is **no AI analysis scoped to a
   specific filing** — no filing summary, no Risk-Factors digest, no MD&A
   digest, no "important changes" for one document.
2. **User value.** Highest of the candidates. Directly delivers the roadmap
   line "SEC Filing Analysis" (10-K / 10-Q Analysis, Filing Summaries, Risk
   Factors, Management Discussion, Important Changes) and establishes the
   foundation for a later, separately scoped "AI Financial Copilot → Filing
   Q&A" capability (not part of C-1 / M14 scope — §10). Completes the
   two-part `FilingViewer` spec (Component Inventory §FilingViewer:
   "Variants: Filing content, Filing analysis"), of which only "Filing
   content" now exists.
3. **Existing-data reuse.** M13's `filing_chunks` + `GET …/content`; the
   hybrid retriever; the synthesizer / fact-checker LangGraph pattern;
   `SourceReference` + citation infrastructure; the SSE job lifecycle;
   `useResearchJob`-shaped frontend hooks.
4. **Architectural complexity.** **Medium–High.** A fourth LLM surface;
   needs its own API contract and architecture decision pack; likely a new
   scoped graph or node; touches the frozen LangGraph architecture. Carries
   an unresolved design question (§7).
5. **Dependencies.** *Governance dependencies:* none blocked — C-1 builds
   directly on M13 and has no governance-blocked prerequisite. *Technical
   sequencing dependency:* C-2 (Structured Filing Extraction) **may** become
   a prerequisite depending on the §7 architecture decision — an open
   question for the future contract / architecture phase, not decided here.
6. **Scope risk.** **Med–High.** "Fixed analysis outputs" vs "conversational
   Filing Q&A" must be bounded early or it becomes a chat feature; whole-
   filing vs retrieval-scoped analysis is an architecture fork with cost
   implications.
7. **Why now.** M13 was the prerequisite — it just made the persisted
   filing text readable through an authorized endpoint. This is the direct,
   evidence-supported continuation of the M12 → M13 application-capability
   track.
8. **Explicit exclusions (high level; not a contract).** No generic filing
   chatbot; no multi-turn conversational Q&A; no cross-filing comparison;
   no alerts; no ingestion redesign; no provider redesign; no Redis / cache
   layer; no unrelated financial visualization. Whether it may or must
   introduce RAG, structured section extraction, or persisted analysis is
   **left to the architecture phase** (§7).

### C-2 — Structured Filing-Section Extraction

1. **User problem.** `filing_chunks` are ~900-char slices with no section
   identity; a user cannot jump to "just the Risk Factors" or read a clean
   MD&A. `FilingViewer` currently calls each chunk a "section" only as a
   navigation convenience.
2. **User value.** High. Better in-filing navigation; a likely prerequisite
   for high-quality Filing Analysis (C-1).
3. **Existing-data reuse.** `filing_chunks`, the ingest pipeline, the M13
   read envelope shape.
4. **Architectural complexity.** **Med–High.** New schema (section
   boundaries / labels) + a new ingest or graph node (frozen-architecture
   change — Document 58 §9), a contract decision, and probably a re-ingest
   or backfill path.
5. **Dependencies.** None blocked. Document 60 §16 and Document 58 §9
   already record structured extraction as a **separate DEFERRED item**.
6. **Scope risk.** **Medium.** "Which sections, how identified (heading
   heuristics vs LLM), stored where" is a real design space.
7. **Why now.** Raw text is served; structuring it is the natural next
   structuring step and de-risks C-1.
8. **Explicit exclusions.** No AI analysis of the extracted sections (that
   is C-1); no new provider; no visualization; no cross-filing work.

### C-3 — Financial Visualization (charts over M12 financials)

1. **User problem.** Financial statements render as tables only; the
   roadmap's "Data Visualization" (Revenue / Profit / Margin / Growth /
   Ratio charts) is unbuilt.
2. **User value.** Medium–High, highly visible.
3. **Existing-data reuse.** `GET /companies/{ticker}/financials` already
   returns the multi-period `periods[]` metric series; `recharts` is the
   roadmap-designated library (not yet installed in `web/`).
4. **Architectural complexity.** **Low–Medium — frontend-only.** Document
   58 §9 explicitly records that M12 removed the data blocker and "any
   remaining work is frontend (`recharts`), not a Backend & AI milestone".
5. **Dependencies.** None.
6. **Scope risk.** **Low.**
7. **Why now.** The data blocker is already gone; nothing else is needed.
8. **Explicit exclusions.** No backend change; no new endpoint; no derived
   / aggregated metrics beyond what `financials` returns.
   **Classification caveat:** this is a **frontend** initiative, not a
   Backend & AI milestone — it can proceed on the frontend track
   independently of this reconciliation's milestone recommendation.

### C-4 — "What Changed Since Last Review" (period / prior-report diff brief)

1. **User problem.** A returning user re-reads a full brief instead of
   getting "what's new since last time". The roadmap names "What Changed
   Since Last Review" under Company Research.
2. **User value.** Medium–High for retention.
3. **Existing-data reuse.** The `reports` collection (prior briefs), the
   financials `periods[]` series, and the M9.1 comparison-explanation diff
   pattern.
4. **Architectural complexity.** **Medium.** Needs prior-report / period
   selection and a diff-synthesis path — likely a new endpoint plus scoped
   reuse of the existing pipeline.
5. **Dependencies.** None blocked. Adjacent to (but not) Durable Research
   Sessions, which is `BLOCKED` pending a product decision + ADR + a new
   collection (Document 58 §10).
6. **Scope risk.** **Medium.** "What changed" scope (financials-only vs
   narrative vs both) must be bounded.
7. **Why now.** Enough report history and multi-period financial data now
   exist for a diff to be meaningful.
8. **Explicit exclusions.** No durable sessions; no notifications / alerts;
   no new collection; no watchlist.

### C-5 — Governance closure + register hygiene (Post-M13 reconciliation + Document 58 §28 + GH-1/2/4/5/6)

1. **User problem.** None user-facing. Governance integrity.
2. **User value.** Low for users; **high for governance** — it prevents a
   future document citing a stale register (`00_README` index stops at M7;
   `11_ADR_Index` has no M8/M10/M11 rows; `Feature_Parity_Tracker` Phase 4B
   note is now doubly stale — M12 closed the financials gap and M13 closed
   the filing-content-pane gap) as evidence that shipped M8–M13 work "does
   not exist" or "is unapproved".
3. **Existing-data reuse.** N/A — documentation only.
4. **Architectural complexity.** **Low.**
5. **Dependencies.** None.
6. **Scope risk.** **Low.**
7. **Why now.** This is the fifth-plus milestone transition reconstructed
   after the fact (Document 58 §14 GH-7); Document 58 is unratified **and**
   untracked while its recommendation has already shipped.
8. **Explicit exclusions.** No source / test / architecture change; no
   milestone selection or authorization. This document itself is the first
   step of C-5.

---

## 7. Filing Analysis as a Candidate — the Open Architectural Question

If C-1 (Filing Analysis) proceeds, its contract / architecture phase must
resolve the following. **This document does not resolve them.** Existing
governance **does not** resolve them — Document 60 §16 defers *structured
section extraction* but does not state whether analysis can operate without
it; Document 58 §9 records structured extraction as a separate deferred
item.

| Question | Current evidence | Resolved by governance? |
|---|---|---|
| **Are the existing filing chunks sufficient input for analysis?** | Chunks are `chunk_idx` + `text`, ~900 chars, 120-char overlap, **no section identity, no headings** (`FilingViewer.tsx`: "they carry no headings of their own"). A whole-filing pass over the ordered chunks is mechanically possible for small filings; large filings (up to ~200 KB / hundreds–thousands of chunks, `08` §4.4) make a single pass costly. | **No.** |
| **Are section boundaries required?** | "Risk Factors summary" / "MD&A summary" implies knowing which chunks *are* those sections. Without boundaries, analysis is either whole-filing or retrieval-selected. | **No — open.** |
| **Is structured extraction (C-2) a prerequisite?** | Plausible: C-2 would give the section labels C-1 needs. Also plausibly avoidable: retrieval or an LLM classification pass could locate sections at analysis time. | **No — open. This is the sequencing fork.** |
| **Can analysis be performed without introducing RAG?** | A whole-filing pass avoids retrieval. A relevance-scoped pass would introduce retrieval into a **new** surface — an architectural decision (the retriever is currently report-pipeline-only). | **No — open.** |
| **Does analysis require LLM usage?** | Yes — "analysis / summary" is inherently generative. This makes C-1 a **fourth LLM surface**, unlike M12 and M13 which are LLM-free reads. | Yes (implied) — but the *shape* (new graph vs new node vs reuse) is open. |
| **Would citations be required?** | The roadmap's "Trusted AI" pillar (Grounded AI, Source Traceability, Citation Inspection) and the `FilingViewer` usage rule ("Analysis always anchored to the filing") strongly imply **yes** — analysis anchored to `chunk_idx` ranges at minimum. | Partially — the product spec implies it; the mechanism is open. |
| **Is persisted analysis required?** | Not obviously. Analysis could be computed on demand (like `reports`) or persisted (a new field / collection — which M13's exclusions and the "no new collection" discipline would scrutinise). | **No — open.** |
| **Is conversational Filing Q&A in scope?** | The roadmap lists "Filing Q&A" under "AI Financial Copilot", but a multi-turn chat surface is materially heavier than fixed analysis outputs and is the most likely scope-creep vector. | **No — open; recommended exclusion (§10).** |

**The architectural question this reconciliation surfaces (and leaves for
the contract / architecture phase):**

> *Can Filing Analysis operate effectively over the current persisted,
> unstructured chunk representation, or does it require structured filing
> section extraction (C-2) as a prerequisite?*

A legitimate outcome of C-1's architecture phase is the finding that C-2
must come first — which would **re-sequence** the roadmap. The
recommendation in §9 is made with that possibility explicitly open.

---

## 8. Candidate Comparison

**Methodology.** Qualitative ordinal ratings (Low / Medium / High), no
composite numeric score. Ranking is by the combination of **user value ×
strategic relevance** (does it advance the equity-research mission and the
frozen roadmap) against **complexity + scope risk + dependency risk**
(what stands in the way), with **data reuse** and **architectural
leverage** as tie-breakers. C-3 is ranked but flagged as a frontend
initiative, not a Backend & AI milestone.

| # | Candidate | User value | Strategic relevance | Data reuse | Arch. leverage | Complexity | Scope risk | Dependency risk | Notes |
|---|---|---|---|---|---|---|---|---|---|
| **1** | **C-1 Filing Analysis** | **High** | **High** (completes "SEC Filing Analysis"; establishes the foundation for a later, separately scoped Filing Q&A capability; finishes the FilingViewer spec) | **High** (M13 data + retriever + synthesizer/fact-checker + citations + SSE) | **High** (direct M12→M13 continuation) | Med–High | **Med–High** (Q&A creep; whole-filing vs retrieval fork) | **Medium** (open §7 question; possible C-2 prerequisite) | Strongest overall; the §7 question is the main uncertainty |
| **2** | **C-2 Structured Filing Extraction** | Med–High | Medium–High (navigation; de-risks C-1) | Medium (chunks + ingest) | Medium (prerequisite-adjacent to C-1) | **Med–High** (new schema + node; frozen-architecture change; re-ingest) | Medium | Low | Delivers navigation, not analysis; heavier than C-1 for lower standalone value |
| **3** | **C-3 Financial Visualization** | Med–High | Medium (roadmap "Data Visualization") | **High** (M12 `periods[]` ready) | Low (no backend leverage) | **Low–Med (frontend-only)** | **Low** | **Low** | **Not a Backend & AI milestone** — frontend track; can proceed independently |
| **4** | **C-4 "What Changed"** | Med–High | Medium (retention; roadmap Company Research line) | Medium (reports + financials + M9.1 diff pattern) | Medium | Medium | Medium (scope of "changed") | Medium (adjacent to BLOCKED Durable Sessions) | Valuable retention feature; fuzzier scope than C-1 |
| **5** | **C-5 Governance closure + hygiene** | Low (users) / **High (governance)** | High (integrity; unblocks a clean next cycle) | N/A | N/A | Low (docs) | Low | None | Not a product milestone; this document is step 1 of it |

---

## 9. Recommended Next-Milestone Direction

**Recommendation: C-1 — Filing Analysis (grounded AI analysis scoped to a
single filing, over the filing content M13 now serves).**

**Governance status of this recommendation.** C-1 Filing Analysis is the
**preferred roadmap direction** proposed by this reconciliation. It is
**not** formally selected as the M14 milestone — formal milestone selection
is a separate CTO act, subsequent to roadmap ratification (§11, §13). This
section recommends a direction; it selects nothing.

**Why C-1 over the alternatives.** It is the only candidate that is
simultaneously (a) the highest-value **named** user-facing capability gap
left in the core Company Research domain (the roadmap's "SEC Filing
Analysis" line, plus the foundation for a later, separately scoped "Filing
Q&A" capability, and the unbuilt half of the frozen `FilingViewer` spec),
(b) the direct, evidence-supported continuation of
the M12 → M13 application-capability track (M13 was the prerequisite read
path), (c) a heavy reuser of infrastructure already built and hardened —
the hybrid retriever, the synthesizer / fact-checker pattern,
`SourceReference` citations, the SSE job lifecycle — so it delivers user
value without premature infrastructure, and (d) free of any
governance-blocked dependency (unlike G8 remediation, the judge gate,
Durable Research Sessions, or M9 closure). C-2 is heavier and delivers
navigation rather than analysis; C-3 is a frontend initiative, not a
Backend & AI milestone; C-4 is valuable but a narrower retention feature
with fuzzier scope; C-5 is governance hygiene (and is recommended
*alongside* C-1's governance track, §13, not instead of it).

**Explicit caveat.** C-1 carries the unresolved chunk-vs-section
architectural question (§7). Its contract / architecture phase must resolve
whether Filing Analysis can operate over the current unstructured chunk
representation or requires structured section extraction (C-2) first. **A
legitimate outcome of that phase is a decision to sequence C-2 before C-1.**
This recommendation is for the *direction*; it does not pre-decide the
sequencing.

**This is a roadmap recommendation only. It does not authorize
implementation.** It creates no contract, no architecture, no scope freeze,
no implementation requirement beyond the high-level boundary in §10, no
commit, and no push.

---

## 10. Scope Boundary (high level only — NOT a contract)

For the recommended direction (C-1 Filing Analysis), the following
high-level exclusions are supported by §5–§7 and are recorded so that a
future contract / architecture phase starts from a bounded surface. **This
is not a contract and not an architecture decision.** The contract phase
sets the real scope.

**Filing Analysis should NOT include:**

- A generic filing chatbot or any general-purpose conversational agent.
- Multi-turn conversational Filing Q&A (fixed / structured analysis outputs
  first; conversational Q&A is a separate, later, scoped decision).
- Cross-filing comparison, trend analysis, or any multi-filing aggregation.
- Alerts, notifications, watchlists, or any scheduling capability.
- Ingestion redesign — no change to `agents/ingest.py`, `chunk_text`,
  chunk size, or overlap.
- Provider redesign or a new provider dependency (LLM access stays through
  `agents/llm.py`).
- A new Redis / cache layer or any response-caching / invalidation
  mechanism.
- Unrelated financial visualization (that is C-3, a separate frontend
  initiative).
- Any G8 remediation step, any change to H-1 / G7 / the judge / the
  self-consistency gate.
- Any change to Documents 59 / 60 / 61 or to the M13 implementation.

**Deliberately left OPEN for the contract / architecture phase (not
excluded, not required here):**

- Whether structured section extraction (C-2) is a prerequisite (§7).
- Whether retrieval / RAG is introduced into this new surface, or analysis
  runs whole-filing over ordered chunks.
- Whether analysis output is computed on demand or persisted (and if
  persisted, in what representation — a new collection would face the "no
  new collection" scrutiny M13 applied).
- The citation mechanism (the product's "Trusted AI" pillar implies
  filing-anchored citations; the mechanism is a design decision).

---

## 11. Governance Decision

```text
C-1 — Filing Analysis:               PREFERRED ROADMAP DIRECTION (this document's recommendation) —
                                     NOT formally selected as the M14 milestone.
C-1 formal M14 milestone selection:  NOT MADE — a separate CTO act, subsequent to roadmap ratification
Roadmap position of this document:   PROPOSED — CTO DECISION REQUIRED (this document is not yet ratified)
C-1 contract:                        NOT YET PROPOSED / NOT RATIFIED
C-1 architecture decision pack:      NOT YET PROPOSED / NOT RATIFIED
C-1 implementation:                  NOT AUTHORIZED
C-1 commit:                          NOT AUTHORIZED
C-1 push:                            NOT AUTHORIZED

Document 58:                         UNRATIFIED HISTORICAL PROPOSAL (§3); §28 disposition is a CTO hygiene decision
Gate (JUDGE_SELF_CONSISTENCY_GATE_VERSION):   0   (unchanged)
G7 / G8 / H-1:                       unchanged (§4)
```

This document **invents no authorization**, issues none, and implies none.
**CTO roadmap ratification of this document may record C-1 as the preferred
roadmap direction for subsequent contract and architecture work; it does
not constitute formal M14 milestone selection, contract approval,
architecture approval, implementation authorization, commit authorization,
or push authorization.** Ratification adopts the reconciliation findings
(§1–§8) as the authoritative Post-M13 roadmap position; it does **not**
authorize the C-1 contract's content, the C-1 architecture, C-1
implementation, a commit, or a push. The governance separation is preserved
and not weakened. The ordered progression — each step a distinct CTO act
that does **not** confer the next — is:

    candidate  →  preferred roadmap direction  →  formal M14 milestone
    selection  →  contract  →  architecture  →  implementation authorization

Equivalently, `recommendation ≠ formal milestone selection ≠ implementation
authorization ≠ commit authorization ≠ push authorization`. **C-1 Filing
Analysis is at "preferred roadmap direction"; it has not been formally
selected as the M14 milestone.** Each downstream step is a separate,
subsequent CTO governance act (§13).

---

## 12. Risks

| # | Risk | Description | Mitigation |
|---|---|---|---|
| R-1 | **Scope explosion (Filing Analysis → chatbot)** | "Filing Analysis" drifts into multi-turn conversational Filing Q&A, a materially larger surface. | §10's exclusion list; the contract phase must draw the "fixed outputs, no chat" line explicitly. |
| R-2 | **Chunk-vs-section architectural mismatch** | Analysis over ~900-char unstructured chunks may not produce a coherent "Risk Factors summary" without section boundaries; the design could stall or over-build. | §7 surfaces the question as the first thing the architecture phase must resolve; re-sequencing C-2 before C-1 is an accepted possible outcome. |
| R-3 | **Premature RAG / LLM architecture** | The team wires retrieval into a new filing surface, or builds a persisted-analysis store, before the contract establishes it is needed. | §10 leaves RAG / persistence OPEN, not assumed; the "don't build ahead of evidence" discipline (Documents 44 §4.4, 47 §16, 52 §13) applies. |
| R-4 | **"Obviousness" risk (carried from Document 58 §27 / Document 51 §22)** | C-1, C-2, G8, and the judge gate are technically proximate and could be started without fresh authorization because prerequisites look satisfied. | §11's explicit `IMPLEMENTATION NOT AUTHORIZED`; the two-stage-plus convention in §13; classification is the safeguard, not a green light. |
| R-5 | **Governance drift on Document 58** | Document 58 remains unratified **and** untracked while its recommendation has shipped — an inconsistent state that could confuse a future reader or reconciliation. | §3 determines its status precisely; §13 / §14 fold its disposition into the next CTO decision; §3.3 states the residual ambiguity rather than inventing a resolution. |
| R-6 | **Frozen-register staleness (Document 58 §14 GH-1 / GH-2 / GH-5)** | `00_README`, `11_ADR_Index`, and `Feature_Parity_Tracker` now materially understate M8–M13; a future document could cite one as evidence that shipped work is unapproved. | C-5; §13 recommends folding the numbered amendments into the next governance cycle. |
| R-7 | **Contract-gap risk (from Document 58 §27)** | No ratified contract exists for C-1 (or any candidate). Skipping to implementation would repeat the failure the two-stage convention prevents — which M13 correctly avoided via Documents 59 / 60. | §13's uncollapsed gate sequence; §14's acceptance criteria. |
| R-8 | **H-1 / G8 dependency** | None. Both are closed / blocked, non-production, and explicitly out of every candidate's scope (§4). | No mitigation required; recorded so the absence of a dependency is explicit. |
| R-9 | **Fourth-LLM-surface architectural load** | C-1 adds a fourth LLM surface (after report / compare-explain / learning) and touches the frozen LangGraph architecture (§2.3 reducer, `G-1` node-name contract). | The architecture decision pack must treat any LangGraph change as a stop-and-CR item, per `CLAUDE.md` and the frozen frontend/backend architecture rules. |

---

## 13. Next Governance Action

**Recommended immediate action:** submit this document for **CTO review and
roadmap ratification**, together with a CTO decision on the Document 58 §28
disposition (§3.3).

**The gate sequence — none of these steps may be collapsed:**

```text
Post-M13 roadmap reconciliation   ← THIS DOCUMENT (62). PROPOSED — CTO DECISION REQUIRED.
        ↓  CTO roadmap ratification  (adopts §1–§8; records C-1 as the PREFERRED ROADMAP DIRECTION; Document 58 §28 disposition decided)
formal M14 milestone selection     (a separate CTO act — NOT performed by roadmap ratification; C-1 is not the M14 milestone until this step)
        ↓  CTO milestone-selection decision
next-milestone contract proposal   (a new "M14 Filing Analysis API Contract" artifact — NOT created here)
        ↓  CTO contract ratification
architecture decision pack         (a new "M14 Filing Analysis Architecture Decision Pack" — NOT created here;
                                    must resolve the §7 chunk-vs-section question and may re-sequence C-2 before C-1)
        ↓  CTO architecture ratification
separate implementation authorization   (its own distinct, scope-bound CTO governance act — NOT this document,
                                         NOT roadmap ratification, NOT contract ratification, NOT architecture ratification)
        ↓
engineering implementation
        ↓
technical review
        ↓
commit authorization  (separate)   →   push authorization  (separate)
```

**Also recommended, independently of the milestone track (C-5):**

- Complete or explicitly close out Document 58 §28 (CTO decision — §3.3).
- Numbered amendments via `docs/governance/Documentation_Governance.md`'s
  change-request chain for GH-1 (`00_README` index), GH-2 (`11_ADR_Index`),
  and GH-5 (`Feature_Parity_Tracker` Phase 4B note — now stale for both
  M12 and M13). GH-4 (M9 formal-closure conflict) and GH-6 (missing M10
  core completion record) remain CTO rulings, unblocking nothing active.

**The frontend track (C-3 Financial Visualization)** can proceed under
frontend governance independently of this sequence — it is not a Backend &
AI milestone and needs no artifact from this chain.

---

## 14. Acceptance Criteria

All of the following must be **true and on record** before C-1 (Filing
Analysis) may enter implementation. **This document authorizes none of
them.**

1. **This Post-M13 roadmap reconciliation is CTO-ratified** — its findings
   (§1–§8) adopted as the authoritative Post-M13 roadmap position, with C-1
   Filing Analysis carried forward as the **preferred / recommended
   candidate direction** for the subsequent governance phase. Ratification
   of this document is **not** a formal M14 implementation selection, **not**
   contract approval, **not** architecture approval, and **not**
   implementation, commit, or push authorization — each of those remains a
   separate, subsequent governance gate (items 2–5; §13). Ratification also
   does **not** pre-decide sequencing: the subsequent contract / architecture
   phase may determine that C-2 Structured Filing Extraction is a
   prerequisite before C-1 can proceed (§7).
2. **C-1 scope is frozen** — a CTO-ratified statement of what Filing
   Analysis is and is not, resolving §10's OPEN items and the §7
   chunk-vs-section question (or explicitly re-sequencing C-2 first).
3. **A C-1 API contract is CTO-ratified and frozen** — the response
   envelope(s), error semantics, ticker / filing identity, citation
   representation, on-demand vs persisted decision.
4. **A C-1 architecture decision pack is CTO-ratified and frozen** — the
   data-access pattern, whether RAG is introduced, the LangGraph
   change (if any) with its stop-and-CR treatment, the frontend integration
   pattern, and the explicit exclusions.
5. **A separate, subsequent CTO implementation-authorization decision is
   issued** — its own distinct governance act, scope-bound, after items 1–4,
   in the two-stage-plus convention Documents 33+55 (M12), 52 (M10 CI-gate),
   47 (hallucination detection), and 59+60 (M13) all followed. Commit
   authorization and push authorization remain **further** separate acts
   after technical review.

Item 1 is satisfied by the CTO ratification of 2026-08-30 (§16). Until items
2–5 are also satisfied, C-1's status is **RATIFIED PREFERRED ROADMAP
DIRECTION / FORMAL M14 SELECTION PENDING / CONTRACT NOT PROPOSED /
IMPLEMENTATION NOT AUTHORIZED**, and the Post-M13 finding stands: **no next
milestone is currently implementation-authorized.**

---

## 15. Document Provenance and Constraints Honoured

- Created: 2026-08-30. Sole new file:
  `docs/backend_engineering/62_Post_M13_Backend_AI_Roadmap_Reconciliation.md`.
- No source code, test, schema, configuration, or infrastructure file was
  modified.
- **Documents 58, 59, 60, and 61 were read, not modified.** Documents 59
  and 60 remain CTO-RATIFIED / FROZEN; Document 61 remains the durable
  reconciliation of the historical M13 implementation-authorization
  provenance and is unchanged.
- The M13 implementation commit `244ca5c` and the governance commit
  `f1c18c3` were inspected, not altered. No amend / rebase / merge / reset /
  stash / clean was performed. Nothing was staged, committed, or pushed.
- The known unrelated working-tree material
  (`web/features/workspace-home/ui/CompanySearch.test.tsx`; the untracked
  Document 58; `backend/evaluation/self_consistency/phase_h1_generalization_matrix/`;
  `FROZEN`, `Semantic`, `_)`, `or`, `structured`) was not staged, modified,
  renamed, or deleted.
- The repository's M13 publication state is synchronized
  (`HEAD` = `origin/main` = `f1c18c3`, `0 / 0`); the working tree is **not
  Git-clean** — it holds the known unrelated pre-existing changes and
  artifacts listed above (§1.7).
- No date, timestamp, decision number, or authorization wording was
  fabricated. No retroactive authorization is claimed. No existing
  governance decision is re-interpreted or duplicated — Document 61's
  authorization-provenance reconciliation is cited, not restated as a new
  interpretation.

---

## 16. CTO Ratification (2026-08-30)

Recorded from the CTO's ratification decision of 2026-08-30. §0–§15 above
are unchanged in substance; this section records the decision and the
status transition (`🟡 PROPOSED — CTO DECISION REQUIRED` → `🟢 CTO-RATIFIED`).

**Decision: RATIFIED.** The CTO ratified Document 62 as the authoritative
Post-M13 Backend & AI Roadmap Reconciliation. The ratified position,
recorded verbatim from the decision:

- M13 is COMPLETE / PUBLISHED.
- Document 61 is VERSION-CONTROLLED / PUBLISHED.
- C-1 Filing Analysis is the PREFERRED ROADMAP DIRECTION for subsequent
  governance work.
- C-1 is NOT formally selected as the M14 milestone.
- Formal M14 milestone selection remains a separate CTO decision.
- The chunk-vs-section architectural question remains OPEN.
- C-2 Structured Filing Extraction remains a possible technical sequencing
  prerequisite, subject to the future contract / architecture decision.
- Filing Q&A remains excluded from the bounded C-1 capability and is
  reserved for a later separately scoped capability.
- G8 remains BLOCKED / CARRIED FORWARD.
- H-1 remains CLOSED WITH GOVERNANCE FOLLOW-UP.
- No M14 contract is approved by this ratification.
- No M14 architecture is approved by this ratification.
- No implementation authorization is granted by this ratification.
- No commit authorization is granted by this ratification.
- No push authorization is granted by this ratification.

**Document 58.** This ratification does **not** retroactively ratify
Document 58. Document 58 remains an unratified historical / consumed roadmap
proposal unless separately resolved by a future explicit governance
decision (§3).

**Next governance action.** A separate CTO decision regarding **formal M14
milestone selection** (§13). **No engineering work is authorized from this
ratification alone.** Acceptance-criteria item 1 (§14) is now satisfied;
items 2–5 remain open.

**Recording note.** This section records a decision already issued by the
CTO; it creates no authorization of its own. Adding it changed only this
document, in the working tree — nothing was staged, committed, or pushed.
Committing Document 62 to version control is a separate, subsequently
CTO-authorized step (the model Document 61's governance commit `f1c18c3`
followed).

---

**NO IMPLEMENTATION PERFORMED. NO SOURCE, TEST, SCHEMA, CONFIGURATION, OR
INFRASTRUCTURE FILE CREATED OR MODIFIED. DOCUMENTS 58 / 59 / 60 / 61 NOT
MODIFIED. DOCUMENT 58 NOT RATIFIED. THE M13 IMPLEMENTATION COMMIT `244ca5c`
AND GOVERNANCE COMMIT `f1c18c3` NOT ALTERED. NO M14 CONTRACT CREATED. NO M14
ARCHITECTURE PACK CREATED. NO M14 MILESTONE FORMALLY SELECTED. NO
IMPLEMENTATION, COMMIT, OR PUSH AUTHORIZATION GRANTED. NO STAGE. NO COMMIT.
NO PUSH. NO MERGE / REBASE / RESET / STASH / CLEAN. THIS DOCUMENT IS
`🟢 CTO-RATIFIED (2026-08-30)` AS THE AUTHORITATIVE POST-M13 ROADMAP POSITION
AND AUTHORIZES NO ENGINEERING WORK (§16).**
