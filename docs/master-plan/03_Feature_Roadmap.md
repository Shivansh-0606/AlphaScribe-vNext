# AlphaScribe vNext — Feature Roadmap

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 1.0.0 |
| **Phase** | Product Discovery |
| **Owner** | Product Team |
| **Approved By** | CTO Review |
| **Approval Date** | 2026-07-18 |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | Yes |

**Downstream Dependencies:** PRDs · UX Flows · Wireframes · Design Specifications ·
System Architecture · API Contracts · Database Design · AI Architecture ·
Engineering Tasks · QA Test Plans · Acceptance Criteria

> **Traceability:** The Version 1.0 (MVP) scope is aligned to the approved
> [User Personas](../design/01_User_Personas.md) and
> [User Journeys](../design/02_User_Journeys.md). "Version 1.0" throughout this
> document refers to the **product/MVP release**, distinct from this document's
> baseline version (1.0.0).

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 1.0.0 | 2026-07-18 | Product Team | ✅ Approved Baseline | Initial frozen product baseline. Consolidates prior discovery-phase drafts: journey synchronization (J-01–J-06), cross-document consistency pass (audience alignment, research-continuity and research-report reframing, removal of duplicate/generic items), and recording the AI Conversation Lifecycle as future documentation. No roadmap redesign. |

---

# Roadmap Philosophy

AlphaScribe will be developed in carefully planned phases.

Each release must deliver meaningful value to users while maintaining high engineering quality.

Our philosophy is:

> Build less, but build it exceptionally well.

Every feature added to the platform must support our core mission:

> Reduce hours of manual equity research into minutes.

---

# Product Development Strategy

Instead of building every possible finance feature at once, AlphaScribe will evolve through multiple releases.

Each version focuses on solving one level of user problems before moving to the next.

Version progression:

Research
↓

Analysis
↓

Intelligence
↓

Automation

---

# Version 1.0 — MVP

Goal:

Deliver the best AI-powered equity research experience for retail investors.

> Scope note: The MVP is scoped to the Primary personas — P-01 Retail Investor
> and P-02 Student / Learner — and their approved journeys J-01 through J-06.
> Journeys for the secondary personas (P-03 Professional Analyst, P-04 Long-Term
> Investor, P-05 Content Creator / Finance Writer) are intentionally deferred
> until post-MVP.

## Authentication & AI Setup

- User Registration
- Login
- Social Authentication (Google)
- User Profile
- API Key Management
- BYOK Support
- Managed AI Support
- AI Setup Validation
- Guided Onboarding

---

## Research Workspace

- Beautiful Landing Page
- Research Workspace Home
- Recent Research
- Quick Actions
- Search Bar

---

## Company Research

- Company Search
- Company Overview
- Business Summary
- Financial Highlights
- Key Metrics
- Period-over-Period Performance
- What Changed Since Last Review

---

## Financial Statements

- Income Statement
- Balance Sheet
- Cash Flow
- Quarterly Results
- Annual Results

---

## AI Financial Copilot

- Company Q&A
- Filing Q&A
- Financial Explanations
- Earnings Analysis
- Risk Identification
- Revenue Analysis
- Business Model Explanation

---

## Trusted AI

- Grounded AI
- Explainable AI
- Source Traceability
- Citation Inspection

---

## SEC Filing Analysis

- 10-K Analysis
- 10-Q Analysis
- Filing Summaries
- Risk Factors
- Management Discussion
- Important Changes

---

## Company Comparison

- Compare Multiple Companies
- Financial Ratios
- Revenue Comparison
- Margin Comparison
- Growth Comparison

---

## Learning Mode

- Learner-Level Explanations
- Concepts Explained in Context
- Guided Concept Exploration
- Worked Analysis Examples
- Interpretation Self-Check

---

## Research Reports

- Research Report Generation
- Grounded Conclusions
- Preserved Reasoning
- Source-Backed Insights
- Exportable Research Artifacts

---

## Data Visualization

