# Next-Agent Handoff

**Updated:** 2026-08-10 — Arena session 019feb3e (post-PR-#64, live-verified audit)
**Branch for this session:** `arena/019feb3e-docsheet`
**Audited baseline:** `54b37f7` ("Merge PR #64") — current `main` HEAD and current live deployment

## Read first

1. `AGENTS.md`
2. `SCOREBOARD.md` and `.scoreboard/scoreboard.yml`
3. `.scoreboard/agent-handoff.md`
4. `.scoreboard/manual-workflow-edits.md`
5. `docs/audits/2026-08-10-arena-019feb3e-full-audit.md`
6. `INSTRUCTIONS.md`

## 1. Current status

DocSheet is a static GitHub Pages catalogue with separate raw and curated data lanes. The data pipeline is healthy and **the previously release-blocking frontend defect is now fixed, merged to `main`, and verified live** (session 019feb3e). PR #64 (`54b37f7`) is deployed (Pages built @10:34Z), main CI run `31379726756` is green, and the public `build-manifest.json` + deployed `columns.js` are byte-verified to carry the P0 fix. Effective score is **8.1/10, gate conditional_pass** — conditional only on the owner switching Pages to CI-gated (Actions) deployment and giving explicit visual acceptance. The remaining engineering work is preventive (CI module syntax-check, ESLint `no-undef`, removal of residual `.dataset-tab` dead code).

## 2. Incident and completed frontend work

The baseline's `docs/js/columns.js` called `isExtraEditionRow(row)` without importing it. Main CI run `31373716254` failed **25/25 Playwright specs** because no row rendered, after legacy Pages had already deployed the commit.

This branch now:

1. restores the missing import and removes redundant imports;
2. executes edition formatting in Node and browser regressions;
3. removes all 10 absent-ID overview/stats/review-nav paths and 411 net lines;
4. completes shortcuts-modal labelling, focus entry/trap, Escape close, and focus restoration;
5. passes a live search-query getter into formatters so highlights update on every redraw;
6. applies target-hash query versions to every local ES-module edge;
7. traverses the full import graph in `FrontendDeliveryContractTests`;
8. refreshes module/app/style hashes, visible build ID, and the build manifest.

Local checks pass. PR #64 CI run `31378465750` passes 149 offline, 3 Node, and **28/28 Playwright tests**. Merge/deploy plus exact live-build verification remain.

### Remaining findings

- Legacy Pages is still `main:/docs` and can deploy before CI; owner steps are in `.scoreboard/manual-workflow-edits.md`.
- Axe/Lighthouse automation is optional follow-up, not a current release blocker.
- Issue #18 still needs owner Drive access.

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
PASS  Node frontend regressions (3/3)
PASS  full ES-module import-graph hash contract
PASS  npm audit: 0 vulnerabilities
PASS  pip check
PASS  repaired targeted edition formatter runtime probe
BLOCK local Playwright browser download (sandbox CDN ECONNRESET)
BLOCK live curl probe (sandbox TLS connection restriction)
```

Main CI run `31373716254` proves the audited baseline failed 25/25 browser specs with no rendered rows. PR #64 CI run `31378465750` proves the repaired/cleaned frontend passes 3/3 Node and 28/28 browser tests. The exact public deployment still needs verification.

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

1. **Owner:** switch Pages from legacy `main:/docs` to the Actions `workflow` build type so deploy depends on a green `Validate data pipeline and site` job (`.scoreboard/manual-workflow-edits.md`). This is the single remaining delivery risk.
2. **Owner:** give explicit visual acceptance of the now-live, byte-verified build.
3. **Agent-safe quick wins:** add `node --check docs/js/*.js` + ESLint `no-undef` to `ci.yml`; remove the residual `.dataset-tab` dead code (4 `app.js` lookups + CSS, zero matching elements).
4. Optionally add axe-core/Lighthouse automation; raise `helpers.py`/`relationships.py` coverage.
5. Resolve GitHub issue #18 when owner Drive access is available.

Historical session details remain in `archive/`, `docs/audits/`, `.scoreboard/history.md`, and the dated decision records; they are not repeated here.
