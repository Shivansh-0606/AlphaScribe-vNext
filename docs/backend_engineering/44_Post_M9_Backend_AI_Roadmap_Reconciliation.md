# 44 — Post-M9 Backend & AI Roadmap Reconciliation

**Status:** 🟡 PROPOSED — CTO DECISION REQUIRED
**Type:** Roadmap reconciliation (research-only, no code changed, no architecture decided)
**Pattern:** Same genre as [`17_M4_Backend_Capability_Roadmap_Reconciliation.md`](17_M4_Backend_Capability_Roadmap_Reconciliation.md) and [`28_Post_M6_Roadmap_Reconciliation.md`](28_Post_M6_Roadmap_Reconciliation.md) — reconciles current repository state against the prior ratified roadmap and recommends what comes next. This document does not itself ratify anything.

---

## 1. Purpose

Document 17's ratified 5-milestone roadmap (M5→M6→M7→M8→M9) is, per the current CTO directive, now fully executed. That roadmap did not define what comes after M9 as a milestone — it appended a documentation-only "AI Platform Evolution Roadmap" (§7) naming five candidate future concern-areas, each gated behind its own trigger, explicitly not a prescribed build-now list. No document since has evaluated those triggers against real repository state or recommended a next milestone. This reconciliation does that, following the same method Document 28 used to name M7: verify claims against primary sources, check triggers against actual evidence, and recommend exactly one next scope for CTO review — not implement it.

---

## 2. Current M9 State

Kept as three separate axes per this task's instruction not to conflate "implemented" with "merged," or code state with governance state.

### A. Governance status

| Document | Own primary header | Own closing statement |
|---|---|---|
| [41 — Architecture](41_M9_Pre_Implementation_Architecture_Decision_Pack.md) | 🟡 **Draft — awaiting CTO and Backend & AI Design Reviewer 2 approval** | §20: *"READY FOR REVIEWER 2 APPROVAL"* — not "approved" |
| [42 — Product Semantics](42_M9_Product_Decision_Explanation_Semantics.md) | 🟡 **Draft — pending CTO ratification** | No approval marker anywhere in the document; ends "Unresolved: None remaining in this record" (content-complete, governance-status unchanged) |
| [43 — API Contract](43_M9_API_Contract_Decision_Pack.md) | 🟢 **APPROVED / FROZEN — CTO RATIFIED** | Its own dependency line claims 41 and 42 as "🟢 APPROVED/FROZEN" |

**Finding, independently re-verified this session:** Document 43's claim that 41 and 42 are approved/frozen is **not corroborated by 41 and 42's own primary status fields**, which still read Draft. This is not new — the prior reconciliation reported the same thing — but it has not been corrected in the interim; the file headers are byte-identical to the previous check. Per this task's instruction, this is recorded as a governance/documentation inconsistency, not silently edited, and not treated as blocking this document (it does not touch 41/42/43).

Additionally, and not previously noted: [`00_README.md`](00_README.md)'s own "Implementation phase" table — the authoritative document index — stops at Document 29 and that row's own status reads: *"🟡 ENGINEERING COMPLETE / EXTERNAL VERIFICATION PENDING (not APPROVED, not CLOSED)"*. That is, **even M7's entry in the ratification register has never been marked approved**, let alone M8 or M9, neither of which appear in the index at all (documents 30–43, 14 documents, zero index entries). The "M8/M9 CLOSED" status asserted in this conversation's CTO directives has no corresponding entry anywhere in the primary governance register.

### B. Implementation status (verified this session, hermetic)

| Item | Verified state |
|---|---|
| M9.1 comparison explanation | `backend/agents/comparison_explanation.py` present; makes a real LLM call (`chat_json` → `ComparisonExplanationSchema`, `agents/llm.py`); enforces citation/grounding validation (`validate_and_map_citations`, zero-citation-reject) matching Learning's precedent; wired into `server.py` (4 routes: `POST /reports/compare/explain`, `GET .../{id}`, `GET .../{id}/stream`, `POST .../{id}/cancel`) |
| M9.1 tests | `test_comparison_explanation_pure.py`, `_execution.py`, `_endpoint.py` — **51/51 passing**, run this session |
| M9.2 rescore removal | `POST /reports/rescore` confirmed absent from `server.py` and from the live OpenAPI schema |
| Route inventory | `test_route_inventory.py` — **3/3 passing** this session, including the M9.2 regression guard (`test_rescore_route_removed`); `APPROVED_ROUTES` = 41 |
| Full hermetic suite | 302/302 passing as of the M9.2 validation pass this session (unchanged since — no production code has moved) |

### C. Git / merge status

