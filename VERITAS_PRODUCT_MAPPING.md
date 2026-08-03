# Veritas Official Product Mapping

**Source:** Veritas Publishing public WordPress product API
**Generated inventory:** `data/veritas_official_products.csv`
**Website inventory tab:** `Veritas Products`
**Mapping date:** 2026-08-03

## Result

| Measure | Count |
|---|---:|
| Published official Veritas product records retrieved | 191 |
| Normalized-title matches to the migrated research master | 110 |
| Official products requiring review | 81 |
| Existing migrated master items | 308 |
| Existing Nightingale-Conant discovery candidates | 4 |
| Page 1 “Everything” records after adding unreviewed official products | 393 |

## Hybrid model implemented

- **Everything** is the broad discovery/master view. It contains the clean migrated items, the existing Nightingale-Conant discovery candidates, and the 81 unreviewed Veritas products that did not automatically match a migrated item.
- **Veritas Products** is the complete 191-row official commercial-product inventory. It keeps product title, URL, published date, product-category classes, normalized-match count, matched master UUID/title where available, and mapping status.
- A normalized title match is an aid, not a final identity decision. Commercial listings may represent a compilation, edition, set, or related product rather than the same material record.
- Matching products are not duplicated in the Everything view. Their relationship remains visible in the Veritas Products inventory.

## Implemented but unreviewed items

The 81 unmatched official Veritas products have been added to the broad Everything view with the official Veritas URL and a documentation note. They intentionally have no UUID, catalogue code, ownership value, or claimed item type until reviewed.

This approach preserves the instruction to show everything while retaining the approved human-review boundary for durable research-master identity data.

## Review workflow

1. Filter `data/veritas_official_products.csv` by `mapping_status = unreviewed_official_product`.
2. Decide whether each product is a distinct material item, an edition/format of an existing item, a compilation, or a related product.
3. For a distinct material item, approve type/year/format/title and then assign a UUID and code in a later master build.
4. For an existing material item, attach the official URL/source relationship without creating a duplicate master record.
5. Keep the inventory row regardless of the decision so official commercial provenance remains auditable.

## Reproducibility

`fetch_veritas_catalogue.py` paginates the official API and writes the inventory. It handles the API’s final-page HTTP 400 response as end-of-pagination. The GitHub Actions workflow `Map Veritas Catalogue` refreshes the inventory on demand; it does not auto-import products into the approved master.
