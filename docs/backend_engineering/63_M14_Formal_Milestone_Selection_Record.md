# 63 — M14 Formal Milestone Selection Record

**Status:** 🟢 **M14 MILESTONE FORMALLY SELECTED — M14 = C-1 FILING
ANALYSIS.** This document records a **separate CTO milestone-selection
decision** taken on 2026-08-30, subsequent to and **distinct from** the CTO
ratification of
[62_Post_M13_Backend_AI_Roadmap_Reconciliation.md](62_Post_M13_Backend_AI_Roadmap_Reconciliation.md).
It performs the "formal M14 milestone selection" gate that Document 62 §13 /
§16 explicitly reserved as its own subsequent CTO act. **Selecting the
milestone authorizes progression to the contract-governance stage only. It
authorizes no contract, no architecture, no source/test/schema/
infrastructure change, no RAG, no persistence, no LangGraph change, no
Filing Q&A, no implementation, no commit, and no push** — see §5, §7, §8.
**Type:** Governance / milestone-selection decision record (documentation
only — no source code, test, schema, API route, migration, index,
configuration, infrastructure, LangGraph topology, MongoDB
collection/schema, Redis, provider, RAG, G8, H-1, or Gate state created or
modified to produce this record; Documents 58, 59, 60, 61 read, not
modified; Document 62 read, not modified). The only file this task creates
is this document.
**Date:** 2026-08-30.
**Precedent / lineage.** For M13 the milestone-direction selection was
folded into contract/architecture ratification (Document 59 §14 + Document
60 selecting the M13 direction from Document 58 §21). Document 62
deliberately **un-folds** that step for M14: its §11, §13, and §16 record
"formal M14 milestone selection" as a distinct CTO act that roadmap
ratification does **not** perform. This record is that act, written in the
short standalone decision-record form of
[54_M10_Governance_Authorization_Reconciliation_Record.md](54_M10_Governance_Authorization_Reconciliation_Record.md),
[56_M12_Governance_Authorization_Reconciliation_Record.md](56_M12_Governance_Authorization_Reconciliation_Record.md),
and
[61_M13_Governance_Authorization_Reconciliation_Record.md](61_M13_Governance_Authorization_Reconciliation_Record.md).
None of those precedents is modified by this document.

---

## 0. What This Document Is and Is Not

**Is:** a record of one CTO governance decision — the formal selection of
C-1 Filing Analysis as the M14 milestone — plus a precise statement of the
governance state that selection creates and the gates that still stand
between M14 and implementation.

**Is not:** a contract, an API contract proposal, an architecture decision
pack, a scope freeze, an implementation authorization, a commit
authorization, a push authorization, an amendment to any frozen or historical
document, a reopening of M13, or a reopening of H-1 / G8. It resolves no
open architectural question — the Filing Analysis chunk-vs-section question
(§6) stays open exactly as Document 62 §7 left it. It creates no endpoint,
no schema, no index, no migration, no test, no LangGraph node, no
`window.claude`-style runtime, and introduces no dependency.

---

## 1. Decision

**M14 = C-1 Filing Analysis — FORMALLY SELECTED.**

C-1 Filing Analysis — grounded AI analysis scoped to a single filing, over
the filing content that M13 now serves — is hereby **formally selected as
the M14 milestone**. This advances C-1 from the "preferred roadmap
direction" status established by Document 62 to "formally selected
milestone", and thereby opens the M14 **contract-governance stage**. It
does nothing else. C-1's substance, scope, exclusions, and the open
sequencing question are unchanged from Document 62 §6 / §7 / §9 / §10.

---

## 2. Decision Date

**2026-08-30.**

Same calendar date as the CTO ratification of Document 62 (Document 62 §16),
but a **separate, subsequent decision** — see §4.

---

## 3. Authority

This is a **separate CTO milestone-selection decision**, taken by the CTO
**following** and **on top of** the CTO ratification of Document 62 (Post-M13
Backend & AI Roadmap Reconciliation), which occurred on 2026-08-30 and is
recorded in Document 62 §16.

Document 62's ratification adopted the reconciliation's findings and named
C-1 the **preferred roadmap direction**; it did **not** select the M14
milestone, and it said so explicitly (Document 62 §11, §13, §16, §14 item 1).
The present decision is the distinct governance act that Document 62
reserved for later. This record **only records** that decision; it invents
no authority, issues no authorization beyond milestone selection, and
implies none.

---

