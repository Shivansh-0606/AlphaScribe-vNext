# AlphaScribe vNext — Requirements Traceability Matrix

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen (baseline; downstream columns grow over time) |
| **Version** | 1.0.0 |
| **Phase** | Product Discovery |
| **Owner** | Product Team |
| **Approved By** | CTO Review |
| **Approval Date** | 2026-07-18 |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | Yes (traceability index) |

**Downstream Dependencies:** PRDs · UX Specifications · Architecture · API ·
Database · Engineering Tasks · QA Tests · Acceptance Criteria

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 1.0.0 | 2026-07-18 | Product Team | ✅ Approved Baseline | Initial matrix with full upstream traceability (Strategy → Vision → Persona → Journey → Roadmap) and placeholders for downstream artifacts. |

---

# Purpose

This matrix is the single index that links every approved product decision to the
downstream artifacts that will implement and verify it. At baseline, the
**upstream** columns (Strategy → Roadmap) are complete; the **downstream** columns
(PRD → Acceptance Criteria) are intentional **placeholders** (`TBD`) to be filled
as those artifacts are authored during the PRD and engineering phases.

Traceability flows in one direction:

```
Product Strategy → Vision → Persona → Journey → Roadmap Item
→ PRD → UX Spec → Architecture → API → Database → Engineering Task → QA Test → Acceptance Criteria
```

Every row must trace back to an approved product decision. No downstream artifact
may exist without a parent row here.

> **Note:** The Product Strategy body is not yet authored (see
> [Product Strategy](../master-plan/01_Product_Strategy.md)). Strategy references
> below point to the intended anchor and are marked accordingly until that
> document is frozen.

---

# Upstream Traceability (Baseline — Complete)

Each MVP roadmap capability is traced to the journey and persona it serves. The
Strategy and Vision columns anchor each capability to approved intent.

| Ref | Product Strategy | Product Vision | Persona(s) | User Journey | Feature Roadmap Item (MVP) |
|-----|------------------|----------------|-----------|--------------|-----------------------------|
| RTM-01 | _Pending_ | Trust-first AI research; BYOK & Managed AI | P-01, P-02 | J-01 | Authentication & AI Setup |
| RTM-02 | _Pending_ | AI-native research workspace | P-01, P-02 | J-01, J-02 | Research Workspace |
| RTM-03 | _Pending_ | Research companies faster | P-01 | J-02 | Company Research |
| RTM-04 | _Pending_ | Understand businesses deeply | P-01, P-02 | J-02, J-05 | Financial Statements |
| RTM-05 | _Pending_ | AI copilot enhances every workflow | P-01, P-02 | J-02, J-04, J-05 | AI Financial Copilot |
| RTM-06 | _Pending_ | Grounded, explainable, source-traceable AI | P-01, P-02 | J-02, J-05 | Trusted AI |
| RTM-07 | _Pending_ | Analyze SEC filings | P-02 | J-05 | SEC Filing Analysis |
| RTM-08 | _Pending_ | Compare companies effectively | P-01 | J-03 | Company Comparison |
| RTM-09 | _Pending_ | Professional capability for everyone | P-02 | J-04, J-05 | Learning Mode |
| RTM-10 | _Pending_ | Explainable, source-backed reports | P-01, P-02 | J-02, J-06 | Research Reports |
| RTM-11 | _Pending_ | Interactive visualizations | P-01 | J-02, J-03 | Data Visualization |
| RTM-12 | _Pending_ | Save research; return without rework | P-01, P-02 | J-06 | Research Sessions |

---

# Downstream Traceability (Placeholders — To Be Completed)

Downstream columns are populated as PRDs and engineering artifacts are authored.
`TBD` indicates a required future link, not an optional one.

| Ref | Roadmap Item | PRD | UX Specification | Architecture Component | API | Database | Engineering Task | QA Test | Acceptance Criteria |
|-----|--------------|-----|------------------|------------------------|-----|----------|------------------|---------|---------------------|
| RTM-01 | Authentication & AI Setup | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| RTM-02 | Research Workspace | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| RTM-03 | Company Research | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| RTM-04 | Financial Statements | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| RTM-05 | AI Financial Copilot | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| RTM-06 | Trusted AI | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| RTM-07 | SEC Filing Analysis | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| RTM-08 | Company Comparison | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| RTM-09 | Learning Mode | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| RTM-10 | Research Reports | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| RTM-11 | Data Visualization | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| RTM-12 | Research Sessions | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

---

# How to Use This Matrix

- **Authoring a PRD:** find the `RTM-##` row for the capability, confirm its
  upstream anchors, and replace the PRD `TBD` with a link to the new PRD.
- **Adding any downstream artifact:** it must attach to an existing `RTM-##` row.
  If no row fits, the work is out of scope until a
  [Change Request](Documentation_Governance.md#change-request-process) adds one.
- **Removing a capability:** requires a Change Request; the row is marked
  Superseded, not deleted.
