# AlphaScribe vNext — State Catalogue

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Version** | 0.1.1 |
| **Phase** | Design (pre-PRD) |
| **Owner** | Product & Design |
| **Approved By** | _Pending_ |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For screen/component state behavior (pending approval) |

**Downstream Dependencies:** Frontend implementation · QA Test Plans · PRDs · Acceptance Criteria

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft | Initial definitive state catalogue for MVP screens, components, and interactions. |
| 0.1.1 | 2026-07-18 | Product & Design | 📝 Draft | Experiential alignment to the Design Constitution (v1.1): enriched AI Thinking/Streaming with experience guidance; added Experiential State Facets (Gathering Evidence, Progressive Rendering, Saving Research, Resume Session, Context Restored, Partial Results, Synchronization, Confidence Building) as facets of existing states/capabilities. No new features. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Design Constitution](00_Design_Constitution.md), [Screen Inventory](05_Screen_Inventory.md), [UX Specifications](06_UX_Specifications.md), [Component Inventory](09_Component_Inventory.md), [Interaction Patterns](10_Interaction_Patterns.md), [Accessibility](12_Accessibility.md) |
| **Used By** | Frontend implementation, QA Test Plans, Acceptance Criteria, PRDs. |
| **Related Documents** | [Navigation Structure](04_Navigation_Structure.md), [Design System](08_Design_System.md), [Responsive Behavior](11_Responsive_Behavior.md) |

> This is the **definitive** catalogue of states referenced throughout the blueprint.
> Screens, components, and interactions name these states rather than re-defining them.
> Behavior only — no implementation. All states honor the WCAG AA requirements in
> [Accessibility](12_Accessibility.md).

---

# Introduction

Every screen in the [Screen Inventory](05_Screen_Inventory.md) declares a set of
**Required States**; every such state is defined once here across a fixed set of
facets: **Purpose · Trigger · Displayed Information · Available Actions · Recovery
Behaviour · Accessibility Requirements.**

Two universal rules govern all states (from the Vision, Strategy, and Navigation
Structure):

- **Never trap the user** — every state offers a way forward or back.
- **Never lose work** — no state discards in-progress research (J-06).

---

# State Applicability Matrix

| State | Primary screens |
|-------|-----------------|
| Loading | All |
| Skeleton | SCR-06, SCR-07, SCR-09, SCR-10 |
| Empty | SCR-04, SCR-06, SCR-07, SCR-09 |
| No Results | SCR-05, SCR-09 |
| Offline | All (global) |
| Permission Denied | SCR-03, SCR-06, SCR-11 |
| Authentication Required | All protected (SCR-02 gate) |
| Error | All |
| Partial Failure | SCR-06, SCR-07 |
| Success | SCR-02, SCR-03, SCR-10, SCR-11 |
| Timeout | SCR-06, SCR-08, SCR-10 (AI/export) |
| AI Thinking | SCR-06, SCR-07, SCR-08 |
| AI Streaming | SCR-06, SCR-07, SCR-08 |

---

# Loading

- **Purpose:** Indicate that requested content or an action is in progress.
- **Trigger:** Any asynchronous fetch or submission begins.
- **Displayed Information:** A clear in-progress indication scoped to the affected region; existing content remains until replaced.
- **Available Actions:** Navigation remains available; the user is never blocked from moving elsewhere; the in-progress action is not re-triggerable.
- **Recovery Behaviour:** Resolves to Loaded, Empty, Error, or Timeout; prolonged loads escalate to Timeout.
- **Accessibility Requirements:** Region announced as busy; focus not stolen; progress not conveyed by motion alone.

# Skeleton

- **Purpose:** Preserve layout and set expectations while structured content loads.
- **Trigger:** A content region (metrics, statements, library lists, report) is loading its data.
- **Displayed Information:** Placeholder structure mirroring the eventual content shape; no fabricated values.
- **Available Actions:** Surrounding navigation and loaded regions remain usable.
- **Recovery Behaviour:** Replaced in place by real content, Empty, or Error.
- **Accessibility Requirements:** Announced as loading; placeholders are not read as real data.

# Empty

