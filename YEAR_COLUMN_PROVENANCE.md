# Year Column Provenance Audit — Full Inventory (358 rows)

**Date:** 2026-08-07 (updated 2026-08-07 evening: 11 edition blank years fixed via inheritance)
**Master baseline:** 366 records (310 lecture / 40 book / 8 discussion / 7 highlight / 1 other) — after the 2026-08-07 rulings; blank years 17 (13 intentional + 4 under investigation), blank formats **0** (Oxford 2003 talk verified streaming-only 2026-08-07)
**Goal:** list every master row's `year` entry and explain how the number came about:
- Recording date (lecture/discussion)
- First-publication year (book)
- Listing date (Veritas published_date — storefront appearance, should be avoided)
- User input via ledger / candidate promotion / work-family inheritance
- Blank — intentional pre-2000 (Volume Series) or under investigation

Generated from `data/research_master_draft.csv` + `migration_review_ledger.csv` + `manual_master_candidates.csv` + `edition_candidates.csv` + `veritas_official_products.csv`.

Detailed CSV: `data/year_provenance.csv` (358 rows, machine-readable) — regenerated after fix.

## Summary counts (after 2026-08-07 fix: 11 lecture audiobook editions now inherit year from matched master)

| Provenance | Count | Meaning |
|---|---:|---|
| `ledger_user_input` | 278 | Year from reviewed ledger `proposed_year` (hand-maintained after bootstrap). For books = first-publication; for lectures/discussions = recording date where known, otherwise year derived from official product slug or Audible © year research |
| `manual_candidate_promotion` | 21 | Year from `manual_master_candidates.csv` `proposed_year` then promoted as master row (e.g., Satsang monthlies 2006-2010, Unity Church CDs 2005-2006, Devotion to Truth Talk, Mind Heart Service, etc.) |
| `edition_candidate_promotion_year_inherited` | 20 | Edition candidate — year inherited from matched master (lecture recording year) or explicit promotion year. Includes 9 original explicit + 11 fixed Audible/HH lecture audiobooks (2002-2007) |
| `blank_intentional_pre2000` | 13 | Volume Series (raw rows 223-235) intentionally blank pre-2000 per owner ruling 2026-08-04: “do not name any if cannot name all” — no catalogue code, filename no year prefix |
| `blank_under_investigation` | 7 | Ledger `proposed_year` blank remains blank — needs research: Devotion to Truth (225), Mind Heart Service PART1/2 (226-227), In the World But Not of It Audio (246 deferred), Discussion Series How to Live Like Prayer (278), Permanent Inner Peace (281), What is Real Success (284) |
| `veritas_published_date_backfill` | 7 | Ledger blank but filled from Veritas `published_date` (listing date) via `backfill_months_from_official_source()`. These are **suspect – listing date, not recording date**: Spiritual Will 2023 (228-229, product 52945 listed 2023-02-11), Verification of Spiritual Realities 2014 (230-232, product 1830 listed 2014-01-21), Golden Word Book Signing 2007 (265, product 1552 listed 2007-03-16), God is Hidden 2014 (268, product 1810 listed 2014-01-06) |
| `manual_candidate_blank_year` | 5 | Manual candidate promoted but `proposed_year` blank remains blank |
| `edition_candidate_year_inherited_or_blank` | 4 | Edition candidate blank but master year present via other path (maybe work family inheritance or duplicate) |
| `academic_publication_year` | 3 | Academic works promoted: Orthomolecular 1973, Qualitative 1998, Dialogues 1998 — first-publication year from external bibliographic evidence |

Total 358 → 356 → 363 → **366** (legacy duplicates 281/284 excluded; 7 Highlights promoted; NC/Audible/Hay House programs 369-372 added; record 246 excluded as duplicate of 329), blank years **17** (13 intentional + 4 under investigation), blank formats **0**.

Fix applied 2026-08-07: `data/edition_candidates.csv` 11 Audible/HH lecture audiobooks (edition-audible-wtg-nature/advaita/root, dni-intention/alignment, tms-id/emotions, srmm-godvs, tlc-perception, compassion, hh-liveprayer) now have `proposed_year` = matched master year (2002-2007). `build_catalogue_pages.py` excludes edition rows from series-compilation lecture count (raw_row_number filter) to prevent Highlights counts inflating from 6→8.

## Year blank breakdown (18 after fix, was 31)

