# AlphaScribe vNext — Experience Design System

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 0.1.0 |
| **Milestone** | M1 — Visual Foundation |
| **Owner** | Experience Design Department |
| **Approved By** | CTO |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | Yes — for the AlphaScribe visual design system |

**Downstream Dependencies:** Frontend implementation · Component styling · Design tokens ·
QA visual review · PRDs (visual acceptance criteria)

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Experience Design | 📝 Draft | Milestone 1 — Visual Foundation: README plus ten foundational visual-system documents. Grounds the system in the existing frozen theme. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Design Constitution](../design/00_Design_Constitution.md), [Design System](../design/08_Design_System.md), [Product Vision](../master-plan/02_Product_Vision.md), [Accessibility](../design/12_Accessibility.md), [States](../design/13_States.md) |
| **Used By** | Component Inventory styling, Frontend implementation, QA visual review, all future Experience Design milestones. |
| **Related Documents** | [Information Architecture](../design/03_Information_Architecture.md), [Navigation Structure](../design/04_Navigation_Structure.md), [Interaction Patterns](../design/10_Interaction_Patterns.md), [Responsive Behavior](../design/11_Responsive_Behavior.md) |

---

# Purpose

The Experience Design System defines **how AlphaScribe looks** — the visual language that
renders the approved product blueprint. The frozen Product Discovery and Product Design
documents define *what the product is, why it exists, and how users interact with it*. This
directory adds only the visual layer, in full compliance with the
[Design Constitution](../design/00_Design_Constitution.md).

It is the single source of truth for color, typography, spacing, grid, elevation, shape,
iconography, illustration, and the design tokens that unify them. It is complete enough for
Engineering to implement the visual system without ambiguity, while remaining
implementation-agnostic (tokens and rationale, not framework code).

# Scope

**In scope (Milestone 1):** the visual foundation — the ten documents listed below, and the
token system that expresses them.

**Out of scope:** product/UX/navigation/IA changes (frozen); new features; implementation code;
React components; high-fidelity screens; motion choreography beyond token-level intent;
illustration or icon assets (directories are reserved, unpopulated).

# Grounding: this system formalizes the existing identity

AlphaScribe already has an approved visual identity in the codebase theme (a warm-light,
editorial-fintech look: a cream parchment canvas, ink-navy type, and a single emerald→teal
signature accent, expressed as HSL CSS variables). **This milestone documents, justifies, and
extends that identity into a complete, scalable system — it does not invent a new palette or
contradict the established theme.** Where these documents state concrete values, they reflect
the existing token set so documentation and product stay in lockstep.

# Design Philosophy (what the visuals must communicate)

Per the Constitution, the visual language is **calm but alive, premium, AI-native,
trust-first, research-focused, emotionally engaging, spatially consistent, accessible,
responsive, and timeless.** It deliberately avoids trend-driven aesthetics so the product
still reads as premium years from now. Craft comes from refinement and restraint, never
decoration (Constitution §11, §14, §19).

We studied the *principles* — not the appearance — of information-dense, trusted, and crafted
products (editorial clarity, calm density, AI transparency, spatial layering). AlphaScribe
establishes its **own** recognizable identity: warm paper, ink, and a single confident
emerald→teal signal. It imitates nothing.

# Documentation Structure

| # | Document | Defines |
|---|----------|---------|
| 00 | [README](00_README.md) | Purpose, scope, structure, process, relationships (this file). |
| 01 | [Visual Language Guidelines](01_Visual_Language_Guidelines.md) | The overarching visual identity and how all elements combine. |
| 02 | [Color System](02_Color_System.md) | Semantic color palette, roles, contrast, financial signal colors, AI treatment. |
| 03 | [Typography System](03_Typography_System.md) | Type families, scale, weights, line height, tracking, roles. |
| 04 | [Spacing System](04_Spacing_System.md) | The spacing scale and rhythm rules. |
| 05 | [Grid System](05_Grid_System.md) | Layout grid, columns, gutters, reading width, breakpoints. |
| 06 | [Elevation & Shadow System](06_Elevation_Shadow_System.md) | Spatial depth, layering, elevation levels. |
| 07 | [Shape & Border Radius System](07_Shape_Radius_System.md) | Corner language, borders, edges. |
| 08 | [Iconography Guidelines](08_Iconography_Guidelines.md) | Icon style, sizing, usage, accessibility. |
| 09 | [Illustration Guidelines](09_Illustration_Guidelines.md) | Illustration role, style, restraint. |
| 10 | [Design Tokens](10_Design_Tokens.md) | The consolidated, canonical token catalogue all others feed into. |

