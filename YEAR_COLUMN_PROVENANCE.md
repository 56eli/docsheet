# Year Column Provenance — Policy & Audit Notes

**Status:** living policy doc (slimmed 2026-08-07).
**Authoritative per-row data:** the curated master's `year`, `month`, and
`year_source` columns (`data/research_master_draft.csv` /
`docs/master.json`). Do **not** re-create a separate CSV mirror — the
retired `data/year_provenance.csv` drifted twice (its doc claimed "358 rows"
while the file held 368), and duplicated what the master already exposes.
Current per-source counts are derivable from `year_source` on demand.

**Master baseline at last audit:** 365 records (309 lecture) after the
2026-08-07 rulings; blank years **17** (13 intentional pre-2000 Volume Series
+ 4 under investigation where no recording-year evidence is reachable),
blank formats **0**.

## What `year` means per item type

- **Lecture / discussion:** recording date where known (ledger `proposed_year`).
- **Book:** first-publication year — never the Veritas storefront
  `published_date`. `backfill_months_from_official_source()` skips books;
  enforced by `test_books_use_first_publication_year_not_product_listing`.
- **Volume Series (pre-2000):** intentionally blank per owner ruling
  2026-08-04 ("do not name any if cannot name all") — no catalogue code, no
  year prefix in filenames; backfill explicitly skips the series.
- **Edition release dates are not lecture recording dates:** four promoted
  carrier rows (327–330) use reviewed Veritas `published_date` backfills as
  their edition release year (`year_source = Veritas listing backfill (edition)`).
  They must not be read as recording dates for their related lecture work.
- **Rows 228–232, 265, and 268 do not currently use listing-date backfills:**
  228/229 retain ledger recording year 2004; 230–232 and 268 remain blank under
  investigation; 265 retains ledger recording year 2007.

## How each number is derived (method per source)

- **Ledger (`migration_review_ledger.csv` `proposed_year`):** hand-maintained
  after the `generate_migration_ledger.py` bootstrap; every change carries a
  `review_reason` with evidence (product slug dates `(2008-10-...)`, title
  dates, Audible © years, owner input — e.g. Office Series 1982, Hawkins died
  2012).
- **Manual candidates:** `manual_master_candidates.csv` `proposed_year`
  (Satsang monthlies from product-title months; Unity Church CDs 2005/2006;
  book candidates = first-publication).
- **Edition candidates:** `edition_candidates.csv` `proposed_year` — explicit
  or inherited from the matched master (2026-08-07 fix: 11 Audible/Hay House
  lecture audiobooks inherit the master recording year 2002-2007 instead of
  blank; 4 Veritas audio editions keep `published_date` audio-release years
  2009-2012, acceptable as release years).
- **Academic works (359-361):** first-publication year from external
  bibliographic evidence (1973 / 1998 / 1998).
- **Backfill:** `backfill_months_from_official_source()` fills year+month from
  Veritas `published_date` only when the ledger year is blank (books and
  Volume Series skipped; for rows with an existing year it fills month only
  when the years match).

## 2026-08-07 code note

`build_catalogue_pages.py` `validate_series_compilations()` filters on
non-empty `raw_row_number`, so edition audiobook years (2002-2007) do not
inflate Highlights compilation lecture counts (e.g. Transcending Mind 2004:
official evidence = 6; unfiltered counting would have found 8).

## Open work

1. **Four edition release dates (327–330):** retain them as carrier-release
   dates unless better edition evidence surfaces; do not promote them to a
   lecture recording date. The distinct blank-year work remains item 2 below.
2. **4 under-investigation blanks (230-232, 268):** Veritas product/streaming/
   series pages state no recording year; no Audible listing exists; Amazon
   shows only a 2015 CD re-release (God is Hidden); Vimeo trailer removed.
   Keep blank per the no-guessing rule; revisit with physical-media evidence.
3. Every year change documents its evidence in the ledger `review_reason`.
