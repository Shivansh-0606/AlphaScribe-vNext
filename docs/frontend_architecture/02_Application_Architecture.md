# AlphaScribe vNext — Application Architecture

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft — Awaiting CTO Review |
| **Version** | 0.1.0 |
| **Department / Milestone** | Frontend Architecture · M2 — Application Architecture |
| **Governed by** | [Frontend Architecture Constitution](01_Frontend_Architecture_Constitution.md) (frozen) |
| **Last Updated** | 2026-07-19 |
| **Source of Truth** | Yes — the parent application-architecture document for M2 (02.1–02.7 detail it) |

> **Repository-path note.** The milestone brief showed both `docs/frontend_architecture/` (Repository
> Location) and `docs/04_Frontend_Architecture/` (tree label). Milestone 1 established the department at
> **`docs/frontend_architecture/`** (home of the frozen README and Constitution); these M2 documents are
> placed there for continuity — one department, one directory. This is an organizational placement, not
> an architectural decision.

---

## Purpose

Define the **overall structural architecture** of the AlphaScribe vNext frontend: its high-level layers,
the relationships and boundaries between modules, and the interaction model by which a user action becomes
a rendered, grounded result. This document is the **parent** of Milestone 2; documents 02.1–02.7 detail
each dimension (project structure, feature organization, routing, layout, components, UI layer, dependency
rules). It realizes — and never redefines — the [Constitution](01_Frontend_Architecture_Constitution.md).

## Scope

**In scope:** the frontend's architectural layers, module relationships, architectural boundaries
(including the server/client boundary and the frontend/backend boundary), and the end-to-end interaction
model — at the level of structure and responsibility.

**Out of scope:** application code, components, routes, folder scaffolding, state/data/API implementations
(Constitution §2, §5); product/design/experience decisions (frozen upstream); and the detailed treatments
delegated to 02.1–02.7.

## Dependencies

- **Governing:** [Constitution](01_Frontend_Architecture_Constitution.md) — especially §4.1 Clean
  Architecture, §4.3 Separation of Concerns, §4.5 Feature-Based Organization, §4.12 Stable Public
  Interfaces, §4.14 Progressive Decoupling, §5 Constraints (stack), §6 Boundaries, §6.5 Design System
  Ownership, §7 Rendering Philosophy.
- **Frozen upstream:** [Information Architecture](../design/03_Information_Architecture.md),
  [Navigation Structure](../design/04_Navigation_Structure.md),
  [Screen Inventory](../design/05_Screen_Inventory.md),
  [Component Inventory](../design/09_Component_Inventory.md) (templates),
  [States](../design/13_States.md), and the
  [Experience Design Engineering Handoff](../experience_design/engineering_handoff/00_README.md)
  (token consumption, component mapping/layering, responsive, motion, accessibility).
- **Downstream detail:** [02.1 Project Structure](02.1_Project_Structure.md) …
  [02.7 Module Dependency Rules](02.7_Module_Dependency_Rules.md).

## Architectural Decisions

### AD-1 — A layered architecture with inward-pointing dependencies (Clean Architecture)
The frontend is organized into concentric layers; **dependencies point inward** toward stable
abstractions, never outward toward volatile detail (Constitution §4.1). Outer layers know inner ones;
inner layers know nothing of outer ones.

