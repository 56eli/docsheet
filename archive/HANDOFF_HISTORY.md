# Handoff History (archived session chronicles)

Superseded session narratives moved out of `NEXT_AGENT_HANDOFF.md` in the
2026-08-07 hygiene checkpoint (hygiene batch 2, item D). **Not current state**
— for the current state always use `../NEXT_AGENT_HANDOFF.md` §3 and the
generated `../RECONCILIATION_REPORT.md`. Kept for provenance: these entries
explain *why* past rulings were made.

---

## 4. What happened in the 2026-08-03 sessions (in order)

1. **Full coherence audit** → 4 critical data defects fixed (earlier PRs, merged).
2. **CI red-on-main fix (`52502d4`):** committed Pages outputs were built with
   `--include-pending` while the script defaulted to off → plain `--check`
   differed. Default flipped via `BooleanOptionalAction`; meta record-types
   guard added.
3. **Docs consolidation (`2f05c0f`):** root Markdown 41 → 20; rulings under
   `decisions/`, superseded material under `archive/` (both indexed).
4. **Taxonomy mapper (`1b1a38b`):** `map_series_taxonomy.py` implements the
   Category Dominance Policy; fetcher now persists `product_cat` names.
5. **Inventory refresh (`d37bdc6`):** 4 stale primary matches (1728/1742/1695/1560)
   demoted to `unreviewed_official_product`; 1661 relinked to record 264; queue
   ruled (147 approved / 3 rejected); `apply_series_approvals()` wired into the
   master build (first application provably 0 series changes).
6. **Spreadsheet UX (`b747233`):** compact column defaults, Year+Month merged
   into display-only `year_month` (YYYY-MM), Series moved between Master ID and
   Title, CSV export now exports the **whole sheet** (`rowRange "all"`).
7. **Tests + fail-safes (this turn):**
   - `tests/test_pipeline.py` — 93 tests: end-to-end write/check/tamper runs of
     all generators in sandboxed input copies, run-twice determinism for the two
     bootstrap generators, offline replay of the live fetcher (synthetic API
     rebuilt from the committed inventory + retry-ladder unit tests), CLI
     entrypoint smoke, drift rendering, and the full rule matrices.
   - `.coveragerc` + `requirements-dev.txt`; coverage gate 80% → **92% actual**.
   - New fail-safes in `build_catalogue_pages.py`:
     `validate_veritas_inventory()` now enforces count-consistency **and**
     `matched_master_titles` correctness (hand-edit drift fails the build);
     the catalogue meta now raises if `everything_record_types` doesn't cover
     every row.
   - Test-authoring trap that cost an hour: a shared class sandbox is polluted
     when a determinism test regenerates the ledger before sibling tests use
     it — tests now build a **fresh sandbox per test**.
8. **CI landed on `main` (`6b28e66`)** — owner applied the workflow-file
   changes; run `30834666253` green (includes the full deterministic suite +
   coverage gate + Playwright).
9. **Independent re-audit + doc-status pass (branch
   `arena/019fc893-docsheet`):** verified every previous claim (93 tests,
   92% coverage, all `--check` modes, CI green on `main` at `6b28e66`), then
   closed the remaining status-quo drift the earlier pass had left: README/
   handoff catalogue codes 223 → **225**; `MIGRATION_REVIEW_LEDGER.md`
   disposition table (item 308 → **306**, research_note 8 → **10**);
   `archive/OFFICIAL_CATALOGUE_DISCOVERY.md` and `archive/VERITAS_PRODUCT_MAPPING.md`
   308-master/344-Everything → 317/363; `archive/RELATIONSHIP_EXPANSION_AUDIT.md`
   (304 URL-bearing masters, 157 distinct URLs, 293 primary / 8 related);
   `archive/ITEM_TYPE_CLASSIFICATION_PROPOSAL.md` marked implemented;
   `archive/README.md` UNBLOCK note resolved. Found and closed **F1**: the 11
   promoted masters (309–319) had a Veritas URL but no primary relationship
   row — 11 reviewed `primary_product_for_item_part` rows were added
   (owner-approved 2026-08-03), the coverage guard in
   `build_catalogue_pages.py` was promoted from a warning to a **hard build
   failure**, and the relationship count is now **312**. Added
   **documentation-currency tests** so README/handoff/ledger-doc counts can
   never silently drift from the generated data again. Details in
   `archive/AUDIT_2026-08-03_FULL.md` §12.
10. **Edition model + session close-out (branch
    `arena/019fc893-docsheet`):** owner directed one row per work × carrier.
    Phases 1–4 implemented (work_id plumbing, edition-candidate layer with
    pinned UUIDs, inventory-wide batches, Work/Edition UI columns) and the
    full batch applied: master 317 → **350** (24 edition rows + 9 Satsang
    monthlies), 193 works / 326 members (work_id 350/350), overrides →106
    (incl. candidate-provenance support, 316/318 Hay House links), book-format
    backfill (12 books), relationships →327, Everything →396, New Work Review
    lane (14 → 5 rows after the Satsang rulings), D6a per-part works + C1
    split, doc-currency/coverage/tamper tests (93 tests, 92%). Live site
    checked: serves `main` (363 rows) until this branch merges.
