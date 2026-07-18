# AlphaScribe vNext — Color System

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Version** | 0.1.0 |
| **Milestone** | M1 — Visual Foundation |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For color |

**Downstream Dependencies:** [Design Tokens](10_Design_Tokens.md) · Frontend implementation · Charts · Component styling

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Experience Design | 📝 Draft | Color system formalized from the frozen warm-light theme (HSL CSS variables + semantic accents). |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Visual Language Guidelines](01_Visual_Language_Guidelines.md), [Design Constitution](../design/00_Design_Constitution.md), [Design System](../design/08_Design_System.md), [Accessibility](../design/12_Accessibility.md) |
| **Used By** | [Elevation](06_Elevation_Shadow_System.md), [Iconography](08_Iconography_Guidelines.md), [Illustration](09_Illustration_Guidelines.md), [Design Tokens](10_Design_Tokens.md) |
| **Related Documents** | [States](../design/13_States.md), [Component Inventory](../design/09_Component_Inventory.md) |

---

# Purpose

Defines AlphaScribe's semantic color system: the palette, the roles each color plays, contrast
requirements, financial-signal colors, and how AI content is colored. It formalizes the
existing theme so documentation and product share one source of truth.

# Goals

- One coherent, warm-light palette that is calm, premium, and legible for long reading.
- Semantic roles (not raw colors) so meaning is stable and themable.
- Guaranteed WCAG 2.1 AA contrast for text and meaningful UI.
- A single signature signal (emerald→teal) plus reserved financial and chart colors.

# Design Principles

1. **Semantic, not literal.** Product code references roles (`--foreground`, `--brand-from`),
   never raw hex — so meaning is consistent and the theme is centrally controlled.
2. **One canvas, one ink, one signal.** Warm parchment ground, ink-navy type, a single
   emerald→teal accent (Visual Language §Decision Rationale).
3. **Color is meaning.** Accent and financial colors are reserved for emphasis and genuine
   signal; nothing is colored for decoration (Constitution §11, §19).
4. **Never color alone.** Every color-coded meaning is reinforced by text or shape
   (Constitution §17; Accessibility).

# Color Roles & Values

The canonical values are HSL CSS variables (consumed as `hsl(var(--token))`), with a few
semantic accents as hex. These reflect the established theme.

## Surfaces & Text

| Token | HSL | Approx. | Role |
|-------|-----|---------|------|
| `--background` | `38 27% 91%` | `#EEEAE2` | Warm parchment canvas (the "paper"). |
| `--surface` / `--card` / `--popover` | `40 28% 95%` | `#F6F3EF` | Raised content surfaces (lift, not pure white). |
| `--surface-hover` | `38 22% 89%` | `#E9E3DA` | Gentle warm hover on surfaces. |
| `--foreground` | `215 40% 14%` | `#15212F` | Primary ink-navy text. |
| `--muted` | `38 22% 90%` | `#ECE6DD` | Quiet background fill. |
| `--muted-foreground` | `215 14% 40%` | `#59626F` | Secondary text, captions, metadata. |
| `--border` / `--input` | `36 18% 83%` | `#DBD5CC` | Warm hairline dividers and input borders. |
| `--input-bg` | `42 30% 96%` | `#F8F5F0` | Warm off-white input fields. |
| `--code-bg` | `210 16% 92%` | `#E9ECEF` | Muted code/data surface. |

## Primary, Secondary, Accent

| Token | HSL | Approx. | Role |
|-------|-----|---------|------|
| `--primary` | `215 40% 14%` | `#15212F` | Ink-navy solid buttons and strong text. |
| `--primary-foreground` | `42 30% 96%` | cream | Text on navy buttons. |
| `--secondary` | `38 20% 88%` | `#E7E0D6` | Warm light secondary surface. |
| `--accent` | `162 36% 84%` | `#CFE7DD` | Soft emerald tint (quiet highlight). |
| `--accent-foreground` | `162 84% 15%` | deep emerald | Text on the emerald tint. |

## Signature Gradient (the one signal)

| Token | HSL | Approx. | Role |
|-------|-----|---------|------|
| `--brand-from` | `162 88% 28%` | `#069169` | Deep emerald — start of the signature gradient. |
| `--brand-to` | `176 82% 29%` | `#0D8C82` | Deep teal — end of the signature gradient. |
| `--ring` | `162 84% 28%` | deep emerald | Focus ring (see [README](00_README.md) & Accessibility). |

The emerald→teal gradient is AlphaScribe's single recognizable signal. Use it sparingly: the
primary action, the AI/verified/positive moment, and focus. Deepened intentionally so it reads
**rich, not neon**.

