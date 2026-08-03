# Schema Cleanup Report — 2026-08-03

## Summary

Successfully cleaned up the master schema by:
1. **Notes column cleanup**: Removed 14 inappropriate/redundant notes (13 raw_source_note entries, 1 "my pdfs are trash")
2. **raw_row_number column separation**: Split into two columns - numeric-only `raw_row_number` and new `candidate_key` column for candidate:* values

**Result:** Cleaner schema with better separation of concerns, all 93 tests passing.

---

## 1. Notes Column Cleanup

### Initial State
- 59 records with notes
- Types of notes:
  - 13 "Raw source note: veritas/only sold via audible..." (redundant with source_url columns)
  - 20 "Promoted from official candidate..." (provenance notes)
  - 1 "Display title corrects raw 'Volume II' to Volume I..." (important documentation)
  - 1 "my pdfs are trash" (inappropriate)
  - 24 "Promoted edition audio/video of work..." (edition promotion notes)

### Actions Taken
- Removed all 13 "Raw source note:" entries (redundant with source_url_* columns)
- Removed 1 inappropriate note ("my pdfs are trash")
- Kept 45 provenance/provenance-related notes

### Result
- **Before:** 59 records with notes
- **After:** 45 records with notes
- **Removed:** 14 notes (23.7% reduction)
- **Kept:** All important provenance and documentation notes

---

## 2. raw_row_number Column Separation

### Initial State
- `raw_row_number` column contained mixed values:
  - 306 numeric values (e.g., "7", "8", "9")
  - 44 candidate:* values (e.g., "candidate:edition-audible-tlc-perception")
- Long candidate:* values (up to 40 chars) were causing display issues

### Actions Taken

#### 2.1 Schema Update
Added new column `candidate_key` to the FIELDS list in `build_research_master.py`:
```python
FIELDS = [
    ...,
    "raw_row_number", "candidate_key",
]
```

#### 2.2 Code Updates
Updated three locations in `build_research_master.py` where candidate rows are created:
- Line ~843: Edition promotion rows
- Line ~992: Manual candidate promotion rows
- Line ~967: Regular ledger items

Changed from:
```python
"raw_row_number": f"candidate:{key}",
```

To:
```python
"raw_row_number": "",
"candidate_key": f"candidate:{key}",
```

#### 2.3 Source Override Support
Updated `apply_source_overrides()` to check both `raw_row_number` and `candidate_key`:
```python
items_by_raw = {}
for row in items:
    if row["raw_row_number"]:
        items_by_raw[row["raw_row_number"]] = row
    if row.get("candidate_key"):
        items_by_raw[row["candidate_key"]] = row
```

#### 2.4 Product Relationship Validation
Updated `validate_product_relationships()` in `build_catalogue_pages.py` to check both columns:
```python
master_provenance = master["raw_row_number"] or master.get("candidate_key", "")
if relation["raw_row_number"] != master_provenance:
    raise ValueError(...)
```

#### 2.5 Test Update
Updated test `test_approved_promotion_mints_edition_row` to check `candidate_key` instead of `raw_row_number`.

### Result
- **raw_row_number**: Now numeric-only (306 records) or empty (44 records)
- **candidate_key**: Contains candidate:* values (44 records)
- **No data loss**: All provenance information preserved
- **Better display**: Short numeric values in raw_row_number column

---

## 3. Verification

### Test Results
- ✅ All 93 tests passing
- ✅ `build_research_master.py --check` passes
- ✅ `build_catalogue_pages.py --check` passes
- ✅ All other `--check` modes pass

### Data Integrity
- 350 master records
- 306 records with numeric raw_row_number
- 44 records with candidate_key
- 0 records with candidate:* in raw_row_number (correctly separated)
- 45 records with notes (provenance/documentation only)

---

## 4. Files Modified

### Code Files
1. `build_research_master.py` — Added candidate_key to FIELDS, updated 3 candidate creation locations, updated apply_source_overrides()
2. `build_catalogue_pages.py` — Updated validate_product_relationships() to check both columns
3. `tests/test_pipeline.py` — Updated test to check candidate_key

### Data Files (regenerated)
1. `data/research_master_draft.csv` — New schema with candidate_key column
2. `data/research_master_draft.json` — Regenerated from CSV
3. `docs/master.json` — Regenerated
4. `docs/catalogue-meta.json` — Regenerated
5. All other `docs/*.json` files — Regenerated

---

## 5. Benefits

### Data Quality
- ✅ Cleaner separation of concerns (numeric provenance vs candidate keys)
- ✅ Removed redundant notes (raw_source_note duplicated source_url info)
- ✅ Removed inappropriate content ("my pdfs are trash")
- ✅ Preserved all important provenance documentation

### Display/UX
- ✅ raw_row_number column now shows short numeric values (1-3 chars)
- ✅ No more long candidate:* strings in raw_row_number column
- ✅ Better readability in spreadsheet views

### Maintainability
- ✅ Clear distinction between ledger-sourced rows (raw_row_number) and candidate-sourced rows (candidate_key)
- ✅ Easier to query/filter by provenance type
- ✅ Consistent with database normalization principles

---

## 6. Migration Notes

For anyone working with the master data:
- **raw_row_number**: Now contains only numeric values (ledger row numbers) or is empty
- **candidate_key**: Contains candidate:* identifiers for promoted candidates
- To find the provenance of a record, check both columns:
  - If `raw_row_number` is numeric → ledger-sourced
  - If `candidate_key` is non-empty → candidate-promoted
- Source overrides can reference either column (both are checked)
- Product relationships validation checks both columns

---

**Report generated:** 2026-08-03  
**Branch:** `arena/019fc925-docsheet`  
**Test suite:** 93 tests, 92% coverage  
**Session duration:** Schema cleanup and separation
