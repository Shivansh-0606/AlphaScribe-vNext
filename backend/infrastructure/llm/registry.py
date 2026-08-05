"""The single provider-dispatch table, fixing 01 D-3.

Before this module: agents/llm.py had TWO independent copies of the
provider→function dispatch chain (`_generate_sync` and `validate_key`'s
inner `_run()`), and they resolved `base_url` DIFFERENTLY —
`_generate_sync` (via `_active()`) consulted the `LLM_BASE_URL` env var as a
fallback; `validate_key` did not. A key validated against
`PROVIDER_BASE_URL[provider]` could then generate against a different
endpoint entirely if an operator had `LLM_BASE_URL` set, silently.

This module does not reimplement the per-provider HTTP calls — it imports
and calls agents.llm's existing `_gen_gemini`/`_gen_anthropic`/
`_gen_openai_compatible` (unchanged, still the only code that talks to a
provider SDK). It supplies the ONE dispatch table and the ONE base_url
resolution function; agents/llm.py's `_generate_sync` and `validate_key` both
now call `dispatch()` instead of each having their own if/elif chain (see
agents/llm.py's own updated docstring on the call sites).

`agents/llm.py` is not moved here — 06 AD-10 schedules that physical move for
Phase 6. This module is new infrastructure the existing module delegates to,
which is exactly the strangler-fig discipline (06 AD-4): a target to migrate
toward, not a big-bang relocation.
"""
from __future__ import annotations

import os

_OPENAI_COMPATIBLE_PROVIDERS = frozenset(
    {"openai", "groq", "openrouter", "deepseek", "mistral", "custom"}
)


def resolve_base_url(provider: str, explicit_base_url: str | None, provider_base_urls: dict) -> str | None:
    """The one base_url resolution rule both call sites now share:
    explicit override > operator's LLM_BASE_URL env var > the provider's
    known built-in URL. Previously only `_generate_sync`'s path (via
    `_active()`) consulted the env var — this is the fix for that
    divergence, not a new precedence rule invented here."""
    return explicit_base_url or os.environ.get("LLM_BASE_URL") or provider_base_urls.get(provider)


def dispatch(
    provider: str,
    system: str,
    user: str,
    model: str,
    key: str,
    base_url: str | None,
    *,
    gen_gemini,
    gen_anthropic,
    gen_openai_compatible,
) -> str:
    """The one place a provider name maps to a call. Adding a provider means
    adding one branch here — not one branch in two different functions.

    The three `gen_*` callables are passed in rather than imported directly,
    so this module has no import-time dependency on agents.llm (which
    WOULD create a cycle: agents/llm.py imports this module to call
    dispatch(); this module must not import agents/llm.py back). Both real
    call sites (agents/llm.py's `_generate_sync` and `validate_key`) pass
    their own existing `_gen_gemini`/`_gen_anthropic`/`_gen_openai_compatible`
    module functions — the actual provider logic is unchanged.
    """
    if provider == "gemini":
        return gen_gemini(system, user, model, key)
    if provider == "anthropic":
        return gen_anthropic(system, user, model, key)
    if provider in _OPENAI_COMPATIBLE_PROVIDERS:
        return gen_openai_compatible(system, user, model, key, base_url)
    raise ValueError(f"Unknown LLM provider: {provider}")
