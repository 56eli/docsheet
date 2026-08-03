# Year-Month Backfill Report — 2026-08-03

## Summary

Successfully backfilled **86 year values** and **95 month values** using Veritas inventory `published_date` data, reducing blank year fields from 33.1% to 8.6% and blank month fields from 43.4% to 16.3%.

## Results

### Before Backfill
- **Blank year**: 116/350 records (33.1%)
- **Blank month**: 152/350 records (43.4%)

### After Backfill
- **Blank year**: 30/350 records (8.6%) — **74% reduction**
- **Blank month**: 57/350 records (16.3%) — **63% reduction**

### Backfill Details
- **Year filled**: 86 records
- **Month filled**: 95 records
- **Books**: Year filled for 26 records (month intentionally left blank for books)
- **Lectures/Discussions**: Both year and month filled where data available

## Implementation

### Enhanced Function: `backfill_months_from_official_source()`

**Location**: `build_research_master.py` (line 240)

**Changes**:
1. Now uses Veritas inventory `published_date` field (ISO format YYYY-MM-DD)
2. Backfills both year and month (previously only month)
3. Handles records without `legacy_tempid` (most records)
4. For books: only fills year (publication months not meaningful)
5. For lectures/discussions: fills both year and month
6. Retains legacy tempid-based extraction as fallback

**Logic**:
```python
# For each record with blank year/month:
# 1. Look up Veritas inventory by source_url_veritas
# 2. Extract published_date (YYYY-MM-DD format)
# 3. For books: fill year only
# 4. For lectures/discussions: fill both year and month
# 5. Fallback to legacy tempid extraction if no inventory data
```

## Remaining Blanks

### Blank Year (30 records)
All 30 records have **no source URL**, making year inference impossible:
- 12 books (Hay House books without Veritas storefront)
- 3 discussions
- 14 lectures
- 1 untyped (deferred record UUID 264)

### Blank Month (57 records)
- **38 books**: 12 without URL + 26 with URL (intentionally blank — books don't have meaningful months)
- **3 discussions**: No URL
- **15 lectures**: No URL
- **1 untyped**: No URL (deferred record UUID 264)

**Note**: The 26 books with URLs correctly have year filled but no month. This is intentional — books have publication years but months are not meaningful for catalogue purposes.

## Data Quality

### Verification
- ✅ All 93 unit tests pass
- ✅ `build_research_master.py --check` passes
- ✅ `build_catalogue_pages.py --check` passes
- ✅ Backfill is deterministic and reviewable
- ✅ No existing year/month values were overwritten

### Examples of Backfilled Records

| UUID | Title | Year | Month | Type | Source |
|------|-------|------|-------|------|--------|
| 199 | Q&A Session (Jan 2011) | 2011 | 01 | lecture | published_date |
| 200 | Q&A Session (Mar 2011) | 2011 | 03 | lecture | published_date |
| 251 | Satsang Series (Jan 2007) | 2007 | 01 | lecture | published_date |
| 286 | Power vs Force | 2014 | — | book | published_date (year only) |
| 287 | The Eye of the I | 2014 | — | book | published_date (year only) |

## Impact

### Year-Month Display Column
The UI's year-month display column now shows complete dates for **293/350 records** (83.7%), up from **198/350** (56.6%) before backfill.

### Format Distribution (Unchanged)
Format backfill from previous session remains intact:
- DVD: 254 (72.6%)
- book: 29 (8.3%)
- CD: 26 (7.4%)
- audio: 23 (6.6%)
- streaming: 10 (2.9%)
- blank: 8 (2.3%)

## Next Steps

The remaining 30 blank-year and 57 blank-month records require:
1. **Manual review**: Owner input on dates for records without URLs
2. **Additional data sources**: Hay House API, Audible API, or other publisher data
3. **Decision**: Whether to leave blank or assign estimated dates

---

**Report generated**: 2026-08-03  
**Branch**: `arena/019fc925-docsheet`  
**Test suite**: 93 tests, 92% coverage  
**Combined improvement**: Format backfill (89%) + Year-month backfill (74%/63%)
