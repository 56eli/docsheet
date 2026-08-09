# Next-Agent Handoff

**Prepared:** 2026-08-08 (post-D-01-collapse verification) — current handoff for
branch `arena/019fe2db-docsheet` (PR #39, open). See
`FULL_STACK_AUDIT_2026-08-08_INDEPENDENT.md` (current independent audit +
§10 postscript with before/after counts) and the session log at the bottom of
§6. The declared-current Arena audit
(`FULL_STACK_AUDIT_2026-08-08_ARENA.md`) and the fresh-eyes pass
(`FULL_STACK_AUDIT_2026-08-08_ARENA_FRESH_EYES.md`) remain at root; earlier
2026-08-08 audits are in `archive/`. Headline results this session:
- **Independent full-stack audit (`FULL_STACK_AUDIT_2026-08-08_INDEPENDENT.md`):**
  all six `--check` modes, 125/125 tests, 91% coverage green from a fresh
  Python 3.11 venv (pandas 3.0.5 / coverage 7.15.4); independent pandas probes
  bypassing the project's own validators surfaced 8 catalogue findings
  (D-01…D-08), 3 build/code findings (B-01…B-03), and 5 doc/handoff drifts
  (DOC-01…DOC-05). No critical/data-loss issues.
- **D-01 duplicate-row collapse (owner-selected "collapse"):** two work
  families contained both a raw `format=streaming` row and a promoted
  `format=DVD` row sharing the same primary Veritas URL
  (`w-devotion-to-truth-talk` = 225/311; `w-mind-heart-and-service` =
  226/227/310). Retired the duplicate streaming masters 225/226/227 and kept
  311/310 as the single DVD masters with the streaming page in
  `reference_url_1` (matching the 278–285 precedent). Net counts: 365 →
  **362 masters**, 281 → **278 codes**, 72 → **75 exclusions**, 341 → **338
  work-family memberships**, 336 → **333 derived primary relationships**,
  343 → **340 total relationships**, 365 → **362 filename rows**. 134
  overrides, 39 promotions, 7 compilations, 191 works, and 5 mapping
  decisions unchanged. UUID gaps are now `{225, 226, 227, 246, 249, 264,
  281, 284, 302, 309}`.
- **Touches for the collapse:** ledger raw rows 249/250/251 `item` →
  `duplicate`; promoted candidates 54219/55473 now carry `proposed_owned=true`
  (ownership re-homed from the retired raw rows); `work_families.csv`
  memberships 225/226/227 removed and the 310/311 evidence notes rewritten;
  `series_category_mapping.csv` 54219 → 310 and 55473 → 311;
  `veritas_official_products.csv` mirrors re-derived by
  `sync_inventory_mirrors.py`; `filename_proposal_YYYYMM.csv` retired rows
  removed and master 311's `(DVD)` carrier suffix reverted to plain
  `2003 - Devotion to Truth Talk.mp4`.
- **Ledger `proposed_month` normalisation:** fixed a pre-existing pandas
  float-formatting regression (`"1.0"…"12.0"`) back to zero-padded
  `"01"…"12"`. The broken values were breaking the series-compilation
  validator's month-range string comparison (exposed mid-fix).
- **Tests:** 125/125 deterministic (4 fixtures updated for the new mirror
  state: `DerivedPrimaryRelationships` 336 → 333, the two
  `SyncInventoryMirrors` drift fixtures, `reduced_pending_view` 365 → 362,
  and the filename-uniqueness guard reseeded onto the current clean set);
  coverage remains 91% (lowest module 88%, floor 85%); `node --check` clean;
  `npm audit` 0 vulns.
- **Docs refreshed:** README, NEXT_AGENT_HANDOFF (this file),
  MIGRATION_REVIEW_LEDGER, EDITION_MODEL_PROPOSAL,
  FILENAME_PROPOSAL_YYYYMM_DVD01_V4, PRODUCT_RELATIONSHIP_SCHEMA,
  UX_REWORK_SUGGESTIONS, YEAR_COLUMN_PROVENANCE.
- **Left open for owner triage (no code/data changes in PR #39):**
  - **D-04 (Low/Med):** RESOLVED in branch `arena/019fe5d4-docsheet` (2026-08-09): Amazon paperback URLs for masters 359–361 no longer duplicate into `reference_url_1`; `build_research_master.py:1394` now treats Amazon URLs as curated-source URLs and `reference_url_1` is blank for 359–361 (verified 0 `amazon==reference` duplicates).
  - **B-01 (Med):** RESOLVED in branch `arena/019fe5d4-docsheet` (2026-08-09): two Spanish Audible titles moved from hardcoded `build_catalogue_pages.py:797–815` into `data/international_discovery_queue.csv` (36 → 38 rows); `international-products.json` is now fully input-driven (38 → 38 parity) and `catalogue-meta.json` now publishes `international_products: 38`.
  - **B-02/B-03, D-02 (moot after retirement), D-03, D-05–D-08,
    DOC-01–DOC-05** — described in the independent audit.
  - Open Issue #18 (ownership cross-check vs lak.nz Drive) still needs
    triage; `main` branch-protection / required-status-checks could not be
    observed with this token (403).

**Previous (2026-08-08 follow-up, branch `arena/019fe244-docsheet`, PR #37
merged):** independent full-stack audit
(`FULL_STACK_AUDIT_2026-08-08_ARENA_FRESH_EYES.md`) plus owner-approved data
and doc fixes (D-01…D-05 from that audit, S-1…S-8 hygiene). The
fresh-eyes baseline is preserved in
`FULL_STACK_AUDIT_2026-08-08_ARENA_FRESH_EYES.md`. Headline results that
session:
- **Independent audit:** all six `--check` modes, 125/125 tests, 91% coverage
  green after the F-01/F-02 follow-up fixes; the original 115-test audit found
  one new live-data defect (stale Veritas decision row for
  product 50491) + four doc/CI drifts (D-1…D-5); all fixed — the 50491 overlay
  row (`matched_by_title→121`) contradicted the inventory/master (primary
  source of master 278) and would have caused a false Map-Veritas diff;
  removed, overlay 10→9, decisions doc + handoff updated.
- **Catalogue-code minting rule documented (D-5):** codes go only to
  `lecture`/`discussion` rows with a verified year at minting time, explaining
  why pre-2000 and blank-year candidate/edition rows correctly have none.
- **Filename-first UX:** **Proposed File Name** is now a visible, frozen lead
  column right after a compact **CM** record-type badge (full phrase in the
  tooltip/filter); the curated master reads like a file explorer.
- **Full UX rework:** faceted filters (Series/Year/Type/Format/Owned) with
  removable chips + per-view persistence; clickable stats chips; shorter tab
  labels (Candidates/Exclusions/Decisions/Compilations/Publishers); monospace
  filename with muted extension; carrier-color dots in Edition; "Copy file
  name" drawer action; work-group row striping; per-view sort/scroll
  persistence; keyboard shortcuts (`/`, `j/k`, `y`, `?`) with a help overlay.
  New `tests/ux-enhancements.spec.js` (9 browser tests; suite now 18 browser
  tests).
- **Owner applied CI snippet** in the GitHub web editor: the JS-syntax step
  now loops `tests/*.spec.js`; `WORKFLOW_WEB_EDITOR_GUIDE.md` +
  `archive/UNBLOCK_INSTRUCTIONS.md` record it applied.
- `UX_REWORK_SUGGESTIONS.md` documents the prioritized backlog.

**Previous (2026-08-08 follow-up, branch `arena/019fe0ef-docsheet`, merged):**
owner streaming-reference ruling applied — raw streaming rows may stand alone,
while DVD/CD products carry streaming pages in `reference_url_1`; work families
225/311 and 226/227/310 merged, DVD rows 310/311 no longer store
`streaming video` as `format_detail`, Unity Church title months backfilled,
filename metadata mirrors guarded, series-taxonomy queue hides approved
conflicts, raw CSV hygiene applied, and the site was reworked into a
minimalist table-first UI with View settings / Expand everything.
- **C1/C2 master 265 ruled + applied** (Option A): publisher-verbatim URL kept
  + documented; carrier corrected `audiobook → CD` (`three CD; 2h56m`); format
  inference hardened (CD markers beat "– Audio"; malformed `https-…` slugs
  blank); US Audible audiobook tracked as a manual lead.
- **C3 198X convention applied**: documented in README; site renders
  `c. 1980s` with a deterministic year sorter (raw value preserved).
- **C4 owned semantics applied**: README vocabulary + `Owned`/`Not owned`
  badges.
- **DP-1/2/3 work-family merge applied**: 11 multi-part groups consolidated
  (208 → **193 works**, now **191** after the 225/311 and 226/227/310 follow-up merges); master 202 left the `w-power-vs-force` book work;
  26 PART-marker canonicals cleaned.
- **QA-5 fixed**: `legacy_title` + `proposed_filename_display` restored to the
  published Everything view; new **schema-contract test** (suite **115**).
- **S-a…S-g**: code-order/`candidate:`-prefix docs, test-count house rule,
  contract test, year-research memo (no authoritative dates for 230–232/268).
- **Site redesign applied + simplified** (IA groups + stats strip + empty
  states; a11y roving tabs/focus/reduced-motion/link labels; official inventory tabs;
  minimalist neutral theme; View settings with wrap cells / density / summary toggle /
  **Expand everything**): `archive/SITE_UX_REDESIGN_PROPOSAL_2026-08-08.md`.
- **Raw CSV hygiene applied**: 3 broken Advaita URLs fixed; 13 repeated
  `2cds each?` tempids cleared; ledger mirrors and generated views refreshed;
  approved source overrides now 131.

**Previous:** 2026-08-07 — latest refresh: full project audit + post-PR #27 review (branch `arena/019fdd68-docsheet`; see `archive/TEMP_RESPONSE_AUDIT_2026-08-07_POST_PR27.md`). **Heads-up:** the PR #27 merge left CI **red on `main`** — the Playwright `csv-export.spec.js` still asserted the candidate review filter exists even though all candidate lanes are now 0; the toolbar is hidden by design when every row is `master`. The spec was made data-driven on this branch; merge its PR to green `main`.
**Earlier same-day:** full-stack audit + post-PR #26 review (branch `arena/019fdd28-docsheet`; see `archive/FULL_STACK_AUDIT_2026-08-07_DEEP.md` and `archive/TEMP_RESPONSE_AUDIT_2026-08-07_POST_PR26.md`).
**Earlier branches:** `arena/019fdcc5-docsheet`, `arena/019fdb8b-docsheet`, `arena/019fc9b5-docsheet`, closed out via PRs #24–#26 (merged to `main`); earlier same-day work landed via PRs #11–#23.

If you are the next agent: **read this file top to bottom before touching
anything.** It is written to give you full context in five minutes.

---

## 1. What this project is

DocSheet is a static GitHub Pages catalogue of David R. Hawkins material:
`_hawkins archive clone - Sheet1.csv_` (374 raw rows) flows through a
hand-maintained `migration_review_ledger.csv` into generators that emit 19
`docs/*.json` sheets rendered by Tabulator (`docs/index.html`, `docs/app.js`).

| Generator | Input → Output (committed artifacts; never hand-edit) |
|---|---|
| `process_data.py` | raw CSV → `docs/data.json` (`docs/meta.json` was stopped 2026-08-07 — never consumed; footer reads HTTP `Last-Modified`) |
| `build_research_master.py` | raw CSV + ledger + review overlays → `data/research_master_draft.{csv,json}`, `data/research_master_exclusions.csv` |
| `build_catalogue_pages.py` | master + all review CSVs → the 19 `docs/*.json` sheets + `docs/catalogue-meta.json` (20 JSON files total) |
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
python sync_inventory_mirrors.py --check   # derived inventory mirrors (clean since the 2026-08-07 flip-both ruling)
python process_data.py --check        # if wired into your tooling
python -m unittest discover tests     # 125 tests, offline, ~3s
coverage run -m unittest discover tests && coverage report   # gate: 85%; currently 91%
node --check docs/app.js && node --check playwright.config.js && for spec in tests/*.spec.js; do node --check "$spec"; done
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
  suite (3 spec files / 18 tests: `column-layout` 4, `csv-export` 5,
  `ux-enhancements` 9); don't burn time installing locally.
- Python 3.11 / Node 22 in-sandbox; CI uses 3.12 / **Node 22** (owner applied
  the `node-version: "20" → "22"` bump as commit `406116f` on `main`,
  2026-08-08 — item K ✅ DONE; snippet remains in
  `archive/UNBLOCK_INSTRUCTIONS.md` for reference). Workflows are
  owner-managed; the Arena app cannot push `.github/workflows/*`.

## 3. Current verified state (committed, checked)

| Layer | Count | Notes |
|---|---:|---|
| Raw rows / ledger rows | 374 / 374 | `hawkins archive clone - Sheet1.csv`, `migration_review_ledger.csv` |
| Curated master | 362 | 306 lecture / 40 book / 8 discussion / 7 highlight / 1 other — **no untyped records** (record 246 ruled 2026-08-07: duplicate of the audio edition already held as master 329, excluded; record 309 ruled 2026-08-07: duplicate of the Oxford talk already held as master 221, un-minted); duplicate streaming masters 225/226/227 retired 2026-08-08 (D-01 collapse into promoted DVD masters 311/310 per the one-DVD/CD-master-with-streaming-reference ruling); incl. 24 minted edition rows (320–343) + 9 Satsang monthlies (344–352) + 6 manual candidates (353–358) + 3 academic (359-361) + 7 annual Highlights (362–368, series Lecture Highlights) + The Discovery 369 / Ultimate David Hawkins Library 370 / OM 371 (unique NC+Audible programs) + How to Surrender to God 372 (unique Hay House program, owner rulings 2026-08-07); legacy duplicates 281/284 excluded 2026-08-07 (same 2012 Discussion Series talks as promoted masters 312/313) |
| Everything view | **362** | 362 master + 0 candidate_veritas (Map poster ruled excluded_related_material 2026-08-07) + 0 candidate_pending_promotion + 0 discovery + 0 hayhouse + 0 audible (all review lanes ruled out 2026-08-07) |
| Exclusions / source overrides | 75 / 134 | includes the 4 Nightingale-Conant audio-edition URLs filled 2026-08-04 and the Audible/NC/Hay House URLs of masters 369–372 (now 134 incl. the 18 Amazon direct links, the 3 academic-book Amazon links moved onto the curated `source_url_amazon` column on 2026-08-08, and the product-53277 link moved from retired duplicate 309 onto master 221; the three Advaita URL overlays were retired after the raw CSV was fixed on 2026-08-08); the 3 D-01 duplicate raw rows (249/250/251) were moved from `item` to `duplicate` on 2026-08-08 |
| Veritas inventory | 191 products | categories populated 191/191; **5** approved mapping decisions, all excluded-related-material rows (the 7 Highlights, 50411/1542, and stale 50491 overlays were lifted; 53062/50398/50378/50432 were also removed 2026-08-08 after exact primary-URL evidence); the D-01 collapse re-derived 54219 / 55473 to single master IDs (310 / 311) |
| Everything relationships | 340 product relationships, 7 series compilations | 333 derived primary + 7 related_material |
| Candidate pool | 39 reviewed manual candidates (all 39 promoted — candidate manual-veritas-53277 un-minted 2026-08-07 as duplicate of master 221 — incl. 9 Satsang monthlies, 6 manual candidates, 3 academic, 7 Highlights, 3 NC/Audible programs, 1 Hay House program, 0 pending), 2 manual leads; 24 edition candidates all promoted | |
| Work families | 191 works / 338 members approved; work_id coverage 362/362 | `data/work_families.csv` (338 rows) plus the 24 edition-promotion work_ids in `data/edition_promotions.csv` |
| Series taxonomy | 186 matched products → **177 approved / 0 proposed / 9 rejected**; all proposals ruled; conflict queue 0 rows (50521's former R3 conflict is retained as an approved mapping, not a pending queue item) | 3 approvals re-series masters 357 (On The Road Talk Series) + 312/313 (Discussion Series); 7 Highlights → Lecture Highlights (R1, owner ruling 2026-08-07); 50411 approved R4 no-op after owner ruling moved it to 286; 1542 stays rejected (Media Miscellaneous category must not re-series 331); 9 rejections carry documented rationale |
| Test suite | **125 tests; coverage 91% total, every pipeline module ≥ 88%** (build_catalogue_pages.py = 89%) | `.coveragerc` enforces `fail_under = 85` (raised 2026-08-07) |

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
  `item_type` vocabulary 2026-08-03** — validators reject them everywhere;
  the last unreviewed discovery-triage lane
  (`data/official_discovery_queue.csv`) was ruled empty on 2026-08-07 (the 3
  NC programs promoted to masters 369–371, Map poster 1560 excluded), so no
  free-text `audio` remains anywhere.
- **No title-based inference for `series`, and a commercial listing is not
  master identity.** Four records once linked to the wrong edition because of
  title matching.
- **Compact master IDs are stable once issued.**
- **`work_id` comes only from approved `data/work_families.csv` rows** — for
  minted edition rows (masters 320–343) it comes from the approved `work_id`
  column of `data/edition_promotions.csv` instead. Never infer work identity
  from titles alone (C2 lesson); `proposed` rows are validated but never applied.
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
  **✅ FULLY APPLIED — see §3 "Current verified state" for the authoritative
  counts** (362 masters, 191 works / 338 memberships in `work_families.csv`
  plus 24 edition-promotion work_ids covering 362/362, 134 overrides, 340
  relationships, 278 codes, 24 minted edition rows 320–343, filename proposal
  v4.1). The paragraph below is the **superseded 2026-08-03/04 proposal
  snapshot** retained for provenance; do not treat its counts (358 rows,
  201 works, 127 overrides, 336 relationships, Everything 378) as current.
  <!-- BEGIN SUPERSEDED 2026-08-03/04 SNAPSHOT -->
  ~~Master **358 rows** (307 lecture / 40 book / 10
  discussion / 1 untyped) incl. 24 minted edition rows (320–343, pinned
  UUIDs in `edition_promotions.csv` — never renumber), 9 promoted
  Satsang monthlies (344–352), 6 promoted manual candidates (353–358) + 3 academic (359-361, Orthomolecular 1973, Qualitative 1998, Dialogues 1998),
  with Path duplicate 302 removed and Volume Series years stripped to blank pre-2000 per owner (catalogue codes 284→271 after the strip; **281** as of the 2026-08-07 year-provenance fixes);
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
  promoted 2026-08-03 as master UUIDs 353–358.~~
  <!-- END SUPERSEDED SNAPSHOT -->
- ~~**Record 246** (`"In the World But Not of It" – Audio`, the 1 untyped record; reassigned from UUID 264 in the deduplication rebuild):
  deferred pending physical-edition confirmation~~ — **RULED 2026-08-07**:
  duplicate of the audio edition already held as master 329; record 246
  excluded and its uuid un-minted (uuid 246 no longer exists in the master).
  Product 1661 is mapping-row only — do **not** add a source override.
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
- ~~**Four always-empty master columns**~~ — **resolved 2026-08-07 (owner
  ruling: drop all four)**: `location_physical`, `location_digital`,
  `location_streaming`, `reference_url_2` removed from schema, sheet, specs
  and docs (25 master columns remain; re-adding is a git revert away).
  Outcome memo: `archive/RULING_PREP_EMPTY_COLUMNS.md`. (`source_url_hay_house`
  is **not** empty — **27** values after the 2026-08-03 Hay House backfill
  and later corrections — and `source_url_nightingale_conant` holds **6**
  values: the four 2026-08-04 NC edition fills plus the NC/Audible program
  masters 369–370.)
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
  4 retirement guards. ~~Remaining: the 4 free-text `audio` values in the
  unreviewed discovery triage lane (owner ruling)~~ — **resolved 2026-08-07**:
  the discovery triage lane was ruled empty (3 NC programs promoted to
  masters 369–371, Map poster 1560 excluded), so no free-text `audio`
  remains anywhere.
- Widen browser tests: all 19 tabs (Catalogue · Review workspace · Sources groups), column chooser, drawer, dark mode
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