```
git log --oneline -8
ca3548e docs: fix README hero blurb still reading as SEC-only
b25ec34 docs: update READMEs for Indian (NSE/BSE) filings support, fix stale claims
078cb6a docs: update README for financial statements + Learning features, backend layers
40d922e M8 financials acquisition endpoint: orchestration, route, and frontend wiring
881d942 M8 financial statements: domain/application/infrastructure implementation
6781cc2 M8 acquisition-state architecture: decision, orchestration, and readiness review
5d47c7a M7 streaming lifecycle test hardening + M8 financial statements design pack
```

**M7 and M8 are merged to `main`.** **M9.1 and M9.2 are not.** `backend/agents/comparison_explanation.py`, its three test files, and the `server.py`/test-suite edits for both M9.1 and M9.2 all remain uncommitted working-tree changes. "M9 closed" in this conversation means "coded and hermetically green in the working tree," not "merged" — a materially different claim than M7/M8's actual merged state.

---

## 3. Source-of-Truth Findings

Summarized from §2, restated once for the record per this task's explicit "Source-of-Truth" requirement:

1. **43 claims 41/42 are approved; 41/42's own headers say Draft.** A live instance of exactly the trap the source-of-truth priority rule warns against. Not corrected since the last check. Not edited here.
2. **00_README.md's ratification register does not reach M8 or M9 at all**, and its one entry closest to them (M7, Document 29) is itself explicitly marked not-approved by its own text. The register cannot be read as evidence that M7, M8, or M9 are CTO-ratified — only the conversational CTO directives assert that.
3. **M9 code is unmerged.** Two different senses of "closed" are in play — working-tree-complete-and-tested vs. merged-and-released — and only the former is true today.

None of this is treated as license to reopen M9 (explicitly out of scope) or to silently fix the documents. It is treated as a factor in §10 (Governance Gates) below: whatever milestone is recommended next inherits this unresolved M9 governance debt as a dependency, not a blocker it can route around.

---

## 4. Post-M9 Candidate Areas — Document 17 §7 Analysis

