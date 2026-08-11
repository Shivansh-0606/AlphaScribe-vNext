# M8 — Pre-Implementation Decision Pack

**Status:** 🟡 **Partially decided across three CTO review rounds; a
short remaining list needs final approval.** This document is no longer a
from-scratch proposal — most of it reflects decisions the CTO already
made during review. **M8 implementation remains gated regardless** —
nothing in this document authorizes code, schema, dependency, or
migration changes.

### A. Already CTO-decided (prior review rounds — not reopened here)

- **yfinance initial reproducibility baseline:** `yfinance==1.5.1` (§1)
- **Per-metric unit semantics:** `currency` stays document-level context;
  `unit` exists per metric inside `metrics[]` (§2.D)
- **`scale`:** removed from the v1 persisted model (§2.D)
- **`fiscal_year`:** an AlphaScribe-derived normalized fiscal-period-ending
  year, not a provider-observed label (§2.C)
- **`period_duration`:** omitted from v1 (§2.B)
- **Acquisition state:** three semantic states — not yet acquired /
  available / confirmed unavailable (§4)
- **Acquisition lifecycle:** conceptually separate from
  `FinancialStatement` persistence — `FinancialStatement data ≠
  Acquisition lifecycle state` (§4)
- **Canonical vocabulary governance:** the five-step
  observe→identify→validate→approve→promote process, reviewed/versioned,
  not requiring recurring per-mapping CTO approval (§2/§3)
- **Restatement policy:** latest-provider-value-wins (§2.E)
- **Migration number:** `m0006` (§2.F)
- **BSE/NSE v1 strategy:** yfinance-only, no PDF fallback (§2.G)

### B. Still requiring final CTO approval

- Final confirmation of the `financial_statements` collection name
- Final confirmation of the complete `FinancialStatement` field set (§2.B)
  — the individual field semantics in §A are decided; what remains is
  sign-off on the field set as a whole
- **Final approval of the complete M8 decision pack as a whole**

Everything in §A is already decided and is **not** reopened by this
section. For the three items whose recommendations were settled during
review (restatement policy, migration number `m0006`, BSE/NSE v1
strategy): already decided by the CTO during the review rounds — formal
ratification is completed when the complete M8 decision pack receives
final CTO approval.

**Outside this approval entirely:** the proposed API contract
(`GET /companies/{ticker}/financials`) is a **separate future gate** —
ADR-029 §9/§18 — and is not part of this pack's approval.

**Date:** 2026-08-10
**Inputs:** [`30_ADR_Proposal_M8_Financial_Statements_Data_Model.md`](30_ADR_Proposal_M8_Financial_Statements_Data_Model.md)
(Ratified) · [`31_M8_Provider_Verification_Spike_yfinance.md`](31_M8_Provider_Verification_Spike_yfinance.md).
**Scope:** repository inspection, dependency inspection, and decision
analysis only, per the CTO's explicit brief. No file outside this document
was modified to produce it.

