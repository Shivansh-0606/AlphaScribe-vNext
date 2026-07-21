# AlphaScribe vNext — Component Family 07: Feedback & Status

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Phase** | M2 · Phase 2 — Core Components |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Inherits** | [Component System Foundation](00_Component_System.md) |
| **Frozen mapping** | [`Notification/Toast`](../../design/09_Component_Inventory.md#notification--toast), [`Spinner/Progress`](../../design/09_Component_Inventory.md#spinner--progress) |

> Distinctive detail only. **Family principle (Constitution §21, §19):** waiting must feel *alive
> and productive*, never a frozen void. Loading is scoped to its region; progress always advances;
> nothing appears hung. Implemented in the codebase with `sonner` for toasts (project convention).

---

## Toast ⟶ maps to: `Notification/Toast` (Inventory Molecule)

### Purpose
Communicate a **transient outcome** — success, info, a non-blocking error, a warning — briefly, then
auto-dismiss. For outcomes, **not** for blocking/critical errors (use the [Error state](../../design/13_States.md#error)).

### Anatomy
`[ tone icon ] · message · [ optional action / undo ] · [ dismiss ]` on `--surface`,
`--elevation-3`, stacked in a consistent corner region (`--z-toast`).

### Variants
Per Inventory: **Success · Error (non-blocking) · Info · Warning.** Optional **action** (e.g.
"Undo", "View") — undo-bearing toasts are the preferred alternative to confirm dialogs (§19).

### Sizes
Compact; message wraps to a couple lines max; long content belongs elsewhere.

### States
**Enter · Visible · Dismiss** (Inventory) + **Paused (on hover/focus).** Distinctive:
- Auto-dismiss after a readable duration; **pauses on hover/focus**; error/action toasts persist
  longer or until dismissed.
- Undo action available for the toast's lifetime (Saving Research / reversible-action pattern).

### Accessibility (distinctive)
Announced via a live region — **polite** for success/info, **assertive** for errors; dismissible by
keyboard; not motion-only; auto-dismiss timing accommodates reading (and pauses on focus). Action/
undo is a labeled, keyboard-reachable control.

### Responsive (distinctive)
Corner stack on desktop → top/bottom full-width on mobile; stacking order and behavior preserved.

### Token usage
`--surface`, `--elevation-3`, `--shadow-md`, `--z-toast`, tone icons + `bullish`/`--destructive`/
`warning`/`brand` (with text, never color alone), `type.small`, `--radius-md`, Button tokens (action),
`--motion-duration-base`.

### Motion (signature)
Slide/fade-in from the edge `--motion-duration-base`, `--motion-ease-out`; graceful fade-out. A quiet
"success feels satisfying" moment — never fanfare (§20). Reduced motion → instant appear/disappear.

### Usage guidelines
- **Do** use for outcomes; prefer an Undo toast over a confirm dialog for reversible actions.
- **Do** pause on hover/focus; announce at the right politeness.

### Anti-patterns
- ✗ Toasts for critical/blocking errors (use the Error state); ✗ color-only tone; ✗ auto-dismissing
  an error before it can be read; ✗ celebratory fanfare that breaks the calm (§20).

---

## Notification ⟶ maps to: `Notification/Toast` (persistent variant)

### Purpose
Communicate status that should **persist** until seen/resolved — e.g. a background result ready, an
account/access notice. Distinct from a transient toast; lives in a notifications surface or inline
banner, not an auto-dismissing corner.

### Anatomy
Inline **banner** (within a region) or an item in a **notifications list** (from a header
bell/menu): `[ tone icon ] · message · [ action ] · [ dismiss/mark read ]`.

### Variants
**Inline banner** (region-level status: Offline, Partial Failure notice, Permission notice) ·
**Notification list item** (persistent, mark-as-read).

### Sizes
Banner full-width of its region; list items `md`.

### States
**Unread · Read · Dismissed · Action-pending.** Banners reflect a persistent condition (e.g. Offline)
and clear when it resolves.

### Accessibility (distinctive)
Banners: `role=status`/`alert` per severity; associated with the region they describe; persistent
(not time-dismissed) so they can be read at leisure; count/unread state textual (see
[Badge](05_Content_Data_Display.md)).

### Responsive
Banner reflows full-width; list becomes a sheet/panel on mobile; parity preserved.

### Token usage
As Toast, minus auto-dismiss; `--muted`/tone surfaces for banners; `--border`.

### Motion (signature)
Banner reveals in its region `--motion-duration-base` (no layout jump — reserve space). Reduced
motion → instant.

### Usage guidelines / Anti-patterns
- **Do** use for persistent/important status (Offline, Partial Failure, access); let the user
  resolve/dismiss deliberately.
- ✗ Persistent banners for trivial outcomes (use a Toast); ✗ blocking navigation with a banner;
  ✗ color-only severity.

---

## Progress Indicators ⟶ maps to: `Spinner/Progress` (Inventory Atom)

### Purpose
Indicate ongoing work and its advancement — the visible proof the system is *working, not frozen*
(§21). Determinate where progress is known; indeterminate where it is not.

### Anatomy
**Linear bar** (region/step progress), **circular spinner** (compact/inline busy), or a **step/stage
indicator** (e.g. AI "gathering → reasoning → resolving", export stages). Paired with a text label
for context.

### Variants
Per Inventory: **Indeterminate** (unknown duration — spinner/indeterminate bar) · **Determinate**
(known % — linear bar). Plus **Stage progress** (named steps, used for AI/export flows).

### Sizes
`sm` (inline) / `md` (region) / linear full-width of its region.

### States
**Active** (Inventory). Determinate advances monotonically; stage progress names the current stage.
Long AI/export work uses stage/determinate, not an endless spinner (Timeout bounds it).

### Accessibility (distinctive)
`role=progressbar` with `aria-valuenow/min/max` (determinate) or busy semantics (indeterminate);
announced as busy; **not the only signal** for long waits (pair with text/stage — Inventory rule);
progress not conveyed by motion/color alone.

### Responsive
Constant; linear bars span their region at every size.

### Token usage
`--brand-from→--brand-to` (determinate fill — a sanctioned signal use for AI/primary progress) or
`--muted-foreground` (neutral), `--muted` (track), `--motion-*` (indeterminate cadence),
`type.caption` (label/stage).

### Motion (signature)
Indeterminate: a calm, continuous cadence (`--motion-duration-*`), never frantic. Determinate: fill
advances smoothly. Reduced motion → determinate still fills (essential info); indeterminate shows a
static "busy" text/state (no info loss).

### Usage guidelines
- **Do** prefer determinate/stage for long or AI/export work; always pair with a context label.
- **Do** show forward motion; bound long waits with Timeout.

### Anti-patterns
- ✗ An endless indeterminate spinner for long, boundable work (feels hung — §21); ✗ progress by
  motion/color alone; ✗ a full-screen blocking spinner where a scoped one suffices.

---

## Skeleton ⟶ maps to: `Skeleton` (canonical [state](../../design/13_States.md#skeleton))

### Purpose
Preserve layout and set expectations while **structured** content loads — the "progressive rendering"
feel: the screen is usable and shaped before data arrives (§21).

### Anatomy
Placeholder shapes mirroring the eventual content (title bar, metric rows, table rows, card grid),
in `--muted` with a subtle shimmer; **no fabricated values**.

### Variants
**Text lines · Metric/stat · Table rows · Card · Chart** skeletons — one per major content shape.

### Sizes
Match the real content's dimensions exactly (no layout shift on swap).

### States
**Loading → replaced** in place by real content, Empty, or Error (canonical Skeleton state).

### Accessibility (distinctive)
Region announced as loading; **placeholders are not read as real data** (Inventory/States rule);
`aria-hidden` on the shapes with a single "loading" status for the region.

### Responsive
Skeletons follow the responsive layout of the content they stand in for.

### Token usage
`--muted`/`--surface`, `--radius-sm/md`, a low-amplitude shimmer via `--motion-*` (subtle, calm).

### Motion (signature)
A slow, low-contrast shimmer (`--motion-duration-slow`+) — "loading feels alive", never a flashy
sweep. Reduced motion → static placeholder (no shimmer), still communicating "loading".

### Usage guidelines / Anti-patterns
- **Do** use skeletons for structured content (metrics, tables, reports); match real dimensions;
  render summary-first (progressive).
- ✗ Skeletons that mismatch and cause layout shift; ✗ fabricated numbers in placeholders; ✗ a
  spinner where a skeleton would better preserve layout.

---

## Loader ⟶ maps to: `Spinner/Progress` (indeterminate, generic)

### Purpose
A generic indeterminate busy indicator for **unstructured** or brief waits where a skeleton doesn't
apply (a button's inline spinner, a small region resolving, initial app boot).

### Anatomy
A compact circular spinner, optionally with a short label; scoped to its element/region.

### Variants
**Inline** (in a button/field — see [Buttons](01_Buttons.md)) · **Region** (centered in a small
panel) · **Full-view** (rare — initial boot only, with brand-calm treatment).

### Sizes
`sm` (inline) / `md` (region). Full-view centered.

### States
**Active.** Escalates to Error/Timeout on failure/over-long waits — never spins forever.

### Accessibility (distinctive)
Busy semantics + a text label ("Loading…"); focus not stolen; for anything long, pair with progress/
stage (don't rely on the spinner alone).

### Responsive
Constant; region loaders center within their (responsive) container.

### Token usage
`--muted-foreground`/`--brand` (sparing), `--motion-*`, `type.caption` (label).

### Motion (signature)
Calm continuous rotation; reduced motion → a static "Loading…" text/indicator (no info loss).

### Usage guidelines / Anti-patterns
- **Do** use for brief/unstructured waits; prefer Skeleton for structured content and Progress for
  long/known work.
- ✗ Full-screen loaders that block a scoped operation; ✗ infinite spinners for boundable work;
  ✗ spinner as the sole signal for long waits.

---

## Choosing the right feedback (quick guide)

| Situation | Use |
|-----------|-----|
| Structured content loading (metrics, tables, report) | **Skeleton** |
| Brief/unstructured wait, inline busy | **Loader** |
| Long/known or AI/export work | **Progress** (determinate/stage) + Timeout |
| Transient outcome (saved, exported, undo) | **Toast** |
| Persistent status (Offline, Partial Failure, access) | **Notification / banner** |
| Blocking failure needing resolution | **Error state** (not a toast) — [States](../../design/13_States.md) |

## Family cross-references
- Canonical states this family renders: [States](../../design/13_States.md) (Loading, Skeleton,
  Error, Success, Partial Failure, Timeout, Offline).
- Inline button loading: [Buttons](01_Buttons.md); AI thinking/streaming: [AI Components](08_AI_Components.md).

*Family 07 of 09 · Phase 2 · Milestone 2 · Foundation families complete*
