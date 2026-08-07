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
