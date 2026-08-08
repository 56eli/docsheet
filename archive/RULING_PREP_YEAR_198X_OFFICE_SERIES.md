# Ruling Prep — Year "198X" Placeholder (16 Office Series Lectures, masters 233–250)

**Prepared:** 2026-08-08 · **Status:** awaiting owner ruling · **Branch:** `arena/019fe098-docsheet`
**Audit reference:** `FULL_STACK_AUDIT_2026-08-08.md`, finding **C3**.

---

## 1. What exists today

16 lecture records (masters **233–250**, Office Series) carry a non-year
`198X` placeholder in three places:

| Layer | Current value | Example |
|---|---|---|
| Master `year` | `198X` | 233: `Stress` |
| `year_source` | `Ledger: recording date 198X` | derived from ledger `proposed_year` |
| `catalog_code` | `LECTURE-198X-001 … 016` | code built as `{TYPE}-{year}-{seq:03d}` |
| `proposed_filename` | `198X - Stress.mp4` | reviewed proposal row |
| UI `Year-Month` | `198X` | `year_month = year ? (month ? \`${year}-${month}\` : year) : ""` (docs/app.js:514) |

Evidence in the ledger (rows 260–277, `review_reason`): *"Estimated decade
1980s (198X); most are believed 1982 but exact recording dates are
unconfirmed."* So `198X` is a **documented decade estimate**, not a typo.

### Precedents for "no exact year" rows — two different conventions already in the master

| Convention | Rows | `year` | `year_source` | code | filename prefix |
|---|---|---|---|---|---|
| **A. Blank + labelled source** | 13 Volume Series (202–214) | `` | `Blank: intentional pre-2000 (Volume Series)` | none | none (`Volume I … [1-2].mp4`) |
| **B. Blank + under investigation** | 230–232, 268 (4 rows) | `` | `Blank: under investigation` | none | none (`Verification of Spiritual Realities [1-3].mp4`) |
| **C. Placeholder decade** | 233–250 (16 rows) | `198X` | `Ledger: recording date 198X` | `LECTURE-198X-…` | `198X - …` |

### UI hazard (verified in `docs/app.js`)

- The year column's sorter is Tabulator-inferred from the first row's value
  (`2002` → number sorter); the 16 `198X` cells then sort as **NaN** — unstable
  position when the user clicks the Year header. The explicit numeric-sorter
  guard (app.js:748–758) is bypassed precisely because `198X` fails the
  `/^-?\d+(\.\d+)?$/` test, so the column relies on Tabulator's first-row guess.
- `LECTURE-198X-…` codes and `198X - …` filenames are lexically sortable but
  carry a placeholder where a year is expected.

---

## 2. Option 1 — Blank the year (strict "real years only", aligns with A/B)

**Changes (all input edits, then regenerate):**

1. `migration_review_ledger.csv` rows 260–277: `proposed_year` `198X` → **empty** (16 rows).
2. `build_research_master.py` provenance branch: an empty-year `Office Series`
   row would otherwise fall into `Blank: under investigation` (wrong — the
   decade IS documented). Add a branch (parallel to the Volume Series one):
   `elif series == "Office Series": src = "Blank: estimated 1980s per ledger (Office Series)"`.
3. Codes: the builder mints codes only `if item_type in CODE_ITEM_TYPES and year`
   → the 16 `LECTURE-198X-…` codes **disappear**. Catalogue-code count
   **281 → 265**. (Precedent: 230–232/268 are lecture rows without codes.)
4. `data/filename_proposal_YYYYMM.csv` rows 233–250: re-review to
   **bare-title** names, matching precedent B: `Stress.mp4`, `Health.mp4`,
   `Death and Dying.mp4` … (all globally unique; v4.1 guard passes).
5. Docs: README "281 catalogue codes" → **265**; handoff/deep-audit code counts.

**Pros:** one convention for every unknown-year row; `year` column becomes
fully numeric-sortable; codes/filenames never carry a placeholder year.
**Cons:** the documented decade estimate leaves the `year` column (survives
only in `year_source`); 16 catalogue codes are removed (a visible loss — codes
exist precisely to identify lectures); 16 filename rows need re-review; biggest
churn of the two options.

---

## 3. Option 2 — Keep `198X`, document it, polish the display (recommended)

**No data change.** Three small, reversible edits:

1. **README "Field semantics"** — add one sentence: *"Pre-2000 lectures whose
   decade is established but whose exact recording date is unconfirmed carry
   the placeholder year `198X` (Office Series; ledger evidence — most believed
   1982 — in `year_source`); rows whose decade is also unknown carry a blank
   year with a labelled `year_source`."* This turns the A/B/C divergence into
   a documented, deliberate distinction (decade known vs unknown) instead of an
   inconsistency.
2. **`docs/app.js` display polish (optional, display-only):** render `198X` as
   `c. 1980s` in the Year-Month derivation (app.js:514) and, if desired, in a
   Year-column formatter. The underlying data stays `198X`; exports/CSV keep
   the raw value.
3. **Sorter guard (optional, 2 lines):** if the data layer keeps non-numeric
   year values, pin the `year` column to a **string** sorter (or extend the
   numeric guard with a year-field exclusion) so sorting is deterministic
   (lexical: `198X` before `2002`) instead of Tabulator's NaN inference.

**Pros:** zero data churn; the decade estimate stays in the year column where
visitors see it; codes and filenames keep their identifying values; the fix is
documentation + 2 display lines.
**Cons:** `198X` remains a non-ISO value in the data (acceptable, since the
column is text everywhere it matters, and `year_source` explains it); the
"two conventions" now needs the README sentence to stay coherent (item 1).

---

## 4. Recommendation

**Option 2.** The `198X` values are evidence-backed decade estimates
(ledger), not missing data — blanking them (Option 1) *loses* information and
would strip 16 catalogue codes and year prefixes from 16 filenames for no
functional gain. The real defect is that the convention is **undocumented** and
the UI mishandles it (NaN sort). Option 2 fixes both in a few lines, and keeps
Option 1 available later if a stricter "real years only" policy is ever wanted
(this memo then serves as the change plan).

If Option 2 is approved, the applied change set is: README field-semantics
sentence + (optional) app.js `c. 1980s` display + `year` string-sorter guard
+ 2 Playwright/browser-spec adjustments if display changes are asserted.
All six `--check` modes, tests, and node checks must stay green after.
