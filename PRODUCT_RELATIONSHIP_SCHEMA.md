# Product Relationship Schema

**Status:** Implemented review layer, seeded 2026-08-03  
**Input:** `data/product_relationships.csv`  
**Generated Pages output:** `docs/product-relationships.json`

## Purpose

A research-master item and a commercial product are not interchangeable. One product can cover several item parts; a separately recorded interview, edition, compilation, or related product can have the same or a similar title without being the same material. This table records an explicit, reviewable relationship without duplicating a master item or replacing the item’s primary source URL.

The table is intentionally separate from the flat research-master schema. It can be extended to other sources after each source has a stable official product inventory and a validation rule.

## Required fields

| Field | Rule | Purpose |
|---|---|---|
| `relationship_id` | Unique string beginning `rel-` | Stable identifier for this master-to-product assertion. |
| `master_uuid` | Existing compact master ID | The catalogue item being related; the column name is retained for compatibility. |
| `raw_row_number` | Must match the referenced master row | Human-readable provenance cross-check. |
| `source_name` | `veritas` for the initial implementation | Identifies the official inventory. |
| `source_product_id` | Existing source-inventory product ID | Stable commercial-product reference. |
| `official_product_url` | Exact inventory URL | Source snapshot and clickable evidence. |
| `official_product_title` | Exact inventory title | Source snapshot and validation cross-check. |
| `relationship_type` | See controlled values below | States what is known about the relationship. |
| `review_status` | `reviewed`, `pending`, or `rejected` | Separates evidence from unresolved matches. |
| `reviewed_on` | `YYYY-MM-DD` for `reviewed` rows | Review traceability. |
| `evidence_url` | HTTPS URL | Direct evidence supporting the assertion. |
| `evidence_note` | Non-empty text | Concise reason the relationship exists. |

## Controlled relationship types

| Value | Use when |
|---|---|
| `primary_product_for_item_part` | A product directly represents or sells the referenced top-level item part. Its URL must equal the master record’s Veritas URL. |
| `same_material_edition` | Evidence shows the same material in a different edition or format. |
| `compilation_includes_item` | A compilation demonstrably includes the item. |
| `related_material` | A distinct product is materially related by title/topic/source but is not the same catalogue item. |
| `unresolved` | A candidate relationship is recorded for review without asserting identity. |

## Current reviewed coverage

Every non-empty master `source_url_veritas` is represented as a reviewed `primary_product_for_item_part` relationship after exact URL validation against the committed Veritas inventory. This currently yields 294 item-to-product relationships across 147 distinct primary products; a single product can therefore be related to multiple top-level DVD/CD parts without duplicating an item.

The 2006 *Live Your Life Like a Prayer* product is one such three-disc lecture set, with a reviewed primary relationship for each of the master’s DVD01, DVD02, and DVD03 records. Seven reviewed `related_material` records preserve distinct official products without overwriting a primary source. The reviewed book, Satsang, and final title-match batches are documented in `BOOK_RELATIONSHIP_DECISIONS.md`, `SATSANG_MAPPING_DECISIONS.md`, and `FINAL_TITLE_MATCH_DECISIONS.md`.

See `RELATIONSHIP_EXPANSION_AUDIT.md` for the complete validated coverage and inventory-only disposition boundary.

## Validation and build behavior

`build_catalogue_pages.py` validates every relationship against the current master and Veritas inventory before it writes Pages JSON. It rejects duplicate IDs, unknown master IDs or product IDs, source URL/title drift, invalid controlled values, missing evidence, invalid reviewed dates, and an attempt to make a primary relationship disagree with the master’s primary Veritas URL.

Run:

```bash
python build_catalogue_pages.py
python build_catalogue_pages.py --check
```

The Pages site exposes the generated data in the **Product Relationships** tab. Adding a different source requires adding a stable official inventory plus equivalent validation; it must not bypass this review layer.