> **Revision note (2026-08-10):** the CTO reviewed the original decision
> pack and issued **🟡 APPROVED WITH CHANGES**, requiring four corrections:
> (1) per-metric unit semantics — a document-level `currency`/`scale`
> alone cannot disambiguate a currency-denominated metric (revenue) from a
> per-share metric (diluted EPS) or a count (shares outstanding); (2)
> `fiscal_year` semantics clarified as an AlphaScribe-derived normalization,
> not an observed provider label; (3) canonical-metric promotion
> strengthened from "cross-ticker string match ⟹ auto-promote" to an
> explicit multi-step governance process requiring semantic validation,
> not string equality alone; (4) explicit data-availability/acquisition-
> state semantics, previously left as an open either/or. All four are
> addressed below. Every decision the CTO's brief listed as
> preserved-unchanged (§6 of that review) remains exactly as previously
> recommended — none was reopened.
>
> **Revision note, Round 3 — final targeted revision (2026-08-10):** the
> CTO issued a further **🟡 APPROVED WITH CHANGES**, requiring: removal of
> the unverified `scale` field from the v1 persisted set (§2.D — `scale`
> was inferred from magnitude, not provider-guaranteed, and should not be
> persisted as financial metadata on that basis alone); explicit
> separation of acquisition-lifecycle state from `FinancialStatement` data
> itself (§4); clarification that the canonical-vocabulary governance
> model, not each individual metric mapping, is what the CTO is ratifying
> (§3); and selecting `yfinance==1.5.1` as the initial reproducibility
> baseline rather than a range (§1). All four are addressed below; nothing
> from earlier rounds was silently reopened.
>
> **Revision note, Round 4 — final governance clarification (2026-08-10):**
> corrected the document's opening status so the items already decided in
> Rounds 1–3 are no longer represented as unresolved (new §A/§B split,
> above); clarified that canonical-metric mappings are governed by the
> **Backend & AI architecture/data-governance review process**, not
> recurring per-mapping CTO approval (§3); and tightened the Summary
> Table / Implementation Blockers to a three-way
> decided/requires-final-approval/separate-future-gate distinction (below).
> No previously settled M8 architecture decision was reopened or changed.
>
> **Revision note, Round 5 — CTO final micro-revision (2026-08-10):**
> finalized `fiscal_year` as the canonical field name; removed the
> alternative `normalized_fiscal_year` naming discussion; clarified that
> restatement policy, `m0006`, and the BSE/NSE strategy are already
> CTO-decided and become formally ratified with final approval of the
> complete decision pack; removed the remaining governance ambiguity from
> §B, the Summary Table, and the Implementation Blockers. No architecture
> was changed — documentation cleanup only.

---

## 1. Dependency Reproducibility (investigation only)

**Authoritative dependency mechanism:** `backend/requirements.txt` is the
single, sole mechanism — confirmed by direct inspection:
- `scripts/run.py:137`: `pip install -r requirements.txt` — the local-dev
  setup path.
- `.github/workflows/backend-ci.yml:52,107`: `python -m pip install -r
  requirements.txt` — both CI jobs (hermetic and live), identical command.
- **No lock file exists anywhere** (`*.lock`, `Pipfile.lock`,
  `poetry.lock`, `uv.lock` — none found in the repo).
- **No Dockerfile or docker-compose exists** — confirmed absent (matches
  Document 28 §C's earlier finding, still accurate).
- No alternate dependency-lock mechanism (Poetry, Pipenv, uv, Conda) is in
  use anywhere in the repo.

**Current yfinance reproducibility status: NOT guaranteed.**
`requirements.txt:26` declares `yfinance>=0.2.40` — an open-ended floor
with no ceiling. Every fresh install (local dev, CI, or any future
deployment) resolves to whatever the *latest* version satisfying `>=0.2.40`
is at install time, not necessarily the `1.5.1` verified in Document 31.
CI's `cache-dependency-path: backend/requirements.txt` only keys pip's
*cache*, not a version lock — it does not pin resolution.

**Recommended version strategy (revised per CTO review — decided, not
applied):** `yfinance==1.5.1`, an exact pin. Document 31 verified provider
behavior against this specific version; M8's persistence semantics (the
statement-document shape, row-label expectations, the currency/unit model
in §2.D) depend on that verified behavior actually being what's installed.
An open floor (`>=0.2.40`) or even a bounded range (`>=1.5.1,<2.0.0`)
still permits drift to an unverified version between the one this spike
actually exercised and whatever satisfies the constraint at install time —
exact pinning is the safest initial implementation baseline given that
M8 has not yet been implemented against anything but 1.5.1.