Each document follows a fixed section set: **Purpose · Goals · Design Principles · Decision
Rationale · Usage Guidelines · Best Practices · Anti-patterns · Accessibility Considerations ·
Responsive Considerations · Future Scalability · Constitution References.**

# Relationships Between Documents

```
Design Constitution (frozen, governs everything)
        ↓
01 Visual Language Guidelines  (the identity)
        ↓
02 Color · 03 Typography · 04 Spacing · 05 Grid · 06 Elevation · 07 Shape   (the foundations)
        ↓
08 Iconography · 09 Illustration   (the applied assets language)
        ↓
10 Design Tokens   (consolidates all of the above into the single implementable source)
```

Every foundation document names the tokens it owns; **10 Design Tokens** is the union of them
and the artifact Engineering consumes. No document may introduce a value that does not resolve
to a documented token.

# Review Process

1. **Draft** (Experience Design) → 2. **Internal design review** (consistency, Constitution
compliance, accessibility) → 3. **Cross-document review** (token consistency across 01–10) →
4. **CTO approval** → 5. **Frozen baseline** → 6. **Engineering handoff**.

Changes after freeze follow the [Documentation Governance](../governance/Documentation_Governance.md)
Change Request process. These documents are subordinate to the frozen product baseline and the
Design Constitution; where a visual decision would require a change to any frozen product/UX
artifact, a **Change Request is raised — the frozen artifact is never edited here.**

# Engineering Awareness & Flagged Discrepancies (Change Requests)

The visual system is designed to be practical to implement with **CSS variables + a
utility/Tailwind pipeline**, which the codebase already uses (HSL CSS custom properties
consumed via `hsl(var(--token))`, plus a Tailwind config mapping semantic names to those
variables). The token model is framework-neutral and will hold regardless of the surrounding
stack.

The milestone brief named a target stack that **diverges from the frozen/actual project setup**.
Per the constraints, we do not silently adopt a contradicting stack; we flag these for CTO
decision and keep the documentation implementation-agnostic so it is valid either way:

| # | Brief states | Actual / frozen reality | Recommendation |
|---|--------------|-------------------------|----------------|
| **CR-VIS-01** | Next.js 15 | Frontend is Create React App via **craco**, React 19, **react-router** (per project guide) | Keep visual docs framework-neutral; if Next.js is genuinely intended, raise a platform CR — it is a product/engineering decision outside Experience Design's authority. |
| **CR-VIS-02** | shadcn/ui | Project rules state the repo **does not use shadcn/ui** (no `src/components/ui/`, no `cn()`) and must not reintroduce it | Do **not** predicate the visual system on shadcn. Tokens are consumed directly. If shadcn adoption is desired, it needs an explicit CR against the project guide. |
| **CR-VIS-03** | Tailwind CSS v4 | Repo uses a Tailwind 3-style `tailwind.config.js` (`theme.extend`, `darkMode: ["class"]`) | Token model works with either; if migrating to v4's CSS-first `@theme`, raise an engineering CR. Docs specify tokens, not the Tailwind version. |
| **CR-VIS-04** | (Dark Mode implied by prior briefs) | Single warm-light theme; deliberately no dark mode / no toggle (project guide + Design System §Dark Mode) | MVP is light-only; a dark theme, if ever wanted, is a governance CR — not defined here. |

These CRs change **no** frozen documentation; they record where the brief and the frozen
reality differ so the CTO can decide. All ten documents below remain valid under any of these
outcomes because they specify **tokens and intent**, not framework code.

# Best Practices for Using This System

- Consume **tokens only** — never hardcode a raw value in product code.
- Treat these documents as a set: a color decision that ignores contrast (02 + Accessibility)
  or a spacing decision that ignores the grid (04 + 05) is incomplete.
- When in doubt, prefer **restraint** — the Constitution rewards refinement over addition.

# Accessibility & Responsive Note

Accessibility (WCAG 2.1 AA) and responsive integrity are **requirements, not sections to skim**.
Every foundation document carries its own Accessibility and Responsive considerations, all
consistent with the frozen [Accessibility](../design/12_Accessibility.md) and
[Responsive Behavior](../design/11_Responsive_Behavior.md) specifications.
