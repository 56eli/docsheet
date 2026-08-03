# Project State Audit — DocSheet / Hawkins Research Catalogue

**Audited:** 2026-08-03
**Branch:** `arena/019fc6af-docsheet`
**Main synchronization:** includes `cf2f3c4` (`Update Spreadsheet` now commits `docs/` outputs)
**Scope:** Repository state, reproducibility, review data, Pages artifacts, workflows, and documentation.

## Executive summary

The repository is a working static GitHub Pages research catalogue with a preserved raw spreadsheet, a reproducible 308-record curated master, reviewable source/relationship layers, and a public review workspace. All local generator, check, syntax, and HTTP smoke checks pass. The former high-risk Veritas refresh path is protected in code by a 35-row product-ID decision overlay and a review-only candidate/diff workflow synchronized into `main`; one manual Actions run is still needed because this session's GitHub integration cannot dispatch it.

## Validation completed

| Check | Result |
|---|---|
| Python syntax compilation for all repository scripts | Pass |
| `node --check docs/app.js` | Pass |
| `python build_research_master.py --check` | Pass |
| `python build_catalogue_pages.py --check` | Pass |
| `python reconcile_research_master.py --check` | Pass |
| Isolated clean-directory master/pages rebuild | Pass |
| Local HTTP smoke test for review workspace | Pass |
| `git diff --check` | Pass |

## Current data state

| Layer | Current state | Canonical input / output |
|---|---:|---|
| Raw spreadsheet | 374 data rows | `hawkins archive clone - Sheet1.csv` |
| Migration review | 374 classified rows | `migration_review_ledger.csv` |
| Curated master | 308 CSV + JSON records | `data/research_master_draft.*` |
| Excluded raw rows | 66 | `data/research_master_exclusions.csv` |
| Approved source overrides | 80 | `data/research_master_source_overrides.csv` |
| Manual research leads | 1 | `data/research_manual_leads.csv` |
| Reviewed, unpromoted manual candidates | 17 | `data/manual_master_candidates.csv` |
| Veritas official inventory | 191 products | `data/veritas_official_products.csv` |
| Approved Veritas mapping decisions | 35 | `data/veritas_mapping_decisions.csv` |
| Item-to-product relationships | 301 | `data/product_relationships.csv` |
| Series-compilation relationships | 7 | `data/series_compilation_relationships.csv` |
| Everything Pages view | 344 records | `docs/master.json` |

### Veritas inventory disposition

| Status | Products | Interpretation |
|---|---:|---|
| `matched_by_primary_source` | 147 | Exact URL already used by one or more master records. |
| `matched_by_title` / `matched_by_normalized_title` | 7 | Non-primary title matches; their reviewed relationship/disposition is retained separately. |
| `unique_item` | 9 | Official products not represented by a current master record. |
| `compilation_or_new_edition` | 15 | Broad official candidates; seven annual Highlights have series-level evidence. |
| `unmatched_official_product` | 9 | Date-specific Satsang products with no current master record. |
| `excluded_related_material` | 4 | Explicitly excluded spin-off/promotional material. |

## Public review workspace

The Pages application exposes all core review inputs as dedicated searchable/exportable sheets:

- Review Overview
- Master Candidates (17)
- Manual Leads (1)
- Master Exclusions (66)
- Migration Review (374)
- Source Overrides (80)
- Official Discovery (4)
- Veritas Decisions (35)
- Series Compilations (7)
- Product Relationships (301)

Review tabs have humanized headers, status badges, visual grouping, and a status/disposition filter where multiple values exist. The current public Pages deployment still serves `main` → `/docs`; the branch artifacts become public only after merge/deployment.

## Workflow and deployment state

| Area | State | Audit result |
|---|---|---|
| GitHub Pages | Public, built from `main` → `/docs` | Healthy configuration; branch changes are not deployed yet. |
| Update Spreadsheet workflow | `process_data.py` writes and auto-commits `docs/data.json` + `docs/meta.json` on `main` | Path mismatch is resolved in `main` and synchronized into this branch. |
| Map Veritas Catalogue workflow | Review-only revision fetches a live decision-applied candidate and uploads a CSV/diff artifact; does not auto-commit | Synchronized into `main`; requires one manual live artifact verification run. |
| Pull-request validation | No workflow | Gap. Local checks are documented but not enforced remotely. |

## Findings and prioritized backlog

### P0 — Preserve curated Veritas mapping decisions on refresh (code/data complete; manual run pending)

`data/veritas_mapping_decisions.csv` now stores 35 approved non-primary product-ID decisions and is reapplied after deterministic source/title/date matching. `fetch_veritas_catalogue.py --check` compares the live, decision-applied inventory to the committed inventory. The review-only Map Veritas workflow is synchronized into `main`; it writes a candidate CSV and diff artifact, then fails on a diff instead of auto-committing.

**Remaining action:** perform one manual Actions run to verify its artifact behavior against the live API.

### P1 — Add automated CI and release checks

**Issue:** checks pass locally but there is no PR workflow enforcing syntax, reproducibility checks, JSON generation, or review-input validation.

**Required remedy:** Add a read-only CI workflow for `py_compile`, `node --check`, master/pages/reconciliation `--check`, and an HTTP/static-tab smoke test. Keep remote source fetch manual.

### P1 — Define the candidate-promotion workflow

**Issue:** 17 evidence-backed candidates have durable keys and validation, but no approved mechanism promotes selected rows into the master with a UUID, catalogue code, ownership, and source relationship.

**Required remedy:** Add an explicit promotion-decision input and a reviewed generator path. Do not edit generated master CSV/JSON directly.

### P1 — Decide the nine unmatched Satsang products

**Issue:** the date matcher correctly retains nine official Satsang products as inventory-only, but their potential master-candidate status is unresolved.

**Required remedy:** Review identity, type, year, ownership, and scope one record at a time before promotion or exclusion.

### P2 — Formalize schemas and provenance manifest

**Issue:** custom validation exists for several CSVs, but the master, inventory, relationship, candidate, and review files have no versioned machine-readable schema or build manifest.

**Required remedy:** Publish JSON Schemas/CSV contracts and emit source hashes, row counts, schema version, generator commit, and build time.

### P2 — Make raw-spreadsheet freshness verifiable

**Issue:** `process_data.py` deliberately writes a dynamic timestamp to `docs/meta.json`; it has no equivalent `--check` mode, and the currently committed raw metadata timestamp is older than the research-catalogue artifacts.

**Required remedy:** Add a raw-pipeline validation mode that compares deterministic data and structural metadata while treating the timestamp as expected dynamic output.

### P3 — Browser/accessibility and dependency hardening

**Issue:** the site uses CDN-hosted Tabulator and Google Fonts, inline edits are session-only, and browser interaction tests are only local smoke checks.

**Required remedy:** Add automated browser tests for tabs/search/status filter/export; consider self-hosted dependencies or documented CDN fallback; keep the session-only edit warning prominent or disable editing on review sheets.

## Deliberate, accepted boundaries

- The raw spreadsheet is never modified by generators.
- The research master is not an exhaustive work/edition/copy hierarchy.
- Broad Everything candidates are intentionally distinct from promoted master records.
- Commercial inventory entries may be compilations, formats, editions, derivatives, or related material.
- The project is static; Pages exposes committed `docs/` artifacts publicly under the existing policy.

## Recommended next action

Manually run the review-only **Map Veritas Catalogue** workflow once, then implement the read-only CI workflow. This turns the new refresh safeguard into an operationally verified control before any additional candidate promotion or live-source refresh.
