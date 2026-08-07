# Ruling Prep — Four Always-Empty Master Columns (`location_physical`, `location_digital`, `location_streaming`, `reference_url_2`)

**Prepared:** 2026-08-07 (branch `arena/019fdd68-docsheet`)
**Status:** EXECUTED 2026-08-07 — owner ruled **A (drop all four)** plus a follow-up directive to audit for other redundant columns (permission-first). Outcome below.

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

---

## Outcome (executed 2026-08-07, owner ruling A)

- `build_research_master.py`: `FIELDS` list, all three row constructors
  (ledger/manual-promotion/edition-promotion) slimmed; `reference_urls()`
  simplified to `reference_url()` (single first-URL return; only one caller).
- `build_catalogue_pages.py`: `EVERYTHING_FIELDS` slimmed; **25 master columns
  remain** (was 29).
- `docs/app.js`: `LOW_PRIORITY_FIELDS` cleaned; preset comment updated.
- `tests/column-layout.spec.js`: the Work-column parking test now asserts
  `work_id == legacy_tempid + 1` and the four dropped fields' **absence**
  (silent-reappearance guard).
- Regenerated: master CSV/JSON, all Pages sheets, reconciliation report.
- Verified: 6/6 `--check` modes, 112/112 tests, `node --check` clean.
- Follow-up directive: audit remaining columns for redundancy/uselessness and
  ask permission before any further removals.
