# Project State Audit — DocSheet / Hawkins Research Catalogue

**Audited:** 2026-08-03
**Branch audited:** `arena/019fc714-docsheet`
**Repository:** `56eli/docsheet`
**Live Pages:** `https://56eli.github.io/docsheet/`
**Scope:** Repository architecture, data model, reproducibility, generated Pages artifacts, workflows, live-source controls, UX state, documentation, and prioritized engineering backlog.

## Executive summary

DocSheet is a static GitHub Pages catalogue/review workspace backed by a preserved raw CSV, reviewed CSV decision layers, Python generators, committed JSON artifacts under `docs/`, and a Tabulator-based browser UI. The project now uses compact numeric master IDs (`1` through `308`) instead of long UUID values, and all master references in relationships, Veritas mapping decisions, inventories, generated Pages JSON, documentation, and UI labels have been migrated. The spreadsheet UX has been substantially improved with per-view descriptions, readable URL labels, view-specific column ordering/widths, a column chooser, row details drawer, active filter chips, and CSV export browser smoke-test files. Local deterministic checks pass; the only blocked verification remains true browser execution because this sandbox cannot download Chromium, and workflow-file creation because the configured GitHub App lacks `workflows` permission.

## Validation completed in this audit

| Check | Result | Notes |
|---|---|---|
| `python -m py_compile *.py` | Pass | All repository Python scripts compile under Python 3.11.2. |
| `node --check docs/app.js` | Pass | Spreadsheet JavaScript syntax passes. |
| `node --check playwright.config.js` / `node --check tests/csv-export.spec.js` | Pass | Browser smoke-test files parse. |
| `python build_research_master.py --check` | Pass | 308 master items, 66 exclusions, 80 source overrides, 17 manual candidates validated. |
| `python build_catalogue_pages.py --check` | Pass | 344 Everything rows; generated Pages outputs match inputs. |
| `python reconcile_research_master.py --check` | Pass | Reconciliation report matches current compact-ID ledger/master projection. |
| `npx playwright test --list` | Pass | Two CSV export browser tests are discoverable. |
| Playwright browser execution | Blocked locally | `npx playwright install chromium` fails in this sandbox with TLS/network resets. Run in GitHub Actions or another browser-capable environment. |
| Local HTTP smoke check | Pass | `/docs/`, `app.js`, `master.json`, `product-relationships.json`, and `veritas-products.json` returned HTTP 200. |
| Old UUID scan | Pass | No RFC-style UUID values remain in repository text files after migration. |
| Compact master ID integrity | Pass | 308 unique numeric IDs, min `1`, max `308`, no duplicates. |
| `git diff --check` | Pass | No whitespace errors. |
| `python fetch_veritas_catalogue.py --check` from this sandbox | Blocked by external TLS/network | Local direct API call previously failed after retries with TLS EOF; use the review-only workflow artifact path. |

## Current data state

| Layer | Current state | Canonical input / output |
|---|---:|---|
| Raw spreadsheet | 374 data rows | `hawkins archive clone - Sheet1.csv` |
| Migration review | 374 classified rows | `migration_review_ledger.csv` |
| Curated master | 308 CSV + JSON records | `data/research_master_draft.*` |
| Compact master IDs | `1`–`308`, unique | `uuid` field retained for compatibility, displayed as **Master ID** |
| Excluded raw rows | 66 | `data/research_master_exclusions.csv` |
| Approved source overrides | 80 | `data/research_master_source_overrides.csv` |
| Manual research leads | 1 | `data/research_manual_leads.csv` |
| Reviewed, unpromoted manual candidates | 17 | `data/manual_master_candidates.csv` |
| Veritas official inventory | 191 products | `data/veritas_official_products.csv` |
| Approved Veritas mapping decisions | 35 | `data/veritas_mapping_decisions.csv` |
| Hay House official products | 24 products | `data/hayhouse_official_products.csv` |
| Audible official products | 26 products | `data/audible_official_products.csv` |
| Official discovery candidates | 4 records | `data/official_discovery_queue.csv` |
| International edition leads | 38 Pages rows | `data/international_discovery_queue.csv` plus Spanish Audible listings |
| Item-to-product relationships | 301 reviewed relationships | `data/product_relationships.csv` |
| Series-compilation relationships | 7 reviewed relationships | `data/series_compilation_relationships.csv` |
| Everything Pages view | 344 records | `docs/master.json` |
| Original Spreadsheet Pages view | 374 records | `docs/data.json` |

