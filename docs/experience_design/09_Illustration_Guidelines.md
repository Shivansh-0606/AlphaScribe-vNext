# AlphaScribe vNext — Illustration Guidelines

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Version** | 0.1.0 |
| **Milestone** | M1 — Visual Foundation |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For illustration |

**Downstream Dependencies:** [Design Tokens](10_Design_Tokens.md) · Frontend implementation · `design/illustrations/`

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Experience Design | 📝 Draft | Illustration role, style, and restraint defined, consistent with the calm editorial identity. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Visual Language Guidelines](01_Visual_Language_Guidelines.md), [Color](02_Color_System.md), [Iconography](08_Iconography_Guidelines.md), [Design Constitution](../design/00_Design_Constitution.md) |
| **Used By** | [Design Tokens](10_Design_Tokens.md), empty/onboarding states in [States](../design/13_States.md) |
| **Related Documents** | [Screen Inventory](../design/05_Screen_Inventory.md), [Accessibility](../design/12_Accessibility.md) |

---

# Purpose

Defines the role and style of illustration in AlphaScribe — where it is used, how it looks, and
how restraint keeps the product premium and research-focused rather than playful or decorative.

# Goals

- Use illustration sparingly and purposefully (empty states, onboarding, guidance).
- Keep illustration consistent with the calm, editorial, warm-paper identity.
- Never let illustration compromise clarity, trust, performance, or accessibility.

# Design Principles

1. **Illustration is supportive, never load-bearing.** Any information it conveys is also
   available as text (Design System Illustrations rule; Constitution §11).
2. **Restraint.** Illustration appears only where it genuinely helps orientation or warmth —
   primarily empty and onboarding states.
3. **On-identity.** Palette, line, and tone match the warm-paper, ink, single-signal system —
   editorial and calm, not cartoonish.
4. **Trust over delight.** For a financial research product, credibility outranks whimsy;
   illustration stays understated and professional.

# Where Illustration Is Used

| Context | Purpose |
|---------|---------|
| **Empty states** | Warm, encouraging orientation with a clear next step (Constitution §16; States → Empty). |
| **Onboarding / setup** | Gentle guidance through first-run and AI setup (J-01). |
| **First-run guidance** | Occasional, low-key visual explanation of a concept or affordance. |

Illustration does **not** appear in dense research, data, comparison, or report contexts, where
it would distract from content and trust.

# Style Guidelines

| Aspect | Guideline |
|--------|-----------|
| **Palette** | The system palette only — parchment ground, ink line, the emerald→teal signal used sparingly for a single accent. No off-palette colors. |
| **Line & form** | Line-forward, editorial, calm; consistent stroke that harmonizes with icons and hairline borders. |
| **Tone** | Understated and professional — never cartoonish, whimsical, or mascot-driven. |
| **Complexity** | Simple and light; a few purposeful shapes, generous space — performance- and identity-aware. |
| **Consistency** | One illustration style across the product; do not mix styles. |

# Decision Rationale

- **Sparing use:** research users value focus and trust; heavy illustration would read as
  consumer-app playful and undercut credibility (Personas; Strategy trust-first).
- **On-palette, line-forward:** keeps illustration coherent with the icon and type systems so it
  feels like one crafted product, not stock art.
- **Empty/onboarding focus:** these are the moments where warmth and orientation genuinely help,
  turning a blank or unfamiliar screen into an inviting next step (Constitution §16, Emotional
  Design §5).

# Usage Guidelines

- Reserve illustration for empty, onboarding, and occasional guidance contexts.
- Pair every illustration with a clear text message and action (illustration never carries the
  message alone).
- Keep assets light and in-palette; avoid detail that won't scale or that dates quickly.
- Store source/exported assets in `design/illustrations/` (reserved; unpopulated this milestone).

# Best Practices

- Prefer *one* calm, purposeful illustration over a busy scene.
- Reuse a small, consistent illustration vocabulary rather than bespoke art per screen.
- Test that the screen still fully works (and reads) with the illustration removed.

# Anti-patterns

- Decorative illustration in data/research/report contexts (distracts, erodes trust).
- Mascots, cartoons, or trend-driven styles (breaks the premium editorial identity).
- Off-palette or heavy, detailed art (identity and performance cost).
- Illustration that conveys essential information not also available as text (accessibility
  failure).

# Accessibility Considerations

- Illustrations are decorative/supportive: hidden from assistive tech when decorative, or given a
  concise text alternative when they convey guidance ([Accessibility](../design/12_Accessibility.md)).
- Essential information is always in text, never only in the image.
- Any motion in illustration respects reduced-motion (Constitution §14) and never flashes.
- Sufficient contrast for any illustrated element that must be perceived.

# Responsive Considerations

- Illustration scales gracefully and may be reduced or omitted on small contexts where space is
  better used for content — its absence never removes information (text carries meaning).
- Same style and palette across all sizes.

# Future Scalability

- A defined, small illustration set can grow within the same style rules; new assets are
  reviewed for identity and accessibility fit.
- `design/illustrations/` and `design/assets/` are reserved for future, governed population.
- Should richer illustration ever be warranted (e.g. marketing), it extends the same palette and
  line language rather than introducing a new style.

# Constitution References

[Design Constitution](../design/00_Design_Constitution.md) §11 Visual (restraint), §16 Density &
Readability, §5 Emotional Design (empty/onboarding warmth), §19 Anti-patterns; Design System
Illustrations guidance.
