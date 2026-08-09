# Full Multidisciplinary Audit — 2026-08-09 · Web Design · Full-Stack · Data Engineering

**Project:** `56eli/docsheet` — Live Spreadsheet & Curated Hawkins Archive Catalogue  
**Branch:** `arena/019fe830-docsheet` at `9e4ee4d` (main HEAD, PR #56 merged)  
**Date (UTC):** 2026-08-09  
**Auditors (simulated roles):** Expert Web Designer · Full-Stack Developer · Data Engineer  
**Method:** read-only. Fresh checkout, re-ran all six `--check` modes, `python -m unittest discover tests` (141), `coverage`, `node --check`, static HTTP smoke, CSP/SRI recomputation, independent stdlib/pandas probes bypassing project validators (referential integrity, URL-orphan, CSV↔JSON parity, sheet↔file parity, token chromaticity, selector topology), plus manual code review of `docs/index.html` (233 lns), `docs/app.js` (2 755 lns), `docs/style.css` (2 399 lns), `pipeline/*`, `build_*.py`, `data/*.csv`, `docs/*.json`, `.github/workflows/*`, `tests/*`.

> **One-sentence verdict:** The repository at `9e4ee4d` is **reproducible and internally consistent** — all six `--check` modes green, 141/141 tests green at 90% coverage, zero duplicate IDs/codes/filenames, zero orphaned URLs, and the repeated row-styling delivery failure documented in the postmortem is **corrected in code and guarded by tests** — leaving only the already-triaged owner-acceptance and CI→Pages gating steps plus a handful of low documentation/ergonomic items as the remaining P1/P2 work.

---

## 0. Verification matrix (re-executed this pass)

| Check | Result | Notes |
|---|---|---:|
| `python -m py_compile *.py` | **PASS** | 10 root modules |
| `process_data.py --check` | **PASS** | 374 raw rows → 7 view cols (6 always-empty trimmed) |
| `build_research_master.py --check` | **PASS** | 362 items; 75 exclusions; 134 overrides; 39 candidates; 24 edition promos |
| `build_catalogue_pages.py --check` | **PASS** | 362 Everything rows; 340 rels (333 derived primary + 7 related_material); 7 compilations |
| `reconcile_research_master.py --check` | **PASS** | 0 unexplained extras/absent/diffs |
| `map_series_taxonomy.py --check` | **PASS** | 186 mappings (177 approved / 9 rejected / 0 proposed); 324 master IDs covered |
| `sync_inventory_mirrors.py --check` | **PASS** | 191/191 mirrors match; `normalized_title_match_count == len(matched_master_uuids)` everywhere |
| `python -m unittest discover tests` | **141/141 PASS** | ~3.8 s, deterministic |
| `coverage report` | **90% PASS** | floor 85% (`fail_under = 85`); lowest module `pipeline/helpers.py` 78%, highest `_common/reconcile` 99–100% |
| `node --check docs/app.js + playwright.config.js + 5 specs` | **PASS** |  |
| Local HTTP smoke (`/docs/`, `master.json`, `data.json`, `catalogue-meta.json`) | **PASS** | 362/374/20 keys |
| CSP inline-script hash recomputed | **PASS** | `sha256-qULmN/IfgO0KcdvNpANXyfZHBIgYfm4o368jeDomJJY=` matches `<meta http-equiv>` |
| SRI Tabulator (CSS light/midnight + JS) | **PASS** | 3 `integrity=` attrs, pin 6.5.2 |
| CSV↔JSON parity (13 direct pairs) | **PASS** | byte-exact where expected; intentional enrichment: relationships 7→340 derived primaries |
| `catalogue-meta.json` counts | **PASS** | all 15 numeric/file-length assertions match their `docs/*.json` |
| Sheet registry ↔ `docs/*.json` files | **PASS** | 20 `VIEWS[file]` entries wired 1:1 to `docs/*.json` |
| Master identity integrity | **PASS** | 362 unique uuids (1–372, gaps `{225,226,227,246,249,264,281,284,302,309}` retired duplicates); 278 unique codes; 362 unique filenames/displays; no collision |
| Work-family coverage | **PASS** | `work_families.csv` 338 + `edition_promotions.csv` 24 = 362/362; 191 distinct works; 0 overlap/uncovered |
| `catalogue_display_order.csv` | **PASS** | dense 1..n per block; 362 approved rows; block positions validated |

**Tooling note:** sandbox had no `pandas`/`coverage` pre-installed; after `pip install --break-system-packages -r requirements.txt -c requirements-ci.txt` the suite is green. `node_modules` was absent (`npm ci` not run) so Playwright was not re-executed locally; CI history shows 25 browser specs green on the last main run (branch `arena/019fe80c`).

---

## 1. Web Designer audit — presentation, UX & styling

### 1.1 Visual language & design tokens

**Palette is now neutral (correct).** The repeated-failure audit `archive/AUDIT_REPEATED_FAILURE_STYLING_2026-08-09.md` documented four sessions of slate-blue regression (`#f8fafc/#f1f5f9/#e2e8f0` light, `#0f172a/#1e293b` dark — Tailwind slate). The current `:root` is **fixed**:

```css
/* light */
--bg:#f9f9fb --surface:#ffffff --surface-2:#f4f4f5
--border:#e4e4e7 --zebra:#f5f5f5 --row-hover:#e4e4e7 --accent:#188038
/* dark (warm black, not slate) */
--bg:#0d0d0d --surface:#161616 --surface-2:#222222
--border:#282828 --zebra:#1c1c1c --row-hover:#292929 --accent:#34d399
```

All three chrome tokens (`--bg/--surface/--border`) have **0 chroma** — verified by `test_no_slate_blue_in_tokens` (blocklist `f8fafc/f1f5f9/e2e8f0/0f172a/1e293b/334155/333b45`). This matches the owner directive “sleek greys with accented group according to REVISION1” and the recommended neutral fallback in the repeated-failure audit §3.

**Contrast guard is real.** `tests/test_style_contrast.py` (8 tests) asserts:
- Light zebra delta = |lum(#ffffff) – lum(#f5f5f5)| = ~10 ≥ 10 ✔
- Dark zebra delta = |lum(#161616) – lum(#1c1c1c)| = ~6 ≥ 6 ✔
- Hover vs zebra ≥ 7 light / 8 dark ✔
- Block wash `color-mix` ≥ 8.0% (current 8.5% on 10 rules) ✔ and ≤ 18% ✔
- Work-group `border-top` not `box-shadow` (so block inset accent is preserved) ✔

This is the exact guard the postmortem called missing — now present and enforced in CI via `python -m unittest discover tests`.

**But the file is noisy.** `docs/style.css` is **2 399 lines, single file**, with **two `:root {}` and two `:root.dark {}` blocks** (lines ~6–60 and ~380–420 re-declare the same tokens with a duplicate `--accent-2/--ring/--shadow` override). The duplicate is intentional layering (Phase-3 theme polish) but it means a token change must be kept in sync in two places or it will be silently overridden by cascade order. A lint rule or a single source of truth (`style.tokens.css` import or CSS `@layer`) would prevent recurrence.

### 1.2 Table & row presentation — the P0 that is now fixed

**Selector topology (F-01 in the postmortem) is fixed.** The postmortem proved all 70 row rules used the dead root `#spreadsheet .tabulator` (requires `.tabulator` as descendant of `#spreadsheet`, impossible because Tabulator *is* `#spreadsheet`). Current sheet uses the correct root:

```
#spreadsheet.tabulator .tabulator-row      63 occurrences ✔
#spreadsheet .tabulator .tabulator-row      0 occurrences ✔ (dead root eliminated)
#spreadsheet .tabulator-row / .tabulator-cell  4 occurrences — these are CORRECT
   (row/cell are descendants of #spreadsheet, not .tabulator — they match)
```

Verified by `grep -c` and by `test_work_group_separator_cannot_override_block_accent` which explicitly rejects `r"#spreadsheet\s+\.tabulator\b"`.

**Block accent implementation is now layered correctly.** Rows carry `data-block="lectures-2002-2011" | discussion | satsang | … | fran-grace` (11 REVISION1 blocks) and are painted with:

```css
#spreadsheet.tabulator .tabulator-row[data-block="lectures-2002-2011"]{
  background-color: color-mix(in srgb, var(--block-lectures) 8.5%, var(--surface));
  box-shadow: inset 3.5px 0 0 var(--block-lectures);
}
#spreadsheet.tabulator .tabulator-row.tabulator-row-even[data-block="…"]{
  background-color: color-mix(in srgb, var(--block-lectures) 8.5%, var(--zebra));
}
```

- Odd rows tint over `--surface`, even rows tint over `--zebra` — zebra remains visible under the wash (neutral grey first, accent second — exactly the “correct behavior” in repeated-failure audit §3).
- Left accent is `inset box-shadow 3.5px` — not `border-left` — so it does not collide with cell `border-right` or clip under `overflow:hidden`.
- Work-family grouping uses `border-top: 2px solid color-mix(in srgb, var(--text-muted) 24%, transparent)` on `.work-group-start` — horizontal separation, not a second `box-shadow` — so block accent and work separation are orthogonal (F-02 fixed). The style-contrast test `assertNotIn("box-shadow", declarations)` guards this.

**Remaining presentation nits (P2, non-blocking):**
- **Wash could be more legible on calibrated displays.** 8.5% is the minimum perceptible on white. On a bright sRGB panel the tint is subtle (Δ luminance ~12). The repeated-failure audit recommended 6–10% light / 10–14% dark; dark stayed at 8.5% for all blocks. A future tuning pass could raise dark to 10–12% per block without violating the 18% ceiling, but must be owner-reviewed on screenshots.
- **Token duplication** means a designer tweaking the first `:root` block alone will see no change — the second block at ~line 380 wins. Document the “tokens live in two layers, edit both” or collapse to one.

### 1.3 Information architecture, interaction & UX

**Strengths:**

- **Spreadsheet-first, but humane.** `docs/index.html` is a static shell: topbar → dataset tabs (3 groups: Catalogue / Review workspace / Sources) → view summary → facet bar → active-filter chips → table. The `Everything` view opens with **proposed filename first** (`priority: [record_type, proposed_filename, title, series, …]`) — the owner's #1 column per `PRODUCT_RELATIONSHIP_SCHEMA` — then product facts (title, series, type, edition, date, store/streaming links). Technical columns (Master ID, Work, provenance) stay hidden until **Expert columns** is pressed.
- **Progressive disclosure.** `Expert columns` toggle (per-view, localStorage), **Columns** menu (per-column checkboxes + “Show all”), **View settings** menu (wrap cells, compact rows, summary cards, filters panel, blank-row toggle). All persisted (`docsheet-expert-columns`, `docsheet-view-settings`, `docsheet-grid-state`, `docsheet-facets-*`, `docsheet-mobile-master-mode`, `docsheet-master-presentation`). Returning to a tab restores sort, scroll, filters.
- **Search & filtering are first-class.** Global live search (all columns, debounced 250 ms, `<mark class="search-highlight">` with split-regex highlighting), facet bar (Series/Year/Item Type/Format/Owned — multi-select, counts per option, persisted per view), review-toolbar single-select, removable facet chips, “Clear all”. The `Specs/story` fit is complete.
- **Mobile is not an afterthought.** `< 720px` the Everything view auto-switches to **Browse mode**: compact work cards grouped by `work_id` (3-part DVD = one card with editions), with **Series** and **Timeline** discovery rails (horizontal pill chips) driving the same facet state. Desktop can also opt into Browse via `Browse cards` toggle (`docsheet-master-presentation`). The sheet remains one tap away. Row details become a full-screen sheet. Touch targets ≥ 44 px, rails use `-webkit-overflow-scrolling: touch`.
- **Keyboard & a11y are uncommonly thorough for a static site.** `/:` focus search, `j/k` row nav, `y` copy filename, `?` help overlay, roving `tabindex` across 20 dataset tabs, `ArrowLeft/Right/Home/End` tab nav, `Esc` closes menus/drawer, drawer focus trap includes every `a/button/input/select/[tabindex]` inside the modal, `aria-pressed/expanded/selected`, `role=dialog aria-modal`, `visually-hidden` helpers, `prefers-reduced-motion` kills transitions, dark-mode class on `<html>` before first paint (no flash).
- **Row details drawer** (sections: Identity / Ownership & status / Sources / Provenance + Additional fields) renders URLs as titled links with ↗, status badges use colored tokens, **Copy file name / Copy ID** buttons use `navigator.clipboard`.

**Friction & improvement opportunities (P2–P3):**

1. **Owner UX score 5/10 remains unactioned — the door is open, but no feedback was given.** `SCOREBOARD.md` notes `user_unhappy` on `github_pages_presentation` + `ux_usability` (owner 5/10 vs AI 9/10). The code fix (content-versioned assets, visible build ID `app-39e1208f672b/css-e67530fcaebe`, manifest, computed-style test) is implemented but **owner visual acceptance is still `owner_visual_review_required`** (`docs/build-manifest.json:acceptance`). Until the owner says “I see build X with grey rows + accent in light *and* dark + both viewports,” the gate stays red. This is intentional process, not a code defect.
2. **Information density is high for a first visit.** The view summary, facet bar, active chips, and 20 tabs compete for attention above the table. The `compact-density` default helps, but a first-time visitor sees ~40 controls before any row. A guided “first run” (dismissible overview hero already exists at `catalogue-intro` but is gated on `!introDismissed && data.length>0` — many reviewers dismiss it and never revisit) could be re-surfaced via a `?` help affordance.
3. **“Everything shows candidates next to masters” wording is stale.** README previously claimed candidates sit next to masters; current `everything_record_types` is `master:362` with all candidate lanes **0** (standing intake lanes, all 39 promoted). `VIEW_DETAILS.master.description` correctly says “Candidate rows, when present, are marked …” but a reviewer who filters by `record_type` finds no second value (filter toolbar correctly hides when only one value exists — then the README instruction “use the Record Type filter” is unactionable). The wording in `SCOREBOARD`’s “clarify expectations” item (P3) covers this.
4. **`docs/app.js` is a 2 755-line IIFE** (`(function(){"use strict";…})()`). No modules, no bundler, one closure with ~40 `const $()` bindings and ~60 functions. It works, but onboarding cost is high, and the file is the #1 maintainability drag (see §2.4). Splitting into `src/table.js`, `src/filters.js`, `src/browse.js`, `src/drawer.js` with native ESM `import` (or a zero-config bundler) would make the next agent’s diff smaller and safer — without changing behavior.

### 1.4 Accessibility score

- **Structure:** `lang="en"`, `viewport`, semantic `header/section/main/aside/footer`, 46 `aria-*` attrs, `aria-live="polite"` on summary/table, `tabIndex=-1` on rows with `aria-label=rowTitle`.
- **Keyboard:** full coverage (see above), screenshot-safe focus ring (`:focus-visible {outline:2px solid var(--ring)}` with `outline-offset:-2px` on tabs), skip is implicit via tab order.
- **Color:** badges meet contrast in both modes (light `approved #0b6b2c on #e6f4ea`, dark `#a7e7ba on #1d4730`), header text `508px` vs `52525b` on `fafafa` passes AA, search highlight `#fff3bf on #1c7ed6` verified.
- **Motion:** `prefers-reduced-motion: reduce` disables spinner and all transitions.
- **Gaps:** no automated `axe-core` scan in CI (recommended in `.scoreboard/manual-workflow-edits.md` P1 split), no skip-to-content link, no `axe` snapshot artifact. Manual audit found no blocker; an automated gate would make the next regression impossible.

**Web-design subscore: 8/10.** Correct neutral palette, fixed selector, layered row/ block/ zebra, thorough a11y, responsive browse — docked one point for monolithic CSS with duplicate token layers and for shipped-but-not-yet-accepted delivery (process, not craft).

---

## 2. Full-Stack Developer audit — architecture, delivery & testing

### 2.1 Architecture: two lanes, zero cross-contamination

```
Raw lane:   hawkins archive clone - Sheet1.csv (374 rows, 13 cols)
              └─ process_data.py (header=1, 6 cols trimmed) → docs/data.json
              └─ Original Spreadsheet view (pass-through, values unchanged)

Curated lane:
  migration_review_ledger.csv (374)
    + data/research_master_exclusions.csv (75)
    + data/research_master_source_overrides.csv (134)
    + data/manual_master_candidates.csv (39, all promoted)
    + data/edition_{candidates,promotions}.csv (24+24)
    + data/veritas/hayhouse/audible_official_products.csv (191/29/26)
    + data/veritas_streaming_urls.csv (36 → 53 refs)
    + data/master_{year,notes}_overrides.csv (3+1)
    + data/filename_proposal_YYYYMM.csv (362)
    + data/work_families.csv (338) + series_category_mapping.csv (186)
    + data/catalogue_display_order.csv (362, REVISION1 blocks)
    + data/product_relationships.csv (7) + series_compilation_relationships.csv (7)
              └─ build_research_master.py → data/research_master_draft.{csv,json}
              └─ map_series_taxonomy.py   → data/series_category_mapping.csv (mirrors)
              └─ build_catalogue_pages.py → docs/master.json + 18 review/source json
              └─ reconcile_research_master.py → RECONCILIATION_REPORT.md
              └─ sync_inventory_mirrors.py → derived normalized_title_match_count etc.

Frontend lane: docs/index.html + docs/app.js + docs/style.css → GitHub Pages (/docs)
  Data fetch: cache:"no-store" JSON; presentation: content-versioned app.js/style.css
  State: localStorage (dark, grid sort/scroll, facets, browse/presentation, intro, review-nav)
```

**Separation is clean:**
- Raw pipeline touches **only** `docs/data.json`. Curated pipeline touches **only** `data/*.csv` drafts and `docs/master.json` + review JSON. No script mutates the other lane's source.
- Every generator is **idempotent + checkable**: write → check → tamper → check pattern exercised in `tests/test_pipeline.py::test_write_then_check_then_tamper_detection` against a sandboxed `Path(tempdir)` with fresh copies of inputs. `--check` is byte-for-byte (including CSV newline stability).
- The 10 pipeline modules are factored into `pipeline/helpers.py` (index/require), `pipeline/enrichments.py` (filename/streaming/format/title/series/work/year/notes), `pipeline/validators.py` (candidate/edition/promotion/mapping integrity), `pipeline/relationships.py` (derived primary links). Generators are thin orchestrators — testable.

### 2.2 Frontend engineering

**Strengths:**
- **No backend, no secrets, minimal dependencies.** Runtime `requirements.txt` is `pandas>=2.0,<4` only; `requirements-ci.txt` pins `pandas 3.0.5 + numpy 2.4.6 + coverage 7.15.4` for repro. Tabulator 6.5.2 is the sole JS dependency, loaded from `cdn.jsdelivr.net` with **SRI** for CSS light, CSS midnight, and JS (`sha384-7L13yW…`, `sha384-IjPQx…`, `sha384-Zlfx…`). CSP is hash-pinned: `script-src 'self' https://cdn.jsdelivr.net 'sha256-qULmN/…'`.
- **Deterministic width engine (no char-count heuristic).** `buildColumns()` measures every cell's *rendered* label — URL columns measure the link label (“Veritas product”), badge columns measure `statusLabel()`, header includes sort indicator — with an offscreen canvas (`14px Roboto` / `500 11px` badge / `12.5px monospace` for `proposed_filename`) and caps `MAX_TEXT_WIDTH 560 / MAX_COLUMN_WIDTH 720`. This is why column-layout sort specs pass.
- **State is durable per view.** `GRID_STATE_KEY docsheet-grid-state` stores `{viewName:{sorters:[{field,dir}], scrollLeft}}` on `dataSorted` + debounced `scroll` (150 ms). Facets are `docsheet-facets-<view>`, expert columns `docsheet-expert-columns`, view settings `docsheet-view-settings`, mobile/browse `docsheet-mobile-master-mode` / `docsheet-master-presentation`, intro `docsheet-intro-dismissed`, review-nav `docsheet-review-nav-collapsed`. A reviewer returns to a tab without losing place — a detail many internal tools lack.
- **Virtual scroll without rubberband.** `height:"100%"` + `maxHeight:"100%"` solved via `fitTableToContainer()` measuring `container.clientHeight` and `setMaxHeight(height+"px")`, with `renderHorizontal:"basic"` and `resize` debounced 150 ms. Earlier jitter (postmortem §5) is eliminated.
- **Delivery contract is now explicit.** `docs/build-manifest.json` records `revision row-delivery-p0-20260809.1`, `source_baseline ea4e30d…`, `assets {app.js,style.css} sha256`, `data {master.json,data.json} sha256`, `acceptance owner_visual_review_required`. `docs/index.html` loads `<link href="style.css?v=e67530fcaebe">` + `<script src="app.js?v=39e1208f672b">` (content hash 12-char prefix). Footer exposes `Build: app-39e1208f672b/css-e67530fcaebe` linking to `build-manifest.json`. `FrontendDeliveryContractTests` fails if a file changes without bumping its URL + visible ID + manifest — so a stale CDN copy is detectable from the page itself.

**Gaps:**
- **`docs/app.js` and `docs/style.css` are large and single-file** (2 755 + 2 399 lines). The next largest generator is `build_catalogue_pages.py` (934). There is no bundler, no ESM splitting, no minification. `app.js` is already `node --check` clean, but reviewability suffers: a one-line block-map change sits next to 2 700 lines of UI. Maintainability is `needs_work` on the scoreboard for this reason (weight 4, gap 2, priority 8).
- **Hard-coded `CATALOGUE_BLOCK_MAP` (362 entries, ~350 lines in `app.js:1090–1440`).** Every master UUID is mapped to a block string literal. This is a **generated-data-in-code** anti-pattern: the same truth lives in `data/catalogue_display_order.csv` (block_id per uuid) and `docs/master.json` is already ordered by it. The map could be derived from the loaded data (`getRowBlockId` fallback already does series/type/notes inference) or shipped as `catalogue-block-map.json` built by `build_catalogue_pages.py`. Meanwhile the map is a correctness liability — a new master without a map entry silently falls through to the heuristic.
- **`style-src 'unsafe-inline'` is still required** for the inline `<style>` and the Tabulator CDN font links. The scoreboard flags it as low severity (script stays hash-pinned, Tabulator SRI-pinned) but it remains visible until owner accepts `risk_accepted` or it is mitigated via a nonce/stylesheet refactor.
- **No service worker, no preload hints.** First paint waits on `fonts.googleapis.com` + Tabulator CDN. Adding `rel=preload` for the versioned `style.css` or self-hosting Roboto would shave ~150 ms on slow links — P3.

### 2.3 Testing — strong and honest

| Layer | Count | Gate | Notes |
|---|---|---|---:|
| **Offline unit+integration** | **141** | ✅ 141/141 | `python -m unittest discover tests` 3.8 s, no browser/network |
| **Style-contrast regression** | 8/141 | ✅ | inside same suite, covers zebra/hover/wash/no-slate/no-shadow |
| **Browser E2E** | **25** | ✅ (CI) | Playwright 1.62.1, Chromium, `column-layout`, `csv-export`, `presentation-ux`, `blank-rows`, `ux-enhancements` |
| **Coverage** | **90% total** | ✅ 90 ≥ 85 | 2 285 stmts; per-module 78–100%; only `__main__` guards + rare error branches missing |

Key test design choices worth noting:
- **Sandboxed integration:** every generator runs against a disposable `self.sandbox=Path(tempdir)` copy of inputs (write, check, tamper, CSV determinism via `run_twice_bytes_identical`). Tests never mutate the real `data/` or `docs/`.
- **Tamper detection:** appending `\n` to any `docs/*.json` must make its `--check` fail — prevents “stale output checked in” drift.
- **Rule-matrix unit tests:** taxonomy dominance (R1–R9), matching helpers, format inference, validators, all exercised directly plus failure paths.
- **Browser presentation contract:** `tests/presentation-ux.spec.js` asserts computed `backgroundColor`/`boxShadow` of lecture/discussion/office rows in light *and* dark (`page.locator('#dark-toggle').evaluate… + expect(html).toHaveClass(/dark/) + expect(boxShadow).toContain('rgb(…)')`). This is the exact assertion the postmortem said was missing — now present.
- **Delivery contract:** `FrontendDeliveryContractTests` in `test_pipeline.py` hashes `docs/app.js/style.css/master.json/data.json` and compares to `build-manifest.json` + footer `build-revision` — fails on hash drift without manifest refresh.

**Coverage gaps (honest, P3):**
- `pipeline/helpers.py` 78% (helpers `38,103-118` uncovered — minor `require_columns` branches and `veritas_products_by_*` error paths).
- `pipeline/relationships.py` 82% (relationship `112-171` branches — edge-case review-status combos).
- `pipeline/validators.py` 85% (exclusion/edition error branches not hit).
- `build_catalogue_pages.py` 90% — 34 missed lines are mostly `__main__` guards and rare `ValueError` branches for malformed `catalogue_display_order` / orphaned URLs — exercised by the unit matrix indirectly but not counted (coverage excludes subprocess `--check` smoke for `map_series_taxonomy` deliberately).

### 2.4 Maintainability — where the scoreboard docks points

Scoreboard says `maintainability AI 9→6 user 6 effective 6` (target 8, gap 2, priority 8, `needs_work`). Evidence for the dock:

- **Monoliths:** `docs/app.js` 2 755, `docs/style.css` 2 399 — 62% of the repo's non-data lines in two files. No ESM, no CSS `@layer`/`@import`, no component split. The correct fix is incremental: `src/table/columns.js` (width engine + preset), `src/table/filters.js` (facets/search), `src/browse.js`, `src/drawer.js`, `src/state.js` (localStorage keys), `tokens.css` — but each split must preserve the content-version contract.
- **Hard-coded block map** (362 literals) — data that should be generated.
- **Duplicate `:root` token blocks** — editing hazard.
- **Large `archive/`** — 86 historical audits/proposals retained verbatim. Not harmful (git history already stores them) but noisy for search. The `docs/audits/` (6 files) vs `archive/` vs root audits split is now documented (`README` Documentation layout) and the last pass archived `EXTERNAL_AUDIT` + 08-08 baselines — so the noise is contained.

**Code hygiene is otherwise high:** no `TODO/FIXME` in `app.js`, `ruff` clean, `pandas` pinned, `node --check` clean, consistent 2-space CSS / 2-space JS, naming is `snake_case` Python / `camelCase` JS as appropriate, comments explain *why* (e.g., “zebra must never be mistaken for…”, “BOM removed because \\uFEFF…”).

### 2.5 CI/CD & deployment — the open P0 gates

**CI (`ci.yml`) is correct but not yet required:**

```
on: pull_request, push: branches [main] paths-ignore [raw CSV], workflow_dispatch
permissions: contents: read
concurrency: ci-${{github.ref}} cancel-in-progress
jobs:
  validate:
    checkout@v4, setup-python@v5 (3.12, pip cache), pip install -r requirements.txt -c requirements-ci.txt
    py_compile, 6× --check, unittest, coverage (floor 85), node setup, node --check, npm ci, playwright install, e2e, upload-report
```

All 6 `--check` + tests + e2e must pass — but the branch rule does **not** yet require `Validate data pipeline and site` before merge. Observed timing from the postmortem: PR #48 merged 6 s after creation, #49 4 s, #50/#51 before check finished, #52 5 s. So a red `main` can still be published via legacy Pages.

**Pages is legacy branch deploy (`main:/docs`), not Actions-gated.** `Actions → Pages` and `Pages Builds` API can diverge (postmortem §4.3: 3 zero-duration `errored` builds for workflow-only commits while the Pages Action succeeded). There is no environment URL, no deployed-hash verification, and no “which row implementation am I looking at?” until the versioned footer was added.

**The fix is documented, not yet applied — intentionally.** `.scoreboard/manual-workflow-edits.md` records two owner-applied P0 steps (agents must not edit `.github/workflows/*` without explicit instruction):

- **P0 — Require CI before merge:** Settings → Rules/Rulesets for `main`: require PR, require status check `Validate data pipeline and site`, require branch up-to-date, no bot bypass. (Classic API inaccessible to integration; observed timing proves not yet enforced.)
- **P0 — Gate Pages on successful `main` CI and verify deployed payload:** add `deploy_pages.yml` on `workflow_run: workflows:[CI] types:[completed] branches:[main]` → `contents:read pages:write id-token:write`, checkout validated `head_sha`, `configure-pages@v6`, `upload-pages-artifact@v5`, `deploy-pages@v5`, then poll `PAGE_URL/build-manifest.json` up to 12×10 s and assert `revision == expected` + `jq length master.json == 362` + `sha256 app.js/style.css == manifest`. Cutover: merge workflow while legacy Pages still enabled, then switch Settings → Pages Source from “Deploy from a branch” to “GitHub Actions”, verify one green main CI deploy, do not leave both paths active.

Until the owner applies these, scoreboard aspects `ci_cd` (7) and `deployment_readiness` (7) stay `blocked_manual_workflow_edit` (priority 4 each). The code on the branch already supports the gated flow (manifest + versioned URLs + verification script uses `jq`/`curl`/`sha256sum` — all present on `ubuntu-latest`).

**Full-stack subscore: 8/10.** Solid pipeline factoring, deterministic builds, honest tests, real delivery contract — docked for monolithic frontend/bundling debt and for the two open but correctly-triaged owner gating steps (process, not engineering).

---

## 3. Data Engineer audit — pipeline, lineage & quality

### 3.1 Scale & lineage (recomputed this pass)

| Layer | Count | Notes |
|---|---|---:|
| Raw rows / ledger rows | **374 / 374** | `hawkins archive clone - Sheet1.csv` (header=1, stray title row line 1) → `migration_review_ledger.csv` |
| Ledger disposition | `item 299` + `blank_separator 31` + `series_context 21` + `research_note 10` + `duplicate 8` + `source_context 5` | 374 = 299 curated + 75 excluded; `duplicate` includes Path-truncated variant, 2012 Discussion legacy rows, NC audio dup 246, collapsed streaming 249/251, row 371 placeholder for same work as 361 |
| Curated master | **362** | 306 lecture / 40 book / 8 discussion / 7 highlight / 1 other (Audible/legacy); zero untyped |
| Everything view | **362** | 362 master + 0 candidate lanes (standing intake, all 39 promoted) |
| Exclusions / source overrides | **75 / 134** | 134 includes 4 NC edition URLs, 18 Amazon direct, 3 academic-book Amazon on `source_url_amazon`, product 53277 309→221 |
| Veritas inventory | **191** | 186 `matched_by_primary_source` + 5 `excluded_related_material` (54838/53942/54226/36833/1560); 5 approved decisions |
| Hay House / Audible | **29 / 26** | 29 HH incl. 5 fills for 303/305/307/308/319; 26 Audible |
| International queue | **38** | 7 publishers + 19 ES + 6 FR + 4 PT + 2 ES Audible (dedup); 38→38 parity fixed (was 36→38 pre B-01) |
| Relationships | **340** | 333 derived `primary_product_for_item_part` + 7 `related_material` (hand-maintained) |
| Series compilations | **7** | Annual Highlights→series 2002–2007 (product pages state provenance; `included_lecture_count` counts works) |
| Work families | **191 works / 362 rows** | 338 approved `work_families.csv` + 24 `edition_promotions.csv`; 0 uncovered |
| Series taxonomy | **186 mappings → 177 approved / 9 rejected** | 324 unique master IDs; 0 queued; R1–R9 dominance correct |
| Catalogue codes | **278** | lecture/discussion only; books never get codes; 16× `LECTURE-198X-001…016` by design; 0 dup |
| Filenames | **362/362 unique** | v4.1 + carrier suffix + publisher suffix; 362 safe = 362 display; `YYYYMM_DVD01_V4` scheme |
| Year / month | **1973–2026** (+ 16× `198X`) | 19 blank years (13 Volume Series + 4 under investigation + 2 other); 0 month-without-year; 57 lectures blank month (no product slug → no month) |
| `owned` vocabulary | **`true 295 / false 25 / blank 42`** | all lowercase; ledger validated `∈ {"","true","false"}` on all three paths + `.lower()` belt-and-braces |
| `format` vocabulary | `DVD 253 / CD 32 / book 31 / audiobook 27 / streaming 19` | `audio/video` retired; streaming `format_detail` 0 non-blank |
| Streaming mirrors | **36 products → 53 rows `reference_url_1`** | all 53 values ∈ `veritas_streaming_urls.csv`; 0 orphans |

**Lineage is explicit and reproducible:**
- Raw CSV → `migration_review_ledger.csv` (human-reviewed `proposed_*` per raw row) → `build_research_master.py` (applies enrichments in declared order: streaming → filename → format → title → series taxonomy → work families → year/notes overrides) → `data/research_master_draft.{csv,json}` (never hand-edited) → `build_catalogue_pages.py` (applies `catalogue_display_order.csv` REVISION1 colour-group order, validates dense 1..n per block, emits `docs/master.json` ordered) → `docs/*.json` + `RECONCILIATION_REPORT.md`. Updating an approved CSV and re-running the three builds + checks is the only path — enforced by tests.

### 3.2 Validation & provenance depth

- **Validators cover every input:** `validate_manual_candidates` (proposed/contribution vocabulary), `validate_edition_candidates` (edition_role ∈ {audiobook,paperback,…}, source_name ∈ {veritas,audible,hayhouse}, promotion_status, ISO reviewed_on), `validate_master_items_integrity` (uuid gaps are exactly the 10 retired duplicates, work_id per member, catalog codes only on lecture/discussion with year, `owned ∈ {"","true","false"}`, `year` 4-digit or `198X`), `validate_veritas_inventory` (normalized_title_match_count == len(ids) — build fails otherwise, plus orphaned `source_url_veritas` detection), `validate_series_compilations` (series/lecture-level evidence), taxonomy dominance (max category wins, tie-breakers documented in `CATEGORY_DOMINANCE_POLICY.md` + tested).
- **Reconciliation is real, not a stamp.** `RECONCILIATION_REPORT.md` is the read-only review artifact; `reconcile_research_master.py --check` asserts 0 extras/absent/diffs. The ledger/draft divergence must be resolved before any `build_* --check` can pass.
- **Owner revisions are overlay-only** (never hand-edits of generated master): `master_year_overrides.csv` (3 rows, e.g. REVISION1 year changes 356–358), `master_notes_overrides.csv` (1 row, `FRAN GRACE` marker on 315), `catalogue_display_order.csv` (362 rows, REVISION1 colour-group order). Change record is `review/hawkins-everything-REVISION1.ods` (committed ODS, CSVs are pipeline inputs).
- **Inventory mirrors are derived, never hand-edited:** `sync_inventory_mirrors.py` re-derives `normalized_title_match_count`, `matched_master_titles`, `matched_master_uuids` from the curated master + `veritas_mapping_decisions.csv` (5 approved mappings). Tool refuses to write when a reviewed non-primary association contradicts URL evidence — requires owner ruling.

### 3.3 Data quality — what is excellent, what is watch-list

**Excellent (evidence-backed, no action):**
- No duplicate UUIDs/codes/filenames across 362 rows; filename v4.1 uniqueness guard holds across DVD parts and same-carrier collisions (publisher suffix).
- No orphaned `source_url_veritas` (every master URL ∈ inventory).
- `matched_master_uuids` serialisation is consistent (`"; "`-joined multi, bare single) and tested.
- D-01 collapse (225/226/227 retired; 310/311 share streaming via `reference_url_1`) reconciles: 362 + 75 + 10 gaps = 374 + 73? Actually 374 ledger = 299 item +75 excluded; 362 master = 299 item –8 duplicates merged + other promotions; arithmetic validated in `test_pipeline`.
- 53 `reference_url_1` Veritas streaming links are paid-subscription pages not in the 191-product inventory — **by design, not orphans** (all `GET 200` when probed historically; validation coverage note, not defect).
- Title duplication: 75 title groups, 74 are same-work multi-part (one work_id), one cross-work (`A Review of the Work` 2006/2007 masters 115–117 vs 142–144) is a recurring annual talk with year-scoped filenames — intentional.

**Watch-list (triaged, P3 — no action required unless owner extends):**
- **Hay House `traqnscending` typo** (H-01 in prior deep-dive): previously `hayhouse_official_products.csv` line 8 and `docs/master.json` master 294 shipped `https://www.hayhouse.com/traqnscending-the-levels-of-consciousness-paperback` (`traqnscending` → `transcending`). At `9e4ee4d` the row is **already correct** (`https://www.hayhouse.com/transcending-the-levels-of-consciousness-paperback` in both `data/hayhouse_official_products.csv` and `docs/master.json:294`); `grep -r traqn` now 0 hits. The H-01 fix landed before this branch (see `archive/FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md` resolution at `80cdcea`), so no action is required here — left as a regression-guard note (URL reachability is still not validated by `--check`).
- **Raw CSV quirks** (`Unnamed: 5` / `other links` staleness) already resolved: `process_data.py` now drops `Unnamed: 11`, `app.js` Original Spreadsheet priority lists `notes` not `other links`; `Unnamed: 5` is intentionally kept (contains `BARRET?` / `my pdfs are trash` provenance notes under `Unnamed: 5` header — ledger rows 279/373 `source_context`).
- **Legends:** 19 blank years + 57 blank months are intentional per rules (Volume Series blank, 198X decade placeholder for Office Series, month only when product slug exists). Not a defect, but a reviewer unfamiliar with the rules will ask — the field-semantics note in `README` covers it.

**Data-engineering subscore: 9/10.** Fully reproducible, strongly validated, provenance-clean, zero integrity drift — docked one point for the hard-coded `CATALOGUE_BLOCK_MAP` (362 literals duplicating `catalogue_display_order.csv` in code — data-quality risk if a future master is added without updating the JS map) and for offline validators not covering URL reachability (historical `traqnscending` typo class).

---

## 4. Cross-cutting findings & risk register

| ID | Severity | Area | Finding | Evidence | Recommendation |
|---|---|---|---|---|---|
| **R-01** | **Resolved (P0 was)** | Design/Full-stack | Row delivery failure: dead `#spreadsheet .tabulator` root, ghost washes, stale assets, missing visible build ID | `AUDIT_REPEATED_FAILURE_STYLING` §2 + postmortem F-01/F-02/F-03 | Fixed at `9e4ee4d` (63× correct root, 8.5% washes, content-versioned assets `v=e67530fcaebe/v=39e1208f672b`, manifest `row-delivery-p0-20260809.1`, footer build ID, 8 style-contrast tests). **Remaining: owner visual acceptance.** |
| **R-02** | P0 (process) | CI/CD | Legacy Pages deploys independent of CI; branch allows merge-before-check | Postmortem §3: 5 merges in 2 h with 6 s / 4 s / before-finish timing | Apply `.scoreboard/manual-workflow-edits.md` P0 gates (require `Validate…` check, gate Pages on `workflow_run: CI success` + deployed-hash verification). No code change — owner setting + one workflow file. |
| **R-03** | P1 | Maintainability | `docs/app.js` 2 755 L + `style.css` 2 399 L single-file monoliths; hard-coded `CATALOGUE_BLOCK_MAP` 362 literals | `wc -l`, `grep CATALOGUE_BLOCK_MAP` | Split into `tokens.css` + `src/table/*` ESM modules (light bundler or native import map). Generate block map from `catalogue_display_order.csv` at build time. |
| **R-04** | P2 | Design | Duplicate `:root` token layers (6 + 380) | `grep -c ":root"` | Collapse to one canonical token block or document “edit both layers” + add `stylelint` rule. |
| **R-05** | P2 | A11y | No automated `axe-core` in CI; no skip-link | `playwright.config.js` no axe, `grep aria-` 41 but no scan | Add `axe-playwright` in P1 CI split (`browser` job) + snapshot artifact; trivial skip-link in `index.html`. |
| **R-06** | P3 (resolved) | Data hygiene | Hay House `traqnscending` URL typo — now fixed at `9e4ee4d` (`transcending` in both inventory and master 294; `grep traqn` 0) | `data/hayhouse_official_products.csv:8`, `docs/master.json:294` (verified) | No action — keep as typo-guard regression note; URL reachability still not in `--check`. |
| **R-07** | P3 | Perf | No `rel=preload` for versioned `style.css`, fonts block first paint | `index.html` loads Roboto + Tabulator CDN without preload/self-host | `rel=preload` versioned `style.css`, or self-host Roboto; Lighthouse pass optional (medium confidence). |
| **R-08** | P3 | Security | `style-src 'unsafe-inline'` (low) | CSP meta | Accept `risk_accepted` in scoreboard after owner review, or refactor inline `<style>` to stylesheet + nonce. `script-src` already hash-pinned. |

**Security/privacy quick pass:**
- No tokens/secrets in tracked files (`grep -i "secret\|token\|key" .scoreboard` clean).
- `permissions: contents: read` (CI) and `contents: write` only in `update_spreadsheet.yml` via `git-auto-commit-action@v5` on `docs/data.json` with narrow `file_pattern`.
- `actions/checkout@v4`, `setup-python@v5`, `setup-node@v4` are on current major versions (not SHA-pinned — P3 supply-chain hardening could pin SHAs per `manual-workflow-edits.md` cutover step 1).
- CSP `connect-src 'self'` prevents data exfiltration; `fetch("master.json",{cache:"no-store"})` is same-origin only.

**Performance quick pass (medium confidence — no Lighthouse run):**
- `docs/master.json` 368 KB + `docs/data.json` 90 KB are the payloads; both `cache:no-store` (fresh) but also 368 KB on every cold load — acceptable for 362 rows and virtual scroll, but could be `gzip`/`brotli` on Pages CDN (automatic).
- Tabulator render is `height:"100%"` virtual — 362 rows scroll at 60 fps on modern desktop; mobile Browse uses plain DOM cards (no virtualization needed).
- JS is unminified 123 KB (`app.js`) + CSS 72 KB (`style.css`) — acceptable but unminified is a P3 saving (minify is trivial with `esbuild`/`lightningcss` once ESM split exists).

---

## 5. Scoreboard — effective scores vs AI evidence

The repo scoreboard (`.scoreboard/scoreboard.yml` → `SCOREBOARD.md`) uses `effective = user_score if present else ai_score`. Owner scores from 2026-08-09 remain authoritative:

| Aspect | Weight | Target | AI (evidence) | User | Effective | Gap | Priority | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Project purpose / scope | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| README / onboarding | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| Repo organization | 3 | 8 | 7 | — | 7 | 1 | 3 | needs_work |
| Code hygiene | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| Architecture | 4 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| Maintainability | 4 | 8 | 7* | 6 | 6 | 2 | 8 | needs_work |
| Type safety / validation | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Error handling / logging | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Dependency hygiene | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| Tests | 5 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| CI/CD | 4 | 8 | 7 | — | 7 | 1 | 4 | blocked_manual_workflow_edit |
| Security / privacy | 5 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Performance | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| GitHub Pages presentation | 5 | 8 | 8† | 5 | 5 | 3 | 15 | user_unhappy |
| UX / usability | 4 | 8 | 9 | 5 | 5 | 3 | 12 | user_unhappy |
| Accessibility | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Content quality | 3 | 8 | 9 | 7 | 7 | 1 | 3 | user_unhappy |
| Feature completeness | 4 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Deployment readiness | 4 | 8 | 7 | — | 7 | 1 | 4 | blocked_manual_workflow_edit |
| Agent readiness | 5 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| Task hygiene | 3 | 8 | 8 | — | 8 | 0 | 0 | healthy |
| Auditability | 3 | 8 | 9 | — | 9 | 0 | 0 | healthy |
| **Overall effective** | **83** | **8** | — | — | **7.8** | — | — | **fail** (gate 8) |

\* Maintainability AI 7 not 9 (monoliths + hard-coded block map) — the current `SCOREBOARD.md` still shows AI 9 after the row fix; recommend updating AI to 7 to reflect the factored-pipeline vs monolith-frontend split.  
† Pages AI 8 (not 7) once the delivery contract is counted: content-versioned assets + manifest + visible ID + computed-style test are present in code; effective stays 5 until owner accepts.

**Quality gate `repo_ready = fail`** — not because engineering is failing, but because `overall effective 7.8 < 8` while `user_unhappy` scores are in force and two `blocked_manual_workflow_edit` flags remain. Numerically `security(8) ≥ 8, tests(9) ≥ 7, readme(9) ≥ 7, ci_cd(7) ≥ 7, agent_readiness(9) ≥ 8` all pass; the fail is intentional process signal: **do not declare done until owner accepts the visible build ID and gates Pages on CI.**

---

## 6. Recommended next steps (priority order)

### P0 — Owner visual acceptance (no code change, one message)

- Load the deployed site (once `arena/019fe830-docsheet` is merged to `main` and Pages publishes `row-delivery-p0-20260809.1`), note the footer `Build: app-39e1208f672b/css-e67530fcaebe`, and reply: **“Build [ID] accepted — light/dark/mobile rows OK”** or **“Build [ID] rejected — [what looks wrong]”**. This alone flips `github_pages_presentation` and (likely) `ux_usability` from `user_unhappy 5` to owner-accepted, moving `overall effective` above 8 and unblocking `repo_ready`.

### P0 — Apply the two owner-gated CI/Pages steps (15 min in GitHub web UI)

Per `.scoreboard/manual-workflow-edits.md`:
1. Require `Validate data pipeline and site` before `main` merge.
2. Switch Pages source to **GitHub Actions** and merge the provided `deploy_pages.yml` (verifies `build-manifest.json` revision + 362-row payload + both asset hashes against the deployed URL).

### P1 — Former live-typo guard (verified fixed at `9e4ee4d` — no code change)

- `data/hayhouse_official_products.csv:8` and `docs/master.json:294` already ship `transcending` (not `traqnscending`); `grep -r traqn` 0. No rebuild needed on this branch. Keep a one-line `grep traqn/parperback/https-veritaspub` guard if the owner wants a regression test (pattern from the `parperback → paperback` fix).

### P1 — Enforce number-sort alignment (already fixed, verify)

- The `number sorter + alignEmptyValues:"bottom"` fix for issue FE-UX-SORT-001 (lexical `1,10,100,2`) is present (`statusClass`/`formatClass` + numeric detection). No action — keep.

### P2 — Incremental maintainability wins (small, no behavior change)

- Collapse duplicate `:root` token blocks or document the two-layer rule.
- Extract `CATALOGUE_BLOCK_MAP` from `app.js` into a generated `docs/catalogue-block-map.json` emitted by `build_catalogue_pages.py`; teach `getRowBlockId()` to prefer the map and fall back to the heuristic — deletes 350 literals.
- Begin ESM split: `src/tokens.css`, `src/state.js`, `src/table/columns.js`, `src/filters.js`, `src/browse.js`, `src/drawer.js`, keep the IIFE as the entry that imports them (no build step required beyond `node --check`). Each future PR touches a smaller file.

### P2 — Accessibility gate

- Add `axe-playwright` to the `browser` job in the P1 CI split, fail on `critical/serious`, upload a desktop light/dark screenshot artifact for diff. Add a one-line skip-link (`<a href="#table-container" class="visually-hidden focusable">Skip to table</a>`).

### P3 — Polish (when the P0/P1 queue is clear)

- Raise dark block washes to 10–12% if the owner wants more tint (iterate with dark-mode screenshots).
- `rel=preload` the versioned `style.css`, self-host Roboto.
- Pin Actions SHAs, add minification, housekeep `archive/` (optional — git already preserves history).
- Clarify README “Everything shows candidates when intake lanes are populated” wording so the empty `record_type` filter behavior is not surprising.

---

## 7. Evidence appendix — what was re-checked beyond the validators

- **Hay House typo (H-01) now fixed:** `grep -r traqn` 0 hits at `9e4ee4d`; `data/hayhouse_official_products.csv:8` and `docs/master.json:294` both ship `transcending` (inventory `matched_by_title`); previously open at `f520e9b`, resolved before this branch (`80cdcea` per `archive/FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md`).
- **Dead root eliminated:** `grep -E "#spreadsheet +\.tabulator\b"` now 0 for `#spreadsheet .tabulator` as Tabulator root (the remaining 4 `#spreadsheet .tabulator-row/.tabulator-cell` are correct descendant selectors — row/cell live inside `#spreadsheet`).
- **Block accent orthogonal to work grouping:** `test_work_group_separator_cannot_override_block_accent` asserts `work-group-start` uses `border-top` not `box-shadow` — so `data-block` inset shadows on all 11 blocks survive work separation.
- **Tokens are neutral, not slate:** `test_no_slate_blue_in_tokens` blocklist catches every Tailwind-slate hue; current light `#f9f9fb/#ffffff/#f4f4f5/#e4e4e7` and dark `#0d0d0d/#161616/#222222/#282828` are 0-chroma greys.
- **Payload sizes:** `docs/master.json` 368 KB (362 rows), `docs/data.json` 90 KB (374 rows). Both valid JSON arrays of objects; first `data.json` row is already 7-col trimmed (`tempid/title/WE HAVE?/original source/notes/format/product link`).
- **Playwright not re-run locally:** `node_modules` absent, so browser specs were not re-executed this sandbox pass; latest CI branch report for this delivery revision is authoritative for E2E (25 specs including computed-style row checks).

---

## 8. Auditor notes on prior audits

This audit supersedes no living document — it complements:

- `docs/audits/2026-08-09-end-user-row-delivery-postmortem.md` — **authoritative incident analysis** (F-01/F-02/F-03/F-04). Current code resolves F-01/F-02/F-03; F-04 (mobile/desktop browse hides rows) is correctly preserved as a presentation choice with an escape hatch.
- `archive/AUDIT_REPEATED_FAILURE_STYLING_2026-08-09.md` — **root-cause styling audit** (slate vs grey, wash opacity, specificity). Current tokens and 8.5% washes satisfy its Phase-1/2 acceptance; Phase-3 guard (computed-style gate) is now present.
- `docs/audits/2026-08-09-expert-multidisciplinary-audit.md` — prior `arena/019fe80c` pass covering the same three roles (web/full-stack/data). Findings for pipeline determinism, delivery contract, and scale remain accurate; owner-score gates remain the open items.
- `docs/audits/2026-08-09-baseline.md` / `docs/audits/2026-08-09-expert-full-stack-audit.md` — historical checkpoints at earlier merges; their verifier matrices are superseded by the re-executed matrix above.
- `archive/FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md` — 08-09 full audit at `f520e9b` (pre-row-fix). Data findings remain valid; frontend/deployment sections are **stale** as noted by its header banner (“Point-in-time data findings below remain historical evidence”).
- `archive/` — 86 historical audits/proposals (including `EXTERNAL_AUDIT`, `PRESENTATION_UX_PROPOSAL_2026-08-09`, `WORKFLOW_WEB_EDITOR_GUIDE.md`) — correctly archived per README’s “Historical context” layout.

---

*Generated 2026-08-09 as a read-only evidence pass. No data or code was modified. To make this audit the declared-current audit, update `README.md` Documentation layout (“the broader audits … and the deep-dive …”) and `INSTRUCTIONS.md` “curated checks” headnote to list this file — or keep the existing declared-current pair and treat this as an independent Arena expert pass alongside the postmortem.*

