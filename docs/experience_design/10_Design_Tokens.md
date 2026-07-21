# AlphaScribe vNext — Design Tokens

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 0.1.0 |
| **Milestone** | M1 — Visual Foundation |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | Yes — the consolidated, canonical token catalogue |

**Downstream Dependencies:** Frontend implementation (CSS variables / Tailwind theme) · Component styling · QA visual review

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Experience Design | 📝 Draft | Consolidated token catalogue uniting docs 02–09 and adding opacity, layering, motion, focus, and interaction-state tokens. Grounded in the frozen theme. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Color](02_Color_System.md), [Typography](03_Typography_System.md), [Spacing](04_Spacing_System.md), [Grid](05_Grid_System.md), [Elevation](06_Elevation_Shadow_System.md), [Shape](07_Shape_Radius_System.md), [Iconography](08_Iconography_Guidelines.md), [Illustration](09_Illustration_Guidelines.md), [Design Constitution](../design/00_Design_Constitution.md) |
| **Used By** | Frontend implementation; all component styling; QA visual acceptance. |
| **Related Documents** | [Design System](../design/08_Design_System.md), [Accessibility](../design/12_Accessibility.md), [Interaction Patterns](../design/10_Interaction_Patterns.md) |

---

# Purpose

The single, canonical catalogue of every design token in AlphaScribe. All visual properties in
the product **must** originate here. Each foundation document (02–09) owns its domain; this
document consolidates them and adds the cross-cutting token families (opacity, layering, motion,
focus, interaction states) so Engineering has one unambiguous source.

# Goals

- One source of truth for all visual values; no hardcoded values in product code.
- Semantic naming so meaning (not appearance) drives usage and theming.
- Complete coverage of every required token family, each traceable to its rationale.

# Design Principles

1. **Tokens or nothing.** Product code references tokens; raw values are prohibited.
2. **Semantic > raw.** Roles (`--foreground`, `--space-4`) over literals.
3. **One set, centrally controlled.** A single light-theme token set (Constitution single-theme
   decision); a future theme remaps the same roles.
4. **Every value is justified** in its owning document — nothing exists because it "looks good."

# Token Model & Implementation Awareness

Tokens are expressed as **CSS custom properties** (the established mechanism: HSL color vars
consumed via `hsl(var(--token))`, plus a utility/Tailwind theme mapping semantic names to those
variables). This is framework-neutral and matches the current codebase. See
[README](00_README.md) CR-VIS-01…04 for stack discrepancies flagged for CTO decision; the token
model holds under any outcome. **This document defines tokens and intent, not framework code.**

Naming convention: `--<domain>-<role>[-<variant>]` (e.g. `--space-4`, `--text-lg`,
`--elevation-2`, `--motion-duration-base`).

---

# 1. Color Tokens

Canonical values in [Color](02_Color_System.md). Summary of families:

| Family | Tokens |
|--------|--------|
| Surfaces/text | `--background`, `--surface`, `--surface-hover`, `--card(-foreground)`, `--popover(-foreground)`, `--foreground`, `--muted(-foreground)`, `--border`, `--input`, `--input-bg`, `--code-bg` |
| Primary/secondary/accent | `--primary(-foreground)`, `--secondary(-foreground)`, `--accent(-foreground)` |
| Signature signal | `--brand-from`, `--brand-to`, `--ring` |
| Semantic/financial | `brand`, `bullish`, `bearish`, `warning`, `--destructive(-foreground)` |
| Data-viz ramp | `--chart-1` … `--chart-5` |

All meaning-bearing colors are reinforced by text/shape (never color alone).

# 2. Typography Tokens

Canonical in [Typography](03_Typography_System.md).

- **Families:** `--font-sans` (IBM Plex Sans), `--font-mono` (IBM Plex Mono).
- **Font sizes:** `--text-2xs` (10) · `--text-xs` (12) · `--text-sm` (14) · `--text-base` (16) ·
  `--text-lg` (18) · `--text-xl` (22) · `--text-2xl` (28) · `--text-3xl` (36) · `--text-display` (48).
