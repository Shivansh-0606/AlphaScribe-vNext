# AlphaScribe vNext — Design Constitution

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen — Governing Baseline |
| **Version** | 1.1 |
| **Phase** | Design (governing artifact) |
| **Owner** | Product & Design |
| **Approved By** | CTO |
| **Last Updated** | 2026-07-21 |
| **Source of Truth** | Yes — highest-level governing artifact for all Product & Design work |

**Downstream Dependencies:** Screen Inventory · UX Specifications · Wireframes · Design
System · Component Inventory · Interaction Patterns · Responsive Behavior · Accessibility ·
States · and every future Product & Design artifact.

> **Filename note:** This document was requested as `05_Design_Constitution.md`, but
> `05` was already assigned to the Screen Inventory. It is placed at `00_` to reflect
> its role as the artifact that **precedes and governs** the numbered blueprint
> (05–13), and to avoid overwriting existing work. Renumbering is a governance decision
> for CTO review.

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 1.0 | 2026-07-18 | Product & Design | 📝 Draft | Initial Design Constitution: the governing principles for all Product & Design decisions. Pending CTO approval to freeze. |
| 1.1 | 2026-07-18 | Product & Design | 📝 Draft | Post-CTO-review-1 experiential evolution: expanded North Star, Personality, Visual, Interaction, Motion, Micro-interaction, Anti-Patterns, Review Framework, and Immutable Laws; added Emotional Design (§5), Living Interface (§6), AI Experience (§9), and Spatial Design (§12). Raises experiential ambition (alive, premium, crafted) with no change to trust-first philosophy, features, IA, or Navigation. |
| 1.1 | 2026-07-21 | CTO | 🧊 Frozen | CTO confirms Product Design approved and frozen (Governance Recovery Execution, Phase 0 evidence for GRA-006). No content change. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Product Strategy](../master-plan/01_Product_Strategy.md), [Product Vision](../master-plan/02_Product_Vision.md), [Feature Roadmap](../master-plan/03_Feature_Roadmap.md), [User Personas](01_User_Personas.md), [User Journeys](02_User_Journeys.md), [Information Architecture](03_Information_Architecture.md), [Navigation Structure](04_Navigation_Structure.md) |
| **Used By** | [Screen Inventory](05_Screen_Inventory.md), [UX Specifications](06_UX_Specifications.md), [Wireframes](07_Wireframes.md), [Design System](08_Design_System.md), [Component Inventory](09_Component_Inventory.md), [Interaction Patterns](10_Interaction_Patterns.md), [Responsive Behavior](11_Responsive_Behavior.md), [Accessibility](12_Accessibility.md), [States](13_States.md), and all future Product & Design artifacts. |
| **Related Documents** | [Documentation Governance](../governance/Documentation_Governance.md), [Requirements Traceability Matrix](../governance/Requirements_Traceability_Matrix.md) |

> This is a **constitution**, not a design system or style guide. It defines
> non-negotiable principles and the review framework by which any design work is
> approved or rejected. It is deliberately implementation-agnostic, framework-neutral,
> and free of transient visual trends so it remains valid beyond the MVP.

---

# 1. Purpose

**Why this document exists.** AlphaScribe's promise is trustworthy, AI-native equity
research. That promise is kept or broken in the experience itself — in how information
is organized, how AI behaves, how sources are shown, and how the interface treats the
user's attention and work. This document fixes the principles that protect that promise
so they are not re-litigated in every design decision.

**Why AlphaScribe needs a Design Constitution.** The product will be built by many
people over time. Without a governing reference, quality drifts: each screen invents its
own patterns, AI creeps toward a generic chatbot, dashboards accrete charts, and trust
erodes one small decision at a time. A constitution makes the standard explicit and
enforceable.

**How it governs.** Every Product & Design artifact — Screen Inventory through States,
and everything after — must comply with this document. Where a lower artifact conflicts
with the constitution, the constitution wins; where the constitution conflicts with a
frozen product document (Strategy, Vision, Roadmap, Personas, Journeys, IA, Navigation),
that product document wins and the conflict is escalated for CTO review.

**Who should use it.** Product managers, designers, engineers implementing UI, QA
reviewers, and anyone approving design work.

**When to consult it.** At the start of any design task (to set direction), during
design reviews (to approve or reject), and whenever a decision feels subjective — the
constitution is the tiebreaker.

---

# 2. Design North Star

> **AlphaScribe should feel like a calm, living research workspace that actively thinks
> with you — intelligent, responsive, and continuously assisting, where every answer is
> grounded, every claim is traceable, and you always leave more confident than you
> arrived.**

The emotional destination is **earned confidence** — and that confidence comes from two
sources at once: **correctness** (the work is rigorous, grounded, and traceable) and
**craftsmanship** (the experience is responsive, fluid, and precise in every detail). One
without the other is incomplete: rigorous work in a lifeless shell feels untrustworthy;
polish without substance is hollow.

