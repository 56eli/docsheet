# Full Project Audit — Arena 019febd6

**Date:** 2026-08-10
**Baseline:** `34f4466573688fea0a4867e7424e55742ddf44f4` (main, merged PR #70)
**Branch:** `arena/019febd6-docsheet`
**Disciplines:** Web Design · Full-Stack Development · Data Engineering
**Verdict:** **Healthy / conditional pass (8.1/10) — no new release-blocking or data-integrity defect found**

## One-sentence summary

At commit `34f4466`, `docsheet` is deterministic and healthy: all six generator `--check` modes pass, 149/149 Python tests pass at 90% statement coverage, 6/6 Node export/module tests pass, the full asset/data delivery contract is byte-consistent, and the published data counts match the documented state exactly.

## What I actually ran (independent verification)

This audit re-ran every verification locally in a fresh virtual environment rather than reciting prior audits.

| Verification | Command | Result |
|---|---|---|
| Python compilation | `python -m py_compile *.py pipeline/*.py` | PASS |
| Raw pass-through lane | `python process_data.py --check` | PASS — `docs/data.json` matches source |
| Master ledger reconciliation | `python reconcile_research_master.py --check` | PASS |
| Curated master builder | `python build_research_master.py --check` | PASS — 363 items; 75 exclusions; 134 overrides; 40 candidates |
| Pages catalogue builder | `python build_catalogue_pages.py --check` | PASS — 363 Everything rows |
| Series-taxonomy mapper | `python map_series_taxonomy.py --check` | PASS — 186 mappings; 0 queued |
| Inventory-mirror sync | `python sync_inventory_mirrors.py --check` | PASS |
| Python unit/contract/style suite | `python -m unittest discover tests` | **PASS — 149/149 in 4.0s** |
| Python coverage | `coverage report` | **PASS — 90% (2,327 stmts, 229 miss; floor 85%)** |
| Node module/export suite | `npm run test:unit` | **PASS — 6/6** |
| JS syntax | `node --check` on app.js, all `docs/js/*.js`, all specs | PASS |
| `npm ci` | — | PASS (0 network issues) |
| Delivery contract (manifest vs files) | sha256 compare of every asset/module/data file | PASS — all 13 hashes match `build-manifest.json` |
| Version strings & footer build ID | grep of `index.html` | PASS — `app-e80fdaf002ce` / `css-3a0ae4223b26` match manifest prefixes |
| Working-tree cleanliness | `git status --short` after all checks | CLEAN (checks are read-only) |
| TODO/FIXME scan | grep across code | none |

## Data-engineering findings (independent counts)

Recomputed directly from the committed published payloads (`docs/master.json`, `docs/data.json`):

- **Curated master:** 363 records — item_type 306 lecture / 41 book / 8 discussion / 7 highlight / 1 other.
- **Formats:** 253 DVD / 32 CD / 32 book / 27 audiobook / 19 streaming.
- **Ownership:** 289 true / 25 false / 49 blank/not-stated.
- **Integrity:** 363/363 unique UUIDs; 363/363 unique proposed filenames; 191 distinct work IDs.
- **Raw lane:** 374 records (incl. 31 decorative separators), pass-through intact.
- All figures match `NEXT_AGENT_HANDOFF.md` §3 exactly.

## Full-stack findings

- Two-lane deterministic architecture (raw pass-through vs curated ledger+overlays) is sound and correctly guarded by six `--check` modes.
- Frontend is modularized (`config/formatters/data-utils/mobile/columns/filter-utils/view-utils/ods-export`) behind a hash-versioned import graph; every local edge carries its target SHA-256 prefix and the delivery contract traverses the full graph.
- Export engine now covers XLSX/ODS/CSV/JSON/TSV with zero runtime dependencies for the binary formats, determinism, formula neutralisation, and humanized headers. Node tests exercise all of these.
- `activateView` has an abort-aware, generic visible fatal-render path for async load failures.

## Web-design / UX / a11y findings

- Coherent neutral design token system (light/dark), restrained REVISION1 block washes via `color-mix` at 8.5%, dense-but-uncluttered desktop columns, and a browse-card mobile default with a spreadsheet escape hatch and independent two-axis scrolling.
- Accessibility fundamentals present: semantic controls, labels/states, roving tab-index table navigation, focus-managed dialogs with focus return, and automated contrast tests.
- Search filters all columns live; footer exposes build revision and row count for verifiable delivery.

## Issues found (all documentation drift — no functional defect)

1. **INSTRUCTIONS.md coverage drift:** stated "Current coverage: **85% total**" while the measured and README-declared value is **90%**. Fixed to 90% (README was already correct). This is the same class of drift the INSTRUCTIONS house-rule warns about.
2. **scoreboard Node-test count drift:** `scoreboard.yml` tests aspect stated "3 Node frontend tests" / "3 Node", but `tests/frontend-modules.test.mjs` now contains **6** tests (session 019febb6 added XLSX + JSON/TSV + ODS coverage). Corrected the two current-state `ai_basis` references to 6. Historical `history.md` records were left intact.

## Remaining risks (unchanged, all owner-gated)

- **Deployment race (P1, owner):** Pages still deploys from legacy `main:/docs` and can publish before CI fails. Switch to the Actions `workflow` build type (`manual-workflow-edits.md`).
- **Owner visual acceptance pending:** live build is hash-verified but explicit owner review of the deployed revision is still recorded as `owner_visual_review_required`.
- **Agent-safe quick wins (unapplied):** add `node --check docs/js/*.js` + ESLint `no-undef` to `ci.yml`.
- **Issue #18 (owner):** owned-flags vs lak.nz Drive cross-check needs owner Drive access.
- **Low-severity CSP debt:** `style-src 'unsafe-inline'` remains; script policy is hash-pinned/SRI.

## Files reviewed

`process_data.py`, `build_research_master.py`, `build_catalogue_pages.py`, `reconcile_research_master.py`, `map_series_taxonomy.py`, `sync_inventory_mirrors.py`, `pipeline/*.py`, `tests/*`, `docs/index.html`, `docs/app.js`, `docs/style.css`, `docs/js/*.js`, `docs/build-manifest.json`, `docs/*.json` (data payloads), `README.md`, `INSTRUCTIONS.md`, `.scoreboard/*`, `NEXT_AGENT_HANDOFF.md`, `SCOREBOARD.md`.
