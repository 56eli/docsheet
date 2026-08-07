# Ruling Prep — Four Always-Empty Master Columns (`location_physical`, `location_digital`, `location_streaming`, `reference_url_2`)

**Prepared:** 2026-08-07 (branch `arena/019fdd68-docsheet`)
**Status:** Evidence-only — no data changed. Awaiting owner ruling (question at the end).

---

## TL;DR

All four columns are empty on **all 365 masters**, and **no input holds data
that could ever fill them** — the raw archive never tracked locations, the
ledger's raw link fields are empty, and streaming availability already lives
in `source_url_*` + `reference_url_1` (63 rows). "Populate from evidence" is
not a real option. Recommendation: **drop all four** (re-addable from git
history the day real tracking data exists).

## Evidence

1. **Raw archive has no location data.** Columns are: `uuid, tempid, title,
   WE HAVE?, original source, format, product link, other links` (+ unnamed
   spacers). Ownership → `owned`; sources → `source_url_*`. Nothing about
   physical shelves, digital folders, or streaming destinations.
2. **Ledger link fields are exhausted.** `raw_other_links` is empty on all
   374 ledger rows (verified); `reference_urls()` machinery has nothing left
   to place in `reference_url_2`.
3. **`location_streaming` would duplicate existing columns.** Streaming
   destinations are already modelled in `source_url_veritas/audible/…` and
   `reference_url_1` (the streaming overlay). Duplication is exactly the
   drift class item E just eliminated.
4. **`location_physical` / `location_digital` would require a from-scratch
   owner inventory** — new data creation, not evidence population.
5. **Removal surgery is small and well-guarded:** `build_research_master.py`
   (6 refs: field list + 3 row constructors + validation), `EVERYTHING_FIELDS`
   + master projection in `build_catalogue_pages.py`, `docs/app.js`
   (LOW_PRIORITY_FIELDS + one preset comment), `tests/column-layout.spec.js`
   (2 refs), handoff lines, generated outputs (auto). Zero unittest refs.
   Note: an `app.js` comment documents the 2026-08-04 owner-directed column
   arrangement that *mentions* "Location Physical" as a sheet neighbour —
   cosmetic only.
6. Historical context: the four came from the original schema-migration draft
   as placeholders for future library tracking; they never received data.

## Options

- **A — Drop all four (recommended).** Pure schema slim: scripts, sheet,
  specs, docs, regeneration. Zero information loss (they hold none).
  Re-adding later is a revert away.
- **B — Drop the three location columns, keep `reference_url_2`** as a
  reserved slot (e.g., future streaming + Vimeo pair). Slightly larger sheet.
- **C — Keep all four** because a physical/digital inventory is planned and
  the columns are its landing spots.
