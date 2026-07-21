# AlphaScribe vNext — Component Mapping

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Doc** | M3 · Component Mapping (12) |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |

## Purpose

Map **every approved design component** to its **intended frontend component**: the wrapper name, the
shadcn primitive (or native element) it wraps, its supporting libraries, its variants, states, and
responsive rule. This is the lookup table Engineering uses to scaffold the component layer with zero
naming or dependency ambiguity. **No code** — names and intent only.

## Scope

All 55 components (Families 01–09) + the 5 layout templates (from [Component Inventory Templates](../../design/09_Component_Inventory.md#templates);
detailed screens/layouts are M2 Phase 3, pending). **Out of scope:** implementation and the ⚠-gated
components (Portfolio/News/Timeline) beyond noting their gate.

## Reading the map

- **Design component** = the frozen name (M2 family + [Component Inventory](../../design/09_Component_Inventory.md) role).
- **Frontend component** = the AlphaScribe wrapper Engineering creates (the design name is the source of
  truth for the code name — keep them identical).
- **Wraps / deps** = shadcn primitive or native element + libraries (RHF+Zod forms, TanStack Query data,
  Zustand UI state, Motion animation, sonner toasts, recharts charts, Phosphor icons).
- **Variants / States** = verbatim from the M2 spec (and the Figma variant properties).
- **Responsive** = the one-line rule ([04 Responsive Guide](04_Responsive_Implementation_Guide.md) is authoritative).

Legacy-stack note (CR-VIS-01/02): if the CRA stack is kept, "shadcn primitive" → a native/`Radix`-free
equivalent; the wrapper name, variants, states, and token bindings are unchanged.

---

## Family 01 — Buttons

| Design | Frontend | Wraps / deps | Variants | States | Responsive |
|--------|----------|--------------|----------|--------|-----------|
| Button | `Button` | shadcn `Button` · Motion (micro) | Primary, Secondary, Quiet, Destructive × sm/md/lg | Default/Hover/Focus/Active/Disabled/Loading | ≥44px touch; primary may go full-width mobile |
| Icon Button | `IconButton` | shadcn `Button`(icon) · Phosphor · shadcn `Tooltip` | Quiet, Secondary, Primary, Destructive; Toggle | + Toggle-selected (`aria-pressed`) | 44px touch; tooltip→tap on touch |

## Family 02 — Text Inputs

| Design | Frontend | Wraps / deps | Variants | States | Responsive |
|--------|----------|--------------|----------|--------|-----------|
| Input | `Input` (in `FormField`) | shadcn `Input` · RHF+Zod | Text, Password, Search | Default/Focus/Filled/Invalid/Disabled/Loading | full-width in column; 44px |
| Search | `SearchField` | shadcn `Input`+`Command`+`Popover` · TanStack Query | Global, Company | +Loading/No Results (combobox) | header collapses→expand/sheet mobile |
| Textarea | `Textarea` | shadcn `Textarea` (auto-grow) | Plain, Composer, Auto-grow | Default/Focus/Filled/Invalid/Disabled | full-width; send above keyboard |

## Family 03 — Selection Controls

| Design | Frontend | Wraps / deps | Variants | States | Responsive |
|--------|----------|--------------|----------|--------|-----------|
| Checkbox | `Checkbox` | shadcn `Checkbox` · RHF+Zod | Single, Group, Indeterminate | Default/Hover/Focus/Checked/Indeterminate/Disabled/Invalid | label wraps; 44px |
| Radio | `RadioGroup`/`Radio` | shadcn `RadioGroup` · RHF+Zod | Standard, Card radio | Default/Hover/Focus/Selected/Disabled/Invalid | stacks; card full-width mobile |
| Switch | `Switch` | shadcn `Switch` · Motion (knob) | Setting (immediate) | Off/On/Hover/Focus/Disabled/Pending | 44px; state label persists |
| Select | `Select` | shadcn `Select` (native-backed) | Native, Custom listbox, Searchable | Default/Focus/Open/Selected/Disabled/Invalid/Loading | native picker/sheet mobile |
| Dropdown menu | `DropdownMenu` | shadcn `DropdownMenu` | Action, Account/overflow, Destructive section | Item states; Closed/Open | sheet mobile; 44px |

## Family 04 — Navigation & Wayfinding

| Design | Frontend | Wraps / deps | Variants | States | Responsive |
|--------|----------|--------------|----------|--------|-----------|
| Global Navigation | `GlobalNav` | Next `Link`+`usePathname` · Zustand | Full, Condensed, Drawer | Default/Current/Hover/Focus | rail→icon-rail→drawer; parity |
| Global Header | `GlobalHeader` | composes SearchField, DropdownMenu, Button | Public, Authenticated | Default | search collapses mobile |
| Tabs / Section Nav | `Tabs` | shadcn `Tabs` · Motion (indicator) | Underline, Scrollable | Default/Active/Focus | overflow→scroll; picker mobile |
| Segmented Control | `SegmentedControl` | shadcn `ToggleGroup`(single) · Motion | 2–3, up to 5 | Default/Hover/Focus/Selected/Disabled | →Select if too wide |
| Breadcrumbs | `Breadcrumbs` | shadcn `Breadcrumb` | Standard, Truncated | Default/Hover/Focus; current `aria-current` | →‹ Parent mobile |
| Pagination | `Pagination` | shadcn `Pagination` · TanStack Query | Numbered, Prev/Next, Load more, Infinite | +Current/Disabled/Loading | →Prev/Next mobile |
| Sidebar | `Sidebar` | shadcn `Sidebar`/`Sheet` · Zustand (collapse) | Nav, Contextual, Collapsible | Expanded/Collapsed/Hover/Focus | rail→icon→off-canvas sheet |

## Family 05 — Content & Data Display

| Design | Frontend | Wraps / deps | Variants | States | Responsive |
|--------|----------|--------------|----------|--------|-----------|
| Card | `Card` | shadcn `Card` · Motion (lift) | Static, Interactive, Selectable, Media | Default/Hover/Focus/Active/Selected/Loading/Empty/Error | grid→stack; padding steps down |
| Table | `Table`/`DataTable` | shadcn `Table` (+TanStack Table optional) · TanStack Query | Data, Statement, Comparison, Sortable, Selectable | Default/Loading/Empty/Partial Failure/Sort/row states | h-scroll + sticky; record-rows mobile |
| Chip | `Chip` | wrapped token · Motion | Filter, Input/removable, Choice, Static | Default/Hover/Focus/Selected/Disabled | wrap/scroll; 44px |
| Badge | `Badge` | shadcn `Badge` | Neutral, Bullish, Bearish, Warning, Verified, Count | Static | constant |
| Avatar | `Avatar` | shadcn `Avatar` | Initials, Icon, With-status | Static/interactive-when-trigger | constant |

## Family 06 — Overlays

| Design | Frontend | Wraps / deps | Variants | States | Responsive |
|--------|----------|--------------|----------|--------|-----------|
| Tooltip | `Tooltip` | shadcn `Tooltip` · Motion | Text, Definition | Hidden/Visible | tap on touch |
| Popover | `Popover` | shadcn `Popover` · Motion | Menu, Suggestions, Info/preview, Filter | Closed/Open/Focus-within | →bottom sheet mobile |
| Dialog | `Dialog` | shadcn `Dialog` · Motion · (RHF for form dialogs) | Confirmation, Form, Alert | Closed/Open/Loading/Error/Success | full-screen mobile |
| Drawer | `Drawer`/`Sheet` | shadcn `Sheet` · Motion · Zustand | Nav (modal), Contextual, AI companion (non-modal) | Closed/Open/Loading/Focus (+AI states) | side→sheet; companion reflows desktop |

## Family 07 — Feedback & Status

| Design | Frontend | Wraps / deps | Variants | States | Responsive |
|--------|----------|--------------|----------|--------|-----------|
| Toast | `Toast` | **sonner** | Success, Error, Info, Warning (+action/undo) | Enter/Visible/Paused/Dismiss | corner→top/bottom mobile |
| Notification | `Notification`/`Banner` | region banner / list | Inline banner, List item | Unread/Read/Dismissed/Action-pending | full-width; sheet list mobile |
| Progress | `Progress` | shadcn `Progress` · Motion | Indeterminate, Determinate, Stage | Active | full-width bars |
| Skeleton | `Skeleton` | shadcn `Skeleton` | Text, Metric, Table, Card, Chart | Loading→replaced | follows content layout |
| Loader | `Loader`/`Spinner` | wrapped · Motion | Inline, Region, Full-view | Active | centered in container |

## Family 08 — AI Components

| Design | Frontend | Wraps / deps | Variants | States | Responsive |
|--------|----------|--------------|----------|--------|-----------|
| Prompt Composer | `PromptComposer` | Textarea + IconButton + Chip · Zustand · Query(stream) | Company, Comparison, Learning | Default/Focus/Filled/Disabled/Sending | docks bottom; above keyboard |
| AI Suggestions | `AISuggestions` | choice Chips | Starter, Follow-up, Learner | Default/Hover/Focus/Selected/Loading | wrap/scroll |
| Thinking State | `AIThinking` | Motion · live region | Thinking, Gathering evidence, Stage | Active→Streaming/Error/Timeout | in companion/inline |
| Streaming Response | `AIStream` | Motion (stream pace) · Query stream · live region | — | Streaming/Complete/Interrupted/Timeout | measure preserved |
| AI Chat Bubble | `AITurn` | composes Response Card | User, AI, System/notice | Sent; AI states | threaded list |
| AI Response Card | `AIResponseCard` | SourceReference, Confidence, ActionToolbar · react-markdown | Summary, Copilot, Filing analysis, Learning | Thinking/Streaming/Loaded/Error/Timeout/Insufficient | reflows |
| Citation Card | `SourceReference` | Link · Phosphor | Inline citation, Source list item, Unavailable | Default/Focus/Unavailable | inline wrap; section mobile |
| Source Preview | `SourcePreview` | Popover/Drawer + SourceReference | Inline peek, Side preview, Filing anchor | Closed/Open/Loading/Unavailable/Error | popover→sheet mobile |
| Evidence Card | `EvidenceCard` | SourceReference group | Inline, Panel | Default/Loading/Complete/Partial | inline→drawer mobile |
| Confidence Indicator | `ConfidenceIndicator` | Badge/text | Qualitative | Static/Insufficient | inline |
| AI Action Toolbar | `AIActionToolbar` | IconButtons · sonner (confirm) | During-streaming, On-complete | Streaming/Complete/Disabled | row→overflow mobile |

## Family 09 — Research Components

| Design | Frontend | Wraps / deps | Variants | States | Responsive |
|--------|----------|--------------|----------|--------|-----------|
| Company Header | `CompanyHeader` | Badge, Button, Tabs · Query | Full, Condensed | Default/Loading/Partial/Sticky | condense on scroll; stack mobile |
| Company Card | `CompanyCard` | Card + ListItem · Query | Result, Recent, Picker | Default/Hover/Focus/Selected/Loading/Partial | grid→stack |
| Financial Metric Card | `MetricStat` | Card + SourceReference | Neutral, Bullish, Bearish, Sparkline, Compact | Default/Empty/Loading | reflows grid |
| KPI Tiles | `KPITiles` | compact MetricStat grid | Overview, Comparison | Default/Loading/Partial/Empty | 4/3/2→1 col |
| Financial Tables | `StatementTable` | Table + SegmentedControl · Query | Income, Balance, Cash Flow; annual/quarterly | Default/Loading/Empty/Partial Failure | h-scroll/record-rows |
| Chart Container | `ChartFigure` | **recharts** + data-table toggle · SegmentedControl | Revenue, Profit, Margin, Growth, Ratio | Default/Loading/Empty/Partial Failure | resize; table primary mobile |
| Analyst Summary Card | `AISummary` | = AIResponseCard (summary role) | Company summary | Thinking/Streaming/Loaded/Error | precedes figures |
| Comparison Card | `ComparisonColumn` | MetricStat + Table + Badge | Member, Add-placeholder | Default/Empty/Partial Failure/Loading | columns→h-scroll→stack |
| Filing Viewer | `FilingViewer` | AIResponseCard + SourceReference · Query | Filing content, Filing analysis | Default/Loading/Empty/Error/AI states | side-by-side→toggle |
| Report Viewer | `ReportViewer` | SourceReference + Button(export) | Report view (+serif PDF export) | Default/Loading/Error/Success/Timeout | single column; controls reachable |
| News Card ⚠ | `NewsCard` (gated) | Card + SourceReference | — | — | — · **[CR-002](../../governance/change_requests/CR-SCOPE-002_News.md)** |
| Research Timeline ⚠ | `ResearchTimeline` (gated) | ListItem sequence | Activity, Company history | Default/Empty/Loading/Error | **[CR-003](../../governance/change_requests/CR-SCOPE-003_Research_Timeline.md)** |
| Watchlist Item | `WatchlistItem` | ListItem + IconButton · Zustand (watchlist store) | Standard, Compact | Default/Hover/Focus/Loading/Empty/Partial | rows; 44px |
| Portfolio Card ⚠ | `PortfolioCard` (gated) | Card + MetricStat | — | — | **[CR-001](../../governance/change_requests/CR-SCOPE-001_Portfolio.md)** — do not build |

## Layout Templates (from Component Inventory; M2 Phase 3 pending)

| Design template | Frontend | Composition | Screens |
|-----------------|----------|-------------|---------|
| PublicTemplate | `PublicLayout` | GlobalHeader(public) · Main · Footer | SCR-01, 02 |
| SetupTemplate | `SetupLayout` | GlobalHeader · Main · Footer (nav suppressed) | SCR-03 |
| WorkspaceTemplate | `WorkspaceLayout` | GlobalHeader · GlobalNav · Main · Footer | SCR-04, 05, 09, 11 |
| ResearchTemplate | `ResearchLayout` | WorkspaceLayout + SectionNav + AI companion | SCR-06, 07, 08 |
| DocumentTemplate | `DocumentLayout` | WorkspaceLayout + linear doc + source panel + export | SCR-10 |

> Layout templates' full grid/sticky/scroll specs are M2 Phase 3 (pending); the composition and screen
> mapping above are frozen from the Component Inventory.

## Decision Rationale

- **Design name = code name** eliminates a whole class of ambiguity and makes Figma↔code review trivial.
- **Wrap-a-primitive rows** make dependencies explicit so scaffolding is mechanical, and a primitive swap
  (CR-VIS-02) touches one wrapper, not every screen.

## References to Previous Milestones

[M2 Component families](../Components/00_Component_System.md) · [Component Inventory](../../design/09_Component_Inventory.md) ·
[States](../../design/13_States.md) · [Navigation Structure](../../design/04_Navigation_Structure.md) · [02 Specs](02_Component_Specifications.md).

## Best Practices

- Scaffold in dependency order ([11](11_Engineering_Implementation_Guidelines.md)); keep variant/state
  prop unions 1:1 with this table and the Figma variants.

## Anti-patterns

- ✗ Renaming components in code. ✗ Variants/states not in this map. ✗ Building ⚠-gated rows before CR approval.

## Engineering Considerations

- `AISummary` = `AIResponseCard` in a role, not a separate component — don't fork it.
- Watchlist reuses the existing legacy watchlist store pattern (Zustand) — carry it forward.

## Accessibility Considerations

Each wrapper owns its a11y contract ([06](06_Accessibility_Implementation_Guide.md)); the map names the
primitive that provides the correct semantics (shadcn primitives are chosen partly for their a11y base).

## Future Maintenance

Update when M2 Phases 3–7 land (layout/screen detail) and when any CR changes a component. Governed by
[13](13_Design_System_Governance.md).

---

*Experience Design Department · Milestone 3 · Document 12 of 14*
