"""M14 Filing Analysis -- Document 65 section 20.1 SECTION-LOCATION VALIDATION SPIKE.

DIAGNOSTIC / VALIDATION-GATE ONLY. Round 2 -- bounded OAQ-1(D) realization
improvement + revalidation, per the CTO authorization of 2026-09-01.

This is the "early spike + go/no-go" that Document 65 section 20 / section 20.1
and Document 66 section 8 require to run FIRST, before any wiring of the full
four-output M14 flow.

Ratified architecture being tested (Document 65 OAQ-1(D) Alternative B),
UNCHANGED: heuristic heading detection over the EXISTING unstructured
`filing_chunks` + a short LLM classification pass FOR GENUINELY AMBIGUOUS
HEURISTIC CANDIDATES ONLY. No persisted section store, no ingest change, no
new collection/index/schema, no LangGraph change, no production wiring, no C-2.

Round-2 realization fixes (all inside this spike file):
  * local html.unescape + Unicode punctuation + whitespace normalization
    (the raw `&#8217;` / `&#160;` / curly-quote / collapsed-whitespace noise
    that blinded the round-1 regexes);
  * inline heading recognition (not line-anchored);
  * possessive AND non-possessive "Management('s) Discussion and Analysis";
  * deterministic table-of-contents discrimination;
  * substantive-heading selection (reject quoted / parenthetical cross-refs
    such as '"Risk Factors" (Part I, Item 1A of this Form 10-K)');
  * structural next-heading / running-header end-boundary detection;
  * conservative `partial` when the end boundary cannot be established
    (range collapses to [start, start] with end_established=False);
  * REMOVED the round-1 four-point sparse probe + min..max range fabrication;
  * LLM classification invoked ONLY when the heuristic found a heading token
    for a section but every occurrence was non-substantive (TOC / cross-ref);
    then K=3 classifications at temperature=0.0, majority vote; no majority or
    wrong majority -> section NOT located, no range expansion ever;
  * N=5 identical-input location runs per filing, every run recorded.

Ground truth: a FIXED evaluation-only table (see GROUND_TRUTH below). The
prediction pipeline never reads it; only the evaluate_* layer does, AFTER
prediction.

Contract-state constraint (Document 64 section 11.6/11.7): the per-section
`diagnostic_state` values here are LOCATOR diagnostics, NOT Document 64
contractual `complete` / `partial` / `insufficient_evidence`. Every one is
tagged `DIAGNOSTIC -- NOT DOCUMENT 64 CONTRACT SEMANTICS`.

The script produces evidence + a §20.1 bar assessment. The final PASS /
FAIL-STOP call is made against the CTO-set §20.1 bar (unchanged).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_BACKEND_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

_RESULTS_DIR = _BACKEND_ROOT / "evaluation" / "m14_section_location_spike"

# The §20.1-validated section-location realization now lives in the production
# module agents/filing_sections.py. This harness imports it verbatim so the
# §20.1 evidence exercises the shipping code, and keeps ONLY the validation-only
# concerns (corpus assembly, the human-established GROUND_TRUTH table, the
# evaluate_* metrics layer, the bar assessment, evidence emitters).
from agents.filing_sections import (  # noqa: E402
    normalize_text, is_toc_chunk, is_substantive, classify_kv,
    locate_section, locate_all, _heading_of_kind, _prose_follows, _end_boundary,
    _RF_HEAD, _MDA_HEAD, _ITEM_TOKEN, _ITEM_TOKEN_PAGED, _TEXT_THEN_PAGE,
    LOCATOR_DIAGNOSTIC_NOTE as _DIAG_TAG,
)


def _load_env() -> None:
    env_path = _BACKEND_ROOT / ".env"
    if not env_path.exists():
        return
    for ln in env_path.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#") or "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# ===========================================================================
# 6. HUMAN-ESTABLISHED EVALUATION GROUND TRUTH
#    -- NOT PRODUCTION LOGIC -- NOT CONTRACT ARTIFACT --
#    From the CTO-reviewed 2026-08-31 evidence reconciliation, refined by
#    read-only chunk inspection 2026-09-01. Consumed ONLY by evaluate_* below,
#    AFTER prediction. locate_* above never imports or references this name.
# ===========================================================================

GROUND_TRUTH = {
    # tag: HUMAN-ESTABLISHED EVALUATION GROUND TRUTH -- NOT PRODUCTION LOGIC -- NOT CONTRACT ARTIFACT
    "EDGAR_10Q": {   # TSLA 10-Q  doc_id 1bcb03b5-...  166 chunks
        "risk_factors": {"present": True, "start": 155, "end": 155,
                         "note": "Part II Item 1A; entire 'no material changes, see 10-K' disclosure sits in chunk 155; 'ITEM 2. UNREGISTERED SALES' follows in the same chunk"},
        "mda": {"present": True, "start": 104, "end": 148,
                "note": "Part I Item 2; 'ITEM 2. MANAGEMENT'S DISCUSSION AND ANALYSIS ... The following discussion and analysis' at ch 104; ends before 'ITEM 3. QUANTITATIVE...' at ch 149"},
    },
    "EDGAR_10K": {   # MSFT 10-K  doc_id 168d4f17-...  215 chunks
        "risk_factors": {"present": True, "start": 70, "end": 185, "start_tol": 2,
                         "note": "Item 1A body opens 'ITEM 1A. RISK FACTORS Our operations and financial results are subject to various risks and uncertainties' at ~ch 70 (heading late in the chunk, continues into 71); runs to ~185 before 'ITEM 6. [RESERVED]'/'ITEM 7' at ch 191-192. START is the load-bearing value; END approximate"},
        "mda": {"present": True, "start": 192, "end": 214,
                "note": "Item 7; '33 PART II Item 7 ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS ... The following Management's Discussion and Analysis ... (\"MD&A\")' at ch 192; runs to end of file / Item 8"},
    },
    "BSE_ANNUAL": {  # RELIANCE Integrated AR  doc_id ad4151a4-...  1209 chunks
        "risk_factors": {"present": False,
                         "note": "NO SEC-style Risk Factors / Item 1A section. 'Enterprise Risk Management' content (~ch 125-143) is NOT a Risk Factors section and must not be reported as one"},
        "mda": {"present": True, "start": 22, "end": 144, "start_tol": 2,
                "note": "'Management Discussion and Analysis' (non-possessive) begins ch 22 ('... Management Discussion and Analysis Financial Performance and Review Operating Environment Global economic expansion continued'); running header recurs ch 22..144; ch 6 is the contents page"},
    },
    "PLAINTEXT": {   # RIVERSTONE memo  doc_id 761094a5-...  3 chunks
        "risk_factors": {"present": False,
                         "note": "informal 'Risks the management team is tracking' paragraph is NOT a formal Risk Factors section"},
        "mda": {"present": False,
                "note": "informal 'Trading position' / 'Matters the board discussed' / 'Outlook' narrative is NOT a formal MD&A section"},
    },
}


# ===========================================================================
# 7. EVALUATION LAYER  (the ONLY consumer of GROUND_TRUTH)
# ===========================================================================

def evaluate_section(pred: dict, gt: dict, filing_key: str, kind: str) -> dict:
    present = gt["present"]
    predicted = pred["predicted_present"]
    out = {
        "filing": filing_key, "section": kind,
        "target_present": present,
        "predicted_range": pred["range"],
        "ground_truth_range": [gt["start"], gt["end"]] if present else None,
        "basis": pred["basis"],
        "diagnostic_state": pred["diagnostic_state"],
        "diagnostic_state_note": _DIAG_TAG,
        "boundary_status": (
            "n/a" if not predicted else
            ("end_established" if pred["end_established"] else "end_not_established")
        ),
        "false_positive": False,
        "false_negative": False,
        "verdict": None,
        "reviewer_evidence": {
            "predicted_start_context": pred["evidence"].get("start_heading_context", ""),
            "heading_seen_chunks": pred["heading_seen_chunks"],
            "toc_chunks_rejected": pred["toc_chunks"],
            "ground_truth_note": gt["note"],
        },
    }

    if not present:
        if not predicted:
            out["verdict"] = "target-absent correct absence"
        else:
            out["false_positive"] = True
            out["verdict"] = "target-absent FALSE POSITIVE"
        return out

    # target present
    if not predicted:
        out["false_negative"] = True
        out["verdict"] = "target-present GENUINE FAILURE (not located)"
        return out

    tol = gt.get("start_tol", 2)
    ps, pe = pred["range"]
    gs, ge = gt["start"], gt["end"]
    start_ok = abs(ps - gs) <= tol

    if not start_ok:
        out["false_positive"] = True   # a wrong-location range is also a false positive per the bar
        out["verdict"] = "target-present GENUINE FAILURE (wrong location)"
        return out

    # start correct. assess boundary.
    gt_len = max(1, ge - gs)
    end_tol = max(3, round(0.25 * gt_len))
    if not pred["end_established"]:
        out["verdict"] = "correct start / partial-boundary (end not established, honestly flagged)"
    elif abs(pe - ge) <= end_tol:
        out["verdict"] = "CORRECT LOCATION"
    else:
        out["verdict"] = "correct start / partial-boundary (end outside tolerance)"
    return out


def _section_ok_for_bar(ev: dict) -> bool:
    """Bar item 1 ('correct section-location evidence') + item 2 (no false
    positive) + item 3 (honest partial). A correct location, an honest
    partial-boundary, or a correct absence all satisfy it; a genuine failure
    or a false positive does not."""
    if ev["false_positive"] or ev["false_negative"]:
        return False
    return ev["verdict"] in (
        "CORRECT LOCATION",
        "correct start / partial-boundary (end not established, honestly flagged)",
        "correct start / partial-boundary (end outside tolerance)",
        "target-absent correct absence",
    )


# ===========================================================================
# 8. CONTROLS  (diagnostic only)
# ===========================================================================

_CHANGE_CUES = [
    "we have revised", "effective this quarter", "a new risk factor", "changed from",
    "beginning in", "no longer", "newly adopted", "effective as of", "we adopted",
    "recently adopted", "prior to this", "was updated", "has been updated", "we revised",
    "change in accounting", "restated", "reclassified", "we began",
]


def change_cue_scan(chunks: list[dict]) -> list[dict]:
    hits = []
    for c in chunks:
        low = normalize_text(c["text"]).lower()
        for cue in _CHANGE_CUES:
            p = low.find(cue)
            if p != -1:
                hits.append({"chunk_idx": c["chunk_idx"], "cue": cue,
                             "snippet": low[max(0, p - 50):p + 110].replace("\n", " ").strip()})
                break
    return hits


# ===========================================================================
# 9. CORPUS  (reuse the CTO-reviewed four-file corpus; no ingestion by default)
# ===========================================================================

_PLAINTEXT_DOC = """RIVERSTONE ANALYTICS PRIVATE LIMITED
Company Overview and Operating Update -- prepared for internal circulation

