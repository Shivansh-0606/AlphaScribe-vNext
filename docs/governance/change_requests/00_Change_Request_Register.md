# AlphaScribe vNext — Change Request Register

| Field | Value |
|-------|-------|
| **Purpose** | Track formal Change Requests raised against the frozen Product & Design baseline |
| **Owner** | Governance (CTO decision authority) |
| **Process** | [Documentation Governance](../Documentation_Governance.md) |
| **Last Updated** | 2026-07-18 |

> A Change Request is raised whenever downstream work (design, engineering) encounters something that
> would **add, remove, or alter** frozen product scope. Scope is not changed unilaterally — the CR
> documents the case and the CTO decides (Approve / Reject / Defer). Until a CR is explicitly
> approved, the **frozen baseline remains authoritative** and the flagged item is **not** designed or
> built.

---

## Open Change Requests

| CR ID | Title | Raised by | Type | Recommendation | Status |
|-------|-------|-----------|------|----------------|--------|
| [CR-SCOPE-001](CR-SCOPE-001_Portfolio.md) | Portfolio (Portfolio Card / Workspace) | Experience Design (M2/P2) | Scope addition | **Defer → V2.0** | 🟡 Open |
| [CR-SCOPE-002](CR-SCOPE-002_News.md) | News (News Card / News Intelligence) | Experience Design (M2/P2) | Scope addition | **Defer → V1.1** | 🟡 Open |
| [CR-SCOPE-003](CR-SCOPE-003_Research_Timeline.md) | Research Timeline | Experience Design (M2/P2) | Presentation clarification | **Approve (bounded to Research History); Reject activity-log reading** | 🟡 Open |

## Context: why these three were raised

All three surfaced during **Milestone 2, Phase 2 (Core Component Design)**. The M2 component brief
listed a **Portfolio Card**, **News Card**, and **Research Timeline**. When mapped to the frozen
[Component Inventory](../../design/09_Component_Inventory.md), [Screen Inventory](../../design/05_Screen_Inventory.md),
[IA](../../design/03_Information_Architecture.md), [Navigation](../../design/04_Navigation_Structure.md),
and [Feature Roadmap](../../master-plan/03_Feature_Roadmap.md), their *capabilities* could not be
traced to the MVP baseline. They were documented in
[Family 09](../../experience_design/Components/09_Research_Components.md) as **⚠ SCOPE — presentation
patterns only, gated behind these CRs**, and no capability has been designed pending decision.

## Decision summary (at a glance)

| Item | In frozen MVP? | Where the baseline places it | Recommended action |
|------|:--------------:|------------------------------|--------------------|
| **Portfolio** | ❌ No (explicitly excluded ×4 docs) | Roadmap **V2.0** — Portfolio Workspace | **Defer to V2.0** |
| **News** | ❌ No | Roadmap **V1.1** — News Intelligence | **Defer to V1.1** |
| **Research Timeline** | ✅ Yes, as **Research History** | MVP — Research Sessions / Research Library | **Approve** as a presentation of Research History; **reject** any new activity-tracking scope |

## Decision log (to be completed by CTO)

| CR ID | Decision | Decided by | Date | Notes |
|-------|----------|-----------|------|-------|
| CR-SCOPE-001 | ☐ Approve ☐ Reject ☐ Defer | | | |
| CR-SCOPE-002 | ☐ Approve ☐ Reject ☐ Defer | | | |
| CR-SCOPE-003 | ☐ Approve ☐ Reject ☐ Defer | | | |

---

*Until decisions are recorded above, the frozen documentation is the authoritative scope baseline and
the flagged capabilities are not to be designed or implemented.*
