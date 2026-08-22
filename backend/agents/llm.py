"""Multi-provider LLM wrapper (Gemini / OpenAI / Groq).

Provides `chat_json(...)` for structured Pydantic outputs and `chat_text(...)`
for free-form text. The active provider + API key can be set per-request via a
contextvar (so users can bring their own key in the UI), falling back to
environment variables for local/dev use.

Public surface (`chat_text`, `chat_json`, `DEFAULT_LIGHT_MODEL`,
`DEFAULT_HEAVY_MODEL`) is unchanged for every existing caller, so the agent
nodes need no modification. `chat_text`/`chat_json` gained one additive,
optional `temperature` kwarg (default `None` = each provider's pre-existing
behavior, untouched) for Document 47's model-assisted evaluator — no
existing call site passes it.
"""
from __future__ import annotations
import asyncio
import ipaddress
import json
import os
import re
import socket
import threading
from contextvars import ContextVar
from typing import Type, TypeVar, get_origin, get_args
from urllib.parse import urlparse
from pydantic import BaseModel, ValidationError

# M2 Phase 1 (01 D-3 fix, ADR pending): the one place a provider name maps to
# a call, and the one base_url resolution rule — both _generate_sync and
# validate_key delegate to this instead of each carrying their own duplicated
# if/elif chain. See infrastructure/llm/registry.py's module docstring.
from infrastructure.llm.registry import dispatch as _dispatch_provider
from infrastructure.llm.registry import resolve_base_url as _resolve_base_url
from infrastructure.observability.metrics import llm_calls_total, llm_tokens_total
from infrastructure.observability.tracing import get_tracer

T = TypeVar("T", bound=BaseModel)

# Per-request LLM credentials. Set by the API layer from request headers; falls
# back to environment variables when unset (local dev / .env).
#   {"provider": "gemini"|"openai"|"groq", "api_key": "...",
#    "light_model": "...", "heavy_model": "..."}
_LLM_CTX: ContextVar[dict | None] = ContextVar("_LLM_CTX", default=None)

# Sensible free-tier-friendly defaults per provider.
PROVIDER_DEFAULTS = {
    "gemini":     ("gemini-2.0-flash-lite", "gemini-2.0-flash"),
    "openai":     ("gpt-4o-mini", "gpt-4o"),
    "anthropic":  ("claude-haiku-4-5", "claude-sonnet-4-6"),
    "groq":       ("llama-3.1-8b-instant", "llama-3.3-70b-versatile"),
    "openrouter": ("openai/gpt-4o-mini", "anthropic/claude-sonnet-4.5"),
    "deepseek":   ("deepseek-chat", "deepseek-chat"),
    "mistral":    ("mistral-small-latest", "mistral-large-latest"),
    # any OpenAI-compatible endpoint (aipipe, local LLMs). base_url from request.
    "custom":     ("gpt-4o-mini", "gpt-4o-mini"),
}

# Built-in base URLs for OpenAI-compatible providers.
PROVIDER_BASE_URL = {
    "groq":       "https://api.groq.com/openai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "deepseek":   "https://api.deepseek.com/v1",
    "mistral":    "https://api.mistral.ai/v1",
}

# Symbolic tiers — resolved to a concrete model at call time based on provider.
DEFAULT_LIGHT_MODEL = "__light__"
DEFAULT_HEAVY_MODEL = "__heavy__"


def set_llm_context(provider: str | None, api_key: str | None,
                    light_model: str | None = None, heavy_model: str | None = None,
                    base_url: str | None = None):
    """Set the active provider/key for the current async context. Returns a token
    to reset later. No-op-ish if provider/key missing (falls back to env)."""
    return _LLM_CTX.set({
        "provider": (provider or "").lower() or None,
        "api_key": api_key or None,
        "light_model": light_model or None,
        "heavy_model": heavy_model or None,
        "base_url": base_url or None,
    })


def reset_llm_context(token) -> None:
    try:
        _LLM_CTX.reset(token)
    except Exception:  # noqa: BLE001
        pass


