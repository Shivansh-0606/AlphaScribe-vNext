# AlphaScribe vNext — Visual Language Guidelines

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Version** | 0.1.0 |
| **Milestone** | M1 — Visual Foundation |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For the overarching visual identity |

**Downstream Dependencies:** All Experience Design documents (02–10) · Frontend implementation

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Experience Design | 📝 Draft | Initial visual language for AlphaScribe, grounded in the frozen warm-light editorial-fintech identity. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Design Constitution](../design/00_Design_Constitution.md), [Design System](../design/08_Design_System.md), [Product Vision](../master-plan/02_Product_Vision.md), [README](00_README.md) |
| **Used By** | [Color](02_Color_System.md), [Typography](03_Typography_System.md), [Spacing](04_Spacing_System.md), [Grid](05_Grid_System.md), [Elevation](06_Elevation_Shadow_System.md), [Shape](07_Shape_Radius_System.md), [Iconography](08_Iconography_Guidelines.md), [Illustration](09_Illustration_Guidelines.md), [Design Tokens](10_Design_Tokens.md) |
| **Related Documents** | [User Personas](../design/01_User_Personas.md), [Accessibility](../design/12_Accessibility.md) |

---

# Purpose

This document defines AlphaScribe's **visual identity** — the recognizable character that every
foundation document (color, type, spacing, etc.) serves. It translates the
[Design Constitution](../design/00_Design_Constitution.md)'s experiential ambition (calm but
alive, premium, AI-native, trust-first) into a coherent visual direction, and sets the rules
by which all visual elements combine.

# Goals

- Establish one unmistakable identity, so any screen reads as *AlphaScribe*.
- Give downstream documents a shared north star, so color/type/space decisions cohere.
- Encode the Constitution visually: calm density, spatial depth, evidence-forward AI, restraint.
- Remain timeless and implementation-agnostic.

# Design Principles

1. **Editorial, not dashboard.** The product reads like a well-set research document — generous
   reading rhythm, clear hierarchy, quiet chrome — not a chart-dense control panel.
2. **Warm paper, ink, one signal.** A warm parchment canvas and ink-navy type form a calm
   ground; a single emerald→teal accent is the product's one confident signal.
3. **Calm but alive.** Stillness by default; life through responsiveness, spatial depth, and
   refined motion (Constitution §5, §6, §14) — never through decoration.
4. **Evidence forward.** The visual system always keeps sources reachable and AI content
   distinguishable from source material (Constitution §18, §22).
5. **Density with air.** Information-dense where research demands it, always with breathing room
   so density never becomes clutter.
6. **Restraint as craft.** Emphasis is scarce and therefore meaningful; premium comes from
   refinement, not addition (Constitution §11).

# Decision Rationale

- **Why warm-light, single theme:** the established identity is a warm parchment canvas that
  reduces glare for long reading sessions (research is a reading task, Personas P-01/P-02),
  with ink-navy for maximum legibility. A single light theme keeps one coherent identity and
  honors the frozen "single token set, no toggle" decision.
- **Why one accent (emerald→teal):** trust products earn credibility through restraint. One
  signature signal — used for primary emphasis, the AI/verified signal, and focus — reads as
  confident and calm; a multi-accent palette would read as generic SaaS.
- **Why editorial character:** the target personas research by reading; an editorial system
  optimizes comprehension and feels premium and timeless, unlike trend-driven UI.
- **Why sharp, structural edges (see [Shape](07_Shape_Radius_System.md)):** the identity leans
  on crisp, precise structure — an editorial-terminal precision — that signals rigor. This is a
  deliberate identity choice, not an omission.

# Usage Guidelines

- Treat the canvas as **paper**: content sits on warm ground; surfaces lift subtly to
  establish foreground/background (see [Elevation](06_Elevation_Shadow_System.md)).
- Reserve the **emerald→teal signature** for the product's few most meaningful moments: the
  primary action, the AI/verified/positive signal, and focus. Everywhere else, ink and paper
  carry the design.
- Lead with **type and space**, not color or ornament — hierarchy is built primarily through
  typographic scale and spacing rhythm (03, 04).
- Keep **AI visually embedded** in research context and always paired with a source path; never
  style AI as a separate, authoritative surface (Constitution §8, §9).
- Let **financial meaning** (bullish/bearish/warning) use its reserved semantic colors only for
  genuine signal, never decoration (see [Color](02_Color_System.md)).

# Best Practices

- Build a screen from **hierarchy first** (what matters, in what order), then apply color only
  where it carries meaning.
- Use **whitespace as structure** — grouping and calm come from space, not borders or boxes.
- Prefer **one strong focal point** per view (Constitution §7.1), supported by a calm field.
- Make **liveness felt through motion and depth**, applied with restraint and always removable
  without losing meaning.

# Anti-patterns

- **Multi-accent rainbow UI** — dilutes the single-signal identity; reads as generic.
- **Decorative gradients, glass, or shadow** for their own sake (Constitution §19) — depth and
  color must carry meaning.
- **Dashboard-ification** — packing a view with charts and widgets at equal weight; buries the
  research.
- **Pure-white, cold surfaces** — breaks the warm-paper identity and increases glare.
- **Ornamental motion** — anything that distracts from research (Constitution §14).

# Accessibility Considerations

The identity is built on high-legibility ink-on-paper contrast and never relies on color alone
for meaning. All foundation documents inherit the WCAG 2.1 AA requirement from
[Accessibility](../design/12_Accessibility.md); the visual language must make AA the easy
default (e.g. ink-navy on parchment, reserved semantic colors with text/shape reinforcement).

# Responsive Considerations

The identity is **constant across desktop, tablet, and mobile** — the same warm, calm, premium
character at every size (Constitution §18; [Responsive Behavior](../design/11_Responsive_Behavior.md)).
Only density and arrangement adapt; the paper, ink, signal, type, and rhythm do not change.

# Future Scalability

- The single-signal system leaves deliberate room to grow: additional data-visualization hues
  already exist as a reserved chart ramp ([Color](02_Color_System.md)) without touching the
  core identity.
- A future dark theme (should a CR ever approve one — see [README](00_README.md) CR-VIS-04)
  would be a *second token set* mapped to the same semantic roles, leaving this identity intact.
- The token architecture ([Design Tokens](10_Design_Tokens.md)) lets the identity extend to new
  surfaces (marketing, exports, future product areas) without redefinition.

# Constitution References

Aligns with the [Design Constitution](../design/00_Design_Constitution.md): §2 North Star
(calm, living, confident), §3 Personality, §5–§6 Emotional/Living Interface, §8–§9 AI, §11
Visual, §12 Spatial, §14 Motion, §18–§19 Trust/Anti-patterns, §22 Trust & Transparency.
