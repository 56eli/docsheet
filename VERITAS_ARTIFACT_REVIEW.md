# Veritas Artifact Review — Run 30803991007

**Reviewed:** 2026-08-03
**Workflow:** `Map Veritas Catalogue`
**Run:** `30803991007` (branch `main`, head SHA `2e95222`)
**Artifact:** `veritas-inventory-review-30803991007` (ID `8851979247`, 16,922 bytes)
**Reviewed by:** diff supplied by the repository owner and verified offline against the committed inventory.

## Outcome

**The live Veritas catalogue has not changed.** The refresh reported no new
products, no delisted products, and no upstream title, date, URL, category, or
product-ID edits. All 191 products are unchanged.

The diff contained **exactly six changed lines**, each altering **one derived
field** — `normalized_title_match_count` — from `0` to `1`:

| Product ID | Title | Was | Should be |
|---:|---|---:|---:|
| 53062 | In the World But Not Of It: Transforming Everyday Experience… | 0 | 1 |
| 50491 | How to Live Your Life Like A Prayer (2012) | 0 | 1 |
| 50411 | Power vs. Force: The Hidden Determinants of Human Behavior book | 0 | 1 |
| 50398 | Truth vs. Falsehood: How to Tell the Difference (Book) | 0 | 1 |
| 50432 | A Map of Consciousness | 0 | 1 |
| 1542 | Power vs. Force Audio Book | 0 | 1 |

All six are `matched_by_title` rows carrying exactly one master ID.

## Root cause — a committed-data defect, not an upstream change

`normalized_title_match_count` is a **derived** field: it must always equal the
number of IDs in `matched_master_uuids`. In these six rows the committed
inventory claimed `0` while naming one master ID — an internal contradiction.

The cause is ordering inside `apply_mapping_decisions()` in
`fetch_veritas_catalogue.py`. When an approved decision is applied, the function
sets `matched_master_uuids`, `matched_master_titles`, **and** recomputes
`normalized_title_match_count` from the approved ID list. The committed file had
been written at a point where the overlay's ID assignment was recorded but the
recomputed count was not carried through, so the count kept its pre-overlay
value of `0`.

The live refresh then computed the field correctly and the guard flagged the
difference. **The workflow behaved exactly as designed** — it surfaced a real
inconsistency in our own committed data.

### Verification performed

Re-applying the 35 approved decisions to the committed inventory offline
reproduces the artifact's proposed values precisely:

- The overlay changes **only** `normalized_title_match_count` — no other field
  in any of the 191 rows differs.
- It corrects exactly the same six product IDs listed in the artifact.
- The resulting file is byte-identical to the refresh candidate for these fields.

This means the change is fully reproducible from committed inputs and required
no trust in the artifact contents.

## Action taken

1. **Corrected `data/veritas_official_products.csv`** by regenerating it through
   the approved decision overlay. Six rows, one field each; no mapping status,
   master ID, title, URL, date, or review note changed.
2. **Added a guard** — `validate_veritas_inventory()` in
   `build_catalogue_pages.py` now fails the build whenever any inventory row's
   `normalized_title_match_count` disagrees with its `matched_master_uuids`,
   naming the offending product IDs. Verified by deliberately reintroducing the
   defect, which produced:

   ```
   ValueError: data/veritas_official_products.csv has derived match counts that
   contradict their matched master IDs:
     - product 50432: normalized_title_match_count='0' but 1 matched master ID(s)
   ```

3. Rebuilt `docs/veritas-products.json`; all `--check` modes pass.

## Note on the artifact's master IDs

The artifact was produced from head SHA `2e95222` at 10:03 UTC, **before** the
compact-ID migration merged at 10:43 UTC. Its `matched_master_uuids` column
therefore still shows old RFC-style UUIDs (e.g.
`019fc4e7-d1e7-7d0b-a52e-a0e4cdf23091`). Those values are **stale and were not
imported**. The current repository uses compact numeric IDs (`1`–`308`), and the
correction above was derived from current committed inputs, not from the
artifact's ID column.

## Consequence for the next refresh

With the inventory corrected, a re-run of **Map Veritas Catalogue** against an
unchanged live catalogue should now **pass** rather than fail, because the
committed inventory finally matches what deterministic matching plus the
approved overlay produce. That makes the next failure a meaningful signal of a
genuine upstream change.

**Recommended:** re-run the workflow once to confirm a clean pass. This also
retires the standing "unreviewed live divergence" risk.

## Status

✅ **Closed.** No upstream catalogue change; internal derived-field defect found,
corrected, and guarded against recurrence.

## Addendum — taxonomy snapshot refresh (2026-08-03)

A live retrieval of `/wp-json/wp/v2/product?_fields=id,link,product_cat` (191
products) plus `/wp-json/wp/v2/product_cat` (35 terms) confirms:

- **ID/link inventory identical** to the reviewed committed inventory (no
  upstream additions or removals), consistent with the "closed" status above —
  title/date fields were not re-compared in this retrieval.
- The empty `official_categories` column was a **fetcher defect**, not upstream
  absence: the previous fetcher read categories from `class_list`, which the
  API no longer populates. `fetch_veritas_catalogue.py` now requests the
  `product_cat` field and resolves term IDs through the taxonomy endpoint.
- `official_categories` is now populated on all 191 products (missing values
  would have rendered as `unresolved-category-<id>`; none did), enabling the
  Category Dominance Policy mapper (`map_series_taxonomy.py`,
  [SERIES_TAXONOMY_MAPPING.md](SERIES_TAXONOMY_MAPPING.md)).
