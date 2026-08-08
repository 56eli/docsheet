# UI Principles & Project-Specific Implementation Suggestions

**Prepared:** 2026-08-08  
**Project:** DocSheet / Hawkins Archive Live Spreadsheet  
**Scope:** The static GitHub Pages catalogue, review workspace, Tabulator table,
responsive layout, accessibility, export flows, and frontend test strategy.

This is a design guide rather than a visual redesign specification. The goal is
to keep future UI changes coherent as the catalogue, review lanes, and edition
model grow.

## 1. Design principles

### P1 — Purpose before metadata
The first screen should answer the visitor's primary question immediately:
“What file/work is this, and what can I do with it?” Internal IDs and
provenance should not compete with the filename, title, series, edition, and
source links.

**DocSheet application:** keep `Proposed File Name`, `Title`, `Series`,
`Item Type`, `Edition`, and `Year-Month` ahead of technical fields. Keep
`Record Type` as a small provenance rail rather than a full text column.

### P2 — Progressive disclosure, not information removal
Advanced information should be one deliberate action away, not permanently
removed. The default view should be calm; Expert columns, row details, the
Columns menu, and Expand everything should expose the complete record for deep
review.

**Implementation:** keep the current Expert columns toggle and drawer, but
make the state obvious, persistent per view, keyboard reachable, and reversible
with Reset current view.

### P3 — Organize by user task
Information architecture should reflect jobs users perform, not the database's
file list. Browse the catalogue, review decisions, and inspect source
inventories are distinct tasks.

**Implementation:** retain the three groups — Catalogue, Review workspace, and
Sources — and consider a Review menu once the 19-tab wall becomes a larger
barrier than a benefit. Keep the most frequent destinations one click away.

### P4 — Make the visual hierarchy predictable
A user should be able to predict what is important from position, size, weight,
and grouping before reading every value. One primary action, one primary
identity, and one primary status should exist per row.

**Implementation:** freeze only the identity rail (`Record Type`, filename,
title); use a restrained header; reserve the accent for active navigation,
primary links, and focus/selection states.

### P5 — Use semantic consistency everywhere
The same state must look and read the same across tables, filters, drawers,
exports, and empty states. Labels must describe the underlying data rather than
an implementation detail.

**Implementation:** centralize status labels/classes; use `Owned`, `Not owned`,
and `Not stated` consistently; keep `CM` compact only inside the cell and use
“Curated master” in the header, tooltip, filter, drawer, and export metadata.
Do not introduce a second label for the same state.

### P6 — Respect column budgets
A wide table is useful only when width is allocated according to information
value. Short controls and badges should never consume the width intended for
long-form identity fields.

**Implementation:** define explicit width budgets for the master view. A good
starting point is:

| Column | Budget | Rationale |
|---|---:|---|
| Record Type | 54px | Compact `CM`/candidate rail; tooltip carries full meaning. |
| Proposed File Name | 340px max | Important, monospace, but must not dominate the frozen rail. |
| Title | 150–560px | Primary human identity. |
| Series | 180px minimum | Avoid truncating the main browsing facet. |
| Notes/reasons | 560px max | Readable in the drawer or wrapped mode, not an endless table column. |
| Short IDs | measured/narrow | Technical fields belong behind Expert mode. |

Measure data-driven widths for content columns, but let the budget override the
measurement for compact controls. Add an automated width assertion for each
critical budget.

### P7 — Optimize for scanning and comprehension
Users scan rows, compare editions, and look for outliers. Long prose belongs
in a drawer or wrapped mode; repeated visual noise belongs in a compact badge or
icon with a tooltip.

**Implementation:** keep the compact default density, muted filename extension,
carrier dots, work-group accent, and wrapped Expand everything mode. Do not put
full URLs or repeated explanatory prose in the default cells.

### P8 — Search and filters should work together
Search is for known terms; facets are for exploration. Both must show the
result count, active state, and an easy way back to the full dataset.

**Implementation:** keep global search across raw values, add discoverable
Series/Year/Type/Format/Owned facets, expose removable chips, preserve filters
per view, and make Clear all filters return the status to the unfiltered count.
Blank values need a named option such as “Not stated,” not an invisible hole.

### P9 — Always show system state and feedback
A static data application still has loading, success, empty, stale, and failure
states. A blank table is ambiguous and a silent export is untrustworthy.

