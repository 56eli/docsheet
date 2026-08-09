# Presentation & UX Improvement Proposal — 2026-08-09

> **📦 ARCHIVED (2026-08-09):** the proposal is fully implemented (Phases A–D)
> and its implementation notes live with it here. Re-verification and any
> follow-up work are tracked via the scoreboard aspects
> `github_pages_presentation` / `ux_usability`.

**Status:** ✅ **IMPLEMENTED (Phases A–D, owner-approved "full plan" 2026-08-09)** —
see the implementation notes at the bottom. Re-verification is pending the
owner's reaction/re-score; AI scores are unchanged until a re-audit.
**Driven by:** owner user scores `github_pages_presentation = 5/10`,
`ux_usability = 5/10` (scoreboard aspects `github_pages_presentation`,
`ux_usability`, related: `accessibility`, `performance`, `repo_organization`).
**AI baseline view:** the current site is feature-rich (19 views, filters,
browse mode, dark mode — AI scores 9/9/8); the gap between AI 9 and owner 5
means the *experience*, not the feature set, is what falls short. This plan
targets first impressions, findability, and polish — the things a feature
list cannot capture.

---

## What the site is (context for the plan)

A personal, curated catalogue of David R. Hawkins material (362 master
records; lectures/books/discussions/highlights; DVD/CD/audiobook/streaming;
Veritas + Hay House + Audible + Nightingale-Conant sources) rendered as a
read-only spreadsheet with 19 views. It is also the owner's review workspace
for the curation pipeline. Two audiences: **visitor** (browse/learn what
exists, what is owned) and **owner** (review lanes, decisions, exports).

## Diagnosed friction points (from code + data review)

1. **No first impression.** The page opens straight into a dense Tabulator
   grid — no title context, no summary of what this is, no entry points.
   A visitor has to know the tabs already.
2. **Spreadsheet-first on desktop, browse-first only on mobile.** Desktop
   users never get the friendly Browse/Series/Timeline experience that
   mobile users get — the best UI is hidden behind a phone breakpoint.
3. **19 tabs in 3 groups** = overwhelming information architecture for a
   visitor; review workspace tabs are mixed with catalogue tabs.
4. **No collection narrative.** The data is rich (series, years, owned
   status, formats) but nothing surfaces "what do I own / what's missing /
   what does the collection look like" — the most compelling story for a
   collector's archive (and directly relevant to open issue #18).
5. **Series and Timeline are rails on mobile only** — no desktop equivalent,
   no series landing pages, no year-based browsing.
6. **Search is powerful but invisible** — no hint of what it does, no
   suggestions, no way to search by series/year from a friendly UI.
7. **Visual polish is utilitarian** (Google-Sheets-inspired): fine for the
   review workspace, flat for a presentation.
8. **No guided first-run / help** beyond the keyboard-shortcuts overlay.

## Proposed improvements (grouped, with effort estimates)

### Phase A — First impression & landing (highest impact, smallest effort)

- **A1. Welcome/overview hero above the table on the Everything view**
  (dismissible): project title, one-line description, key stats chips
  (already built in the stats strip — reuse), and quick links:
  *Browse series →*, *Timeline →*, *What's in the collection →*.
  Effort: small (HTML/CSS/JS, reuses existing chips).
- **A2. Desktop Browse mode.** Port the mobile Browse UI (work stacks,
  Series rail, Timeline rail) to a desktop layout option — "Browse / Table"
  toggle for the Catalogue group instead of Browse being phone-only.
  Effort: medium (responsive rework of existing mobile components).
- **A3. Series landing strip on the Everything view** — clickable series
  cards (name, record count, year range, owned count) that filter the table
  (data already exists; facets already filter). Effort: small–medium.

### Phase B — Information architecture & findability

- **B1. Split visitor vs. reviewer navigation.** Collapse Review workspace +
  Sources tabs into a single "Review" button (opens the current tab strip in
  a dropdown/secondary bar); Catalogue group (Everything, Series, Timeline,
  Compilations) stays prominent. Effort: medium (IA + CSS).
- **B2. Search upgrade:** placeholder hints ("Search titles, series, years…
  press / to focus"), visible search help, and series/year quick-filter
  buttons in the search area. Effort: small.
- **B3. Series & year landing views** (read-only "cards" views): pick a
  series → card list of its works with owned badges and links; year →
  chronological listing. Effort: medium (new views, data already present).

### Phase C — Collection story (tie-in with issue #18)

- **C1. Collection overview card(s):** owned vs not-owned vs unknown
  breakdown per series/format/year (data present: `owned` 295 true / 25
  false / 42 blank), e.g. "You own 82% of the 2002–2011 lecture series."
  Effort: small (computed client-side from master.json).
- **C2. Wishlist/missing view:** "Not owned" quick view (already filterable;
  make it a one-click chip). Effort: trivial.
- **C3. When issue #18 lands** (owner cross-checks against the lak.nz
  Drive), surface reconciliation results in the same cards. Effort: later.