## 4. Relationship to Document 62

- **Document 62 established C-1 Filing Analysis as the preferred roadmap
  direction.** That was the whole of what its ratification did on the M14
  question (Document 62 §9, §11, §16).
- **Document 62 did not formally select M14.** It states this in terms:
  "C-1 is NOT formally selected as the M14 milestone" and "Formal M14
  milestone selection remains a separate CTO decision" (Document 62 §16;
  see also §11, §13, §14 item 1, and the closing block).
- **This document performs that separate selection gate.** It consumes the
  "formal M14 milestone selection" step named in Document 62 §13's
  gate sequence and §14 item 1's "FORMAL M14 SELECTION PENDING" status,
  and it does not touch, reinterpret, re-ratify, or amend Document 62 —
  Document 62 is cited here, not edited.

The ordered progression this decision sits within — each arrow a distinct
CTO act that does **not** confer the next:

```text
Document 62
CTO-RATIFIED POST-M13 ROADMAP
        ↓
C-1
PREFERRED ROADMAP DIRECTION
        ↓
THIS GOVERNANCE DECISION
        ↓
M14 = C-1 FILING ANALYSIS
FORMALLY SELECTED
        ↓
M14 CONTRACT PROPOSAL
        ↓
CONTRACT RATIFICATION
        ↓
ARCHITECTURE DECISION PACK
        ↓
ARCHITECTURE RATIFICATION
        ↓
IMPLEMENTATION AUTHORIZATION
```

Downstream of implementation authorization, the further separate acts of
Document 62 §13 still apply in order: engineering implementation → technical
review → commit authorization → push authorization.

---

## 5. Current M14 Governance State

```text
M14 milestone:      FORMALLY SELECTED
M14 direction:      C-1 Filing Analysis
Contract:           NOT YET PROPOSED / NOT RATIFIED
Architecture:       NOT YET PROPOSED / NOT RATIFIED
Implementation:     NOT AUTHORIZED
Commit:             NOT AUTHORIZED
Push:               NOT AUTHORIZED
```

Formal M14 selection does **NOT** authorize any of the following:

- contract implementation;
- architecture implementation;
- source-code changes;
- test changes;
- schema changes;
- infrastructure changes;
- RAG adoption;
- persistence (new field / collection / store);
- structured filing-section extraction (C-2);
- LangGraph topology changes;
- Filing Q&A (multi-turn or single-turn conversational);
- implementation of any kind;
- commit;
- push.

In particular, formal M14 selection does **not** constitute contract
approval, architecture approval, implementation authorization, commit
authorization, or push authorization. Each of those remains gated behind its
own subsequent CTO governance act in the §4 progression.

---

## 6. Architecture Uncertainty (preserved, not resolved)

The following question, surfaced by Document 62 §7 and left open by its
ratification (Document 62 §16), **remains open** and is **not** resolved by
this milestone selection:

> Whether Filing Analysis can operate effectively over the existing
> persisted **unstructured** filing chunks (`chunk_idx` + `text`, ~900
> chars, 120-char overlap, no section identity, no headings), or whether it
> **requires** C-2 Structured Filing Extraction as a prerequisite, is an
> **open contract / architecture decision**.

Consequences of leaving it open, restated from Document 62 so this record
stands alone:

- **C-2 Structured Filing Extraction remains only a _possible_ technical
  sequencing prerequisite** for C-1 — not a confirmed one, not a governance
  blocker. **C-2 is not selected as M14; C-2 is not rejected.** Whether C-2
  must precede C-1 is for the M14 contract / architecture phase to decide.
- A legitimate outcome of that phase is a decision to **sequence C-2 before
  C-1**, which would re-order the roadmap. This milestone selection is made
  with that possibility explicitly open.
- Whether RAG / retrieval is introduced into this new surface, whether
  analysis output is computed on demand or persisted, and the citation
  mechanism, all remain **OPEN** design decisions for the contract /
  architecture phase (Document 62 §7, §10).

This document does not answer any of these. It records that M14 is C-1 and
that these questions travel into the contract stage unchanged.

---

## 7. Scope Boundary (carried forward from Document 62 §10, unchanged)

M14 / C-1 Filing Analysis is **bounded Filing Analysis**. It must **NOT**
become:

- a generic filing chatbot or general-purpose conversational agent;
- multi-turn Filing Q&A (Filing Q&A stays **excluded** from C-1 / M14 and
  remains a future, **separately scoped** capability);
