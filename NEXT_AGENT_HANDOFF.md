# Next-Agent Handoff

**Updated:** 2026-08-10 — Arena session 019feaf6
**Branch for this session:** `arena/019feaf6-docsheet`
**Audited baseline:** `aa1f1b76465e140b9cb62761d365765f0541d7d8`

## Read first

1. `AGENTS.md`
2. `SCOREBOARD.md` and `.scoreboard/scoreboard.yml`
3. `.scoreboard/agent-handoff.md`
4. `.scoreboard/manual-workflow-edits.md`
5. `docs/audits/2026-08-10-arena-019feaf6-full-audit.md`
6. `INSTRUCTIONS.md`

## 1. Current status

DocSheet is a static GitHub Pages catalogue with separate raw and curated data lanes. The data pipeline is healthy. The audited PR #63 baseline had a release-blocking JavaScript regression; this branch now carries a targeted repair with local executable coverage, pending GitHub browser validation.

## 2. P0 repair status

The audited baseline's `docs/js/columns.js:242` called `isExtraEditionRow(row)` without importing it from `docs/js/data-utils.js`. A direct module/formatter probe reproduced:

```text
ReferenceError: isExtraEditionRow is not defined
```

Main CI run `31373716254` independently confirmed end-user impact: **25/25 Playwright specs failed** because no `.tabulator-row` rendered, even though the legacy Pages deployment had already succeeded.

The repair on this branch:

1. imports `isExtraEditionRow` in `columns.js`;
2. removes redundant imports from `app.js` and `mobile.js`;
3. adds `tests/frontend-modules.test.mjs`, which executes the edition formatter and checks the row-373 Extra badge;
4. runs that Node test automatically through `pretest:e2e` before Playwright;
5. adds a focused browser regression, bringing the Playwright suite to 26 specs;
6. refreshes module/app versions, visible build ID, and `docs/build-manifest.json`.

Local Node, Python, coverage, syntax, dependency, and six-check verification passes. PR #64 CI run `31375672387` also passes the Node test and all 26 Playwright specs; merge/deploy plus exact live-build verification remain.

### Other confirmed frontend findings

- Search filtering is live, but extracted column formatters captured the empty string passed at initialization, so later search terms are not highlighted. Pass a query getter or otherwise read current state at formatter execution.
- Nested ES-module imports are unversioned even though `app.js` imports each module with `?v=`. This produces duplicate URL identities and permits stale nested modules; fix the whole import graph or bundle it.
- Ten app lookups have no matching HTML element: `catalogue-intro`, `hero`, `hero-dismiss`, `overview-btn`, `overview-cards`, `review-nav-groups`, `review-nav-toggle`, `series-strip-list`, `show-stats-toggle`, `stats-strip`. Restore and test that interface or remove its dormant JS/CSS.
- The keyboard-shortcuts dialog lacks complete modal focus/Escape behavior.
- Legacy Pages is still `main:/docs` and can deploy before CI; owner steps are in `.scoreboard/manual-workflow-edits.md`.

## 3. Current verified state

| Metric | Current |
|---|---:|
| Raw published rows | 374 (31 blank separators, hidden by default) |
| Curated master | 363 |
| Everything view | **363** |
| Work IDs | 191 |
| Catalogue codes | 278 unique |
| Proposed filenames | 363 unique |
| Item types | 306 lecture / 41 book / 8 discussion / 7 highlight / 1 other |
| Formats | 253 DVD / 32 CD / 32 book / 27 audiobook / 19 streaming |
| Ownership | 312 true / 25 false / 26 blank |
| Exclusions / source overrides | 75 / 134 |
| Manual candidates / leads | 40 / 4 |
| Everything relationships | 340 product relationships, 7 series compilations |
| Veritas / Hay House / Audible | 191 / 29 / 26 |
| International products | 38 |
| Display blocks | 12, complete and dense |

No duplicate master ID, catalogue code, or filename was found. All non-empty master URLs are HTTPS. Display order covers all 363 masters exactly.

## 4. Verification at this audit

