# Next-Agent Handoff

**Prepared:** 2026-08-07 — latest refresh: full project audit + post-PR #27 review (branch `arena/019fdd68-docsheet`; see `archive/TEMP_RESPONSE_AUDIT_2026-08-07_POST_PR27.md`). **Heads-up:** the PR #27 merge left CI **red on `main`** — the Playwright `csv-export.spec.js` still asserted the candidate review filter exists even though all candidate lanes are now 0; the toolbar is hidden by design when every row is `master`. The spec was made data-driven on this branch; merge its PR to green `main`.
**Earlier same-day:** full-stack audit + post-PR #26 review (branch `arena/019fdd28-docsheet`; see `FULL_STACK_AUDIT_2026-08-07_DEEP.md` and `archive/TEMP_RESPONSE_AUDIT_2026-08-07_POST_PR26.md`).
**Earlier branches:** `arena/019fdcc5-docsheet`, `arena/019fdb8b-docsheet`, `arena/019fc9b5-docsheet`, closed out via PRs #24–#26 (merged to `main`); earlier same-day work landed via PRs #11–#23.

If you are the next agent: **read this file top to bottom before touching
anything.** It is written to give you full context in five minutes.

---

## 1. What this project is

DocSheet is a static GitHub Pages catalogue of David R. Hawkins material:
`_hawkins archive clone - Sheet1.csv_` (374 raw rows) flows through a
hand-maintained `migration_review_ledger.csv` into generators that emit 20
`docs/*.json` sheets rendered by Tabulator (`docs/index.html`, `docs/app.js`).

| Generator | Input → Output (committed artifacts; never hand-edit) |
|---|---|
| `process_data.py` | raw CSV → `docs/data.json`, `docs/meta.json` |
| `build_research_master.py` | raw CSV + ledger + review overlays → `data/research_master_draft.{csv,json}`, `data/research_master_exclusions.csv` |
| `build_catalogue_pages.py` | master + all review CSVs → the 20 `docs/*.json` sheets + `docs/catalogue-meta.json` |
| `map_series_taxonomy.py` | Veritas inventory + mapping review input → `data/series_category_mapping.csv`, `data/series_taxonomy_review_queue.csv` |
| `fetch_veritas_catalogue.py` | live Veritas API (review-only; never auto-commit) → candidate inventory |
| `reconcile_research_master.py` | everything → `RECONCILIATION_REPORT.md` |
| `generate_migration_ledger.py` / `generate_lecture_review.py` | one-off **bootstrap** tools; their outputs are afterwards **hand-maintained** |

## 2. Verify your environment first (60 seconds)

```bash
python -m py_compile *.py
python build_research_master.py --check
python build_catalogue_pages.py --check
python reconcile_research_master.py --check
python map_series_taxonomy.py --check
python process_data.py --check        # if wired into your tooling
python -m unittest discover tests     # 103 tests, offline, ~2s
coverage run -m unittest discover tests && coverage report   # gate: 80%; currently 92%
node --check docs/app.js && node --check tests/csv-export.spec.js
```

Sandbox traps learned the hard way (all still true):

- **pip refuses to install system-wide (PEP 668).** Use a venv:
  `python3 -m venv /tmp/venv && /tmp/venv/bin/pip install -r requirements-dev.txt`
- **veritaspub.com is unreachable from the sandbox** via curl/urllib (TLS EOF)
  but **works via the agent page-fetch tool** with compact `_fields`
  (`/wp-json/wp/v2/product?per_page=100&page=N&_fields=id,date,link,title,product_cat`).
