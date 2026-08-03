# Series Compilation Relationship Schema

**Status:** Implemented review layer, 2026-08-03  
**Input:** `data/series_compilation_relationships.csv`  
**Generated Pages output:** `docs/series-compilations.json`

## Purpose

A Highlights product can demonstrably draw clips from every lecture in an annual series while still not identifying the exact DVD01/DVD02/DVD03 part that supplied each clip. This schema records the supported **series-level** relationship without inventing per-part inclusion assertions.

It complements `data/product_relationships.csv`, which remains for claims about a specific master item.

## Required fields

| Field | Purpose |
|---|---|
| `relationship_id` | Unique identifier beginning `series-compilation-`. |
| `source_name`, `source_product_id` | Stable official product-inventory reference; the first implementation supports `veritas`. |
| `official_product_url`, `official_product_title` | Exact inventory snapshot validated at build time. |
| `relationship_type` | Must be `compilation_draws_from_series`. |
| `target_series`, `target_year` | Exact master-series scope. |
| `target_month_start`, `target_month_end` | Optional inclusive month range; both are blank or both are valid `01`–`12` values. |
| `included_lecture_count` | Count stated by the source page; validated against distinct lecture titles in the master scope. |
| `review_status`, `reviewed_on` | Reviewed state and ISO review date. |
| `evidence_url`, `evidence_note` | Product-page evidence and concise rationale. |

## Validation behavior

`build_catalogue_pages.py` verifies that the source product exists in the Veritas inventory, the title/URL match it exactly, the target series/year/month scope exists in the master, and the evidenced lecture count equals the distinct lecture titles in that scope. It enriches the Pages output with the target part count and lecture-title list for review.

## Current coverage

The seven Highlights products for 2002–2007 are reviewed series compilations. Their source pages establish clips from all lectures in each named annual scope; the two 2002 products use separate January–June and July–December ranges. No per-DVD-part `compilation_includes_item` relationships are asserted.
