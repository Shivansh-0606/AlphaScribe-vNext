# Backend Engineering Milestone 2 — Implementation Charter

**Status:** 🟢 **ACTIVE** — opened 2026-08-03
**Milestone:** Backend Engineering M2 (implementation)
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main` · commit `7404b67`
**Governed by:** Backend Architecture `v1.0` (Documents
[`06`](06_Clean_Architecture_Migration_Plan.md)–[`11`](11_ADR_Index.md), 🔒 frozen 2026-08-03)

---

## 0. What this document is

A **work order**, not another architecture document. The sequencing, exit
criteria, and rationale are already frozen in
[`06 §7`](06_Clean_Architecture_Migration_Plan.md); this adds only what a
coding session needs that the architecture set does not contain: entry
conditions, working conventions, the handoff packet, and how to raise a
conflict against a frozen decision.

**Nothing here may restate or reinterpret a frozen decision.** Where this
document and Documents 06–11 disagree, 06–11 win and this document is wrong.

---

## 1. Entry conditions

| # | Condition | State |
|---|---|---|
| E-1 | Architecture set frozen at v1.0 | ✅ 2026-08-03 |
| E-2 | All ratification items decided | ✅ recorded in [`00_README`](00_README.md) register |
| E-3 | ADR index published | ✅ [`11`](11_ADR_Index.md), ADR-001…028 |
| E-4 | **Architecture package committed to git** | ❌ **BLOCKING — see §2** |
| E-5 | Working tree clean enough to branch from | ⚠️ 45 uncommitted paths predate this milestone |

## 2. ⚠️ E-4 — the freeze is not yet durable

`docs/backend_engineering/` is **untracked**: 0 of 12 files are in git. A frozen
document set that exists only in a working tree has no freeze — there is no
immutable record of what was ratified, no way to diff a future amendment against
it, and `git clean` would delete it.

**Required first action, before any implementation commit:**

```bash
git add docs/backend_engineering/ && git commit -m "docs(backend): freeze Backend Architecture v1.0 (M1)"
```

Tagging it makes later amendments diffable against the ratified state:

```bash
git tag -a backend-arch-v1.0 -m "Backend Architecture v1.0 — ratified 2026-08-03"
```

Until E-4 is met, treat Milestone 2 as **not started**. The 45 other
uncommitted paths (E-5) predate this milestone and are a separate cleanup
decision — they are not this charter's scope, but a phase branch taken from a
dirty tree will carry them into its diff.

---

## 3. Scope and sequence

Authoritative order: [`06 §7`](06_Clean_Architecture_Migration_Plan.md).
Reproduced here as a checklist only — **do not** treat this table as the source.

| Phase | Deliverable | Exit criteria | Status |
|---|---|---|---|
| **0** | Safety net — contract tests, unit tests for the 14 untested pure functions, security regression tests, hermetic CI | [`06 §7.1`](06_Clean_Architecture_Migration_Plan.md) | ⬜ next |
| 1 | App factory, `Settings`, container skeleton; `10` SD-3/SD-4/SD-15 | " | ⬜ |
| 2 | Domain extraction | " | ⬜ |
| 3 | Ports + Mongo adapters; `08 m0001` (25 indexes); `maxTimeMS` | " | ⬜ |
| 4 | Job lifecycle + EventBus (`01 D-1` fix); job deadlines (ADR-011) | " | ⬜ |
| L | Learning feature — **must follow Phase 4** | " | ⬜ |
| 5 | LLM adapter, single provider dispatch | " | ⬜ |
| 6 | Router split; authorization model; `server.py` **deleted** | " | ⬜ |
| 7 | Redis, OTel + Prometheus, Docker, CI gates | " | ⬜ |

**Phase 0 is the whole of the first work order.** It is the only phase that
changes no production code, and it is what makes every later phase verifiable.

---

## 4. Working conventions

| # | Rule | Source |
|---|---|---|
| W-1 | **One phase per PR.** No phase depends on a later phase's code. | `06 §5.3` |
| W-2 | **Moves are moves.** A relocation PR does not also change logic. Behavior changes are isolated to Phases 4 and 6, each with its test written first. | `06 §5.3` |
| W-3 | **Cite the stable ID**, not the reasoning, in commits, PRs, and code comments — e.g. `fixes 01 D-1`, `per ADR-018`. | `00_README` conventions |
| W-4 | The **Phase-0 OpenAPI snapshot is the contract oracle.** A phase that changes it fails CI; only Phase L may regenerate it (4 additive routes). | `06 §5.3` |
| W-5 | **`ponytail:` markers are preserved**, not opportunistically resolved. | `06` C-5 |
| W-6 | **`pytest.ini` `addopts` is not modified.** Test markers go on tests. | `06` C-4 |
| W-7 | Do not delete `backend/tests/backend_test_iter*.py`. | `06` C-6 |
| W-8 | `git mv` where possible, so review sees a rename rather than a rewrite. | `06 §5.3` |

---

## 5. Handoff packet for a coding session

A coding conversation starting Phase 0 needs exactly this context. Nothing more
should be pasted in — the documents are in the repo.

```
Repo    : Shivansh-0606/AlphaScribe-vNext   branch main @ 7404b67
Governs : docs/backend_engineering/06–11 (Backend Architecture v1.0, FROZEN)
Task    : Migration Phase 0 — safety net. Scope + exit criteria: 06 §5.1, §7.1.
Build   : - tests/contract/  OpenAPI snapshot + response-key assertions, all 31 routes  (02 F-6)
          - tests/unit/      the 14 untested pure functions                             (05 §3.2)
          - tests/unit/      security regression tests for existing controls            (10 SR-11)
          - tests/unit/test_architecture.py  dependency-rule AST walk                   (06 AD-5)
          - @pytest.mark.live markers on network-dependent tests                        (05 T-1)
          - pytest-cov baseline + hermetic CI job                                       (10 §11)
