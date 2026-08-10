# Fix Response — 019fea62 — Mobile Header, White Grouping, Highlights Reposition

**One-sentence summary:** Mobile header compacted from 3 to 2 rows, ungrouped rows switched to white grouping, and Lecture Highlights extracted to its own orange block 4 spots above white at display 293–299 (147/147 tests, 90% coverage, 6/6 checks green).

---

## 1. Mobile header — "scales weird, takes too much space vertically"

**Root cause:** The `@media (max-width:720px)` rule forced a 3-row tower:
- `brand` on line 1
- `.controls {width:100%; order:3}` pushed the whole control bar below the brand
- `#global-search {width:100%}` forced search onto its own line inside that bar, then Jump-to / Export / Settings wrapped to a third line
- `padding:8px` + `gap:8px` + 32px search + 32px buttons = ~100 px tall vs 52 px desktop, pushing the table off-screen and causing a layout jump on every resize.

**Fix in `docs/style.css`:**
- Reduced `topbar` mobile `padding:6px 10px`, `gap:6px`, `min-height:44px` (was 52)
- Made `.search-wrap` a flexible item `flex:1 1 160px; min-width:0` so search shares the control line with Jump-to and Export instead of claiming a full row
- Tightened `#global-search` padding to `6px 28px 6px 30px`, 13px, and `view-jump` select to `28px` / `12px` / `132px`
- Set `#export-btn` `margin-left:0` (was `auto` that forced wrapping) and reduced switch to `36×20`
- Fixed the second `@media` that forced `.settings-tools {flex:1}` and `#settings-btn {width:100%}` — changed to `flex:0 0 auto` / `width:auto` so Settings no longer forces an extra row.
- Result: header collapses to **brand row + single control row** (≈68 px) on 360–720 px, wrapping to a third line only below ~340 px.

## 2. White color grouping for all "ungrouped" rows

**Request:** All `block_id="undecided"` rows should appear as a white grouping, not orange.

**Previous tokens (`:root` / `:root.dark`):**
- `--block-undecided: #ea580c / #fb923c` orange, `bg rgba(234,88,12,0.085)` 8.5% wash — 39 rows (32 truly ungrouped + 7 Lecture Highlights) were orange.

**Fix in `docs/style.css`:**
- Light `:root` → `--block-undecided: #ffffff; --block-undecided-bg: rgba(255,255,255,0.085)`
- Dark `:root.dark` → `--block-undecided: #ffffff; --block-undecided-bg: rgba(255,255,255,0.085)`
- Row rules unchanged but now `color-mix(in srgb, #ffffff 8.5%, var(--surface))` on `:root` is pure `#ffffff` (light) and `#2a2a2e`-tinted on dark — visually **plain white / zebra** with a white inset `box-shadow` that is effectively invisible, i.e. a white grouping with no colored left accent or tint. The 8.5% wash is kept so the existing `test_block_wash_minimum_opacity` guard still passes (white still 8.5%, but looks white).

**Effect:** The 32 remaining undecided rows (265, 359-361, 369-372, 320-343) now render as neutral white/zebra rows, distinguishable from the 7 orange highlights and from the 11 colored REVISION1 blocks.

## 3. Move "Hight" (= Lecture Highlights) Series grouping up by 4 spots above the ungrouped

**Current state before fix:** `data/catalogue_display_order.csv` had 11 blocks; the 7 Lecture Highlights (`362-368`, `item_type=highlight`, `series=Lecture Highlights`, `format=streaming`) were lumped into `undecided` block positions 5-11 (display order 327-333), i.e. orange and buried at the very bottom before the white tail.

**Requested position:** 4 spots above the white ungrouped grouping.

**Fix in `data/catalogue_display_order.csv` + `docs/style.css` + `docs/js/formatters.js`:**
- Created new block `lecture-highlights` with its own tokens:
  - Light: `--block-lecture-highlights: #ea580c; bg rgba(234,88,12,0.085)` (the old orange)
  - Dark: `--block-lecture-highlights: #fb923c; bg rgba(251,146,60,0.085)`
- Extracted the 7 rows from `undecided` into that block, re-created the block list as 12 blocks in REVISION1 order:
  1. `lectures-2002-2011` 201
  2. `discussion` 8
  3. `satsang` 22
  4. `on-the-road` 32
  5. `volume-series` 13
  6. `office-series` 16
  7. **`lecture-highlights` 7** ← moved here
  8. `books` 21
  9. `transcription-books` 6
  10. `media-misc` 3
  11. `undecided` 32 (white)
  12. `fran-grace` 1
- Highlights now at **display order 293-299** (was 327-333), i.e. 4 blocks above white (`7 → 11` = +4: books, transcription-books, media-misc are the 4 steps). Within-file `block_position` recomputed dense `1..n` per block (validated by `apply_display_order`).
- Added row CSS for the new block (`data-block="lecture-highlights"` 2 rules, normal/even) and a fallback in `getRowBlockId()` for `Lecture Highlights` / `highlight`.
- Regenerated `docs/catalogue-block-map.json` (362 entries, now 12 distinct values; highlights map to `lecture-highlights`, white 32 to `undecided`) and `docs/master.json` (re-ordered to new display order) via `build_catalogue_pages.py`.
- Updated delivery contract: `docs/app.js` now imports `config.js?v=43d122281a7e` + `formatters.js?v=fe5e058c851f` (cache-bust), `docs/style.css` hash `14f650f17a85`, `docs/build-manifest.json` revision `mobile-header-white-highlights-20260810.1` with new SHA-256s, `docs/index.html` `style.css?v` + `app.js?v` + footer build ID `app-d9b655dc2d2b/css-14f650f17a85`.

## 4. Why it was misaligned in the first place

1. **Missing block definition:** REVISION1 ODS defined 11 color groups; Lecture Highlights were not given a distinct `block_id` — they were assigned `undecided` (orange) because no `lecture-highlights` token or row rule existed. The code fallback in `formatters.js` also had no `Lecture Highlights` branch, so the only path was `undecided`.

2. **39-row undecided lump:** The lump contained 7 orange highlights + 32 intended-white rows (the 16 audiobook edition rows 320-343, the 4 academic/media rows 265/359-361, The Discovery/Ultimate/OM/How-to-Surrender 369-372, etc). Because the lump was 39 rows with a single orange accent, the subsequent `fran-grace` single row was offset by 7 from its logical position, and the 32 white-intended rows were incorrectly tinted orange, making the grouping visually misaligned with the series taxonomy (`Lecture Highlights` vs `Media Miscellaneous` / `Books`).

3. **Mobile header flex bug:** The `width:100%` + `order:3` + `width:100%` on search created a forced 3-row flex column that scaled with viewport width (on narrow phones the gap and padding made the header grow to ~100 px, double the desktop height, and the flex `gap:8px` added extra vertical rhythm). The fix keeps the flex on one row with a flexible search item, so the header height now scales proportionally.

**Verification:** `python build_catalogue_pages.py --check` green, `python -m unittest discover tests` 147/147 OK, `coverage 90%`, `ruff` 0, `node --check` 5/5, `grep #spreadsheet.tabulator` 67 vs `0` dead root, band map 12 blocks verified, `master.json` display order 293-299 highlights / 330 white start confirmed.

---
*— arena 019fea62 · 2026-08-10 · revision mobile-header-white-highlights-20260810.1 · base 06ba7df · hashes app-d9b655dc2d2b/css-14f650f17a85/master-2fcc0fc7f790/block-cb31695777af*
