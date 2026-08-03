# API Coverage Audit & Parity Matrix

**Status:** Audit · **Milestone:** Backend Engineering M1 · **Date:** 2026-08-03
**Backend source of truth:** `backend/server.py` @ `7404b67`
**Frontend source of truth:** `web/features/*/integration/api.ts` + `schemas.ts`
**No contracts were modified.**

---

## 1. Method

Every route was enumerated from the `@api.<method>` decorators in `server.py`
(single `APIRouter`, prefix `/api`, no sub-routers). Every frontend call site
was enumerated by grepping `web/` for `/api/` string literals — all 30 hits
resolve to six `integration/api.ts` modules plus two doc comments, confirming
the 02.2 AD-1 rule (features are the only layer touching `apiFetch`) holds with
zero violations.

**Totals:** 31 implemented backend routes · 25 frontend call sites across 21
distinct routes · 4 frontend-declared routes with no backend · 10 backend
routes with no frontend consumer.

---

## 2. Status definitions

| Status | Meaning |
|---|---|
| ✅ **Implemented** | Backend route exists, a frontend module calls it, and the response shape satisfies the feature's Zod schema. |
| 🟡 **Partial** | Both sides exist, but the contract is under-specified, loosely validated, or the backend returns a superset/variant the schema does not fully model. |
| ❌ **Missing** | Frontend declares and calls the route; no backend implementation exists (404 at runtime). |
| ⚪ **Unconsumed** | Backend route exists and works; no `web/` consumer. Not dead — several are operational or reserved — but outside the migrated product surface. |
| 🔻 **Deprecation candidate** | Unconsumed *and* carries a correctness, security, or maintenance liability. Requires a decision. |

Note: **no route is formally deprecated today.** Nothing in `server.py` or
`docs/planning/05-API-Documentation.md` marks an endpoint as deprecated, and no
`Deprecation`/`Sunset` headers are emitted. The 🔻 rows are *candidates*, raised
as Engineering Questions, not decisions taken by this audit.

---

## 3. API Parity Matrix

### 3.1 Health & meta

| # | Method | Path | Backend | Frontend consumer | Status |
|---|---|---|---|---|---|
| 1 | GET | `/api/` | `server.py:182` | — | ⚪ Unconsumed |
| 2 | GET | `/api/health` | `server.py:187` | — | ⚪ Unconsumed — see Observability Audit §4 (D-7) |

### 3.2 Authentication & account (`account-setup`)

| # | Method | Path | Backend | Frontend consumer | Status |
|---|---|---|---|---|---|
| 3 | POST | `/api/auth/register` | `server.py:201` | `account-setup/integration/api.ts:38` | ✅ Implemented |
| 4 | POST | `/api/auth/login` | `server.py:215` | `…api.ts:31` | ✅ Implemented |
| 5 | POST | `/api/auth/logout` | `server.py:274` | `…api.ts:45` | ✅ Implemented |
| 6 | POST | `/api/auth/logout-all` | `server.py:303` | `…api.ts:49` | ✅ Implemented |
| 7 | GET | `/api/auth/me` | `server.py:285` | `…api.ts:27` | ✅ Implemented |
| 8 | DELETE | `/api/auth/me` | `server.py:312` | `…api.ts:74` | ✅ Implemented |
| 9 | POST | `/api/auth/password` | `server.py:290` | `…api.ts:67` | ✅ Implemented |
| 10 | POST | `/api/auth/forgot-password` | `server.py:236` | `…api.ts:53` | ✅ Implemented |
| 11 | POST | `/api/auth/reset-password` | `server.py:257` | `…api.ts:60` | ✅ Implemented |

Auth parity is **complete and exact** — every backend auth route has a
consumer, every consumer has a route, and `account-setup/integration/schemas.ts`
mirrors the Pydantic constraints field-for-field (`max_length=254` ↔
`.max(254)`, `min_length=8` ↔ `.min(8)`).

### 3.3 AI access

| # | Method | Path | Backend | Frontend consumer | Status |
|---|---|---|---|---|---|
| 12 | POST | `/api/llm/validate` | `server.py:809` | `account-setup/integration/llm-api.ts:9` | ✅ Implemented |

