# AlphaScribe vNext — Component Specifications (Engineering Handoff)

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Doc** | M3 · Component Specifications (02) |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Design source (frozen)** | [M2 Component families 00–09](../Components/00_Component_System.md) · [Component Inventory](../../design/09_Component_Inventory.md) |

## Purpose

Give Engineering the **implementation-ready specification** for every approved component. The
design-side spec (Purpose · Anatomy · Variants · States · Responsive · Accessibility · Motion · Token
usage) already exists in full in the **M2 component family docs**; this document does **not duplicate
it**. Instead it (a) points to the authoritative family spec, and (b) adds the three handoff-only
facets the milestone requires — **Content rules · Edge cases · Usage examples** — plus the
**implementation binding** (which shadcn primitive / which library) for the vNext stack.

## Scope

All 55 components across Families 01–09. **In scope:** the engineering addenda + implementation binding
per family. **Out of scope:** re-stating the frozen design spec (linked), and any redesign.

## How to read a component (the combined spec)

For any component, its **complete** specification = the M2 family entry **+** this document's addenda:

```
M2 family doc  →  Purpose · Anatomy · Variants · Sizes · States · Accessibility · Responsive · Token usage · Motion · Usage guidelines · Anti-patterns
   +
This doc (02)  →  Content rules · Edge cases · Usage examples · Implementation binding (shadcn/RHF/Zod/Query/Zustand/Motion)
   +
Cross-refs     →  Tokens [03] · Responsive [04] · Motion [05] · Accessibility [06] · Mapping [12]
```

## Universal engineering contract (applies to every component)

