# Backend Engineering Milestone 4 — Backend Capability & Roadmap Reconciliation

**Status:** ✅ **COMPLETE** (research/audit only — no code changed, per this milestone's own constraint)
**Milestone:** Backend Engineering M4 · **Date:** 2026-08-05
**Governed by:** Backend Architecture `v1.0` (🔒 frozen); Product Roadmap `v1.0.0` (🧊 frozen,
[`03_Feature_Roadmap.md`](../master-plan/03_Feature_Roadmap.md)); Screen Inventory `v0.1.1` (🧊 frozen,
[`05_Screen_Inventory.md`](../design/05_Screen_Inventory.md))
**Follows:** [`16_M2_Company_Research_Findings_Report.md`](16_M2_Company_Research_Findings_Report.md)
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main`, working tree atop commit `e5650be`

---

## 0. Method

Every classification below is traced to one of the five evidence sources this
milestone specifies, not asserted. Where a source doc is silent or itself
stale, that is stated explicitly rather than papered over.

| Source | Documents actually read this pass |
|---|---|
| Frozen Product Roadmap | `master-plan/03_Feature_Roadmap.md` (MVP v1.0 → V1.1 → V2.0 → Future Vision) |
| Frozen Backend Architecture v1.0 | `06`–`11`, plus audits `01`/`02`/`04`/`05` for unresolved findings |
| Frozen ADRs | `11_ADR_Index.md` (28 ADRs + "Decisions deliberately deferred" table) |
| Approved frontend implementation | `governance/Feature_Parity_Tracker.md`, `design/05_Screen_Inventory.md` (SCR-01…SCR-11), `governance/change_requests/00_Change_Request_Register.md`, direct read of `web/features/*` (6 feature dirs: `account-setup`, `workspace-home`, `company-research`, `comparison`, `research-library`, `learning`) |
| Current backend repository | `server.py` (37 routes), `agents/`, `domain/`, `application/`, `infrastructure/`, `app/` directory contents; `agents/schemas.py`'s actual extraction fields; live + hermetic test run (162/162 hermetic, 39/43 live — this session) |

**One correction surfaced immediately:** `Feature_Parity_Tracker.md §6` still describes Learning's
backend as "zero capability exists... every real call 404s" — that was true when Milestone 3
(Frontend Engineering) closed on 2026-08-03, but Milestone 2 (this same engineering track,
2026-08-04/05) implemented it in full. The tracker itself is stale on this one point;
treated as fixed throughout this report, evidenced by `15_M2_Phase2_Learning_Implementation_Report.md`
and this session's own passing `backend_test_iter7.py` (9/9).

---

## 1. Backend Capability Matrix

Scoped to the frozen MVP (Version 1.0) roadmap sections, since that is the
approved, currently-buildable baseline — V1.1/V2.0/Future Vision items are
listed once at the end as **Not Required** with the roadmap's own reason,
not re-litigated bullet-by-bullet.

| Roadmap Capability (MVP v1.0) | Classification | Evidence |
|---|---|---|
| **Authentication & AI Setup** | | |
| User Registration, Login, Profile | ✅ Fully Implemented | `server.py` `/auth/register`, `/auth/login`, `/auth/me`; `agents/auth.py` |
| Social Authentication (Google) | ❌ **Missing** | No OAuth code anywhere in `agents/auth.py` or `requirements.txt`. **Conflicts with a standing constraint**: `CLAUDE.md` explicitly says "Do not add JWT, OAuth, or cloud-SDK auth dependencies" for this stdlib-only auth system, while the frozen roadmap lists "Social Authentication (Google)" as MVP scope. Neither doc defers to the other — this is a genuine open conflict between two frozen documents, not a simple backlog item. See §4 (Critical finding) and §6. |
| API Key Management, BYOK Support, Managed AI Support, AI Setup Validation | ✅ Fully Implemented | `POST /llm/validate`, `agents/llm.py`'s multi-provider dispatch, per-request context (`set_llm_context`) |
| Guided Onboarding | N/A (frontend-only) | No backend capability implied beyond AI Setup Validation above |
| **Research Workspace** | | |
| Company Search, Recent Research, Search Bar | ✅ Fully Implemented | `GET /companies/search`, `GET /reports` (list) — both confirmed consumed by `workspace-home` |
| Quick Actions | N/A (frontend-only) | No distinct backend capability implied |
| **Company Research** | | |
| Company Search, Company Overview, Business Summary | ✅ Fully Implemented | `POST /reports/generate` → synthesizer's `draft_report` |
| Financial Highlights, Key Metrics | 🟡 Partially Implemented | `agents/schemas.py::FinancialsSchema` extracts 7 fields only (`revenue`, `revenue_yoy`, `eps`, `net_income`, `operating_margin`, `free_cash_flow`, `guidance`) — single-period, LLM-extracted-from-text, not a structured financial-statement source. Sufficient for the frontend's current `MetricStat` rendering (per `Feature_Parity_Tracker.md §3`'s Phase 4B note), insufficient for "Key Metrics" as a distinct, richer capability. |
| Period-over-Period Performance, "What Changed Since Last Review" | 🟡 Partially Implemented | Achievable via `context_report_id` follow-up (prior brief injected into the next synthesis) — a general-purpose mechanism, not a dedicated period-comparison capability |
| **Financial Statements** (Income/Balance/Cash Flow, Quarterly/Annual) | ❌ **Missing** | Confirmed by direct code read: `agents/ingest.py` never calls `yfinance`'s `.financials`/`.balance_sheet`/`.cashflow` (only `.info`); no statement-shaped data is persisted anywhere. Independently confirmed in `Feature_Parity_Tracker.md §3`'s Phase 4B note ("no backend data source exists for either"). |
| **AI Financial Copilot** | | |
| Company Q&A, Filing Q&A | 🟡 Partially Implemented | Same `context_report_id` re-run mechanism as above — a real capability, but one-shot-per-question (re-runs the whole pipeline), not true multi-turn conversational Q&A |
| Financial Explanations | ✅ Fully Implemented | Learning backend (`POST /api/learning/explain` + graph), built M2 |
| Earnings Analysis, Revenue Analysis, Business Model Explanation | 🟡 Partially Implemented | Covered generically inside `draft_report`'s free-form prose; no dedicated structured output for any of the three |
| Risk Identification | ✅ Fully Implemented | `ToneSchema.key_risks` (`tone_risk_node`) |
| **Trusted AI** | | |
| Grounded AI, Explainable AI, Source Traceability, Citation Inspection | ✅ Fully Implemented | `[n]` citation convention end-to-end (reports + Learning), `source_documents` on every output, Law 3 enforced by `fact_checker_node` (reports) and citation post-processing (Learning) |
| **SEC Filing Analysis** | | |
| 10-K/10-Q ingestion, Filing Summaries | ✅ Fully Implemented | `POST /ingest/edgar`, EDGAR→BSE→yfinance cascade in `agents/ingest.py` |
| Risk Factors, Management Discussion, Important Changes (as **distinct, structured** outputs) | ❌ **Missing** | No dedicated extraction for these specific 10-K/10-Q sections — subsumed generically into `draft_report`'s prose and `ToneSchema.key_risks`, not separately identifiable |
| **Company Comparison** | | |
| Compare Multiple Companies, Financial Ratios/Revenue/Margin/Growth Comparison | ✅ Fully Implemented | `POST /reports/compare` (2-4 reports, pure lookup) |
| AI Company Comparison (explanation of differences) | ❌ **Missing** | `compare_reports` never calls an LLM — confirmed by direct code read. Also named as a required AI feature in `05_Screen_Inventory.md`'s SCR-07 definition ("AI Features Used: AI Company Comparison (explanation of differences)") — this is a **frozen-screen-spec gap**, not just a roadmap wishlist item. |
| **Learning Mode** | | |
| Learner-Level Explanations, Concepts Explained in Context | ✅ Fully Implemented | M2 Phase L |
| Guided Concept Exploration | 🟡 Partially Implemented | The `context_report_id`/follow-up mechanism enables continuation, but there is no dedicated "guided" multi-step flow — each explanation is an independent one-shot call |
| Worked Analysis Examples, Interpretation Self-Check | ❌ **Missing** | No backend capability corresponds to either; not present in the frozen `03_Learning_Backend_Design.md` contract either — genuinely not built on either side |
| **Research Reports** | | |
| Research Report Generation, Grounded Conclusions, Preserved Reasoning, Source-Backed Insights | ✅ Fully Implemented | `POST /reports/generate` + full pipeline |
| Exportable Research Artifacts | N/A (frontend-only) | `research-library`'s client-side markdown export needs no backend endpoint (confirmed working, `Feature_Parity_Tracker.md §3` Phase 5) |
| **Data Visualization** | | |
| Revenue/Profit/Margin/Growth Charts | ❌ **Missing** | Zero chart-ready backend data source — blocked on the same gap as Financial Statements above (a single-period, 7-field extraction cannot power a time-series chart). Frontend side also unbuilt (confirmed: `recharts` not installed in `web/`, per `CLAUDE.md`'s own "neither is installed... add them when one is [built]" note). |
| **Research Sessions** | | |
| Saved Reasoning, Saved Sources, Research History | ✅ Fully Implemented | Every report persists `draft_report`/events (reasoning) and `source_documents` (sources); `GET /reports` serves history |
| Resume Research | 🟡 Partially Implemented | Achievable via `context_report_id`, not a dedicated "resume" capability |
| Durable Research Sessions (as a **distinct session/conversation entity**) | ❌ **Missing** | No session concept beyond an individual report — confirmed repeatedly in `Feature_Parity_Tracker.md §5` ("no session concept beyond a report") |
| **V1.1 / V2.0 / Future Vision** (Watchlists, News Intelligence, Earnings Center, Advanced Reports, Valuation Tools, Portfolio, Screeners, AI Research Agents, Collaboration, Market Intelligence, Alternative Data, Predictive Intelligence, Global Markets, Enterprise) | ⚪ **Not Required** | Explicitly out of MVP scope per the roadmap's own version boundaries; Portfolio and News additionally have resolved Change Requests (`CR-SCOPE-001`→V2.0, `CR-SCOPE-002`→V1.1) confirming deferral, not oversight |
| `POST /reports/rescore` | 🔻 **Deprecated candidate** | No frontend consumer (confirmed again this session); admin-gated as of M3 (`16`) but still an unbounded, cross-tenant-capable operation nothing in the product needs. Recommend deletion in a future pass, per the original `01 D-2`/`02 §4.5` recommendation. |

---

## 2. Frontend ↔ Backend Feature Parity Matrix

| Frontend feature (`web/features/`) | Frontend status | Backend status | API compatibility | Remaining work | Blocking issues |
|---|---|---|---|---|---|
| `account-setup` | In Progress (Migrated: Signup, AI Access Setup) | Fully Implemented | ✅ Compatible | Google OAuth (see §1, §4 — Critical) | The OAuth/CLAUDE.md conflict — needs a product/CTO decision, not engineering effort alone |
| `workspace-home` | In Progress | Fully Implemented | ✅ Compatible | None backend-side | None |
| `company-research` | In Progress (all 5 sections enabled, none Migrated) | Mostly Fully Implemented, 2 real gaps | ✅ Compatible for what's built | Financial Statements + Filing content-reading pane both need new backend data sources (§1) before the frontend's existing honest placeholders can become real content | Both are **backend-blocked**, not frontend-blocked — frontend already built the progressive-enhancement placeholder per its own Phase 4B resolution |
| `comparison` | In Progress | Fully Implemented for table compare; Missing for AI explanation | ✅ Compatible | AI-generated comparison explanation (§1) — an LLM call inside `compare_reports`, new prompt, no contract change needed (`POST /reports/compare`'s response can add a field additively) | None structural — this is a scoped, buildable gap |
| `research-library` | In Progress | Fully Implemented for Reports; Missing for Sessions/Saved Exports/History-as-distinct-entities | ✅ Compatible for what's built | Durable Research Sessions as a first-class entity (§1) — a genuine new backend capability (not just a route), would need a new collection + ADR per this milestone's own "new architectural decision requires an ADR" rule | Needs an ADR before implementation — flagged, not decided here |
| `learning` | In Progress | ✅ Fully Implemented (M2, this session's predecessor) | ✅ Compatible, contract-tested | Worked Analysis Examples, Interpretation Self-Check (§1) — genuinely unbuilt on both sides, not currently part of the frozen `03` contract | Would need a contract amendment (EQ) before backend work, since `03`'s frozen contract has no field for either |

**Screen coverage note:** `05_Screen_Inventory.md` defines **SCR-05 — Search Results** as a
distinct MVP screen with its own dependencies. No `web/features/` directory or route
corresponds to it as a separate destination — `workspace-home`'s inline debounced search
appears to have absorbed this responsibility rather than a dedicated results screen being
built. The backend capability it would need (`GET /companies/search`) already exists and
works, so **this is not a backend gap** — flagged here because neither the Feature Parity
Tracker nor any Screen-Inventory-conformance doc explicitly reconciles SCR-05 against what
was actually built, and this reconciliation task's own evidence-only mandate means it should
be named rather than silently absorbed into "workspace-home, done."

---

## 3. API Contract Validation

All 37 live routes, cross-checked against `02_API_Coverage_Audit.md`'s original 31-route
matrix (Milestone 1), the 2 additive Phase 1 routes, and the 4 additive Learning routes
(Milestone 2). **No contract was modified this pass** — this is inventory only.

| Category | Count | Routes |
|---|---|---|
| ✅ Compatible | 33 | All `/auth/*` (9), `/ingest/*` (5), `/companies*` (4), `/filings`, `/tickers`, `/llm/validate`, `/reports/generate`, `/reports/{id}/cancel`, `/reports/{id}/stream`, `/reports/{id}`, `/reports` (list), `DELETE /reports/{id}`, `/reports/compare`, `/health`, `/health/ready`, `/metrics`, all 4 `/learning/*` routes |
| 🟡 Partially compatible | 2 | `GET /reports/{id}/stream` — works, framing correct, but inherits the pre-existing process-local job-registry limitation on a restarted process's stale cache hits (`15 §1.5`, not a contract defect); `GET /reports/{id}` — returns 3 structurally different bodies by design (`02 §4.3`), frontend already models this loosely, not a bug |
| 🟠 Divergent | 0 | None found |
| ⚪ Missing (documented, not contract-breaking) | 1 | `POST /companies/ensure` — fully implemented server-side, zero frontend consumer (`02 §4.1`, unchanged since Milestone 1) |

**Zero divergent contracts.** The one "Missing" entry is a route that exists and works but
has no caller — an integration gap, not an implementation gap, and explicitly out of scope
for a backend-only milestone with "no frontend changes" as a constraint.

---

## 4. Remaining Engineering Findings

Consolidated from `01` (D-series), `04` (O-series), `05` (T-series), cross-checked against
what M2/M3 actually closed. Status legend: ✅ Closed this track · 🟡 Partially addressed ·
❌ Still open.

### Critical

| ID | Finding | Status | Note |
|---|---|---|---|
| — | **Google Social Authentication is frozen-roadmap MVP scope, but `CLAUDE.md` forbids adding an OAuth dependency to this stdlib-only auth system.** Neither document defers to the other. | ❌ Open — **not an engineering gap, a document conflict** | Building it would violate `CLAUDE.md`; not building it leaves a frozen MVP roadmap item permanently unimplemented. Needs a product/CTO ruling (new ADR or roadmap amendment), not code. See §6. |

### High

| ID | Finding | Status | Note |
|---|---|---|---|
| `D-5`/`EQ-3` | Report reads unscoped (IDOR-by-obscurity) — any authenticated caller with a report UUID can read it | ❌ Open | Explicitly deferred to Migration Phase 6 (`06 §7`) — a 29-route behavior change needing its own reviewable PR, not a side effect of any prior milestone |
| `T-8` | Concurrent-consumer stream splitting | ✅ Closed | Fixed by M2's `EventBus` cutover; port-conformance tests prove 2 concurrent subscribers each see every event (Phase 1) |
| `T-9` | Replay-on-reconnect (`to_skip` logic) | ✅ Closed (differently) | The fragile code T-9 was about no longer exists — deleted in M2's cutover, replaced by `EventBus`'s atomic replay-then-subscribe, which the port-conformance suite covers |

### Medium

| ID | Finding | Status | Note |
|---|---|---|---|
| `D-4` | No unit-testable seam — `server.py` still does import-time env+Mongo construction | ❌ Open | `Settings`/`Container` exist (Phase 1) but `server.py` itself was never refactored into an app factory; Migration Phase 1's `create_app()` AD-1 is not fully realized |
| `D-7`/`O-12` | `/health` does two unindexed full-collection counts per call | ❌ Open | Untouched by any milestone so far |
| `O-2` | Pipeline trace events never reach the structured logs (only EventBus + Mongo) | ❌ Open | One `logger.info` inside `push()` would close this — still not done |
| `O-3` | Unstructured, non-JSON logs | ❌ Open | Blocking for any hosted log aggregation |
| `O-8` | No per-node timing in the trace | ❌ Open | Same gap this session's own `15 §1.4` "Remaining technical debt" flagged for Learning specifically — applies to reports too |
| `O-9` | Trace not cross-job queryable | ❌ Open | |
| `O-10` | External provider calls (EDGAR/BSE/yfinance/Resend) untraced | ❌ Open | |
| `O-13` | `/health`'s `llm_key_configured` only checks Gemini | ❌ Open | |
| `T-1` | Non-hermetic live suite | 🟡 Mitigated | CI (`.github/workflows/backend-ci.yml`) runs `-m "not live"` only — hermetic in CI; the live suite itself still needs real infra by design, unchanged |
| `T-4` | Failure paths largely untested | 🟡 Partially addressed | Some new failure-path tests landed across M2/M3 (deadline enforcement, citation rejection, admin gate); the original gap list (429 on `MAX_ACTIVE_JOBS`, truncation-guard 422) not exhaustively covered |
| `T-6` | No restart-recovery test | ❌ Open | Restart-recovery was verified **manually** in M2 (the startup sweep observably marked 9 orphaned jobs `failed` mid-session) but never captured as an automated test — explicitly flagged as a gap in `15 §1.5` |
| `T-11` | Streaming an already-finished job | ❌ Open | No explicit test for reconnecting to a terminal job's stream (reports or Learning) |
| `T-12` | Unknown/other-user job id on stream | 🟡 Partially addressed | Covered for Learning (`test_learning_reads_are_scoped_to_the_owner`); reports intentionally stay unscoped (`D-5`), so "another user's job" doesn't apply there by design, but "authenticated + nonexistent id" isn't explicitly tested for reports |
| `T-13` | Cancel-mid-stream event assertion | 🟡 Partially addressed | Learning's `test_cancel_stops_an_in_flight_job` verifies terminal status via `GET`, not the `pipeline/warn` event's presence in the stream itself |
| `T-14` | Strict event-ordering assertion | 🟡 Partially addressed | Live tests check the *set* of required node events appears; none strictly asserts `pipeline/start` is first and `pipeline/ok`/`event: end` is last, every time |

### Low

| ID | Finding | Status | Note |
|---|---|---|---|
| `D-9` | Chunk re-ingest never dedupes | Deliberate (`ponytail:`) | Leave — documented, upgrade path stated |
| `D-10` | Numeric-only fact-checking (qualitative fabrication undetected) | Deliberate (`ponytail:`) | Leave for reports; Learning's citation-validation is a different, narrower mitigation for a different content type, already built |
| `O-4` | Log level hardcoded | 🟡 Partial | `Settings.log_level` field exists (Phase 1) but is not confirmed wired into the actual logging configuration — needs a direct check, not verified this pass |
| `O-5` | No access-log correlation | ❌ Open | |
| `O-6` | No log rotation | ❌ Open | |
| `O-11` | Retry loop invisible | 🟡 Partially addressed | `llm_calls_total{outcome="error"}` (M2) gives aggregate retry visibility via Prometheus; per-attempt log lines still absent |
| `O-15` | `/health`'s `"ok": true` is a literal, never `false` | ❌ Open | |
| `T-7` | `/ingest/pdf` has no test | ❌ Open | |
| `T-10` | Keepalive-after-120s-idle test | ❌ Open | Explicitly low priority (slow to test) in the original audit too |

**Everything marked ✅ Closed above is independently verified** — either by this session's
own passing test runs (T-8, T-9) or by direct citation to the M2/M3 reports that fixed them
(`D-1`, `D-2`/`EQ-2`, `D-3`, `D-6`, `D-8`, `O-1`, `O-14`, `T-2`, `T-3`, `T-5` — not re-tabled
above since they're fully closed with no residual note).

---

## 5. Technical Debt Register

| Item | Impact | Risk | Recommended Resolution | Estimated Effort |
|---|---|---|---|---|
| `server.py` not yet an app factory (`D-4`) | Every hermetic test still imports the whole module; slows test isolation work | Low (mitigated by the parallel hermetic suite) | Extract `create_app()` per `06 AD-1`; Migration Phase 1's stated-but-incomplete deliverable | Medium (touches every route's import path) |
| `EQ-3` / `D-5` — reports unscoped reads | Any authenticated caller can read any tenant's report by UUID | Medium (accepted risk today, explicitly recorded in-code) | Scope `GET /reports/{id}`, `/stream`, `/cancel`, `list_reports`, `compare_reports`, `delete_report` to owner+sample, matching Learning's already-shipped pattern | Medium-High — 5+ routes, needs its own reviewable PR per `06 §7 Ph6`'s own scope note |
| Observability gaps (`O-2/3/5/6/8/9/10/13/15`) | Low day-to-day impact locally; would block a real hosted deployment's incident response | Medium (invisible until an incident happens) | Batch as one Observability Hardening pass: JSON logging, pipeline-trace-to-log bridge, per-node span timing (needs the node-level instrumentation Phase 3's port injection was supposed to enable), external-call tracing | Medium — mostly additive, no architecture change |
| `/health` full-collection counts + Gemini-only key check (`D-7`/`O-12`/`O-13`/`O-15`) | Self-inflicted load on every probe interval; misleading status for non-Gemini deployments | Low-Medium | `estimated_document_count()` instead of `count_documents({})`; check the active provider's actual key, not hardcoded Gemini; derive `"ok"` from a real check | Small — a few hours |
| Untested restart-recovery, cancel-mid-stream event, stream-of-finished-job, strict event-ordering (`T-6/11/13/14`) | Real behavior is correct (manually verified for T-6; correct by construction for the others) but unguarded against regression | Low today, grows with each future change to the streaming/job code | Add the 4 missing test cases — all are extensions of test infrastructure that already exists (`EventBus`/`JobLifecycle` port-conformance suites, `backend_test_iter7.py`'s live-lifecycle pattern) | Small — no new infrastructure needed, just test cases |
| `POST /reports/rescore` still unbounded + zero consumers | Wasted endpoint surface; O(collection) synchronous work if ever triggered | Low (now admin-only) | Delete, per the original `01 D-2` recommendation now that admin-gating (this session) removed the urgency | Trivial |
| Real-Redis verification (`JOB_BACKEND=redis`) | Both graphs share untested-against-real-Redis adapters | Low-Medium (only matters at the point of a Redis-backed deployment) | A 30-minute smoke test against a real Redis instance, inherited unresolved from Phase 1 through M2 (`15 §5.1`'s "one condition") | Small |
| Financial Statements / Data Visualization backend gap | Blocks 2 frozen MVP roadmap capabilities and 2 frontend honest-placeholder sections from becoming real | Medium (product-visible gap, not a defect) | New yfinance-based extraction (`.financials`/`.balance_sheet`/`.cashflow`) + a new schema/collection; likely warrants its own ADR given it's new data modeling, not a bug fix | Medium-Large |
| AI Comparison explanation, Learning self-check/worked-examples | Named in frozen screen specs / roadmap, zero backend | Low (contained, optional features) | Comparison: additive LLM call, no contract break, small. Learning: needs a contract amendment (EQ) first, since `03`'s frozen schema has no field for either | Small (Comparison) / Medium (Learning, contract-gated) |
| Google OAuth vs. `CLAUDE.md`'s stdlib-only constraint | Blocks a frozen MVP roadmap item indefinitely until resolved | **Not resolvable by engineering effort alone** | Raise as a formal product/CTO decision: either amend the roadmap (drop Social Auth from MVP) or amend `CLAUDE.md`'s constraint (permit one OAuth dependency) | N/A — decision, not implementation |

---

## 6. Recommended Backend Roadmap

Ordered by dependency, not by size — Milestone 5 unblocks the most other work per
effort spent.

### Milestone 5 — Report-Read Authorization Cutover (EQ-3)

- **Objective:** Close the one remaining unscoped-read security gap, matching the pattern Learning already shipped.
- **Scope:** `GET /reports/{id}`, `/stream`, `POST .../cancel`, `GET /reports` (list), `POST /reports/compare`, `DELETE /reports/{id}` — scope every read/write to owner+sample, per `EQ-3`'s already-ratified ruling (`00_README.md`'s register: "Scope (404 cross-tenant); no frontend path affected").
- **Dependencies:** None — `is_owned_or_shared` (Phase 1) already built and unit-tested, unused until now.
- **Complexity:** Medium — mechanical but touches 5-6 routes; needs its own focused PR per `06 §7 Ph6`'s explicit scope note.
- **Expected deliverables:** Route changes, an extended `test_reports_scoping.py`, an implementation report matching the `15`/`16` format.

### Milestone 6 — Observability Hardening

- **Objective:** Close the Medium-severity observability gaps (§5) that block real incident response in a hosted deployment.
- **Scope:** JSON structured logging, pipeline-trace-to-log bridge (`O-2`), per-node span timing, external-provider call tracing, `/health` correctness fixes (`estimated_document_count`, real provider key check, derived `"ok"`).
- **Dependencies:** None architecturally; benefits from Milestone 5 landing first only in that both touch `server.py`'s route bodies (sequencing reduces merge conflicts, not a hard blocker).
- **Complexity:** Medium — additive instrumentation, no architecture change, no new ADR expected.
- **Expected deliverables:** Wired logging config, extended `04_Observability_Audit.md` closure notes, before/after log samples in the implementation report.

### Milestone 7 — Streaming/Lifecycle Test Hardening

- **Objective:** Close the remaining Low-risk-but-real test gaps (`T-6/7/10/11/13/14`) using infrastructure that already exists.
- **Scope:** Automated restart-recovery test, cancel-mid-stream event assertion, finished-job-stream reconnect test, strict event-ordering assertion, `/ingest/pdf` test coverage.
- **Dependencies:** None — pure test-writing against existing, unchanged production code.
- **Complexity:** Small.
- **Expected deliverables:** New test files/cases, a coverage delta report.

### Milestone 8 — Financial Statements & Data Visualization Backend

- **Objective:** Close the largest genuine product-capability gap — real multi-period financial statement data, unblocking both the frozen "Financial Statements" roadmap section and Data Visualization (frontend and backend both currently blocked on this).
- **Scope:** New yfinance-based extraction (`.financials`/`.balance_sheet`/`.cashflow`), a new persisted shape (collection or embedded document — needs design), API surface for the frontend to consume (new route or an additive field on the existing report shape — contract question).
- **Dependencies:** Requires a **new ADR** (this is new data modeling, not a bug fix, per this milestone's own "any new architectural decision requires an ADR" rule) and likely a formal Engineering Question if it changes any existing response shape.
- **Complexity:** Medium-Large — new external-data integration, new schema, new frontend consumption (though frontend build-out is out of a backend-only milestone's scope).
- **Expected deliverables:** ADR, ratified contract addition, implementation + the standard 5-report deliverable set.

### Milestone 9 — Small Capability Closures (Comparison AI + rescore deletion)

- **Objective:** Close the two small, contained, low-risk product gaps and one piece of dead surface.
- **Scope:** `POST /reports/compare`'s AI-generated explanation-of-differences (additive field, one new LLM call); delete `POST /reports/rescore` (zero consumers, admin-gated but still unneeded surface, per `01 D-2`'s original recommendation).
- **Dependencies:** None.
- **Complexity:** Small.
- **Expected deliverables:** One additive contract field (Comparison), one route removal (rescore) — both individually small enough to combine into one milestone.

### Not recommended as a milestone (decision required first)

- **Google Social Authentication** and **Durable Research Sessions** (as a first-class entity) both need a product/CTO decision or a new ADR *before* any engineering milestone can be scoped — see §4 (Critical finding) and §1. Listing either as a roadmap milestone today would be scoping around an unresolved conflict rather than resolving it.
- **Learning's Worked Analysis Examples / Interpretation Self-Check** are real roadmap items but have no home in the frozen Learning contract (`03`) — an EQ against that contract should precede scoping, not follow it.

---

## Summary determination

There is no work remaining that resembles "implement a missing backend for an existing
frontend feature" at the scale of Milestones 2 or 3 — both of those gaps are closed. What
remains is: one unresolved document conflict (Critical), one deferred security-scoping
cutover with a ratified answer waiting to be executed (Milestone 5), a cluster of
observability and test-hardening debt with no architectural risk (Milestones 6-7), and one
genuinely new capability that needs its own ADR before it can be built (Milestone 8). No
milestone above duplicates work already completed in M1-M3.

---

## 7. AI Platform Evolution Roadmap (Post-Milestone 9)

**This section documents, it does not implement.** Everything above (§1-§6) is the
application-maturity roadmap — closing capability gaps, security scoping, observability,
and test debt against the product as it exists today. Milestones 5-9 assume a single-instance
deployment serving a small, known set of AI features. That assumption holds today; it will
not hold indefinitely. AlphaScribe is an AI-native platform, not an application that happens
to call an LLM — as more AI features ship (Comparison's explanation, richer Learning, Financial
Statements-driven analysis, whatever V1.1+ adds), the concerns below stop being optional and
start being load-bearing. Named here, in dependency order, so the pattern is on record before
it's urgent — no new ADR, no architecture change, no revision to §1-§6's milestones.

Each area follows the same shape `11_ADR_Index.md`'s own "Decisions deliberately deferred"
table already uses in this repo: not a gap, a trigger.

### 7.1 AI Evaluation & Regression

**Why this becomes necessary:** today, output quality is checked two ways — `agents/scoring.py`'s
RAGAS-lite scorecard (computed per-report, never compared against a baseline or trended) and
manual live verification (this milestone's own predecessor reports lean on "live-verified
against the real backend" repeatedly, because nothing else exists). That is adequate for two
AI graphs built by one team in one sitting. It stops being adequate the moment a prompt changes,
a model is swapped, or a third AI feature (Comparison's explanation, per §1's roadmap) ships —
none of those events currently has any automated way to prove they didn't silently degrade
output quality. `01 D-10`'s already-documented blind spot (qualitative fabrication passes
faithfulness scoring undetected) is exactly the kind of regression this would need to catch
and today cannot.

| Future capability | Architectural recommendation | Trigger to build |
|---|---|---|
| Golden benchmark datasets | A versioned, repo-tracked set of (ticker, query/concept) → expected-characteristics pairs, spanning both graphs | Before any second prompt revision to either graph ships |
| Regression evaluation | Compare pipeline output against the golden baseline release-over-release, not just "the code path executed" | Same trigger — the first time a prompt or model changes post-launch |
| Citation quality scoring | Extend `agents/scoring.py`'s existing citation-coverage rubric from a per-report number into a tracked, trended metric | Once more than one AI surface produces citations that need comparing over time |
| Hallucination detection | A structured, sampled adversarial check extending past `D-10`'s numeric-only blind spot | When a third AI-generating endpoint ships (today: reports, Learning; a natural line to redraw the scope at) |
| Prompt regression testing | Version prompts explicitly; diff behavior before/after a prompt change against the golden set | Same trigger as regression evaluation |
| Automated evaluation pipelines | A separate, non-blocking (cost-bearing) CI job alongside the existing hermetic/live split in `.github/workflows/backend-ci.yml` | Once golden datasets + regression evaluation exist to run |

### 7.2 AI Provider Governance

**Why this stays centralized, not duplicated per feature:** `agents/llm.py` already centralizes
provider dispatch — that consolidation (`01 D-3`) replaced two independently-drifting dispatch
paths with one, and is exactly the precedent this section extends rather than reopens. Every
AI feature this repo has or will build (reports, Learning, a future Comparison explanation)
should keep depending on that one seam. The alternative — each feature growing its own retry,
failover, or cost logic — is how `D-3` happened in the first place: two call sites, one
condition, and eventually a divergence nobody planned. Centralizing here is not a preference,
it's not repeating a defect already fixed once.

| Future capability | Architectural recommendation | Trigger to build |
|---|---|---|
| Provider capability matrix | A structured table of what each provider supports (function calling, JSON mode, context length) — `PROVIDER_DEFAULTS` today is model-name defaults only, not capabilities | When a feature needs a capability not every configured provider has |
| Provider routing policies | Rules for selecting a provider per request, generalizing the existing light/heavy tier concept | Once more than the current two tiers are needed |
| Automatic failover | Cross-provider fallback — today `chat_text`'s 4-attempt retry loop stays on the same provider throughout | The first time a provider outage, not just a transient error, causes a user-visible failure |
| Timeout budgets | A budget tracked *across* a multi-call pipeline, not just per-request (today: `LG-11`'s deadlines bound the whole job, but nothing allocates time *between* calls) | When a pipeline routinely spends its whole deadline in one slow call, starving the rest |
| Cost-aware routing | Route by real-time cost signal, not capability alone | Once §7.3's cost observability exists to inform it |
| Health monitoring | Provider-level health (latency, error rate) distinct from `/health`'s own app-liveness check | Once more than one provider is live simultaneously in production |
| Model lifecycle management | A deprecation/rotation policy for the specific model strings `PROVIDER_DEFAULTS` hardcodes today | Ahead of the first provider-announced model deprecation |

### 7.3 AI Cost Optimization

**Focus: architecture, not implementation.** Today, cost visibility is a single dimension —
`llm_calls_total` (this session's own addition) counts calls by provider/model/tier/outcome,
with no dollar figure attached. That is sufficient for "is the pipeline calling the LLM the
number of times expected" and insufficient for "what does this feature cost to run."

| Future capability | Architectural recommendation | Trigger to build |
|---|---|---|
| Prompt optimization | Token-efficient prompt design informed by real usage data, not guessed | Once real usage volume exists to analyze |
| Embedding lifecycle management | A caching/reuse policy for `fastembed`'s models and a re-embedding trigger policy for corpus updates | When corpus size or re-ingest frequency makes re-embedding cost material |
| Cache effectiveness | Extend the existing `(ticker, query)` report cache's effectiveness tracking; Learning deliberately has no cache yet (`03 §10 EQ-5`) | Once cache-hit-rate data would actually change a decision |
| Token budgeting | Move from `_format_docs`'s `max_chars` proxy to real token counting | When a provider's actual token limit, not a character-count approximation, starts binding |
| Cost observability | Add a cost dimension alongside `llm_calls_total`'s existing provider/model/tier/outcome labels | Once §7.2's provider governance exists to act on the signal |

### 7.4 Capacity Planning

**When this becomes necessary, not before:** the current design — one process, one shared
`MAX_ACTIVE_JOBS` budget, `JOB_BACKEND=memory` by default (`09 RR-10`, ratified) — is the right
architecture for today's scale, not a placeholder waiting to be replaced. Capacity planning
work is triggered by evidence of real growth, not built ahead of it; building it early would
be solving a problem that doesn't exist yet at the cost of one that does (§1-§6).

| Future capability | Architectural recommendation | Trigger to build |
|---|---|---|
| Concurrent users | Model realistic concurrent-job load against the shared `MAX_ACTIVE_JOBS` budget | When the budget is observed to bind in normal (not pathological) usage |
| Queue growth | Move from the in-memory default toward the already-built-but-unverified Redis-backed `JobStore`/`EventBus` (`JOB_BACKEND=redis`) | The same trigger `15 §5.1`'s inherited condition already names: a real Redis-backed deployment |
| MongoDB scaling | Beyond today's single-node replica set (`08 DA-5`, ratified) toward read replicas or sharding | Query latency or write volume evidence, not a schedule |
| Redis scaling | Beyond today's single instance (`09 §9.7`, no HA in v1, revisit trigger already recorded there) | Same document's own stated trigger |
| Horizontal deployment | Multiple `server.py` processes behind a load balancer, requiring the Redis-backed job/event backend as a precondition | Once a single process's throughput, not its code, is the bottleneck |
| Storage growth | The filing corpus retained indefinitely (`08 §9`'s ratified erasure boundary) vs. job/event collections' existing 30-day TTL | Disk/index-size evidence from the real corpus, not a projection |

### 7.5 Production Operations

**Why this follows architecture stabilizing, not precedes it:** defining an SLO against a
still-changing pipeline measures the wrong thing — the target would need re-deriving after
every phase in §6. `10 §12` already has an incident-response model, but scoped to security
incidents specifically; this section is that same pattern's natural extension to general
AI-pipeline operations, once there is a stable pipeline to operate.

| Future capability | Architectural recommendation | Trigger to build |
|---|---|---|
| SLOs / SLIs | Define against real production traffic patterns, not projected ones | Once real traffic exists to measure |
| Alerting | Consume the Prometheus metrics that already exist (`pipeline_runs_total`, `llm_calls_total`, `http_request_duration_seconds`) — instrumented, not yet alerted on | Once §7.5's SLOs exist to alert against |
| Incident response | Extend `10 §12`'s existing severity model and playbooks from security incidents to AI-pipeline incidents (a provider outage, a cost spike) | Once §7.2/§7.3 give provider/cost incidents something to page on |
| Disaster recovery | A documented MongoDB backup/restore procedure — not present in any frozen document today | Before, not after, the first production data-loss scenario |
| Deployment verification | A real deployment gate — today's `.github/workflows/backend-ci.yml` verifies tests, not a deployment | Once a deployment pipeline exists at all (none does today) |
| Operational runbooks | Codify `10 §12`'s incident playbooks and this section's future additions into living, maintained runbooks | Once Milestones 5-9 land and the architecture they describe stops changing week to week |

---

*Companion documents:* [`01_Backend_Architecture_Review.md`](01_Backend_Architecture_Review.md) ·
[`02_API_Coverage_Audit.md`](02_API_Coverage_Audit.md) ·
[`04_Observability_Audit.md`](04_Observability_Audit.md) ·
[`05_Testing_Audit.md`](05_Testing_Audit.md) ·
[`11_ADR_Index.md`](11_ADR_Index.md) ·
[`15_M2_Phase2_Learning_Implementation_Report.md`](15_M2_Phase2_Learning_Implementation_Report.md) ·
[`16_M2_Company_Research_Findings_Report.md`](16_M2_Company_Research_Findings_Report.md) ·
[`Feature_Parity_Tracker.md`](../governance/Feature_Parity_Tracker.md) ·
index: [`00_README.md`](00_README.md)
