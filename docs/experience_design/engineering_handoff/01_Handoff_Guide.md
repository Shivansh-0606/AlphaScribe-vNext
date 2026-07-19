# AlphaScribe vNext — Engineering Handoff Guide

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Milestone / Doc** | M3 · Handoff Guide (01) |
| **Owner** | Experience Design → Frontend Architecture & Engineering |
| **Last Updated** | 2026-07-18 |

## Purpose

Define **how the design-to-engineering handoff operates**: what the repository is expected to look
like, how design artifacts map to it, the workflow by which Engineering consumes the frozen design,
who owns what, and how work is reviewed. This is the operating manual for the boundary between the
two departments.

## Scope

**In scope:** repository expectations, folder organization, handoff workflow, source-of-truth
hierarchy, ownership boundaries, review workflow. **Out of scope:** actual code structure decisions
(Engineering's to make within these guardrails), CI/CD, and infrastructure.

## 1. Repository Expectations

The handoff assumes the **vNext target stack** (Next.js 15 · React 19 · TypeScript · Tailwind CSS v4 ·
shadcn/ui · Motion · CSS Variables · Zustand · TanStack Query · React Hook Form · Zod). See
[00 README §Stack Divergence](00_README.md#change-requests-and-the-stack-divergence) — this is a
greenfield frontend; the legacy CRA app is the proven token source, not the build target.

Expectations Engineering should satisfy (the *why* is in later docs):

- **Design tokens are the single styling source.** A generated token layer (CSS variables via Tailwind
  v4 `@theme`) is the only place raw values live. No hex/px/ms/z-index literals in components
  ([03 Token Mapping](03_Design_Token_Mapping.md)).
- **shadcn/ui primitives are wrapped, not consumed raw.** Each shadcn primitive is wrapped by an
  AlphaScribe component that binds it to tokens, states, and a11y obligations
  ([12 Component Mapping](12_Component_Mapping.md)).
- **A single light theme, one token set.** No dark mode, no second token set (Constitution;
  CR-VIS-04). shadcn's theming is configured to the one light theme only.
- **State, data, and forms have designated libraries:** Zustand (client/UI state, e.g. watchlist,
  companion open/collapsed), TanStack Query (server data: companies, filings, AI), React Hook Form +
  Zod (all forms and validation). The design's state/validation rules ([States], [02]) map onto these.
- **Accessibility is enforced in CI** (axe/linting) as a merge gate ([06](06_Accessibility_Implementation_Guide.md)).

## 2. Folder Organization (expected shape, not mandated code)

A suggested structure that satisfies the handoff; Engineering may adapt names, not intent:

```
app/                    Next.js 15 App Router routes (one per Screen Inventory screen)
components/
  ui/                   shadcn primitives (generated) — wrapped, not used directly in screens
  foundation/           AlphaScribe wrappers of primitives (Button, Input, …) — Families 01–07
  ai/                   AI components — Family 08
  research/             Research components — Family 09
  layouts/              Layout templates — M2 Phase 3 (pending)
lib/
  tokens/               generated token layer (from Design Tokens) — the styling source of truth
  state/                Zustand stores
  api/                  TanStack Query hooks/clients
  validation/           Zod schemas
styles/                 global CSS, @theme token declarations, fonts (IBM Plex)
public/assets/          exported icons/illustrations/logo (08 Asset Export Standards)
```

Design-side artifacts live under `docs/experience_design/` and `design/` and are **read-only inputs**
to Engineering — never edited by Engineering (raise a CR instead).

## 3. Handoff Workflow

```
FROZEN DESIGN (M1/M2)  →  M3 HANDOFF DOCS (this package)  →  ENGINEERING IMPLEMENTATION
        │                          │                                    │
   source of truth          explains "how"                    consumes, never redecides
        └──────────────── CR loop if a gap/conflict is found ───────────┘
```

1. **Consume the foundation first.** Implement tokens ([03]) and the a11y harness ([06]) before any
   component — everything else depends on them ([11 Implementation Guidelines](11_Engineering_Implementation_Guidelines.md)).
2. **Build primitives → foundation wrappers → AI/research components → layouts → screens**, in the
   dependency order of [11].
3. **Each component is "done" only when** its spec ([02]), tokens ([03]), responsive ([04]), motion
   ([05]), and accessibility ([06]) obligations all pass, verified by [10 Design QA](10_Design_QA_Process.md).
4. **Screens** are assembled from approved layouts + components only; no new components introduced at
   screen time (M2 Phase 4 rule).
5. **A gap or conflict → stop and raise a CR** ([13 Governance](13_Design_System_Governance.md)); never
   resolve a design ambiguity in code.

## 4. Source-of-Truth Hierarchy

Authoritative order (full form in [00 README](00_README.md#source-of-truth-hierarchy-authoritative-order)):
**Product Discovery → Design Constitution → Product Design → Experience Design M1 → M2 → M3 handoff →
code.** Higher wins; code introduces no design decisions. The Design Constitution's 18 Immutable Laws
override any lower artifact.

## 5. Ownership Boundaries

| Concern | Owner | Notes |
|---------|-------|-------|
| Visual language, tokens, components, screens, states, motion intent, a11y requirements | **Experience Design** (frozen) | Changes only via CR |
| Token *delivery* (Tailwind v4 `@theme`, generation), component code, state/data/form architecture, routing, performance | **Frontend Engineering** | Within the design contract |
| Product scope, IA, navigation, features | **Product** (frozen) | Changes only via CR |
| CR adjudication / freeze | **CTO** | Final authority |
| This handoff package | **Experience Design** (authors) → **Engineering** (consumers) | Experience Design maintains; Engineering may not edit, only CR |

**The bright line:** Engineering decides *how to build*; Design decides *what it is and how it must
look/behave*. When those blur, the CR process arbitrates.

## 6. Review Workflow

Two review tracks, both required before a component/screen merges:

1. **Engineering review** (code correctness, architecture, performance, types) — Engineering-owned.
2. **Design QA review** (visual accuracy, token compliance, responsive, motion fidelity, a11y,
   cross-screen consistency) — per [10 Design QA Process](10_Design_QA_Process.md), Experience Design
   or a delegated design-QA reviewer.

A change touching the design system (a new variant, a token) additionally requires the **CR + design
review** path in [13 Governance](13_Design_System_Governance.md). Merge requires: both reviews pass +
a11y CI green + Design QA sign-off recorded.

## Decision Rationale

- **Foundation-first ordering** prevents the classic failure where components are built on ad-hoc
  values and later retrofitted to tokens (expensive, drift-prone).
- **Wrapping shadcn** (not consuming raw) keeps the token/a11y/state contract in one place and makes a
  future primitive swap cheap — insulating the product from the CR-VIS-02 uncertainty.
- **Two review tracks** guarantee that "compiles and works" never ships without "matches the design
  and is accessible."

## References to Previous Milestones

[Design Constitution](../../design/00_Design_Constitution.md) · [Design System](../../design/08_Design_System.md) ·
[Component Inventory](../../design/09_Component_Inventory.md) · [Design Tokens](../10_Design_Tokens.md) ·
[M2 Component families](../Components/00_Component_System.md) · [M1 README stack CRs](../00_README.md).

## Best Practices

- Stand up tokens + a11y harness + one primitive end-to-end as a **vertical slice** before scaling out.
- Keep the token generation single-sourced from [Design Tokens](../10_Design_Tokens.md); never hand-edit
  the generated layer.
- Record Design QA sign-off in the PR so the audit trail exists.

## Anti-patterns

- ✗ Editing frozen design docs to match code. ✗ Using shadcn primitives directly in screens.
- ✗ Starting screens before components pass QA. ✗ Resolving a design gap in a component instead of a CR.

## Engineering Considerations

- Next.js 15 App Router: one route per Screen Inventory screen; server components for data-heavy read
  surfaces (statements, filings), client components for interactive/AI surfaces.
- TanStack Query owns all server-state (best-effort external data → its error/partial states map to
  [States](../../design/13_States.md) Partial Failure/Timeout).

## Accessibility Considerations

The a11y harness ([06]) is part of the *foundation*, not a later pass; the review workflow makes a11y a
merge gate. No handoff step is complete with a11y deferred.

## Future Maintenance

Revisit this guide when the stack decision (CR-VIS-01…03) is finalized or when M2 Phases 3–7 land
(add the layout/screen assembly steps). Governed by [13](13_Design_System_Governance.md).

---

*Experience Design Department · Milestone 3 · Document 01 of 14*
