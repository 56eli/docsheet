# Temporary Analysis: Everything View + All Pages Purposes (2026-08-03)

**Task completion summary:** Analyzed Everything view and all 17+ pages; confirmed intentional mixed provenance design and that all review sheets serve coherent, documented purposes.

## 1. "Everything" sheet — does it show every unique item?

**Yes — that is exactly how it is intentionally handled right now.**

From `build_catalogue_pages.py`:
- The `master.json` (Everything tab) **deliberately combines**:
  - All 317 curated master records (`record_type = "master"`)
  - + official candidate rows from:
    - `official_discovery_queue.csv` (`candidate_discovery`)
    - Unreviewed/unique/compilation Veritas products (`candidate_veritas`)
    - Unreviewed Hay House products (`candidate_hayhouse`)
    - Unreviewed Audible products (`candidate_audible`)
- Every row carries an explicit `record_type` provenance label so reviewers can instantly distinguish curated vs. candidate.
- The generator comment states: *"The Everything sheet intentionally shows curated master records next to official product candidates so they can be compared."*
- Current count (from `catalogue-meta.json`): 353 Everything rows (317 master + 36 candidates).
- Only `master` rows are considered the actual catalogue; candidates are shown for review/comparison only.

This design supports the review workflow (compare official listings against the master without polluting the master itself).

## 2. Review of all other pages / tabs

All 17+ views have **sensical, coherent purposes** aligned with the research-catalogue workflow. None appear redundant or contradictory:

| View | File | Purpose (from code + VIEW_DETAILS) | Sensical? |
|------|------|------------------------------------|---------|
| Everything | `master.json` | Curated masters + official candidates side-by-side for comparison | Yes (explicit design goal) |
| Review Overview | `review-overview.json` | Index of all review sheets, counts, purposes, source files | Yes (navigation / state dashboard) |
| Master Candidates | `manual-candidates.json` | Evidence-backed official candidates awaiting explicit promotion decision | Yes (promotion queue) |
| Manual Leads | `manual-leads.json` | Manual edition/copy/research leads outside the master | Yes (research leads) |
| Master Exclusions | `master-exclusions.json` | Raw rows intentionally excluded + disposition/reason | Yes (provenance ledger) |
| Migration Review | `migration-review.json` | Raw-row provenance and proposed migration metadata | Yes (migration audit trail) |
| Source Overrides | `source-overrides.json` | Approved official source links applied after original ledger | Yes (post-migration corrections) |
| Official Discovery | `official-discovery.json` | Nightingale-Conant + platform candidates awaiting source/relationship review | Yes (discovery queue) |
| Veritas Decisions | `veritas-mapping-decisions.json` | Approved product-ID mapping dispositions re-applied on every refresh | Yes (refresh guard) |
| Veritas Products | `veritas-products.json` | Full reviewed official Veritas inventory + mapping status | Yes (official inventory view) |
| Product Relationships | `product-relationships.json` | Reviewed item-to-product assertions (primary/related/edition/etc.) | Yes (relationship evidence layer) |
| Series Compilations | `series-compilations.json` | Evidence-backed annual Highlights / compilation links (series-level, not per-DVD) | Yes (compilation evidence) |
| Hay House Products | `hayhouse-products.json` | Official Hay House listings for source discovery/deduplication | Yes (publisher inventory) |
| Audible Products | `audible-products.json` | Official Audible listings for source discovery/edition review | Yes (platform inventory) |
| International Products | `international-products.json` | Non-English / market-specific leads | Yes (international scope) |
| Approved Publishers | `publishers.json` | Registry of approved sources + roles | Yes (source authority) |
| Original Spreadsheet | `data.json` | Immutable raw source for provenance checks | Yes (raw evidence) |

**Overall verdict:** The page set is well-designed for a living research catalogue. Everything is the comparison workspace; the rest are focused review / inventory / relationship sheets. No obvious duplication or nonsensical tabs. The `record_type` mechanism and explicit provenance notes keep the mixed view honest.

**Next engineering notes (for owner):**
- The design correctly prevents candidates from silently becoming masters.
- All review inputs are committed CSVs; generated JSONs are read-only.
- Current state (353 Everything rows) matches the documented 317 master + 36 candidates.

This file is temporary and can be deleted after review.