def _active() -> dict:
    """Resolve provider + key + models from context, else environment."""
    ctx = _LLM_CTX.get() or {}
    provider = ctx.get("provider") or os.environ.get("LLM_PROVIDER") or "gemini"
    provider = provider.lower()

    key = ctx.get("api_key")
    if not key:
        env_keys = {
            "gemini": "GEMINI_API_KEY", "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY", "groq": "GROQ_API_KEY",
            "openrouter": "OPENROUTER_API_KEY", "deepseek": "DEEPSEEK_API_KEY",
            "mistral": "MISTRAL_API_KEY",
        }
        key = os.environ.get(env_keys.get(provider, ""))
        if provider == "gemini" and not key:
            key = os.environ.get("GOOGLE_API_KEY")

    d_light, d_heavy = PROVIDER_DEFAULTS.get(provider, PROVIDER_DEFAULTS["gemini"])
    light = ctx.get("light_model") or os.environ.get("LLM_LIGHT_MODEL") or d_light
    heavy = ctx.get("heavy_model") or os.environ.get("LLM_HEAVY_MODEL") or d_heavy
    base_url = ctx.get("base_url") or os.environ.get("LLM_BASE_URL") or PROVIDER_BASE_URL.get(provider)
    return {"provider": provider, "api_key": key, "light": light, "heavy": heavy, "base_url": base_url}


