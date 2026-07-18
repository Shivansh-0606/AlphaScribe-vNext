# AlphaScribe vNext — Elevation & Shadow System

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Version** | 0.1.0 |
| **Milestone** | M1 — Visual Foundation |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For elevation, depth & layering |

**Downstream Dependencies:** [Design Tokens](10_Design_Tokens.md) · Frontend implementation · Overlays, panels, menus

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Experience Design | 📝 Draft | Elevation levels, shadow philosophy, and z-index layering defined for the warm-paper spatial model. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Color](02_Color_System.md), [Visual Language Guidelines](01_Visual_Language_Guidelines.md), [Design Constitution](../design/00_Design_Constitution.md) (§12 Spatial), [Design System](../design/08_Design_System.md) |
| **Used By** | [Design Tokens](10_Design_Tokens.md), [Shape](07_Shape_Radius_System.md) |
| **Related Documents** | [Interaction Patterns](../design/10_Interaction_Patterns.md), [States](../design/13_States.md) |

---

# Purpose

Defines how AlphaScribe expresses **spatial depth** — the layering of surfaces, elevation
levels, shadow treatment, and z-index ordering — realizing the Constitution's Spatial Design
philosophy (§12) with restraint.

# Goals

- Give the workspace a legible sense of foreground/background and focus.
- Establish a small, consistent elevation scale and a disciplined z-index order.
- Keep depth meaningful and calm — never decorative (Constitution §12, §19).

# Design Principles

1. **Depth is meaning.** Elevation communicates relationship and focus, not ornament.
2. **Paper, not glass.** The identity is warm paper; surfaces lift subtly through tone and
   soft shadow, not heavy drop-shadows or decorative blur.
3. **Restraint (ambient polish).** Just enough depth to give a sense of place; never enough to
   distract or reduce contrast (Constitution §12).
4. **Layer order is a system.** A single z-index scale governs stacking; no arbitrary values.

# Elevation Scale

Depth is expressed primarily through **surface tone + hairline border**, with **soft,
warm-tinted shadow** added only as elevation increases. Shadow values are tuned in build; the
levels and their *intent* are canonical.

| Token | Level | Surface & treatment | Use |
|-------|-------|---------------------|-----|
| `--elevation-0` | Base (canvas) | `--background` (parchment), no shadow | The paper ground; primary reading field. |
| `--elevation-1` | Raised surface | `--surface`, hairline `--border`, minimal/no shadow | Cards, content sections, panels. |
| `--elevation-2` | Contextual | `--surface`, hairline, subtle soft shadow | Embedded AI/source panels, hover-raised items. |
| `--elevation-3` | Overlay | `--popover`, soft shadow, clear separation | Menus, dropdowns, tooltips, drawers. |
| `--elevation-4` | Modal/Dialog | `--surface`, stronger soft shadow + scrim | Focused modal tasks (background inert). |

Shadows are **soft, low-opacity, warm-neutral**, never hard or colored. Depth increases
monotonically with focus/transience.

# Z-Index / Layering Tokens

A single ordered scale prevents stacking conflicts.

| Token | Value band | Layer |
|-------|-----------|-------|
| `--z-base` | 0 | Normal content flow. |
| `--z-raised` | 10 | Raised surfaces, sticky sub-headers. |
| `--z-nav` | 100 | Persistent header / global navigation. |
| `--z-drawer` | 200 | Contextual drawers (embedded AI/source side surfaces). |
| `--z-overlay` | 300 | Dropdowns, popovers, tooltips. |
| `--z-modal` | 400 | Modals/dialogs and their scrim. |
| `--z-toast` | 500 | Notifications/toasts (above all, transient). |

# Decision Rationale

- **Tone-and-border first, shadow second:** on a warm-paper canvas, subtle surface lift reads as
  premium and calm; heavy shadows would feel like generic material UI and clash with the
  editorial identity. This also keeps contrast intact (accessibility).
- **Warm-neutral soft shadow:** matches the paper world; a cool/hard shadow would look pasted-on.
- **Monotonic elevation with focus:** the most transient/important surfaces (modals, toasts) sit
  highest — depth mirrors attention (Constitution §12 focus management).
- **Explicit z-scale:** removes the classic "z-index arms race" and keeps layering maintainable.

# Usage Guidelines

- Use `--elevation-1` for most content surfaces; reserve higher levels for genuinely transient or
  focus-demanding surfaces.
- Pair elevation with the correct z-token — never hand-pick z-index values.
- Embedded AI/source panels sit at `--elevation-2` / `--z-drawer`: beside content, present but
  calm — never elevated like a separate app.
- Modals use `--elevation-4` with a scrim that renders the background inert (Interaction
  Patterns → Modals) while preserving underlying work (Constitution §7.4).

# Best Practices

- Prefer the *least* elevation that communicates the relationship.
- Keep shadow soft and subtle; if a shadow is doing decorative work, remove it.
- Use motion to make elevation changes feel continuous (a surface *rising*), per Constitution
  §14 — subtle, never theatrical.

# Anti-patterns

- Decorative or heavy drop shadows; neon/colored shadows (Constitution §19).
- Glassmorphism/blur used for style rather than genuine layering (the theme's subtle cell
  treatment is functional, not a license for decorative glass).
- Arbitrary z-index values outside the scale.
- Elevating everything (flattens the hierarchy that elevation exists to express).

# Accessibility Considerations

- Depth never reduces text contrast below AA; shadows/scrims must not lower legibility
  ([Accessibility](../design/12_Accessibility.md)).
- Overlays (menus, modals) manage focus correctly and are dismissible by keyboard (focus trap +
  restore) — a spatial concern with an accessibility contract.
- Depth is not the *only* signal of a relationship; grouping and labels reinforce it.

# Responsive Considerations

- Elevation semantics are constant across sizes; on mobile, side drawers may present as
  full-height contextual surfaces but keep the same elevation/z meaning.
- Motion for elevation respects reduced-motion (instant change, no lost information).

# Future Scalability

- New surface types map onto an existing elevation level; a genuinely new level is added to the
  scale (reviewed), never improvised.
- A future dark theme would re-tune shadow opacity/tone for a dark ground while keeping the same
  elevation and z-index roles.

# Constitution References

[Design Constitution](../design/00_Design_Constitution.md) §12 Spatial Design, §11 Visual, §14
Motion, §19 Anti-patterns; [Design System](../design/08_Design_System.md) Depth philosophy.
