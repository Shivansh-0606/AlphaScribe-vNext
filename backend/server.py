"""AlphaScribe FastAPI backend — Multi-Agent Equity Research Copilot."""
from __future__ import annotations
import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

from agents import auth, notify
from agents.graph import build_graph
from agents.learning_graph import build_learning_graph
from agents.ingest import (
    extract_pdf_text,
    fetch_bse_annual_report,
    fetch_edgar_latest,
    fetch_yfinance,
    ingest_document,
)
from agents.sample_data import SAMPLES
from agents.scoring import compute_scorecard
from agents.retrieval import retrieval_status
from agents import company_index

# M2 Phase 1 shared infrastructure — additive; see
# docs/backend_engineering/14_M2_Phase1_Implementation_Report.md for exactly
# what each import below is wired into, and what stays built-and-tested-
# standalone (not yet cut over) this phase.
from app.api.errors import domain_error_handler
from app.container import build_container
from app.settings import load_settings
from domain.errors import DomainError, InfrastructureError, NotFoundError, RateLimitedError, ValidationError
from domain.financials import AcquisitionOutcome, PeriodType, StatementType
from domain.models import JobKind
from infrastructure.mongo.client import ping as mongo_ping
from infrastructure.redis.client import ping as redis_ping
from infrastructure.mongo.indexes import ensure_indexes as ensure_mongo_indexes
from infrastructure.observability.logging import install_correlation_filter, set_correlation_id
from infrastructure.observability.metrics import (
    acquisition_request_total,
    auth_failures_total,
    authz_denied_total,
    comparison_explanation_runs_total,
    filing_analysis_runs_total,
    deadline_exceeded_total,
    http_request_duration_seconds,
    http_requests_total,
    jobs_active,
    pipeline_duration_seconds,
    pipeline_runs_total,
    render_latest as render_metrics,
    report_cache_lookups_total,
)
from infrastructure.observability.tracing import get_tracer, setup_tracing
from opentelemetry.trace import Status, StatusCode
from infrastructure.security.authorization import require_admin
from infrastructure.streaming.sse import sse_response
from pymongo.errors import DuplicateKeyError

from agents.comparison_explanation import (
    GroundingError,
    compute_evidence_fingerprint,
    compute_identity_key,
    generate_explanation,
)
from agents.filing_analysis import (
    FilingAnalysisGroundingError,
    analyze_filing,
)

# ---------------------------------------------------------------------------
# DB / App setup
# ---------------------------------------------------------------------------

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client[DB_NAME]

app = FastAPI(title="AlphaScribe", version="0.1.0")
api = APIRouter(prefix="/api")

# M2 Phase 4 cutover (06 §7; 14's readiness condition 3): job bookkeeping and
# SSE fan-out go through the shared application/jobs.py::JobLifecycle +
# EventBus infrastructure (fixes 01 D-1 — two concurrent SSE readers used to
# split one job's events) instead of the old JOBS/JOB_QUEUES dicts. One
# shared MAX_ACTIVE_JOBS budget now covers both research and Learning jobs
# (JobKind.RESEARCH / JobKind.LEARNING), per 03's design.
#
# RUNNING_TASKS is the one thing this infrastructure deliberately doesn't
# track (a JobStore entry isn't a live asyncio.Task) — needed so a cancel
# request can actually interrupt an in-flight graph run, same role the old
# JOBS[job_id]["task"] played.
settings = load_settings()
container = build_container(settings)
RUNNING_TASKS: dict[str, asyncio.Task] = {}
_tracing_started = False

# Fire-and-forget background tasks with no natural key (unlike RUNNING_TASKS
# above, keyed by job_id for cancel_report's lookup). asyncio.create_task()
# only holds a weak reference to the task it returns — a documented footgun
# (see the asyncio docs' own "Save a reference to the result" warning): with
# no strong reference retained anywhere, the task can be garbage-collected
# before it completes, even while the process stays healthy. This set is
# that strong reference; the done-callback removes it once the task
# finishes, so it never grows unbounded.
_BACKGROUND_TASKS: set[asyncio.Task] = set()


def _track_background_task(task: asyncio.Task) -> asyncio.Task:
    """Retains an already-created fire-and-forget task until it completes,
    then discards it automatically. Does not create a task itself — callers
    still own `asyncio.create_task(...)` (or, for M8, the orchestrator's own
    `schedule()`); this only fixes the reference-lifetime gap."""
    _BACKGROUND_TASKS.add(task)
    task.add_done_callback(_BACKGROUND_TASKS.discard)
    return task

# Compile graphs once at startup.
graph = build_graph(db)
learning_graph = build_learning_graph(db)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("alphascribe")

# Surface the active LLM provider at startup (helps diagnose quota/key issues).
from agents.llm import _active  # noqa: E402
_cfg = _active()
logger.info("LLM provider=%s  light=%s  heavy=%s  key=%s",
            _cfg["provider"], _cfg["light"], _cfg["heavy"],
            "set" if _cfg["api_key"] else "MISSING")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class IngestTextRequest(BaseModel):
    ticker: str = Field(max_length=20)
    source: str = Field(max_length=200, description="Human label, e.g. '10-Q FY24 Q3'")
    text: str = Field(max_length=1_000_000)   # ~1MB; chunker handles the rest
    company_name: Optional[str] = Field(default=None, max_length=200)


class IngestEdgarRequest(BaseModel):
    ticker: str = Field(max_length=20)
    form_type: str = Field(default="10-Q", max_length=20)


class GenerateRequest(BaseModel):
    ticker: str = Field(max_length=20)
    query: str = Field(max_length=2000)
    context_report_id: Optional[str] = None   # if set, treat as a follow-up
                                              # and inject prior brief into synth
    llm_provider: Optional[str] = None        # gemini|openai|groq|custom
    llm_api_key: Optional[str] = None         # bring-your-own key (not stored)
    llm_base_url: Optional[str] = None        # for custom OpenAI-compatible endpoints
    llm_model: Optional[str] = None           # optional model override
    no_cache: bool = False                    # force a fresh run, skip cache


class ExplainRequest(BaseModel):
    ticker: str = Field(max_length=20)
    concept: str = Field(max_length=500)
    context_report_id: Optional[str] = None   # SCR-06 "Explain This" — grounds
                                              # the explanation in that report's figures
    llm_provider: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model: Optional[str] = None


class JobSummary(BaseModel):
    id: str
    ticker: str
    query: str
    status: str
    created_at: str
    fact_check_status: Optional[bool] = None
    retry_count: Optional[int] = None


class RegisterRequest(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=256)


class LoginRequest(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=256)
    remember: bool = False


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(max_length=256)
    new_password: str = Field(min_length=8, max_length=256)


class DeleteAccountRequest(BaseModel):
    email: str = Field(max_length=254)


class ForgotPasswordRequest(BaseModel):
    email: str = Field(max_length=254)


class ResetPasswordRequest(BaseModel):
    email: str = Field(max_length=254)
    otp: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=256)


def _set_session_cookie(response: Response, token: str, remember: bool) -> None:
    kwargs: dict[str, Any] = dict(
        key=auth.COOKIE_NAME, value=token, httponly=True, secure=True,
        samesite="lax", path="/",
    )
    if remember:
        kwargs["max_age"] = int(auth.SESSION_TTL_REMEMBER.total_seconds())
    # else: no max-age -> session cookie, cleared when the browser closes
    response.set_cookie(**kwargs)


async def current_user(request: Request) -> dict:
    """Dependency: cookie -> session -> user, or 401. Wired into every tool
    route (Phase 4 login wall) — only Landing/Docs/health/auth stay open."""
    user = await auth.get_current_user(db, request.cookies.get(auth.COOKIE_NAME))
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def _deny_cross_tenant(user_id: str, resource_id: str, *, resource_kind: str) -> HTTPException:
    """EQ-3 cutover (00_README.md ratification register: "Scope (404 cross-tenant)";
    01 D-5). A denial is logged for security monitoring (M5 scope: "audit logging
    for authorization decisions") but the response stays a generic 404 — same
    status a genuinely nonexistent id gets, so a caller probing UUIDs can't use
    the response to distinguish "not yours" from "doesn't exist" (mirrors
    agents/learning_nodes.py's identical owner-scoped 404 pattern, shipped M2)."""
    logger.warning("cross-tenant %s access denied: user=%s id=%s", resource_kind, user_id, resource_id)
    authz_denied_total.labels(endpoint=resource_kind, **{"class": "owner_scoped"}).inc()
    return HTTPException(status_code=404, detail=f"{resource_kind} not found")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@api.get("/")
async def root():
    return {"service": "alphascribe", "version": "0.1.0"}


@api.get("/health")
async def health():
    # M6 — O-12/O-13 fixed without changing the response shape (no contract
    # change, 04 O-16 confirms nothing consumes it): `estimated_document_count`
    # is a metadata read (O(1)), not the full collection scan
    # `count_documents({})` was; `_active()` resolves whichever provider is
    # actually configured (LLM_PROVIDER), not a hardcoded Gemini-only check —
    # the same function server.py's own startup log line already trusts.
    llm_key = bool(_active().get("api_key"))
    docs = await db.filings.estimated_document_count()
    chunks = await db.filing_chunks.estimated_document_count()
    return {
        "ok": True,
        "llm_key_configured": llm_key,
        "filings": docs,
        "chunks": chunks,
        "retrieval": retrieval_status(),
    }


@api.get("/health/ready")
async def health_ready():
    """M2 Phase 1 — additive readiness probe (04 §5.3, 10 §4.4; anticipated
    in 11_ADR_Index.md's "API-contract impact" table as an approved
    addition). A TRUE liveness/dependency check, not `/health`'s document
    counts (04 O-12): `mongo_ping` is a metadata round-trip
    (`{"ping": 1}`), not a collection scan. No frontend consumer — this is
    an operator/orchestrator probe, same posture as `/health`.

    M6 A2: also verifies Redis, but ONLY when `container.job_backend ==
    "redis"` — under the `JOB_BACKEND=memory` default (09 RR-10, the
    no-Docker developer path), `redis_client` is None and this check is
    skipped entirely, so readiness never gains a dependency that mode
    deliberately doesn't have. Response gains one field (`redis`, null
    under the memory backend) — additive, no existing key removed or
    retyped; no test or `web/` code path depends on this endpoint's exact
    shape (04 O-16)."""
    try:
        await mongo_ping(db)
        mongo_ok = True
    except Exception:  # noqa: BLE001 — readiness must report, never 500
        mongo_ok = False

    redis_ok: bool | None = None
    if container.redis_client is not None:
        try:
            await redis_ping(container.redis_client)
            redis_ok = True
        except Exception:  # noqa: BLE001 — readiness must report, never 500
            redis_ok = False

    ready = mongo_ok and (redis_ok is not False)
    return JSONResponse(
        status_code=200 if ready else 503,
        content={
            "ready": ready,
            "mongo": mongo_ok,
            "redis": redis_ok,
            "job_backend": container.job_backend,
            "retrieval": retrieval_status(),
        },
    )


@api.get("/metrics")
async def metrics():
    """M2 Phase 1 — additive Prometheus scrape endpoint (04 §3.3, 07 §7.2,
    09 §12, 10 §13 catalogs). Public, matching `/health`'s posture — a real
    deployment scrapes this from a private network (10 SD-5), which is an
    operational concern, not a code one."""
    body, content_type = render_metrics()
    return Response(content=body, media_type=content_type)


@api.post("/auth/register")
async def register(req: RegisterRequest, response: Response):
    email = req.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email")
    try:
        user = await auth.create_user(db, email, req.password)
    except ValueError:
        raise HTTPException(status_code=409, detail="Email already registered")
    token, _ = await auth.create_session(db, user["id"], remember=False)
    _set_session_cookie(response, token, remember=False)
    return auth.public_user(user)


@api.post("/auth/login")
async def login(req: LoginRequest, response: Response):
    # Keyed by email only (not IP): this is a shared single-process backend,
    # and IP-keying would let unrelated brute-force attempts against other
    # accounts lock out a legitimate user behind the same NAT/proxy.
    # Recorded before the DB await (not after, on failure) so concurrent
    # requests for the same key can't all read the pre-attempt count and
    # slip past the cap together; clear_hits undoes it on success.
    key = f"login:{req.email.strip().lower()}"
    if auth.is_rate_limited(key):
        auth_failures_total.labels(reason="rate_limited").inc()
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")
    auth.record_hit(key)
    user = await auth.authenticate(db, req.email, req.password)
    if not user:
        auth_failures_total.labels(reason="bad_credentials").inc()
        raise HTTPException(status_code=401, detail="Invalid email or password")
    auth.clear_hits(key)
    token, _ = await auth.create_session(db, user["id"], remember=req.remember)
    _set_session_cookie(response, token, remember=req.remember)
    return auth.public_user(user)