- **The Arena GitHub App cannot push workflow-file changes** (historical: the
  CI workflow was applied to `main` by the owner as commit `6b28e66`, "Add
  verification and testing steps to CI workflow", and its run passed). Any
  future `.github/workflows/*` edit may still be rejected; prepared snippets
  live in `archive/UNBLOCK_INSTRUCTIONS.md` for the owner to apply in the web
  editor.
- **Chromium/Playwright cannot download in the sandbox.** CI runs the browser
  tests (5 specs); don't burn time installing locally.
- Python 3.11 / Node 22 in-sandbox; CI uses 3.12 / Node 20 — keep code compatible.

## 3. Current verified state (committed, checked)

| Layer | Count | Notes |
|---|---:|---|
| Raw rows / ledger rows | 374 / 374 | `hawkins archive clone - Sheet1.csv`, `migration_review_ledger.csv` |
| Curated master | 365 | 309 lecture / 40 book / 8 discussion / 7 highlight / 1 other — **no untyped records** (record 246 ruled 2026-08-07: duplicate of the audio edition already held as master 329, excluded; record 309 ruled 2026-08-07: duplicate of the Oxford talk already held as master 221, un-minted); incl. 24 minted edition rows (320–343) + 9 Satsang monthlies (344–352) + 6 manual candidates (353–358) + 3 academic (359-361) + 7 annual Highlights (362–368, series Lecture Highlights) + The Discovery 369 / Ultimate David Hawkins Library 370 / OM 371 (unique NC+Audible programs) + How to Surrender to God 372 (unique Hay House program, owner rulings 2026-08-07); legacy duplicates 281/284 excluded 2026-08-07 (same 2012 Discussion Series talks as promoted masters 312/313) |
| Everything view | **365** | 365 master + 0 candidate_veritas (Map poster ruled excluded_related_material 2026-08-07) + 0 candidate_pending_promotion + 0 discovery + 0 hayhouse + 0 audible (all review lanes ruled out 2026-08-07) |
| Exclusions / source overrides | 72 / 134 | includes the 4 Nightingale-Conant audio-edition URLs filled 2026-08-04 and the Audible/NC/Hay House URLs of masters 369–372 (109 approved at that time after dedup of the Path duplicate; now 134 incl. the 18 Amazon direct links and the product-53277 link moved from retired duplicate 309 onto master 221, owner ruling 2026-08-07) |
| Veritas inventory | 191 products | categories populated 191/191; 12 approved mapping decisions (7 Highlights suppression rows lifted 2026-08-07; Map poster 1560 ruled excluded_related_material 2026-08-07) |
| Everything relationships | 343 product relationships, 7 series compilations | 336 derived primary + 7 related_material |
| Candidate pool | 39 reviewed manual candidates (all 39 promoted — candidate manual-veritas-53277 un-minted 2026-08-07 as duplicate of master 221 — incl. 9 Satsang monthlies, 6 manual candidates, 3 academic, 7 Highlights, 3 NC/Audible programs, 1 Hay House program, 0 pending), 1 manual lead; 24 edition candidates all promoted | |
| Work families | 208 works / 341 members approved; work_id coverage 365/365 | `data/work_families.csv` |
| Series taxonomy | 186 matched products → **176 approved / 0 proposed / 10 rejected**; all proposals ruled | 3 approvals re-series masters 357 (On The Road Talk Series) + 312/313 (Discussion Series); 7 Highlights → Lecture Highlights (R1, owner ruling 2026-08-07); 7 rejections carry documented rationale |
| Test suite | **107 tests; coverage 91% total, every pipeline module ≥ 88%** (build_catalogue_pages.py = 88%) | `.coveragerc` enforces `fail_under = 85` (raised 2026-08-07) |

All catalogue data was verified against the live Veritas API on 2026-08-03
(see `archive/FULL_STACK_AUDIT_2026-08-03.md` and `archive/AUDIT_2026-08-03_FULL.md`,
`archive/VERITAS_ARTIFACT_REVIEW.md`).

## 4. Session history (archived)

The 2026-08-03 session chronicle (~315 lines) and the 2026-08-04 final-audit
notes moved to `archive/HANDOFF_HISTORY.md` in the 2026-08-07 hygiene
checkpoint. Recent sessions (2026-08-07) stay below, between §6 and §7.

## 5. Binding data rules (violating these has caused real defects)

- **Never hand-edit generated files** — `data/research_master_draft.*`,
  `docs/*.json`, `data/series_category_mapping.csv`/`…review_queue.csv` beyond
  their declared review columns (`review_status`/`reviewed_on`/`review_notes`
  + dominance overrides). Fix the input, regenerate, re-run every `--check`.
- **`migration_review_ledger.csv` and `lecture_series_review.csv` are
  hand-maintained after bootstrap generation.** Regenerating them over the
  committed copies intentionally produces diffs (title fixes, month "08" vs
  ""; that is normal, not damage.
- **`item_type` = what a record IS; `format` = its carrier.** DVD lectures are
  `lecture`+`DVD`. The `audio`/`video` medium values were **retired from the
  `item_type` vocabulary 2026-08-03** — validators reject them; only the
  unreviewed discovery-triage lane (`data/official_discovery_queue.csv`, 4 NC
  rows) still carries free-text `audio` pending an owner ruling.
- **No title-based inference for `series`, and a commercial listing is not
  master identity.** Four records once linked to the wrong edition because of
  title matching.
- **Compact master IDs are stable once issued.**
- **`work_id` comes only from approved `data/work_families.csv` rows.**
  Never infer work identity from titles alone (C2 lesson); `proposed` rows
  are validated but never applied.
- **A book's `year` is its first-publication year, never the storefront
  listing date.** `backfill_months_from_official_source()` skips `book` rows;
  book years come only from the reviewed ledger / candidate `proposed_year`.
  Books never get a catalogue code (codes are lecture/discussion only).
- **Primary product relationships are derived from the master, not stored.**
  `data/product_relationships.csv` holds only non-primary rows
  (`related_material`). A master with a `source_url_veritas` automatically
  gets its primary relationship; never add a `primary_product_for_item_part`
  row to that CSV.
- **A lecture's `month` is never taken from a different-year product listing.**
  `backfill_months_from_official_source` fills a lecture month from the
  product date only when the product's year matches the record's year. If a
  record's recording month is known, set it in the reviewed input
  (`proposed_month`); otherwise leave it blank (year-only).
- **Titles are cleaned only against the official listing.** Public lecture
  titles drop trailing part/disc/transcoding noise only when the stripped form
  matches the official Veritas title; never guess a title. The verbatim raw
  text always stays in `legacy_title`.
- **Relationships stay at the evidence level actually supported** (item-level
  when proven; series-level for annual Highlights).
- **Merchandise (card decks, wall charts) are products, not master records.**

## 6. Open work, prioritized

**P0 — Owner-actions:**

- ✅ **CI is live on `main`** (commit `6b28e66`, "Add verification and testing
  steps to CI workflow"): `py_compile`, `process_data.py --check`,
  `map_series_taxonomy.py --check`, all three generator checks, the unittest
  suite, the 85% coverage gate, JS syntax, and the Playwright browser suite.
  Latest run passed 2026-08-03 (run `30834666253`). Nothing outstanding here.
- ⚠️ **Re-run the Map Veritas Catalogue workflow on `main` after this branch
  merges** — the 2026-08-04 refresh diff was reviewed and accepted (see
  `archive/HANDOFF_HISTORY.md` (2026-08-03 chronicle, item 15) and
  `archive/VERITAS_ARTIFACT_REVIEW.md` Addendum 3), the reviewed
  inventory is LF-normalized like the fetcher output, **and the Veritas 50810
  title drift (`Vol II` → `Volume II`) was reconciled in branch
  `arena/019fcbde-docsheet`**, so the next run should print "Candidate matches
  the reviewed inventory" and pass.

**P1 — Data decisions needing a ruling:**

- **Edition model (owner-directed; see `EDITION_MODEL_PROPOSAL.md`):**
  **fully applied + filename proposal v4 + Volume year strip.** Master **358 rows** (307 lecture / 40 book / 10
  discussion / 1 untyped) incl. 24 minted edition rows (320–343, pinned
  UUIDs in `edition_promotions.csv` — never renumber), 9 promoted
  Satsang monthlies (344–352), 6 promoted manual candidates (353–358) + 3 academic (359-361, Orthomolecular 1973, Qualitative 1998, Dialogues 1998),
  with Path duplicate 302 removed and Volume Series years stripped to blank pre-2000 per owner (catalogue codes 284→271 after the strip; **280** as of the 2026-08-07 year-provenance fixes);
  **201 works / 334 members approved → 209 works / 342 members by
  2026-08-07 (281/284 excluded as duplicates of 312/313; +7 Highlights;
  +3 NC/Audible programs 369–371), work_id coverage 366/366**
  (D6a per-part ruling + C1 split applied + academic families + Volume canonical mapping);
  overrides 127 (candidate-provenance supported, incl. 316/318 Hay House,
  the 4 Nightingale-Conant edition URLs, and 18 Amazon direct links;
  was 109 pre-PR24), 36 approved streaming URLs → 59 master rows
  (was 34 → 52 pre-PR23);
  relationships 336 (328 derived + 8 related); Everything 378 (0 pending candidates; Veritas
  candidate rows 28 → 8 after the 2026-08-04 refresh linked all
  already-promoted works). Proposed filename column added between Title and Item Type (YYYY-MM - Name [1/3].mp4 safe [1-3] display [1/3], no bracket for single, audiobook label removed). Remaining model
  work: all 5 New Work Review queue rows and 6 pending manual candidates were
  promoted 2026-08-03 as master UUIDs 353–358.
- **Record 246** (`"In the World But Not of It" – Audio`, the 1 untyped record; reassigned from UUID 264 in the deduplication rebuild):
  deferred pending physical-edition confirmation; product 1661 is mapping-row
  only — do **not** add a source override yet.
- **Candidate promotion path:** All 26 reviewed manual candidates promoted (26/26, 0 pending); 0 New Work Review queue rows remaining.
- ~~**10 conflicting series-taxonomy proposals**~~ — **RULED 2026-08-04**:
  **3 approved** (1814 → master 357 re-seriesed to On The Road Talk Series;
  50485/50488 → masters 312/313 re-seriesed to Discussion Series; build
  confirms exactly 3 series changes) and **7 rejected** with rationale in
  the review notes (1546/1548, 1661/1695/1728/1742, 55576 — the curated
  series stands; editions keep their work's series; the publisher's
  "Media Miscellaneous" shelf describes the carrier, not the series). Taxonomy is
  now **169 approved / 0 proposed / 10 rejected** (179 matched products).
- **`format` blank on 8 records** (was 73): the 2026-08-03 format backfill
  inferred 65 formats (89% fill rate). The remaining 8 blank-format records
  have no automated inference match — root cause and evidence in `archive/TEMP_RESPONSE_AUDIT_2026-08-03.md`
  §11c/§11d. Second inference-pass evidence (SKU prefixes, product-detail
  strings, streaming markers) stays in
  `archive/TEMP_FORMAT_POPULATION_PROPOSAL.md`.
- **Four always-empty master columns** (`location_physical`,
  `location_digital`, `location_streaming`,
  `reference_url_2`): populate or drop. (`source_url_hay_house` is **not**
  empty — 28 values after the 2026-08-03 Hay House backfill —
  and `source_url_nightingale_conant` holds **4** values after the
  2026-08-04 NC edition fills.)
- ~~**Nightingale-Conant provenance**~~ — **resolved 2026-08-04**: the four
  NC-published audio editions (masters 327–330) now carry their official
  NC product URLs via candidate-keyed overrides (110 total). The remaining
  NC products (The Ultimate David Hawkins Library, The Discovery, Naked)
  are unmapped compilations/programs that stay in the official discovery
  queue pending owner ruling; see the decision note in
  `archive/TEMP_NIGHTINGALE_PROVENANCE.md`.

**P2 — Hygiene:**

- ~~Add a `LICENSE`~~ — **done 2026-08-04** (MIT, `LICENSE`; README links it).
- ~~Remove deprecated `audio`/`video` item types~~ — **done 2026-08-03**
  (branch `arena/019fc9b5-docsheet`): `DEPRECATED_MEDIUM_ITEM_TYPES` removed;
  the 8 last candidate rows migrated to owner-approved types; 100 tests incl.
  4 retirement guards. Remaining: the 4 free-text `audio` values in the
  unreviewed discovery triage lane (owner ruling).
- Widen browser tests: all 15 tabs, column chooser, drawer, dark mode
  (added `tests/column-layout.spec.js` 2026-08-04: Work-column placement +
  measured-width assertions).


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
- Result: master **365** (309 lecture), promoted candidates **39**, overrides **134**, relationships **343** (derived primary moved 309 → 221), work families **208 works / 341 members**; all 5 `--check` + 107 tests + doc-parity green.

### Hygiene batch 1 EXECUTED (owner picks A+B from `archive/TEMP_RESPONSE_HYGIENE_2026-08-07.md`, 2026-08-07)

- **A — root-doc triage:** 9 completed/executed docs moved to `archive/` (Title/Item-Type proposals, Ruling-Prep memo, FULL_STACK_AUDIT_2026-08-04_FINAL_358_V2, Lecture-Year investigation, Veritas artifact+mapping reviews, Official-Catalogue discovery, Pages deployment analysis); every cross-reference in README/handoff/EDITION_MODEL/decisions/ fixed, stale root refs (`FULL_STACK_AUDIT_2026-08-03.md`, `…2026-08-04_FINAL.md`, `AUDIT_REPORT_2026-08-04.md`) pointed at archive. Root: 27 → 18 Markdown files.
- **B — year mirror retired:** `data/year_provenance.csv` deleted (consumed by no script; had already drifted 358-vs-368); `YEAR_COLUMN_PROVENANCE.md` rewritten as policy + audit notes pointing at the master's authoritative `year_source` column.
- **F — withdrawn (premise corrected in the report):** the taxonomy "queue" is *generated* from `series_category_mapping.csv` by `map_series_taxonomy.py` and all 4 rows are already ruled — a derived attention-view with 0 pending conflicts, not a second register. No change made.
- Batches 2 (coverage-gate raise + handoff checkpoint) and 3 (derivable-mirrors tool) proposed, awaiting owner pick.

### Hygiene batch 2 EXECUTED (owner pick, 2026-08-07)

- **C — coverage gate:** `.coveragerc` `fail_under` 80 → **85** (actual 91% total, floor module 88%); README/INSTRUCTIONS floor mentions updated.
- **D — handoff checkpoint:** §4's 2026-08-03 chronicle (~315 lines) + the 2026-08-04 final-audit notes moved to `archive/HANDOFF_HISTORY.md`; handoff 572 → 258 lines; section numbers kept (§4 is now an archive pointer; §3/§4 heading shape preserved for the doc-parity tests).
- Remaining hygiene offers: batch 3 (derivable-mirrors tool, item E); deferred/ruling items H/I/J; owner-action K (CI Node 20 → 22, workflows permission).

## 7. House-keeping for every turn

- Keep docs accurate with each push (counts live in `docs/catalogue-meta.json`;
  cite those numbers — do not hand-count).
- Present long results via a committed Markdown report
  (`archive/TEMP_RESPONSE_AUDIT_2026-08-03.md` is the 2026-08-03 log;
  `FULL_STACK_AUDIT_2026-08-07_DEEP.md` is the current full-project audit); the
  chat should stay a one-sentence summary plus the `ask_user` question for
  what is next.
- Update this handoff at the end of each session so the next agent inherits
  your context verbatim.
