# AlphaScribe vNext — Responsive Implementation Guide

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Milestone / Doc** | M3 · Responsive Implementation Guide (04) |
| **Owner** | Experience Design Department |
| **Design source (frozen)** | [Responsive Behavior](../../design/11_Responsive_Behavior.md) · [Grid](../05_Grid_System.md) · Constitution §18 |
| **Last Updated** | 2026-07-18 |

## Purpose

Tell Engineering **exactly how the design adapts across sizes** — breakpoints, grid, per-component
behavior, navigation adaptation, and the priorities at each context — so no responsive decision is left
to implementation guesswork. The governing frozen rule: **structure and destinations are constant;
only presentation density and arrangement adapt** (Constitution §18).

## Scope

Breakpoints, layout adaptation, component behavior, grid changes, navigation adaptation, and mobile/
tablet/desktop priorities. **Out of scope:** per-screen redlines (M2 Phase 4, pending) — the rules here
apply to every screen once assembled.

## Decision Rationale

- **One structure, adaptive density** (not separate mobile/desktop products) keeps the experience, code,
  and navigation single-sourced — the identity is constant at every size (Visual Language §Responsive).
- **Mobile prioritizes the current research task**; it condenses the rest rather than removing it, so no
  capability is lost on small screens (§18 navigation parity — the anti-"hidden navigation" rule).

## 1. Breakpoints

**Source:** [Grid tokens](../10_Design_Tokens.md#4-grid-tokens) · [Grid System](../05_Grid_System.md).
Tokens: `--bp-mobile · --bp-tablet · --bp-desktop · --bp-wide`, mapped to Tailwind `screens`.

| Context | Range (intent) | Grid columns | Container | Primary intent |
|---------|----------------|--------------|-----------|----------------|
| **Mobile** | small phones → ~640 | **4** | fluid, edge margins `--grid-margin` | the current research task, condensed |
| **Tablet** | ~640 → ~1024 | **8** | fluid with max | same structure, compact density |
| **Desktop** | ~1024 → ~1440 | **12** | `--grid-max-content` | full concurrent navigation + companion |
| **Wide** | ~1440+ | **12** | capped at `--grid-max-content` | extra whitespace, not extra density |

**Reading measure** (`--reading-max` ~68–75ch) is honored at **every** size — content columns never
exceed it even on wide screens. Sizes are rem-based (respect zoom, §06).

## 2. Layout Adaptation (per template)

**Source:** [Component Inventory Templates](../../design/09_Component_Inventory.md#templates); detailed
grids are M2 Phase 3 (pending). Rules that hold now:

| Template | Desktop | Tablet | Mobile |
|----------|---------|--------|--------|
| Workspace | header + persistent nav rail + content | header + condensed icon-rail + content | header + menu-button drawer + content |
| Research | nav rail + content + **non-modal AI companion (reflows content)** | condensed rail + content + companion (narrower/toggle) | content-first; companion = summoned **sheet** |
| Document (Report) | nav + single reading column + source panel | same, source panel may collapse | single column; sources as a section |
| Public/Setup | centered content, generous space | same | full-width, stacked |

**Sticky regions:** Global Header (`--z-nav`), Section Nav / condensed Company Header on scroll, table
sticky header + first column. **Scroll:** page scrolls the content region; overlays/companion manage
their own internal scroll; wide tables/charts scroll **within their container** (page never scrolls
horizontally).

## 3. Grid Changes

12 → 8 → 4 columns (desktop→tablet→mobile). Multi-column card/metric grids reflow by column count
(e.g. KPI Tiles 4→3→2→1) — **the set stays complete**, only the arrangement changes. Gutters/margins
from `--grid-gutter`/`--grid-margin`. Content never drops below the reading measure legibility.

## 4. Component Behavior (the adaptation rules, consolidated)

Authoritative per-component "Responsive" is in each [M2 family](../Components/00_Component_System.md);
the recurring patterns:

| Pattern | Desktop | Mobile adaptation |
|---------|---------|-------------------|
| **Overlays** | popover/menu anchored; dialog centered | popover→**bottom sheet**; dialog→**full-screen**; drawer→sheet |
| **Tables** | full columns | h-scroll + sticky header/first col, or reflow to label:value **record rows** (no data dropped) |
| **Tabs / Section Nav** | full tablist | overflow→horizontal scroll, or section **picker**; all sections reachable |
| **Search** | inline field | header collapses to icon → expands to full-width field/sheet; suggestions = sheet |
| **AI companion** | non-modal side drawer, reflows content | summoned **sheet** (may be modal for reach) |
| **Sidebar / Nav** | persistent rail | icon-rail (tablet) → off-canvas focus-trapped drawer (mobile); **destination parity** |
| **Charts** | chart + optional table | data-table equivalent may become primary |
| **Hover-only affordances** | hover reveals | **tap-to-reveal** (never hover-only on touch) |

## 5. Navigation Adaptation

**Source:** [Navigation Structure §Responsive](../../design/04_Navigation_Structure.md#responsive-navigation).
**Every destination exists at every size**; only presentation density changes. Desktop = full global +
contextual concurrently; tablet = compact; mobile = current context prioritized, secondary movements
condensed (drawer) but reachable. Current location exposed by indicator + `aria-current` at all sizes.
**No destination may appear on one context and be absent on another** (anti-pattern).

## 6. Context Priorities

- **Mobile priorities:** the active research content first; AI is summoned, not persistent; one primary
  action visible; dense data becomes scrollable/record-row; touch targets ≥ 44px; keyboard/software-
  keyboard ergonomics (send above keyboard).
- **Tablet behavior:** same structure as desktop at higher density; companion narrower or toggle; rail
  condensed to icons with labels on hover/focus.
- **Desktop behavior:** full concurrent navigation + non-modal AI companion that **reflows** (never
  overlaps) content; widest set of movements visible; wide screens add whitespace, not density.

## References to Previous Milestones

[Responsive Behavior](../../design/11_Responsive_Behavior.md) · [Grid](../05_Grid_System.md) ·
[Navigation Structure](../../design/04_Navigation_Structure.md) · [M2 families](../Components/00_Component_System.md) · Constitution §18.

## Best Practices

- Mobile-first implementation of each component, then progressively enhance density.
- Verify reading measure at wide sizes (cap content width; don't let text run edge-to-edge).
- Test the companion reflow at desktop and the sheet at mobile as one behavior, two presentations.

## Anti-patterns

- ✗ Removing a destination/capability on mobile (hidden-navigation §23). ✗ Horizontal page scroll.
- ✗ Hover-only affordances on touch. ✗ Dropping data columns instead of reflowing. ✗ A second, divergent
  mobile layout/product.

## Engineering Considerations

- Tailwind responsive utilities driven by the `--bp-*` screens; container queries where a component's
  context (not viewport) should drive its density (e.g. a card in a reflowing grid).
- Next.js: the App-Router layout hosts persistent nav/header; screens are the content region.

## Accessibility Considerations

Touch targets ≥ 44px on touch; reflow to 320px width and to 200% zoom **without loss of content or
horizontal scrolling** of the page (WCAG 1.4.10 Reflow) — see [06](06_Accessibility_Implementation_Guide.md).
Focus order stays logical across breakpoint changes.

## Future Maintenance

When M2 Phase 3 (Layout Templates) and Phase 4 (Screens) land, add per-template grid specs and per-screen
redlines here. Governed by [13](13_Design_System_Governance.md).

---

*Experience Design Department · Milestone 3 · Document 04 of 14*
