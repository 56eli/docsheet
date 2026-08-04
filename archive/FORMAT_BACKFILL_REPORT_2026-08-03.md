# Format Backfill Report — 2026-08-03

## Summary

Successfully inferred **65 out of 73 blank formats** (89.0% fill rate), reducing blank formats from **20.9% to 2.3%** of all records.

## Results

### Before
- **73 records** with blank format (20.9% of 350 master records)
- No automated inference for these records

### After
- **8 records** with blank format (2.3% of 350 master records)
- **65 formats inferred** and applied

### Format Distribution (Final)

| Format | Count | Percentage |
|--------|------:|-----------:|
| DVD | 254 | 72.6% |
| book | 29 | 8.3% |
| CD | 26 | 7.4% |
| audio | 23 | 6.6% |
| streaming | 10 | 2.9% |
| (blank) | 8 | 2.3% |

## Inference Methods

Enhanced `infer_format_from_official_source()` in `build_research_master.py` with the following patterns:

### 1. URL Slug Patterns
- **DVD**: `video`, `muscle-testing-video`, `volume-*`, `vol-*`
- **CD**: `cd-set`, `satsang` + `cd`
- **Streaming**: `question-answer`, `question-and-answer`, `q&a`
- **Audio**: `audio`, `– audio`, ` audio`
- **Book**: `book`, `(book)`

### 2. Category-Based Patterns
- **DVD**: `On the Road - Talk Series`, `Archival Office Visit Series`, `Volume Series`
- **CD**: `Satsang` (all Satsang products are CD sets)
- **Streaming**: `Discussion Series` (all discussion products are streaming)

### 3. Item-Type Fallback
- **Book**: `item_type="book"` with no URL (Hay House books without Veritas storefront)

## Remaining Blanks (8 records)

All 8 remaining blanks have **no source URL**, making format inference impossible without additional data:

| UUID | Item Type | Title | Issue |
|------|-----------|-------|-------|
| 221 | lecture | Progressive Levels of Consciousness | No URL |
| 225 | lecture | Devotion to Truth | No URL |
| 226 | lecture | Mind, Heart, and Service PART1 | No URL |
| 227 | lecture | Mind, Heart, and Service PART2 | No URL |
| 264 | untyped | "In the World But Not of It" – Audio | No URL, deferred record |
| 278 | discussion | How to Live Your Life Like a Prayer | No URL |
| 281 | discussion | Permanent Inner Peace | No URL |
| 284 | discussion | What is Real Success | No URL |

**Resolution**: These records need manual review or additional data sources to assign formats.

## Code Changes

### Modified File: `build_research_master.py`

**Function**: `infer_format_from_official_source()`

**Changes**:
1. Fixed pattern matching for `question-and-answer` (was only checking `question-answer`)
2. Added `vol-` prefix check (was only checking `volume-`)
3. Added category-based inference for DVD/CD/streaming products
4. Restructured to not return early when URL is missing (allows fallback patterns)
5. Added `item_type="book"` fallback for records without URLs

**Test Coverage**: All 93 tests pass, including format inference tests.

## Verification

- ✅ All 93 unit tests pass
- ✅ `build_research_master.py --check` passes
- ✅ `build_catalogue_pages.py --check` passes
- ✅ Format inference is deterministic and reviewable
- ✅ No existing formats were overwritten (only blanks were filled)

## Impact

- **Edition column** (display) now shows format information for 342/350 records (97.7%)
- **Year-Month column** unchanged (separate issue, requires date inference)
- **Item type** unchanged (only 1 untyped record remains: UUID 264)

## Next Steps

The remaining 8 blank formats require:
1. Manual review of the 8 records
2. Additional data sources (e.g., Veritas API lookup by title, owner knowledge)
3. Decision on whether to assign default formats or leave blank

---

**Report generated**: 2026-08-03  
**Branch**: `arena/019fc925-docsheet`  
**Test suite**: 93 tests, 92% coverage
