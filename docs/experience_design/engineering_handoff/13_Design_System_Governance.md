# AlphaScribe vNext — Design System Governance

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Doc** | M3 · Design System Governance (13) |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Related** | [Documentation Governance](../../governance/Documentation_Governance.md) · [CR Register](../../governance/change_requests/00_Change_Request_Register.md) |

## Purpose

Define how the AlphaScribe design system is **maintained, changed, versioned, and owned** after handoff —
so it stays coherent, trustworthy, and accessible across a multi-year build and many contributors. This
is the rulebook that keeps the frozen design and the living code from drifting apart.

## Scope

Future contribution rules, versioning, Change Request process, review requirements, ownership model,
deprecation strategy, documentation maintenance. Applies to the design system (tokens, components,
patterns, docs) and its Figma + code manifestations.

## Decision Rationale

- **Explicit governance** is the difference between a design system that compounds in value and one that
  rots into per-team forks. The cost of the process is far below the cost of drift.
- **CR-gated changes to frozen scope** protect the product's core promises (trust, a11y, focus) from
  erosion "one small decision at a time" (Constitution §Purpose).

## 1. Ownership Model

| Layer | Owner | Authority |
|-------|-------|-----------|
| Product scope, IA, navigation, features | Product (frozen) | change via CR + CTO |
| Design Constitution & Immutable Laws | Design (governing) | change only via governance CR + CTO |
| Visual system, tokens, components, motion, a11y requirements | **Experience Design** (frozen) | change via CR |
| Token *delivery*, component code, state/data/form architecture | **Frontend Engineering** | within the design contract |
| The design system as a shared asset | **Design System stewards** (a named Design+Eng pair) | triage CRs, maintain library + docs |
| Final adjudication / freeze | **CTO** | approves/rejects CRs |

**Bright line (from [01](01_Handoff_Guide.md#5-ownership-boundaries)):** Design decides *what it is / how it
looks & behaves*; Engineering decides *how to build it*. Ambiguity → CR.

## 2. Change Request (CR) Process

The single path for any change to frozen design/product scope (also used for the M2 scope items and the
CR-VIS stack flags):

```
1. Raise CR      problem, why, traceability (Strategy/Vision/IA/Nav/Roadmap), value, complexity, risks, recommendation
2. Triage        stewards assess impact + which frozen docs it touches
3. Review        design review (Constitution + a11y + token compliance) + eng feasibility
4. CTO decision  Approve / Reject / Defer  (recorded in the CR Register)
5. Apply         update the frozen doc(s) + Figma + tokens + code together; version bump
6. Communicate   publish notes; update dependents
```

- **CR is required for:** new/changed tokens, new components/variants, visual-language changes, new
  features/scope, navigation/IA changes, a second theme, or anything contradicting the Constitution.
- **CR is not required for:** implementation-internal choices that don't change design (perf, refactors,
  file structure).
- **Register:** all CRs tracked in [00_Change_Request_Register.md](../../governance/change_requests/00_Change_Request_Register.md)
  (open items: CR-SCOPE-001/002/003 scope; CR-VIS-01…04 stack).

## 3. Contribution Rules (adding to the system)

- **Reuse before adding** — a new component/variant must prove nothing existing serves the need (§7.5,
  §14 Immutable Law: nothing exists that doesn't earn its place).
- **Token-first** — new visual values are tokens in the owning doc, never inline literals.
- **Complete or not at all** — a new component ships with all its states, responsive behavior, a11y,
  motion, and docs (the M2 attribute set) or it doesn't ship.
- **Constitution-compliant** — passes the §24 review framework; no anti-patterns (§23).
- **Accessible by construction** — meets [06](06_Accessibility_Implementation_Guide.md) before merge.

## 4. Versioning

- **Semantic versioning** of the design system (library + tokens + docs): **major** = breaking token/
  component change (migration needed); **minor** = additive (new component/variant/token); **patch** =
  fixes/clarifications.
- **Figma library, token package, and docs share the version**; a change bumps all three together so they
  never diverge.
- **Changelog** maintained (what changed, migration notes, affected components/screens).

## 5. Review Requirements

Every change merges only with: **design review** (Constitution + tokens + a11y), **engineering review**
(correctness/types/perf), **Design QA** ([10](10_Design_QA_Process.md)), and — for frozen-scope changes —
**CTO approval**. Sign-offs recorded. A11y and trust defects are always blocking.

## 6. Deprecation Strategy

```
Mark deprecated  (doc + Figma + code annotation, with the replacement + reason + target removal version)
   → Migrate     dependents move to the replacement (tracked)
   → Confirm      no remaining references (grep/library usage)
   → Remove       in a major version; archived in Figma page 99
```

- Never hard-delete a used token/component; deprecate → migrate → remove.
- Deprecations are communicated in the changelog with a migration path and a removal version.

## 7. Documentation Maintenance

- **Docs are updated with the change, in the same CR** — never after the fact, never left to drift.
- The **frozen upstream is edited only via CR**; this handoff package (M3) is updated to match, not the
  reverse. Code that drifts from docs is a **defect**, not a reason to edit the docs.
- Keep the source-of-truth hierarchy ([00](00_README.md)) authoritative; when docs conflict, the higher
  one wins and the lower is corrected.

## References to Previous Milestones

[Documentation Governance](../../governance/Documentation_Governance.md) · [CR Register](../../governance/change_requests/00_Change_Request_Register.md) ·
Constitution §Purpose/§23/§24/§25 · [Component System](../Components/00_Component_System.md) · [01 Handoff Guide](01_Handoff_Guide.md).

## Best Practices

- Name design-system stewards (a Design+Eng pair) so CRs have an owner and triage doesn't stall.
- Bump Figma + tokens + docs + code together; a version that's true in one place and stale in another is
  the start of drift.
- Prefer deprecation over deletion; keep a clean changelog.

## Anti-patterns

- ✗ Editing frozen docs to match drifted code. ✗ Adding a component/variant without a CR + full spec.
- ✗ Hard-deleting used tokens/components. ✗ Version bump in one artifact but not the others. ✗ Resolving a
  design question in code instead of a CR.

## Engineering Considerations

- Automate drift detection where possible (token export diff Figma↔code; library-usage reports for
  deprecation).
- Gate merges on the required reviews in CI; record Design QA + CTO sign-off in the PR.

## Accessibility Considerations

Accessibility is a **standing acceptance criterion** of every CR and every version — a change that
regresses a11y cannot be approved (Immutable Law 10). Deprecations must not remove an accessible path
without an equal-or-better replacement.

## Future Maintenance

Revisit governance when the team scales (more stewards), when the stack decision lands, and at each major
version. This document itself changes via the CR process. It is the steady-state rulebook after the
Experience Design Department is frozen.

---

*Experience Design Department · Milestone 3 · Document 13 of 14*
