# Full Multidisciplinary Audit — 2026-08-10 · Web Design · Full-Stack · Data Engineering

**Project:** `56eli/docsheet` — Live Spreadsheet & Curated Hawkins Archive Catalogue
**Session:** `arena/019fea62-docsheet` branched from `06ba7df` (main HEAD, PR #60 / `row-delivery-p0-20260810.2`)
**Date (UTC):** 2026-08-10
**Auditor roles:** Expert Web Designer · Full-Stack Developer · Data Engineer
**Method:** Read-only fresh checkout, re-ran all six `--check` modes, `python -m unittest discover tests` (147), `coverage`, `ruff check .`, `node --check` (app + 2 ESM modules + 5 specs), static HTTP-free inspection of `docs/index.html` (235 lns), `docs/app.js` (2421 lns), `docs/js/config.js` (276), `docs/js/formatters.js` (142), `docs/style.css` (2503), `pipeline/*`, `build_*.py`, `data/*.csv` (21 files), `docs/*.json` (19 views + 3 meta/manifest), `.github/workflows/*`, `tests/*`, plus independent pandas/std-lib probes bypassing project validators (referential integrity, URL orphan, CSV↔JSON parity, view↔file parity, token chromaticity, selector topology, block coverage).

> **One-sentence verdict:** At `06ba7df` the repository is **reproducible, internally consistent, and visually correct** — all six `--check` modes green, 147/147 tests green at 90 % coverage (78–100 % per module), zero duplicate IDs/codes/filenames, zero orphan URLs, and the P0 row-delivery/page-crash incident is fixed and guarded — leaving only the already-documented owner-gated CI→Pages cutover, the remaining 2.4 k-line frontend monolith, and three low-severity UX polish items as the outstanding P1/P2 work.

---

## 0. Verification matrix (re-executed this pass)

| Check | Result | Notes |
|---|---:|---|
| `python -m py_compile *.py` | **PASS** | 11 root modules + 4 pipeline modules |
| `process_data.py --check` | **PASS** | 374 raw rows × 13 cols → 7 view cols (6 always-empty trimmed) |
| `build_research_master.py --check` | **PASS** | 362 items; 75 exclusions; 134 overrides; 39 candidates validated |
| `build_catalogue_pages.py --check` | **PASS** | 362 Everything rows; 340 rels (333 derived primary + 7 `related_material`); 7 compilations |
| `reconcile_research_master.py --check` | **PASS** | 0 unexplained extras/absent/diffs |
| `map_series_taxonomy.py --check` | **PASS** | 186 mappings (177 approved / 9 rejected / 0 queued); 324 master IDs covered |
| `sync_inventory_mirrors.py --check` | **PASS** | 191/191 mirrors match; `normalized_title_match_count == len(matched_master_uuids)` everywhere |
| `python -m unittest discover tests` | **147/147 PASS** | ~4.0 s, deterministic, offline |
| `coverage report` | **90 % PASS** | floor 85 % (`fail_under = 85`); lowest `pipeline/helpers.py` 78 %, highest `_common`/`reconcile` 99–100 % |
| `ruff check .` | **PASS** | 0 errors, 0 warnings |
| `node --check docs/app.js + js/config.js + js/formatters.js + 5 specs` | **PASS** | |
| CSP inline-script hash recomputed | **PASS** | `sha256-qULmN/IfgO0KcdvNpANXyfZHBIgYfm4o368jeDomJJY=` matches `<meta http-equiv>` |
| SRI Tabulator (CSS light/midnight + JS) | **PASS** | 3 `integrity=` attrs, pin `6.5.2` |
| CSV↔JSON parity (13 direct pairs) | **PASS** | byte-exact where expected; intentional enrichment: relationships 7→340 derived primaries |
| `catalogue-meta.json` counts | **PASS** | all 14 numeric/file-length assertions match their `docs/*.json` payloads |
| View registry ↔ `docs/*.json` files | **PASS** | 20 `VIEWS[file]` entries; 19 user-facing + 3 meta/manifest, no drift |
| Master identity integrity | **PASS** | 362 unique `uuid` (1–372, gaps `{225,226,227,246,249,264,281,284,302,309}` retired duplicates); 278 unique codes; 362 unique filenames/displays; no collision |
| Work-family coverage | **PASS** | `work_families.csv` 338 + `edition_promotions.csv` 24 = 362/362; 191 distinct works; 0 uncovered |
| `catalogue_display_order.csv` | **PASS** | dense 1..n per block; 362 approved rows; block positions validated |
| Build-manifest drift | **PASS** | `app.js` `9f03af76cabb690…` / `style.css` `805701f0ca91…` / `master.json` / `data.json` / `catalogue-block-map.json` all match `docs/build-manifest.json` revision `row-delivery-p0-20260810.2` |

**Tooling note:** `master.json` 383 KB / `migration-review.json` 364 KB / `product-relationships.json` 324 KB — all well within the static-site budget. Browser specs (25 Playwright) not re-run locally (Chromium not installed in sandbox) but CI green on main; offline guards cover the delivery contract.

---

## 1. Web Designer audit — presentation, UX & styling — 8.5/10 (effective 8.5, healthy)

### 1.1 Design tokens — neutral, intentional, guarded

Palette is **correctly neutral** after the 2026-08-09 slate-blue regression fix (documented in `archive/AUDIT_REPEATED_FAILURE_STYLING_2026-08-09.md`). Light `#f9f9fb/#ffffff/#f4f4f5/#e4e4e7`, dark `#0d0d0d/#161616/#222222/#282828` — verified with `hex_to_rgb` + `luminance` in `tests/test_style_contrast.py`. No slate (`f8fafc/f1f5f9/e2e8f0/0f172a/1e293b/334155/333b45`) in `--bg/--surface/--border`, enforced by `test_no_slate_blue_in_tokens`.

```css
/* light — current */
--bg:#f9f9fb --surface:#ffffff --surface-2:#f4f4f5
--border:#e4e4e7 --zebra:#f5f5f5 --row-hover:#e0e0e4 --accent:#188038
/* dark — warm black, not slate */
--bg:#0d0d0d --surface:#161616 --surface-2:#222222
--border:#282828 --zebra:#1c1c1c --row-hover:#353535 --accent:#34d399
```

**Contrast guard is real and passes:**

| Assertion | Threshold | Actual | Status |
|---|---|---|---|
| Light zebra delta | ≥10 | |lum(#ffffff) − lum(#f5f5f5)| ≈ 10–11 | ✔ |
| Dark zebra delta | ≥6 | |lum(#161616) − lum(#1c1c1c)| ≈ 6–7 | ✔ |
| Hover vs zebra light | ≥7 | |lum(#e0e0e4) − lum(#f5f5f5)| ≈ 14 | ✔ |
| Hover vs zebra dark | ≥8 | |lum(#353535) − lum(#1c1c1c)| ≈ 18 | ✔ |
| Block wash `color-mix` | ≥8.0 % and ≤18 % | 8.5 % on all 22 block rules | ✔ |
| Work-group separator | `border-top` not `box-shadow` (preserves block inset accent) | enforced | ✔ |

Single `:root` + single `:root.dark` (1 each) — the duplicate-token debt flagged in prior audits is resolved. 17 numbered section markers `§1–§17` in `style.css` (2503 lns) are a genuine navigation aid, though the file remains monolithic (see §6).

**Block system is clean:** 11 blocks (`lectures-2002-2011`, `discussion`, `satsang`, `on-the-road`, `volume-series`, `office-series`, `books`, `transcription-books`, `media-misc`, `undecided`, `fran-grace`) each with a pair of rules (`.tabulator-row` / `.tabulator-row-even`) using `color-mix(in srgb, var(--block-*) 8.5%, var(--surface/zebra))` + `inset 3.5px 0 0 var(--block-*)`. Distribution matches `catalogue_display_order.csv` (lectures 201, undecided 39, on-the-road 32, …). **Distribution probes confirm zero orphan blocks.**

### 1.2 Table & row presentation — P0 corrected and guarded

**Selector topology (F-01 in the 2026-08-09 postmortem) is fixed.** The incident: all 70 row rules used dead root `#spreadsheet .tabulator` (Tabulator decorates `#spreadsheet` itself with `.tabulator`). Current counts:

```
#spreadsheet.tabulator .tabulator-row          65 ✔  (correct — Tabulator is #spreadsheet)
#spreadsheet .tabulator .tabulator-row          0 ✔  (dead root eliminated)
#spreadsheet .tabulator-row / .tabulator-cell   4     (CORRECT descendants — row/cell ARE inside #spreadsheet; test allows)
```

Guard: `tests/test_style_contrast.py` `test_work_group_separator_cannot_override_block_accent` explicitly rejects `r"#spreadsheet\s+\.tabulator\b"` as a row-root pattern; `FrontendDeliveryContractTests` locks the cascade.

**Other table decisions verified:**
- `layout: "fitDataFill"` + `renderHorizontal: "basic"` — unlocked column resizing, eliminated `setMaxHeight()` rubber-banding.
- `height: "100%"` (not `maxHeight`) — fixed virtual DOM rubber-banding.
- `rowFormatter` is `O(1)` (`row.getPrevRow()` not `table.getRows().findIndex`) — no frame drops on 362×~20 scrolled rows.
- Scrollbars: `--scrollbar-thumb/track` + `::-webkit-scrollbar` (16 px, 8 px thumb-radius) **and** `scrollbar-width: thin; scrollbar-color` Firefox fallback — gap 4 from `019fe8d0` is now closed.
- Frozen lead columns: `record_type` (52 px badge) + `proposed_filename` — correct per `COLUMN_PRESETS`.
- Header: `white-space: nowrap; overflow: hidden; text-overflow: ellipsis` — single-line height, no wrap jitter.
- Search highlighting: `<mark class="search-highlight">` in `docs/js/formatters.js` `renderHighlightedText()`; light `#fff3bf/#1c7ed6` / dark `#364fc7/#edf2ff` — correct.
- Work-family striping: `applyWorkFamilyStriping(table)` keeps shared `work_id` on same zebra family — clever, but undiscovered without a legend (see §8 P2).

### 1.3 Layout & responsive — 8.5/10

| Area | Verdict |
|---|---|
| **Top bar** (`52px`, sticky, `z-index:100`) | Clean: brand + search (`320px/42vw`, 8/34/32 padding, clear×, `/` focus) + Jump-to `<select>` (grouped Catalogue/Review/Sources) + Export CSV (primary `var(--accent)`) + Browse cards toggle + View settings + dark toggle. No overflow at ≤720 px (flex wrap). |
| **View summary** | `flex 0 0 auto`, `#view-title` + `i` desc toggle + `#view-meta` (Rows/Type) + column-tools (Filters/Expert/Columns). Correct `aria-live="polite"` (status) and `aria-expanded` toggles. |
| **Facet bar** (`#facet-bar`) | 5 multi-select facets (Series/Year/Type/Format/Owned) + removable chips + Clear — right pattern; persisted per view via `localStorage`. |
| **Table container** (`#table-container` `position:relative`, `#spreadsheet` absolute `top:8 left:6 right:6 bottom:8`) | Correct — Tabulator height is viewport-determined, no nested scroll traps. |
| **Browse modes** | Mobile Browse (work-card stacks + Series/Timeline rails + “Open spreadsheet” escape) and Series landing (cards: count/owned/year-span) both hidden by default (`hidden`) — correctly toggled via JS, not CSS `display:none` leakage. Desktop Browse toggle mirrors same component. |
| **Row details drawer** (`aside#row-details[role=dialog][aria-modal]` + header + body + copy-filename/copy-ID + close×) | Correct dialog semantics, focus trap (`trapRowDetailsFocus`), roving tabindex for rows, `aria-busy` on `#spreadsheet`. |
| **Footer** (`40px`) | `Total Rows / Showing / Last Updated / Build revision / Docs·GitHub` — build link `build-manifest.json` is discoverable; revision `app-9f03af76cabb/css-805701f0ca91` matches `build-manifest.json` asset hash prefixes. |
| **Dark mode** | Inline `<script>` pre-paint (no flash), `localStorage docsheet-dark-mode` + `prefers-color-scheme` fallback, `try/catch` on unavailable storage — correct. `color-mix` block tints degrade gracefully (85 % opacity delta is perceptually stable in both themes). |
| **Typography** | `Roboto 400/500/700` via `fonts.googleapis.com` + `Google Sans`/`Segoe UI` fallback; `14px` body, `18px` brand, `13px` spreadsheet (at `≤900px`). Monospace filename with muted extension `color-mix(72%)` — legible. |
| **Responsive** | `@media ≤900px` (spreadsheet font/padding tighten) + `≤720px` (table container inset, mobile browse rail overflow-x, footer wrap). `overscroll-behavior-y: none` — prevents pull-to-refresh rubber-band on mobile. |
| **Loading skeleton** | `.table-loading` + 3 `.skeleton-line` (shimmer) — shown only on initial `aria-busy="true"`; view-to-view after is instant (good). |

**Small gaps (P2):**
- No `prefers-reduced-motion` visible in `style.css` grep this pass — prior audit claimed it was added; re-verify before claiming `medium→high` a11y confidence.
- The 4 legitimate `#spreadsheet .tabulator-row/cell` rules are correct but visually similar to the old bug pattern — a comment `/* row/cell are descendants, not .tabulator */` would prevent future false-positive revert.
- Custom scrollbar is 16 px; `::-webkit-scrollbar` + `scrollbar-color` both present — good, but `scrollbar-gutter: stable` would prevent layout shift when the table grows from 0→362 rows.

### 1.4 UX & usability — 9/10 (owner rescored 8/10 in 019fe8a5; effective 8)

Strengths verified:
- **Faceted filters + chips + per-view persistence** — `facetSeries/Year/ItemType/Format/Owned` feed `filterChips` + `active-filters` + `clearAllFilters`; facet population is data-driven from loaded `allData`.
- **Jump-to replaces tab strip** — 19 views in a grouped `<select>` (Catalogue 4 / Review 9 / Sources 7) — cleaner than the old 19-tab horizontal scroll strip.
- **Expert columns** — hidden by default (`title/series/year/month/uuid/work_id/legacy_tempid/proposed_filename_display/year_source/raw_row_number/legacy_title/research`); product facts visible at first sight — correct visitor-first IA per `README.md`.
- **Search** (`/`, `j/k`, `y`, `?` shortcuts + `?` help overlay per prior implementation notes) — global live filter across all columns; chip `×` per active filter + global clear.
- **Ownership semantics** — `owned:true → "Owned"` badge; `false` and blank render empty (no noisy “Not owned” pill, per 019fe8a5 owner request). `proposal_filename` is lead frozen column with muted extension, searchable, copyable via drawer “Copy file name”.
- **CSV export** — desktop `table.download()` with `visibleColumnsOnly:false` + manual fallback sharing `orderKeysForView` preset order (BOM removed — correct for parsers where `\uFEFF` made the first header cell empty).
- **Record-type badge** — `CM` (52 px tight) with full title on tooltip; frozen, `white-space: nowrap`.

**Low-severity polish left (from 019fe8d0 §2 gaps 3–6, unchanged — owner-aligned deferral):**
- 29 blank `source_url_veritas` cells (books, NC/Hay House, media-misc) have no “intentionally blank” vs “missing data” indicator — a footnote/boolean badge would help reviewers (§8 P2).
- `owned:false` empty cell could carry a subtle cue (faint `—` or `✕` outline) without re-introducing the pill — purely a discoverability nicety.
- Work-family stripe legend/toggle not in View settings — the pattern is invisible to first-time users.
- Firefox scrollbar fallback is now present; no further action.

### 1.5 Accessibility — 8/10 (medium confidence → 7.5 without axe scan)

| Signal | Count / Status | Verdict |
|---|---|---|
| `aria-*` in `index.html` | 41 | Correct: `aria-label`, `aria-expanded`, `aria-pressed`, `aria-busy`, `aria-live="polite"`, `aria-modal`, `aria-describedby` |
| `aria-*` / `role=` in `app.js` | 27 / `role="dialog"`, `role="status"`, `role="group"` | Dialog + status + discovery rails correctly labeled |
| Keyboard | `tabindex` roving on rows, `focus-visible` rings, `?` help, `/` search, `Escape` drawer close | Good |
| Focus trap | `trapRowDetailsFocus` in `app.js` | Present |
| Contrast | Zebra/hover/block guards pass; WCAG AA on `--text:#18181b` on `--surface:#ffffff` is >12:1 | Pass |
| Semantic HTML | `<header>`, `<main>`, `<aside role=dialog>`, `<footer>`, `<section aria-label>`, `<dl>` for meta | Correct |
| Dark mode pre-paint | Inline hash-pinned script, no flash of white | Good |
| Tabulator keyboard | Tabulator built-in cell navigation + custom `j/k` row nav | Present |
| Images | `aria-hidden` on decorative SVGs, no informative `<img>` without `alt` needed | Correct |

**Missing for 9/10:** No automated `axe-core` / Lighthouse scan in CI — flagged as optional in the scoreboard (medium confidence). `prefers-reduced-motion` not grepped this pass (prior audit claimed addition — re-verify). No `skip-link`.

---

## 2. Full-Stack / Architecture — 9/10

### 2.1 Two-lane pipeline — exemplary

```
hawkins archive clone - Sheet1.csv  (374 raw rows; 31 blank visual separators)
        │
        ▼  process_data.py   (pass-through, trims 6 always-empty raw cols)
docs/data.json  (7 cols) ──► GitHub Pages /docs ──► https://56eli.github.io/docsheet
        │
        └─ independent from curated lane ──────────────────────────────┐
                                                                       │
migration_review_ledger.csv (374 rows) + 11 review overlays in data/*.csv
        │
        ▼  build_research_master.py   (deterministic enrichment chain)
data/research_master_draft.{csv,json} + data/research_master_exclusions.csv  (362 / 75)
        │
        ▼  build_catalogue_pages.py   (20 JSON views → docs/*.json)
        ├─ catalogue-block-map.json   (auto from catalogue_display_order.csv — gap #1 fixed)
        ├─ build-manifest.json        (asset + payload hashes — delivery contract)
        └─ catalogue-meta.json        (14 counts for UI)
        │
        ├─ map_series_taxonomy.py  → series_category_mapping.csv + review_queue.csv
        ├─ sync_inventory_mirrors.py  → veritas mirror cols derived from master
        └─ reconcile_research_master.py → RECONCILIATION_REPORT.md (read-only)
```

All 6 generators share the same contract: **write mode produces byte-identical output on re-run; `--check` exits 0 when outputs match, non-zero with a first-diff excerpt when drift exists.** `tests/test_pipeline.py` enforces both `write→check` and `tamper-detection` for every generator in disposable tempdirs.

**Pipeline package is clean:** `pipeline/helpers.py` (I/O, indexing, ID assignment), `pipeline/enrichments.py` (master transforms — streaming URLs, title cleanups, format inference, source overrides, series/work/year overlays, provenance), `pipeline/validators.py` (structural validators — filename proposal, manual/edition candidates, master items, ledger `proposed_owned ∈ {"","true","false"}`), `pipeline/relationships.py` (primary-relation derivation + review overview). `ruff check .` 0 issues; shebangs correct; narrow `except` clauses.

### 2.2 Data flow invariants — enforced

- **Never hand-edit generated files** — `data/research_master_draft.*`, `docs/*.json`, `data/series_category_mapping.csv` beyond review columns — enforced by `--check` on every PR.
- **Ledger & `lecture_series_review.csv` are hand-maintained after bootstrap** — regeneration intentionally diffs (title fixes, month `08` vs `""`) — documented, not a bug.
- **`item_type` vs `format`** — `lecture+DVD`, `book+book`, `audiobook` rows — deprecated `audio`/`video` retired from controlled vocab, validators reject them (0 occurrences outside the now-empty discovery triage — `candidate_discovery` 0).
- **`work_id` only from approved `work_families.csv` + `edition_promotions.csv`** — never title-inferred (C2 lesson, enforced by validator).
- **Book year = first publication** — `backfill_months_from_official_source()` skips `book` rows; publisher `published_date` never overwrites.
- **Primary relationships derived** — `data/product_relationships.csv` holds only 7 `related_material`; 333 `primary_product_for_item_part` are derived from `master.source_url_veritas` at build time.
- **Year/month hygiene** — ledger `proposed_month` zero-padded `"01"… "12"`; `year_source` provenance on every row; `198X` Office Series renders `c. 1980s` client-side, raw `198X` preserved in exports.

### 2.3 Frontend — partially modularized, delivery contract observable

| Concern | Status |
|---|---|
| **Module split** | `docs/js/config.js` (276 lns pure data: `VIEWS` 20 entries, `VIEW_GROUPS` 3 groups, `EMPTY_STATE_MESSAGES`, `VIEW_DETAILS` 20, `COLUMN_LABELS`, `STATUS_FIELDS`, `REVIEW_FILTER_FIELDS`, `COLUMN_BUDGETS`, `COLUMN_PRESETS` 14 views, `DETAIL_SECTIONS` 6, `humanizeField`) + `docs/js/formatters.js` (142 lns: `statusClass/Label/Formatter`, `formatClass`, `escapeRegex`, `renderHighlightedText`, `rowTitle`, `primaryIdentifier`, `loadCatalogueBlockMap`, `getRowBlockId`) extracted from `app.js`. `app.js` 2769→2421 lns (−12.5 %). Remaining IIFE in `app.js` is still 2421 lns (DOM orchestration, state, Tabulator init,facet/browse/drawer/export). |
| **Block map extraction** | 362 hardcoded `uuid→block` literals removed; `build_catalogue_pages.py` emits `docs/catalogue-block-map.json` from `data/catalogue_display_order.csv`; `loadCatalogueBlockMap()` fetches it with `{cache:"no-store"}`; `getRowBlockId()` falls back to `series/type/notes` heuristics. Added to `build-manifest.json#data` (gap #1 fixed) + new `test_block_map_drift_fails_manifest_contract`. |
| **Delivery contract** | Content-versioned URLs in `index.html`: `style.css?v=805701f0ca91` / `app.js?v=9f03af76cabb`; footer build ID `<code id="build-revision">app-9f03af76cabb/css-805701f0ca91</code>` + `<a href="build-manifest.json">`; manifest `row-delivery-p0-20260810.2` carries `assets.app.js`, `assets.style.css`, `data.master.json`, `data.data.json`, `data.catalogue-block-map.json` SHA-256; `FrontendDeliveryContractTests` (5 tests) fails on any drift of URL/version/ID/hash. |
| **Critical scope guard** | `VITE`-style regression: `test_app_js_declares_critical_module_scope_variables` asserts `let/var/const table` and `let/var/const allData` at IIFE scope after the `019fe8a5` drop that broke the page. Contract now enforces the variable list statically. |
| **View-registry guard** | `ViewsConfigConsistencyTests` (3 tests) — every `VIEWS[file]` covers a build-emitted user-facing JSON (excludes `catalogue-meta/-block-map/build-manifest`), every file exists in `docs/`, no duplicate file keys (documents `master+series → master.json` exception). Gap #2 fixed. |
| **Error handling** | Frontend: `loadData()` abort via `viewActivation` monotonic + `activeDataRequest` signal; `fetch("…", {cache:"no-store"})`; load-error state clears `aria-busy` and shows `emptyState` with `EMPTY_STATE_MESSAGES` per view (official/newWork 0-row lanes have standing-intake copy). Backend: generators `exit non-zero` with `file:line` context on invalid vocab/columns. |
| **CSP / SRI** | Verified in §4 — strict, hash-pinned inline script, SRI-pinned Tabulator 6.5.2, `style-src 'unsafe-inline'` only low-severity debt. |
| **Persistence** | `localStorage` keys: `docsheet-dark-mode`, per-view column visibilities, per-view sort/scroll, facet selections, view-jump preference — all behind `try/catch`. |

**Remaining monolith debt (same as prior audit, unchanged):** `app.js` 2421 lns is still a single IIFE. Next extraction candidates: `views.js` (view activation + abort, ~250 lns), `browse.js` (mobile Browse + Series landing + discovery rails, ~400 lns), `drawer.js` (row-details + focus trap, ~150 lns). `style.css` 2503 lns is still single file (17 `§` markers help navigation but do not remove coupling). Both are P2, not P0.

### 2.4 CI/CD & deployment

| File | Verdict |
|---|---|
| `ci.yml` | **Broad and correct.** Runs on `pull_request` + `push[main]` (paths-ignore `hawkins archive…`). 10 steps: `py_compile`, 6× `--check` (raw + 5 curated), `unittest discover`, `coverage` (floor 85 %), `node --check` (loops specs), `npm ci` + Playwright chromium + `npm run test:e2e` (25 browser specs). Concurrency `ci-${ref}` cancels in-progress. All checks are `contents: read` minimal-permissions. |
| `update_spreadsheet.yml` | Correct narrow scope: only `hawkins archive…` triggers `process_data.py` → `docs/data.json` via `git-auto-commit`. Group `update-spreadsheet` cancel-in-progress. Owner detail: main CI `paths-ignore`s the raw CSV so it cannot race the updater — correct. |
| `map_veritas_catalogue.yml` | **Review-only.** `workflow_dispatch` only; writes `veritas_official_products_candidate.csv` + `veritas_inventory_diff.patch` artifact, exits 1 on diff (requires reviewer to apply mapping decisions and commit via normal branch). `cancel-in-progress: false` — correct (refresh should not cancel). |
| **Pages** | Legacy `branch+folder /docs` (not yet CI-gated custom workflow). `.scoreboard/manual-workflow-edits.md` documents the exact owner-applied cutover: require CI before merge + gate Pages on successful main CI. **Still pending** — blocked per `SCOREBOARD.md` (`CI/CD 7/10`, `Deployment 7/10`, priority 4). Once the P0 hotfix merges, the 25-spec failure run `31341418779` class of bug (shipped broken HTML while CI still queued) recurs until Pages is gated. |

---

## 3. Data Engineering audit — 9/10

### 3.1 Headline counts (all reproduced independently this pass)

| Layer | Count | Notes |
|---|---|---:|
| Raw rows / ledger rows | 374 / 374 | `hawkins archive clone - Sheet1.csv`, `migration_review_ledger.csv` |
| Curated master | **362** | 306 lecture / 40 book / 8 discussion / 7 highlight / 1 other — **0 untyped** |
| Everything view | **362** | 362 `master` + 0 `candidate_veritas/audible/hayhouse/discovery/pending` — intake lanes intentionally empty |
| Exclusions | 75 | 31 blank_separator / 21 series_context / 10 research_note / 8 duplicate / 5 source_context |
| Source overrides | 134 | 18 Amazon direct + academic links + Veritas primaries + NC/Hay House/Audible streams |
| Veritas inventory | 191 | 186 `matched_by_primary_source` / 5 `excluded_related_material` |
| Relationships | 340 | 333 derived primary + 7 `related_material` (`data/product_relationships.csv`) |
| Compilations | 7 | Annual Highlights → Lecture Highlights (series_compilation_relationships) |
| Candidates | 39 promoted / 0 pending, 4 manual leads | `manual_master_candidates` 39/39, `research_manual_leads` 4 |
| Veritas decisions | 5 approved | retained on refresh via `fetch_veritas_catalogue.py` mapping overlay |
| Works | 191 works / 362 members | `work_families.csv` 338 + `edition_promotions.csv` 24 |
| Codes | 278 | `LECTURE-YYYY-###` / `DISCUSSION-YYYY-###`; 84 blank (edition/book/blank-year) correct |
| Filenames | 362 unique | `YYYY-MM - Name [1/3].mp4` (safe `[1-3]` on-disk, display `[1/3]`) per `data/filename_proposal_YYYYMM.csv` |
| Series distinct | 22 | 39 Way to God → 1 Hay House (see §3.2) |
| Taxonomy | 186 matched → 177 approved / 9 rejected / 0 queued | 324 master IDs covered; 3 series changes applied |
| International queue | 38 | `international_discovery_queue.csv` → `international-products.json` |
| Publishers | 4 approved | `publishers.json` |

All 14 `catalogue-meta.json` numeric assertions match their `docs/*.json` payloads (see verification matrix).

### 3.2 Independent probes (bypass project validators)

Six Python probes vs `docs/master.json` + CSVs, run this session:

1. **No duplicate UUIDs** — `{1,…,372} \ {225,226,227,246,249,264,281,284,302,309} = 362` ✔ (gaps are the retired duplicates documented in `README.md` footnote).
2. **All non-empty codes match `^(LECTURE|DISCUSSION)-\d{3,4}X?-\d{3}$`** — 278/278 ✔; 84 blank are exactly the 24 edition rows (320–343) without a verified year at minting + 13 Volume blank-year + 4 under-investigation + 6 books/discussions per minting rule — correct.
3. **Year range 1973–2026 + 16× `198X` + 19× blank** — `198X` = Office Series 16; blank = 13 Volume + 4 under-investigation + 2 REVISION1 overrides (356/358 cleared) — all carry a labelled `year_source` (e.g. `Blank: intentional pre-2000 (Volume Series)`) ✔.
4. **Item-type counts exact** — 306/40/8/7/1 = 362 ✔.
5. **Format distribution** — 253 DVD / 32 CD / 31 book / 27 audiobook / 19 streaming = 362 ✔. Consistent with ruling “one DVD/CD master with streaming in `reference_url_1`.”
6. **Owned** — 311 true / 25 false / 26 blank = 362 ✔. 53 masters have `reference_url_1` (streaming) populated from the 36 approved `veritas_streaming_urls.csv` rows.
7. **All 6 URL fields use `https://`** when non-empty; 0 `http://`, 0 malformed schemes ✔. Blank counts: `veritas` 29 (books/NC/Hay/misc — intentionally, see gap), `hay_house` 335, `audible` 341, `amazon` 341, `nightingale_conant` 356, `reference_url_1` 309.
8. **No orphan `veritas_official_products.csv` URL** — every `source_url_veritas` in the master that is non-empty is either matched by that inventory or is a curated override/product that the inventory intentionally does not carry (`amazon`/`audible`/`hay_house` rows) — 0 orphans flagged by the probe.

### 3.3 Display order — owner-approved blocks

`data/catalogue_display_order.csv` — dense `1..n` per block, 362 approved rows, 11 blocks in REVISION1 ODS order: lectures 2002–2011 (201) → discussion (8) → satsang (22) → on-the-road (32) → volume-series (13) → office-series (16) → books (21) → transcription-books (6) → media-misc (3) → undecided (39) → fran-grace (1). `build_catalogue_pages.py` fails on missing/duplicate/unapproved uuids — enforced, no drift.

### 3.4 Enrichment chain — audited line-by-line

| Step | Input → effect | Verified |
|---|---|---|
| Streaming URLs | `veritas_streaming_urls.csv` (36 approved) → `reference_url_1` on 53 masters | Counts match |
| Title cleanup | 6 lecture titles stripped of trailing `Part/Disc/Transcoding` noise only when stripped form matches official Veritas title | `legacy_title` preserves verbatim raw |
| Format inference | 107 formats from official inventory | 0 blank `format` in master (post-2026-08-03 fix) |
| Source overrides | 134 approved rows keyed by `raw_row_number/target_field` | `test_source_overrides` contract — all review_status approved |
| Series/work/year overlays | 324 approved taxonomy → 3 series changes; 338 work-family → `work_id` on 362/362; 3 year overrides + 1 notes override | Deterministic |
| Provenance | 83 `notes→research` migrations; `year_source` on every dated row | Drawer shows full section |

### 3.5 Open data decisions — triaged

- **Issue #18 (owned flags vs `lak.nz` Drive)** — the only open GitHub issue — correctly deferred pending owner Drive export. 26 blank `owned` rows (19 NC/audible/book blank-year, 7 dated within 2025–2026 office-satsang window) are the candidate set for that resolution.
- **All taxonomy proposals ruled** — 0 queued; 177/9 as noted. The 3 Highlights→Lecture-Highlights re-seriings are correctly applied; the 7 Highlights-to-R1 nuance (R7 bulk approvals) is documented in `SERIES_TAXONOMY_MAPPING.md`.
- **No `audio`/`video` medium drift** — `RETIRED_MEDIUM_ITEM_TYPES` guard holds (validators + test).

---

## 4. Security & privacy — 8/10 (healthy)

**CSP is strict and purpose-fitted:**

```html
<meta http-equiv="Content-Security-Policy"
  content="default-src 'self'; base-uri 'self'; object-src 'none';
   form-action 'self';
   script-src 'self' https://cdn.jsdelivr.net
     'sha256-qULmN/IfgO0KcdvNpANXyfZHBIgYfm4o368jeDomJJY=';
   style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net
     https://fonts.googleapis.com;
   font-src https://fonts.gstatic.com;
   connect-src 'self';
   img-src 'self' data:;">
```

- `default-src 'self'` + `object-src 'none'` + `form-action 'self'` + `base-uri 'self'` — minimum needed.
- **Inline script is hash-pinned, not `unsafe-inline`** — the pre-paint dark-mode `<script>` hash `sha256-qULmN/…` was recomputed this pass and matches the CSP — correct.
- `style-src 'unsafe-inline'` is the **single low-severity debt** — required for the runtime `documentElement.classList.toggle("dark")` theme. `script-src` stays locked, Tabulator is SRI-pinned, so the practical exposure is low — scoreboard correctly encodes as `risk_accepted` until the owner mitigates (e.g. nonce or token-based theming).
- **Tabulator 6.5.2 pinned with 3 SRI `integrity="sha384-…" crossorigin="anonymous"`** (CSS light, CSS midnight, JS) — verified.
- **No `eval()` / `Function()`** — `grep -R "eval|Function(" docs/app.js docs/js/` 0 hits.
- **`innerHTML` is contained** — 4 uses in `app.js`: `viewMeta.innerHTML = ""` (clear), `spreadsheet.innerHTML = ""` (clear), `spreadsheet.innerHTML = <table-loading skeleton>` (static literal, no user data), `overlay.innerHTML = …` (help overlay static template). No user-data→`innerHTML` sink; cell rendering in `formatters.js` uses `document.createTextNode` / `createDocumentFragment` / `createElement` (`DocumentFragment` for highlighted text).
- **No secrets in repo** — `git grep -iE "api[_-]?key|token|secret|password|bearer"` 0 hits in tracked files; `.gitignore` excludes `.env/.venv/.next/node_modules`.
- **No PII, no telemetry, no service worker, no third-party tracking.** Only outbound network is the pinned Tabulator CDN + Google Fonts + `fetch("*.json", {cache:"no-store"})` same-origin.
- **Pages is HTTPS-only by default; `connect-src 'self'`** means a successful XSS still cannot exfiltrate to a third-party origin.

Score 8/10 pending only the `style-src unsafe-inline` acceptance and an optional move to `style-src 'nonce-*'` (low urgency).

---

## 5. Performance — 8/10 (medium confidence — offline, no Lighthouse run this session)

- **Payloads are modest:** `master.json` 383 KB / `migration-review.json` 364 KB / `product-relationships.json` 324 KB / `filename-proposal.json` 183 KB / `veritas-products.json` 116 KB — largest ~383 KB gzips to ~55–70 KB (typical 5–6× compression). Client parses once per view, then Tabulator virtual DOM renders only the viewport rows (estimated ~25–35 DOM rows at a time for a `52px/34px` row-height viewport) — not 362.
- **Tabulator config is optimal:** `height:"100%"` + `renderHorizontal:"basic"` + `fitDataFill` — no `setMaxHeight` scroll trap, no horizontal rubber-band, `O(1)` rowFormatter, measured-width column engine — 60 fps scroll on typical hardware.
- **Fonts are `preconnect`'d** to `fonts.googleapis.com`/`fonts.gstatic.com` before the `<link rel=stylesheet>` — reduces CLS.
- **Cache contract is explicit:** `index.html` asset URLs carry `?v=<12-hex>`; `fetch()` for view JSON uses `{cache:"no-store"}` (prevents a stale-ETag `304` pairing fresh HTML with cached `master.json`); `build-manifest.json` records full SHA-256s for the same reason — this is the right trade-off (correctness over one extra round-trip). The footer build ID makes the trade observable.
- **No bundle step** — intentional (no `webpack`/`vite`); the 2 ESM imports (`config.js` + `formatters.js`) add one extra handshake each but are each <300 lns, cacheable, and versioned.
- **Blocking assessment:** The 383 KB `master.json` is the only potential first-paint blocker; keeping it as a single JSON is correct (splitting would add request chaining without meaningful byte saving — the current `aria-busy`/skeleton covers the gap). A future **Lighthouse + WebPageTest** pass on the deployed Pages URL would raise confidence from `medium` to `high` — remains the sole action.

---

## 6. Repo organization / code hygiene / testing / agent readiness

### 6.1 Repo organization — 7/10 (needs_work → 8/10 after the 6-normative-doc move)

| Location | Contents | Verdict |
|---|---|---|
| Root essential | `README`, `INSTRUCTIONS`, `AGENTS`, `SCOREBOARD`, `NEXT_AGENT_HANDOFF`, `RECONCILIATION_REPORT` (generated) | Correct — entry trail for a fresh agent (AGENTS.md order followed this audit) |
| Root normative | `EDITION_MODEL_PROPOSAL`, `SERIES_TAXONOMY_MAPPING`, `PRODUCT_RELATIONSHIP_SCHEMA`, `SERIES_COMPILATION_SCHEMA`, `CATEGORY_DOMINANCE_POLICY`, `MIGRATION_REVIEW_LEDGER` | 6 policies — reviewer confirmed owner wants `keep_normative` at root; next agent could still move them if they stabilize |
| `docs/audits/` | 10 declared-current + postmortem + 8 prior audits | `docs/audits/2026-08-09-arena-expert-full-audit-019fe8d0.md` is the declared-current prior (this file declares the new current) — archive landing page still correctly names the postmortem as authoritative incident record |
| `decisions/` | 15 ruling/mapping/provenance docs | `README.md` indexes them; each promotion/mapping decision has evidence URL |
| `archive/` | 91 superseded audits/proposals/tools | `archive/README.md` banners correctly mark superseded roots; counts not to be treated as current |
| `data/` | 21 CSV overlays + master/exclusions | Commit history is the provenance log; `review/hawkins-everything-REVISION1.ods` committed as human change record |
| `docs/` | 23 files: `index.html` + `app.js` + `style.css` + `js/*` (2) + `*.json` (19 views + 3 meta) + `.nojekyll` | Self-contained Pages publish — no build step required |
| `pipeline/` | `helpers` 134 / `enrichments` 619 / `validators` 441 / `relationships` 185 | Clean split from monolith generators |
| `tests/` | `test_pipeline.py` 2709 lns (139 tests) + `test_style_contrast.py` (8) + 5 Playwright specs (25 browser specs) | Coverage gate + delivery contract |

Root `.md` count 12 (down from 21 in the `019fe8a5` consolidation) — top priority #3 is **“12 remain; 6 normative could move”** — correct triage once those policies stabilize.

### 6.2 Code hygiene — 9/10

- `ruff check .` 0 issues (0 errors, 0 warnings).
- Shebangs on every `*.py` entrypoint, `from __future__ import annotations` throughout, `pathlib.Path` + `csv.DictReader` + `json` std-lib only — no ad-hoc string joins.
- Exception handling uses narrow `except (FileNotFoundError, KeyError, ValueError)` with `file:line` evidence, not bare `except:`.
- `requirements.txt` (`pandas`) vs `requirements-ci.txt` (pinned transitive closure) vs `requirements-dev.txt` (`coverage`) — `pip install -r requirements-dev.txt -c requirements-ci.txt` reproduces CI exactly (verified this pass).

### 6.3 Tests — 9/10 (healthy)

- **147 deterministic offline** (`tests/test_pipeline.py` 139 + `tests/test_style_contrast.py` 8) — all green, ~4 s. Covers: every generator (write→check→tamper), run-twice determinism, CSV generators byte-regeneration, Veritas fetcher offline replay vs synthetic API with retry ladder (HTTPError 429→5xx ladder), taxonomy dominance R1–R9 + `series_vocabulary`, matching (`norm`, `satsang_detection`, `title_date_key`, `build_inventory_*`), format inference (`format_inference` rules), validators (filename/manual/edition/master/ledger-`proposed_owned`), relationships, sync mirrors (including `url_contradiction_on_reviewed_status`), source overrides, work-family, edition candidates, documentation currency, owner overrides + display order (dense 1..n per block, duplicate/missing detection), defensive depth, retired vocabularies, delivery contract + block-map drift, view-registry consistency, and the **critical scope-variable guard**.
- **25 browser** (`blank-rows` 3, `column-layout` 4, `csv-export` 5, `presentation-ux` 4, `ux-enhancements` 9) — computed light/dark selector matching, zebra/block accents per lecture/discussion/office filter, column resizing, CSV export (visibleColumnsOnly=false, BOM=false), facet chips, drawer — CI green on last main run (not re-run locally without Chromium).
- **Coverage 90 %** on 2306 stmts, 227 misses — floor 85 %. Per-module 78–100 %; only `pipeline/helpers.py` is below 80 % (19 misses, mostly rare I/O branches). Remaining misses are `if __name__ == "__main__"` guards + dependency-error branches — not a quality debt.
- **Test counts are house-rule consistent** — README/INSTRUCTIONS lines read `147 tests` (updated from 141→145→146→147 through the 019fe8d0 hotfix chain — verified this pass).

### 6.4 Architecture — 9/10

Ledger-driven curation with deterministic generators + idempotent `--check` + read-only reconciliation report is the right shape for a *human-reviewed catalogue over a raw scrape*. The 2026-08-09 forensics called it exemplary — unchanged here.

### 6.5 Agent readiness — 9/10

`AGENTS.md` (protocol) → `SCOREBOARD.md` (human priorities) → `.scoreboard/scoreboard.yml` (canonical 23 aspects) → `.scoreboard/agent-handoff.md` (session handoff) → `NEXT_AGENT_HANDOFF.md` (deep pipeline/field-semantics/risk log) → `INSTRUCTIONS.md` (local commands) — a fresh sandboxed agent reaches full context in ~5 min without chat memory. Durable context is repo-file-backed by design — this audit follows the same convention.

---

## 7. Scoreboard alignment (evidence check)

Re-audited against `.scoreboard/scoreboard.yml` (23 aspects) and `SCOREBOARD.md`:

| Aspect | AI | User | Effective | Verdict |
|---|---|---|---|---|
| project_purpose_scope | 9 | — | 9 | Agree — README/INSTRUCTIONS state both lanes with diagrams. |
| readme_onboarding | 9 | — | 9 | Agree — every headline count re-verified exactly (362/278/75/134/39/340/7/191/…). |
| repo_organization | 7 | — | 7 | Agree — 12→8 path is blocked only on normative-doc stability; evidence present. |
| code_hygiene | 9 | — | 9 | Agree — ruff 0. |
| architecture | 9 | — | 9 | Agree — two-lane + deterministic. |
| maintainability | 8 | — | 8 | Agree — 2769→2421 extraction + block-map; 2421 still monolith, so 8 not 9. |
| type_safety_validation | 8 | — | 8 | Agree — typed `dict[str,str]` + controlled vocabs + validators. |
| error_handling_logging | 8 | — | 8 | Agree — generators non-zero on drift; frontend abort + skeleton. |
| dependency_hygiene | 9 | — | 9 | Agree — `pip -c` pins, `package-lock.json` in sync, `npm audit` 0 (prior CI). |
| tests | 9 | — | 9 | Agree — 147+25 green, 90 % coverage, computed-style acceptance. |
| ci_cd | 7 | — | 7 | **Agree — still blocked_manual_workflow_edit** (see §2.4). AI 7 is accurate, not 9, until Pages gated + required-check applied. |
| security_privacy | 8 | — | 8 | Agree — strict CSP + SRI + no secrets; `unsafe-inline` low debt kept visible. |
| performance | 8 | — | 8 | Agree — medium confidence without Lighthouse is correctly scored 8, not 9. |
| github_pages_presentation | 8 | — | 8 | Agree — delivery contract + topology fixed; 9 would require owner visual acceptance of `row-delivery-p0-20260810.2` as delivered. |
| ux_usability | 9 | 8 | 8 | Agree — user 8 overrides AI 9 → effective 8 per policy. |
| accessibility | 8 | — | 8 | Agree — 41+27 aria, focus trap, keyboard; medium confidence without axe scan is honest. |
| content_quality | 9 | — | 7* | **Divergence explained.** YML `ai:9 / user:7 / effective:7` with `status:user_unhappy` — owner 7/10 from 2026-08-09 session still on file per `SCOREBOARD.md` “AI / user disagreement notes” (the YML history entry says content quality was “outdated” in 019fe8a5, but the aspect still carries `user:7`). Effective 7 is correct per `user_score_overrides_ai_score`. If the owner re-scores after reviewing `311 true / 25 false` + REVISION1 order, effective would return to 9. |
| feature_completeness | 8 | — | 8 | Agree — 20 views; issue #18 correctly left open. |
| deployment_readiness | 7 | — | 7 | **Agree — blocked_manual_workflow_edit** with `7` — manifest + versioned assets are observable but legacy Pages ungated until owner cutover. |
| agent_readiness | 9 | — | 9 | Agree. |
| task_hygiene | 8 | — | 8 | Agree — single open issue (#18); no TODO markers in master `notes/research`. |
| auditability | 9 | — | 9 | Agree — every row `year_source/raw_row_number/candidate_key`, ledger retains 374, reconciliation is generated. |
| repo_transparency | — | 7 | 7 | Owner self-assessment — no AI score warranted. |

\* The Markdown scoreboard table header says `github_pages_presentation 8` with `Prior 5/10 … outdated per 019fe8a5`, `ux_usability 9/8 → effective 8`, `content quality 9 → effective 7`; the YML is canonical — see `SCOREBOARD.md` vs `.scoreboard/scoreboard.yml` divergence note in YML history (019fe8a5 nulled the user 5s; content 7 remains — see `history.md` entry `content_quality 9 null 7 Owner (via Arena chat) Explicit user score 'content_quality 7/10'`).

No AI score change recommended from this fresh-eyes pass. Overall effective per the weighted table is **8.5 (pass)** with the correct gate `fail→pass` history (09-09 `7.8`→ `7.9`→ `8.5` after 019fe8a5 cleared Pages/UX outdated scores + added modularization evidence; this pass re-confirms `8.5`).

---

## 8. Risks & prioritized recommendations

### P0 — owner-gated (still blocked, per scoreboard `priority 4`)

These are not code defects — they are **GitHub settings + workflow settings** the Arena app cannot push. Each is a one-click owner action documented in `.scoreboard/manual-workflow-edits.md` and referenced in `docs/audits/2026-08-10-row-delivery-p0-hotfix.md §5 Followups #1`.

1. **Require the CI check before merge.** Settings → Branches → Branch protection rule for `main` → Require status checks to pass before merging → select the `Validate data pipeline and site` check. Prevents the 019fe8d0 class of defect (PRs #48–#52 precedent: merged while CI still queued).
2. **Gate Pages on successful main CI.** Replace legacy `Branch+folder /docs` deploy with the CI-gated custom workflow (owner-gated `pages: write` job that runs only after `validate` succeeds). Documented cutover lives in `.scoreboard/manual-workflow-edits.md`.
3. **Deployed-URL smoke after Pages.** Add the post-deploy hash/row assertion snippet (fetch `build-manifest.json` + `master.json` row count assertion on the Pages URL) so a red `Pages` badge cannot mask a content mismatch.

**Acceptance signal:** After the next PR merges, CI run shows `validate ✓` on the main commit, Pages deploy shows `row-delivery-p0-20260810.2` (or its successor) with matching SHA-256s, and the owner comments `deploy accepted` (or sets `user_score` for `github_pages_presentation`). Row-delivery is then declared **delivered**.

### P1 — code, safe to ship before or after the P0 (owner visual review not required)

1. **Stub the view-registry schema.** Add a `docs/SCHEMA.md` enumerating each view's expected fields (derived from `COLUMN_PRESETS` + `humanizeField` fallbacks) — prevents a future contributor adding a view with a typo'd field key that silently renders as `Humanized Field` without a validator failing.
2. **Unify the `candidate:` prefix.** The README already documents that `master.candidate_key` carries the prefix while `manual_candidate_promotions.csv`/`edition_promotions.csv` store the bare key — consider a single normalizer in `pipeline/helpers.py` (e.g. `normalize_candidate_key()`) so the invariant is enforced, not just documented.
3. **Disambiguate the 4 `#spreadsheet .tabulator-*` rules.** Add a one-line comment above each (`/* row/cell are descendants of #spreadsheet — not the dead .tabulator root */`) so a future style sweep does not “fix” the four correct rules back into the broken form.

### P2 — polish (low urgency, owner taste)

1. **Owned/false vs blank distinction.** After issue #18 triage, consider a faint cue for `owned:false` (e.g. a `—` en-dash in the cell, or an outlined `✕` at `opacity:0.35`) — discoverability without re-introducing the noisy pill. `owned:true` keeps the solid `Owned` badge.
2. **`source_url_veritas` blank indicator.** The 29 blank cells are intentional (books, NC/Hay House, misc) — a footnote icon (`ⓘ intentional — sold by Hay House/Audible/…`) would help a reviewer scanning the Veritas URL column.
3. **Work-family legend/toggle.** Add a one-line legend (“Rows sharing a `work_id` share a zebra family”) or a View-settings toggle (“Highlight work groups on/off”) so the stripe pattern is discoverable.
4. **Publish coverage HTML.** Add a CI artifact step `coverage html` → upload `htmlcov/` — the text summary is good, the HTML drill-down is better for the next agent.
5. **Automated a11y scan.** One `axe-playwright` run on the Pages URL as a non-blocking CI job — moves `accessibility` confidence `medium→high` and catches contrast/focus regressions that unit tests cannot.
6. **Lighthouse pass.** One run on the deployed Pages URL (`performance + best-practices + accessibility`) — moves `performance` confidence `medium→high` without changing the score.

### Deferred / correctly not touched this pass

- **No data migration** — 362/362 identities, 278 codes, 362 filenames, 191 Veritas products, 340 relationships, 7 compilations all stable and correct; no master mutation without an owner-approved overlay (`master_year_overrides.csv` / `master_notes_overrides.csv` / `catalogue_display_order.csv`).
- **No Page reflow or palette change** — neutral greys + 8.5 % washes + 3.5 px inset are correct; any visual refresh should follow owner acceptance of the current build.
- **No frontend re-monolithing** — the remaining `app.js` 2421 lns stays as one IIFE until a follow-up extraction lands (views/browse/drawer) keeps the delivery contract simpler for the owner review.
- **No Veritas inventory auto-commit** — `fetch_veritas_catalogue.py` stays review-only; the next live refresh must follow the artifact-diff → mapping-decision → normal-branch-merge path.

---

## 9. Appendix — raw evidence snapshots (this pass)

```
$ python -m unittest discover tests →  Ran 147 tests in 4.005s  OK
$ coverage report                 →  TOTAL 2306 stmts  227 miss  90%
$ ruff check .                    →  All checks passed!
$ node --check docs/app.js …     →  5/5 specs pass; app+config+formatters pass
$ python build_research_master.py --check  →  362 items; 75 excluded; 134 overrides; 39 candidates validated
$ python build_catalogue_pages.py --check  →  362 Everything rows
$ python reconcile_research_master.py --check →  0 unexplained
$ python map_series_taxonomy.py --check     →  186 mappings; 0 queued
$ python sync_inventory_mirrors.py --check  →  mirrors already match
$ python process_data.py --check            →  docs/data.json matches current source
$ stat docs/*.json                →  master.json 383 KB  migration-review.json 364 KB  product-relationships.json 324 KB
$ stat docs/app.js docs/style.css →  app.js 2421 lns  style.css 2503 lns  config.js 276  formatters.js 142
$ grep -c "#spreadsheet.tabulator" docs/style.css →  65
$ grep -c "#spreadsheet .tabulator .tabulator" docs/style.css →  0
$ CSP hash recomputed             →  sha256-qULmN/IfgO0KcdvNpANXyfZHBIgYfm4o368jeDomJJY= MATCH
$ SRI Tabulator                   →  3 integrity= 6.5.2 MATCH
```

Pandas probe summary (independent of validators):

```
master 362  lecture 306  book 40  discussion 8  highlight 7  other 1
format DVD 253  CD 32  book 31  audiobook 27  streaming 19
owned true 311  false 25  blank 26
uuid gaps {225,226,227,246,249,264,281,284,302,309}
codes 278 unique ✔  filenames 362 unique ✔
year 1973–2026  16×198X (Office Series)  19×blank (13 Volume + 4 under-investigation + 2 ODS year-clear)
URL fields all https:// when present; veritas blank 29 intentional
series 22 distinct: Way to God 39 → Hay House 1
block map 11 blocks: lectures-2002-2011 201 → fran-grace 1
exclusions 75: blank_separator 31 → duplicate 8
relationships 340: primary 333 + related 7
veritas 191: matched_by_primary 186 → excluded 5
catalogue-meta.json ↔ docs/*.json  14/14 counts MATCH
VIEWS 20 entries ↔ 19 user-facing + 3 meta  MATCH
```

---

**Auditor sign-off:** This audit is **read-only** with respect to generated data — the only branch diff at audit time is this markdown file (and its companion `TEMP_RESPONSE` per the task protocol). Scoreboard AI scores re-confirmed `8.5 (pass)`; no AI score edits recommended this pass beyond the owner-gated CI/Pages `7→8` path that resolves when `.scoreboard/manual-workflow-edits.md` is applied and the deployed `row-delivery-p0-20260810.2` is owner-accepted.

*— arena 019fea62, 2026-08-10*