### Master integrity snapshot

| Check | Result |
|---|---:|
| Master IDs | 308 non-empty, 0 duplicates, range `1`–`308` |
| Catalogue codes | 198 non-empty, 0 duplicates |
| Raw row provenance keys | 308 non-empty, 0 duplicates |
| Item types | 198 `lecture`, 23 `book`, 87 blank/unclassified |
| Ownership | 281 `true`, 27 `false` |
| Master Veritas source URLs | 294 non-empty |
| Master Audible source URLs | 8 non-empty |

### Veritas inventory disposition

| Status | Products | Interpretation |
|---|---:|---|
| `matched_by_primary_source` | 147 | Exact URL already used by one or more master records. |
| `matched_by_title` / `matched_by_normalized_title` | 7 | Reviewed non-primary title matches retained by decision overlay. |
| `unique_item` | 9 | Official products not represented by a current master record. |
| `compilation_or_new_edition` | 15 | Broad official candidates; seven annual Highlights have series-level evidence. |
| `unmatched_official_product` | 9 | Date-specific Satsang products with no current master record. |
| `excluded_related_material` | 4 | Explicitly excluded spin-off/promotional material. |

## Architecture and data-flow assessment

```text
Raw Google Sheets CSV
  ├─ process_data.py ───────────────▶ docs/data.json + docs/meta.json
  └─ migration_review_ledger.csv
       ├─ build_research_master.py ─▶ compact master IDs + data/research_master_draft.* + exclusions
       │    ├─ source overrides
       │    └─ manual candidates validated but not promoted
       └─ build_catalogue_pages.py ─▶ docs/master.json and review/product JSON sheets
```

### Strengths

- Raw evidence is preserved and generators do not mutate the source spreadsheet.
- Compact numeric master IDs are stable across rebuilds by raw row number and capped at the approved 1–10000 range.
- All current relationship and inventory references were migrated to compact master IDs.
- Generated master and Pages artifacts have read-only `--check` modes.
- Reconciliation compares committed generated files against the current ledger projection before rebuilding.
- Reviewed source overrides, Veritas mapping decisions, product relationships, and series-compilation relationships are explicit CSV inputs instead of hidden edits in generated JSON.
- Pages review UX now has view descriptions, row counts/type/export metadata, readable source links, column presets, a column chooser, row details, active filter chips, and CSV export smoke-test files.
- The Veritas refresh workflow remains review-only and writes ignored candidate/diff artifacts rather than auto-committing live data.

## UX state

Implemented during this session:

1. **CSV export smoke tests:** `package.json`, `package-lock.json`, `playwright.config.js`, and `tests/csv-export.spec.js` add tests for filtered export and selected-view export filenames.
2. **View descriptions/counts:** each tab shows purpose, row count, type, and export filename.
3. **Readable URL cells:** long URLs render as labels such as “Veritas product” or “Evidence” while preserving raw values in data/export.
4. **Column presets:** important columns are reordered, width-tuned, and frozen per view; compact Master ID columns are slimmer.
5. **Column chooser:** users can hide/show columns per active view and restore all columns.
6. **Row details drawer:** clicking a row opens all fields in a readable side drawer.
7. **Active filter feedback:** search/review filters appear as chips with a clear-all control.

Known UX backlog:

- Disable or clarify session-only editing.
- Add explicit export modes (`filtered`, `all visible`, later `selected`).
- Add copy-to-clipboard affordances for IDs and source URLs.
- Add real browser CI once workflow permissions are available.

## Workflow and deployment state

