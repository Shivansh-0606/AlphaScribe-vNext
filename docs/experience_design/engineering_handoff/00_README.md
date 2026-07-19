# AlphaScribe vNext — Engineering Handoff (Milestone 3)

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Milestone** | M3 — Engineering Handoff & Design-to-Code Readiness |
| **Owner** | Experience Design Department |
| **Audience** | Frontend Architecture & Engineering Department |
| **Approved By** | _Pending CTO Review_ |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | Yes — the index and entry point for the engineering handoff package |

---

## Purpose

This directory is the **final deliverable of the Experience Design Department**: the complete,
implementation-ready translation of AlphaScribe's frozen design system into engineering guidance.
Its single objective is a **zero-ambiguity handoff** — Engineering should never have to *guess* a
spacing value, a state, a breakpoint, a token, a motion curve, an accessibility requirement, a
naming rule, or a behavior. Every such decision is already made upstream and is pointed to here.

This package **explains how to implement**; it contains **no application code** and **changes no
frozen artifact**.

## Scope

**In scope (M3):** the 15 handoff documents listed below — guidance, mappings, standards, process,
and governance that let Engineering begin implementation without making design decisions.

**Out of scope:** application/React code; any change to frozen Product, Design, or Experience Design
artifacts; new features; redesign of screens or components; visual-language changes. Any required
change is raised as a **Change Request** (see [§ Change Requests](#change-requests-and-the-stack-divergence)).

## Documentation Standard (every doc in this package)

Each of the 15 documents carries the same fixed section set the milestone requires:
**Purpose · Scope · Decision Rationale · References to Previous Milestones · Best Practices ·
Anti-patterns · Engineering Considerations · Accessibility Considerations · Future Maintenance.**

## The 15 Handoff Documents

| # | Document | What Engineering gets |
|---|----------|-----------------------|
| 00 | [README](00_README.md) | This index, source-of-truth hierarchy, stack-divergence status, readiness. |
| 01 | [Handoff Guide](01_Handoff_Guide.md) | Repo expectations, folder org, workflow, ownership, review. |
| 02 | [Component Specifications](02_Component_Specifications.md) | The engineering-lens spec for every component (anatomy→edge cases). |
| 03 | [Design Token Mapping](03_Design_Token_Mapping.md) | Every token → its Tailwind v4 / CSS-variable / shadcn implementation intent. |
| 04 | [Responsive Implementation Guide](04_Responsive_Implementation_Guide.md) | Breakpoints, grid, per-context adaptation, nav adaptation. |
| 05 | [Motion Specifications](05_Motion_Specifications.md) | Every animation: trigger, duration, easing, reduced-motion, interruption. |
| 06 | [Accessibility Implementation Guide](06_Accessibility_Implementation_Guide.md) | WCAG AA implementation contract, keyboard, focus, SR, contrast, zoom, targets. |
| 07 | [Icon & Illustration Asset Guide](07_Icon_Illustration_Asset_Guide.md) | Icons, illustrations, logo usage, formats, naming, versioning. |
| 08 | [Asset Export Standards](08_Asset_Export_Standards.md) | SVG/PNG standards, naming, folders, version control. |
| 09 | [Figma Organization Guide](09_Figma_Organization_Guide.md) | Page hierarchy, variables/styles, library, branching, review. |
| 10 | [Design QA Process](10_Design_QA_Process.md) | Repeatable QA: visual, token, a11y, responsive, motion, cross-screen. |
| 11 | [Engineering Implementation Guidelines](11_Engineering_Implementation_Guidelines.md) | Priorities, component/screen order, dependency map, risks, validation. |
| 12 | [Component Mapping](12_Component_Mapping.md) | Every design component → intended frontend component, deps, variants, states. |
| 13 | [Design System Governance](13_Design_System_Governance.md) | Contribution, versioning, CR process, review, ownership, deprecation. |
| 14 | [Final Handoff Checklist](14_Final_Handoff_Checklist.md) | The completion gate — honest status of every readiness criterion. |

## Source-of-Truth Hierarchy (authoritative order)

When two documents appear to conflict, the **higher** one wins. This ordering is the backbone of
the whole handoff.

```
1. Product Discovery (FROZEN)      Strategy · Vision · Feature Roadmap
2. Design Constitution (governs)   00_Design_Constitution.md  — 18 Immutable Laws
3. Product Design (FROZEN)         IA · Navigation · Screen Inventory · UX Specs · Wireframes ·
                                   Design System · Component Inventory · Interaction Patterns ·
                                   Responsive Behavior · Accessibility · States
4. Experience Design M1 (FROZEN)   Visual Language · Color · Type · Spacing · Grid · Elevation ·
                                   Shape · Iconography · Illustration · Design Tokens
5. Experience Design M2            Creative Exploration (Dir. C) · Component families 00–09
6. Engineering Handoff M3 (this)   Guidance only — never overrides 1–5
7. Application code                Consumes 1–6; introduces no design decisions
```

**Rule:** M3 (this package) and the code beneath it may **explain and map** the frozen design, never
**redefine** it. If implementation appears to need a value the frozen layer doesn't provide, that is a
**gap to escalate via CR**, not a decision for Engineering to make.

## Change Requests and the Stack Divergence

The milestone's **engineering target** (Next.js 15, React 19, TypeScript, Tailwind CSS v4, shadcn/ui,
Motion, CSS Variables, Zustand, TanStack Query, React Hook Form, Zod) **diverges from the current
repository**, whose frozen project guide describes a Create React App (craco) + react-router app that
deliberately does **not** use shadcn/ui, and a Tailwind 3-style config.

This divergence was already recorded during M1 as **CR-VIS-01…04**
([Experience Design README §Engineering Awareness](../00_README.md#engineering-awareness--flagged-discrepancies-change-requests)).
This handoff resolves the divergence **as a documentation stance**, not by editing any frozen file:

- **"vNext" is treated as a greenfield frontend rebuild** on the named target stack. The existing CRA
  app is the *current/legacy* frontend; its theme (HSL CSS variables, IBM Plex, the exact token
  values) is the **proven source of the token values** this package maps forward — nothing is
  reinvented.
- **Token *values* are frozen and identical** across current and target; only their *delivery
  mechanism* (Tailwind v4 `@theme`, shadcn primitives) changes. [03 Token Mapping](03_Design_Token_Mapping.md)
  makes this explicit.
- **shadcn/ui adoption for vNext** is documented as the target's primitive layer, mapped onto the
  frozen tokens and the "single light theme, no second token set" rule. This is a *platform* decision
  above Experience Design's authority; it is surfaced, not decided, here. If the CTO keeps the CRA
  stack, this package remains valid because it specifies **tokens and intent, not framework code** —
  [12 Component Mapping](12_Component_Mapping.md) notes the CRA equivalent where relevant.

**No frozen document is edited by this package.** Divergences are cited to CR-VIS-01…04 and the
[M2 scope CRs](../../governance/change_requests/00_Change_Request_Register.md).

## Honest Readiness Status (what exists vs. what is referenced)

A truthful handoff states what it stands on. As of this milestone:

| Upstream layer | Status in repo | Handoff coverage |
|----------------|----------------|------------------|
| Product Discovery, Design Constitution, Product Design (IA→States) | ✅ Present & frozen | Fully referenced |
| Experience Design M1 (Visual Foundation, 10 docs + tokens) | ✅ Present & frozen | Fully mapped (03, 04, 05, 06) |
| Experience Design M2 — Phase 1 Creative Exploration (Direction C) | ✅ Present & approved | Governs 02, 04, 05 |
| Experience Design M2 — Phase 2 Component families (00–09, all 55) | ✅ Present | Fully specified (02, 12) |
| Experience Design M2 — Phases 3–7 (Layout Templates, Hi-Fi Screens, Figma Library, Prototypes, Design QA) | ⚠️ **Not yet produced in repo** (Phase 2 gate was paused for review) | Handoff documents the **process/standards** (09, 10) and the **layout/screen contracts** at the component and token level; **screen-by-screen visual redlines depend on those artifacts and are marked pending in [14 Final Checklist](14_Final_Handoff_Checklist.md)** |
| M2 scope items (Portfolio/News/Timeline) | ⏳ Open CRs (001/002/003) | Excluded from handoff pending CTO decision |

**Consequence:** component-, token-, responsive-, motion-, and accessibility-level handoff is complete
and grounded in real frozen artifacts. **Screen-level visual QA and prototype handoff cannot be
declared complete until M2 Phases 3–7 exist.** [14 Final Handoff Checklist](14_Final_Handoff_Checklist.md)
reports this honestly rather than asserting a completeness the repo does not yet have. This is a
deliberate staff-engineering integrity choice, surfaced for CTO awareness.

## Decision Rationale

- **One index, fixed structure, fixed section set** → predictable navigation for a team that will
  live in these docs for years; low onboarding cost; easy audit.
- **Explicit source-of-truth ordering** → conflicts resolve deterministically, not by debate.
- **Divergence surfaced, not silently resolved** → protects the freeze and keeps design authority
  where it belongs (Constitution governance rule).

## References to Previous Milestones

- Product Discovery — [Strategy](../../master-plan/01_Product_Strategy.md) · [Vision](../../master-plan/02_Product_Vision.md) · [Roadmap](../../master-plan/03_Feature_Roadmap.md)
- [Design Constitution](../../design/00_Design_Constitution.md) · Product Design set ([IA](../../design/03_Information_Architecture.md) … [States](../../design/13_States.md))
- Experience Design M1 — [README](../00_README.md) + foundations 01–10
- Experience Design M2 — [Creative Exploration](../Creative_Exploration/00_Creative_Exploration.md) · [Component families](../Components/00_Component_System.md)

## Best Practices

- Read [01 Handoff Guide](01_Handoff_Guide.md) and [03 Token Mapping](03_Design_Token_Mapping.md)
  **first**; they frame everything else.
- Treat the docs as a **set** — a component isn't "done" until its tokens (03), responsive (04),
  motion (05), and accessibility (06) obligations are all met.
- When something seems missing, **check the source-of-truth hierarchy before inventing** — the answer
  is usually already frozen upstream.

## Anti-patterns

- ✗ Implementing from this package while ignoring the frozen upstream it points to.
- ✗ "Filling a gap" with a design decision in code instead of raising a CR.
- ✗ Re-theming, adding a dark mode, or introducing a value not resolvable to a token.
- ✗ Treating the screen-level handoff as complete before M2 Phases 3–7 exist.

## Engineering Considerations

- The whole package is framework-neutral at the token level and target-specific (Next.js 15/shadcn)
  at the mapping level; both are labeled so a stack change doesn't invalidate the design contract.
- Nothing here blocks starting the **foundation layer** (tokens, primitives, a11y harness) — that
  work is safe to begin now (see [11 Implementation Guidelines](11_Engineering_Implementation_Guidelines.md)).

## Accessibility Considerations

Accessibility (WCAG 2.1 AA) is a **gate, not a section** across this package; [06](06_Accessibility_Implementation_Guide.md)
is its authoritative contract and every other doc defers to it. No component or screen is "done"
until its a11y obligations pass.

## Future Maintenance

This package is versioned and governed by [13 Design System Governance](13_Design_System_Governance.md).
It is updated only when a frozen upstream artifact changes via CR; it is never edited to match code
that drifted. When M2 Phases 3–7 land, update [14 Final Checklist](14_Final_Handoff_Checklist.md) and
the screen-level sections of [02](02_Component_Specifications.md)/[04](04_Responsive_Implementation_Guide.md).

---

*Experience Design Department · Milestone 3 · Document 00 of 14*
