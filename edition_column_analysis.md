# Edition Column Standardization Analysis

## Overview

The "Edition" column (merged from `format` + `format_detail` in the frontend) has several standardization inconsistencies that affect display clarity and data quality.

---

## Current State

### Format Distribution
- DVD: 253 rows
- CD: 32 rows
- book: 31 rows
- audiobook: 27 rows
- streaming: 22 rows

### format_detail Patterns (48 unique values)

#### DVD Rows (253 total)

| Pattern | Count | Examples | Issue |
|---------|-------|----------|-------|
| `DVD01`, `DVD02`, `DVD03` | 66 each (198 total) | UUIDs 1-198 (lecture series 2002-2006) | Numeric with carrier prefix |
| `Part 1`, `Part 2`, `Part 3` | 10 total | UUIDs 202-207, 212, 222-224, 230-232 | Title case, space-separated |
| `PART1`, `PART2`, `PART3` | 8 total | UUIDs 215-220, 228-229 | Uppercase, no space |
| `A-01` through `A-12`, `B-01`, `B-03`, `B-04`, `B-06` | 16 total | UUIDs 233-250 (Office Series) | Lecture identifiers, not parts |
| `CD & DVD set` | 1 | UUID 327 | Mixed format notation |
| (blank) | 13 total | UUIDs 213-214, 266-276 (single-part DVDs) | Missing part notation |

#### CD Rows (32 total)

| Pattern | Count | Examples | Issue |
|---------|-------|----------|-------|
| (blank) | 25 total | UUIDs 251-260, 262-265 (Satsang series) | Single CDs, no part needed |
| `one CD; 67 min` | 2 | UUIDs 354, 356 | Descriptive |
| `three CD; 2h56m` | 1 | UUID 265 | Descriptive |
| `three CD; 3h45m` | 1 | UUID 353 | Descriptive |
| `one CD; 60 min` | 1 | UUID 355 | Descriptive |
| `On-the-Road audio` | 1 | UUID 357 | Descriptive |
| `6-CD set (Nightingale-Conant)` | 1 | UUID 329 | Descriptive |

#### audiobook Rows (27 total)

| Pattern | Count | Examples | Issue |
|---------|-------|----------|-------|
| `Audiobook` | 19 total | UUIDs 320-338 (book audiobook editions) | **Redundant** (format already says audiobook) |
| (blank) | 4 total | UUIDs 369-372 (Nightingale-Conant/Hay House) | Missing |
| `Audio program` | 2 | UUIDs 328, 330 | Descriptive |
| `Audio program (Hay House)` | 1 | UUID 343 | Descriptive |
| `original 12-session audio program` | 1 | UUID 358 | Descriptive |

---

## Issues Identified

### 1. Inconsistent Part Notation (DVD)
Three different notations for essentially the same information:
- `DVD01` (carrier prefix + number)
- `Part 1` (title case, space)
- `PART1` (uppercase, no space)

**Impact**: The Everything view shows inconsistent Edition values like "DVD · DVD01", "DVD · Part 1", "DVD · PART1" for what are essentially the same type of multi-part content.

**Test expectation**: `tests/test_pipeline.py::test_cleaned_multi_part_titles_keep_part_detail_in_master` expects `Part 1`, `Part 2`, `Part 3` format.

### 2. Redundant "Audiobook" Values
19 audiobook rows have `format_detail = "Audiobook"` which is redundant since `format = "audiobook"`.

**Impact**: Edition column shows "audiobook · Audiobook" which is redundant.

### 3. Blank format_detail on Single-Part Items
13 DVD and 4 audiobook rows have blank `format_detail` despite having `part_index = 1/1` in the filename proposal.

**Impact**: Edition column shows just "DVD" or "audiobook" without any part notation (acceptable for single items, but inconsistent with multi-part items that always show part numbers).

### 4. Descriptive vs. Standardized CD Details
CD rows have varied descriptive text ("one CD; 67 min", "three CD; 2h56m", etc.) instead of standardized notation.

**Impact**: Inconsistent display; some show carrier info, others don't.

---

## Recommendations

### Option A: Full Standardization (Recommended)

1. **Standardize all DVD part notations to "Part X" format:**
   - `DVD01` → `Part 1`
   - `DVD02` → `Part 2`
   - `DVD03` → `Part 3`
   - `PART1` → `Part 1`
   - `PART2` → `Part 2`
   - `PART3` → `Part 3`

2. **Preserve Office Series identifiers:**
   - Keep `A-01` through `B-06` as-is (these are lecture IDs, not parts)

3. **Clear redundant audiobook values:**
   - Set `format_detail = ""` for the 19 rows with "Audiobook"

4. **Fill blank format_detail where part_index exists:**
   - For items with `part_index = 1/1`, optionally set `format_detail = "Part 1"` for consistency

5. **Leave CD descriptive values or standardize:**
   - Satsang single CDs: leave blank (no part needed)
   - Multi-CD sets: could standardize to "1/3", "2/3", etc. or keep descriptive

**Pros**: Clean, consistent Edition column; matches test expectations; easy to maintain.

**Cons**: Loses the "DVD" prefix that clarified these were DVD parts (but the format column already shows "DVD").

### Option B: Minimal Fixes

1. Only fix the `PART1/PART2/PART3` → `Part 1/Part 2/Part 3` inconsistency
2. Clear redundant "Audiobook" values
3. Leave DVD01/DVD02/DVD03 as-is

**Pros**: Less changes, preserves DVD prefix distinction.

**Cons**: Still has two part notations (DVD01 vs Part 1); less consistent.

---

## Implementation Notes

- Changes should be made in `data/research_master_draft.csv` (the source of truth)
- `build_catalogue_pages.py` will need to be re-run to regenerate `docs/master.json`
- Tests in `tests/test_pipeline.py::test_cleaned_multi_part_titles_keep_part_detail_in_master` already expect "Part X" format
- The filename_proposal_YYYYMM.csv has `part_index` and `part_total` columns that could drive the standardization

---

## Files to Modify

1. `data/research_master_draft.csv` - Update format_detail values
2. `docs/master.json` - Regenerate from build
3. Possibly `build_research_master.py` - If standardization should be automated
4. `tests/test_pipeline.py` - May need updates if test expectations change
