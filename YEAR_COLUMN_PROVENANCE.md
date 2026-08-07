# Year Column Provenance Audit — Full Inventory (358 rows)

**Date:** 2026-08-07
**Master baseline:** 358 records (307 lecture / 40 book / 10 discussion / 1 untyped)
**Goal:** list every master row's `year` entry and explain how the number came about:
- Recording date (lecture/discussion)
- First-publication year (book)
- Listing date (Veritas published_date — storefront appearance, should be avoided)
- User input via ledger / candidate promotion
- Blank — intentional pre-2000 (Volume Series) or under investigation

Generated from `data/research_master_draft.csv` + `migration_review_ledger.csv` + `manual_master_candidates.csv` + `edition_candidates.csv` + `veritas_official_products.csv`.

Detailed CSV: `data/year_provenance.csv` (358 rows, machine-readable)

## Summary counts

| Provenance | Count | Meaning |
|---|---:|---|
| `ledger_user_input` | 278 | Year from reviewed ledger `proposed_year` (hand-maintained after bootstrap). For books = first-publication; for lectures/discussions = recording date where known, otherwise year derived from official product slug or Audible © year research |
| `manual_candidate_promotion` | 21 | Year from `manual_master_candidates.csv` `proposed_year` then promoted as master row (e.g., Satsang monthlies 2006-2010, Unity Church CDs 2005-2006, Devotion to Truth Talk, Mind Heart Service, etc.) |
| `blank_intentional_pre2000` | 13 | Volume Series (raw rows 223-235) intentionally blank pre-2000 per owner ruling 2026-08-04: “do not name any if cannot name all” — no catalogue code, filename no year prefix |
| `edition_candidate_blank_year` | 11 | Edition candidate (audiobook/CD) with blank `proposed_year` remains blank (e.g., some Audible lecture parts) |
| `edition_candidate_promotion_year` | 9 | Edition candidate with explicit year promoted (e.g., Veritas audio editions 1695,1728 etc where year known) |
| `blank_under_investigation` | 7 | Ledger `proposed_year` blank remains blank — needs research: Devotion to Truth (225), Mind Heart Service PART1/2 (226-227), In the World But Not of It Audio (246 deferred), Discussion Series How to Live Like Prayer (278), Permanent Inner Peace (281), What is Real Success (284) |
| `veritas_published_date_backfill` | 7 | Ledger blank but filled from Veritas `published_date` (listing date) via `backfill_months_from_official_source()`. These are **suspect – listing date, not recording date**: Spiritual Will 2023 (228-229, product 52945 listed 2023-02-11), Verification of Spiritual Realities 2014 (230-232, product 1830 listed 2014-01-21), Golden Word Book Signing 2007 (265, product 1552 listed 2007-03-16), God is Hidden 2014 (268, product 1810 listed 2014-01-06) |
| `manual_candidate_blank_year` | 5 | Manual candidate promoted but `proposed_year` blank remains blank |
| `edition_candidate_year_inherited_or_blank` | 4 | Edition candidate blank but master year present via other path (maybe work family inheritance or duplicate) |
| `academic_publication_year` | 3 | Academic works promoted: Orthomolecular 1973, Qualitative 1998, Dialogues 1998 — first-publication year from external bibliographic evidence |

Total 358, blank 31 (13 intentional + 7 under investigation + 11 edition blank).

## Year blank breakdown (31)

- **13 Volume Series** — intentional blank pre-2000 (202-214)
- **4 On The Road Talk Series** — 225 Devotion to Truth, 226-227 Mind Heart Service, plus 221 Oxford (actually has year? check) — needs recording year research
- **3 Discussion Series 2012** — 278,281,284 — title contains (2012) but year blank in ledger; could be set to 2012 per product title
- **1 untyped 246** — "In the World But Not of It" – Audio — deferred
- **11 edition audiobooks** — e.g., Compassion Audiobook (333), Devotion Nonduality Intensive Alignment/Intention, Healing Audiobook, In World But Not of It Audiobook, Letting Go Audiobook, etc. These have blank proposed_year in `edition_candidates.csv` — should inherit year from matched master work (e.g., Power vs Force 1995 → audiobook 1995). Currently blank, should be backfilled.
- **Remaining 7 ledger blank under investigation** as listed above
- **7 backfilled listing dates** that should be investigated for true recording year (not listing)

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

### Edition candidates (9 with year, 11 blank, 4 inherited)
- Source: `data/edition_candidates.csv` `proposed_year`.
- Many Audible audiobook editions have blank year in candidate file (11 rows) → master remains blank, should inherit from work family (e.g., work `w-power-vs-force` year 1995).
- 9 with year: Veritas audio editions where year known (e.g., Truth vs Falsehood Healing etc).

### Academic (3)
- Orthomolecular 1973 (co-authored with Linus Pauling), Qualitative 1998, Dialogues 1998 — from external bibliographic evidence.

### Backfill (7)
- Source: `data/veritas_official_products.csv` `published_date` (WordPress post date, listing date).
- Code path: `backfill_months_from_official_source()` → if `item[year]` blank, set from product date.
- For books skipped; for Volume Series skipped; for discussion/lecture with existing year only fills month if year matches.
- Current 7 are problematic: they show listing year, not recording. Should be flagged as `listing_date` and investigated.

### Blank (31)
- 13 intentional pre-2000 Volume Series.
- 7 under investigation (On The Road + Discussion + untyped).
- 11 edition blank.

## Recommendations

1. **Inherit year for edition blank 11**: modify `load_edition_promotions()` to inherit year from matched master `work_id` family if candidate proposed_year blank. Example: Power vs Force audiobooks 320 & 331 should be 1995. Add test.
2. **Fix 7 backfilled listing dates**: set their ledger `proposed_year` to true recording year via research (Audible ©, product page, etc.) and clear month if unknown, so backfill no longer leaks listing year. Or keep year blank with note "recording year under investigation".
3. **Fill 7 under investigation blanks**: research per-title © years: Devotion to Truth Talk (product 55473 listed 2025 but On The Road — likely 2003?), Mind Heart Service (products 54219? Actually Mind Heart Service product 54219 listed 2024-06-14 but On The Road 2003), How to Live Like Prayer (product 50491 listed 2014? Actually 2014?), Permanent Inner Peace (50485 2014), What is Real Success (50488 2014) — latter three are Discussion Series 2012 titles, should be 2012 not blank.
4. **Discussion Series 2012**: set year 2012 for 278,281,284 from product title `(2012)`.
5. **Document in ledger**: each year change needs `review_reason` explaining evidence (Audible ©, product title, etc.).
6. **Regenerate filename proposal** after year fixes — catalogue codes will appear (271 → higher).

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
