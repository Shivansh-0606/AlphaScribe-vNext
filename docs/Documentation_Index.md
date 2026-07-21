# AlphaScribe vNext — Documentation Index

| Field | Value |
|-------|-------|
| **Document Status** | ✅ Approved (living index) |
| **Version** | 1.0.0 |
| **Phase** | Product Discovery → PRD |
| **Owner** | Product Team |
| **Last Updated** | 2026-07-21 |
| **Source of Truth** | Yes (documentation landing page) |

This is the landing page for all AlphaScribe vNext documentation. It is a
**living index**: as new documents are authored, add them to the relevant
section with an accurate status badge.

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 1.0.0 | 2026-07-18 | Product Team | ✅ Approved | Initial documentation index covering the frozen product baseline and governance documents. |
| 1.1.0 | 2026-07-21 | Governance (Recovery Execution) | ✅ Approved | Refreshed to list Design, Experience Design, and Frontend Architecture packages that existed but were missing from this index (GRA-010); reflects freeze decisions recorded 2026-07-21. |

---

# Status Legend

| Badge | Meaning |
|-------|---------|
| 📝 Draft | Being authored; not yet reviewed. |
| 🔍 Review | Content complete; under review. |
| ✅ Approved | Reviewed and accepted. |
| 🧊 Frozen | Locked baseline; definitive source of truth. |
| 🗄️ Archived | No longer active; retained for history. |

Lifecycle, versioning, and change rules are defined in
[Documentation Governance](governance/Documentation_Governance.md).

---

# Product

The frozen product baseline (Version 1.0.0). Source of truth for all downstream work.

| Document | Status | Version |
|----------|--------|---------|
| [Product Strategy](master-plan/01_Product_Strategy.md) | 🧊 Frozen | 1.0.0 |
| [Product Vision](master-plan/02_Product_Vision.md) | 🧊 Frozen | 1.0.0 |
| [Feature Roadmap](master-plan/03_Feature_Roadmap.md) | 🧊 Frozen | 1.0.0 |
| [User Personas](design/01_User_Personas.md) | 🧊 Frozen | 1.0.0 |
| [User Journeys](design/02_User_Journeys.md) | 🧊 Frozen | 1.0.0 |
| Competitive Strategy & Product Moat | 🗄️ Not yet created | — |

---

# Design (Product Design)

Frozen 2026-07-21 (CTO confirmation, Governance Recovery Execution). Treated as one immutable unit by
downstream Frontend Architecture ([Constitution §5.2](frontend_architecture/01_Frontend_Architecture_Constitution.md)).

| Document | Status | Version |
|----------|--------|---------|
| [Design Constitution](design/00_Design_Constitution.md) | 🧊 Frozen (governing) | 1.1 |
| [Information Architecture](design/03_Information_Architecture.md) | 🧊 Frozen | — |
| [Navigation Structure](design/04_Navigation_Structure.md) | 🧊 Frozen | — |
| [Screen Inventory](design/05_Screen_Inventory.md) | 🧊 Frozen | — |
| [UX Specifications](design/06_UX_Specifications.md) | 🧊 Frozen | — |
| [Wireframes](design/07_Wireframes.md) | 🧊 Frozen | — |
| [Design System](design/08_Design_System.md) | 🧊 Frozen | — |
| [Component Inventory](design/09_Component_Inventory.md) | 🧊 Frozen | — |
| [Interaction Patterns](design/10_Interaction_Patterns.md) | 🧊 Frozen | — |
| [Responsive Behavior](design/11_Responsive_Behavior.md) | 🧊 Frozen | 0.1.1 |
| [Accessibility](design/12_Accessibility.md) | 🧊 Frozen | 0.1.1 |
| [States](design/13_States.md) | 🧊 Frozen | — |

---

# Experience Design

Foundation + component layer + M3 engineering handoff frozen 2026-07-21 (CTO confirmation). **M2 Phases
3–7 (Layout Templates, High-Fidelity Screens, Figma library, Prototypes, screen-level Design QA) are
formally deferred, not produced** — see the
[Final Handoff Checklist](experience_design/engineering_handoff/14_Final_Handoff_Checklist.md) for the
authoritative, honest breakdown.