@api.post("/auth/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    """Always returns the same response regardless of whether the email is
    registered or the send succeeds — don't leak account existence. Keyed by
    email only (see /auth/login) — caps OTP spam per victim without an
    IP dimension that would self-DoS shared networks/proxies."""
    email = req.email.strip().lower()
    key = f"reset-req:{email}"
    if not auth.is_rate_limited(key):
        auth.record_hit(key)
        user = await db.users.find_one({"email": email})
        if user:
            otp = await auth.create_password_reset(db, email)
            # Fire-and-forget: awaiting the outbound Resend HTTP call here
            # would make this branch measurably slower than the not-found
            # branch, leaking account existence via response timing even
            # though the response body is identical either way.
            _track_background_task(asyncio.create_task(notify.send_otp_email(email, otp)))
    return {"ok": True}


@api.post("/auth/reset-password")
async def reset_password(req: ResetPasswordRequest):
    email = req.email.strip().lower()
    key = f"reset-verify:{email}"
    if auth.is_rate_limited(key):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")
    auth.record_hit(key)  # see /auth/login: recorded before the await, not after, to close the race
    ok = await auth.verify_password_reset(db, email, req.otp)
    user = await db.users.find_one({"email": email}) if ok else None
    if not ok or not user:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    auth.clear_hits(key)
    await auth.update_password(db, user["id"], req.new_password)
    await auth.delete_all_sessions(db, user["id"])
    return {"ok": True}


@api.post("/auth/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get(auth.COOKIE_NAME)
    if token:
        await auth.delete_session(db, token)
    response.delete_cookie(
        key=auth.COOKIE_NAME, path="/", httponly=True, secure=True, samesite="lax",
    )
    return {"ok": True}


@api.get("/auth/me")
async def me(user: dict = Depends(current_user)):
    return auth.public_user(user)


@api.post("/auth/password")
async def change_password(req: ChangePasswordRequest, request: Request,
                           user: dict = Depends(current_user)):
    if not auth.verify_password(req.current_password, user["password_salt"], user["password_hash"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    await auth.update_password(db, user["id"], req.new_password)
    # Changing the password signs out every other device; this one stays
    # signed in since the caller just proved they know the (new) password.
    token = request.cookies.get(auth.COOKIE_NAME)
    await auth.delete_other_sessions(db, user["id"], token)
    return {"ok": True}


@api.post("/auth/logout-all")
async def logout_everywhere(response: Response, user: dict = Depends(current_user)):
    await auth.delete_all_sessions(db, user["id"])
    response.delete_cookie(
        key=auth.COOKIE_NAME, path="/", httponly=True, secure=True, samesite="lax",
    )
    return {"ok": True}


@api.delete("/auth/me")
async def delete_account(req: DeleteAccountRequest, response: Response,
                          user: dict = Depends(current_user)):
    if req.email.strip().lower() != user["email"]:
        raise HTTPException(status_code=400, detail="Email confirmation does not match")
    # Cascade: user's own sessions + reports. Shared filings/chunks corpus and
    # is_sample reports (user_id=None) are intentionally untouched.
    report_ids = [
        r["id"] for r in
        await db.reports.find({"user_id": user["id"]}, {"id": 1, "_id": 0}).to_list(None)
    ]
    await db.reports.delete_many({"user_id": user["id"]})
    if report_ids:
        await db.jobs.delete_many({"id": {"$in": report_ids}})
        for rid in report_ids:
            RUNNING_TASKS.pop(rid, None)
    await auth.delete_all_sessions(db, user["id"])
    await db.users.delete_one({"id": user["id"]})
    response.delete_cookie(
        key=auth.COOKIE_NAME, path="/", httponly=True, secure=True, samesite="lax",
    )
    return {"ok": True}


@api.post("/ingest/text")
async def ingest_text(req: IngestTextRequest, user: dict = Depends(current_user)):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is empty")
    result = await ingest_document(
        db, ticker=req.ticker, source=req.source, text=req.text,
        company_name=req.company_name,
    )
    return result


@api.post("/ingest/edgar")
async def ingest_edgar(req: IngestEdgarRequest, user: dict = Depends(current_user)):
    doc = await fetch_edgar_latest(req.ticker, req.form_type)
    if not doc:
        raise HTTPException(status_code=404, detail=f"No {req.form_type} found for {req.ticker}")
    result = await ingest_document(
        db, ticker=req.ticker, source=doc["source"], text=doc["text"],
        company_name=doc.get("company_name"),
    )
    result["url"] = doc.get("url")
    return result


@api.post("/ingest/samples")
async def ingest_samples(user: dict = Depends(current_user)):
    ingested = []
    for s in SAMPLES:
        # skip if already there
        exists = await db.filings.find_one({"ticker": s["ticker"], "source": s["source"]})
        if exists:
            continue
        r = await ingest_document(
            db, ticker=s["ticker"], source=s["source"], text=s["text"],
            company_name=s.get("company_name"),
        )
        ingested.append(r)
    return {"ingested": ingested, "total_samples": len(SAMPLES)}


def _reject_oversize(request: Request, limit: int) -> None:
    """Reject an upload by Content-Length before buffering the whole body into
    memory. The post-read len() check still backstops a missing/lying header."""
    cl = request.headers.get("content-length")
    if cl and cl.isdigit() and int(cl) > limit:
        raise HTTPException(status_code=413, detail=f"File exceeds {limit // (1024 * 1024)}MB")


@api.post("/ingest/audio")
async def ingest_audio(
    request: Request,
    file: UploadFile = File(...),
    ticker: str = Form(...),
    source: str = Form("Audio Transcript"),
    company_name: Optional[str] = Form(None),
    language: Optional[str] = Form("en"),
    user: dict = Depends(current_user),
):
    """Transcribe an audio file via OpenAI Whisper and ingest the transcript.

    Supports mp3, mp4, mpeg, mpga, m4a, wav, webm. Max 25MB.
    """
    ALLOWED = {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"}
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"Unsupported audio type: .{ext}")

    _reject_oversize(request, 25 * 1024 * 1024)
    raw = await file.read()
    if len(raw) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Audio file exceeds 25MB")
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=501,
            detail="Audio ingest is disabled — set GEMINI_API_KEY to enable transcription.",
        )

    # Map file extension to a MIME type Gemini accepts.
    MIME = {
        "mp3": "audio/mp3", "mpeg": "audio/mpeg", "mpga": "audio/mpeg",
        "m4a": "audio/mp4", "mp4": "audio/mp4", "wav": "audio/wav",
        "webm": "audio/webm",
    }
    try:
        import google.generativeai as genai
        from agents.llm import GEMINI_LOCK

        def _transcribe() -> str:
            # configure() is process-global; share llm.py's lock so a concurrent
            # pipeline Gemini call can't swap the key out from under us.
            with GEMINI_LOCK:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    os.environ.get("GEMINI_LIGHT_MODEL", "gemini-2.5-flash")
                )
                prompt = (
                    "Transcribe this audio verbatim to plain text. "
                    "Return only the transcript, no commentary."
                )
                resp = model.generate_content([
                    prompt,
                    {"mime_type": MIME.get(ext, "audio/mpeg"), "data": raw},
                ])
            return resp.text or ""

        transcript = await asyncio.to_thread(_transcribe)
    except Exception:
        # Don't echo the raw provider error: SDK exceptions can embed the API
        # key (Gemini passes it as a ?key=... URL param). Full detail is logged.
        logger.exception("gemini transcription failed")
        raise HTTPException(status_code=502, detail="Transcription failed. See server logs.")

    if not transcript or not transcript.strip():
        raise HTTPException(status_code=422, detail="Transcript was empty")

    result = await ingest_document(
        db, ticker=ticker, source=source, text=transcript,
        company_name=company_name,
    )
    result["transcript_chars"] = len(transcript)
    result["transcript_preview"] = transcript[:400]
    return result


@api.post("/ingest/pdf")
async def ingest_pdf(
    request: Request,
    file: UploadFile = File(...),
    ticker: str = Form(...),
    source: str = Form("Annual Report"),
    company_name: Optional[str] = Form(None),
    user: dict = Depends(current_user),
):
    """Extract text from an uploaded PDF (e.g. an Indian annual report) and ingest it.

    Gives non-US stocks a rich narrative source, since yfinance only returns a
    2-line summary. Scanned/image PDFs extract nothing — we detect that and tell
    the user to paste the text instead.
    """
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext != "pdf":
        raise HTTPException(status_code=400, detail=f"Not a PDF: .{ext}")

    _reject_oversize(request, 50 * 1024 * 1024)
    raw = await file.read()
    if len(raw) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="PDF exceeds 50MB")
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        text = await asyncio.to_thread(extract_pdf_text, raw)
    except Exception as e:
        logger.exception("pdf extraction failed")
        raise HTTPException(status_code=422, detail=f"Couldn't read PDF: {e}")

    if not text or not text.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "No text found — this looks like a scanned/image PDF. "
                "Copy the text and use 'Paste text' instead."
            ),
        )

    result = await ingest_document(
        db, ticker=ticker, source=source, text=text, company_name=company_name,
    )
    result["extracted_chars"] = len(text)
    result["text_preview"] = text[:400]
    return result


@api.get("/companies")
async def list_companies(user: dict = Depends(current_user)):
    """Ticker -> company name mapping derived from ingested filings."""
    rows = await db.companies.find({}, {"_id": 0}).to_list(1000)
    return {"companies": {r["ticker"]: r["name"] for r in rows if r.get("name")}}


@api.get("/companies/search")
async def companies_search(q: str, limit: int = 8, user: dict = Depends(current_user)):
    """Fuzzy search the SEC company universe. Falls back to locally ingested
    companies if the SEC index hasn't been loaded yet."""
    q = (q or "").strip()
    if not q:
        return {"results": []}

    if not company_index.is_loaded():
        # kick a background load — first call may return few results, subsequent are richer
        asyncio.create_task(company_index.load_index())

    results = company_index.search(q, limit=limit)

    # augment with which companies we already have filings for
    if results:
        tickers = [r["ticker"] for r in results]
        have = set()
        cursor = db.filings.find({"ticker": {"$in": tickers}}, {"ticker": 1, "_id": 0})
        async for row in cursor:
            have.add(row["ticker"])
        for r in results:
            r["has_filings"] = r["ticker"] in have

    # If SEC index unavailable, fall back to our own companies collection
    if not results:
        qn = q.lower()
        local = await db.companies.find({}, {"_id": 0}).to_list(1000)
        local_scored = []
        for row in local:
            name = (row.get("name") or "").lower()
            tk = (row.get("ticker") or "").lower()
            if qn in name or qn in tk:
                local_scored.append({
                    "ticker": row["ticker"],
                    "name": row.get("name") or row["ticker"],
                    "has_filings": True,
                })
        results = local_scored[:limit]

    return {"results": results, "index_loaded": company_index.is_loaded()}


class EnsureRequest(BaseModel):
    ticker: str
    refresh: bool = False


@api.post("/companies/ensure")
async def ensure_company(req: EnsureRequest, user: dict = Depends(current_user)):
    """Guarantee we have some filing for `ticker`. If none (or `refresh=True`),
    fetch latest 10-Q (falling back to 10-K) from SEC EDGAR and ingest it."""
    ticker = req.ticker.strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="ticker required")

    # M8 Step 6 — Document 36 §4.1's "existing ingestion step" acquisition
    # trigger: fire-and-forget financial-statement acquisition for this
    # ticker, unconditional (fires whether or not text filings already
    # exist, since financial-statement acquisition is a separate, possibly
    # not-yet-attempted concern). Matches the /auth/forgot-password
    # OTP-email precedent exactly (asyncio.create_task, never awaited) —
    # safe because AcquireFinancialsUseCase.acquire() never raises (Step 5).
    # schedule() already created these tasks; retaining them here only
    # fixes their reference lifetime, it does not create a second task.
    for task in container.financials_orchestrator.schedule(ticker, trigger="ensure_company"):
        _track_background_task(task)

    # Indian tickers aren't in SEC EDGAR
    exch = company_index.lookup_exchange(ticker)
    name = company_index.lookup_ticker(ticker)

    exists = await db.filing_chunks.count_documents({"ticker": ticker}) > 0
    if exists and not req.refresh:
        latest = await db.filings.find_one(
            {"ticker": ticker}, {"_id": 0}, sort=[("created_at", -1)]
        )
        return {
            "ticker": ticker,
            "company_name": name,
            "exchange": exch,
            "action": "already_ingested",
            "latest_filing": latest,
        }

    # US companies: try SEC EDGAR first (full filings, richest source).
    if exch != "IN":
        for form in ("10-Q", "10-K"):
            try:
                doc = await fetch_edgar_latest(ticker, form)
            except Exception as e:
                logger.warning("EDGAR fetch failed for %s %s: %s", ticker, form, e)
                doc = None
            if doc and doc.get("text"):
                result = await ingest_document(
                    db, ticker=ticker, source=doc["source"], text=doc["text"],
                    company_name=doc.get("company_name"),
                )
                result["action"] = "ingested_from_edgar"
                result["url"] = doc.get("url")
                result["filing_date"] = doc.get("filing_date")
                result["form_type"] = form
                result["exchange"] = "US"
                return result

    # Indian companies: try BSE's latest annual-report PDF first — it's the rich
    # narrative source (MD&A, mgmt commentary) that yfinance can't give. Falls
    # through to yfinance below on any failure (anti-bot, scanned PDF, no code).
    if exch == "IN":
        try:
            bdoc = await fetch_bse_annual_report(ticker)
        except Exception as e:
            logger.warning("BSE annual-report fetch failed for %s: %s", ticker, e)
            bdoc = None
        if bdoc and bdoc.get("text"):
            result = await ingest_document(
                db, ticker=ticker, source=bdoc["source"], text=bdoc["text"],
                company_name=bdoc.get("company_name") or name,
            )
            result["action"] = "ingested_from_bse"
            result["url"] = bdoc.get("url")
            result["exchange"] = "IN"
            return result

    # Fallback (and primary path for non-US): Yahoo Finance profile — works for
    # any listed company worldwide (NSE/BSE tickers via .NS/.BO suffixes).
    try:
        ydoc = await fetch_yfinance(ticker, exch)
    except Exception as e:
        logger.warning("yfinance fetch failed for %s: %s", ticker, e)
        ydoc = None
    if ydoc and ydoc.get("text"):
        result = await ingest_document(
            db, ticker=ticker, source=ydoc["source"], text=ydoc["text"],
            company_name=ydoc.get("company_name"),
        )
        result["action"] = "ingested_from_yfinance"
        result["url"] = ydoc.get("url")
        result["exchange"] = exch or "US"
        return result

    raise HTTPException(
        status_code=404,
        detail=(
            f"Couldn't fetch data for {name or ticker} from SEC EDGAR or Yahoo "
            "Finance. Try 'Paste text' or 'Upload audio' on the Ingest page."
        ),
    )


