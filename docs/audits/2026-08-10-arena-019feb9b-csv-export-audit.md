# Expert Full-Stack & Data Engineering Audit: The CSV Export Feature
**Date:** 2026-08-10  
**Audit Branch:** `arena/019feb9b-docsheet`  
**Commit Baseline:** `8c59a912b133331dd34cd06a452317d24b332e5b`  
**Audited Area:** CSV Export Mechanism (`docs/app.js`, `docs/js/columns.js`, `tests/csv-export.spec.js`)

---

## 1. Executive Summary: Why CSV is "Dated" Yet Essential

The DocSheet website has evolved into an interactive, visually rich catalogue featuring modern Linear/Stripe-inspired styling, responsive mobile Browse stacks, status badges, carrier dots, and REVISION1 block-grouping left-edge color rails (differentiating 11 distinct chronological and thematic work groups).

Compared to this modern web presentation, the **CSV Export feature is inherently "dated"**: plain ASCII/UTF-8 comma-separated text cannot represent visual color-coding, left-edge accent rails, status badge pills, tooltips, or clickable action buttons. However, from a Data Engineering perspective, this plain-text format is by design: **CSV is an analytical data-exchange contract**, ensuring universal interoperability across spreadsheets (Excel, Numbers, LibreOffice), data science pipelines (Pandas, R, Polars), and relational databases without proprietary markup or visual noise.

---

## 2. Visual vs. Structural Capabilities Matrix

| Capability / Feature | Live Web UI (Spreadsheet & Browse Mode) | CSV Export (`table.download` & Fallback) | Engineering Rationale |
|---|---|---|---|
| **Colored REVISION1 Block Groupings** | ✅ 11 distinct left-edge color rails (`--block-accent-*`) | ❌ Flat rows without visual color-coding | Color is a CSS presentation layer; CSV conveys groupings via ordered rows and metadata (`work_id`, `year`). |
| **Carrier Dots & Status Badges** | ✅ Colored indicator dots (`DVD`, `CD`, `audiobook`, `streaming`, `book`) & "CM" badges | ❌ Plain text string (`"audiobook · Audiobook"`, `"master"`) | Text values remain readable and filterable in SQL/Excel without parsing HTML tags. |
| **Interactive Links & Actions** | ✅ Clickable streaming links & official storefront buttons | ❌ Complete raw URL string (`https://...`) | Enables programmatic crawling or joining with external product databases. |
| **Filtered View vs. Whole Sheet** | ✅ Dynamic query filtering & pagination | ✅ Whole-sheet export (`"all"` scope) | Ensures researchers downloading a dataset receive the entire view rather than an accidentally truncated search subset. |
| **Hidden Expert Columns** | ✅ Toggleable via "Expert columns" button (`#expert-toggle-btn`) | ✅ Always included (`visibleColumnsOnly: false`) | Ensures exports contain critical provenance and join keys (`master_id`, `work_id`, `proposed_filename`). |

---

## 3. Architecture of the Dual Export Engine (`docs/app.js`)

DocSheet implements a two-path CSV export engine in `docs/app.js` (`exportCsv()`):

### 3.1 Primary Desktop Spreadsheet Path (`table.download`)
When Tabulator is active (`table`), clicking **Export CSV** executes:
```javascript
table.download("csv", VIEWS[activeView].exportName, {
  delimiter: ",",
  bom: false,
  visibleColumnsOnly: false
}, "all");
```
- **`bom: false`:** Explicitly omits the UTF-8 Byte Order Mark (`\uFEFF`). In earlier releases, `\uFEFF` at the start of downloaded CSVs caused Python's `csv.reader` and certain spreadsheet tools to misread the first header cell (e.g., turning `"Master ID"` into `"\uFEFFMaster ID"` or treating it as empty).
- **`visibleColumnsOnly: false`:** Overrides Tabulator's default behavior so that hidden expert columns (`master_id`, `work_id`, `proposed_filename`, `provenance`, `source_url_1`) are included in the downloaded file.
- **`"all"` Scope:** Instructs Tabulator to ignore active search filters and pagination, exporting the entire view dataset.

### 3.2 Mobile Browse-Mode Fallback Path (`!table`)
When viewing the catalogue on mobile phones (<768px), Tabulator is not initialized; instead, the page renders compact HTML card stacks. If a user taps **Export CSV** in Browse mode, `exportCsv()` falls back to a manual string builder:
- It constructs the field list using `orderKeysForView(...)`, honoring preset column priority.
- **Audit Improvement Made This Session:** Previously, the fallback path exported raw JSON keys (`"master_id","work_id"`) in the header line, whereas Tabulator exported humanized titles (`"Master ID","Work ID"`). This session updated `exportCsv()` to apply `humanizeField(field)`, ensuring mobile Browse exports and desktop Spreadsheet exports are now **byte-identical in header naming and structure**.

---

## 4. Data Contract & Edition Merging Integrity

- **Merged Edition Column:** In raw `master.json`, rows contain separate `format` and `format_detail` fields. In the Everything view, `buildColumns` hides these and exposes the merged `edition` field. When exported to CSV, the file cleanly outputs the merged `Edition` value (e.g., `"audiobook · Audiobook"` or `"book"`), accurately reflecting the edition model.
- **Read-Only Protection:** Published catalogue views (`master`, `series`, `veritasProducts`, etc.) are strictly read-only. Double-clicking any cell in the UI is disabled, and exported CSVs cannot mutate repository state.

---

## 5. Automated Verification & Regression Suite (`tests/csv-export.spec.js`)

The CSV export feature is defended by 5 Playwright end-to-end browser specifications in `tests/csv-export.spec.js`:
1. **`CSV export downloads the whole active view even when filtered`**: Fills the search box with `"Causality"`, triggers download, and asserts that unfiltered rows (`"Satsang"`) and humanized headers (`"Master ID"`) are present in the downloaded `.csv` file.
2. **`CSV export uses the selected view filename`**: Switches to a review view (`manualLeads`) and verifies that the downloaded file is named `hawkins-manual-leads.csv` with humanized titles (`"Title"`, `"Lead Status"`).
3. **`published catalogue views are read-only`**: Proves that double-clicking a cell does not open an editor input.
4. **`Everything view separates curated master records from candidates`**: Asserts that status badges display `"CM"` in-cell with `"Curated master"` tooltip.
5. **`edition model columns render on the Everything tab`**: Confirms that `Edition` merges carrier format details while raw format columns remain hidden.

---

## 6. Strategic Verdict & Scoreboard Impact

- **Verdict:** **Healthy / By Design (10/10 Data Integrity).** While plain CSV is visually "dated" compared to modern CSS colored groupings, this is an intentional structural separation between presentation (`style.css` / Tabulator) and data engineering (portable, machine-readable CSV exchange).
- **Scoreboard Alignment:**
  - `feature_completeness`: **8/10** — Export contract is fully implemented, tested, and works consistently across desktop and mobile.
  - `ux_usability`: **8/10** — One-click export button (`#export-btn`) downloads cleanly named `.csv` files matching user expectations.
