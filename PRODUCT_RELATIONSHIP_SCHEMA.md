# Product Relationship Schema

**Status:** Implemented review layer; primary rows derived since 2026-08-04  
**Input:** `data/product_relationships.csv` (non-primary rows only)  
**Generated Pages output:** `docs/product-relationships.json`

## Purpose

A research-master item and a commercial product are not interchangeable. One product can cover several item parts; a separately recorded interview, edition, compilation, or related product can have the same or a similar title without being the same material. The relationship layer records an explicit, reviewable relationship without duplicating a master item or replacing the item’s primary source URL.

**Since 2026-08-04 the primary link is no longer hand-maintained.** Every
master record already carries its primary Veritas product URL in
`source_url_veritas`, so `build_catalogue_pages.derive_primary_relationships`
derives the `primary_product_for_item_part` rows automatically from the
master. `data/product_relationships.csv` therefore holds **only the genuinely
distinct non-primary relationships** (`related_material`).

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

**Invariant (by construction):** every master with a non-empty
`source_url_veritas` automatically yields one reviewed
`primary_product_for_item_part` relationship (derived by
`derive_primary_relationships` after exact URL validation against the
committed Veritas inventory). There is no separate coverage guard to
maintain — the rows exist whenever the master's URL exists. The historical
gap (the 11 promoted candidates 309–319, whose promotion path did not mint
relationship rows) is moot: those masters now carry their URL and therefore
derive their primary relationship automatically.

As of 2026-08-08 the relationship layer renders **343 rows = 336 derived
primary + 7 reviewed `related_material`** across 187 distinct products. The
2006 *Live Your Life Like a Prayer* product is one such three-disc lecture
set, with a primary relationship for each of the master’s DVD01, DVD02, and
DVD03 records (all three derived from the same master URL). Seven reviewed
`related_material` records preserve distinct official products without
overwriting a primary source. The reviewed book, Satsang, and final title-match
batches are documented in `decisions/BOOK_RELATIONSHIP_DECISIONS.md`,
`decisions/SATSANG_MAPPING_DECISIONS.md`, and `decisions/FINAL_TITLE_MATCH_DECISIONS.md`.

See `archive/RELATIONSHIP_EXPANSION_AUDIT.md` for the complete validated coverage and inventory-only disposition boundary.

## Validation and build behavior

`build_catalogue_pages.py` validates every relationship against the current master and Veritas inventory before it writes Pages JSON. It rejects duplicate IDs, unknown master IDs or product IDs, source URL/title drift, invalid controlled values, missing evidence, invalid reviewed dates, and an attempt to make a primary relationship disagree with the master’s primary Veritas URL.

Run:

```bash
python build_catalogue_pages.py
python build_catalogue_pages.py --check
```

The Pages site exposes the generated data in the **Product Relationships** tab. Adding a different source requires adding a stable official inventory plus equivalent validation; it must not bypass this review layer.