@api.post("/companies/{ticker}/financials/acquire")
async def acquire_financials(
    ticker: str, period_type: PeriodType, user: dict = Depends(current_user)
) -> dict:
    """M8 Step 7 — Document 33 Amendment §1-§17 (frozen wire contract). A
    thin HTTP adapter only: reads current AcquisitionState for the three
    statement-type identities implied by (ticker, period_type) through the
    same repository port Step 5 uses, schedules acquisition only for
    whichever are not_yet_acquired via Step 6's orchestrator, and maps the
    result onto the frozen four-outcome response. No AS-4/AS-5/provider-
    classification/acquisition-state-transition logic lives here — that
    stays in application/financials.py (Step 5) and
    application/financials_orchestration.py (Step 6), invoked, not
    reimplemented. GET /companies/{ticker}/financials is a separate,
    unbuilt, unrelated governance gate — not touched by this endpoint.
    """
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValidationError("ticker required", code="validation_error")

    rate_limit_key = f"acquire:{user['id']}:{ticker}:{period_type.value}"
    if auth.is_rate_limited(rate_limit_key):
        raise RateLimitedError("Too many acquisition requests for this ticker. Retry in a moment.")
    auth.record_hit(rate_limit_key)

    with get_tracer().start_as_current_span("financials.acquire_endpoint") as span:
        span.set_attribute("ticker", ticker)
        span.set_attribute("period_type", period_type.value)
        try:
            results = await asyncio.gather(
                *(container.acquisition_states.get(ticker, period_type, st) for st in StatementType)
            )
        except Exception as e:  # noqa: BLE001 — synchronous infra failure, Document 33 §8's 502 case
            logger.exception(
                "acquisition-state read failed ticker=%s period_type=%s", ticker, period_type.value
            )
            raise InfrastructureError("Failed to read acquisition state. See server logs for details.") from e

        states = dict(zip(StatementType, results))
        not_yet = [st for st, state in states.items() if state is AcquisitionOutcome.NOT_YET_ACQUIRED]

        if not_yet:
            outcome = "requested"
            for task in container.financials_orchestrator.schedule(
                ticker, period_types=[period_type], statement_types=not_yet, trigger="acquire_endpoint"
            ):
                _track_background_task(task)
        elif all(state is AcquisitionOutcome.AVAILABLE for state in states.values()):
            outcome = "available"
        elif all(state is AcquisitionOutcome.CONFIRMED_UNAVAILABLE for state in states.values()):
            outcome = "confirmed_unavailable"
        else:
            outcome = "mixed"

        span.set_attribute("acquisition.outcome", outcome)
        acquisition_request_total.labels(outcome=outcome).inc()
        logger.info(
            "acquisition request ticker=%s period_type=%s outcome=%s", ticker, period_type.value, outcome
        )
        return {"ticker": ticker, "period_type": period_type.value, "outcome": outcome}


@api.get("/companies/{ticker}/financials")
async def get_financials(
    ticker: str, period_type: PeriodType, user: dict = Depends(current_user)
) -> dict:
    """M12 — Document 33 §1-§10 (CTO-ratified, Round 7). A thin, read-only
    HTTP adapter: reads persisted FinancialStatement rows through the same
    repository port the acquisition use case uses, reads each
    StatementType's AcquisitionState through the same port
    acquire_financials uses, groups statements by statement_type, and
    assembles the frozen response envelope (Document 33 §3.2). Never calls
    a provider synchronously and never schedules acquisition (Document 33
    §4) — that is exclusively POST .../acquire's job.
    """
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValidationError("ticker required", code="validation_error")

    with get_tracer().start_as_current_span("financials.get_endpoint") as span:
        span.set_attribute("ticker", ticker)
        span.set_attribute("period_type", period_type.value)
        try:
            fetched = await container.financial_statements.get(ticker, period_type)
            state_results = await asyncio.gather(
                *(container.acquisition_states.get(ticker, period_type, st) for st in StatementType)
            )
        except Exception as e:  # noqa: BLE001 — synchronous infra failure, Document 33 §5 row 4's 502 case
            logger.exception(
                "financials read failed ticker=%s period_type=%s", ticker, period_type.value
            )
            raise InfrastructureError("Failed to read financial statements. See server logs for details.") from e

        states = dict(zip(StatementType, state_results))
        by_type: dict[StatementType, list] = {st: [] for st in StatementType}
        for statement in fetched:
            by_type[statement.statement_type].append(statement)

        statements = {}
        for st in StatementType:
            # Document 33 §6.2 (Round 6/7, CTO-ratified) — period_end descending,
            # most recent period first, identically for annual and quarterly.
            periods = sorted(by_type[st], key=lambda s: s.period_end, reverse=True)
            statements[st.value] = {
                "acquisition_state": states[st].value,
                "periods": [
                    {
                        "period_end": p.period_end,
                        "fiscal_year": p.fiscal_year,
                        "currency": p.currency,
                        "source": p.source,
                        "fetched_at": p.fetched_at,
                        "metrics": [m.model_dump(mode="json") for m in p.metrics],
                    }
                    for p in periods
                ],
            }

        return {"ticker": ticker, "period_type": period_type.value, "statements": statements}


async def _load_ordered_filing_chunks(doc_id: str, ticker: str, *, context: str) -> list[dict]:
    """One filing's persisted chunks as an ordered `[{chunk_idx, text}]` list.

    `chunk_idx` ascending is authoritative (Document 59 §6): the query carries
    an explicit `.sort("chunk_idx", 1)` AND the result is re-sorted in Python
    so incidental Mongo order is never trusted. `_id` / `embedding` are
    stripped. A row whose `chunk_idx` is not an int or whose `text` is not a
    str is omitted and logged, not fatal (Document 59 §8 / OD-8).

    Shared verbatim by M13 `get_filing_content` and M14 `_run_filing_analysis`
    (bounded-revision M-1) — one implementation, identical behaviour. `context`
    only labels the malformed-row warning line.
    """
    raw_chunks = await (
        db.filing_chunks.find({"doc_id": doc_id}, {"_id": 0, "embedding": 0})
        .sort("chunk_idx", 1)
        .to_list(length=None)
    )
    chunks = sorted(
        (
            {"chunk_idx": c["chunk_idx"], "text": c["text"]}
            for c in raw_chunks
            if isinstance(c.get("chunk_idx"), int) and isinstance(c.get("text"), str)
        ),
        key=lambda c: c["chunk_idx"],
    )
    if len(chunks) != len(raw_chunks):
        logger.warning(
            "%s: %d malformed chunk(s) omitted for doc_id=%s ticker=%s",
            context, len(raw_chunks) - len(chunks), doc_id, ticker,
        )
    return chunks


@api.get("/companies/{ticker}/filings/{doc_id}/content")
async def get_filing_content(
    ticker: str, doc_id: str, user: dict = Depends(current_user)
) -> dict:
    """M13 — Filing Content Reading (Document 59 CTO-RATIFIED / FROZEN,
    Document 60 CTO-RATIFIED / FROZEN, 2026-08-27; M13 Implementation
    Authorization, 2026-08-27). A thin, read-only HTTP adapter over the
    filing text already persisted at ingest: reads the `filings` metadata
    row and its ordered `filing_chunks` directly through `db` (Document 60
    §3.1 / OD-A — no new repository/port/service), strips embeddings, and
    returns the frozen envelope (Document 59 §5.1). Never calls a provider,
    never triggers acquisition, never writes.

    - `(ticker, doc_id)` identity — the `filings` row must match both, or
      404 (Document 59 §8 / OD-6). A `doc_id` under a different ticker
      "does not exist for the requested company".
    - Zero chunks for a real filing → 200 with `content.chunks: []`
      (Document 59 §8 / OD-7), never a fabricated body.
    - `chunk_idx` ascending is authoritative (Document 59 §6): the query
      carries an explicit `.sort("chunk_idx", 1)` and the result is
      re-ordered in Python so incidental Mongo order is never trusted.
    - OD-8 (delegated to this phase): a chunk missing an integer
      `chunk_idx` or a string `text` is omitted and logged, rather than
      500-ing the whole read or fabricating content — the smallest
      deterministic behaviour consistent with Document 59 §8's non-binding
      candidate; no `partial` flag is added (the UI does not need one).
    """
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValidationError("ticker required", code="validation_error")

    with get_tracer().start_as_current_span("filings.get_content_endpoint") as span:
        span.set_attribute("ticker", ticker)
        span.set_attribute("doc_id", doc_id)
        try:
            filing = await db.filings.find_one({"ticker": ticker, "doc_id": doc_id}, {"_id": 0})
            if filing is None:
                raise NotFoundError("filing not found")  # Document 59 §8 / OD-6 — 404

            chunks = await _load_ordered_filing_chunks(doc_id, ticker, context="filing content")

            return {
                "doc_id": filing["doc_id"],
                "ticker": filing["ticker"],
                "company_name": filing.get("company_name"),
                "source": filing["source"],
                "created_at": filing["created_at"],
                "num_chunks": filing["num_chunks"],
                "char_count": filing["char_count"],
                "content": {"chunks": chunks},
            }
        except DomainError:
            raise  # NotFoundError / ValidationError pass through unchanged (Document 59 §9)
        except Exception as e:  # noqa: BLE001 — synchronous infra failure or an unassemblable row, Document 59 §8/§9's 502 case
            logger.exception(
                "filing content read failed ticker=%s doc_id=%s", ticker, doc_id
            )
            raise InfrastructureError(
                "Failed to read filing content. See server logs for details."
            ) from e


@api.get("/filings")
async def list_filings(ticker: Optional[str] = None, user: dict = Depends(current_user)):
    q: dict = {}
    if ticker:
        q["ticker"] = ticker.upper()
    rows = await db.filings.find(q, {"_id": 0}).sort("created_at", -1).to_list(200)
    return {"filings": rows}


@api.get("/tickers")
async def list_tickers(user: dict = Depends(current_user)):
    tickers = await db.filings.distinct("ticker")
    return {"tickers": sorted(tickers)}


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

