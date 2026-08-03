# Project State Audit — DocSheet / Hawkins Research Catalogue

**Audited:** 2026-08-03
**Branch audited:** `arena/019fc714-docsheet`
**Base commit:** `2e952227f034a7407945bd13c218934f6a4e9157` (`main`, `origin/main`)
**Repository:** `56eli/docsheet`
**Live Pages:** `https://56eli.github.io/docsheet/`
**Scope:** Repository architecture, data model, reproducibility, generated Pages artifacts, workflows, live-source controls, security posture, and prioritized engineering backlog.

## Executive summary

DocSheet is a static GitHub Pages catalogue/review workspace backed by a preserved raw CSV, reviewed CSV decision layers, Python generators, and committed JSON artifacts under `docs/`. The local deterministic checks pass, clean-checkout rebuilds reproduce the curated catalogue, and GitHub Pages is built from `main` → `/docs`. The largest immediate operational issue is no longer an unverified workflow path: the review-only **Map Veritas Catalogue** workflow has run on `main`, fetched a live candidate successfully, and failed intentionally because the candidate differs from the reviewed committed inventory; the uploaded artifact now needs human review before any inventory update is accepted. The largest engineering gap is still the lack of CI enforcing the existing local checks.

## Validation completed in this audit

| Check | Result | Notes |
|---|---|---|
| `git status --short --branch` | Pass | Clean at audit start on `arena/019fc714-docsheet`. |
| `python -m py_compile *.py` | Pass | All repository Python scripts compile under Python 3.11.2. |
| `node --check docs/app.js` | Pass | JavaScript syntax passes under Node v22.22.3. |
| `python build_research_master.py --check` | Pass | 308 master items, 66 exclusions, 80 source overrides, 17 manual candidates validated. |
| `python build_catalogue_pages.py --check` | Pass | 344 Everything rows; generated Pages outputs match inputs. |
| `python reconcile_research_master.py --check` | Pass | Reconciliation report matches current ledger/master projection. |
| `git diff --check` | Pass | No whitespace errors. |
| Isolated clean-checkout rebuild | Pass | `process_data.py`, master build, Pages build, and reconciliation rebuild succeeded in a temporary checkout after installing requirements. |
| Local HTTP smoke check | Pass | `/docs/`, `app.js`, `style.css`, `master.json`, `data.json`, and `catalogue-meta.json` all returned HTTP 200 from a local server. |
| GitHub Pages configuration | Pass | GitHub API reports Pages status `built`, source `main` + `/docs`, URL `https://56eli.github.io/docsheet/`. |
| Live Pages fetch | Pass | Public site returned the Hawkins Archive table content. |
| `python fetch_veritas_catalogue.py --check` from this sandbox | Blocked by external TLS/network | Local direct API call failed after retries with TLS EOF; a GitHub Actions run reached the comparison step, so review should use the workflow artifact. |
| Latest `Map Veritas Catalogue` run on `main` | Intentional failure requiring review | Run `30803991007` succeeded through candidate fetch, failed at candidate-vs-reviewed compare, and uploaded the review artifact. Local artifact download hit a GitHub artifact blob EOF. |

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
| Master IDs | 308 non-empty, 0 duplicates |
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

### Relationship disposition

| Relationship layer | Count | Status |
|---|---:|---|
| `primary_product_for_item_part` | 294 | Reviewed |
| `related_material` | 7 | Reviewed |
| `compilation_draws_from_series` | 7 | Reviewed |

## Architecture and data-flow assessment

```text
Raw Google Sheets CSV
  ├─ process_data.py ───────────────▶ docs/data.json + docs/meta.json
  └─ migration_review_ledger.csv
       ├─ build_research_master.py ─▶ data/research_master_draft.* + exclusions
       │    ├─ source overrides
       │    └─ manual candidates validated but not promoted
       └─ build_catalogue_pages.py ─▶ docs/master.json and review/product JSON sheets
```

### Strengths

- Raw evidence is preserved and generators do not mutate the source spreadsheet.
- Generated master and Pages artifacts have read-only `--check` modes.
- Reconciliation compares committed generated files against the current ledger projection before rebuilding.
- Reviewed source overrides, Veritas mapping decisions, product relationships, and series-compilation relationships are explicit CSV inputs instead of hidden edits in generated JSON.
- The Veritas refresh workflow is review-only and writes ignored candidate/diff artifacts rather than auto-committing live data.
- Pages exposes review inputs as first-class searchable/exportable tabs, improving non-developer review access.
- Workflow permissions are reasonably narrow: Map Veritas has `contents: read`; Update Spreadsheet uses write permission only for the auto-commit job.

### Boundaries that should remain deliberate

- The curated master is not a complete work/edition/copy hierarchy.
- Commercial products may be primary items, editions, compilations, related material, or inventory-only leads; title matches alone are not identity proof.
- Manual candidates are intentionally not promoted until a reviewed promotion path exists.
- `docs/` artifacts are generated public deployment outputs; review decisions belong in `data/` CSV inputs and Markdown decision logs.

## Workflow and deployment state

