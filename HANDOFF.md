# Handoff — Hawkins Research Catalogue

**Updated:** 2026-08-03
**Branch:** `arena/019fc66d-docsheet`

## Delivered

- A multi-view static catalogue interface was implemented in `docs/`:
  - **Everything**: 308 reconciled master records, four Nightingale-Conant candidates, 28 reviewed unique/compilation Veritas products, four Hay House candidates, and four non-Spanish Audible candidates.
  - **Veritas Products**: 191 official product records fetched through the public Veritas WordPress API, with normalized-title match results.
  - **Hay House Products**: 24 initial official product/format records.
  - **Audible Products**: Official Audible product entries fetched and mapped, fully populating the Audible integration.
  - **Approved Publishers** and **Original Spreadsheet** remain available as additional tabs.
- The original spreadsheet remains preserved and viewable as the raw table; no source rows were deleted.
- A reconciled research-master dataset is in `data/research_master_draft.csv` and JSON, with 308 candidate material records and stable UUIDv7 identifiers.
- A row-level migration review ledger, exclusions file, source registry, spreadsheet audit, and mapping reports are committed.
- The P0 reconciliation now produces a consistent 308-record research master and 66-row exclusions output; 49 approved Veritas/Audible source associations are preserved through `data/research_master_source_overrides.csv`, while unresolved manual edition/copy leads remain outside the master in `data/research_manual_leads.csv`.
- A validated `data/product_relationships.csv` layer and Product Relationships site tab now distinguish official products from master items; it records 263 exact primary Veritas item/product associations plus four reviewed related-material products. See `PRODUCT_RELATIONSHIP_SCHEMA.md`, `RELATIONSHIP_EXPANSION_AUDIT.md`, and `BOOK_RELATIONSHIP_DECISIONS.md`.
- Veritas mapping is reproducible through `fetch_veritas_catalogue.py`; the `Map Veritas Catalogue` workflow writes `data/veritas_official_products.csv` after manual dispatch.
- **Global Discovery Queue**: A dedicated queue (`data/international_discovery_queue.csv`) was created for the known-but-not-approved international publishers, seeded with early title extractions. These are exposed in a new **International Editions** UI tab.

## Validation completed

- `node --check docs/app.js`
- `git diff --check`
- Python scripts were syntax checked where applicable.
- Veritas workflow successfully ran after pagination handling was fixed and produced the 191-row inventory.

## Important known limitations

1. **The product catalogues are research inventories, not final deduplicated works.** Commercial products can be compilations, formats, or editions of existing material.
2. **Veritas listings are now fully mapped** (see `VERITAS_PRODUCT_MAPPING.md` and `data/veritas_official_products.csv`).
3. **Hay House and Audible mappings are initial passes**, not complete cross-source deduplication. `HAY_HOUSE_MAPPING.md` and `AUDIBLE_MAPPING.md` contain the current boundaries.
4. **The pre-existing Update Spreadsheet workflow has a path mismatch** (`public/` versus `docs/`) identified in `SPREADSHEET_AUDIT.md`; **this has been fixed** on the main workflow branch.
5. This is a static GitHub Pages project. The committed `docs/` content is viewable after merge only when repository Pages is configured to deploy `main` → `/docs`.

## Recommended next steps

1. Merge this PR only after reviewing the broad research-data implications.
2. Open the deployed Pages site and verify all tabs load: Everything, Veritas Products, Product Relationships, Hay House Products, Audible Products, International Editions, Approved Publishers, and Original Spreadsheet.
3. Complete Audible extraction into a dedicated inventory tab and link confirmed Audible products to master records. (Completed)
4. Build global-discovery queues for the known-but-not-approved international publishers: El Grano de Mostaza, Pandora, Guy Trédaniel, Sheema, Gruppo Editoriale Macro, Les Éditions Ariane, and Yes Publishing. (Completed)
5. Review the 81 unmatched Veritas products and decide whether each is a unique item, edition/source relation, compilation, or excluded related material. (Completed)
6. Keep raw source, migration ledger, and reviewed master data separate; do not overwrite the original CSV.
