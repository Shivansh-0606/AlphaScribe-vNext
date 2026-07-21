# AlphaScribe vNext — Creative Exploration & Direction

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen — Direction C "The Study" selected (2026-07-18). Phase 1 gate cleared. |
| **Version** | 0.1.0 |
| **Milestone** | M2 — Production Design System & High-Fidelity Experience |
| **Phase** | Phase 1 — Creative Exploration |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Decision Required** | CTO / Design Lead selects ONE direction before Phase 2 begins |

**Companion asset:** [`design/figma/01_Creative_Exploration/direction-boards.svg`](../../../design/figma/01_Creative_Exploration/direction-boards.svg)

---

## Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On (frozen)** | [Design Constitution](../../design/00_Design_Constitution.md) · [Visual Language](../01_Visual_Language_Guidelines.md) · [Color System](../02_Color_System.md) · [Typography System](../03_Typography_System.md) · [Spacing](../04_Spacing_System.md) · [Grid](../05_Grid_System.md) · [Elevation](../06_Elevation_Shadow_System.md) · [Shape/Radius](../07_Shape_Radius_System.md) · [Design Tokens](../10_Design_Tokens.md) · [Screen Inventory](../../design/05_Screen_Inventory.md) |
| **Governs (downstream)** | Phase 2 Core Components · Phase 3 Layouts · Phase 4 Screens · Phase 5 Figma System · Phase 6 Prototypes · Phase 7 QA |

---

## 0. The Constraint That Shapes This Exploration

> **The visual identity is frozen and is NOT under exploration.**

Milestone 1 and the Design Constitution already fix, immutably:

- Warm parchment canvas (`#EEEAE2`), ink-navy type (`#15212F`), a **single** emerald→teal signature signal (`--brand-from #069169` → `--brand-to #0D8C82`).
- IBM Plex Sans (reading/UI) + IBM Plex Mono (figures, labels), with the signature uppercase `label-mono` mark.
- Sharp, structural, editorial edges; **single light theme** (no toggle, one token set).
- Semantic color reserved for meaning; no decorative gradients/glass/shadow (Constitution §19, §23).

Therefore, **"exploring multiple visual directions" here does not mean proposing alternative identities.** That would breach the freeze and the "no redesign" mandate. It means exploring distinct **expressions** of the one frozen identity — how far we lean editorial vs. spatial, how present the AI companion is, how much depth and motion carry "aliveness," how dense the research surface runs.

Every direction below uses the **same tokens, same type, same one signal.** They differ only in *emphasis and composition* — the levers a design system legitimately leaves open. The decision is not "which look," but **"which expression of AlphaScribe best satisfies the North Star."**

The North Star is the scoring rubric for the entire phase:

> *"AlphaScribe should feel like a **calm, living research workspace that actively thinks with you** — intelligent, responsive, and continuously assisting, where every answer is grounded, every claim is traceable, and you always leave more confident than you arrived."*

Note the two words in tension that the whole exploration must reconcile: **calm** and **living**. Constitution v1.1 Immutable Laws 16–18 make this explicit — *"the interface must feel alive"* and *"calm and alive are partners, not opposites."* A direction that wins calm but loses life fails Law 16; one that wins life but loses calm fails Laws 14 and 17. The right direction holds both.

---

## 1. Mood Boards

Mood boards here are **references-in-words + specimen swatches** (rendered in the companion SVG), not scraped imagery — the identity is already fixed, so the mood board's job is to pin the *feeling* each direction targets, using only frozen tokens.

### Board A — "The Broadsheet" (Editorial-Forward)
**Feeling:** a serious financial publication you trust — a long-read research briefing set on fine paper. Quiet chrome to the point of near-invisibility. The page *is* the product.

- **Texture & ground:** flat warm parchment, hairline rules only (`--border`), no elevated panels in the reading column. Structure comes from type and space, not boxes.
- **Voice of AI:** a research editor writing in the margin — inline, quiet, always cited.
- **Reference feeling:** FT/Economist long-form · a well-set annual report · a printed equity research note · Stripe Docs' reading calm.
- **One-line:** *"Read the company like a briefing."*