AlphaScribe is not a static dashboard that waits to be operated. It is a workspace that
**collaborates** — acknowledging the user's actions, revealing information as it becomes
relevant, and making the presence of an intelligent assistant felt without ever becoming
loud. The product should feel *alive and attentive*, yet unmistakably *calm*.

Every design decision should move the experience toward this feeling. A choice that makes
the product busier, noisier, flashier, or less trustworthy moves away from the North Star.
So does a choice that makes it feel dead, mechanical, or inert. Both failures are
departures from the destination.

---

# 3. Product Personality

AlphaScribe's personality is that of a **trusted senior analyst**: capable, composed, and
transparent. It never performs; it informs.

| Quality | What it means | How it shapes design |
|---------|---------------|----------------------|
| **Professional** | Serious about accuracy and craft. | Editorial clarity; no gimmicks; restraint over spectacle. |
| **Confident** | Sure of its work, without overstating. | Clear hierarchy; decisive defaults; calm affordances. |
| **Trustworthy** | Shows its evidence. | Sources always reachable; AI never presented as unquestionable. |
| **Focused** | Serves the research task. | One primary intent per screen; secondary things recede. |
| **Calm** | Never anxious or noisy. | Quiet color use; purposeful motion; generous space. |
| **Precise** | Exact, not vague. | Specific labels and copy; accurate figures with meaning. |
| **Transparent** | Hides nothing material. | Uncertainty is shown; AI content is distinguishable from source. |

The following complementary qualities give the personality its *life* — they are what
separate a premium AI-native workspace from a static enterprise tool. They coexist with,
and never override, the qualities above.

| Quality | What it means | How it shapes design |
|---------|---------------|----------------------|
| **Refined** | Considered down to the smallest detail. | Craftsmanship in every state, transition, and edge; nothing left rough. |
| **Dynamic** | Alive and attentive, never inert. | The interface responds to interaction and reflects its current state at all times. |
| **Responsive** | Acknowledges the user instantly. | Every input is met with immediate, proportionate feedback. |
| **Intelligent** | Feels like it is thinking with you. | AI presence is visible and collaborative; sensible defaults anticipate intent. |
| **Crafted** | Built with evident care. | Consistent rhythm, depth, and polish; details reward attention. |
| **Premium** | Quietly high-end. | Quality through refinement and restraint, not ornament. |
| **Elegant** | Simple made graceful. | Fluid transitions and spatial clarity; complexity resolved, not exposed. |

**Calm does not mean static.** Calm is the *absence of noise and anxiety*, not the absence
of life. A calm interface can still be fluid, responsive, and alive — it simply never
shouts.

**Professional does not mean lifeless.** Seriousness about accuracy and craft is expressed
through polish and responsiveness, not through rigidity. The most professional products in
the world feel meticulously alive.

Any design that reads as loud, playful, salesy, or opaque is off-personality — and so is
any design that reads as dead, sluggish, or mechanically inert.

---

# 4. Product Experience Philosophy

The experience is governed by these commitments, derived from the frozen
[Product Vision](../master-plan/02_Product_Vision.md) and
[Product Strategy](../master-plan/01_Product_Strategy.md):

- **Research before interface.** The interface serves the research task; it never becomes
  the point. Chrome recedes; content and evidence lead.
- **AI supports thinking, it does not replace it.** AI accelerates understanding and
  keeps the user as the decision-maker (Strategy: *AI as an assistant, never an authority*).
- **Reduce cognitive load.** Group related information; disclose progressively; never make
  the user hold more in mind than the task requires.
- **Respect user attention.** Every element must earn its place; nothing competes with the
  research for the user's focus.
- **Preserve user progress.** No action — including navigation and errors — may lose the
  user's work (Journeys: J-06).
- **Make confidence visible.** Grounding, explanation, and sources are shown, not implied,
  so trust is the default state.

---

# 5. Emotional Design Philosophy

This section defines the **emotional experience** AlphaScribe should create — not its
visual style. Craftsmanship is felt before it is seen; these are the feelings every design
decision should produce. They serve, and never compromise, the trust-first destination.

- **The interface should feel alive.** It responds, reflects its state, and conveys an
  attentive presence — never inert or frozen.
- **The interface should acknowledge user actions.** Every action is met with immediate,
  proportionate feedback, so the user always knows they were heard.
- **The interface should reward exploration.** Moving deeper into research feels smooth and
  worthwhile, never punishing or disorienting.
- **The interface should encourage curiosity.** It invites the next question and the next
  company, making the path to deeper understanding feel open.
- **The interface should reduce anxiety during AI operations.** Waiting on AI feels calm and
  legible — the user sees work happening, not a stalled void.
