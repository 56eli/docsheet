# 2026-08-09 — Multidisciplinary Project Audit (Web Design, Full-Stack Development, & Data Engineering)

**Project:** `56eli/docsheet` (Live Spreadsheet Pipeline & Curated Hawkins Research Catalogue)  
**Date (UTC):** 2026-08-09  
**Branch:** `arena/019fe80c-docsheet`  
**Commit:** `87bea49c8f89adb356bbfbec79fc99ccbf58abb5`  
**Auditor Roles:** Expert Web Designer, Full-Stack Developer, & Data Engineer  

---

## 1. Executive Summary & System Scorecard

`docsheet` is a dual-pipeline archival spreadsheet and interactive catalogue dedicated to the complete body of work by Dr. David R. Hawkins (lectures, series, books, audio programs, videos, On-The-Road talks, and office sessions). It publishes a responsive, searchable Google Sheets–inspired web table on GitHub Pages, backed by a deterministic data transformation and curation pipeline.

### Architectural Overview
1. **Pass-Through Live Spreadsheet Pipeline:** Ingests the raw spreadsheet (`hawkins archive clone - Sheet1.csv`), trims six always-empty raw columns from the published view per owner ruling, and generates `docs/data.json` without modifying cell contents.
2. **Curated Research Catalogue Pipeline:** Merges raw source records with a reviewed migration ledger (`migration_review_ledger.csv`), review overlays (`data/*.csv`), edition models, official publisher inventories (Veritas Publishing, Hay House, Audible), taxonomy mappings, and owner overrides to output 19 structured catalogue datasets (`docs/*.json`).

### Current Health & Quality Gate Scorecard
| Metric / Dimension | Status | Value / Score | Details |
|---|---|---|---|
| **Pipeline Determinism** | 🟢 PASS | 100% Idempotent | All 6 generator CLI `--check` modes pass with zero drift |
| **Offline Test Suite** | 🟢 PASS | 141 / 141 tests | `python -m unittest discover tests` (133 pipeline/contract + 8 style contrast) |
| **Code Coverage** | 🟢 PASS | 90% TOTAL | Exceeds the 85% repository floor (`.coveragerc`) |
| **Linter Hygiene** | 🟢 PASS | 0 Errors / 0 Warnings | `ruff check .` passes 100% clean across all scripts and tests |
| **Browser E2E Suite** | 🟢 PASS | 25 / 25 specs | Playwright browser smoke tests (`npm run test:e2e` in CI) |
| **Asset Delivery Contract** | 🟢 PASS | SHA-256 Pinned | `app-cf43f33a062c` & `css-71a1e6b2ca25` content hashes locked in manifest |
| **Overall Scoreboard Gate** | 🟡 FAIL (7.8 / 10) | Weighted Effective: 7.8 | Minimal gate is 8.0; fails due to owner scores (5/10 presentation & UX) and open manual CI/Pages workflow cutovers |

---

## 2. Web Designer Audit (Frontend Presentation, UI/UX, & Styling)

### A. Visual Presentation & Layout Design
- **Google Sheets Aesthetic:** The frontend (`docs/index.html`, `docs/style.css`) successfully emulates a crisp, professional Google Sheets layout, featuring frozen header rows, clean tabular gridlines, subtle alternating zebra stripes, and responsive desktop/mobile view transitions.
- **Row Styling & Visual Grouping:**
  - **REVISION1 Block Colors:** 11 distinct color blocks represent content categories and series, rendered using inset box-shadows so they do not collide with table borders.
  - **Work-Family Grouping:** Rows belonging to the same `work_id` are visually grouped using a horizontal `border-top` separator, preventing CSS specificity conflicts with row background accents.
- **Dark Mode & Contrast Accessibility:**
  - Dark mode (`#theme-toggle`) auto-detects user OS preference on first visit and persists selection via `localStorage`.
  - Contrast ratios for lecture, discussion, and office row accents in both light and dark themes are rigorously verified by `tests/test_style_contrast.py`.

