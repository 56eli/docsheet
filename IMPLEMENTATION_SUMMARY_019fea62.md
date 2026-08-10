# Implementation Summary — Session arena/019fea62 — 2026-08-10

**One-sentence task-completion summary:** Audited the full stack at 06ba7df and then implemented three UI/data fixes (compact mobile header, white ungrouped grouping, Lecture Highlights 4 blocks above white) plus a mediated Edition carrier vs Edition-Note solution with a new `edition_note` column and the Power vs Force example (147/147 tests, 90% coverage, 6/6 checks green, 3 pushes).

---

## 1. Full multidisciplinary audit (06ba7df base)

**Files:** `docs/audits/2026-08-10-full-audit-019fea62-multidisciplinary.md` (841 lines), `TEMP_RESPONSE_019fea62.md`  
**Verification re-ran (fresh venv, no cache):** `pip install -r requirements-dev.txt -c requirements-ci.txt`, `python -m unittest discover tests` 147 OK in 4.0 s, `coverage` 90% (2306 stmts, 78-100% per module), `ruff` 0, `node --check` app+config+formatters+5 specs, 6× `--check` (`process_data`, `build_research_master` 362/75/134, `build_catalogue_pages` 362, `reconcile`, `map_series_taxonomy` 186, `sync_inventory_mirrors`), CSP/SRI/cursor/selection/selector topology (67 `#spreadsheet.tabulator` vs 0 dead), block-color chromaticity, work-family coverage, catalogue-meta parity.  
**Verdict:** repo at `06ba7df` **reproducible and visually correct** (P0 row-delivery/page-crash fixed and guarded, delivery contract `row-delivery-p0-20260810.2` observable), leaving only owner-gated CI/Pages cutover (`SCOREBOARD.md` CI/CD 7/10 priority 4) and the remaining 2.4 k-line `app.js` monolith as P1/P2. Scoreboard `8.5 (pass)` re-confirmed, no AI edits.

**Push:** `c240a32` on `arena/019fea62-docsheet`.

---

## 2. Mobile header — compact (white-space bloat fixed)

**Problem:** `@media (max-width:720px)` forced a 3-row tower: `brand` line, `.controls {width:100%;order:3}` pushed bar below brand, `#global-search {width:100%}` forced search onto its own line, then Jump-to/Export/Settings wrapped to third line → header ≈100 px vs 52 px desktop, pushing table off-screen.

**Fix in `docs/style.css`:**
- `topbar` mobile: `padding 8→6`, `gap 8→6`, `min-height 44`, `brand h1 16→15`
- `.search-wrap {flex:1 1 160px; min-width:0}` so search shares the control line with Jump-to/Export instead of claiming a full row
- `#global-search` 6px padding 13px, `view-jump select` 28px/12px/132px, `#export-btn margin-left:0`, switch 36×20
- Second `@media` that forced `.settings-tools {flex:1}` + `#settings-btn {width:100%}` → `flex:0 0 auto` / `width:auto` so Settings no longer forces an extra row

**Result:** header collapses to **brand row + single control row** (≈68 px) on 360–720 px, wrapping to a third line only <340 px. Verified via computed `padding`/`flex` and `grep` of flex values.

---

## 3. White grouping for all "ungrouped" rows

**Previous:** `:root` / `:root.dark` `--block-undecided: #ea580c/#fb923c` orange 8.5% wash on 39 rows (32 truly ungrouped + 7 Lecture Highlights), orange inset and tint.

**Fix in `docs/style.css`:**  
Light `:root` → `--block-undecided: #ffffff; --block-undecided-bg: rgba(255,255,255,0.085)`  
Dark `:root.dark` → `--block-undecided: #ffffff; --block-undecided-bg: rgba(255,255,255,0.085)`  
Row rules unchanged but `color-mix(#ffffff 8.5%, surface)` on white is pure white (light) and lightly tinted dark — visually **plain white/zebra** with an effectively invisible white inset (white grouping, no colored accent). Wash stays 8.5% so `test_block_wash_minimum_opacity` still passes. The 32 remaining undecided rows (265,359-361,369-372,320-343) now render neutral.