- **The interface should celebrate successful completion subtly.** Success is affirmed
  quietly and gracefully, never with fanfare that breaks the calm.
- **The interface should create confidence through responsiveness.** A system that reacts
  instantly and predictably *feels* trustworthy, reinforcing the confidence that correctness
  earns.
- **The interface should make waiting feel productive.** Progress and partial results turn
  waiting into visible advancement, not dead time.

Emotional design is a first-class requirement here, equal in weight to correctness. A
product that is right but feels lifeless has not met the North Star.

---

# 6. Living Interface Philosophy

The interface itself should feel **active** — a living workspace, not a static document. This
is a product philosophy, not implementation guidance.

- **Interfaces should react naturally to user interaction.** Response feels organic and
  immediate, as if the surface is aware of the user.
- **Components should feel responsive rather than static.** Elements acknowledge focus,
  hover, and selection with life, not rigidity.
- **Information should progressively reveal itself.** Content and detail emerge in a natural
  order as they become relevant, rather than appearing all at once or sitting inert.
- **Surfaces should feel layered and spatial.** The workspace has depth and relationship
  between foreground and background, giving structure a sense of place.
- **The application should always communicate its current state.** The user is never left
  guessing what the system is doing; state is continuously legible.
- **The interface should never feel frozen.** Even during heavy work, the product signals
  liveness — nothing appears hung or abandoned.
- **AI should appear actively working rather than simply loading.** AI presence reads as a
  partner gathering evidence and thinking, not a generic spinner.

A living interface is not a busy one. Liveness is expressed through responsiveness, depth,
and continuous state — never through noise, movement for its own sake, or visual clutter.

---

# 7. User Experience Principles

Each principle below is enforceable: a reviewer can approve or reject work against it.

## 7.1 One primary intent per screen
- **Principle:** Every screen has a single, obvious primary purpose.
- **Why:** Focus reduces cognitive load and speeds the research task (Strategy: minimal clicks).
- **Practical implications:** One primary action/region dominates; secondary options recede; competing calls-to-action are removed.
- **Good example:** Workspace Home leads unmistakably with company search.
- **Bad example:** A home screen giving equal weight to search, promotions, tips, and settings.
- **Exceptions:** None for MVP screens.
- **Review checklist:** ☐ Is the primary intent identifiable in under two seconds? ☐ Does anything compete with it that could be demoted or removed?

## 7.2 Summary before detail
- **Principle:** Present the summarized view first; detail on demand.
- **Why:** Progressive disclosure matches how the personas research (P-01, P-02) and prevents overload.
- **Practical implications:** Overviews and plain-language summaries precede raw figures and statements.
- **Good example:** A company opens on business summary and key metrics, with statements a step deeper.
- **Bad example:** Landing a user directly in a dense financial statement.
- **Exceptions:** A user's explicit deep-link to a detail level.
- **Review checklist:** ☐ Does the highest level appear first? ☐ Is detail reachable without being forced up front?

## 7.3 Every insight is traceable
- **Principle:** Any AI-generated or derived claim exposes a path to its source.
- **Why:** Traceability is the product's core differentiator (Trusted AI).
- **Practical implications:** Insights carry a reachable source reference; nothing authoritative is source-less.
- **Good example:** A summary claim links to the filing passage it derives from.
- **Bad example:** A confident metric or statement with no way to verify it.
- **Exceptions:** None.
- **Review checklist:** ☐ Can the user reach the evidence for every claim? ☐ Is the source path keyboard-reachable?

## 7.4 Never lose the user's work
- **Principle:** No interaction discards in-progress or saved research.
- **Why:** Durable research is a promised value (J-06).
- **Practical implications:** Back, navigation, errors, and timeouts preserve context; Resume Session restores prior reasoning and sources.
- **Good example:** Returning from an error retains the active session.
- **Bad example:** A failed request resetting the screen to blank.
- **Exceptions:** Explicit, confirmed user-initiated discard.
- **Review checklist:** ☐ Does every exit path preserve work? ☐ Is any destructive action explicit and confirmed?

## 7.5 Predictable and consistent
- **Principle:** The same element behaves the same way everywhere.
- **Why:** Consistency lowers the learning cost and builds trust.
- **Practical implications:** Shared patterns/components reused; no bespoke one-offs where a standard exists.
- **Good example:** Source references look and behave identically across screens.
- **Bad example:** Three different comparison behaviors in three places.
- **Exceptions:** A genuinely novel need with no existing pattern — then it becomes the new standard.
- **Review checklist:** ☐ Does this reuse existing patterns? ☐ Would a user be surprised by any behavior here?

## 7.6 Recovery over failure
- **Principle:** Every dead-end state offers a way forward.
- **Why:** Trust survives failure only if the user is never stuck.
- **Practical implications:** Empty, error, no-result, and permission states each provide a next step.
- **Good example:** "No matches — refine or broaden your search."
- **Bad example:** A blank screen after a failed search.
- **Exceptions:** None.
- **Review checklist:** ☐ Does every non-happy state provide a recovery action?