### B. Recent UX & UI Enhancements
- **Unlocked Column Resizing & Jitter-Free Scrolling:** Switched Tabulator layout to `fitDataFill` with `renderHorizontal: "basic"` and removed `setMaxHeight()` calls on virtual scroll `renderComplete`, eliminating horizontal scroll rubber-banding and enabling free user column resizing.
- **Wider Prominent Scrollbars:** Widened `.tabulator-tableholder::-webkit-scrollbar` from 12px to 16px with an 8px border-radius thumb for comfortable grab targets.
- **Proposal File Name Readability:** Upgraded lead column font size to `13px` semi-bold (`font-weight: 600`) with high-contrast extension text (`color-mix(in srgb, var(--text) 72%, transparent)`) and removed the hard 340px truncation cap.
- **Work-Family Stripe Grouping & Gentle Zebra Parity:** Softened alternating zebra backgrounds (`#fafafa` light / `#1c1c1c` dark) and implemented `applyWorkFamilyStriping(table)` so consecutive rows belonging to the same `work_id` (such as a 3-set DVD) share the same row background color while alternating work families change color.
- **Header Truncation Resolution:** The "Record Type" header previously suffered from vertical letter-by-letter wrapping. This was resolved by removing `overflow-wrap: anywhere` and `max-width: 54px` in `docs/style.css` and removing the hard column width lock (`{ width: 54, minWidth: 54, maxWidth: 54 }`) in `docs/app.js`.
- **Search Query Highlighting:** Live instant search now highlights matched text snippets inside cells using `<mark class="search-highlight">`, improving scannability across long lecture notes and titles.
- **Responsive Mobile Layouts:** On mobile devices, the default "Everything" sheet automatically switches from a wide Tabulator grid to interactive work-card Browse mode, supported by dedicated "Series" and "Timeline" discovery rails and a persistent "Spreadsheet view" escape hatch.
- **Keyboard Shortcuts & Drawer Accessibility:**
  - Full keyboard navigation is supported (`/` to focus search, `Esc` to clear/blur, `g e` for Everything, `g s` for Series, `?` for keyboard shortcuts modal).
  - Row details drawer (`#row-drawer`) incorporates a robust accessible focus trap (`trapRowDetailsFocus`) and ARIA-labelled close controls.

### C. Design Recommendations & Next Steps
1. **Address Owner's 5/10 UX/Presentation Scores:**
   - **Interactive Visual Overlay Diff Preview:** Create a lightweight browser preview mode allowing the owner to toggle between the raw pass-through view (`docs/data.json`) and the curated master view (`docs/master.json`) side-by-side.
   - **Custom Contrast & Accent Themes:** Give users a settings toggle in `#view-settings-menu` to switch between "Standard REVISION1 Colors" and a "High-Contrast Neutral Palette" for enhanced readability in brightly lit environments.
   - **Mobile Filter Bar Enhancement:** Convert desktop facet filter checkboxes into scrollable, touch-friendly pill chips on mobile viewports.

---

## 3. Full-Stack Developer Audit (System Architecture, CI/CD, & Testing)

### A. System Architecture & Pipeline Design
- **Separation of Concerns:** The architecture clearly demarcates raw data processing (`process_data.py`) from curated catalogue compilation (`build_research_master.py`, `build_catalogue_pages.py`, `map_series_taxonomy.py`, `sync_inventory_mirrors.py`, `reconcile_research_master.py`).
- **Code Modularization:** Core pipeline logic is cleanly factored into `pipeline/helpers.py`, `pipeline/enrichments.py`, `pipeline/validators.py`, and `pipeline/relationships.py`, making generators maintainable and testable.
- **Deterministic Build Outputs:** Every pipeline generator implements `--check` mode, verifying that generated `docs/*.json` and CSV reports match committed state without generating spurious git diffs.

### B. Delivery Contract & Versioning Safety
- **SHA-256 Cache-Busting & Manifest Contract:** `docs/build-manifest.json` locks the SHA-256 hashes of `docs/app.js`, `docs/style.css`, `docs/master.json`, and `docs/data.json`.
- **Visible Build Verification:** `docs/index.html` loads content-versioned assets (`app-cf43f33a062c.js` / `css-71a1e6b2ca25.css`) and displays the active build ID in the page footer.
- **Automated Regression Guard:** `FrontendDeliveryContractTests` in `tests/test_pipeline.py` fails the test suite if an asset hash drifts without updating the manifest and footer build ID.

### C. CI/CD & Scoreboard Governance
- **Persistent Scoreboard System:** The repo maintains `.scoreboard/scoreboard.yml` and `SCOREBOARD.md` to track project health, risk flags, and priority gaps across agent sessions.
- **Open Manual Workflow Risk:** As documented in `.scoreboard/manual-workflow-edits.md`, GitHub Pages deployment currently remains independent of GitHub Actions CI checks.
- **Security & Privacy Hygiene:** Content Security Policy (CSP) headers are declared in `docs/index.html`. Script resources are SRI/hash-pinned, with no tokens or secrets exposed in tracked files.

