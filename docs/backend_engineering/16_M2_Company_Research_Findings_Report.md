# Backend Engineering — Company Research Backend Findings Report

**Status:** ✅ **COMPLETE**
**Milestone:** Backend Engineering M3 ("Company Research Backend"), as scoped by user direction · **Date:** 2026-08-05
**Governed by:** Backend Architecture `v1.0` (🔒 frozen) — Documents
[`01`](01_Backend_Architecture_Review.md), [`02`](02_API_Coverage_Audit.md), [`06`](06_Clean_Architecture_Migration_Plan.md)–[`11`](11_ADR_Index.md)
**Follows:** [`15_M2_Phase2_Learning_Implementation_Report.md`](15_M2_Phase2_Learning_Implementation_Report.md)
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main`, working tree atop commit `e5650be`

---

## 0. Scope correction — read this first

The milestone brief that opened this work item asked to **"implement the
complete backend that powers the Company Research experience,"** describing
it as if the capability does not yet exist. It does. Verified before any
code was touched:

- `POST /api/reports/generate`, `GET /api/reports/{id}/stream`,
  `GET /api/reports/{id}`, `POST /api/reports/{id}/cancel` are all marked
  `✅ Implemented` (or `🟡 Partial` for two specific, narrow, already-documented
  reasons — see below) in `02_API_Coverage_Audit.md §3`, which audited this
  exact pipeline during Milestone 1 — before Learning was even designed.
- `web/features/company-research/` consumes these routes successfully today
  (unlike Learning's pre-M2 state, where `integration/api.ts` carried an
  explicit "every call 404s, that's expected" docstring).
- This is the same 6-node LangGraph, retrieval pipeline, streaming
  transport, and job lifecycle that Milestone 2 Part A just cut over onto
  `JobLifecycle`/`EventBus` (`15 §0`) — extensively regression-tested in
  that same session.

**Raised to the user before implementation** (per this milestone's own "if
implementation requires changing an approved contract: STOP" instruction,
applied to the more fundamental issue of a false premise): confirmed via
`AskUserQuestion` that the actual deliverable is **closing the two concrete,
already-ratified/documented gaps against this existing pipeline** — `EQ-2`
(`00_README.md`'s ratification register: `POST /reports/rescore` must be
admin-gated) and `F-7` (`02 §5`: a schema-naming divergence between two
independently-declared frontend Zod schemas) — not a from-scratch
reimplementation. This report covers exactly that narrower, evidence-based
scope.

---

## 1. Company Research Implementation Report

### 1.1 Features implemented (this pass)

| Finding | Change |
|---|---|
| **EQ-2** — `POST /reports/rescore` had no authorization gate; any authenticated user could trigger a full-collection, cross-tenant scorecard rewrite (`02 §4.5`, `01 §7`) | Added `require_admin(user, message=...)` — the same helper `generate_report`'s custom-provider gate and `/llm/validate` already use, with its own non-LLM-specific message. One line, `server.py::rescore_reports`. |
| **F-7** — `02 §5` flagged that `company-research/integration/schemas.ts`'s `reportDocSchema` (requires `source_documents`) and `research-library/integration/schemas.ts`'s independently-declared same-named schema (narrower) "have diverged" | **Investigated, no backend change made** — see §1.3. This is not an active bug. |

### 1.2 Files changed

| File | What |
|---|---|
| `server.py` | `rescore_reports` now calls `require_admin` before any DB access |
| `infrastructure/security/authorization.py` | Module docstring corrected — it previously scoped this exact cutover to "Phase 6" as part of a larger EQ-2/EQ-3 bundle; updated to reflect EQ-2 landed now, standalone, while EQ-3 (owner-scoping all report reads — a 29-route behavior change) remains correctly deferred |
| `tests/unit/test_server_helpers.py` | +1 test: `rescore_reports` rejects a non-admin, calling the route function directly (hermetic — `require_admin` raises before any Mongo access, so no live DB is needed) |
| `tests/backend_test_iter2.py` | `test_rescore_reports` → `test_rescore_reports_requires_admin`; now asserts 403 for a regular authenticated session instead of asserting the previously-unauthorized 200 success |

### 1.3 F-7 investigation — why no backend change

Traced both schemas to their actual call sites:

- `company-research/integration/api.ts` calls `GET /reports/{id}` (single-report fetch) via `reportStatusResponseSchema` → `reportDocSchema`. `server.py`'s `get_report` returns the **full** document for this call — `source_documents` is genuinely present. No mismatch.
- `research-library/integration/schemas.ts` declares its **own**, independently-named `reportDocSchema` for the same single-fetch endpoint (deliberately, per that file's own header comment citing `02.2 AD-3`: "each feature validates its own trust boundary; features don't import each other's internals") — narrower fields, matching what that screen renders.
- `GET /reports` (the list endpoint `02 §5`'s finding is about) is called **only** by `research-library`, via a **third**, correctly-scoped schema (`reportListItemSchema`/`reportsListResponseSchema`) that does **not** require `source_documents`/`events` — matching exactly what `server.py`'s `list_reports` actually projects out.

No call site anywhere validates the list response against the stricter `reportDocSchema`. The audit's own text already said as much ("safe today"); this pass confirms it precisely rather than leaving it as an open question. **F-7 requires no backend fix** — the "divergence" is two independently-and-correctly-scoped frontend schemas sharing a name across feature boundaries, an intentional architectural choice (`AD-3`), not a contract bug. No frontend change was made either, consistent with this milestone's "no frontend workflow changes" constraint — there is nothing to change on either side.

### 1.4 ADRs / stable IDs referenced

`02 §4.5` (rescore finding), `02 §5` F-7 (schema finding); `00_README.md` ratification register (EQ-2 ruling: "Admin-gate (403 for non-admins)"); `01 §7` (EQ series origin); `10 §4.3`/ADR-024 (authorization model, `require_admin`); `02.2 AD-3` (per-feature schema independence, cited in `research-library`'s own schema file).

### 1.5 Remaining risks

| Risk | Assessment |
|---|---|
| `POST /reports/rescore` still has no pagination/cap — `db.reports.find({})` with no filter, one `update_one` per doc, synchronous in the request handler | Unchanged from `02 §4.5`'s finding. Severity is now much lower (only trusted admin accounts can trigger it, not any authenticated user), and EQ-2's ratified ruling was specifically "admin-gate," not "also add pagination" — adding a cap wasn't asked for and would be scope beyond the ratified decision. Flagged, not fixed, this pass. |
| `EQ-3` (owner-scope all report reads) remains open | Explicitly out of this pass's scope (a 29-route behavior change, correctly deferred to Migration Phase 6 per `06 §7`) |
| `4.1`'s `/companies/ensure` frontend-integration gap | Out of scope — a frontend consumption gap, not a backend defect, and this milestone permits no frontend changes |
| `4.4`'s unconsumed `DELETE /api/reports/{id}` | Out of scope — same reasoning |

### 1.6 Technical debt

None introduced. The one line added (`require_admin` call) follows an existing, tested pattern exactly.

---

## 2. API Compatibility Report

**No approved contract changed.** `POST /reports/rescore` has no frontend
consumer (`02 §4.5`: "no frontend consumer, no admin gate") — confirmed
again this pass by grepping `web/` for any call site; none exists. Admin-gating
a route nothing calls changes zero observable frontend behavior. `F-7`
resulted in no change on either side (§1.3).

| Check | Result |
|---|---|
| Route surface unchanged (33 → 37 stays 37, no new/removed/renamed routes) | ✅ `test_route_inventory.py` unmodified, still green |
| `POST /reports/rescore` response shape (`{"updated": int}`) unchanged for the one caller class that can now reach it (admins) | ✅ unchanged — only the gate is new |
| Anonymous caller still gets 401 (unchanged, auth check precedes the new admin check) | ✅ `test_anonymous_rescore_rejected` |
| Non-admin authenticated caller now gets 403 instead of 200 | ✅ Intentional, ratified (`EQ-2`) — this is the one deliberate, ratified behavior change in this pass, on a route with zero frontend consumers |

**Deviations from the frozen contract: none.**

---

## 3. Test Report

### 3.1 Added tests

| Count | File | What |
|---|---|---|
| 1 | `tests/unit/test_server_helpers.py` | `test_rescore_reports_rejects_a_non_admin_before_touching_the_db` — hermetic, calls the route function directly |
| 0 new / 1 modified | `tests/backend_test_iter2.py` | `test_rescore_reports` → `test_rescore_reports_requires_admin`, assertion flipped from 200 to 403 |

The admin-success path is deliberately **not** live-tested — it would require this server's real `ADMIN_EMAILS` account, and a shared dev database's test suite shouldn't be logging into a real admin identity. The hermetic test proves the gate calls `require_admin` correctly (already unit-tested in isolation in `test_authorization.py`); combined, these two facts (gate is called; gate works) cover the success path by composition without needing a live admin session.

### 3.2 Passing tests

```
Hermetic (pytest -m "not live"):  162 passed, 0 failed   (Phase L baseline: 161; +1 this pass)
Live — rescore-specific:            2 passed, 0 failed   (admin-gate rejection + anonymous rejection)
Live — full suite (pytest -m live): 39 passed, 4 failed  (same 4 pre-existing failures documented in `15 §3.3`, reproduced identically — see below)
```

### 3.3 Remaining gaps

The full live suite's 4 failures are **unchanged in identity** from `15 §3.3`
(`test_sse_stream`, `test_get_report`, `test_list_reports_contains_job`,
`test_samples_visible_to_any_authed_user`) — the same pre-existing dev-database
cache staleness and process-local job-registry properties already root-caused
in that report, reproduced identically in this session's own full-suite run.
Nothing in this pass's diff touches any code path those failures exercise.

One additional pre-existing, unrelated flake was newly observed this session
in isolation (not present in the full-suite run, consistent with `15`'s
established pattern of cache/data-scarcity-driven flakiness):
`backend_test_iter2.py::test_compare_ok` and its 3 sibling compare tests
depend on a `two_report_ids` fixture requiring ≥2 reports for a specific
ticker/query in the shared dev database; when run in isolation this dev
database had only 1. Not reproduced when the full suite ran (other files'
fixtures had already populated enough matching reports by then). Not caused
by this pass's changes — no code this pass touched is on that fixture's path.

---

## 4. Performance Report

No pipeline, retrieval, or streaming code was modified this pass — the
Company Research pipeline's performance characteristics are unchanged from
`15 §4`'s measurements (research graph: ~92s for one real run in that
session's environment, against a local, occasionally-unreliable LLM). No new
performance data was collected this pass since no performance-relevant code
changed; re-measuring would not reflect anything different from what `15`
already recorded honestly.

| Metric | Status |
|---|---|
| Retrieval latency | Unchanged from `15 §4` (retrieval code untouched) |
| First streaming event latency | Not measured (same gap noted in `15 §4`) |
| End-to-end execution time | Unchanged — see `15 §4`'s research-graph number |
| Cache utilization | Unchanged — the `(ticker, query)` report cache is untouched by this pass |
| External provider latency | Unchanged — no provider-facing code touched |

---

## 5. Production Readiness Assessment

### 5.1 Determination

> ## ✅ **Ready for CTO Review**

### 5.2 Evidence

| Claim | Evidence |
|---|---|
| The Company Research backend already fully powers the approved frontend experience | Established fact, not new work this pass — `02`'s audit (Milestone 1) and `15`'s Part A cutover (Milestone 2) both confirm this independently; reconfirmed by this pass's investigation (§0) |
| EQ-2 closed | `require_admin` gate live, hermetically tested (route-level, no DB touch) and live-tested (403 for non-admin, 401 for anonymous, both against the real running server) |
| F-7 resolved as a non-issue | Traced every call site; none combines the wrong schema with the wrong endpoint; documented precisely in §1.3 rather than left as an open question |
| No contract or frontend regression | §2 — zero deviations, zero frontend consumers affected |
| Tests pass | 162/162 hermetic (+1), rescore-specific live tests 2/2, full live suite at its established 39/43 baseline (4 pre-existing, unrelated, already root-caused in `15`) |

### 5.3 What remains, for a future pass (not blocking this one)

- `EQ-3` (owner-scope all report reads) — correctly out of scope, Phase 6 per `06 §7`.
- `4.1`/`4.4` (frontend integration gaps for `/companies/ensure` and `DELETE /reports/{id}`) — frontend-side work, out of scope for a backend-only, no-frontend-changes milestone.
- `4.5`'s unbounded-work concern on `/reports/rescore` — lower severity post-admin-gate; a cap/pagination would be a natural follow-up if this route sees real admin traffic, but wasn't part of the ratified EQ-2 decision.
- The 4 pre-existing live-suite failures inherited from `15` — dev-environment/data-state issues, not code defects; would clear in a fresh database.

---

*Companion documents:* [`02_API_Coverage_Audit.md`](02_API_Coverage_Audit.md) ·
[`15_M2_Phase2_Learning_Implementation_Report.md`](15_M2_Phase2_Learning_Implementation_Report.md) ·
index: [`00_README.md`](00_README.md)
