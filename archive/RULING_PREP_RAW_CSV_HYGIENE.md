# Ruling Prep — Raw Spreadsheet Hygiene (`hawkins archive clone - Sheet1.csv`)

**Prepared:** 2026-08-08 · **Status:** awaiting owner action (Google Sheet) · **Branch:** `arena/019fe098-docsheet`
**Audit reference:** `FULL_STACK_AUDIT_2026-08-08.md`, finding **C5**.
**Rule of thumb:** the raw CSV is the owner's source of truth ("you edit
this"); the curated master and the pass-through view (`docs/data.json`) are
derived. Fixing the raw removes the defects from the public **Original
Spreadsheet** tab; a follow-up ledger/mirror edit cleans the curated
`legacy_tempid` for the 13 affected masters.

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

## 3. After the raw edit (owner) → follow-up (agent, on request)

1. **Owner:** fix the 16 cells in Google Sheets, re-export the CSV over
   `hawkins archive clone - Sheet1.csv`, commit. The "Update Spreadsheet"
   workflow (or `python process_data.py`) regenerates `docs/data.json` — the
   Original Spreadsheet tab then shows the clean URLs and blank tempid cells.
2. **Agent follow-up (only after the raw change is committed):**
   - `migration_review_ledger.csv`: clear `raw_tempid` on rows 280–292;
     correct `raw_product_link` on rows 28–30; update the two
     `review_reason` markers (quarantined-URL / repeated-placeholder) to note
     "raw fixed 2026-08-08".
   - `python build_research_master.py` → masters **251–263** regenerate with
     `legacy_tempid` **blank** (the only master diff).
   - Re-run `build_catalogue_pages.py`, `reconcile_research_master.py`, all
     six `--check` modes, and the test suite.
3. **Verification:** master count stays 365; codes stay 281; the only master
   diff is 13 `legacy_tempid` cells going blank; `docs/data.json` (374 rows)
   shows corrected URLs and no `2cds each?`.

**Decision needed:** (a) apply all 16 raw fixes, or (b) fix only the 3 URLs
(minimal — the broken link is the visible defect; the junk tempid is
cosmetic in the curated `legacy_tempid` mirror). Recommendation: **(a)** —
both are trivial cell edits and 1b also cleans the curated layer.