- **Purpose:** Communicate that a region legitimately has no content yet, with a path forward.
- **Trigger:** No data exists for a region (e.g. no recent research, no comparison members, no saved research).
- **Displayed Information:** A plain explanation of why it's empty and what to do next.
- **Available Actions:** A clear next step (e.g. start a search, add a company, begin research); never a dead end.
- **Recovery Behaviour:** Transitions to content once the user acts.
- **Accessibility Requirements:** Empty message and its action are announced and keyboard reachable.

# No Results

- **Purpose:** Communicate that a query/filter matched nothing.
- **Trigger:** Search or filtering returns zero matches (SCR-05, SCR-09).
- **Displayed Information:** That nothing matched, with the active query/filters visible.
- **Available Actions:** Refine, broaden, or clear filters; return to the full set.
- **Recovery Behaviour:** Adjusting the query/filters returns results without losing prior input.
- **Accessibility Requirements:** Zero-result outcome announced; refine/clear actions reachable.

# Offline

- **Purpose:** Inform the user that connectivity is lost and set expectations.
- **Trigger:** Network connectivity is unavailable.
- **Displayed Information:** A calm notice of limited connectivity and what remains possible.
- **Available Actions:** Retry when back online; the user keeps their place and in-progress work.
- **Recovery Behaviour:** Graceful degradation; restores automatically or on retry when connectivity returns, without losing context.
- **Accessibility Requirements:** Status announced; not conveyed by color/icon alone.

# Permission Denied

- **Purpose:** Communicate that an action isn't permitted in the current access state.
- **Trigger:** An action requires access the user doesn't currently have (e.g. AI access not validated; a restricted operation).
- **Displayed Information:** What is restricted and the recoverable path (e.g. configure/validate AI access).
- **Available Actions:** A clear route back to a permitted state (e.g. to Onboarding & AI Setup / Settings); never a hard stop.
- **Recovery Behaviour:** Resolving the access requirement restores the action.
- **Accessibility Requirements:** Message announced; recovery path keyboard reachable.

# Authentication Required

- **Purpose:** Enforce the login wall while preserving intent.
- **Trigger:** An unauthenticated user reaches a protected screen, or a session expires.
- **Displayed Information:** That sign-in is needed to continue.
- **Available Actions:** Proceed to Authentication (SCR-02); the intended destination is remembered where possible.
- **Recovery Behaviour:** After sign-in, the user returns to their intended destination; unsaved intent is preserved where feasible.
- **Accessibility Requirements:** Redirect and messaging announced; focus moves to the sign-in entry.

# Error

- **Purpose:** Communicate a failure clearly and recoverably.
- **Trigger:** A request or action fails.
- **Displayed Information:** What happened and the next step, in specific, non-blaming language; scoped to the affected region.
- **Available Actions:** Retry and/or an alternative path; global and back navigation remain available.
- **Recovery Behaviour:** Retry resolves transient errors; the user never loses in-progress work or the ability to move on.
- **Accessibility Requirements:** Announced assertively for blocking errors; text-based; associated with the region/field.

# Partial Failure

- **Purpose:** Show available information when some parts fail — critical for best-effort data sources.
- **Trigger:** Some data/sections succeed while others fail (e.g. a financial source unavailable; a comparison member not comparable). Aligns with the Vision's best-effort external-source principle.
- **Displayed Information:** The successful content, with failed parts clearly flagged (not silently omitted).
- **Available Actions:** Use what's available; retry the failed part independently.
- **Recovery Behaviour:** Failed parts can recover without discarding the rest; the screen never collapses wholesale.
- **Accessibility Requirements:** Failed/"not comparable" regions announced explicitly; not blank-by-implication.

# Success

- **Purpose:** Confirm that an action completed.
- **Trigger:** An action (sign-in, AI setup validation, export, settings save) succeeds.
- **Displayed Information:** A clear, brief confirmation of the outcome.
- **Available Actions:** Continue the workflow; the confirmation does not block.
- **Recovery Behaviour:** N/A (terminal-positive); the user proceeds.
- **Accessibility Requirements:** Confirmation announced politely; not conveyed by color alone.

# Timeout

- **Purpose:** Bound waits that run too long (notably AI and export).
- **Trigger:** An operation exceeds a reasonable time without resolving (SCR-06/08 AI; SCR-10 export).
- **Displayed Information:** That it's taking longer than expected and what the user can do.
- **Available Actions:** Retry or cancel; any partial output already produced (e.g. streamed AI text) is retained.
- **Recovery Behaviour:** Retry restarts the operation; partial results and context are preserved; never a silent hang.
- **Accessibility Requirements:** Timeout status announced; retry/cancel reachable.

