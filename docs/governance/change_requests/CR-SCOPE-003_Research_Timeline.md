# Change Request — CR-SCOPE-003: Research Timeline

| Field | Value |
|-------|-------|
| **CR ID** | CR-SCOPE-003 |
| **Title** | Research Timeline (presentation of Research History) |
| **Status** | 🟡 Open — Awaiting CTO decision |
| **Raised By** | Experience Design Department (Milestone 2, Phase 2) |
| **Raised On** | 2026-07-18 |
| **Type** | Presentation clarification (potential no-op vs. minor scope) |
| **Affects** | Component Inventory · Screen Inventory · Research Library (IA domain) |
| **Decision** | ☐ Approve ☐ Reject ☐ Defer — _pending_ |

> Raised because Milestone 2's component brief lists a **Research Timeline**, and it must be confirmed
> whether this is (a) an alternate *presentation* of the already-MVP **Research History** capability —
> which would introduce **no new scope** — or (b) a new activity/audit-tracking capability, which
> would exceed the MVP. Unlike CR-001/002, the underlying capability here is **already in the MVP**.

---

## 1. Feature Description

A **Research Timeline** presents the user's research activity/history in chronological order —
sessions, reports, and history events grouped by time — with a **Resume Session** affordance to return
to prior work. Two possible interpretations:

- **(A) Presentation of Research History** — a chronological visual treatment of the **Research
  History** and **Research Sessions** that already exist in the MVP Research Library. *No new data or
  capability; a design choice within an existing domain.*
- **(B) New activity/audit timeline** — a richer log tracking every user action/event over time
  (beyond saved sessions/reports/history). *This would be new capability and scope.*

This CR exists to force that choice explicitly.

## 2. Why It Was Flagged

While composing Family 09, "Research Timeline" did not map to a named frozen *screen*, only to a
*capability* (Research History). The risk is interpretation (B) quietly adding an
activity-tracking/audit capability the baseline does not define. Interpretation (A) is in-scope but
should be confirmed as the intended, bounded reading.

## 3. Current Traceability Against Frozen Baseline

| Baseline document | Finding | Verdict |
|-------------------|---------|---------|
| **Product Strategy** | Emphasizes research continuity and "recall over reconstruction"; durable, resumable research is a core value. Consistent with a history view. | ✅ Consistent (as history) |
| **Product Vision** | MVP Goals include "Save research for future reference"; Research Sessions capability is MVP. | ✅ In scope (as history) |
| **Information Architecture** | **Research Library** domain explicitly contains **"Research History"** (and Research Sessions, Reports, Saved Exports). Research History is a first-class MVP surface. | ✅ In scope (interp. A) |
| **Navigation Structure** | **Research Library** global destination = "sessions, reports, history"; **Resume Session** is the canonical return action (J-06); "Research History" is a discovery surface. | ✅ In scope (interp. A) |
| **Feature Roadmap** | **MVP → Research Sessions:** "Durable Research Sessions, Saved Reasoning, Saved Sources, Resume Research, **Research History**." | ✅ In scope (interp. A) |

**Summary:** Interpretation **(A)** — a timeline presentation of **Research History** — is fully
within the frozen MVP (five documents confirm Research History as MVP). Interpretation **(B)** — a new
activity/audit-tracking capability — is **not** in the baseline and would be out of MVP scope.

## 4. User Value

- **P-01 & P-02:** medium-high — a clear chronological view of prior research directly supports J-06
  (never lose work; resume) and "recall over reconstruction." A timeline can make Resume Session more
  intuitive than a flat list.
- Value is realized entirely by presenting **existing** Research History well; no new capability is
  required to deliver it.

## 5. Business Value

- **Retention:** positive — an inviting way back into prior work reinforces AlphaScribe as the return
  workspace (a stated success metric).
- **Cost:** near-zero for interpretation (A) (it reuses existing data); meaningful for (B).

## 6. Engineering Complexity

- **Interpretation (A):** **Low** — a chronological presentation of already-persisted Research
  Sessions/History; reuses existing data and the Research Library. Primarily a UI grouping/sorting
  concern.
- **Interpretation (B):** **Medium-high** — requires capturing, storing, and modeling granular
  activity events (a new event log), with its own privacy considerations. Out of MVP.

## 7. UX Impact

- **(A):** additive and low-risk — a presentation option *within* the Research Library domain
  (alongside/instead of a list). Must reuse the frozen **Research Session** / **Resume Session**
  vocabulary and the `ListItem` "Research Session" pattern. No new destination.
- **(B):** would add a distinct surface and states, and risks becoming an activity feed that competes
  with the calm research focus.

## 8. AI Impact

- Minimal. The timeline displays prior research (which already contains grounded AI insights and their
  sources); it introduces no new AI behavior. It must **not** editorialize or rank past research
  (no recommendations — Law 4). Resuming a session restores that session's AI context (Resume Session
  facet).

## 9. Dependencies

- **(A):** Research Sessions / Research History (already MVP); the `ListItem` "Research Session"
  variant and Resume Session action (already specified).
- **(B):** a new activity-event capture/storage capability (not in baseline).

## 10. Risks

- **Scope drift from (A) into (B):** the main risk — a "timeline" invites feature-creep toward a full
  activity log. Must be explicitly bounded to presenting Research History.
- **Terminology drift:** must use frozen vocabulary (Research Session, Resume Session, Research
  History), not coin "activity"/"feed".
- **Redundancy:** if it duplicates the Research Library list without added clarity, it adds surface
  without value.

## 11. Recommended Release

- **Interpretation (A): MVP** — as a presentation of the existing Research History within the Research
  Library (no roadmap change).
- **Interpretation (B): Defer (Future)** — as a new capability, not justified for the MVP.

## 12. CTO Recommendation

### → **Approve — bounded to Interpretation (A)** (Reject interpretation B)

**Rationale:** The underlying capability (**Research History**) is already MVP-frozen in five
documents, so presenting it as a timeline introduces **no new scope** and directly strengthens J-06
(resume, never lose work) at near-zero engineering cost. **Recommendation: Approve** the Research
Timeline **strictly as an optional presentation of Research History within the Research Library
domain**, reusing the frozen Research Session / Resume Session vocabulary and introducing **no** new
data, capability, destination, or activity/audit log. **Reject** interpretation (B) (a new
activity-tracking capability) for the MVP; if desired later, it returns as its own CR.

**Guardrail for design:** the Research Timeline component may proceed *only* as a view over existing
Research Sessions/History. If, during design, it requires any event/data not already produced by the
Research Sessions capability, design must stop and re-raise this CR.

---

*Change Request raised under the [Documentation Governance](../Documentation_Governance.md) process.
Frozen baseline remains authoritative until this CR is explicitly approved.*