---

# 8. AI Integration Philosophy

AI must feel like an **embedded research partner**, never a separate chatbot
(Vision: *not "ChatGPT for Finance"*).

- **When AI appears:** within the research context it supports — summarizing a company,
  answering a question about the current subject, interpreting a filing, explaining a
  concept, or comparing companies. It is reached in place, not visited as a destination.
- **When AI stays silent:** when it has nothing grounded to add; when the user is reading
  or navigating and AI would interrupt; when a request falls outside available evidence.
- **How AI explains itself:** as reasoning the user can follow, in plain language, never a
  bare verdict. It shows how a conclusion was reached.
- **How AI cites sources:** every insight carries a reachable path to its evidence; sources
  attach as/after content resolves; AI content is visibly distinguishable from source
  material.
- **How AI earns trust:** by being grounded (from primary sources, not open-ended memory),
  explainable, and consistent — the same rigor every time.
- **How AI handles uncertainty:** it states uncertainty plainly rather than fabricating
  confidence; it prefers an honest "not enough evidence" to a confident guess.
- **How AI encourages learning:** for learners (P-02), it explains at the learner's level,
  ties concepts to the real company, and invites the next question instead of closing the
  topic.

**AI must never:** issue buy/sell/financial recommendations; present itself as an
authority above the user; hide its uncertainty; or appear as a standalone chat divorced
from research context.

**Review checklist:** ☐ Is the AI embedded in a research context (not a separate chatbot)?
☐ Is every AI claim grounded and source-linked? ☐ Is AI content distinguishable from
source material? ☐ Is uncertainty shown honestly? ☐ Does AI avoid recommendations and
remain an assistant?

---

# 9. AI Experience Philosophy

Where §8 governs how AI *behaves*, this section governs how AI *feels*. AI is the most
visible expression of the product's intelligence, and its experience is where "alive" and
"collaborative" are won or lost. These are experience principles, not implementation.

- **AI should appear to think.** Before output begins, the user perceives the assistant
  actively considering the question — a moment of visible thought, not a dead pause.
- **AI should progressively reveal work.** Understanding unfolds in a natural order rather
  than arriving as a sudden monolithic block.
- **AI should stream naturally.** Output emerges at a human, readable pace — legible as it
  arrives, never a jarring dump or a stalled wait.
- **AI should communicate progress.** The user always senses forward motion: gathering,
  reasoning, resolving.
- **AI should feel collaborative.** It reads as a partner working *with* the user on their
  research, not a black box returning a verdict.
- **AI should visibly gather evidence.** Because insight is grounded, the experience makes
  the sourcing felt — the user sees evidence being drawn upon, reinforcing trust.
- **AI should reduce uncertainty while remaining honest.** The experience is reassuring and
  steady, yet never manufactures false confidence; honesty about limits is part of feeling
  trustworthy.

The AI experience must always remain **calm and embedded**. Liveness here means presence and
progress, never theatrics — the assistant is felt, not performed. This section adds nothing
to what AI *does* (§8 and the frozen Vision govern that); it only raises how its work should
*feel*.

**Review checklist:** ☐ Does the AI appear to think and progress, not just spin? ☐ Does
output stream at a readable, natural pace? ☐ Does the experience feel collaborative and
evidence-gathering? ☐ Is it reassuring without overstating confidence? ☐ Does it stay calm
and embedded (no theatrics)?

---

# 10. Information Architecture Principles

These govern how financial information is organized, consistent with the frozen
[Information Architecture](03_Information_Architecture.md).

- **Summary before detail** — the most summarized level appears first.
- **Business before metrics** — understand what the company does before its numbers.
- **Explanation before visualization** — a metric's meaning precedes its chart; a number
  never appears without what it means.
- **Always preserve traceability** — insight remains structurally attached to its source.
- **Progressive disclosure** — depth is available on demand, never forced.
- **Related information stays together** — everything about one company lives in one place;
  each fact has a single home (no duplication).

**Review checklist:** ☐ Does information flow summary → detail? ☐ Is business context shown
before figures? ☐ Does every metric carry its meaning? ☐ Is every insight traceable to a
source? ☐ Is anything duplicated that should be referenced instead?

---

# 11. Visual Philosophy

The visual language is calm, editorial, and precise. Specific colors and components are
defined downstream in the [Design System](08_Design_System.md); this section governs the
*intent* behind them.

