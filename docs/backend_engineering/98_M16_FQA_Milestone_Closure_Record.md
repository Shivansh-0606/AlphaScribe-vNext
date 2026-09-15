# 98 — M16 / FQA Milestone Closure Record

**Status:** 🟢 **M16 / FQA v1 — CLOSED FROM THE IMPLEMENTATION AND
PUBLICATION PERSPECTIVE.** This document formally records that the
engineering delivery of **M16 = Filing Q&A (FQA v1)** is complete: the
ratified API contract ([Document 87 Revision 2](87_M16_Filing_QA_API_Contract_Proposal.md))
and ratified architecture ([Document 90](90_M16_Filing_QA_Architecture_Decision_Pack.md),
as amended for candidate selection by [Document 95](95_D90_Candidate_Selection_Architecture_Amendment_Decision.md) /
[Document 96](96_Document95_Candidate_Selection_Architecture_Amendment_Ratification_Record.md))
were implemented under the ratified implementation authorization
([Document 94 Revision 1](94_M16_Filing_QA_Implementation_Authorization_Decision.md),
ratified by [Document 97 Revision 1](97_Document94_Revision1_CTO_Ratification_Record.md)),
the implementation was committed as `9035e27`, and that commit is verified
published to `origin/main` with zero divergence.

**No prior persisted M16 closure document existed before this one.** Unlike
M14 and M15 — each of which had its implementation-review outcome and
milestone closure recorded in a numbered, committed governance document
(Documents 66/79 respectively) before the next milestone's roadmap
reconciliation began — M16's implementation-acceptance and
"publication-gate-closed" status were, until this document, asserted only
in-session, conversationally, across the implementation and commit-
authorization tasks that produced commit `9035e27`. This document is the
**first persisted record** of that closure; it does not claim a prior one
existed (§6).