def assert_public_url(url: str) -> None:
    """Raise ValueError unless `url` is an http(s) endpoint on a public host.

    SSRF guard for the client-supplied custom LLM base_url: a caller must not be
    able to point the server's outbound request at loopback/private/link-local/
    reserved addresses (cloud metadata at 169.254.169.254, intranet hosts).
    ponytail: resolves the host once here; a determined attacker could DNS-rebind
    between this check and the SDK's own connect. Pin the resolved IP in the HTTP
    client if that threat ever matters.

    Escape hatch: LLM_ALLOW_PRIVATE_BASE_URL=true in the server's own .env skips
    this check entirely, so a self-hoster can point at a local LLM (Ollama, LM
    Studio, ...). This is an operator-controlled deployment setting, not
    something a client request can flip — only set it for a single-user/local
    instance, since it reopens the SSRF hole for anyone who can reach this API.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("must be an http(s) URL")
    if os.environ.get("LLM_ALLOW_PRIVATE_BASE_URL", "").strip().lower() in ("1", "true", "yes"):
        return
    try:
        infos = socket.getaddrinfo(parsed.hostname, parsed.port,
                                   proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        raise ValueError("host does not resolve") from e
    for *_, sockaddr in infos:
        ip = ipaddress.ip_address(sockaddr[0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            raise ValueError("resolves to a non-public address")


def _resolve_model(model: str, cfg: dict) -> str:
    if model == DEFAULT_LIGHT_MODEL:
        return cfg["light"]
    if model == DEFAULT_HEAVY_MODEL:
        return cfg["heavy"]
    return model


# --------------------------------------------------------------------------
# Provider backends (blocking; run in a thread)
# --------------------------------------------------------------------------
# Guards google.generativeai's process-global configure(). Shared with the
# audio-transcription path in server.py, which uses the same global.
GEMINI_LOCK = threading.Lock()

# Per-call network timeout so a hung provider connection can't tie up a worker
# thread indefinitely (the to_thread executor is shared with PDF/audio work).
_REQUEST_TIMEOUT = float(os.environ.get("LLM_REQUEST_TIMEOUT", "120"))


class NonRetryableLLMError(RuntimeError):
    """A deterministic failure (bad config, truncated output) where retrying just
    burns more calls + backoff for the same result. chat_text re-raises these
    immediately instead of looping."""


def _record_usage(usage_sink: dict | None, *, input_tokens, output_tokens) -> None:
    """M6 token-usage metric: best-effort, never raises — a provider SDK
    changing its usage-field shape must not break generation itself."""
    if usage_sink is None:
        return
    try:
        if input_tokens is not None:
            usage_sink["input_tokens"] = int(input_tokens)
        if output_tokens is not None:
            usage_sink["output_tokens"] = int(output_tokens)
    except Exception:  # noqa: BLE001
        pass


def _gen_gemini(system: str, user: str, model: str, key: str, *, usage_sink: dict | None = None,
                 temperature: float | None = None) -> str:
    import google.generativeai as genai
    # google.generativeai.configure() sets a PROCESS-GLOBAL key, so two
    # concurrent requests with different keys would clobber each other and a
    # call could run under the wrong caller's key (cross-tenant billing/leak).
    # Hold the lock across configure+generate so the key can't change mid-call.
    # ponytail: global lock serializes all Gemini traffic; upgrade path is the
    # newer google-genai SDK whose Client(api_key=...) takes a per-call key.
    # temperature=None (every existing caller) passes no generation_config at
    # all — identical to this function's behavior before Document 47's judge
    # path existed. Only an explicit caller (the judge) gets one.
    gen_config = genai.GenerationConfig(temperature=temperature) if temperature is not None else None
    with GEMINI_LOCK:
        genai.configure(api_key=key)
        gm = genai.GenerativeModel(model_name=model, system_instruction=system)
        resp = gm.generate_content(
            user, request_options={"timeout": _REQUEST_TIMEOUT}, generation_config=gen_config,
        )
    cand = (getattr(resp, "candidates", None) or [None])[0]
    if getattr(getattr(cand, "finish_reason", None), "name", "") == "MAX_TOKENS":
        # Truncated brief — don't let a cut-off draft reach the fact-checker.
        raise NonRetryableLLMError("Gemini output was truncated (MAX_TOKENS).")
    usage = getattr(resp, "usage_metadata", None)
    _record_usage(
        usage_sink,
        input_tokens=getattr(usage, "prompt_token_count", None),
        output_tokens=getattr(usage, "candidates_token_count", None),
    )
    try:
        return resp.text or ""
    except Exception:  # noqa: BLE001
        parts = []
        for cand in getattr(resp, "candidates", []) or []:
            for part in getattr(getattr(cand, "content", None), "parts", []) or []:
                if getattr(part, "text", None):
                    parts.append(part.text)
        return "\n".join(parts)


def _gen_openai_compatible(system: str, user: str, model: str, key: str, base_url: str | None,
                            *, usage_sink: dict | None = None, temperature: float | None = None) -> str:
    # openai>=1.0 SDK; Groq is OpenAI-compatible via base_url.
    from openai import OpenAI
    # max_retries=0: chat_text already owns the retry/backoff loop. The SDK's
    # default (2) multiplies on top of ours — 4 attempts x 3 SDK tries x 120s
    # timeout balloons a hung request to ~24 min before it surfaces.
    client = (OpenAI(api_key=key, base_url=base_url, timeout=_REQUEST_TIMEOUT, max_retries=0)
              if base_url else OpenAI(api_key=key, timeout=_REQUEST_TIMEOUT, max_retries=0))
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        # 0.3 is every existing caller's unchanged default; temperature=None
        # (the default) preserves it exactly. Only an explicit caller (the
        # Document 47 judge) overrides it.
        temperature=temperature if temperature is not None else 0.3,
        # Cap output: without this, OpenRouter reserves the model's max output
        # (e.g. 64K) from your credit balance and 402s on low-credit accounts.
        # The pipeline's largest output (the brief) is prompted to <500 words
        # (~700 tokens), so 2048 leaves ~3x headroom. Raise via env if needed.
        max_tokens=int(os.environ.get("LLM_MAX_OUTPUT_TOKENS", "2048")),
    )
    choice = resp.choices[0]
    if choice.finish_reason == "length":
        # Surface truncation instead of letting a cut-off brief flow into the
        # fact-checker as if it were complete.
        raise NonRetryableLLMError(
            "LLM output was truncated by the max_tokens cap "
            "(LLM_MAX_OUTPUT_TOKENS). Raise it in backend/.env and retry."
        )
    usage = getattr(resp, "usage", None)
    _record_usage(
        usage_sink,
        input_tokens=getattr(usage, "prompt_tokens", None),
        output_tokens=getattr(usage, "completion_tokens", None),
    )
    return choice.message.content or ""


def _gen_anthropic(system: str, user: str, model: str, key: str, *, usage_sink: dict | None = None,
                    temperature: float | None = None) -> str:
    import anthropic
    # max_retries=0 for the same reason as the OpenAI path: chat_text owns retries,
    # the SDK default (2) would compound multiplicatively.
    client = anthropic.Anthropic(api_key=key, timeout=_REQUEST_TIMEOUT, max_retries=0)
    # temperature=None (every existing caller) omits the kwarg entirely, same
    # as before Document 47's judge path existed — the Anthropic SDK's own
    # provider default applies unchanged. Only an explicit caller overrides it.
    extra = {"temperature": temperature} if temperature is not None else {}
    resp = client.messages.create(
        model=model, max_tokens=4096, system=system,
        messages=[{"role": "user", "content": user}],
        **extra,
    )
    if resp.stop_reason == "max_tokens":
        # Same truncation guard as the other providers (was missing here).
        raise NonRetryableLLMError("Anthropic output was truncated (max_tokens=4096).")
    usage = getattr(resp, "usage", None)
    _record_usage(
        usage_sink,
        input_tokens=getattr(usage, "input_tokens", None),
        output_tokens=getattr(usage, "output_tokens", None),
    )
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")


def _generate_sync(system: str, user: str, model: str, *, usage_sink: dict | None = None,
                    temperature: float | None = None) -> str:
    cfg = _active()
    provider, key = cfg["provider"], cfg["api_key"]
    if not key:
        raise NonRetryableLLMError(
            f"No API key for provider '{provider}'. Set it in backend/.env or "
            "paste a key in the app (Settings)."
        )
    real_model = _resolve_model(model, cfg)
    try:
        return _dispatch_provider(
            provider, system, user, real_model, key, cfg["base_url"],
            gen_gemini=_gen_gemini, gen_anthropic=_gen_anthropic,
            gen_openai_compatible=_gen_openai_compatible,
            usage_sink=usage_sink, temperature=temperature,
        )
    except ValueError as e:
        # dispatch() raises ValueError for an unknown provider; this call
        # site's existing contract is RuntimeError (validate_key's contract
        # is ValueError — see below). Preserved so no caller's except clause
        # needs to change.
        raise RuntimeError(str(e)) from e


async def validate_key(provider: str, api_key: str, base_url: str | None = None,
                        model: str | None = None) -> None:
    """Live-validate a BYOK key with a single trivial completion call — no retry
    loop (unlike `chat_text`; a bad key should fail once, not four times with
    backoff), no persistence, no real content generated. Raises on failure
    (invalid key, unreachable provider, unknown provider); returns normally on
    success. Callers turn the raised exception into a `{"valid": False, ...}`
    response rather than an HTTP error — an invalid key is an expected outcome
    of validation, not a server failure.
    """
    provider = (provider or "").strip().lower()
    if not api_key or not api_key.strip():
        raise ValueError("API key is required.")
    d_light, _ = PROVIDER_DEFAULTS.get(provider, PROVIDER_DEFAULTS["gemini"])
    real_model = model or d_light
    # M2 Phase 1 (01 D-3 fix): previously `base_url or PROVIDER_BASE_URL.get(...)`
    # — did not consult LLM_BASE_URL, unlike _generate_sync's resolution via
    # _active(). A key validated against PROVIDER_BASE_URL could then
    # generate against a different endpoint (LLM_BASE_URL) silently. Both
    # call sites now share the exact same resolution function.
    resolved_base_url = _resolve_base_url(provider, base_url, PROVIDER_BASE_URL)
    system, user = "You validate API connectivity.", "Reply with exactly one word: OK"

    def _run() -> str:
        return _dispatch_provider(
            provider, system, user, real_model, api_key, resolved_base_url,
            gen_gemini=_gen_gemini, gen_anthropic=_gen_anthropic,
            gen_openai_compatible=_gen_openai_compatible,
        )

    await asyncio.wait_for(asyncio.to_thread(_run), timeout=_REQUEST_TIMEOUT)


_KEY_PARAM_RE = re.compile(r"(?i)([?&]key=)[^&\s'\"]+")


def redact_key_from_error(err: Exception, api_key: str) -> str:
    """Provider SDK exceptions can embed the raw key (Gemini passes it as a
    `?key=...` URL query param — see server.py's pipeline error handler for the
    same concern). A validation failure message is shown back to the very user
    who submitted the key, but it must never round-trip the key verbatim
    through a response body (or anywhere a log/browser history could capture
    it) — belt-and-suspenders: redact both the literal key substring and any
    `key=...` URL param shape."""
    text = str(err)
    if api_key:
        text = text.replace(api_key, "***REDACTED***")
    return _KEY_PARAM_RE.sub(r"\1***REDACTED***", text)


def _retry_after_seconds(err: Exception) -> float | None:
    m = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", str(err))
    if m:
        return float(m.group(1))
    m = re.search(r"try again in ([\d.]+)s", str(err), re.IGNORECASE)
    return float(m.group(1)) if m else None


_TIER_LABELS = {DEFAULT_LIGHT_MODEL: "light", DEFAULT_HEAVY_MODEL: "heavy"}


async def chat_text(system: str, user: str, *, model: str = DEFAULT_HEAVY_MODEL,
                     temperature: float | None = None) -> str:
    # The one shared call site behind every node's chat_text/chat_json call
    # (chat_json delegates to this) — instrumenting here covers both graphs
    # (report + Learning) without a per-node metrics call.
    cfg = _active()
    labels = {"provider": cfg["provider"], "model": _resolve_model(model, cfg),
              "tier": _TIER_LABELS.get(model, "explicit")}
    last_err: Exception | None = None
    for attempt in range(4):
        # M6 — doc 26 §Trace Coverage's named gap: "individual retry attempts
        # inside chat_text's backoff loop... not traced". Each attempt is now
        # its own child span (nests under whatever span is active when
        # chat_text is called — a node span during a pipeline run), so a
        # provider that's silently retrying shows up as N spans, not one
        # HTTPX span indistinguishable from a single slow call.
        with get_tracer().start_as_current_span(
            "llm.attempt", attributes={"attempt": attempt, **labels}
        ):
            try:
                usage: dict = {}
                result = await asyncio.to_thread(
                    _generate_sync, system, user, model, usage_sink=usage, temperature=temperature,
                )
                llm_calls_total.labels(**labels, outcome="success").inc()
                if usage.get("input_tokens") is not None:
                    llm_tokens_total.labels(provider=labels["provider"], model=labels["model"],
                                             kind="input").inc(usage["input_tokens"])
                if usage.get("output_tokens") is not None:
                    llm_tokens_total.labels(provider=labels["provider"], model=labels["model"],
                                             kind="output").inc(usage["output_tokens"])
                return result
            except NonRetryableLLMError:
                llm_calls_total.labels(**labels, outcome="error").inc()
                raise  # deterministic — retrying wastes calls + backoff
            except Exception as e:  # noqa: BLE001
                llm_calls_total.labels(**labels, outcome="error").inc()  # one per failed attempt, retries visible
                last_err = e
        if attempt == 3:
            break
        wait = _retry_after_seconds(last_err)
        if wait is None:
            wait = 2.0 * (attempt + 1)
        await asyncio.sleep(min(wait, 30.0))
    raise last_err  # type: ignore[misc]


def _type_name(ann) -> str:
    s = str(ann).replace("typing.", "")
    if s.startswith("<class '") and s.endswith("'>"):
        s = s[len("<class '"):-len("'>")]  # e.g. "str", "float"
    return s


def _schema_hint(model: Type[BaseModel], _indent: int = 0) -> str:
    """Readable field spec for the prompt, recursing into nested Pydantic models
    so array-of-object schemas (e.g. FactCheckSchema.claims) show their item fields."""
    pad = "  " * (_indent + 1)
    lines: list[str] = []
    for name, f in model.model_fields.items():
        ann = f.annotation
        origin = get_origin(ann)
        args = get_args(ann)
        req = "required" if f.is_required() else "optional"
        desc = f" - {f.description}" if f.description else ""
        if isinstance(ann, type) and issubclass(ann, BaseModel):
            lines.append(f'{pad}"{name}": object ({req}){desc}, with fields:')
            lines.append(_schema_hint(ann, _indent + 1))
        elif origin in (list, tuple) and args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
            lines.append(f'{pad}"{name}": array ({req}){desc}, each item an object with fields:')
            lines.append(_schema_hint(args[0], _indent + 1))
        else:
            lines.append(f'{pad}"{name}": {_type_name(ann)} ({req}){desc}')
    return "\n".join(lines)


def _strip_code_fence(text: str) -> str:
    """Strip a single fence that wraps the whole string, e.g. ```json / ```markdown."""
    text = text.strip()
    m = re.match(r"^```[a-zA-Z0-9]*\s*\n?(.*?)\n?\s*```$", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text


async def chat_json(
    system: str,
    user: str,
    schema: Type[T],
    *,
    model: str = DEFAULT_LIGHT_MODEL,
    temperature: float | None = None,
) -> T:
    """Ask the LLM for a JSON object and validate it against a Pydantic schema."""
    # Describe the fields directly instead of dumping the JSON Schema. The raw
    # schema (with its own "properties"/"type" keys) tempts weaker models to echo
    # the envelope back, e.g. {"properties": {...}, "type": "object"}.
    guardrail = (
        "\n\nReturn ONLY a single JSON object with exactly these keys "
        "(no wrapper, no \"properties\" key, no schema metadata). "
        "Include every field named below verbatim; do not rename or replace them "
        "with index/id fields. No prose, no markdown fences.\n"
        + _schema_hint(schema)
    )
    # Qwen3 is a hybrid "thinking" model — it emits a <think>...</think> block
    # before every answer by default, which is pure latency overhead for a
    # mechanical JSON-extraction task (no benefit, and on local/CPU inference
    # it's often what pushes a call past the timeout). "/no_think" is Qwen's
    # documented prompt-level soft-switch, honored across serving backends
    # (Ollama, vLLM, native API) since it's trained into the chat template.
    real_model = _resolve_model(model, _active())
    user_msg = f"{user}\n/no_think" if "qwen" in real_model.lower() else user
    raw = await chat_text(system + guardrail, user_msg, model=model, temperature=temperature)
    raw = _strip_code_fence(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data, recovered, span_err = None, False, None
        m = re.search(r"\{.*\}|\[.*\]", raw, re.DOTALL)
        if m:
            # This strategy's own JSONDecodeError must not escape. A response
            # whose *first* field is well-formed and whose second one is not
            # (M11: a valid "verdict" line followed by a bare, unquoted
            # "rationale" value) still matches this regex, so the span parses no
            # better than `raw` did — and letting the error propagate skipped
            # both the fallback below and the readable message that carries the
            # raw output needed to diagnose it.
            try:
                data, recovered = json.loads(m.group(0)), True
            except json.JSONDecodeError as e:
                span_err = e  # keep it: this attempt parsed furthest
        if not recovered:
            # Model sometimes drops the outer braces, returning bare "k": v pairs.
            try:
                data = json.loads("{" + raw.strip().rstrip(",") + "}")
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"LLM did not return JSON ({span_err or e}): {raw[:400]}"
                ) from (span_err or e)
    # Model sometimes echoes the JSON Schema envelope instead of an instance,
    # e.g. {"properties": {<real values>}, "type": "object"}. Unwrap it when the
    # top level has none of the expected fields but does carry "properties".
    if (
        isinstance(data, dict)
        and "properties" in data
        and isinstance(data["properties"], dict)
        and not (set(schema.model_fields) & set(data))
    ):
        data = data["properties"]
    # Model sometimes returns a bare array when schema wraps one list field.
    if isinstance(data, list):
        list_fields = [
            name for name, f in schema.model_fields.items()
            if "list" in str(f.annotation).lower()
        ]
        if len(list_fields) == 1:
            data = {list_fields[0]: data}
    try:
        return schema.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"Pydantic validation failed: {e}\nRaw: {raw[:400]}")
