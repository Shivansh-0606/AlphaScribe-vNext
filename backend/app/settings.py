"""Centralized, validated configuration (M2 Phase 1 "Configuration" scope;
06 AD-9). One typed `Settings` object replaces the ~24 scattered
`os.environ.get(...)` reads across server.py/agents/*.py — this module does
not remove those call sites yet (that is each module's own Phase migration,
e.g. agents/llm.py's env reads move when infrastructure/llm/ fully replaces
it in a later phase); `Settings` is additive infrastructure new code can
depend on today, and existing code can adopt incrementally without a
flag-day cutover, matching the strangler-fig discipline (06 AD-4).

Fails fast at construction, mirroring web/lib/config/env.ts's own AD-5
("Invalid/missing config FAILS FAST... rather than surfacing as a confusing
runtime error") — the frontend already does this; the backend didn't.
"""
from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    # env_file=None deliberately: server.py already calls
    # load_dotenv(ROOT_DIR / ".env") once, at the true entrypoint, before
    # Settings is constructed. A second independent .env load here would be
    # a second place "which .env wins" has to be reasoned about — exactly
    # the kind of hidden import-time side effect 06 AD-1/ADR-003 exists to
    # eliminate, not reintroduce one layer up.

    environment: Environment = Environment.DEVELOPMENT

    # --- datastores ---
    mongo_url: str = Field(validation_alias="MONGO_URL")
    db_name: str = Field(validation_alias="DB_NAME")
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")

    # --- CORS (10 SD-2) ---
    cors_origins: str = Field(default="http://localhost:3001", validation_alias="CORS_ORIGINS")

    # --- secrets with insecure defaults (10 SD-3) ---
    otp_pepper: str = Field(default="dev-insecure-otp-pepper", validation_alias="OTP_PEPPER")
    resend_api_key: str = Field(default="", validation_alias="RESEND_API_KEY")
    admin_emails: str = Field(default="", validation_alias="ADMIN_EMAILS")

    # --- job execution limits (07 §5) ---
    max_active_jobs: int = Field(default=8, validation_alias="MAX_ACTIVE_JOBS")
    job_deadline_research_s: float = Field(default=300.0, validation_alias="JOB_DEADLINE_RESEARCH_S")
    job_deadline_learning_s: float = Field(default=120.0, validation_alias="JOB_DEADLINE_LEARNING_S")
    # M9.1 — a single chat_json call, not a multi-node graph (Document 41 §5/§13.1),
    # so a much shorter budget than research/learning is appropriate.
    job_deadline_comparison_explanation_s: float = Field(default=60.0, validation_alias="JOB_DEADLINE_COMPARISON_EXPLANATION_S")
    job_deadline_grace_s: float = Field(default=30.0, validation_alias="JOB_DEADLINE_GRACE_S")
    max_job_lifetime_s: float = Field(default=600.0, validation_alias="MAX_JOB_LIFETIME_S")

    # --- LLM ---
    llm_provider: str = Field(default="gemini", validation_alias="LLM_PROVIDER")
    llm_allow_private_base_url: bool = Field(default=False, validation_alias="LLM_ALLOW_PRIVATE_BASE_URL")

    # --- observability ---
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    otel_exporter_endpoint: str = Field(default="", validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    prometheus_enabled: bool = Field(default=True, validation_alias="PROMETHEUS_ENABLED")

    # --- feature flags (free-form, not yet consumed by anything —
    # deliberately empty by default; see the module docstring on YAGNI) ---
    feature_flags: dict[str, bool] = Field(default_factory=dict)

    @field_validator("cors_origins")
    @classmethod
    def _no_wildcard_cors(cls, v: str) -> str:
        # 10 SD-2: "*" is invalid with allow_credentials=True anyway (the
        # ASGI layer would reject it), but failing here gives a readable
        # error at startup instead of a confusing CORS failure at request
        # time.
        if "*" in v.split(","):
            raise ValueError('CORS_ORIGINS must be an explicit origin list, not "*" (10 SD-2)')
        return v

    @model_validator(mode="after")
    def _production_secret_gates(self) -> "Settings":
        # 10 SD-3: fail startup rather than silently degrade in production.
        if self.environment is not Environment.PRODUCTION:
            return self
        problems: list[str] = []
        if self.otp_pepper == "dev-insecure-otp-pepper":
            problems.append(
                "OTP_PEPPER is unset or equals the committed dev default — "
                "OTP hashes would be offline-brute-forceable (10 T-03/SD-3)."
            )
        if not self.resend_api_key:
            problems.append(
                "RESEND_API_KEY is unset — password-reset OTPs would be "
                "written to logs at WARNING (10 T-21/SD-3)."
            )
        if problems:
            raise ValueError(
                "Refusing to start with ENVIRONMENT=production and an insecure "
                "config:\n  - " + "\n  - ".join(problems)
            )
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def admin_email_set(self) -> set[str]:
        return {e.strip().lower() for e in self.admin_emails.split(",") if e.strip()}

    @property
    def job_deadline_s(self) -> dict[str, float]:
        return {
            "research": self.job_deadline_research_s,
            "learning": self.job_deadline_learning_s,
            "comparison_explanation": self.job_deadline_comparison_explanation_s,
        }


def load_settings() -> Settings:
    """The one place Settings is constructed from the environment — callers
    (the container, tests) always go through this, never `Settings()`
    directly, so a future change to how config is sourced (e.g. a secret
    manager in production) has exactly one call site to change."""
    return Settings()  # type: ignore[call-arg]  # values come from env, not kwargs