- **Hierarchy:** the eye is guided to what matters first; importance is unambiguous.
- **Whitespace:** space is a tool for grouping and calm, not emptiness to be filled.
- **Density:** dense enough to be efficient for research, never so dense it overwhelms.
- **Rhythm:** consistent spacing and repetition create a predictable, readable cadence.
- **Balance:** composition feels settled, not lopsided or cramped.
- **Contrast:** used to signal importance and ensure legibility, never for decoration.
- **Restraint:** emphasis is scarce and therefore meaningful; the signature accent is used
  sparingly.
- **Consistency:** one visual system, applied uniformly; the same meaning always looks the
  same.

**Premium is built, not decorated.** A premium visual experience emerges from the disciplined
combination of the following — none of which is ornament:

- **Thoughtful motion** — transitions and feedback that make the interface feel considered.
- **Depth** — spatial layering that gives structure a sense of place (see §12).
- **Rhythm** — consistent cadence that makes composition feel intentional.
- **Progressive reveal** — information that unfolds gracefully rather than appearing inert.
- **Visual breathing room** — generous space that signals confidence and calm.
- **Elegant transitions** — state changes that feel natural and continuous.
- **Carefully crafted interaction feedback** — the small responses that make quality felt.

Premium quality comes from **refinement, not decoration**: the removal of the unnecessary and
the perfecting of the essential. The product should look like a premium research instrument —
alive and crafted — not a marketing page or a trend-chasing dashboard.

---

# 12. Spatial Design Philosophy

The workspace should feel **spatial** — surfaces with depth and relationship, not flat panels
stacked on a page. Spatial design is how the interface communicates structure, focus, and
liveness without noise. This section is intent only; it prescribes no glassmorphism, blur,
shadow, color, or component values (those, where appropriate, belong to the
[Design System](08_Design_System.md)).

- **Visual depth:** the interface has a sense of near and far that helps the user read
  structure at a glance.
- **Layer hierarchy:** surfaces are ordered by importance and role, so the eye understands
  what sits above what.
- **Focus management:** the current focus is spatially clear; what matters now comes forward,
  what doesn't recedes.
- **Surface relationships:** related surfaces feel connected; unrelated ones feel distinct.
- **Elevation:** raised surfaces (transient, contextual, or active content) read as elevated
  in a consistent, meaningful way.
- **Context awareness:** the space reflects where the user is and what they are doing, giving
  orientation without extra chrome.
- **Foreground/background distinction:** primary work is unmistakably in front; supporting
  context sits behind without competing.
- **Ambient polish:** depth and layering are applied with restraint to create quiet
  refinement — felt, not noticed.

Spatial depth serves clarity and calm. It must never become decorative texture, and it must
never obscure content, reduce contrast, or compromise accessibility.

---

# 13. Interaction Philosophy

Interactions should feel effortless and dependable — natural, not mechanical.

- **Predictable:** actions do what the user expects; the same action always yields the same
  result.
- **Intentional:** every interaction has a clear purpose; nothing exists to be clever.
- **Responsive:** the system acknowledges input immediately, even when the result takes time.
- **Forgiving:** mistakes are easy to recover from; destructive actions are guarded.
- **Efficient:** the path from intent to result is as short as the task allows.
- **Natural:** interactions follow the user's intuition; nothing feels stiff, abrupt, or
  arbitrary.
- **Responsive feedback:** every input produces immediate, proportionate acknowledgment.
- **Predictive behaviour:** the product anticipates likely intent with intelligent defaults,
  reducing steps before the user asks.
- **Smooth state transitions:** moving between states feels continuous, never a jarring cut.
- **Intelligent defaults:** the most helpful option is chosen for the user by default, kept
  simple and overridable.
- **Seamless continuity:** context carries across actions and screens so the experience feels
  like one continuous flow.

Interactions reduce user effort by removing steps, remembering context, anticipating intent,
and never making the user re-do work the system could preserve. The goal is interaction that
feels *effortless* — as if the product is one step ahead — not merely functional.

---

# 14. Motion Philosophy

**Motion must communicate. Motion must never distract from research.**

Motion is a primary instrument of craftsmanship and liveness — used well, it is much of what
separates a premium experience from a static one. Beyond communicating, purposeful motion
should:

- **Create continuity** — connect where the user was to where they are.
- **Build confidence** — a responsive, fluid system feels trustworthy.
- **Reinforce hierarchy** — direct the eye to what matters, in what order.
- **Guide attention** — lead the user through a change without a jarring cut.
- **Improve perceived performance** — make waits feel shorter and work feel underway.
- **Reward interaction** — acknowledge the user's action with a satisfying, proportionate
  response.
- **Express craftsmanship** — the precision and quality of motion is felt as care.
- **Create emotional continuity** — sustain a calm, coherent feeling across the experience.
- **Make AI feel alive** — convey the assistant thinking, gathering, and streaming.
- **Make transitions feel natural** — state changes read as organic, not mechanical.
- **Provide subtle delight** — small, refined moments that make the product a pleasure to use.

