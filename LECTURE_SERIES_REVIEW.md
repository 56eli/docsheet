# Lecture Series — Migration Review Batch

**Status:** Review-only proposal; no item records, UUIDs, catalogue codes, or source data have been changed.
**Review CSV:** `lecture_series_review.csv`
**Generator:** `generate_lecture_review.py`

## Batch summary

| Measure | Value |
|---|---:|
| Candidate lecture-part records | 198 |
| Distinct proposed canonical lecture titles | 65 |
| Ownership proposal | 198 `true` (all current `LS` rows are marked ✅) |
| Valid proposed Veritas URLs | 192 |
| Quarantined malformed Veritas URLs | 3 |
| Missing product URLs | 3 |

### Candidate parts by year

| Year | Parts |
|---|---:|
| 2002 | 36 |
| 2003 | 18 |
| 2004 | 18 |
| 2005 | 30 |
| 2006 | 24 |
| 2007 | 27 |
| 2008 | 21 |
| 2009 | 12 |
| 2010 | 6 |
| 2011 | 6 |

## Canonical-title proposal rule

The batch proposes only one mechanical cleanup: remove the final parenthesized date and trailing DVD part label from each title. For example:

```text
Raw:      Causality: The Ego's Foundation (Jan 2002) DVD01
Proposed: Causality: The Ego's Foundation
```

The part remains represented separately by `format = DVD` and `format_detail = DVD01`. No other spelling, punctuation, or wording change is proposed in this batch.

## Required review points

1. Confirm that the ten proposed series labels and all year/month extractions are correct.
2. Confirm that one canonical title shared by DVD01/02/03 is desired while each disc remains a separate flat item.
3. Resolve the three quarantined August 2002 *Advaita* product links (raw rows 28–30); the source contains a duplicated URL prefix.
4. Research or provide source URLs for the three February 2007 *Relativism vs Reality* parts (raw rows 144–146), which have no product link.
5. Record approval or correction in `approval` and `review_notes` columns before any IDs are generated.

## Approval boundaries

Approving this batch would approve only the migration metadata proposals for the 198 `LS` rows. It would **not** change the raw CSV, alter the published site, create UUIDs, generate catalogue codes, or approve non-lecture records.