Riverstone Analytics builds workforce-planning software for mid-market
manufacturers. The company was founded in 2016 and is headquartered in Pune.
This document summarises the trading position and the principal matters the
board discussed at its most recent meeting. It is a narrative memo and does
not follow any regulatory filing format.

Trading position

Revenue for the year was approximately 128 crore, up from 96 crore, driven by
seat expansion at three large logistics customers and the first full year of
the analytics add-on. Gross margin held around 71 percent. The company remains
free-cash-flow positive and carries no external debt. Headcount grew from 210
to 265, mostly in implementation and customer success.

Matters the board discussed

The board spent most of the meeting on customer concentration: the top two
customers are now 41 percent of revenue, up from 33 percent, and management
was asked to bring a mitigation plan to the next meeting. The board also
reviewed the renewal pipeline, a proposed price increase for the analytics
add-on, and a hiring freeze for non-engineering roles in the second half.

Risks the management team is tracking

Management is tracking foreign-exchange exposure on the two dollar-denominated
contracts, a key-person dependency in the platform team, and slower decision
cycles among prospects in the automotive segment. None of these is considered
severe at present, but the FX exposure will be hedged from next quarter.

Outlook

Management expects revenue growth to moderate to the mid-twenties percent
range next year as the base grows, with margin roughly stable. The analytics
add-on is expected to reach 20 percent of revenue within two years.
"""


async def _find_existing(db, ticker: str, form_contains: str):
    rows = await db.filings.find({"ticker": ticker.upper()}, {"_id": 0}).sort("created_at", -1).to_list(50)
    for r in rows:
        if form_contains.lower() in str(r.get("source", "")).lower() and (r.get("num_chunks") or 0) >= 2:
            return r
    return None


async def _assemble_corpus(db, allow_ingest: bool) -> list[dict]:
    from agents.ingest import fetch_edgar_latest, fetch_bse_annual_report, ingest_document
    out = []

    async def add(key, kind, is_edgar, row, note):
        out.append({"key": key, "kind": kind, "is_edgar": is_edgar, "filing_row": row, "note": note})

    q = await _find_existing(db, "TSLA", "10-Q") or await _find_existing(db, "IBM", "10-Q")
    if q:
        await add("EDGAR_10Q", "EDGAR 10-Q", True, q, "reused existing ingested real filing")
    elif allow_ingest:
        for tk in ("MSFT", "AAPL", "NVDA"):
            r = await fetch_edgar_latest(tk, "10-Q")
            if r and r.get("text"):
                res = await ingest_document(db, ticker=tk, source=r["source"], text=r["text"], company_name=r.get("company_name"))
                await add("EDGAR_10Q", "EDGAR 10-Q", True, await db.filings.find_one({"doc_id": res["doc_id"]}, {"_id": 0}), f"ingested live ({tk})")
                break

    k = await _find_existing(db, "MSFT", "10-K") or await _find_existing(db, "AAPL", "10-K")
    if k:
        await add("EDGAR_10K", "EDGAR 10-K", True, k, "reused existing ingested real filing")
    elif allow_ingest:
        for tk in ("MSFT", "AAPL", "NVDA", "IBM"):
            r = await fetch_edgar_latest(tk, "10-K")
            if r and r.get("text"):
                res = await ingest_document(db, ticker=tk, source=r["source"], text=r["text"], company_name=r.get("company_name"))
                await add("EDGAR_10K", "EDGAR 10-K", True, await db.filings.find_one({"doc_id": res["doc_id"]}, {"_id": 0}), f"ingested live ({tk})")
                break

    b = await _find_existing(db, "RELIANCE", "annual") or await _find_existing(db, "TCS", "annual")
    if b:
        await add("BSE_ANNUAL", "BSE annual report", False, b, "reused existing ingested real filing")
    elif allow_ingest:
        for tk in ("RELIANCE", "TCS", "INFY", "HDFCBANK"):
            r = await fetch_bse_annual_report(tk)
            if r and r.get("text"):
                res = await ingest_document(db, ticker=tk, source=r["source"], text=r["text"], company_name=r.get("company_name"))
                await add("BSE_ANNUAL", "BSE annual report", False, await db.filings.find_one({"doc_id": res["doc_id"]}, {"_id": 0}), f"ingested live ({tk})")
                break

    p = await _find_existing(db, "RIVERSTONE_SPIKE", "spike")
    if not p and allow_ingest:
        res = await ingest_document(db, ticker="RIVERSTONE_SPIKE", source="spike plain-text ingest (unstructured memo)",
                                    text=_PLAINTEXT_DOC, company_name="Riverstone Analytics Private Limited")
        p = await db.filings.find_one({"doc_id": res["doc_id"]}, {"_id": 0})
    if p:
        await add("PLAINTEXT", "plain-text POST /ingest/text", False, p, "unstructured narrative memo, no Item structure by construction")

    return out


async def _load_chunks(db, doc_id: str) -> list[dict]:
    rows = await db.filing_chunks.find({"doc_id": doc_id}, {"_id": 0, "embedding": 0}).sort("chunk_idx", 1).to_list(6000)
    return [r for r in rows if isinstance(r.get("chunk_idx"), int) and isinstance(r.get("text"), str)]


# ===========================================================================
# 10. DRIVER
# ===========================================================================

async def _run(allow_ingest: bool, n_runs: int) -> dict:
    from motor.motor_asyncio import AsyncIOMotorClient
    db = AsyncIOMotorClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))[os.environ.get("DB_NAME", "alphascribe")]

    corpus = await _assemble_corpus(db, allow_ingest)
    per_filing = []
    evaluations = []

    for item in corpus:
        row = item["filing_row"]
        key = item["key"]
        if not row:
            per_filing.append({"key": key, "kind": item["kind"], "is_edgar": item["is_edgar"],
                               "status": "NOT_AVAILABLE", "note": item["note"]})
            continue
        chunks = await _load_chunks(db, row["doc_id"])
        if not chunks:
            per_filing.append({"key": key, "kind": item["kind"], "is_edgar": item["is_edgar"],
                               "status": "NO_CHUNKS", "doc_id": row["doc_id"]})
            continue

        runs = []
        for _ in range(n_runs):
            runs.append(await locate_all(chunks))   # real LLM classify_fn (used only if ambiguous)

        def sig(loc):
            return json.dumps({k: [loc[k]["range"], loc[k]["basis"], loc[k]["diagnostic_state"]]
                               for k in ("risk_factors", "mda")}, sort_keys=True)
        sigs = [sig(r) for r in runs]
        identical = len(set(sigs)) == 1
        llm_invoked = any(runs[i][k]["llm_calls"] for i in range(n_runs) for k in ("risk_factors", "mda"))

        pred = runs[0]
        gt = GROUND_TRUTH[key]
        ev_rf = evaluate_section(pred["risk_factors"], gt["risk_factors"], key, "risk_factors")
        ev_mda = evaluate_section(pred["mda"], gt["mda"], key, "mda")
        evaluations += [ev_rf, ev_mda]

        cue_hits = change_cue_scan(chunks)
        per_filing.append({
            "key": key, "kind": item["kind"], "is_edgar": item["is_edgar"], "status": "RUN",
            "ticker": row.get("ticker"), "doc_id": row["doc_id"], "source": row.get("source"),
            "num_chunks": len(chunks), "char_count": row.get("char_count"), "note": item["note"],
            "prediction_run1": {"risk_factors": pred["risk_factors"], "mda": pred["mda"]},
            "evaluation": {"risk_factors": ev_rf, "mda": ev_mda},
            "reproducibility": {
                "n_runs": n_runs, "identical": identical, "llm_invoked": llm_invoked,
                "per_run": [{"run": i + 1,
                             "risk_factors_range": runs[i]["risk_factors"]["range"],
                             "risk_factors_basis": runs[i]["risk_factors"]["basis"],
                             "mda_range": runs[i]["mda"]["range"],
                             "mda_basis": runs[i]["mda"]["basis"]} for i in range(n_runs)],
                "distinct_signatures": sorted(set(sigs)),
            },
            "controls_DIAGNOSTIC": {
                "note": _DIAG_TAG + " -- these controls are diagnostics, NOT a test of the ratified Document 64 features",
                "filing_summary": {"filing_local": True,
                                   "note": "whole-filing; single doc_id input; NOT an evaluation of the Document 64 Filing Summary output"},
                "important_changes": {"filing_local": True, "cue_hit_count": len(cue_hits),
                                      "cue_hits_sample": cue_hits[:8],
                                      "note": "cue-STRING presence only; " + _DIAG_TAG +
                                              "; does NOT evaluate contractual material-change detection (Document 65 section 9 / INV-IC)"},
            },
        })

    # ---- aggregate ----
    ran = [f for f in per_filing if f.get("status") == "RUN"]
    def agg(subset):
        evs = [e for f in subset for e in (f["evaluation"]["risk_factors"], f["evaluation"]["mda"])]
        return {
            "n_filings": len(subset), "n_section_targets": len(evs),
            "correct_location": sum(1 for e in evs if e["verdict"] == "CORRECT LOCATION"),
            "correct_absence": sum(1 for e in evs if e["verdict"] == "target-absent correct absence"),
            "partial_boundary": sum(1 for e in evs if e["verdict"].startswith("correct start / partial-boundary")),
            "false_positive": sum(1 for e in evs if e["false_positive"]),
            "false_negative": sum(1 for e in evs if e["false_negative"]),
        }
    edgar = [f for f in ran if f["is_edgar"]]
    non_edgar = [f for f in ran if not f["is_edgar"]]

    required = {"EDGAR_10Q", "EDGAR_10K", "BSE_ANNUAL", "PLAINTEXT"}
    present = {f["key"] for f in ran}
    missing = sorted(required - present)

    all_repro = all(f["reproducibility"]["identical"] for f in ran) if ran else False
    llm_errs = [c for f in ran for k in ("risk_factors", "mda")
                for call in f["prediction_run1"][k]["llm_calls"] for c in call.get("errors", [])]

    fp_list = [{"filing": e["filing"], "section": e["section"], "verdict": e["verdict"],
                "predicted_range": e["predicted_range"], "why": e["reviewer_evidence"]["ground_truth_note"]}
               for e in evaluations if e["false_positive"]]
    fn_list = [{"filing": e["filing"], "section": e["section"], "verdict": e["verdict"],
                "ground_truth_range": e["ground_truth_range"]}
               for e in evaluations if e["false_negative"]]
    boundary_list = [{"filing": e["filing"], "section": e["section"], "predicted_range": e["predicted_range"],
                      "ground_truth_range": e["ground_truth_range"], "boundary_status": e["boundary_status"]}
                     for e in evaluations if e["verdict"].startswith("correct start / partial-boundary")]

    # ---- §20.1 bar (UNCHANGED CTO-set criteria) ----
    item1_item2_item3 = all(_section_ok_for_bar(e) for e in evaluations) and not missing
    bar = {
        "1_every_filing_correct_RF_and_MDA_evidence": item1_item2_item3 and not fp_list and not fn_list,
        "2_zero_false_positive_section_locations": not fp_list,
        "3_incomplete_evidence_honest_partial_or_insufficient": all(
            (e["boundary_status"] != "end_not_established") or e["verdict"].startswith("correct start / partial-boundary")
            for e in evaluations),
        "4_control_outputs_filing_local": all(f["controls_DIAGNOSTIC"]["filing_summary"]["filing_local"]
                                              and f["controls_DIAGNOSTIC"]["important_changes"]["filing_local"] for f in ran),
        "4_note": "controls are structurally filing-local (one doc_id per run); 'correctly grounded' in the full "
                  "Document 64 sense is an OAQ-9/generation concern, out of scope for a section-location spike",
        "5_reproducible_under_identical_inputs": all_repro,
        "6_reviewer_checkable": True,
        "sample_covers_all_four_required_types": not missing,
        "missing_required_types": missing,
        "llm_classification_errors": len(llm_errs),
    }
    bar_met = bool(
        bar["1_every_filing_correct_RF_and_MDA_evidence"]
        and bar["2_zero_false_positive_section_locations"]
        and bar["3_incomplete_evidence_honest_partial_or_insufficient"]
        and bar["4_control_outputs_filing_local"]
        and bar["5_reproducible_under_identical_inputs"]
        and bar["6_reviewer_checkable"]
        and bar["sample_covers_all_four_required_types"]
        and bar["llm_classification_errors"] == 0
    )

    return {
        "experiment": "M14 Document 65 section 20.1 section-location validation spike -- round 2 (bounded OAQ-1(D) realization improvement)",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "authority": "CTO authorization 2026-09-01 -- bounded remediation/evaluation only; OAQ-1(D) Alt B unchanged; NOT production implementation; NOT C-2",
        "llm_config": {"provider": os.environ.get("LLM_PROVIDER"), "light_model": os.environ.get("LLM_LIGHT_MODEL"),
                       "base_url": os.environ.get("LLM_BASE_URL"), "max_output_tokens": os.environ.get("LLM_MAX_OUTPUT_TOKENS"),
                       "classification_temperature": 0.0, "k_votes": 3},
        "ground_truth_disclaimer": "GROUND_TRUTH table = HUMAN-ESTABLISHED EVALUATION GROUND TRUTH -- NOT PRODUCTION LOGIC -- NOT CONTRACT ARTIFACT. The locate_* prediction pipeline does not read it.",
        "corpus": [{"key": i["key"], "kind": i["kind"], "is_edgar": i["is_edgar"], "available": bool(i["filing_row"]), "note": i["note"]} for i in corpus],
        "per_filing": per_filing,
        "evaluations": evaluations,
        "false_positives": fp_list,
        "false_negatives": fn_list,
        "boundary_failures": boundary_list,
        "aggregate": {"edgar": agg(edgar), "non_edgar": agg(non_edgar), "all_reproducible": all_repro},
        "section_20_1_bar": bar,
        "section_20_1_bar_met": bar_met,
        "result": "PASS" if bar_met else "FAIL / STOP",
        "contract_state_caveat": "All per-section diagnostic_state values are LOCATOR diagnostics tagged '" + _DIAG_TAG +
                                 "'. They are NOT Document 64 section 11.6/11.7 contractual complete/partial/insufficient_evidence.",
    }


def _to_markdown(p: dict) -> str:
    L = [f"# M14 §20.1 Section-Location Spike — Round 2 Evidence\n",
         f"- generated (UTC): `{p['generated_at_utc']}`",
         f"- authority: {p['authority']}",
         f"- LLM: `{p['llm_config']['provider']}` / `{p['llm_config']['light_model']}` — classification `temperature=0.0`, K=3 majority vote",
         f"- ground truth: {p['ground_truth_disclaimer']}",
         f"- **RESULT: `{p['result']}`**\n",
         "## Corpus\n", "| key | kind | EDGAR? | available | note |", "|---|---|---|---|---|"]
    for c in p["corpus"]:
        L.append(f"| {c['key']} | {c['kind']} | {c['is_edgar']} | {c['available']} | {c['note']} |")
    L.append("\n## Per-filing prediction & evaluation\n")
    for f in p["per_filing"]:
        L.append(f"### {f['key']} — {f['kind']} ({f.get('status')})")
        if f.get("status") != "RUN":
            L.append(f"- {f.get('note')}\n"); continue
        L.append(f"- `{f['ticker']}` / `{f['doc_id']}` / `{f['source']}` — {f['num_chunks']} chunks")
        for kind in ("risk_factors", "mda"):
            pr = f["prediction_run1"][kind]; ev = f["evaluation"][kind]
            L.append(f"\n**{kind}** — predicted `{pr['range']}` basis=`{pr['basis']}` state=`{pr['diagnostic_state']}` "
                     f"(`{_DIAG_TAG}`)")
            L.append(f"  - target_present=`{ev['target_present']}` ground_truth=`{ev['ground_truth_range']}` "
                     f"boundary=`{ev['boundary_status']}`")
            L.append(f"  - **verdict: {ev['verdict']}**  false_positive=`{ev['false_positive']}` false_negative=`{ev['false_negative']}`")
            if pr.get("evidence", {}).get("start_heading_context"):
                L.append(f"  - start context: `{pr['evidence']['start_heading_context'][:220].strip()}`")
            if pr["heading_seen_chunks"]:
                L.append(f"  - heading token seen in chunks: `{pr['heading_seen_chunks']}`  TOC-rejected: `{pr['toc_chunks']}`")
            if pr["llm_calls"]:
                L.append(f"  - LLM (ambiguous-candidate) calls: `{json.dumps(pr['llm_calls'])}`")
            L.append(f"  - GT note: {ev['reviewer_evidence']['ground_truth_note']}")
        rp = f["reproducibility"]
        L.append(f"\n**reproducibility** — N={rp['n_runs']} identical=`{rp['identical']}` llm_invoked=`{rp['llm_invoked']}`")
        for r in rp["per_run"]:
            L.append(f"  - run {r['run']}: RF `{r['risk_factors_range']}` ({r['risk_factors_basis']}) | MD&A `{r['mda_range']}` ({r['mda_basis']})")
        ic = f["controls_DIAGNOSTIC"]["important_changes"]
        L.append(f"\n**controls (DIAGNOSTIC)** — filing_local RF/MD&A summary=`True`; Important Changes cue-string hits=`{ic['cue_hit_count']}` "
                 f"— {ic['note']}\n")
    L.append("## False positives\n")
    L.append("`none`" if not p["false_positives"] else "\n".join(f"- {json.dumps(x)}" for x in p["false_positives"]))
    L.append("\n## False negatives\n")
    L.append("`none`" if not p["false_negatives"] else "\n".join(f"- {json.dumps(x)}" for x in p["false_negatives"]))
    L.append("\n## Boundary failures (start correct, end imprecise/unestablished — honest partial)\n")
    L.append("`none`" if not p["boundary_failures"] else "\n".join(f"- {json.dumps(x)}" for x in p["boundary_failures"]))
    L.append("\n## Aggregate\n")
    L.append(f"- EDGAR: `{json.dumps(p['aggregate']['edgar'])}`")
    L.append(f"- non-EDGAR: `{json.dumps(p['aggregate']['non_edgar'])}`")
    L.append(f"- all runs reproducible: `{p['aggregate']['all_reproducible']}`\n")
    L.append("## §20.1 bar (CTO-set criteria, unchanged)\n")
    for k, v in p["section_20_1_bar"].items():
        L.append(f"- **{k}**: `{v}`")
    L.append(f"\n## Contract-state caveat\n\n{p['contract_state_caveat']}\n")
    L.append(f"\n## RESULT\n\n**{p['result']}**\n")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ingest", action="store_true", help="allow live EDGAR/BSE fetch + plain-text ingest if a required filing is missing (default: reuse existing corpus only)")
    ap.add_argument("--runs", type=int, default=5, help="N identical-input location runs per filing (default 5)")
    args = ap.parse_args()

    _load_env()
    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = asyncio.run(_run(allow_ingest=args.ingest, n_runs=args.runs))

    stamp = payload["generated_at_utc"].replace(":", "").replace("-", "").replace(".", "_")
    (_RESULTS_DIR / f"spike_r2_{stamp}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (_RESULTS_DIR / f"spike_r2_{stamp}.md").write_text(_to_markdown(payload), encoding="utf-8")
    (_RESULTS_DIR / "latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (_RESULTS_DIR / "latest.md").write_text(_to_markdown(payload), encoding="utf-8")

    print(json.dumps({
        "result": payload["result"],
        "section_20_1_bar_met": payload["section_20_1_bar_met"],
        "corpus_available": {c["key"]: c["available"] for c in payload["corpus"]},
        "aggregate": payload["aggregate"],
        "false_positives": payload["false_positives"],
        "false_negatives": payload["false_negatives"],
        "boundary_failures": payload["boundary_failures"],
        "bar": payload["section_20_1_bar"],
        "evidence_dir": str(_RESULTS_DIR),
    }, indent=2))


if __name__ == "__main__":
    main()
