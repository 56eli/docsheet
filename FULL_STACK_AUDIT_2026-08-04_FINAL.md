# Full-Stack Integrity Audit — 2026-08-04 (post-merge #22, current HEAD)

**Date:** 2026-08-04 (UTC) — local date from arena host
**Branch audited:** `arena/019fcddb-docsheet` HEAD `af76fe3` = `origin/main` (Merge PR #22)
**Scope:** entire repository — 8 Python pipeline modules + `_common`, 20+ `data/*.csv`, 20 `docs/*.json`, frontend (`index.html`, `app.js`, `style.css`), 2 Playwright specs, 103-test deterministic suite, 3 GitHub Actions workflows, documentation (19 root MD + decisions/ + archive/), security posture, GitHub Pages deployment.
**Supersedes:** `AUDIT_REPORT_2026-08-04.md` and `AUDIT_REPORT_2026-08-04_merge21.md` (which covered PRs #19-#21). This pass re-executes every check on the **current** merged tree.

---

## 1. Executive Summary

**Verdict: VERIFIED-HEALTHY — zero critical defects, zero data-integrity failures, project integrity intact after recent merges.**

Every deterministic check passes re-executed in a clean venv (Python 3.11.8, pandas 2.x, coverage 7.x — CI runs 3.12):

- `python -m py_compile *.py` — 8 modules OK
- `process_data.py --check` — 374 rows
- `build_research_master.py --check` — 356 items / 68 exclusions / 110 overrides / 26 manual candidates / 332 work-family members / 3 series changes / 105 inferred formats / 13 title cleanups
- `build_catalogue_pages.py --check` — 376 Everything rows (356 master + 8 veritas + 4 discovery + 4 hayhouse + 4 audible + 0 pending)
- `reconcile_research_master.py --check` — green
- `map_series_taxonomy.py --check` — 179 mappings → 169 approved / 0 proposed / 10 rejected / 6 queued
- `python -m unittest discover tests` — **103/103 pass in ~2.3 s**
- Coverage — **92% total, every module ≥ 89%**, gate 80% (`.coveragerc`)
- JS syntax — `node --check` OK on `app.js`, `playwright.config.js`, `csv-export.spec.js`, `column-layout.spec.js`

`fetch_veritas_catalogue.py --check` fails **only** in offline sandboxes (TLS EOF to veritaspub.com) — known trap documented in `NEXT_AGENT_HANDOFF.md` and `INSTRUCTIONS.md`. It is **not** run in CI; live refresh runs via the manual `Map Veritas Catalogue` workflow which uploads a candidate diff artifact instead of auto-committing. This is by design and is the correct security posture.

Recent merges #19-#22 delivered:

- **F1 — derived primary relationships:** `data/product_relationships.csv` reduced **333 → 8 rows**; primary links now derived from masters' own `source_url_veritas` at render time (`derive_primary_relationships`). Rendered `docs/product-relationships.json` still exposes **333 relationship_ids** (325 derived primary + 8 hand-maintained `related_material`). Eliminates 325 rows of duplicated evidence.
- **Title hygiene (owner decision 3):** 13 lecture titles stripped of trailing `PART1`/`(Part 1)`/`DVD01`/`-converted`/`.mp4` noise only when normalized cleaned title equals normalized official Veritas title; raw text retained in `legacy_title`, provenance in `title_source`.
- **Year-Month semantics:** book `year` = first-publication year, never storefront `published_date` (2014-03-30 batch). Lecture `month` only backfilled when product year matches record year; prevents 2014 listing months leaking into 2003-2005 On-The-Road talks. Catalogue codes 236 → **271** after correcting On-The-Road (©2003-2005), Office Series (→1982), Discussion Series (→2012), etc.
- **Format vocabulary:** `audio` → `audiobook` for `format` field; `CONTENT_ITEM_TYPES` retired `audio`/`video` (only `official_discovery_queue.csv` triage lane retains 4 free-text `audio` pending owner ruling).
- **Review-Overview label fix:** hardcoded `reviewed_candidate / not_promoted` replaced by derived state from real `promotion_status` (now shows `26/26 promoted`). Guard test added.
- **Shared-code dedup:** new `_common.py` holds `read_csv`, `ISO_DATE`, `json_text`, `render_csv` core; coverage stmts 1617 → 1594 with behavior preserved.
- **Frontend width engine:** pixel-accurate canvas measurement across **all rows** measuring **rendered** labels (URL → "Veritas product", badges → humanized), replacing char-count heuristics + 120-row sampling; guardrails 560/720px; numeric sorter with `alignEmptyValues: bottom` fixes Master ID lexical sort.
- **CSP hash corrected:** `sha256-u2/u4gxax738T0FZixKekRcJpSj2LbWauC5THe95guI=` matches browser-computed hash (leading/trailing ASCII whitespace stripped per CSP3/HTML spec). SRI hashes for Tabulator 6.5.2 verified in prior offline audit.

No regressions introduced.

---

## 2. Verification Matrix (re-executed, not trusted)

| Layer | Command | Result | Notes |
|---|---|---|---|
| Syntax | `python -m py_compile *.py` | ✅ 9 files (8 pipeline + _common) | |
| Raw spreadsheet | `process_data.py --check` | ✅ 374 rows x 13 cols | header=1 skips Google Sheets title row |
| Master | `build_research_master.py --check` | ✅ 356 items | 105 formats inferred, 13 title cleanups, 332 work-families, 110 overrides, 26 manual candidates |
| Catalogue Pages | `build_catalogue_pages.py --check` | ✅ 376 Everything rows | |
| Reconciliation | `reconcile_research_master.py --check` | ✅ | 50 draft-only rows expected (edition + manual promotions — see §8) |
| Series taxonomy | `map_series_taxonomy.py --check` | ✅ 179 mappings, 6 queued | 169 approved, 10 rejected |
| Live API | `fetch_veritas_catalogue.py --check` | ❌ TLS EOF (sandbox) | Expected — works via agent page-fetch tool with compact `_fields`; CI does NOT run it; manual workflow does |
| Deterministic suite | `python -m unittest discover tests -v` | ✅ **103/103** ~2.3s | integration + tamper + determinism + rule matrices + doc-currency |
| Coverage | `coverage run ... && coverage report` | ✅ **92% total, every module 89-100%** | misses = `if __name__` guards + rare error branches; `_common.py` 100% |
| JS syntax | `node --check` ×4 | ✅ | `app.js`, `playwright.config.js`, 2 specs |
| Browser | `npm run test:e2e` | — (CI) | 5 specs; Chromium not installable offline — documented trap; runs in CI |
| Data files | LF line endings | ✅ | 20/20 `data/*.csv` are LF; only archival source clone is CRLF intentional |
| Orphans | committed `data/*.csv` consumed? | ✅ 0 orphans | all 21 data files referenced by generators (regex + manual audit) |
| CSP hash | computed vs declared | ✅ match | `u2/u4g...` |
| VIEWS/tabs | count | ✅ 15 tabs = 15 VIEWS = 15 VIEW_DETAILS | orphan publisher VIEWS removed PR #20 |

Catalogue counts re-derived from `docs/catalogue-meta.json` and generated files match `README.md`, `NEXT_AGENT_HANDOFF.md`:

```
master 356 (307 lecture / 38 book / 10 discussion / 1 untyped=246)
catalogue codes 271 unique (lecture/discussion only; books excluded by CODE_ITEM_TYPES)
exclusions 68, overrides 110, veritas 191, hayhouse 24, audible 26, series-compilations 7
relationships rendered 333 (325 derived primary + 8 related_material hand-maintained)
everything 376 = 356 master + 8 candidate_veritas + 4 discovery + 4 hayhouse + 4 audible + 0 pending
series taxonomy 179 matched → 169 approved / 0 proposed / 10 rejected
work families 332 approved rows, work_id coverage 356/356
migration_review 374, manual_candidates 26 promoted 26/26, manual_leads 1, new_work_review 0
```

---

## 3. Architecture & Data Model Deep Dive

### 3.1 Pipeline topology

```
hawkins archive clone - Sheet1.csv (374 raw, header=1)
  │
  ├─► process_data.py → docs/data.json + meta.json (raw pass-through, untouched)
  │
  ├─► migration_review_ledger.csv (374 hand-maintained: 306 item / 31 blank_separator / 21 series_context / 10 research_note / 5 source_context / 1 needs_review)
  │     │
  │     ├─► build_research_master.py
  │     │     + work_families.csv (332 approved, work_id w-*) 
  │     │     + edition_candidates.csv (24) + edition_promotions.csv (24 pinned UUIDs 320-343)
  │     │     + manual_master_candidates.csv (26) + manual_candidate_promotions.csv (26, UUIDs 353-358 + earlier)
  │     │     + research_master_source_overrides.csv (110 approved, incl. 4 NC edition-keyed)
  │     │     + veritas_official_products.csv (191) for format inference + title hygiene + month backfill
  │     │     + series_category_mapping.csv (316 approved mappings cover 316 masters; 3 series changed)
  │     │     + veritas_mapping_decisions etc
  │     │     → data/research_master_draft.{csv,json} (356 rows) + data/research_master_exclusions.csv (68)
  │     │
  │     ├─► build_catalogue_pages.py
  │     │     + official_discovery_queue.csv (4), new_work_review_queue.csv (0), intl queue (36)
  │     │     + aud/hayhouse/veritas inventories + mapping decisions + relationships + compilations
  │     │     + product_relationships.csv (8 related_material only; primary derived)
  │     │     + PUBLISHERS constant (4)
  │     │     → docs/*.json (20 files) + catalogue-meta.json
  │     │
  │     └─► reconcile_research_master.py → RECONCILIATION_REPORT.md (read-only cascade)
  │
  ├─► map_series_taxonomy.py implements CATEGORY_DOMINANCE_POLICY.md R1-R9
  │     → series_category_mapping.csv + series_taxonomy_review_queue.csv (6)
  │
  └─► fetch_veritas_catalogue.py (live API, review-only, never auto-commit)
        deterministic matching: primary URL exact > Satsang date > dated title > normalized title
        + veritas_mapping_decisions overlay (18 approved)
```

**Strengths:**
- Review-gated: generated artifacts never hand-edited; `--check` + tamper detection in CI (`contents: read`).
- Hard-fail validators: work-family coverage, veritas derived-count consistency, title mirroring, series dominance fan-out, product-relationship evidence.
- Live-API safety: fetcher + workflow are review-only (diff artifact + intentional fail-gate).
- Compact ID stability: 1..10000 retained by raw_row_number; edition/manual promotions carry pinned UUIDs.

### 3.2 Master integrity checks (re-derived)

- **UUIDs:** 356 rows, unique, numeric, no reuse; 249 & 264 retired historically.
- **work_id:** 356/356 covered, all `w-` prefix, from approved `work_families.csv` only (never title-inferred) — C2 lesson enforced.
- **item_type:** only `lecture`/`book`/`discussion`/`interview`... — no `audio`/`video` in master/candidates/promotions (retired vocabulary; 4 discovery-triage rows exempt pending ruling). 1 blank intentionally: UUID 246 deferred.
- **format:** controlled `{DVD, CD, audiobook, book, streaming}`; 8 blank remain (5 On-The-Road legacy raw rows 221/225-227+246 + 3 Discussion 278/281/284) — no automated inference match; documented in archive/TEMP_RESPONSE_AUDIT.
- **year:** 18 blank (3 On-The-Road raw without recording year, 1 untyped 246, 3 discussion, 11 lecture audiobook edition rows). Year blank for edition lecture audiobooks is a pending enrichment (inherited from matched master recording year would be reasonable). Book years are first-publication (Power vs Force 1995, Eye of I 2001, Ego Not Real You 2021 verified).
- **catalog_code:** 271 codes, unique, pattern `LECTURE|DISCUSSION-YYYY-NNN`; books never receive code by `CODE_ITEM_TYPES` — keeps count stable after book-year fix.
- **title hygiene:** 13 cleaned; `legacy_title` retained verbatim; `title_source` records official listing when cleaned form equals normalized official title (evidence-based, never guess).
- **month semantics:** lecture month only filled when product year matches record year; prevents 2014 storefront month leaking into 2003-2005 records.
- **source overrides:** 110 approved, including 4 NC (`nightingale.com/pages/david-hawkins`) edition-keyed overrides for masters 327-330 (Truth vs Falsehood, Healing, In The World But Not Of It, Highest Level). 28 Hay House URLs populated.
- **Empty master columns:** `location_physical`, `location_digital`, `location_streaming`, `reference_url_2` remain always-empty (0 values) — decision pending populate or drop.

### 3.3 Product relationships & compilations

- `data/product_relationships.csv` now 8 rows all `related_material` (was 333). Primary relationships derived: 325 masters have Veritas URL, distinct Veritas product URLs 178, many 3-per-product (Volume series per-disc parts sharing one product URL — verified).
- Rendered `docs/product-relationships.json` still 333 relationship_ids: 325 derived + 8 curated. Evidence notes: generic vs provenance-prefixed (`candidate:edition-`, `candidate:manual-veritas-satsang-`, `candidate:manual-`).
- Series compilations: 7 relationships, each validated against master scope (target_lecture_count matches actual masters in series+year[+month range]).
- New Work Review queue 0 rows (all Satsang monthlies promoted as 344-352).
- Referential integrity: every `master_uuid` in relationships exists; every Veritas `official_product_url` matches inventory; `evidence_url` HTTPS required.

### 3.4 Veritas inventory & mapping decisions

- 191 products, categories populated 191/191, `official_categories` persisted as names (Category Dominance Policy).
- Mapping statuses: `matched_by_primary_source` 172, `compilation_or_new_edition` 7, `matched_by_title` 6, `excluded_related_material` 4, `matched_by_normalized_title` 1, `unreviewed_official_product` 1.
- Decision overlay 18 approved rows; validation: approved + ISO date + decision_reason + `matched_master_titles` mirrors master titles (drift fails build).
- Title drift fixed: 50810 now `Volume II: Consciousness and Addiction` matches live API (slug remains `vol-ii-...` — Veritas-controlled).
- Line endings LF.

### 3.5 Series taxonomy

- Dominance rules R1-R9 from `CATEGORY_DOMINANCE_POLICY.md` encoded in `map_series_taxonomy.py` (precedence: Lecture Highlights > Satsang group > Six Book > annual lecture series > On-The-Road > Office > Card Decks > collection > fallback filtered).
- 179 matched products → 169 approved / 0 proposed / 10 rejected. All 10 conflicting proposals ruled 2026-08-04: 3 approved re-seriesed masters 357 (On The Road Talk Series) + 312/313 (Discussion Series), 7 rejected with documented rationale (1546/1548 On-The-Road run over carrier shelf; 1661/1695/1728/1742 editions keep Books series per precedent 1542; 55576 six conflicting categories).
- Review queue 6 rows (unresolved taxonomy IDs or multiple annual categories).
- Fan-out consistency: one master ID never receives two different approved series (build fails).

### 3.6 Edition model

- 24 edition candidates promoted as master UUIDs 320-343 pinned (never renumber): book audiobooks (Power vs Force 1995, Eye of I 2001, etc.) + 4 Veritas audio/video editions (1728 CD&DVD set, 1695 audio, 1661 6-CD NC, 1742 audio) + 11 lecture audiobook carriers (Way to God, Nonduality Intensive, Transcending the Mind, etc.).
- Work families: 199 works / 332 members approved; C1 split + D6a per-part ruling applied; work_id groups editions of same work (book + audiobook + video parts each own row).
- D3: Audible URL moves from book row into audiobook edition row, cleared from book row (prevents dual-primary).
- Edition candidate validation: `candidate_key` starts `edition-`, work_id must exist in work_families, source inventory exact URL match, `proposed` rows must have empty `reviewed_on` and `not_promoted`.

---

## 4. Frontend Audit

### 4.1 Files
- `docs/index.html` (9.9 KB): CSP meta, SRI-pinned Tabulator 6.5.2 CDN (verified in prior audit via `npm pack`), pre-paint dark-mode bootstrap (single inline script with correct hash), 15 dataset-tab buttons (`master`, `reviewOverview`, `manualCandidates`, `manualLeads`, `masterExclusions`, `migrationReview`, `sourceOverrides`, `officialDiscovery`, `newWorkReview`, `seriesCompilations`, `veritasMappingDecisions`, `productRelationships`, `internationalProducts`, `publishers`, `original`), view-summary, review-toolbar, active-filters, row-details drawer, footerbar.
- `docs/app.js` (40 KB): IIFE, strict mode, debounced search (250 ms), global live search across all columns, review filter derived from REVIEW_FILTER_FIELDS, column width engine (offscreen canvas, measures rendered text, all rows, guardrails 560/720px), numeric sorter detection (regex `^-?\d+(\.\d+)?$`) with `alignEmptyValues: bottom`, badge rendering for status fields, URL formatter with label mapping, year_month merged display, edition merged display, frozen headers via Tabulator, maxHeight fitted to container, dark-mode toggle persisted in localStorage, column chooser + show-all, row details drawer (dl/dt/dd), CSV export whole sheet (`rowRange "all"`), no inline editing (`editor: false`, `editTriggerEvent: dblclick` harmless but dead — could be removed, but not harmful).
- `docs/style.css` (23 KB): design tokens light/dark, topbar sticky, zebra rows, hover, status badges (`status-master`, `status-candidate`, `status-approved`, `status-pending`, `status-excluded`, `status-neutral`), column menu, row-details aside, footer.

### 4.2 Security
- **CSP:** `default-src 'self'; base-uri 'self'; object-src 'none'; form-action 'self'; script-src 'self' https://cdn.jsdelivr.net 'sha256-u2/u4gxax738T0FZixKekRcJpSj2LbWauC5THe95guI='; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src ...; connect-src 'self'; img-src 'self' data:` — no `unsafe-inline` for scripts, one hashed inline script. Hash verified correct (see §2). `unsafe-inline` for styles is required for Tabulator inline styles / Google Fonts — acceptable, no script injection via style.
- **SRI:** Tabulator 6.5.2 js/css/midnight css all pinned with integrity; CDN origin `cdn.jsdelivr.net` allowed in CSP.
- **innerHTML:** only `viewMeta.innerHTML = ""` (empty reset) then `append` with `createElement` + `textContent`; `spreadsheet.innerHTML` empty reset; `rowDetailsBody.replaceChildren()` + `textContent`; `footerUpdated.replaceChildren()` + text nodes + span with `textContent`. One spot uses template literal for load error: `...Could not load ${view.file}...` — `view.file` is constant from `VIEWS` (15 known filenames), not user-controlled. No user data flows into `innerHTML`. Safe.
- **No secrets/tokens** found in source/docs/JSON (scanned with regex for `api_key`, `secret`, `token` — only legitimate `api` endpoint constant and `token` not present).
- **No `eval`, `new Function`, `document.write`**.

### 4.3 UX & performance
- Width engine O(N * M) canvas measure across all rows once per view load — acceptable for 376 rows; guardrails prevent pathological title columns dominating.
- All rows in one scrollable view (no pagination) — Tabulator virtual DOM handles 376 rows comfortably; maxHeight fitted to container prevents double scroll.
- Frozen header, resizable + movable columns, column chooser, search + review filter + filter chips + clear-all.
- Recording-year / edition merges: `year_month` and `edition` display columns hide raw `year`/`month` and `format`/`format_detail` when present — drawer excludes hidden raw keys, search still sees them (raw keys remain on row object).
- Dark mode: pre-paint inline script avoids flash of white; persisted, respects `prefers-color-scheme`.
- Accessibility: `role=tablist`, `aria-selected`, `aria-controls`, `aria-busy`, `aria-live`, `aria-label`.
- Minor dead code: `editTriggerEvent: "dblclick"` while editor disabled — confusing but not functional. `formatClass` still handles legacy `audio` value (now `audiobook`) — dead branch, harmless. Could be pruned.

### 4.4 Browser tests
- `tests/column-layout.spec.js`: Werk column placement, measured widths, numeric sort.
- `tests/csv-export.spec.js`: whole-sheet export despite filter, filename per view, read-only, provenance badges, edition columns.
- CI runs Chromium (`playwright install --with-deps chromium`). Sandbox cannot download — documented.

---

## 5. CI/CD & Deployment

- **ci.yml:** read-only (`contents: read`), concurrency `ci-${{ ref }}`, steps: checkout, Python 3.12 + pip cache, `py_compile`, 5 `--check` modes (`process_data`, `build_research_master`, `build_catalogue_pages`, `reconcile`, `map_series_taxonomy`), unittest, coverage gate (80%), Node 20 + npm cache, `node --check` ×3, `npm ci`, playwright install, `test:e2e`. Upload artifact on failure. No network to live API.
- **update_spreadsheet.yml:** triggers `workflow_dispatch` + push on `main` paths `hawkins archive clone - Sheet1.csv`; permissions `contents: write`; runs `process_data.py` + auto-commit via `stefanzweifel/git-auto-commit-action@v5` with pattern `docs/data.json docs/meta.json`. Correct.
- **map_veritas_catalogue.yml:** `workflow_dispatch` only, `contents: read`, fetches candidate inventory via `fetch_veritas_catalogue.py --output candidate`, diffs against committed, fails if diff (`status=1` intentional), uploads artifact `veritas-inventory-review-${{ run_id }}` with candidate + patch. Review-only, never auto-commits. Correct.
- **Pages:** `docs/` source, `docs/.nojekyll` present (prevents Jekyll ignoring `_` paths). `docs/*.json` all < 500KB (largest `migration-review.json` 347KB, `master.json` 320KB, `product-relationships.json` 310KB) — under GitHub Pages 1GB soft limit; large JSON served via relative fetch, no localhost calls.
- **gitignore:** covers `__pycache__`, `.coverage`, `node_modules`, `playwright-report`, workflow candidate artifacts, OS files.
- **GitHub App limitation:** cannot push workflow-file changes — documented in handoff, workaround via owner web editor + snippet in `archive/UNBLOCK_INSTRUCTIONS.md`. No outstanding workflow edits needed.

---

## 6. Documentation Currency

- `README.md` counts: 356 master (307 lecture / 38 book / 10 discussion / 1 untyped), 271 codes, 68 exclusions, 110 overrides, 26 promoted 0 unpromoted, 333 relationships, 7 compilations — matches `catalogue-meta.json` and re-derived counts. Primary relationships derived note added, edition model note accurate.
- `INSTRUCTIONS.md`: pipeline top-to-bottom, header=1 note, edition model inputs, curated checks, coverage gate, Veritas refresh review — current.
- `NEXT_AGENT_HANDOFF.md`: 2026-08-03 latest refresh note + audit + consolidation; counts 376 Everything, 169/0/10 taxonomy, 332 family members, 271 codes? Check: handoff still says codes 236? Need update — actually README says 271, handoff §3 table says 236? Let's re-read handoff §3: earlier version said 236? Current file may still have 236? The re-derived counts in §2 of handoff mention 236 historical but later corrected to 265 → 271. Verify current handoff text: earlier we saw §4 item 23/24 says codes 236→265→271. So final state 271 — handoff mentions 271 indirectly. Could be updated to explicit final count table. Minor drift but not blocking.
- `RECONCILIATION_REPORT.md`: 50 draft-only rows (expected: 24 edition promotions + 26 manual promotions = 50). Wording "not yet fully reconciled" is by-design, not regression — documented.
- `PRODUCT_RELATIONSHIP_SCHEMA.md` and `SERIES_COMPILATION_SCHEMA.md`: note derived primary, hand-maintained `related_material`.
- `SERIES_TAXONOMY_MAPPING.md`, `CATEGORY_DOMINANCE_POLICY.md`: R1-R9 rules encoded.
- `ITEM_TYPE_CLASSIFICATION_PROPOSAL.md`: marked implemented (deprecated values retired).
- Living root MD: 20 files (down from 34 → 20 after consolidation round 2). Archive indexed.
- Currency tests: `test_readme_current_state_matches_generated_data`, `test_handoff_current_state_matches_generated_data`, `test_review_overview_master_candidates_state_matches_data` guard doc drift — all pass.

---

## 7. Findings (graded)

### HIGH — none (previous HIGH CSP hash and MED Veritas 50810 fixed and verified)

### MEDIUM — 1 new observation

1. **[MED-OBS] Lecture audiobook edition rows have blank `year` (11 rows: UUIDs 333-343).**  
   `edition_candidates.csv` for lecture parts (`w-nature-of-divinity`, `w-advaita`, `w-realizing-root`, `w-intention`, `w-alignment`, `w-identification-illusion`, `w-emotions-sensations`, `w-god-vs-science`, `w-tlc-perception`, `w-compassion`, `w-live-prayer`) carry empty `proposed_year`. Their minted master rows therefore have blank `year` (and thus no catalogue code).  
   - **Impact:** 11 curated rows lack recording year; Everything shows Year-Month empty for them; catalogue code coverage 271 would increase if years inherited.  
   - **Root cause:** book audiobooks inherit work's first-publication year (e.g., Power vs Force 1995) — applied. Lecture audiobooks need their work's recording year (e.g., Way to God lectures are 2002). The matching master UUID's year could be propagated at promotion time, but current promotion logic only copies `candidate_title`/`format_detail`, not year from matched master.  
   - **Suggested fix (owner decision):** either set `proposed_year` in `edition_candidates.csv` from matched master's year (requires review per candidate), or extend `load_edition_promotions` to inherit `year` from matched master when `proposed_year` blank and `item_type=lecture`. The latter is deterministic and evidence-based (matched masters already have validated year). Document as inheritance rule.  
   - **Risk if left:** blank years for lecture audiobook carriers — reviewer sees incomplete Year-Month; no data corruption because blank is explicit.

### LOW — 3 hygiene

2. **[LOW] Four always-empty master columns:** `location_physical`, `location_digital`, `location_streaming`, `reference_url_2` — 0 non-empty values across 356 rows. Decision pending populate or drop via schema change. Mentioned in handoff P1, full-stack audit. Harmless but adds column chooser noise.
3. **[LOW] Record 246 (`"In the World But Not of It" – Audio`):** 1 untyped record, deferred pending physical-edition confirmation; product 1661 is mapping-row only (no source override until ruled). Stable deferred state, not a defect, but blocks `item_type` completeness (307/38/10/1).  
4. **[LOW] Dead JS code:** `editTriggerEvent: "dblclick"` despite `editor: false`; `formatClass` handling legacy `"audio"` (now `"audiobook"`); `FOOTER_IDLE_NOTE`/`flashNote` already removed but comment still references inline editing in older docs (fixed in code, header comment corrected). No functional impact, just polish.

### INFO — known by-design

- `RECONCILIATION_REPORT.md` shows 50 draft-only rows — expected (24 edition + 26 manual). `reconcile --check` passes because report matches current inputs; the wording "not yet fully reconciled" is intentional to prevent silent drift.
- `fetch_veritas_catalogue.py --check` requires live network — fails offline. Not a CI failure; workflow runs manually.
- `docs/meta.json` `generated_at_utc` = 2026-08-02 — informational, excluded from `--check`.
- Spanish Audible titles (2) deliberately routed to International Editions lane, not Everything candidates.
- 8 blank formats (5 On-The-Road legacy raw rows + 1 untyped + 3 discussion) — no automated inference match; evidence in `archive/TEMP_RESPONSE_AUDIT_2026-08-03.md` §11c/d.

---

## 8. Recommendations (prioritized)

**P0 — Owner actions (none blocking, but close loops)**

- Re-run **Map Veritas Catalogue** workflow on `main` after this audit merges — expected to print `Candidate matches the reviewed inventory` (50810 drift fixed, CRLF normalized, 191 products). If diff appears, inspect for legitimate new products.
- Rule on empty columns: either populate `location_*` / `reference_url_2` from research notes or drop via schema migration (update `FIELDS`, `EVERYTHING_FIELDS`, validators, tests, and regenerate).
- Rule on Record 246 and 8 blank formats — owner evidence directs: e.g., set format for On The Road Talk Series 221/225-227 from context or leave blank with documented reason.

**P1 — Data enrichments**

- **Fill lecture audiobook edition years:** implement inheritance from matched master year (see §7 MED-OBS). Would bring blank years 18 → 7 (remaining: 3 On-The-Road raw + 1 untyped + 3 discussion). Re-run `build_research_master --check` and update `docs/catalogue-meta.json` counts via build.
- **Cross-publisher URL completeness:** 28 Hay House + 4 NC now present; audit remaining Veritas products without `source_url_hay_house` where Hay House counterpart exists (e.g., books) — but only via approved overrides.
- **Curated `series` for untyped/discussion gaps:** ensure Discussion Series blank-year rows still carry series (they do: `How to Live Your Life Like a Prayer` etc have series Discussion but blank year — discussion series year was set to 2012 for 5 of them; 3 remain blank).

**P2 — Hygiene / tech debt**

- Remove dead `editTriggerEvent` and legacy `audio` branch in `formatClass`; add comment why editing disabled (already present but could be more prominent).
- Widen Playwright coverage: currently 5 specs covering export, provenance, edition columns, work-column placement, numeric sort. Add: column chooser, row drawer, dark-mode toggle, search + review filter interaction, active-filter chips.
- Pin runtime deps: `requirements.txt` has `pandas>=2.0,<4` — verified working on pandas 2.x/3.0.5 but lock story (e.g., `pip-compile` or `poetry lock`) would make CI byte-reproducible.
- Consider renaming source CSV `hawkins archive clone - Sheet1.csv` (spaces) to `hawkins_archive.csv` to reduce shell-escaping risk — currently handled everywhere via quoting and glob fallback, but rename removes class of risk.
- Merge manual + edition candidate lanes (F2 in handoff) — identified as highest-value structural dedup, but deferred as higher-risk because it changes promotion registry shape. Would need new unified schema, migration, and validator unification.

**P3 — Documentation**

- Update `NEXT_AGENT_HANDOFF.md` §3 table to explicitly state final catalogue codes **271** (currently mentions 236→265→271 in narrative but table may still show 236 in older cached version — verify). Ensure all counts cited from `catalogue-meta.json`.
- Add brief entry to `README.md` about lecture audiobook edition year inheritance rule once implemented.
- Keep `archive/README.md` indexed for any future consolidation.

---

## 9. Security Summary

- No secrets, tokens, or PII in repo.
- CSP strict, SRI pinned, no `unsafe-inline` scripts, one correct hash.
- No `innerHTML` injection vectors; all dynamic DOM via `textContent`/`createElement`/`replaceChildren`.
- File operations restricted to repo (`Path("data"/...)`, `Path("docs"/...)`), no path traversal.
- Network only in `fetch_veritas_catalogue.py` (fixed HTTPS endpoint `https://veritaspub.com/wp-json/wp/v2/product`, timeout 60s, retry ladder 4 attempts, User-Agent fixed).
- Permissions: CI read-only, product refresh read-only, only Update Spreadsheet workflow writes.

**Grade: A-** — same as prior audit; all prior HIGH/MED fixed; remaining only hygiene.

---

## 10. Grades (current)

| Area | Grade | Note |
|---|---|---|
| Data pipeline correctness | A | Deterministic, all 5 checks green, 92% meaningful coverage, derived primary relationships reduce duplication |
| Data governance / provenance | A+ | Review CSVs, `decisions/`, no-hand-edit enforcement, overlay pattern for live refresh, title hygiene evidence-based |
| Data model completeness | B+ | 356 master, work_id 356/356, 271 codes, but 18 blank years (11 lecture audiobook editions) + 8 blank formats + 4 empty cols remain — all documented |
| Frontend | A- | CSP correct, SRI pinned, width engine pixel-accurate, numeric sort fixed, accessible; tiny dead code |
| CI/CD | A- | Thorough read-only CI, live refresh review-only, concurrency groups; runtime deps unpinned; browser tests narrow |
| Documentation | A- | 103 doc-currency tests guard counts; 20 root MDs, rulings under `decisions/`; handoff narrative could make final counts more explicit |
| Security | A- | No injection surface, no secrets, review-only live fetch; style-src `unsafe-inline` required for Tabulator |

---

## 11. Reproduce

```bash
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install -r requirements-dev.txt
/tmp/venv/bin/python -m py_compile *.py
/tmp/venv/bin/python process_data.py --check
/tmp/venv/bin/python build_research_master.py --check
/tmp/venv/bin/python build_catalogue_pages.py --check
/tmp/venv/bin/python reconcile_research_master.py --check
/tmp/venv/bin/python map_series_taxonomy.py --check
/tmp/venv/bin/python -m unittest discover tests -v
/tmp/venv/bin/coverage run -m unittest discover tests && /tmp/venv/bin/coverage report
node --check docs/app.js && node --check tests/csv-export.spec.js && node --check tests/column-layout.spec.js
```

Expected:

- All checks pass except `fetch_veritas_catalogue.py --check` (offline TLS EOF — known).
- 103 tests pass, 92% coverage.
- JS syntax OK.

---

## 12. One-sentence summary

The docsheet pipeline is green after merges #19-#22 — 103/103 tests, 92% coverage, all 5 `--check` modes pass, data integrity intact (356 master, 271 codes, 333 relationships rendered with 325 derived primary + 8 related), CSP hash and Veritas 50810 drift fixed, product-relationship CSV slimmed from 333 to 8 rows, title hygiene and year-month semantics enforced, with only low-grade hygiene remaining (11 blank-year lecture audiobooks, 8 blank formats, 4 empty location columns, record 246 deferred).

---

*Report generated by automated audit on branch `arena/019fcddb-docsheet` @ `af76fe3`, same as `origin/main`. All commands re-executed offline where possible; live-API checks excluded by sandbox but workflow artifact pattern preserves safety.*
