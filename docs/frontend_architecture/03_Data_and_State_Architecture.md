# AlphaScribe vNext — Data & State Architecture

| Field | Value |
|-------|-------|
| **Document Status** | ✅ Approved in Principle (CTO) — Refinement Pass Applied |
| **Version** | 0.1.1 |
| **Owner** | Frontend Architecture |
| **Approved By** | CTO — approved in principle |
| **Department / Milestone** | Frontend Architecture · M3 — Data & State Architecture |
| **Governed by** | [Constitution](01_Frontend_Architecture_Constitution.md) · [02 Application Architecture](02_Application_Architecture.md) (frozen) |
| **Last Updated** | 2026-07-19 |
| **Source of Truth** | Yes — parent of the M3 data/state documents (03.1–03.15 detail it) |

## Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-19 | Frontend Architecture | Draft (approved in principle) | Initial Milestone 3 parent document. |
| 0.1.1 | 2026-07-19 | Frontend Architecture | Refinement pass | CTO refinement pass: metadata standardized across the package; documents 03.12–03.15 and architecture sequence diagrams added. No approved architectural decision changed. |

## Purpose

Establish the **complete frontend data architecture**: what categories of data/state exist, who owns each,
where each lives in the layered architecture, how they flow, and how the system stays resilient. This is
the parent of Milestone 3; documents 03.1–03.11 detail each dimension. It **architects** data and state —
it implements no stores, hooks, or clients (Constitution §2; milestone constraint).

## Scope

**In scope:** the data/state taxonomy, ownership map, lifecycle overview, and the boundaries between state
categories. **Out of scope:** implementation of stores/hooks/API clients; product/design/backend
redesign; the detailed treatments delegated to 03.1–03.11.

## Dependencies

- **Governing:** [Constitution](01_Frontend_Architecture_Constitution.md) §4.1 (Clean Architecture), §4.3
  (SoC), §4.9 (Type Safety), §4.10 (Explicitness / predictable data flow), §4.12 (Stable Public
  Interfaces), §4.13 (Fail Fast), §4.15 (Observability), §5.4 (stack), §6 (Boundaries); [02 Application
  Architecture](02_Application_Architecture.md) (the layers), [02.6 UI Layer](02.6_UI_Layer_Architecture.md)
  (state-/data-binding sub-layers), [02.2 Feature Organization](02.2_Feature_Organization.md),
  [02.7 Module Dependency Rules](02.7_Module_Dependency_Rules.md).
- **Frozen upstream:** [Information Architecture](../design/03_Information_Architecture.md) (entities &
  relationships), [States](../design/13_States.md), [Product Vision](../master-plan/02_Product_Vision.md)
  (trust-first, best-effort data), Design Constitution Law 6 (never lose work); frozen **login-wall auth**
  (stdlib opaque sessions — project guide).

## Architectural Decisions

### AD-1 — Five categories of state, each with a single owner (no duplication)
All frontend data is classified into exactly five categories; **each datum has one authoritative owner**
and is never copied into another category (the "prevent duplicated state" requirement, and §4.10 predictable
ownership):

| Category | Definition | Owner (technology) | Detail |
|----------|------------|--------------------|--------|
| **Server state** | Data owned by the backend (companies, filings, statements, AI responses, sessions, reports) — remote, shared, cached client-side | **TanStack Query** (in the Application layer) | [03.2](03.2_Server_State_Strategy.md), [03.5](03.5_Caching_Strategy.md) |
| **Client (UI) state** | Ephemeral/session UI concerns (companion open/collapsed, active section, filters/selection, watchlist) | **Zustand** (feature-scoped) | [03.1](03.1_State_Management_Strategy.md) |
| **Form state** | In-progress input in a form until submission | **React Hook Form** | [03.8](03.8_Form_Architecture.md) |
| **URL / route state** | Navigable, shareable location + non-sensitive params | **Router** (App Router) | [02.3](02.3_Routing_Architecture.md) |
| **Derived state** | Values computed from the above | **Computed at read time** — never stored | [03.10](03.10_Data_Flow_Principles.md) |

**The cardinal rule:** *server data is never mirrored into a client store; form values are not duplicated
into client state; derived values are computed, not stored.* One datum, one home.

### AD-2 — Client state vs. server state is the primary boundary
The clearest, most consequential separation (a quality requirement): **anything the backend owns is server
state (Query); anything only the UI owns is client state (Zustand).** If a datum could be requested from or
persisted to the backend, it is server state. This single test resolves most ownership questions and is
enforced by the dependency rules ([02.7](02.7_Module_Dependency_Rules.md)).

### AD-3 — Data lives along the layered architecture
Mapping to [02 AD-1](02_Application_Architecture.md):
- **Integration layer** — the typed API client + Zod validation; the trust boundary where remote data
  becomes trusted, typed frontend models ([03.3](03.3_API_Layer_Architecture.md), [03.9](03.9_Validation_Strategy.md)).
