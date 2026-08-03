# Product Relationship Expansion Audit

**Reviewed:** 2026-08-03  
**Scope:** Exact master Veritas URLs only; no title-only product match was promoted automatically.

## Result

| Measure | Count |
|---|---:|
| Master records | 308 |
| Master records with a Veritas source URL | 263 |
| Distinct primary Veritas product URLs | 120 |
| Primary product relationships recorded | 263 |
| Reviewed related-material relationships | 4 |
| Total reviewed relationships | 267 |
| Distinct official Veritas products represented | 124 |

Every non-empty `source_url_veritas` in the reconciled master exactly matches a URL in `data/veritas_official_products.csv`. A `primary_product_for_item_part` relationship is therefore recorded for each of the 263 item rows. This makes an existing approved source association queryable in the relationship view; it does not create or duplicate a master item.

Four reviewed `related_material` relationships retain distinct official products without replacing an existing primary source: the 2012 *How to Live Your Life Like A Prayer* interview and the book products for *In the World, But Not of It*, *Truth vs Falsehood*, and *Healing and Recovery*. See `BOOK_RELATIONSHIP_DECISIONS.md` for the bounded book review.

## Deliberately not promoted

The Veritas inventory currently contains **313** unmodeled master/product pairings across **41** distinct products where the inventory’s existing title-based match does not equal the master record’s primary Veritas URL. These are not automatically relationships: title normalization can conflate editions, interviews, books, compilation products, and date-specific Satsang records.

Examples requiring individual evidence review include:

- book or audiobook products sharing a title with a lecture/video item;
- the multi-date Satsang product matches, where a generic normalized title would create many false pairings;
- compilation and later-edition products;
- products with a related but not identical title.

They remain visible in `data/veritas_official_products.csv` and the **Veritas Products** tab. Add one to `data/product_relationships.csv` only after recording its relationship type, review status, and product-page evidence.

## Validation

`build_catalogue_pages.py` validates that every relationship’s master UUID/raw row, Veritas product ID, official URL, title, status, and evidence are internally consistent before publishing `docs/product-relationships.json`.
