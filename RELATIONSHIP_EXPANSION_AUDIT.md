# Product Relationship Expansion Audit

**Reviewed:** 2026-08-03  
**Scope:** Exact master Veritas URLs only; no title-only product match was promoted automatically.

## Result

| Measure | Count |
|---|---:|
| Master records | 308 |
| Master records with a Veritas source URL | 276 |
| Distinct primary Veritas product URLs | 133 |
| Primary product relationships recorded | 276 |
| Reviewed related-material relationships | 4 |
| Total reviewed relationships | 280 |
| Distinct official Veritas products represented | 137 |

Every non-empty `source_url_veritas` in the reconciled master exactly matches a URL in `data/veritas_official_products.csv`. A `primary_product_for_item_part` relationship is therefore recorded for each of the 276 item rows. This makes an existing approved source association queryable in the relationship view; it does not create or duplicate a master item.

Four reviewed `related_material` relationships retain distinct official products without replacing an existing primary source: the 2012 *How to Live Your Life Like A Prayer* interview and the book products for *In the World, But Not of It*, *Truth vs Falsehood*, and *Healing and Recovery*. See `BOOK_RELATIONSHIP_DECISIONS.md` for the bounded book review. The date-specific Satsang source batch is documented in `SATSANG_MAPPING_DECISIONS.md`.

## Deliberately not promoted

The Veritas inventory currently contains **27** unmodeled master/product pairings across **19** distinct products where the inventory’s existing title-based match does not equal the master record’s primary Veritas URL. These are not automatically relationships: title normalization can conflate editions, interviews, books, compilations, and other related products. Satsang Month/Year matching is now date-aware and no longer contributes a false cross-date candidate set.

Examples requiring individual evidence review include:

- book or audiobook products sharing a title with a lecture/video item;
- compilation and later-edition products;
- products with a related but not identical title.

They remain visible in `data/veritas_official_products.csv` and the **Veritas Products** tab. Add one to `data/product_relationships.csv` only after recording its relationship type, review status, and product-page evidence.

## Validation

`build_catalogue_pages.py` validates that every relationship’s master UUID/raw row, Veritas product ID, official URL, title, status, and evidence are internally consistent before publishing `docs/product-relationships.json`.
