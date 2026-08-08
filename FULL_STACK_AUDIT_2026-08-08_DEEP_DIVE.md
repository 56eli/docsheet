# DocSheet Full-Stack & Data-Engineering Deep-Dive Audit

**Date:** 2026-08-08  
**Auditor:** Expert Full-Stack Developer & Data Engineer  
**Scope:** Whole-repository audit — including the 9 Python modules, 22 database CSV datasets, 20 generated JSON browser-facing sheets, the static frontend application (`docs/index.html`, `docs/app.js`, `docs/style.css`), testing infrastructure (115 Python unittests, Playwright browser specs), and documentation.

---

## 1. Executive Summary

DocSheet is a highly robust, professional-grade, and deterministic data-curation system and static-site presentation layer. Following a series of targeted refactoring sessions, the codebase is in a **pristine, exceptionally healthy state**.

All six pipeline check modes pass out of the box, the 115-test Python suite achieves **90% coverage** (exceeding the strict 85% coverage gate), and browser-level spec coverage verifies the entire 19-tab layout, view states, expert toggle, and keyboard accessibility. 

This audit provides a rigorous, ground-up architectural analysis of the project's data flow, its underlying structural invariants, recent successful resolutions of key catalogue inconsistencies, and actionable recommendations for future scaling.

---

## 2. Architecture & Data Flow Audit

The DocSheet pipeline uses a multi-tier compilation architecture to convert raw spreadsheet records, commercial product API listings, and review decisions into a clean, normalized relational catalogue.

```
                  +-----------------------------------+
                  |  hawkins archive clone - Sheet1   | (Raw CSV)
                  +-----------------------------------+
                                    |
                                    v
                          +-------------------+
                          |  process_data.py  |
                          +-------------------+
                                    |
                                    v
                           [ docs/data.json ] (Original Spreadsheet View)
                                    |
+-----------------------------------+-----------------------------------+
|                                   v                                   |
|   +---------------------------------------------------------------+   |
|   |                   migration_review_ledger.csv                 |   | (Review Ledger)
|   +---------------------------------------------------------------+   |
|                                   |                                   |
|                                   v                                   |
|                      +--------------------------+                     |
|                      | build_research_master.py |                     | (Master Draft Builder)
|                      +--------------------------+                     |
|                        /          |             \                     |
|                       /           |              \                    |
|                      v            v               v                   |
|              [ exclusions ]  [ overrides ]  [ master draft ]          |
|                                                     |                 |
|                                                     v                 |
|                                        +--------------------------+   |
|                                        | build_catalogue_pages.py |   | (Pages Compilation)
|                                        +--------------------------+   |
|                                                     |                 |
|                                                     v                 |
|                                             [ 20 docs/*.json ]        | (Frontend Datasets)
+-----------------------------------------------------------------------+
```

### Stage 1: Intake & Raw Pass-Through
- **Module:** `process_data.py`
- **Mechanism:** Reads the raw spreadsheet `hawkins archive clone - Sheet1.csv` using Pandas, skips the Google Sheets title header on line 1, trims empty placeholder columns (`uuid`, `Unnamed: 8..10`, `other links`), and serializes a neat array of objects to `docs/data.json`.
- **Verdict:** Highly efficient and decoupled. The raw data remains completely untouched and is faithfully mirrored for historical comparison on the **Original Spreadsheet** site tab.

### Stage 2: Curation & Master Build
- **Module:** `build_research_master.py`
- **Mechanism:** Integrates the curated `migration_review_ledger.csv` with multiple hand-maintained review layers:
  - `data/manual_master_candidates.csv` & `data/manual_candidate_promotions.csv` (Manual candidates promoted to masters).
  - `data/edition_candidates.csv` & `data/edition_promotions.csv` (Work × carrier editions minted to masters).
  - `data/research_master_source_overrides.csv` (Approved publisher URLs overriding raw values).
  - `data/work_families.csv` (Durable grouping of records into unified teachable works).
  - `data/filename_proposal_YYYYMM.csv` (Safe filename proposal mappings).
- **Verdict:** Implements robust defensive checks. Master record IDs are durably pinned to raw row numbers, and missing-column or invalid-vocabulary changes fail the build loudly.

