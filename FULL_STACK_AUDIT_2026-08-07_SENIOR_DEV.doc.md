# Project Audit — DocSheet (56eli/docsheet)

**Audit Date:** 2026-08-07  
**Auditor:** Senior Developer + Data Analyst  
**Branch:** `arena/019fdd48-docsheet` (current)  
**Base Commit:** `918e665` (PR #27 merge into main)

---

## 1. Project Overview

**DocSheet** is a live spreadsheet renderer that displays Hawkins Archive data (David Hawkins MD's spiritual corpus 1995-2026) as an interactive, searchable web table on GitHub Pages using Tabulator.

### Project Type
- **Primary:** Interactive web table rendering (GitHub Pages + Tabulator 6.5.2)
- **Secondary:** Curated research catalogue pipeline with review governance
- **Tertiary:** Automated inventory fetching from Veritas Publishing API

### Core Components

| Component | Description |
|-----------|-------------|
| **Frontend** | `docs/index.html`, `docs/app.js` (929 lines), `docs/style.css` — Tabulator-based spreadsheet with 15 views, dark mode, CSV export, column chooser |
| **Raw pipeline** | `process_data.py` — Pass-through CSV→JSON for the "Original Spreadsheet" view |
| **Curated pipeline** | `build_research_master.py`, `build_catalogue_pages.py`, `map_series_taxonomy.py`, `reconcile_research_master.py`, `fetch_veritas_catalogue.py` — Generates the curated master catalogue and review sheets |
| **Test suite** | `tests/test_pipeline.py` (1,779 lines, 107 tests, 91% coverage) + Playwright e2e (`tests/column-layout.spec.js`, `tests/csv-export.spec.js`) |

---

## 2. Repository Structure

```
docsheet/
├── .github/workflows/
│   ├── ci.yml                    # Read-only validation: 5 checks + tests + coverage + JS + Playwright
│   ├── update_spreadsheet.yml    # Manual + CSV-push triggered: regenerates docs/data.json
│   └── map_veritas_catalogue.yml # Manual only: fetches Veritas inventory candidate for review
├── data/                         # Input CSVs (22 files, ~1.2MB total)
│   ├── research_master_draft.{csv,json}  # 366 curated master records
│   ├── migration_review_ledger.csv       # 374-row provenance ledger
│   ├── research_master_source_overrides.csv  # 133 approved overrides
│   ├── work_families.csv         # 209 works, 342 members
│   ├── edition_candidates/promotions.csv  # 24 editions
│   ├── veritas_official_products.csv  # 191 products (live-verified)
│   ├── veritas_streaming_urls.csv  # 36 streaming URL mappings
│   ├── filename_proposal_YYYYMM.csv  # 366 unique filenames
│   ├── series_category_mapping.csv  # 186 taxonomy mappings
│   ├── product_relationships.csv    # 8 related_material rows
│   ├── series_compilation_relationships.csv  # 7 compilations
│   └── ... (candidates, queues, decisions)
├── docs/                         # Generated outputs (20 JSONs + index.html/app.js/style.css)
│   ├── master.json               # Everything view: 366 master + candidates
│   ├── catalogue-meta.json       # Counts and metadata
│   ├── data.json                 # Raw spreadsheet pass-through
│   └── ... (review sheets, relationships, etc.)
├── tests/
│   ├── test_pipeline.py          # 107 deterministic tests
│   ├── column-layout.spec.js     # Playwright: Work column placement, widths, sort
│   └── csv-export.spec.js        # Playwright: CSV export, read-only, record types
├── .coveragerc                   # Coverage floor: 80% (actual 91%)
├── requirements.txt              # pandas
├── requirements-dev.txt          # + coverage
├── package.json                  # Playwright 1.62.1 for e2e
└── *.md                          # 25 root documentation files + decisions/ + archive/
```

---

## 3. Current Verified State (Post-PR #26, 2026-08-07)

### Curated Master
| Metric | Count | Notes |
|--------|-------|-------|
| Master records | **366** | 310 lecture / 40 book / 8 discussion / 7 highlight / 1 other |
| Everything view | **366** | 366 master + 0 candidates (all ruled out) |
| Catalogue codes | **281** | Lecture/discussion only, books never coded |
| Exclusions | **72** | |
| Source overrides | **133** | 73 veritas, 27 hayhouse, 10 audible, 5 NC, 18 Amazon |
| Work families | **209 works / 342 members** | 100% coverage |
| Editions | **24** | Minted as UUIDs 320-343 etc, D3 applied |
| Product relationships | **343** | 335 derived primary + 8 related_material |
| Series compilations | **7** | Highlights annual |
| Series taxonomy | **186 matched → 176 approved / 0 proposed / 10 rejected** | Queue: 6 (informational conflicts) |
| Filename proposal | **366 unique** | Safe `[1-3]` / display `[1/3]` |
| Streaming refs | **59 masters** | Via 36 product IDs in veritas_streaming_urls.csv |
| Year blanks | **18** | 13 Volume Series (intentional) + 5 under investigation |
| Format blanks | **2** | Oxford 2003 (221) + untyped 246 |
| Untyped records | **0** | Record 246 ruled duplicate of master 329 and excluded 2026-08-07 |

### Veritas Inventory Verification (2026-08-03)
- **191 products** reconciled exactly via live API fetch (100+91 split)
- All 195 verifiable lecture months match publisher's own dates
- Mapping: 179 matched_by_primary_source, 6 matched_by_title, 5 excluded_related_material, 1 matched_by_normalized_title

---

## 4. Pipeline Architecture

### Data Flow

```
hawkins archive clone - Sheet1.csv (374 raw rows)
         │
         ├── process_data.py ──► docs/data.json + meta.json (raw pass-through)
         │
         └── migration_review_ledger.csv (374 dispositions)
                  │
                  ├── build_research_master.py ──► research_master_draft.{csv,json}
                  │       (applies: source overrides → streaming → filename → 
                  │        backfill months → format inference → title cleanup →
                  │        series approvals → work families → integrity)
                  │
                  ├── build_catalogue_pages.py ──► 20 docs/*.json + catalogue-meta.json
                  │       (derives primary relationships from master URLs,
                  │        builds Everything view with record_type, review sheets)
                  │
                  ├── map_series_taxonomy.py ──► series_category_mapping.csv + queue
                  │       (dominance rules R1-R9, vocabulary mapping)
                  │
                  ├── reconcile_research_master.py ──► RECONCILIATION_REPORT.md
                  │       (read-only drift comparison of ledger vs master)
                  │
                  └── fetch_veritas_catalogue.py ──► veritas_official_products.csv (candidate)
                          (review-only, never auto-commits, retry ladder MAX_PAGE_ATTEMPTS=4)
```

### Key Design Decisions

1. **One row per edition** (since 2026-08-03): Work × carrier model. Book, audiobook, and video are separate rows. DVD lecture parts each keep their own row, grouped under one work.

2. **work_id from approved families only**: Never title-inferred. Assigned only from reviewed `data/work_families.csv` rows with `review_status=approved`.

3. **Derived primary relationships**: Every master with `source_url_veritas` gets exactly one derived `primary_product_for_item_part` relationship. Only distinct non-primary relationships (`related_material`) are hand-maintained in `data/product_relationships.csv`.

4. **Filename proposal v4**: Pattern `YYYY-MM - Name [1/3].mp4`, safe `[1-3]` on-disk, display `[1/3]`, no bracket for single part, audiobook label removed from name (`.m4b` indicates), Volume Series stripped of years (pre-2000 unknown), Satsang month stripped.

5. **Year source tracking**: `year_source` field added 2026-08-07 showing provenance: Ledger recording/first-pub, Veritas listing backfill, Manual candidate, Edition inherited, Blank intentional, etc.

6. **Retired vocabulary**: `audio` and `video` retired from controlled vocabulary 2026-08-03. Use content class (`item_type`) + carrier in `format`. Validators now reject them.

7. **Book years = first-publication year**: Never the storefront listing date. Veritas listed a batch of books with `published_date` 2014-03-30 (site appearance date), but Power vs Force was first published 1995, The Eye of the I in 2001, etc. Backfill skips `item_type='book'` entirely.

---

## 5. Test Suite Analysis

### Test Types (107 tests, 91% coverage)

| Category | Tests | Coverage |
|----------|-------|----------|
| **Pipeline Integration** | write→check→tamper for all 5 generators, CSV determinism, CLI smoke, reduced pending view | Full pipeline |
| **Taxonomy Dominance** | Rule matrix R1-R9, vocabulary coverage | `map_series_taxonomy.py` |
| **Veritas Matching** | norm(), title_date_key(), satsang detection, category_names, split_uuids, build_inventory (primary/satsang/normalized/unreviewed), mapping decisions validation | `fetch_veritas_catalogue.py` |
| **Inventory Validation** | Count consistency, unknown UUID, title mismatch, everything_record defaults, record_type coverage | `build_catalogue_pages.py` |
| **Format Inference** | Slug signals, never overwrite, exact URL lookup, category guard, Highlights→streaming, compact ID | `build_research_master.py` |
| **Process Data Failure Paths** | Missing outputs, stale data.json, invalid meta, missing CSV, fallback pickup | `process_data.py` |
| **Veritas Fetcher Offline** | Synthetic live API replay, write→check, tamper, custom output rejection, API failure preserves inventory | `fetch_veritas_catalogue.py` |
| **GetPage Retry** | Pagination until 400, HTML retries, non-list retries, 400 first page, URLError retries, taxonomy compact fields | `fetch_veritas_catalogue.py` |
| **Reconcile Drift** | Markdown/code cell hygiene, compare_drafts (extras/missing/changed), report sections, stale check | `reconcile_research_master.py` |
| **Derived Primary Relationships** | Builds from master URLs, note provenance, committed 335+8=343, CSV holds only non-primary, deleting related_material fails check | `build_catalogue_pages.py` |
| **Work Families** | Committed clean, approved assigns, proposed not applied, unknown member, missing columns, needs date/evidence/canonical, duplicate member, tamper drift | `build_research_master.py` |
| **Edition Candidates** | Committed clean, promotion mints, requires status flip, unknown work/master/product, duplicate key, hayhouse valid + mismatch, shape validation, promotion edges, tamper when row vanishes | `build_research_master.py` |
| **Source Overrides** | Proposed not applied, approved applies, candidate-keyed applies, invalid status fails | `build_research_master.py` |
| **New Work Queue** | Committed clean, unknown product, URL mismatch, duplicate, empty title | `build_catalogue_pages.py` |
| **Documentation Currency** | README current state, handoff table, migration ledger summary, review overview state derived, backfill month guard, title cleanup only matching, books use first-publication year, Volume Series filenames, official title cleanup | Multiple docs |
| **Defensive Depth** | Edition UUID stability, source override idempotency, missing column clear error, untyped allowlist 246, malformed work_id, missing work_id in catalogue build, filename proposal group coherence, part_index range | Multiple |
| **Retired Vocabulary** | Vocabulary excludes audio/video, committed inputs clean, manual candidate audio fails, ledger video fails | `build_research_master.py` |

### Playwright E2E (CI only — Chromium not installable in sandbox)
- **column-layout.spec.js**: Work column parked between Legacy ID and Location Physical, measured widths, numeric sort asc 1/2/3 desc 372/371
- **csv-export.spec.js**: CSV export whole view even when filtered, view-specific filename, read-only cells, record type separation, edition model columns

---

## 6. CI/CD Analysis

### ci.yml (Read-only validation)
```
Triggers: pull_request, push to main, workflow_dispatch
Permissions: contents: read
Concurency: ci-${{ github.ref }} (cancel in-progress)

Steps:
  1. Checkout
  2. Python 3.12 + pip cache
  3. pip install -r requirements.txt
  4. py_compile *.py
  5. process_data.py --check
  6. build_research_master.py --check
  7. build_catalogue_pages.py --check
  8. reconcile_research_master.py --check
  9. map_series_taxonomy.py --check
  10. python -m unittest discover tests
  11. pip install -r requirements-dev.txt + coverage run + coverage report (80% floor)
  12. Node 20 + npm cache
  13. node --check app.js + playwright.config.js + csv-export.spec.js
  14. npm ci
  15. npx playwright install --with-deps chromium
  16. npm run test:e2e
  17. Upload playwright-report artifact on failure (7-day retention)
```

**Assessment:** Comprehensive, well-structured. All checks are read-only (no writes to repo). Concurrency group prevents stale runs. The GITHUB_TOKEN auto-commit trap is documented in the update_spreadsheet workflow (commits don't trigger Pages deploy).

### update_spreadsheet.yml (Raw spreadsheet pipeline)
```
Triggers: workflow_dispatch (manual), push to main when CSV changes
Permissions: contents: write

Steps:
  1. Checkout
  2. Python 3.12 + pip cache
  3. pip install -r requirements.txt
  4. python process_data.py
  5. git-auto-commit-action: commits docs/data.json + docs/meta.json
     commit_user: github-actions[bot]
```

**Assessment:** Simple, appropriate. The GITHUB_TOKEN commit trap is known/documented — commits don't trigger Pages deployment, so manual re-run or PAT needed. No schedule defined yet.

### map_veritas_catalogue.yml (Review-only inventory refresh)
```
Trigger: workflow_dispatch ONLY (manual)

Steps:
  1. Checkout selected branch
  2. Python 3.12
  3. python fetch_veritas_catalogue.py --output data/veritas_official_products_candidate.csv
  4. git diff --no-index verified_inventory candidate > veritas_inventory_diff.patch
     - Exit 0: candidate matches (no diff)
     - Exit 1: diff exists (review required)
     - Exit >1: error
  5. Upload artifact: candidate CSV + diff patch (always, even on failure)
```

**Assessment:** Excellent governance. Review-only pattern prevents auto-commit of unvetted live data. Artifact provides candidate + diff for manual review. Concurrency set to false (don't cancel — each refresh is independent).

---

## 7. Frontend Analysis

### Architecture
- **Framework:** Vanilla JS + Tabulator 6.5.2 (CDN, pinned with SRI)
- **Styles:** Custom CSS + Google Fonts (Roboto)
- **Data loading:** fetch() with `cache: "no-store"`, Last-Modified header displayed

### Features (All Implemented)
| Feature | Status |
|---------|--------|
| 15 views (Everything + 9 review sheets + Product Relationships + Series Compilations + International + Publishers + Original) | ✅ |
| Global live search (250ms debounce, all columns) | ✅ |
| Review filter (auto-detects field with >1 distinct value, multi-value select) | ✅ |
| Active filter chips + Clear all | ✅ |
| Column chooser (visibility checkboxes, Show all, fitTable) | ✅ |
| CSV export (whole view, rowRange all — filters don't reduce export) | ✅ |
| Dark mode (localStorage persisted, OS preference first time, no flash) | ✅ |
| Row details drawer (all fields, URL links, status badges) | ✅ |
| Column width engine (offscreen canvas, measured pixels, 560/720 caps, min 60) | ✅ |
| Numeric sort with alignEmptyValues bottom (fixes 1,10,100 lexical bug) | ✅ |
| Merged Year-Month and Edition columns | ✅ |
| Frozen header + internal scroll (maxHeight 100%) | ✅ |
| Resizable + movable columns | ✅ |
| Work column parked between Legacy ID and Location Physical | ✅ |
| proposed_filename column between Title and Item Type | ✅ |
| Read-only (editor: false) | ✅ |
| Accessibility: aria-live, aria-busy, role tablist/tab, aria-selected, keyboard Esc | ✅ |
| CSP: default-src self, object-src none, form-action self, script-src self + cdn.jsdelivr.net + SRI hash, style-src self + unsafe-inline + cdn + fonts.googleapis.com, font-src fonts.gstatic.com, connect-src self, img-src self + data: | ✅ |
| SRI pinned for Tabulator CSS + JS | ✅ |
| `.nojekyll` present (bypasses Jekyll timeout on large JSONs) | ✅ |

### Security Assessment
- **No secrets** in repo, no env vars needed
- **No eval**, no innerHTML (footer uses textContent, drawer uses textContent + anchor)
- **CSP** correctly restricts sources
- **SRI** verified for Tabulator
- **LF line endings** (CRLF issue fixed)
- **No innerHTML injection** — all user-visible text uses textContent or safe anchor creation

---

## 8. Documentation Health

### Root Documentation (25 Markdown files)
- README.md — Project overview, quick start, catalogue-data safeguard, current state
- INSTRUCTIONS.md — Detailed setup guide, pipeline test suite, Veritas refresh review
- NEXT_AGENT_HANDOFF.md — Current state table, open work, recommendations
- FULL_STACK_AUDIT_2026-08-07_DEEP.md — Most recent comprehensive audit
- FULL_STACK_AUDIT_2026-08-04_FINAL_358_V2.md — Previous audit (358 master)
- CATALOGUE_READABILITY_ROADMAP.md, CATEGORY_DOMINANCE_POLICY.md, EDITION_MODEL_PROPOSAL.md, FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md, GITHUB_PAGES_DEPLOYMENT_ANALYSIS.md, ITEM_TYPE_CLASSIFICATION_PROPOSAL.md, LECTURE_SERIES_REVIEW.md, LECTURE_YEAR_INVESTIGATION.md, MIGRATION_REVIEW_LEDGER.md, OFFICIAL_CATALOGUE_DISCOVERY.md, OFFICIAL_SOURCE_REGISTRY.md, PRODUCT_RELATIONSHIP_SCHEMA.md, RECONCILIATION_REPORT.md, REVIEW_MODEL_SLIM_ANALYSIS.md, SERIES_COMPILATION_SCHEMA.md, SERIES_TAXONOMY_MAPPING.md, SERIES_WORK_REGROUPING_PROPOSAL.md, TITLE_HYGIENE_PROPOSAL.md, VERITAS_ARTIFACT_REVIEW.md, VERITAS_PRODUCT_MAPPING.md, YEAR_COLUMN_PROVENANCE.md

### Decisions (13 files in decisions/)
AUDIBLE_MAPPING.md, BOOK_RELATIONSHIP_DECISIONS.md, COMPILATION_CANDIDATE_DECISIONS.md, FINAL_TITLE_MATCH_DECISIONS.md, HAY_HOUSE_MAPPING.md, HIGHLIGHTS_COMPILATION_DECISIONS.md, NIGHTINGALE_CONANT_MAPPING.md, README.md, RECONCILIATION_DECISIONS.md, SATSANG_MAPPING_DECISIONS.md, SERIES_REGROUPING_DECISIONS.md, UNIQUE_ITEM_CANDIDATE_DECISIONS.md, VERITAS_MAPPING_DECISIONS.md

### Archive (46 files)
Superseded audits, backfill reports, dedup scripts — indexed in archive/README.md, not normative

### Documentation Currency Tests
5 guards verify docs match generated data:
1. README current state numbers
2. NEXT_AGENT_HANDOFF table
3. MIGRATION_REVIEW_LEDGER classification summary
4. Review Overview Master Candidates state (derived, not hardcoded)
5. Volume Series filenames match titles
6. Backfill month guard (listing month not leak)
7. Official title cleanup only matches
8. Books use first-publication year not listing

**Assessment:** Comprehensive but some known drift:
- FILENAME_PROPOSAL_V4.md still mentions "1995-1999 estimated" for Volume Series, but master now uses blank (pre-2000 unknown). Should update.
- RECONCILIATION_REPORT.md shows 53 extras as "not yet fully reconciled" — these are expected from edition/promotion layer, not a failure. Could use clarifying note.

---

## 9. Known Issues & Open Work

### P0 — Owner Actions (Already Documented)
1. Re-run Map Veritas Catalogue workflow after merge — should pass clean (191 exact match, LF normalized, title drift fixed)
2. Verify GitHub Pages live site serves master 366 after merge

### P1 — Data Decisions Needing Ruling
1. **Year blank 18**: 13 Volume Series intentionally blank (pre-2000 unknown) + 5 under investigation (Verification of Spiritual Realities 230-232, record 246 now excluded, God is Hidden 268). Remaining need © year research.
2. **Format blank 2**: Oxford 2003 (221) + untyped 246 (now excluded). Should infer from series: On The Road → DVD, Discussion → streaming.
3. **Record 246 untyped**: Now ruled duplicate of master 329 and excluded (2026-08-07). ✅
4. **Streaming blind spot**: 36 product IDs → 59 masters have streaming URL. Methodology proven, ~115 more Veritas lecture products need fetch (5 per turn per handoff).
5. **Official discovery queue 4 NC**: Ultimate Library, Discovery, Healing, Naked — need content/edition review. Healing is possible_related_match to Healing and Recovery but distinct program.
6. **HayHouse 4 + Audible 6+3 unreviewed**: Need mapping decisions (unique_item / compilation_or_new_edition / excluded_related_material).
7. **Series taxonomy queue 6**: Informational conflicts (IDs 202, 121, 50521). All approved/rejected but queue still shows because fan-out conflict persists. Either clear queue_reason after ruling or accept as transparent audit trail.

### P2 — Hygiene / Tech Debt
1. **FILENAME_PROPOSAL_V4.md doc drift**: Says Volume Series 1995-1999 estimated, but master now blank pre-2000. Should update.
2. **RECONCILIATION_REPORT.md wording**: Shows 53 extras as "not yet fully reconciled" even though expected from edition layer. Could clarify.
3. **ITEM_TYPE vs FORMAT**: `format` vocabulary includes `book` as carrier (odd — carrier is paperback/hardcover). Could consider `format_detail` for carrier subtype later.
4. **Frontend bundle**: Tabulator via CDN — offline dev needs network. Could vendor locally.
5. **CI**: GITHUB_TOKEN Pages trigger ban still requires manual re-run or PAT for update_spreadsheet workflow.

---

## 10. Grades (Subjective, from FULL_STACK_AUDIT_2026-08-07_DEEP.md)

| Area | Grade | Rationale |
|------|-------|-----------|
| Data pipeline determinism | A+ | 5 checks green, run-twice deterministic, tamper detection, idempotency |
| Data governance | A+ | Reviewed inputs, approval registry, no title-based inference, derived primary |
| Completeness | A+ | 366 master, 191 Veritas inventory ruled (0 unreviewed), 0 format blank, 18 year blank (documented), 0 untyped |
| Edition model | A+ | 209 works, 342 members, 24 editions, D3 applied, work_id coverage 100% |
| Frontend | A | Measured-width engine, numeric sort fixed, Work parked, filename column, CSP+SRI, dark mode, .nojekyll |
| Tests | A+ | 107 deterministic, offline replay, rule matrices, doc-currency guards, 91% coverage |
| CI/CD | A- | 5 checks + unittest + coverage + JS + Playwright, concurrency, but GITHUB_TOKEN Pages trigger ban |
| Docs | B+ | Comprehensive, but FILENAME_PROPOSAL_V4 still mentions 1995-1999 vs blank reality, reconciliation report 53 extras misleading |
| Security | A- | CSP+SRI, no innerHTML, LF, but style-src unsafe-inline needed for Tabulator (could tighten) |

---

## 11. Recent Changes (Since Last Audit)

### PR #24 (Amazon/year-source changes)
- Added `source_url_amazon` as Amazon search link
- Added `year_source` field next to Year-Month showing provenance
- Regenerated `docs/review-overview.json` and `docs/source-overrides.json`
- 127 approved source overrides, 18 Amazon direct-link overrides

### PR #25 (Legacy duplicate exclusion)
- Excluded rows 281/284 (duplicate 2012 Discussion Series talks as promoted masters 312/313)
- Master: 356, Everything: 376, exclusions: 71, codes: 278

### PR #26 (Highlights promotion + final cleanup)
- Promoted 7 annual Highlights products to curated master (362-368, series "Lecture Highlights")
- Master: 363, Everything: 376 (candidate_veritas 8 → 1)
- Relationships: 343 (335 derived + 8)
- Taxonomy: 186 (176 approved)
- Works: 206/339
- Tests: 107, coverage: 91%

### Day-end 2026-08-07 (Discovery/Audible/HayHouse ruling)
- Deduplicated discovery/Audible lanes
- Promoted 3 unique programs: 369 The Discovery ©2007, 370 The Ultimate David Hawkins Library ©2016 (Nightingale-Conant), 371 OM ©2017 (Media Miscellaneous)
- Master: 366, Everything: 371 (discovery 0, audible 0)
- Overrides: 132, promoted candidates: 39, works: 209/342, codes: 280

### Final HayHouse ruling
- Live Life As A Prayer = 343
- Letting Go Journal/Deck excluded as merchandise
- How to Surrender to God promoted as master 372 (Hay House series, ©2019, audiobook)
- Master: 366 (310 lecture / 40 book / 8 discussion / 7 highlight / 1 other)
- Everything: 366 (all candidates ruled out)
- Map poster 1560 ruled excluded_related_material
- Overrides: 133, codes: 281, exclusions: 72, candidates: 40
- All 16 Office Series lectures standardized to year 198X (LECTURE-198X-001 through 016)
- UUID 331 series corrected to "Books", disambiguated from UUID 320 ([1-2]/[2-2] removed)
- Completed human-readable row-by-row filename audit (3 Satsang month mismatches and trailing dots resolved)

---

## 12. Recommendations (Prioritized)

1. **Sync FILENAME_PROPOSAL_V4.md** to current blank Volume Series reality
2. **Research year/format blanks**: Batch 5 product IDs per turn, fetch veritaspub product pages for © years
3. **Continue streaming blind spot**: Batch fetch streaming URLs for remaining ~115 Veritas lecture products
4. **Rule on official discovery queue**: Decide on 4 NC programs (promote / exclude / related_material)
5. **Rule on HayHouse/Audible remaining**: 4 HayHouse + 6 Audible + 3 possible unreviewed
6. **Clarify taxonomy queue**: Either empty when all ruled or document as informational conflict trail
7. **Update RECONCILIATION_REPORT.md wording**: Note 53 extras are expected from edition/promotion layer
8. **Consider vendoring Tabulator locally** for offline dev
9. **Consider PAT for update_spreadsheet workflow** to trigger Pages deploy, or document manual re-run requirement

---

## 13. Summary

**Verdict: HEALTHY & VERIFIED** — The DocSheet project is a well-architected, thoroughly tested data pipeline and interactive spreadsheet renderer for the Hawkins Archive. The curated catalogue pipeline is deterministic and green (107/107 tests, 91% coverage, all 5 --check modes pass). The frontend is polished (Tabulator 6.5.2 with measured-width engine, dark mode, CSP+SRI, accessibility). Governance is strong (reviewed inputs, approval registry, no title-based inference, derived primary relationships). Open items are intentional review boundaries (year/format blanks, unreviewed inventory candidates, streaming blind spot), not pipeline defects. Documentation is comprehensive but has minor drift in FILENAME_PROPOSAL_V4.md and RECONCILIATION_REPORT.md wording that should be corrected.

**One-sentence summary:** The DocSheet project is a production-ready, deterministically-tested data pipeline and interactive spreadsheet renderer for the Hawkins Archive with 366 curated master records, 107 passing tests at 91% coverage, strong governance controls, and a polished Tabulator-based frontend — with known, documented review-boundary gaps rather than defects.

---

*Audit completed 2026-08-07. Repository: 56eli/docsheet, branch arena/019fdd48-docsheet.*