- **Application layer** — owns state: server-state cache (Query), client state (Zustand), form state (RHF),
  and the use-cases/mutations that change them.
- **UI layer** — *binds* state into presentation (state-/data-binding sub-layers, [02.6](02.6_UI_Layer_Architecture.md));
  presentational components never fetch or own state.

### AD-4 — One predictable, unidirectional data flow
Data flows **down** (as props into presentation), events flow **up** (to use-cases) — one direction, always
([02.6 AD-4](02.6_UI_Layer_Architecture.md); §4.10). Detailed in [03.10](03.10_Data_Flow_Principles.md).

### AD-5 — Data architecture upholds the frozen product guarantees
- **Never lose work (Law 6):** state ownership + persistence + caching are designed so in-progress research
  survives navigation, error, and timeout, and Resume Session restores context ([03.5](03.5_Caching_Strategy.md),
  [03.11](03.11_Error_Boundary_and_Recovery.md)).
- **Trust-first:** grounding/traceability originate server-side and are preserved intact client-side; AI
  content stays distinct and sourced (server state never fabricated or silently mutated).
- **Best-effort data:** partial/failed external data degrades to the frozen Partial Failure/Timeout/Offline
  States, never a crash ([03.4](03.4_Data_Fetching_Strategy.md), [03.11](03.11_Error_Boundary_and_Recovery.md)).
- **Fail fast (§4.13):** invalid/unexpected data is caught at the boundary and surfaced, never silently
  carried forward.

## Data Lifecycle (overview)

```
Request (use-case) → Integration layer (fetch over contract → validate → map to model)
   → Application layer stores it: server-state cache (Query) — the client's working copy of server truth
      → UI binds & renders (progressive: summary → detail), announcing changes accessibly
   → Mutation (use-case) → Integration → server → cache updated/invalidated (± optimistic) → UI re-renders
Client (UI) state (Zustand) lives independently for UI concerns; Form state (RHF) lives until submit;
Derived state is computed on read. None duplicates another.
```

## Design Rationale

A small, explicit taxonomy with single ownership is the most reliable way to prevent the classic
frontend failure of duplicated, drifting state (§4.10). Separating client from server state lets each be
managed by the tool built for it (Zustand for ephemeral UI, TanStack Query for remote/cached data),
which maximizes maintainability and scalability while keeping the design implementation-agnostic. Anchoring
data in the layered architecture keeps behavior out of presentation and preserves the trust and
never-lose-work guarantees structurally.

## Alternatives Considered

- **A single global store for everything** (server + UI) — rejected: forces manual caching/invalidation,
  duplicates server truth, and tangles concerns (contra §4.3, "prevent duplicated state").
- **Server state cached inside Zustand** — rejected: reinvents TanStack Query's caching poorly and
  reintroduces duplication; Query owns server state.
- **Storing derived values** — rejected: creates a second source of truth that drifts; derived state is
  computed (§4.10).

## Trade-offs

- **Two state systems (Zustand + Query) vs. one:** more concepts to learn, but each is simpler and correct
  for its job; the boundary (AD-2) makes the choice mechanical. Accepted.
- **Strict single-ownership vs. convenience copies:** occasionally binding across a boundary is more
  verbose than a quick copy, but copies are exactly what corrupts state over time. Accepted.

## Risks

- **Category leakage** (server data creeping into Zustand, or derived values stored). *Mitigation:* AD-2
  test + dependency rules ([02.7](02.7_Module_Dependency_Rules.md)) + review.
- **Stale-as-fresh** (cache showing outdated data as current, harming trust). *Mitigation:* freshness
  philosophy ([03.5](03.5_Caching_Strategy.md)); server remains authoritative.
- **Lost work** on error/nav. *Mitigation:* AD-5 + [03.11](03.11_Error_Boundary_and_Recovery.md).

## Future Extension Points

- New server entities (roadmap features) enter as new Query domains behind the integration layer — no
  change to the taxonomy (§4.14).
- Offline-first depth (persisted cache) extends [03.5](03.5_Caching_Strategy.md) without changing ownership.
- Real-time/collaborative data (future) attaches as a new server-state transport, still Query-owned.

## References to Previous Milestones

M1 [Constitution](01_Frontend_Architecture_Constitution.md) §4.1/§4.3/§4.9/§4.10/§4.12/§4.13/§4.15/§5/§6;
M2 [02](02_Application_Architecture.md)/[02.2](02.2_Feature_Organization.md)/[02.6](02.6_UI_Layer_Architecture.md)/[02.7](02.7_Module_Dependency_Rules.md).
Frozen: IA, States, Product Vision, Design Law 6, login-wall auth.

---

*Frontend Architecture · Milestone 3 · Document 03 (parent) · v0.1.0 (Draft)*
