# M8 — Provider Verification Spike: yfinance Statement Data

**Status:** ✅ **Complete — read-only verification spike.** No production
code, tests, Mongo collections, migrations, API routes, frontend, or Redis
were touched. This document records observations only.
**Date:** 2026-08-10
**Authorized by:** ADR-029 (Ratified) §"Next step: provider verification
spike" — [`30_ADR_Proposal_M8_Financial_Statements_Data_Model.md`](30_ADR_Proposal_M8_Financial_Statements_Data_Model.md).
**Method:** an isolated script (not part of the repository, not imported by
any production code) called `yfinance.Ticker(...)` directly against the
project's installed `yfinance` package and inspected the actual returned
objects. No Mongo, no server, no writes anywhere. Full raw output was
captured and is the source for every finding below — nothing here is
inferred beyond what the script actually printed.

---

## 1. Installed yfinance version

`yfinance==1.5.1` (pandas `3.0.3`), resolved from this project's `.venv`.
`backend/requirements.txt` pins `yfinance>=0.2.40` — 1.5.1 is what's
actually installed and was verified; the loose `>=` pin means a fresh
install elsewhere could resolve a different (likely newer) version, so
this spike's specifics should be re-checked if the pin is ever tightened
or the environment rebuilt.

## 2. Provider attributes verified

All eight attributes named in ADR-029 §6/§18 **exist** on `yfinance.Ticker`
for both tickers tested:

| Attribute | Exists | Notes |
|---|---|---|
| `.financials` | ✅ | Income statement, annual |
| `.quarterly_financials` | ✅ | Income statement, quarterly |
| `.balance_sheet` | ✅ | Annual |
| `.quarterly_balance_sheet` | ✅ | Quarterly |
| `.cashflow` | ✅ | Annual |
| `.quarterly_cashflow` | ✅ | Quarterly |
| `.cash_flow` | ✅ | **Confirmed alias of `.cashflow`** — byte-identical output observed for both tickers |
| `.quarterly_cash_flow` | ✅ | **Confirmed alias of `.quarterly_cashflow`** — same |

**Engineering implication:** only one of the two cash-flow spellings needs
to be called; `.cashflow`/`.quarterly_cashflow` are recommended as the
primary names (matching the non-underscored `.financials`/
`.balance_sheet` naming convention already used for the other two
statements).

## 3. Statement shapes

All six statement/period combinations return a **`pandas.DataFrame`** with:
- **Rows = line-item labels** (the DataFrame *index*, dtype `str`)
- **Columns = period-end dates** (dtype `datetime64[s]`, one `Timestamp`
  per column)

This confirms ADR-029 §6.2's assumption ("period end — the specific date
yfinance's DataFrame column label represents") was correct in orientation.

| Ticker | Statement | Shape (rows × periods) | Empty? |
|---|---|---|---|
| AAPL | `.financials` | 39 × 5 | No |
| AAPL | `.quarterly_financials` | 33 × 5 | No |
| AAPL | `.balance_sheet` | 69 × 5 | No |
| AAPL | `.quarterly_balance_sheet` | 65 × 7 | No |
| AAPL | `.cashflow` | 53 × 5 | No |
| AAPL | `.quarterly_cashflow` | 46 × 6 | No |
| RELIANCE.NS | `.financials` | 50 × 5 | No |
| RELIANCE.NS | `.quarterly_financials` | 37 × 5 | No |
| RELIANCE.NS | `.balance_sheet` | 77 × 5 | No |
| RELIANCE.NS | `.quarterly_balance_sheet` | 77 × 3 | No |
| RELIANCE.NS | `.cashflow` | 47 × 5 | No |
| RELIANCE.NS | `.quarterly_cashflow` | **0 × 0** | **Yes — empty** |

**Row count is not fixed** — it varies by ticker (39 vs. 50 income-statement
rows) and by period_type for the same ticker (69 annual vs. 65 quarterly
balance-sheet rows for AAPL). This confirms ADR-029's existing caution
("yfinance's DataFrame row labels vary by ticker") was correct, and extends
it: row count also varies by period type for the *same* ticker.

**Column count (period coverage) is not fixed either** — AAPL's quarterly
balance sheet returned 7 periods; RELIANCE's returned only 3. Coverage
depth is provider-side and not guaranteed uniform.

## 4. Representative row labels

Grouped by statement type. A representative sample (not exhaustive — see
§9 for the full scope of what remains unverified) from both tickers:

**Income statement** (`.financials`): `Total Operating Income As Reported`,
`Net Income From Continuing Operation Net Minority Interest`, `EBITDA`,
`EBIT`, `Normalized EBITDA`, `Total Expenses`, `Diluted EPS`,
`Diluted Average Shares`, `Reconciled Cost Of Revenue`.