**Type:** Governance / milestone-closure record (documentation only — no
source code, test, configuration, schema, migration, index, route,
LangGraph node/topology, MongoDB collection/schema, Redis usage, provider,
evaluation-infrastructure, or frontend file created or modified to produce
it; Documents 67–97 read, not modified; the repository's actual Git and
test state re-verified this session, not assumed. The only file this task
creates is this document.

**Date:** 2026-09-13.

**Precedent / lineage.** This record follows the same standalone
milestone-closure form [Document 79](79_M15_C4_Milestone_Closure_Record.md)
established for M15 — document metadata table, governance-ladder table,
Git-publication verification block, known-issues register, explicit
non-authorization statements — adapted for one M16-specific fact Document
79 did not need to state: that no interim implementation-review document
was persisted before this closure record. It does not re-decide, redesign,
reinterpret, or reopen any of Documents 83–97, and it authorizes nothing
downstream (§9, §10).

---

## 1. Document Identity

| Field | Value |
|---|---|
| Document number | 98 |
| Title | M16 / FQA Milestone Closure Record |
| Milestone | M16 = Filing Q&A (FQA v1) — single-turn, stateless with respect to durable conversational/research state, single-filing, `(ticker, doc_id)` identity (Documents 83/85; Document 84/86 §title) |
| Governance stage | Engineering-delivery + publication closure (this act) |
| Status | 🟢 CLOSED — implementation and publication perspective only (§9) |
| Files created by this task | this document only |
| Files modified by this task | none |

---

## 2. Purpose

M16 = Filing Q&A (FQA v1) has cleared scope pre-decision, milestone
selection, API contract ratification, architecture ratification, the
candidate-selection amendment, and implementation authorization (§4). Its
implementation was committed (`9035e27`) and that commit is verified
published to `origin/main` (§7). **No document has yet formally closed the
milestone.** This document performs exactly that closure act: it records,
from repository evidence gathered this session, that M16's implementation
and publication are complete, states plainly what is and is not evidenced
by a persisted document versus by conversation (§6), records the two known
outstanding issues without resolving them (§8), and draws the explicit
governance boundary around what this closure does **not** authorize (§9).
It does not reopen, redesign, or reinterpret Documents 83–97, and it makes
no decision about deployment or about what comes after M16 (§9, §10).

---

## 3. Milestone Scope — What M16/FQA v1 Delivered

Per the ratified contract ([Document 87 Revision 2](87_M16_Filing_QA_API_Contract_Proposal.md))
and ratified architecture ([Document 90](90_M16_Filing_QA_Architecture_Decision_Pack.md),
as amended by [Documents 95/96](95_D90_Candidate_Selection_Architecture_Amendment_Decision.md)),
implemented exactly within the [Document 94 Revision 1](94_M16_Filing_QA_Implementation_Authorization_Decision.md)
file boundary:

- one new pure module, `backend/agents/filing_qa.py` — deterministic
  candidate curation (the Document 95/96-ratified position formula for
  `N > K`, unchanged "select every chunk" for `N ≤ K`), at most one
  `chat_json` answer-generation call per job, and a deterministic
  citation-structure validator producing the closed two-value `state`
  (`answered` | `insufficient_evidence`) per Document 87 R2 §9;
- the four-route async job family under
  `/api/companies/{ticker}/filings/{doc_id}/qa` (create / status / stream /
  cancel), additive in `backend/server.py`, reusing `container.job_lifecycle`,
  `sse_response`, `require_admin`, `assert_public_url`, and
  `agents/retrieval.py` unmodified;
- the AH-2 process-local, TTL-bounded result buffer (`_FILING_QA_RESULTS`),
  a structural peer of M14/M15's own buffers — no Mongo or Redis
  final-result persistence, no sticky sessions, no cross-process `GET`;
- one additive `JobKind.FILING_QA`, one additive `filing_qa_runs_total`
  metrics counter, and additive `Settings` fields
  (`job_deadline_filing_qa_s`, `fqa_max_question_chars`,
  `fqa_max_answer_chars`, `fqa_max_sources`);
- the route-inventory contract guard moved `51 → 55`;
- 57 new hermetic tests (`test_filing_qa.py`, `test_filing_qa_endpoint.py`,
  `test_filing_qa_result_buffer.py`) and 9 new live-HTTP tests
  (`backend_test_iter8.py`).

Explicitly **not** delivered, per the same authorization's exclusions:
Durable Research Sessions, multi-turn conversation, cross-filing/corpus/
portfolio research, MongoDB or Redis final-result persistence, new
LangGraph architecture, or any frontend change.

---

## 4. Authorization Lineage

Every stage below was independently re-verified this session against each
document's own status banner (not assumed from filenames or from this
document's predecessor tasks' summaries):

```text
D83 (FQA Scope Pre-Decision)              → D85 (Ratification)     🟢 CTO-RATIFIED
D84 (M16 Milestone Selection)             → D86 (Ratification)     🟢 CTO-RATIFIED — M16 = Filing Q&A (FQA v1)
D87 Rev 2 (M16 API Contract)              → D88 → D89 → D92         🟢 RATIFIED
D90 (M16 Architecture Decision Pack)      → D91 → D93               🟢 RATIFIED
D95 (Candidate-Selection Amendment)       → D96 (Ratification)      🟢 RATIFIED — amends D90 §5 only
D94 Revision 1 (Implementation Auth.)     → D97 Revision 1 (Ratif.) 🟢 CTO-RATIFIED
       ↓
M16 implementation → commit 9035e27 → pushed to origin/main (§7)
       ↓
THIS DOCUMENT (98) — engineering-delivery + publication closure
```

No document in this chain is reopened, reinterpreted, or amended by this
closure record.

---

## 5. Implementation Verification

- **Implementation commit:** `9035e2714eb7a6323932c667b6a251981a73293b`
  (short `9035e27`), subject `feat(m16): implement filing qa v1`.