| Package | Status |
|---------|--------|
| Visual foundation (00–10: Visual Language, Color, Typography, Spacing, Grid, Elevation, Shape, Iconography, Illustration, Tokens) | 🧊 Frozen |
| [Creative Exploration](experience_design/Creative_Exploration/00_Creative_Exploration.md) (Direction C) | 🧊 Frozen |
| Component families (Components/00–09, 55 components) | 🧊 Frozen |
| Engineering Handoff package (00–14, 15 documents) | 🧊 Frozen |
| Layouts, Screens, Figma library, Prototypes, Design QA (M2 Phases 3–7) | 🗄️ Deferred — not produced |

---

# Frontend Architecture

| Package | Status |
|---------|--------|
| M1 Constitution | ✅ Approved (CTO) |
| M2 Application Architecture (8 files) | 📝 Draft — awaiting CTO review (content authored, not yet frozen) |
| M3 Data & State Architecture | ✅ Approved (CTO) |
| M4 Experience Infrastructure | ✅ Approved (CTO) |
| M5 Engineering Readiness & Governance | ✅ Approved (CTO) |

Canonical frontend codebase: **`web/`** (Next.js 15 / React 19 / TypeScript / Tailwind v4 / shadcn/ui) —
CTO decision, 2026-07-21 (see [CR Register](governance/change_requests/00_Change_Request_Register.md)).
`frontend/` (Create React App) is non-canonical; repository-structure cleanup (archiving/labeling) is
flagged but not yet executed.

---

# Governance

| Document | Status | Version |
|----------|--------|---------|
| [Documentation Governance](governance/Documentation_Governance.md) | 🧊 Frozen | 1.0.0 |
| [Requirements Traceability Matrix](governance/Requirements_Traceability_Matrix.md) | 🧊 Frozen | 1.0.0 |
| [Product Discovery Completion Report](governance/Product_Discovery_Completion_Report.md) | ✅ Approved | 1.0.0 |
| [Change Request Register](governance/change_requests/00_Change_Request_Register.md) | 🧊 Live register — 7/7 tracked CRs resolved | — |

---

# Sections (Placeholders for Upcoming Phases)

The following sections are reserved for documents authored in the PRD and
engineering phases. Each new document must trace to the frozen product baseline
via the [Requirements Traceability Matrix](governance/Requirements_Traceability_Matrix.md).

| Section | Scope | Status |
|---------|-------|--------|
| **Backend** | Backend service documentation. | 🗄️ Not yet created (implementation exists in `backend/`; no doc package) |
| **AI** | AI architecture, prompting, evaluation, conversation lifecycle. | 🗄️ Not yet created |
| **Database** | Data models and schema design. | 🗄️ Not yet created |
| **API** | API contracts and specifications. | 🗄️ Not yet created |
| **Engineering** | PRDs, engineering tasks, implementation plans. | 🗄️ Not yet created (see legacy `docs/planning/` below) |
| **QA** | Test plans, acceptance criteria, quality gates. | 🗄️ Not yet created |
| **Operations** | Deployment, monitoring, runbooks. | 🗄️ Not yet created |
| **Decision Records (ADR)** | Architecture Decision Records. | 🗄️ Deferred — 11 candidates indexed ([05.6](frontend_architecture/05.6_Architecture_Decision_Record_Index.md)), authoring deferred 2026-07-21; `docs/decisions/` intentionally empty |

---

# Legacy

| Package | Relationship to current documentation |
|---------|----------------------------------------|
| `docs/planning/` (01-PRD through 10-Design-Prompts) | Pre-dates `docs/master-plan/`, `docs/design/`, and `docs/experience_design/`. Superseded by those packages where they overlap; not maintained as a source of truth. Retained for history. |
| `memory/PRD.md` | Same relationship — superseded by the frozen product baseline and current governance packages. |

---

# Reading Order (New Contributors)

1. [Product Strategy](master-plan/01_Product_Strategy.md) →
   [Product Vision](master-plan/02_Product_Vision.md) →
   [User Personas](design/01_User_Personas.md) →
   [User Journeys](design/02_User_Journeys.md) →
   [Feature Roadmap](master-plan/03_Feature_Roadmap.md)
2. [Documentation Governance](governance/Documentation_Governance.md) — how documents are managed.
3. [Requirements Traceability Matrix](governance/Requirements_Traceability_Matrix.md) — how decisions map to work.
4. [Product Discovery Completion Report](governance/Product_Discovery_Completion_Report.md) — phase status and PRD authoring rules.