- **Wrap, don't consume raw.** Each component wraps a shadcn primitive (or a native element) and binds
  it to tokens ([03]), the shared state model ([Component System §4](../Components/00_Component_System.md#4-universal-state-model)),
  and its a11y obligations ([06]). Screens never import shadcn primitives directly.
- **Props express variant/size/state**, matching the M2 variant/size/state names verbatim (→ [12 Mapping](12_Component_Mapping.md)
  and the Figma variant naming). No visual variant exists in code that isn't in the design.
- **Controlled where forms/validation apply** (React Hook Form + Zod); **server data via TanStack
  Query**; **client/UI state via Zustand**. No component fetches or validates ad-hoc.
- **Reduced-motion + focus-visible are non-optional** and come from the foundation, not per-component.
- **Content rules** below govern copy/formatting; **edge cases** are the states Engineering must
  explicitly handle (empty/overflow/failure), all resolving to canonical [States](../../design/13_States.md).

---

## Family 01 — Buttons & Icon Buttons  ([spec](../Components/01_Buttons.md))
**Implementation binding:** shadcn `Button` wrapped as `Button`/`IconButton`; variants Primary/Secondary/
Quiet/Destructive map to the wrapper's `variant` prop (not shadcn's default names). Loading state ties
to the triggering mutation (TanStack Query `isPending`).

- **Content rules:** labels name the outcome ("Export report"), sentence case, no terminal punctuation;
  icon-only buttons require `aria-label` naming the outcome; one Primary per view/region.
- **Edge cases:** long label → wrap to `sm`/shorten with equal accessible name, never truncate to an
  ambiguous glyph; loading → reserve width (no reflow), button non-activatable + `aria-busy`; disabled
  with non-obvious reason → adjacent explanation.
- **Usage examples:** "Export report" (Primary) on Report Viewer; "Add to watchlist" (toggle IconButton,
  `aria-pressed`) on Company Header; "Stop" (Quiet) during AI streaming.

## Family 02 — Text Inputs  ([spec](../Components/02_Text_Inputs.md))
**Implementation binding:** shadcn `Input`/`Textarea` wrapped inside a `FormField` bound to **React Hook
Form + Zod**; Search wraps `Input` + shadcn `Command`/`Popover` for the combobox; Textarea auto-grow.

- **Content rules:** every field has a visible `<label>` (placeholder ≠ label); help text is a format
  example; error text is specific and non-blaming; password reveal labeled "Show/Hide password".
- **Edge cases:** invalid on submit → focus first error, keep entered value (never clear); async
  validation → in-field busy, not blocking; Search no-results → keep query + offer refine/broaden/clear
  ([No Results state](../../design/13_States.md#no-results)); Textarea max-length → counter warns before
  the limit, never silent truncation.
- **Usage examples:** email/password on Auth; global company Search (combobox) in the header; AI Prompt
  Composer (Textarea base, Enter-to-send / Shift+Enter newline).

## Family 03 — Selection Controls  ([spec](../Components/03_Selection_Controls.md))
**Implementation binding:** shadcn `Checkbox`/`RadioGroup`/`Switch`/`Select`/`DropdownMenu`, each wrapped
and bound to RHF+Zod (form controls) or an action handler (Dropdown menu = actions, not values).

- **Content rules:** every selected/checked state has a non-color cue; radio groups default to the
  recommended option (Managed AI is the frictionless default); switch label describes the *on* meaning.
- **Edge cases:** switch persistence failure → revert + explain (never a silent false state); Select
  long list → searchable + selected marked with check; Dropdown destructive item → confirmed + focus
  returns to trigger; indeterminate checkbox for partial groups.
- **Usage examples:** AI access mode (card RadioGroup: Managed vs BYOK) on Onboarding/Settings; period
  Select; row overflow DropdownMenu.

## Family 04 — Navigation & Wayfinding  ([spec](../Components/04_Navigation.md))
**Implementation binding:** Next.js App Router `Link` + `usePathname` drive current/`aria-current`;
shadcn `Tabs`/`NavigationMenu`/`Breadcrumb`; Sidebar collapse state in **Zustand** (persisted). **No
destination exists in code that isn't in [Navigation Structure](../../design/04_Navigation_Structure.md).**

- **Content rules:** destination labels use frozen IA domain names (Workspace Home, Research Library —
  not "Dashboard"); tabs map to IA content levels only; breadcrumbs reflect the true hierarchy.
- **Edge cases:** tab overflow → horizontal scroll (never ambiguous wrap); mobile → nav becomes a
  focus-trapped drawer with destination parity; current-location by indicator + `aria-current`, not
  color alone; sidebar collapsed → labels on hover/focus.
- **Usage examples:** Global Navigation rail (6 destinations); company Section Nav (Overview/Financials/
  Filings/AI Insights/Export); Library › Reports › [title] breadcrumb.

## Family 05 — Content & Data Display  ([spec](../Components/05_Content_Data_Display.md))
**Implementation binding:** shadcn `Card`/`Table`/`Badge`/`Avatar`; Chip is a wrapped token; interactive
cards are a single focusable control. Tables render server data via TanStack Query; **charts pair with a
data-table equivalent** ([09 Research](../Components/09_Research_Components.md)).

- **Content rules:** figures use `type.figure` tabular mono, decimal-aligned; every metric paired with
  meaning; Bullish/Bearish badges carry text (never color alone); avatars use a real name, not "avatar".
- **Edge cases:** table Partial Failure → flag failed cells ("unavailable"/"not comparable"), never
  silently blank; card at rest is flat (elevate only on hover/focus/selected); wide table → horizontal
  scroll with sticky header/first column; empty vs. zero (never fabricate "0" for "no data").
- **Usage examples:** Company result Card; financial StatementTable; "not comparable" Badge in Comparison.

## Family 06 — Overlays  ([spec](../Components/06_Overlays.md))
**Implementation binding:** shadcn `Tooltip`/`Popover`/`Dialog`/`Sheet`(drawer); **Motion** for
enter/exit; focus trap + return-to-trigger built into the wrappers; z-index/shadow from tokens.

- **Content rules:** tooltips are supplementary only (never essential/interactive content); dialog
  titles state the decision; destructive dialog primary is **not** the default-focused action.
- **Edge cases:** dialog submit error → handle **inside** the dialog, preserve input (never close-and-
  lose); Esc closes (except required decisions); mobile → popover→sheet, dialog→full-screen; the AI
  companion drawer is **non-modal on desktop and must reflow, not overlap, content** (Direction C).
- **Usage examples:** learner-term definition Tooltip; Source Preview Popover; irreversible-action
  confirmation Dialog; AI companion Sheet.

## Family 07 — Feedback & Status  ([spec](../Components/07_Feedback_Status.md))
**Implementation binding:** **sonner** for toasts (proven in the legacy app; keep unless a CR replaces
it); Skeletons as token-shaped placeholders; Progress determinate/stage for AI/export; live regions for
announcements. Loading tied to TanStack Query states.

- **Content rules:** toasts for outcomes (not blocking errors → use Error state); prefer Undo toast over
  confirm dialog; progress paired with a context label; skeletons never show fabricated values.
- **Edge cases:** error toast must not auto-dismiss before it can be read (pause on hover/focus); long/
  known work → determinate/stage + Timeout (never an endless spinner); reduced motion → static skeleton
  + static busy text (no info loss); persistent conditions (Offline/Partial Failure) → banner, not toast.
- **Usage examples:** "Report exported" success toast + Undo; metric-grid Skeleton; AI stage Progress
  (gathering→reasoning→resolving).

## Family 08 — AI Components  ([spec](../Components/08_AI_Components.md))  ⚠ trust-critical
**Implementation binding:** streaming via server streaming → **Motion**-paced reveal; conversation/
companion state in **Zustand**; AI requests via TanStack Query (streaming); **every claim carries a
reachable citation**; AI content visibly distinct from source. Governed by Constitution §8–9, Laws 3–5,8.

- **Content rules:** AI content labeled as AI; plain language; uncertainty stated honestly ("not enough
  evidence"); **no recommendations** (Law 4); confidence qualitative, never false-precision (Law 8);
  citations describe their target (never "source"/"click here").
- **Edge cases:** stream interrupted/timeout → **retain partial output** + retry (never lose it);
  completion → every claim sourced (block/flag any unsourced claim); no valid AI access → composer
  explains + routes to AI setup; unavailable source → flagged honestly, not dropped; SR announces
  streaming **considerately** (not per-character).
- **Usage examples:** Analyst Summary (AISummary) leading SCR-06 before figures; Copilot answer with
  inline citations + Evidence card; Thinking→Streaming in the companion.

## Family 09 — Research Components  ([spec](../Components/09_Research_Components.md))
**Implementation binding:** compositions of Families 01–08; server data via TanStack Query (best-effort
external → Partial Failure/Timeout states); charts via **recharts** + data-table equivalent. **Portfolio/
News/Timeline are gated behind [CRs 001/002/003](../../governance/change_requests/00_Change_Request_Register.md)
— do not implement until approved.**

- **Content rules:** explain before quantify (never a bare number); every figure/insight traceable;
  reports preserve reasoning + sources on export (Law 6); frozen vocabulary (Company Research, Research
  Session, Resume Session).
- **Edge cases:** best-effort data missing → Partial Failure flags, screen never collapses; Comparison
  "not comparable" announced; Report export must **never strip citations**; Company Header name = screen
  `h1`; KPI set stays complete on mobile (reflow, not drop).
- **Usage examples:** SCR-06 Company workspace (Header + KPI Tiles + Analyst Summary + StatementTable +
  FilingViewer); SCR-07 Comparison; SCR-10 Report Viewer.

---

## Decision Rationale

- **Reference-not-duplicate** avoids two divergent specs for one component (the classic drift that makes
  a handoff untrustworthy). The M2 family is the single design spec; 02 adds only the engineering delta.
- **Content rules + edge cases explicit** because these are where implementations silently diverge from
  intent (truncation, empty-vs-zero, losing input on error) — naming them removes the ambiguity.

## References to Previous Milestones

[M2 Component families](../Components/00_Component_System.md) · [Component Inventory](../../design/09_Component_Inventory.md) ·
[States](../../design/13_States.md) · [Interaction Patterns](../../design/10_Interaction_Patterns.md) · Constitution.

## Best Practices

- Build the M2 family spec + this addenda side-by-side per component; a component PR links both.
- Encode edge-case states as first-class UI, not afterthoughts — they are the trust surface.

## Anti-patterns

- ✗ A code variant not in the design. ✗ Consuming shadcn primitives raw in screens. ✗ Fabricating data
  for empty states. ✗ Losing user input on error. ✗ Building the ⚠-gated components before CR approval.

## Engineering Considerations

- Co-locate variant/size/state prop unions with the component; keep them 1:1 with Figma variant names
  ([09 Figma Guide](09_Figma_Organization_Guide.md), [12 Mapping](12_Component_Mapping.md)).
- Streaming and Partial Failure are the highest-risk implementations — see [11 Risk areas](11_Engineering_Implementation_Guidelines.md).

## Accessibility Considerations

Each family's distinctive a11y is in its M2 spec; the enforceable contract (keyboard maps, roles, live
regions, focus management) is [06](06_Accessibility_Implementation_Guide.md). No component is "done"
without it.

## Future Maintenance

When M2 Phases 3–7 land, screen-level usage examples expand here. New components enter via CR + a new
M2 family entry, then an addenda here. Governed by [13](13_Design_System_Governance.md).

---

*Experience Design Department · Milestone 3 · Document 02 of 14*