| Area | State | Audit result |
|---|---|---|
| GitHub Pages | Public, built from `main` → `/docs` | Healthy before branch merge; branch changes deploy after merge. |
| Update Spreadsheet workflow | Manual and CSV-change trigger on `main`; regenerates raw `docs/data.json` and `docs/meta.json` | Functional pattern, but lacks a `process_data.py --check` mode and writes dynamic timestamps. |
| Map Veritas Catalogue workflow | Manual only; review-only candidate/diff artifact | Latest known `main` run `30803991007` fetched a candidate and intentionally failed at compare, requiring artifact review. |
| Pull-request validation | Browser tests exist, but no CI workflow was pushed | Adding `.github/workflows/ci.yml` was blocked by GitHub App `workflows` permission. |
| Branch state | Work pushed to `arena/019fc714-docsheet` | Ready for PR/merge per user request after final documentation update. |

## Security, privacy, and supply-chain assessment

| Area | Assessment | Risk |
|---|---|---|
| Secrets | No application secrets or credentials are required by code; GitHub auth is external to repo. | Low |
| Workflow permissions | Existing workflow permissions are narrow; workflow-file updates are blocked by current GitHub App permissions. | Operational gap |
| External JavaScript/CSS | Tabulator is pinned to `6.5.2` via jsDelivr, but no Subresource Integrity or self-hosted fallback exists. | Medium |
| External fonts | Google Fonts are loaded from the public site. | Low/Medium privacy dependency |
| Python dependencies | `requirements.txt` only specifies `pandas>=2.0`; no upper bound or lock/constraints file. | Medium reproducibility risk |
| Node dependencies | Playwright is locked in `package-lock.json`; browser binaries still download at test runtime. | Medium network/runtime dependency |
| Content Security Policy | Static site has no CSP header/meta policy; inline dark-mode bootstrap currently requires inline script allowance. | Medium hardening gap |
| User editing | Tabulator inline edits are session-only and not persisted; footer warns users. | Medium UX/data-governance risk if reviewers misunderstand |
| Live remote fetch | Veritas API availability/TLS behavior varies by environment; workflow artifact path is the authoritative review route. | Medium operational risk |

## Findings and prioritized backlog

### P0 — PR and merge the current branch

The branch contains a coordinated data migration, generated artifact rebuild, frontend UX improvements, tests, and documentation updates. Merge as a unit so `main` and Pages are internally consistent.

### P1 — Add CI workflow once workflow permissions are available

The test files are committed, but `.github/workflows/ci.yml` could not be pushed because the configured GitHub App lacks workflow-file permission. Add CI when permissions are available: Python compilation, master/pages/reconciliation checks, `node --check`, `npm ci`, `npm run test:e2e`, and static JSON/page smoke tests. Keep live Veritas fetching manual.

### P1 — Review the current live Veritas candidate artifact

Run `30803991007` uploaded artifact `veritas-inventory-review-30803991007` (`artifact_id=8851979247`, digest `3f06b4499dd21840abf995725621f1f7724261f2546e1ae7d6da8c2427f15c3d`). Download outside this sandbox, inspect candidate/diff, and only then update reviewed inventory or mapping decisions.

### P1 — Disable or clarify session-only editing

Inline edits are convenient but can mislead reviewers. Disable editing by default for review sheets or add a stronger unsaved-edits state.

### P1 — Define candidate-promotion workflow

17 evidence-backed manual candidates are durable and validated, but no approved generator path promotes selected candidates into the master with compact ID, catalogue code, ownership, source provenance, and rationale.

### P2 — Formalize schemas and build provenance

Publish machine-readable CSV/JSON contracts and emit source hashes, row counts, schema version, generator commit, and build time.

### P2 — Make the raw spreadsheet pipeline checkable

Add a deterministic `process_data.py --check` mode that compares `docs/data.json` and structural metadata while treating the timestamp as dynamic/expected.

## Recommended next action

Open a PR from `arena/019fc714-docsheet`, review the compact-ID migration and UX changes as one unit, merge it to `main`, then verify the Pages deployment.