### Board B — "The Workbench" (Spatial-Forward)
**Feeling:** a living analyst's desk — layered surfaces, a persistent research context you build on, an AI partner visibly present and working alongside you. The workspace, not the document, is the hero.

- **Texture & ground:** parchment base with clearly elevated foreground surfaces (per [Elevation](../06_Elevation_Shadow_System.md)); a persistent companion rail; foreground/background depth (Constitution §12).
- **Voice of AI:** a co-analyst in a companion surface — thinking, gathering evidence, streaming, always in view.
- **Reference feeling:** a refined IDE/research terminal · Linear's spatial calm · Arc's living surfaces · a Bloomberg terminal *rethought for calm.*
- **One-line:** *"Work the company at a living desk."*

### Board C — "The Study" (Editorial × Spatial Synthesis)
**Feeling:** an editorial reading core resting inside a calm, considered workspace. A well-set page **on** a quiet desk. Depth is present but restrained; the AI is embedded inline yet can step forward as a companion when summoned.

- **Texture & ground:** parchment reading column (from A) with *subtle* elevation reserved for genuine foreground focus and transient surfaces (from B) — depth used only where it clarifies, never as texture.
- **Voice of AI:** embedded inline beside the evidence, with an evidence-forward companion that appears **in context** when the user asks — present when needed, silent when not (Constitution §8: "reached in place, not visited as a destination").
- **Reference feeling:** the reading comfort of A + the spatial liveness of B, disciplined. A research desk where the page leads and the room supports.
- **One-line:** *"Read the company at a living research desk."* — the North Star sentence, almost verbatim.

---

## 2. Design References (and how each maps to the freeze)

References are used **only as feeling anchors**, never as things to copy — the identity is ours and fixed.

| Reference | What we take (feeling) | What we explicitly reject | Ties to |
|-----------|------------------------|---------------------------|---------|
| FT / Economist long-form | Editorial hierarchy through type; reading calm; trust through restraint | Their brand color, ornament, ad density | Dir. A/C |
| Printed equity research note | Figures paired with meaning; scannable numeric columns; sober authority | Dense unstructured walls of numbers | All |
| Stripe Docs | Calm reading rhythm; quiet chrome; premium neutrality | Their palette; SaaS marketing gloss | Dir. A/C |
| Linear | Spatial calm; keyboard-first; refined motion; "alive but quiet" | Dark-first identity; product-management metaphors | Dir. B/C |
| Refined IDE / research terminal | Companion surfaces; persistent working context; mono precision | Terminal coldness; chart overload; visual noise | Dir. B/C |
| A considered annual report | Paper character; generous measure; figures as first-class citizens | Static, non-interactive feel | Dir. A/C |

**Anti-references (what AlphaScribe must never resemble — Constitution §23):** generic AI SaaS, a standalone ChatGPT clone, a chart-overloaded dashboard, glassmorphism/gradient decoration. Every direction below is screened against these.

---

## 3. Visual Language Exploration

All three directions share the frozen [Visual Language](../01_Visual_Language_Guidelines.md): *editorial not dashboard; warm paper, ink, one signal; calm but alive; evidence forward; density with air; restraint as craft.* They differ on the **composition levers** the visual language leaves open:

| Lever | A — Broadsheet | B — Workbench | C — Study |
|-------|----------------|---------------|-----------|
| **Chrome presence** | Near-zero; page fills the frame | Persistent rails + companion always visible | Minimal chrome; companion summoned in-context |
| **Surface/elevation use** | Flat paper, hairlines only | Layered surfaces, clear foreground/background | Flat reading column + reserved elevation for focus/transient |
| **Structure comes from** | Type + space almost entirely | Space + depth + surface boundaries | Type + space, depth used sparingly for focus |
| **Density** | Lowest (long-read) | Highest (workspace) | Calibrated per screen (read = airy, compare = denser) |
| **Where the eye lands** | The prose | The active surface / AI partner | The primary content, with evidence one glance away |

**Reading against §11 (Visual) & §12 (Spatial):** A honors §11 beautifully but under-uses §12 (depth, foreground/background). B honors §12 fully but risks §11's restraint and the §23 "dashboard/clutter" anti-pattern. C applies §12 *with restraint* — "ambient polish… felt, not noticed" (§12) — which is exactly how the constitution frames depth.