**Implementation:** retain the loading spinner, `aria-busy`, empty-lane cards,
read-only note, Last Updated value, search result count, and explicit load
errors. Add a small “data snapshot” indicator to review/inventory views when a
live refresh candidate has not been accepted.

### P10 — Treat provenance as a product feature
This catalogue is also a research and review tool. Users need to know whether a
row is curated, derived, reviewed, pending, excluded, or merely discovered.
Trust is damaged when those categories look interchangeable.

**Implementation:** distinguish `master`, candidate, derived primary
relationship, and hand-reviewed related material visually and in the drawer.
Show raw row/candidate key, review date/reason, source product ID, and evidence
links in a predictable Provenance section.

### P11 — Accessibility is a baseline, not a phase
Keyboard users, screen-reader users, low-vision users, and users with reduced
motion should have the same core capabilities as pointer users.

**Implementation:** preserve visible focus rings, roving tab navigation, real
button/label semantics, `aria-selected`, `aria-expanded`, `aria-busy`, and
external-link announcements. Never use color alone for status; pair color with
text/icon/tooltip. Keep touch targets at least 44px where practical and test
light/dark contrast for every badge state.

### P12 — Responsive means task continuity
Mobile should not be a shrunken desktop. A user must still search, switch views,
inspect a row, open a link, copy a filename, and export.

**Implementation:** keep horizontal table scrolling for comparison, use the
full-width row-details sheet for record inspection, maintain large close and
control targets, keep search at the top, and avoid placing critical actions in
hover-only affordances.

### P13 — Read-only data needs safe, explicit actions
The published site must not imply that a browser edit is persisted. Actions
that change user state should be clear, reversible, and scoped to the current
view.

**Implementation:** keep generated tables read-only, label exports accurately,
make Copy filename provide confirmation, keep Reset current view separate from
Clear filters, and preserve the raw source in the Original Spreadsheet view.
If an action could alter repository data, link to the declared review input
rather than simulating an edit in the browser.

### P14 — Performance and resilience are UX concerns
A fast table that fails when a CDN is blocked is not resilient. A slow table
that does unnecessary work on every tab switch is not scalable.

**Implementation:** keep per-view JSON splitting and no-pagination scrolling at
this catalogue size; cancel or ignore stale fetch responses during rapid tab
switches; avoid measuring hidden/unused columns repeatedly; consider vendoring
Tabulator assets or providing a local fallback; keep SRI/CSP and test them.

### P15 — Design decisions need contract tests
The UI is a compiled projection of CSV/JSON schemas. A visual preference becomes
a regression when it is not encoded as a contract.

**Implementation:** test view/file/tab parity, published Everything keys,
critical column order/frozen state, width budgets, status labels, keyboard
shortcuts, exports, empty states, and the read-only promise. Keep browser tests
small and user-outcome-focused; use Python tests for generated data contracts.

### P16 — Prefer reversible, incremental changes
The catalogue is used for real review work. Large visual changes can hide data
or break a familiar workflow even when the page looks cleaner.

**Implementation:** ship one IA or interaction change at a time, preserve the
Expand everything escape hatch, record decisions in this document, add a
regression test, and keep a short changelog in the PR description.

## 2. What is already working well

- Filename-first master layout and frozen identity columns.
- Compact `CM` provenance badge with a full tooltip.
- Expert columns and Expand everything for progressive disclosure.
- Faceted filters with removable chips and per-view persistence.
- Explicit empty-state cards for standing intake lanes.
- Row-details drawer, copy filename action, keyboard shortcuts, and external
  link labels.
- Generated JSON view split, read-only tables, CSV export, CSP/SRI, and a
  deterministic Python pipeline.
- Current Record Type fix: a **54px** width budget keeps the first rail compact;
  the full meaning remains in the header/tooltip.
- Task-oriented Jump to navigation groups the 19 views by Catalogue, Review
  workspace, and Sources without removing the direct tab rail.
- Row details now use Identity/Status/Sources/Provenance sections, copy filename
  and copy ID actions, focus trapping, and focus return to the source row.

## 3. Project-specific implementation roadmap

### P0 — Protect the identity rail

1. Keep `record_type` at 54px in the Tabulator column definition and CSS.
2. Keep the `Record Type` header wrapped rather than widening the column.
3. Keep candidate/CM badge text ellipsized with a tooltip.
4. Add/maintain a Playwright assertion that Record Type is no wider than 80px,
   while filename/title/series meet their minimums.
