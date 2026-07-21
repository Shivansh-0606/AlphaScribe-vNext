# AlphaScribe vNext — Grid System

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 0.1.0 |
| **Milestone** | M1 — Visual Foundation |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For layout grid & breakpoints |

**Downstream Dependencies:** [Design Tokens](10_Design_Tokens.md) · Frontend implementation · Responsive layout

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Experience Design | 📝 Draft | Responsive grid, columns, gutters, reading width, and breakpoint tokens defined. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Spacing](04_Spacing_System.md), [Typography](03_Typography_System.md), [Visual Language Guidelines](01_Visual_Language_Guidelines.md), [Responsive Behavior](../design/11_Responsive_Behavior.md) |
| **Used By** | [Design Tokens](10_Design_Tokens.md), [Elevation](06_Elevation_Shadow_System.md) |
| **Related Documents** | [Navigation Structure](../design/04_Navigation_Structure.md), [Wireframes](../design/07_Wireframes.md) |

---

# Purpose

Defines the layout grid, columns, gutters, container widths, reading measure, and breakpoints —
the spatial skeleton on which every screen is composed. It implements the frozen
[Responsive Behavior](../design/11_Responsive_Behavior.md) structurally, without changing it.

# Goals

- A consistent, flexible layout structure across desktop, tablet, and mobile.
- A comfortable reading measure for text-heavy research.
- Breakpoints that adapt *density and arrangement* while preserving structure (Constitution §18).

# Design Principles

1. **Structure invariant, density adaptive.** The same grid logic everywhere; only column count
   and container width change (Responsive Behavior).
2. **Reading measure protected.** Long-form content never exceeds a comfortable line length.
3. **Grid derives from spacing.** Gutters and margins use the [Spacing](04_Spacing_System.md)
   scale so layout and rhythm agree.
4. **Content-first.** The grid serves research reading and evidence, not decoration.

# Breakpoints (tokens)

Representative min-width breakpoints (the token names are canonical; exact px are tuned in
build and align to the Responsive Behavior contexts).

| Token | Context | Approx. min-width | Base columns |
|-------|---------|-------------------|--------------|
| `--bp-mobile` | Mobile | 0 | 4 |
| `--bp-tablet` | Tablet | ~640–768px | 8 |
| `--bp-desktop` | Desktop | ~1024px | 12 |
| `--bp-wide` | Wide desktop | ~1440px | 12 (wider gutters/margins) |

Mobile-up (progressive): styles target the smallest context first and enhance upward.

# Columns, Gutters, Margins

| Token | Value | Role |
|-------|-------|------|
| `--grid-columns` | 12 (desktop) / 8 (tablet) / 4 (mobile) | Column count per context. |
| `--grid-gutter` | `--space-4` (16) default; `--space-6` (32) on wide | Space between columns. |
| `--grid-margin` | `--space-4`→`--space-8` by context | Page edge margins (grow with width). |
| `--grid-max-content` | ~1280–1440px | Max workspace container width. |
| `--reading-max` | ~68–75ch | Max measure for long-form reading columns. |

# Layout Zones

The persistent frame from [Navigation Structure](../design/04_Navigation_Structure.md) /
[Wireframes](../design/07_Wireframes.md) maps onto the grid:

- **Header / Global Navigation:** full-width, aligned to page margins.
- **Main content:** within the grid; research reading columns constrained to `--reading-max`.
- **Embedded AI / source side panel:** occupies grid columns beside content on desktop; reflows
  below/in-flow on smaller contexts (Responsive Behavior) — always embedded, never a separate
  destination.

# Decision Rationale

- **12/8/4 columns** is a proven, divisible structure that supports side-by-side content + AI
  panel on desktop and clean single-column stacking on mobile, matching the frozen responsive
  arrangement.
- **Reading-max in `ch`** ties measure to the font, guaranteeing comfortable line length across
  sizes regardless of container width (research is a reading task).
- **Gutters from the spacing scale** keep layout and rhythm unified; wide screens get larger
  gutters (`--space-6` = the 32px structural unit) for editorial air.

# Usage Guidelines

- Constrain long-form research/learning text to `--reading-max`, even inside a wide workspace.
- Place the embedded AI/source panel in grid columns beside content on desktop; never let it
  push reading measure beyond comfort.
- Use the full grid for comparison tables and data, allowing horizontal scroll *within the
  region* (not the page) when content exceeds width.
- Keep header/nav aligned to page margins for a stable, oriented frame (adaptive headers,
  [Interaction Patterns](../design/10_Interaction_Patterns.md)).

# Best Practices

- Compose from the grid, not from absolute positioning.
- Preserve vertical rhythm (spacing) alongside horizontal grid alignment.
- Let density adapt by breakpoint while keeping the same structural intent.

# Anti-patterns

- Full-width unconstrained reading text (harms measure/comprehension).
- Page-level horizontal scroll (tables must scroll within their own region).
- Breakpoint layouts that *remove* destinations or content (Responsive Behavior forbids this —
  only density adapts).
- Off-grid, ad-hoc placement that breaks alignment and rhythm.

# Accessibility Considerations

- Reflow: content reflows to a single column on small contexts without loss of information or
  horizontal scrolling of the page ([Accessibility](../design/12_Accessibility.md)).
- Orientation is not locked; layouts work in portrait and landscape.
- Reading measure and spacing support low-vision and cognitive accessibility.

# Responsive Considerations

Directly implements [Responsive Behavior](../design/11_Responsive_Behavior.md): structure and
destinations are constant; column count, gutters, margins, and arrangement adapt. The product
feels like the same premium workspace at every size (Constitution §18).

# Future Scalability

- Additional breakpoints (e.g. ultra-wide) extend the same token model without redefining the
  grid.
- New layout zones (future product areas) compose onto the existing column system.
- The `ch`-based reading measure scales with any future type change automatically.

# Constitution References

[Design Constitution](../design/00_Design_Constitution.md) §11 Visual, §16 Readability, §18
Responsive; implements [Responsive Behavior](../design/11_Responsive_Behavior.md) structurally.