**Purposeful delight is encouraged; meaningless spectacle is prohibited.** The line is
*distraction*: motion must never pull attention away from research, never be excessive, and
never exist purely as ornament. It is always brief, calm, and in service of understanding.

- **Transitions:** signal continuity — where the user came from and where they are now.
- **Feedback:** confirm that input was received and something is happening.
- **State changes:** make shifts (loading → loaded, thinking → streaming) legible and fluid.
- **Progress indication:** show that long or AI-bound work is advancing, not frozen.
- **Reduced motion:** all motion respects the user's reduced-motion preference; when
  reduced, motion is minimized or replaced with an instant change, losing no information.

**Review checklist:** ☐ Does each motion communicate, guide, or reassure? ☐ Is it refined and
proportionate (not excessive or ornamental)? ☐ Could it distract from research (if so, reduce
it)? ☐ Is reduced-motion honored with no information loss?

---

# 15. Content & Copywriting Principles

Words are part of the interface and carry the same standard of clarity and trust.

- **Plain language:** clear, direct, and human; explain before quantifying.
- **Professional tone:** informative and neutral — never hype, never marketing
  (Strategy: free of marketing language).
- **Explain financial terminology:** define terms in context for learners (P-02); never
  assume fluency the user may not have.
- **Avoid unnecessary jargon:** use precise terms when they add meaning, plain words
  otherwise.
- **Transparent AI wording:** AI content is labeled as such and phrased so its evidence is
  clear; never implies certainty it doesn't have; never gives recommendations.
- **Action-oriented labels:** buttons and controls name their outcome ("Export report",
  "Resume Session"), never vague ("OK", "Go").
- **Consistent terminology:** use the frozen vocabulary (Company Research, Research Session,
  Resume Session, Trusted AI) verbatim; never coin synonyms.

**Review checklist:** ☐ Is the copy plain, neutral, and specific? ☐ Are financial terms
explained? ☐ Is AI wording transparent and recommendation-free? ☐ Do labels name outcomes?
☐ Is terminology consistent with the frozen baseline?

---

# 16. Information Density & Readability

- **When to summarize:** by default, and at every entry into a topic — lead with the
  shortest true version.
- **When to expand:** on the user's demand, or when the task genuinely requires detail
  (statements, filings).
- **How to avoid overwhelming users:** show one level of depth at a time; keep dense data in
  its own scannable region; never surface everything at once.
- **Progressive disclosure:** the primary lever for managing density — depth is layered, not
  dumped.
- **Financial data presentation:** figures are aligned and scannable, paired with meaning,
  and never presented as an undifferentiated wall of numbers.
- **Reading comfort:** comfortable reading width and rhythm for text-heavy research; research
  is a reading task and the layout must respect that.

---

# 17. Accessibility Constitution

Accessibility is **mandatory**, not a phase. The target is **WCAG 2.1 AA**, defined in full
in [Accessibility](12_Accessibility.md); the constitution fixes it as non-negotiable.

- **Keyboard navigation:** every action and movement is fully keyboard operable; no
  pointer-only paths; no keyboard traps.
- **Focus order:** logical, matching reading order; visible focus always; predictable focus
  on navigation and on error.
- **Screen readers:** correct roles, names, states, and landmarks; dynamic changes and AI
  streaming announced appropriately.
- **Contrast:** meets AA; meaning is never conveyed by color alone.
- **Semantic structure:** sequential headings and native semantics first; ARIA only to fill
  genuine gaps.
- **Motion reduction:** honored everywhere, with no loss of information.
- **Error messaging:** specific, text-based, associated with its region, and recoverable.
- **Inclusive design:** designed for the full range of users and inputs from the start, not
  retrofitted.

**Review checklist:** ☐ Fully keyboard operable? ☐ Visible, logical focus? ☐ Correct
semantics and announcements? ☐ AA contrast, no color-only meaning? ☐ Reduced motion
honored? ☐ Errors specific and associated?

---

# 18. Responsive Design Principles

Principles, not layouts (layouts live in [Responsive Behavior](11_Responsive_Behavior.md)).

- **Content priority:** the research task stays primary at every size; smaller contexts
  prioritize the current task and condense the rest.
- **Interaction adaptation:** interactions adapt to input (pointer, touch) without changing
  what is possible.
- **Navigation consistency:** structure and destinations are identical across contexts; only
  presentation density adapts — no destination appears in one context and not another.
- **Touch ergonomics:** adequate target sizing and spacing; no mis-tap traps.
- **Reading comfort:** comfortable reading and legibility preserved across all sizes.

---

# 19. Micro-interaction Philosophy

Small interactions build (or erode) confidence. They are where craftsmanship is felt most
directly — the accumulated quality of a hundred tiny, refined responses is what makes a
product feel premium and alive.