**This is an initial reproducibility baseline, not a permanent refusal to
upgrade.** The intended future upgrade process is: upgrade the pin →
re-run a provider verification spike (matching Document 31's method)
against the new version → confirm no regression in the shapes/labels/
behavior M8 depends on → only then make the dependency change, deliberately
and separately from routine dependency maintenance.

**Files that would need changing (if approved):** `backend/requirements.txt`
only — no other file references a yfinance version constraint.

**Risks of changing the version:**
- An exact/narrow pin loses automatic bugfix and security updates until
  manually revisited.
- If `1.5.1` has any latent bugs, pinning it locks those in.
- A tighter pin needs periodic manual review to stay current — a small
  ongoing maintenance cost, not a one-time fix.
- Changing `requirements.txt` invalidates CI's pip cache once (a minor
  CI runtime cost, not a correctness risk).

**No dependency file was modified to produce this section** — this is a
recommendation for a future, separately-approved change.

---

## 2. Financial Semantics Decision Pack

### A. Collection name

**Recommend confirming `financial_statements` as final.** It follows the
existing collection-naming convention exactly (plural, snake_case, no
prefix — matching `companies`, `filings`, `filing_chunks`, `reports`,
`jobs`, `explanations`). No evidence surfaced a reason to deviate.

### B. Exact field names