11. **Deduplication, URL fills, format/year backfills, and schema cleanup (`b23e082`, PR #17):**
    Resolved duplicate audio record territory for "In the World But Not of It" (legacy untyped row 296 rebuilt as compact UUID **246**, deferred). Backfilled 65 blank formats from official inventory (fill rate 89%, blanks 73 → **8**), backfilled 86 years (blanks 116 → **30**) and 95 months (blanks 152 → **57**). Cleaned 14 redundant notes from master and separated `raw_row_number` into numeric `raw_row_number` and `candidate_key`. Fixed Nightingale-Conant URL placement and added 7 Hay House URLs (overrides 100 → **106**).
12. **Full project audit, documentation status-quo refresh, and fail-safe enhancements (branch `arena/019fc974-docsheet`):**
    Conducted a full project audit and updated all core documentation (`NEXT_AGENT_HANDOFF.md`, `SERIES_TAXONOMY_MAPPING.md`, `SESSION_SUMMARY_2026-08-03.md`, `README.md`, `INSTRUCTIONS.md`) to resolve stale references to record 264 (now **246**), 73 blank formats (now **8**), 100 overrides (now **106**), and series taxonomy counts (149 matched / 146 approved). Archived 4 temporary analysis scripts (`dedup_analysis.py`, `dedup_analysis2.py`, `find_nc_url.py`, `dedup_plan.md`) to `archive/` so default `--source=.` test coverage measures only the 8 pipeline modules and reports a clean **92%** (all modules ≥ 89%). Added structural invariant fail-safes in `build_research_master.py` (`validate_master_items_integrity`) and `build_catalogue_pages.py` (`validate_work_family_coverage`) with 3 new defensive tests (**96 tests**, all passing). Added `docs/.nojekyll` and created `GITHUB_PAGES_DEPLOYMENT_ANALYSIS.md` to troubleshoot and prevent GitHub Pages deployment failures on large JSON files. Consolidated web UI (`docs/index.html`) by removing redundant raw publisher inventory tabs ("Veritas Products", "Hay House Products", "Audible Products"), making the Everything tab authoritative while preserving JSON endpoints for pipeline validation.
13. **Full-stack audit + documentation consolidation round 2 (this turn, branch `arena/019fc9b5-docsheet`):**
    Independently re-verified the entire stack from a clean venv (all 5 `--check`
    modes, 96 tests, 92% coverage, JS syntax, and every published catalogue
    count against `docs/catalogue-meta.json`) and published the findings as
    `archive/FULL_STACK_AUDIT_2026-08-03.md`. Consolidated the root Markdown from
    **34 → 20 files**: archived the five overlapping 2026-08-03 audits
    (`AUDIT_2026-08-03_FULL`, `COMPREHENSIVE_AUDIT`, `STATUS_QUO_AUDIT`,
    `TEMP_RESPONSE_AUDIT`, `EVERYTHING_VERIFICATION_REPORT`), the five dated
    backfill reports, `SESSION_SUMMARY_2026-08-03.md`, and four closed
    point-in-time reviews (`SPREADSHEET_AUDIT`, `SPREADSHEET_UX_REVIEW`,
    `UUID_264_REVIEW`, `RELATIONSHIP_EXPANSION_AUDIT`) to `archive/` (indexed
    in `archive/README.md`); all moved files are preserved in git history and
    remain reachable at their `archive/` paths. Fixed prose drift the
    currency tests don't cover: README record-type table `(350)` → `(356)`,
    README audit link now targets the current full-stack audit, and the §6
    "six always-empty master columns" claim corrected to **five** (Hay House
    URLs were populated by the 2026-08-03 backfill — 28 values). Verified
    post-move: all 5 `--check` modes pass, 96 tests green, no broken
    root↔archive links.
14. **Retired the deprecated `audio`/`video` `item_type` vocabulary (this turn, same branch):**
    `DEPRECATED_MEDIUM_ITEM_TYPES` deleted from `build_research_master.py`;
    candidates, promotions, master, and ledger validators now all enforce
    `CONTENT_ITEM_TYPES` directly (4 enforcement points). The last 8
    `manual_master_candidates.csv` rows still using the values were migrated
    to their owner-approved promoted types (cross-checked against
    `data/manual_candidate_promotions.csv`: 6 × `audio`→`lecture`,
    2 × `video`→`discussion`), and the 2 Spanish-Audible literals in
    `build_catalogue_pages.py` were fixed `audio`→`book` (matching the
    queue's own typing; regenerated `docs/international-products.json`).
    Master output provably unchanged (`--check` green). Test suite **96 →
    100**: vocabulary assertion, committed-input sweep (with the documented
    `official_discovery_queue.csv` triage exemption), and two
    build-failure guard tests (candidate `audio`, ledger `video` — the
    latter caught that only `disposition="item"` ledger rows reach the
    validator). Coverage 92%.
15. **Map-Veritas refresh accepted + Veritas candidates linked to their masters (2026-08-04, same branch):**
    The workflow's diff artifact was reviewed: the live fetch correctly
    re-matched 13 products to masters minted on 2026-08-03 (9 Satsang
    monthlies 344–352, edition rows 327/328/330, and 1661 → 329) — the gate
    failed by design. Accepted the diff after asserting **every changed row
    against its master's primary Veritas URL**. Then lifted the overlay's 17
    stale suppression rows (`veritas_mapping_decisions.csv` 35 → 18): the
    products for already-promoted masters 309–319 and 353–358 no longer need
    their pre-promotion dispositions preserved, so the deterministic
    primary-source matcher now links them (owner-directed "promote all
    Veritas candidates" request). Reviewed inventory rewritten with LF
    endings (it was committed CRLF while the fetcher writes LF — the reason
    every artifact diff displays as a whole-file rewrite). Everything 396 →
    **376** (`candidate_veritas` 28 → **8**: the 7 annual Highlights
    compilations, which live in the Series Compilations lane by ruling, and
    the Map of Consciousness poster, merchandise). Series taxonomy absorbed
    the 30 newly matched products as **30 new `proposed` rows** (146
    approved unchanged; 20/30 proposals equal the curated series baseline,
    10 differ — **ruled 2026-08-04, see §4 item 17**). `RECONCILIATION_REPORT.md`
    regenerated; all 5 `--check` modes green; 100 tests pass after currency
    updates. The next Map Veritas workflow run should pass with "Candidate
    matches the reviewed inventory."
16. **Frontend layout engine + hygiene batch (2026-08-04, same branch):**
    Column widths are now measured in **real pixels with an offscreen
    canvas** across **all rows** and the **rendered** text (URL columns
    measure their link label, badges measure the humanized label, headers
    include the sort indicator) — replacing the char-count heuristics +
    120-row sampling that had repeatedly failed to fit widest entries;
    long-text guardrails at 560/720px. Dead `COLUMN_WIDTHS` table removed.
    Work column parked between **Legacy ID** and **Location Physical** in the
    Everything view via per-view `moveAfter` (owner-directed, display-only).
    Hygiene: MIT `LICENSE` added (README links it), stale "inline editing"
    header comment corrected, dead `cellEdited`/`flashNote`/`FOOTER_IDLE_NOTE`
    code removed, `footerUpdated` now uses `textContent` (no interpolated
    `innerHTML`). New CI e2e spec `tests/column-layout.spec.js` guards the
    Work-column placement and width application (runs in CI; Chromium is not
    installable in the sandbox).
17. **Taxonomy rulings + Nightingale-Conant fills + Master-ID sort fix
    (2026-08-04, same branch):**
    (a) **All 10 remaining series-taxonomy proposals ruled:** **3 approved**
    — product 1814 → master **357** (Media Miscellaneous → **On The Road Talk
    Series**; publisher category and original evidence agree), products
    50485/50488 → masters **312/313** (→ **Discussion Series**; the 2012
    discussion per-title works) — and **7 rejected** with documented
    rationale (1546/1548: the On-The-Road run stands over the carrier shelf;
    1661/1695/1728/1742: editions keep their work's `Books` series,
    precedent product 1542; 55576: six conflicting publisher categories, no
    dominant home). Master regenerated: **3 series changed**, taxonomy now
    169 approved / 0 proposed / 10 rejected, 316 approved mappings cover
    316 master IDs.
    (b) **`source_url_nightingale_conant` 0 → 4:** the official NC author
    page (nightingale.com/pages/david-hawkins, fetched live 2026-08-04)
    lists exactly 7 Hawkins programs; the 4 that are master audio editions
    (masters **327–330**: Truth Vs Falsehood, Healing, In The World But Not
    Of It, The Highest Level Of Enlightenment) got approved override rows
    keyed by edition candidate key; the other 3 (Ultimate Library / The
    Discovery / Naked) are unmapped compilations that stay in the discovery
    queue pending owner ruling. Hay House: no new fills — the only
    unreviewed inventory products are a merchandise journal/deck and an
    audio title already living as a `candidate_hayhouse` row. Overrides
    **106 → 110**; `archive/TEMP_NIGHTINGALE_PROVENANCE.md` annotated as
    resolved.
    (c) **Master ID sort order fixed:** `docs/app.js` auto-detects
    fully-numeric columns and attaches Tabulator's built-in `number` sorter
    with `alignEmptyValues: "bottom"` — Master ID now counts 1, 2, 3, …
    (was 1, 10, 100, …) and blank candidate IDs pin to the bottom in both
    directions. Root cause: without an explicit sorter Tabulator guesses
    from the first row, and a blank first-row value falls back to a string
    sort. New e2e assertions in `tests/column-layout.spec.js` (click the
    header → 1/2/3 asc, 358/357 desc — IDs 249/264 are retired, so max is
    358) run in CI; ordering additionally verified in the sandbox by
    replaying Tabulator 6.5.2's `_sortRow` semantics over real
    `docs/master.json`.
    (d) **Test fixtures:** `tests/test_pipeline.py` now strips
    edition-keyed override rows (`drop_edition_scoped_overrides`) when a
    fixture rewrites the edition layer, so synthetic candidate fixtures
    coexist with the committed 2026-08-04 NC overrides. 100 tests pass,
    all 5 `--check` modes green.
18. **Year-Month semantics: books use first-publication year (2026-08-04):**
    Owner-directed: the Year-Month column must show the **recording date**
    (lectures/discussions) or **first release date** (books), never the day
    the product was **listed on the website**. The whole classic-books batch
    (Power vs Force, The Eye of the I, I: Reality and Subjectivity, Truth vs
    Falsehood, Letting Go, Healing and Recovery, Reality Spirituality and
    Modern Man, Transcending the Levels of Consciousness, and The Ego is Not
    the Real You) showed `2014` — the Veritas storefront `published_date`
    (2014-03-30 batch), not their real publication years. Fixes:
    `build_research_master.backfill_months_from_official_source()` now skips
    `item_type='book'` rows entirely (book `year` is **never** derived from a
    product-listing date); book first-publication years were set in the
    reviewed inputs (`migration_review_ledger.csv` 23 rows,
    `manual_master_candidates.csv` 6 rows, `edition_candidates.csv` 9
    audiobook rows = their work's year); and catalogue codes are now
    **lecture/discussion-only** (`CODE_ITEM_TYPES`) so books never receive a
    code even though they now carry years. Verified: Power vs Force = **1995**,
    The Eye of the I = **2001**, The Ego is Not the Real You = **2021**; codes
    still **236**; 101 tests pass (new `test_books_use_first_publication_year_not_product_listing`
    regression guard), 92% coverage, all 5 `--check` modes green.
19. **Pipeline safe-trim (2026-08-04):** owner requested a slimmer
    `build_research_master.py` (it felt like "building a mountain for one
    change"). Performed a **behavior-preserving dedup only**: added
    `read_csv` / `index_csv` / `veritas_products_by_id` / `veritas_products_by_url`
    / `require_columns` helpers and replaced the ~20 inline `with …open…
    csv.DictReader` blocks (which rebuilt the same Veritas lookup dicts in 4+
    places). No signatures or semantics changed; `--check` output is
    byte-identical; 101 tests pass; coverage 92% (module 615 → 580 stmts).
    The remaining weight is the review-gated data model itself (editions,
    work families, taxonomy, promotions, validation), not redundancy — a
    bigger structural cut (merging the manual + edition candidate lanes) was
    offered but deferred as higher-risk.
20. **F1: derive primary product relationships (2026-08-04, owner-approved):**
    `data/product_relationships.csv` was **333 → 8 rows**: every
    `primary_product_for_item_part` row exactly duplicated the master's own
    `source_url_veritas`, so those 325 rows are now **derived** from the master
    at render time by `build_catalogue_pages.derive_primary_relationships`
    (one primary relationship per master with a Veritas URL; the 8 distinct
    `related_material` rows stay in the CSV). `validate_primary_relationship_coverage`
    was removed (primary rows are auto-generated by construction). Verified:
    the rendered `docs/product-relationships.json` has the identical 333
    `relationship_id`s; the only difference is the `evidence_note` text on 4
    rows (3 Causality three-disc special notes + 1 source-override note now
    use the generic provenance note). Tests 101 → 100 (replaced the 6 obsolete
    coverage-guard tests with 5 `DerivedPrimaryRelationshipTests`); 92%
    coverage, all 5 `--check` modes green. See `PRODUCT_RELATIONSHIP_SCHEMA.md`.
21. **Review-Overview "Master Candidates" label fixed (2026-08-04):** the
    Review-Overview row for Master Candidates hardcoded
    `reviewed_candidate / not_promoted` even though all 26 candidates are
    promoted (a LOW finding from the audit). `build_catalogue_pages.py` now
    **derives** `current_state` and `purpose` from the real
    `promotion_status` column (`26/26 promoted`), and a new
    `test_review_overview_master_candidates_state_matches_data` doc-currency
    guard prevents it drifting again. Tests 100 → 101; 92% coverage, all 5
    `--check` modes green.
22. **Re-audit + shared-code dedup (2026-08-04):** full project re-audit
    confirmed the pipeline green (101 tests, 92% coverage, all 5 checks) and
    then removed cross-module duplication **without regression risk** by
    adding `_common.py`, a tiny shared helper module the generators already
    import (they already cross-import each other, so a shared module is
    consistent with the design). Moved into it the 5× duplicated `read_csv`,
    the 4× duplicated `ISO_DATE`, the 2× duplicated `json_text`, and the
    4-way CSV writer core as `render_csv` (the three `csv_text`/`write_csv`
    wrappers with different signatures keep their own names and now delegate
    to it). Removed the resulting unused `io`/`json`/`csv`/`re` imports.
    Combined coverage statements 1617 → **1594**; 101 tests, 92% coverage,
    all 5 `--check` modes green. Every committed data file is still consumed
    by a generator (no orphans). Remaining structural dedup is **F2** (merge
    the manual + edition candidate lanes — deliberately deferred as the one
    higher-risk cut).
23. **Lecture recording-year correction (2026-08-04, owner-approved):**
    investigation (`archive/LECTURE_YEAR_INVESTIGATION.md`) found 35 lectures showed
    `year=2014` = the Veritas **storefront-listing** date, not their recording
    date. For the On-the-Road talks the Audible ©year is the reliable recording
    year, and it **varies (©2003–2005)**, not a uniform 2003. Corrected the 8
    verified talks to their true recording years and **cleared their wrong
    listing months** (year-only): ©2003 Compassion / God Is the Infinite Field /
    Power of Devotion / You Are the Light; ©2004 All Is Divinity / Spiritual
    Reality / Virtues; ©2005 The Prevailing Silence. Mechanism:
    `backfill_months_from_official_source` now fills a lecture month from the
    product date **only when the product's year matches the record's year** (a
    2014 listing month can no longer leak into a 2003-2005 record); recording
    months known from titles were set in the reviewed inputs (Become That Which
    You Are = June, Love is a Way of Being = January, Unity Church March/June).
    Side effect: the corrected lectures gain catalogue codes. Extending the
    research to the rest of the batch (same session): **13 On-the-Road talks
    corrected** (©2003–2005) and the **16 Office Series talks corrected to
    1982** (the owner pointed out Hawkins died in 2012; the Office-Visit CDs
    were released 1982 — Worry/Fear/Anxiety Jul 1982, A Map of Consciousness
    Dec 1982, Sexuality Apr 1982 — so 1982 is the recording year, not the 2014
    storefront re-listing). **4 talks stay flagged** (Verification of Spiritual
    Realities 230–232, God is Hidden 268, Peace 357, Don't Set Sail 356)
    pending their © years. Catalogue codes **236 → 265**.
    Tests 101 → **102** (new backfill-guard regression test), 92% coverage, all
    5 checks green.

24. **Post-2012 audit (2026-08-04, owner request):** checked every record
    with a year after 2012 (the year Hawkins died). Books are fine (their year
    is the posthumous publication year), but lectures/discussions are
    recordings from his lifetime, so a year > 2012 is a release date, not a
    recording year. Corrected the **5 Discussion Series talks to 2012** (their
    product titles say "(2012)") and **Transcending the Ego to 2004** (Audible
    ©2004). **The Essence of Letting Go (2025) is genuinely posthumous** (a Hay
    House audio compilation) and stays 2025. **7 lecture records remain
    flagged** with release-date years > 2012 pending their recording years:
    Spiritual Will (228–229), Progressive Levels of Consciousness (309),
    Verification of Spiritual Realities (230–232), God is Hidden (268), Don't
    Set Sail (356), Peace is the Natural State (357). Catalogue codes
    **265 → 271**. Tests 102, 92% coverage, all 5 checks green.

25. **Format vocabulary: `audio` → `audiobook` (2026-08-04, owner decision):**
    per the readability roadmap decisions, `format` now uses a small closed
    vocabulary `{DVD, CD, book, audiobook, streaming}` — the 24 `audio` format
    values were renamed `audiobook` (across the master, edition candidates/
    promotions, a manual candidate, and the Audible-candidate rendering).
    `EDITION_FORMATS` / `MANUAL_CANDIDATE_FORMATS` and `infer_format` updated.
    Note `audio`/`video` remain **retired as item_type** (unchanged), and the
    `audio` **edition_role** value is unchanged. Tests 102, 92% coverage, all 5
    checks green.

26. **Title hygiene (2026-08-04, owner decision 3):** public lecture titles
    are cleaned **only where the stripped form matches the official Veritas
    listing title** (`apply_official_title_cleanup` + `_strip_title_part_noise`).
    Removed trailing `PART1`/`(Part 1)`/`DVD0x`/`-converted`/`.mp4` noise from
    **13 lecture titles** (Volume II/III/V parts, Presence of Spiritual
    Awareness, Verification of Spiritual Realities) — accepted only when the
    normalized cleaned title equals the normalized official inventory title,
    never a guess. Raw text stays in `legacy_title`; `title_source` records the
    official listing. Synced the 5 stale `matched_master_titles` rows in the
    Veritas inventory. Tests 102 → **103** (title-cleanup regression guard),
    92% coverage, all 5 checks green.

---

## 2026-08-04 Final Audit (arena/019fcddb-docsheet, same as main)

- Full integrity audit re-executed: all 5 --check modes pass (fetch_veritas offline expected), 103/103 tests, 92% coverage, JS syntax OK.
- Counts confirmed: master 356 (307 lecture/38 book/10 discussion/1 untyped), catalogue codes 271, exclusions 68, overrides 110, relationships rendered 333 (325 derived primary + 8 related_material hand-maintained), veritas 191, everything 376, taxonomy 169/0/10, work families 332.
- CSP hash verified correct `sha256-u2/...`, SRI pinned, no innerHTML injection, LF line endings.
- New finding: 11 lecture audiobook edition rows (UUIDs 333-343) have blank year (proposed_year empty in edition_candidates.csv) — suggestion: inherit year from matched master.
- Reports: `archive/FULL_STACK_AUDIT_2026-08-04_FINAL.md` (this audit) + earlier `archive/AUDIT_REPORT_2026-08-04.md`.
- Proposed: `FILENAME_SCHEME_PROPOSAL.md` — year-first human filename scheme (`2004-02 TM - Thought and Ideation [DVD01].mp4`) with three profiles (canonical/human/plex) + organizer script roadmap.

---

# Archived 2026-08-07–08 session logs (moved from NEXT_AGENT_HANDOFF on 2026-08-09 hygiene, arena/019fe620-docsheet)

## 2026-08-07 Post-PR #27 Audit (arena/019fdd68-docsheet)

- Full re-verification green: 5 `--check` modes, **107/107 tests**, coverage **91%** (`build_catalogue_pages.py` at **88%** — the "every module ≥ 89%" claim in README/INSTRUCTIONS/this file was stale; corrected to ≥ 88%), JS syntax OK. Live site serves 366 masters / 0 candidates.
- **F1 (fixed here): CI red on `main` since the PR #27 merge** (run `31202697657`) — `tests/csv-export.spec.js` "Everything view separates curated master records from candidates" still required `option[value="candidate_veritas"]`; with 0 candidates `configureReviewFilter()` hides the toolbar by design. Spec rewritten data-driven (derives record-type set from `master.json`; asserts the filter UI when candidates exist, the hidden toolbar + bare `Showing: N` status when all-master). Chromium is CI-only, so watch the PR's "Run browser smoke tests" step.
- **F2 (fixed here):** README/INSTRUCTIONS drift — 103 → **107 tests**, 92% → **91%** coverage.
- Notes: international discovery queue is **36 rows** (7 publisher + 19 ES / 6 FR / 4 PT unreviewed), not 19 as the post-PR #26 audit said; masters with `reference_url_1` now **63** (promotions grew it); PR #24's merge also had a red CI run (generated-output drift, already fixed via PR #25).
- Report: `archive/TEMP_RESPONSE_AUDIT_2026-08-07_POST_PR27.md`.

### Distributor title alignment (same branch, owner directive)

- **60 master titles aligned to official distributor naming** (directive: "fix titles per official naming; make everything correct"), every one live-verified: full Veritas WP-API re-fetch (191 products), 5 slug re-queries, live Nightingale-Conant author page; Hay House/Audible from committed reviewed inventories; Amazon via approved override evidence. Report + full change table + rules (R1–R5): `archive/TEMP_RESPONSE_TITLE_AUDIT_2026-08-07.md`.
- Inputs edited, outputs regenerated (never hand-edited): ledger `proposed_title` on 54 rows (+ part designators preserved in `format_detail`: `Part 1/2/3`, `PART1`, `A-01…B-06`), 1 edition candidate (341 → official `Perception vs. Essence`), 2 manual candidates (312/313 drop `(2012)` per R2), filename proposal re-synced on 57 rows, inventory + mapping-decision title mirrors re-synced (`; `-joined `matched_master_uuids`, `| `-joined titles — don't split on the wrong separator).
- **50491 re-linked:** product 50491 (*How to Live Your Life Like A Prayer (2012)*) was title-matched to master 121 (name collision with the Nov-2006 lecture); it is master 278's own listing → approved override on ledger raw 315, inventory primary matches **180**, stale `rel-veritas-50491-121` removed (related_material **7**), taxonomy queue conflict rows dropped **6 → 4**. Relationships: **343 = 336 derived primary + 7 related** (docs/tests updated).
- Store titles **renamed upstream**: 225 → `Devotion to Truth Talk`, 228/229 → `Spiritual Will Inspiring Q & A`, 226/227 → `Mind, Heart and Service: The Pathway of Devotional Non-Duality`; Volumes I/IV official names include `Muscle Testing` / `Consciousness:` subtitles — the test guard `test_volume_series_filename_groups_match_volume_titles` now encodes those.
- All 5 `--check` modes + 107/107 tests + `node --check` green after every batch.

### Hay House inventory fill + wrong-link removal (same branch, owner pick)

- **5 reviewed rows added** to `data/hayhouse_official_products.csv` (24 → **29**) for masters 303/305/307/308/319, every one live-fetched from hayhouse.com (short main-title convention; HH subtitles + ISBN/pub-date in `review_notes`).
- **Defect removed:** master 315's `source_url_hay_house` override (`power-of-love-hardcover`, approved 2026-08-03 off a bad `web_search`) points to **James Van Praagh's** *The Power of Love: Connecting to the Oneness* — a different author's book. Hay House carries no Hawkins edition at that slug (16-item live author-catalog scan checked). Override row deleted (overrides **133**; master hay_house URLs 28 → **27**); git history preserves the original ruling.
- Counts after both today's batches: master 366, relationships **343 = 336 derived + 7 related**, overrides **133**, HH inventory **29**; all checks + 107 tests green.
- **v4 filename rule amendment (same branch, owner pick):** `/` now maps to `-` in proposed filenames (was stripped) → masters 199–201 are `2011-01 - Question-Answer Session.mp4` etc. Rule line updated in `FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md`; the volume-filename test's sanitize helper mirrors the amended rule.

### Duplicate ruling EXECUTED: master 309 merged into 221 (product 53277, owner ruling 2026-08-07)

- Evidence + outcome memo: `archive/RULING_PREP_PROGRESSIVE_LEVELS_309_221.md`. Veritas product 53277's own description names **Oxford, England** — the same talk as raw-derived master **221**; minted master **309** (from candidate `manual-veritas-53277`) was a duplicate with the storefront year 2023.
- **Option A executed:** candidate un-minted (promotion-registry + candidate rows deleted; provenance in git history + memo — same pattern as the wrong-override deletion), 309's work-family/filename/year-provenance rows removed, approved override on raw 245 moved the product URL onto 221 (streaming overlay then auto-adds its `reference_url_1`), inventory + series-taxonomy mirrors retargeted 53277 → 221.
- Result at that point: master **365** (309 lecture), promoted candidates **39**, overrides **134** (now **131** after the 2026-08-08 raw Advaita URL fix retired three redundant overlays), relationships **343** (derived primary moved 309 → 221), work families **208 works / 341 members**; all 5 `--check` + 107 tests + doc-parity green.

### Hygiene batch 1 EXECUTED (owner picks A+B from `archive/TEMP_RESPONSE_HYGIENE_2026-08-07.md`, 2026-08-07)

- **A — root-doc triage:** 9 completed/executed docs moved to `archive/` (Title/Item-Type proposals, Ruling-Prep memo, FULL_STACK_AUDIT_2026-08-04_FINAL_358_V2, Lecture-Year investigation, Veritas artifact+mapping reviews, Official-Catalogue discovery, Pages deployment analysis); every cross-reference in README/handoff/EDITION_MODEL/decisions/ fixed, stale root refs (`FULL_STACK_AUDIT_2026-08-03.md`, `…2026-08-04_FINAL.md`, `AUDIT_REPORT_2026-08-04.md`) pointed at archive. Root: 27 → 18 Markdown files.
- **B — year mirror retired:** `data/year_provenance.csv` deleted (consumed by no script; had already drifted 358-vs-368); `YEAR_COLUMN_PROVENANCE.md` rewritten as policy + audit notes pointing at the master's authoritative `year_source` column.
- **F — withdrawn (premise corrected in the report):** the taxonomy "queue" is *generated* from `series_category_mapping.csv` by `map_series_taxonomy.py` and all 4 rows are already ruled — a derived attention-view with 0 pending conflicts, not a second register. No change made.
- Batches 2 (coverage-gate raise + handoff checkpoint) and 3 (derivable-mirrors tool) proposed, awaiting owner pick.

### Hygiene batch 2 EXECUTED (owner pick, 2026-08-07)

- **C — coverage gate:** `.coveragerc` `fail_under` 80 → **85** (actual 91% total, floor module 88%); README/INSTRUCTIONS floor mentions updated.
- **D — handoff checkpoint:** §4's 2026-08-03 chronicle (~315 lines) + the 2026-08-04 final-audit notes moved to `archive/HANDOFF_HISTORY.md`; handoff 572 → 258 lines; section numbers kept (§4 is now an archive pointer; §3/§4 heading shape preserved for the doc-parity tests).

### Hygiene batch 3 EXECUTED: derivable inventory mirrors (owner pick, 2026-08-07)

- **New tool `sync_inventory_mirrors.py`** (~170 lines, 96% covered, 4 fixture tests — suite **107 → 111**): re-derives the Veritas inventory's mirror columns from the master — `matched_master_uuids` for `matched_by_primary_source` rows (authoritative = master `source_url_veritas`, same join as `derive_primary_relationships`), `matched_master_titles` (` | `-joined), and `normalized_title_match_count` (`; `-joined ID count) for every row. Reviewed columns (`mapping_status`, `review_notes`, non-primary associations) are never touched. It **refuses to write** on violations (unknown IDs; primary status with no URL on any master) or on **URL-evidence contradictions** of reviewed non-primary cells (owner-ruling territory). Run it after changing master titles/URLs; documented in INSTRUCTIONS + §2 (its `--check` intentionally exits 1 on the 2 known contradictions below until ruled; a committed-state-clean test + CI wiring — owner permission needed for CI — follow the ruling).
- **First-run harvest — 2 mechanical drifts fixed** (stale since the title-alignment session; tax/JSON mirrors regenerated): product 55473 cell `311` → **`225; 311`**; product 54219 cell `310` → **`226; 227; 310`**. The derived relationships already pointed this way; only mirrors were stale.
- **2 contradictions RESOLVED (owner ruling: flip both, 2026-08-07):** products **50411**/**1542** are now plain `matched_by_primary_source` to masters **286**/**331**; their 2026-08-03 decision-overlay rows were **removed** (primary matches need no overlay row; the decisions vocabulary only covers non-primary outcomes — provenance in git history, decisions 12 → **10**). Master 202 keeps both products as `related_material`. Taxonomy: 50411 approved R4 no-op under the 2026-08-04 delegation, 1542 stays R7-rejected (Media Miscellaneous store category must not re-series 331's Books series); the 202 series conflict dissolved (queue 4 → **1**, only 50521 R3 remains); statuses 176/10 → **177 approved / 9 rejected**. New committed-state guard test locks `--check` clean.
- Also fixed in passing: handoff §2 quick-verify block was stale (103 tests/gate 80/92% → 111 tests/gate 85/91%).

### Empty-column ruling + schema redundancy execution (owner rulings, 2026-08-07)

- **4 always-empty columns dropped** (`location_physical`, `location_digital`, `location_streaming`, `reference_url_2`) — owner ruling; memo `archive/RULING_PREP_EMPTY_COLUMNS.md`. Master schema 29 → 25.
- **Redundancy review approved 3/3** (`archive/SCHEMA_REDUNDANCY_REVIEW.md`, passes 1+2): `title_source` dropped (259/265 duplicated `legacy_title`; the 6 unique "Official listing" evidence values now live in `notes` as "Title cleaned against official listing: X"; fetcher date extraction switched to `legacy_title`, provably behavior-neutral); `docs/meta.json` stopped (nothing but `process_data.py`'s self-check had ever read it; footer uses HTTP `Last-Modified`); Original view trims 5 always-empty raw columns (13 → 8; raw CSV untouched). Master schema now **24 columns**.
- Suite 112 → **110 tests** (2 meta-specific failure-path tests retired); all 6 `--check` + node green; review sheets otherwise adjudicated keep (verbatim raw mirrors, invariant vocabulary, intake lanes).

### Filename proposal v4.1: collision fix + global uniqueness guard (owner directive 6-part, item 6; 2026-08-07)

- **Defect found in the naming-consistency pass:** master **225** (raw owned streaming row) and master **311** (promoted DVD/product row) both generate `2003 - Devotion to Truth Talk.mp4` — the *same talk* carried on two media, neither part-indexed, so the per-group rules could not separate them. (Contrast the `226;227;310` family: its raw parts carry `[1-2]`/`[2-2]` part brackets, so no collision there.)
- **v4.1 carrier-suffix rule:** when the same proposed filename would serve two master rows with different carriers, append ` (DVD)` / ` (streaming)` after the title and before the extension: 225 = `2003 - Devotion to Truth Talk (streaming).mp4`, 311 = `2003 - Devotion to Truth Talk (DVD).mp4`.
- **New guard in `validate_filename_proposal_groups`:** *global* uniqueness of `proposed_filename` and `proposed_filename_display` (not just within work families) — a ValueError citing the v4.1 rule fails the build on any seeded duplicate. 2 new tests (`test_filename_proposal_filenames_are_globally_unique`, `test_filename_uniqueness_guard_fails_on_seeded_duplicate`), suite 110 → **112**.
- Filename sheet: **365 rows = 365 unique safe = 365 unique display**; `FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md` carries the v4.1 amendment. All 6 `--check` + 112 tests + node green.

### Owner 6-part directive EXECUTED (documentation, re-audit, hygiene, UX, mobile, naming — 2026-08-07 PM)

1. **Docs updated + project re-audited:** `archive/FULL_STACK_AUDIT_2026-08-07_DEEP.md` got a PM refresh — exec summary, repo layout, *Current Verified State* table, pipeline deep-dive (all module line/stmt/coverage numbers; `sync_inventory_mirrors.py` added) and reproduction commands re-executed live, plus a PM Session Changelog section itemizing all 8 same-day rulings. Handoff stale bits fixed (meta.json removed from generator table, 112 tests, codes 281).
2. **Hygiene leftovers:** README now documents the two intentionally-empty sheets (Official Discovery, New Work Review) as standing **intake lanes**; CI **item K** documented — Node 20 EOL 2026-04, owner must bump the workflow to 22 (app can't push `.github/workflows/*`).
3. **Visitor-first UX:** Everything view reordered to product facts first (Title · Series · Item Type · Edition · Year-Month · Catalogue Code · Owned · Veritas/Hay House/Audible/Amazon/Nightingale-Conant links · Streaming · Notes); technical columns (uuid, work_id, legacy_tempid, proposed_filename(_display), year_source, raw_row_number, legacy_title) hidden behind a persisted **Expert columns** toggle; friendly labels (`Veritas (Official Store)`, `Streaming`) and linkified cells (`Amazon page`, `Streaming link`); view description rewritten.
4. **Mobile:** dense cells (13px, 5×8 padding), full-width row-details sheet with 44px close target, touch-height scrolling tabs, stacked view-tools; expert toggle flex-fills.
5. **Naming scheme:** filename v4.1 (earlier this session) — carrier suffix + global-uniqueness guard, 365 unique safe = 365 unique display.
6. **Specs:** Playwright specs enable Expert columns before asserting technical columns; new `column-layout` spec locks the visitor-first default. CI note: watch the "Run browser smoke tests" step after merge (Chromium is CI-only here).

## 2026-08-08 Session (arena/019fe098-docsheet → PR #30, MERGED)

Full-stack audit + deep QA + site redesign day. Report:
`archive/FULL_STACK_AUDIT_2026-08-08.md` (sections 1–14); memos in `archive/`.

- **Audit re-verified everything** (112 tests at start, 6 `--check` green,
  90% coverage, counts vs `docs/catalogue-meta.json`) and found 5 catalogue
  inconsistencies + 4 setup drifts (C1–C5, S1–S5).
- **Rulings executed (owner-approved, applied this session):**
  - C1/C2 master 265: publisher-verbatim URL kept + documented (live WP-API
    evidence; product 1552, no clean slug exists); `format` corrected
    `audiobook → CD` (`three CD; 2h56m`) via ledger 297 + filename proposal
    `.m4b → .mp3`; format-inference rule hardened + 2 tests; de-listed US
    Audible audiobook (B00KZ1QMX8) → manual lead. Memo:
    `archive/RULING_PREP_MASTER_265_GOLDEN_WORD_BOOK_SIGNING.md`.
  - C3 198X: kept (evidence-backed decade estimate); README documents the
    convention; site renders `c. 1980s` with a deterministic string sorter.
    Memo: `archive/RULING_PREP_YEAR_198X_OFFICE_SERIES.md`.
  - C4 `owned`: vocabulary documented (true/false/blank=not stated); badges
    read `Owned`/`Not owned`.
  - DP-1/2/3 work-family merge: 11 multi-part lecture groups (27 rows)
    consolidated into 11 works (208 → **193**); master 202 removed from
    `w-power-vs-force` (book work keeps 286); 26 PART-marker canonicals
    cleaned; filename-proposal work_ids re-synced. Memo:
    `archive/RULING_PREP_WORK_FAMILY_PART_MERGE.md`.
  - QA-5: `legacy_title` + `proposed_filename_display` restored to the
    published Everything view (`EVERYTHING_FIELDS` + derived display from the
    filename sheet); new schema-contract test locks the keys (suite **115**).
- **Doc/setup:** S1/S3/S4 drifts fixed; S2 Node 20→22 applied by owner on
  `main` (`406116f`); S-a/S-b/S-c quick wins; S-g year research (no
  authoritative dates for masters 230–232/268 — keep "under investigation").
- **Deep QA pass:** QA-2 relationships/mirrors clean; QA-3 refs/JSON schema
  clean (3 broken archive links fixed); QA-4 Satsang parity clean (code-order
  caveat documented); QA-5 (above); QA-6 editions/URLs/vocabulary clean;
  QA-7 final gate — full pipeline re-run produces zero diffs.
- **Site redesign Phases 1–3 applied** (owner UX brief): tab groups
  (Catalogue / Review workspace / Sources), stats strip from
  `catalogue-meta.json`, empty-state cards, a11y (roving tabs, focus rings,
  reduced motion, link aria-labels, 44px mobile targets), theme (gradient
  header, green hover/selection, themed scrollbars, footer repo link).
  Proposal: `archive/SITE_UX_REDESIGN_PROPOSAL_2026-08-08.md`.
- **CI:** green on every commit (Python checks, 115 tests, 90% coverage against the 85% gate,
  JS syntax, 9-test Playwright suite).
- **Owner actions still open:** optionally supply recording dates for masters
  230–232/268 if known; C5 raw-CSV hygiene is now applied in the follow-up
  session below.



- Keep docs accurate with each push (counts live in `docs/catalogue-meta.json`;
  cite those numbers — do not hand-count).
- Present long results via a committed Markdown report
  (`archive/TEMP_RESPONSE_AUDIT_2026-08-03.md` is the 2026-08-03 log;
  `archive/FULL_STACK_AUDIT_2026-08-07_DEEP.md` is the current full-project audit); the
  chat should stay a one-sentence summary plus the `ask_user` question for
  what is next.
- Update this handoff at the end of each session so the next agent inherits
  your context verbatim.

## 2026-08-08 Follow-up Session (arena/019fe0ef-docsheet)

Requested by owner after the audit: "start fixing everything", then "redo the whole page, minimalistic, with extra settings to expand everything," then update docs / push / PR / merge.

- **Catalogue consistency fixed:** work-family rows 225/311 (`Devotion to Truth Talk`) now share `w-devotion-to-truth-talk`; rows 226/227/310 (`Mind, Heart and Service`) now share `w-mind-heart-and-service`; guard added so same Veritas URL + normalized title + type + series + year cannot split across work IDs again.
- **Streaming-reference ruling applied:** raw streaming-only rows can stand as `format=streaming`; DVD/CD rows keep their carrier and put streaming availability in `reference_url_1`. Manual candidates 54219/55473 now declare `proposed_format=DVD`, blank `format_detail`; generated masters 310/311 no longer say `DVD · streaming video`.
- **Filename proposal guard:** `validate_filename_proposal_mirrors()` now checks proposal metadata mirrors against the final master when the full proposal set is present; fixed stale mirrors for UUID 221 (format), 225/310 (work_id), and title-month-backed Unity Church rows 354/355 (month 03/06 via `month_from_title`).
- **Series taxonomy queue clarified:** `map_series_taxonomy.py` no longer emits already-reviewed approved/rejected conflicts into `data/series_taxonomy_review_queue.csv`; current queue = 0.
- **Official inventory tabs exposed:** Veritas Products, Hay House Products, Audible Products, and Filename Proposal are now first-class Pages tabs; Review Overview includes them.
- **Raw CSV hygiene applied end-to-end:** fixed 3 Advaita raw product URLs, cleared 13 `2cds each?` tempids, updated `migration_review_ledger.csv`, regenerated `docs/data.json`, blanked masters 251–263 `legacy_tempid`, and retired three now-redundant Advaita source overrides (approved overrides 134 → 131).
- **Minimalist UI pass:** neutral table-first theme in `docs/style.css`; `View settings` menu in `docs/index.html`/`docs/app.js`; settings persist in `localStorage`; controls include Wrap long cell text, Compact rows, Show summary cards, Reset current view, and **Expand everything** (all columns + Expert columns + wrapped roomy rows).
- **Setup/docs fixes:** CSP inline-script hash updated, export/read-only docs corrected, local JS syntax verification now covers every `tests/*.spec.js` (workflow edit requires GitHub App workflow permission and was not included in the pushed commit), direct-file unittest ordering fixed, vacuous edition UUID stability test fixed, current coverage docs updated to 90%.
- **Verification:** `process_data.py --check`, `build_research_master.py --check`, `build_catalogue_pages.py --check`, `reconcile_research_master.py --check`, `map_series_taxonomy.py --check`, `sync_inventory_mirrors.py --check`, `python -m unittest discover tests` (115), `coverage report` (90%, gate 85), and all node syntax checks pass locally. Local Playwright browser execution remains blocked by sandbox Chromium download/TLS issues; CI should run the 9 browser tests.

## 2026-08-08 Session 2 (arena/019fe11d-docsheet)

Independent full-stack audit + catalogue fix + UX rework. Report:
`archive/FULL_STACK_AUDIT_2026-08-08_INDEPENDENT.md`; UX backlog:
`UX_REWORK_SUGGESTIONS.md`; web-editor workflow guide:
`WORKFLOW_WEB_EDITOR_GUIDE.md`.

- **Audit (all checks re-run live):** six `--check` modes, 115/115 tests, 90%
  coverage, JS syntax green; independent cross-field sweeps over every
  CSV/JSON and the living docs.
- **D-1 stale Veritas decision 50491 (FIXED):** `data/veritas_mapping_decisions.csv`
  still had `50491, matched_by_title, 121` while the inventory, master, and
  Product Relationships sheet correctly treat 50491 as the **primary source of
  master 278**. `apply_mapping_decisions()` overrides deterministic matching,
  so the stale row would (a) make the Veritas Decisions sheet tell reviewers
  the wrong master and (b) cause `fetch_veritas_catalogue.py --check` / the
  Map Veritas workflow to report a false diff. Removed the row (overlay
  10→9); regenerated `docs/veritas-mapping-decisions.json`,
  `docs/review-overview.json`, `docs/catalogue-meta.json`. Verified the
  deterministic overlay now matches the committed inventory with 0 mismatches.
- **D-2 decisions doc updated:** `decisions/VERITAS_MAPPING_DECISIONS.md`
  "Current seed" rewritten from stale "18" to 9 (5 excluded + 4 non-primary)
  with the 2026-08-07 Highlights lift, 50411/1542 removal, and this 50491 fix.
- **D-3 handoff drift:** "all 15 tabs" → "all 19 tabs" backlog bullet; Veritas
  decision count in §3 updated 10→9.
- **D-4 CI coverage of both specs:** owner applied the `for spec in
  tests/*.spec.js` JS-syntax block in the web editor (documented applied in
  `WORKFLOW_WEB_EDITOR_GUIDE.md` / `archive/UNBLOCK_INSTRUCTIONS.md`). The
  Arena app can't push `.github/workflows/*`.
- **D-5 catalogue-code rule:** README field semantics now state codes are
  assigned to lecture/discussion rows with a verified year at minting time,
  so pre-2000 blank/198X rows and blank-`proposed_year` candidates/editions
  correctly carry no code (281 total); codes are never retrofitted.
- **Filename-first UI (owner directive):** `proposed_filename` moved out of
  the Expert-hidden list to a visible, **frozen** column immediately after
  `record_type`; `proposed_filename_display` stays Expert-only. Record-type
  badges now read **CM** (compact); the full "Curated master" phrase remains
  in the tooltip, column header, review-filter option, and active-filter chip.
- **Full UX rework (P0–P3, no data changes):** faceted multi-select filter
  bar on Everything (Series/Year/Type/Format/Owned) with per-value counts,
  removable chips, and `localStorage` persistence per view; stats chips are
  now buttons that jump to their sheets; shorter tab labels (Candidates,
  Exclusions, Decisions, Compilations, Publishers — full names stay in the
  Review Overview data and export filenames); monospace Proposed File Name
  with a muted `.mp4`/`.mp3`/`.m4b` extension suffix; carrier-color dots in
  the Edition column (DVD/CD/audiobook/streaming/book, AA dark-mode); a
  "Copy file name" button in the row-details drawer; work-group row striping
  (left accent on the first row of each consecutive `work_id` run); per-view
  persistence of sort + horizontal scroll; keyboard shortcuts (`/` search,
  `j`/`k` move rows + open details, `y` copy filename, `?` shortcuts overlay,
  ignored while typing). CSS for all of the above + mobile wrapping.
- **Tests:** new `tests/ux-enhancements.spec.js` (7 browser tests) covering
  facet narrowing/removal, facet-bar visibility, stats navigation, the CM
  tooltip, the muted filename extension, and `/`. Existing
  `column-layout.spec.js` / `csv-export.spec.js` updated for the
  proposed_filename-default and CM-badge changes. Python suite is now 117;
  browser suite is now 16 tests (3 spec files) — CI runs them.
- **Verification:** all six `--check` modes, 115/115 Python tests, 90%
  coverage, `node --check` on app.js + all 3 specs, and `py_compile *.py`
  pass locally. The local Playwright run is blocked by the sandbox Chromium
  download; CI must run the 16 browser tests.
- **Open / future (see `UX_REWORK_SUGGESTIONS.md`):** a "Needs your decision"
  cross-sheet inbox was proposed but skipped while all queues are 0 (it would
  be empty today); nested column groups and a review-lanes dropdown are
  documented P1–P2 options. The 198X Office Series convention and the 4
  "under investigation" years remain owner-ruled as-is.

## 2026-08-08 Guard follow-up (current)

- **F-03/F-04 implemented:** Pages build now fails offline when a populated
  master Veritas URL is absent from the reviewed inventory or when a mapping
  decision disagrees with the committed inventory/master evidence.
- **Four additional stale overlays corrected:** products 53062, 50398, 50378,
  and 50432 were marked non-primary despite being exact primary URLs of masters
  300, 289, 291, and 247. The rows were removed, inventory statuses restored
  to `matched_by_primary_source`, and the decision overlay is now 5 excluded
  products only. Book/edition and map-poster decision docs were updated.
- **Regression coverage:** the preceding guard checkpoint reached 123 tests, 91% total coverage (lowest
  module 88%), all six `--check` modes and the Node syntax checks pass. The
  decision guard includes committed-state, malformed-overlay, and exact-primary
  URL fixtures; source fallback fixtures cover unrelated and ambiguous CSVs.
- **CI hardening owner-applied:** `process_data.py` requires the raw header shape
  and fails on ambiguous fallback files; `requirements-ci.txt` pins the tested
  Python set; main now has the raw-only trigger, constraint install wiring, and
  Node-24-compatible action majors. `requirements-ci.txt` is now on `main`
  through merged PR #34; main CI run `31265148365` passed after the merge.
- **Remaining audit work:** optional local frontend asset fallback (F-08) and
  repository housekeeping.

## 2026-08-08 Audit-policy and documentation follow-up (current)

Owner selected both audit policy recommendations and documentation/governance
cleanup after reviewing the fresh checkpoint in
`FULL_STACK_AUDIT_2026-08-08_ARENA.md` §12.

- **Edition column standardized:** all `format_detail` values normalized to `Part 1`/`Part 2`/`Part 3` format (was `DVD01`/`DVD02`/`DVD03` and `PART1`/`PART2`/`PART3`); 19 redundant `Audiobook` values cleared; 223 rows standardized. Documentation updated across CATALOGUE_READABILITY_ROADMAP.md, LECTURE_SERIES_REVIEW.md, PRODUCT_RELATIONSHIP_SCHEMA.md, SERIES_COMPILATION_SCHEMA.md, decisions/FINAL_TITLE_MATCH_DECISIONS.md, decisions/RECONCILIATION_DECISIONS.md. Tests updated.
- **Same-carrier filename rule clarified:** masters 320/331 now use
  `1995 - Power vs. Force (Audible).m4b` and
  `1995 - Power vs. Force (Veritas).m4b`. The generic audiobook label remains
  removed; a publisher suffix is the reviewed exception only when same-work,
  same-year, same-carrier editions would otherwise collide. Their proposal
  `clean_title` is `Power vs. Force`, with no artificial part indexes.
- **Regression coverage:** two deterministic guards lock the six part details
  and the two publisher-suffixed filenames. Suite: **125 tests**.
- **Documentation governance applied:** corrected the active v4 filename
  samples/rules (including `198X` Office Series), updated year provenance to
  distinguish the four edition-release backfills (327–330) from lecture
  recording dates, corrected the workflow guide's stale `setup-node@v4` /
  "both specs" references, and labelled the older 2026-08-08 audit narrative
  historical. The current Arena audit was cleaned of corrupted trailing text.
- **Still open implementation work:** frontend stale-fetch/race hardening,
  keyboard-accessible row-detail source links, confirmation of `main` branch
  protection/required checks, issue #18 triage, and optional local Tabulator
  fallback. These are documented in the current Arena audit rather than fixed
  in this data/documentation follow-up.

## 2026-08-08 Mobile Browse mode (current)

Owner requested a phone-first catalogue experience rather than forcing the
spreadsheet grid into a narrow viewport. The Everything view now defaults to
**Browse mode** at `max-width: 720px`:

- Groups the 362 master rows into compact `work_id` stacks; expand a stack to
  inspect its editions/parts, use **Source** / **Stream** quick links, or open
  the existing full detail drawer.
- Keeps filtering/search state and the whole-view CSV export working from card
  mode; cards are a client-side presentation of the existing `master.json`, not
  a second data source.
- Provides a persistent **Spreadsheet** / **Browse cards** switch. The full
  Tabulator grid remains available for expert comparison and the browser stores
  that preference. Resizing back to desktop restores the normal grid.
- Adds a Playwright mobile-viewport regression test for default work stacks,
  Source CTA, and the Spreadsheet escape hatch. Browser suite: **17 tests**
  across 3 specs (local Chromium download remains sandbox-blocked; CI must run
  it).

A local visual review can be served with `python -m http.server 8000 --bind
0.0.0.0`. Remaining frontend audit items are the stale-fetch response guard and
row-detail keyboard focus trap.

## 2026-08-08 Frontend correctness + accessibility hardening (current)

Owner selected the remaining P0 frontend audit work after Mobile Browse mode.

- **Race-safe tab loading:** `activateView()` now aborts the preceding fetch and
  uses a monotonic activation token. `loadData()` no longer writes global UI
  state itself; only the still-current activation commits rows, timestamp, and
  footer metadata. A delayed `manual-leads.json` Playwright route proves an old
  response cannot replace the newly selected Everything view.
- **Accessible detail-modal links:** the focus trap now cycles every visible
  focusable descendant, including official/evidence links in the drawer body,
  rather than only the three header controls. The browser test asserts Tab
  reaches the first source link after Copy filename, Copy ID, and Close.
- **Browser coverage:** 2 further Playwright tests added; browser suite is now
  **18 tests across 3 specs**. Local browser download is sandbox-blocked, so
  rely on PR CI for Chromium execution.

## 2026-08-08 Mobile discovery shelves (current)

Owner selected the next mobile iteration: a browseable series/timeline layer on
top of work stacks.

- Browse mode now renders horizontal **Series** and **Timeline** rails above
  the cards. Each chip shows a count and writes to the same persisted
  `activeFacets` state used by the existing desktop filter panel; card results,
  active-filter chips, clear controls, and status counts stay in sync.
- The rails intentionally preserve multi-select behavior (tap another chip to
  add it; tap an active chip or the rail's All option to remove it) while
  avoiding a phone-hostile `<select multiple>` as the primary discovery UI.
- The Mobile Browse Playwright scenario now verifies a Satsang shelf filter
  produces `Showing: 25 of 365` and clears back to the complete catalogue.

## 2026-08-08 Arena fresh-eyes audit + owner-approved fixes (PR #37, current)

Branch `arena/019fe244-docsheet`. Independent full-stack audit
(`FULL_STACK_AUDIT_2026-08-08_ARENA_FRESH_EYES.md`) plus all owner-approved
resolutions, delivered as PR #37 (CI green, merged).

- **Fresh-eyes audit:** all six `--check` modes re-run in a clean venv, 125/125
  tests, 91% coverage, plus standalone pandas probes (bypassing the pipeline's
  own validators): raw-row accounting airtight (374 raw → 302 adopted + 72
  excluded), no duplicate uuid/catalog_code/filename, retired vocabulary fully
  purged, CSP + SRI-pinned frontend. **No critical findings** — all drift.
- **D5 (owner ruling):** unofficial archive.org mirror removed from master 94
  `reference_url_1` at the source (raw CSV row 106 + ledger); all artifacts
  regenerated in documented order; raw/ledger diffs = 1 cell each.
- **D4 (owner ruling):** 3 academic-book Amazon links (masters 359–361) moved
  onto the curated `source_url_amazon` column via candidate-keyed approved
  overrides — overrides **131 → 134** (README + this handoff §3/§6 bumped).
- **Doc drift fixed:** README 198X-code clause (16 Office Series rows DO carry
  `LECTURE-198X-001…-016`), `work_id` provenance (approved
  `edition_promotions.csv` for minted editions 320–343), handoff 123 → 125
  tests, record-246/free-text-audio/NC-HayHouse-count stale P-bullets,
  19 sheets + meta (not "20 + meta"), README documents International
  Editions + Publishers sheets, INSTRUCTIONS archive pointer,
  `.coveragerc` eight → ten modules, `[streaming]` log wording, plus a CI
  badge and a uuid-is-a-compact-integer note in the README.
- **Audit noise reduced:** root full-stack audits 6 → 2 (declared-current
  `…_ARENA.md` + the fresh-eyes pass); the 4 superseded ones moved to
  `archive/` via `git mv`; `archive/README.md` stale root pointer repaired;
  all cross-references repathed (two dangling ones were inside the
  declared-current audit itself).
- **Left intentionally:** nothing requiring code/data action. Watch items:
  duplicate URL storage pattern previously seen on 359–361 (`reference_url_1` ==
  curated `source_url_amazon`) was cleared 2026-08-09 (now 0 duplicates; all
  Amazon-only books have blank `reference_url_1`), so no dedupe candidate
  remains; the pattern is now consistent.