- **Feedback:** every input is acknowledged immediately.
- **Hover behaviour:** reveals affordance or supplementary help; never hides essential
  content behind hover alone.
- **Selection:** clearly and consistently indicated, non-color-only.
- **Loading:** communicated with skeletons/progress, scoped to the affected region.
- **Confirmation:** outcomes are confirmed briefly and clearly.
- **Undo:** where feasible, prefer reversible actions and offer undo over hard confirmation
  dialogs.
- **Progress:** long operations always show advancement, never a frozen wait.
- **Empty states:** explain why something is empty and offer the next step.

The following refine these into the premium quality AlphaScribe is held to:

- **Every interaction acknowledges the user.** Nothing the user does goes unrecognized.
- **Hover states reveal confidence.** Hover communicates that an element is ready and
  responsive, reinforcing that the interface is alive.
- **Selection feels intentional.** Choosing something feels deliberate and satisfying, not
  incidental.
- **Loading feels alive.** Waiting reads as active work — skeletons and progress that
  reassure, never an inert blank.
- **Success feels satisfying.** Completion is affirmed with quiet grace that rewards the user.
- **Empty states encourage action.** Emptiness invites the next step rather than signaling a
  dead end.
- **Progress indicators reassure users.** The user always sees that the system is advancing.
- **Components respond naturally.** Elements react with organic, proportionate life, never
  stiffly.

Subtle, consistent micro-interactions make the product feel dependable, premium, and alive —
because the user is never left guessing whether the system heard them, and every small moment
is crafted. Refinement, not spectacle, is the goal.

---

# 20. Error, Empty & Success State Philosophy

The emphasis is always **recovery, not failure**. Canonical behaviors live in
[States](13_States.md); the constitution fixes the attitude.

- **Nothing exists (Empty):** explain the emptiness and offer a first step; never a blank
  dead end.
- **Search returns nothing (No Results):** show the query, and offer to refine, broaden, or
  clear.
- **AI cannot answer:** say so honestly; offer what is possible; never fabricate a confident
  answer.
- **Errors occur:** specific, non-blaming language; state the next step; preserve the user's
  work; keep navigation available.
- **Work completes (Success):** confirm clearly and briefly, then let the user continue.

No state may trap the user or lose work.

---

# 21. Performance-Aware Design

Design decisions must respect that research often happens on imperfect networks.

- **Perceived performance:** favor immediate acknowledgment and progressive reveal over
  waiting for completeness.
- **Skeleton loading:** preserve layout and set expectations while structured content loads.
- **Progress feedback:** every wait shows advancement; nothing appears frozen.
- **Incremental rendering:** show what is ready as it becomes ready; AI streams rather than
  blocks.
- **Avoid unnecessary visual complexity:** fewer, purposeful elements render faster and read
  clearer.
- **Design for slow networks:** graceful degradation and partial results (Partial Failure)
  rather than all-or-nothing.

---

# 22. Trust & Transparency Principles

Trust is the product. It is earned by construction, not by claim.

- **Every AI insight is explainable** — the user can follow the reasoning.
- **Every important statement is traceable** — a path to evidence is always reachable.
- **Never hide uncertainty** — the interface shows what is unknown or unavailable.
- **Never exaggerate confidence** — tone and presentation match the strength of the evidence.
- **Always distinguish AI-generated content from source material** — the user always knows
  what is AI reasoning versus primary source.

**Review checklist:** ☐ Is every AI insight explainable? ☐ Is every important claim
traceable? ☐ Is uncertainty shown honestly? ☐ Is confidence proportionate to evidence? ☐ Is
AI content visibly distinct from source?

---

# 23. Anti-Patterns (Mandatory)

AlphaScribe must **never** become the following. Each is prohibited because it breaks the
North Star, the personality, or the trust promise.

| Anti-pattern | Why it is harmful |
|--------------|-------------------|
| **Generic AI SaaS** | Interchangeable, trustless; abandons the research-desk identity and the trust differentiator. |
| **ChatGPT clone / standalone chatbot** | Contradicts the embedded-AI philosophy; strips context and source grounding (Vision: *not "ChatGPT for Finance"*). |
| **Dashboard overloaded with charts** | Density without meaning; raises cognitive load and buries the research. |
| **Glassmorphism / decorative effects** | Ornament over clarity; distracts from content and dates quickly. |
| **Meaningless gradients** | Decoration masquerading as design; dilutes the signature accent's meaning. |
| **Visual clutter** | Competes with research for attention; erodes calm and focus. |
| **Excessive, distracting, or meaningless animation** | Pulls attention from research and breaks calm; motion that neither communicates, guides, nor delights with purpose is ornament (see §14). |
| **Hidden navigation** | Breaks predictability; makes users hunt and lose their place. |
| **Dark patterns** | Betray user trust — categorically forbidden; the product exists to earn trust. |
| **Feature overload** | Contradicts the focused MVP; dilutes the one thing done exceptionally well. |
| **Unexplained AI outputs** | Directly attacks the trust promise; an unsourced, unexplained claim is worse than none. |
| **Poor accessibility** | Excludes users and violates the accessibility constitution. |
| **Static, lifeless, or inert interfaces** | The opposite failure: a product that never responds, reveals, or acknowledges reads as a dead enterprise dashboard and abandons the premium, alive experience. |

