# Product Relationship Expansion Audit

**Reviewed:** 2026-08-03  
**Scope:** Exact master Veritas URLs only; no title-only product match was promoted automatically.

## Result

| Measure | Count |
|---|---:|
| Master records | 308 |
| Master records with a Veritas source URL | 294 |
| Distinct primary Veritas product URLs | 147 |
| Primary product relationships recorded | 294 |
| Reviewed related-material relationships | 7 |
| Total reviewed relationships | 301 |
| Distinct official Veritas products represented | 154 |

Every non-empty `source_url_veritas` in the reconciled master exactly matches a URL in `data/veritas_official_products.csv`. A `primary_product_for_item_part` relationship is therefore recorded for each of the 294 item rows. This makes an existing approved source association queryable in the relationship view; it does not create or duplicate a master item.

Seven reviewed `related_material` relationships retain distinct official products without replacing an existing primary source: the 2012 *How to Live Your Life Like A Prayer* interview; the book products for *In the World, But Not of It*, *Truth vs Falsehood*, and *Healing and Recovery*; the *Power vs. Force* book and audiobook; and *A Map of Consciousness*. See `BOOK_RELATIONSHIP_DECISIONS.md`, `SATSANG_MAPPING_DECISIONS.md`, and `FINAL_TITLE_MATCH_DECISIONS.md` for the review batches.

## Candidate review completion

There are now **zero** unmodeled product/master candidate pairs. Every previously title-only pair has an explicit disposition: an exact primary source, a reviewed `related_material` assertion, or a date-corrected mapping. Date-sensitive Satsang and *A Review of the Work* titles no longer generate cross-date pairings.

Official products that remain outside the master are still retained in `data/veritas_official_products.csv` and the **Veritas Products** tab with their own inventory disposition, such as `unique_item`, `compilation_or_new_edition`, `excluded_related_material`, or `unmatched_official_product`. Any future source refresh must be reviewed before adding a new relationship.

## Validation

`build_catalogue_pages.py` validates that every relationship’s compact master ID/raw row, Veritas product ID, official URL, title, status, and evidence are internally consistent before publishing `docs/product-relationships.json`.
