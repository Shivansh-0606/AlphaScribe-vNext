# Change Request — CR-SCOPE-001: Portfolio (Portfolio Card / Portfolio Workspace)

| Field | Value |
|-------|-------|
| **CR ID** | CR-SCOPE-001 |
| **Title** | Portfolio capability (surfaced via "Portfolio Card" component) |
| **Status** | 🟢 Resolved — Deferred to V2.0 |
| **Raised By** | Experience Design Department (Milestone 2, Phase 2) |
| **Raised On** | 2026-07-18 |
| **Type** | Product scope change (adds capability beyond frozen MVP baseline) |
| **Affects** | Component Inventory · Screen Inventory · IA · Navigation · Feature Roadmap |
| **Decision** | ☐ Approve ☑ Defer ☐ Reject — **Defer to V2.0**, decided by CTO, 2026-07-21 |

> Raised because Milestone 2's component brief lists a **Portfolio Card**, but the frozen baseline
> places Portfolio outside the MVP. Per governance, the Experience Design Department does not add or
> remove product scope unilaterally; it raises a CR. No Portfolio design will be produced until this
> CR is explicitly approved.

---

## 1. Feature Description

A **Portfolio** capability lets a user group companies/holdings they own or track and view aggregate
information about that grouping — typically holdings, allocation/weights, aggregate valuation, and
performance over time. In the Milestone 2 component brief this surfaces as a **Portfolio Card**
(a summary tile for a portfolio/holdings group), which implies an underlying Portfolio Workspace
(tracking, analytics, allocation, performance).

Distinct from **Watchlists** (a lightweight list of companies to follow, no holdings/valuation) and
from **Recent Research / Research Sessions** (durable research artifacts). Portfolio implies
position/holdings data the product does not currently ingest.

## 2. Why It Was Flagged

While composing Family 09 (Research Components), the Portfolio Card could not be traced to any frozen
MVP capability. It implies **holdings and valuation data** and a **performance-tracking** capability
that the frozen documents explicitly exclude from the MVP. Designing it would silently expand product
scope and imply a data-ingestion and calculation capability Engineering has not been scoped for.

## 3. Current Traceability Against Frozen Baseline

| Baseline document | Finding | Verdict |
|-------------------|---------|---------|
| **Product Strategy** (§ Out of scope, line ~245) | Lists "…**portfolio execution**, brokerage integration, options or crypto trading" as explicitly out of scope. | ❌ Out of scope |
| **Product Vision** (§ Out of Scope (MVP)) | Lists "Portfolio execution", "Brokerage integrations". Long-Term Vision names "Watchlists" (not Portfolio) as a near-term ecosystem item. | ❌ Not MVP |
| **Information Architecture** (§ MVP Scope Boundaries → Intentionally Excluded) | "Live trading, execution, brokerage, **portfolio**, options, crypto, and social investing — out of scope by Vision." Portfolio is **not** an IA domain. | ❌ Not an IA domain |
| **Navigation Structure** (§ Global Navigation) | Six global destinations: Workspace Home, Research, Compare, Learning, Research Library, Settings. **No Portfolio destination.** | ❌ No destination |
| **Feature Roadmap** | **Version 2.0 → "Portfolio Workspace"**: Portfolio Tracking, Portfolio Analytics, Allocation Analysis, Performance Tracking. | ✅ Already roadmapped to **V2.0** |

**Summary:** Portfolio is unambiguously excluded from the MVP by four frozen documents and is already
placed in **Version 2.0** by the Roadmap. This is not a gap to fill; it is a deliberate boundary.

## 4. User Value

- **For P-01 (Retail Investor):** moderate-to-high *eventually* — tracking owned positions and their
  performance is a natural extension once research is solved. **Low for the MVP problem** ("reduce
  hours of research into minutes"), which is about *understanding companies*, not *tracking holdings*.
- **For P-02 (Student/Learner):** low — learners research to understand, not to manage a portfolio.
- Net: real long-term value, but orthogonal to the MVP's core research job.

## 5. Business Value

- **Long-term:** high — portfolio tracking increases retention and daily active use, and is a
  recognized step toward the "complete research ecosystem" long-term vision.
- **MVP:** low and dilutive — it competes for scope against the differentiator (trust-first,
  grounded research) and pulls toward the crowded portfolio-tracker market where AlphaScribe has no
  edge. Contradicts "build less, but build it exceptionally well."

## 6. Engineering Complexity

**High.** Requires capability the MVP stack does not have:
- Holdings/position data model (quantities, cost basis, transactions) and its persistence.
- Market-value ingestion and aggregate valuation/performance calculation (time-series).
- Allocation math and performance attribution.
- New security/privacy surface (holdings are sensitive financial data → heightened handling).
- New IA domain, navigation destination, and screens.
This is a **workspace**, not a component — the "card" is the tip of a large iceberg.

## 7. UX Impact

- Adds a new top-level domain and destination → changes Navigation Structure and IA (both frozen).
- Introduces a data type (holdings) with its own states (empty portfolio, stale prices, partial
  valuation failure) across new screens.
- Risk of pulling the product's center of gravity from *research* to *tracking*, weakening the
  "one primary intent" and "research-first" positioning if introduced prematurely.

## 8. AI Impact

- Opens pressure toward **portfolio-level recommendations** ("rebalance", "your allocation is
  overweight X") — which collide directly with **Immutable Law 4 (AI never issues recommendations)**
  and the "assistant, not authority" principle. Any Portfolio AI must be carefully fenced to
  explanation-only, raising design/guardrail cost.
- Grounding/traceability model would need extension to portfolio-level aggregates.

## 9. Dependencies

- Market/price data ingestion pipeline (beyond current best-effort filing/statement sources).
- Holdings data entry or brokerage import (brokerage integration is itself out of scope).
- Valuation Tools (Roadmap V2.0) are natural companions — Portfolio is co-located with them in V2.0
  for good reason.
- Would require CRs/updates to IA, Navigation, Screen Inventory, and Roadmap.

## 10. Risks

- **Scope creep** into a full portfolio/brokerage product — the exact expansion the Vision guards against.
- **Trust risk:** holdings data raises privacy/security stakes and invites recommendation-shaped AI.
- **Focus dilution:** weakens the MVP's "solve one problem exceptionally well" mandate.
- **Rework risk:** designing it now, pre-data-model, would likely be redesigned at V2.0 anyway.

## 11. Recommended Release

**Version 2.0** — where the Roadmap already places "Portfolio Workspace." No change to the roadmap is
needed; the correct action is simply *not to build it in the MVP*.

## 12. CTO Recommendation

### → **Defer** (to Version 2.0)

**Rationale:** Portfolio is not a scope *gap* — it is an intentional, quadruple-confirmed boundary
(Strategy, Vision, IA, Navigation) and is already scheduled in Roadmap V2.0. Building it now would
expand the MVP against its core mandate, add high engineering + security cost, and create AI-guardrail
risk (Law 4). **Recommendation: Defer.** The "Portfolio Card" component is withdrawn from the MVP
component library and re-raised as part of the V2.0 Portfolio Workspace design effort, when the
supporting data model and valuation capability exist. Reject any attempt to introduce a
"lite" holdings/valuation feature into the MVP under a different name.

**If the CTO instead wants Portfolio in the MVP:** this CR must be upgraded to formal amendments of
the Product Vision, IA, Navigation Structure, and Feature Roadmap, with Engineering sizing the data
model, price ingestion, and AI guardrails first.

---

*Change Request raised under the [Documentation Governance](../Documentation_Governance.md) process.
Frozen baseline remains authoritative until this CR is explicitly approved.*
