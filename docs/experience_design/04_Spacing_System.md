# AlphaScribe vNext — Spacing System

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Version** | 0.1.0 |
| **Milestone** | M1 — Visual Foundation |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For spacing |

**Downstream Dependencies:** [Grid](05_Grid_System.md) · [Design Tokens](10_Design_Tokens.md) · Frontend implementation

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Experience Design | 📝 Draft | Spacing scale and rhythm rules established on a 4px base / 8px rhythm, consistent with the theme's 32px structural grid. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Visual Language Guidelines](01_Visual_Language_Guidelines.md), [Typography](03_Typography_System.md), [Design Constitution](../design/00_Design_Constitution.md) |
| **Used By** | [Grid](05_Grid_System.md), [Design Tokens](10_Design_Tokens.md) |
| **Related Documents** | [Design System](../design/08_Design_System.md), [Responsive Behavior](../design/11_Responsive_Behavior.md) |

---

# Purpose

Defines the spacing scale and the rules for applying it, so the product has a consistent,
premium rhythm and uses whitespace as a structural tool.

# Goals

- One spacing scale for all margins, padding, and gaps — no ad-hoc values.
- Rhythm and grouping that make dense research legible and calm.
- Alignment with the structural grid so spacing and layout reinforce each other.

# Design Principles

1. **Space is structure.** Grouping and calm come from space, not boxes or borders
   (Visual Language; Constitution §11).
2. **One scale.** All spacing derives from a single token scale; nothing off-scale.
3. **Rhythm over randomness.** Consistent steps create a predictable, premium cadence.
4. **Density with air.** Dense where research needs it, always with breathing room.

# The Scale

Base unit **4px**; primary rhythm **8px**. A single scale (rem-based; 1 step = 0.25rem = 4px).

| Token | rem / px | Typical use |
|-------|----------|-------------|
| `--space-0` | 0 / 0 | Reset. |
| `--space-1` | 0.25 / 4 | Hairline gaps, icon-to-label. |
| `--space-2` | 0.5 / 8 | Tight internal padding, compact rows. |
| `--space-3` | 0.75 / 12 | Control padding, small gaps. |
| `--space-4` | 1.0 / 16 | Default component padding / gap. |
| `--space-5` | 1.5 / 24 | Group separation. |
| `--space-6` | 2.0 / 32 | Section spacing (aligns to the 32px structural grid). |
| `--space-7` | 2.5 / 40 | Large section separation. |
| `--space-8` | 3.0 / 48 | Major layout blocks. |
| `--space-9` | 4.0 / 64 | Page-level rhythm / hero spacing. |
| `--space-10` | 6.0 / 96 | Generous editorial breathing room. |

# Decision Rationale

- **4px base / 8px rhythm** is the industry-proven grid for pixel-crisp alignment and easy
  mental math; it composes cleanly with the type scale and the **32px structural grid** already
  present in the theme (`grid-lines` uses 32px), so `--space-6` (32) is a natural section unit.
- **Rem-based** so spacing scales with user font-size preferences (accessibility) rather than
  fixing pixels.
- **A single scale** eliminates the drift that makes products feel unrefined; consistency *is*
  the premium quality here.

# Usage Guidelines

- Use **tighter steps (1–3)** for intra-component spacing, **mid steps (4–6)** for
  component/group spacing, and **larger steps (7–10)** for section and page rhythm.
- Express relationship through proximity: related items closer, distinct groups farther apart
  (reduces cognitive load — Constitution §7).
- Prefer **gap** (space between) over margins where possible for predictable rhythm.
- Align section spacing to `--space-6` (32) to harmonize with the structural grid.

# Best Practices

- Increase whitespace to signal calm and confidence in key moments (e.g. AI insight, primary
  action) rather than adding borders.
- Keep vertical rhythm consistent within a reading column so scanning feels effortless.
- Scale spacing *down a step* (not off-scale) in dense contexts like tables.

# Anti-patterns

- Off-scale values (e.g. 7px, 13px, 30px) — breaks rhythm and refinement.
- Using borders/dividers where space would group more calmly.
- Uniform spacing everywhere (no proximity grouping) — flattens hierarchy.
- Cramming to increase density at the cost of readability (Constitution §16).

# Accessibility Considerations

- Rem-based spacing scales with user zoom/font settings, preserving layout integrity.
- Adequate spacing supports touch-target sizing and prevents mis-taps
  ([Accessibility](../design/12_Accessibility.md); [Responsive Behavior](../design/11_Responsive_Behavior.md)).
- Sufficient separation aids readers with low vision and cognitive load.

# Responsive Considerations

- Section/page spacing steps **down one level** on smaller contexts to preserve content
  priority without cramping; intra-component spacing generally holds.
- Touch contexts maintain minimum spacing for target size; the scale never produces
  sub-minimum gaps around interactive elements.

# Future Scalability

- New spacing needs pick an existing step; if a genuinely new step is required it is added to
  the scale (reviewed), never used inline.
- The scale composes with future components and surfaces without redefinition.

# Constitution References

[Design Constitution](../design/00_Design_Constitution.md) §11 Visual (whitespace, rhythm,
breathing room), §7 IA (proximity/grouping), §16 Density & Readability; grounded in the theme's
32px structural grid.
