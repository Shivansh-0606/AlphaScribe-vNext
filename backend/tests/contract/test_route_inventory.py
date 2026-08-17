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
    ("POST", "/api/reports/compare/explain"),              # M9.1 — additive, Document 43 §5
    ("GET", "/api/reports/compare/explain/{id}"),           # M9.1 — additive, Document 43 §5/§8
    ("GET", "/api/reports/compare/explain/{id}/stream"),    # M9.1 — additive, Document 43 §5/§17
    ("POST", "/api/reports/compare/explain/{id}/cancel"),   # M9.1 — additive, Document 43 §5/§13
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
    # (comparison explanation, Document 43).
    assert len(APPROVED_ROUTES) == 41


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
          "Step 7 (financials acquire) + 4 additive M9.1 (comparison explanation) routes exactly")
