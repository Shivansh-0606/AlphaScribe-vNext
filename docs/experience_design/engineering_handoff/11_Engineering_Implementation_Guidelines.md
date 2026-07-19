# AlphaScribe vNext — Engineering Implementation Guidelines

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Milestone / Doc** | M3 · Engineering Implementation Guidelines (11) |
| **Owner** | Experience Design Department (for Engineering) |
| **Last Updated** | 2026-07-18 |

## Purpose

Give Engineering a **sequenced plan**: what to build first, in what order, what depends on what, where the
risk concentrates, and how to validate — so implementation proceeds without stalling on missing
foundations or building things out of order. This is guidance for *sequencing and risk*, not architecture
(Engineering owns architecture within the design contract).

## Scope

Implementation priorities, component implementation order, screen implementation order, dependency mapping,
risk areas, validation process. **Out of scope:** code, framework internals, and the ⚠-gated components
(Portfolio/News/Timeline) pending CRs.

## Decision Rationale

- **Foundation-first, dependency-ordered** build prevents the expensive retrofit where components are made
  before tokens/a11y exist and later reworked.
- **Trust/AI + best-effort-data paths are front-loaded** in risk because they are where the product's
  differentiator (and its worst failure modes) live.

## 1. Implementation Priorities (phases)

```
P0 Foundation      tokens (03) + a11y harness (06) + Motion/reduced-motion provider + shadcn setup bound to tokens
P1 Primitives      Families 01–03, 05–07 foundation wrappers (Button…Toast) — the reusable base
P2 Navigation/Layout  Family 04 + the 5 layout templates (needs M2 Phase 3)
P3 AI components   Family 08 (streaming, citations, companion) — trust-critical
P4 Research components  Family 09 (compositions) — needs P1–P3
P5 Screens         SCR-01…11 assembled from approved layouts+components (needs M2 Phase 4)
P6 Prototypes/flows validation of journeys J-01…J-06 (needs M2 Phase 6)
```

**P0 is safe to start now** — it depends only on frozen M1 tokens + the frozen Accessibility spec, both
present. P2/P5/P6 depend on M2 Phases 3–7 (paused) and should not start until those artifacts exist.

## 2. Component Implementation Order

Within P1→P4, build in dependency order (a component ships only after its dependencies pass QA):

```
Button, IconButton, Input, Textarea, Label/Icon
  → FormField (Input+RHF+Zod), Checkbox/Radio/Switch/Select/DropdownMenu
  → Badge, Chip, Avatar, Card, Table, Skeleton, Loader, Progress, Toast(sonner)
  → Tooltip, Popover, Dialog, Drawer/Sheet
  → Tabs, SegmentedControl, Breadcrumbs, Pagination, Sidebar, GlobalNav, GlobalHeader
  → SourceReference, Citation, SourcePreview, EvidenceCard, ConfidenceIndicator
  → PromptComposer, AISuggestions, AIThinking, AIStream, AIResponseCard, AIActionToolbar
  → MetricStat, KPITiles, StatementTable, ChartFigure, CompanyHeader/Card, ComparisonColumn,
    FilingViewer, ReportViewer, AISummary, WatchlistItem
```

## 3. Screen Implementation Order

Once layouts + components exist, order screens by dependency + value (Screen Inventory IDs):

```
SCR-02 Auth → SCR-03 Onboarding/AI Setup   (gate: everything requires a session + AI access)
SCR-04 Workspace Home → SCR-05 Search       (entry + discovery)
SCR-06 Company Research                      (the core value; largest composition)
SCR-07 Comparison → SCR-08 Learning/Filing  (derived from Company Research)
SCR-10 Report Viewer → SCR-09 Research Library (preserve/resume)
SCR-11 Settings → SCR-01 Landing            (support + public)
```

Rationale: build the auth/AI-access gate first (nothing works without it), then the entry→core→derived→
preserve flow that mirrors journeys J-01→J-06.

## 4. Dependency Mapping (key)