- **File boundary:** `git show --name-only --format= 9035e27` lists exactly
  ten files — `backend/agents/filing_qa.py`,
  `backend/app/settings.py`, `backend/domain/models.py`,
  `backend/infrastructure/observability/metrics.py`, `backend/server.py`,
  `backend/tests/backend_test_iter8.py`,
  `backend/tests/contract/test_route_inventory.py`,
  `backend/tests/unit/test_filing_qa.py`,
  `backend/tests/unit/test_filing_qa_endpoint.py`,
  `backend/tests/unit/test_filing_qa_result_buffer.py` — matching the
  Document 94 Revision 1 §5.1/§5.2 exhaustive authorized boundary exactly,
  with no file outside it and no file from §5.3's explicit exclusion list
  present. Re-confirmed this session via `git show --stat --oneline
  9035e27` against the record made at commit time — unchanged.
- **No unrelated work is present in the commit** — `web/features/workspace-home/ui/CompanySearch.test.tsx`
  and every governance document (Documents 67–97) remain outside it,
  confirmed by the same `git show --name-only` listing.

---

## 6. Review and Acceptance — Precisely What Is and Is Not Evidenced

**Evidenced by persisted, committed repository state:**

- the ratified governance chain in §4 (each document's own status banner,
  re-read this session);
- the implementation commit `9035e27` and its exact file boundary (§5);
- the commit's presence on `origin/main` with zero divergence (§7);
- the hermetic test result `788 passed, 1 failed`, reproduced this session
  by actually running `pytest backend/tests/unit backend/tests/contract -q`
  (§8) — not asserted from memory.

**Not evidenced by any persisted governance document — evidenced only by
conversation, across this session's prior tasks:**

- the claim that a "CTO implementation review" of the M16 code took place
  and passed;
- the claim that a "CTO post-push review" took place and passed.

Unlike M15, where [Document 79](79_M15_C4_Milestone_Closure_Record.md) §2
could cite an actual prior review outcome as part of its own governance
ladder, **no numbered document records an M16 implementation-review or
post-push-review verdict.** This closure record does not manufacture one.
It records only what the repository itself demonstrates: the code exists,
matches its authorization boundary, passes its authorized test floor
(modulo the one known, out-of-boundary failure in §8), and is published.
Whether a conversational review that is not persisted anywhere in
`docs/backend_engineering/` should be treated as satisfying the same
governance weight as Documents 66/76/78's persisted ratification records is
a standing-process question this document raises but does not resolve —
it is not this record's place to decide that retroactively.

---

## 7. Git Publication Verification

Re-verified this session, independent of any cached state:

```text
git rev-parse HEAD                              -> 9035e2714eb7a6323932c667b6a251981a73293b
git log -1 --oneline                            -> 9035e27 feat(m16): implement filing qa v1
git branch --show-current                       -> main
git remote -v                                   -> origin  https://github.com/Shivansh-0606/AlphaScribe-vNext.git
git fetch origin main                           -> (performed; updates only the local remote-tracking ref)
git rev-parse origin/main                       -> 9035e2714eb7a6323932c667b6a251981a73293b
git rev-list --left-right --count origin/main...HEAD -> 0   0
git reflog show refs/remotes/origin/main        -> top entry: 9035e27 refs/remotes/origin/main@{0}: update by push
```

| Field | Value |
|---|---|
| Commit SHA | `9035e2714eb7a6323932c667b6a251981a73293b` |
| Parent | `f8c06649e94f45c388bbecf3eeedb9e5340f2024` (M15 — "feat(m15): implement change brief") |
| Branch | `main` |
| `origin/main` | `9035e2714eb7a6323932c667b6a251981a73293b` |
| Synchronization | `0 ahead / 0 behind` — local `main` and `origin/main` are identical |
| Publication mode | A normal fast-forward push — the reflog's `update by push` entry, together with `.git/FETCH_HEAD` recording the same SHA for `branch 'main' of` the `origin` URL, is the remote's own evidence that this commit was received as an ordinary push, not force-pushed or otherwise rewritten |
| Boundary verification | §5 — exactly the ten authorized M16 files, nothing else |