async def _run_pipeline(job_id: str, ticker: str, query: str,
                        prior_brief: str = "",
                        llm_provider: str | None = None,
                        llm_api_key: str | None = None,
                        llm_base_url: str | None = None,
                        llm_model: str | None = None,
                        user_id: str | None = None) -> None:
    from agents.llm import set_llm_context, reset_llm_context
    _tok = (
        set_llm_context(llm_provider, llm_api_key,
                        light_model=llm_model, heavy_model=llm_model, base_url=llm_base_url)
        if (llm_provider or llm_api_key) else None
    )
    started = asyncio.get_event_loop().time()
    await container.job_lifecycle.mark_running(job_id)
    await db.jobs.update_one({"id": job_id}, {"$set": {"status": "running"}}, upsert=True)

    async def push(ev: dict) -> None:
        # JobLifecycle.publish fans the event out to every SSE subscriber
        # (EventBus, fixes 01 D-1); the Mongo mirror lets a reconnecting
        # client's GET /reports/{id} see trace history even if the
        # in-memory EventBus lost it (e.g. after a restart).
        await container.job_lifecycle.publish(job_id, ev)
        await db.jobs.update_one(
            {"id": job_id},
            {"$push": {"events": ev}, "$set": {"updated_at": ev.get("ts", "")}}
        )

    # M6 — job-level parent span (doc 26's "background job tracing" gap):
    # this background task runs after the initiating request's own span
    # already ended, so without an explicit parent here, each node's span
    # (instrument_node()) would root its own independent trace instead of
    # nesting under one job-level trace. Entered/exited manually (not `with`)
    # because it must wrap the pre-existing try/except/finally without
    # reindenting the whole block; `finally` below guarantees the exit runs
    # exactly once regardless of outcome.
    _job_span_cm = get_tracer().start_as_current_span("pipeline.research", attributes={"job_id": job_id})
    _job_span = _job_span_cm.__enter__()
    try:
        initial: dict = {
            "ticker": ticker.upper(),
            "query": query,
            "retry_count": 0,
            "trace": [],
        }
        if prior_brief:
            initial["prior_brief"] = prior_brief
        final_state: dict = {}
        last_node_name = "unknown"
        async for event in graph.astream(initial, {"recursion_limit": 25}):
            # event is {node_name: node_return_value}
            for _node_name, node_state in event.items():
                last_node_name = _node_name
                if not isinstance(node_state, dict):
                    continue
                final_state.update(node_state)
                for t in node_state.get("trace", []):
                    await push(t)
            # 07 §5.4/LG-11: deadline is checked at node boundaries (between
            # yielded graph events), not preemptively mid-node — the coarsest
            # granularity that still bounds a pathological job to roughly its
            # deadline instead of the ~57-minute unbounded worst case.
            if await container.job_lifecycle.is_past_deadline(job_id):
                deadline_exceeded_total.labels(graph="research", node=last_node_name).inc()
                raise TimeoutError(f"job exceeded its {settings.job_deadline_s['research']}s deadline")

        # Persist final state (strip trace for storage cleanliness)
        completed_at = datetime.now(timezone.utc).isoformat()
        report_doc = {
            "id": job_id,
            "ticker": ticker.upper(),
            "query": query,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": completed_at,
            "draft_report": final_state.get("draft_report", ""),
            "extracted_data": final_state.get("extracted_data", {}),
            "sentiment_analysis": final_state.get("sentiment_analysis", {}),
            "source_documents": final_state.get("source_documents", []),
            "fact_check_status": bool(final_state.get("fact_check_status")),
            "validation_errors": final_state.get("validation_errors", []),
            "verified_claims": final_state.get("verified_claims", []),
            "retry_count": int(final_state.get("retry_count", 0)),
            "events": await container.events.history(job_id),
            "user_id": user_id,
        }
        report_doc["scorecard"] = compute_scorecard(report_doc)
        # attach company name for display
        comp = await db.companies.find_one({"ticker": ticker.upper()}, {"_id": 0})
        report_doc["company_name"] = comp.get("name") if comp else None
        await db.reports.insert_one(report_doc)
        await db.jobs.update_one(
            {"id": job_id},
            {"$set": {"status": "completed",
                      "report_id": job_id,
                      "fact_check_status": report_doc["fact_check_status"],
                      "retry_count": report_doc["retry_count"],
                      "completed_at": completed_at}}
        )
        await container.job_lifecycle.complete(job_id)
        pipeline_runs_total.labels(graph="research", status="completed").inc()
    except asyncio.CancelledError:
        completed_at = datetime.now(timezone.utc).isoformat()
        await db.jobs.update_one(
            {"id": job_id}, {"$set": {"status": "cancelled", "completed_at": completed_at}}
        )
        # Idempotent — cancel_report already calls job_lifecycle.cancel() to
        # publish the warn event before interrupting this task; this call is
        # a no-op in that case (job already terminal) and a safety net if
        # cancellation is ever triggered another way.
        await container.job_lifecycle.cancel(job_id)
        pipeline_runs_total.labels(graph="research", status="cancelled").inc()
        # M6 fast-follow: the span context manager's __exit__ is always
        # called with (None, None, None) below (it must run exactly once
        # from the shared `finally`, regardless of which branch handled the
        # exception) — so it can never auto-detect an error here. The
        # outcome is already known at this point in every except branch;
        # set it explicitly rather than relying on exception propagation
        # the span will never see.
        _job_span.set_status(Status(StatusCode.ERROR, "Job cancelled"))
    except TimeoutError as e:
        # LG-11: a pathological job (retry loops, a slow provider) is bounded
        # to its deadline instead of running unbounded — no raw exception
        # detail to redact here, unlike the generic branch below.
        logger.warning("pipeline %s: %s", job_id, e)
        err = "Analysis exceeded its time budget and was stopped."
        completed_at = datetime.now(timezone.utc).isoformat()
        await db.jobs.update_one(
            {"id": job_id}, {"$set": {"status": "failed", "error": err, "completed_at": completed_at}}
        )
        await container.job_lifecycle.fail(job_id, err)
        pipeline_runs_total.labels(graph="research", status="failed").inc()
        _job_span.set_status(Status(StatusCode.ERROR, err))
    except Exception:
        # Don't persist/stream the raw error: provider SDK exceptions can embed
        # the API key (Gemini passes it as a ?key=... URL param), and this text
        # is written to Mongo and pushed to the client. Full detail is logged.
        logger.exception("pipeline failed")
        err = "Analysis failed. See server logs for details."
        completed_at = datetime.now(timezone.utc).isoformat()
        await db.jobs.update_one(
            {"id": job_id}, {"$set": {"status": "failed", "error": err, "completed_at": completed_at}}
        )
        await container.job_lifecycle.fail(job_id, err)
        pipeline_runs_total.labels(graph="research", status="failed").inc()
        _job_span.set_status(Status(StatusCode.ERROR, err))
    finally:
        if _tok is not None:
            reset_llm_context(_tok)
        RUNNING_TASKS.pop(job_id, None)
        jobs_active.labels(kind="research").dec()
        pipeline_duration_seconds.labels(graph="research").observe(
            asyncio.get_event_loop().time() - started
        )
        _job_span_cm.__exit__(None, None, None)


class ValidateLlmKeyRequest(BaseModel):
    provider: str
    api_key: str = Field(min_length=1, max_length=512)
    base_url: str | None = None
    model: str | None = None


@api.post("/llm/validate")
async def validate_llm_key(req: ValidateLlmKeyRequest, user: dict = Depends(current_user)):
    """Live-checks a BYOK key with one trivial completion call — the frontend's
    Onboarding & AI Setup step needs this to satisfy the frozen UX spec's
    "validity checked before continue" requirement. Never persists the key,
    never generates real content. Same admin/SSRF restriction as
    `/reports/generate`'s custom-provider path, since this is the same probe
    surface (a client-supplied base_url the server fetches)."""
    provider = req.provider.strip().lower()
    if provider == "custom":
        # M2 Phase 1 cutover (10 §4.2/ADR-024): was an inline
        # `if not auth.is_admin(user): raise HTTPException(403, ...)` —
        # same condition, same status code, same message (verified in
        # tests/unit/test_authorization.py and by the full contract suite).
        require_admin(user)
        if req.base_url:
            from agents.llm import assert_public_url
            try:
                assert_public_url(req.base_url)
            except ValueError as e:
                return {"valid": False, "error": str(e)}

    from agents.llm import redact_key_from_error, validate_key
    try:
        await validate_key(provider, req.api_key, req.base_url, req.model)
        return {"valid": True}
    except Exception as e:  # noqa: BLE001
        logger.warning("LLM key validation failed for provider=%s: %s", provider, e)
        return {"valid": False, "error": redact_key_from_error(e, req.api_key)}


@api.post("/reports/generate")
async def generate_report(req: GenerateRequest, user: dict = Depends(current_user)):
    ticker = req.ticker.strip().upper()
    if not ticker or not req.query.strip():
        raise HTTPException(status_code=400, detail="ticker and query are required")

    # Custom provider (bring-your-own OpenAI-compatible endpoint) is admin-only
    # — it's the only path that accepts a client-supplied base_url at all, so
    # gating it here also gates the SSRF surface below to a trusted operator.
    # M2 Phase 1 cutover (10 §4.2/ADR-024) — same condition, restructured
    # from a single condensed `if X and not Y: raise` into `if X:
    # require_admin(user)`; behaviorally identical.
    if req.llm_provider == "custom" or req.llm_base_url:
        require_admin(user)

    # SSRF guard: the custom LLM endpoint is client-supplied and fetched by the
    # server, so it must not point at internal/loopback addresses.
    if req.llm_base_url:
        from agents.llm import assert_public_url
        try:
            assert_public_url(req.llm_base_url)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Custom LLM base URL must be a publicly reachable http(s) "
                    "address — the server calls it directly, so localhost and "
                    "private-network addresses aren't allowed. Use a hosted "
                    "endpoint, or tunnel a local LLM with ngrok/cloudflared."
                ),
            )

    # Require at least one ingested chunk for the ticker
    has_data = await db.filing_chunks.count_documents({"ticker": ticker}) > 0
    if not has_data:
        raise HTTPException(
            status_code=400,
            detail=f"No filings ingested for {ticker}. Ingest a filing first "
                   f"(POST /api/ingest/samples for demo data).",
        )

    # Cache: an identical (ticker, query) analysis with no follow-up context and
    # no new filings since is deterministic enough to reuse — saves time + quota
    # with zero accuracy cost (same sources, same verified brief). `no_cache`
    # forces a fresh run.
    if not req.context_report_id and not req.no_cache:
        latest_filing = await db.filings.find_one(
            {"ticker": ticker}, {"created_at": 1, "_id": 0}, sort=[("created_at", -1)]
        )
        # EQ-3 (M5): scoped to owner+sample — an unscoped cache lookup could
        # hand a caller a job_id for another tenant's report, which now (with
        # get_report/stream_report/cancel_report all owner-scoped) would 200
        # here and then 404 on every subsequent read. Same predicate as
        # list_reports; this is "backward-compatible migration behavior" for
        # the read-scoping cutover, not new report-generation scope — a
        # cache hit is a disguised read.
        cached = await db.reports.find_one(
            {"ticker": ticker, "query": req.query.strip(),
             "$or": [{"user_id": user["id"]}, {"is_sample": True}]},
            {"id": 1, "created_at": 1, "fact_check_status": 1, "user_id": 1, "is_sample": 1, "_id": 0},
            sort=[("created_at", -1)],
        )
        is_hit = bool(cached) and (
            not latest_filing
            or cached.get("created_at", "") >= latest_filing.get("created_at", "")
        )
        report_cache_lookups_total.labels(result="hit" if is_hit else "miss").inc()
        if is_hit:
            # A cache hit skips _run_pipeline (where user_id normally gets set),
            # so an unclaimed report a signed-in user reuses would otherwise
            # never show up in their history. Claim it once; leave already-owned
            # reports and curated public samples alone. (Unclaimed reports are a
            # pre-Phase-4 leftover — every report is user-owned going forward.)
            if not cached.get("user_id") and not cached.get("is_sample"):
                await db.reports.update_one(
                    {"id": cached["id"], "user_id": None}, {"$set": {"user_id": user["id"]}}
                )
            return {"job_id": cached["id"], "cached": True}

    # Cap concurrency (shared budget across research + Learning jobs, 03's
    # design) — enforced by JobLifecycle.start() below, which raises
    # RateLimitedError (-> 429 via domain_error_handler) once
    # settings.max_active_jobs is hit.
    job_id = str(uuid.uuid4())
    prior_brief = ""
    if req.context_report_id:
        prior = await db.reports.find_one(
            {"id": req.context_report_id}, {"draft_report": 1, "_id": 0}
        )
        if prior:
            prior_brief = prior.get("draft_report", "") or ""
    await container.job_lifecycle.start(
        job_id, JobKind.RESEARCH, user["id"], ticker=ticker,
        deadline_s=settings.job_deadline_s["research"],
    )
    jobs_active.labels(kind="research").inc()
    created_at = datetime.now(timezone.utc).isoformat()
    await db.jobs.insert_one({
        "id": job_id,
        "ticker": ticker,
        "query": req.query,
        "status": "queued",
        "created_at": created_at,
        "context_report_id": req.context_report_id,
        "user_id": user["id"],  # EQ-3 cutover — needed for get_report's restart-mirror tier
        "events": [],
    })
    RUNNING_TASKS[job_id] = asyncio.create_task(
        _run_pipeline(job_id, ticker, req.query, prior_brief=prior_brief,
                      llm_provider=req.llm_provider, llm_api_key=req.llm_api_key,
                      llm_base_url=req.llm_base_url, llm_model=req.llm_model,
                      user_id=user["id"])
    )
    return {"job_id": job_id}


@api.post("/reports/{job_id}/cancel")
async def cancel_report(job_id: str, user: dict = Depends(current_user)):
    job = await container.job_lifecycle.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    if job.user_id != user["id"]:
        # EQ-3 (01 D-5): a job is never a shared sample — only a completed
        # report can be — so ownership is the whole check here.
        raise _deny_cross_tenant(user["id"], job_id, resource_kind="job")
    if job.is_terminal():
        return {"job_id": job_id, "status": job.status.value, "note": "already finished"}
    task = RUNNING_TASKS.get(job_id)
    if task and not task.done():
        task.cancel()
    await container.job_lifecycle.cancel(job_id)
    await db.jobs.update_one({"id": job_id}, {"$set": {"status": "cancelled"}})
    return {"job_id": job_id, "status": "cancelled"}


async def _report_stream_events(job_id: str, user_id: str):
    """Wraps the shared EventBus subscription (infrastructure/streaming/sse.py
    frames whatever this yields) to inject the completed-report snapshot as a
    `final` event right after the terminal `pipeline/ok` — exactly the order
    the existing frontend contract expects (company-research/internal/
    streamStages.ts:39-40: "the final report snapshot arrives right after the
    pipeline/ok event that already set completed — must not regress").

    `user_id` re-scopes the final-report fetch (EQ-3) — belt-and-suspenders
    with stream_report's own ownership check below, mirroring
    _learning_stream_events' identical double-check."""
    async for ev in container.events.subscribe(job_id):
        yield ev
        if ev.get("node") == "pipeline" and ev.get("status") == "ok":
            doc = await db.reports.find_one(
                {"id": job_id, "$or": [{"user_id": user_id}, {"is_sample": True}]},
                {"_id": 0},
            )
            if doc:
                yield {"node": "final", "status": "ok", "report": doc}


@api.get("/reports/{job_id}/stream")
async def stream_report(job_id: str, user: dict = Depends(current_user)):
    job = await container.job_lifecycle.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    if job.user_id != user["id"]:
        raise _deny_cross_tenant(user["id"], job_id, resource_kind="job")
    return sse_response(_report_stream_events(job_id, user["id"]), stream_name="report")