- **Font weights:** `--font-weight-regular` (400) · `-medium` (500) · `-semibold` (600) ·
  `-bold` (700).
- **Line heights:** `--leading-tight` (1.15) · `-snug` (1.3) · `-normal` (1.55) · `-relaxed` (1.7).
- **Letter spacing:** `--tracking-tight` (-0.01em) · `-normal` (0) · `-label` (0.22em).
- **Semantic roles:** `type.display / h1 / h2 / h3 / body / body-strong / small / caption /
  label / figure / code` (compose the above).

# 3. Spacing Tokens

Canonical in [Spacing](04_Spacing_System.md). 4px base / 8px rhythm:
`--space-0` (0) · `-1` (4) · `-2` (8) · `-3` (12) · `-4` (16) · `-5` (24) · `-6` (32) · `-7` (40) ·
`-8` (48) · `-9` (64) · `-10` (96).

# 4. Grid Tokens

Canonical in [Grid](05_Grid_System.md).

- **Breakpoints:** `--bp-mobile` · `--bp-tablet` · `--bp-desktop` · `--bp-wide`.
- **Structure:** `--grid-columns` (12/8/4) · `--grid-gutter` (→ spacing) · `--grid-margin` ·
  `--grid-max-content` · `--reading-max` (~68–75ch).

# 5. Radius Tokens

Canonical in [Shape](07_Shape_Radius_System.md).
`--radius` (0, base) · `--radius-sm` (2) · `--radius-md` (4) · `--radius-pill` (9999).

# 6. Border Tokens

Canonical in [Shape](07_Shape_Radius_System.md).
`--border-width` (1) · `--border-color` (→ `--border`) · `--border-strong` · `--focus-ring-width` (2).

# 7. Elevation Tokens

Canonical in [Elevation](06_Elevation_Shadow_System.md).
`--elevation-0` (canvas) · `-1` (raised) · `-2` (contextual) · `-3` (overlay) · `-4` (modal).

# 8. Shadow Tokens

Soft, warm-neutral, low-opacity; tuned in build. Named by elevation they serve:

| Token | Intent |
|-------|--------|
| `--shadow-none` | Base/flat (canvas, most surfaces). |
| `--shadow-sm` | Subtle lift for contextual surfaces (`--elevation-2`). |
| `--shadow-md` | Overlays (`--elevation-3`: menus, popovers, drawers). |
| `--shadow-lg` | Modals/dialogs (`--elevation-4`). |

Shadows are soft and never colored/hard (see Elevation rationale).

# 9. Opacity Tokens

For disabled states, scrims, and subtle layering — not for decoration.

| Token | Value | Use |
|-------|-------|-----|
| `--opacity-disabled` | 0.45 | Disabled controls (with non-opacity cues too). |
| `--opacity-muted` | 0.65 | De-emphasized secondary elements. |
| `--opacity-scrim` | 0.55 | Modal backdrop scrim over content. |
| `--opacity-full` | 1 | Default. |

Disabled state is never signaled by opacity alone (accessibility).

# 10. Layering (Z-index) Tokens

Canonical in [Elevation](06_Elevation_Shadow_System.md).
`--z-base` (0) · `--z-raised` (10) · `--z-nav` (100) · `--z-drawer` (200) · `--z-overlay` (300) ·
`--z-modal` (400) · `--z-toast` (500).

# 11. Motion Tokens

Governed by [Design Constitution](../design/00_Design_Constitution.md) §14 — motion communicates,
never distracts; always honors reduced-motion.

## Duration