- cross-filing comparison, trend analysis, or any multi-filing aggregation
  (no cross-filing reasoning);
- an ingestion redesign (no change to `agents/ingest.py`, `chunk_text`,
  chunk size, or overlap);
- a provider redesign or a new provider dependency (LLM access stays
  through `agents/llm.py`);
- premature RAG — retrieval into this new surface is **not** assumed;
- persisted analysis — persistence is **not** adopted here and is
  introduced only if later justified and approved in the contract /
  architecture phase;
- a persistent research-session system — Durable Research Sessions remain
  `BLOCKED` (Document 62 §6 C-4 / Document 58 §10) and are **not** in M14
  scope;
- unrelated financial visualization (that is C-3, a separate frontend
  initiative);
- any G8 remediation step or any change to H-1 / G7 / the judge / the
  self-consistency gate;
- any change to Documents 59 / 60 / 61 or to the M13 implementation.

The M14 contract phase sets the real, binding scope. The list above is the
inherited high-level boundary, not a contract.

---

## 8. Downstream Governance

**The next authorized governance activity is preparation of the M14
contract proposal** — a new "M14 Filing Analysis API Contract" artifact —
subject to the project's normal governance process (`docs/governance/`
change-request and ratification chain, mirroring how Documents 59 / 60 were
produced and ratified for M13).

To be precise:

> **Selection of M14 authorizes progression to the contract-governance
> stage. It does not authorize implementation.**

No code, test, schema, index, migration, configuration, infrastructure,
LangGraph, MongoDB, or Redis change is authorized by this record. The M14
contract proposal, its ratification, the M14 architecture decision pack,
its ratification, and a separate implementation-authorization decision must
all occur — in that order, each a distinct CTO act — before any Filing
Analysis source code may be written (§4).

The frontend track (C-3 Financial Visualization) and the governance-hygiene
track (C-5) remain independent of this milestone selection, exactly as
Document 62 §13 records.

---

## 9. Existing Governance State (preserved, unchanged)

This decision changes none of the following. They are restated so this
record is self-contained:

```text
M13 (Filing Content Reading)     COMPLETE / PUBLISHED (commit 244ca5c; governance reconciliation f1c18c3) — unchanged
G8                               BLOCKED / CARRIED FORWARD — unchanged (Document 62 §4.2)
H-1                              CLOSED WITH GOVERNANCE FOLLOW-UP — unchanged (Document 62 §4.1)
Document 58 (Post-M12 Reconc.)   UNRATIFIED / HISTORICAL / CONSUMED / UNTRACKED — unchanged (Document 62 §3);
                                  not retroactively ratified by this decision
Document 59 (M13 API Contract)   CTO-RATIFIED / FROZEN — read, not modified
Document 60 (M13 Arch. Pack)     CTO-RATIFIED / FROZEN — read, not modified
Document 61 (M13 Gov. Reconc.)   INFORMATIONAL / VERSION-CONTROLLED / PUBLISHED — read, not modified
Document 62 (Post-M13 Reconc.)   CTO-RATIFIED (2026-08-30) — read, not modified; cited as the basis for this decision
Gate (JUDGE_SELF_CONSISTENCY_GATE_VERSION)   0 — unchanged
G7                               NO ARCHITECTURE CHANGE — unchanged
```

Neither H-1 nor G8 blocks, gates, or drives M14. Both remain standing debt
the CTO may separately choose to address; neither is reopened here.

---

## 10. Repository / Working-Tree State

Recorded by read-only `git` inspection this session. **No `git` mutation was
performed** — no `add` / stage, no `commit`, no `push`, no `amend`, no
`rebase`, no `merge`, no `reset`, no `stash`, no `clean`.

- **M13 publication state is synchronized:** `HEAD` = `origin/main` =
  `f1c18c37f0650b4f66f1ad4b8b6a6e0579f67e09`; ahead/behind `0 / 0`. The M13
  implementation commit `244ca5c` and the M13 governance commit `f1c18c3`
  are unchanged and were not inspected in a way that could alter them.