### Phase D — Polish & trust

- **D1. Typography/color pass:** better type scale, improved card/badge
  styling, consistent spacing; keep the spreadsheet aesthetic for review
  views. Effort: medium.
- **D2. Loading & transitions:** skeleton loading for tab switches, smoother
  view transitions, `prefers-reduced-motion` respect. Effort: small.
- **D3. Accessibility pass:** run axe-core on the deployed site; fix
  findings (scoreboard `accessibility` currently 8/medium confidence).
  Effort: small–medium.
- **D4. Empty/edge states copy polish** (e.g. "No works match…" →
  friendlier + suggestions). Effort: trivial.

## What I will NOT do unless asked

- No redesign of the review workspace (it is a tool, not a showcase).
- No new dependencies (keep the site dependency-free beyond Tabulator).
- No changes to catalogue data or pipeline.
- No `.github/workflows/*` edits (deployment stays as-is).

## Proposed sequencing

1. A1 + A3 + C1 + C2 (quick wins, one commit) — immediate visible change.
2. A2 (desktop browse) + B1 (navigation split) — the structural moves.
3. B2 + D1 + D4 (polish).
4. B3 + D3 (new views + a11y verification).
5. C3 once issue #18 has owner input.

Each phase keeps all six `--check` modes and the 126-test suite green; the
19 browser specs get extended per phase (following the existing spec
patterns).

## Implementation notes (2026-08-09, after owner approved "full plan")

- **A1 ✅** Catalogue overview hero above the table on the Everything view:
  title, one-line description, quick actions (Browse cards / Series overview /
  Collection overview / Not owned), dismissible ("Show overview" restores it;
  persisted per browser).
- **A2 ✅** Desktop Browse cards: new toolbar toggle on the Everything view
  (desktop only; phones keep their own mode). Reuses the work-card UI —
  cards, edition stacks, and Series/Timeline discovery rails — in a
  responsive multi-column layout.
- **A3 ✅** Series strip (chips with counts) above the table; clicking filters
  the catalogue and scrolls to the table.
- **B1 ✅** "Review workspace" nav toggle collapses/expands the review +
  sources tab row (default expanded; persisted). All 20 tabs remain in the
  DOM and reachable.
- **B2 ✅** Search placeholder/hint updated ("Search titles, series, years…
  (press /)") with a title tooltip; the existing `/` and `?` shortcuts stay.
- **B3 ✅** New **Series** tab (Catalogue group): a client-side Series browser
  card grid (records, owned count, year span) built from master.json; picking
  a series opens the Everything view filtered to it. Implemented as a
  client-rendered view rather than a new JSON contract.
- **C1 ✅** Collection overview cards: overall owned / not-owned / not-stated
  plus per-series progress bars (top 8 series by size).
- **C2 ✅** "Not owned" one-click action in the hero (sets the Owned facet).
- **D1 ✅** Typography/color/card polish for hero, chips, cards, nav toggle;
  review views keep the spreadsheet aesthetic.
- **D2 ✅** Loading skeleton in place of the plain "Loading…" text; new
  transitions guarded by `prefers-reduced-motion`.
- **D3 ⚠️** Static accessibility pass on the new controls (aria-labels,
  aria-expanded/aria-controls, aria-pressed, roles) + new browser spec
  asserting them. An automated axe-core scan still cannot run in the Arena
  sandbox (no browser download) — scheduled for CI/follow-up.
- **D4 ✅** Friendlier empty/edge copy in browse mode and the series landing.

**Tests:** new `tests/presentation-ux.spec.js` (7 browser tests; suite now
26). All six `--check` modes and 126/126 Python tests remain green.

**Deviations from the proposal text:** the standalone "Series & year landing
views" (B3) is shipped as the Series browser + the existing Series/Timeline
rails; a separate year-landing view was folded into the Timeline rail to keep
the view contract unchanged. No new dependencies; no pipeline or workflow
changes.

## Questions for the owner (still open — please react)

1. Does the new first impression (hero + overview + series strip) address
   the 5/10? What is still missing?
2. Is the target audience mostly *you* (reviewer) or mostly *visitors*
   (sharing the catalogue)? This decides how far the visitor-facing polish
   should go.
3. Any specific complaint behind the 5/10 — e.g. "too cluttered",
   "doesn't look like a real site", "can't find X", "slow"?
4. Should the Series tab replace the Everything tab as the landing view?
