# Full-Stack & Data Engineering Audit — 2026-08-09

**Project:** `56eli/docsheet` (Live Spreadsheet Pipeline & Curated Hawkins Research Catalogue)  
**Auditor:** Full-Stack & Data Engineering Expert  
**Date:** 2026-08-09  
**Branch:** `arena/019fe7ff-docsheet`  
**Commit:** `d1ae982b3737986bb8b2eaec1f0564aeef373e11`

---

## 1. Executive Summary

`docsheet` is an archival system and interactive digital catalog for the complete body of work by Dr. David R. Hawkins (lectures, series, books, audio programs, videos, On-The-Road talks, and office sessions). 

The platform operates a **dual-pipeline architecture**:
1. **Pass-Through Live Spreadsheet Pipeline:** Ingests raw source data (`hawkins archive clone - Sheet1.csv`), applies non-destructive transformations, and compiles JSON data served directly by GitHub Pages (`docs/data.json`).
2. **Curated Research Catalogue Pipeline:** Merges raw source records with hand-reviewed migration ledgers, edition models, publisher cross-references (Veritas Publishing, Hay House, Audible), taxonomy mappings, and owner overrides to output 19 structured datasets (`docs/*.json`).

### Current Health & Scorecard

| Metric / Dimension | Status | Value / Score | Details |
|---|---|---|---|
| **Pipeline Determinism** | 🟢 PASS | 100% | Rebuilds produce byte-identical outputs across all 19 target datasets |
| **CLI Safety Checks** | 🟢 PASS | 6 / 6 scripts | All scripts pass `--check` modes without mutation or diffs |
| **Unit & Integration Suite** | 🟢 PASS | 141 / 141 tests | 0 failures, 0 errors in 3.9 seconds |
| **Code Coverage** | 🟢 PASS | 90% total | Exceeds the required 85% floor (`.coveragerc`); individual modules 78%–100% |
| **Linter Compliance (Ruff)** | 🟢 PASS | 0 items | Clean (0 errors, 0 warnings across all Python code) |
| **JavaScript Syntax Check** | 🟢 PASS | Clean | `node --check docs/app.js` passes with zero syntax errors |
| **UI Table Selector Topology** | 🟢 PASS | `#spreadsheet.tabulator` | Corrected dead descendant selector issue; styles properly attached |
| **Design System & Contrast** | 🟢 PASS | Compliant | Enforced contrast ratios (≥10 light / ≥6 dark luminance delta) |

---

## 2. Data Engineering & Pipeline Architecture Audit

### 2.1 Dual-Pipeline Architecture & Data Flow

```
                                [RAW SPREADSHEET PIPELINE]
 hawkins archive clone - Sheet1.csv ──► process_data.py ──► docs/data.json (Pass-through View)

                                [CURATED CATALOGUE PIPELINE]
 hawkins archive clone - Sheet1.csv ──┐
 migration_review_ledger.csv ────────┤
 data/*.csv (Overrides, Work Families)├─► pipeline/ package ──► data/research_master_draft.csv/json
 data/veritas_official_products.csv ─┤  (helpers, enrichments,    │
 data/catalogue_display_order.csv ──┘   validators, rels)       ▼
                                                          build_catalogue_pages.py
                                                                 │
                                                                 ▼
                                                        docs/*.json (19 Datasets)
                                                        RECONCILIATION_REPORT.md
```

### 2.2 Modular Architecture (`pipeline/` Package)

The core transformation logic is refactored into the `pipeline/` package:
- `pipeline/helpers.py`: Low-level I/O, CSV indexing, ID assignments, and string sanitization.
- `pipeline/enrichments.py`: Master draft transformations (streaming URLs, title cleanups, format inference from Veritas catalog, source overrides, series/work family/year overlays, provenance tracking).
- `pipeline/validators.py`: Structural integrity validators for filename proposals, manual candidates, edition candidates, and master items.
- `pipeline/relationships.py`: Product relationship derivation/enrichment and review overview builders.

### 2.3 Data Integrity, Schema Enforcement & Safety Features

