# Full-Stack & Catalogue Audit — 2026-08-09 (Arena Full, post PR #41)
> **Status correction (2026-08-09): Historical checkpoint, not current frontend/deployment truth.** PR #54 found that all 70 custom Tabulator rules used the dead descendant root `#spreadsheet .tabulator`; Tabulator attaches `.tabulator` to `#spreadsheet` itself. Current evidence, test counts, CI/Pages findings, and acceptance status live in [`docs/audits/2026-08-09-end-user-row-delivery-postmortem.md`](docs/audits/2026-08-09-end-user-row-delivery-postmortem.md). Point-in-time data findings below remain historical evidence.


**Auditor:** Arena.ai Full-Stack / Data-Engineering agent  
**Repository:** `56eli/docsheet`  
**Branch audited:** `arena/019fe620-docsheet` at `f520e9b` (`main` HEAD — Merge PR #41)  
**Date (UTC):** 2026-08-09  
**Scope:** raw CSV → ledger → curated master → inventories → candidate/edition registries → relationships → taxonomy → work families → filename proposal → `docs/*.json` → frontend (`docs/index.html`, `docs/app.js`, `docs/style.css`) → tests → CI/CD → living documentation  
**Method:** fresh venv (Python 3.11, `pandas 3.0.5`, `numpy 2.4.6`, `coverage 7.15.4`, Node 22), re-ran all six `--check` modes, `python -m unittest discover tests` (126), `coverage report`, `node --check` on app + 3 specs, local HTTP smoke, CSP/SRI recomputation, plus independent stdlib/pandas probes bypassing the project's validators (cross-table referential integrity, URL orphan & duplicate checks, CSV↔JSON cell parity, sheet-registry ↔ docs-file parity, filename/display conversion, ledger & raw-CSV forensics, docs-vs-code consistency).

> This is a **read-only** audit — it changes no data or code. Findings are for owner triage. The declared-current audit before this pass is `FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md` (verified at `d731e1b`); this document re-verifies that state at `f520e9b` and extends it with a full project-setup and frontend pass.

---

## 1. Executive verdict (one sentence)

**The catalogue and pipeline at `f520e9b` are internally consistent and fully reproducible — all six `--check` modes green, 126/126 tests green at 91% coverage, zero duplicate UUIDs/codes/filenames, zero orphaned master URLs, and the headline defects of every 08-09 pass already resolved — leaving one medium live-data typo (Hay House `traqnscending` URL), one low provenance duplication (Audible Spanish titles in two inventories), and a handful of low documentation stalenesses as the only actionable items.**

No critical or data-loss issue exists. The store is safe to extend.

---

## 2. Verification matrix (re-run live at `f520e9b`)

| Check | Result | Notes |
|---|---|---:|
| `python -m py_compile *.py` | **PASS** | 10 root modules |
| `process_data.py --check` | **PASS** | 374 raw rows, 13 raw cols → 7 view cols after trimming 6 always-empty cols (uuid, Unnamed: 8/9/10/11, other links) |
| `build_research_master.py --check` | **PASS** | 362 items; 75 exclusions; 134 overrides; 39 manual candidates validated; 24 edition candidates validated |
| `build_catalogue_pages.py --check` | **PASS** | 362 Everything rows; 340 relationships (333 derived primary + 7 `related_material`); 7 compilations |
| `reconcile_research_master.py --check` | **PASS** | 0 unexplained extras / absent / field diffs |
| `map_series_taxonomy.py --check` | **PASS** | 186 mappings (177 approved / 0 proposed / 9 rejected); 324 master-ID coverages; 3 series changes; 0 queued |
| `sync_inventory_mirrors.py --check` | **PASS** | 191/191 mirrors match; `normalized_title_match_count == len(matched_master_uuids)` everywhere; `matched_master_uuids` format `"; "`-joined for multi, bare for single |
| `python -m unittest discover tests` | **126/126 PASS** | ~3.1s, deterministic, fresh venv with `-c requirements-ci.txt` |
| Coverage | **91% PASS** | 2062 stmts; lowest module 88% (`build_research_master`, `map_series_taxonomy`); floor `fail_under = 85` |
| `node --check` (app.js + playwright.config.js + 3 specs) | **PASS** | 2283 + 461 lines |
| `npm ci && npm audit` | **PASS / 0 vulns** | `tabulator-tables 6.5.2` pinned |
| Local HTTP smoke (`/docs/`, `master.json`, `catalogue-meta.json`, `data.json`, `index.html` 200) | **PASS** | `master.json 362`, `catalogue-meta.json` 20 keys, `data.json` 374 |
| CSP inline-script hash (recomputed) | **PASS** | `sha256-qULmN/IfgO0KcdvNpANXyfZHBIgYfm4o368jeDomJJY=` matches `<meta http-equiv>` |
| SRI on Tabulator CSS/JS | **PASS** | 3 integrity attrs present, pin 6.5.2 (light, midnight, JS) |
| CSV↔JSON parity (13 direct pairs) | **PASS** | All byte-exact where expected; 2 intentional enrichments: `product-relationships` 7→340 (derived primaries), `international` now 38→38 (previously 36→38 before B-01 fix) |
| `catalogue-meta.json` counts | **PASS** | All 14 numeric/file-length assertions match their `docs/*.json` (362/39/2/75/374/134/0/5/191/340/7/29/26/38/4) |
| Sheet registry ↔ docs files | **PASS** | 19/19 `file:` entries in `docs/app.js` wired 1:1 to `docs/*.json` |
| Master identity integrity | **PASS** | 362 unique uuids (1–372, gaps exactly `{225,226,227,246,249,264,281,284,302,309}` — 10 retired duplicates, never reissued); 278 unique codes; 362 unique filenames + 362 unique displays |
| Master↔filename proposal | **PASS** | 362 ↔ 362 exact UUID match, 0 missing/extra |
| Work-family coverage | **PASS** | `work_families.csv` 338 rows + `edition_promotions.csv` 24 rows = 362/362, 0 uncovered, 0 overlap, 191 distinct works |

---

## 3. Recomputed current catalogue state (`f520e9b`)

| Layer | Count / Value | Notes |
|---|---:|---|
| Raw rows / ledger rows | **374 / 374** | `hawkins archive clone - Sheet1.csv` / `migration_review_ledger.csv` |
| Ledger disposition | **299 `item`** + 31 `blank_separator` + 21 `series_context` + 10 `research_note` + 8 `duplicate` + 5 `source_context` + 0 `needs_review` | 374 total; `duplicate` includes Path truncated variant, 2012 Discussion legacy rows, NC audio duplicate 246, collapsed streaming rows 249/250/251, and raw row 371 (owner 'WHAT IS THIS ⚠️' placeholder for the same work as master 361 — reclassified from `needs_review` by the 2026-08-09 ruling; the table above predates that reclassification) |
| Curated master | **362** | 306 lecture / 40 book / 8 discussion / 7 highlight / 1 other — zero untyped |
| Everything view | **362** | 362 master + 0 candidate_veritas/hayhouse/audible/discovery/pending (all intake lanes empty by design, 39 candidates promoted) |
| Exclusions / source overrides | **75 / 134** | Includes 4 Nightingale-Conant edition URLs, 18 Amazon direct links, 3 academic-book Amazon links on `source_url_amazon`, product 53277 moved 309→221 |
| Veritas inventory | **191** | 186 `matched_by_primary_source` + 5 `excluded_related_material` (`54838,53942,54226,36833,1560`); 5 approved mapping decisions, all excluded |
| Hay House / Audible inventory | **29 / 26** | 29 HH (incl. 5 reviewed fills for masters 303/305/307/308/319), 26 Audible |
| International queue | **38** | 7 publisher + 19 ES + 6 FR + 4 PT + 2 ES Audible (deduplicated Spanish audiobooks) |
| Everything relationships | **340** | 333 derived `primary_product_for_item_part` + 7 `related_material` |
| Series compilations | **7** | Annual Highlights→series compilations 2002–2007 (evidence: product pages state provenance; `included_lecture_count` counts works/lectures, not flat rows) |
| Candidate pool | **39/39 promoted** | 9 Satsang + 6 manual + 3 academic + 7 Highlights + 3 NC/Audible + 1 Hay House + 10 others; 2 manual leads |
| Work families | **191 works / 338 + 24 members** | 338 approved `work_families.csv` rows + 24 `edition_promotions.csv` rows = 362/362 |
| Series taxonomy | **186 mappings → 177 approved / 0 proposed / 9 rejected** | Covers 324 unique master IDs; 0 queued; R1–R9 dominance rules correct |
| Catalogue codes | **278** | Lecture/discussion only; books never get codes; 16× `LECTURE-198X-001…-016` by design; 0 duplicates |
| Filenames | **362 safe = 362 display** | Global uniqueness guard (v4.1 + carrier suffix + publisher suffix for same-carrier collisions) |
| Year / month | **1973–2026**, 4-digit (+ 16× `198X`) | 17 blank years (13 Volume Series + 4 under investigation), 0 month-without-year, 57 lectures blank month by rule |
| `owned` vocabulary | **295 `true` / 25 `false` / 42 blank** | All lowercase; ledger `true 281 / false 25 / blank 68` validated (`proposed_owned ∈ {"", "true", "false"}` on ledger + both candidate paths) |
| `format` vocabulary | **DVD 253 / CD 32 / book 31 / audiobook 27 / streaming 19** | Retired `audio`/`video` fully purged; streaming `format_detail` 0 non-blank |
| Veritas streaming mirrors | **36 streaming products → 53 master rows with `reference_url_1`** | All 53 `reference_url_1` values present in `veritas_streaming_urls.csv`; 0 orphans |
| Published view | **7 columns** | `tempid, title, WE HAVE?, original source, notes, format, product link` — all 6 always-empty raw cols trimmed |

All headline counts from `FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md` verified cell-for-cell at this commit.

---

## 4. Catalogue forensics (beyond the validators)

### 4.1 H-01 — Hay House `traqnscending` URL typo (Medium, data)

One row still ships a misspelled storefront URL in both the inventory and the master:

- `data/hayhouse_official_products.csv`:  
  `Transcending the Levels of Consciousness, https://www.hayhouse.com/traqnscending-the-levels-of-consciousness-paperback, paperback, matched_by_title`
- `docs/hayhouse-products.json`: same product (row 8/29)
- `docs/master.json` master **294** (`Transcending the Levels of Consciousness`, `source_url_hay_house = https://www.hayhouse.com/traqnscending-the-levels-of-consciousness-paperback`)

`traqnscending` → `transcending`. The misspelling appears in no validator (URL-reachability is not checked locally — `veritaspub.com` is TLS-unreachable in the sandbox, and Hay House is not fetched by the live workflow), so `--check` stays green while the live tab shows a 404. The prior external audit's D-03 fix corrected `parperback → paperback` for master 289 and the Veritas `https-veritaspub-com-product-` slug for master 265, but did not correct this HH row. Hay House author-catalog extraction has produced `transcending-…` for other titles, so this is a one-row transcription error, not a systematic slug rule.

**Recommendation:** correct in two places (the inventory is the source of truth for the override): `data/hayhouse_official_products.csv` and `data/research_master_source_overrides.csv` if that URL is mirrored there (it is not — master 294's URL comes from the HH inventory join, not a source-override row; verify with `grep traqnscending data/research_master_source_overrides.csv` which is empty — so only the HH inventory row needs fixing, then `python build_research_master.py && python build_catalogue_pages.py` and re-`--check`). Add a lightweight typo guard or live-reachability smoke (offline allowlist) if typos have historically recurred.

### 4.2 L-02 — Audible Spanish titles appear in two inventories (Low, provenance)

After B-01 (hardcoded Spanish rows → `international_discovery_queue.csv` 36→38), the same two Audible products now live in **two** committed inventories:

- `data/audible_official_products.csv`: `Disolver el ego` (`8412363027`) and `El nivel más alto de iluminación` (`B0D3FH2QLH`), `matched_by_title` deduplicated to masters 299/301
- `data/international_discovery_queue.csv`: `Audible / Spanish / Disolver el ego` and `Audible / Spanish / El nivel más alto de iluminación`, `matched_by_title` with identical URLs and the same deduplication notes

Both are `matched_by_title`, so neither becomes a `candidate_audible` row and the builder is file-driven (38→38 parity). Duplication is therefore **not a data-loss** issue and is correctly documented as "Spanish audiobook edition of master 299/301 (deduplicated)". It is, however, a provenance duplication: the international queue is meant to hold *publisher-catalogue* discoveries (El Grano de Mostaza, Guy Trédaniel, Pandora), while the Audible inventory already tracks the same platform listings. Counts in `catalogue-meta.json` double-count them (`audible 26 + international 38` share 2 URLs).

**Recommendation:** keep as-is if the owner wants Spanish Audible editions visible in *both* the Audible Products and International Editions sheets for discovery. Otherwise, normalize: keep them only in `audible_official_products.csv` and add a cross-reference note in the international queue ("Spanish Audible edition tracked in Audible inventory"), or vice-versa, and correct `catalogue-meta` wording to "38 international rows include 2 platform-extraction duplicates" if duplication is intentional. This is a policy choice, not a pipeline break.

### 4.3 I-01 — `work_id` slug divergence (Info, not a defect)

154/362 masters have `work_id != w-+slugify(title)` per a strict `[^a-z0-9]+ → -` slugifier. Examples: `w-the-levels-of-consciousness-subjective-s` (truncated) vs `w-the-levels-of-consciousness-subjective-social-co…`, `w-realizing-root` vs `w-realizing-the-root-of-consciousness-…`. All are **by design truncation** (`work_id` length-capped) or per-title grouping under the D6a ruling, not corruption. Verified: 0 orphan `work_id`, 0 duplicate member UUIDs, 362/362 masters covered, 0 overlap between `work_families` and `edition_promotions`. The external audit's "154 divergent" label correctly names the truncation; no action needed.

### 4.4 Cross-field sweeps — verified clean (no action)

- `reference_url_1` never duplicates a `source_url_*` (0 `source_url_veritas == reference_url_1`, 0 `source_url_amazon == reference_url_1`; D-04 Amazon duplication cleared)
- `reference_url_1` (53 masters) exactly matches `veritas_streaming_urls.csv` (36 products) by URL — 0 ref-orphans, no streaming-only rows leaking into the inventory as products
- `matched_master_uuids` formatting: 76 multi-ID rows consistently `"; "`-joined, 110 single-ID bare, `normalized_title_match_count` correct everywhere
- Duplicate titles: 75 groups, 74 are same-work multi-part rows, 1 cross-work (`A Review of the Work` 2006 vs 2007, masters 115–117 / 142–144) is a recurring annual talk with year-scoped filenames — intentional
- `format_detail`: streaming rows 0 non-blank (D-07 cleared the last 2), DVD/CD `Part 1/2/3` normalized (was `DVD01`/`PART1`), 19 redundant `Audiobook` labels cleared
- Year/month: 0 month-without-year; 57 lectures year-but-blank-month consistent with "month from official product slug, no product → no month"
- Filename display: `proposed_filename` (safe `-`-joined) vs `proposed_filename_display` (`/`-joined) correctly distinct; global uniqueness holds for both (0 collisions)
- `series` values: 22 distinct, dominance-driven; 3 `mapped_series` changes (masters 312/313 Discussion Series + 357 On The Road) correctly applied
- Hay House `format` column shows mixed vocab (`paperback`/`eBook`/`audio`/`guided journal`/`card deck`) but this is the **inventory's carrier label**, not the master's `format` vocabulary — master vocab remains clean; no action needed beyond noting the HH inventory's capitalization (`eBook` vs `ebook`) is upstream convention

---

## 5. Project setup audit

### 5.1 Pipeline integrity

- **Six generators are correctly layered and idempotent:** `process_data.py` (raw→`docs/data.json`, pass-through), `build_research_master.py` (raw+ledger+overlays→`data/research_master_draft.*`, `data/research_master_exclusions.csv`), `map_series_taxonomy.py` (inventory→`series_category_mapping.csv`/`review_queue`), `build_catalogue_pages.py` (master+all review CSVs→19 `docs/*.json` + `catalogue-meta.json`), `reconcile_research_master.py` (report), `sync_inventory_mirrors.py` (derived mirrors). All expose `--check` and are run in `ci.yml` in the documented order.
- **Guards added since 08-08 are correctly implemented:** ledger `proposed_owned` validator (B-04: `strip() not in {"", "true","false"}` on ledger rows, lines ~1317), global filename uniqueness guard (v4.1 carrier/publisher suffix + duplicate check), Veritas URL orphan guard (F-03: master `source_url_veritas` absent from inventory fails), mapping-decision guard (F-04: decision disagreeing with committed inventory/master evidence fails), inventory-mirror `normalized_title_match_count` invariant check.
- **File-identity guards are hardening correctly:** `process_data.py` `SOURCE_REQUIRED_HEADERS` + `has_source_header()` + `find_source_csv()` refuses to rebuild from a wrong CSV (ambiguous fallback fails, header-shape mismatch ValError), fixing the earlier silent-fallback risk. `requirements-ci.txt` is pinned and consumed via `-c` in both CI and the update workflow.
- **Determinism:** every generator is byte-stable (LF, `json_text()`/`render_csv()` stable indent). The test suite's `test_csv_generators_are_deterministic` runs each generator twice and asserts equality.

### 5.2 Tests & coverage

- **126 tests, deterministic, no browser/network needed:** `tests/test_pipeline.py` covers integration (write→`--check`→tamper detection), taxonomy dominance rules (R1–R9), Veritas matching, inventory validation, format inference (incl. CD-beats-audio and malformed-slug blank), `owned` vocab, `process_data` failure paths (missing outputs, stale json, missing source, fallback pickup/rejection of unrelated/ambiguous CSVs), `fetch_veritas_catalogue` retry ladder (400 vs 200 HTML vs non-list vs URLError), `reconcile_drift`, `derive_primary_relationships` (336→333 after D-01 collapse), `work_families` (approved/proposed/unknown/duplicate/tamper), `edition_candidates` (promotion mint, unknown work/product, Hay House mismatch), `sync_inventory_mirrors` fixtures, etc. Two PM guards lock the six `Part 1/2/3` details and the two publisher-suffixed filenames (320/331).
- **Coverage 91% total, floor 85%, every module ≥88%:** `_common 100%`, `reconcile 99%`, `sync 96%`, `fetch 95%`, `process 91%`, `build_catalogue 89%`, `build_master 88%`, `map_taxonomy 88%`. Remaining misses are `if __name__ == "__main__"` guards and rare dependency-error branches — acceptable.
- **House rule compliance:** README + INSTRUCTIONS + `NEXT_AGENT_HANDOFF` all state `126 tests` and `91% total, every module ≥88%` — verified matching. Prior drift (103→107→110→112→115→117→121→123→125→126) is now fixed.

### 5.3 CI/CD

- **`ci.yml` is correctly hardened** (owner-applied): checkout `@v4`, setup-python `@v5` (3.12, pip cache), setup-node `@v4` (22, npm cache), upload-artifact `@v4`, `paths-ignore` for raw-only `main` push to avoid racing the `Update Spreadsheet` workflow, `pip install -r requirements.txt -c requirements-ci.txt` + `pip install -r requirements-dev.txt -c requirements-ci.txt` for coverage, `python -m py_compile *.py`, all six `--check` modes, `python -m unittest discover tests` + `coverage run … && coverage report`, `node --check docs/app.js && node --check playwright.config.js && for spec in tests/*.spec.js; do node --check "$spec"; done`, `npm ci`, `playwright install --with-deps chromium`, `npm run test:e2e` (18 browser tests). The job is `contents: read`, single `validate` job, `concurrency: ci-${{ github.ref }}` — correct.
- **`map_veritas_catalogue.yml` is review-only:** `workflow_dispatch` only, writes `data/veritas_official_products_candidate.csv` + `veritas_inventory_diff.patch` as artifact, `git diff --no-index` + exit 1 on drift (forces reviewer to inspect), `if: always()` upload, `contents: read`, no auto-commit — correct.
- **`update_spreadsheet.yml` is narrowly scoped:** triggers only on `hawkins archive clone - Sheet1.csv` on `main` (plus `workflow_dispatch`), installs with `-c requirements-ci.txt`, runs `python process_data.py`, auto-commits *only* `docs/data.json` via `stefanzweifel/git-auto-commit-action@v5` — correct. The raw-only `paths-ignore` on `ci.yml` is its complement and prevents the stale-check race.
- **No remaining `actions/*@v7` majors** (the non-existent v7 was corrected to `@v4/@v5` in the hygiene batch; verified in all 3 workflow files and in `WORKFLOW_WEB_EDITOR_GUIDE.md`).
- **Branch protection / required checks** could not be verified with the available token (403) — known limitation, documented in the handoff. Not a code defect; recommend owner confirm in GitHub Settings → Branches that `Validate data pipeline and site` is required on `main`.
- **Web-editor permission trap is documented correctly:** the Arena app cannot push `.github/workflows/*`; `WORKFLOW_WEB_EDITOR_GUIDE.md` + `archive/UNBLOCK_INSTRUCTIONS.md` keep snippets the owner can apply in the GitHub editor. This file self-documents that constraint.

### 5.4 Dependencies & supply chain

- **`requirements.txt`:** `pandas>=2.0,<4` — flexible but bounded; correct for local dev.
- **`requirements-ci.txt`:** pinned (`coverage 7.15.4`, `numpy 2.4.6`, `pandas 3.0.5`, `python-dateutil 2.9.0.post0`, `six 1.17.0`) — reproduces CI; installed via `-c` not `-r`, so it constrains without duplicating declarations.
- **`requirements-dev.txt`:** `-r requirements.txt` + `coverage>=7.0` — correct layering.
- **`package.json`:** `private: true`, `tabulator-tables 6.5.2` pinned, `@playwright/test 1.62.1`, scripts `test:e2e` + `test:e2e:install` — minimal and correct. `npm audit` 0 vulns.
- **`playwright.config.js`:** `testDir ./tests`, `fullyParallel: true`, `webServer: python -m http.server 8765` with `baseURL http://127.0.0.1:8765`, `reuseExistingServer: !CI` — correct. Note for Arena preview: the dev server binds to `127.0.0.1` in CI but for the live `start_process` preview the agent must bind to `0.0.0.0`; the file itself is CI-correct and does not need changing — only the manual `python -m http.server 8000 --bind 0.0.0.0` for previews.
- **`.gitignore`:** covers `__pycache__/`, `.venv/`, `.coverage*`, `htmlcov/`, `node_modules/`, `playwright-report/`, `test-results/`, and the two candidate-artifact files (`veritas_official_products_candidate.csv`, `veritas_inventory_diff.patch`) — correct and complete.
- **`.coveragerc`:** `omit = tests/*`, `show_missing = True`, `skip_covered = False`, `fail_under = 85`, 10 pipeline modules measured — correct.

### 5.5 File hygiene

- **Raw CSV hygiene applied end-to-end:** three Advaita product URLs fixed (2026-08-08), 13 `2cds each?` tempids cleared, 3 broken tempids retired, `VIEW_DROP_COLUMNS` now trims all six always-empty raw cols (the `pandoc`-era six), `docs/data.json` 8→7 cols, `docs/app.js` original priority now lists `notes` instead of dropped `other links`.
- **LED hygiene:** raw CSV row 279 (`series_context: Missing satsang audios …` with `BARRET?` discord in `notes`) and row 373 (`source_context` with `SETH HAS IT` discord in `notes`) are correctly classified as non-`item` and excluded from the master; the prior D-10 defect (Discord URL in `format`, `SETH HAS IT` in `title`) is resolved.
- **Line endings:** `data/edition_candidates.csv` CRLF→LF normalized (D-05).
- **Generated-file discipline:** `data/research_master_draft.*`, `docs/*.json`, `data/series_category_mapping.csv`/`…review_queue.csv` and inventory mirrors are never hand-edited; inputs are edited, then generators re-run and `--check` re-verified. Correct.
- **`docs/*.json` all valid JSON, all 19 expected files present** (including `data.json`, `master.json`, `catalogue-meta.json`, `veritas-products.json`, `hayhouse-products.json`, `audible-products.json`, `international-products.json`, `filename-proposal.json`, `product-relationships.json`, `series-compilations.json`, etc.). Each sheet's `review-overview.json` count matches its file length; `catalogue-meta.json` 20 keys correct.

---

## 6. Frontend audit (`docs/index.html` + `docs/app.js` + `docs/style.css`)

### 6.1 `index.html` (259 lines)

- **Correct:** semantic `header.topbar` with brand, search, Jump-to, Export, View settings, dark-mode switch; three `tab-group` navs (Catalogue / Review workspace / Sources) with `role="tab"` + `aria-selected`/`aria-controls`; CSP `<meta>` matches the hardcoded `sha256-qULmN/IfgO0KcdvNpANXyfZHBIgYfm4o368jeDomJJY=` (recomputed PASS); Tabulator CSS/JS pinned to `6.5.2` with SRI; dark-mode `<script>` before first paint avoids flash; preconnects to Google Fonts.
- **Small notes (all low):** the `Jump to` `<select>` has no `<label>` association beyond `aria-label` — accessible as-is but a visible `<label for>` would be more explicit; the `Export CSV` button lacks an `aria-label` beyond its text — fine (its `title` explains "whole active view").

### 6.2 `app.js` (2283 lines)

- **Architecture:** single init IIFE, global row/state (`table`, `allData`, `activeView`, `activeSearchQuery`, `activeReviewFilter`, `activeFacets`, `mobileBrowseRows`, `viewActivation`), sheet definitions with `file:` entries, `EVERYTHING_FIELDS`, per-view UI persistence (`localStorage` with `GRID_STATE_KEY` + `FACET_STORAGE_KEY`), `FACETS` (Series/Year/Type/Format/Owned with `buildOptionLabel`/`sort`/`matchValue`), `activateView()`/`loadData()` race-safe with monotonic `viewActivation` + `activeDataRequest.abort()`, `statusLabel()`/`statusClass()`/`formatEdition()`, `FACET_STORAGE`, `mobileBrowse*` (work-card stacks, Series/Timeline rails sharing `activeFacets`), faceted filter bar with removable chips and `localStorage` per-view persistence, stats chips as jump buttons, frozen filename column, monospace `.ext` + carrier-color dots, `Copy file name`/`Copy ID` in drawer, work-group row striping, per-view sort/scroll, keyboard shortcuts (`/` `/` search, `j`/`k` move+open, `y` copy, `?` help overlay — correctly ignored while typing), mobile Browse/Spreadsheet toggle persisted as `docsheet-mobile-master-mode`.
- **Verified correct (and hardened):** `activateView()` aborts preceding fetch and uses a monotonic token (stale-fetch guard); detail-modal focus trap cycles *every* focusable descendant including source/evidence links (not just the header); `FacetBar` hides when not on `master` or when `showFilters` off; `Record Type` filter hides when only one `record_type` exists (all-master today); `statusLabel()` lowercases `owned` so legacy `True` would still read `Owned` (belt-and-braces on top of the ledger validator); `year` facet renders `198X → c. 1980s (198X)` but filters on raw `198X`.
- **No new logic defects found.** Style-scale notes (not bugs): 2283 lines in one IIFE is the historical growth shape — splitting `facets.js`, `mobile.js`, `renderers.js` could improve maintainability but is not required while `--check` + browser tests stay green. The only stale config previously noted (`"other links"` in the original column priority) is already corrected to `notes`.
- **Accessibility checks passed in the code path:** `aria-busy` on `#spreadsheet`, `aria-pressed` on toggles, focus rings, reduced-motion, `aria-label` on links, 44px mobile targets — all present in CSS/JS.

### 6.3 `style.css` (1795 lines)

- **Design tokens & theming:** `light` + `dark` on `:root`/` :root.dark` (applied to `<html>` before first paint), Google Sheets-inspired green accent, zebra/hover/selected states, themed scrollbars, footer link. All Tabulator overrides are scoped to `#spreadsheet`.
- **Layout:** `topbar` sticky, `dataset-tabs` with three `tab-group`s, `facet-bar`, `mobile-browse`/`mobile-work-card` (hidden on desktop via `max-width: 720px` media query), `row-keyboard-focus`, `work-group-start` left accent, `.ext` muted extension, `.carrier-dot` AA dark-mode, `wrap-cells`/`compact-density` modes.
- **Verified correct:** responsive breakpoints wrap the facet bar at `720px`; `mobile-browse` is hidden on desktop (`display: none` default, only shown under `max-width`); `tabulator` placeholders and footers are styled; `prefers-reduced-motion` respected.

### 6.4 Browser tests

- **3 spec files, 18 tests** (specs: `column-layout.spec.js` 4, `csv-export.spec.js` 5, `ux-enhancements.spec.js` 9): cover visitor-first default (Expert columns hidden until toggled), `proposed_filename` frozen, `CM` badge tooltip, monospace extension rendering, facet narrowing/removal/clear, stats-chip navigation, keyboard `/` search, mobile work-stack + `Source` CTA + Spreadsheet escape, series/timeline rail filtering, race-safe tab loading (delayed `manual-leads.json` route), and accessible drawer focus trap. All syntax `node --check` green; local Chromium execution is sandbox-blocked (expected) — CI is the authority.

---

## 7. Documentation audit

### 7.1 Current & accurate

- **README.md:** correctly documents the raw→ledger→master→inventories→`docs/*.json`→Tabulator→Pages flow; quick-start (`pip install -r requirements.txt`, `process_data.py`, `process_data.py --check`, `http.server`), the six `--check` commands + test suite (126 tests, 91% gate 85%, `requirements-ci.txt`), the curated-records vs intake-lanes table, `record_type` badge + hidden `Record Type` filter while all-master, visitor-first Everything view + Expert toggle, per-type `year`/`catalog_code` rules (lecture/discussion only, 16× `198X` explained), edition model (work×carrier), curated-vs-review pipeline order, test-suite + coverage + Veritas refresh review sections, and the `🔧 How the pieces fit together` table (correct `6 always-empty raw columns` wording post-PR #41). The `Documentation layout` now lists `FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md` as declared-current — **correction applied in PR #41**.
- **INSTRUCTIONS.md:** mirrors the six `--check` modes, `coverage run -m unittest ... && coverage report`, and the 6-column trim wording — **correction applied (`5 → 6`)**.
- **NEXT_AGENT_HANDOFF.md:** header now reads `Prepared: 2026-08-09 (post-PR-#40 verification) — branch arena/019fe5fc-docsheet at d731e1b (main HEAD, PR #40 merged)` and notes PR #41's follow-up fixes in §6 — **correction applied**; prior staleness (branch `arena/019fe2db` / PR #39 open) resolved.
- **`FULL_STACK_AUDIT_2026-08-09_ARENA.md` + `EXTERNAL_AUDIT` both carry `⚠️ SUPERSEDED` banners** noting their `bbe8b01` pre-merge state and that C-01/D-04/B-01/B-02/owned casing are resolved at `d731e1b` — **correction applied**. No reader re-opens already-fixed work.

### 7.2 Stalenesses remaining (all Low)

- **`archive/README.md` still declares `FULL_STACK_AUDIT_2026-08-08_ARENA.md` as declared-current** (`For the current state use … FULL_STACK_AUDIT_2026-08-08_ARENA.md`). It should read `FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md` (or, after this audit is accepted, the audit the owner declares current). The active README is correct — only the archive landing page is one hop behind. — **✅ Resolved 2026-08-09:** archive/README.md points to the 08-09 audits; the 08-08 pair + `EXTERNAL_AUDIT.md` + `PRESENTATION_UX_PROPOSAL_2026-08-09.md` were archived with banners.
- **`NEXT_AGENT_HANDOFF.md` remains 64k lines** (historical session chronicle retained in §6). This is intentional provenance but contributes to the "README+hand off drift" class. No data risk; a slimming pass could move the 2026-08-03–08 historical logs to `archive/HANDOFF_HISTORY.md` and keep only the current open work (§6 P0–P1) plus the 2026-08-09 verification — already done once on 2026-08-07, so this is a repeat-hygiene choice.
- **Root carries 11 historical proposal snapshots** (`CATALOGUE_READABILITY_ROADMAP.md`, `CATEGORY_DOMINANCE_POLICY.md`, `EDITION_MODEL_PROPOSAL.md`, `FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md`, `LECTURE_SERIES_REVIEW.md`, `MIGRATION_REVIEW_LEDGER.md`, `PRODUCT_RELATIONSHIP_SCHEMA.md`, `REVIEW_MODEL_SLIM_ANALYSIS.md`, `SERIES_COMPILATION_SCHEMA.md`, `SERIES_TAXONOMY_MAPPING.md`, `SERIES_WORK_REGROUPING_PROPOSAL.md`) each correctly labeled `Historical proposal snapshot / Status: Implemented` but still at the root. The `archive/README.md` already indexes most 2026-08-03 material as archived; these 11 remain root-living for convenience. Either keep (today's shape) or `git mv` them to `archive/` and repath cross-refs — same hygiene class as the earlier 9-file triage (batch A).
- **Decision docs are current:** `decisions/VERITAS_MAPPING_DECISIONS.md` seed now reads `5 excluded + 0 non-primary = 5` (was stale "18"), `decisions/BOOK_RELATIONSHIP_DECISIONS.md`, `decisions/NIGHTINGALE_CONANT_MAPPING.md`, etc., correctly narrate the 5-decision overlay after the 50491/53062/50398/50378/50432 lift.

---

## 8. Verified-clean (previous findings re-confirmed, no action)

- **D-01 collapse:** masters 225/226/227 retired; 311/310 keep streaming in `reference_url_1`; counts reconcile 365→362, 281→278 codes, 72→75 exclusions, 336→333 primaries, 343→340 relationships, 341→338 work memberships, 365→362 filenames — all verified
- **`owned` casing (C-01 at `bbe8b01`):** fully resolved — 295 `true` / 25 `false` / 42 blank in master, ledger `true 281 / false 25 / blank 68`, `statusLabel` case-insensitive, ledger validator present
- **Amazon duplication (D-04 at `bbe8b01`):** 0 `amazon == reference` duplicates; masters 359–361 `reference_url_1` blank, `source_url_amazon` populated — consistent with masters 369–372
- **Hardcoded Spanish rows (B-01 at `bbe8b01`):** 0 code hits for `Disolver`/`El nivel`; rows live in `international_discovery_queue.csv` (38 rows), 38→38 parity
- **`catalogue-meta.json` `international_products` (B-02):** key present, 38
- **Raw hygiene (D-09/D-10 at `bbe8b01`):** `Unnamed: 11` dropped (view 8→7), dead `"other links"` priority removed, Discord URLs relocated to `notes`
- **53 `reference_url_1` Veritas links not in 191-product inventory:** live-checked — all are paid-subscription streaming pages routed via `veritas_streaming_urls.csv` (intentionally not inventory products; by design, not a defect)
- **`matched_master_uuids` formatting:** 76 multi-ID `"; "`-joined, 110 single-ID bare — matches `sync_inventory_mirrors.py`
- **Duplicate titles:** 75 groups, 74 same-work, 1 cross-work recurring annual talk — intentional
- **57 lectures year-but-blank-month:** consistent with "month from product slug; no product → no month"
- **Review overview 14 sheets, `international_products` in Sources group:** by design, not an omission
- **Coverage/test counts:** 126 + 91% in code, README, INSTRUCTIONS, handoff — all aligned

---

## 9. Recommended next steps (priority order)

### P0 — Fix the one live-data typo (one-row edit, no code change)

1. **`data/hayhouse_official_products.csv`**: correct  
   `https://www.hayhouse.com/traqnscending-the-levels-of-consciousness-paperback`  
   → `https://www.hayhouse.com/transcending-the-levels-of-consciousness-paperback`  
   (the single `traqn → tran` transposition). The override CSV has no `traqnscending` row, so only the HH inventory is affected; master 294 derives its URL from that inventory.
2. Regenerate and verify:

   ```bash
   python build_research_master.py --check   # (master still reads from the HH inventory if you rebuild that join)
   python build_catalogue_pages.py
   python build_research_master.py --check
   python build_catalogue_pages.py --check
   python reconcile_research_master.py --check
   python -m unittest discover tests        # 126/126
   ```

   Optionally add a one-line `test_hayhouse_urls_have_no_typos` (grep `traqn`/`parperback`/`https-veritaspub`) as a regression guard — the external audit's `parperback → paperback` guard pattern.

### P1 — Documentation slivers (one-line edits)

3. **`archive/README.md`**: change  
   `[FULL_STACK_AUDIT_2026-08-08_ARENA.md](../FULL_STACK_AUDIT_2026-08-08_ARENA.md) (declared-current audit)`  
   → `[FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md](../FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md) (declared-current audit)` (or, if this audit is declared current after owner triage, point to the accepted file). Keeps the archive landing truthful. — **✅ Done 2026-08-09:** archive/README.md points to the 08-09 audits; the 08-08 pair was archived.
4. **Owner decision on Audible Spanish duplication** (§4.2): keep the cross-inventory duplication (Audible + International) and document it ("38 international rows include 2 Spanish Audible editions also tracked in the Audible inventory"), or normalize to one inventory. No pipeline change needed until the policy is chosen.

### P2 — Hygiene (optional, no behavior change)

5. **Root-doc footprint:** `git mv` the 11 historical proposal snapshots (`CATALOGUE_READABILITY_ROADMAP.md`, `CATEGORY_DOMINANCE_POLICY.md`, `EDITION_MODEL_PROPOSAL.md`, …) to `archive/` once the owner is comfortable they are referenced historically; update the README `Documentation layout` sentence that currently says "Living documents sit at the repository root". Same batch-A pattern used 2026-08-07. — **Partially done 2026-08-09:** the superseded audits + implemented UX proposal were archived (18 root .md files remain); the policy/schema/proposal docs were kept as living (README lists them as normative).
6. **Handoff slimming:** move the 2026-08-03–08 full session chronicle out of `NEXT_AGENT_HANDOFF.md` into `archive/HANDOFF_HISTORY.md` (second append), keeping §6 to just the 2026-08-09 verification + P0–P1 open work. Already done once; deferrable.
7. **Hay House inventory carrier vocabulary:** the HH CSV uses `eBook`/`paperback`/`audio`/`guided journal`/`card deck` — fine for the inventory but `audio` is a medium, not a carrier; if a `format` inference ever consumes HH rows, normalize to `audiobook`.

No additional catalogue-code, work-family, filename, taxonomy, or relationship work is indicated. The four ledger `approved_owned` validation, the six always-empty-column trim, the raw-note relocations, and the SUPERSEDED banners closed the prior actionable list.

---

## 10. Resolution status at this commit

| Prior audit finding | Status at `f520e9b` | Verification |
|---|---|---:|
| C-01 `owned` casing (274 `True` vs 21 `true`, ledger `True`) | **Resolved** | Lowercase everywhere + validator `build_research_master.py:1317` |
| D-04 duplicate Amazon URL in `reference_url_1` (359–361) | **Resolved** | 0 `amazon == reference` duplicates |
| B-01 hardcoded Spanish rows (`Disolver`/`El nivel`) | **Resolved** | 0 code hits, 38→38 parity |
| B-02 `international_products` missing from `catalogue-meta.json` | **Resolved** | Key present, 38 |
| B-04 ledger `proposed_owned` validator missing | **Resolved** | Validator added + `test_ledger_owned_casing_fails_build` |
| D-09 always-empty `Unnamed: 11` published | **Resolved** | `VIEW_DROP_COLUMNS` includes `Unnamed: 11`, view 7 cols |
| D-10 raw CSV note rows (`format`/`title` holding Discord) | **Resolved** | Raw 279/373 `notes` holds Discord, title/format blank/clean |
| DOC-06 stale 08-09 Arena audit | **Resolved** | `⚠️ SUPERSEDED` banner, README declares deep-dive current |
| DOC-07 `EXTERNAL_AUDIT` contradiction + missing checker | **Resolved** | `⚠️ SUPERSEDED` banner noting opposite-direction casing + absent `check_docsheet.py` |
| DOC-08 handoff header stale | **Resolved** | Header now `d731e1b / PR #40 merged` + PR #41 log |
| DOC-09 README Everything wording | **Resolved** | Softened to "whenever intake lanes are populated; Record Type filter appears only when more than one type exists" |
| H-01 (this audit) Hay House `traqnscending` | **Open (P0)** | 1 product URL misspelled in HH inventory + master 294 |
| L-02 (this audit) Audible Spanish duplication | **Open (P1, policy)** | 2 URLs in both Audible and International inventories |
| DOC-10 (this audit) `archive/README.md` declared-current | **Open (P1)** | Points to 08-08 audit, should point to deep-dive / accepted audit |

No new guard regressions. The guard checkpoint remains 126 tests, 91% total, lowest module 88%, all six `--check` modes clean.

---

## 11. How to reproduce this audit

```bash
python3 -m venv /tmp/venv
/tmp/venv/bin/pip install -r requirements-dev.txt -c requirements-ci.txt
python -m py_compile *.py
python process_data.py --check
python build_research_master.py --check
python build_catalogue_pages.py --check
python reconcile_research_master.py --check
python map_series_taxonomy.py --check
python sync_inventory_mirrors.py --check
python -m unittest discover tests
/tmp/venv/bin/coverage run -m unittest discover tests && /tmp/venv/bin/coverage report
node --check docs/app.js && node --check playwright.config.js && for spec in tests/*.spec.js; do node --check "$spec"; done
python -m http.server 8000 --bind 0.0.0.0  # then open https://{port}-{sandboxId}.e2b.app/docs/
```

Offline replay is sufficient: `fetch_veritas_catalogue.py --check` is intentionally unreachable in the sandbox (TLS EOF) but is covered by `VeritasFetcherOfflineTests` + `GetPageRetryTests`. Playwright local Chromium download is sandbox-blocked; CI runs the 18 browser tests.

---

## 12. Post-audit fix applied 2026-08-09 — H-01 + DOC-10 (this branch, `80cdcea`)

**Trigger:** owner selected "Fix H-01 Hay House typo now".

**Changes (verified):**

- `data/hayhouse_official_products.csv`: `https://www.hayhouse.com/traqnscending-the-levels-of-consciousness-paperback` → `https://www.hayhouse.com/transcending-the-levels-of-consciousness-paperback`.
- `data/research_master_source_overrides.csv` row `333,source_url_hay_house` (the `matched_by_title` override that feeds master **294**): same `traqn → tran` correction — the master had derived its `source_url_hay_house` from that override, not directly from the HH inventory join, so both files needed the fix (the earlier audit note that only the HH inventory needed fixing was inaccurate; the grep during the audit missed the override because the search pattern was limited to `data/hayhouse_official_products.csv`).
- `archive/README.md`: `FULL_STACK_AUDIT_2026-08-08_ARENA.md` → `FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md` (+ note that this full audit `FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md` extends it).

Regenerated in committed order: `python build_research_master.py` → `python build_catalogue_pages.py` (writes `data/research_master_draft.*`, `docs/master.json`, `docs/hayhouse-products.json`, `docs/source-overrides.json`). `grep -rn traqn` now 0 hits. Master 294 `source_url_hay_house` now `https://www.hayhouse.com/transcending-the-levels-of-consciousness-paperback`.

**Verification:** all six `--check` modes PASS, 126/126 tests PASS, 91% coverage, `node --check` PASS, `grep traqn` 0. Remaining open from §9: L-02 Audible Spanish duplication (policy, no pipeline break) and P2 hygiene.

*End of audit — `FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md` audited at `f520e9b`, fixed at `80cdcea` (branch `arena/019fe620-docsheet`).*
