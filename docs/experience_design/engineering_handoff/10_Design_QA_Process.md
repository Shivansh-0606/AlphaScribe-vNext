# AlphaScribe vNext — Design QA Process

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Doc** | M3 · Design QA Process (10) |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |

## Purpose

Define a **repeatable Design QA process** that verifies implemented UI against the frozen design — a gate
every component and screen passes before it ships. It makes "matches the design and is accessible" a
checkable, non-negotiable step, not a subjective opinion.

## Scope

Visual accuracy, component consistency, token compliance, accessibility, responsive behavior, motion
fidelity, cross-screen consistency. Applies to every component and (once built) every screen. **Out of
scope:** engineering code review (separate track, [01 §Review](01_Handoff_Guide.md#6-review-workflow)).

## Decision Rationale

- **A checklist gate** turns quality from heroics into process — the only thing that holds over a
  multi-year build across many engineers.
- **Two independent tracks** (engineering review + design QA) ensure neither correctness nor fidelity is
  assumed from the other.

## When Design QA runs

1. **Per component** — before a component merges (it becomes a reusable dependency; defects multiply).
2. **Per screen** — before a screen merges (assembly-level fidelity + cross-screen consistency).
3. **Release gate** — the [14 Final Checklist](14_Final_Handoff_Checklist.md) before a milestone/release.

## The QA Checklist (seven passes)

### Pass 1 — Visual Accuracy
- ☐ Matches the approved design (spacing, sizing, hierarchy, alignment) within tolerance.
- ☐ Correct type roles (no ad-hoc sizes), correct color roles, correct radius/elevation.
- ☐ Warm-paper/ink identity intact; signal used only where sanctioned; no pure white/black.

### Pass 2 — Component Consistency
- ☐ Uses the shared component (no bespoke one-off where a standard exists — §7.5).
- ☐ Variants/sizes/states match the M2 spec + [12 Mapping](12_Component_Mapping.md) names.
- ☐ Same element behaves identically everywhere it appears.

### Pass 3 — Token Compliance
- ☐ **No raw values** (hex/px/ms/z-index) — tokens only ([03](03_Design_Token_Mapping.md)); lint green.
- ☐ Color/spacing/radius/elevation/motion/focus all resolve to tokens.
- ☐ No new token introduced inline (would require a CR).

### Pass 4 — Accessibility ([06](06_Accessibility_Implementation_Guide.md))
- ☐ Keyboard-only walkthrough: fully operable, logical order, no trap, visible focus, focus returns.
- ☐ Screen-reader spot-check (NVDA/VoiceOver): roles/names/states, landmarks, live-region announcements,
  AI streaming considerate.
- ☐ Contrast AA; **no meaning by color alone** (non-color cue present); color-blind simulation OK.
- ☐ 200% zoom / 320px reflow with no clipping or horizontal page scroll; touch targets ≥ 44px.
- ☐ Reduced-motion honored losslessly.

### Pass 5 — Responsive ([04](04_Responsive_Implementation_Guide.md))
- ☐ Mobile/tablet/desktop/wide behave per the guide; structure constant, density adapts.
- ☐ Navigation parity (no destination lost); overlays adapt (sheet/full-screen); tables reflow/scroll
  without dropping data; reading measure preserved.

### Pass 6 — Motion Fidelity ([05](05_Motion_Specifications.md))
- ☐ Each animation matches its catalogue entry (trigger/duration/easing/purpose).
- ☐ Interruptible/reversible; no layout shift over read content; AI motion calm (no theatrics).
- ☐ Reduced-motion fallback verified; no info lost.

### Pass 7 — Cross-Screen Consistency
- ☐ Shared regions (header, nav, companion, source references) identical across screens.
- ☐ Frozen vocabulary used verbatim (Company Research, Research Session, Resume Session, Trusted AI).
- ☐ AI content visibly distinct from source everywhere; citations present on every AI claim.

## Tooling

- **Automated:** axe (a11y) + token-lint + visual-regression snapshots in CI (catch regressions cheaply).
- **Manual:** the keyboard/SR/reflow passes automation can't cover; a reviewer runs them from this
  checklist.
- **Evidence:** QA sign-off (with the checklist state) recorded on the PR/branch for audit.

## Defect handling

- A design defect is filed against the **implementation** (not the frozen design). If QA reveals the
  *design* is wrong/ambiguous, that is a **CR** ([13](13_Design_System_Governance.md)), not a silent code
  fix.
- Severity: a11y and trust (unsourced AI claim, lost work, color-only meaning) defects are **blocking**.

## References to Previous Milestones

Constitution §24 (Design Review Framework) · [Accessibility](../../design/12_Accessibility.md) ·
[States](../../design/13_States.md) · [M2 families](../Components/00_Component_System.md) · handoff docs [03]–[06], [12].

## Best Practices

- Run QA per component (cheap) so screen QA is mostly assembly + cross-screen.
- Keep the checklist in the PR template; make sign-off a required field.
- Automate the mechanical passes (token, contrast, visual-regression); reserve human time for keyboard/SR.

## Anti-patterns

- ✗ Merging with QA deferred. ✗ Fixing a design ambiguity in code instead of a CR. ✗ Treating automated
  axe as sufficient (it catches a minority). ✗ Signing off without the keyboard/SR pass.

## Engineering Considerations

- Wire the automated passes into CI as required checks; store visual-regression baselines from the
  approved Figma/screens once M2 Phases 4/5 land.

## Accessibility Considerations

Pass 4 is the largest and is **blocking** — this process is the operational guarantee behind Immutable Law
10. No exceptions.

## Future Maintenance

Add screen-level visual-regression baselines when M2 Phase 4/5 exist. Keep passes in sync with the frozen
specs (update via CR only). Governed by [13](13_Design_System_Governance.md).

---

*Experience Design Department · Milestone 3 · Document 10 of 14*