5. Verify both the default reader mode and Expert/Expand everything mode; a
   user setting must not silently undo the width budget.

### P1 — Introduce a formal column configuration

Create one source of truth such as `COLUMN_BUDGETS` in `app.js`:

```js
const COLUMN_BUDGETS = {
  record_type: { width: 54, minWidth: 54, maxWidth: 54, frozen: true },
  proposed_filename: { maxWidth: 340, frozen: true },
  title: { minWidth: 150, maxWidth: 560, frozen: true },
  series: { minWidth: 180 },
  notes: { maxWidth: 560 },
};
```

`buildColumns()` should apply these budgets after measuring content, and the
column-layout spec should read the same contract through observable DOM widths.
This avoids one-off CSS fixes drifting away from the measured-width engine.

### P1 — Make the table modes explicit

Keep three named modes rather than accumulating switches with unclear effects:

- **Browse:** compact, product facts, identity rail.
- **Review:** filters, wrapped cells, row details, provenance columns.
- **Expand:** every column, roomy rows, Expert mode on.

The current settings menu can remain the implementation surface; the mode names
would make the mental model clearer and simplify reset behavior.

### P1 — Strengthen task-oriented navigation

- Keep Everything as the default landing view.
- Add a “Review” menu when tab labels no longer fit comfortably.
- Add a “Sources” shortcut to the Veritas inventory and Filename Proposal.
- Keep stats chips as navigation, but make the destination and row count
  accessible in the button label.

### P2 — Improve review trust

Add a drawer layout with stable sections:

1. **Identity:** filename, title, work, type, edition, year.
2. **Ownership/status:** owned, record type, review status.
3. **Sources:** official/product/streaming links.
4. **Provenance:** raw row or candidate key, source product ID, review date,
   evidence note, decision reason.
5. **Actions:** copy filename, copy ID, open source, close.

This avoids making the user reconstruct evidence from 24 flat fields.

### P2 — Improve keyboard and screen-reader flows

- Add a visible “Keyboard shortcuts” hint for first-time users.
- Add `e` to open the selected row and `c` to copy the filename/ID only when
  the action is available.
- Give the drawer a focus trap and return focus to the originating row on close.
- Add browser tests for focus order, Escape, drawer focus return, and the
  reduced-motion setting.

### P2 — Add explicit UI state telemetry without tracking users

Use development-only `console.info` events or a test hook for:

- view activated,
- JSON load success/failure,
- active filter count,
- export started/completed,
- row drawer opened.

Do not send personal data or browsing history to a remote service. This makes
CI/debugging easier without adding analytics or privacy obligations.

### P3 — Improve resilience and mobile polish

- Vendor the pinned Tabulator assets or implement a local fallback.
- Add a compact refresh/snapshot label to the source/inventory views.
- Test 320px, 768px, and wide desktop layouts.
- Keep the table horizontally scrollable but ensure the identity rail remains
  visible and does not cover the first non-frozen column.

## 4. Acceptance checklist for future UI PRs

A UI PR should answer all of these before merge:

- What user task is improved?
- Which fields/actions become more or less prominent?
- Does the default view remain usable without Expert mode?
- Does the change preserve the identity rail width budget?
- Does it work with keyboard only, dark mode, reduced motion, and mobile width?
- What happens while loading, with zero rows, on fetch failure, and after reset?
- Does CSV export still include the intended columns and rows?
- Is the data read-only behavior still explicit?
- Which Playwright or schema test encodes the new contract?
- Is the change reversible through View settings or a clear navigation path?

## 5. Suggested next UI sequence

1. **Now:** keep and verify the 54px Record Type rail fix.
2. **Next:** formalize `COLUMN_BUDGETS` and add width-budget assertions for the
   frozen identity rail.
3. **Then:** give the drawer stable Identity/Provenance/Actions sections and
   add focus-return tests.
4. **Then:** simplify the 19-tab navigation into task-oriented groups/menu
   behavior without hiding one-click access to the major source sheets.
5. **Finally:** address local asset fallback and deeper responsive/performance
   testing.

The catalogue data model remains the source of truth; these recommendations
should improve comprehension and review ergonomics without changing any
catalogue record.