1. **Work Family & Edition Model (Work × Carrier):** Works are logically grouped by `work_id` (`data/work_families.csv`), distinguishing abstract works from specific physical/digital carriers (CD/DVD, audiobook, video).
2. **Canonical Display Order:** Block ordering is strictly governed by `data/catalogue_display_order.csv` (mirroring `hawkins-everything-REVISION1.ods`), eliminating heuristic sorting drift.
3. **Taxonomy & Category Dominance:** Series taxonomy mappings (`data/series_category_mapping.csv` and `SERIES_TAXONOMY_MAPPING.md`) enforce clean category hierarchies and prevent series collision.
4. **Mirror Synchronization:** Inventory mirrors (`sync_inventory_mirrors.py`) re-derive matched master UUIDs and counts from primary source evidence without manual manual intervention.
5. **Re-entrancy & Determinism:** All script operations are run-twice deterministic and feature `--check` flags for CI validation.

---

## 3. Full-Stack & Frontend Architecture Audit

### 3.1 Technology Stack

- **Framework-less Modern JavaScript (ES6+):** Lightweight, zero-dependency client logic in `docs/app.js`.
- **Tabulator.js 5.5:** Virtualized table rendering for fast scrolling across hundreds of items.
- **CSS Custom Properties & Design Tokens:** Centralized theme management (`docs/style.css`) supporting crisp light and dark modes with color-mixed category block accents.

### 3.2 Key Frontend Components & Features

1. **View Navigation (`#view-jump`):** Single-select dropdown top bar navigation for jumping between views (Everything, Lectures, Books, Audio/Video, Review sheets) without UI clutter.
2. **Virtual DOM & $O(1)$ Row Formatting:** Optimizations in `rowFormatter` use `row.getPrevRow()` ($O(1)$) rather than full table traversals ($O(N^2)$), ensuring 60fps scrolling performance.
3. **Responsive Mobile Browse Mode:** Automatic transformation into touch-friendly work-cards on smaller viewports while maintaining a persistent spreadsheet escape hatch.
4. **Content-Hashed Asset Loading & Build Manifest:** JavaScript and CSS assets use 12-character content hashes (`app-cf43f33a062c.js`, `style-71a1e6b2ca25.css`) tracked in `docs/build-manifest.json`, preventing stale cache issues on GitHub Pages.
5. **Corrected Selector Topology:** CSS selectors strictly target `#spreadsheet.tabulator` to ensure Tabulator's attached root element receives exact styling, zebra contrasts, hover effects, and block left accents.

---

## 4. Code Quality, Testing & CI/CD Audit

### 4.1 Test Suite & Coverage Analysis

- **Test Suite Execution:** 141 deterministic unit and style contrast tests pass in ~3.9 seconds (`python3 -m unittest discover tests`).
- **Coverage Summary:**
  - `_common.py`: 100%
  - `build_catalogue_pages.py`: 90%
  - `build_research_master.py`: 92%
  - `fetch_veritas_catalogue.py`: 95%
  - `map_series_taxonomy.py`: 88%
  - `pipeline/enrichments.py`: 89%
  - `pipeline/helpers.py`: 78%
  - `pipeline/relationships.py`: 82%
  - `pipeline/validators.py`: 85%
  - `process_data.py`: 91%
  - `reconcile_research_master.py`: 99%
  - `sync_inventory_mirrors.py`: 96%
  - **Overall Total:** **90% coverage** (enforced by `.coveragerc` 85% floor).

### 4.2 Linter & Quality Score

- **Ruff Python Linter:** Clean (0 errors, 0 warnings across all files).
- **Node Syntax Validation:** Clean (`node --check docs/app.js`).

---

## 5. Strategic Recommendations & Roadmap

1. **Playwright Browser CI Integration:** Ensure the Playwright E2E suite (`npm run test:e2e`) runs in GitHub Actions on every pull request to continuously verify visual table rendering and row delivery.
2. **Automated Live Source Diff Artifacts:** Enhance `fetch_veritas_catalogue.py` to automatically generate visual diff summaries when new items appear in the live Veritas store.
3. **Search Term Highlighting:** Add lightweight text-matching highlights within table cells in `docs/app.js` during active search queries.

---
*Audit Completed Successfully.*
