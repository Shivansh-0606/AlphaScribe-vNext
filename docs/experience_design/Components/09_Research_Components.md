# AlphaScribe vNext — Component Family 09: Research Components

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Milestone / Phase** | M2 · Phase 2 — Core Components |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Inherits** | [Component System Foundation](00_Component_System.md) + Families 01–08 |
| **Frozen mapping** | [`MetricStat`](../../design/09_Component_Inventory.md#metricstat), [`StatementTable`](../../design/09_Component_Inventory.md#statementtable), [`ComparisonTable`](../../design/09_Component_Inventory.md#comparisontable), [`ChartFigure`](../../design/09_Component_Inventory.md#chartfigure), [`FilingViewer`](../../design/09_Component_Inventory.md#filingviewer), [`ReportDocument`](../../design/09_Component_Inventory.md#reportdocument), [`ListItem`](../../design/09_Component_Inventory.md#listitem), [`AISummary`](../../design/09_Component_Inventory.md#aisummary) |

> These are **compositions** of the primitives (Families 01–07) and AI components (08). They add no
> new primitives. **Scope note:** a research component must trace to the frozen
> [Screen Inventory](../../design/05_Screen_Inventory.md) / [IA](../../design/03_Information_Architecture.md).
> Where the M2 brief lists a component whose *capability* is not clearly in the frozen baseline, it is
> flagged **⚠ SCOPE** below — documented as a presentation pattern only, pending a Change Request to
> confirm the capability. Design must not invent product scope.

> **Two rules dominate this family** (Constitution §7, §16, §22): **explain before quantify** (never
> a number without its meaning) and **every figure/insight is traceable**. Financial figures use
> `type.figure` (tabular mono), decimal-aligned; direction is never color-only (▲/▼ + sign).

---

## Company Header ⟶ composes: Header pattern (SCR-06)

### Purpose
Identify the company under research and anchor its section navigation — the orienting masthead of the
Company Research workspace.

### Anatomy
`[ name · ticker/exchange · sector · size ] · [ key identity badges ] · [ primary actions: add to
watchlist / compare / export ] · [ Section Nav: Overview/Financials/Filings/AI Insights/Export ]`.
Flat, editorial masthead (Direction C).

### Variants
**Full** (workspace) · **Condensed** (sticky on scroll — compact identity + section nav).

### States
**Default · Loading (skeleton) · Partial (some identity data unavailable, flagged) · Sticky/condensed.**

### Accessibility
Company name is the screen's `h1`; section nav is the [Tabs/SectionNav](04_Navigation.md) pattern;
actions are labeled; sticky condensed retains the accessible name and nav.

### Responsive
Full masthead → condensed sticky header on scroll → stacked identity + scrollable section nav on
mobile. All sections reachable (parity).

### Token usage
`type.h1`/`type.label` (identity), `Badge`, Button/Icon Button (actions), `--border` (masthead rule),
`--z-nav` (sticky), Tabs tokens.

### Motion (signature)
Condense-on-scroll transition `--motion-duration-base` (continuity). Reduced motion → instant condense.

### Usage guidelines / Anti-patterns
- **Do** make the company name the h1; keep section nav mapped to IA levels only.
- ✗ A busy, chart-laden header (§23); ✗ adding sections/destinations beyond IA; ✗ actions that imply
  recommendations.

---

## Company Card ⟶ composes: interactive `Card` + `ListItem`

### Purpose
Represent a company as a scannable, selectable unit in results, recents, and comparison pickers — the
entry point into Company Research.

### Anatomy
`[ name · ticker · sector ] · [ one or two key figures with meaning ] · [ optional badge ] ·
[ primary action: Open / Add ]`. Interactive card (flat at rest, lifts on hover/focus).

### Variants
**Result card** (search) · **Recent card** (Workspace Home) · **Picker card** (add to comparison).

### States
**Default · Hover · Focus · Selected (picker) · Loading (skeleton) · Partial (missing figures flagged).**

### Accessibility
Single focusable unit with a clear name; primary action reachable; figures paired with meaning;
selected (picker) carries a non-color cue.

### Responsive
Grid → stacked list on mobile; figures may reduce to the single most relevant, never fabricated.

### Token usage
Interactive Card tokens; `type.figure` (figures), `type.caption` (meta), `Badge`, Button.

### Motion (signature)
Hover/focus lift (Card §); reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** show at most one–two meaningful figures with meaning; one primary action.
- ✗ Cramming many equal-weight metrics (mini-dashboard); ✗ figures without meaning; ✗ color-only signal.

---

## Financial Metric Card ⟶ maps to: `MetricStat` (Inventory Molecule)

### Purpose
Present **one financial metric with its meaning** and a source path — the atomic unit of "explain
before quantify" (§7, §22).

### Anatomy
`[ label (name) ] · [ value: type.figure ] · [ direction ▲/▼ + sign ] · [ meaning/explanation ] ·
[ SourceReference ]`.

### Variants
Per Inventory: **Neutral · Bullish · Bearish.** Plus **with sparkline** (uses [Chart Container](#chart-container-⟶-maps-to-chartfigure-inventory-organism)) and **compact** (KPI tile, below).

### States
Per Inventory: **Default · Empty (no data) · Loading (skeleton).** Distinctive: Empty explains "no
data" (not a fabricated 0); direction never color-only.

### Accessibility
Value and meaning read together as one unit; tone via text/▲▼ + sign, not color alone; source
reachable.

### Responsive
Reflows in metric grids; meaning may collapse to a tooltip/expand on the smallest sizes but is never
removed.

### Token usage
`type.figure` (mono tabular), `type.caption` (meaning), `bullish`/`bearish` (+ sign), `SourceReference`,
Card tokens.

### Motion (signature)
Skeleton→value cross-fade; optional count-up is **off by default** (can distract; only if it aids and
is reduced-motion-safe). Reduced motion → instant value.

### Usage guidelines / Anti-patterns
- **Do** always pair value with meaning and a source; show direction with sign + arrow.
- ✗ A number with no meaning (Inventory rule); ✗ color-only direction; ✗ fabricated value for "no data".

---

## KPI Tiles ⟶ composes: compact `MetricStat` grid

### Purpose
A tight, scannable row/grid of the few headline metrics for a company (e.g. revenue, margin, growth,
P/E) — summary-level, above detail (§7.2).

### Anatomy
A small grid of compact Metric Cards (label · figure · direction), optionally a mini-sparkline;
consistent rhythm; each tile still exposes meaning (via expand/tooltip) and a source.

### Variants
**Overview KPIs** (SCR-06) · **Comparison KPIs** (per company).

### States
**Default · Loading (skeleton grid) · Partial (missing tiles flagged) · Empty.**

### Accessibility
A labeled group; each tile the MetricStat pattern; meaning reachable; not color-only.

### Responsive
4/3/2 columns → single column on mobile; the *set* stays complete (no dropped KPIs), only reflows.

### Token usage
Compact MetricStat tokens; grid via `--space-*`; optional sparkline (Chart Container).

### Motion (signature)
Progressive reveal of tiles (summary-first) `--motion-duration-base`. Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** limit to the few headline KPIs; keep meaning reachable; lead the company view with these
  (summary before detail).
- ✗ A wall of tiles that becomes a dashboard (§23); ✗ meaning-less figures; ✗ inconsistent tile rhythm.

---

## Financial Tables ⟶ maps to: `StatementTable` (Inventory Organism)

### Purpose
Present financial statements (Income / Balance / Cash Flow; annual/quarterly) as accessible tabular
data — **after** summary and metrics in the hierarchy (§16).

### Anatomy
The [Table](05_Content_Data_Display.md) pattern specialized: period columns, line-item row headers,
tabular-mono decimal-aligned values, subtotals, a period [Segmented Control](04_Navigation.md)
(annual/quarterly), sticky header/first column.

### Variants
Per Inventory: **Income · Balance · Cash Flow**; **annual/quarterly**.

### States
Per Inventory: **Default · Loading (skeleton) · Empty · Partial Failure** (unavailable lines/periods
flagged, never silently blank).

### Accessibility
Full table semantics (caption, `scope`, header association); row/column keyboard nav; `aria-sort`
where sortable; figures paired with meaning; not color-only; accessible summary for large tables.

### Responsive
Horizontal scroll with sticky header/first column; mobile may reflow to per-line "record" rows
(label: value across periods) — **no data dropped** (§16, §18).

### Token usage
Table tokens; `type.figure`, `bullish`/`bearish`, `--border`, sticky via `--z-raised`.

### Motion (signature)
Skeleton→data; period switch settles `--motion-duration-base`. Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** place after summary/metrics; align on decimal; flag gaps; provide the period selector.
- ✗ A statement before the summary (violates summary-before-detail); ✗ silent omissions; ✗ a
  "wall of numbers" with no rhythm/meaning.

---

## Chart Container ⟶ maps to: `ChartFigure` (Inventory Organism)

### Purpose
Visualize financial data (revenue, profit, margin, growth, ratios) — **always paired with an
accessible data equivalent** (Inventory rule; §17). Built with `recharts` (project convention).

### Anatomy
`[ title · meaning ] · [ range/metric Segmented Control ] · chart · [ legend ] · [ accessible data
table toggle ] · [ SourceReference ]`. Uses the [chart ramp](../02_Color_System.md) only to
distinguish series.

### Variants
Per Inventory: **Revenue · Profit · Margin · Growth · Ratio**; line/bar as apt.

### States
Per Inventory: **Default · Loading (skeleton) · Empty · Partial Failure.** Distinctive: Empty/Partial
explain; the data-table equivalent is always available.

### Accessibility (distinctive — critical)
Series distinguishable **without color** (labels/patterns/markers — Color chart-ramp rule); an
equivalent data table is provided (toggle or adjacent); title/meaning present; described per
[Accessibility](../../design/12_Accessibility.md); keyboard-focusable data points where feasible.

### Responsive
Chart resizes; legend reflows; on mobile the data-table equivalent may be the primary presentation;
range selector preserved.

### Token usage
`--chart-1`…`--chart-5` (series only), `type.caption` (labels/meaning), `--border`/`--muted`
(axes/grid, low-contrast), Segmented Control, SourceReference.

### Motion (signature)
Series draw-in on load `--motion-duration-slow`, `--motion-ease-out` (once, removable). Reduced motion
→ static chart, no draw-in.

### Usage guidelines / Anti-patterns
- **Do** pair every chart with a data-table equivalent; distinguish series without color; state meaning.
- ✗ Color-only series; ✗ a chart with no accessible equivalent; ✗ decorative multi-hue where a single
  series suffices (chart ramp is for series, not decoration).

---

## Analyst Summary Card ⟶ maps to: `AISummary` (Inventory Organism)

### Purpose
The grounded, plain-language **AI summary** at the top of company insights — leads the view, precedes
figures, always sourced (SCR-06). This is the [AI Response Card](08_AI_Components.md) in its
"company summary" role.

### Anatomy / Variants / States / Motion
Per [AI Response Card](08_AI_Components.md#ai-response-card--maps-to-aisummary--copilotpanel-answer)
(Analyst/Company Summary variant): AI label · content · citations · Evidence · optional Confidence ·
AI Action Toolbar. States: **AI Thinking · Streaming · Loaded · Error.**

### Accessibility / Token usage
Per AI Response Card; **precedes figures**; readable linearly; sources reachable; visibly AI.

### Usage guidelines / Anti-patterns
- **Do** lead the company view with this before figures; always source it; keep it visibly AI and
  recommendation-free.
- ✗ Placing figures before the summary; ✗ an unsourced summary; ✗ any recommendation (Law 4).

---

## News Card ⟶ composes: `Card` + `SourceReference`   ⚠ SCOPE

### Purpose
Present a relevant news/filing-adjacent item with its source. **⚠ Trace to baseline:** confirm "news"
is within the frozen [Screen Inventory](../../design/05_Screen_Inventory.md)/IA scope; if AlphaScribe
sources only primary filings, "news" may be out of scope — documented here as a presentation pattern
pending CR confirmation.

### Anatomy
`[ headline ] · [ source · date ] · [ optional snippet ] · [ SourceReference to primary source ]`.

### Variants / States
**Standard · Compact.** States: **Default · Hover · Focus · Loading · Unavailable (flagged).**

### Accessibility / Responsive / Token usage / Motion
Per interactive [Card](05_Content_Data_Display.md) + [SourceReference](08_AI_Components.md); source
descriptive and reachable; reflows to list on mobile; hover/focus lift; reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** attach a primary source; keep neutral, non-hype framing (§15).
- ✗ Unsourced items; ✗ marketing/hype tone; ✗ presenting news as AI insight without provenance.
  **✗ Do not ship until scope confirmed.**

---

## Comparison Card ⟶ composes: `ComparisonTable` cell / per-company column

### Purpose
Present one company within a side-by-side comparison on comparable terms, flagging non-comparability
honestly (SCR-07).

### Anatomy
A per-company column/card of aligned MetricStats + identity + remove action, within the
[ComparisonTable](../../design/09_Component_Inventory.md#comparisontable); "not comparable" flags where
metrics don't align.

### Variants / States
**Member card · Add-member placeholder.** States per Inventory ComparisonTable: **Default · Empty (no
members) · Partial Failure (not comparable) · Loading.**

### Accessibility
Header-anchored comparison navigation; "not comparable" announced (not blank); remove action labeled;
figures paired with meaning; not color-only.

### Responsive
Columns → horizontally scrollable comparison → stacked per-company sections on mobile; comparability
flags preserved.

### Token usage
MetricStat + Table tokens; `Badge` ("not comparable"); Button (add/remove); SourceReference.

### Motion (signature)
Add/remove member settles `--motion-duration-base`. Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** flag gaps/non-comparability rather than hiding; members come from Company Research (derived
  domain); pair figures with meaning.
- ✗ Silently omitting non-comparable metrics; ✗ implying a "winner" (recommendation, Law 4).

---

## Filing Viewer ⟶ maps to: `FilingViewer` (Inventory Organism)

### Purpose
Present SEC/BSE filings and their **grounded AI analysis**, with analysis always anchored to the
filing (source traceability) — SCR-06, SCR-08.

### Anatomy
`[ filing nav: sections ] · [ filing content ] · [ AI analysis anchored to sections ] ·
[ SourceReference / anchors ]`. Split reading: filing on one side, anchored analysis on the other
(Direction C: page + summoned analysis).

### Variants
Per Inventory: **Filing content · Filing analysis.**

### States
Per Inventory: **Default · Loading · Empty (uncovered) · Error · AI Thinking/Streaming.**

### Accessibility
Navigable sections; analysis linked to source anchors (keyboard reachable); AI analysis visibly
distinct from filing text; announced considerately.

### Responsive
Side-by-side (desktop) → stacked/toggle between filing and analysis (mobile), analysis anchored to the
section; no content lost.

### Token usage
Reading tokens (`type.body`/`--leading-normal`), AI Response Card (analysis), SourceReference/anchors,
`--border` (section rules).

### Motion (signature)
Analysis streams anchored to the section (see [Streaming Response](08_AI_Components.md)); jump-to-anchor
scroll `--motion-duration-base`. Reduced motion → instant jump.

### Usage guidelines / Anti-patterns
- **Do** anchor every analysis claim to the filing; keep analysis visibly AI; navigable sections.
- ✗ Analysis not anchored to source (breaks traceability); ✗ AI analysis indistinguishable from the
  filing text; ✗ recommendations.

---

## Report Viewer ⟶ maps to: `ReportDocument` (Inventory Organism)

### Purpose
Present a grounded, source-backed research **report** with export — conclusion + reasoning + content
+ sources, preserving reasoning and sources on export (J-06) — SCR-10.

### Anatomy
`[ conclusion ] · [ reasoning ] · [ content sections ] · [ SourceReferences ] · [ Export ]`, in a
linear, editorial document (DocumentTemplate). This is the Broadsheet reading core, at its purest.

### Variants
Per Inventory: **Report view** (+ export/serif PDF template — the codebase's `ReportView.jsx` serif
export).

### States
Per Inventory: **Default · Loading · Error · Success (export) · Timeout.** Export preserves reasoning
and sources (Law 6).

### Accessibility
Linear reading order; headings sequential; sources reachable; export outcome announced; export never
strips citations.

### Responsive
Single readable column at every size (`--reading-max`); export controls reachable; sources as a
section on mobile.

### Token usage
Reading tokens (`type.h1..body`, `--leading-normal/relaxed`), SourceReference, Button (export),
`--reading-max`.

### Motion (signature)
Calm, minimal — progressive reveal of sections on load; export success = quiet Toast. Reduced motion
→ instant.

### Usage guidelines / Anti-patterns
- **Do** keep the report a linear, sourced document; preserve reasoning + sources on export.
- ✗ Export that drops sources/reasoning (Law 6); ✗ a report without traceable claims; ✗ recommendations.

---

## Research Timeline ⟶ composes: `ListItem` sequence   ⚠ SCOPE

### Purpose
Show the sequence of a user's research activity / a company's research history to support **Resume
Session** and continuity (J-06). **⚠ Trace to baseline:** confirm a "timeline" view exists in the
frozen Screen Inventory (vs. the Research Library list); documented as a presentation pattern over the
existing Research Sessions capability, pending CR confirmation.

### Anatomy
A vertical sequence of research events/sessions (subject · timestamp · resume action), grouped by
time; each item is the [ListItem](05_Content_Data_Display.md) "Research Session" variant exposing
**Resume Session**.

### Variants / States
**Activity timeline · Company research history.** States: **Default · Empty · Loading · Error.**

### Accessibility
An ordered, labeled list; each item focusable with subject + date; **Resume Session** labeled;
time grouping is textual.

### Responsive
Vertical list at every size; comfortable rhythm; reachable resume actions.

### Token usage
ListItem tokens; `type.caption` (timestamps); `--border` (connector, decorative/`aria-hidden`).

### Motion (signature)
Progressive reveal of items `--motion-duration-base` (continuity). Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** expose Resume Session on session items; use the frozen "Research Session" vocabulary.
- ✗ Inventing a new activity-tracking capability (**scope — CR required**); ✗ decorative timeline
  ornament without function.

---

## Watchlist Item ⟶ composes: `ListItem`

### Purpose
Represent a saved/followed company in a watchlist for quick return (backed by the codebase watchlist
store). Continuity — get back to companies the user cares about.

### Anatomy
`[ company name · ticker ] · [ one key figure + direction ] · [ open · remove ]`, the ListItem
"Company" variant with a remove (toggle) action.

### Variants / States
**Standard · Compact.** States: **Default · Hover · Focus · Loading · Empty (no watchlist) · Partial
(figure unavailable, flagged).**

### Accessibility
Focusable item with company name; open + remove labeled (remove toggles `aria-pressed` on the
[Icon Button](01_Buttons.md)); figure paired with meaning; not color-only.

### Responsive
List rows at every size; touch targets ≥ 44px; remove reachable.

### Token usage
ListItem tokens; `type.figure` (figure), Icon Button (remove/add — toggle), `Badge`.

### Motion (signature)
Add/remove settles `--motion-duration-base`; removed item collapses (removable without meaning loss).
Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** make add/remove a clear labeled toggle; show one meaningful figure with meaning; empty state
  invites adding a company.
- ✗ Ambiguous remove affordance; ✗ figures without meaning; ✗ color-only direction.

---

## Portfolio Card ⟶ composes: `Card` + `MetricStat`   ⚠ SCOPE

### Purpose
Summarize a grouping of companies/holdings the user tracks. **⚠ Trace to baseline:** "Portfolio" as a
capability (holdings, weights, valuation) is **not clearly in the frozen Screen Inventory/IA** — this
is documented as a presentation pattern only and **must not be built until a Change Request confirms
the capability.** If out of scope, it is dropped; if a watchlist-grouping only, it reduces to a
titled group of Watchlist Items.

### Anatomy (pattern, pending scope)
`[ portfolio/group name ] · [ member count ] · [ optional aggregate figures with meaning + source ] ·
[ open ]`, composing Card + MetricStat + ListItem.

### States / Accessibility / Responsive / Token usage / Motion
Per Card + MetricStat + ListItem patterns; figures paired with meaning and sources; not color-only;
reflows to list on mobile.

### Usage guidelines / Anti-patterns
- **⚠ Do not implement without a CR** confirming Portfolio scope and its data sources.
- ✗ Inventing holdings/valuation capability in design; ✗ any aggregate that implies performance
  advice (Law 4); ✗ figures without source/meaning.

---

## Scope-flag summary (for CTO review)

| Component | Status | Action needed |
|-----------|--------|---------------|
| Company Header, Company Card, Financial Metric Card, KPI Tiles, Financial Tables, Chart Container, Analyst Summary Card, Comparison Card, Filing Viewer, Report Viewer, Watchlist Item | ✅ Traces to frozen baseline | Proceed |
| **News Card** | ⚠ SCOPE | [CR-SCOPE-002](../../governance/change_requests/CR-SCOPE-002_News.md) — recommend Defer → V1.1 |
| **Research Timeline** | ⚠ SCOPE | [CR-SCOPE-003](../../governance/change_requests/CR-SCOPE-003_Research_Timeline.md) — recommend Approve (bounded to Research History) |
| **Portfolio Card** | ⚠ SCOPE | [CR-SCOPE-001](../../governance/change_requests/CR-SCOPE-001_Portfolio.md) — recommend Defer → V2.0 |

> The three ⚠ SCOPE items are formally raised as Change Requests in the
> [Change Request Register](../../governance/change_requests/00_Change_Request_Register.md). Per
> governance, they remain **presentation patterns only** and are **not designed or built** until the
> CTO records a decision. The frozen baseline stays authoritative.

## Family cross-references
- Primitives: Families [01](01_Buttons.md)–[07](07_Feedback_Status.md); AI: [08](08_AI_Components.md).
- Frozen roles & screen coverage: [Component Inventory](../../design/09_Component_Inventory.md).
- Scope source of truth: [Screen Inventory](../../design/05_Screen_Inventory.md),
  [Information Architecture](../../design/03_Information_Architecture.md).

*Family 09 of 09 · Phase 2 · Milestone 2 — Component families complete*
