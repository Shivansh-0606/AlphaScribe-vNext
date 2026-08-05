"""Contract test: every request-body Pydantic model's REQUIRED field set must
exactly match the corresponding frozen frontend Zod schema
(web/features/*/integration/schemas.ts). This is the class of bug 02 F-1
identified as the most likely implementation mistake (a handler returning/
requiring a different envelope than the frontend validates at the trust
boundary) — the Learning routes don't exist yet, but the mechanism that would
have caught that mistake belongs in Phase 0, before any handler is written.

Deterministic, not brittle: an added OPTIONAL field on either side never
breaks this test — only a required-field mismatch does, which is exactly the
signal that would break `apiFetch`'s trust-boundary validation in production.

    python -m pytest backend/tests/contract/test_request_schemas.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_contract_test")

import server  # noqa: E402

# name -> required fields, transcribed from web/features/*/integration/schemas.ts.
# Zod's z.object({...}) with no `.optional()`/`.default()` on a field == required.
EXPECTED_REQUIRED = {
    "LoginRequest": {"email", "password"},                      # account-setup/schemas.ts
    "RegisterRequest": {"email", "password"},
    "ChangePasswordRequest": {"current_password", "new_password"},
    "DeleteAccountRequest": {"email"},
    "ForgotPasswordRequest": {"email"},
    "ResetPasswordRequest": {"email", "otp", "new_password"},
    "GenerateRequest": {"ticker", "query"},                     # company-research/schemas.ts
    "CompareRequest": {"report_ids"},
    "IngestTextRequest": {"ticker", "source", "text"},
    "IngestEdgarRequest": {"ticker"},                           # form_type has a Zod .default()
    "ValidateLlmKeyRequest": {"provider", "api_key"},           # llm-schemas.ts
    "ExplainRequest": {"ticker", "concept"},                    # learning/schemas.ts explainRequestSchema
}


def _components():
    return server.app.openapi()["components"]["schemas"]


def test_every_expected_model_still_exists():
    components = _components()
    missing = set(EXPECTED_REQUIRED) - set(components)
    assert not missing, f"request models removed or renamed: {sorted(missing)}"


def test_required_fields_match_the_frozen_frontend_schema():
    components = _components()
    mismatches = []
    for model, expected in EXPECTED_REQUIRED.items():
        actual = set(components[model].get("required", []))
        if actual != expected:
            mismatches.append(f"{model}: backend requires {sorted(actual)}, "
                               f"frontend contract requires {sorted(expected)}")
    assert not mismatches, "\n".join(mismatches)


if __name__ == "__main__":
    test_every_expected_model_still_exists()
    test_required_fields_match_the_frozen_frontend_schema()
    print("ok: every request model's required fields match the frozen frontend Zod schema")