Contract note: the backend returns `200 {"valid": false, "error": "…"}` for an
invalid key rather than a 4xx (`server.py:835-837`) — deliberate, and
`validateLlmKeyResponseSchema` models it. Correct on both sides.

### 3.4 Ingest (`company-research`)

| # | Method | Path | Backend | Frontend consumer | Status |
|---|---|---|---|---|---|
| 13 | POST | `/api/ingest/text` | `server.py:337` | `company-research/integration/api.ts:25` | ✅ Implemented |
| 14 | POST | `/api/ingest/edgar` | `server.py:348` | `…api.ts:32` | ✅ Implemented |
| 15 | POST | `/api/ingest/samples` | `server.py:361` | `…api.ts:39` | ✅ Implemented |
| 16 | POST | `/api/ingest/audio` | `server.py:385` | — | ⚪ Unconsumed |
| 17 | POST | `/api/ingest/pdf` | `server.py:465` | — | ⚪ Unconsumed |

`/ingest/audio` and `/ingest/pdf` were live in the legacy CRA app's Ingest page.
`web/` has no ingest screen — `company-research` calls only the three JSON
ingest routes. Both are **functional and tested** (`backend_test_iter5.py`
covers audio validation paths); they are awaiting a UI, not rotting.
`docs/design/05_Screen_Inventory.md` does not define an Ingest screen, so this
gap is a **product scope question, not a backend gap**.

### 3.5 Companies & filings

| # | Method | Path | Backend | Frontend consumer | Status |
|---|---|---|---|---|---|
| 18 | GET | `/api/companies/search` | `server.py:521` | `workspace-home/integration/api.ts:8` | ✅ Implemented |
| 19 | GET | `/api/companies` | `server.py:514` | — | ⚪ Unconsumed |
| 20 | POST | `/api/companies/ensure` | `server.py:569` | — | 🟡 **Partial — see §4.1** |
| 21 | GET | `/api/companies/trending` | `server.py:1077` | — | ⚪ Unconsumed |
| 22 | GET | `/api/filings` | `server.py:659` | `company-research/integration/api.ts:59` | ✅ Implemented |
| 23 | GET | `/api/tickers` | `server.py:668` | — | ⚪ Unconsumed |

### 3.6 Reports

| # | Method | Path | Backend | Frontend consumer | Status |
|---|---|---|---|---|---|
| 24 | POST | `/api/reports/generate` | `server.py:840` | `company-research/…/api.ts:43` | ✅ Implemented |
| 25 | GET | `/api/reports/{id}/stream` | `server.py:970` | `company-research/…/api.ts:75` (SSE) | 🟡 **Partial — see §4.2** |
| 26 | GET | `/api/reports/{id}` | `server.py:1019` | `company-research/…/api.ts:50`, `research-library/…/api.ts:6` | 🟡 **Partial — see §4.3** |
| 27 | POST | `/api/reports/{id}/cancel` | `server.py:955` | `company-research/…/api.ts:54` | ✅ Implemented |
| 28 | GET | `/api/reports` | `server.py:1040` | `research-library/…/api.ts:14`, `comparison/…/api.ts:10`, `workspace-home/…/api.ts:13` | ✅ Implemented |
| 29 | POST | `/api/reports/compare` | `server.py:1135` | `comparison/integration/api.ts:15` | ✅ Implemented |
| 30 | DELETE | `/api/reports/{id}` | `server.py:1057` | — | ⚪ Unconsumed — **see §4.4** |
| 31 | POST | `/api/reports/rescore` | `server.py:1116` | — | 🔻 **Deprecation candidate — see §4.5** |

### 3.7 Learning (SCR-08) — frontend contract, no backend

| # | Method | Path | Backend | Frontend consumer | Status |
|---|---|---|---|---|---|
| 32 | POST | `/api/learning/explain` | — | `learning/integration/api.ts:21` | ❌ **Missing** |
| 33 | GET | `/api/learning/{id}/stream` | — | `learning/integration/api.ts:44` (SSE) | ❌ **Missing** |
| 34 | GET | `/api/learning/{id}` | — | `learning/integration/api.ts:28` | ❌ **Missing** |
| 35 | POST | `/api/learning/{id}/cancel` | — | `learning/integration/api.ts:32` | ❌ **Missing** |

