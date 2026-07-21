# AlphaScribe vNext — Component Family 08: AI Components

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Phase** | M2 · Phase 2 — Core Components |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Inherits** | [Component System Foundation](00_Component_System.md) |
| **Frozen mapping** | [`CopilotPanel`](../../design/09_Component_Inventory.md#copilotpanel), [`AISummary`](../../design/09_Component_Inventory.md#aisummary), [`SourceReference`](../../design/09_Component_Inventory.md#sourcereference) |

> These components carry the product's promise. They are governed not just by the foundation but by
> **Constitution §8 (AI behavior), §9 (AI experience), and Immutable Laws 3–5, 8** — and by
> [States: AI Thinking / AI Streaming](../../design/13_States.md#ai-thinking). Read the family
> contract below before any single component; it is non-negotiable.

---

## AI Family Contract (applies to every component here)

| Rule | Source | What it means for these components |
|------|--------|-----------------------------------|
| **Embedded, never a standalone chatbot** | Law 5; §8; §23 | AI lives *in* the research context (company, comparison, filing), reached in place. The companion is **summoned and recedes** (Direction C) — never a persistent side-chat. |
| **Every insight is traceable** | Law 3; §7.3, §22 | No AI claim appears without a reachable, keyboard-accessible source path. A source-less AI statement is a defect. |
| **AI content is visibly distinct from source** | §22; §8 | The user always knows what is AI reasoning vs. primary source — via labeling + the signal affinity, not decoration. |
| **Uncertainty is honest; confidence ≤ evidence** | Laws 4, 8; §8–9 | The AI states limits plainly ("not enough evidence") rather than fabricating confidence. Confidence indicators never overstate. |
| **No recommendations** | Law 4; §8 | Never buy/sell/financial advice; the AI assists thinking, it does not decide. |
| **Feels like thinking, not spinning** | §9; States | Thinking, gathering evidence, and streaming are *visible and calm* — a partner working with you, "felt, not performed." |

---

## Prompt Composer ⟶ composes: `CopilotPanel` input / `Textarea`

### Purpose
Where the user asks the embedded AI a question **about the current subject** (this company, this
comparison, this filing, a concept). The entry point to a collaborative exchange — always scoped to
context.

### Anatomy
`[ context chip: "About Infosys" ] · Textarea (auto-grow) · [ AI Suggestions ] · [ AI Action
Toolbar / send ]`. The context chip makes the embedding visible — the user sees the AI is grounded
in the current subject, not a blank chatbot.

### Variants
Per `CopilotPanel` contexts: **Company · Comparison · Learning (concept).** Difference is the context
chip + suggestion source, not identity.

### Sizes
Textarea base (§ [Text Inputs](02_Text_Inputs.md)); send is a `md`/`lg` primary Icon Button.

### States
**Default · Focus · Filled · Disabled (no valid AI access) · Sending → AI Thinking.** Distinctive:
- **Disabled/Permission Denied:** when AI access isn't validated, the composer explains and routes to
  [AI setup](../../design/09_Component_Inventory.md#aiaccessselector) — never a dead field.
- On submit → the conversation shows a **Thinking State**, then **Streaming Response**.

### Accessibility (distinctive)
Labeled multiline input; the context is programmatically associated (the user knows the scope);
Enter-to-send with Shift+Enter for newline (documented, discoverable); send is a labeled control;
submit moves attention to the arriving response region considerately (not stealing focus mid-read).

### Responsive
Docks at the bottom of the AI companion drawer; on mobile stays reachable above the keyboard;
suggestions become a scrollable chip row.

### Token usage
Textarea tokens + context chip ([Chip](05_Content_Data_Display.md)) + primary Icon Button
(`--brand` send) + `type.label` (context).

### Motion (signature)
Send → the composer settles and a Thinking State appears in the conversation
(`--motion-duration-base`, continuity). Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** always show the context scope; route to AI setup when access is missing.
- ✗ A context-free, open-ended chatbot prompt (breaks Law 5 embedding); ✗ Enter-to-send with no
  newline gesture; ✗ enabling send with no valid AI access.

---

## AI Suggestions ⟶ composes: choice `Chip`s

### Purpose
Offer grounded next questions ("What drove margin change?", "Compare to peers", "Explain P/E") to
**encourage curiosity** (§5) and lower the blank-prompt cost — always scoped to the current subject.

### Anatomy
A row/wrap of choice [chips](05_Content_Data_Display.md) above/below the composer, each a
context-relevant question; selecting one populates/sends the prompt.

### Variants
**Starter suggestions** (empty composer) · **Follow-up suggestions** (after a response) · **Learner
suggestions** (P-02 — concept explanations).

### States
**Default · Hover · Focus · Selected(activated) · Loading (generating suggestions).** Suggestions
are relevant to the current subject and prior turn (continuity).

### Accessibility (distinctive)
A labeled group of buttons/choice chips; keyboard operable; activating a suggestion is announced as
sending a question; suggestions are supplementary (the composer is always usable directly).

### Responsive
Wrap or horizontal-scroll chip row; reachable on touch.

### Token usage
Choice Chip tokens; `--accent`/`--brand` affinity (sparing) to read as AI-suggested.

### Motion (signature)
Suggestions reveal progressively `--motion-duration-base` (curiosity, not clutter). Reduced motion →
instant.

### Usage guidelines / Anti-patterns
- **Do** keep suggestions grounded in the current subject and the last turn; make them optional.
- ✗ Generic, context-free suggestions; ✗ suggestions that imply recommendations ("Should I buy?");
  ✗ a wall of suggestion chips that competes with reading.

---

## Thinking State ⟶ maps to: [AI Thinking state](../../design/13_States.md#ai-thinking)

### Purpose
Show the assistant **actively considering** the question *before output begins* — a calm, brief
moment of visible thought that reassures, not a generic spinner or a frozen void (§9).

### Anatomy
Within the embedded AI region: a small AI presence mark + a calm "thinking / gathering evidence"
indication (optionally naming the stage), on the AI surface. Never a separate destination.

### Variants
**Thinking** (considering) · **Gathering evidence** (the sourcing made visible — the trust-building
facet) · **Stage-named** (considering → gathering → reasoning).

### States
**Active** → transitions to **Streaming Response**, **Error**, or **Timeout** (bounded — never an
endless think).

### Accessibility (distinctive)
Announced as a busy state within the AI region; **does not steal focus** (the user can keep reading);
stage text is real text, not motion-only; cancelable where applicable.

### Responsive
Renders in the companion drawer / inline AI region at every size.

### Token usage
`--brand` presence mark (a sanctioned signal use — AI presence), `--muted-foreground` stage text,
calm `--motion-*`, `type.caption`/`type.label`.

### Motion (signature)
A gentle, continuous presence pulse or evidence-gathering cue — **calm, embedded, never theatrical**
(§9). Reduced motion → a static "Thinking…/Gathering evidence…" text (no info loss).

### Usage guidelines / Anti-patterns
- **Do** make thinking feel like a partner engaging; show evidence being gathered; bound it (Timeout).
- ✗ A generic spinner divorced from AI presence; ✗ dramatized "thinking" theatrics; ✗ stealing focus;
  ✗ an unbounded think with no timeout.

---

## Streaming Response ⟶ maps to: [AI Streaming state](../../design/13_States.md#ai-streaming)

### Purpose
Reveal AI output **progressively, at a human readable pace**, with **sources attaching as content
resolves** — turning the wait into visible, collaborative progress (§9).

### Anatomy
The response text streams into an AI Response Card; inline **citations** appear/attach as claims
resolve; a "stop generating" control; on completion, all sources are attached and the AI Action
Toolbar becomes available.

### States
**Streaming → Complete / Interrupted / Timeout.** Distinctive:
- **Interrupted/Timeout:** partial content is **retained** with a retry; prior content never lost
  (Law 6; Timeout state).
- **Complete:** every claim carries its source; content is distinguishable as AI.

### Accessibility (distinctive — critical)
Announced **considerately** (not per-character — batched/polite updates); completion announced;
sources keyboard-reachable as they attach; a stop control is labeled and reachable; streaming region
is a labeled live region.

### Responsive
Streams in the companion/inline region at every size; readable measure preserved.

### Token usage
`type.body`/`--leading-normal` (readable), citation affordances (`--brand`/`SourceReference`),
`--motion-duration-stream` (human pace), stop = Quiet/Icon Button.

### Motion (signature)
Text emerges at a legible cadence (`--motion-duration-stream`); citations attach with a subtle mark.
The signature "alive" moment — steady, not jarring. Reduced motion → content appears in progressive
chunks instantly (still progressive, no per-glyph animation), sources attach on resolve.

### Usage guidelines / Anti-patterns
- **Do** stream at a readable pace; attach sources as claims resolve; retain partials on interruption.
- ✗ A jarring full dump or a stalled void; ✗ per-character screen-reader spam; ✗ losing partial
  output on stop/timeout; ✗ finishing with any unsourced claim.

---

## AI Chat Bubble ⟶ composes: `CopilotPanel` turn (embedded)

### Purpose
Represent a single turn (user question / AI response) in the embedded contextual exchange. **Not** a
social-messenger bubble — a calm, editorial turn within the research companion.

### Anatomy
User turn: concise, right/inset, ink on subtle surface. AI turn: an **AI Response Card** (below) with
label, content, citations, toolbar. The exchange is threaded but calm and evidence-forward.

### Variants
**User turn** · **AI turn** (= AI Response Card) · **System/notice turn** (e.g. "not enough evidence",
access notice).

### States
User: **Sent.** AI: **Thinking · Streaming · Complete · Error/Timeout.**

### Accessibility (distinctive)
Turns are a labeled log/list; roles/authorship clear (who said what) textually, not by color alone;
AI turns distinguishable as AI in the accessibility tree; keyboard navigable.

### Responsive
Threaded list in the companion drawer / sheet; comfortable measure; reachable controls.

### Token usage
`--surface`/`--muted` (user turn), AI Response Card tokens, `type.body`, `type.label` (authorship).

### Motion (signature)
New turn enters `--motion-duration-base` (continuity). Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** keep the exchange embedded, calm, and evidence-forward; label authorship textually.
- ✗ A playful social-chat aesthetic; ✗ authorship by color/side alone; ✗ detaching the thread into a
  standalone chat destination (Law 5).

---

## AI Response Card ⟶ maps to: `AISummary` / `CopilotPanel` answer

### Purpose
Present a grounded AI answer or the company **AI Summary** — plain-language, source-backed, visibly
AI, honest about uncertainty. On SCR-06 the AI Summary **precedes figures** (summary before detail).

### Anatomy
`[ AI label + presence mark ] · [ optional Confidence Indicator ] · content (plain language) ·
inline citations · [ Evidence/Citation cards ] · [ AI Action Toolbar ]`. On a distinct AI surface so
it reads as AI, not primary source.

### Variants
**Company AI Summary** (SCR-06, precedes figures) · **Copilot answer** (Q&A) · **Filing analysis**
(anchored to filing) · **Learning explanation** (P-02, at the learner's level).

### States
**AI Thinking · AI Streaming · Loaded · Error · Timeout · Insufficient-evidence** (honest "can't
answer" — offers what *is* possible). Distinctive: never rendered without sources.

### Accessibility (distinctive)
Readable linearly; the AI label is in the accessibility tree (distinct from source); citations and
evidence keyboard-reachable; uncertainty stated in text; announced on completion.

### Responsive
Reflows to the companion/content width; citations remain reachable; measure preserved.

### Token usage
AI surface (`--surface` + `--brand` affinity mark, sparing), `type.body`/`--leading-normal`,
`SourceReference`/citation tokens, Confidence Indicator, AI Action Toolbar.

### Motion (signature)
Streams in (see Streaming Response); sources attach on resolve. Reduced motion → progressive chunks.

### Usage guidelines / Anti-patterns
- **Do** lead the company view with the AI Summary before figures; always attach sources; show
  uncertainty honestly; keep AI visibly distinct from source.
- ✗ AI answer without sources; ✗ AI styled identically to primary source (ambiguous provenance);
  ✗ a confident answer where evidence is thin (Law 8); ✗ any recommendation (Law 4).

---

## Citation Card ⟶ maps to: `SourceReference` (Inventory Molecule)

### Purpose
Link an AI claim to its **underlying evidence** — the trust mechanism. Present wherever an AI insight
appears; **never omitted** (Inventory rule; Law 3).

### Anatomy
Inline **citation** (a numbered/labeled reference within the text) and/or a **source list item**
(document · locator, e.g. "FY24 Annual Report, p.42"; "Q4 earnings call") that opens a Source Preview.

### Variants
Per Inventory: **Inline citation** · **Source list item.** Plus **Unavailable** (flagged, honest).

### States
Per Inventory: **Default · Focus · Unavailable (flagged).** Distinctive: an unavailable source is
**announced and flagged**, not silently dropped (honesty; Partial Failure).

### Accessibility (distinctive)
Descriptive, focusable link that names what it points to (never "source"/"click here"); the
inline↔list relationship is navigable; unavailable state announced; keyboard reachable (Law 3
requires the source path be keyboard-reachable).

### Responsive
Inline citations wrap with text; source list becomes a section/sheet on mobile; all reachable.

### Token usage
`brand`/link styling (evidence is always visibly reachable — Color §Usage), `type.caption`,
`--focus-ring-*`, `icon.*` (source type).

### Motion (signature)
Attaches with a subtle mark as a claim resolves (Gathering Evidence facet). Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** describe the target; keep every AI claim cited; flag unavailable sources honestly.
- ✗ Omitting a citation; ✗ vague "source" links; ✗ hiding that a source is unavailable.

---

## Source Preview ⟶ composes: `Popover`/`Drawer` + `SourceReference`

### Purpose
Let the user **verify evidence in place** — peek at the cited passage/filing section without losing
their research context (traceability made effortless).

### Anatomy
A [popover](06_Overlays.md) or side [drawer](06_Overlays.md) showing the source excerpt with the
relevant passage anchored/highlighted, the document/locator, and a link to the full source.

### Variants
**Inline peek** (popover — quick) · **Side preview** (drawer — read alongside) · **Filing anchor**
(jumps to the filing section, per `FilingViewer`).

### States
**Closed · Open · Loading · Unavailable · Error.** Unavailable/Error explain honestly and offer the
full source where possible.

### Accessibility (distinctive)
Opened from the citation with focus management + return-to-trigger (overlay contract); the anchored
passage is programmatically indicated; keyboard reachable; does not lose the user's place.

### Responsive
Popover on desktop → bottom sheet on mobile; drawer variant for read-alongside.

### Token usage
Overlay tokens (`--elevation-3`, `--shadow-md`, `--z-overlay/drawer`), highlight via `--accent`
(passage), `type.body`/`type.caption`.

### Motion (signature)
Reveal from the citation origin `--motion-duration-base` (continuity). Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** let users verify in place without losing context; anchor/highlight the cited passage.
- ✗ Forcing a full navigation away to see a source (loses place); ✗ a preview that can't reach the
  full source; ✗ hiding an unavailable source behind a broken preview.

---

## Evidence Card ⟶ composes: `SourceReference` group

### Purpose
Group the **evidence behind a specific insight** — the set of sources an AI claim/summary draws upon
— so grounding is *visible*, reinforcing trust (Gathering Evidence facet).

### Anatomy
A card listing the source references (document · locator · type) that support the adjacent AI
content, each opening a Source Preview; optional relevance/snippet.

### Variants
**Inline evidence** (attached under a claim) · **Evidence panel** (all sources for a response/summary).

### States
**Default · Loading (gathering) · Complete · Partial (some unavailable, flagged).**

### Accessibility (distinctive)
A labeled group associating evidence with its insight; each item a descriptive, focusable
SourceReference; partial/unavailable flagged textually.

### Responsive
Inline under the claim or a drawer panel on mobile; reachable.

### Token usage
Card tokens + SourceReference tokens; `type.caption`; `--brand` evidence affinity (sparing).

### Motion (signature)
Sources populate as gathered (progressive, `--motion-duration-base`) — the sourcing made felt.
Reduced motion → instant list.

### Usage guidelines / Anti-patterns
- **Do** make the evidence set for an insight visible and reachable; flag gaps honestly.
- ✗ An insight with hidden/absent evidence; ✗ evidence detached from the claim it supports.

---

## Confidence Indicator ⟶ composes: `Badge`/text (honest signal)

### Purpose
Communicate the **strength of evidence** behind an AI claim so confidence never exceeds evidence
(Law 8; §8) — an honesty instrument, not a score to inflate.

### Anatomy
A small textual indicator (e.g. "Well-supported" / "Limited evidence" / "Not enough evidence") with
an optional non-color cue; always paired with the reachable evidence.

### Variants
**Qualitative** (well-supported / limited / insufficient) — preferred, honest and plain. Avoid false
precision (no fake percentages implying certainty the evidence lacks).

### States
**Static** per claim; **Insufficient** → the AI states it plainly and offers what *is* possible.

### Accessibility (distinctive)
Meaning in **text**, never color/icon alone (§17); associated with the claim it qualifies; reachable.

### Responsive
Inline with the claim at every size.

### Token usage
`Badge`/text tokens; `warning`/`--muted-foreground` for limited/insufficient (with text);
`type.caption`/`type.label`.

### Motion (signature)
None (a steady, honest signal). Reduced motion: unaffected.

### Usage guidelines / Anti-patterns
- **Do** state confidence plainly and proportionately to evidence; pair with the evidence itself.
- ✗ Inflated/false-precision confidence (Law 8); ✗ confidence by color alone; ✗ high confidence with
  thin or unreachable evidence.

---

## AI Action Toolbar ⟶ composes: `Icon Button`s on an AI Response

### Purpose
Offer actions on an AI response — copy, add to research/report, view sources, regenerate, stop,
give feedback — **once content resolves** (not during a jarring stream).

### Anatomy
A compact row of labeled [icon buttons](01_Buttons.md) attached to an AI Response Card; appears on
completion/hover-focus; "stop" is available during streaming.

### Variants
**During streaming** (Stop) · **On complete** (Copy · Add to report/session · View sources ·
Regenerate · Feedback).

### States
**Streaming (Stop only) · Complete (full set) · Disabled (context-dependent).** Actions preserve the
response and its sources (Law 6).

### Accessibility (distinctive)
Each action a labeled icon button (foundation §8); keyboard reachable; "Add to report/session"
confirms quietly (Toast/undo); no action loses the response or its citations.

### Responsive
Compact row → overflow menu on mobile; primary actions stay visible.

### Token usage
Icon Button tokens; `--state-hover-surface`; Toast for confirmations.

### Motion (signature)
Toolbar reveals on completion `--motion-duration-base` (doesn't distract mid-stream). Reduced motion
→ instant.

### Usage guidelines / Anti-patterns
- **Do** keep Stop available while streaming; reveal the full set on completion; confirm adds with
  undo.
- ✗ Actions that strip citations when copying/adding (breaks traceability); ✗ a toolbar that competes
  with reading during streaming; ✗ any "act on this recommendation" action (Law 4).

---

## Family cross-references
- Companion surface & summon/recede behavior: [Overlays → Drawer](06_Overlays.md); Direction C.
- Canonical AI states: [States: AI Thinking / AI Streaming / Timeout](../../design/13_States.md).
- Filing-anchored analysis & report evidence: [Research Components](09_Research_Components.md)
  (`FilingViewer`, `ReportViewer`).
- Governing philosophy: [Constitution §8–9, Laws 3–5, 8](../../design/00_Design_Constitution.md).

*Family 08 of 09 · Phase 2 · Milestone 2*