## Financial & Semantic Signal (reserved)

| Token | Value | Role |
|-------|-------|------|
| `brand` | `#047857` | Legible accent/link text on cream (emerald-700). |
| `bullish` | `#059669` | Verified / positive financial signal (emerald-600). |
| `bearish` | `#DC2626` | Negative financial signal (red-600). |
| `warning` | `#D97706` | Caution / needs attention (amber-600). |
| `--destructive` | `0 70% 46%` (`#C62D2D`) | Destructive/error affordances. |

**These colors carry meaning and are never decorative.** `bullish`/`bearish` appear only for
genuine financial direction; `warning` only for caution.

## Data Visualization Ramp (reserved)

| Token | HSL | Hue | Use |
|-------|-----|-----|-----|
| `--chart-1` | `162 78% 34%` | emerald | Primary series (ties to the signature). |
| `--chart-2` | `0 70% 48%` | red | Secondary/contrast series. |
| `--chart-3` | `32 90% 42%` | amber | Tertiary series. |
| `--chart-4` | `210 84% 44%` | blue | Quaternary series. |
| `--chart-5` | `280 52% 50%` | violet | Fifth series. |

The chart ramp is the *only* place multiple hues coexist, and only to distinguish data series —
never as UI decoration. Series must also be distinguishable without color (label/pattern) per
[Accessibility](../design/12_Accessibility.md).

# Decision Rationale

- **HSL variables** make lightness/tint adjustments legible and centralize theming; `hsl(var())`
  consumption keeps product code semantic.
- **Warm parchment over pure white** reduces glare for long research reading and gives the
  premium "paper" character; surfaces are warm off-white so they lift subtly, not glaringly.
- **Ink-navy over pure black** is softer, editorial, and still exceeds AA contrast on parchment.
- **Deepened emerald→teal** avoids a neon look that would read as trendy and cheapen the signal;
  depth reads as confident and timeless.
- **Amber warning replaces neon yellow** because yellow is nearly invisible on cream — a
  legibility-driven decision, not aesthetic.

# Usage Guidelines

- Reference **tokens/roles**, never raw hex, in product code.
- Text: `--foreground` for primary, `--muted-foreground` for secondary; never place body text on
  the accent tint.
- Primary action: navy (`--primary`) or the signature gradient for the single most important
  action per context — not both competing.
- Financial values: apply `bullish`/`bearish` to the value's direction, paired with a
  sign/indicator (never color alone).
- AI content: distinguish AI insight from source material using surface and the signature signal
  for AI affordances, while keeping AI calm and embedded (Constitution §8, §22). Source
  references use link/`brand` styling so evidence is always visibly reachable.

# Best Practices

- Build with paper + ink first; add the signal last, only where meaning demands it.
- Keep large fills neutral (canvas/surface/muted); saturate only small, meaningful marks.
- Validate every text/background pair against AA before shipping (see Accessibility).

# Anti-patterns

- Coloring UI chrome with the signature gradient (dilutes the signal).
- Using `bullish`/`bearish`/chart hues decoratively (breaks "color is meaning").
- Pure-white cards or pure-black text (breaks the warm-editorial identity).
- Conveying state by color alone (fails accessibility).
- Introducing new accent hues outside the reserved chart ramp without a CR.

# Accessibility Considerations

- **Contrast:** body text (`--foreground`) on canvas/surface meets AA (≥ 4.5:1); large text and
  essential UI meet ≥ 3:1. `--muted-foreground` is reserved for secondary text where its
  contrast remains AA-compliant at the sizes used.
- **Focus:** the deep-emerald `--ring` provides a visible, AA-contrast focus indicator on all
  interactive elements.
- **No color-only meaning:** financial direction, status, and chart series always carry a
  non-color cue. Full rules in [Accessibility](../design/12_Accessibility.md).

# Responsive Considerations

Color is identical across desktop, tablet, and mobile — no palette changes by breakpoint
(Constitution §18). Only the *amount* of surface vs. canvas shifts with density; roles do not
change.

# Future Scalability

- New semantic needs get a **new token/role**, reviewed for contrast and identity fit — never an
  inline color.
- A future dark theme (CR-VIS-04) would remap the same roles to a second token set, leaving all
  product references unchanged.
- The chart ramp can extend with additional accessible hues as data-viz needs grow, without
  touching the core identity.

# Constitution References

[Design Constitution](../design/00_Design_Constitution.md) §11 Visual, §18 Trust, §19
Anti-patterns, §22 Trust & Transparency; [Accessibility](../design/12_Accessibility.md)
Contrast & no-color-only rules; [Design System](../design/08_Design_System.md) color roles.