---

## 4. Typography Exploration

Type is the primary hierarchy instrument in all directions (frozen [Typography](../03_Typography_System.md) — IBM Plex Sans/Mono, 9-step scale, `label-mono`). Exploration is in **typographic posture**, not families or scale.

| Aspect | A — Broadsheet | B — Workbench | C — Study |
|--------|----------------|---------------|-----------|
| **Reading measure** | Wide, book-like (~68–72ch) | Narrower, workspace columns (~56–62ch) | Comfortable ~62–66ch reading core |
| **Heading rhythm** | Large `h1/h2` steps, editorial air | Tighter steps to conserve vertical space | Editorial steps, one level down inside dense surfaces |
| **`label-mono` role** | Sparse — quiet section markers | Frequent — labels every surface/rail | Purposeful — marks sections & AI/evidence affordances |
| **Figures (`type.figure`)** | Inline within prose, tabular | Dense tabular blocks in workbench panels | Tabular, grouped in scannable metric regions |
| **Risk** | Can feel *too* document-static | `label-mono` overuse → busy | Requires discipline to keep labels scarce |

**Verdict:** All are legitimate uses of the frozen scale. C's "editorial core, mono for precision and AI/evidence marks" is the most faithful to §16 (readability) *and* the "editorial-terminal" character named in Typography §Design Principles. Specimen in companion SVG.

---

## 5. Color Exploration

Zero freedom on palette (frozen [Color System](../02_Color_System.md)). The only exploration is **how much of the one signal each direction spends, and where** — the discipline that keeps the emerald→teal signal meaningful (Constitution §11 restraint; §19 anti-patterns).

| Signal budget | A — Broadsheet | B — Workbench | C — Study |
|---------------|----------------|---------------|-----------|
| **Primary action** | 1 per view, navy or signal | 1 per surface — risk of many at once | 1 per context, deliberate |
| **AI / verified moment** | Rare inline mark | Persistent companion tinted with signal | Signal on AI affordance + verified/evidence, in-context |
| **Focus ring** | `--ring` deep emerald (constant) | constant | constant |
| **Surfaces** | Pure paper + hairline | Paper + warm off-white elevated surfaces | Paper core + reserved off-white for focus/transient |
| **Signal-dilution risk** | Lowest | **Highest** (many surfaces tinted → signal loses meaning) | Low (signal stays scarce, tied to action/AI/evidence) |

**Reading against Color §Anti-patterns ("coloring UI chrome with the signature gradient dilutes the signal"):** B's persistent tinted companion is the risk to watch. C spends the signal only on action, AI presence, verified/evidence, and focus — keeping it *rare and therefore meaningful.*

---

## 6. Spatial Exploration

This is the axis of greatest difference, and where Constitution v1.1 (§6 Living Interface, §12 Spatial) raises the bar over a static document.

- **A — Broadsheet:** essentially 2 planes (paper + hairline structure). Transient surfaces (menus, dialogs) elevate; the reading plane never does. **Calm: excellent. Alive/spatial: thin** — risks Law 16 ("must feel alive… spatial").
- **B — Workbench:** 3–4 planes always present (background · reading · companion · transient), persistent foreground/background. **Alive/spatial: excellent. Calm: at risk** — persistent multi-plane depth can read busy, brushing §23 "visual clutter."
- **C — Study:** 2 planes at rest (paper + hairline), **elevation summoned on demand** for focus surfaces, the AI companion, and transient content — then it recedes. Depth appears *when it means something* and disappears when it doesn't. This matches §12 exactly: *"raised surfaces (transient, contextual, or active content) read as elevated… ambient polish… felt, not noticed."*

**Spatial verdict:** C treats depth as a **verb** (elevate to focus) rather than a **constant texture** — the constitution's stated intent. It gets B's aliveness only when the moment earns it, keeping A's calm the rest of the time. Elevation values are already fixed in [Elevation](../06_Elevation_Shadow_System.md); this is about *when* to spend them.

---

