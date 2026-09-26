# Landing (SCR-01) — Trust Positioning, Footer, Returning-User Routing — Implementation Brief

**Date:** 2026-09-26. **Author:** Docs. **For:** Frontend Engineer (via Docs
Reviewer). **Governing docs (all 🧊 Frozen unless noted):**
[`05_Screen_Inventory.md`](../design/05_Screen_Inventory.md) SCR-01,
[`06_UX_Specifications.md`](../design/06_UX_Specifications.md) SCR-01,
[`07_Wireframes.md`](../design/07_Wireframes.md) SCR-01 + the shared frame,
[`00_Design_Constitution.md`](../design/00_Design_Constitution.md) §15
(Content & Copywriting Principles). Non-frozen, cited for requirements only:
[`planning/01-PRD.md`](../planning/01-PRD.md) §7 ("Living draft") and
[`planning/07-Roadmap-Milestones.md`](../planning/07-Roadmap-Milestones.md)
milestone 5. Current code was read this session: `web/app/(public)/page.tsx`,
`web/components/layouts/{Footer,PublicTemplate}.tsx`, and
`web/features/account-setup/` (`AuthGate`, `useAuthStatus`, `LoginForm`).

## 0. What the frozen docs actually specify (read before §2)

The tracker's Landing row
([`Feature_Parity_Tracker.md`](../governance/Feature_Parity_Tracker.md) §1)
says Landing is "still missing the wireframe's trust-positioning copy and
footer legal content". Read closely, the frozen docs specify **content
types, not copy**:

| Element | What is specified, verbatim | Exact copy specified? |
|---|---|---|
| Trust positioning | 05: "Product value proposition; trust positioning (grounded, explainable, source-traceable)." 07 wireframe: "Trust positioning (grounded · explainable · sourced)". 06: "Information Hierarchy: Value proposition → trust positioning → entry action." | **No.** Three attribute names, no sentences. |
| Footer | 07 SCR-01: "[Legal · Support]"; "Footer: legal/support." Shared frame: "[Legal/Support links]". | **No.** Link categories only: no link targets, no legal text. |
| Returning user | 06 SCR-01 Edge Cases: "Returning authenticated user is routed onward rather than shown marketing." | N/A (behavior, not copy). |
| Copy rules | 00 §15: "informative and neutral — never hype, never marketing"; "never gives recommendations"; "use the frozen vocabulary ... verbatim; never coin synonyms." | Principles only. |

Nothing else in `docs/design/`, `docs/experience_design/`, or
`docs/frontend_architecture/` gives Landing copy, legal text, or a legal or
support destination. This was confirmed by searching all three trees for
landing, footer, legal, privacy, terms, disclaimer, and trust.

Two non-frozen planning docs add a **requirement** but no approved wording:
- PRD §7: "**Not investment advice** — legal disclaimer required (esp.
  India/SEBI)."
- Roadmap milestone 5: "disclaimers, ToS/Privacy".

No Terms of Service or Privacy Policy document exists anywhere in the repo.