- Revenue Charts
- Profit Charts
- Margin Charts
- Growth Charts
- Financial Ratio Charts

---

## Research Sessions

- Durable Research Sessions
- Saved Reasoning
- Saved Sources
- Resume Research
- Research History

---

## Deferred to Post-MVP

The following were considered for the MVP but deferred to keep it focused:

- Favorite Companies — removed as duplicative; returning to companies is already
  served by Recent Research (Research Workspace) and Research Sessions, and
  ongoing tracking is covered by Watchlists in Version 1.1.
- Notifications — deferred to Version 1.1, where it is represented concretely as
  Company, Price, and Earnings Alerts under Watchlists.

---

# Version 1.1

Goal:

Increase research productivity.

## Watchlists

- Multiple Watchlists
- Company Alerts
- Price Alerts
- Earnings Alerts

---

## News Intelligence

- Company News
- AI News Summary
- Sentiment Analysis
- Important Events

---

## Earnings Center

- Earnings Calendar
- Earnings Transcript Analysis
- Guidance Comparison
- Surprise Analysis

---

## Advanced Reports

- Custom Report Templates
- Scheduled Reports
- Research Sharing

---

# Version 2.0

Goal:

Professional research workspace.

## Valuation Tools

- DCF Model
- Relative Valuation
- Comparable Company Analysis
- Multiple Valuation

---

## Portfolio Workspace

- Portfolio Tracking
- Portfolio Analytics
- Allocation Analysis
- Performance Tracking

---

## Screeners

- Fundamental Screener
- Technical Screener
- AI Stock Discovery

---

## AI Research Agents

- Earnings Agent
- Filing Agent
- Valuation Agent
- News Agent
- Risk Agent

---

## Collaboration

- Shared Workspace
- Team Notes
- Research Sharing
- Organization Accounts

---

# Future Vision

The long-term roadmap includes:

## Market Intelligence

- Macro Analysis
- Sector Analysis
- Industry Trends
- Economic Calendar

---

## Alternative Data

- Insider Trading
- Institutional Ownership
- Analyst Ratings
- Supply Chain Signals

---

## Predictive Intelligence

- Forecast Models
- AI Scenario Analysis
- Risk Prediction
- Financial Forecasting

---

## Global Markets

- International Stocks
- ETFs
- Mutual Funds
- Bonds
- Commodities

---

## Enterprise

- Bloomberg Migration Tools
- API Access
- Custom AI Models
- Enterprise Security
- Team Administration

---

# Future Documentation

The following are planned **documentation** deliverables, not current MVP
features. They are recorded here so scope stays clear as PRD writing begins.

- **AI Conversation Lifecycle** — future documentation will define how the AI
  copilot behaves across a research session, including conversation continuity,
  follow-up interactions, context retention, conversation history, and research
  session continuity. The MVP delivers the copilot and Research Sessions
  capabilities; the detailed lifecycle model is deferred to that future
  documentation and does not expand MVP scope.

---

# Features Explicitly Out of Scope

The following will NOT be developed until product-market fit is achieved:

- Brokerage Integration
- Live Trading
- Crypto Trading
- Social Investing
- Copy Trading
- Options Trading Platform
- High-Frequency Trading
- Tax Filing
- Personal Finance Management

---

# Prioritization Framework

Every feature request will be evaluated using the following criteria:

1. Does it reduce research time?

2. Does it improve research quality?

3. Does it increase user trust?

4. Does it fit the product vision?

5. Can it be maintained long-term?

If the answer to most of these questions is "No", the feature should not be added.

---

# Success Criteria

Version 1.0 is considered successful if users can:

- Research any public company within minutes.
- Understand financial statements easily.
- Ask contextual financial questions.
- Generate professional research reports.
- Compare companies efficiently.
- Trust AI-generated insights.

---

# Long-Term Goal

AlphaScribe aims to become the world's most intuitive AI-native equity research platform.

We are not competing by adding the most features.

We are competing by delivering the best research experience.

Every release should move AlphaScribe closer to becoming the default workspace for modern equity research.