@api.get("/reports/{job_id}")
async def get_report(job_id: str, user: dict = Depends(current_user)):
    # EQ-3 (01 D-5): every tier scoped to owner+sample. A cross-tenant id at
    # any tier falls through to the next exactly like a nonexistent one would
    # — the caller can't tell "not yours" from "doesn't exist" (§ _deny_cross_tenant).
    doc = await db.reports.find_one(
        {"id": job_id, "$or": [{"user_id": user["id"]}, {"is_sample": True}]},
        {"_id": 0},
    )
    if not doc:
        # maybe still running — return job snapshot (in-memory/Redis, or the
        # persisted Mongo mirror if the in-process one is gone, e.g. restart)
        job = await container.job_lifecycle.get(job_id)
        if job:
            if job.user_id != user["id"]:
                raise _deny_cross_tenant(user["id"], job_id, resource_kind="report")
            return {"status": job.status.value, "id": job_id,
                     "events": await container.events.history(job_id)}
        job_doc = await db.jobs.find_one({"id": job_id, "user_id": user["id"]}, {"_id": 0})
        if job_doc:
            return {"status": job_doc.get("status", "unknown"),
                    "id": job_id,
                    "events": job_doc.get("events", [])}
        raise HTTPException(status_code=404, detail="report not found")
    # ensure scorecard exists for old reports
    if "scorecard" not in doc:
        doc["scorecard"] = compute_scorecard(doc)
        await db.reports.update_one({"id": job_id}, {"$set": {"scorecard": doc["scorecard"]}})
    return {"status": "completed", "id": job_id, "report": doc}


@api.get("/reports")
async def list_reports(ticker: Optional[str] = None, limit: int = 50,
                        user: dict = Depends(current_user)):
    # Login wall means every caller is a real account now, so listing always
    # scopes to the caller's own reports plus the curated public samples —
    # never another user's history.
    q: dict = {"$or": [{"user_id": user["id"]}, {"is_sample": True}]}
    if ticker:
        q["ticker"] = ticker.upper()
    rows = (
        await db.reports.find(q, {"_id": 0, "events": 0, "source_documents": 0})
        .sort("created_at", -1)
        .to_list(limit)
    )
    return {"reports": rows}


@api.delete("/reports/{report_id}")
async def delete_report(report_id: str, user: dict = Depends(current_user)):
    # Scoped to the caller's own reports — unlike the read-side endpoints,
    # deletion is destructive/irreversible, so it can't lean on the report id
    # being an unguessable UUID the way GET/compare do. Without this, any
    # signed-in user could delete another user's report or (since `is_sample`
    # ids are visible to every caller via GET /reports) the shared public
    # samples. Samples have user_id=None, so this also makes them read-only.
    result = await db.reports.delete_one({"id": report_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="report not found")
    await db.jobs.delete_one({"id": report_id})
    # Also evict the in-process task handle — RUNNING_TASKS/JobStore entries
    # are irrelevant once a report is deleted, but leaving a dangling task
    # reference around serves no purpose.
    RUNNING_TASKS.pop(report_id, None)
    return {"deleted": report_id}


# ---------------------------------------------------------------------------
# Learning (03_Learning_Backend_Design.md) — Backend Engineering M2 Phase L.
# Built on the same JobLifecycle/EventBus infrastructure as reports (Part A
# cutover above), sharing one MAX_ACTIVE_JOBS budget via JobKind.LEARNING.
# Response shapes use "id", never "job_id" (02 F-1 — the frontend contract's
# most likely implementation mistake).
# ---------------------------------------------------------------------------

async def _run_explanation(job_id: str, ticker: str, concept: str, query: str,
                           company_name: str | None,
                           prior_brief: str = "",
                           prior_financials: dict | None = None,
                           llm_provider: str | None = None,
                           llm_api_key: str | None = None,
                           llm_base_url: str | None = None,
                           llm_model: str | None = None,
                           user_id: str | None = None) -> None:
    from agents.llm import set_llm_context, reset_llm_context
    _tok = (
        set_llm_context(llm_provider, llm_api_key,
                        light_model=llm_model, heavy_model=llm_model, base_url=llm_base_url)
        if (llm_provider or llm_api_key) else None
    )
    started = asyncio.get_event_loop().time()
    await container.job_lifecycle.mark_running(job_id)
    await db.explanation_jobs.update_one({"id": job_id}, {"$set": {"status": "running"}})

    async def push(ev: dict) -> None:
        await container.job_lifecycle.publish(job_id, ev)
        await db.explanation_jobs.update_one(
            {"id": job_id},
            {"$push": {"events": ev}, "$set": {"updated_at": ev.get("ts", "")}}
        )

    # M6 — job-level parent span, same reasoning as _run_pipeline's (research).
    _job_span_cm = get_tracer().start_as_current_span("pipeline.learning", attributes={"job_id": job_id})
    _job_span = _job_span_cm.__enter__()
    try:
        initial: dict = {"ticker": ticker.upper(), "query": query, "concept": concept, "trace": []}
        if company_name:
            initial["company_name"] = company_name
        if prior_brief:
            initial["prior_brief"] = prior_brief
        if prior_financials:
            initial["prior_financials"] = prior_financials
        final_state: dict = {}
        last_node_name = "unknown"
        async for event in learning_graph.astream(initial, {"recursion_limit": 10}):
            for _node_name, node_state in event.items():
                last_node_name = _node_name
                if not isinstance(node_state, dict):
                    continue
                final_state.update(node_state)
                for t in node_state.get("trace", []):
                    await push(t)
            if await container.job_lifecycle.is_past_deadline(job_id):  # 07 §5.4/LG-11
                deadline_exceeded_total.labels(graph="learning", node=last_node_name).inc()
                raise TimeoutError(f"job exceeded its {settings.job_deadline_s['learning']}s deadline")

        explanation_text = final_state.get("explanation", "")
        if not explanation_text:
            # explainer_node already pushed an "explainer"/"error" trace event
            # (LLM failure or Law 3's zero-citation reject, 03 §5.2) — fail the
            # job rather than persisting an ungrounded/empty explanation.
            completed_at = datetime.now(timezone.utc).isoformat()
            err = "The explanation could not be grounded in the retrieved filings."
            await db.explanation_jobs.update_one(
                {"id": job_id}, {"$set": {"status": "failed", "error": err, "completed_at": completed_at}}
            )
            await container.job_lifecycle.fail(job_id, err)
            pipeline_runs_total.labels(graph="learning", status="failed").inc()
            return

        completed_at = datetime.now(timezone.utc).isoformat()
        explanation_doc = {
            "id": job_id,
            "ticker": ticker.upper(),
            "concept": concept,
            "explanation": explanation_text,
            "source_documents": final_state.get("source_documents", []),
            "company_name": company_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": completed_at,
            "user_id": user_id,
            "cited_sources": final_state.get("cited_sources", []),
        }
        await db.explanations.insert_one(explanation_doc)
        await db.explanation_jobs.update_one(
            {"id": job_id},
            {"$set": {"status": "completed", "explanation_id": job_id, "completed_at": completed_at}}
        )
        await container.job_lifecycle.complete(job_id)
        pipeline_runs_total.labels(graph="learning", status="completed").inc()
    except asyncio.CancelledError:
        completed_at = datetime.now(timezone.utc).isoformat()
        await db.explanation_jobs.update_one(
            {"id": job_id}, {"$set": {"status": "cancelled", "completed_at": completed_at}}
        )
        await container.job_lifecycle.cancel(job_id)  # idempotent — see _run_pipeline's identical note
        pipeline_runs_total.labels(graph="learning", status="cancelled").inc()
        _job_span.set_status(Status(StatusCode.ERROR, "Job cancelled"))  # see _run_pipeline's identical note
    except TimeoutError as e:
        logger.warning("learning pipeline %s: %s", job_id, e)
        err = "The explanation exceeded its time budget and was stopped."
        completed_at = datetime.now(timezone.utc).isoformat()
        await db.explanation_jobs.update_one(
            {"id": job_id}, {"$set": {"status": "failed", "error": err, "completed_at": completed_at}}
        )
        await container.job_lifecycle.fail(job_id, err)
        pipeline_runs_total.labels(graph="learning", status="failed").inc()
        _job_span.set_status(Status(StatusCode.ERROR, err))
    except Exception:
        # Never echo the raw exception — provider SDK errors can embed the API
        # key (mirrors _run_pipeline's identical redaction).
        logger.exception("learning pipeline failed")
        err = "Explanation failed. See server logs for details."
        completed_at = datetime.now(timezone.utc).isoformat()
        await db.explanation_jobs.update_one(
            {"id": job_id}, {"$set": {"status": "failed", "error": err, "completed_at": completed_at}}
        )
        await container.job_lifecycle.fail(job_id, err)
        pipeline_runs_total.labels(graph="learning", status="failed").inc()
        _job_span.set_status(Status(StatusCode.ERROR, err))
    finally:
        if _tok is not None:
            reset_llm_context(_tok)
        RUNNING_TASKS.pop(job_id, None)
        jobs_active.labels(kind="learning").dec()
        pipeline_duration_seconds.labels(graph="learning").observe(
            asyncio.get_event_loop().time() - started
        )
        _job_span_cm.__exit__(None, None, None)


@api.post("/learning/explain")
async def explain_concept(req: ExplainRequest, user: dict = Depends(current_user)):
    ticker = req.ticker.strip().upper()
    concept = req.concept.strip()
    if not ticker or not concept:
        raise HTTPException(status_code=400, detail="ticker and concept are required")

    # Same admin/SSRF gate as /reports/generate (03 §4.3) — llm_base_url is a
    # new server-side-fetch surface here too and must not reopen the SSRF
    # hole the report path already closed.
    if req.llm_provider == "custom" or req.llm_base_url:
        require_admin(user)
    if req.llm_base_url:
        from agents.llm import assert_public_url
        try:
            assert_public_url(req.llm_base_url)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Custom LLM base URL must be a publicly reachable http(s) "
                    "address — the server calls it directly, so localhost and "
                    "private-network addresses aren't allowed."
                ),
            )

    # Fail fast, before a job exists (03 §2 empty-corpus behavior) — cheaper
    # than the streamed backstop for the common case of an un-ingested ticker.
    has_data = await db.filing_chunks.count_documents({"ticker": ticker}) > 0
    if not has_data:
        raise HTTPException(
            status_code=400,
            detail=f"No filings ingested for {ticker}. Ingest a filing first "
                   f"(POST /api/ingest/samples for demo data).",
        )

    comp = await db.companies.find_one({"ticker": ticker}, {"_id": 0})
    company_name = comp.get("name") if comp else None

    # R-1: expanded retrieval query — concept + company + (optional) the
    # context report's own question — composed at the call site only; no
    # change to agents/retrieval.py.
    query = f"{concept} {company_name or ticker}"
    prior_brief = ""
    prior_financials: dict = {}
    if req.context_report_id:
        prior = await db.reports.find_one(
            {"id": req.context_report_id},
            {"draft_report": 1, "extracted_data": 1, "query": 1, "_id": 0},
        )
        if prior:
            prior_brief = prior.get("draft_report", "") or ""
            prior_financials = prior.get("extracted_data") or {}
            if prior.get("query"):
                query += f" {prior['query']}"

    job_id = str(uuid.uuid4())
    await container.job_lifecycle.start(
        job_id, JobKind.LEARNING, user["id"], ticker=ticker,
        deadline_s=settings.job_deadline_s["learning"],
    )
    jobs_active.labels(kind="learning").inc()
    await db.explanation_jobs.insert_one({
        "id": job_id,
        "ticker": ticker,
        "concept": concept,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "context_report_id": req.context_report_id,
        "user_id": user["id"],
        "events": [],
    })
    RUNNING_TASKS[job_id] = asyncio.create_task(
        _run_explanation(job_id, ticker, concept, query, company_name,
                         prior_brief=prior_brief, prior_financials=prior_financials,
                         llm_provider=req.llm_provider, llm_api_key=req.llm_api_key,
                         llm_base_url=req.llm_base_url, llm_model=req.llm_model,
                         user_id=user["id"])
    )
    return {"id": job_id}


@api.post("/learning/{id}/cancel")
async def cancel_explanation(id: str, user: dict = Depends(current_user)):
    job = await container.job_lifecycle.get(id)
    if job is None or job.user_id != user["id"]:
        raise HTTPException(status_code=404, detail="job not found")
    if job.is_terminal():
        return {"id": id, "status": job.status.value}
    task = RUNNING_TASKS.get(id)
    if task and not task.done():
        task.cancel()
    await container.job_lifecycle.cancel(id)
    await db.explanation_jobs.update_one({"id": id}, {"$set": {"status": "cancelled"}})
    return {"id": id, "status": "cancelled"}


async def _learning_stream_events(job_id: str, user_id: str):
    """Mirrors _report_stream_events: injects the completed ExplanationDoc as
    a `final` event right after the terminal `pipeline/ok` (03 §1.2 — the
    `final` event is what useExplanationJob.ts:81-83 writes into the
    react-query cache)."""
    async for ev in container.events.subscribe(job_id):
        yield ev
        if ev.get("node") == "pipeline" and ev.get("status") == "ok":
            doc = await db.explanations.find_one(
                {"id": job_id, "user_id": user_id},
                {"_id": 0, "user_id": 0, "cited_sources": 0},
            )
            if doc:
                yield {"node": "final", "status": "ok", "explanation": doc}


@api.get("/learning/{id}/stream")
async def stream_explanation(id: str, user: dict = Depends(current_user)):
    job = await container.job_lifecycle.get(id)
    if job is None or job.user_id != user["id"]:
        raise HTTPException(status_code=404, detail="job not found")
    return sse_response(_learning_stream_events(id, user["id"]), stream_name="learning")


