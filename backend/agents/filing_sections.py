"""M14 Filing Analysis -- analysis-time section location (Document 65 OAQ-1(D)
Alternative B): deterministic heuristic heading detection over the EXISTING
unstructured `filing_chunks`, bounded section-range location, and -- ONLY for a
genuinely ambiguous heuristic candidate -- a short K=3 majority-vote LLM
classification pass with conservative disagreement handling.

This module is the production home of the realization that CLEARED the Document
65 section 20.1 STOP/CONTINUE validation gate on 2026-09-01 (PASS: 0 false
positives, 0 false negatives, N=5 reproducible). The gate harness
`backend/scripts/m14_section_location_spike.py` and its unit tests import from
here, so the §20.1 evidence exercises this exact code.

What this module does NOT do (Document 65 section 23 / Document 66):
  * no persisted section store, no ingest change, no `chunk_text` change;
  * no sparse-probe / min(probe)..max(probe) range fabrication;
  * no semantic-similarity -> formal-section-identity conversion;
  * no treating table-of-contents entries as substantive sections;
  * no C-2 / structured-section extraction.

Known limitation carried from the §20.1 evidence: for a section whose start is
located but whose END cannot be structurally established (no next-section
heading, no running header), the range conservatively collapses to
[start, start] with `end_established = False` and `diagnostic_state =
"located_partial_boundary"`. Callers must surface that honestly as `partial`
(Document 64 section 11.7), never as `complete`.
"""
from __future__ import annotations

import html
import re
from collections import Counter

# ponytail: the §20.1 PASS behind this realization is a bounded deterministic
# check -- 4 hand-picked filings (EDGAR 10-K / 10-Q, BSE annual, plain text),
# N=5 repeat runs, 0 FP / 0 FN -- NOT a statistical accuracy claim over the
# filing population. Heading shapes outside that corpus can still mis-locate;
# the conservative fallbacks (collapse to [start,start], defer to `partial`)
# bound the damage but do not eliminate it. Upgrade path: a larger labelled
# corpus + a tracked precision/recall gate before any "generally validated"
# claim.

# `diagnostic_state` values below are LOCATOR diagnostics -- NOT Document 64
# section 11.6/11.7 contractual complete/partial/insufficient_evidence. The
# analysis layer (agents/filing_analysis.py) maps grounding results to the
# contract states; it does not reuse these strings on the wire.
LOCATOR_DIAGNOSTIC_NOTE = "locator diagnostic -- not a Document 64 output state"

# ===========================================================================
# 1. NORMALIZATION  (pure, deterministic, stdlib only)
# ===========================================================================

_PUNCT_MAP = {
    "’": "'", "‘": "'", "‛": "'", "ʼ": "'",
    "“": '"', "”": '"', "„": '"',
    "–": "-", "—": "-", "−": "-",
    "\xa0": " ", " ": " ", " ": " ", " ": " ", " ": " ",
    "﻿": "", "​": "",
    "…": "...",
}


