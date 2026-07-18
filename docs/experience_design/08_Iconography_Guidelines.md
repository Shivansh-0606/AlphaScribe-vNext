# AlphaScribe vNext — Iconography Guidelines

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Version** | 0.1.0 |
| **Milestone** | M1 — Visual Foundation |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For iconography |

**Downstream Dependencies:** [Design Tokens](10_Design_Tokens.md) · [Illustration](09_Illustration_Guidelines.md) · Frontend implementation · `design/icons/`

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Experience Design | 📝 Draft | Icon style, sizing, usage, and accessibility defined around the project's established icon family. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Visual Language Guidelines](01_Visual_Language_Guidelines.md), [Color](02_Color_System.md), [Typography](03_Typography_System.md), [Shape](07_Shape_Radius_System.md), [Design Constitution](../design/00_Design_Constitution.md) |
| **Used By** | [Design Tokens](10_Design_Tokens.md), [Component Inventory](../design/09_Component_Inventory.md) styling |
| **Related Documents** | [Accessibility](../design/12_Accessibility.md), [Navigation Structure](../design/04_Navigation_Structure.md) |

---

# Purpose

Defines AlphaScribe's icon language — family, style, sizing, color, and usage rules — so icons
reinforce meaning and the calm, precise identity without clutter.

# Goals

- One consistent icon family and style across the product.
- Icons that clarify meaning (source, export, compare, AI, search) and never decorate.
- Accessible icon usage with labels and adequate targets.

# Design Principles

1. **Icons support meaning, not decoration** (Constitution §11, §19). Every icon earns its place.
2. **Consistent family and weight.** One outline family, one visual weight, sized from tokens.
3. **Pair with text for critical actions.** Icons never replace a required label for critical
   controls (Design System Iconography rule).
4. **Calm and precise.** Line icons that match the editorial-terminal crispness.

# Icon Family & Style

| Aspect | Guideline |
|--------|-----------|
| **Family** | The project's established icon library — **Phosphor Icons** — used as a single, consistent set. Do not mix icon libraries. |
| **Style** | Outline/line style at a consistent weight for the default UI; a heavier/filled weight is reserved for selected/active or high-emphasis states, applied consistently. |
| **Stroke** | Uniform stroke that reads crisply on parchment; optically balanced with `type` and `--border` hairlines. |
| **Grid** | Icons drawn on a consistent optical grid so they align with text and controls. |

Reusing the established Phosphor family avoids introducing a new dependency and keeps the
existing product coherent (Constitution: reuse before adding).

# Icon Sizing Tokens

| Token | Size | Use |
|-------|------|-----|
| `--icon-xs` | 14px | Inline with `--text-sm`/caption; dense contexts. |
| `--icon-sm` | 16px | Default inline with body/controls. |
| `--icon-md` | 20px | Standalone actions, nav items. |
| `--icon-lg` | 24px | Prominent actions, section markers. |
| `--icon-xl` | 32px | Empty-state / feature emphasis (sparingly). |

Icon size pairs with the adjacent type size and the spacing scale (icon-to-label gap =
`--space-1`/`--space-2`).

# Color

- Icons inherit text color by default (`currentColor`): `--foreground` for primary,
  `--muted-foreground` for secondary.
- The **signature signal** (emerald→teal / `brand`) is reserved for AI, verified/positive, and
  focus-relevant icons — used sparingly.
- Financial-direction icons pair with `bullish`/`bearish` **and** a directional shape (arrow),
  never color alone.

# Semantic Icon Roles (examples, not new features)

| Concept | Meaning conveyed |
|---------|------------------|
| Source / citation | Reach evidence behind an insight (Trusted AI). |
| AI / copilot | Embedded AI presence (calm, not a separate chatbot). |
| Compare | Add/enter comparison. |
| Export / download | Produce a research artifact (J-06). |
| Search | Discovery entry. |
| Resume | Resume Session (return to saved work). |

These label existing capabilities; iconography introduces no new features.

# Decision Rationale

- **Phosphor (established):** a comprehensive, neutral, precise outline set that suits the
  editorial identity and is already the project's icon dependency — reuse over addition.
- **Outline default, filled for active:** a clear, consistent state language that reads calmly
  and avoids visual noise.
- **currentColor + reserved signal:** keeps icons quiet by default and makes the emerald signal
  meaningful when it appears.

# Usage Guidelines

- Use a single family and weight; size from `--icon-*` tokens matched to adjacent type.
- Provide an accessible name for every meaningful icon; hide purely decorative icons from
  assistive tech.
- Never use an icon as the sole label for a critical/destructive action — pair with text.
- Keep icon-to-label spacing on the scale (`--space-1`/`--space-2`).
- Reserve the signature color for AI/verified/focus icons only.

# Best Practices

- Choose the most literal, unambiguous icon for a concept; consistency of metaphor across the
  product matters more than cleverness.
- Align icons optically with text baselines/centers.
- Prefer text labels in dense data contexts where icons could be ambiguous.

# Anti-patterns

- Mixing icon families or weights (unrefined, inconsistent).
- Decorative icons that add no meaning (Constitution §19).
- Icon-only critical actions without labels (accessibility + clarity failure).
- Recoloring icons arbitrarily or overusing the signature signal.
- Inconsistent sizing off the `--icon-*` scale.

# Accessibility Considerations

- Meaningful icons have accessible names; decorative icons are `aria-hidden`
  ([Accessibility](../design/12_Accessibility.md)).
- Icon-only controls carry an accessible label and meet minimum target sizing (with spacing).
- Icon color meets contrast against its surface; meaning never rests on color alone.
- Icons scale with the type/zoom system and remain crisp.

# Responsive Considerations

- Icon roles and family are constant across sizes; touch contexts may step up one size for
  target ergonomics without changing meaning.
- Icon+label pairs may collapse to icon-only *only* where an accessible label is retained and
  the meaning is unambiguous (e.g. condensed navigation).

# Future Scalability

- New concepts pick an existing-family icon and register a semantic role; the family stays
  singular.
- The `design/icons/` directory is reserved for any custom marks that the standard family
  cannot express (reviewed for style match) — unpopulated in this milestone.
- A custom AlphaScribe glyph set, if ever needed, would match the established stroke/grid so the
  identity stays coherent.

# Constitution References

[Design Constitution](../design/00_Design_Constitution.md) §11 Visual, §19 Anti-patterns, §22
Trust (source icons); [Accessibility](../design/12_Accessibility.md) icon labeling & targets.
