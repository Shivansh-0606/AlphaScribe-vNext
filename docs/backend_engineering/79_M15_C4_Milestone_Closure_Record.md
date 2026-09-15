# 79 — M15 / C-4 Milestone Closure Record

**Status:** 🟢 **M15 / C-4 — CLOSED FROM THE ENGINEERING-DELIVERY
PERSPECTIVE.** This document formally records that the engineering delivery
of **M15 = C-4 — "What Changed Since Last Review"** is complete: the
ratified API contract ([Document 70 R4](70_M15_What_Changed_API_Contract_Proposal.md))
and ratified architecture ([Document 73 R1](73_M15_Architecture_Decision_Pack.md))
were implemented under the ratified implementation authorization
([Document 75](75_M15_Implementation_Authorization_Decision.md) /
[Document 76](76_Document75_CTO_Implementation_Authorization_Ratification_Record.md),
as amended for §14 by [Document 77](77_D75_Section14_Testing_Floor_Clarification_and_Amendment_Decision.md) /
[Document 78](78_Document77_CTO_D75_Section14_Amendment_Ratification_Record.md)),
the implementation commit passed a CTO post-commit technical review, was
push-authorized, was pushed to `origin/main`, and passed a CTO post-push
review.

**Type:** Governance / milestone-closure record (documentation only — no
source code, test, configuration, schema, migration, index, route,
LangGraph node/topology, MongoDB collection/schema, Redis usage, provider,
evaluation-infrastructure, or frontend file created or modified to produce
it; Documents 67–78 read, not modified. The only file this task creates is
this document.

**Date:** 2026-09-08.

**Precedent / lineage.** This record follows the standalone
decision-record / status-record form the M15 chain already uses for a
governance act recorded as its own artifact without editing any prior
document — [Document 72](72_Document70_R4_CTO_Ratification_Record.md)
(contract ratification), [Document 74](74_Document73_R1_CTO_Architecture_Ratification_Record.md)
(architecture ratification), [Document 76](76_Document75_CTO_Implementation_Authorization_Ratification_Record.md)
(implementation-authorization ratification), and
[Document 78](78_Document77_CTO_D75_Section14_Amendment_Ratification_Record.md)
(§14 amendment ratification). It is one step further down the ladder: a
**delivery-closure** record. It does not re-decide, redesign, reinterpret,
or reopen any of Documents 67–78, and it authorizes nothing downstream
(§6, §7).

---

## 1. Document Metadata

| Field | Value |
|---|---|
| Document number | 79 |
| Title | M15 / C-4 Milestone Closure Record |
| Milestone | M15 = C-4 — "What Changed Since Last Review" (Document 68 §4; Document 69 §2; Document 72 §5; Document 74 §6; Document 75 §1; Document 76 §1) |
| Governance stage | Engineering-delivery closure (this act) |
| Predecessor gates | Implementation → CTO post-commit review PASS → push authorization → push to `origin/main` → CTO post-push review PASS |
| Approved implementation commit | `f8c06649e94f45c388bbecf3eeedb9e5340f2024` (short `f8c0664`) — verified this session (§4) |
| Parent commit | `be4949b5b33ea73cfedf81c03bebbdaa953772b8` (M14 — "feat(m14): implement filing analysis") |
| Successor gate (NOT created here) | None authorized by this record. Deployment, release, and M16 selection each remain separate, later, distinct CTO acts (§6, §7). |
| Files created by this task | this document only |
| Files modified by this task | none |

---

## 2. Status / Authority

🟢 **M15 / C-4 — ENGINEERING DELIVERY COMPLETE AND CLOSED.**

**Governance ladder — every prior stage ratified; this record closes the
delivery stage only:**

| # | Stage | Status |
|---|---|---|
| 1 | Milestone selection | 🟢 CTO-RATIFIED (Document 68, via Document 69) — **M15 = C-4** |
| 2 | API contract ratification | 🟢 CTO-RATIFIED (Document 70 R4, via Document 72) |
| 3 | Architecture ratification | 🟢 CTO-RATIFIED (Document 73 R1, via Document 74) |
| 4 | Implementation authorization | 🟢 CTO-RATIFIED (Document 75, via Document 76) |
| 4a | D75 §14 testing-floor amendment | 🟢 CTO-RATIFIED (Document 77, via Document 78) |
| 5 | Implementation + CTO post-commit review | 🟢 COMPLETE — commit `f8c0664`, review **PASS** |
| 6 | Push authorization + push + CTO post-push review | 🟢 COMPLETE — pushed to `origin/main`, review **PASS** |
| 7 | **Engineering-delivery closure** | 🟢 **THIS DOCUMENT (79)** |
| — | Deployment / release / production rollout | NOT PERFORMED — separate, later, distinct CTO acts; not authorized here (§6) |
| — | M16 selection | NOT PERFORMED — not authorized here (§6) |

This document performs exactly one act: **recording the closure of M15 /
C-4 engineering delivery.** It does not perform, and does not imply, any
downstream stage.

---

## 3. Governance Chain / Provenance (recorded accurately, not re-decided)

| Artifact / event | Role | State |
|---|---|---|
| **Document 68** — M15 Formal Milestone Selection Record | Milestone selection | 🟢 CTO-RATIFIED via Document 69 — **M15 = C-4** |
| **Document 69** — Document 68 CTO Ratification Record | Milestone-selection ratification | 🟢 CTO-RATIFIED |
| **Document 70, Revision R4** — M15 / C-4 API Contract | API contract | 🟢 CTO-RATIFIED via Document 72 |
| **Document 72** — Document 70 R4 CTO Ratification Record | API-contract ratification | 🟢 CTO-RATIFIED |
| **Document 73, Revision R1** — M15 / C-4 Architecture Decision Pack | Architecture decision (AH-1, AH-2 resolved) | 🟢 CTO-RATIFIED via Document 74 |
| **Document 74** — Document 73 R1 CTO Architecture Ratification Record | Architecture ratification | 🟢 CTO-RATIFIED |
| **Document 75** — M15 Implementation Authorization Decision | Implementation authorization | 🟢 CTO-RATIFIED via Document 76 |
| **Document 76** — Document 75 CTO Implementation Authorization Ratification Record | Implementation-authorization ratification | 🟢 CTO-RATIFIED |
| **Document 77** — D75 §14 Testing-Floor Clarification and Amendment Decision | Bounded amendment of D75 §14's eighth (golden-dataset) bullet | 🟢 CTO-RATIFIED via Document 78 |
| **Document 78** — Document 77 CTO D75 §14 Amendment Ratification Record | §14 amendment ratification (amendment now in effect) | 🟢 CTO-RATIFIED |
| **M15 / C-4 implementation** | Source, tests, one additive `JobKind.CHANGE_BRIEF`, one additive `job_deadline_change_brief_s`, four additive routes under `/api/companies/{ticker}/changes`, AH-2 process-local result buffer, `change_brief_runs_total{outcome, comparison_type}` counter | 🟢 COMPLETE — strictly within Document 75 §15's authorized scope |
| **Commit `f8c06649e94f45c388bbecf3eeedb9e5340f2024`** (short `f8c0664`) — "feat(m15): implement change brief" | The approved implementation commit; single parent `be4949b` (M14) | 🟢 CREATED |
| **CTO post-commit review** | Technical review of the committed implementation against Documents 70 R4 / 72 / 73 R1 / 74 / 75 / 76 / 77 / 78 | 🟢 **PASS** |
| **Push authorization** | The distinct CTO act permitting the approved commit to reach `origin/main` (governance-ladder stage 6; Document 75 §2 / §16 / §18) | 🟢 GRANTED (recorded by the CTO in the closure authorization) |
| **Push to `origin/main`** | Publication of `f8c0664` to the shared remote | 🟢 COMPLETE — verified this session (§4): `origin/main` reflog `update by push`, 2026-09-08 14:18:40 +0530, linear fast-forward `be4949b → f8c0664` |
| **CTO post-push review** | Review confirming the published remote state matches the approved commit and no divergence, force, or extra commit occurred | 🟢 **PASS** (recorded by the CTO in the closure authorization; the git-verifiable facts underpinning it are independently confirmed in §4) |

No governance state above is changed by this document. Each is cited, not
re-decided.

---

## 4. Verified Git Facts (read-only inspection, this session, 2026-09-08)

**No `git` mutation was performed to produce this record** — no
`add` / stage, no `commit`, no `push`, no `amend`, no `rebase`, no
`merge`, no `reset`, no `restore`, no `stash`, no `clean`.

| Check | Command | Result |
|---|---|---|
| Local HEAD | `git rev-parse HEAD` | `f8c06649e94f45c388bbecf3eeedb9e5340f2024` |
| Remote head | `git rev-parse origin/main` | `f8c06649e94f45c388bbecf3eeedb9e5340f2024` |
| HEAD == origin/main | comparison | **equal** |
| Ahead / behind | `git rev-list --left-right --count origin/main...HEAD` | `0	0` |
| Upstream tracking | `git branch -vv` | `* main f8c0664 [origin/main] feat(m15): implement change brief` — no `[ahead]` / `[behind]` marker |
| Commits ahead of remote | `git log --oneline origin/main..HEAD` | *(empty)* |
| Parent of HEAD | `git rev-parse HEAD^` | `be4949b5b33ea73cfedf81c03bebbdaa953772b8` (single parent) |
| Parent count | `git cat-file -p HEAD \| grep -c '^parent'` | `1` (single-parent; not a merge) |
| Fast-forward lineage | `git merge-base --is-ancestor be4949b… HEAD` | **true** — `be4949b` is an ancestor of `f8c0664`; the remote advanced `be4949b → f8c0664` linearly |
| Push event | `git reflog show origin/main --date=iso` | `f8c0664 refs/remotes/origin/main@{2026-09-08 14:18:40 +0530}: update by push` (prior: `be4949b @{2026-09-03 …}: update by push`) — a normal push entry, **not** `forced-update` |
| Additional commits | `git reflog -n 5` (HEAD) | top entry `f8c0664 HEAD@{0}: commit: feat(m15): implement change brief` — no later `rebase` / `amend` / `reset` / `commit` entry |
| Commit message | `git log -1 --format='%s%n%b'` | `feat(m15): implement change brief` + `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>` |

### 4.1 Commit-hash provenance note (transcription correction)

The closure-authorization request quoted the full 40-character commit hash
as `f8c06649e94f45c388edf81c03bebbdaa953772b8`. **That string does not
resolve to any object in this repository** — `git rev-parse --verify
f8c06649e94f45c388edf81c03bebbdaa953772b8` fails with *"Needed a single
revision."* It matches the real hash only for the first 18 hex digits
(`f8c06649e94f45c388…`) and then diverges, its tail
(`…edf81c03bebbdaa953772b8`) coinciding with the tail of the **parent**
(M14) hash `be4949b5b33ea73cf` `edf81c03bebbdaa953772b8` — i.e. an apparent
splice of the two hashes.

**The canonical value recorded throughout this document —
`f8c06649e94f45c388bbecf3eeedb9e5340f2024` — is taken directly from
`git rev-parse HEAD`, which equals `git rev-parse origin/main`.** The
abbreviated form `f8c0664` and the parent hash
`be4949b5b33ea73cfedf81c03bebbdaa953772b8` given in the request are both
correct and are unchanged here. This note exists so the discrepancy is
resolved by an auditable correction rather than by silently propagating a
non-resolving hash into the governance record.

---

## 5. Closure Facts (stated explicitly)

1. **M15 / C-4 implementation is complete** — the ratified Document 70 R4
   contract and Document 73 R1 architecture are realized in the approved
   commit, strictly within Document 75 §15's authorized scope; the
   Document 75 §14 testing floor (as amended by Documents 77 / 78) is
   satisfied and its hermetic suite is green.
2. **The approved implementation commit is
   `f8c06649e94f45c388bbecf3eeedb9e5340f2024`** (short `f8c0664`), single
   parent `be4949b5b33ea73cfedf81c03bebbdaa953772b8` (M14). See §4.1 for
   the correction of the hash as quoted in the closure-authorization
   request.
3. **The commit was successfully pushed to `origin/main`** — confirmed by
   the `origin/main` reflog entry `update by push` dated
   2026-09-08 14:18:40 +0530.
4. **Local `HEAD` and `origin/main` were verified equal** — both resolve
   to `f8c06649e94f45c388bbecf3eeedb9e5340f2024`.
5. **Ahead / behind divergence was `0 / 0`** —
   `git rev-list --left-right --count origin/main...HEAD` returned `0 0`;
   `git branch -vv` shows no `[ahead]` / `[behind]` marker.
6. **The push was a normal fast-forward** — `be4949b` is an ancestor of
   `f8c0664`; the remote advanced `be4949b → f8c0664` on a linear history
   with no merge commit.
7. **No force push occurred** — the `origin/main` reflog records a plain
   `update by push`, not a `forced-update`; the fast-forward lineage in
   fact 6 is consistent with this.
8. **No additional commit was created** — the HEAD reflog's top entry is
   still the single `commit: feat(m15): implement change brief` for
   `f8c0664`, with no subsequent `commit` / `amend` / `rebase` / `reset`
   entry; `git log origin/main..HEAD` is empty.
9. **No deployment or release occurred** — publication to `origin/main` is
   source-control publication only; no build, tag, environment promotion,
   or release artifact was produced, and none is authorized by this record
   (§6).
10. **No implementation remediation is required** — the CTO post-commit
    technical review returned **PASS** with no blocker and no required
    revision, and the CTO post-push review returned **PASS**.
11. **The unrelated working-tree items were intentionally left untouched**
    — the pre-existing, unrelated modified and untracked items enumerated
    in §8 were not staged, modified, renamed, deleted, or cleaned;
    authoring this document touched only the file
    `docs/backend_engineering/79_M15_C4_Milestone_Closure_Record.md`.
12. **M15 / C-4 is CLOSED from the engineering-delivery perspective** —
    contract, architecture, implementation authorization, implementation,
    post-commit review, push authorization, push, and post-push review are
    all complete and PASS; this record formalizes that closure.

---

## 6. What This Record Does NOT Do (governance boundaries)

This closure record **does not**, and must not be read to:

- modify, amend, reinterpret, or reopen **Documents 67–78**, or any
  earlier governance document;
- modify any **source code**, **test**, or **configuration** file;
- modify **MongoDB architecture** (no collection, schema, index, or
  migration is introduced, altered, or authorized);
- modify **Redis architecture** (no key pattern, cache, or persistence
  usage is introduced, altered, or authorized);
- modify **LangGraph architecture** (`agents/graph.py` and
  `07_LangGraph_Architecture.md` remain untouched; C-4 stays out-of-graph
  exactly as ratified);
- **reopen M14** (the parent commit `be4949b` and the M14 contract remain
  frozen and unaffected);
- **reopen M15 implementation** (the delivery is closed, not resumed);
- **authorize deployment**, **authorize release**, or authorize any
  production rollout — each remains a separate, later, distinct CTO act;
- **select M16** or otherwise begin the next milestone;
- **authorize any future implementation** of any kind;
- **reinterpret the Document 70 R4 contract** — its request/response
  shapes, the two mutually-exclusive `period` / `report` modes, the
  distinct financial (`{index, statement_type, period_end, metric}`) and
  narrative (`{index, report_id, field}`) citation shapes, the mandatory
  both-sides narrative grounding, the `complete` / `partial` /
  `insufficient_evidence` state vocabulary, the zero-new-error-class
  taxonomy, and the job / SSE / BYOK / SSRF boundaries all stand exactly
  as ratified;
- **alter AH-1** (the `report`-mode `items[]` structured-schema-extension
  resolution) or **AH-2** (the process-local, TTL-bounded, in-process
  job-result buffer; restart loss accepted; cross-process `GET`
  unsupported; no sticky sessions; no Redis or MongoDB final-result
  persistence; no cross-process reconstruction; SSE does not bypass the
  invariant) — both remain exactly as ratified by Documents 73 R1 / 74;
- **turn future golden-dataset `report`-mode evaluation into a current
  implementation requirement** — per Documents 77 / 78 it is
  evaluation / validation evidence and tracked follow-up work, **not** a
  prerequisite for M15 / C-4 delivery being complete and **not** a bar to
  this closure; this record neither reclassifies it further nor schedules
  it (§7).

---

## 7. Downstream / Still-Open (preserved exactly — not resolved or scheduled here)

- **Golden-dataset `report`-mode evaluation evidence** — remains
  legitimate, desirable, tracked follow-up work under Documents 77 §6–§7
  and 78, to be undertaken only if and when separately authorized. Any
  engineering it needs (extending the `Surface` model, adding an adapter,
  wiring surface dispatch, updating loader exact-set tests, authoring the
  case corpus) requires its **own** separate authorization and is neither
  performed nor pre-authorized by this record.
- **Deployment / release / production rollout** — not performed, not
  authorized; separate, later, distinct CTO acts (Document 74 §18;
  Document 75 §16; Document 76 §16 / §17).
- **M16 selection** — not performed, not authorized here.
- **Open Contract Decisions OCD-1 … OCD-6** (Document 70 §22) and **Open
  Architectural Questions AAQ-1 … AAQ-4** (Document 73 §24) — remain
  exactly as open as Documents 75 §11 and 76 leave them. This record
  resolves none of them and reads none of them as resolved.
- **Multi-instance / cross-process job-result retention (AAQ-3)** — remains
  explicitly out of M15's supported execution model; the single-backend-
  process invariant for the `POST → completion → GET` lifecycle stands as
  ratified.

---

## 8. Repository / Working-Tree State and Provenance

Recorded by read-only inspection this session. **This is a point-in-time
snapshot observed during the creation of this record on 2026-09-08**, not
a claim about repository state at any later reading time. **No `git`
mutation was performed** — no `add` / stage, no `commit`, no `push`, no
`amend`, no `rebase`, no `merge`, no `reset`, no `restore`, no `stash`, no
`clean`.

- `HEAD = origin/main = f8c06649e94f45c388bbecf3eeedb9e5340f2024`
  (`f8c0664`, "feat(m15): implement change brief") — the M15 / C-4
  implementation commit, now published.
- Document number 79 was verified free before creation (highest existing
  Backend & AI governance document was 78; no Document 79 existed prior to
  this task).
- Documents 67–78 were read, not modified. Their ratified content is
  cited, not amended, above.
- No source code, test, schema, index, migration, route, handler,
  LangGraph node, prompt, retrieval / RAG code, MongoDB collection, Redis
  component, provider, configuration, evaluation-infrastructure, or
  frontend file was created or modified. `.gitignore` was not modified.
- The working tree is **not** Git-clean. It contains known, pre-existing,
  unrelated items this document does **not** stage, modify, rename,
  delete, or clean:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated — not touched)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/  (untracked, M11 evidence — not touched)
  ?? both                                                          (untracked, unexplained pre-existing artifact — not touched)
  ?? current_period_end`                                          (untracked, unexplained pre-existing artifact — not touched)
  ?? NOT                                                           (untracked, 0-byte stray shell-tooling artifact — see note below — not touched)
  ?? expect                                                        (untracked, 0-byte stray shell-tooling artifact — see note below — not touched)
  ?? docs/backend_engineering/67_...md through 78_...md            (pre-existing untracked governance documents — not modified)
  ```

  **Stray 0-byte shell-tooling artifacts.** The untracked entries `both`,
  `current_period_end\``, `NOT`, and `expect` are 0-byte files that
  appear to be produced by this environment's shell tooling from tokens in
  command / output text (the same phenomenon Document 77 §18 records for a
  file named `404)` that a prior session's tooling created). They are
  **not** application, test, configuration, or governance content, were
  **not** created or touched by the authoring of this document, and are
  left in place because this documentation-only task is instructed not to
  clean, reset, restore, stash, or stage unrelated working-tree items.
  They are flagged here for CTO disposition.

- This document adds one further untracked file — itself
  (`docs/backend_engineering/79_M15_C4_Milestone_Closure_Record.md`). It
  is **untracked and not yet version-controlled.** Staging or committing
  it is a separate, subsequently CTO-authorized step, not performed here.

---

**🟢 M15 / C-4 — ENGINEERING DELIVERY COMPLETE AND CLOSED. THE RATIFIED
DOCUMENT 70 R4 API CONTRACT AND DOCUMENT 73 R1 ARCHITECTURE WERE
IMPLEMENTED UNDER THE RATIFIED DOCUMENT 75 / 76 IMPLEMENTATION
AUTHORIZATION (D75 §14 AS AMENDED BY DOCUMENTS 77 / 78), STRICTLY WITHIN
D75 §15'S SCOPE — ONE ADDITIVE `JobKind.CHANGE_BRIEF`, ONE ADDITIVE
`job_deadline_change_brief_s`, FOUR ADDITIVE ROUTES UNDER
`/api/companies/{ticker}/changes`, THE AH-2 PROCESS-LOCAL RESULT BUFFER,
AND THE `change_brief_runs_total{outcome, comparison_type}` COUNTER. THE
APPROVED IMPLEMENTATION COMMIT IS
`f8c06649e94f45c388bbecf3eeedb9e5340f2024` (SHORT `f8c0664`), SINGLE
PARENT `be4949b5b33ea73cfedf81c03bebbdaa953772b8` (M14) — VERIFIED VIA
`git rev-parse`; THE 40-CHARACTER HASH QUOTED IN THE CLOSURE-AUTHORIZATION
REQUEST DID NOT RESOLVE AND HAS BEEN CORRECTED HERE (§4.1). THE COMMIT
PASSED A CTO POST-COMMIT TECHNICAL REVIEW (PASS), WAS PUSH-AUTHORIZED, AND
WAS PUSHED TO `origin/main` AS A NORMAL FAST-FORWARD (`be4949b → f8c0664`,
`origin/main` REFLOG `update by push`, 2026-09-08 14:18:40 +0530) WITH NO
FORCE PUSH AND NO ADDITIONAL COMMIT; LOCAL `HEAD` AND `origin/main` ARE
EQUAL WITH `0 / 0` AHEAD-BEHIND DIVERGENCE; THE CTO POST-PUSH REVIEW
RETURNED PASS. NO IMPLEMENTATION REMEDIATION IS REQUIRED. NO DEPLOYMENT OR
RELEASE OCCURRED. THIS RECORD MODIFIES NO SOURCE, TEST, CONFIGURATION,
MONGODB, REDIS, OR LANGGRAPH ARTIFACT; MODIFIES NO DOCUMENT 67–78;
REOPENS NEITHER M14 NOR M15 IMPLEMENTATION; REINTERPRETS NEITHER THE
DOCUMENT 70 CONTRACT NOR AH-1 / AH-2; DOES NOT TURN FUTURE GOLDEN-DATASET
`report`-MODE EVALUATION INTO A CURRENT IMPLEMENTATION REQUIREMENT (IT
REMAINS TRACKED FOLLOW-UP PER DOCUMENTS 77 / 78); AND AUTHORIZES NO
DEPLOYMENT, NO RELEASE, NO M16 SELECTION, AND NO FUTURE IMPLEMENTATION.
ALL SIX OPEN CONTRACT DECISIONS (OCD-1 … OCD-6) AND ALL FOUR OPEN
ARCHITECTURAL QUESTIONS (AAQ-1 … AAQ-4) REMAIN EXACTLY AS OPEN AS
DOCUMENTS 75 / 76 LEAVE THEM. THE UNRELATED WORKING-TREE ITEMS WERE
INTENTIONALLY LEFT UNTOUCHED. NO STAGE. NO COMMIT. NO PUSH. NO MERGE /
REBASE / RESET / AMEND. M15 / C-4 IS CLOSED FROM THE ENGINEERING-DELIVERY
PERSPECTIVE.**