- **13 Volume Series** — intentional blank pre-2000 (202-214)
- **3 Verification of Spiritual Realities** (230-232) — under investigation (backfilled 2014 listing year cleared)
- **1 untyped 246** — "In the World But Not of It" – Audio — deferred, blank
- **1 God is Hidden Within the Beauty of the Music** (268) — under investigation (backfilled 2014 listing year cleared)
- **Resolved earlier**: Discussion Series 278/281/284 → 2012 per product title `(2012)` (281/284 then excluded 2026-08-07 as duplicates of 312/313); On The Road 225-227 now have ledger recording years
- **Previously 11 edition audiobooks** (333-343) — fixed 2026-08-07 by inheriting year from matched master: now all have year (2002-2007)

Remaining blank = 13 intentional + 4 under investigation = **17**.

## Fixed 2026-08-07: edition year inheritance

| Candidate | Matched master | Year inherited |
|---|---|---:|
| edition-audible-wtg-nature (The Way to God: Nature of Divinity…) | 19 | 2002 |
| edition-audible-wtg-advaita | 22 | 2002 |
| edition-audible-wtg-root | 13 | 2002 |
| edition-audible-dni-intention | 79 | 2005 |
| edition-audible-dni-alignment | 76 | 2005 |
| edition-audible-tms-id | 64 | 2004 |
| edition-audible-tms-emotions | 61 | 2004 |
| edition-audible-srmm-godvs | 127 | 2007 |
| edition-audible-tlc-perception | 106 | 2006 |
| edition-audible-compassion | 267 | 2003 |
| edition-hh-liveprayer | 121 | 2006 |

Code fix: `build_catalogue_pages.py` `validate_series_compilations()` now filters `raw_row_number` non-empty, so edition audiobooks with year 2002-2007 do not inflate Highlights compilation counts (e.g., Transcending Mind 2004 expected 6, would have found 8 after year fill). This preserves official Highlights evidence (6 lectures) while keeping edition years.

### Edition candidates (20 with year, 4 inherited/blank, etc)
- Source: `data/edition_candidates.csv` `proposed_year`.
- After fix, 20 have explicit year (9 original + 11 inherited from matched master).
- 4 Veritas audio editions (tvf-cddvd, healing-audio, itwbnoi-audio, hle-audio) have blank proposed_year but get year via `published_date` backfill (2011,2010,2009,2012) — listing year, acceptable as audio release.

### Blank (18)
- 13 intentional pre-2000 Volume Series.
- 4 under investigation (Verification of Spiritual Realities 230-232 + God is Hidden 268).

## Detailed per-row (abbreviated — full CSV is authoritative)

| UUID | Title | Type | Series | Year | Y-Type | Detail |
|---: |---|---|---|---:|---|---|

*Full table in `data/year_provenance.csv` — 358 rows. Below is sample tail:*

```
202 Volume I-Power vs Force (Part 1) lecture Volume Series  blank_intentional_pre2000
203 Volume I-David Hawkins -Applied Kinesiology-Power vs Force - Part 2 lecture Volume Series  blank_intentional_pre2000
...
225 Devotion to Truth lecture On The Road Talk Series  blank_under_investigation  ledger raw 249 proposed_year blank remains blank
226 Mind, Heart, and Service PART1 lecture On The Road  blank_under_investigation
227 Mind, Heart, and Service PART2 lecture On The Road  blank_under_investigation
228 Spiritual Will PART1 lecture On The Road 2023 veritas_published_date_backfill product 52945 published_date 2023-02-11 (listing date, should be recording)
229 Spiritual Will PART2 same 2023 backfill
230 Verification of Spiritual Realities lecture On The Road 2014 backfill product 1830 2014-01-21
...
246 "In the World But Not of It" – Audio  Media Miscellaneous  blank_under_investigation ledger raw 296
...
278 How to Live Your Life Like a Prayer discussion Discussion Series  blank_under_investigation
281 Permanent Inner Peace discussion Discussion Series  blank_under_investigation
284 What is Real Success discussion Discussion Series  blank_under_investigation
...
```

## Recording date vs Listing date — policy

- **Books:** `year` = first-publication year, never Veritas `published_date`. `backfill_months_from_official_source()` skips `item_type=book`. Enforced by test `test_books_use_first_publication_year_not_product_listing`.
- **Lectures/Discussions:** `year` = recording date where known, otherwise fallback to publisher product date **only if product's year matches record's year** (month guard). Backfill fills missing year **and** month from Veritas `published_date` only when ledger year blank — this is currently how 7 rows got listing years (228-232,265,268). Those need verification: e.g., Spiritual Will was recorded pre-2012 (Hawkins died 2012) but listed 2023 — year 2023 is listing, should be recording year.
- **Volume Series:** year intentionally blank pre-2000 per owner. `backfill_months_from_official_source()` explicitly skips `series == Volume Series`.
- **Audible © year:** For On-the-Road talks, Audible © year is reliable recording year (©2003-2005) and varies, not uniform 2003. Already corrected 13 On-the-Road talks.

## How each number was derived — method per type