Rules   : W-1…W-8 in 12_M2_Implementation_Charter.md §4.
          Changes NO production code. Contracts unchanged (06 C-1, C-2).
```

**Why Phase 0 first, in one line:** the controls it pins — contract shapes,
security invariants, streaming behavior — are currently protected by four unit
tests and a lot of careful comments; moving that code without pinning it first
is the most likely way the system loses a property silently
([`10`](10_Backend_Security_Architecture.md) SR-11).

---

## 6. Raising a conflict against a frozen decision

Implementation will find things the architecture did not anticipate. The
procedure is **not** to quietly deviate:

1. **Stop at the conflict.** Do not implement a workaround that contradicts a
   frozen decision.
2. **Name the decision** — the ADR and the source document ID.
3. **State what implementation revealed** that the decision did not account for.
4. Raise it as an **Engineering Question** in the CTO Office, as `EQ-4` onward
   (the series is owned by [`01 §7`](01_Backend_Architecture_Review.md)).
5. On resolution: append a numbered amendment to the frozen document, update the
   ADR's status to `Superseded by ADR-0NN`, add the new ADR, and only then
   implement.

A frozen document that gets silently worked around is worse than no document.

---

## 7. Definition of done — Milestone 2

| # | Criterion |
|---|---|
| M2-1 | Phases 0–7 and L complete, each meeting its `06 §7.1` exit criteria |
| M2-2 | `backend/server.py` deleted |
| M2-3 | All 31 approved routes + 4 Learning routes served, OpenAPI snapshot matching except the 4 additive Learning entries |
| M2-4 | Hermetic CI green: contract, unit, architecture, security, Redis conformance |
| M2-5 | Coverage baseline published and improved on |
| M2-6 | `docker compose up` runs backend + Mongo (RS) + Redis + Prometheus |
| M2-7 | Degradation drills passed: Redis-down ([`09 §8`](09_Redis_Architecture.md)), Mongo restore ([`08 §12.2`](08_MongoDB_Data_Architecture.md)) |
| M2-8 | Every ADR marked `Accepted` is either implemented or has a tracked deviation |

---

## 8. Out of scope for Milestone 2

| Item | Where it belongs |
|---|---|
| Deleting `frontend/` (legacy CRA) | Gated on `Feature_Parity_Tracker.md` + a CTO-approved Legacy Frontend Removal Plan |
| Frontend changes of any kind | `06` C-2 — frozen |
| The 45 pre-existing uncommitted paths | Separate cleanup decision (§2, E-5) |
| SQ-1 corpus partitioning | Product decision, still open (ADR-027) |
| Anything in [`11 §Deferred`](11_ADR_Index.md) | Has a stated revisit trigger; none are met |

---

*Governing set:* [`00_README.md`](00_README.md) ·
[`06`](06_Clean_Architecture_Migration_Plan.md) ·
[`07`](07_LangGraph_Architecture.md) · [`08`](08_MongoDB_Data_Architecture.md) ·
[`09`](09_Redis_Architecture.md) ·
[`10`](10_Backend_Security_Architecture.md) · [`11`](11_ADR_Index.md)