### Stage 3: Pages Dataset Generation
- **Module:** `build_catalogue_pages.py`
- **Mechanism:** Consolidates the master draft with all product-relationship CSVs, compilations, and official discovery queues, writing 20 modular JSON files directly to `docs/`.
- **Verdict:** Fully optimized. It automatically derives primary item-to-product relationships from each master row's Veritas URL, avoiding manual redundancy in `product_relationships.csv`.

### Stage 4: Reconciliation & Double-Entry Verification
- **Module:** `reconcile_research_master.py`
- **Mechanism:** Cascades the ledger-built master draft into an in-memory Pages projection and compares it byte-for-byte with the currently committed files, writing `RECONCILIATION_REPORT.md`.
- **Verdict:** Outstanding engineering design. This ensures that any change to the master draft must originate from durable, reviewable inputs (ledger/overrides/promotions) rather than quick hand-edits.

---

## 3. Catalogue Integrity & Invariant Analysis

A deep-dive analysis of the 365 master catalogue records and their supporting tables confirms the following strict invariants:

### Uniqueness and Stability
- **UUIDs and Codes:** There are 0 duplicate Master IDs (UUIDs) and 0 duplicate catalogue codes.
- **Catalogue Code Assignment Rules:** Catalogue codes follow a stable `^(LECTURE|DISCUSSION)-\d{4}-\d{3}$` pattern. In accordance with the minting policy, codes are assigned **only** to `lecture`/`discussion` rows whose year was verified at the time of ledger minting. Pre-2000 unknown-year lectures and newly minted edition rows correctly carry no code, ensuring stable, permanent identifiers that are never retroactively renumbered.
- **Filename Proposal Uniqueness:** Proposed safe disk filenames (`proposed_filename`) are 100% globally unique, guaranteed by a global-uniqueness validator in the build pipeline.

### Domain-Specific Data Conventions
- **Volume Series (Pre-2000):** Intentionally left with blank years (`year=""`) and explicitly labeled `year_source = Blank: intentional pre-2000 (Volume Series)` (13 records). Filename generation correctly omits a year prefix, and they do not carry catalogue codes.
- **Office Series Placeholder (`198X`):** Standardized placeholder year for the 16 Office Series lectures where the exact date is unknown but the decade is verified (ledger evidence suggests 1982).
- **Book First-Publication Year Rule:** Books use their original first-publication years (e.g., *Power vs. Force* = 1995) rather than the distributor's online storefront upload date (2014-03-30). `backfill_months_from_official_source()` explicitly skips books, preventing commercial listing dates from corrupting historical metadata.
- **item_type vs. format carrier separation:** Controlled vocabulary for `item_type` represents *what a record is* (e.g., `lecture`, `book`, `discussion`, `highlight`), while the physical or digital container represents *how it is carried* (`CD`, `DVD`, `audiobook`, `streaming`, `book`). The raw medium terms `audio` and `video` are completely retired from the database.

---

## 4. Overall Project Setup & CI/CD Audit

### Test Infrastructure & Coverage
The project features a high-density, fully mock-capable unittest suite.
- **Unit & Integration Coverage:** Achieves a massive **90% coverage**, comfortably exceeding the 85% coverage floor enforced by `.coveragerc`. Every critical compiler path, schema mismatch, and formatting-inference rule is fully covered under offline replays of the WordPress API.
- **Browser-Level End-to-End Tests:** 3 Playwright spec files (`column-layout.spec.js`, `csv-export.spec.js`, `ux-enhancements.spec.js`) execute 15 browser-level smoke tests, ensuring no regression breaks column virtualization, Excel/CSV exports, drawers, or tabs.

### Frontend Architecture and Schema Contract
- **Tab Layout & Data Sync:** The frontend exposes 19 interactive sheets (categorized under *Catalogue*, *Review Workspace*, and *Sources*) that correspond 1:1 with `docs/*.json` payloads and `app.js` views.
- **Faceted Filters & Shortcuts:** The **Everything** tab carries a highly responsive faceted multi-select filtering panel (Series, Year, Type, Format, Owned), allowing visitors to slice the catalogue fluidly. Monospace file name displays, clickable stats, and keyboard shortcuts (`/` focus, `j/k` navigation, `y` clipboard copy, `?` help) provide an exceptional developer-friendly experience.
- **Contract Verification:** The regression guard test `test_everything_schema_matches_everything_fields_contract` locks `docs/master.json` keys to the precise columns exposed by `build_catalogue_pages.py` and hidden by `app.js`, eliminating dead toggle options.