- **The working tree is NOT Git-clean.** It contains known, pre-existing,
  unrelated changes and artifacts that this document does **not** stage,
  modify, rename, delete, or clean:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx   (pre-existing, unrelated test-flake hardening)
  ?? docs/backend_engineering/58_Post_M12_Backend_AI_Roadmap_Reconciliation.md   (untracked governance proposal)
  ?? docs/backend_engineering/62_Post_M13_Backend_AI_Roadmap_Reconciliation.md   (untracked; commit is a separate CTO-authorized step — Doc 62 §16)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/          (untracked — M11 Phase H-1 evidence)
  ?? FROZEN
  ?? Semantic
  ?? _)
  ?? or
  ?? structured                                             (five untracked zero-byte editor/hook artifacts)
  ```

- **This document adds one further untracked file — itself**
  (`docs/backend_engineering/63_M14_Formal_Milestone_Selection_Record.md`).
  It is **untracked and not yet version-controlled.** Committing it is a
  separate, subsequently CTO-authorized step (the model Document 61's
  governance commit `f1c18c3` followed).
- Correct terminology for the state: **refs synchronized; working tree
  contains pre-existing unrelated artifacts plus this new untracked
  governance record.** The tree is **not** "clean".

---

## 11. Provenance and Constraints Honoured

- Created: 2026-08-30. Sole new file:
  `docs/backend_engineering/63_M14_Formal_Milestone_Selection_Record.md`.
  Document number 63 was verified free before creation (highest existing
  Backend & AI governance document was 62).
- Wording-aligned 2026-08-30 (same session) against a subsequent CTO
  re-issue of the formal M14 selection directive — **same decision, same
  date, same authority**. The alignment made explicit: the §4 progression
  rendering, the §5 `M14 direction` label and the "does not constitute …
  approval" line, the §6 "C-2 is not selected / not rejected" statement, and
  the §7 persistent-research-session exclusion. No change to the decision,
  its date, its authority, or any governance state. No new document was
  created for the re-issue; per the anti-duplication convention this
  existing record is the single formal M14 selection artifact.
- No source code, test, schema, index, migration, configuration, or
  infrastructure file was created or modified. No LangGraph topology,
  MongoDB collection/schema, or Redis state was touched. No dependency was
  introduced. No RAG or provider work was performed.
- **Documents 58, 59, 60, and 61 were read, not modified.** Document 62 was
  read, not modified. No frozen or historical governance record was
  rewritten; the decision is recorded in this new artifact instead.
- The M13 implementation commit `244ca5c` and the governance commit
  `f1c18c3` were not altered. Nothing was staged, committed, or pushed.
- No date, timestamp, decision number, or authorization wording was
  fabricated. The decision date (2026-08-30) and the authority (a separate
  CTO milestone-selection decision following the CTO ratification of
  Document 62) are recorded as given. No retroactive authorization is
  claimed. No prior governance decision is re-interpreted or duplicated —
  Document 62 is cited, not restated as a new interpretation.

---

**M14 IS FORMALLY SELECTED = C-1 FILING ANALYSIS. THIS IS A SEPARATE CTO
MILESTONE-SELECTION DECISION, DISTINCT FROM THE CTO RATIFICATION OF DOCUMENT
62. NO M14 CONTRACT PROPOSED OR RATIFIED. NO M14 ARCHITECTURE PROPOSED OR
RATIFIED. NO IMPLEMENTATION, COMMIT, OR PUSH AUTHORIZATION GRANTED. THE
CHUNK-VS-SECTION QUESTION REMAINS OPEN. C-2 STRUCTURED FILING EXTRACTION
REMAINS ONLY A POSSIBLE TECHNICAL SEQUENCING PREREQUISITE. FILING Q&A
REMAINS EXCLUDED FROM C-1 / M14. G8 REMAINS BLOCKED / CARRIED FORWARD. H-1
REMAINS CLOSED WITH GOVERNANCE FOLLOW-UP. DOCUMENT 58 REMAINS UNRATIFIED /
HISTORICAL / CONSUMED AND IS NOT RETROACTIVELY RATIFIED. M13 REMAINS
COMPLETE / PUBLISHED. DOCUMENTS 58–61 NOT MODIFIED. NO SOURCE, TEST, SCHEMA,
OR INFRASTRUCTURE FILE CREATED OR MODIFIED. NO STAGE. NO COMMIT. NO PUSH. NO
MERGE / REBASE / RESET / STASH / CLEAN. THE NEXT AUTHORIZED GOVERNANCE
ACTIVITY IS PREPARATION OF THE M14 CONTRACT PROPOSAL, SUBJECT TO THE NORMAL
GOVERNANCE PROCESS; SELECTION AUTHORIZES PROGRESSION TO THE
CONTRACT-GOVERNANCE STAGE ONLY, NOT IMPLEMENTATION.**
