# AlphaScribe vNext — Motion Specifications

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Milestone / Doc** | M3 · Motion Specifications (05) |
| **Owner** | Experience Design Department |
| **Design source (frozen)** | Constitution §14 · [Motion tokens](../10_Design_Tokens.md#11-motion-tokens) · [Interaction Patterns](../../design/10_Interaction_Patterns.md) |
| **Target library** | **Motion** (`motion`) |
| **Last Updated** | 2026-07-18 |

## Purpose

Specify **every animation** in the product so Engineering implements motion that **communicates, never
decorates** (Constitution §14) — with an exact trigger, purpose, duration, easing, reduced-motion
fallback, interruption behavior, and accessibility note for each. If a motion here can be removed
without losing meaning, it should not exist.

## Scope

All component and transition motion, sourced from the M2 families' "Motion (signature)" entries and the
[Motion tokens](../10_Design_Tokens.md#11-motion-tokens). **Out of scope:** per-screen choreography for
screens not yet built (M2 Phase 4/6, pending) — the primitives here compose into them.

## Decision Rationale

- **Token-driven durations/easings** (§11) mean every animation shares one vocabulary → coherence, and a
  single reduced-motion switch collapses them all safely.
- **Direction C** makes motion *earned*: it appears on interaction, transition, and around AI — never as
  ambient decoration. This is how "calm but alive" is implemented, not decorated.

## Global rules (apply to every animation)

- **Durations/easings come from tokens only:** `--motion-duration-instant/fast/base/slow/stream`;
  `--motion-ease-standard/out/in/emphasis`. No ad-hoc ms/curves.
- **Reduced motion (`prefers-reduced-motion: reduce`) is mandatory and lossless:** all durations collapse
  to `instant`; motion is replaced by an instant state change; **no information is lost** (essential
  progress like determinate bars remains, just without decorative movement).
- **Interruptible:** user-driven transitions (open/close, tab switch, hover) are interruptible and
  reversible mid-flight; a new input takes precedence over an in-progress animation (no queueing jank).
- **Never block interaction** on an animation completing; **never animate layout in a way that shifts
  content the user is reading**.
- **Purpose test (review gate):** each animation must communicate continuity, feedback, hierarchy,
  perceived performance, or AI liveness. If none apply → remove it.

## Motion Catalogue

| # | Animation | Trigger | Purpose | Duration | Easing | Reduced-motion | Interruption |
|---|-----------|---------|---------|----------|--------|----------------|--------------|
| M1 | Button/control **hover/press** | pointer over / down | feedback ("heard you") | `fast` 120ms | standard | instant fill change | immediate on new state |
| M2 | **Focus ring** appear | `:focus-visible` | show focus | `fast` | standard | instant (ring still shows) | n/a |
| M3 | Input **focus border/ring** | field focus | orient ("you are here") | `fast` | standard | instant | immediate |
| M4 | Input **error reveal** | validation fail | show error in reserved space (no shift) | `base` 150ms | out | instant text | replaced on revalidate |
| M5 | Checkbox/radio **check draw** | toggle | selection feels intentional | `fast` | out | instant glyph | immediate |
| M6 | Switch **knob slide** | toggle | physical on/off | `base` | standard | instant position | immediate |
| M7 | **Selected fill slide** (segmented/tabs indicator) | select | continuity between options | `base`/`fast` | standard | instant move | immediate to new target |
| M8 | **Tab panel** cross-fade | tab change | continuity | `base` | standard | instant swap | immediate |
| M9 | Card/interactive **hover lift** | pointer over | "alive on interaction" (Dir. C) | `base` | out | instant, no lift | reverses on leave |
| M10 | **Popover/menu/tooltip** reveal | open | continuity from trigger origin | `base` | out | instant appear | closes immediately on Esc/outside |
| M11 | **Dialog** enter (scrim + panel) | open | considered interruption | `slow` 240ms | out | instant, scrim instant | Esc/action closes immediately |
| M12 | **Drawer / AI companion** slide-in | summon | "companion arrives," continuity | `slow` | out | instant show | collapses immediately |
| M13 | **Toast** enter/exit | outcome | quiet success/notice | `base` | out | instant appear/disappear | pause on hover/focus; dismiss immediate |
| M14 | **Skeleton shimmer** | region loading | "loading feels alive" | `slow`+ loop | standard | **static placeholder** (no shimmer) | ends when data arrives |
| M15 | **Progress** (indeterminate cadence) | busy | reassure work is advancing | loop | standard | static "busy" text | ends on resolve |
| M16 | **Progress** (determinate fill) | known progress | show advancement | `base` per step | out | **fill still advances** (essential) | reflects real progress |
| M17 | **AI Thinking** presence pulse / evidence-gather | AI considering | partner engaging (not spinner) | gentle loop | standard | static "Thinking…/Gathering evidence…" | ends on stream/timeout |
| M18 | **AI Streaming** text reveal | AI output | readable, alive, collaborative | `stream` (human pace) | out | progressive **chunks** instantly (still progressive) | Stop retains partial output |
| M19 | **Citation attach** mark | claim resolves | grounding made visible | `base` | out | instant | n/a |
| M20 | **Progressive content reveal** (KPI/sections, summary-first) | data arrives | perceived performance | `base` staggered | out | instant | n/a |
| M21 | **Company Header condense** on scroll | scroll past threshold | continuity, orient | `base` | standard | instant condense | reverses on scroll up |
| M22 | **Chart series draw-in** | chart load | orient to data (once) | `slow` | out | **static chart** (no draw) | n/a |
| M23 | **Chip add/remove** | add/remove | acknowledge change | `fast`/`base` | standard/out | instant | immediate |

**AI motion (M17–M19) is trust-critical:** it must read as *calm, embedded, felt — not performed*
(Constitution §9). No theatrics, no dramatized "typing." Streaming pace must stay readable.

## Interruption Behavior (detail)

- **Reversible transitions** (hover, open/close, tab, condense) reverse from their current position; they
  never snap to end then restart.
- **AI streaming**: a Stop request halts the stream and **retains the partial output** with a retry
  ([States: AI Streaming/Timeout](../../design/13_States.md#ai-streaming)); it never discards produced text.
- **Navigation mid-animation**: a route/tab change cancels in-flight decorative motion and lands at the
  destination's resting state.

## References to Previous Milestones

Constitution §5/§6/§9/§14/§19 · [Motion tokens](../10_Design_Tokens.md#11-motion-tokens) ·
[Interaction Patterns](../../design/10_Interaction_Patterns.md) · [States](../../design/13_States.md) ·
each [M2 family](../Components/00_Component_System.md) "Motion (signature)".

## Best Practices

- Drive Motion with the token durations/easings; centralize a reduced-motion provider so every animation
  honors it without per-component code.
- Prefer transform/opacity animation (compositor-friendly) over animating layout properties.
- Stagger progressive reveals subtly (summary-first) — never a long cascade that delays reading.

## Anti-patterns

- ✗ Ambient/decorative motion (breaks calm, §23). ✗ Dramatized AI "typing" theatrics (§9).
- ✗ Layout-shifting animation over content being read. ✗ Motion that blocks input. ✗ Reduced-motion that
  drops information (e.g. hiding a determinate progress bar). ✗ Per-character SR announcements during
  streaming (see §06).

## Engineering Considerations

- **Motion** library orchestrates enter/exit (`AnimatePresence`-style) for overlays/companion; shadcn's
  Radix primitives expose open state to drive it.
- Streaming pace (M18) is a product-tuned constant (`--motion-duration-stream`) — expose it as config, not
  a magic number, so it can be tuned without redesign.

## Accessibility Considerations

- `prefers-reduced-motion` honored globally and losslessly (WCAG 2.3.3).
- No motion is the **sole** carrier of information (progress/state also textual).
- Streaming announced **considerately** (batched/polite live region), completion announced — never
  per-character (§06). Focus is never yanked by an animation.

## Future Maintenance

Add per-screen choreography when M2 Phase 4/6 (Screens/Prototypes) land. Any new animation must pass the
purpose test and add a reduced-motion fallback. Governed by [13](13_Design_System_Governance.md).

---

*Experience Design Department · Milestone 3 · Document 05 of 14*