```
        ┌──────────────────────────────────────────────────────────┐
        │  Presentation / UI Layer                                   │  screens, layouts, design-system
        │  (composition of design-system + feature UI)               │  components (Experience Design owns
        │                                                            │  visuals; see §6.5)
        │   ┌──────────────────────────────────────────────────┐    │
        │   │  Feature Layer                                     │    │  one module per frozen IA domain
        │   │  (Company Research, Comparison, Learning,          │    │  (02.2); each a bounded context
        │   │   Research Library, Workspace Home, Account/Setup) │    │  with a stable public surface
        │   │   ┌──────────────────────────────────────────┐    │    │
        │   │   │  Application / Orchestration Layer         │    │    │  use-cases, client state (Zustand),
        │   │   │  (behavior, state ownership, data hooks)   │    │    │  server-state (TanStack Query),
        │   │   │   ┌──────────────────────────────────┐     │    │    │  forms (RHF+Zod)
        │   │   │   │  Integration Layer                 │     │    │    │  typed API-contract client,
        │   │   │   │  (API contract client, adapters,   │     │    │    │  validation at the trust
        │   │   │   │   validation, mappers)             │     │    │    │  boundary (§4.9)
        │   │   │   └──────────────────────────────────┘     │    │    │
        │   │   └──────────────────────────────────────────┘    │    │
        │   └──────────────────────────────────────────────────┘    │
        └──────────────────────────────────────────────────────────┘
   Foundation / Shared (cross-cutting, depended on by all, depends on nothing app-specific):
   design-token consumption · wrapped shadcn primitives · shared types · utilities ·
   accessibility harness · observability · error/fail-fast · motion vocabulary
```

- **Presentation / UI** — renders the approved experience by composing the frozen design system (its
  visuals owned by Design, §6.5) with feature UI. Detailed in [02.5](02.5_Component_Architecture.md),
  [02.6](02.6_UI_Layer_Architecture.md), [02.4](02.4_Layout_Architecture.md).
- **Feature** — one cohesive module per frozen IA domain, each a **bounded context** with a small public
  surface ([02.2](02.2_Feature_Organization.md); Constitution §4.5, §4.12, §4.14).
- **Application / Orchestration** — owns behavior and **state ownership** (client vs. server state),
  use-cases, and data-access hooks. *State/data are architected here, not implemented in this milestone.*
- **Integration** — the typed, validated boundary to the backend API contract (§6); all external data is
  untrusted until validated (§4.9, §4.13).
- **Foundation / Shared** — cross-cutting capabilities every layer may use, which depend on nothing
  application-specific (keeps the core stable; §4.12, §4.14).

### AD-2 — Feature modules are bounded contexts derived from the frozen IA
Features are **not invented**; they are the frozen [IA domains](../design/03_Information_Architecture.md).
Each is a bounded context that communicates only through its public interface ([02.2](02.2_Feature_Organization.md)).
This binds the architecture to approved scope and makes growth additive.

### AD-3 — The server/client boundary is an architectural boundary
Per Constitution §7, the default is server rendering for content-led, read-heavy surfaces; client
rendering is reserved for genuine interactivity and live experience (AI companion, streaming, forms). This
boundary is explicit and governed at the UI and routing layers ([02.3](02.3_Routing_Architecture.md),
[02.6](02.6_UI_Layer_Architecture.md)).

### AD-4 — The design system is consumed, never redefined
The component layering (primitive → foundation → AI → research → feature → screen) follows the frozen M3
handoff; Architecture owns the **consumption model and layering**, Design owns visuals/tokens, Engineering
owns implementation (§6.5; [02.5](02.5_Component_Architecture.md)).

### AD-5 — One interaction model, uniformly applied
Every user action follows one predictable path (below), so the product is consistent and predictable
(Constitution §3 predictability, §4.10 explicitness).

## Interaction Model

A representative flow (e.g. asking the AI a question about a company), expressed as responsibilities, not
code:

```
User action (Presentation/UI, client island)
   → Application layer use-case (owns behavior; decides client vs. server state)
      → Integration layer (typed request over the API contract; validates the response — §4.9/§4.13)
         → Backend (owns AI/grounding/data — §6.2)
      ← streamed, grounded result (sources attach as claims resolve — §7 streaming, States: AI Streaming)
   ← Application layer updates state (server-state cache / client state), preserving prior work (Law 6)
← Presentation re-renders progressively (summary→detail), announcing changes accessibly (§4.6)
```

Cross-cutting throughout: **accessibility by default** (§4.6), **fail fast** on unexpected/invalid
conditions while handling expected [States](../design/13_States.md) gracefully (§4.13),
**observability** of the trust-critical path (§4.15), and **never-lose-work** (§6.3, Design Law 6).

## Architectural Boundaries (summary)