**The problem is distraction, not animation.** Subtle delight, refinement, responsiveness,
and premium motion are **encouraged** — they are how the product feels alive and crafted. What
is prohibited is motion (or any effect) that distracts from research, is excessive, or is
purely ornamental. Liveness and calm are partners, not opposites.

Any work exhibiting these anti-patterns is rejected on sight.

---

# 24. Design Review Framework

Every design review evaluates the work against the following. Questions are measurable — a
reviewer answers yes/no and the work is rejected on any material "no."

## Product Experience
- ☐ Is the screen's single primary intent obvious?
- ☐ Does it advance an approved journey (J-01–J-06) and serve a persona (P-01/P-02)?
- ☐ Does it move toward the North Star (earned confidence through correctness *and*
  craftsmanship)?
- ☐ **Does the interface feel alive** rather than static or inert?
- ☐ **Does the product feel premium** — crafted, refined, and considered?
- ☐ **Does the product create emotional confidence** through its responsiveness?

## UX
- ☐ Summary before detail?
- ☐ Consistent with existing patterns (no gratuitous one-offs)?
- ☐ Does every non-happy path offer recovery?

## Accessibility
- ☐ Fully keyboard operable with visible, logical focus?
- ☐ AA contrast and no meaning by color alone?
- ☐ Correct semantics and announcements, reduced motion honored?

## Consistency
- ☐ Uses frozen terminology verbatim?
- ☐ Reuses design tokens/components rather than inventing values?

## Trust
- ☐ Is every AI claim explainable and source-traceable?
- ☐ Is AI content distinguishable from source material?
- ☐ Is uncertainty shown honestly, with no exaggerated confidence?

## Motion
- ☐ Does each animation communicate, guide, or reassure?
- ☐ **Does motion improve understanding** (continuity, hierarchy, perceived performance)?
- ☐ Is it refined and proportionate — never excessive, distracting, or ornamental?
- ☐ Is reduced-motion honored with no information loss?

## Interaction & Craft
- ☐ **Does interaction acknowledge the user** immediately and proportionately?
- ☐ **Does the interface feel responsive** and natural rather than mechanical?
- ☐ **Does craftsmanship appear in every interaction** — states, transitions, and edges?
- ☐ Are intelligent defaults and continuity reducing user effort?

## Performance
- ☐ Immediate acknowledgment and progressive reveal?
- ☐ Skeletons/progress for waits; degrades gracefully on slow networks?
- ☐ Does waiting feel productive (visible progress, partial results)?

## AI
- ☐ Embedded in research context (not a standalone chatbot)?
- ☐ No recommendations; assistant, not authority?
- ☐ **Does AI feel actively collaborating** — thinking, gathering evidence, streaming?
- ☐ Is AI presence reassuring without overstating confidence?

## Readability
- ☐ Density managed via progressive disclosure?
- ☐ Financial data paired with meaning and comfortably readable?

## Premium Experience
- ☐ Does it feel calm, precise, and crafted — not decorated or trend-chasing?
- ☐ Is restraint evident (emphasis scarce and meaningful)?

---

# 25. Design Constitution — Immutable Laws

These are the governing rules for all future Product & Design work. They change only by a
governance Change Request with CTO approval.

1. **Clarity is more valuable than novelty.**
2. **Research comes before presentation.**
3. **Every important claim must be traceable to its source.**
4. **AI must always explain itself, and never issue recommendations.**
5. **AI is an embedded research partner, never a standalone chatbot.**
6. **Users must never lose completed or in-progress work.**
7. **Interfaces should reduce thinking, not increase it.**
8. **Uncertainty is shown honestly; confidence never exceeds the evidence.**
9. **Consistency beats creativity.**
10. **Accessibility is mandatory, not optional.**
11. **Motion must communicate, and must never distract from research.**
12. **Premium comes from craftsmanship and restraint — not decoration.**
13. **Every state offers a path forward; the user is never trapped.**
14. **Nothing exists in the interface that does not earn its place.**
15. **No dark patterns — ever.**
16. **The interface must feel alive — responsive, spatial, and continuously aware of its state.**
17. **Calm and alive are partners, not opposites; the product is never static, never noisy.**
18. **Confidence is earned by correctness and by craftsmanship, together.**

These laws are the highest-level governing rules for AlphaScribe's Product & Design work.
Where any artifact conflicts with them, the artifact is wrong.
