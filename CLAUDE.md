# AlphaScribe — project guide for Claude

AI equity-research assistant: a LangGraph agent pipeline turns SEC/BSE filings
into grounded research briefs, served by FastAPI to a Next.js UI.

## Architecture

- **Backend** (`backend/`): FastAPI (`server.py`) + a LangGraph pipeline in
  `agents/`. Flow: `retriever → (extractor ‖ tone) → synthesizer →
  fact_checker`, with a conditional router that retries the synthesizer or
  ends (`agents/graph.py`). State is a `TypedDict` in `agents/state.py`.
- **Auth is a login wall** (`agents/auth.py`): every tool endpoint requires a
  session (`current_user` dependency in `server.py`); only Landing, Docs,
  `/health`, and `/auth/*` are public. Stdlib-only — `hashlib.scrypt` for
  password hashing, `secrets.token_urlsafe` opaque session tokens hashed at
  rest in a Mongo `sessions` collection (no JWT, no `bcrypt`/`passlib`). This
  is a deliberate, intentional design — not dead scaffold to prune. Do not
  strip it or reintroduce a JWT/OAuth dependency.
- **LLM access** goes through `agents/llm.py` only — `chat_text` / `chat_json`.
  It is multi-provider (Gemini, OpenAI-compatible, Anthropic) with per-request
  keys via a `contextvar`. Do not call provider SDKs directly from nodes.
- **Retrieval** (`agents/retrieval.py`): hybrid BM25 (`rank-bm25`) + dense
  (`fastembed`) with a reranker. Data in MongoDB via `motor` (async).
- **Frontend** (`web/`): Next.js 15 (App Router), React 19, TypeScript strict.
  Routes/composition in `app/`, presentational components in `components/`
  (`foundation/` design-system wrappers + `ai/`, `research/`, `layouts/`),
  one module per IA domain in `features/` (`ui/application/integration/internal`
  + a sanctioned `index.ts` public surface — never import a feature's
  internals from outside it), shared code in `lib/`. Governed by the frozen
  docs in `docs/frontend_architecture/` — an implementation need that
  conflicts with one of them is a stop-and-raise-a-CR situation, not a
  silent judgment call. The legacy Create React App (`frontend/`, craco,
  React Router) is a **frozen, read-only reference implementation** — do not
  add features to it, do not point tooling at it, and touch it only for a
  critical bug fix if absolutely necessary. It stays in the repo until
  `docs/governance/Feature_Parity_Tracker.md` reaches 100% migrated and a
  CTO-approved Legacy Frontend Removal Plan authorizes deleting it — do not
  delete `frontend/` on your own initiative.

## Conventions

- **Package manager is npm**, not yarn. Lockfile is `web/package-lock.json`;
  there is no `yarn.lock`. `scripts/run.py` installs with plain `npm install`.
  Never add a `yarn.lock`.
- **Frontend imports use the `@/` alias** (`@/lib/...`, `@/components/...`),
  configured in `web/tsconfig.json`.
- **Toasts use `sonner` directly** (`import { toast } from "sonner"`).
- **This repo now uses shadcn/ui primitives** (`web/components/ui/`, Radix +
  `class-variance-authority`, plus the `cn()` helper in
  `web/lib/utils/cn.ts`) — this reverses the old CRA-era "no shadcn" rule,
  which only applied to the retired `frontend/` app. Per
  `web/README.md`/`docs/frontend_architecture`, `components/ui` is the raw
  primitive layer and must **never** be imported outside
  `components/foundation`; features and pages import only `foundation/`
  wrappers. Do not import `components/ui` directly from a feature.
- **Icons**: `@phosphor-icons/react`. **Charts**: `recharts`. **Markdown**:
  `react-markdown`. Reach for these before adding anything new — neither is
  installed in `web/` yet since no chart/markdown-rendering feature has been
  built there; add them when one is.
- **Test IDs**: the CRA-era convention lived at
  `frontend/src/constants/testIds/alphascribe.js`; `web/` has no product
  features yet, so no equivalent exists — establish one (e.g.
  `web/lib/constants/testIds.ts`, applied via `data-testid`) when the first
  feature screen is built, rather than inline string literals.
- **Client persistence**: the CRA-era `usePersistedState` (sessionStorage)
  and watchlist store (`useSyncExternalStore`) have no `web/` port yet —
  re-establish an equivalent under `web/lib/state/` when the first feature
  that needs it is built, consistent with the state-ownership rules in
  `docs/frontend_architecture/03_Data_and_State_Architecture.md`.
- **Single light theme.** The app uses a warm-light / editorial-fintech theme:
  a cream paper canvas, ink-navy type, and an emerald→teal signature accent.
  `web/styles/tokens.css` defines exactly one token set — there is
  deliberately no theme toggle and no second (dark) token set. Keep new UI on
  these tokens — no raw hex in components. Do not add a theme toggle or a
  second token set.

## Dependencies

Keep both dependency manifests lean — they were deliberately pruned of an
unused scaffold. Before adding a dependency, confirm nothing already installed
(or the stdlib / platform) does the job. Auth exists (see Architecture above)
but is stdlib-only; do not add JWT, OAuth, or cloud-SDK auth dependencies.
Password-reset OTP email goes through the existing `httpx` dep to Resend
(`agents/notify.py`) — no email SDK.

## Backend specifics

- Python 3.11, Pydantic v2. LLM structured output is validated against the
  schemas in `agents/schemas.py`.
- Scoring (`agents/scoring.py`) is intentionally dependency-free (RAGAS-lite,
  stdlib `re` only). Keep it that way.
- External data sources are best-effort: BSE/yfinance failures must return
  `None` and fall back, never crash a request (see `agents/ingest.py`).
- Login and password-reset OTP attempts are rate-limited by a process-local
  in-memory counter in `agents/auth.py` (`is_rate_limited`/`record_hit`),
  keyed by email only (not IP — see the comment on `/auth/login` in
  `server.py`). Fine for the single-instance backend; would need Mongo/Redis
  if this ever scales to multiple instances.

## Running & testing

- One command: `python scripts/run.py` (sets up venv + portable MongoDB +
  deps, then starts all three services). Ports: backend `8001`, frontend
  `3001`, MongoDB `27017`.
- Backend tests (`backend/tests/`) are live HTTP tests against a running
  server, run with pytest-xdist. **Do not change `pytest.ini`'s `addopts`**
  (`-n 2 --dist loadscope`) — the suites assume that layout.
- The `backend_test_iter*.py` files are additive per-feature suites, not
  superseded snapshots; keep them.

## Deliberate shortcuts

Shortcuts with a known ceiling are marked with a `ponytail:` comment naming the
ceiling and upgrade path (currently one, in `agents/ingest.py`). Preserve these
markers; don't silently "fix" the thing they intentionally defer.