@api.get("/learning/{id}")
async def get_explanation(id: str, user: dict = Depends(current_user)):
    # EQ-3 (03 §7.3, §10): Learning reads are scoped to the owner — unlike
    # GET /reports/{id}'s accepted-risk unscoped posture, scoping a *new*
    # surface costs one query predicate.
    doc = await db.explanations.find_one(
        {"id": id, "user_id": user["id"]},
        {"_id": 0, "user_id": 0, "cited_sources": 0},
    )
    if doc:
        return {"status": "completed", "id": id, "explanation": doc}
    job = await container.job_lifecycle.get(id)
    if job and job.user_id == user["id"]:
        return {"status": job.status.value, "id": id}
    job_doc = await db.explanation_jobs.find_one({"id": id, "user_id": user["id"]}, {"_id": 0})
    if job_doc:
        return {"status": job_doc.get("status", "unknown"), "id": id}
    raise HTTPException(status_code=404, detail="explanation not found")


@api.get("/companies/trending")
async def trending_companies(limit: int = 8, user: dict = Depends(current_user)):
    """Return the companies with the most generated reports (proxy for interest)."""
    pipeline = [
        {"$group": {"_id": "$ticker", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]
    rows = await db.reports.aggregate(pipeline).to_list(limit)
    tickers = [r["_id"] for r in rows]
    # look up company names
    comp_rows = await db.companies.find({"ticker": {"$in": tickers}}, {"_id": 0}).to_list(len(tickers))
    name_by_ticker = {c["ticker"]: c.get("name") for c in comp_rows}
    # fallback: SEC index
    trending = [
        {
            "ticker": r["_id"],
            "name": name_by_ticker.get(r["_id"])
                    or company_index.lookup_ticker(r["_id"])
                    or r["_id"],
            "count": r["count"],
        }
        for r in rows
    ]
    # If we have very few reports, seed with popular US tickers
    if len(trending) < limit:
        seeds = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "NFLX"]
        have = {t["ticker"] for t in trending}
        for s in seeds:
            if s in have:
                continue
            name = name_by_ticker.get(s) or company_index.lookup_ticker(s)
            if name:
                trending.append({"ticker": s, "name": name, "count": 0})
            if len(trending) >= limit:
                break
    return {"trending": trending[:limit]}


class CompareRequest(BaseModel):
    report_ids: list[str] = Field(min_length=2, max_length=4)


@api.post("/reports/compare")
async def compare_reports(req: CompareRequest, user: dict = Depends(current_user)):
    """Load 2-4 reports side by side for portfolio comparison."""
    # EQ-3 (01 D-5): scoped at the query, same predicate as list_reports —
    # a requested id belonging to another tenant simply isn't in `rows`,
    # naturally excluded rather than special-cased.
    rows = await db.reports.find(
        {"id": {"$in": req.report_ids}, "$or": [{"user_id": user["id"]}, {"is_sample": True}]},
        {"_id": 0, "events": 0, "source_documents": 0},
    ).to_list(len(req.report_ids))
    # preserve requested order
    by_id = {r["id"]: r for r in rows}
    ordered = [by_id[i] for i in req.report_ids if i in by_id]
    excluded = set(req.report_ids) - set(by_id)
    if excluded:
        # Not necessarily cross-tenant — a typo'd/deleted id looks identical
        # here (query-level filtering can't distinguish "not yours" from
        # "doesn't exist" without a second, unscoped query). Logged as a
        # visibility exclusion, not asserted as a denied access attempt.
        logger.warning("compare: requested report(s) not visible to caller: user=%s ids=%s",
                        user["id"], sorted(excluded))
    if len(ordered) < 2:
        raise HTTPException(status_code=404, detail="fewer than 2 reports found")
    return {"reports": ordered}


# ---------------------------------------------------------------------------
# M9.1 — Comparison AI explanation (Documents 41/42/43, frozen).
#
# A separate, additive capability — /reports/compare above is completely
# unmodified (Document 41 §10/§11, Document 43 §4/§21). Reuses the existing
# job infrastructure (JobKind.COMPARISON_EXPLANATION, application/jobs.py's
# JobLifecycle, unchanged) and the existing chat_json/chat_text LLM
# abstraction (agents/llm.py, unchanged) exactly as _run_pipeline/
# _run_explanation already do.
# ---------------------------------------------------------------------------


class ExplainComparisonRequest(BaseModel):
    report_ids: list[str] = Field(min_length=2, max_length=4)
    llm_provider: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model: Optional[str] = None


class _InsufficientResolvedReportsError(Exception):
    """Execution-time resolution (Document 41 §13.2/§16) narrowed the
    authorized set below 2 — the job fails with the exact same message/
    posture compare_reports itself already uses for this case (Document 43
    §12/§16), not a generic AI-failure message."""


async def _resolve_authorized_reports(report_ids: list[str], user_id: str) -> list[dict]:
    """The one EQ-3 owner-or-sample authorization/resolution predicate, reused
    identically at admission time (fast-fail, non-authoritative) and execution
    time (authoritative) — Document 41 §13.2/§16, Document 43 §16. Mirrors
    compare_reports's own query/projection/ordering exactly; never trusts a
    caller-supplied "already authorized" claim."""
    rows = await db.reports.find(
        {"id": {"$in": report_ids}, "$or": [{"user_id": user_id}, {"is_sample": True}]},
        {"_id": 0, "events": 0, "source_documents": 0},
    ).to_list(len(report_ids))
    by_id = {r["id"]: r for r in rows}
    return [by_id[i] for i in report_ids if i in by_id]


def _serialize_explanation_result(artifact: dict, *, id_: str) -> dict:
    """Exact Document 43 §9 ExplanationResult shape — strips internal-only
    fields (identity_key, evidence_fingerprint) and always echoes the
    REQUESTED job id, never whichever job's generation happened to win the
    persistence race for this identity (Document 43 §9's justified id
    coupling; §14.1's canonical-identity indirection — the wire-contract
    `id` is "which job did you ask about," not "what Mongo happened to store")."""
    return {
        "id": id_,
        "comparison_report_ids": artifact["comparison_report_ids"],
        "narrative": artifact["narrative"],
        "sources": artifact["sources"],
        "cited_source_indices": artifact["cited_source_indices"],
        "limitations": artifact["limitations"],
        "evidence_completeness": artifact["evidence_completeness"],
        "generated_at": artifact["generated_at"],
    }


async def _dedup_lookup_or_create_explanation_job(
    resolved: list[dict], report_ids: list[str], user_id: str, identity_key: str,
) -> dict:
    """Document 43 §15/§15.1/§15.2's dedup table, admission-time half —
    admission-time resolution is sufficient for this INITIAL lookup because it
    reuses the identical authorization predicate rerun at execution time;
    execution time remains authoritative and may still diverge, reconciled in
    _run_comparison_explanation (§14.1's reconciliation invariant). Returns
    {"id","status","reused"} (Document 43 §7).

    The durable ARTIFACT is shared across users by canonical identity (it has
    no owner — Document 41 §12.2's identity is report-set + prompt/schema/
    provider/model, not caller). The client-visible JOB REFERENCE this
    function returns is never shared: a caller can only GET/stream/cancel a
    job it owns (server.py's ownership-scoped queries, unchanged), so every
    branch below either finds or creates a job doc scoped to `user_id` —
    never hands back another user's job id, even when the underlying work or
    artifact is legitimately reused across users (e.g. two users comparing
    the same sample reports)."""
    now = datetime.now(timezone.utc).isoformat()

    # 1. Reusable existing artifact? (complete always reusable; partial only if
    #    the evidence state that produced it still matches, §15.1 — never
    #    unconditionally.) The artifact itself is looked up globally by
    #    identity_key (shareable), but the job reference handed back is always
    #    scoped to THIS caller.
    fingerprint = compute_evidence_fingerprint(resolved)
    existing_artifact = await db.comparison_explanations.find_one({"identity_key": identity_key}, {"_id": 0})
    if existing_artifact and (
        existing_artifact["evidence_completeness"] == "complete"
        or existing_artifact.get("evidence_fingerprint") == fingerprint
    ):
        job_doc = await db.comparison_explanation_jobs.find_one(
            {"resolved_identity_key": identity_key, "status": "completed", "user_id": user_id}, {"_id": 0}
        )
        if job_doc:
            return {"id": job_doc["id"], "status": "completed", "reused": True}
        # No job THIS caller owns already points at the shared artifact —
        # either it outlived its 30-day TTL mirror (I-30), or a DIFFERENT
        # user's job produced it first. Either way, create a fresh,
        # already-completed job scoped to the current user pointing at the
        # same shared artifact, rather than ever handing back a job id this
        # caller could never GET (the bug this corrective pass fixes).
        new_id = str(uuid.uuid4())
        await db.comparison_explanation_jobs.insert_one({
            "id": new_id, "report_ids": report_ids, "identity_key": identity_key,
            "active_identity_key": None, "resolved_identity_key": identity_key,
            "status": "completed", "created_at": now, "updated_at": now,
            "completed_at": now, "user_id": user_id, "events": [], "error": None,
        })
        return {"id": new_id, "status": "completed", "reused": True}

    # 2. No reusable artifact — atomically admit a new job, or attach to one
    #    already active FOR THIS USER (Step 10: insert_one + a partial unique
    #    index on active_identity_key, I-29 — not check;await;insert).
    #
    #    Scoped per-user (`f"{user_id}:{identity_key}"`), not globally, for
    #    the same reason as branch 1: a bare identity_key here would let
    #    dedup hand caller B the job id of caller A's still-running
    #    generation, which caller B can never GET/stream/cancel (owner-scoped
    #    by design, unchanged). If two different users' jobs genuinely race
    #    on the same canonical identity, each gets its own job id and each
    #    independently reaches the execution-time artifact dedup in
    #    _run_comparison_explanation (comparison_explanations' own
    #    identity_key unique index, I-31) — whichever finishes first
    #    produces the shared artifact; the other adopts it via the existing
    #    DuplicateKeyError-recovery path there. No job is ever exposed to a
    #    user who doesn't own it, and the artifact is still shared correctly.
    job_id = str(uuid.uuid4())
    active_key = f"{user_id}:{identity_key}"
    new_job_doc = {
        "id": job_id, "report_ids": report_ids, "identity_key": identity_key,
        "active_identity_key": active_key, "resolved_identity_key": None,
        "status": "queued", "created_at": now, "updated_at": now,
        "user_id": user_id, "events": [], "error": None,
    }
    for _attempt in range(2):
        try:
            await db.comparison_explanation_jobs.insert_one(new_job_doc)
            return {"id": job_id, "status": "queued", "reused": False}
        except DuplicateKeyError:
            existing = await db.comparison_explanation_jobs.find_one(
                {"active_identity_key": active_key}, {"_id": 0}
            )
            if existing is not None:
                return {"id": existing["id"], "status": existing["status"], "reused": True}
            # The active job that collided with us just turned terminal
            # between our insert failing and this read — retry once; the
            # partial index only blocks a second *active* row, and none
            # exists now.
    raise InfrastructureError("Could not admit comparison-explanation job.")


async def _run_comparison_explanation(
    job_id: str, report_ids: list[str], user_id: str,
    llm_provider: str | None = None, llm_api_key: str | None = None,
    llm_base_url: str | None = None, llm_model: str | None = None,
) -> None:
    from agents.llm import _active, reset_llm_context, set_llm_context

    _tok = (
        set_llm_context(llm_provider, llm_api_key, light_model=llm_model,
                        heavy_model=llm_model, base_url=llm_base_url)
        if (llm_provider or llm_api_key) else None
    )
    started = asyncio.get_event_loop().time()
    await container.job_lifecycle.mark_running(job_id)
    await db.comparison_explanation_jobs.update_one(
        {"id": job_id}, {"$set": {"status": "running", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    async def push(ev: dict) -> None:
        await container.job_lifecycle.publish(job_id, ev)
        await db.comparison_explanation_jobs.update_one(
            {"id": job_id},
            {"$push": {"events": ev}, "$set": {"updated_at": ev.get("ts", "")}},
        )

    _job_span_cm = get_tracer().start_as_current_span(
        "pipeline.comparison_explanation", attributes={"job_id": job_id}
    )
    _job_span = _job_span_cm.__enter__()
    outcome = "failed"
    try:
        await push({"node": "pipeline", "status": "start", "message": "Explaining comparison"})

        # Execution-time authorization — authoritative, never trusts admission
        # time (Document 41 §13.2/§16, Document 43 §15.2/§16). No snapshot: a
        # fresh read is safe because reports are immutable after creation.
        resolved = await _resolve_authorized_reports(report_ids, user_id)
        if len(resolved) < 2:
            raise _InsufficientResolvedReportsError("fewer than 2 reports found")

        if await container.job_lifecycle.is_past_deadline(job_id):
            # NOT deadline_exceeded_total: that metric's graph/node labels are
            # tied to LangGraph node-boundary semantics (research/learning's
            # real graph.astream() node names, above) — this capability has no
            # graph and no nodes, so a graph="comparison_explanation" label
            # would misrepresent what's running (Document 43 §16/§20,
            # explicitly rejected). comparison_explanation_runs_total's own
            # `outcome` label already exists for exactly this kind of
            # capability-appropriate visibility — reused below via the
            # `deadline_exceeded` outcome value rather than introducing a new
            # metric or a graph-shaped one.
            raise TimeoutError(
                f"job exceeded its {settings.job_deadline_s['comparison_explanation']}s deadline"
            )

        cfg = _active()
        exec_identity_key = compute_identity_key(
            [r["id"] for r in resolved], provider=cfg["provider"], model=cfg["light"]
        )
        fingerprint = compute_evidence_fingerprint(resolved)

        # Reconciliation (Document 41 §14.1, Document 43 §15.2): persistence
        # is always keyed by the EXECUTION-time identity, never the
        # admission-time one used only to admit this job. A cheap early read
        # here is a pure efficiency optimization (skip the LLM call if
        # someone else already produced this exact canonical artifact) — the
        # insert-with-DuplicateKeyError-fallback below is what actually
        # enforces "no two durable artifacts share an identity," atomically.
        existing_artifact = await db.comparison_explanations.find_one(
            {"identity_key": exec_identity_key}, {"_id": 0}
        )
        if existing_artifact and (
            existing_artifact["evidence_completeness"] == "complete"
            or existing_artifact.get("evidence_fingerprint") == fingerprint
        ):
            artifact = existing_artifact
        else:
            await push({"node": "explainer", "status": "start", "message": "Generating explanation"})
            explanation = await generate_explanation(resolved)
            artifact = {
                "id": job_id,
                "identity_key": exec_identity_key,
                "comparison_report_ids": [r["id"] for r in resolved],
                "evidence_fingerprint": fingerprint,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                **explanation,
            }
            try:
                await db.comparison_explanations.insert_one(artifact)
            except DuplicateKeyError:
                # Someone else won the race for this exact execution-time
                # identity between our read above and our insert — their
                # artifact answers the exact same authorized question this
                # generation would have, so adopt it rather than erroring or
                # duplicating.
                fresh = await db.comparison_explanations.find_one(
                    {"identity_key": exec_identity_key}, {"_id": 0}
                )
                if fresh and (
                    fresh["evidence_completeness"] == "complete"
                    or fresh.get("evidence_fingerprint") == fingerprint
                ):
                    artifact = fresh
                else:
                    # The pre-existing doc is itself a stale partial — replace
                    # it. Still a single atomic document write; no lock, no
                    # transaction.
                    await db.comparison_explanations.update_one(
                        {"identity_key": exec_identity_key}, {"$set": artifact}
                    )
            await push({"node": "explainer", "status": "ok",
                       "message": f"Explanation generated ({artifact['evidence_completeness']})"})

        outcome = f"completed_{artifact['evidence_completeness']}"
        completed_at = datetime.now(timezone.utc).isoformat()
        await db.comparison_explanation_jobs.update_one(
            {"id": job_id},
            {"$set": {"status": "completed", "resolved_identity_key": exec_identity_key,
                      "active_identity_key": None, "completed_at": completed_at,
                      "updated_at": completed_at}},
        )
        await container.job_lifecycle.complete(job_id)
        comparison_explanation_runs_total.labels(outcome=outcome).inc()
    except asyncio.CancelledError:
        outcome = "cancelled"
        completed_at = datetime.now(timezone.utc).isoformat()
        await db.comparison_explanation_jobs.update_one(
            {"id": job_id},
            {"$set": {"status": "cancelled", "active_identity_key": None, "updated_at": completed_at}},
        )
        # Idempotent — cancel_comparison_explanation may have already called
        # job_lifecycle.cancel() before interrupting this task; a no-op then.
        await container.job_lifecycle.cancel(job_id)
        comparison_explanation_runs_total.labels(outcome=outcome).inc()
        _job_span.set_status(Status(StatusCode.ERROR, "Job cancelled"))
    except Exception as e:  # noqa: BLE001 — never leak raw provider/validation text to the client
        logger.exception("comparison explanation failed")
        if isinstance(e, _InsufficientResolvedReportsError):
            outcome = "failed"
            err = "fewer than 2 reports found"
        elif isinstance(e, GroundingError):
            outcome = "failed"
            err = "The comparison could not be explained with a fully grounded, cited explanation."
        elif isinstance(e, TimeoutError):
            # See the is_past_deadline check above: capability-appropriate
            # deadline visibility via comparison_explanation_runs_total's
            # `outcome` label, not the graph-shaped deadline_exceeded_total.
            outcome = "failed_deadline_exceeded"
            err = "Explanation generation exceeded its time budget and was stopped."
        else:
            outcome = "failed"
            err = "Explanation generation failed. See server logs for details."
        completed_at = datetime.now(timezone.utc).isoformat()
        await db.comparison_explanation_jobs.update_one(
            {"id": job_id},
            {"$set": {"status": "failed", "error": err, "active_identity_key": None,
                      "updated_at": completed_at}},
        )
        await container.job_lifecycle.fail(job_id, err)
        comparison_explanation_runs_total.labels(outcome=outcome).inc()
        _job_span.set_status(Status(StatusCode.ERROR, err))
    finally:
        if _tok is not None:
            reset_llm_context(_tok)
        RUNNING_TASKS.pop(job_id, None)
        jobs_active.labels(kind="comparison_explanation").dec()
        _job_span_cm.__exit__(None, None, None)


@api.post("/reports/compare/explain")
async def explain_comparison(req: ExplainComparisonRequest, user: dict = Depends(current_user)):
    """M9.1 — separate, additive capability (Document 43 §5-§8). Does not
    modify /reports/compare in any way."""
    # Same admin/SSRF gate as /reports/generate and /learning/explain (Document
    # 43 §6/§19 — inherits the existing BYOK/managed-AI policy verbatim).
    if req.llm_provider == "custom" or req.llm_base_url:
        require_admin(user)
    if req.llm_base_url:
        from agents.llm import assert_public_url
        try:
            assert_public_url(req.llm_base_url)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Custom LLM base URL must be a publicly reachable http(s) "
                    "address — the server calls it directly, so localhost and "
                    "private-network addresses aren't allowed."
                ),
            )

    # Admission-time authorization/resolution — fast-fail convenience, NOT
    # authoritative (Document 43 §16; execution time is, §13.2).
    resolved = await _resolve_authorized_reports(req.report_ids, user["id"])
    if len(resolved) < 2:
        raise HTTPException(status_code=404, detail="fewer than 2 reports found")

    from agents.llm import _active, reset_llm_context, set_llm_context

    _tok = (
        set_llm_context(req.llm_provider, req.llm_api_key, light_model=req.llm_model,
                        heavy_model=req.llm_model, base_url=req.llm_base_url)
        if (req.llm_provider or req.llm_api_key) else None
    )
    try:
        cfg = _active()
        identity_key = compute_identity_key(
            [r["id"] for r in resolved], provider=cfg["provider"], model=cfg["light"]
        )
    finally:
        if _tok is not None:
            reset_llm_context(_tok)

    result = await _dedup_lookup_or_create_explanation_job(resolved, req.report_ids, user["id"], identity_key)
    if not result["reused"]:
        # Genuinely new work — admit through the existing shared JobLifecycle
        # budget (Document 41 §5: one MAX_ACTIVE_JOBS ceiling across every
        # kind) only now, not before the dedup check above, so a reused
        # response never consumes an admission slot.
        await container.job_lifecycle.start(
            result["id"], JobKind.COMPARISON_EXPLANATION, user["id"],
            deadline_s=settings.job_deadline_s["comparison_explanation"],
        )
        jobs_active.labels(kind="comparison_explanation").inc()
        RUNNING_TASKS[result["id"]] = asyncio.create_task(
            _run_comparison_explanation(
                result["id"], req.report_ids, user["id"],
                llm_provider=req.llm_provider, llm_api_key=req.llm_api_key,
                llm_base_url=req.llm_base_url, llm_model=req.llm_model,
            )
        )
    return result


@api.post("/reports/compare/explain/{id}/cancel")
async def cancel_comparison_explanation(id: str, user: dict = Depends(current_user)):
    job_doc = await db.comparison_explanation_jobs.find_one({"id": id, "user_id": user["id"]}, {"_id": 0})
    if job_doc is None:
        raise HTTPException(status_code=404, detail="job not found")
    if job_doc["status"] in ("completed", "failed", "cancelled"):
        return {"id": id, "status": job_doc["status"]}
    task = RUNNING_TASKS.get(id)
    if task and not task.done():
        task.cancel()
    try:
        await container.job_lifecycle.cancel(id)
    except NotFoundError:
        pass  # Redis-resident Job already expired/absent; the Mongo mirror below is authoritative
    await db.comparison_explanation_jobs.update_one(
        {"id": id}, {"$set": {"status": "cancelled", "active_identity_key": None}}
    )
    return {"id": id, "status": "cancelled"}


async def _comparison_explanation_stream_events(job_id: str, user_id: str):
    """Mirrors _learning_stream_events exactly: injects the completed
    ExplanationResult as a `final` event right after the terminal
    `pipeline/ok` event (Document 43 §17's frozen SSE contract — the existing
    convention, unmodified)."""
    async for ev in container.events.subscribe(job_id):
        yield ev
        if ev.get("node") == "pipeline" and ev.get("status") == "ok":
            job_doc = await db.comparison_explanation_jobs.find_one(
                {"id": job_id, "user_id": user_id}, {"_id": 0}
            )
            if job_doc and job_doc.get("resolved_identity_key"):
                artifact = await db.comparison_explanations.find_one(
                    {"identity_key": job_doc["resolved_identity_key"]}, {"_id": 0}
                )
                if artifact:
                    yield {"node": "final", "status": "ok",
                           "explanation": _serialize_explanation_result(artifact, id_=job_id)}


@api.get("/reports/compare/explain/{id}/stream")
async def stream_comparison_explanation(id: str, user: dict = Depends(current_user)):
    job_doc = await db.comparison_explanation_jobs.find_one({"id": id, "user_id": user["id"]}, {"_id": 0})
    if job_doc is None:
        raise HTTPException(status_code=404, detail="job not found")
    return sse_response(
        _comparison_explanation_stream_events(id, user["id"]), stream_name="comparison_explanation"
    )


@api.get("/reports/compare/explain/{id}")
async def get_comparison_explanation(id: str, user: dict = Depends(current_user)):
    job_doc = await db.comparison_explanation_jobs.find_one({"id": id, "user_id": user["id"]}, {"_id": 0})
    if job_doc is None:
        raise HTTPException(status_code=404, detail="job not found")
    if job_doc["status"] == "completed" and job_doc.get("resolved_identity_key"):
        artifact = await db.comparison_explanations.find_one(
            {"identity_key": job_doc["resolved_identity_key"]}, {"_id": 0}
        )
        if artifact:
            return {"status": "completed", "id": id,
                    "explanation": _serialize_explanation_result(artifact, id_=id)}
    return {"status": job_doc["status"], "id": id}


# ---------------------------------------------------------------------------
# M14 — Filing Analysis (Documents 63/64/65/66; §20.1 OAQ-1(D) = PASS).
# Additive: a fourth async LLM surface after Research / Learning /
# Comparison-Explanation. Mirrors _run_comparison_explanation's out-of-graph
# orchestration (Document 65 §11 / OAQ-7) on top of the existing JobLifecycle,
# EventBus/SSE, and agents/llm.py abstractions -- all unmodified.
#
# PERSISTENCE = fallback C (Document 65 §12 / Document 66 §5 C-l / §9.1): no
# `filing_analyses` / `filing_analysis_jobs` collection is authorized (that
# needs a separate 08_MongoDB_Data_Architecture.md + ADR), so a completed
# analysis is held ONLY for the job's lifetime in the in-process buffer below
# -- a direct peer of RUNNING_TASKS -- then evicted. `reused` is therefore
# always False (Document 64 §12 on-demand path; run-to-run textual variation
# is contract-permitted). No Mongo write, no Redis, no Job/JobStore change.
# ---------------------------------------------------------------------------

# ponytail: fallback-C persistence -- a completed analysis lives only in this
# process, only until its max_job_lifetime_s TTL (or a 256-entry oldest-first
# eviction), and not across a restart or a second backend instance (the buffer,
# like RUNNING_TASKS and the auth rate-limiter, assumes a single instance).
# GET after expiry returns {status: completed} with no `analysis`. Upgrade
# path: the Document 65 OAQ-5 durable two-collection store (`filing_analyses` /
# `filing_analysis_jobs`), gated on a separate 08_MongoDB_Data_Architecture.md
# + ADR authorization (Document 66 §9.1) -- deliberately not built here.
_FILING_ANALYSIS_RESULTS: dict[str, tuple[str, dict, float]] = {}  # id -> (user_id, analysis_payload, expires_at_epoch_s)
_FA_MAX_ENTRIES = 256


def _fa_now() -> float:
    return datetime.now(timezone.utc).timestamp()


def _store_filing_analysis_result(job_id: str, user_id: str, payload: dict) -> None:
    now = _fa_now()
    _FILING_ANALYSIS_RESULTS[job_id] = (user_id, payload, now + settings.max_job_lifetime_s)
    for k in [k for k, v in list(_FILING_ANALYSIS_RESULTS.items()) if v[2] <= now]:
        _FILING_ANALYSIS_RESULTS.pop(k, None)
    if len(_FILING_ANALYSIS_RESULTS) > _FA_MAX_ENTRIES:
        oldest = sorted(_FILING_ANALYSIS_RESULTS, key=lambda k: _FILING_ANALYSIS_RESULTS[k][2])
        for k in oldest[: len(_FILING_ANALYSIS_RESULTS) - _FA_MAX_ENTRIES]:
            _FILING_ANALYSIS_RESULTS.pop(k, None)


def _get_filing_analysis_result(job_id: str, user_id: str) -> dict | None:
    entry = _FILING_ANALYSIS_RESULTS.get(job_id)
    if not entry:
        return None
    uid, payload, exp = entry
    if exp <= _fa_now():
        _FILING_ANALYSIS_RESULTS.pop(job_id, None)
        return None
    if uid != user_id:  # job records are owner-scoped (Document 64 §15)
        return None
    return payload


class FilingAnalysisRequest(BaseModel):
    # BYOK field set, verbatim from GenerateRequest / ExplainRequest
    # (Document 64 §9.2). No output-selection parameter (CQ-2). The body is
    # optional -- a bare POST analyses the filing with the server's env key.
    llm_provider: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model: Optional[str] = None


async def _run_filing_analysis(
    job_id: str, ticker: str, doc_id: str, user_id: str,
    llm_provider: str | None = None, llm_api_key: str | None = None,
    llm_base_url: str | None = None, llm_model: str | None = None,
) -> None:
    from agents.llm import reset_llm_context, set_llm_context

    _tok = (
        set_llm_context(llm_provider, llm_api_key, light_model=llm_model,
                        heavy_model=llm_model, base_url=llm_base_url)
        if (llm_provider or llm_api_key) else None
    )
    await container.job_lifecycle.mark_running(job_id)

    async def push(ev: dict) -> None:
        await container.job_lifecycle.publish(
            job_id, {**ev, "ts": datetime.now(timezone.utc).isoformat()}
        )

    async def progress(node: str, message: str) -> None:
        await push({"node": node, "status": "ok", "message": message})

    _span_cm = get_tracer().start_as_current_span(
        "pipeline.filing_analysis", attributes={"job_id": job_id}
    )
    _span = _span_cm.__enter__()
    outcome = "failed"
    try:
        await push({"node": "pipeline", "status": "start", "message": "Analysing filing"})

        # Execution-time (ticker, doc_id) resolution. Reports/filings are
        # immutable after ingest, so a fresh read is safe. 404 non-disclosure
        # (Document 64 §10; Document 59 OD-6).
        filing = await db.filings.find_one({"ticker": ticker, "doc_id": doc_id}, {"_id": 0})
        if filing is None:
            raise NotFoundError("filing not found")

        chunks = await _load_ordered_filing_chunks(doc_id, ticker, context="filing analysis")

        if await container.job_lifecycle.is_past_deadline(job_id):
            raise TimeoutError("deadline")

        result = await analyze_filing(chunks, doc_id, db=db, ticker=ticker, progress=progress)

        if await container.job_lifecycle.is_past_deadline(job_id):
            raise TimeoutError("deadline")

        analysis_payload = {
            "doc_id": filing["doc_id"],
            "ticker": filing["ticker"],
            "company_name": filing.get("company_name"),
            "source": filing["source"],
            "created_at": filing["created_at"],
            "prompt_version": result["prompt_version"],
            "schema_version": result["schema_version"],
            "outputs": result["outputs"],
        }
        _store_filing_analysis_result(job_id, user_id, analysis_payload)

        states = [o["state"] for o in result["outputs"].values()]
        if all(s == "insufficient_evidence" for s in states):
            outcome = "completed_insufficient_evidence"
        elif any(s in ("partial", "insufficient_evidence") for s in states):
            outcome = "completed_partial"
        else:
            outcome = "completed_complete"
        await container.job_lifecycle.complete(job_id)
        filing_analysis_runs_total.labels(outcome=outcome).inc()
    except asyncio.CancelledError:
        outcome = "cancelled"
        _FILING_ANALYSIS_RESULTS.pop(job_id, None)
        await container.job_lifecycle.cancel(job_id)  # idempotent
        filing_analysis_runs_total.labels(outcome=outcome).inc()
        _span.set_status(Status(StatusCode.ERROR, "Job cancelled"))
    except Exception as e:  # noqa: BLE001 — never leak raw provider/validation text
        logger.exception("filing analysis failed")
        if isinstance(e, NotFoundError):
            outcome, err = "failed", "Filing not found."
        elif isinstance(e, TimeoutError):
            outcome, err = "failed_deadline_exceeded", "Filing analysis exceeded its time budget and was stopped."
        elif isinstance(e, FilingAnalysisGroundingError):
            outcome, err = "failed", "Filing analysis could not be produced with fully grounded citations."
        else:
            outcome, err = "failed", "Filing analysis failed. See server logs for details."
        _FILING_ANALYSIS_RESULTS.pop(job_id, None)
        await container.job_lifecycle.fail(job_id, err)
        filing_analysis_runs_total.labels(outcome=outcome).inc()
        _span.set_status(Status(StatusCode.ERROR, err))
    finally:
        if _tok is not None:
            reset_llm_context(_tok)
        RUNNING_TASKS.pop(job_id, None)
        jobs_active.labels(kind="filing_analysis").dec()
        _span_cm.__exit__(None, None, None)


@api.post("/companies/{ticker}/filings/{doc_id}/analysis")
async def create_filing_analysis(
    ticker: str, doc_id: str,
    req: Optional[FilingAnalysisRequest] = None,
    user: dict = Depends(current_user),
):
    """M14 — create an async Filing Analysis job for one filing (Document 64
    §9.1 / Document 65 §13). Additive; changes no existing route."""
    req = req or FilingAnalysisRequest()
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValidationError("ticker required", code="validation_error")

    # Same admin/SSRF gate as every other BYOK surface (Document 64 §9.2 / §15).
    if req.llm_provider == "custom" or req.llm_base_url:
        require_admin(user)
    if req.llm_base_url:
        from agents.llm import assert_public_url
        try:
            assert_public_url(req.llm_base_url)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Custom LLM base URL must be a publicly reachable http(s) "
                    "address — the server calls it directly, so localhost and "
                    "private-network addresses aren't allowed."
                ),
            )

    # (ticker, doc_id) identity — 404 non-disclosure (Document 64 §10; Document 59 OD-6).
    filing = await db.filings.find_one({"ticker": ticker, "doc_id": doc_id}, {"_id": 0, "doc_id": 1})
    if filing is None:
        raise NotFoundError("filing not found")

    job_id = str(uuid.uuid4())
    await container.job_lifecycle.start(
        job_id, JobKind.FILING_ANALYSIS, user["id"], ticker=ticker,
        deadline_s=settings.job_deadline_s["filing_analysis"],
    )
    jobs_active.labels(kind="filing_analysis").inc()
    RUNNING_TASKS[job_id] = asyncio.create_task(
        _run_filing_analysis(
            job_id, ticker, doc_id, user["id"],
            llm_provider=req.llm_provider, llm_api_key=req.llm_api_key,
            llm_base_url=req.llm_base_url, llm_model=req.llm_model,
        )
    )
    # fallback C: no stored artifact -> never a reuse (Document 64 §12).
    return {"id": job_id, "status": "queued", "reused": False}


