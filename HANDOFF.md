# Handoff — Hawkins Research Catalogue

**Updated:** 2026-08-03
**Branch:** `arena/019fc4ab-docsheet`

## Delivered

- A three-tab/static catalogue interface was implemented in `docs/`:
  - **Everything**: 308 clean migrated records, four initial Nightingale-Conant candidates, and 81 unmatched official Veritas products.
  - **Veritas Products**: 191 official product records fetched through the public Veritas WordPress API, with normalized-title match results.
  - **Hay House Products**: 24 initial official product/format records.
  - **Approved Publishers** and **Original Spreadsheet** remain available as additional tabs.
- The original spreadsheet remains preserved and viewable as the raw table; no source rows were deleted.
- A clean draft research-master dataset is in `data/research_master_draft.csv` and JSON, with 308 candidate material records and UUIDv7 identifiers.
- A row-level migration review ledger, exclusions file, source registry, spreadsheet audit, and mapping reports are committed.
- Veritas mapping is reproducible through `fetch_veritas_catalogue.py`; the `Map Veritas Catalogue` workflow writes `data/veritas_official_products.csv` after manual dispatch.
- Initial Audible inventory contains 23 extracted official entries. Additional Audible titles were identified but not yet added to a dedicated catalogue tab.

## Validation completed

- `node --check docs/app.js`
- `git diff --check`
- Python scripts were syntax checked where applicable.
- Veritas workflow successfully ran after pagination handling was fixed and produced the 191-row inventory.

## Important known limitations

1. **The product catalogues are research inventories, not final deduplicated works.** Commercial products can be compilations, formats, or editions of existing material.
2. **81 Veritas listings are intentionally unreviewed** in the Everything view; see `VERITAS_PRODUCT_MAPPING.md` and `data/veritas_official_products.csv`.
3. **Hay House and Audible mappings are initial passes**, not complete cross-source deduplication. `HAY_HOUSE_MAPPING.md` and `AUDIBLE_MAPPING.md` contain the current boundaries.
4. **The full Audible author page extraction is unfinished.** The initial 23-row CSV omits further discovered entries such as `OM`, several Transcending/Way-to-God products, and Spanish editions.
5. **The GitHub Actions workflow must be dispatched from GitHub’s Actions UI** because the Arena GitHub integration lacks workflow-dispatch permission.
6. **The pre-existing Update Spreadsheet workflow has a path mismatch** (`public/` versus `docs/`) identified in `SPREADSHEET_AUDIT.md`; fix this before relying on automatic raw-data refreshes.
7. This is a static GitHub Pages project. The committed `docs/` content is viewable after merge only when repository Pages is configured to deploy `main` → `/docs`.

## Recommended next steps

1. Merge this PR only after reviewing the broad research-data implications.
2. Open the deployed Pages site and verify all tabs load: Everything, Veritas Products, Hay House Products, Approved Publishers, and Original Spreadsheet.
3. Complete Audible extraction into a dedicated inventory tab and link confirmed Audible products to master records.
4. Build global-discovery queues for the known-but-not-approved international publishers: El Grano de Mostaza, Pandora, Guy Trédaniel, Sheema, Gruppo Editoriale Macro, Les Éditions Ariane, and Yes Publishing.
5. Review the 81 unmatched Veritas products and decide whether each is a unique item, edition/source relation, compilation, or excluded related material.
6. Keep raw source, migration ledger, and reviewed master data separate; do not overwrite the original CSV.
