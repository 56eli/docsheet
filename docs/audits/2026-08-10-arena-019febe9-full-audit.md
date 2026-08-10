# Full Project Audit — Arena 019febe9

**Date:** 2026-08-10
**Baseline:** `b40133a8ae826d14ee2aed4578f1500165d25650` (main, merged PR #71)
**Branch:** `arena/019febe9-docsheet`
**Disciplines:** Web Design · Full-Stack Development · Data Engineering
**Verdict:** **Healthy / conditional pass (8.1/10) — no release-blocking or data-integrity defect found; four P3 doc/UX findings and one previously documented P2 CI gap recorded**

## One-sentence summary

At commit `b40133a`, `docsheet` is deterministic and healthy: all six generator `--check` modes pass, 149/149 Python tests pass at 90% coverage, 9/9 Node export/module tests pass, the delivery contract is byte-consistent (live deployed `build-manifest.json` byte-identical to the committed one), and every published-data integrity check I recomputed independently passes — with only small documentation/UX drift and the known CI lint gap remaining.

## What I actually ran (independent verification)

Fresh `pandas 3.0.5 / numpy 2.4.6 / coverage 7.15.4` environment, per `requirements-ci.txt`.

| Verification | Command | Result |
|---|---|---|
| Python compilation | `python -m py_compile *.py pipeline/*.py` | PASS |
| Raw pass-through lane | `python process_data.py --check` | PASS |
| Master ledger reconciliation | `python reconcile_research_master.py --check` | PASS |
| Curated master builder | `python build_research_master.py --check` | PASS (363 items) |
| Pages catalogue builder | `python build_catalogue_pages.py --check` | PASS (363 Everything rows) |
| Series-taxonomy mapper | `python map_series_taxonomy.py --check` | PASS (186 mappings; 0 queued) |
| Inventory-mirror sync | `python sync_inventory_mirrors.py --check` | PASS |
| Python suite | `python -m unittest discover tests` | **PASS — 149/149 in 3.9s** |
| Python coverage | `coverage report` | **PASS — 90% (2,327 stmts, 229 miss; floor 85%)** |
| Node module/export suite | `npm run test:unit` | **PASS — 9/9** |
| JS syntax | `node --check` on app.js, all `docs/js/*.js`, all specs | PASS |
| Dependency hygiene | `npm audit` / `pip check` | PASS — 0 vulnerabilities / no broken requirements |
| Delivery contract | sha256 of every asset/module/data file vs `build-manifest.json` | PASS — all 13 hashes match |
| Version strings & footer build ID | `index.html` refs vs manifest prefixes | PASS — `app-36a70a60728c/css-3a0ae4223b26` |
| Live deployment | public `56eli.github.io/docsheet/build-manifest.json` | PASS — **byte-identical** to committed manifest |
| Live-source fetcher | `python fetch_veritas_catalogue.py --check` | BLOCKED by sandbox TLS (documented limitation; offline replay tests cover it) |
| TODO/FIXME/HACK scan | grep across `*.py`/`*.js`/`*.mjs` | none |

## Data-engineering findings (independent recomputation)

Recomputed directly from committed published payloads (`docs/master.json`, `docs/data.json`, `docs/product-relationships.json`, `docs/veritas-products.json`, `data/catalogue_display_order.csv`):

- **Curated master:** 363 records — 306 lecture / 41 book / 8 discussion / 7 highlight / 1 other.
- **Formats:** 253 DVD / 32 CD / 32 book / 27 audiobook / 19 streaming. **Ownership:** 289 true / 25 false / 49 blank.
- **Integrity:** 363/363 unique UUIDs (1–373 with the documented retired gaps); 363/363 unique proposed filenames; 191 distinct `work_id`s; 278 unique `catalog_code`s (all `LECTURE-YYYY-###` / `DISCUSSION-YYYY-###`, including the documented `198X` decade placeholder); every non-empty URL is `https://`; every `month` is 01–12; `item_type` and `format` values all inside the controlled vocabularies.
- **Display order:** 12 blocks, positions dense 1..n within each block, covers all 363 masters exactly (201 + 8 + 22 + 32 + 13 + 16 + 7 + 22 + 6 + 3 + 32 + 1).
- **Block map:** `docs/catalogue-block-map.json` covers all 363 master UUIDs; the map is the source of truth for row/export coloring.
- **Referential integrity:** 340 product relationships all reference existing master UUIDs; relationship types are only `primary_product_for_item_part` / `related_material`; 0 non-https evidence URLs. Veritas mirror columns are consistent: 0 products whose `matched_master_uuids` cannot be resolved to a master, 0 `normalized_title_match_count` mismatches, 0 products with IDs but empty title mirrors.
- **Raw lane:** 374 records incl. 31 decorative separators; pass-through intact.
- **Review lanes:** 75 exclusions, 134 source overrides, 40 manual candidates, 4 manual leads, 5 Veritas mapping decisions, 29 Hay House, 26 Audible, 38 international products, 4 approved publishers. Two intake lanes (Official Discovery, New Work Review) are intentionally empty.

All counts match `NEXT_AGENT_HANDOFF.md` §3 and `docs/catalogue-meta.json`.

## Full-stack findings

- Two-lane deterministic architecture (raw pass-through vs curated ledger+overlays) is sound; every write path has a `--check` twin and the CI workflow runs all six plus the 149-test suite and coverage floor.
- Frontend is modularized behind a hash-versioned ES-module graph (9 modules); every local import edge carries its target SHA-256 prefix and the delivery-contract test traverses the full graph.
- Export engine covers XLSX/ODS/CSV/JSON/TSV with zero runtime dependencies for the binary formats (hand-rolled ZIP + XML), deterministic filenames, formula neutralisation, and REVISION1 block styling; 9 Node tests cover every production block id, the palette, and the `undecided` fallback.
- `activateView` is abort-aware with a monotonic activation token, a visible fatal-render state, and an `aria-busy` lifecycle; `loadCatalogueBlockMap` is awaited before first render so row blocks are correct on the first paint.
- The raw lane and curated lane are properly isolated; the raw updater owns `docs/data.json` while curated builders own `docs/*.json` catalogue payloads.

## Web-design / UX / a11y findings

- Coherent token-driven design system (single `:root` / `:root.dark` block, light + dark palettes), REVISION1 block washes via `color-mix` at 8.5%, work-family striping, frozen record-type/filename rail, measured-pixel column widths, and an independent two-axis mobile Spreadsheet scroller.
- Accessibility fundamentals verified by the green suite: semantic controls, `aria-expanded`/`aria-pressed`/`aria-label` states, roving/focus-managed dialogs with focus return (row details, shortcuts overlay), `aria-live` search status, and automated style-contrast tests.
- The default (reader) layout is spec-locked by `tests/column-layout.spec.js`: Proposed File Name, Item Type, Owned, Notes, Edition, and the six official-source links are visible at first sight; title, series, year-month, and technical columns stay hidden until Expert columns.
- Dark mode is applied pre-first-paint; the CSP keeps scripts hash-pinned/SRI and `connect-src 'self'`.

## Issues found

All non-blocking; ordered by practical priority.

1. **P2 (agent-safe, previously documented, still open): CI has no `docs/js/*.js` syntax check and no `no-undef` lint.** `ci.yml` runs `node --check` on `docs/app.js`, `playwright.config.js`, and `tests/*.spec.js`, but not the 8 extracted modules. Note for precision: `node --check` is syntax-only and would **not** have caught the P0-class ReferenceError (a missing module-scope declaration); ESLint `no-undef` (or `node --check` on a graph-walking harness) would. Add `for m in docs/js/*.js; do node --check "$m"; done` plus an `no-undef` lint pass.

2. **P3 (doc drift): README "visitor-first" paragraph is inverted vs the implemented, spec-asserted layout.** `README.md` claims title/series/date are visible at first sight and proposed file names are hidden under Expert; the executable spec (`column-layout.spec.js`) and `COLUMN_PRESETS.master` assert the opposite (proposed file name is the frozen first-sight rail; title/series/year-month are Expert-hidden). Fixed in this session to describe the real layout.

3. **P3 (doc drift): `.scoreboard/agent-handoff.md` "Current data state" ownership numbers are stale.** It reports 282 true / 13 false / 68 blank — the intermediate state of session 019feb3e before the 019feb8c revert — while the same file's own bullet, `history.md`, `SCOREBOARD.md`, `NEXT_AGENT_HANDOFF.md`, and the published payloads all say 289 true / 25 false / 49 blank. Fixed in this session.

4. **P3 (UX): the shortcuts-help overlay advertises `←` / `→` "Switch tabs", but no handler exists.** `handleGlobalShortcuts` in `app.js` implements `/`, `j`, `k`, `y`, `?` only; the arrow-key roving block was removed with the `.dataset-tab` tab bar cleanup (019feb3e) and the help entry was left behind. **Fixed in this session:** the stale entry was removed from the overlay and a regression guard (`expect(dialog).not.toContainText('Switch tabs')`) was added to `tests/ux-enhancements.spec.js`; app.js content version, footer build ID, and manifest hash refreshed (delivery contract green).

5. **P3 (robustness): the `getRowBlockId` fallback classifier cannot reproduce the block map.** If `catalogue-block-map.json` fails to load, the fallback (series/type rules in `formatters.js`) mapped only 9 blocks and could not express `lectures-2002-2011` — the largest block (201 rows) — so those rows and the ODS/XLSX exports would silently lose their REVISION1 grouping, and a handful of other rows would receive *wrong* fallback colors. **Fixed in this session:** a generated snapshot module `docs/js/block-map-fallback.js` (uuid→block for all 363 approved display-order rows) is embedded as the fallback, and a Node test asserts `getRowBlockId` equals the approved CSV for every row (fallback == map for all 363); the module is registered in the delivery contract.

## Remaining risks (unchanged, owner-gated)

- **Deployment race (P1, owner):** Pages still deploys from legacy `main:/docs` and can publish before CI fails; the reviewed Actions-gated `deploy_pages.yml` is ready in `.scoreboard/manual-workflow-edits.md`.
- **Owner visual acceptance pending:** the live build is hash-verified but `acceptance: owner_visual_review_required` remains.
- **Issue #18 (owner):** owned-flags vs lak.nz Drive cross-check needs owner Drive access.
- **Low-severity CSP debt:** `style-src 'unsafe-inline'` remains; script policy is hash-pinned/SRI.

## Files reviewed

`process_data.py`, `build_research_master.py`, `build_catalogue_pages.py`, `reconcile_research_master.py`, `map_series_taxonomy.py`, `sync_inventory_mirrors.py`, `fetch_veritas_catalogue.py`, `pipeline/*.py`, `tests/*`, `docs/index.html`, `docs/app.js`, `docs/style.css`, `docs/js/*.js`, `docs/build-manifest.json`, `docs/*.json` (payloads), `data/catalogue_display_order.csv`, `.github/workflows/ci.yml`, `README.md`, `INSTRUCTIONS.md`, `SCOREBOARD.md`, `.scoreboard/*`, `NEXT_AGENT_HANDOFF.md`.