### D. Full-Stack Recommendations & Next Steps
1. **Apply CI-Gated Pages Cutover:** Owner should apply the instructions in `.scoreboard/manual-workflow-edits.md` to gate GitHub Pages deployments on successful `main` CI workflow completion.
2. **Automated Accessibility Testing in CI:** Integrate an automated `axe-core` accessibility scan into the Playwright E2E suite (`npm run test:e2e`) to catch ARIA or contrast regressions automatically.
3. **Frontend Script Refactoring:** Progressively split `docs/app.js` (2,728 lines) into smaller ES module bundles (e.g., `src/table.js`, `src/filters.js`, `src/mobile.js`) compiled via a lightweight build step or native ES modules.

---

## 4. Data Engineer Audit (Data Pipeline, Ledger Integrity, & Provenance)

### A. Dataset Scale & Ledger Provenance
- **Raw Input Scale:** `hawkins archive clone - Sheet1.csv` contains 374 raw rows (including 31 blank separator rows) across 13 source columns.
- **Curated Catalogue Scale:** `data/research_master_draft.csv` compiles 362 active master records, supplemented by 75 excluded rows (`data/research_master_exclusions.csv`), 134 source overrides (`data/research_master_source_overrides.csv`), and 39 reviewed edition promotions (`data/edition_promotions.csv`).
- **Ledger Integrity:** Every record in `migration_review_ledger.csv` carries explicit provenance, audit history, raw row numbers, and disposition reasons.

### B. Schema Governance & Vocabularies
- **Strict Controlled Vocabularies:** Data generators enforce controlled vocabularies for `item_type`, `format`, and `owned` status. Drift or unexpected values trigger immediate build failures with file and line context.
- **Unique Identifier Stability:** UUIDs (`uuid_1` through `uuid_372`) are strictly assigned; 10 retired duplicate IDs are documented and never recycled.
- **Edition Model:** Works with multiple media releases (audiobooks, CD sets, DVD sets) are grouped under a shared `work_id` while maintaining distinct row-level `format_detail` attributes.

### C. Official Publisher Inventories & Mirror Sync
- **Official Source Registries:** The pipeline integrates reviewed external inventories from Veritas Publishing (192 products, 37 streaming URLs), Hay House (30 products), Audible (27 products), and an International queue (39 items).
- **Automated Mirror Synchronization:** `sync_inventory_mirrors.py` derives and synchronizes inventory mirror columns (`normalized_title_match_count`, `matched_master_titles`, `matched_master_uuids`) from the curated master without hand-editing.
- **Reconciliation Transparency:** `RECONCILIATION_REPORT.md` is automatically generated by `reconcile_research_master.py` and confirms 100% alignment between ledger dispositions and published datasets.

### D. Data Engineering Recommendations & Next Steps
1. **Triage Open Product Issue #18:** Complete the owned-flags cross-check against the lak.nz Google Drive inventory once owner Drive export access is available.
2. **Automated External Link Health Checks:** Create a weekly GitHub Actions workflow that performs non-blocking HTTP HEAD requests against official Veritas and Hay House product URLs to report broken links or redirects.
3. **Continuous Edition Promotion:** Review pending items in `data/edition_candidates.csv` and promote verified multi-format releases into `data/edition_promotions.csv`.

---

## 5. Consolidated Prioritized Action Plan

| Priority | Role | Aspect / Area | Action Item | Next Step / Owner Action Required |
|---:|:---|:---|:---|:---|
| **15** | Web Designer | GitHub Pages presentation | Owner Acceptance of Row Delivery P0 | Request owner to inspect live site footer build ID (`app-cf43f33a062c/css-71a1e6b2ca25`) and confirm visual acceptance |
| **12** | Web Designer | UX / usability | Interactive Overlay Diff & Filter Chips | Implement touch-friendly mobile filter chips and clarify specific owner feedback on 5/10 score |
| **8** | Full-Stack | Maintainability | Modularize `docs/app.js` | Break `docs/app.js` into focused ES modules for view management, Tabulator table initialization, and mobile navigation |
| **4** | Full-Stack | CI/CD & Deploy Readiness | CI-Gated GitHub Pages Deploy | Owner to execute documented settings changes in `.scoreboard/manual-workflow-edits.md` to prevent red-CI Pages deploys |
| **3** | Data Engineer | Content quality | Link Health Check Workflow | Add automated scheduled HTTP status checks for Veritas and Hay House catalog URLs |
| **—** | Data Engineer | Feature completeness | Triage Open Issue #18 | Execute owned-flags reconciliation against lak.nz Drive export once provided |
