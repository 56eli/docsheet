# Next-Agent Handoff

**Prepared:** 2026-08-09 (REVISION1 ODS owner revision applied — see below) — current handoff for
branch `arena/019fe6c1-docsheet`.
**Scoreboard:** this repo now has a persistent scoreboard — read
`SCOREBOARD.md`, `.scoreboard/scoreboard.yml`, `.scoreboard/agent-handoff.md`,
and `AGENTS.md` first; they are the durable agent-memory layer (Arena
sessions may expire after PR merge).

## Headline results (2026-08-09 REVISION1 ODS pass, current)

- **Owner uploaded `hawkins-everything-REVISION1.ods` to `main`** (commit
  `fa51f67`): a colour-coded expert-columns export of the Everything view.
  Decoded cell-by-cell (values + fill colours from `content.xml`): all 362
  rows matched the master; the file carries **58 proposed-filename edits**
  (unified `OTR - ` prefix on 32 On-The-Road rows, `198X - A-01 … B-06` codes
  on the 16 Office rows, `DISCUSSION - ` prefix on 8 discussion rows, year
  dropped on 356/358, year 2014→2003 on 357, truncated 312 completed as
  `2012 - DISCUSSION - Permanent Inner Peace.mp4`), **1 notes edit**
  (`FRAN GRACE` on master 315, replacing the provenance note — owner chose
  replace-entirely), **year data changes** (356/358 cleared, 357 → 2003 with
  month cleared; owner chose apply-full), and **colour-group presentation
  order** (owner-confirmed block order: 2002-2011 lectures → discussion →
  satsang → on-the-road → volumes → office → books → transcription → media-misc
  → undecided → Fran Grace last).
- **Applied through new reviewed overlays** (no hand-edits to generated
  files): `data/master_year_overrides.csv` (3 rows),
  `data/master_notes_overrides.csv` (1 row), and
  `data/catalogue_display_order.csv` (362 rows; dense 1..n per block;
  `build_catalogue_pages.py` reorders the Everything view + CSV export and
  fails on duplicates/missing uuids/unapproved rows). Filename edits landed
  in the reviewed `data/filename_proposal_YYYYMM.csv` (safe + display
  variants; year/month mirrored for 356–358). The change record itself is
  committed as `review/hawkins-everything-REVISION1.ods`.
- **Tests 126 → 132** (new `OwnerOverrideAndDisplayOrderTests` class);
  coverage 91% → 90% (floor 85; both generator modules still 88%).
  All six `--check` modes pass; README documents the new inputs.
- **Fresh audit** (`docs/audits/2026-08-09-arena-full-audit.md`) plus
  F-01..F-04 fixes and the repo-organization archival are in this branch's
  earlier commit `18295b6` — see the section below.

