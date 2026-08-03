# Product Relationship Expansion Audit

**Reviewed:** 2026-08-03  
**Scope:** Exact master Veritas URLs only; no title-only product match was promoted automatically.

## Result

| Measure | Count |
|---|---:|
| Master records | 317 |
| Master records with a Veritas source URL | 304 |
| Distinct primary Veritas product URLs (master `source_url_veritas`) | 157 |
| Masters covered by a reviewed primary relationship | 293 |
| Primary product relationships recorded | 293 |
| Reviewed related-material relationships | 8 |
| Total reviewed relationships | 301 |
| Distinct official products referenced by relationship rows | 154 (146 primary + 8 related) |
| URL-bearing masters **without** a primary relationship | 11 (promoted candidates 309–319) |

Every non-empty `source_url_veritas` in the reconciled master exactly matches a URL in `data/veritas_official_products.csv`. The 293 pre-promotion URL-bearing masters are each covered by a reviewed `primary_product_for_item_part` relationship.

**Coverage gap (2026-08-03):** the 11 promoted candidates (master IDs 309–319) were added to the master with their official Veritas URL through the reviewed promotion path, but `data/product_relationships.csv` was not extended with their primary relationships — the promotion path does not mint relationship rows. The relationship view is therefore incomplete for exactly those 11 records, and `build_catalogue_pages.py` prints a warning while this gap exists. This needs an owner decision: add 11 reviewed primary relationship rows (mechanical: URL equality is already validated) or demote the promotion source URLs until the rows exist.

The eight reviewed `related_material` relationships retain distinct official products without replacing an existing primary source: *A Map of Consciousness* wall chart (1560), the *Truth vs. Falsehood* CD & DVD set (1728), *Healing* audio (1695), *"In the World But Not of It" – Audio* (1661), *The Highest Level of Enlightenment – Audio* (1742), the 2012 *How to Live Your Life Like A Prayer* interview (50491), and the *Power vs. Force* book (50411) and audiobook (1542). See `decisions/BOOK_RELATIONSHIP_DECISIONS.md`, `decisions/SATSANG_MAPPING_DECISIONS.md`, and `decisions/FINAL_TITLE_MATCH_DECISIONS.md` for the review batches.

## Candidate review completion

There are now **zero** unmodeled product/master candidate pairs. Every previously title-only pair has an explicit disposition: an exact primary source, a reviewed `related_material` assertion, or a date-corrected mapping. Date-sensitive Satsang and *A Review of the Work* titles no longer generate cross-date pairings.

Official products that remain outside the master are still retained in `data/veritas_official_products.csv` and the **Veritas Products** tab with their own inventory disposition, such as `unique_item`, `compilation_or_new_edition`, `excluded_related_material`, or `unmatched_official_product`. Any future source refresh must be reviewed before adding a new relationship.

## Validation

`build_catalogue_pages.py` validates that every relationship’s compact master ID/raw row, Veritas product ID, official URL, title, status, and evidence are internally consistent before publishing `docs/product-relationships.json`.
