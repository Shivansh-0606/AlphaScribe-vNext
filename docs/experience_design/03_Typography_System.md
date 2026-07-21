# AlphaScribe vNext — Typography System

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 0.1.0 |
| **Milestone** | M1 — Visual Foundation |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For typography |

**Downstream Dependencies:** [Design Tokens](10_Design_Tokens.md) · Frontend implementation · Content styling

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Experience Design | 📝 Draft | Typography system formalized from the frozen IBM Plex families; defines scale, weights, line height, tracking, and roles. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Visual Language Guidelines](01_Visual_Language_Guidelines.md), [Design Constitution](../design/00_Design_Constitution.md), [Design System](../design/08_Design_System.md) |
| **Used By** | [Spacing](04_Spacing_System.md), [Grid](05_Grid_System.md), [Design Tokens](10_Design_Tokens.md) |
| **Related Documents** | [Accessibility](../design/12_Accessibility.md), [Information Architecture](../design/03_Information_Architecture.md) |

---

# Purpose

Defines AlphaScribe's typographic system — families, scale, weights, line heights, letter
spacing, and semantic roles — the primary instrument of hierarchy in an editorial,
research-focused product.

# Goals

- Maximize reading comfort and comprehension for a text-heavy research task.
- Build clear hierarchy primarily through type (not color or ornament).
- Provide a small, consistent, timeless scale that scales across the product.
- Support accurate financial figures via tabular/mono type.

# Design Principles

1. **Type carries hierarchy.** Structure comes first from size and weight, per the editorial
   identity (Visual Language §Design Principles).
2. **Two families, clear roles.** A humanist sans for reading and UI; a mono for figures, code,
   and precise labels — the "editorial-terminal" character.
3. **Readable rhythm.** Comfortable line height and measure; research is a reading task
   (Constitution §16 Density & Readability).
4. **Restraint.** A limited scale and few weights; consistency over variety.

# Type Families

| Token | Family | Role |
|-------|--------|------|
| `--font-sans` | **IBM Plex Sans** (system-ui, sans-serif fallback) | Body, UI, headings — the default reading and interface face. |
| `--font-mono` | **IBM Plex Mono** (ui-monospace fallback) | Financial figures, tabular data, code, and precise uppercase labels. |

**OpenType features:** the sans uses `font-feature-settings: "ss01","ss02","cv01"` (established
in the theme) for a refined, editorial letterform character. Mono is used with tabular figures
for aligned numeric columns.

# Font Weights

| Token | Weight | Use |
|-------|--------|-----|
| `--font-weight-regular` | 400 | Body text, most reading. |
| `--font-weight-medium` | 500 | Emphasis, UI labels, secondary headings. |
| `--font-weight-semibold` | 600 | Headings, strong emphasis, key figures. |
| `--font-weight-bold` | 700 | Display / highest-emphasis headings (sans only). |

Mono ships 400/500/600. Weights above the loaded set must not be synthesized.

# Type Scale (font-size tokens)

A restrained modular scale (rem-based; base body = 1rem ≈ 16px). Sizes are tokens, not inline
values.

| Token | Size (rem / px) | Role |
|-------|-----------------|------|
| `--text-2xs` | 0.625 / 10 | Uppercase mono micro-labels (see Label pattern). |
| `--text-xs` | 0.75 / 12 | Captions, metadata, dense table text. |
| `--text-sm` | 0.875 / 14 | Secondary body, UI controls. |
| `--text-base` | 1.0 / 16 | Primary body / reading text. |
| `--text-lg` | 1.125 / 18 | Lead paragraphs, emphasized body. |
| `--text-xl` | 1.375 / 22 | Heading 3 / section headings. |
| `--text-2xl` | 1.75 / 28 | Heading 2 / screen headings. |
| `--text-3xl` | 2.25 / 36 | Heading 1 / page titles. |
| `--text-display` | 3.0 / 48 | Landing/hero display (marketing surfaces). |

# Line Height

| Token | Value | Use |
|-------|-------|-----|
| `--leading-tight` | 1.15 | Display and large headings. |
| `--leading-snug` | 1.3 | Headings, short UI text. |
| `--leading-normal` | 1.55 | Body reading text (comfortable measure). |
| `--leading-relaxed` | 1.7 | Long-form explanations / learning content. |

# Letter Spacing (tracking)