def normalize_text(raw: str) -> str:
    """Decode HTML entities, fold Unicode punctuation, collapse whitespace.

    Deterministic. Changes only the representation the detector reads -- it
    does NOT touch `agents/ingest.py::_clean_html`, persisted chunks, or any
    other consumer of `filing_chunks`.
    """
    if not raw:
        return ""
    t = html.unescape(raw)                       # &#8217; -> ' ; &#160; -> \xa0 ; &amp; -> &
    for k, v in _PUNCT_MAP.items():
        t = t.replace(k, v)
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"[ \t\f\v]+", " ", t)
    t = re.sub(r" *\n *", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


# ===========================================================================
# 2. HEADING PATTERNS  (searched over normalized text; position/context checked
#    separately -- NOT line-anchored)
# ===========================================================================

# "RISK FACTORS" tolerant of the "RIS K FACTORS" artifact (a stripped inline
# tag left a space inside the word).
_RISK_FACTORS = r"r\s?i\s?s\s?k\s+factors"
_MDNA = r"management'?s?\s+discussion\s+and\s+analysis"   # possessive OR not

_RF_HEAD = re.compile(
    rf"\bitem\s*1a\b[.\s:)\-]*{_RISK_FACTORS}\b"      # "Item 1A. Risk Factors"
    rf"|(?<![A-Za-z])(?<!\")\b{_RISK_FACTORS}\b",     # bare "Risk Factors" heading
    re.I,
)
_MDA_HEAD = re.compile(
    rf"\bitem\s*[27]\b[.\s:)\-]*{_MDNA}"              # "Item 2./7. Management('s) D&A"
    rf"|(?<![A-Za-z])(?<!\"){_MDNA}",                 # bare heading
    re.I,
)
_ITEM_TOKEN = re.compile(r"\b(item\s+\d+[ab]?|part\s+[ivx]+)\b", re.I)
# token -> title phrase (>=1 non-Item/Part capitalised word) -> page number.
# Guards against counting the "N" in "PART II Item N" as a page number.
_ITEM_TOKEN_PAGED = re.compile(
    r"\b(?:item\s+\d+[ab]?|part\s+[ivx]+)\b[.\s:)\-]*"
    r"(?:(?!item\b|part\b)[A-Za-z]{2,}[ ,'&/()\-]+){1,8}\d{1,3}(?=\s|$)", re.I)
_TEXT_THEN_PAGE = re.compile(r"[A-Za-z][A-Za-z ,'&/\-]{4,60}?\s\d{1,3}(?=\s+[A-Z(])")

_CROSSREF_AFTER = re.compile(
    r"^[\s,;'\"\)]*\(?\s*(?:part\s+[ivx]+|see\b)"          # "(Part II ...", "see ..."
    r"|^[\s,;'\"\)]{0,4}\(part\s+[ivx]+",
    re.I,
)
_OF_THIS_FORM = re.compile(r"\bof\s+this\s+form\s*10-?[kq]\b", re.I)


# ===========================================================================
# 3. TOC / SUBSTANTIVE-HEADING DISCRIMINATION  (pure, deterministic)
# ===========================================================================

def is_toc_chunk(norm: str) -> bool:
    """A navigation / table-of-contents chunk -- its heading mentions are not
    section locations."""
    if not norm:
        return False
    if len(_ITEM_TOKEN_PAGED.findall(norm)) >= 3:
        return True
    if len(_TEXT_THEN_PAGE.findall(norm)) >= 4:
        return True
    distinct = {m.group(0).lower() for m in _ITEM_TOKEN.finditer(norm)}
    if len(distinct) >= 6:
        return True
    return False


_MDNA_TITLE_TAIL = re.compile(
    r"^\s*of\s+financial\s+condition(\s+and\s+results\s+of\s+operations)?", re.I)


def _prose_follows(after: str) -> bool:
    """True if `after` begins the running SECTION BODY -- a real sentence in
    mostly-lowercase prose -- rather than a heading title-tail followed by a
    page number and the next Item (a table-of-contents line), a quoted
    cross-reference, or another heading."""
    body = _MDNA_TITLE_TAIL.sub("", after).lstrip()   # skip the MD&A title-tail
    if not body:
        return False
    if body[0] in "\"')]}0123456789":
        return False
    if _CROSSREF_AFTER.match(body):
        return False
    if re.match(r"^(item\s*\d|part\s+[ivx]+\b)", body, re.I):
        return False
    window = body[:220]
    # "<page number> Item 3" / "<page number> Part II" -> a contents-page line
    if re.search(r"\b\d{1,3}\s+(item\s+\d|part\s+[ivx]+)\b", window, re.I):
        return False
    words = re.findall(r"[A-Za-z]{2,}", window)
    if len(words) < 6:
        return False
    lower_first = sum(1 for w in words if w[0].islower())
    return lower_first / len(words) >= 0.4      # section body prose is mostly lowercase


def is_substantive(norm: str, m: "re.Match", kind: str) -> bool:
    """The heading match is the real section occurrence, not a quoted /
    parenthetical cross-reference and not a bare TOC line."""
    start, end = m.span()
    before = norm[max(0, start - 40):start]
    after = norm[end:end + 200]

    # Reject "... in "Risk Factors" (Part I, Item 1A of this Form 10-K) ..."
    if _OF_THIS_FORM.search(norm[start:end + 90]):
        return False
    prev_ch = norm[start - 1] if start > 0 else ""
    next_ch = norm[end] if end < len(norm) else ""
    if prev_ch in ('"', "'") or next_ch in ('"', "'"):
        return False
    if re.match(r"^[\s,;]{0,3}[\"')]", after):
        return False
    if _CROSSREF_AFTER.match(after):
        return False

    # (a) the match itself carries the Item-number prefix ("ITEM 1A. RISK
    #     FACTORS ...", "ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS ...").
    if re.match(r"\s*item\s*(1a|2|7)\b", m.group(0), re.I) and _prose_follows(after):
        return True

    # (b) a bare heading immediately preceded by the Item-number token.
    item_prefix = {"rf": r"item\s*1a\b[.\s:)\-]*$", "mda": r"item\s*[27]\b[.\s:)\-]*$"}[kind]
    if re.search(item_prefix, before, re.I) and _prose_follows(after):
        return True

    near_start = start <= 220 or len(norm[:start].strip()) < 70
    return bool(near_start and _prose_follows(after))


# ===========================================================================
# 4. K-of-3 LLM classification  (ambiguous heuristic candidates ONLY)
# ===========================================================================

async def llm_classify_once(chunk_text: str) -> dict:
    """One `chat_json` LIGHT classification at temperature 0.0. Returns
    {"label": "risk_factors"|"mda"|"other"|None, "error": str|None}."""
    from pydantic import BaseModel, Field
    from agents.llm import chat_json, DEFAULT_LIGHT_MODEL

    class SectionLabel(BaseModel):
        label: str = Field(description="one of: risk_factors, mda, other")

    try:
        out = await chat_json(
            "You label one text chunk from a company filing by which section it "
            "belongs to. JSON only. label must be exactly one of: risk_factors, mda, other.",
            f"CHUNK:\n{chunk_text[:1600]}\n\nWhich section is this chunk part of?",
            SectionLabel, model=DEFAULT_LIGHT_MODEL, temperature=0.0,
        )
        lab = out.label.strip().lower()
        return {"label": lab if lab in ("risk_factors", "mda", "other") else "other", "error": None}
    except Exception as e:  # noqa: BLE001
        return {"label": None, "error": f"{type(e).__name__}: {str(e)[:200]}"}


async def classify_kv(chunk_text: str, classify_fn=None, k: int = 3) -> dict:
    """K classifications, majority vote. Disagreement (no strict majority) or a
    non-matching majority is resolved CONSERVATIVELY by the caller -- this
    function only reports; it never expands a range."""
    fn = classify_fn or llm_classify_once
    votes = []
    for _ in range(k):
        votes.append(await fn(chunk_text))
    labels = [v.get("label") for v in votes]
    counts = Counter(l for l in labels if l)
    majority, majority_n = (counts.most_common(1)[0] if counts else (None, 0))
    strict = majority is not None and majority_n * 2 > k
    return {
        "votes": labels,
        "majority": majority if strict else None,
        "strict_majority": strict,
        "errors": [v["error"] for v in votes if v.get("error")],
    }


# ===========================================================================
# 5. SECTION LOCATION  (Document 65 OAQ-1(D) Alt B -- deterministic heuristic
#    primary; LLM only for ambiguous heuristic candidates)
# ===========================================================================

_NEXT_KIND_PATTERNS = {
    # section-kind -> regexes that mark a DIFFERENT following section
    "rf": [re.compile(r"\bitem\s*1b\b", re.I), re.compile(r"\bitem\s*1c\b", re.I),
           re.compile(r"\bitem\s*2\b[.\s:)\-]+(properties|unregistered)", re.I),
           re.compile(r"\bitem\s*3\b[.\s:)\-]+(legal|defaults)", re.I),
           re.compile(r"\bunresolved\s+staff\s+comments\b", re.I)],
    "mda": [re.compile(r"\bitem\s*7a\b", re.I), re.compile(r"\bitem\s*8\b[.\s:)\-]+financial", re.I),
            re.compile(r"\bitem\s*3\b[.\s:)\-]+quantitative", re.I),
            re.compile(r"\bitem\s*4\b[.\s:)\-]+controls", re.I),
            re.compile(r"\bquantitative\s+and\s+qualitative\s+disclosures\b", re.I),
            re.compile(r"\bpart\s+ii\b[.\s]+other\s+information", re.I)],
}


def _heading_of_kind(norm: str, kind: str):
    pat = _RF_HEAD if kind == "rf" else _MDA_HEAD
    return pat.search(norm)


def _end_boundary(norm_chunks, start_idx: int, kind: str) -> dict:
    """Return {end, established, rule}. Deterministic. `end` is a LIST INDEX."""
    pat = _RF_HEAD if kind == "rf" else _MDA_HEAD
    nexts = _NEXT_KIND_PATTERNS[kind]

    # rule 1: next DIFFERENT-section heading (may be inside the start chunk itself)
    for j in range(start_idx, len(norm_chunks)):
        seg = norm_chunks[j]
        if j == start_idx:
            hm = pat.search(seg)
            seg_after = seg[hm.end():] if hm else seg
        else:
            seg_after = seg
        if any(p.search(seg_after) for p in nexts):
            end = start_idx if j == start_idx else j - 1
            return {"end": max(start_idx, end), "established": True, "rule": "next-different-heading"}

    # rule 2: a genuine RUNNING HEADER -- THIS section's heading token recurs on
    # >= 3 later chunks. The section ends at the last chunk of that run (allowing
    # gaps between header appearances, since running headers reprint only every
    # few pages). Bounded so a stray later mention cannot over-extend.
    occ = [j for j in range(start_idx + 1, len(norm_chunks))
           if pat.search(norm_chunks[j]) and not is_toc_chunk(norm_chunks[j])]
    if len(occ) >= 3:
        last = start_idx
        for j in occ:
            if j - last <= 20:          # still within the running-header stretch
                last = j
            else:
                break
        if last > start_idx and sum(1 for j in occ if j <= last) >= 3:
            return {"end": last, "established": True, "rule": "running-header-run"}

    # rule 3: cannot establish -> conservative
    return {"end": start_idx, "established": False, "rule": "end-not-established"}


async def locate_section(chunks: list[dict], kind: str, classify_fn=None) -> dict:
    """Locate one section in an ordered list of `{"chunk_idx": int, "text": str}`.

    `kind` in {"rf", "mda"}. Returns a prediction dict:
      predicted_present, range ([start_chunk_idx, end_chunk_idx] | None), basis
      ("structural" | "llm-ambiguous-candidate" | "heading-absent"),
      start_chunk, end_chunk, end_established, boundary_rule, diagnostic_state
      ("located_bounded" | "located_single_chunk" | "located_partial_boundary" |
       "not_located"), heading_seen_chunks, toc_chunks, llm_calls, evidence.
    """
    norm_chunks = [normalize_text(c["text"]) for c in chunks]
    idx_of = [c["chunk_idx"] for c in chunks]

    heading_seen_at: list[int] = []
    substantive_at: list[int] = []
    toc_at: list[int] = []
    for i, seg in enumerate(norm_chunks):
        m = _heading_of_kind(seg, kind)
        if not m:
            continue
        heading_seen_at.append(idx_of[i])
        # A chunk whose heading is followed by real section prose IS a section
        # occurrence, even if the chunk also packs other Item headings (short
        # Part-II items, page footers). is_toc_chunk only classifies chunks
        # that are NOT substantive.
        if is_substantive(seg, m, kind):
            substantive_at.append(i)  # list index, not chunk_idx
        elif is_toc_chunk(seg):
            toc_at.append(idx_of[i])

    llm_calls: list[dict] = []
    basis = None
    start_i = None

    if substantive_at:
        start_i = substantive_at[0]
        basis = "structural"
    elif heading_seen_at:
        # heading token exists but only in TOC / cross-ref positions -> AMBIGUOUS.
        # LLM classifies the best non-TOC candidate chunk(s) only.
        cand_list_idx = [i for i, seg in enumerate(norm_chunks)
                         if _heading_of_kind(seg, kind) and not is_toc_chunk(seg)][:2]
        want = "risk_factors" if kind == "rf" else "mda"
        for li in cand_list_idx:
            kv = await classify_kv(chunks[li]["text"], classify_fn=classify_fn, k=3)
            llm_calls.append({"chunk_idx": idx_of[li], **kv})
            if kv["strict_majority"] and kv["majority"] == want:
                start_i = li
                basis = "llm-ambiguous-candidate"
                break
        # no strict matching majority -> conservative: NOT located, no range.

    if start_i is None:
        return {
            "kind": kind, "predicted_present": False, "range": None,
            "basis": basis or "heading-absent",
            "start_chunk": None, "end_chunk": None, "end_established": None,
            "boundary_rule": None, "diagnostic_state": "not_located",
            "diagnostic_state_note": LOCATOR_DIAGNOSTIC_NOTE,
            "heading_seen_chunks": heading_seen_at[:20], "toc_chunks": toc_at[:20],
            "llm_calls": llm_calls, "evidence": {},
        }

    start_chunk = idx_of[start_i]
    bnd = _end_boundary(norm_chunks, start_i, kind)
    end_chunk = idx_of[bnd["end"]]
    established = bnd["established"]

    if established:
        rng = [start_chunk, end_chunk]
        dstate = ("located_bounded"
                  if end_chunk > start_chunk or bnd["rule"] == "next-different-heading"
                  else "located_single_chunk")
    else:
        rng = [start_chunk, start_chunk]         # conservative collapse
        dstate = "located_partial_boundary"

    m = _heading_of_kind(norm_chunks[start_i], kind)
    head_ctx = norm_chunks[start_i][max(0, m.start() - 20): m.start() + 200].replace("\n", " ")
    return {
        "kind": kind, "predicted_present": True, "range": rng, "basis": basis,
        "start_chunk": start_chunk, "end_chunk": rng[1], "end_established": established,
        "boundary_rule": bnd["rule"], "diagnostic_state": dstate,
        "diagnostic_state_note": LOCATOR_DIAGNOSTIC_NOTE,
        "heading_seen_chunks": heading_seen_at[:20], "toc_chunks": toc_at[:20],
        "llm_calls": llm_calls,
        "evidence": {
            "start_heading_context": head_ctx,
            "start_chunk_first_400": norm_chunks[start_i][:400],
        },
    }


async def locate_all(chunks: list[dict], classify_fn=None) -> dict:
    """Locate Risk Factors and MD&A. Returns {"risk_factors": <pred>, "mda": <pred>}."""
    rf = await locate_section(chunks, "rf", classify_fn=classify_fn)
    mda = await locate_section(chunks, "mda", classify_fn=classify_fn)
    return {"risk_factors": rf, "mda": mda}