@api.get("/companies/{ticker}/filings/{doc_id}/analysis/{id}")
async def get_filing_analysis(
    ticker: str, doc_id: str, id: str, user: dict = Depends(current_user)
):
    payload = _get_filing_analysis_result(id, user["id"])
    if payload is not None:
        return {"id": id, "status": "completed", "analysis": payload}
    job = await container.job_lifecycle.get(id)
    if job is None or job.user_id != user["id"]:
        raise HTTPException(status_code=404, detail="analysis job not found")
    return {"id": id, "status": job.status.value}


async def _filing_analysis_stream_events(job_id: str, user_id: str):
    """Mirrors _comparison_explanation_stream_events: inject the completed
    analysis payload as a `final` event right after the terminal `pipeline/ok`
    (the frozen SSE convention — Document 65 §11)."""
    async for ev in container.events.subscribe(job_id):
        yield ev
        if ev.get("node") == "pipeline" and ev.get("status") == "ok":
            payload = _get_filing_analysis_result(job_id, user_id)
            if payload is not None:
                yield {"node": "final", "status": "ok", "analysis": payload}


@api.get("/companies/{ticker}/filings/{doc_id}/analysis/{id}/stream")
async def stream_filing_analysis(
    ticker: str, doc_id: str, id: str, user: dict = Depends(current_user)
):
    job = await container.job_lifecycle.get(id)
    if job is None or job.user_id != user["id"]:
        raise HTTPException(status_code=404, detail="analysis job not found")
    return sse_response(
        _filing_analysis_stream_events(id, user["id"]), stream_name="filing_analysis"
    )


