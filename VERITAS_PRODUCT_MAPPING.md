# Veritas Official Product Mapping

**Source:** Veritas Publishing public WordPress product API
**Generated inventory:** `data/veritas_official_products.csv`
**Website inventory tab:** `Veritas Products`
**Mapping date:** 2026-08-03

## Result

| Measure | Count |
|---|---:|
| Published official Veritas product records retrieved | 191 |
| Exact primary-source matches | 147 |
| Remaining title-based matches | 7 |
| Official products with no master match | 9 |
| Products marked as unique or compilations | 24 |
| Products excluded as non-teaching material | 4 |
| Existing migrated master items | 308 |
| Existing Nightingale-Conant discovery candidates | 4 |
| Current “Everything” records (including all approved-source candidates) | 344 |

## Hybrid model implemented

- **Everything** is the broad discovery/master view. It contains the 308 reconciled master items, four Nightingale-Conant candidates, 24 reviewed Veritas unique/compilation products, four Hay House candidates, and four non-Spanish Audible candidates.
- **Veritas Products** is the complete 191-row official commercial-product inventory. It keeps product title, URL, published date, product-category classes, normalized-match count, matched master UUID/title where available, and mapping status.
- A normalized title match is an aid, not a final identity decision. Commercial listings may represent a compilation, edition, set, or related product rather than the same material record.
- Matching products are not duplicated in the Everything view. Reviewed item-to-product assertions are available separately in the **Product Relationships** tab.

## Reviewed candidate products

The 24 products classified as `unique_item` or `compilation_or_new_edition` are included in Everything with their official Veritas URL and a documentation note. Seventeen have reviewed, unpromoted evidence rows in `data/manual_master_candidates.csv` (nine unique products and eight selected compilation/derivative products); they intentionally have no master UUID, catalogue code, ownership value, or master-source relationship until a separate promotion decision is approved. The seven annual Highlights remain broad candidates, with their evidence-backed annual scope recorded in `data/series_compilation_relationships.csv` rather than unsupported per-DVD-part links.

This approach preserves broad discovery coverage while retaining the approved human-review boundary for durable research-master identity data.

## Review workflow

1. Review the existing `unique_item`, `compilation_or_new_edition`, `excluded_related_material`, and `unmatched_official_product` decisions in `data/veritas_official_products.csv` when new evidence appears.
2. For any title that has multiple dated master groups, use the exact Month/Year mapping; never use a title-only match across dates.
3. Add a relationship in `data/product_relationships.csv` only when product-page evidence supports a controlled relationship type; title matching alone is not enough.
4. For a distinct material item, approve type/year/format/title and then assign a UUID and code in a later master build.
5. For an existing material item, attach the official URL/source relationship without creating a duplicate master record.
6. Keep the inventory row regardless of the decision so official commercial provenance remains auditable.

## Reproducibility

`fetch_veritas_catalogue.py` paginates the official API, gives exact primary source URLs precedence, preserves Month/Year when a normalized title spans multiple dated master groups, and then reapplies the product-ID keyed approvals in `data/veritas_mapping_decisions.csv`. Use `python fetch_veritas_catalogue.py --check` to compare live, decision-applied output with the committed inventory.

A prepared revision of the manual **Map Veritas Catalogue** workflow writes a candidate CSV and diff artifact for review rather than auto-committing live inventory changes. The workflow YAML needs a manual GitHub commit before this operational safeguard is active; see [VERITAS_MAPPING_DECISIONS.md](VERITAS_MAPPING_DECISIONS.md) for the decision contract and refresh procedure.
