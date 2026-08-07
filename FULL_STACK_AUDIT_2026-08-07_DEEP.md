# Full-Stack Deep Audit — 2026-08-07

> **Post-PR #24 audit note (2026-08-07, branch `arena/019fdcc5-docsheet`):** The original deep audit below was written before the final PR #24 Amazon/year-source changes landed. A follow-up audit found one generated-output drift and fixed it by regenerating `docs/review-overview.json` and `docs/source-overrides.json` so the Pages review sheets now reflect **127 approved source overrides** and the 18 Amazon direct-link overrides. Current checks pass after that regeneration: 5 Python `--check` modes, 104/104 unit tests, 91% coverage, and JavaScript syntax checks. Local Playwright e2e remained inconclusive because Chromium download failed in the sandbox with TLS `ECONNRESET`; CI should still exercise it. See `archive/TEMP_RESPONSE_AUDIT_2026-08-07_POST_PR24.md` for the current post-merge audit.
>
> **2026-08-07 session sync:** current-state counts below were refreshed post-PR #24/#25 — catalogue codes **280** (was 271), source overrides **127** (was 109), rendered relationships **336** (328 derived + 8 related), streaming refs **59 masters** (was 56), year blanks **18** (was 31), format blanks **2** (was 8), tests **106** (91% coverage). Later same day: legacy duplicate rows 281/284 excluded (same 2012 Discussion Series talks as promoted masters 312/313, owner ruling) → master **356**, Everything **376**, exclusions **71**, codes **278**. Final state 2026-08-07: the 7 annual Highlights products promoted to curated master (362–368, series **Lecture Highlights**, year from title, filename = title) → master **363**, Everything **376** (candidate_veritas 8 → 1), relationships **343** (335 derived + 8), taxonomy **186** (176 approved), works **206/339**, tests **107**. Day-end: discovery/Audible lanes deduplicated and the 3 unique programs promoted (**369 The Discovery ©2007, 370 The Ultimate David Hawkins Library ©2016 — series Nightingale-Conant; 371 OM ©2017, Media Miscellaneous**) → master **366** (309 lecture / 40 book / 8 discussion / 7 highlight / 1 other / 1 untyped), Everything **371** (discovery 0, audible 0; healing matched to 328, Naked excluded multi-contributor), overrides **132**, promoted candidates **39**, works **209/342**, codes **280** (the two lecture-typed NC programs carry codes). Day-end: **record 246 ruled a duplicate of master 329 and excluded** (no untyped records remain); HayHouse lane ruled (Live Life As A Prayer = 343, Letting Go Journal/Deck excluded as merchandise, **How to Surrender to God promoted as master 372** — Hay House series, ©2019, audiobook) → master **366** (310 lecture / 40 book / 8 discussion / 7 highlight / 1 other), Everything **367** (only the Map poster veritas candidate remains), overrides **133**, codes **281**, exclusions **72**, candidates **40**.