**Provenance note.** The commit-authorization task that produced `9035e27`
in this session explicitly did not execute `git push` — push was
unauthorized at that point. The reflog nonetheless shows the push occurred
before this session's next turn began. This record states that fact plainly
rather than asserting who performed it: the evidence establishes *that* the
commit is published and unaltered, not *by what action* the push itself was
run.

---

## 8. Known Issues

Recorded as of this session, neither fixed nor reinterpreted:

### 8.1 Test failure

```text
788 passed, 1 failed
```

```text
backend/tests/unit/test_settings.py::test_job_deadline_dict_matches_07_5_4
```

**Classification:** Known D94 boundary gap. Outside the authorized M16
implementation boundary. Not fixed as part of M16. `test_settings.py` is
not named in Document 94 Revision 1 §5 or §8's exhaustive authorized-file
lists, and §8 states no existing test file beyond
`test_route_inventory.py` is authorized to be modified. The failure is the
mechanical, unavoidable consequence of the separately-authorized
`job_deadline_s` dictionary addition (§5.2) not being reflected in this
one pre-existing test's exact-equality assertion. Resolving it requires a
separate, explicit authorization to touch `test_settings.py` — not granted
by this closure record.

### 8.2 Zero-byte working-tree artifacts

Current count: **18** untracked, zero-byte, fragment-named files
(`1\``, `K,`, `K\``, `NOT`, `POST`, `Path`, `Sep`, `backend/2`,
`backend/None`, `backend/set[tuple[str`, `backend/whole-filing`, `both`,
`cancel`, `current_period_end\``, `empty)`, `expect`, `never`, `{p}`).

- **Unresolved** — present at the time of this closure record.
- **Outside M16 closure scope** — not created by, not part of, and not a
  gating condition of M16's implementation or publication.
- **No cleanup performed** — none renamed, deleted, modified, or staged by
  this or any prior M16-related task.
- **Root cause not investigated here** — it remains a separate engineering-
  hygiene matter for a future, dedicated investigation.

---

## 9. Governance Boundaries

- **M16 publication gate: CLOSED.** The implementation is committed,
  file-boundary-verified, and published to `origin/main` with zero
  divergence (§5, §7).
- **Deployment authorization: NOT GRANTED.** Publication to `origin/main`
  is not deployment. No environment has been targeted, no release process
  invoked, no deployment gate opened by this document or by anything it
  records.
- **M17 / next milestone: NOT SELECTED.** This document closes M16 only. It
  does not perform, and does not authorize, a Post-M16 Backend & AI Roadmap
  Reconciliation, a milestone-selection act, or any statement about what
  comes next.
- **Future roadmap decisions remain separate, subsequent, explicit CTO
  governance acts** — as they have been at every prior milestone boundary
  in this chain (Documents 67→68, 81→84).
- This document does not reopen, redesign, reinterpret, or amend Documents
  83 through 97.

---

## 10. Closure Decision

**M16 / Filing Q&A (FQA v1) is formally CLOSED from an implementation and
publication perspective**, on the evidence in §5–§7: the ratified contract
and architecture (as amended) were implemented within the ratified
Document 94 Revision 1 boundary, committed as `9035e27` with no unrelated
work included, and that commit is verified published to `origin/main` with
zero divergence. Two known issues (§8) remain open and unresolved, neither
blocking this closure nor authorized to be fixed by it. This closure grants
no deployment authorization and selects no next milestone (§9); both remain
distinct, future, explicit CTO governance acts.

**🟢 M16 / FQA v1 — CLOSED (implementation + publication). Deployment: NOT
AUTHORIZED. Next milestone: NOT SELECTED.**