The legacy `frontend/src/pages/Landing.jsx` does contain trust copy (e.g.
"Every claim traces back to a source.", "No hallucinated numbers..."). It is
**not** a source here. It predates the frozen baseline, its tone ("No
hallucinated numbers") conflicts with §15's neutral, non-marketing rule,
and parts of it describe product claims no frozen doc approves. The same
discipline that kept Dashboard from porting the legacy stats strip applies.

## 1. Goal

Close Landing's remaining gap against the frozen SCR-01 spec **without
inventing copy**:
- build the trust-positioning region and the returning-user routing, which
  the frozen docs fully determine;
- leave every sentence of product and legal wording to the §5 decisions.

## 2. Scope

**In scope — buildable now, fully determined by frozen docs:**

1. **Trust-positioning region** on `web/app/(public)/page.tsx`. It goes
   *between* the value proposition and the entry actions, per 06's
   hierarchy "value → trust → entry". The current page goes straight from
   value to the CTAs.
   - Three items, labeled with the frozen attribute names verbatim:
     **Grounded**, **Explainable**, **Source-traceable**. These are 05's
     wording; 07's "sourced" is the same attribute, and 05 is the fuller
     form. Docs Reviewer, please confirm the choice.
   - **No body sentences under the labels** until §5 OQ-1 is answered.
   - The region needs no heading of its own. If one is used, it must not
     be product copy beyond the frozen term "trust positioning", which is
     an internal spec term and should *not* be shown to users. The
     simplest compliant build is the three labels alone, as a semantic
     list.
2. **Returning-user routing** (06 SCR-01 Edge Cases):
   - When `useAuthStatus()` (the public surface of
     `@/features/account-setup`) resolves `authenticated`, the page does
     `router.replace("/workspace")`. `/workspace` is the same default
     destination `LoginForm` uses after sign-in.
   - While the status is `loading`, the page still renders its content,
     with the entry actions working immediately. 06 requires
     "Content-first; entry action available as soon as rendered" and "If
     the page cannot fully load, the entry action still functions". So do
     **not** gate Landing behind a spinner the way `AuthGate` gates
     protected routes.
   - `unauthenticated` and identity-fetch errors show the page normally.
     Fail open to marketing: this is a public page, not a protected one.
3. **Tests** in `web/app/(public)/page.test.tsx`:
   - the three trust labels render in the order value → trust → entry;
   - an authenticated status calls `router.replace("/workspace")`;
   - loading and unauthenticated statuses render the page with both CTAs;
   - the existing single-`h1` and jest-axe tests still pass.
   - Per CLAUDE.md, if a test ID is needed, establish
     `web/lib/constants/testIds.ts` rather than inline literals.

**Out of scope, by CTO-2 decision (§5, 2026-09-26). Do not build:**
- any explanatory sentence for the three trust attributes (OQ-1: labels
  only);
- any legal text, including a "not investment advice" disclaimer (OQ-2:
  a product-wide compliance item for real legal review, tracked outside
  this page);
- turning the footer's "Legal · Support" into links (OQ-3: an accepted,
  documented gap).