```text
PASS  all six generator --check modes
PASS  149/149 Python unit/contract/style tests
PASS  90% Python statement coverage (2327 statements; floor 85%)
PASS  recursive Python compilation
PASS  JavaScript syntax for app, all 7 modules, Node/browser specs
PASS  Node edition-formatter regression (1/1)
PASS  npm audit: 0 vulnerabilities
PASS  pip check
PASS  repaired targeted edition formatter runtime probe
BLOCK local Playwright browser download (sandbox CDN ECONNRESET)
BLOCK live curl probe (sandbox TLS connection restriction)
```

Main CI run `31373716254` proves the audited baseline failed 25/25 browser specs with no rendered rows. PR #64 CI run `31375672387` proves the repair passes the Node regression and 26/26 browser specs. The exact public deployment still needs verification.

## Data pipeline rules

### Raw lane

```text
hawkins archive clone - Sheet1.csv
  -> process_data.py
  -> docs/data.json
```

The CSV has a decorative first row; `process_data.py` reads the real header with `header=1`. The published raw view drops six always-empty columns only.

### Curated lane

```text
migration_review_ledger.csv + reviewed data/*.csv overlays
  -> build_research_master.py
  -> data/research_master_draft.{csv,json}
  -> build_catalogue_pages.py
  -> docs/*.json
```

Never hand-edit generated master or Pages JSON. Owner changes belong in reviewed overlays such as:

- `data/master_year_overrides.csv`
- `data/master_notes_overrides.csv`
- `data/edition_notes.csv`
- `data/catalogue_display_order.csv`
- candidate/promotion/work-family/source-override registries in `data/`

After approved curated-input changes, rebuild in this order:

```bash
python build_research_master.py
python map_series_taxonomy.py
python build_research_master.py
python build_catalogue_pages.py
python reconcile_research_master.py
```

Then run all six checks:

```bash
python process_data.py --check
python reconcile_research_master.py --check
python build_research_master.py --check
python build_catalogue_pages.py --check
python map_series_taxonomy.py --check
python sync_inventory_mirrors.py --check
```

## Important semantics

- `item_type` is content class; `format` is carrier.
- `audio` and `video` are retired item-type/format vocabulary values.
- One row represents one edition/carrier of a work; `work_id` groups editions.
- `uuid` is a stable compact integer ID, not a UUID; retired IDs are never reused.
- Catalogue codes are stable and are not backfilled/renumbered.
- `year=198X` is a reviewed decade placeholder; blank years can be intentional.
- `owned` is tri-state: `true`, `false`, or blank/not stated.
- `notes` is owner-facing only; provenance belongs in `research`/`year_source`.
- `edition_note` is reviewed free text and currently populated for two Power vs Force rows.

See `README.md`, `EDITION_MODEL_PROPOSAL.md`, `PRODUCT_RELATIONSHIP_SCHEMA.md`, `SERIES_COMPILATION_SCHEMA.md`, and `decisions/` for the full contracts.

## Delivery contract

If `docs/app.js`, `docs/style.css`, any `docs/js/*.js` module, `docs/master.json`, `docs/data.json`, or `docs/catalogue-block-map.json` changes, refresh:

- query-string content versions;
- visible footer build ID;
- all matching hashes in `docs/build-manifest.json`.

The existing contract tests validate committed hashes but do **not** prove JavaScript execution. Browser tests and a deployed revision check remain mandatory.

## Open work in priority order

1. Merge/deploy PR #64, verify the exact live build revision/hashes/screenshots, and obtain owner acceptance.
2. Owner: require CI and gate Pages deployment.
3. Repair live search highlighting after extraction.
4. Make nested module cache versioning consistent.
5. Restore or remove dormant hero/stats/review-navigation code.
6. Fix shortcuts-dialog accessibility; add axe-core.
7. Resolve GitHub issue #18 when owner Drive access is available.

Historical session details remain in `archive/`, `docs/audits/`, `.scoreboard/history.md`, and the dated decision records; they are not repeated here.