| Layer | Depends on | Blocks |
|-------|-----------|--------|
| Tokens (P0) | M1 Design Tokens (frozen ✅) | everything |
| A11y harness (P0) | Accessibility spec (frozen ✅) | every component |
| Primitives (P1) | P0 | AI/research/screens |
| Layouts (P2) | Primitives + **M2 Phase 3 (pending)** | screens |
| AI (P3) | Primitives + streaming infra + Trusted-AI backend | research/screens |
| Research (P4) | P1–P3 + TanStack Query data (best-effort sources) | screens |
| Screens (P5) | P1–P4 + **M2 Phase 4 (pending)** | prototypes |

**Backend dependencies** (existing FastAPI/LangGraph/Mongo per project guide): AI streaming, source
retrieval, best-effort external data (BSE/yfinance) — their **Partial Failure/Timeout** contract
([States]) must be implemented on the client, not assumed away.

## 5. Risk Areas (front-load attention here)

| Risk | Why | Mitigation |
|------|-----|-----------|
| **AI streaming + citation attach** (Family 08) | trust-critical; partial output, sources attaching, considerate SR announcements | build as a P3 vertical slice early; test interrupt/timeout retains partials; never ship an unsourced claim |
| **Best-effort data / Partial Failure** | external sources fail; must degrade, not crash (§Vision) | implement Partial Failure/Timeout states first-class in every data component (Family 09) |
| **Never lose work** (Law 6) | resume session, error/nav preserving context | client state (Zustand) + persistence design must guarantee no-loss across nav/error/timeout |
| **Token/no-raw-values discipline** | drift erodes the whole system | lint gate + Design QA Pass 3 from day one |
| **A11y at scale** | easy to regress across many screens | CI axe + per-component keyboard/SR tests from P1 |
| **Stack decision (CR-VIS-01/02)** | Next.js/shadcn vs CRA unresolved | keep components token-driven + primitive-wrapped so a swap is localized |
| **Non-modal AI companion reflow** | must reflow, not overlap, desktop content (Dir. C) | validate layout at desktop early; it's a common overlay mistake |

## 6. Validation Process

- **Per PR:** engineering review + Design QA ([10](10_Design_QA_Process.md)) + a11y CI + token lint.
- **Per phase:** a vertical slice demoed against the relevant journey (e.g. P3 → an AI Q&A with citations
  end-to-end) before scaling the phase out.
- **Per milestone:** the [14 Final Checklist](14_Final_Handoff_Checklist.md).
- **Gate:** no unsourced AI claim, no lost-work path, no color-only meaning, no raw values — these are
  blocking everywhere.

## References to Previous Milestones

[Screen Inventory](../../design/05_Screen_Inventory.md) · [User Journeys](../../design/02_User_Journeys.md) ·
[Component Inventory](../../design/09_Component_Inventory.md) · [States](../../design/13_States.md) ·
handoff [02], [03], [06], [12]; Constitution Laws 3–6, 8, 10.

## Best Practices

- Ship P0 + one primitive + one AI slice as an end-to-end vertical before breadth.
- Treat Partial Failure/Timeout/empty as first-class, designed states — not error afterthoughts.
- Keep the stack-swap surface small (wrappers) until CR-VIS is resolved.

## Anti-patterns

- ✗ Building components before tokens/a11y. ✗ Screens before components pass QA. ✗ Assuming external data
  always succeeds. ✗ Building ⚠-gated components pre-CR. ✗ Deferring a11y/token discipline "until later."

## Engineering Considerations

- Next.js App Router: server components for read-heavy surfaces (statements/filings), client for
  interactive/AI; TanStack Query for all server state; Zustand for UI/session state; RHF+Zod for forms.
- Streaming: design the client stream handler + reduced-motion + considerate SR announcement together.

## Accessibility Considerations

A11y harness is P0, not a phase-end pass; every phase's validation includes the keyboard/SR passes. The
journey-level success measure ([06](06_Accessibility_Implementation_Guide.md)) is part of P6 validation.

## Future Maintenance

Update the order/dependency map when M2 Phases 3–7 land (unblocks P2/P5/P6) and when CR-VIS resolves.
Governed by [13](13_Design_System_Governance.md).

---

*Experience Design Department · Milestone 3 · Document 11 of 14*