### Ledger rows (278)
- Source: `migration_review_ledger.csv` column `proposed_year`.
- Hand-maintained after bootstrap `generate_migration_ledger.py`. Reviewed reason in ledger documents research.
- For classic books (Power vs Force 1995, Eye of I 2001, etc.): first-publication year from bibliographic research (Amazon, Open Library, etc.), not 2014-03-30 batch listing date.
- For lectures 2002-2011: year from product slug `2008-10-practical-spirituality-oct-2008` → 2008, or from title `(Jan 2002)`, or from Audible ©.
- For Office Series 1982: owner pointed out Hawkins died 2012, Office CDs 1982 → year set to 1982.

### Manual candidates (21 + 5 blank)
- Source: `data/manual_master_candidates.csv` `proposed_year`.
- Satsang monthlies (344-352): year from Veritas product title date extraction e.g., `Satsang Series (Jan 2006)` → 2006, per SATSANG_MAPPING_DECISIONS Addendum.
- Unity Church CDs (1546/1548 → masters 311? actually 310-311 etc): March 2005, June 2006 from product title.
- Book candidates (38608, 47979 etc): first-publication year (e.g., Book of Slides, Ego is Not Real You).

### Edition candidates (20 with year after fix, 4 with backfill year)
- Source: `data/edition_candidates.csv` `proposed_year`.
- Before fix, 11 Audible/HH lecture audiobooks had blank year → master blank. Fixed 2026-08-07 by setting proposed_year = matched master year (2002-2007).
- After fix: 20 with explicit year (9 original + 11 inherited).
- 4 Veritas audio editions (tvf-cddvd, healing-audio, itwbnoi-audio, hle-audio) keep blank proposed_year but receive year via `published_date` backfill (2011,2010,2009,2012) — audio release year, acceptable.

### Academic (3)
- Orthomolecular 1973 (co-authored with Linus Pauling), Qualitative 1998, Dialogues 1998 — from external bibliographic evidence.

### Backfill (7)
- Source: `data/veritas_official_products.csv` `published_date` (WordPress post date, listing date).
- Code path: `backfill_months_from_official_source()` → if `item[year]` blank, set from product date.
- For books skipped; for Volume Series skipped; for discussion/lecture with existing year only fills month if year matches.
- Current 7 are problematic: they show listing year, not recording. Should be flagged as `listing_date` and investigated. They are: 228-229 Spiritual Will 2023, 230-232 Verification 2014, 265 Golden Word 2007, 268 God is Hidden 2014.

### Blank (18 after fix)
- 13 intentional pre-2000 Volume Series.
- 4 under investigation (Verification of Spiritual Realities 230-232 + God is Hidden 268).

## Recommendations (updated after fix)

1. **✅ Done 2026-08-07: inherit year for edition blank 11** — 11 lecture audiobook editions now have year 2002-2007.
2. **Fix 7 backfilled listing dates**: set their ledger `proposed_year` to true recording year via research (Audible ©, product page, etc.) and clear month if unknown, so backfill no longer leaks listing year. Or keep year blank with note "recording year under investigation".
3. ~~**Fill the under-investigation blanks**~~ — **2026-08-07 research**: record 246 resolved (duplicate of 329); Devotion/Mind Heart/Discussion-2012 resolved earlier. Remaining 4 (230-232, 268): no recording-year evidence reachable — Veritas product/streaming/series pages state none, no Audible listing exists, Amazon shows only the 2015 CD re-release (God is Hidden), Vimeo trailer page removed. Keep blank per the no-guessing rule; revisit with physical-media evidence.
4. ~~**Discussion Series 2012**: set year 2012 for 278,281,284 from product title `(2012)`.~~ — **done**; 281/284 were then excluded 2026-08-07 as duplicates of promoted masters 312/313 (owner ruling), so only 278 remains in the master with that provenance.
5. **Document in ledger**: each year change needs `review_reason` explaining evidence (Audible ©, product title, etc.).
6. **Regenerate filename proposal** after year fixes — catalogue codes will appear (now 278 after the 2026-08-07 year-provenance fixes and the 281/284 exclusion; codes only appear once a record has a year).

## Full CSV columns

`data/year_provenance.csv`:
- uuid
- title
- item_type
- series
- year
- month
- raw_row_number
- candidate_key
- source_url_veritas
- year_source_type (enum as above)
- year_source_detail (human explanation with product IDs, dates, evidence)

*Generated 2026-08-07 via Python script in audit.*

## Veritas workflow status

2026-08-07 workflow run reported **Status success, artifact without content** → live inventory 191 matches committed, no drift. Method: `fetch_veritas_catalogue.py` + overlay 18 decisions.

*End of year provenance doc.*
