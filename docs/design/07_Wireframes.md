# AlphaScribe vNext — Wireframes (Low-Fidelity)

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 0.1.1 |
| **Phase** | Design (pre-PRD) |
| **Owner** | Product & Design |
| **Approved By** | CTO |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For screen information hierarchy |

**Downstream Dependencies:** Component Inventory · Interaction Patterns · Responsive
Behavior · Design Specifications · PRDs

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft | Initial low-fidelity, structured-text wireframes for the eleven MVP screens. |
| 0.1.1 | 2026-07-18 | Product & Design | 📝 Draft | Experiential alignment to the Design Constitution (v1.1): added interaction-intent Experience Annotations (progressive reveal, AI thinking/streaming, evidence, continuity, depth) and applied them to the Company Research wireframe. Remains low-fidelity; no visual styling added. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Design Constitution](00_Design_Constitution.md), [Screen Inventory](05_Screen_Inventory.md), [UX Specifications](06_UX_Specifications.md), [Navigation Structure](04_Navigation_Structure.md), [Information Architecture](03_Information_Architecture.md) |
| **Used By** | [Component Inventory](09_Component_Inventory.md), [Responsive Behavior](11_Responsive_Behavior.md), Design Specifications, PRDs. |
| **Related Documents** | [User Journeys](02_User_Journeys.md), [Design System](08_Design_System.md) |

> These are **low-fidelity** wireframes expressed as structured text. They show
> **information hierarchy and region composition only** — not visual design, spacing,
> sizing, color, or components. Regions map to areas defined in the IA and Navigation
> Structure. No new screen regions or features are introduced.

---

# Conventions

- Boxes denote **regions**, not components; nesting denotes containment/priority.
- `[Global Nav]` and `[Global Search]` are the same persistent regions across screens
  (defined in [Navigation Structure](04_Navigation_Structure.md)); shown per screen
  for completeness, specified once here.
- `AI:` marks an AI-bearing region (embedded, per Vision — never a separate chatbot).
- Order top-to-bottom reflects information priority, not pixel position.

## Experience Annotations

These wireframes remain low-fidelity and carry **no visual styling**. To align with the
[Design Constitution](00_Design_Constitution.md), regions may be annotated with *interaction
intent* — how the region should feel and behave over time — never with visual design. The
following markers appear where relevant:

- `↻ reveal` — content should **progressively reveal** rather than appear inert or all at once.
- `⋯ thinking` — an AI region should read as **actively thinking** before output.
- `≋ streaming` — AI output **streams naturally** as it resolves.
- `⌖ evidence` — sources **visibly attach** to the insight as it resolves.
- `→ continuity` — a transition into/out of this region should **preserve context** (no reset).
- `↧ depth` — this region sits on a distinct **spatial layer** (foreground/background
  relationship), per Spatial Design (§12) — depth of meaning, not a visual effect.

Annotations describe *intended experience only*; the Design System and downstream UX own how
they are realized. They inherit the Constitution's Living Interface (§6), AI Experience (§9),
Motion (§14), and Spatial Design (§12) philosophies.

**Shared frame (applies to all authenticated screens):**

```
┌─ Header ──────────────────────────────────────────────┐
│ [Brand]      [Global Search]           [Account/Menu]  │
├─ Global Navigation ───────────────────────────────────┤
│ Home · Research · Compare · Learning · Library · Settings │
├─ Main Content (per screen) ───────────────────────────┤
│ ...                                                    │
├─ Footer ──────────────────────────────────────────────┤
│ [Legal/Support links]                                  │
└───────────────────────────────────────────────────────┘
```

For each screen below: **Header · Navigation · Main Content · AI Areas · Side Panels ·
Footer · Primary Actions · Secondary Actions.**

---

# SCR-01 — Landing Page