| Token | Value | Use |
|-------|-------|-----|
| `--motion-duration-instant` | 0ms | Reduced-motion / immediate. |
| `--motion-duration-fast` | 120ms | Micro-feedback (hover, press). |
| `--motion-duration-base` | 150ms | Standard transitions (matches theme's 150ms). |
| `--motion-duration-slow` | 240ms | Larger transitions, reveals, elevation changes. |
| `--motion-duration-stream` | contextual | AI streaming cadence (readable, human pace). |

## Animation Curves (easing)

| Token | Curve intent | Use |
|-------|--------------|-----|
| `--motion-ease-standard` | gentle in-out | Most state transitions (theme default `ease`). |
| `--motion-ease-out` | decelerate | Entrances / reveals (theme's `ease-out`, e.g. ticker-in). |
| `--motion-ease-in` | accelerate | Exits. |
| `--motion-ease-emphasis` | refined in-out | Occasional purposeful delight (subtle, never spectacle). |

Reduced-motion collapses durations to `--motion-duration-instant` and removes non-essential
animation with no information loss.

# 12. Focus Ring Tokens

Accessibility-critical; always visible.

| Token | Value | Role |
|-------|-------|------|
| `--focus-ring-color` | `--ring` (deep emerald) | Focus indicator color (AA contrast). |
| `--focus-ring-width` | 2px | Ring thickness. |
| `--focus-ring-offset` | 2px | Gap between element and ring for legibility. |

Focus is never removed, only styled; it appears on all interactive elements
([Accessibility](../design/12_Accessibility.md)).

# 13. Interaction State Tokens

Standard, consistent responses to input across components (Constitution §19 Micro-interaction;
[Interaction Patterns](../design/10_Interaction_Patterns.md)).

| Token | Role |
|-------|------|
| `--state-hover-surface` | → `--surface-hover` (warm hover on surfaces). |
| `--state-hover-emphasis` | Slight emphasis on interactive text/controls. |
| `--state-active` | Pressed/active affordance (proportionate, brief). |
| `--state-selected` | Selected state (`--accent` tint + non-color cue). |
| `--state-focus` | Composes the focus-ring tokens. |
| `--state-disabled` | `--opacity-disabled` + reduced emphasis (plus non-opacity cue). |

Every state acknowledges the user immediately and proportionately (alive, responsive feel).

---

# Decision Rationale (why a token system)

- **Consistency & craft:** a single token set is what makes the product feel one crafted whole;
  drift is the enemy of premium (Constitution §11).
- **Maintainability:** central control means a change propagates once, safely.
- **Themability:** semantic roles let a future theme (or brand extension) remap values without
  touching product code.
- **Accessibility guarantee:** encoding focus, contrast-safe colors, and non-opacity-only states
  as tokens makes accessible defaults the easy path.

# Usage Guidelines

- Reference tokens exclusively; a raw value in product code is a defect.
- Compose higher-level decisions (component styles) from these tokens; do not introduce new
  primitives inline.
- When a needed value doesn't exist, add a **new token in the owning document** (reviewed),
  never a one-off literal.

# Best Practices

- Keep the token set small and semantic; resist proliferation.
- Validate new color/contrast tokens against AA before adding.
- Map Tailwind/theme names 1:1 to these tokens so the utility layer and CSS variables never
  diverge.

# Anti-patterns

- Hardcoded hex, px, ms, or z-index values in product code.
- Duplicate tokens with the same value and different names (ambiguity).
- Per-component bespoke tokens where a shared one exists.
- Overriding a token's *meaning* locally.

# Accessibility Considerations

- Color tokens ship AA-compliant pairings; focus tokens are always applied; disabled/selected
  states carry non-color/non-opacity cues; motion tokens honor reduced-motion. All per
  [Accessibility](../design/12_Accessibility.md).

# Responsive Considerations

- Grid/spacing/type tokens adapt by breakpoint per their owning docs; color, radius, elevation,
  motion, and interaction tokens are constant across sizes (Constitution §18 — the product feels
  the same premium at every size).

# Future Scalability

- New domains add a new token family here, sourced from a new owning document.
- A future dark theme is a **second token set** mapping the same semantic roles to dark-ground
  values (CR-VIS-04) — zero product-code changes.
- The catalogue is the stable contract between design and engineering as the product grows.

# Constitution References

Governed throughout by the [Design Constitution](../design/00_Design_Constitution.md): §11
Visual, §12 Spatial, §14 Motion, §17 Accessibility, §18 Responsive, §19 Micro-interaction/
Anti-patterns; consolidates the [Design System](../design/08_Design_System.md) token families.