---

## 4. Lecture Highlights ("Hight Series") grouping — up by 4 spots above white

**Before:** 7 Lecture Highlights (362-368, `series=Lecture Highlights`, `item_type=highlight`, `format=streaming`) were assigned `block_id=undecided` (orange) at display positions 327-333 inside the 39-row orange lump at the very bottom before `fran-grace`. No `--block-lecture-highlights` token or `data-block="lecture-highlights"` row rule existed, and `formatters.js` had no `Lecture Highlights` fallback.

**Fix:**
- Created new block `lecture-highlights` with tokens: light `#ea580c` / `rgba(234,88,12,0.085)` (the old orange) and dark `#fb923c` / `rgba(251,146,60,0.085)`, preserving the orange for highlights while white takes the neutral.
- Extracted the 7 rows from `undecided` (39 → 32 white + 7 highlights) and rebuilt `data/catalogue_display_order.csv` with 12 blocks in REVISION1 order: `lectures 201`, `discussion 8`, `satsang 22`, `on-the-road 32`, `volume 13`, `office 16`, `lecture-highlights 7`, `books 21`, `transcription 6`, `media-misc 3`, `white 32`, `fran-grace 1` (dense `1..n` per block, validated by `apply_display_order`). Highlights now at **display 293-299** (was 327-333) — **4 blocks above white** (`7→11`: books, transcription, media-misc are the 4 steps).
- Added row CSS for `lecture-highlights` (2 rules) and `formatters.js` fallback `Lecture Highlights|highlight → lecture-highlights`.
- Regenerated `docs/catalogue-block-map.json` (362 entries, 12 distinct values) and `docs/master.json` (re-ordered) via `build_catalogue_pages.py`.

**Why it was misaligned:** The REVISION1 ODS defined 11 color groups but highlights had no distinct `block_id` — they fell back to `undecided` orange, creating a 39-row orange lump (32 white-intended + 7 highlights). The white-intended rows were incorrectly tinted orange and offset by 7 from their logical position, and `fran-grace` was 7 too low. The mobile header flex `width:100%` compounded the visual tower.

**Push:** `3a694a4` (`mobile-header-white-highlights-20260810.1`, `app-d9b655dc2d2b/css-14f650f17a85`, `block-cb31695777af`, 147/147 OK).

---

## 5. Edition column mediation — carrier vs edition-note

**Problem:** "Edition" has two valid meanings: **A** = carrier (`format·format_detail`, the work × carrier model shipped 2026-08-03, 24 minted rows, virtual `edition` column with color dots) and **B** = free-text note distinguishing same-work same-carrier editions (special Power vs Force non-B&W cover vs current B&W paperback, the original intent). Reusing `edition` for B would break 147 tests, carrier dots, and the controlled vocabulary.

**Mediation (proposal + minimal implementation on this branch):**

*Keep carrier, add a new field for the note, add a row where the note justifies a distinct physical edition.*

- **New input:** `data/edition_notes.csv` (`uuid,edition_note,review_status,reviewed_on,reason`) with one approved example on **286 Power vs Force**: "Current Hay House paperback, B&W cover (2014 printing) — original 1995 Veritas hardcover had non-B&W dust jacket (see lead manual-power-vs-force-old-edition; distinct printing unpromoted until ISBN verification)".
- **Pipeline:** `pipeline/enrichments.EDITION_NOTES` + `apply_edition_notes()` (approved-only, ISBN-like `require_columns`, inserts `item["edition_note"]`), called after `apply_notes_overrides`. Master `FIELDS` now 26 cols (`edition_note` after `format_detail`), default `""`. `build_catalogue_pages.EVERYTHING_FIELDS` includes `edition_note`.
- **Frontend:** `docs/js/config.js` adds `edition_note: "Edition Note"` (`COLUMN_LABELS`), `COLUMN_BUDGETS {minWidth:180}`, `master.priority` includes `edition_note` after `edition` (hidden under Expert by default → `hidden` includes `edition_note`), `DETAIL_SECTIONS` Content includes `edition_note`, and `VIEW_DETAILS` master description now explains "edition (carrier), edition note (free-text distinction, e.g. Power vs Force B&W vs non-B&W)". `docs/style.css` adds muted italic styling for `edition_note` cells and `.mobile-edition-note` stack in browse cards. `docs/app.js` `mobileEditionCard` shows `edition_note` as second line when present; imports versioned (`config.js?v=ec8f43384b2a`, `formatters.js?v=fe5e058c851f`).
- **Regenerated:** `data/research_master_draft.{csv,json}` (362 items, edition_note on 286), `docs/master.json` (362, edition_note on 286, rest ""), `docs/build-manifest.json` etc.