@api.post("/companies/{ticker}/filings/{doc_id}/analysis/{id}/cancel")
async def cancel_filing_analysis(
    ticker: str, doc_id: str, id: str, user: dict = Depends(current_user)
):
    job = await container.job_lifecycle.get(id)
    if job is None or job.user_id != user["id"]:
        raise HTTPException(status_code=404, detail="analysis job not found")
    if job.is_terminal():
        return {"id": id, "status": job.status.value}
    task = RUNNING_TASKS.get(id)
    if task and not task.done():
        task.cancel()
    await container.job_lifecycle.cancel(id)
    _FILING_ANALYSIS_RESULTS.pop(id, None)  # cancellation guarantees the result is not published
    return {"id": id, "status": "cancelled"}


# ---------------------------------------------------------------------------
# Wire router + middleware
# ---------------------------------------------------------------------------

app.include_router(api)


@app.exception_handler(RequestValidationError)
async def _validation_error_handler(request: Request, exc: RequestValidationError):
    # FastAPI's default 422 handler echoes each invalid field's raw value
    # verbatim (pydantic's `input` key) — that would put a too-short password
    # in plaintext in the response body. Strip it app-wide.
    errors = jsonable_encoder(exc.errors())
    for e in errors:
        e.pop("input", None)
    return JSONResponse(status_code=422, content={"detail": errors})


# M2 Phase 1 — additive (app/api/errors.py). No existing route currently
# raises a DomainError, so this changes zero existing responses; it is new
# capability for new code (starting with infrastructure/security/
# authorization.py's require_admin, cut over above).
app.add_exception_handler(DomainError, domain_error_handler)


@app.middleware("http")
async def _correlation_id_and_metrics(request: Request, call_next):
    """M2 Phase 1 — additive request-timing + correlation-id middleware
    (04 O-1: "no correlation identifier... a stack trace in the log is
    unattributable with concurrent jobs"; 10 §11's http_requests_total /
    http_request_duration_seconds). Every request gets a correlation id
    (reused from the client's X-Request-ID if present, so a request can be
    traced end-to-end from a load balancer through this process's logs).
    """
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    set_correlation_id(request_id)
    start = asyncio.get_event_loop().time()
    try:
        response = await call_next(request)
    finally:
        set_correlation_id(None)
    duration = asyncio.get_event_loop().time() - start
    route_path = request.scope.get("route").path if request.scope.get("route") else request.url.path
    http_requests_total.labels(
        method=request.method, path=route_path, status=str(response.status_code)
    ).inc()
    http_request_duration_seconds.labels(method=request.method, path=route_path).observe(duration)
    response.headers["x-request-id"] = request_id
    return response


app.add_middleware(
    CORSMiddleware,
    # Cookie-based sessions cross-origin (dev is the web/ Next.js frontend on
    # :3001 / backend :8001) require credentials allowed AND an explicit
    # origin — "*" is invalid with credentials. Every tool route is gated
    # behind the login wall (Phase 4), so this is load-bearing, not just for
    # manual testing.
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:3001").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _warmup():
    """Preload embedding + rerank models in the background so the first pipeline
    run does not incur ~30-40s of cold-start model download / ONNX load."""
    install_correlation_filter()  # M2 Phase 1 — 04 O-1
    # M2 Phase 4 — activates the tracing infra Phase 1 built and proved safe
    # but left uncalled (14 §4 R-3: "a future 'just call setup_tracing()'
    # change is one line"). Safe with no collector configured (spans are
    # created, not exported — see the module docstring); this is what makes
    # Learning requests carry real spans end-to-end. Guarded so re-entering
    # the startup event (e.g. a test opening multiple TestClient(app)
    # contexts against this same module-level app) doesn't re-instrument an
    # already-instrumented app object.
    global _tracing_started
    if not _tracing_started:
        setup_tracing(app, otel_exporter_endpoint=settings.otel_exporter_endpoint)
        _tracing_started = True
    # M2 Phase 1: infrastructure/mongo/indexes.py's ensure_indexes supersedes
    # agents/auth.py's (08 §5.1's full 25-index set — the original 5 auth
    # indexes plus 20 more, incl. the users.id and filing_chunks.ticker
    # indexes that fixed 08 §1's headline finding: every hot-path query was
    # a full collection scan). agents.auth.ensure_indexes is unchanged and
    # still correct on its own — this call simply supersedes it, matching
    # infrastructure/mongo/indexes.py's own module docstring.
    created = await ensure_mongo_indexes(db)
    logger.info("MongoDB indexes ensured: %d across %d collections",
                sum(len(v) for v in created.values()), len(created))

    # M2 Phase 4 restart-recovery sweep (01 D-6, design doc 03 §7.2): any job
    # still `queued`/`running` in Mongo when this process starts was orphaned
    # by the previous process dying — there is no producer left for it, and
    # without this it would report "running" forever to a polling client.
    # Covers both `jobs` (research) and `explanation_jobs` (Learning).
    now_iso = datetime.now(timezone.utc).isoformat()
    for coll_name in ("jobs", "explanation_jobs"):
        result = await db[coll_name].update_many(
            {"status": {"$in": ["queued", "running"]}},
            {"$set": {"status": "failed", "error": "Server restarted mid-run.",
                      "completed_at": now_iso}},
        )
        if result.modified_count:
            logger.warning("startup sweep: marked %d orphaned %s row(s) failed",
                            result.modified_count, coll_name)

    async def _run():
        from agents.retrieval import _get_embedder, _get_reranker  # noqa: WPS437
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, _get_embedder)
            await loop.run_in_executor(None, _get_reranker)
            logger.info("retrieval warmup complete")
        except Exception as e:
            logger.warning("retrieval warmup failed: %s", e)
        try:
            n = await company_index.load_index()
            logger.info("company index loaded (%d rows)", n)
        except Exception as e:
            logger.warning("company index load failed: %s", e)

    asyncio.create_task(_run())


@app.on_event("shutdown")
async def _shutdown():
    mongo_client.close()
