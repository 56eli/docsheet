# Ruling Prep — Raw Spreadsheet Hygiene (`hawkins archive clone - Sheet1.csv`)

**Prepared:** 2026-08-08 · **Status:** applied on branch `arena/019fe0ef-docsheet`
**Audit reference:** `FULL_STACK_AUDIT_2026-08-08.md`, finding **C5**.
**Rule of thumb:** the raw CSV is the owner's source of truth ("you edit
this"); the curated master and the pass-through view (`docs/data.json`) are
derived. The 2026-08-08 follow-up fixed the raw CSV, refreshed `docs/data.json`,
and cleaned the curated `legacy_tempid` mirror for the 13 affected masters.

---

## 1. Defects to fix (16 cells on 16 lines)

All line numbers refer to the committed CSV
`hawkins archive clone - Sheet1.csv` (real header on line 2; `process_data.py`
reads with `header=1`).

### 1a. Broken product links — 3 cells (column `product link`)

| Line | tempid | Title | Before | After |
|---|---|---|---|---|
| 28 | `LS200208_1` | Advaita: The Way to God Through Mind (Aug 2002) DVD01 | `https://veritaspub.com/product/https://veritaspub.com/product/2002-08-advaita-the-way-to-god-through-mind/` | `https://veritaspub.com/product/2002-08-advaita-the-way-to-god-through-mind/` |
| 29 | `LS200208_2` | Advaita: The Way to God Through Mind (Aug 2002) DVD02 | same duplicated-prefix URL | same corrected URL |
| 30 | `LS200208_3` | Advaita: The Way to God Through Mind (Aug 2002) DVD03 | same duplicated-prefix URL | same corrected URL |

The curated master already carries the corrected URL (masters 22–24); the
ledger quarantined the raw value (`Product URL has duplicated prefix and is
quarantined for correction.`) and the **pass-through Original Spreadsheet tab
still exposes the broken link** to visitors today.

### 1b. Stray annotation in the `tempid` column — 13 cells

Lines **280–292**, all with tempid `2cds each?` (Satsang Series Jan 2007 …
Nov 2010; masters 251–263). The tempid column must hold an identifier; this
is a repeated annotation, not one. **After: blank** for all 13.

| Line | Title | Before (tempid) | After |
|---|---|---|---|
| 280–292 (13 rows) | Satsang Series (Jan 2007) … (Nov 2010) | `2cds each?` | *(empty)* |

These are valid rows (owned `❌`, source `veritas/only sold via audible`) whose
`legacy_tempid` currently exposes the junk string in the curated master.

---

## 2. What NOT to change (deliberate provenance, keep verbatim)

| Row(s) | Why it stays |
|---|---|
| Line 1 (`archive clbs`) | Stray Google-Sheets title row — `process_data.py` reads with `header=1`, removing it would break the pipeline |
| Lines 3–4 (series headings, e.g. `Series 2002: The Way to God`) | `series_context` rows in the ledger; provenance |
| Lines 273, 276 (`where is B-02? might not exist.` / `B-05`) | The annotation is in the **title** column of two *excluded* rows (ledger: "Owner approved exclusion on 2026-08-03: literal Office Series B-02/B-05 non-item"); not master records, kept as evidence |
| `SAT2011Q01–Q03`, `VOL101–VOL701`, `OFF01–OFF18` tempid schemes | Legitimate alternate identifier schemes used by the source for Q&A/Volume/Office rows |
| Line 295 (`❌❌ MOST ARE MISSING ❌❌`) | `research_note` row; provenance |

---

## 3. Applied follow-up

Applied 2026-08-08 on `arena/019fe0ef-docsheet`:

1. Fixed all 16 raw cells in `hawkins archive clone - Sheet1.csv`.
2. Refreshed `docs/data.json`, so the Original Spreadsheet tab now shows the
   corrected Advaita URL and blank Satsang tempid cells.
3. Updated `migration_review_ledger.csv`: rows 28–30 now carry the corrected
   `raw_product_link` / `proposed_source_url_veritas`, rows 280–292 have blank
   `raw_tempid`, and the relevant `review_reason` cells document the raw fix.
4. Retired the three now-redundant Advaita `source_url_veritas` overrides
   (approved source overrides **134 → 131**) because the ledger now carries the
   corrected source URL directly.
5. Rebuilt the curated master and Pages outputs. Master count stays **365**;
   catalogue-code count stays **281**; masters **251–263** now have blank
   `legacy_tempid` instead of the repeated `2cds each?` annotation.