# AI Thinking

- **Purpose:** Signal that the embedded AI is preparing a response, before output begins.
- **Trigger:** An AI insight, copilot answer, filing analysis, or learning explanation is requested.
- **Displayed Information:** A clear "working" indication within the embedded AI region (never a separate destination).
- **Available Actions:** The user can continue reading existing content; the request can be cancelled where applicable.
- **Recovery Behaviour:** Transitions to AI Streaming, Error, or Timeout.
- **Accessibility Requirements:** Announced as a busy state; does not steal focus.
- **Experience (Constitution §9):** AI should *appear to think* — a calm, brief moment of visible consideration that reads as a research partner engaging with the question, not a generic spinner or a frozen wait. It reassures without over-dramatizing; the user feels the assistant is working *with* them.

# AI Streaming

- **Purpose:** Reveal AI output progressively as it is produced.
- **Trigger:** The AI begins returning a response.
- **Displayed Information:** Partial output readable as it arrives; sources attach as/after content resolves (source traceability preserved).
- **Available Actions:** Read as it streams; stop generation; inspect sources once present.
- **Recovery Behaviour:** Interruption/Timeout leaves partial content with a retry; prior content retained; completion attaches all sources.
- **Accessibility Requirements:** Streaming announced considerately (not per-character); completion announced; sources keyboard reachable (see [Accessibility](12_Accessibility.md)).
- **Experience (Constitution §9):** Output should *stream naturally* at a human, readable pace — understanding unfolding progressively, evidence visibly gathering and attaching as it resolves. It should feel collaborative and reassuring, turning the wait into visible, productive progress, never a jarring dump or a stalled void.

---

# Experiential State Facets

Beyond the canonical states above, the [Design Constitution](00_Design_Constitution.md)
requires that certain moments *feel* a particular way. The following are **experiential
facets** of the existing states and capabilities — how a moment should feel, not new product
features. They add no capability, endpoint, or scope; each maps to a canonical state or an
already-approved capability.

| Facet | Maps to | How it should feel |
|-------|---------|--------------------|
| **AI Thinking** | AI Thinking state | The assistant *considering* the question — present and calm, not a spinner. |
| **Streaming** | AI Streaming state | Understanding *unfolding* at a readable pace; alive, collaborative. |
| **Gathering Evidence** | AI Thinking/Streaming + Trusted AI | The user *sees* sources being drawn upon and attaching — grounding made visible, reinforcing trust. |
| **Progressive Rendering** | Loading / Skeleton | Content *arriving in priority order* (summary first), the screen usable before completion — fast and alive, never a blank wait. |
| **Saving Research** | Loading → Success (Research Sessions) | Preserving work feels *effortless and safe* — quiet acknowledgment that reasoning and sources are secured, never anxiety about loss. |
| **Resume Session** | Resume Session (Navigation/J-06) | Returning feels like *stepping back into a living workspace* — continuous, not a cold restart. |
| **Context Restored** | Resume Session / Back navigation | Prior reasoning, sources, and place *return intact*; the user feels remembered and oriented. |
| **Partial Results** | Partial Failure state | What's available is shown *confidently*, gaps flagged honestly — useful and trustworthy rather than broken. |
| **Synchronization** | State consistency (not a new sync feature) | The interface stays *consistent with the user's saved research* — never stale or contradictory. *This describes the experience of consistency only; it introduces no background-sync capability.* |
| **Confidence Building** | Cross-cutting (responsiveness + traceability) | The cumulative feeling that the product is *rigorous and responsive* — confidence earned through both correctness and craftsmanship (Constitution North Star). |

Each facet honors the two universal state rules: **never trap the user, never lose work.**

---

# Consistency Notes

- State names here are canonical; other blueprint documents reference them verbatim.
- AI states (Thinking, Streaming) are always **embedded** within research contexts,
  consistent with the Vision and [Design System](08_Design_System.md) AI principles —
  never a standalone chatbot surface.
- Partial Failure and Timeout directly support the frozen product principle that
  external data is best-effort and must degrade gracefully rather than crash a workflow.