The declared-current audits are
`FULL_STACK_AUDIT_2026-08-09_ARENA_EXPERT.md` (this session's expert pass,
verified at `556bf48`), `FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md`
(verified at `d731e1b`) and its extension
`FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md` (verified at `f520e9b`,
H-01/L-02/DOC-10 clarified at `2bc99ec`; its ledger-disposition table was
updated for the 2026-08-09 reclassification);
the historical baseline pair `FULL_STACK_AUDIT_2026-08-08_ARENA.md` and
`FULL_STACK_AUDIT_2026-08-08_ARENA_FRESH_EYES.md` was archived 2026-08-09 with
the other superseded root audits (`archive/EXTERNAL_AUDIT.md` carries a
SUPERSEDED banner; `archive/FULL_STACK_AUDIT_2026-08-09_ARENA.md` too —
pre-PR-#40 findings). See the session log at the bottom of §6.
Headline results (2026-08-09 expert pass, current):
- **Expert full-stack audit (`FULL_STACK_AUDIT_2026-08-09_ARENA_EXPERT.md`):**
  all six `--check` modes, 126/126 tests, 91% coverage green (pandas 3.0.5 /
  coverage 7.15.4); ~20 independent pandas probes bypassing the project's own
  validators reproduced every README count exactly (362 masters, 278 codes,
  75 exclusions, 134 overrides, 39 promotions, 340 relationships, 7
  compilations, 191 works, 191 products, 10 UUID gaps) and found **no
  data-loss or correctness defects**. Seven low-severity items were reported
  and **all seven were fixed this session** (see below).
- **Ledger row 371 reclassification (owner-approved 2026-08-09):** the single
  `needs_review` row — the raw sheet's "Dialogues on Consciousness and
  Spirituality: WHAT IS THIS ⚠️⚠️⚠️" placeholder — was reclassified to
  `duplicate` (of promoted master 361, promoted from
  `manual-academic-dialogues-1998`). Dispositions are now 299 `item` /
  31 `blank_separator` / 21 `series_context` / 10 `research_note` /
  **8 `duplicate`** / 5 `source_context` / **0 `needs_review`**; the 75-row
  exclusion set, `docs/master-exclusions.json`, `docs/migration-review.json`,
  `MIGRATION_REVIEW_LEDGER.md`, and the disposition table in
  `FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md` were regenerated/updated with
  it. No master-row, code, or count changed.
- **Doc fixes:** SERIES_TAXONOMY_MAPPING.md corrected (the seven Highlights
  products ARE in the category mapping as approved R1 rows matched to masters
  362–368, not "out of scope / unmatched"); `decisions/HIGHLIGHTS_COMPILATION_DECISIONS.md`
  gained the `-2002-dvd` slug note (product 1800's URL slug says "dvd" but
  the storefront carrier is Streaming — master keeps `format=streaming`);
  handoff header refreshed for this branch.
- **Original Spreadsheet view (audit §3.4):** the 31 fully-empty raw
  separator rows are now hidden by default — grid, footer count, and CSV
  export all agree — with a persisted "Show blank separator rows" View
  setting (visible only on that tab) restoring the verbatim 374-row sheet.
  New `tests/blank-rows.spec.js` derives its expected counts from
  `data.json`.
- **Wording (audit §3.6):** README, INSTRUCTIONS, and the `process_data.py`
  docstring now state that the raw pipeline is pass-through *except* for the
  six always-empty raw columns trimmed from the published view.
- **Archival footnote (audit §3.7):** `archive/FULL_STACK_AUDIT_2026-08-08_INDEPENDENT_ROOT.md`
  corrected for the record — the 17 blank-year rows are 13 Volumes + 4
  under-investigation; the 7 Highlights rows carry years and omit the prefix
  per the separate "filename equals title" directive.
- **Presentation/UX implementation (owner approved the full plan):** see
  `archive/PRESENTATION_UX_PROPOSAL_2026-08-09.md` (implemented, archived
  2026-08-09) — catalogue overview hero +
  collection stats + series strip, desktop Browse cards toggle, Review
  workspace nav toggle, Series browser tab, search hints, loading skeleton,
  a11y labels. Browser suite grew 19 → **26 tests** (new
  `tests/presentation-ux.spec.js`). Scoreboard AI scores for
  github_pages_presentation/ux_usability/accessibility are **unchanged
  pending re-audit** — the owner's 5/10 user scores still stand and the
  effective scores still drive priority (15/12).
- **Still open:** GitHub issue #18 (owned flags vs lak.nz Drive); the
  presentation/UX re-score and re-audit after the owner reviews the new
  first impression.

Headline results (2026-08-08 independent pass, baseline):
- **Independent full-stack audit (`archive/FULL_STACK_AUDIT_2026-08-08_INDEPENDENT_ROOT.md`):**
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
  UX_REWORK_SUGGESTIONS (now `archive/UX_REWORK_SUGGESTIONS.md`), YEAR_COLUMN_PROVENANCE.
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
(`archive/FULL_STACK_AUDIT_2026-08-08_ARENA_FRESH_EYES.md`) plus owner-approved data
and doc fixes (D-01…D-05 from that audit, S-1…S-8 hygiene). The
fresh-eyes baseline is preserved in
`archive/FULL_STACK_AUDIT_2026-08-08_ARENA_FRESH_EYES.md`. Headline results that
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
  now loops `tests/*.spec.js`; `archive/WORKFLOW_WEB_EDITOR_GUIDE.md` +
  `archive/UNBLOCK_INSTRUCTIONS.md` record it applied.
- `archive/UX_REWORK_SUGGESTIONS.md` documents the prioritized backlog.

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
python -m unittest discover tests     # 126 tests, offline, ~3s
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
| Test suite | **126 tests; coverage 91% total, every pipeline module ≥ 88%** (build_catalogue_pages.py = 89%) | `.coveragerc` enforces `fail_under = 85` (raised 2026-08-07) |

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
  now **177 approved / 9 rejected / 0 queued** (186 mapping rows; the earlier
  "169 approved / 10 rejected / 179 matched" snapshot was superseded by the
  50521 resolution and the 2026-08-09 mapping refresh — the master build
  applies 324 approved master-level mappings with 3 series changes).
- ~~**`format` blank on 8 records**~~ — **resolved**: 0/362 master rows are
  blank today (the inference grew to 107 formats from the official inventory;
  the 2026-08-03 snapshot of 8 blank records and its evidence live in
  `archive/TEMP_RESPONSE_AUDIT_2026-08-03.md` §11c/§11d, with the second
  inference pass in `archive/TEMP_FORMAT_POPULATION_PROPOSAL.md`).
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


## Archived history (2026-08-07–08)

Intermediate 2026-08-07–08 session logs (Post-PR #27 audit, distributor title alignment, Hay House fill, duplicate ruling 309→221, hygiene batches 1–3, empty-column ruling, filename v4.1, 6-part directive, 2026-08-08 audit, follow-up, Session 2, Guard follow-up, audit-policy follow-up, Mobile Browse, Frontend hardening, Mobile shelves, Fresh-eyes PR #37) have been archived to [`archive/HANDOFF_HISTORY.md`](archive/HANDOFF_HISTORY.md) in this hygiene pass. See that file for the full chronicle; the current handoff retains only the 2026-08-09 verification.

## 2026-08-09 Full-stack deep-dive + owner-approved fixes (arena/019fe5fc-docsheet, current)

Branch `arena/019fe5fc-docsheet` at `d731e1b` (PR #40 merged into `main`).
Deep-dive audit (`FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md`, read-only,
then owner-approved fixes applied in this branch).

- **Audit result:** all six `--check` modes green, 126/126 tests (one added),
  91% coverage, HTTP/CSP/SRI clean, and the 08-09 Arena pass's headline
  findings (C-01, D-04, B-01, B-02) verified **already resolved at HEAD**.
  Remaining findings: B-04 (ledger `proposed_owned` validator missing),
  D-09 (always-empty `Unnamed: 11` still published; `Unnamed: 5` junk column),
  D-10 (raw CSV note rows), DOC-06…09 (stale audits/README/handoff).
- **Fixes applied (owner-approved, all checks re-run green):**
  - B-04: `build_research_master.py` now validates ledger `proposed_owned ∈
    {"", "true", "false"}` before build (mirrors candidate validators); new
    test `test_ledger_owned_casing_fails_build` (tests 125 → 126).
  - D-09: `process_data.py` drops `Unnamed: 11` (view 8 → 7 columns; all six
    always-empty columns now trimmed); `docs/app.js` `original` priority list
    replaces dead `"other links"` with `notes`.
  - D-10: raw CSV row 279 Discord URL moved out of the `format` column and row
    373's `SETH HAS IT` note out of `title` into the notes column (header
    added: `notes`); ledger raw mirrors + review_reason updated for both rows
    (row 373 → "Owner note relocated to notes column; not a catalogue item.");
    exclusions/migration-review artifacts regenerated.
  - DOC-06…09: `archive/FULL_STACK_AUDIT_2026-08-09_ARENA.md` +
    `archive/EXTERNAL_AUDIT.md` got
    SUPERSEDED banners; README documentation layout now declares the deep-dive
    current, Everything-view wording softened (candidates only when intake
    lanes are populated; Record Type filter hidden while all rows are
    `master`), current-audit pointer updated; INSTRUCTIONS "5 → 6 always-empty
    columns"; test counts 125 → 126 in README/INSTRUCTIONS.
- **Left open for owner triage:** none from this pass. Watch items: the
  ledger validator is the enforced fix for the C-01 class (silent `.lower()`
  remains as belt-and-braces); `reference_url_1` Veritas links (53) are not
  mirrored in the 191-product inventory (all live-checked OK, by design).

## 2026-08-09 Full-stack audit + hygiene (arena/019fe620-docsheet, previous)

Branch `arena/019fe620-docsheet` at `2bc99ec`. Full audit
`FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md` (read-only at `f520e9b`, fixes at `80cdcea`/`2bc99ec`).

- **Audit result:** all six `--check` modes green, 126/126 tests, 91% coverage, no duplicate UUIDs/codes/filenames, 0 orphan Veritas URLs, headline defects of every prior pass verified resolved.
- **Docs hygiene:** normative schemas/policies intentionally kept at root as living policies — owner confirmed `keep_normative`.

## 2026-08-09 CSV export fix + audit note (arena/019fe6ad-docsheet, current — this session)

Branch `arena/019fe6ad-docsheet` (current working branch, from `408f31e` / PR #44 merge). Read-only audit + one fix applied:

- **Audit scope:** CSV export feature (`docs/app.js` `exportCsv()`) — desktop `table.download()` vs mobile/manual fallback inconsistency, BOM effect on parsers, hidden column exclusion.
- **Findings verified:**
  1. Desktop download excluded hidden expert columns (`visibleColumnsOnly` defaults `true` in Tabulator).
  2. Manual fallback included all fields but used JSON insertion order (different from preset order).
  3. BOM (`\uFEFF`) at file start caused some CSV parsers to treat the first header cell as empty / missing.
- **Fix applied (docs/app.js):**
  - Added `visibleColumnsOnly: false` to desktop `table.download()` so all expert/provenance fields are included.
  - Aligned manual fallback field list with preset order (`orderKeysForView` + hidden fields + data keys) so desktop/mobile exports match.
  - Removed BOM from both desktop (`bom: false`) and manual fallback (`\uFEFF` removed) — eliminates parser error where the first row/header appeared missing.
- **Verification:** `node --check docs/app.js` passes; no pipeline module changed; 126 tests unchanged; `docs/*.json` artifacts unaffected.
- **Scoreboard impact:** improves usability (priority 12, user 5/10) by making CSV exports consistent across desktop/mobile; does not directly change presentation (priority 15) or maintainability (priority 8).
- **Next open work:** owner should confirm BOM removal is acceptable for their Excel/CSV workflow; if BOM is needed for Excel UTF-8, it can be restored selectively.

- **Verification:** `git diff --stat`: `docs/app.js | 18 insertions(+), 3 deletions(-)`.

## 2026-08-09 Expert full-stack audit + low-severity fixes (arena/019fe659-docsheet, current)

Branch `arena/019fe659-docsheet` from `main` at `556bf48` (main HEAD = merge of PR #43). Full audit at `FULL_STACK_AUDIT_2026-08-09_ARENA_EXPERT.md` (kept at root as a declared-current audit).

- **Expert audit:** all six `--check` modes green, 126/126 tests, 91% coverage; ~20 independent pandas probes bypassing the project's validators reproduced every README count exactly and found no data-loss/correctness defects. Seven low-severity findings (§3 of the audit); the Playwright browser suite could not be re-run in the sandbox (CDN blocked) but CI is green.
- **Ledger row 371 reclassification (owner-approved):** the last `needs_review` row ("Dialogues on Consciousness and Spirituality: WHAT IS THIS ⚠️⚠️⚠️") → `duplicate` of promoted master 361. Regenerated `research_master_exclusions.csv`, `docs/master-exclusions.json`, `docs/migration-review.json`, `RECONCILIATION_REPORT.md`; updated `MIGRATION_REVIEW_LEDGER.md` and the disposition table in `FULL_STACK_AUDIT_2026-08-09_ARENA_FULL.md`. Counts unchanged (75 exclusions; 0 `needs_review`).
- **Doc fixes:** SERIES_TAXONOMY_MAPPING.md Highlights paragraph corrected (all seven Highlights products are approved R1 mapping rows, matched to masters 362–368); `decisions/HIGHLIGHTS_COMPILATION_DECISIONS.md` gained the product-1800 `-dvd` slug note; stale §6 counts in this handoff (taxonomy 169/10 → 177/9, blank-format 8 → 0) corrected.
- **Frontend (audit §3.4):** Original Spreadsheet view hides the 31 blank separator rows by default with a "Show blank separator rows" View setting; added `tests/blank-rows.spec.js` (browser suite now 19 tests). Pass-through wording clarified in README/INSTRUCTIONS/process_data.py (§3.6).
- **Verification:** all six `--check` modes PASS, 126/126 tests PASS, coverage 91%.

## 2026-08-09 Presentation/UX implementation, Phases A–D (arena/019fe659-docsheet, current)

Owner approved the full plan (`archive/PRESENTATION_UX_PROPOSAL_2026-08-09.md`,
archived 2026-08-09 after implementation) after
providing user scores (presentation 5, UX 5, content 7, maintainability 6).

- **Shipped (commit `7ed3a5f`):** catalogue overview hero + collection stats
  + series strip on Everything; desktop Browse cards toggle (work-card UI +
  Series/Timeline rails at any width); Review-workspace nav toggle; Series
  browser tab (client-side, from master.json); search hints; loading
  skeleton; `prefers-reduced-motion`; a11y labels. New
  `tests/presentation-ux.spec.js` (7 specs; suite 19 → 26).
- **Verified:** 6/6 `--check`, 126/126 tests, `node --check` clean, CSS
  brace-balanced, no duplicate HTML ids. Browser specs run in CI.
- **Scoreboard:** AI scores unchanged pending re-audit; user scores still
  make presentation (15) and UX (12) the top priorities. Gate remains
  `fail` (7.9 < 8) until the owner re-scores or the aspects are re-audited.

## 2026-08-09 Independent fresh-eyes audit + doc cleanup + refactoring (arena/019fe63c-docsheet, previous)

Branch `arena/019fe63c-docsheet` from `main` at `150f080`.

- **Independent audit:** all six `--check` modes green, 126/126 tests, 91% coverage, all README claims match generated data exactly (362 masters, 278 codes, 75 exclusions, 134 overrides, 39 promotions, 340 relationships, 7 compilations, 191 Veritas products). Zero critical/data-loss issues. Full audit at `archive/FULL_STACK_AUDIT_2026-08-09_ARENA_INDEPENDENT_FRESH.md`.
- **Documentation cleanup (root `.md` count 24 → 18):**
  - Archived 7 files to `archive/`: `FULL_STACK_AUDIT_2026-08-09_ARENA.md` (superseded), `FULL_STACK_AUDIT_2026-08-08_INDEPENDENT.md` (duplicate of archive copy), `UI_PRINCIPLES_AND_SUGGESTIONS.md`, `UX_REWORK_SUGGESTIONS.md`, `WORKFLOW_FIX_DROPINS_2026-08-09.md`, `WORKFLOW_WEB_EDITOR_GUIDE.md`.
  - Renamed `EXTERNAL_AUDIT` → `EXTERNAL_AUDIT.md`.
  - Updated cross-references in `README.md`, `NEXT_AGENT_HANDOFF.md`, `archive/README.md`.
  - Fixed README "Documentation layout" section to match current state.
- **Code refactoring:**
  - Extracted `apply_year_source_provenance()` from `build_master()` (296 → 192 lines).
  - Extracted `build_review_overview()` from `build_catalogue()` (346 → 239 lines).
  - All 6 `--check` modes and 126/126 tests pass after refactoring.
- **Verification:** all six `--check` modes PASS, 126/126 tests PASS, `coverage 91%`.