**Balance sheet** (`.balance_sheet`): `Ordinary Shares Number`,
`Share Issued`, `Net Debt`, `Total Debt`, `Tangible Book Value`,
`Working Capital`, `Stockholders Equity`, `Common Stock Equity`,
`Total Capitalization`.

**Cash flow** (`.cashflow`): `Free Cash Flow`, `Capital Expenditure`,
`Repayment Of Debt`, `Issuance Of Debt`, `Financing Cash Flow`,
`End Cash Position`, `Beginning Cash Position`, `Changes In Cash`,
`Cash Dividends Paid`.

**Label format:** Title Case, space-separated, human-readable — not raw
API field codes (e.g. not `netIncome` or `NET_INCOME`).

## 5. Period metadata findings

| Concept | Status | Evidence |
|---|---|---|
| **Period type** (annual vs. quarterly) | **OBSERVED** | Directly determined by which attribute was called (`.financials` vs. `.quarterly_financials`, etc.) — not a field inside the data itself |
| **Period end** | **OBSERVED** | The DataFrame column labels, as `pandas.Timestamp` (§3) |
| **Fiscal year** | **DERIVED, imperfectly** | Not an explicit field. AAPL's periods end Sept 30 (its known fiscal year-end); RELIANCE's end March 31 (India's standard fiscal year-end) — yfinance clearly returns each company's *actual* fiscal calendar, not a forced calendar-year view. But there is no explicit "FY2025" label — a fiscal-year label would have to be derived from the period-end date, and for companies whose fiscal year spans a calendar-year boundary (like RELIANCE's Apr–Mar year), the derivation convention (is 2026-03-31 "FY2026" or "FY2025-26"?) is not determined by this spike — a naming/convention decision, not a data-availability question |
| **Reporting period duration** | **NOT AVAILABLE** (as an explicit field) | No field states "this is a 12-month period" vs. "this is a 3-month period" — it must be inferred entirely from which attribute (`quarterly_` prefix or not) was called, same as period type |

## 6. Currency findings

`.info.currency` and `.info.financialCurrency` are **both present and
equal** for both tickers: `'USD'`/`'USD'` for AAPL, `'INR'`/`'INR'` for
RELIANCE.NS. **`financialCurrency` is the more directly relevant field**
for statement data specifically (distinct from any trading-currency
field), and this spike found no case where it diverged from `currency` —
though only two tickers were tested, so that's not proof they never
diverge (e.g., for an ADR/GDR or dual-listed security).

## 7. Scale/unit findings

**Values are raw units, not scaled**, for both tickers — evidenced by
magnitude sanity-checking against known real-world figures:
- AAPL "Normalized EBITDA" ≈ $144.7B (`144,748,000,000.0`) — consistent
  with Apple's actual reported EBITDA in raw dollars, not thousands or
  millions.
- RELIANCE.NS "Net Debt" ≈ ₹2.37 trillion (`2,370,940,000,000.0`) —
  consistent with Reliance's actual reported figures in raw rupees.

No explicit "scale" or "unit" metadata field was found anywhere in
`.info` or on the statement DataFrames themselves — this conclusion is
**inferred from magnitude**, not read from a provider-supplied field.
**This spike did not exhaustively check every line item or a wider ticker
sample**, so "yfinance always returns raw units" is a reasonably strong
but not certainty-level finding — flagged, not overclaimed.

## 8. US ticker result (AAPL)

All eight attributes returned non-empty, well-formed data. No exceptions,
no missing statement types. Considered **fully usable** as a data source
for M8's US-ticker path.

## 9. Indian/BSE/NSE ticker result (RELIANCE.NS)

Five of six statement/period combinations returned usable data (annual and
quarterly income statement, annual and quarterly balance sheet, annual
cash flow). **One gap found: `.quarterly_cashflow`/`.quarterly_cash_flow`
returned an empty `(0, 0)` DataFrame** — not an exception, not missing
data with partial rows, but a genuinely empty result. This is a specific,
narrow gap (quarterly cash flow only), not a general failure of the
`.NS`-suffix routing path (which otherwise worked correctly — `.info`
resolved the right company, exchange, currency, and the other five
statement/period combinations all returned real data).

**No exception was raised at any point** for the Indian ticker — the
"failure" is a silently-empty DataFrame, which matters for implementation:
code consuming this must check `.empty`, not just catch exceptions, to
correctly detect this case.

## 10. Canonical-mapping observations

**Not finalized here (per ADR-029's own scope) — but the evidence is
notably more encouraging than the ADR assumed.** A meaningful number of
row labels are **identical strings across both tickers** for
economically-equivalent concepts: `Free Cash Flow`, `Net Debt`,
`Total Debt`, `Ordinary Shares Number`, `Share Issued`,
`Tangible Book Value`, `Capital Expenditure`, `Financing Cash Flow`,
`Repayment Of Debt`, `Issuance Of Debt` all appeared verbatim in both
AAPL's and RELIANCE.NS's statements.

**Engineering implication:** yfinance already appears to apply its own
internal normalization across source markets — the "canonical financial
concept" work ADR-029 §6.1 scoped may turn out to be closer to "use
yfinance's own row labels as the canonical vocabulary directly" than
"build a bespoke mapping table from scratch." This is an *observation*
from two tickers, not a conclusion — a wider ticker/exchange sample would
be needed before relying on it, and it does not remove the need for a
`canonical_metric` layer (unmapped/unexpected labels still need
somewhere to go), but it meaningfully de-risks the mapping-table effort
ADR-029 flagged as unresolved.

## 11. Unknown/unmapped row behavior

Not exercised in this spike — no mapping table exists yet to test against
(§6.1/§10, above: finalizing the vocabulary is out of this spike's scope).
What this spike *does* confirm: every row returned by yfinance has a
well-formed string label and a numeric-or-NaN value — there is no
observed case of a row with a missing/null label, which means the
"preserve unknown provider rows" mechanism ADR-029 §6.1 designed has
well-formed input to work with in every observed case.

## 12. Engineering implications

- Use `.financials`/`.balance_sheet`/`.cashflow` (and their `quarterly_`
  counterparts) — not the `_cash_flow` spelling, which is a confirmed
  alias.
- Statement-document identity fields map cleanly: `period_end` = the
  DataFrame column `Timestamp`, `period_type` = which attribute was
  called (not a field in the data).
- `fiscal_year` and `period_duration` (ADR-029 §6.2) require an explicit
  **naming/derivation convention decision** — the data itself doesn't
  provide either as a labeled field. Not resolvable by more spiking; this
  is a decision, not a fact to discover.
- `financialCurrency` (from `.info`) is the recommended currency source
  over `currency`, though both matched in every case tested.
- Scale/unit: no explicit metadata field exists; raw-units is the
  consistent *observed* behavior across both tickers tested, but nothing
  in the API guarantees it — worth a defensive sanity-check (e.g. flag
  suspiciously small magnitudes) rather than blind trust, if implemented.
- `RELIANCE.NS` quarterly cash flow is empty — any BSE/NSE coverage
  decision (ADR-029 §18, still open) should account for this as a known,
  narrow gap, not assume full parity with US tickers.
- Consuming code must check `DataFrame.empty`, not rely on exceptions, to
  detect "no data" for a given statement/period combination.

## 13. Decisions that now have enough evidence

- **Attribute selection**: `.financials`, `.quarterly_financials`,
  `.balance_sheet`, `.quarterly_balance_sheet`, `.cashflow`,
  `.quarterly_cashflow` are the right eight-minus-two (aliases) to call.
- **`period_end` is directly observable** from the DataFrame column labels
  — no derivation needed for this one field.
- **BSE/NSE coverage is partial, not binary**: RELIANCE.NS works for 5/6
  statement/period combinations; quarterly cash flow specifically is
  empty. This replaces ADR-029's prior "unverified whether yfinance
  returns statement data at all for Indian exchange suffixes" with a
  precise, narrower finding.

## 14. Decisions that remain unresolved

- The full canonical-metric vocabulary and label-to-concept mapping table
  (ADR-029 §6.1/§18) — this spike found encouraging cross-ticker label
  overlap (§10) but did not, and was not scoped to, finalize the
  vocabulary.
- The `fiscal_year`/`period_duration` naming and derivation convention
  (§5, above) — a decision, not a data-availability question; still
  belongs to ADR-029 §18's "still requiring CTO approval"/implementation
  scoping.
- Whether the RELIANCE.NS quarterly-cash-flow gap (§9) is representative
  of BSE/NSE tickers generally, or specific to this one ticker — only one
  Indian ticker was tested, consistent with this spike's stated purpose
  (determine *whether* yfinance returns usable data per category, not
  guarantee market coverage).
- Whether scale is *always* raw units across a wider ticker sample (§7) —
  two tickers is not proof.
- Whether `currency`/`financialCurrency` ever diverge (§6) — not observed,
  not ruled out.
- BSE PDF fallback design (explicitly out of this spike's scope, per
  ADR-029 and the CTO's instruction not to design it here).

---

*Companion documents:
[`30_ADR_Proposal_M8_Financial_Statements_Data_Model.md`](30_ADR_Proposal_M8_Financial_Statements_Data_Model.md)
(the ratified ADR this spike verifies against) ·
[`28_Post_M6_Roadmap_Reconciliation.md`](28_Post_M6_Roadmap_Reconciliation.md).*

*This is a verification report, not an implementation. No code, schema,
migration, route, or dependency change was made. M8 implementation
requires separate authorization beyond this spike and ADR-029's
ratification (see ADR-029 §18's remaining open items).*