| Area | State | Audit result |
|---|---|---|
| GitHub Pages | Public, built from `main` → `/docs` | Healthy; API reports `built`, live site loads. |
| Update Spreadsheet workflow | Manual and CSV-change trigger on `main`; installs requirements; regenerates `docs/data.json` and `docs/meta.json`; auto-commits those two files | Functional pattern, but lacks a `process_data.py --check` mode and writes dynamic timestamps. |
| Map Veritas Catalogue workflow | Manual only; review-only candidate/diff artifact; latest `main` run fetched candidate and failed at compare | Correctly surfaced a live inventory diff for review. Download/inspect artifact before accepting any changes. |
| Pull-request validation | No CI workflow could be pushed from this sandbox | Branch adds Playwright CSV-export smoke tests and npm scripts; adding `.github/workflows/ci.yml` was blocked because the configured GitHub App lacks `workflows` permission. |
| Branch state | `arena/019fc714-docsheet` is based on current `main` merge commit | No open PRs at audit time. |

## Security, privacy, and supply-chain assessment

| Area | Assessment | Risk |
|---|---|---|
| Secrets | No application secrets or credentials are required by code; GitHub auth is external to repo. | Low |
| Workflow permissions | Existing permissions are narrow for the jobs' purpose. | Low |
| External JavaScript/CSS | Tabulator is pinned to `6.5.2` via jsDelivr, but no Subresource Integrity or self-hosted fallback exists. | Medium |
| External fonts | Google Fonts are loaded from the public site. | Low/Medium privacy dependency |
| Python dependencies | `requirements.txt` only specifies `pandas>=2.0`; no upper bound or lock/constraints file. In this audit, a fresh install resolved to pandas 3.0.5. | Medium reproducibility risk |
| Content Security Policy | Static site has no CSP header/meta policy; inline dark-mode bootstrap currently requires inline script allowance. | Medium hardening gap |
| User editing | Tabulator inline edits are session-only and not persisted; footer warns users. | Medium UX/data-governance risk if reviewers misunderstand |
| Live remote fetch | Veritas API availability/TLS behavior varies by environment; workflow artifact path is the authoritative review route. | Medium operational risk |

## Findings and prioritized backlog

### P0 — Review the current live Veritas candidate artifact

The latest `Map Veritas Catalogue` run on `main` (`30803991007`) reached the candidate-generation step, then failed at the comparison step because the live, decision-applied candidate differs from `data/veritas_official_products.csv`. That failure is intentional and means the safeguard is operating.

**Required remedy:** Download the `veritas-inventory-review-30803991007` artifact from GitHub Actions, inspect `data/veritas_inventory_diff.patch` and `data/veritas_official_products_candidate.csv`, then decide whether to update the reviewed inventory and/or `data/veritas_mapping_decisions.csv`. Do not replace the committed inventory blindly.

### P1 — Add CI workflow once workflow-file permissions are available

**Issue:** This branch adds `package.json`, `playwright.config.js`, and `tests/csv-export.spec.js` for CSV-export browser smoke coverage, but the actual `.github/workflows/ci.yml` file could not be pushed because the configured GitHub App refused workflow-file updates without `workflows` permission. The browser test also could not be executed in this sandbox because Playwright Chromium download failed with TLS/network resets.

**Required remedy:** After reconnecting/updating GitHub permissions for workflow edits, add a read-only CI workflow that runs the existing Python/data checks, `node --check`, `npm ci`, and `npm run test:e2e`; keep live Veritas fetching manual/outside CI.

### P1 — Define the candidate-promotion workflow

**Issue:** 17 evidence-backed manual candidates are durable and validated, but no approved generator path promotes selected candidates into the master with ID, catalogue code, ownership, source provenance, and rationale.

**Required remedy:** Add a promotion-decision input keyed by `candidate_key`; update `build_research_master.py` to generate stable promoted records; keep non-promoted candidates visible in review sheets.

### P1 — Decide the nine unmatched Satsang products

**Issue:** Nine official Satsang products remain `unmatched_official_product`; the date-aware matcher intentionally leaves them inventory-only until identity/scope is reviewed.

**Required remedy:** Review each product for candidate, exclusion, or inventory-only disposition before promotion.

### P2 — Formalize schemas and build provenance

**Issue:** Validation is embedded in scripts and Markdown, but there are no versioned machine-readable contracts or build manifests.

**Required remedy:** Publish JSON Schema/CSV contracts for master, candidates, overrides, inventory decisions, product relationships, and series compilations; emit source hashes, row counts, schema version, generator commit, and build time.

### P2 — Make the raw spreadsheet pipeline checkable

**Issue:** `process_data.py` writes a dynamic `generated_at_utc` timestamp and has no `--check`; this makes raw pipeline freshness hard to verify without changing the working tree.

**Required remedy:** Add a deterministic `--check` mode that compares `docs/data.json` and structural metadata while treating the timestamp as dynamic/expected.

### P2 — Pin or constrain dependencies

**Issue:** `pandas>=2.0` permits future major-version behavior changes; this audit's clean environment installed pandas 3.0.5.

**Required remedy:** Add a constraints/lock strategy or explicit tested version range, then verify workflow caching still works.

### P3 — Browser/accessibility and frontend hardening

**Issue:** Current frontend validation is syntax/static smoke only; CDN dependencies have no SRI/fallback; inline editing may invite confusion.

**Required remedy:** Add browser tests for tabs, search + review filter composition, export, keyboard navigation, dark mode, and load errors; consider self-hosting/pinning assets with SRI; consider disabling edits on review sheets or adding stronger view-level warnings.

## Recommended next action

Start with P0: review the Veritas workflow artifact diff from run `30803991007`, because it is a real live-source divergence already surfaced by the safeguard; after that, implement the P1 read-only CI workflow so every future data or UI change is automatically guarded.