| Field | Recommended type | Rationale |
|---|---|---|
| `ticker` | string | Matches existing convention (`companies.ticker` et al.) |
| `period_type` | `"annual" \| "quarterly"` | Already proposed in ADR-029; matches roadmap wording |
| `period_end` | ISO-8601 date string | Matches the repo's universal convention (every existing schema stores dates as `"ISO-8601 str"`, never a native BSON Date — `08` §4 throughout). Sourced directly from the yfinance DataFrame column `Timestamp` (Document 31 §3), truncated to date granularity (the time component is always `00:00:00` — not meaningful, see §C below) |
| `fiscal_year` | string, e.g. `"2025"` | See §C — AlphaScribe-derived, not provider-observed |
| `statement_type` | `"income" \| "balance_sheet" \| "cash_flow"` | Already decided (ADR-029 §6.5/§8) |
| `currency` | string, ISO 4217 | Sourced from `.info.financialCurrency` (Document 31 §6's recommendation over `.info.currency`); document-level context (§D) |
| `source` | `"yfinance"` | Matches existing `filings.source` convention |
| `fetched_at` | ISO-8601 datetime string | Matches existing convention |
| `metrics` | array of metric objects | Contains the persisted financial line items; each metric contains `canonical_metric`, `provider_label`, `value`, and `unit` as defined in §2.D |

**`period_duration` — recommend dropping as a stored field (reasoning
revised per CTO review).** ADR-029 §6.2 proposed it to guard against a TTM
(trailing-twelve-month) figure being mistaken for a quarterly one.
Document 31 found no evidence of TTM-labeled columns anywhere —
`.quarterly_*` calls returned only quarter-end dates for both tickers
tested. **This is not a claim that "annual" always spans exactly 12
months or "quarterly" always spans exactly 3 calendar months** — no such
guarantee was observed or is assumed. The narrower, evidence-supported
statement is: the current provider surface distinguishes annual from
quarterly periods entirely through *which attribute was called*
(`.financials` vs. `.quarterly_financials`, etc.), and nothing observed
in Document 31 requires an explicit duration field to make that
distinction usable for v1. Recommend omitting it from v1 per "do not
invent unnecessary fields" — it can be added later if analytical
requirements (e.g. exact period-span math) require it, not because the
underlying periods are assumed to have a fixed length.

### C. Period semantics

| Concept | Classification | Rule |
|---|---|---|
| `period_type` | **OBSERVED** | Recorded as whichever attribute produced the document (`.financials` → `"annual"`, `.quarterly_financials` → `"quarterly"`) — not read from a field inside the data itself (Document 31 §5 confirmed no such field exists) |
| `period_end` | **OBSERVED** | The DataFrame column `Timestamp`, taken verbatim (date component only) |
| `fiscal_year` | **DERIVED (AlphaScribe convention, not provider fact)** | See clarification below — revised per CTO review |
| `period_duration` | *(dropped, §B)* | N/A |

**`fiscal_year` semantic clarification (field name finalized per CTO
micro-revision):** the final field name is **`fiscal_year`** — decided,
not open. Its semantic: `fiscal_year` is an **AlphaScribe-derived
normalized fiscal-period-ending year, computed from `period_end`** — it
is **not** an observed provider label, and Document 31 did not observe
yfinance asserting any such label. Concretely, the rule is:
`fiscal_year` = the calendar year of `period_end` (e.g. AAPL's
`2025-09-30` → `"2025"`; RELIANCE's `2026-03-31` → `"2026"`). This must
not be read as "RELIANCE's period ending 2026-03-31 has been observed to
carry a provider fiscal-year label of '2026'" — no such label exists in
what was observed; this is AlphaScribe's own normalization, chosen for
simplicity and determinism rather than an attempt to replicate each
issuer's own human-facing fiscal-year label (which Document 31 confirmed
is not present in the data, §5, and which — for a company like RELIANCE
whose fiscal year spans a calendar-year boundary — the issuer itself
might call "FY2025-26" or similar). **No jurisdiction-specific label
format (e.g. `"FY2025-26"`) is proposed for v1** — only the single
normalized ending-year value, kept deliberately minimal.

### D. Currency and per-metric unit semantics (revised — `scale` removed per CTO review)

**The original decision pack's document-level-only `currency`/`scale`
was insufficient, per the first CTO review, and per-metric `unit` was
added to correct it.** A single statement document mixes metrics with
genuinely different semantic units — `Total Revenue` is
currency-denominated, `Diluted EPS` is currency-*per-share*, `Diluted
Average Shares` is a share count, and a margin/ratio metric (where one is
later derived or provided) is dimensionless. A document-level `currency`
alone cannot make a share-count or a per-share value unambiguous — it can
only describe metrics that are actually plain currency amounts.

**`scale` is removed from the v1 persisted field set, per this final
revision.** The reasoning: Document 31 §7 inferred "raw units" purely by
sanity-checking observed magnitudes against known real-world figures — it
did **not** find an explicit, provider-guaranteed scale metadata field
anywhere in `.info` or the statement DataFrames. That observation is
sufficient to *note* the apparent behavior (as Document 31 does) but is
**not sufficient to persist `scale` as a financial-metadata invariant on
every statement document** — doing so would assert a guarantee the
provider itself never made. `scale` can be introduced later if a verified
requirement emerges (e.g. a wider ticker sample surfacing a genuine
scale-metadata field, or a magnitude inconsistent with raw units).

**Revised persisted shape:**

```
FinancialStatement
├── currency   ("USD", "INR", ...)          — document-level currency context
└── metrics[]
    ├── canonical_metric
    ├── provider_label
    ├── value
    └── unit   ("currency" | "currency_per_share" | "shares" | "ratio" | "percentage" | "count")
```

**Semantic relationship (explicit, not implied):**
- `currency` (document-level) supplies the currency context **only for
  metrics whose `unit` is `"currency"` or `"currency_per_share"`** — it
  has no meaning for a `"shares"`, `"ratio"`, `"percentage"`, or
  `"count"` metric, and must not be read as applying to every metric in
  the document indiscriminately.
- `unit` (per-metric, inside `metrics[]`) is what actually determines how
  to interpret a given metric's `value` — the only field of this kind
  that varies per line item within one document, and (with `scale`
  removed) now the sole per-metric semantic-interpretation field.

**This is deliberately a small, closed enumeration for v1**, not a
general-purpose units system: `currency`, `currency_per_share`, `shares`,
`ratio`, `percentage`, `count` cover every metric category observed in
Document 31's row-label sample (income/balance/cash-flow line items,
per-share figures, share counts). It is not exhaustive by construction —
an unrecognized unit is a data-mapping question to resolve when
encountered (same evidence-driven posture as §3's canonical-metric
governance below), not a reason to expand the enumeration speculatively
now.

### E. Restatement policy