## 7. Motion Exploration

Motion philosophy is frozen (Constitution §14: *"communicate… never distract"*; reduced-motion honored with no info loss). Exploration is in **motion budget and personality** per direction. Full specs are a Phase 6 / Motion deliverable; here we set posture.

| Motion trait | A — Broadsheet | B — Workbench | C — Study |
|--------------|----------------|---------------|-----------|
| **Default temperament** | Minimal — fades & instant states | Ambient — surfaces & companion animate often | Reserved — motion at transitions, focus, and AI |
| **Signature moments** | Progressive text reveal | Companion "thinking," surface transitions | Continuity transitions + AI think→gather→stream |
| **Perceived-performance role** | Skeletons only | Skeletons + ambient liveness | Skeletons + AI progress + gentle continuity |
| **Distraction risk (§14)** | Lowest | **Highest** (ambient motion competes with reading) | Low (motion tied to meaning: continuity, feedback, AI) |
| **Reduced-motion fallback** | Trivial | More to strip back | Clean — every motion has an instant-state equivalent |

**Motion verdict:** C spends motion on the three things §14 explicitly blesses — **continuity, feedback, and making AI feel alive** — and nowhere else. This is "purposeful delight, not spectacle" by construction.

---

## 8. AI Experience Exploration

The AI experience is where "alive," "collaborative," and "trust-first" are won or lost (Constitution §8 behavior, §9 feel). AI must be **embedded, never a standalone chatbot** (Immutable Law 5; anti-pattern §23). The directions differ in *how present* the partner is.

| AI dimension | A — Broadsheet | B — Workbench | C — Study |
|--------------|----------------|---------------|-----------|
| **Where AI lives** | Inline margin notes only | Persistent companion surface, always visible | Inline beside evidence **+** companion summoned in-context |
| **Presence** | Quiet, easily missed | Strong, always-on | Present when relevant, silent when reading (Constitution §8) |
| **Thinking → streaming** | Text reveal in place | Prominent companion "working" state | Visible think→gather-evidence→stream, in the reading context |
| **Evidence/citation** | Inline citation links | Companion evidence panel | Citations inline + evidence peek in-context (evidence-forward) |
| **Risk** | AI under-felt → fails "AI-native," §9 | Always-on companion drifts toward "ChatGPT sidebar" → Law 5 risk | Requires clear rules for when the companion appears |
| **"Not a chatbot" test (Law 5)** | Passes (too quiet) | **At risk** (persistent side chat reads chatbot-like) | Passes strongest — AI is *in* the research, summoned in place |

**AI verdict:** The constitution is unusually specific here: AI is *"reached in place, not visited as a destination"* (§8), *"embedded"* and *"felt, not performed"* (§9). B's always-on companion is the exact shape the anti-pattern warns against (a standalone chat surface). C's *"inline + summoned-in-context companion"* is the literal §8/§9 model: the partner is present in the research, thinks visibly, gathers evidence, streams — and goes quiet when the user is reading.

---

## 9. Constitution Evaluation Matrix

Each direction scored against the governing checks (Constitution §24 Review Framework + Immutable Laws). Scale: ✅ strong · ◻ adequate/at-risk · ⚠ likely fails.

| Constitution axis | A — Broadsheet | B — Workbench | C — Study |
|-------------------|:--:|:--:|:--:|
| §2 North Star — *calm, living workspace* | ◻ (calm, under-living) | ◻ (living, under-calm) | ✅ |
| §3 Personality — trustworthy **and** alive | ◻ | ◻ | ✅ |
| §5–6 Emotional / Living Interface | ⚠ (risks inert) | ✅ | ✅ |
| §7 One primary intent; summary→detail | ✅ | ◻ (many surfaces compete) | ✅ |
| §8–9 AI embedded, felt, not a chatbot | ◻ (under-felt) | ⚠ (persistent side-chat risk) | ✅ |
| §11 Visual — restraint, hierarchy | ✅ | ◻ (restraint at risk) | ✅ |
| §12 Spatial — depth with restraint | ⚠ (too flat) | ◻ (depth as constant texture) | ✅ |
| §14 Motion — communicate, not distract | ✅ | ◻ (ambient motion risk) | ✅ |
| §16 Density & readability | ✅ | ◻ | ✅ |
| §19 / §23 Anti-patterns avoided | ✅ | ⚠ (clutter/dashboard risk) | ✅ |
| §17 Accessibility (AA, no color-only) | ✅ | ✅ | ✅ |
| Immutable Law 16–17 (alive; calm+alive partners) | ⚠ | ◻ | ✅ |
| **Net** | **Calm, not alive** | **Alive, not calm** | **Calm *and* alive** |