| Token | Value | Use |
|-------|-------|-----|
| `--tracking-tight` | -0.01em | Large display/headings (optical tightening). |
| `--tracking-normal` | 0 | Body and most UI. |
| `--tracking-label` | 0.22em | Uppercase mono micro-labels (established `label-mono` pattern). |

# Semantic Type Roles

| Role | Family / Size / Weight / Leading | Notes |
|------|----------------------------------|-------|
| `type.display` | sans / display / 700 / tight | Marketing/hero only. |
| `type.h1` | sans / 3xl / 600 / snug | Page/screen title. |
| `type.h2` | sans / 2xl / 600 / snug | Section heading. |
| `type.h3` | sans / xl / 600 / snug | Subsection. |
| `type.body` | sans / base / 400 / normal | Primary reading text. |
| `type.body-strong` | sans / base / 600 / normal | In-body emphasis. |
| `type.small` | sans / sm / 400 / normal | Secondary/UI text. |
| `type.caption` | sans / xs / 400 / normal | Metadata, dates, source labels. |
| `type.label` | **mono / 2xs / 500 / snug**, uppercase, `tracking-label` | The signature micro-label (`label-mono`). |
| `type.figure` | **mono / (contextual) / 500**, tabular figures | Financial values and aligned numerics. |
| `type.code` | mono / sm / 400 | Code / raw data on `--code-bg`. |

# Decision Rationale

- **IBM Plex Sans + Mono:** an open, humanist-yet-precise pairing that reads as editorial and
  trustworthy (not trend-driven), with an excellent mono for financial figures — reinforcing the
  research/terminal character without imitating any product. Already the established theme.
- **Mono for figures:** financial accuracy is a trust concern; tabular mono aligns columns and
  makes numbers scannable (Personas; Constitution §22).
- **The uppercase mono micro-label:** a distinctive, restrained identity mark that labels
  sections/metadata precisely without adding visual weight.
- **Restrained scale (≈ 9 steps):** enough range for clear hierarchy, few enough to stay
  consistent and timeless.

# Usage Guidelines

- Establish hierarchy with **size and weight first**; use color only to add meaning, not rank.
- Keep body reading at `--text-base` with `--leading-normal`; use `--leading-relaxed` for
  long-form learning explanations.
- Use `type.figure` (tabular mono) for all financial values; align numeric columns on the
  decimal.
- Reserve `type.label` for short uppercase labels only — never for sentences.
- Respect the reading **measure** (see [Grid](05_Grid_System.md) max content width).

# Best Practices

- Sequential heading levels (h1 → h2 → h3) with no skips — visual *and* semantic order.
- Pair every metric value (`type.figure`) with its meaning (Constitution §7: explain before
  quantify).
- Limit line length to a comfortable measure for sustained reading.

# Anti-patterns

- Faux weights (synthesizing weights not loaded) — degrades craft and legibility.
- Using mono for long prose or sans for aligned figures.
- Building hierarchy with color instead of type.
- Tiny body text to fit more in — density must never sacrifice readability (Constitution §16).
- All-caps for anything but short labels (harms readability).

# Accessibility Considerations

- Body text meets AA contrast (see [Color](02_Color_System.md)); minimum comfortable body size
  is `--text-base` for reading contexts, with `--text-sm`/`--text-xs` reserved for secondary/
  metadata where legible.
- Respect user font-size / zoom: sizes are rem-based so they scale with user preferences; layout
  must reflow without clipping ([Responsive Behavior](../design/11_Responsive_Behavior.md)).
- Never convey meaning by weight/case alone without a textual cue.

# Responsive Considerations

- The scale is constant in role; larger display/heading sizes may step down one level on smaller
  contexts to preserve measure and rhythm — the *hierarchy* never changes, only the magnitude.
- Reading measure is maintained across breakpoints via the grid's max content width.

# Future Scalability

- New roles map onto existing size/weight tokens rather than introducing new sizes.
- Additional languages/scripts inherit the family fallbacks; the token roles remain stable.
- If a variable-font upgrade is adopted, weights map onto the same weight tokens with no role
  changes.

# Constitution References

[Design Constitution](../design/00_Design_Constitution.md) §11 Visual, §16 Density &
Readability, §7 IA principles (explain before quantify), §22 Trust; grounded in
[Design System](../design/08_Design_System.md) typography roles.
