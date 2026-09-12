"""Contract test: the backend's route surface must exactly match the 31
approved routes enumerated in 02_API_Coverage_Audit.md's API Parity Matrix,
MINUS 1 (`POST /reports/rescore`, removed M9.2 — zero frontend consumers,
zero backend consumers beyond its own tests; see 00_README.md's EQ-2
ratification and 17's B-7 deprecation-candidate finding),
PLUS the 2 additive M2 Phase 1 routes below (GET /health/ready, GET /metrics)
— both were pre-anticipated as approved additions in
docs/backend_engineering/11_ADR_Index.md's "API-contract impact of the whole
set" table (04 §5.3, 10 §4.4), have no frontend consumer, and modify no
existing route — PLUS the 4 Learning routes (M2 Phase L), the one addition
the Implementation Charter's W-4 explicitly anticipates: "only Phase L may
regenerate [this] (4 additive routes)" — PLUS 1 M8 Step 7 route
(`POST /companies/{ticker}/financials/acquire`), the frozen wire contract in
docs/backend_engineering/33_M8_Financials_API_Contract_Review.md's "Amendment
— Financials Acquisition Request Endpoint" section (§1-§17, CTO approved) —
PLUS 4 M9.1 routes (`/reports/compare/explain` and its `{id}`/`{id}/stream`/
`{id}/cancel` siblings). Document 43
(docs/backend_engineering/43_M9_API_Contract_Decision_Pack.md) is
CTO-approved/frozen and defines these four routes at §5 (as are Documents
41/42, the architecture/semantics it implements). Implementation began under
a separate, earlier CTO directive authorizing work against Document 43 while
it was still proposed — this file states Document 43's current status; it is
not the source of that approval.
Every field/path/status shape is transcribed verbatim from the frozen frontend
contract (web/features/learning/integration/schemas.ts) — see
03_Learning_Backend_Design.md §1 — except the M8 addition, transcribed from
Document 33's Amendment section instead (no frontend consumer exists yet,
Document 37 §10), and the M9.1 addition, transcribed from Document 43 §5-§13
instead (no frontend consumer exists yet either — M9.1 is backend-only per its
own CTO authorization).
PLUS 1 M12 route (`GET /companies/{ticker}/financials`), the frozen read
contract in docs/backend_engineering/33_M8_Financials_API_Contract_Review.md
§1-§10 — CTO-ratified 2026-08-24 (Round 7 / M12 Governance Ratification) —
with implementation separately CTO-authorized the same day (M12
Implementation Authorization decision).
PLUS 1 M13 route (`GET /companies/{ticker}/filings/{doc_id}/content`), the
frozen read contract in
docs/backend_engineering/59_M13_Filing_Content_Read_API_Contract.md (OD-1,
CTO-ratified 2026-08-27) with the thin-adapter architecture in
docs/backend_engineering/60_M13_Filing_Content_Reading_Architecture_Decision_Pack.md
(CTO-ratified 2026-08-27) — implementation separately CTO-authorized
2026-08-27 (M13 Implementation Authorization decision).
PLUS 4 M16 routes (Filing Q&A `.../filings/{doc_id}/qa` and its
`{id}`/`{id}/stream`/`{id}/cancel` siblings), the frozen contract in
docs/backend_engineering/87_M16_Filing_QA_API_Contract_Proposal.md §3.1
(Revision 2, CTO-ratified via Documents 88/89/92) and the ratified
architecture in Document 90 (candidate selection as amended by Documents
95/96) — implementation separately CTO-authorized (Document 94 Revision 1,
ratified by Document 97 Revision 1).

This is the automated guard on 06 C-1 ("no approved API contract may change")
— it is deliberately an exact-set assertion, not a fuzzy/partial one: adding,
removing, or renaming a route is a contract change and must fail this test
loudly, with the offending path in the diff, rather than pass silently. It
caught exactly this addition during Phase 1's own development — see
docs/backend_engineering/14_M2_Phase1_Implementation_Report.md.

Deterministic, not a snapshot: the expected set is a literal, reviewable list
transcribed from the approved contract — not a serialized blob that breaks on
any incidental OpenAPI metadata change.

    python -m pytest backend/tests/contract/test_route_inventory.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_contract_test")

import server  # noqa: E402

# Transcribed verbatim from 02_API_Coverage_Audit.md §3 (31 routes), plus the
# 2 approved-additive M2 Phase 1 routes (see the module docstring).
APPROVED_ROUTES = {
    ("GET", "/api/"),
    ("GET", "/api/health"),
    ("GET", "/api/health/ready"),   # M2 Phase 1 — additive, 11's impact table
    ("GET", "/api/metrics"),        # M2 Phase 1 — additive, 11's impact table
    ("POST", "/api/auth/register"),
    ("POST", "/api/auth/login"),
    ("POST", "/api/auth/logout"),
    ("POST", "/api/auth/logout-all"),
    ("GET", "/api/auth/me"),
    ("DELETE", "/api/auth/me"),
    ("POST", "/api/auth/password"),
    ("POST", "/api/auth/forgot-password"),
    ("POST", "/api/auth/reset-password"),
    ("POST", "/api/llm/validate"),
    ("POST", "/api/ingest/text"),
    ("POST", "/api/ingest/edgar"),
    ("POST", "/api/ingest/samples"),
    ("POST", "/api/ingest/audio"),
    ("POST", "/api/ingest/pdf"),
    ("GET", "/api/companies"),
    ("GET", "/api/companies/search"),
    ("POST", "/api/companies/ensure"),
    ("GET", "/api/companies/trending"),
    ("GET", "/api/filings"),
    ("GET", "/api/tickers"),
    ("POST", "/api/reports/generate"),
    ("GET", "/api/reports/{job_id}/stream"),
    ("GET", "/api/reports/{job_id}"),
    ("POST", "/api/reports/{job_id}/cancel"),
    ("GET", "/api/reports"),
    ("DELETE", "/api/reports/{report_id}"),
    ("POST", "/api/reports/compare"),
    ("POST", "/api/learning/explain"),        # M2 Phase L — additive
    ("GET", "/api/learning/{id}/stream"),     # M2 Phase L — additive
    ("GET", "/api/learning/{id}"),            # M2 Phase L — additive
    ("POST", "/api/learning/{id}/cancel"),    # M2 Phase L — additive
    ("POST", "/api/companies/{ticker}/financials/acquire"),  # M8 Step 7 — additive, Document 33 Amendment
    ("GET", "/api/companies/{ticker}/financials"),  # M12 — additive, Document 33 §1-§10 (CTO-ratified Round 7)
    ("POST", "/api/reports/compare/explain"),              # M9.1 — additive, Document 43 §5
    ("GET", "/api/reports/compare/explain/{id}"),           # M9.1 — additive, Document 43 §5/§8
    ("GET", "/api/reports/compare/explain/{id}/stream"),    # M9.1 — additive, Document 43 §5/§17
    ("POST", "/api/reports/compare/explain/{id}/cancel"),   # M9.1 — additive, Document 43 §5/§13
    ("GET", "/api/companies/{ticker}/filings/{doc_id}/content"),  # M13 — additive, Document 59 §3.2/§16 (OD-1, CTO-ratified 2026-08-27) / Document 60
    # M14 Filing Analysis — 4 additive routes, transcribed verbatim from
    # docs/backend_engineering/64_M14_Filing_Analysis_API_Contract.md §9.1
    # (CTO-ratified 2026-08-31) and the ratified route family in Document 65 §13;
    # implementation separately CTO-authorized (M14 Implementation Authorization).
    ("POST", "/api/companies/{ticker}/filings/{doc_id}/analysis"),
    ("GET", "/api/companies/{ticker}/filings/{doc_id}/analysis/{id}"),
    ("GET", "/api/companies/{ticker}/filings/{doc_id}/analysis/{id}/stream"),
    ("POST", "/api/companies/{ticker}/filings/{doc_id}/analysis/{id}/cancel"),
    # M15 — C-4 "What Changed Since Last Review" — 4 additive routes,
    # transcribed verbatim from
    # docs/backend_engineering/70_M15_What_Changed_API_Contract_Proposal.md
    # §10.1 (Revision R4, CTO-ratified 2026-09-06 via Document 72) and the
    # ratified architecture in Document 73 R1 §16; implementation separately
    # CTO-authorized (Document 75, ratified by Document 76).
    ("POST", "/api/companies/{ticker}/changes"),
    ("GET", "/api/companies/{ticker}/changes/{id}"),
    ("GET", "/api/companies/{ticker}/changes/{id}/stream"),
    ("POST", "/api/companies/{ticker}/changes/{id}/cancel"),
    # M16 — Filing Q&A (FQA v1) — 4 additive routes, transcribed verbatim
    # from docs/backend_engineering/87_M16_Filing_QA_API_Contract_Proposal.md
    # §3.1 (Revision 2, CTO-ratified via Documents 88/89/92) and the ratified
    # architecture in Document 90 (candidate selection as amended by
    # Documents 95/96); implementation separately CTO-authorized (Document
    # 94 Revision 1, ratified by Document 97 Revision 1).
    ("POST", "/api/companies/{ticker}/filings/{doc_id}/qa"),
    ("GET", "/api/companies/{ticker}/filings/{doc_id}/qa/{id}"),
    ("GET", "/api/companies/{ticker}/filings/{doc_id}/qa/{id}/stream"),
    ("POST", "/api/companies/{ticker}/filings/{doc_id}/qa/{id}/cancel"),
}

_HTTP_METHODS = {"get", "post", "put", "delete", "patch"}


def _actual_routes() -> set[tuple[str, str]]:
    schema = server.app.openapi()
    return {
        (method.upper(), path)
        for path, methods in schema["paths"].items()
        for method in methods
        if method.lower() in _HTTP_METHODS
    }


def test_route_count_matches_the_approved_contract():
    # 31 approved (02) - 1 removed (M9.2: POST /reports/rescore) + 2 additive
    # M2 Phase 1 (health/ready, metrics) + 4 additive M2 Phase L (Learning)
    # + 1 additive M8 Step 7 (financials acquire) + 4 additive M9.1
    # (comparison explanation, Document 43) + 1 additive M12 (financials read)
    # + 1 additive M13 (filing content read, Documents 59/60)
    # + 4 additive M14 (filing analysis, Documents 64 §9.1 / 65 §13)
    # + 4 additive M15 (change brief, Documents 70 R4 §10.1 / 73 R1 §16)
    # + 4 additive M16 (filing Q&A, Documents 87 R2 §3.1 / 90 / 94 Revision 1).
    assert len(APPROVED_ROUTES) == 55


def test_no_routes_were_added_removed_or_renamed():
    actual = _actual_routes()
    missing = APPROVED_ROUTES - actual
    added = actual - APPROVED_ROUTES
    assert not missing, f"approved routes missing from the live app: {sorted(missing)}"
    assert not added, (
        f"undocumented routes found — either update 02_API_Coverage_Audit.md's "
        f"Parity Matrix (if this is an approved, reviewed addition) or revert "
        f"the change: {sorted(added)}"
    )


def test_rescore_route_removed():
    # M9.2 regression guard: POST /reports/rescore (zero consumers) was
    # deleted, not just left out of APPROVED_ROUTES by omission.
    assert ("POST", "/api/reports/rescore") not in _actual_routes()


if __name__ == "__main__":
    test_route_count_matches_the_approved_contract()
    test_no_routes_were_added_removed_or_renamed()
    test_rescore_route_removed()
    print("ok: live route surface matches the 31 approved - 1 removed (M9.2: rescore) "
          "+ 2 additive M2 Phase 1 + 4 additive M2 Phase L (Learning) + 1 additive M8 "
          "Step 7 (financials acquire) + 4 additive M9.1 (comparison explanation) "
          "+ 1 additive M12 (financials read) + 1 additive M13 (filing content read) "
          "+ 4 additive M14 (filing analysis) + 4 additive M16 (filing Q&A) routes exactly")