**Branch:** `arena/019fdb8b-docsheet` (HEAD `0b54614`, same as `main` at PR #23 merge)
**Date:** 2026-08-07
**Auditor:** senior dev + data analyst pass, offline + live checks
**Scope:** entire repo — 9 Python modules, 22 data/*.csv, 20 docs/*.json, frontend (index.html/app.js/style.css), 3 workflows, tests (103), docs (20 root Markdown + 13 decisions + archive)

## Executive Summary

**Verdict: HEALTHY & VERIFIED, with known, documented gaps that are intentional review boundaries, not drift.**

- Pipeline deterministic, 5 `--check` modes green (pandas missing in base image is expected sandbox trap, venv run proves green)
- Tests: **106/106 pass**, coverage **91% total, every module ≥89%** (gate 80%)
- Current curated master: **358 records** = 307 lecture / 40 book / 10 discussion / 1 untyped (246 deferred)
- Everything view: **378 rows** = 358 master + 8 candidate_veritas + 4 discovery + 4 hayhouse + 4 audible + 0 pending
- Catalogue codes: **280** distinct (lecture/discussion only, books never coded)
- Exclusions: **69**, source overrides: **127 approved** (72 veritas, 26 hayhouse, 7 audible, 4 NC, 18 Amazon)
- Veritas inventory: **191 products** (172 matched_by_primary_source, 7 compilation_or_new_edition, 6 matched_by_title, 4 excluded_related_material, 1 matched_by_normalized_title, 1 unreviewed)
- HayHouse: **24** (20 matched_by_title, 4 unreviewed), Audible: **26** (17 matched_by_title, 6 unreviewed, 3 possible_related_match)
- Product relationships: **336 rendered** = **328 derived primary** (auto-derived from master URL) + **8 related_material** (hand-maintained CSV)
- Series compilations: **7** reviewed
- Work families: **201 works / 334 members**, approved, coverage **358/358**
- Edition layer: **24 candidates / 24 promotions / 24 approved** (minted as master UUIDs 320-343 etc), D3 applied (audible URLs moved off book rows)
- Series taxonomy: **179 matched** → **169 approved / 0 proposed / 10 rejected**, queue **6** (conflict evidence guardrails, all ruled but lingering for visibility)
- Filename proposal: **358 unique**, safe `[1-3]` / display `[1/3]`, grouped by (year_month, clean_title, format), Volume Series canonicalized, Satsang month stripped, audiobook label removed
- Frontend: Tabulator 6.5.2 pinned + SRI, CSP `sha256-u2/...` correct, measured-width engine across all rows, badges, filters, dark mode, `.nojekyll` present
- CI: green on main, 5 checks + unittest + coverage + JS syntax + Playwright

**No blocking defect found.** Open items are P1/P2 review queues, not pipeline breakage.

## Repo Layout

```
hawkins archive clone - Sheet1.csv  (374 raw rows, source of truth, header=1)
migration_review_ledger.csv         (374 rows: 305 item / 69 provenance)
data/
  research_master_draft.{csv,json}  (358 curated master)
  research_master_exclusions.csv    (69)
  research_master_source_overrides.csv (127 approved)
  manual_master_candidates.csv      (29, all promoted)
  manual_candidate_promotions.csv   (29 approvals -> UUIDs 353-361 etc)
  edition_candidates/promotions     (24/24)
  work_families.csv                 (334 rows, 201 works)
  veritas_official_products.csv     (191)
  veritas_mapping_decisions.csv     (18 approved, overlay)
  veritas_streaming_urls.csv        (36 approved -> 59 masters ref1)
  filename_proposal_YYYYMM.csv      (358)
  series_category_mapping.csv       (179)
  series_taxonomy_review_queue.csv  (6)
  product_relationships.csv         (8 related_material only)
  series_compilation_relationships.csv (7)
  official_discovery_queue.csv      (4 NC)
  audible/hayhouse/international queues
docs/
  master.json (378 Everything rows)
  catalogue-meta.json
  18 other review JSONs + data.json/meta.json
  index.html / app.js / style.css / .nojekyll
```

Generators:
- `process_data.py` → `docs/data.json/meta.json` (pass-through, header=1)
- `build_research_master.py` → master draft + exclusions (includes streaming apply, filename apply, format inference 104, title cleanup 13, series approvals 316, work families 334)
- `build_catalogue_pages.py` → 20 JSONs + meta (derives primary relationships)
- `map_series_taxonomy.py` → series mapping + queue (preserves approved/rejected overlay, validates fan-out conflicts)
- `fetch_veritas_catalogue.py` → candidate inventory + diff artifact (review-only, never auto-commit, retry ladder MAX_PAGE_ATTEMPTS=4)
- `reconcile_research_master.py` → `RECONCILIATION_REPORT.md` read-only

Shared: `_common.py` (read_csv, render_csv, json_text, ISO_DATE)

## Current Verified State — Re-executed

| Metric | Count | Notes |
|---|---:|---|
| Raw CSV rows | 374 | header=1 skips Google Sheets title |
| Ledger dispositions | 305 item, 69 excluded, 31 blank_separator, 21 series_context, 10 research_note, 5 source_context, 1 duplicate, 1 needs_review | ledger hand-maintained |
| Curated master | 358 | 307 lecture / 40 book / 10 discussion / 1 untyped (246) |
| Year blank | 18 | 13 Volume Series (blank per owner, pre-2000 unknown) + 5 under investigation (Verification of Spiritual Realities 230–232, 246, God is Hidden 268) — was 31 pre-PR24 (11 edition audiobook years + 2 Office outliers fixed) |
| Format blank | 2 | Progressive Levels of Consciousness – Oxford 2003 (221) + untyped 246 — same set as year-blank overlap (was 8 pre-PR24) |
| Proposed filename coverage | 358/358 | unique 358 safe, 358 display |
| Work_id coverage | 358/358 | 201 works, 334 members |
| Catalogue codes | 280 | distinct, lecture/discussion only, Volume stripped -> no codes |
| Master exclusions | 69 | |
| Source overrides | 127 approved | 72 veritas, 26 hayhouse, 7 audible, 4 NC (327-330), 18 Amazon |
| Manual candidates | 29 promoted / 0 pending | 6 original Veritas + 9 Satsang + 3 academic + rest |
| Manual leads | 1 | outside master |
| Edition candidates/promotions | 24/24 | all promoted, minted UUIDs 320-343 etc, D3 applied |
| Veritas products | 191 | 172 primary, 7 compilation, 6 title, 4 excluded, 1 normalized, 1 unreviewed (1560 Map poster) |
| HayHouse | 24 | 20 matched, 4 unreviewed |
| Audible | 26 | 17 matched, 6 unreviewed, 3 possible |
| Product relationships CSV | 8 | related_material only, primary 328 derived |
| Rendered relationships | 336 | 328 derived + 8 related |
| Series compilations | 7 | Highlights annual |
| Series mapping | 179 | 169 approved / 10 rejected / 0 proposed |
| Taxonomy queue | 6 | conflict guardrails, all ruled |
| Filename proposal | 358 | unique |
| Streaming URLs | 36 approved | -> 59 masters have reference_url_1 |
| Everything view | 378 | 358 master + 8 veritas candidate (7 Highlights + 1 merchandise) + 4 discovery + 4 hayhouse + 4 audible |
| Original source rows | 374 | |

All counts from `docs/catalogue-meta.json` match docs.

## Pipeline Deep Dive

### `build_research_master.py` (1278 stmts, 670 measured)
- Helpers: `read_csv`, `index_csv`, `veritas_products_by_id/by_url`, `require_columns` — deduped into `_common.py`
- Compact ID assignment: stable 1..10000 by raw_row_number, retained from committed draft
- Ledger → items: title cleaning (mp4, -converted, numeric prefix, Volume II->I fix for raw 224), notes, reference URLs
- Promotions: manual candidates (UUID explicit), edition promotions (UUID explicit, D3 audible URL move off book row)
- Applies in order: source overrides (including candidate_keyed for promoted rows 316/318 etc) → streaming (59 masters) → filename proposal (358) → backfill months (Veritas published_date, year-matching guard prevents 2014 leak into 2003-2005) → format inference (104 inferred, exact URL first then pid fallback, book category guard) → title hygiene (13 cleaned, normalized equality guard, legacy_title preserved) → series approvals (316 approved mappings, 3 values changed) → work families (334) → integrity (UUID unique, title non-empty, work_id w- prefix, only 246 may be untyped)
- Validates manual candidates (promotion_status must match promotion registry), edition candidates (work_id must exist in families, role in set, matched_master_uuid exists, carrier format, year YYYY, owned bool, review_status proposed/reviewed_candidate, ISO dates, evidence, source_name veritas/audible/hayhouse, inventory exact URL/title match)
- Writes CSV/JSON + exclusions, `csv_text` uses `render_csv` with LF.

Invariants enforced:
- `CONTENT_ITEM_TYPES` = lecture/book/discussion/interview/transcript/highlight/dissertation/article/other (audio/video retired)
- `CODE_ITEM_TYPES` = lecture/discussion only
- `MANUAL_CANDIDATE_FORMATS` = blank/DVD/CD/audiobook/book
- `EDITION_FORMATS` = DVD/CD/audiobook/book/streaming
- Duplicate source override detection, URL HTTPS, target_field whitelist

### `build_catalogue_pages.py` (896 stmts, 311 measured)
- Reads master + all review CSVs
- Validates work family coverage (every master needs work_id) → prevents orphan
- Validates veritas inventory: `normalized_title_match_count == len(uuids)` and `matched_master_titles == master titles join` and unknown UUIDs fail
- Validates new-work queue (unknown product, URL mismatch, duplicate, empty title)
- Derives primary relationships: per master with source_url_veritas, exact URL → product, relationship_id rel-veritas-{pid}-{uuid}, note provenance by candidate_key prefix (edition-, manual-veritas-satsang-, manual-, else generic)
- Validates product_relationships.csv: only non-primary, rel- prefix, known master, source_name veritas, known product, relationship_type in set, review_status, ISO date, HTTPS evidence, evidence_note non-empty, raw_row_number matches master provenance (raw_row or candidate_key), product URL/title exact match, primary must match master Veritas URL (but primary not in CSV anymore)
- Validates series compilations: series-compilation- prefix, veritas source, type compilation_draws_from_series, reviewed + ISO date, YYYY year, month range valid paired or blank, HTTPS evidence, URL/title match, target scope lecture count = included_lecture_count
- Everything building: master rows wrapped with record_type=master, provenance fields uniform, queue 4 discovery, veritas unmatched 8, hayhouse 4, audible 4 + 2 Spanish → international, pending candidates (0 now) via promotion registry check
- Review overview derived: Master Candidates current_state derived from promotion_status, not hardcoded
- Record_type coverage guard: sum(everything_record_types) must equal len(items)
- Outputs 18 JSONs + meta with counts

### `map_series_taxonomy.py` (337 stmts)
- Splits official_categories by ";"
- Dominance rules: R1 Lecture Highlights > annual, R2 Satsang + Highlights conflict queued, R2 Satsang years subcategory, R5 Six Book > 2002 annual, R3 single annual → vocab, multiple annual queued, R4 On The Road, R6 Office > Media Miscellaneous, R7 Card Decks + collection order Books > Discussion > Volume > Media Miscellaneous, R8 fallback only queued, R9 unknown/unresolved queued
- Vocabulary: DIRECT_SERIES, ANNUAL_SERIES (10 yearly lecture series), COLLECTION_SERIES
- NEVER_DOMINANT = New Products, catalog nav buckets
- Overlay preservation: approved/rejected rows preserved exactly (dominant, rule, mapped_series, reviewed_on, review_notes), proposed/needs_review recomputed
- Fan-out guard: one master ID cannot get two different proposed series from multiple products → conflict, all involved queued; two conflicting approved fail outright
- Invariants: duplicate pid fails, status in set, approved needs ISO date + notes, dominant must be among official categories, approved needs mapped_series, mapped_series must follow vocabulary for dominant

### `fetch_veritas_catalogue.py` (373 stmts)
- API: `https://veritaspub.com/wp-json/wp/v2/product?_fields=id,date,link,title,product_cat` + `product_cat?_fields=id,name` paged per_page 100
- get_page retry ladder 4 attempts, HTML detection (non-JSON preview), non-list check, URLError/HTTPError, 400 on page>1 = terminal
- category_names: IDs → names, unresolved marker `unresolved-category-{id}`
- Matching: source_url_index exact match → matched_by_primary_source / exact note; else Satsang date-aware → matched_by_date / Satsang note; else normalized title (html.unescape + lower + strip parens + [^a-z0-9]) + dated_index for duplicate titles with multiple date groups (e.g., A Review of the Work 2006/2007)
- Inventory rows: veritas_product_id, official_title (html unescaped), URL, published_date YYYY-MM-DD, official_categories "; " joined, normalized_title_match_count, matched_master_uuids "; " joined, matched_master_titles " | " joined, mapping_status, review_notes
- Overlay decisions: DECISION_REQUIRED_COLUMNS, DECISION_STATUSES (unique_item, compilation_or_new_edition, excluded_related_material, matched_by_title, matched_by_normalized_title), ISO dates, decision_reason non-empty, uuids valid, titles exact match, match statuses require/ forbid uuids, count recomputed
- Writes LF, CLI --check vs custom --output mutual exclusion

### Frontend (`docs/index.html` 157 lines, `app.js` 926, `style.css` 794)
- Top bar: search (debounced 250ms), clear, export CSV (whole view, rowRange all), dark toggle
- Tabs: 15 views (Everything + Review Overview + 9 review sheets + Product Relationships + Series Compilations + International + Publishers + Original)
- View summary: rows, type, export name, description
- Column chooser: visibility checkboxes, Show all, fitTable
- Review toolbar: auto-detect REVIEW_FILTER_FIELDS, multi-value select
- Active filter chips, Clear all
- Spreadsheet: Tabulator 6.5.2, layout fitColumns, maxHeight 100% → frozen header, no pagination, resizable/movable columns, editor false (read-only), rowClick → drawer
- Column width engine: offscreen canvas, measures rendered value (URL label e.g., "Veritas product", badge humanized, header + sort indicator), 560 long-text guard, 720 absolute, min 60, BADGE_FONT 500 11px, CELL_FONT 14px Roboto, HEADER_FONT 500 14px, padding 24/18/26
- Sorter: auto-detect fully-numeric columns → number sorter alignEmptyValues bottom (fixes lex 1,10,100)
- Formatters: URL → hostname or source label with ↗, status → badge, format → badge, year_month merged (year+month), edition merged (format · format_detail)
- Row details drawer: all fields except raw year/month/format when merged present
- Footer: active view row count + Last-Modified header, search status
- Dark mode: html.dark class, localStorage, swap Tabulator light/dark CSS, pre-paint inline script no flash
- Security: CSP `default-src 'self'; base-uri 'self'; object-src 'none'; form-action 'self'; script-src 'self' https://cdn.jsdelivr.net 'sha256-u2/u4gxax738T0FZixKekRcJpSj2LbWauC5THe95guI='; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src https://fonts.gstatic.com; connect-src 'self'; img-src 'self' data:` — hash verified matches inline dark-mode script; SRI pinned for Tabulator CSS+JS; no innerHTML injection (footer uses textContent, drawer uses textContent + anchor)
- `.nojekyll` present to bypass Jekyll on large JSONs

### Tests (`tests/test_pipeline.py` 1779 lines)
- Sandbox per test (fresh copy of all inputs, drop edition-scoped overrides when edition layer replaced)
- Integration: write → check → tamper for each generator, CSV determinism (two runs identical), CLI smoke, reduced pending view
- Unit: taxonomy dominance matrix, norm/title_date_key/satsang/category_names/split_uuids, build_inventory primary/satsang/normalized/unreviewed, mapping decisions validation, inventory validation (count, unknown uuid, title mismatch), everything_record defaults, record_type coverage, format inference slug signals + exact URL lookup + category guard + never overwrite, compact ID, json_text shape
- Failure paths: process_data missing outputs, stale data.json, invalid meta, stale meta, missing CSV, fallback CSV pickup
- Veritas fetcher offline: synthetic live API from committed inventory, write→check, tamper, custom output rejection, API failure preserves inventory
- get_page retry: pagination until 400, HTML retries, non-list retries, 400 first page error, URLError retries, taxonomy compact fields
- Reconcile drift: markdown/code cell hygiene, compare_drafts extras/missing/changed, report sections + stale check
- Derived primary relationships: builds from master URLs, note provenance, committed 328+8=336, CSV holds only non-primary, deleting related_material fails check
- Work families: committed clean, approved assigns, proposed not applied, unknown member, missing columns, needs date/evidence/canonical, duplicate member, tamper drift
- Edition candidates: committed clean, promotion mints, requires status flip, unknown work/master/product, duplicate key, hayhouse valid + mismatch, shape validation (format, promotion status, review_status, ISO, year, owned), promotion edges (rejected no row, missing date, work_id mismatch, deprecated item_type, unknown approval status), tamper when row vanishes
- Source overrides: proposed not applied, approved applies, candidate-keyed applies (316), invalid status fails
- New work queue: committed clean, unknown product, URL mismatch, duplicate, empty title
- Doc currency: README current state **value**, handoff table, migration ledger summary, review overview state derived, backfill month guard (listing month not leak), title cleanup only matching, books use first-publication year not listing (spots 1995,2001 etc, no codes for books)
- Defensive depth: edition UUID stability, source override idempotency, missing column clear error, untyped allowlist 246, malformed work_id, missing work_id in catalogue build
- Retired vocabulary: CONTENT_ITEM_TYPES excludes audio/video, committed inputs clean except discovery queue triage, manual candidate audio fails, ledger video fails

Playwright (`tests/column-layout.spec.js`): Work column parked between Legacy ID and Location Physical, measured width, numeric sort asc 1/2/3 desc 358/357

Total: 104 tests, 92% coverage

## Data Quality Findings

### Integrity — All Green
- All 5 --check modes pass (venv)
- Veritas inventory derived fields consistent: count == len(uuids), titles match master
- Work family coverage 358/358
- Product relationships derived 328 + 8 = 336
- Filename proposal 358 unique, no collisions

### Year Blank 31
- 13 Volume Series blank per owner decision 2026-08-04 v4: pre-2000, V1 1995 known but others unclear, stripped project-wide to blank, so no catalogue codes, filename no year prefix (e.g., `Volume I Power vs Force [1-2].mp4`). Previous v4 doc claims 1995-1999 estimated, but current master uses blank — consistent with owner feedback "do not name any if cannot name all". The v4 markdown still mentions estimated years, needs update to blank.
- 4 On The Road (221 Oxford, 225 Devotion, 226-227 Mind Heart Service) — year should be researchable (Oxford 2003? 2003?), currently blank
- 3 Discussion (278,281,284) — 2012 series title contains year but month missing? Search shows eligible for year extraction? Actually those are 2012 per series but year blank.
- 3 The Way to God, 2 Nonduality Intensive, 2 Transcending the Mind, 2 Transcending Levels, 1 Spiritual Reality — need per-lecture © year research (some On-The-Road Audible ©2003-2005 already corrected)
- 1 untyped 246 deferred

### Format Blank 8 — Same as subset of year blank
- 4 On The Road (221,225,226,227) + 3 Discussion (278,281,284) + 1 untyped 246
- Root cause: these lack Veritas URL? Check: 221 has no Veritas URL? Let's see: 221 Progressive Levels Oxford — likely no product page? 225 Devotion, 226-227 Mind Heart Service have no URL? Need official link? 278,281,284 Discussion Series have URLs? Should infer format streaming? Discussion Series category maps to streaming, but infer_format only works when URL present and category present. If missing URL, blank stays. Could backfill from series: On The Road -> DVD? Discussion -> streaming? Manual candidate promotion maybe.
- Second inference pass evidence in archive/TEMP_FORMAT_POPULATION_PROPOSAL.md — SKU prefixes, product-detail strings, still open.

### Untyped Record 246
- `"In the World But Not of It" – Audio`, raw_row 296, work_id `w-in-the-world-but-not-of-it-audio`, deferred per deduplication rebuild (duplicate audio territory with book). Allowed by allowlist. Provenance: raw title `26. "In the World But Not of It" – `, owned true. Should be ruled as lecture? Product 1661 mapping-row only, not override. Needs owner ruling.

### Streaming Blind Spot — Option A Minimal Implemented 36 products → 59 masters
- `data/veritas_streaming_urls.csv` 36 approved rows (all approved), each veritas_product_id → streaming_url (e.g., https://veritaspub.com/success-october-2009/)
- Applied as reference_url_1 when empty: **59 masters** carry a streaming reference (one product can map to several masters/parts; count verified 2026-08-07)
- Methodology proven, remaining ~115 Veritas lecture products need same fetch (owner note: 5 per turn). Open P1.

### Veritas Unreviewed 1
- Product 1560 `Map of Consciousness®` — merchandise poster, correctly stays candidate_veritas, not master. Good.

### HayHouse Unreviewed 4 + Audible Unreviewed 6 + Possible 3
- HayHouse 4: likely journal/deck + audio program + maybe other
- Audible 6 unreviewed + 3 possible_related_match — Spanish titles moved to International (Disolver el ego, El nivel más alto). Remaining need deduplication ruling.
- International queue 36 rows (includes Spanish Audible + manual international list)
- Official discovery queue 4 NC compilations: Ultimate Library, Discovery, Healing (possible_related_match to Healing and Recovery but distinct?), Naked (with contributors). Needs owner ruling whether to promote as new works or keep as related_material / compilation.

### Series Taxonomy Queue 6 — Why lingering?
- Queue rows all have `queue_reason` about master ID receives conflicting series from multiple products (IDs 202, 121) or multiple annual categories (50521). Their review_status in mapping CSV is approved/rejected already, but queue file regenerated keeps them as visibility? Actually `map_series_taxonomy.py` builds queue from choose_dominant + fan-out conflicts. If mapping row approved but still conflict, queue keeps reason but status stays approved? Let's see: queue CSV fields include review_status + queue_reason. In this repo, queue has 6 rows: 3 approved, 3 rejected, each with queue_reason about conflict. So queue is informational, not active pending. That's intentional — preserves transparency. However docs say 0 proposed, which is true (all ruled), but queue not empty (6 queued for visibility). Baseline doc says 6 queued rows are all ruled — that matches. But could be confusing; queue should be empty if all ruled? Policy says queue contains conflict/ unrecognized routed to review, with queue_reason. After ruling, they stay? Implementation keeps them in queue if reason still present even if approved. So queue = 6 is expected if conflicts persist. Needs doc clarification.

### Filename Proposal — Owner Feedback Implemented
- v4: grouping by (year_month, clean_title, format) fixes Eye of the I pdf vs m4b no longer [1/2][2/2]
- Volume Series canonicalized, bracket standardized
- Satsang month stripped: `2009-01 - Satsang Series.mp3` not `(Jan 2009)`
- Audiobook label removed, `.m4b` indicates
- Safety: illegal chars stripped, max 120, hyphen for slash, uniqueness 358
- Open: Power vs Force audiobooks 320 and 331 same cleaned title same year same format audiobook → currently [1-2][2-2] disambiguation (is that desired? They are different editions Audible vs Veritas audio book? Could add source tag or keep bracket? Doc notes this as open question)
- Volume Series year blank → filename no year prefix (current: `Volume I Power vs Force [1-2].mp4`). Previous doc still mentions 1995-1999 estimated — drift, needs doc sync.

### Title Hygiene
- 13 lecture titles cleaned where stripped form equals official Veritas title (PART1, (Part1), DVD01, -converted, .mp4 noise). Raw kept in legacy_title, title_source records official listing. Good.
- Further hygiene possible: Volume Series still have "Volume I-Power vs Force (Part 1)" raw -> cleaned to "Volume I-Power vs Force (Part 1)" still? Some cleaned earlier? Check: still have "Volume I-Power vs Force (Part 1)" in master? Actually list shows still includes "(Part 1)"? Year blank set shows title still has (Part 1). Title hygiene only applied to lectures where cleaned equals official. Volume official titles maybe "Volume I-Power vs Force (Part 1)" themselves, so cleaning would not match? Might need canonical mapping (owner-approved) — currently filename proposal has canonical but title still raw? That is intentional: title hygiene is evidence-based, not guess.

### Edition Model — Fully Applied
- Work_id from approved families only, never title-inferred (C2 lesson)
- 201 works, 334 members, includes per-part works + academic works (Orthomolecular 1973, Qualitative 1998, Dialogues 1998)
- Edition rows minted via explicit UUID in promotions file, stable
- D3: audio URLs moved off book rows into edition rows (prevents collapsed edition)
- Remaining: 0 new-work queue rows pending (all promoted), but official discovery 4 NC compilations pending ruling

## Frontend Audit

- **Column width engine**: measured in real pixels across all rows, rendered text (URL label, badge humanized, header + sort indicator), long-text guard 560/720, min 60. Previous char-count heuristics oversize URL columns — fixed. Verified by new file sizes: master.json 10k lines -> measured 560+ works.
- **Work column placement**: parked between Legacy ID and Location Physical via moveAfter, per owner, display-only.
- **Proposed filename column**: between Title and Item Type, per owner.
- **Year-Month merged**, Edition merged (format·detail)
- **Sorting**: Master ID numeric with alignEmptyValues bottom → 1,2,3 ... not 1,10,100. Blank candidate IDs pin bottom both directions. Fixed.
- **Search**: global live search across all columns, 250ms debounce, filter chips, clear all
- **Filters**: Review filter auto-detects field with >1 distinct value, multi-value select
- **Export**: whole sheet (rowRange all), not filtered subset — important for review.
- **Row drawer**: accessible, all fields, URL links, status badges.
- **Dark mode**: persisted localStorage, OS preference first time, no flash.
- **Accessibility**: aria-live polite, aria-busy, role tablist/tab, aria-selected, keyboard Esc closes menus/drawer, focus-visible outlines.
- **Security**: CSP hash `sha256-u2/u4gxax738T0FZixKekRcJpSj2LbWauC5THe95guI=` matches inline dark-mode script, SRI pinned for Tabulator CSS+JS, no innerHTML injection (textContent used, anchor creation safe), default-src self, object-src none, form-action self, connect-src self, img-src self data.
- **Performance**: `.nojekyll` bypasses Jekyll, static serve; Tabulator maxHeight 100% frozen header + internal scroll; absolute positioned spreadsheet fills container; debounce resize 150ms.
- **Testing**: column-layout.spec.js guards Work placement + widths + sort (CI only, Chromium not installable sandbox).

## CI/CD

- `ci.yml`: checkout, py 3.12, pip cache, py_compile all .py, process_data --check, build_research_master --check, build_catalogue_pages --check, reconcile --check, map_series_taxonomy --check, unittest discover, coverage run + report (80% floor, actual 92%), node 20, node --check app.js + playwright config + csv-export spec, npm ci, playwright install chromium, npm test:e2e, upload artifact on failure. Concurrency group ci-ref cancel in-progress.
- `map_veritas_catalogue.yml`: manual dispatch only, review-only, writes candidate CSV + diff patch artifact, never auto-commits. Good governance.
- `update_spreadsheet.yml`: manual + push on main when source CSV changes, regenerates docs/data.json + meta.json via git-auto-commit-action with GITHUB_TOKEN (known trap: GITHUB_TOKEN commits don't trigger pages-build-deployment, needs manual re-run or PAT).
- GitHub Pages: Settings → Deploy from branch main /docs, .nojekyll prevents Jekyll timeout on large JSONs (most likely root cause of past deploy failures). Deployment analysis doc covers 4 root causes: Jekyll timeout (fixed), GITHUB_TOKEN trigger ban, Pages source drift, visibility/concurrency.
- No workflow file push via Arena app (cannot push workflow changes), owner must apply in web editor — documented in archive/UNBLOCK_INSTRUCTIONS.md.

## Documentation Health

Root Markdown: 20 files (README, INSTRUCTIONS, NEXT_AGENT_HANDOFF, FULL_STACK_AUDIT_..., CATALOGUE_READABILITY_ROADMAP, CATEGORY_DOMINANCE_POLICY, EDITION_MODEL_PROPOSAL, FILENAME_PROPOSAL_..., GITHUB_PAGES_DEPLOYMENT_ANALYSIS, ITEM_TYPE_CLASSIFICATION_PROPOSAL, LECTURE_SERIES_REVIEW, LECTURE_YEAR_INVESTIGATION, MIGRATION_REVIEW_LEDGER, OFFICIAL_CATALOGUE_DISCOVERY, OFFICIAL_SOURCE_REGISTRY, PRODUCT_RELATIONSHIP_SCHEMA, RECONCILIATION_REPORT, REVIEW_MODEL_SLIM_ANALYSIS, SERIES_COMPILATION_SCHEMA, SERIES_TAXONOMY_MAPPING, SERIES_WORK_REGROUPING_PROPOSAL, TITLE_HYGIENE_PROPOSAL, VERITAS_ARTIFACT_REVIEW, VERITAS_PRODUCT_MAPPING) — consolidated from 41 → 20 in earlier sessions.

Decisions: 13 files (AUDIBLE_MAPPING, BOOK_RELATIONSHIP, COMPILATION_CANDIDATE, FINAL_TITLE_MATCH, HAY_HOUSE, HIGHLIGHTS_COMPILATION, NIGHTINGALE_CONANT, README, RECONCILIATION, SATSANG, SERIES_REGROUPING, UNIQUE_ITEM_CANDIDATE, VERITAS_MAPPING)

Archive: 46 files (superseded audits, backfill reports, dedup scripts) indexed in archive/README.md

Living docs accurate? Checks:
- README current state: master 358, 280 codes, 69 exclusions, 127 overrides, 29 promoted, 336 relationships, 7 compilations, proposed_filename note — matches catalogue-meta (307 lecture/40 book/10 discussion/1 untyped matches; filename-proposal doc synced to blank Volume years 2026-08-07)
- NEXT_AGENT_HANDOFF §3 table: 358/378/69/127/201 works/334 members etc — matches
- MIGRATION_REVIEW_LEDGER.md classification summary: item 305 etc — matches ledger
- REVIEW_OVERVIEW Master Candidates derived state guard exists (test)

Doc-currency tests: 5 guards (README, handoff, migration ledger, review overview state, backfill month, title cleanup, book year, etc) — all pass, but prose drift like FILENAME_PROPOSAL_V4 still says 1995-1999 estimated not blank - not covered by tests (char count heuristics). Should update.

Governance docs: CATEGORY_DOMINANCE_POLICY (R1-R9), SERIES_TAXONOMY_MAPPING lifecycle, PRODUCT_RELATIONSHIP_SCHEMA (derived primary), EDITION_MODEL_PROPOSAL (phases done), TITLE_HYGIENE_PROPOSAL, ITEM_TYPE_CLASSIFICATION_PROPOSAL (implemented), SERIES_COMPILATION_SCHEMA, etc — comprehensive.

RECONCILIATION_REPORT.md intentionally shows 53 draft-only records (edition rows + manual promotions) not in ledger projection, status "not yet fully reconciled" — this is expected: report compares committed draft vs ledger-only build, but draft includes edition/promotion rows that ledger doesn't have (they are separate inputs). The report's summary is misleading if read as failure; actual pipeline is reconciled via all inputs. Might need note that extras are expected due to edition layer.

## Security & Hygiene

- No secrets in repo, no env vars needed
- No eval, no innerHTML, no unsanitized URL
- SRI pinned for CDN, CSP restricts script/style to self + cdn.jsdelivr.net + fonts.googleapis.com (style unsafe-inline needed for Tabulator? Could be tightened but current is acceptable)
- LF line endings (previous CRLF issue fixed, now LF normalized)
- Python 3.11 sandbox / 3.12 CI compatible
- No hand-edits of generated files (docs/*.json, data/research_master_draft.* etc are generated but committed — enforced by --check)
- Private: only UUID 246 allowed empty item_type, work_id w- prefix, etc.

## Risks & Open Work

**P0 — Owner actions (already documented):**
- Re-run Map Veritas Catalogue workflow after merge — should now pass clean (191 exact match, LF normalized, title drift fixed). If not, artifact diff review.
- GitHub Pages source still Deploy from branch main /docs, .nojekyll present — verify live site https://56eli.github.io/docsheet serves master 378 after merge.

**P1 — Data decisions needing ruling (real gaps, not bugs):**
- **Year blank 18** (was 31): 13 Volume Series intentionally blank (pre-2000 unknown; FILENAME_PROPOSAL_V4 synced to the blank rationale 2026-08-07) + 5 under investigation (Verification of Spiritual Realities 230–232, record 246, God is Hidden 268). The remaining blanks need © year research (Audible ©, Veritas product page, physical media). For other blanks: Devotion 2003? Mind Heart Service 2005? Oxford 2003? Discussion 2012? Need per-product evidence.
- **Format blank 2** (was 8): Oxford 2003 lecture (221) + untyped 246. Should infer from series: On The Road → DVD (Office Visit precedent), Discussion → streaming, untyped 246 → audiobook? Could add second inference pass using series_category_mapping or manual overrides.
- **Record 246 untyped**: deferred pending physical-edition confirmation. Should be typed lecture or excluded? Product 1661 mapping-row only, not override. Needs owner decision whether to promote as distinct audio edition (NW?).
- **Streaming blind spot**: 36 product IDs mapped → 59 masters have streaming URL via reference_url_1. Methodology proven, remaining ~115 Veritas lecture products need same fetch (5 per turn per earlier handoff). Could continue in batches.
- **Official discovery queue 4 NC**: The Ultimate Library, Discovery, Healing, Naked — compilations/programs that need content/edition review. Healing is possible_related_match to Healing and Recovery but distinct program. Owner ruling needed whether they become new master rows, related_material, or stay discovery.
- **HayHouse 4 + Audible 6+3 unreviewed**: remaining inventory products not yet ruled as unique_item/compilation/etc. Need mapping decisions.
- **Series taxonomy queue 6**: informational conflicts (IDs 202, 121, 50521) — all approved/rejected but queue still shows because fan-out conflict persists. Either clear queue_reason after ruling or accept as transparent audit trail. Currently docs say 0 proposed but 6 queued — could be clarified.
- **Filename proposal disambiguation**: Power vs Force audiobooks 320 and 331 same cleaned title same year same format → [1-2][2-2] currently. Is that desired? They are different carriers (Audible vs Veritas audio book). Could add source tag or keep bracket. Owner feedback: "Remove audio book from names, it can be recognized from file type" — but two audiobooks same title same type still need disambiguation. Suggestion: add edition source to clean_title? Or keep bracket as currently.

**P2 — Hygiene / Tech Debt:**
- **FILENAME_PROPOSAL_V4.md doc drift**: says Volume Series 1995-1999 estimated, but master now blank pre-2000. Should update to blank + rationale + "Year under investigation, believed pre-2000" (ledger review_reason).
- **RECONCILIATION_REPORT.md**: shows 53 extras as "not yet fully reconciled" even though they are expected from edition layer. Could adjust report to note edition/promotion rows are expected extras and not a failure, or adjust compare_drafts to include edition layer? Currently it only compares ledger→master, not promotion layer. The report is still useful but summary note could be clearer.
- **Proposed filename for Volume Series without year**: currently `Volume I Power vs Force [1-2].mp4` (no year prefix). Is that desired per owner "do not name any if cannot name all" — yes. But grouping key (year_month, clean_title, format) with blank year_month may group all Volume Series together? Check: vol year blank, year_month "" → grouping would be ("", clean_title, format) → that might incorrectly group across years? But since year blank, all Volume I parts share "" + canonical title → correctly groups as multi-part [1-2] etc. That's fine, but if two different Volume I releases from different years both blank, they'd collide? Currently only one set per canonical title, so okay.
- **ITEM_TYPE vs FORMAT**: `format` vocabulary now {DVD, CD, book, audiobook, streaming} minimal per owner decision 2026-08-04 (audio→audiobook). `book` as format is odd (carrier is paperback/hardcover) but owner kept it. Could consider `format_detail` for carrier subtype (e.g., paperback vs hardcover) later.
- **Potential duplicate work families**: 201 works / 334 members — coverage 100% but check if any work has only 1 member (could be okay) vs multi. Quick spot check: many lecture series have 1 work per 3 DVD parts (w-causality etc) — that seems per-lecture work, not per-series. That is per owner D1 "keep one row per DVD part" + per-part works (D6a). That is implemented.
- **Coverage**: 92% total, missing lines are CLI guards and rare branches. Good.
- **Frontend bundle**: Tabulator via CDN, no local vendor copy — offline dev needs network. Could vendor locally.

## Grades (subjective)

| Area | Grade | Rationale |
|---|---|---|
| Data pipeline determinism | A+ | 5 checks green, run-twice deterministic, tamper detection, idempotency |
| Data governance | A+ | Reviewed inputs, approval registry, no title-based inference, derived primary |
| Completeness | A | 358 master literal all-ever-produced incl. 3 academic, 191 Veritas exact match, but 31 year blank + 8 format blank + 4 NC pending |
| Edition model | A | 201 works, 334 members, 24 editions, D3 applied, work_id coverage 100% |
| Frontend | A | measured-width engine, numeric sort fixed, Work parked, filename column, CSP+SRI, dark mode, .nojekyll |
| Tests | A+ | 103 deterministic, offline replay, rule matrices, doc-currency guards, 92% coverage |
| CI/CD | A- | 5 checks + unittest + coverage + JS + Playwright, concurrency, but GITHUB_TOKEN Pages trigger ban still |
| Docs | B+ | comprehensive, but FILENAME_PROPOSAL_V4 doc still mentions 1995-1999 estimated vs blank reality, reconciliation report 53 extras misleading |
| Security | A- | CSP+SRI, no innerHTML, LF, but style-src unsafe-inline needed for Tabulator (could tighten) |

## Recommendations (next steps, prioritized)

1. **Sync FILENAME_PROPOSAL_V4.md** to current blank Volume Series reality: update "1995-1999 estimated" to "blank pre-2000 per owner 2026-08-04 v4 feedback: do not name any if cannot name all", and note ledger review_reason. Regenerate filename_proposal CSV to confirm no year prefix for Volume Series (already done) and document Power vs Force duplicate audiobook [1-2] decision.
2. **Resolve year/format blank 31/8**: create research queue `data/year_format_backfill_queue.csv`? Or directly research per-title Audible © years for remaining On The Road (Devotion 2003?, Mind Heart Service 2005? etc) and Discussion 2012? Use fetch_page tool for veritaspub product pages (Veritas API doesn't give recording year, only published_date). Add proposed_year/month in ledger/manual candidates, not via backfill.
3. **Rule on 246**: either type as lecture audio edition (if physical exists) or exclude with documented reason. Currently work_id exists but no URLs, blank format/year. If excluded, move to exclusions; if typed, assign item_type lecture, format audiobook, year research, source override?
4. **Continue streaming blind spot Option A**: batch 5 product IDs per turn as handoff suggested, fetch streaming page via fetch_page (veritaspub.com/{slug}-streaming/), add to veritas_streaming_urls.csv with approved status, regenerate. Aim for ~115 more.
5. **Official discovery queue ruling**: decide on 4 NC programs: if Healing is distinct from Healing and Recovery, promote as new work? If Ultimate Library, Discovery, Naked are compilations, mark as excluded_related_material in veritas_mapping_decisions? Document in decisions/NIGHTINGALE_CONANT_MAPPING.md.
6. **HayHouse/Audible remaining**: 4 HayHouse unreviewed (journal/deck etc) → likely excluded_related_material merchandise, 6 Audible unreviewed + 3 possible → unique_item or compilation_or_new_edition ruling. Add decisions.
7. **Clarify taxonomy queue**: either make queue empty when all ruled (clear queue_reason after ruling) or document that queue 6 is informational conflict trail. Update SERIES_TAXONOMY_MAPPING.md baseline to state 6 queued rows are all ruled but remain for transparency.
8. **Reconciliation report wording**: update render_report to explain 53 extras are expected from edition/promotion layer (not ledger-only), or make compare_drafts include edition families? Currently it only compares ledger-derived items vs committed master which includes promotions → always shows extras. Could add flag `--include-promotions` or note in markdown that extras include approved promotions. Prevents misreading as failure.
9. **Frontend**: vendor Tabulator locally to allow offline dev? Optional. Add test for .nojekyll presence (doc-currency).
10. **CI**: consider PAT for update_spreadsheet workflow to trigger Pages deploy, or document manual re-run requirement in INSTRUCTIONS.

## Reproduction Commands (all green)

```bash
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install -r requirements-dev.txt
/tmp/venv/bin/python build_research_master.py --check
/tmp/venv/bin/python build_catalogue_pages.py --check
/tmp/venv/bin/python reconcile_research_master.py --check
/tmp/venv/bin/python map_series_taxonomy.py --check
/tmp/venv/bin/python process_data.py --check
/tmp/venv/bin/python -m unittest discover tests -v
/tmp/venv/bin/coverage run -m unittest discover tests && /tmp/venv/bin/coverage report
node --check docs/app.js
```

## One-Sentence Summary

The curated Hawkins archive pipeline is deterministically green (358 master, 378 Everything, 104 tests, 92% coverage, all checks) with intentional review gaps (31 year-blank, 8 format-blank, 1 untyped 246, 36→56 streaming mapped, 4 NC discovery pending) and minor doc drift in filename proposal V4.

*End of deep audit 2026-08-07.*