**Recommend confirming ADR-029 §6.4's proposed v1 policy as-is:**
latest-provider-value-wins, whole-document upsert, no historical
provider-version storage. Document 31's spike was a single point-in-time
snapshot and could not observe restatement behavior directly (that would
require re-fetching the same ticker/period across multiple real-world
provider revisions) — nothing in the spike's evidence contradicts the
already-proposed policy, and its simplicity remains appropriate for v1.

### F. Migration numbering

**`m0002` is already taken** — confirmed by direct inspection of `08`
§11's frozen migration table: `m0001_indexes`, `m0002_job_user_id`,
`m0003_learning`, `m0004_job_events_drop`, `m0005_report_timing` are all
already reserved (planned/named in the frozen document, regardless of
each one's current implementation status). **Recommend `m0006` as the
next available number** for M8's collection, if the CTO wants this
tracked as a formal numbered migration.

### G. BSE/NSE strategy

**Recommend adopting exactly the CTO's stated preferred direction:**
support whatever yfinance returns per statement/period combination;
represent unavailable combinations **explicitly** (e.g. a status field or
the simple absence of that one statement-type document, rather than a
crash or a silently-empty response the frontend can't distinguish from
"not yet fetched"); **do not add a BSE PDF fallback to M8 v1.**

**Why this is well-supported by Document 31's evidence, not just
preference:** RELIANCE.NS returned real, usable data for 5 of 6
statement/period combinations — only `.quarterly_cashflow` was empty
(`(0,0)` DataFrame, no exception). This is a narrow, specific gap in one
combination for one ticker, not a systemic BSE/NSE failure. Building a PDF
fallback now would be solving a problem the evidence doesn't show exists
at that scale — one Indian ticker's one quarterly-cash-flow gap doesn't
justify the added complexity/scope of a parsing fallback for v1. If a
wider ticker sample later shows this is a systemic quarterly-cash-flow
gap across most Indian tickers (not just this one), that would be new
evidence justifying revisiting the fallback question — not assumed now.

---

## 3. Canonical Metric Policy (governance strengthened per CTO review)

**The `canonical_metric` / `provider_label` / `value` / `unit` layer is
retained as-is — not replaced with raw yfinance labels.** Document 31's
finding that several labels (`Free Cash Flow`, `Net Debt`, `Total Debt`,
`Ordinary Shares Number`, etc.) appeared identically across both AAPL and
RELIANCE.NS is evidence that yfinance's own labeling is *more consistent
than assumed*, not proof of a universal, stable vocabulary — two tickers
from two exchanges is not a representative sample, and unmapped/unexpected
labels must remain preservable regardless (ADR-029 §6.1's "preserve
unknown rows" mechanism is unaffected by this, and now also preserves
`unit` alongside `provider_label`/`value` for unmapped rows, §2.D).

**Corrected governance process (revised per CTO review — string equality
alone is no longer sufficient to promote a mapping):** the original
proposal risked reading "identical string on two tickers" as
self-validating. It is not — two labels can coincide by string without
the underlying line items being economically equivalent (or, conversely,
two different provider labels can represent the same concept). The
revised process is five explicit steps, none of which is automatic:

1. **Observe** the provider label as it actually appears in ingested data
   (`provider_label`, verbatim).
2. **Identify a candidate canonical concept** — a proposed
   `canonical_metric` this label *might* map to, informed by (but not
   concluded from) evidence like cross-ticker string recurrence.
3. **Validate the semantic meaning** — confirm the candidate label
   actually represents the same accounting concept the canonical name
   implies (e.g. checking the value's position/role within the statement,
   not just matching text) before treating string recurrence as
   meaningful.
4. **Approve the mapping** — an explicit sign-off step, not implied by
   steps 1–3 alone.
5. **Promote to the canonical vocabulary** — only after step 4.

**Until a label completes all five steps, it stays unmapped:**
`canonical_metric: null`, with `provider_label`, `value`, and `unit`
(§2.D) all preserved and queryable. Cross-ticker identical strings
(Document 31's own observed matches, e.g. `Free Cash Flow`) are useful
**candidates for step 2**, not evidence sufficient to skip straight to
step 5.

**Governance ownership (clarified per Round 4 — the CTO is approving the
five-step *process* here, not acting as a recurring operational approver
for every individual metric):**
- Provider labels (`provider_label`) are observed and preserved as they
  actually appear — step 1.
- Candidate canonical mappings are identified — step 2.
- Semantic meaning is validated — step 3.
- Mappings are **reviewed and approved through the Backend & AI
  architecture/data-governance review process** — step 4. This names the
  existing review discipline this repo already applies to architecture
  decisions (the same posture ADR-029 itself went through, §5's ports
  precedent, §10's index precedent) — it is **not** a new department, a
  new approval bureaucracy, a new product feature, or a new workflow
  system, only a clarification of who owns this specific ongoing
  responsibility once the governance model itself is ratified.
- Approved mappings are promoted — step 5 — and become part of a
  **versioned canonical-vocabulary artifact** (a concrete mapping table,
  format not designed here), owned going forward by that same Backend &
  AI architecture/data-governance review process.
- **Individual mappings do not require recurring CTO approval** once this
  five-step governance model itself has been ratified by the CTO (this
  document's own approval request, §A above).
- **Material changes** — a new statement type, a change to the five-step
  process itself, or a mapping decision with significant product/
  architectural impact — can still trigger normal CTO architecture
  review. This is the escalation path, not the default path for routine
  mappings.

**This document does not create the final exhaustive canonical
vocabulary** — only this five-step process and its governance ownership
model, which itself requires CTO sign-off before implementation begins
applying it.

---

## 4. Data Availability / Acquisition State Semantics (added per CTO review)

The original decision pack left this as an open either/or ("explicit
status *or* absence of a statement document") — the CTO's review requires
resolving it to one recommendation, kept lightweight, not a state machine.

**Architectural boundary (clarified per this final revision):**

```
FinancialStatement data  ≠  Acquisition lifecycle state
```

`FinancialStatement` (§2.D) represents **persisted financial data** — a
statement document that exists because a fetch succeeded. Acquisition
state represents **whether AlphaScribe has attempted, and
successfully or unsuccessfully acquired, a given statement** — a
conceptually separate question that exists independently of whether a
`FinancialStatement` document happens to exist. This document does
**not** design the Mongo schema, choose a collection name, or define
fields for either concept beyond what §2/§6 of ADR-029 and §2.B/§2.D
above already fixed for `FinancialStatement` itself — and it explicitly
does **not** propose creating a placeholder `FinancialStatement`
containing fake/empty metrics to represent "not yet acquired" or
"confirmed unavailable." The point of this boundary is narrower and
purely conceptual: **the absence of a `FinancialStatement` document must
not be the sole mechanism used to represent acquisition state**, because
that collapses "haven't tried yet" and "tried, provider confirmed
nothing exists" into the same observable signal (§4's three states,
below, exist to prevent exactly that collapse) — how that boundary gets
implemented (a separate small tracking structure, a status alongside the
document, or something else) is left to implementation.

**Original proposal in this document (superseded — see below): a minimal
three-state acquisition status, evaluated per `(ticker, period_type,
period_end, statement_type)` combination — the same identity ADR-029 §8
already fixed for the statement document itself.**

| State | Meaning |
|---|---|
| **not yet acquired** | No fetch attempt has been made for this identity yet |
| **available** | A fetch succeeded and returned usable data — the statement document exists with a populated `metrics[]` |
| **confirmed unavailable** | A fetch was attempted and the provider explicitly returned no data for this identity (an empty DataFrame, per Document 31 §9 — not an exception, not a timeout) |

This document originally left the acquisition-status *identity/grain*
itself as, in effect, an open recommendation rather than a fixed
decision — it fixed only that the three states above must be
representable and must not collapse into a single "no document" case
(which would make "haven't tried yet" indistinguishable from "tried and
confirmed nothing exists"). **Document 34 subsequently flagged the
`period_end`-inclusive identity above as R10 — a granularity mismatch
against Document 33's per-statement-type response shape.** **Document 35
§6 evaluated company-level, period-level, and statement-type-level
alternatives and definitively resolved R10**, rejecting period-level
granularity (it would require an aggregation rule the architecture has
no evidence to define, and doesn't correspond to an independently
executable provider operation) in favor of statement-type-level:

**Current, ratified `AcquisitionState` identity (Document 35 §6):**
`(ticker, period_type, statement_type)` — **`period_end` is not part of
the `AcquisitionState` identity.** The earlier period-level formulation
above is therefore superseded and must not be used as the implementation
identity.

This does not change `FinancialStatement` itself: `period_end` remains a
valid, required `FinancialStatement` field (§2.B) — individual financial
statements are period-specific, and ADR-029 §8's `FinancialStatement`
identity (`ticker + period_type + period_end + statement_type`) is
unaffected. The correction applies only to the separate
`AcquisitionState` entity's own identity, per the boundary this section
already establishes (`FinancialStatement data ≠ Acquisition lifecycle
state`, above). The storage mechanism for `AcquisitionState` — whether a
field on a placeholder document, a separate small tracking structure, or
something else — remains an implementation-time modeling choice, not
fixed by Document 35 §6 or here.

**Interaction with other decided architecture (stated at the ratified
`AcquisitionState` grain — `ticker, period_type, statement_type`, no
`period_end`):**
- **Cold start** (ADR-029 §8): a `ticker`/`period_type`/`statement_type`
  identity in the **not yet acquired** state is exactly what triggers the
  "controlled initial acquisition path" ADR-029 already established (and
  explicitly did not design the mechanism for) — this section doesn't
  change that, it just names the state that triggers it.
- **Freshness / serve-then-refresh-async** (ADR-029 §8): only applies to
  the **available** state — there is nothing to "serve stale, refresh
  async" for an identity that's **not yet acquired** (nothing persisted
  to serve) or **confirmed unavailable** (refreshing wouldn't change a
  provider-side absence without new evidence prompting a re-check).
- **`RELIANCE.NS` `.quarterly_cashflow` (Document 31 §9)** is the concrete
  example of **confirmed unavailable** — the fetch was attempted, no
  exception occurred, and the provider returned a genuinely empty
  `(0, 0)` DataFrame. Under this scheme, that `ticker`/`period_type`/
  `statement_type` identity would be marked confirmed unavailable rather
  than silently absent, which is precisely what lets the frontend's
  `StatementTable` "Partial Failure" state (ADR-029 §6.5) distinguish
  "this statement type is unavailable for this company" from "we haven't
  checked yet" or a transient fetch problem.

**Not implemented here** — no field, document shape, or code exists yet;
this section resolves the *semantic* question the CTO's review flagged,
and records that Document 35 §6 subsequently resolved the identity/grain
question R10 raised — neither is a new decision made by this
synchronization.

---

## Summary Table

Three-way classification (per Round 4): **DECIDED** (settled in a prior
review round, not reopened) · **REQUIRES FINAL APPROVAL** (recommendation
stands, formal sign-off on this specific pack still outstanding) ·
**SEPARATE FUTURE GATE** (deliberately not part of this pack's approval
at all — a different, later authorization).

| # | Item | Recommendation | Classification |
|---|---|---|---|
| 1 | yfinance version constraint | `yfinance==1.5.1`, exact pin (initial reproducibility baseline, not a permanent refusal to upgrade) | **DECIDED** — the `requirements.txt` *file change* itself remains a **SEPARATE FUTURE GATE**; deciding the version does not authorize editing the file |
| 2 | Collection name | `financial_statements` | **REQUIRES FINAL APPROVAL** |
| 3 | Field set | Per §2.B table; `period_duration` and `scale` both omitted | **REQUIRES FINAL APPROVAL** as the complete field-set confirmation; the individual field semantics (including both omissions) are already **DECIDED** and unchanged |
| 4 | `fiscal_year` | Final field name **`fiscal_year`**; calendar year of `period_end`; AlphaScribe-derived, not provider-observed | **DECIDED** (name and semantic) |
| 5 | Currency/unit model | `currency` document-level; per-metric `unit`; `scale` removed entirely (§2.D) | **DECIDED** |
| 6 | Restatement policy | Latest-provider-value-wins (ADR-029 §6.4) | **DECIDED** — formal ratification occurs with final pack approval |
| 7 | Migration numbering | `m0006` | **DECIDED** — formal ratification occurs with final pack approval |
| 8 | BSE/NSE v1 policy | yfinance-only, no PDF fallback | **DECIDED** — formal ratification occurs with final pack approval |
| 9 | Canonical vocabulary governance | Five-step process; mappings reviewed/approved through the Backend & AI architecture/data-governance review process; versioned artifact; no recurring per-mapping CTO approval; material changes escalate | **DECIDED** — CTO approves the governance model, not each future mapping |
| 10 | Data-availability/acquisition state | Three-state model, explicitly separate from `FinancialStatement` persistence. Identity/granularity subsequently resolved by Document 35 §6 as `(ticker, period_type, statement_type)` — no `period_end` | **DECIDED** — states and identity/granularity both settled (states here; granularity via Document 35 §6); repository/schema/code mechanism remains implementation-level work, nothing implemented |
| 11 | `GET /companies/{ticker}/financials` route | Proposed shape only | **SEPARATE FUTURE GATE** — not part of this pack's approval; needs its own API-contract review (ADR-029 §9/§18) |
| 12 | This decision pack as a whole | — | **REQUIRES FINAL APPROVAL** |

## Implementation Blockers Remaining

- **yfinance version:** `yfinance==1.5.1` is DECIDED; modifying
  `requirements.txt` remains **unauthorized** — deciding the version does
  **not** authorize the file change, which has not been made.
- **`fiscal_year` field name:** DECIDED as `fiscal_year`.
- **Per-metric `unit` semantics:** DECIDED; implementation
  (parsing/assigning `unit` per canonical metric) remains **unauthorized**.
- **Acquisition-state semantics:** DECIDED (three states, conceptually
  separate from `FinancialStatement` data). **Acquisition-state identity
  granularity is also DECIDED — resolved by Document 35 §6 as `(ticker,
  period_type, statement_type)`, without `period_end`**, superseding this
  document's original period-level formulation (§4). Remaining
  implementation work concerns the concrete persistence mechanism,
  repository behavior, schema/index details, and integration with the
  ratified orchestration architecture (Document 36) — all of which remain
  **unauthorized**.
- **Canonical vocabulary governance:** DECIDED; the actual mappings
  remain future work under that governance model — none exist yet.
- **Restatement policy:** DECIDED (latest-provider-value-wins); formal
  ratification occurs with final approval of the complete decision pack.
- **Migration `m0006`:** DECIDED; formal confirmation occurs with final
  approval of the complete decision pack.
- **BSE/NSE yfinance-only strategy:** DECIDED (no PDF fallback for v1);
  formal ratification occurs with final approval of the complete decision
  pack.
- **API contract** (`GET /companies/{ticker}/financials`) remains a
  **SEPARATE FUTURE GATE**, unresolved — ADR-029 §9/§18, unchanged here.
- No collection, index, migration, route, or repository code exists.
- **This decision pack itself still REQUIRES FINAL APPROVAL as a whole**
  (item 12, above) even though most of its individual items are DECIDED.
- **M8 implementation remains unauthorized.**

---

*Companion documents:
[`30_ADR_Proposal_M8_Financial_Statements_Data_Model.md`](30_ADR_Proposal_M8_Financial_Statements_Data_Model.md) ·
[`31_M8_Provider_Verification_Spike_yfinance.md`](31_M8_Provider_Verification_Spike_yfinance.md) ·
[`08_MongoDB_Data_Architecture.md`](08_MongoDB_Data_Architecture.md) §11
(migration numbering, frozen).*