All five areas from [17 §7](17_M4_Backend_Capability_Roadmap_Reconciliation.md#7-ai-platform-evolution-roadmap-post-milestone-9), each evaluated against the same 11 questions. No triggers invented beyond what 17 §7 states.

### 4.1 §7.1 — AI Evaluation & Regression

1. **Capability:** Golden benchmark datasets, regression evaluation, citation quality trending, hallucination detection, prompt regression testing, a non-blocking CI evaluation job.
2. **Trigger(s):** "Before any second prompt revision ships" (datasets/regression/prompt-testing); "once more than one AI surface produces citations that need comparing" (citation scoring); "when a third AI-generating endpoint ships" (hallucination detection); "once golden datasets + regression evaluation exist" (CI pipeline, self-chained).
3. **Currently satisfied?** **Yes, for two of six rows** — see §5 below for the endpoint count.
4. **Evidence:** `agents/comparison_explanation.py` (M9.1) is a genuine third LLM-generating capability alongside reports (`agents/graph.py`) and Learning (`agents/learning_nodes.py`), and it produces citations validated the same way Learning's already are.
5. **Strategically necessary now?** Yes — `01 D-10`'s already-documented blind spot (fabrication passing faithfulness scoring undetected) is unmitigated, and a third AI surface now exists with no shared quality baseline across any of the three.
6. **Depends on unresolved M9 governance?** No architecturally — this is independent, additive tooling (a new `agents/` module + CI job), not a change to `/reports/compare` or the explanation endpoints. It does depend on M9.1 being real (it is, in the working tree) to have a third surface to evaluate at all.
7. **New architecture decision required?** Yes, a small one — dataset format/storage, evaluation harness shape — but bounded and additive, not a system redesign.
8. **Product semantics required?** No — this is an internal engineering-quality tool, not user-facing behavior.
9. **API contract required?** No — no new or changed route.
10. **Implementation-ready today?** No — needs its own (small) architecture decision first.
11. **Better treated as future work?** No — of the five areas, this is the only one whose triggers can be satisfied by engineering work alone, without waiting on production traffic that does not exist (see §7.5 finding: no deployment pipeline exists at all).

### 4.2 §7.2 — AI Provider Governance

1. **Capability:** Capability matrix, routing policies, automatic failover, cross-call timeout budgets, cost-aware routing, provider health monitoring, model lifecycle management.
2. **Triggers:** Each requires either a capability gap a real feature hits, more than the current two tiers, a real provider outage, or production multi-provider traffic.
3. **Currently satisfied?** **No, for all six rows.**
4. **Evidence:** No repository evidence of a feature needing an unsupported provider capability, no evidence of a provider outage, no evidence of production traffic at all (§7.5 finding below: no deployment pipeline exists).
5. **Strategically necessary now?** No.
6. **Depends on unresolved M9 governance?** No.
7–9. Would require its own architecture decision if triggered; no product/contract work implied.
10. **Implementation-ready?** No — not even triggered.
11. **Better treated as future work?** Yes.

### 4.3 §7.3 — AI Cost Optimization

1. **Capability:** Prompt optimization, embedding lifecycle management, cache-effectiveness tracking, real token budgeting, cost observability.
2. **Triggers:** All require real usage volume, corpus growth, or cache-hit data — or chain on §7.2.
3. **Currently satisfied?** **No, for all five rows.**
4. **Evidence:** No production usage data exists to analyze (same absence as §7.2).
5. **Strategically necessary now?** No.
6. **Depends on unresolved M9 governance?** No.
7–9. Deferred until triggered.
10. **Implementation-ready?** No.
11. **Better treated as future work?** Yes.

### 4.4 §7.4 — Capacity Planning

1. **Capability:** Concurrent-user modeling, Redis-backed queue migration, MongoDB/Redis scaling, horizontal deployment, storage growth planning.
2. **Triggers:** All require evidence of real growth or a real Redis-backed production deployment.
3. **Currently satisfied?** **No, for all six rows** — and the document says so about itself: *"the current design... is the right architecture for today's scale, not a placeholder... triggered by evidence of real growth, not built ahead of it."*
4. **Evidence:** `JOB_BACKEND=memory` remains the default (`RR-10`, ratified); no Dockerfile or `docker-compose*` exists anywhere in the repo (confirmed by Document 28's direct search, not re-litigated here); no evidence this has changed.
5. **Strategically necessary now?** No — self-declared not-yet-necessary by its own source document.
6–9. Not applicable while untriggered.
10. **Implementation-ready?** No.
11. **Better treated as future work?** Yes, explicitly, in the document's own words.

### 4.5 §7.5 — Production AI Operations

1. **Capability:** SLOs/SLIs, alerting on existing Prometheus metrics, AI-incident response, disaster recovery, deployment verification, operational runbooks.
2. **Triggers:** Real production traffic; a deployment pipeline; §7.2/§7.3 existing first (chained); or, for disaster recovery, "before the first production data-loss scenario" (a standing, not evidence-gated, trigger).
3. **Currently satisfied?** **No, for five of six rows.** Disaster recovery's trigger is technically always "live" (a standing prudence, not evidence-gated) but the document itself frames the whole section as following *"architecture stabilizing"* — and M9's own architecture is still contested (§2A/§3) and unmerged (§2C), i.e., still changing.
4. **Evidence:** `.github/workflows/backend-ci.yml` verifies tests only, not a deployment (confirmed this session, doc's own words); no Dockerfile exists; no production traffic.
5. **Strategically necessary now?** No, for the traffic/deployment-gated rows. Disaster recovery is arguably always prudent, but out of proportion given no deployment target exists yet to protect.
6. **Depends on unresolved M9 governance?** Indirectly — "architecture stops changing week to week" (this section's own runbooks trigger) is not true while M9's own architecture packs are still Draft.
7–9. Deferred.
10. **Implementation-ready?** No.
11. **Better treated as future work?** Yes.

---

## 5. Trigger Evaluation — §7.1 Third-Endpoint Claim, Verified in Detail

The specific claim under scrutiny: has a "third AI-generating endpoint" shipped, satisfying §7.1's hallucination-detection trigger? Endpoints were not counted merely for existing — each was checked for an actual LLM call.

| Order | Capability | Route(s) | LLM call evidence | AI-generating? |
|---|---|---|---|---|
| 1st | Research reports | `POST /reports/generate` → `agents/graph.py` (retriever → extractor‖tone → synthesizer → fact_checker) | `chat_text`/`chat_json` calls inside `synthesizer`/`fact_checker` nodes (`agents/llm.py`) | Yes |
| 2nd | Learning | `POST /learning/explain` → `agents/learning_nodes.py` (2-node graph) | Same `chat_text`/`chat_json` abstraction | Yes |
| 3rd | Comparison explanation (M9.1) | `POST /reports/compare/explain` | `agents/comparison_explanation.py:209` — `await chat_json(system, user, ComparisonExplanationSchema, model=DEFAULT_LIGHT_MODEL)`, verified this session by direct read | Yes |
| — | Comparison (deterministic) | `POST /reports/compare` | None — Document 41 §10/§11 (frozen) establishes this route is a pure, deterministic, client-cached query, not an LLM call. Correctly **not** counted. | No |

**Conclusion: the third-AI-generating-endpoint trigger is materially satisfied** — comparison-explanation is a genuine third LLM-generating capability, distinct from the deterministic `/reports/compare` it sits beside, and it independently re-implements the same citation-validation discipline Learning already has (so the citation-quality-scoring trigger — "more than one AI surface produces citations that need comparing" — is *also* now satisfied, with three surfaces, not two).

The caveat from §2: this is true of the **working tree**, not of `main`. Whether "shipped" in Document 17 §7.1's sense requires a merge is a judgment call this document does not resolve — it is surfaced as a dependency in §9/§10, not decided here.

---

## 6. Strategic Comparison

| Candidate | Trigger | Trigger satisfied? | Current value | Urgency | Governance readiness | Recommendation |
|---|---|---|---|---|---|---|
| §7.1 AI Evaluation & Regression | 2 of 6 rows individually triggered (citation scoring, hallucination detection); rest not | 🟢 Partially — the two most foundational rows (golden datasets, regression eval) are buildable *now*, independent of any trigger, per the table's own framing | High — closes `01 D-10`'s documented, unmitigated blind spot across 3 AI surfaces | High | Needs one small ADR; no product/contract work | **Recommended** |
| §7.4 Capacity Planning | None of 6 rows | 🔴 No | Low today | Low | Self-declared "don't build ahead of evidence" by its own source doc | Defer |
| §7.2 Provider Governance | None of 6 rows | 🔴 No | Low today | Low | Needs production multi-provider traffic that doesn't exist | Defer |
| §7.3 Cost Optimization | None of 5 rows (chains on §7.2) | 🔴 No | Low today | Low | Chained on an unmet trigger | Defer |
| §7.5 Production AI Operations | ~0 of 6 rows (disaster recovery is a standing trigger, not evidence-gated, but out of proportion with no deployment target) | 🔴 No | Low today | Low | Needs a deployment pipeline that doesn't exist at all | Defer |

**Ranking:** §7.1 > §7.4 > §7.2 ≈ §7.3 > §7.5.

**Why §7.1 over the other four, specifically:** every other candidate is gated on production traffic or a production deployment, and this repository has neither — no Dockerfile, no deployment pipeline (confirmed, `.github/workflows/backend-ci.yml` runs tests only), no live users. Building toward any of §7.2/§7.3/§7.5 today would be building ahead of evidence, which §7.4's own text explicitly names as the wrong failure mode to fall into. §7.1 is categorically different: its foundational deliverables (a golden dataset, a regression harness) do not require production data to be valuable — they require only the two AI graphs and the new third surface that already exist, and they close a real, already-documented quality gap (`01 D-10`) rather than a hypothetical one. It is the only candidate where "necessary" and "buildable today" coincide.

---

## 7. Recommended Next Milestone

**Exactly one recommendation**, status **🟡 PROPOSED — REQUIRES CTO APPROVAL**, not self-ratified by this document.

> **Milestone 10 — AI Evaluation & Regression Foundation**

---

## 8. Proposed Scope

**Objective:** Give the three existing AI-generating surfaces (reports, Learning, comparison-explanation) a shared, versioned quality baseline, closing `01 D-10`'s documented blind spot (qualitative fabrication passing faithfulness scoring undetected) before a fourth surface or a prompt revision makes the absence of one more costly to retrofit.

**In scope** (the two triggers satisfiable without production data, per §7.1's own table):
- A versioned, repo-tracked golden benchmark dataset: `(ticker, query/concept) → expected-characteristics` pairs spanning all three AI-generating surfaces.
- A regression-evaluation harness comparing pipeline output against that baseline, runnable on demand (not yet wired into CI as a blocking gate).
- Extending `agents/scoring.py`'s existing citation-coverage rubric into a metric trended across all three surfaces (now materially possible — see §5).

**Explicit non-goals:**
- Hallucination detection as a standalone adversarial-check feature (§7.1's own "structured, sampled adversarial check" row) — a natural phase 2 once the dataset/harness exist, not bundled in here.
- Prompt regression testing as an enforced CI gate — the harness must exist first; wiring it in as blocking is separately scoped.
- The non-blocking CI evaluation job itself (§7.1's own last row, explicitly chained on "once golden datasets + regression evaluation exist to run").
- Anything from §7.2/§7.3/§7.4/§7.5 — none triggered (§6).
- Resolving the M9 governance inconsistency (§2A/§3) — that is Document 41/42/43's own unfinished business, not this milestone's to fix.

**Dependencies:** see §9.

**Expected architecture work:** One small ADR — dataset storage format/location, evaluation-harness shape, and how it reads from all three `agents/` surfaces without coupling them to each other. Bounded; does not touch `server.py` routes or existing graphs' runtime behavior.

**Expected product/UX work:** None — internal engineering tooling, no user-facing surface.

**Expected API/contract work:** None — no new or changed route.

**Expected implementation work:** New `agents/`-adjacent module(s) for the harness; a dataset directory; unit tests for the harness itself; documentation of how to run it. No production-code behavior change to the three graphs being evaluated.

---

## 9. Dependencies

**Completed:**
- All three AI-generating surfaces exist and are hermetically tested (reports, Learning shipped/merged; comparison-explanation working-tree-complete, 51/51 tests passing).
- `agents/scoring.py`'s existing citation-coverage rubric — the base this milestone extends, not replaces.

**Unresolved (not this milestone's to fix, but load-bearing context for the CTO decision in §14):**
- M9's own governance state (§2A/§3): Documents 41/42 remain Draft; 43's dependency claim is unverified by them.
- M9.1/M9.2 remain uncommitted (§2C). Whether Milestone 10 should wait for M9 to actually merge before treating comparison-explanation as a "shipped" third surface is a judgment call for the CTO, not resolved here.

**Blocked dependencies:** none found — this is the point of §6's ranking; unlike the other four candidates, nothing external blocks §7.1.

---

## 10. Governance Gates

Before any implementation of Milestone 10:

1. CTO decision on this reconciliation document (§14).
2. A small architecture decision (§8's "expected architecture work") — dataset format, harness shape — reviewed and approved before code, per `Documentation_Governance.md`'s Draft → Review → CTO Approval → Frozen → Implementation chain.
3. **Recommended, not required for Milestone 10 itself:** resolve the M9 governance inconsistency (§2A) — Documents 41/42 formally approved or formally revised — since Milestone 10's own premise (a third AI-generating surface exists) rests on M9.1 being real. This document does not block Milestone 10 on that resolution, but flags it as the more foundational open item the CTO may want addressed first or in parallel.

---

## 11. Ownership

**Backend & AI Engineering.** The proposed deliverables — a dataset format, a regression harness reading from `agents/`, an extension to `agents/scoring.py` — are backend/pipeline engineering work with no frontend, UX, or product-decision surface, matching how this area was scoped in Document 17 §7.1 itself and how Documents 17/28 (this document's own precedents) were authored. Not assumed by AI-association alone — verified by the concrete deliverables having no UI, no API contract, and no product-semantics component (§8).

---

## 12. Acceptance Criteria

- A golden benchmark dataset exists, versioned in the repository, covering all three AI-generating surfaces (reports, Learning, comparison-explanation).
- A regression-evaluation harness runs the dataset against current pipeline output and reports a comparable result, on demand.
- `agents/scoring.py`'s citation-coverage rubric is extended into a metric trended across all three surfaces, with a unit test proving the trend calculation.
- Zero production-code behavior change to the three graphs being evaluated (evaluation is observational, not gating, in this milestone).
- Standard hermetic-suite green, no regressions, matching the pattern every prior milestone report in this index used.

---

## 13. Documentation / Governance Hygiene

**00_README.md was inspected, not edited.** Confirmed independently, again, this session: its "Implementation phase" table stops at Document 29 (M7), and that entry's own text reads "not APPROVED, not CLOSED." Documents 30–43 (all of M8 and M9) have zero entries in the index.

Updating the index to add M7/M8/M9 rows would require first deciding *what status to write* — and that is exactly the unresolved governance ambiguity in §2A/§3 (Documents 41/42 Draft vs. 43's claim they're approved; M7's own row already unresolved; M9 unmerged). Writing "✅ complete" or "🟢 Approved" into the index for any of them would manufacture an approval this document has no authority to grant. Per this task's explicit instruction, the README update is **stopped** rather than performed with a guessed status. The dependency — someone with the authority to rule on Documents 41/42/43's actual status, and on whether "closed" requires a merge, needs to resolve that first — is reported here instead.

**No other documentation was edited.** This document is additive only.

---

## 14. CTO Decision Required

🟡 **PROPOSED — CTO DECISION REQUIRED**

This document recommends Milestone 10 — AI Evaluation & Regression Foundation as the next Backend & AI milestone. It does not approve it, does not authorize implementation, and does not create its architecture decision pack. It also surfaces, without resolving, the outstanding M9 governance inconsistency (§2A) and the stale document index (§13) as items the CTO may wish to close out alongside or ahead of a Milestone 10 decision.