These four are the **entire scope of the Learning backend build**. They are
approved, frozen frontend contracts
(`web/features/learning/integration/schemas.ts:3-27`), live-verified against
their honest-failure path in Milestone 3 Phase 8. Full design in
`03_Learning_Backend_Design.md`.

### 3.8 Rollup

| Status | Count | Routes |
|---|---|---|
| ✅ Implemented | 17 | auth ×9, llm/validate, ingest ×3, companies/search, filings, reports/generate, reports/{id}/cancel, reports, reports/compare *(19 rows; 17 distinct after the 2 multi-consumer rows are counted once)* |
| 🟡 Partial | 3 | `/companies/ensure`, `/reports/{id}/stream`, `/reports/{id}` |
| ❌ Missing | 4 | all `/learning/*` |
| ⚪ Unconsumed | 9 | `/`, `/health`, `/ingest/audio`, `/ingest/pdf`, `/companies`, `/companies/trending`, `/tickers`, `/reports/{id}` (DELETE) |
| 🔻 Deprecation candidate | 1 | `/reports/rescore` |

---

## 4. Partial & candidate detail

### 4.1 `POST /api/companies/ensure` — 🟡 Partial

Fully implemented server-side and the single richest data-acquisition path in
the product (EDGAR → BSE → yfinance cascade, `server.py:569-656`), but **no
`web/` module calls it**. `workspace-home` searches companies and
`company-research` generates reports, so a user who picks a company with no
ingested filings hits `POST /reports/generate`'s 400 ("No filings ingested
for X") rather than the ensure-then-generate flow the legacy app used.

Classified Partial rather than Unconsumed because the frontend *does* implement
the user journey this route serves (J-01 company selection), just without
calling it — a genuine integration gap, not an orphaned endpoint.

Response shape also varies by branch: it returns one of five differently-keyed
objects (`already_ingested`, `ingested_from_edgar`, `ingested_from_bse`,
`ingested_from_yfinance`, or 404). Any future consumer needs a union schema.

### 4.2 `GET /api/reports/{id}/stream` — 🟡 Partial

Works, and `company-research` consumes it correctly. Partial for two reasons:

1. **Single-consumer queue defect** (Architecture Review D-1): two concurrent
   readers on one job split the event stream between them. Not a contract
   mismatch — a delivery-guarantee gap the contract silently assumes away.
2. **Framing is undocumented in governance.**
   `docs/planning/05-API-Documentation.md:63-70` documents this stream as
   `event: pipeline` with a `{"stage":…, "msg":…}` payload and a terminal
   `event: done`. The implementation emits **unnamed `data:` messages** with
   `{"node":…, "status":…, "message":…, "ts":…}` and a terminal `event: end`
   (`server.py:987-1006`). `web/lib/api/sse-client.ts` is written against the
   *implementation*, correctly. The API doc is wrong, not the code — flagged in
   Architecture Review D-11.

### 4.3 `GET /api/reports/{id}` — 🟡 Partial

Returns three structurally different bodies depending on job state
(`server.py:1019-1037`): completed → `{status, id, report}`; in-flight
in-memory → `{status, id, events}`; in-flight after restart → same from the
Mongo mirror. The frontend models this as one loose object with everything
optional and `events: z.array(z.record(z.string(), z.unknown()))` —
i.e. **event payloads cross the trust boundary unvalidated**, explicitly noted
in `company-research/integration/schemas.ts:139-150`.

Also carries the unscoped-read posture (D-5): any authenticated caller holding
a report UUID reads it, including another tenant's.

### 4.4 `DELETE /api/reports/{id}` — ⚪ Unconsumed, but *behaviorally required*

The only correctly user-scoped write in the reports surface
(`server.py:1065`), with three dedicated tests
(`test_delete_report_and_verify_removal`, `test_other_user_cannot_delete_my_report`,
`test_cannot_delete_sample`). `research-library` renders saved reports but
offers no delete action, so the capability exists server-side with no way to
reach it. Recommend wiring rather than deprecating — deletion is the one
report operation with no alternative path.

### 4.5 `POST /api/reports/rescore` — 🔻 Deprecation candidate