```
┌─ Header ──────────────────────────────────────────────┐
│ [Brand]                              [Sign in ▸]       │
├─ Main Content ────────────────────────────────────────┤
│  Value proposition (what AlphaScribe is)               │
│  Trust positioning (grounded · explainable · sourced) │
│  [ Get started ]  ← primary entry                      │
├─ Footer ──────────────────────────────────────────────┤
│ [Legal · Support]                                      │
└───────────────────────────────────────────────────────┘
```
- **Header:** Brand; sign-in entry. **Navigation:** minimal (public).
- **Main Content:** value → trust → entry. **AI Areas:** none. **Side Panels:** none.
- **Footer:** legal/support. **Primary Actions:** Get started. **Secondary Actions:** Sign in.

---

# SCR-02 — Authentication

```
├─ Main Content ────────────────────────────────────────┤
│  ( Sign in | Sign up )  ← mode                         │
│  Identity fields                                       │
│  [ Continue ]  ← primary                               │
│  Forgot password? ← secondary                          │
│  Inline validation / error region                      │
```
- **Header:** brand only (pre-session). **Navigation:** none.
- **Main Content:** mode → fields → submit → recovery. **AI Areas:** none. **Side Panels:** none.
- **Footer:** legal/support. **Primary Actions:** Continue. **Secondary Actions:** Switch mode; Forgot password.

---

# SCR-03 — Onboarding & AI Setup

```
├─ Main Content ────────────────────────────────────────┤
│  Choose AI access:                                     │
│   ( ) Managed AI  — zero setup                         │
│   ( ) Bring your own key (BYOK)                        │
│       └ key field (conditional)                        │
│  Validation status region                              │
│  [ Continue ]  ← enabled on validated access           │
```
- **Header:** brand; account menu. **Navigation:** suppressed until setup complete.
- **Main Content:** access choice → conditional key → validation → continue.
- **AI Areas:** access validation only (setup, not research). **Side Panels:** none.
- **Footer:** support. **Primary Actions:** Continue. **Secondary Actions:** Switch access model.

---

# SCR-04 — Workspace Home

```
├─ Main Content ────────────────────────────────────────┤
│  [ Search a company ______________ ]  ← primary focus  │
│  Recent Research                                       │
│   • <company> — <date>                                 │
│   • <comparison> — <date>                              │
│   (Empty state if none)                                │
```
- **Header + Global Nav:** shared frame. **Main Content:** search (primary) → recent research.
- **AI Areas:** none (routes into AI screens). **Side Panels:** none.
- **Footer:** shared. **Primary Actions:** Search. **Secondary Actions:** Open recent item; go to a domain.

---

# SCR-05 — Search Results

```
├─ Main Content ────────────────────────────────────────┤
│  [ Query ____________ ]  [Filter]                      │
│  Results                                               │
│   • Company: <name>                                    │
│   • Prior research: <title> — <date>                   │
│  Recent searches                                       │
│  (No-results guidance region)                          │
```
- **Header + Global Nav:** shared. **Main Content:** query/filter → results → recent searches.
- **AI Areas:** none. **Side Panels:** optional filter region.
- **Primary Actions:** Select result. **Secondary Actions:** Refine query; filter; open recent search.

---

# SCR-06 — Company Research

```
├─ Secondary Navigation (within company) ───────────────┤
│ Overview · Financials · Filings · AI Insights · Export │
├─ Main Content ────────────────────────────────────────┤
│  Company header (name · identity)                      │
│  Overview → Business Summary                            │
│  Financial Metrics (with meaning)                       │
│  Financial Statements (tables)                          │
│  SEC Filings (viewer)                                   │
├─ AI Areas ────────────────────────────────────────────┤
│  AI Summary (grounded, top of insights)   ⋯ thinking ≋ streaming ⌖ evidence │
│  AI: Copilot (contextual Q&A, embedded)   ⋯ thinking ≋ streaming            │
│  AI: Filing Analysis (within Filings)     ⌖ evidence                        │
│  Every insight → [Jump to source]                      │
├─ Side Panels ────────────────────────────────  ↧ depth ┤
│  Copilot panel (embedded, context = this company)  → continuity │
│  Source references                             ⌖ evidence       │
```
- **Header + Global Nav:** shared. **Secondary Navigation:** company content sections (IA levels).
- **Main Content:** content hierarchy Overview→Filings. **AI Areas:** Summary, Copilot, Filing Analysis — all embedded and sourced.
- **Side Panels:** embedded copilot; sources. **Footer:** shared.
- **Primary Actions:** Ask copilot; Save/Export research. **Secondary Actions:** Add to comparison; Explain this (→ Learning); Jump to source.

