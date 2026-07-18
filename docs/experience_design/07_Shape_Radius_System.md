# AlphaScribe vNext — Shape & Border Radius System

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Version** | 0.1.0 |
| **Milestone** | M1 — Visual Foundation |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For shape, corners & borders |

**Downstream Dependencies:** [Design Tokens](10_Design_Tokens.md) · Frontend implementation · Component styling

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Experience Design | 📝 Draft | Corner and border language defined around the theme's crisp, editorial `--radius: 0` base. |

---

# Document Traceabilityv

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Visual Language Guidelines](01_Visual_Language_Guidelines.md), [Color](02_Color_System.md), [Elevation](06_Elevation_Shadow_System.md), [Design Constitution](../design/00_Design_Constitution.md) |
| **Used By** | [Design Tokens](10_Design_Tokens.md), [Iconography](08_Iconography_Guidelines.md) |
| **Related Documents** | [Design System](../design/08_Design_System.md), [Component Inventory](../design/09_Component_Inventory.md) |

---

# Purpose

Defines AlphaScribe's corner and border language — the shape character that expresses editorial
precision — and the border tokens that structure surfaces.

# Goals

- A consistent, recognizable shape identity.
- Structure through crisp edges and hairline borders, in keeping with the editorial-fintech
  character.
- A restrained radius scale for the few cases that warrant softening.

# Design Principles

1. **Crisp precision.** The identity favors sharp, structural edges — an editorial-terminal
   precision that signals rigor and trust (Visual Language §Decision Rationale).
2. **Borders as structure.** Hairline borders (`--border`) delineate surfaces and data with
   calm clarity, working with space rather than heavy containers.
3. **Restraint.** Rounding, where used, is subtle and purposeful — never a decorative motif.

# Radius Scale

The established theme uses a **`--radius` base of `0`** — crisp corners are the signature. A
minimal scale exists for the few elements where a slight softening improves ergonomics or
focus (e.g. small interactive chips, avatars), derived relative to the base.

| Token | Value | Use |
|-------|-------|-----|
| `--radius` (base) | `0px` | Default — cards, panels, inputs, tables, most surfaces. The crisp editorial signature. |
| `--radius-sm` | `2px` | Optional subtle softening on small controls where crispness feels harsh. |
| `--radius-md` | `4px` | Reserved for small, self-contained interactive chips/tags if needed. |
| `--radius-pill` | `9999px` | Reserved strictly for inherently circular/pill elements (e.g. avatar, status dot). |

> **Note (alignment):** the frozen [Design System](../design/08_Design_System.md) named a
> generic radius scale; this document resolves it to concrete values consistent with the
> product's actual crisp identity (`--radius: 0`). No frozen decision is contradicted — the
> Design System was implementation-agnostic; this is its grounded realization. The default
> remains sharp; the scale exists only for justified exceptions.

# Border Tokens

| Token | Value | Role |
|-------|-------|------|
| `--border-width` | `1px` | Standard hairline. |
| `--border-color` | `--border` (`#DBD5CC`) | Warm hairline on paper. |
| `--border-strong` | `--muted-foreground` tint | Emphasis borders (e.g. active/selected). |
| `--focus-ring-width` | `2px` | Focus outline thickness (see focus tokens in [Design Tokens](10_Design_Tokens.md)). |

Structural divider patterns (e.g. divided rows/columns) use `--border` hairlines, consistent
with the theme's `divider-x` / `divider-y` and grid-line treatments.

# Decision Rationale

- **Radius 0 as identity:** crisp corners read as precise, serious, and editorial — reinforcing a
  research/terminal character that competitors' rounded, friendly SaaS shapes do not. It is a
  deliberate identity signature, timeless rather than trendy.
- **Hairline borders over heavy containers:** on warm paper, thin borders structure information
  calmly and keep density legible without visual weight (Constitution §11).
- **Tiny optional radius scale:** a pragmatic escape hatch for ergonomics (small tappable chips,
  circular avatars) without diluting the sharp identity.

# Usage Guidelines

- Default to **crisp corners** (`--radius`) for surfaces, inputs, cards, and tables.
- Use `--radius-sm`/`-md` only for small interactive elements where sharpness is uncomfortable,
  and apply consistently across the same element family.
- Use `--radius-pill` strictly for genuinely circular/pill forms (avatars, status dots).
- Structure surfaces with **hairline `--border`** plus space, not thick outlines or heavy fills.

# Best Practices

- Keep corner treatment consistent within a component family (all inputs the same, all cards the
  same).
- Let borders and space do the structural work; reserve elevation for genuine layering (see
  [Elevation](06_Elevation_Shadow_System.md)).

# Anti-patterns

- Mixed, inconsistent radii across similar components (unrefined).
- Large, pill-y rounding on content surfaces (contradicts the crisp editorial identity).
- Heavy or colored borders as decoration.
- Using radius to "soften" a design instead of using space and hierarchy.

# Accessibility Considerations

- Shape never encodes meaning on its own; it is structural.
- Crisp borders must maintain sufficient contrast against surfaces to remain perceivable
  ([Accessibility](../design/12_Accessibility.md)); the warm hairline meets this at the sizes
  used, reinforced by spacing.
- Focus indication is a ring/outline concern (2px, deep-emerald `--ring`), independent of corner
  radius, and always visible.

# Responsive Considerations

- Shape language is constant across all sizes — the crisp identity does not change by breakpoint.
- Touch targets rely on spacing and size, not rounding, to remain ergonomic.

# Future Scalability

- New components inherit the base radius; any need for a new radius step is reviewed and added to
  the scale, never improvised inline.
- A future theme variant keeps the same shape tokens; corner identity is theme-independent.

# Constitution References

[Design Constitution](../design/00_Design_Constitution.md) §11 Visual (structure, restraint),
§12 Spatial, §19 Anti-patterns; grounds the [Design System](../design/08_Design_System.md)
radius family in the product's actual crisp identity.
