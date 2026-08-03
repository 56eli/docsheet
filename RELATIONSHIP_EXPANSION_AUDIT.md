# Product Relationship Expansion Audit

**Reviewed:** 2026-08-03  
**Scope:** Exact master Veritas URLs only; no title-only product match was promoted automatically.

## Result

| Measure | Count |
|---|---:|
| Master records | 317 |
| Master records with a Veritas source URL | 304 |
| Distinct primary Veritas product URLs (master `source_url_veritas`) | 157 |
| Masters covered by a reviewed primary relationship | 304 |
| Primary product relationships recorded | 304 |
| Reviewed related-material relationships | 8 |
| Total reviewed relationships | 312 |
| Distinct official products referenced by relationship rows | 165 (157 primary + 8 related) |
| URL-bearing masters **without** a primary relationship | 0 |

Every non-empty `source_url_veritas` in the reconciled master exactly matches a URL in `data/veritas_official_products.csv`, and every URL-bearing master is covered by a reviewed `primary_product_for_item_part` relationship (the invariant is enforced as a hard build failure by `validate_primary_relationship_coverage` in `build_catalogue_pages.py`).

**Coverage history (2026-08-03):** the 11 promoted candidates (master IDs 309–319) were initially added to the master with their official Veritas URL through the reviewed promotion path, but the relationship CSV was not extended — the promotion path does not mint relationship rows. The gap was closed the same day with 11 reviewed primary relationship rows (owner-approved, evidence = the promotion registry); the guard was then promoted from a warning to a hard failure so the gap cannot silently recur.

The eight reviewed `related_material` relationships retain distinct official products without replacing an existing primary source: *A Map of Consciousness* wall chart (1560), the *Truth vs. Falsehood* CD & DVD set (1728), *Healing* audio (1695), *"In the World But Not of It" – Audio* (1661), *The Highest Level of Enlightenment – Audio* (1742), the 2012 *How to Live Your Life Like A Prayer* interview (50491), and the *Power vs. Force* book (50411) and audiobook (1542). See `decisions/BOOK_RELATIONSHIP_DECISIONS.md`, `decisions/SATSANG_MAPPING_DECISIONS.md`, and `decisions/FINAL_TITLE_MATCH_DECISIONS.md` for the review batches.

## Candidate review completion

There are now **zero** unmodeled product/master candidate pairs. Every previously title-only pair has an explicit disposition: an exact primary source, a reviewed `related_material` assertion, or a date-corrected mapping. Date-sensitive Satsang and *A Review of the Work* titles no longer generate cross-date pairings.

Official products that remain outside the master are still retained in `data/veritas_official_products.csv` and the **Veritas Products** tab with their own inventory disposition, such as `unique_item`, `compilation_or_new_edition`, `excluded_related_material`, or `unmatched_official_product`. Any future source refresh must be reviewed before adding a new relationship.

## Validation

`build_catalogue_pages.py` validates that every relationship’s compact master ID/raw row, Veritas product ID, official URL, title, status, and evidence are internally consistent before publishing `docs/product-relationships.json`.