| Boundary | Rule | Detail |
|----------|------|--------|
| Frontend ↔ Backend | Typed, validated API contract; frontend depends on the contract, never internals | §6; [02.7](02.7_Module_Dependency_Rules.md) |
| Server ↔ Client | Server-first for content; client for interactivity/live | §7; [02.6](02.6_UI_Layer_Architecture.md) |
| Feature ↔ Feature | Only via public surfaces / shared modules; no deep imports | [02.2](02.2_Feature_Organization.md), [02.7](02.7_Module_Dependency_Rules.md) |
| Design ↔ Architecture ↔ Engineering | Design defines; Architecture consumes/layers; Engineering builds | §6.5; [02.5](02.5_Component_Architecture.md) |
| Layer ↔ Layer | Dependencies point inward only | AD-1; [02.7](02.7_Module_Dependency_Rules.md) |

## Design Rationale

A layered, feature-bounded architecture directly serves the Constitution's goals (§3): it **scales** by
adding bounded modules, stays **maintainable** through low coupling and stable seams, is **predictable**
via one interaction model, and is **production-ready** because resilience, accessibility, and observability
are structural, not bolted on. Deriving features from the frozen IA keeps the architecture faithful to
approved scope and makes it legible to anyone who knows the product.

## Alternatives Considered

- **Technical-type layering only** (all components together, all hooks together, etc.) — rejected: it
  scatters a feature's concerns, raises cross-cutting coupling, and does not scale to hundreds of screens
  (contra §4.5).
- **Fully client-rendered SPA** — rejected: it abandons Next.js 15's server-first strengths, harms
  perceived performance on imperfect networks (a frozen constraint), and weakens SEO for public surfaces
  (contra §7).
- **Feature-to-feature direct dependencies** — rejected: it creates a coupling web that ossifies the
  system (contra §4.12, §4.14); cross-feature needs go through shared modules or routing instead.

## Trade-offs

- **Layer discipline vs. short-term convenience:** inward-only dependencies add indirection but buy
  long-term changeability (§4.14). Accepted deliberately.
- **Server-first vs. interaction latency:** server rendering optimizes first paint and payload but adds a
  round-trip for some interactions; mitigated by client islands where interactivity is real (§7).

## Risks

- **Feature coupling creep** — teams reaching across feature boundaries. *Mitigation:* enforced public
  surfaces + dependency rules ([02.7](02.7_Module_Dependency_Rules.md)); progressive decoupling as a
  review criterion (§4.14).
- **Server/client boundary misplacement** — over-client rendering harming performance, or over-server
  rendering harming interactivity. *Mitigation:* explicit per-surface decisions ([02.6](02.6_UI_Layer_Architecture.md))
  against performance budgets (§4.7).
- **Design-system drift** — Architecture/Engineering altering tokens or forking components.
  *Mitigation:* §6.5 ownership + CR-only token changes.

## Future Extension Points

- New IA domains (future roadmap releases) enter as **new feature modules** behind public surfaces — no
  change to the core (§4.14).
- The integration layer isolates the backend contract, so a contract evolution is a bounded change
  (§4.12) — and would absorb the resolution of the earlier stack/CR-VIS considerations if ever revisited.
- Observability (§4.15) and quality architecture attach at the cross-cutting layer in later milestones
  without restructuring.

## References to the Frontend Architecture Constitution

§4.1 (Clean Architecture), §4.3 (SoC), §4.4 (Composition), §4.5 (Feature-Based Organization), §4.6
(Accessibility by Default), §4.7 (Performance by Design), §4.9 (Type Safety), §4.10 (Explicitness), §4.12
(Stable Public Interfaces), §4.13 (Fail Fast), §4.14 (Progressive Decoupling), §4.15 (Observability), §5
(Constraints/stack), §6 (Boundaries), §6.5 (Design System Ownership), §7 (Rendering Philosophy). Frozen
upstream references as listed under *Dependencies*.

---

*Frontend Architecture · Milestone 2 · Document 02 (parent) · v0.1.0 (Draft, pending CTO review)*