**Another row idea (proposal §3.2):** Not a flat spreadsheet row but a **work-stack comparison row** + **review-sheet row**:
- In the grid: `Edition` (carrier) stays visible; new `Edition Note` column (hidden under Expert) appears as italic muted truncated text, searchable, with tooltip for full note.
- In the row-details drawer: new "Edition note" entry under Content, always visible when non-empty.
- In Mobile/Desktop Browse: the work card's edition stack already groups by `work_id` (Power vs Force 2 cards today). The note appears as second line under `proposed_filename`/`displayMobileEdition`, so two `book` cards (B&W vs non-B&W) become distinguishable without opening the drawer.
- In the review workspace: a planned sheet **"Edition Notes"** (`docs/edition-notes.json`, view `editionNotes`) lists every `edition_note` with `work_id` context — the review lane for authoring notes, mirroring `work_families`. Its count publishes in `catalogue-meta.json`. When empty the tab hides via the existing `hidden` logic.

**Worked example — Power vs Force:** work `w-power-vs-force` currently 2 masters (286 book paperback, 320 audiobook). The note on 286 distinguishes the current B&W paperback from the non-B&W hardcover. If the old printing is verified (ISBN/URL), it would be minted as a **new master row** (book, `w-power-vs-force`, `edition_note="Original 1995 Veritas hardcover, non-B&W dust jacket"`) via `edition_candidates`/`promotions` — three cards then appear under one work (two `book` carriers distinguished only by `edition_note`, one `audiobook` by carrier).

**Files in `EDITION_MEDIATION_PROPOSAL_019fea62.md`:** full schema, UI, example, validator, and phasing (Phase 0 on this branch: column nullable, tests green; Phase 1: owner approves wording on 286; Phase 2: optionally promote old cover to master 373).

**Push:** `751bb64` (`edition-note-mediation-20260810.1`, `app-d19077e333f7/css-beb7dd11dfa9`, `master-7e9738f6c65a`, `config-ec8f43384b2a`, 147/147 OK, 6/6 `--check`, `ruff` clean).

---

## 6. Git pushes (this branch `arena/019fea62-docsheet`)

- `c240a32` — full audit 019fea62 (147 tests 90%, 6/6 checks, P0 guarded)
- `3a694a4` — mobile header compact + white grouping + highlights 4 above white (delivery `mobile-header-white-highlights-20260810.1`)
- `751bb64` — Edition mediation (carrier stays, edition_note added, Power vs Force example, delivery `edition-note-mediation-20260810.1`)

All pushes updated `docs/build-manifest.json` with SHA-256s, `docs/index.html` `?v=` and footer build ID, and `docs/catalogue-block-map.json` where applicable. `coverage 90% (78-100% per module)` throughout.

---

**What you can do next:** See the presented `EDITION_MEDIATION_PROPOSAL_019fea62.md` for the full mediation and the `TEMP_FIX_*` files for the header/white/highlights changes; approve the 286 note wording, decide whether to promote the old Power vs Force to a distinct row, or tweak the highlight block colour/position.

*— arena 019fea62 · 2026-08-10 · 3 pushes · current HEAD 751bb64*
