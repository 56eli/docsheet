# Spreadsheet UX Review

**Reviewed:** 2026-08-03
**Scope:** `docs/index.html`, `docs/app.js`, `docs/style.css`, and the generated JSON-backed Pages workspace.

## Short answer on CSV export

The CSV export code path is still present and wired correctly: `docs/index.html` has the `#export-btn` button, `docs/app.js` binds it to `exportCsv()`, and `exportCsv()` calls Tabulator's built-in `table.download("csv", VIEWS[activeView].exportName, { delimiter: ",", bom: true })` for the currently active/filtered view.

I added Playwright browser smoke tests for CSV export in `tests/csv-export.spec.js`, wired by `playwright.config.js` and the new `npm run test:e2e` script. In this sandbox, the test definitions list successfully, but Chromium download failed with TLS/network resets, so the actual browser click/download test should be certified in GitHub Actions or another environment with working Playwright browser downloads. A CI workflow file was drafted but could not be pushed because the configured GitHub App lacks `workflows` permission for workflow-file updates.

## Best steps to make the spreadsheet more user friendly

### 1. Add view explanations and counts

Users currently land on many tabs with similar table mechanics but different meanings. Add a compact description panel above the table that changes per view:

- what the view represents,
- whether rows are source records, master records, candidates, products, or relationships,
- whether edits are temporary,
- row count and filtered count,
- recommended reviewer action for that view.

**Impact:** High. This reduces confusion between master data, product inventory, review queues, and generated views.

### 2. Replace full raw URLs with readable link labels

Many columns contain long URLs that dominate the table. Render them as labels such as:

- `Veritas product`
- `Audible listing`
- `Evidence`
- `Source override`

Keep the raw URL in tooltip/copy action/export.

**Impact:** High. Tables become much easier to scan without losing provenance.

### 3. Freeze or prioritize key columns per view

Every sheet currently derives columns from JSON keys. Add per-view column presets:

- frozen first column/title/status columns,
- sensible widths,
- hidden low-priority technical fields by default,
- a column chooser to reveal everything.

Example for Everything: freeze `title`, keep `item_type`, `series`, `year`, `owned`, and source links prominent; move `uuid` and raw provenance fields later or hide by default.

**Impact:** High for everyday use.

### 4. Add a row details drawer

Wide spreadsheet rows are hard to read. Clicking a row could open a side panel/modal with:

- title and key metadata,
- all source links,
- notes/evidence,
- relationship summaries,
- copy buttons for UUID/source URLs.

**Impact:** High. Keeps the table compact while preserving full detail.

### 5. Make filters easier than a single status dropdown

The current review filter is useful but only exposes one detected status-like field. Improve with:

- filter chips for common statuses,
- multi-select status filters,
- quick filters like `Owned`, `Missing source`, `Unmatched`, `Manual candidate`, `Needs decision`,
- per-view saved default filters.

**Impact:** High for review workflows.

### 6. Improve global search feedback

Search works across all columns, but users do not see why a row matched. Add:

- highlighted matched text,
- active filter badges,
- a clear-all filters button,
- optional column-specific search.

**Impact:** Medium/high.

### 7. Clarify temporary editing or disable it on review sheets

The footer says edits are session-only, but double-click editing can still mislead reviewers. Options:

- disable inline editing entirely for generated/review sheets,
- or make edits enter a clear temporary sandbox mode,
- or add an explicit unsaved-changes banner after any edit.

**Recommendation:** Disable editing by default for review/product sheets unless there is a planned persistence mechanism.

**Impact:** High for data governance.

### 8. Add better export choices

Current export downloads the active Tabulator view. Make it more explicit:

- `Export filtered rows`
- `Export all rows in this view`
- `Export selected rows` if row selection is added,
- include active view/filter metadata in filename or a companion README.

**Impact:** Medium. Also makes export behavior less ambiguous.

### 9. Add browser tests for core UX

Add Playwright tests that load the local site and verify:

- every tab loads,
- search filters rows,
- status filter combines with search,
- CSV export triggers a download,
- dark mode toggles,
- URL cells render as links,
- no console errors on boot.

**Impact:** High for confidence, especially because CSV export cannot be fully certified by syntax checks alone.

### 10. Improve mobile/tablet behavior

Wide Tabulator grids are desktop-friendly but mobile-hostile. Add one of:

- compact card view on small screens,
- row details-first mobile layout,
- horizontal-scroll affordance and sticky title column.

**Impact:** Medium depending on audience.

## Suggested implementation order

| Priority | Improvement | Why first |
|---:|---|---|
| 1 | Add per-view descriptions/counts | Implemented in `docs/index.html`, `docs/app.js`, and `docs/style.css`; each tab now shows purpose, row count, type, and export filename. |
| 2 | Add browser test for CSV export and tab loading | CSV export smoke tests are added; full browser execution is pending an environment that can download Chromium. |
| 3 | Disable or clarify session-only editing | Prevents accidental trust in unsaved edits. |
| 4 | Add link labels + copy tooltips | Link labels implemented for URL-heavy columns; copy buttons remain future work. |
| 5 | Add per-view column presets/frozen key fields | Implemented: key columns are reordered, width-tuned, and frozen per view; low-priority technical fields move right instead of being hidden so exports remain complete. |
| 6 | Add column chooser | Implemented: users can hide/show visible columns per active view and restore all columns. |
| 7 | Add row details drawer | Implemented: click any table row to inspect all fields in a readable side drawer. |
| 8 | Upgrade filters/search feedback | Implemented active filter chips and clear-all behavior; matched-text highlighting remains future work. |
| 9 | Add explicit export modes | Removes ambiguity around filtered/all exports. |

## Minimal next UX task

The first UX slice is now implemented: view metadata, CSV-export smoke tests, readable URL labels, column ordering/frozen key fields, and a column chooser. The next smallest high-value slice is to either disable/clarify session-only editing or add explicit export modes (`filtered`, `all visible`, and later `selected`).
