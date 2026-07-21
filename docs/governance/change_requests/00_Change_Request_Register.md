# AlphaScribe vNext — Change Request Register

| Field | Value |
|-------|-------|
| **Purpose** | Track formal Change Requests raised against the frozen Product & Design baseline |
| **Owner** | Governance (CTO decision authority) |
| **Process** | [Documentation Governance](../Documentation_Governance.md) |
| **Last Updated** | 2026-07-21 |

> A Change Request is raised whenever downstream work (design, engineering) encounters something that
> would **add, remove, or alter** frozen product scope. Scope is not changed unilaterally — the CR
> documents the case and the CTO decides (Approve / Reject / Defer). Until a CR is explicitly
> approved, the **frozen baseline remains authoritative** and the flagged item is **not** designed or
> built.

---

## Resolved Change Requests

| CR ID | Title | Raised by | Type | Recommendation | Status |
|-------|-------|-----------|------|----------------|--------|
| [CR-SCOPE-001](CR-SCOPE-001_Portfolio.md) | Portfolio (Portfolio Card / Workspace) | Experience Design (M2/P2) | Scope addition | **Defer → V2.0** | 🟢 Resolved |
| [CR-SCOPE-002](CR-SCOPE-002_News.md) | News (News Card / News Intelligence) | Experience Design (M2/P2) | Scope addition | **Defer → V1.1** | 🟢 Resolved |
| [CR-SCOPE-003](CR-SCOPE-003_Research_Timeline.md) | Research Timeline | Experience Design (M2/P2) | Presentation clarification | **Approve (bounded to Research History); Reject activity-log reading** | 🟢 Resolved |

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

## Decision log

| CR ID | Decision | Decided by | Date | Notes |
|-------|----------|-----------|------|-------|
| CR-SCOPE-001 | Defer → V2.0 | CTO | 2026-07-21 | Portfolio Card withdrawn from MVP component library; re-raised as part of V2.0 Portfolio Workspace design. |
| CR-SCOPE-002 | Defer → V1.1 | CTO | 2026-07-21 | News Card withdrawn from MVP component library; re-raised inside V1.1 News Intelligence design. |
| CR-SCOPE-003 | Approve (bounded to Interpretation A) | CTO | 2026-07-21 | Research Timeline approved strictly as a presentation of existing Research History within Research Library. Interpretation B (new activity/audit log) rejected for MVP. |

---

*All three Change Requests are resolved. The frozen documentation baseline is updated accordingly:
no MVP scope change from CR-SCOPE-001/002 (both deferred, no roadmap change needed); CR-SCOPE-003
introduces no new scope (bounded to an existing MVP capability). Downstream artifacts (Component
Inventory, Family 09) may now reflect these dispositions.*

---

## CR-VIS-01…04 — Stack Divergence (registered 2026-07-21)

Raised informally by Experience Design/Frontend Architecture (embedded as flags across ~18 docs,
never entered in this register — the gap itself was GRA-011 in the Governance Recovery Audit) against
the "vNext" `web/` rebuild's target stack vs. the legacy `frontend/` (CRA) app.

| CR ID | Title | Divergence | Decision | Decided by | Date |
|-------|-------|-----------|----------|-----------|------|
| CR-VIS-01 | Framework | Next.js 15 (web/) vs. Create React App (frontend/) | **Approve** — `web/` (Next.js 15) is canonical for vNext | CTO | 2026-07-21 |
| CR-VIS-02 | Component primitives | shadcn/ui vs. no-shadcn (frontend/'s current rule) | **Approve** — shadcn/ui adopted for `web/` | CTO | 2026-07-21 |
| CR-VIS-03 | Styling | Tailwind CSS v4 vs. Tailwind 3 | **Approve** — Tailwind v4 adopted for `web/` | CTO | 2026-07-21 |
| CR-VIS-04 | Theme / dark mode | Brief's dark-mode implications vs. frozen Design System's single light theme | **Reject** — single light theme stays final; no dark mode, no toggle, regardless of the CR-VIS-01/02/03 stack decision | CTO | 2026-07-21 |

**Note:** CR-VIS-04 is deliberately **not** carried by the CR-VIS-01/02/03 approval. The frozen Design
System already settled this ("deliberately no dark mode, no toggle") independent of which frontend
stack is canonical — ADR-0009's framing ("future theme is a token-set addition") describes a
theoretical extension point, not an open question. This CR closes it: rejected, final.

**Downstream impact:** `frontend/` (CRA) is no longer canonical — see the Repository Structure
decision below. `CLAUDE.md`'s current frontend conventions section (npm/craco, "no shadcn", Tailwind
implied v3) describes the now-non-canonical `frontend/` stack and needs reconciling to `web/`'s actual
stack before it can keep governing engineering work in this repo — **flagged, not yet executed** (see
Repository Structure Cleanup below; this is a substantial rewrite of Claude's own operating
instructions for the repo and needs a explicit go-ahead, not a metadata edit).

---

## Repository Structure — Canonical Frontend (GRA-001, decided 2026-07-21)

**Decision:** `web/` (Next.js 15) is the canonical frontend codebase for AlphaScribe vNext, per CTO
ruling 2026-07-21. `frontend/` (Create React App) is non-canonical.

**Not yet executed:** archiving/labeling `frontend/` and reconciling `CLAUDE.md` to describe `web/`'s
actual conventions. This is a structural repository change and a rewrite of the project's operating
instructions — flagged for explicit confirmation before execution, not carried out as part of this
governance-sync pass.