The pattern is deliberate and clear: **A and B each win one half of the North Star and lose the other. C is the only direction that holds both** — which is precisely what Immutable Laws 16–18 require.

---

## 10. Recommended Direction

## → **Direction C — "The Study" (Editorial × Spatial Synthesis)**

### Justification

1. **It is the North Star, almost word-for-word.** The North Star names a *"calm, living research workspace."* A is a calm research *document*; B is a living research *dashboard*; C is a **calm, living research workspace** — the exact noun phrase, with both adjectives intact. When the governing sentence itself resolves the choice, that is the choice.

2. **It is the only direction that satisfies the v1.1 Immutable Laws simultaneously.** Law 16 (*"must feel alive — responsive, spatial, aware of state"*) fails A. Laws 1, 14, 19 (clarity, non-distracting motion, restraint) put B at risk. Law 17 (*"calm and alive are partners, not opposites"*) is only fully met by C. A design can't ship if it fails an immutable law.

3. **It expresses depth and motion as the constitution actually defines them — restrained and meaningful.** §12 asks for *"ambient polish… felt, not noticed"* and elevation *"applied with restraint."* C treats depth as a verb (summoned for focus, then receding), not B's constant texture — honoring the letter of §12.

4. **It resolves the AI experience correctly.** §8/§9 require AI *"reached in place, not visited as a destination,"* *"embedded,"* *"felt, not performed."* C's inline-plus-summoned-companion is that model; B's always-on companion drifts toward the standalone-chatbot anti-pattern (Law 5); A under-delivers the "AI-native" promise.

5. **It is the most maintainable at scale.** C's rule — *"paper reading core, elevation and the companion summoned only when they carry meaning"* — is a simple, teachable law that keeps hundreds of future screens consistent (Constitution §7.5, §24 Consistency). B's "everything is a layered surface" invites per-screen improvisation and clutter drift; A's "never elevate" can't express the interactive screens in the [Screen Inventory](../../design/05_Screen_Inventory.md).

6. **It absorbs the best of the rejected directions** rather than discarding them: A's reading calm becomes C's content core; B's spatial liveness becomes C's on-demand focus and companion. Nothing good is lost; the risks of each extreme are designed out.

### The governing rule this direction hands to Phase 2+

> **"A well-set page on a living desk."** Content is an editorial reading core on flat warm paper; **elevation, motion, and the AI companion are summoned only when they carry meaning, then recede.** The one signal marks action, AI presence, verified/evidence, and focus — nowhere else. Calm is the resting state; life appears on interaction and around the AI, and never as decoration.

This single sentence is the design contract every subsequent phase inherits.

### Explicitly rejected (with reason, for the record)

- **Direction A — Broadsheet:** rejected for failing Immutable Law 16 (feels alive) and under-delivering §5–6, §8–9, §12. *Too static to be AI-native.*
- **Direction B — Workbench:** rejected for risking Laws 1/14/17/19 and the §23 clutter / standalone-chatbot anti-patterns. *Too busy to be calm; its always-on AI reads chatbot-like.*

---

## 11. Phase 1 Gate

**Phase 2 (Core Component Design) must not begin until one direction is selected.** ✅ **Direction C "The Study" was selected on 2026-07-18.** The governing rule in §10 ("A well-set page on a living desk") is now the frozen input to every downstream phase. This document is Approved.

Any request to alter the frozen *identity* (not the expression) — e.g., a second theme, a new accent — is out of scope for direction selection and requires a formal **Change Request** per the Constitution's governance rule.

---

*Prepared by the Experience Design Department · Milestone 2 · Phase 1 of 7*
