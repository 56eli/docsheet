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

## Addendum 2 — reviewed inventory refresh 2026-08-03 (second pass)

A full deterministic regeneration (live API → `build_inventory_rows` → 35
approved overlay decisions reapplied) was committed to close internal drift the
taxonomy work exposed. Change classes, all verified:

1. **Stale primary-source matches corrected (4 products).** Products 1742,
   1728, 1695, and 1560 still claimed `matched_by_primary_source` against
   records whose source fields had since been corrected (the C2/C3 fixes). A
   fresh deterministic match demotes all four to
   `unreviewed_official_product` — they now surface as the four new
   `candidate_veritas` rows in Everything (359 → 363 rows).
2. **Re-link with review significance.** Product 1661 (`in-the-world-but-not
   -of-it-cd`) no longer maps to book record 300; deterministic normalized
   matching now attaches it to **record 264** ("In the World But Not of It –
   Audio") — the deferred record-264 territory from the handoff. This is a
   *mapping* row, not a source override; the deferred physical-edition
   confirmation still stands before any source association is approved.
3. **Upstream rename (1 product).** Product 50810 is now "Vol II:
   Consciousness and Addiction" (was "Volume II: …") — a genuine upstream
   change; the stored titles in `data/product_relationships.csv` (2 cells)
   were aligned to keep validation green.
4. **Overlay title hygiene (3 decision rows).** `matched_master_titles` in
   `data/veritas_mapping_decisions.csv` for products 50411, 50432, 1542 still
   held pre-hygiene titles (`.mp4`-suffix); aligned to current cleaned master
   titles (the overlay's own invariant requires exact equality).
5. **Derived title columns** (≈40 rows) refresh to the cleaned master titles
   (`.mp4`/numeric-prefix removal) — deterministic mirror, no semantic change.

No upstream additions/removals: the 191-product ID set is unchanged.

## Addendum 3 — refresh accepted and candidate/overlay link-up 2026-08-04

The Map Veritas Catalogue workflow's fail-gate fired on a real drift and the
artifact diff was reviewed row by row. Findings and actions:

1. **Diff accepted (13 rows).** The live fetch correctly re-matched products
   whose masters were minted on 2026-08-03: 9 Satsang monthlies (1304/1306/
   1308/1310/1312/1314 → masters 344–349; 1639 → 350; 1697 → 351; 1699 → 352),
   edition rows 1728 → 327, 1695 → 328, 1742 → 330, and 1661 → 329
   (`in-the-world-but-not-of-it-cd` — the edition row, not deferred record
   246). Every accepted row was asserted against its master's primary Veritas
   URL before committing; validator invariants (`count == len(uuids)`,
   `matched_master_titles` equal current master titles) pass.
2. **Overlay trimmed 35 → 18.** The 17 decisions preserving pre-promotion
   `unique_item`/`compilation_or_new_edition` dispositions for products whose
   works are now curated masters (309–319, 353–358) were removed; the
   deterministic primary-source matcher now links them (Everything
   `candidate_veritas` 28 → 8). What remains: the 7 annual Highlights
   compilations (Series Compilations lane by ruling) and the Map of
   Consciousness® poster (merchandise — not a master record).
3. **Line-ending normalization.** The diff rendered as a whole-file rewrite
   because the committed inventory had CRLF endings while the fetcher writes
   `lineterminator="\n"`. The reviewed inventory is now LF, so future
   artifact diffs show content changes only.
4. **Fallout tracked.** Series-taxonomy mapper regenerated: 30 new `proposed`
   rows (20 equal the curated baseline; 10 differ — owner ruling listed in
   `NEXT_AGENT_HANDOFF.md` §6). Everything is 396 → 376 rows. The next
   workflow run should pass clean.

## Addendum 4 — taxonomy rulings, NC edition fills, Master-ID sort (2026-08-04)

1. **All 10 remaining series-taxonomy proposals ruled.** 3 approved:
   product 1814 → master **357** (Peace is the Natural State) re-seriesed
   Media Miscellaneous → **On The Road Talk Series** (publisher category and
   the original On-The-Road audio evidence agree); products 50485/50488 →
   masters **312/313** (the 2012 per-title discussion works) re-seriesed →
   **Discussion Series**. 7 rejected with documented rationale: 1546/1548
   (Unity Church Sedona CDs — the curated On-The-Road run stands over the
   "Media Miscellaneous" carrier shelf), 1661/1695/1728/1742 (audio/CD-DVD
   editions keep their work's `Books` series; precedent: product 1542), and
   55576 (six conflicting publisher categories, no dominant home; original
   12-session audio program, not a transcription-series book). Master rebuilt:
   exactly **3 series values changed**; taxonomy 179 matched → **169 approved
   / 0 proposed / 10 rejected**; 316 approved mappings cover 316 master IDs.
2. **`source_url_nightingale_conant` 0 → 4.** The official Nightingale-Conant
   author page (nightingale.com/pages/david-hawkins) fetched live 2026-08-04
   lists 7 Hawkins programs. The 4 that are master audio editions —
   masters **327–330** (Truth Vs Falsehood, Healing, In The World But Not Of
   It, The Highest Level Of Enlightenment) — received approved override rows
   keyed by edition `candidate_key` (they have no `raw_row_number`). The
   remaining 3 (The Ultimate David Hawkins Library, The Discovery, Naked) are
   unmapped compilations that stay in the official discovery queue pending
   owner ruling. Hay House needed no new fills: its unreviewed inventory rows
   are a merchandise journal/deck and an audio program already carried as a
   `candidate_hayhouse` row. Approved overrides **106 → 110**.
3. **Master ID column sort fixed.** `docs/app.js` detects fully-numeric
   columns and applies Tabulator's built-in `number` sorter with
   `alignEmptyValues: "bottom"`, so Master ID counts 1, 2, 3, … (not the
   lexical 1, 10, 100, … produced by the first-row-guessed string sorter)
   and blank candidate IDs pin to the bottom in both sort directions. CI e2e
   assertion added (`tests/column-layout.spec.js`: ascending 1/2/3,
   descending 358/357 — IDs 249 and 264 are retired); the same ordering was
   verified in the sandbox by replaying Tabulator 6.5.2's `_sortRow`
   semantics against the committed `docs/master.json`.
4. **Verification battery re-run green:** all 5 `--check` modes, 100 unittest
   tests (fixtures now strip edition-keyed overrides when a test rewrites
   the edition layer), coverage 92% (gate 80%), `node --check` on all four
   JS files, `py_compile` on all pipeline modules.
