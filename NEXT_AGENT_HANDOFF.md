# Next-Agent Handoff

**Prepared:** 2026-08-03 — refreshed after the audit/tests/fail-safes session.
**Branch:** `arena/019fc7fe-docsheet`, closed out via
[PR #15](https://github.com/56eli/docsheet/pull/15) (merged to `main`);
earlier same-day work landed via PRs #11–#14.

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
python -m unittest discover tests     # 96 tests, offline, ~2s
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
| Curated master | 356 | 307 lecture / 38 book / 10 discussion / 1 untyped (record **246**, deferred); incl. 24 minted edition rows (320–343) + 9 Satsang monthlies (344–352) + 6 manual candidates (353–358) |
| Everything view | **396** | 356 master + 28 candidate_veritas + 0 candidate_pending_promotion + 4 discovery + 4 hayhouse + 4 audible |
| Exclusions / source overrides | 68 / 106 | |
| Veritas inventory | 191 products | categories populated 191/191; 35 approved mapping decisions |
| Everything relationships | 333 product relationships, 7 series compilations | |
| Candidate pool | 26 reviewed manual candidates (all 26 promoted incl. 9 Satsang monthlies and 6 manual candidates, 0 pending), 1 manual lead; 24 edition candidates all promoted | |
| Work families | 199 works / 332 members approved; work_id coverage 356/356 | `data/work_families.csv` |
| Series taxonomy | 149 matched products → 146 approved / 3 rejected; approved mappings applied as a proven no-op | |
| Test suite | **96 tests; coverage 92% total, every pipeline module ≥ 89%** | `.coveragerc` enforces `fail_under = 80` |

All catalogue data was verified against the live Veritas API on 2026-08-03
(see `AUDIT_2026-08-03_FULL.md`, `VERITAS_ARTIFACT_REVIEW.md`).

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
9. **Independent re-audit + doc-status pass (this turn, branch
   `arena/019fc893-docsheet`):** verified every previous claim (93 tests,
   92% coverage, all `--check` modes, CI green on `main` at `6b28e66`), then
   closed the remaining status-quo drift the earlier pass had left: README/
   handoff catalogue codes 223 → **225**; `MIGRATION_REVIEW_LEDGER.md`
   disposition table (item 308 → **306**, research_note 8 → **10**);
   `OFFICIAL_CATALOGUE_DISCOVERY.md` and `VERITAS_PRODUCT_MAPPING.md`
   308-master/344-Everything → 317/363; `RELATIONSHIP_EXPANSION_AUDIT.md`
   (304 URL-bearing masters, 157 distinct URLs, 293 primary / 8 related);
   `ITEM_TYPE_CLASSIFICATION_PROPOSAL.md` marked implemented;
   `archive/README.md` UNBLOCK note resolved. Found and closed **F1**: the 11
   promoted masters (309–319) had a Veritas URL but no primary relationship
   row — 11 reviewed `primary_product_for_item_part` rows were added
   (owner-approved 2026-08-03), the coverage guard in
   `build_catalogue_pages.py` was promoted from a warning to a **hard build
   failure**, and the relationship count is now **312**. Added
   **documentation-currency tests** so README/handoff/ledger-doc counts can
   never silently drift from the generated data again. Details in
   `AUDIT_2026-08-03_FULL.md` §12.
10. **Edition model + session close-out (this turn, branch
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
12. **Full project audit, documentation status-quo refresh, and fail-safe enhancements (this turn, branch `arena/019fc974-docsheet`):**
    Conducted a full project audit and updated all core documentation (`NEXT_AGENT_HANDOFF.md`, `SERIES_TAXONOMY_MAPPING.md`, `SESSION_SUMMARY_2026-08-03.md`, `README.md`, `INSTRUCTIONS.md`) to resolve stale references to record 264 (now **246**), 73 blank formats (now **8**), 100 overrides (now **106**), and series taxonomy counts (149 matched / 146 approved). Archived 4 temporary analysis scripts (`dedup_analysis.py`, `dedup_analysis2.py`, `find_nc_url.py`, `dedup_plan.md`) to `archive/` so default `--source=.` test coverage measures only the 8 pipeline modules and reports a clean **92%** (all modules ≥ 89%). Added structural invariant fail-safes in `build_research_master.py` (`validate_master_items_integrity`) and `build_catalogue_pages.py` (`validate_work_family_coverage`) with 3 new defensive tests (**96 tests**, all passing). Added `docs/.nojekyll` and created `GITHUB_PAGES_DEPLOYMENT_ANALYSIS.md` to troubleshoot and prevent GitHub Pages deployment failures on large JSON files. Consolidated web UI (`docs/index.html`) by removing redundant raw publisher inventory tabs ("Veritas Products", "Hay House Products", "Audible Products"), making the Everything tab authoritative while preserving JSON endpoints for pipeline validation.

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
  `lecture`+`DVD`. `audio`/`video` item types are deprecated residue.
- **No title-based inference for `series`, and a commercial listing is not
  master identity.** Four records once linked to the wrong edition because of
  title matching.
- **Compact master IDs are stable once issued.**
- **`work_id` comes only from approved `data/work_families.csv` rows.**
  Never infer work identity from titles alone (C2 lesson); `proposed` rows
  are validated but never applied.
- **Relationships stay at the evidence level actually supported** (item-level
  when proven; series-level for annual Highlights).
- **Merchandise (card decks, wall charts) are products, not master records.**

## 6. Open work, prioritized

**P0 — Owner-actions:**

- ✅ **CI is live on `main`** (commit `6b28e66`, "Add verification and testing
  steps to CI workflow"): `py_compile`, `process_data.py --check`,
  `map_series_taxonomy.py --check`, all three generator checks, the unittest
  suite, the 80% coverage gate, JS syntax, and the Playwright browser suite.
  Latest run passed 2026-08-03 (run `30834666253`). Nothing outstanding here.
- ⚠️ **Re-run the Map Veritas Catalogue workflow on `main`** to confirm a clean
  pass now that the derived-field fix (Addendum 2 in `VERITAS_ARTIFACT_REVIEW.md`)
  landed; the last run (`30813523859`) failed only at its intentional
  inventory-diff gate before the fix. Review the candidate/diff artifact before
  accepting any live refresh diff.

**P1 — Data decisions needing a ruling:**

- **Edition model (owner-directed; see `EDITION_MODEL_PROPOSAL.md`):**
  **fully applied.** Master **350 rows** (301 lecture / 38 book / 10
  discussion / 1 untyped) incl. 24 minted edition rows (320–343, pinned
  UUIDs in `edition_promotions.csv` — never renumber) and 9 promoted
  Satsang monthlies (344–352); **193 works / 326 family members approved,
  work_id coverage 356/356** (D6a per-part ruling + C1 split applied);
  overrides 106 (candidate-provenance supported, incl. 316/318 Hay House);
  relationships 333; Everything 396 (0 pending candidates). Remaining model
  work: all 5 New Work Review queue rows and 6 pending manual candidates were
  promoted 2026-08-03 as master UUIDs 353–358.
- **Record 246** (`"In the World But Not of It" – Audio`, the 1 untyped record; reassigned from UUID 264 in the deduplication rebuild):
  deferred pending physical-edition confirmation; product 1661 is mapping-row
  only — do **not** add a source override yet.
- **Candidate promotion path:** All 26 reviewed manual candidates promoted (26/26, 0 pending); 0 New Work Review queue rows remaining.
- **`format` blank on 8 records** (was 73): the 2026-08-03 format backfill
  inferred 65 formats (89% fill rate). The remaining 8 blank-format records
  have no automated inference match — root cause and evidence in `TEMP_RESPONSE_AUDIT_2026-08-03.md`
  §11c/§11d. Second inference-pass evidence (SKU prefixes, product-detail
  strings, streaming markers) stays in
  `archive/TEMP_FORMAT_POPULATION_PROPOSAL.md`.
- **Six always-empty master columns** (`location_*`, Hay House/Nightingale-Conant
  URLs, `reference_url_2`): populate or drop.
- **Nightingale-Conant provenance:** override schema exists; remaining NC
  product URLs missing (`archive/TEMP_NIGHTINGALE_PROVENANCE.md`).

**P2 — Hygiene:**

- Remove deprecated `audio`/`video` item types once unused.
- Add a `LICENSE` (repo is public with none).
- Widen browser tests: all 17 tabs, column chooser, drawer, dark mode.

## 7. House-keeping for every turn

- Keep docs accurate with each push (counts live in `docs/catalogue-meta.json`;
  cite those numbers — do not hand-count).
- Present long results via a committed `TEMP_RESPONSE_*.md` file
  (`TEMP_RESPONSE_AUDIT_2026-08-03.md` is today's log); the chat should stay a
  one-sentence summary plus the `ask_user` question for what is next.
- Update this handoff at the end of each session so the next agent inherits
  your context verbatim.