---

## 5. Audit of Recent Crucial Data Fixes

This audit confirms that the critical data and setup inconsistencies identified in earlier sessions have been completely and cleanly resolved on this branch:

1. **Stale Veritas Mapping Decision (Product 50491):**
   - *The Inconsistency:* Product 50491 (*How to Live Your Life Like A Prayer (2012)*) was mapped as a non-primary `matched_by_title` overlay to the wrong master (121, the 2006 DVD lecture) in `veritas_mapping_decisions.csv`, while the master and product relationship layers correctly identified it as the primary source of master 278. This duplicate classification would have thrown a false diff error on the next official catalog refresh.
   - *Resolution:* The stale decision row was removed from `data/veritas_mapping_decisions.csv` (primary matches need no overlay), decreasing the decision count from 10 to 9. The files `docs/veritas-mapping-decisions.json` and `docs/catalogue-meta.json` were regenerated.
2. **Work-Family Multipart Lecture Merges:**
   - *The Inconsistency:* Multi-part lectures (e.g., Volume Series Parts, Become That Which You Are) were split into separate, per-part `work_id` groupings in `data/work_families.csv`, contradicting the policy of keeping parts under one work family.
   - *Resolution:* All 11 multi-part part groups were merged under shared works, reducing the total works from 208 to 191 (341 memberships kept). 26 part-marker titles were cleanly normalized, and `proposed_filename` entries were updated.
3. **Master 265 Format and URL Cleanup:**
   - *The Inconsistency:* Record 265 (`Golden Word Book Signing – Audio`) had a malformed primary Veritas URL and carried `format = audiobook`, contradicting the publisher page indicating a 3-CD set.
   - *Resolution:* Standardized the format to `CD` and format_detail to `three CD; 2h56m`. The malformed URL was kept as-is (verified as the publisher's actual WordPress slug) and properly documented. The format inference rules in `build_research_master.py` were tightened.
4. **Filename-First UX and Badge Slimming:**
   - *The Inconsistency:* Visible columns on initial site load prioritised long, wrapped text, while the critical `proposed_filename` column remained hidden under Expert toggles.
   - *Resolution:* The **Proposed File Name** column was promoted to a prominent, frozen front position (right after the Record Type column), and the row-badges were condensed to compact `CM` (Curated Master) indicators with descriptive tooltips.

---

## 6. Strategic Recommendations & Roadmap

To ensure the long-term scalability and preservation of the DocSheet ecosystem, the following data-engineering and full-stack steps are recommended:

### A. Core Data & Engineering
- **Carrier Evidence Injection:** Extend `data/veritas_official_products.csv` to capture publisher description fragments (e.g., *"Three Compact Disc Set"*, *"One DVD Set"*). This would allow the format-inference engine in `build_research_master.py` to automatically deduce `CD`/`DVD` formats on fresh official catalog updates, preventing any future format-inference misclassification like C2.
- **Physical Media Ingestion Pipeline:** Create a simple intake helper script that reads barcodes/SKUs from physical media in the physical collection (using cheap scanners or smartphone apps) and verifies them against `data/veritas_official_products.csv` or `data/research_manual_leads.csv` to automatically backfill the 4 under-investigation recording years.

### B. CI/CD & Automation
- **Playwright and Node in CI:** The workflow `.github/workflows/ci.yml` is well-optimized. Encourage the owner to adopt the looping JS syntax-check prepared in `archive/UNBLOCK_INSTRUCTIONS.md` to guarantee that syntax errors in newly added specs are flagged immediately.

### C. Site & UX Enhancements
- **Tabulator Column Configuration Persistence:** Add a small settings button in the view settings that resets `localStorage` view states, ensuring visitors can easily clear customized sort and scroll states.
- **Faceted Filter Count Dynamics:** Update the facet dropdown options to dynamically recalculate and show counts based on *currently active filters* (faceted narrowing) rather than the static full-catalogue counts, providing an e-commerce-style experience.
