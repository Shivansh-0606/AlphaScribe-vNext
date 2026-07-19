# AlphaScribe vNext — Figma Organization Guide

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Milestone / Doc** | M3 · Figma Organization Guide (09) |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |

## Purpose

Define how the AlphaScribe Figma project is **organized, named, variabled, and reviewed**, so the design
source of truth is navigable, scales to hundreds of screens, and maps 1:1 to the token and component
system Engineering implements. This is the contract for the Figma library that mirrors the frozen design
docs.

> **Status note:** the Figma *library artifacts* (the visual component library, variables, and screens)
> correspond to M2 Phase 5 (Design System) and Phases 3–4 (Layouts/Screens), which were **paused for
> review and are not yet produced** in this repo. This guide defines the **required organization** those
> artifacts must follow when built, and is the standard the Design QA/handoff will hold them to. The
> documentation-side source of truth today is the M2 markdown families + M1 tokens.

## Scope

Page hierarchy, component organization, variables, styles, libraries, naming conventions, branching
workflow, review process. **Out of scope:** producing the screens themselves (M2 Phases 3–5).

## Decision Rationale

- **A fixed page hierarchy and naming grammar** is what lets a library scale to hundreds of screens
  without becoming unnavigable — the single biggest cause of design-system rot.
- **Variables map 1:1 to design tokens**, so Figma and code share one source and drift is detectable.

## 1. Page Hierarchy

The Figma file mirrors the M2 `design/figma/` structure and the doc numbering:

```
00 · Cover & Index          project overview, changelog, how-to-use
01 · Foundations            color/type/spacing/grid/elevation/shape specimens (M1) + Variables
02 · Creative Exploration   Direction A/B/C boards (M2 Phase 1) — archived, C marked selected
03 · Core Components        the component library (M2 Phase 2/5) — Families 01–09
04 · Layout Templates       the 5 templates (M2 Phase 3)
05 · Screens                Hi-fi screens by Screen Inventory ID, all states (M2 Phase 4)
06 · Prototypes             interactive flows (M2 Phase 6)
07 · Design QA              QA boards, redlines, sign-off (M2 Phase 7 / M3)
99 · Archive                deprecated/superseded frames
```

## 2. Component Organization

- **Grouped by the 9 families** (01–09), matching [Component Mapping](12_Component_Mapping.md).
- **One component per role** with **variants as properties** (not separate components): `Variant`, `Size`,
  `State` (+ component-specific props). Base + variants live together.
- **Nested/atomic composition:** research components compose foundation+AI components (Figma component
  instances), mirroring the code composition.
- **Slots/props** via component properties (text, boolean, instance-swap) so one component covers its
  matrix.

## 3. Variables (map 1:1 to Design Tokens)

- **Collections** mirror token families: Color, Typography (sizes/weights/leading/tracking), Spacing,
  Radius, Border, Elevation, Shadow, Opacity, Z-index, Motion (duration/easing), Focus, Interaction State.
- **Names match the token names** exactly (`space-4`, `text-lg`, `brand-from`, `elevation-2`, `ring`) so
  Figma ↔ [Design Tokens](../10_Design_Tokens.md) ↔ code are one vocabulary.
- **Single mode** (one light theme; no dark mode — CR-VIS-04). If a future theme is ever approved, it is a
  **second mode** on the same variables (zero rename).
- **Number/color variables** drive components; no raw values on a layer where a variable exists.

## 4. Styles

With variables as the source, styles are thin: **text styles** for the semantic roles (`type.h1`…
`type.figure`), **effect styles** for the 4 shadow/elevation levels, **grid styles** for the 12/8/4
layouts. Color is variable-driven (not legacy color styles) to stay single-sourced.

## 5. Library Publishing

- **One published library** (Foundations + Components + Templates) consumed by the Screens/Prototypes
  files. Screens **never** detach instances — they consume library components so a fix propagates.
- **Semantic versioning** of the library ([13 Governance](13_Design_System_Governance.md)); publish notes
  describe what changed and any migration.

## 6. Naming Conventions

- **Components:** `Family / Component / Variant=… , Size=… , State=…` — e.g.
  `Foundation / Button / Variant=Primary, Size=md, State=Hover` (matches code prop names 1:1).
- **Screens:** `SCR-06 · Company Research / Desktop / Default` (Screen Inventory ID + context + state).
- **Layers:** meaningful names (`metric-value`, not `Frame 214`); auto-layout everywhere; no absolute
  positioning for reflowable content.
- **Variables:** exact token names (§3).

## 7. Branching / Change Workflow

- **Main file = the frozen source of truth**; changes happen on a **Figma branch**.
- Branch → make the change → **Design review** (Constitution + token compliance + a11y) → **CTO approval
  for anything touching frozen scope (CR)** → **merge + publish + version bump**.
- Branch names reference the CR/ticket. No direct edits to main for anything beyond trivial fixes.

## 8. Review Process

Every merge to the library passes: **(1)** token compliance (variables only, names match), **(2)**
variant/size/state completeness (matches M2 spec + [12 Mapping](12_Component_Mapping.md)), **(3)**
accessibility (contrast, focus, non-color-only, labels), **(4)** responsive frames present, **(5)** naming
grammar, **(6)** Constitution alignment. Sign-off recorded on the branch/PR.

## References to Previous Milestones

[Design Tokens](../10_Design_Tokens.md) · [M2 Component families](../Components/00_Component_System.md) ·
[Creative Exploration](../Creative_Exploration/00_Creative_Exploration.md) · [Screen Inventory](../../design/05_Screen_Inventory.md) · [Component Mapping](12_Component_Mapping.md).

## Best Practices

- Build variables first, then components on top (never raw values on layers).
- Keep Figma variant names === code prop names === this guide's grammar — the three must never diverge.
- Screens consume library instances; never detach.

## Anti-patterns

- ✗ Duplicate components instead of variants. ✗ Raw values on layers. ✗ Detached instances in screens.
- ✗ `Frame 214` layer names. ✗ A second color-style system competing with variables. ✗ Editing main
  directly for scope changes (use branch + CR).

## Engineering Considerations

- Because variables === tokens === code names, a token export (e.g. via a Figma variables export) can feed
  the generated token layer ([03](03_Design_Token_Mapping.md)) — keeping design and code in lockstep.
- Variant/state props map directly to component prop unions ([02](02_Component_Specifications.md)).

## Accessibility Considerations

- Contrast and focus are checked at library review; components ship with their a11y annotations
  (roles/labels/keyboard) noted on the Figma component so Engineering sees them at handoff.

## Future Maintenance

Populate pages 03–07 when M2 Phases 3–7 are built to this organization. Keep the page hierarchy and naming
grammar stable. Governed by [13](13_Design_System_Governance.md).

---

*Experience Design Department · Milestone 3 · Document 09 of 14*