`db.reports.find({})` with no filter, then one `update_one` per document
(`server.py:1122-1127`). Any authenticated user can trigger a full-collection
rewrite across every tenant's reports. There is no frontend consumer, no admin
gate, and no pagination or cap.

Two liabilities: **cross-tenant write** and **unbounded work per request**
(an O(collection) synchronous loop inside a request handler).

→ **Engineering Question EQ-2** ([`01_Backend_Architecture_Review.md`](01_Backend_Architecture_Review.md) §7). Recommend deletion;
if kept, gate with the existing `auth.is_admin` the way `/llm/validate` and
`/reports/generate` already gate the custom provider (`server.py:819`, `:849`).

---

## 5. Contract-fidelity findings

Checks of frontend Zod schemas against backend Pydantic models / response
literals. **These are observations; no contract was changed.**

| ID | Finding | Where |
|---|---|---|
| **F-1** | **Learning's response envelope intentionally differs from Reports'.** `POST /reports/generate` → `{job_id, cached?}`; `POST /api/learning/explain` → `{id}`. Likewise cancel: `{job_id, status, note?}` vs `{id, status}`. The Learning backend must emit **`id`**, not `job_id` — a copy-paste of the reports handler would fail the frontend's schema validation at the trust boundary. | `schemas.ts:127-136` vs `learning/…/schemas.ts:41-43, 74-77` |
| **F-2** | **Learning declares no `cached` field.** `explainResponseSchema` is `{id}` only. Zod strips unknown keys, so an extra field would not *break* the parse — but there is no approved surface for a cache-hit signal, so v1 must not depend on one. | `learning/…/schemas.ts:41` |
| **F-3** | **Learning's SSE event schema has no `ts`.** Reports' `streamEventSchema` includes `ts`; Learning's is `{node, status, message?, explanation?}`. Emitting `ts` is harmless (stripped), but the UI cannot order or display it. | `learning/…/schemas.ts:79-85` |
| **F-4** | **Node vocabulary is fixed by the UI.** `deriveStage` branches on exactly `pipeline` (status `start`/`ok`/`warn`/`error`), `retriever`, `explainer`, `final`; anything else falls through to `"thinking"` and the UI never leaves the thinking state. This is the binding constraint on the Learning graph's node names. | `learning/internal/streamStages.ts:25-36` |
| **F-5** | **`explanationDocSchema` requires `source_documents`** (non-optional array) and `explanation` (non-optional string). A grounded-but-sourceless response fails validation. Law 3 is enforced by the schema, not just by prompt. | `learning/…/schemas.ts:56-64` |
| **F-6** | **Nothing verifies any of this.** There is no contract test in either repo half. FastAPI already serves `/openapi.json` for free; no snapshot or schema-diff test consumes it. Highest-value, lowest-cost gap in the whole audit — see `05_Testing_Audit.md` §4. | — |
| **F-7** | **`GET /reports` strips `source_documents` and `events`** from list responses (`server.py:1050`) but `reportDocSchema` marks `source_documents` **required**. `research-library`/`comparison` use a separate list schema, so this is safe today — but the two schemas describing "a report" have diverged, and only one is enforced per call site. | `server.py:1050` vs `company-research/…/schemas.ts:103` |

---

## 6. Summary

- **Auth, AI access, and the core report lifecycle are at full parity.**
- **The only Missing surface is Learning** — 4 routes, fully specified by an
  approved frozen contract, designed in `03_Learning_Backend_Design.md`.
- **Three Partial routes** are partial for delivery-guarantee and
  response-polymorphism reasons, not for missing functionality.
- **Nine unconsumed routes** split into three groups: operational (`/`,
  `/health`), awaiting a UI that the frozen Screen Inventory does not define
  (`/ingest/audio`, `/ingest/pdf`, `/companies`, `/tickers`,
  `/companies/trending`), and one that should be wired
  (`DELETE /reports/{id}`).
- **One route should be gated or removed** (`/reports/rescore`, EQ-2).
- **Zero contract tests exist.** Every parity claim in this document was
  established by reading code, and nothing prevents it from silently going
  stale tomorrow.

---

*Cross-references: `01_Backend_Architecture_Review.md` (D-1, D-2, D-5, D-11),
`03_Learning_Backend_Design.md` (F-1…F-5), `05_Testing_Audit.md` (F-6).*
