# AlphaScribe vNext — Icon & Illustration Asset Guide

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Doc** | M3 · Icon & Illustration Asset Guide (07) |
| **Owner** | Experience Design Department |
| **Design source (frozen)** | [Iconography](../08_Iconography_Guidelines.md) · [Illustration](../09_Illustration_Guidelines.md) |
| **Last Updated** | 2026-07-18 |

## Purpose

Tell Engineering **which assets exist, where they come from, how to name/version/use them** — icons,
illustrations, and the logo — so no one guesses an icon, invents an illustration, or misuses the brand
mark. Asset restraint is part of the identity (Constitution §11, §19): assets carry meaning, never
decoration.

## Scope

Icons, illustrations, logo, formats, naming, versioning, usage rules. **Out of scope:** raster export
mechanics (that's [08 Asset Export Standards](08_Asset_Export_Standards.md)) and Figma library structure
([09](09_Figma_Organization_Guide.md)).

## Decision Rationale

- **A single icon library (Phosphor)** — already the codebase standard — gives one coherent line/weight
  and avoids a mixed-metaphor icon set (a common trust-eroding inconsistency).
- **Illustration is deliberately minimal** — AlphaScribe is a research instrument, not a marketing site;
  restraint keeps it premium and timeless (Illustration Guidelines).

## 1. Icons

- **Library:** **`@phosphor-icons/react`** (frozen codebase standard). Do **not** mix in another icon set
  or hand-draw one-offs; a needed-but-absent icon is chosen from Phosphor or raised as a CR.
- **Style/weight:** one consistent weight across the app (per [Iconography](../08_Iconography_Guidelines.md));
  size to the adjacent text; align optically.
- **Color:** `currentColor` (inherits ink/muted/signal from context) — icons are not independently colored
  except where a token semantically applies.
- **Meaning mapping** (examples, authoritative list in Iconography): source/citation, export, compare,
  AI/presence, search, add/remove (watchlist), expand/collapse, close, more.
- **Usage rules:** decorative icons `aria-hidden`; meaningful icons carry a label (never the sole carrier
  of a critical label — pair with text where the action is critical); consistent icon = consistent
  meaning everywhere.

## 2. Illustrations

- **Role:** supportive and rare — empty states, onboarding moments, occasional reassurance. Never
  decorative filler (Illustration Guidelines; §19 empty states encourage action).
- **Style:** aligned to the warm-paper/ink identity and the signature emerald→teal; calm, editorial,
  restrained; no stock 3D, no trend gradients, no glassmorphism.
- **Palette:** the frozen tokens only (canvas, ink, muted, the one signal). No new hues.
- **Usage rules:** an illustration must earn its place (support comprehension or reassurance) and always
  pair with a text message and a next step (empty/error states never rely on art alone).
- **Directory:** `design/illustrations/` (source) → exported to `public/assets/illustrations/` per [08].

## 3. Logo

- **Usage:** the AlphaScribe wordmark/mark in the Global Header (public + authenticated) and export/report
  templates; consistent placement (Navigation/Header rules).
- **Clear space & min size:** maintain adequate clear space; never crowd or scale below legibility
  (specifics in the Figma logo component / brand sheet).
- **Color:** ink on paper by default; the signature gradient only for the sanctioned mark treatment —
  never recolored ad-hoc.
- **Anti-usage:** don't stretch, recolor outside the sanctioned set, add effects, or place on low-contrast
  backgrounds.

## 4. Formats (summary; mechanics in [08])

| Asset | Primary format | Notes |
|-------|----------------|-------|
| Icons | Phosphor React components (SVG) | `currentColor`; no static PNG icons |
| Illustrations | **SVG** (optimized) | raster (PNG) only if an illustration genuinely can't be vector |
| Logo | **SVG** (+ favicon/app-icon raster set) | vector master; raster only for platform icon slots |

## 5. Naming & Versioning (summary; full rules in [08])

- **Naming:** `kebab-case`, semantic by meaning/role, not appearance (`empty-research.svg`, not
  `green-box.svg`).
- **Versioning:** assets are version-controlled in git alongside code; changes go through PR + Design QA;
  the design source of truth is the Figma library ([09]) — exports are generated from it, not hand-edited.

## References to Previous Milestones

[Iconography](../08_Iconography_Guidelines.md) · [Illustration](../09_Illustration_Guidelines.md) ·
[Color System](../02_Color_System.md) · [States](../../design/13_States.md) (empty/error) · Constitution §11/§19.

## Best Practices

- Reach for an existing Phosphor icon before anything custom; keep one weight.
- Keep illustration count low; every one paired with words and a next step.
- Treat the logo as immutable brand — sanctioned treatments only.

## Anti-patterns

- ✗ Mixed icon sets / hand-drawn one-offs. ✗ Decorative illustrations as filler. ✗ New hues in art.
- ✗ Recolored/stretched/effect-laden logo. ✗ Meaningful icon with no label. ✗ PNG icons where SVG works.

## Engineering Considerations

- Import Phosphor icons per-component (tree-shakeable); standardize a size/weight wrapper so usage is
  consistent and swappable.
- SVGs are inlined or referenced per [08]; optimize (SVGO) on export; ensure `currentColor` is preserved.

## Accessibility Considerations

- Decorative icons/illustrations `aria-hidden`; meaningful ones labeled. Illustration-bearing states still
  meet contrast and never convey the state by image alone (text + action always present).

## Future Maintenance

New icons/illustrations enter via the Figma library + PR + Design QA; the meaning map is updated in
[Iconography](../08_Iconography_Guidelines.md) via CR if a new semantic is introduced. Governed by
[13](13_Design_System_Governance.md).

---

*Experience Design Department · Milestone 3 · Document 07 of 14*