---

# SCR-07 — Comparison

```
├─ Main Content ────────────────────────────────────────┤
│  Selected companies: [A] [B] [+ add]                   │
│  Comparative table                                     │
│   Metric      | A     | B                              │
│   ...         | ...   | ... (⚠ not comparable)         │
├─ AI Areas ────────────────────────────────────────────┤
│  AI: explanation of differences (embedded, sourced)    │
```
- **Header + Global Nav:** shared. **Main Content:** company set → comparative table.
- **AI Areas:** embedded difference explanation. **Side Panels:** optional copilot (difference Q&A).
- **Primary Actions:** Add/remove company; Save comparison. **Secondary Actions:** Open a member (→ SCR-06); ask about a difference.

---

# SCR-08 — Learning

```
├─ Main Content ────────────────────────────────────────┤
│  Company example context (reference)                   │
│  Concept explanation (learner-level)                   │
│  Related concepts / next question                      │
│  Self-check region                                     │
├─ AI Areas ────────────────────────────────────────────┤
│  AI: Learning Assistance (embedded, sourced)           │
│  Concept → [Jump to source] · [Back to company]        │
```
- **Header + Global Nav:** shared. **Main Content:** company context → explanation → related/self-check.
- **AI Areas:** embedded learning assistance. **Side Panels:** copilot (concept Q&A).
- **Primary Actions:** Ask/Explain. **Secondary Actions:** Self-check; jump to source; return to company.

---

# SCR-09 — Research Library

```
├─ Main Content ────────────────────────────────────────┤
│  [Filter]                                              │
│  Research Sessions                                     │
│   • <company/comparison> — <date>  [Resume Session]    │
│  Research Reports                                      │
│   • <title> — <date>                                   │
│  Saved Exports                                         │
│   • <artifact> — <date>                                │
│  Research History                                      │
│  (Empty / No-results regions)                          │
```
- **Header + Global Nav:** shared. **Main Content:** sessions → reports → saved exports → history.
- **AI Areas:** none (returns to AI research). **Side Panels:** optional filter.
- **Primary Actions:** Resume Session; Open report/export. **Secondary Actions:** Filter; open history item.

---

# SCR-10 — Report View

```
├─ Main Content ────────────────────────────────────────┤
│  Report title / subject company                        │
│  Conclusion / summary                                  │
│  Reasoning                                             │
│  Detailed content                                      │
│  Sources                                               │
├─ Primary Actions ─────────────────────────────────────┤
│  [ Export ]                                            │
```
- **Header + Global Nav:** shared. **Main Content:** conclusion → reasoning → detail → sources.
- **AI Areas:** report is AI-generated (upstream), source-backed. **Side Panels:** source references.
- **Primary Actions:** Export. **Secondary Actions:** Inspect source; return to company.

---

# SCR-11 — Settings

```
├─ Main Content ────────────────────────────────────────┤
│  Account                                               │
│   • details + edit                                     │
│  AI Access                                             │
│   • Managed AI / BYOK + status  [Re-validate]          │
│  Session                                               │
│   • [ Sign out ]                                       │
```
- **Header + Global Nav:** shared. **Main Content:** account → AI access → session.
- **AI Areas:** access validation only. **Side Panels:** none.
- **Primary Actions:** Save changes. **Secondary Actions:** Re-validate AI access; Sign out.
