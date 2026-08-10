# Mobile view — bloat reduction plan (mobile-only)

**Date:** 2026-08-10 · Session 019feb3e
**Scope:** changes affect **only** `≤720px` viewports and the mobile-browse render path. **Desktop (`≥721px`) is untouched.** No data, pipeline, accessibility, or spreadsheet-grid changes.

## Diagnosis — what is bloated on mobile

On a ~360–390px phone, the catalogue (Everything) view opens in **Browse mode** (work-card stacks). Before the first catalogue card appears, the user scrolls through roughly **430px of chrome** on a ~640–740px-tall screen — i.e. the entire first viewport is chrome:

| # | Section | Mobile height (est.) | Problem |
|---|---|---:|---|
| 1 | **Topbar** | ~150px (**3 rows**) | Brand row + controls that wrap: search + Jump-to fit row 2; **Export + View settings + dark toggle wrap to a 3rd row** |
| 2 | **View summary** | ~80px | Title + `view-meta` cards (Rows / Type) + toolbar all stack |
| 3 | **Browse intro** | ~70px | "Browse mode" eyebrow + a full sentence + "Open spreadsheet" button, shown on **every** load |
| 4 | **Discovery rails** | ~130px | "Explore by series or year" heading + Series rail (**22 chips**) + Timeline rail (**27 chips**), always expanded |
| 5 | *(content)* | — | The actual work-cards only start here |

Payload note: the page also fetches `master.json` (388 KB) + app/style (72 KB each) + 7 modules + Tabulator CDN on first load. Not "visual bloat", but worth a note; trimming it is a larger change and **not** part of this mobile-only plan unless requested.

Already handled (don't re-fix): in Browse mode, the Expert-columns and Columns-menu buttons are already `display:none` via `.mobile-browse-active`.

## Proposed changes (prioritized, each independently shippable)

### P1 — Collapse the topbar to brand + ONE controls row *(highest impact)*
**Today:** search + Jump-to share a row; Export + View-settings + dark-toggle wrap to a third row.
**Change (mobile-only):**
- Fold **Export CSV** and **View settings** into the existing settings flyout (the settings menu already exists and is mobile-friendly), leaving the bar as **Search + Jump-to + (one compact menu) + dark toggle** — fits a single ~340px row.
- Hide the "Jump to" text label on mobile (keep the select).
- Tighten `--topbar-h` to ~44px and reduce padding.
**Files:** `docs/style.css` (`@media (max-width:720px)`) + `docs/app.js` (mobile-only branch: move the export/settings buttons into the settings menu, or add a compact overflow button). Desktop branch untouched.
**Saves:** ~50–60px (one full row).

### P2 — Compact the Browse intro to a dismissible one-liner
**Today:** eyebrow + full sentence + wide button, ~70px, every load.
**Change (mobile-only):** render a single compact line (e.g. "Browse works as cards · Spreadsheet ↗") with a dismiss "×" that persists per browser; remove the paragraph.
**Files:** `docs/app.js` `renderMobileBrowse` (mobile path only) + `docs/style.css` `.mobile-browse-intro` inside the `≤720px` block.
**Saves:** ~35–40px.

### P3 — Collapse the discovery rails behind a "Filters" disclosure *(content-first)*
**Today:** Series + Timeline rails are always expanded (~130px).
**Change (mobile-only):** default the rails to collapsed; show a compact "Filter by series / year" row that expands on tap (reuse the existing facet state + `mobile-discovery-clear` pattern). One tap restores the current behavior.
**Files:** `docs/app.js` `renderMobileDiscovery` (mobile path) + CSS in the `≤720px` block.
**Saves:** ~100px on the default first view; full functionality one tap away.

### P4 — Condense the view-summary on mobile
**Today:** title row + separate Rows/Type meta cards + toolbar.
**Change (mobile-only):** inline the count into the title (e.g. "Everything · 363 rows"); hide the standalone Type meta card (redundant in the master view); keep the Spreadsheet/Browse toggle compact.
**Files:** `docs/app.js` `updateViewSummary` (add a compact-mobile variant) + CSS `@media (max-width:720px)`.
**Saves:** ~40px.

### Net effect
~430px → ~180–200px of chrome: the **first catalogue cards land in the first viewport** instead of after a full scroll. Roughly **−55% mobile chrome** with zero desktop, data, or a11y impact.

## Verification (how we prove it's mobile-only and correct)
- Full suite stays green: 149 Python tests, 3 Node tests, all six `--check` modes, JS syntax.
- `FrontendDeliveryContractTests` after any app.js/style.css edit → refresh content versions + build ID + manifest hashes.
- Manual: load the live/Pages site in a 360/390/414px viewport (Chrome devtools mobile) — confirm first-screen shows content and that toggling Spreadsheet/Filters/Export still works; confirm desktop (`≥721px`) is byte-identical in behavior.
- (Local Playwright is blocked by the sandbox Chromium download, so browser verification runs in CI.)

## Out of scope (explicit)
Desktop layout, the data pipeline/catalogue, the controlled vocabularies, accessibility (focus traps, ARIA, reduced-motion), CSV export contract, and the Tabulator spreadsheet grid. Payload trimming is a separate, larger effort and is **not** included unless you want it.