The existing `Footer.tsx` already renders "Legal · Support" as plain text,
with a doc comment explaining why ("there is no legal-copy source to link
to — inventing either destination now would be a dead link"). That remains
correct and stays untouched by this brief.

**Explicitly not ported from legacy `Landing.jsx`:** the pipeline diagram,
the live brief example, the feature grid, pricing, the FAQ, the
GitHub/MIT/Pricing footer links, and all legacy copy. None of these appear
in the frozen SCR-01 wireframe.

## 3. Approach

- **Components:** the change stays in `page.tsx`, using `foundation/`
  wrappers only (`Text`, and `Heading` if used); never `components/ui`
  directly. The three labels form a plain `<ul>` with the frozen tokens,
  with no raw hex (CLAUDE.md, single light theme). Icons are optional; if
  used, take them from `@phosphor-icons/react`, one each, and mark them
  decorative (`aria-hidden`).
- **Routing:**
  - Import `useAuthStatus` from `@/features/account-setup` (the public
    surface), never from its internals.
  - The redirect lives in a `useEffect` keyed on the status, so the page
    must become a client component or host a small client child. Prefer a
    small client child (e.g. `ReturningUserRedirect`, rendering `null`)
    placed inside the page. That keeps the marketing content
    server-rendered, per the Frontend Architecture Constitution's SEO note:
    "Public, discoverable surfaces (e.g. marketing/landing...) are
    server-rendered".
  - Put the child in the `account-setup` feature and export it from
    `index.ts`, next to `AuthGate`, whose inverse it is. Do not create a
    new feature module for it.
- **Responsive and accessibility** (11 and 12): the three labels stack on
  narrow widths, and the heading order stays a single `h1`. The footer
  landmark (`contentinfo`) is unchanged.

## 4. Acceptance Criteria

- [ ] Landing renders value proposition → three trust labels (Grounded,
      Explainable, Source-traceable, verbatim) → Get started / Sign in, in
      that DOM order.
- [ ] No new user-visible sentence appears anywhere on the page or in the
      footer beyond those three labels. Diff review: the only new string
      literals are the three labels.
- [ ] Signed in: visiting `/` lands on `/workspace` via replace, so Back
      does not return to Landing.
- [ ] Signed out, identity loading, or the identity fetch erroring: the page
      renders in full, and both CTAs work before identity resolves.
- [ ] Marketing content stays server-rendered; only the redirect child is a
      client component.
- [ ] `page.test.tsx` covers the above; jest-axe is clean; the full `web/`
      test suite, typecheck, and lint are green.
- [ ] Live-verified against the running stack in both states, signed out
      and signed in (redirect observed), with a clean console.
- [ ] Tracker: once all the above pass, including live verification,
      Landing is **eligible for promotion to Migrated**, with the promotion
      reviewed as usual. OQ-1–OQ-3 are resolved as decisions, not blockers
      (§5). The row's note must record the accepted deferrals explicitly:
      - trust positioning is labels only, by decision;
      - the footer's "Legal · Support" is deliberately plain text, not an
        oversight, because neither ToS/Privacy nor `/docs` exists to link
        to;
      - "Legal" ties back to the open, product-wide "not investment advice"
        compliance item (OQ-2), so it is not merely a UI nicety being
        deferred.

## 5. Open Questions / Risks — decided by CTO-2, 2026-09-26

- **OQ-1: trust-positioning copy.** The frozen docs give three attribute
  names and no sentences. Options:
  - (a) Ship the labels alone, as §2 builds. This is compliant, but thin.
  - (b) CTO or Product supplies approved one-line descriptions, written to
    §15's rules (neutral, no hype, no recommendations).
  - (c) Adapt existing frozen language. Candidates are the Constitution's
    North Star, "every answer is grounded, every claim is traceable"
    (00 §2), and "grounded (from primary sources, not open-ended memory),
    explainable, and consistent" (00 §8, "How AI earns trust"). This
    language was written as internal design principle, not user-facing
    copy, so repurposing it is itself a copy decision.
  Docs recommended (a) now, then (b) or (c) as a follow-up if wanted.
  **Decision: (a), labels only, verbatim, nothing more.**
- **OQ-2: the "not investment advice" disclaimer.** PRD §7 says this is
  *required* ("esp. India/SEBI"). The PRD is a living draft, not frozen,
  and gives no wording. This is a legal requirement, not a design nicety.
  It arguably belongs on every AI-output surface, not only Landing's
  footer, and its wording should come from whoever owns legal and
  compliance, not from Docs or Frontend. **Risk if left open:** the
  product ships AI research output with no disclaimer at all. It is
  flagged as the most consequential open question here.
  **Decision: does not block Landing, and remains OPEN as its own
  compliance item.** This is not a gap Landing introduces. It is a
  pre-existing, product-wide question about every AI-output surface. By
  explicit CTO-2 direction, **no engineering or Docs session drafts
  compliance or legal wording**; that needs real legal review, not an AI
  judgment call. This is recorded here so it is not silently dropped. The
  user should take it to actual legal/compliance review, and it is tracked
  outside this page's scope. Until it is resolved, AlphaScribe shows AI
  research output with no investment-advice disclaimer on any surface.
- **OQ-3: footer link destinations.** "[Legal · Support]" needs targets.
  - **Legal:** no ToS or Privacy Policy exists (Roadmap milestone 5 lists
    them as future work).
  - **Support:** `/docs`, the only candidate, is the tracker's remaining
    Not Started row.
  Until destinations exist, `Footer.tsx`'s plain-text rendering is the
  correct, non-dead-link state. Question: does Landing reach Migrated with
  the footer as plain text (accepted, documented gap, the same precedent
  as the Comparison and Research Library deferrals), or does it wait on
  real legal pages?
  **Decision: accepted as a documented gap.** The labels stay plain text,
  with no live links. The tracker row must state that this is deliberate,
  and that "Legal" ties back to OQ-2's open compliance item.
- **Risk: the redirect flashing marketing content.** With content-first
  rendering, a signed-in user may briefly see Landing before the replace.
  This is accepted, because 06's "entry action available as soon as
  rendered" outranks hiding a flash for returning users. If it is judged
  unacceptable, the alternative is a server-side session check in the
  `(public)` route (reading the session cookie in a server component). That
  is a larger change touching auth architecture (03.6), and not proposed
  here.
