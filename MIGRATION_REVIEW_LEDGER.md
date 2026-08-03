# Migration Review Ledger

**Status:** Generated review artifact; no raw data or public site data has been modified.
**Generator:** `generate_migration_ledger.py`
**Ledger:** `migration_review_ledger.csv`

## Purpose

The ledger is the approval surface for migrating the existing spreadsheet into the proposed research-master schema. It retains every raw data row with its original CSV row number and values, alongside conservative proposed classification and metadata. It must be reviewed before any curated dataset is generated.

## Current classification summary

| Proposed disposition | Rows | Treatment |
|---|---:|---|
| `item` | 308 | Candidate flat catalogue records. No UUID or catalogue code has been assigned yet. |
| `blank_separator` | 31 | Empty presentation rows; retained as raw provenance only. |
| `series_context` | 21 | Annual/category labels used only to propose a `series` tag for following item candidates. |
| `research_note` | 8 | Editorial gaps, missing-material reminders, or ambiguous note rows; not items until identity is confirmed. |
| `source_context` | 5 | Landing/reference URLs embedded as title rows; not items. |
| `needs_review` | 1 | Ambiguous non-empty row requiring direct decision before migration. |
| **Total** | **374** | Matches the current source data rows and published JSON row count. |

## Safe proposal rules applied

- The raw source CSV is read only; it is not altered.
- No UUIDs or catalogue codes are generated yet.
- `LSYYYYMM_part` values only suggest year/month, lecture type, DVD detail, and series context; they are retained unchanged as `raw_tempid`.
- ✅ and ❌ are only proposed as `true` and `false` on candidate item rows; blank stays blank.
- Existing valid Veritas product links are proposed as `source_url_veritas` on item candidates.
- The known duplicated-prefix Veritas URL is **quarantined**, not silently corrected, on raw rows 28–30.
- The field `format` is not populated from the raw `format` column because that column contains a Discord URL rather than media-format data.
- No title is automatically canonicalized. The current title is copied only as a review proposal.

## How to review the CSV

Open `migration_review_ledger.csv` in GitHub, a spreadsheet app, or a CSV-aware editor. Review in this order:

1. Filter `disposition = item`; verify the title, series, type, year/month, format, ownership, and Veritas URL proposals.
2. Filter `disposition = needs_review` and `research_note`; decide whether each row is a confirmed missing item, source context, note, or should be excluded.
3. Filter `review_reason` for `quarantined`; decide the intended replacement for the malformed August 2002 product URL.
4. Review `series_context` rows before accepting series assignments for associated items.
5. Approve batches by collection (for example, lecture series first), rather than applying all rows at once.

## Known limitations

This is deliberately a conservative structural classification, not a claim that all 308 candidate rows are ready to publish as research-master items. In particular, non-lecture material needs individual evidence review, title canonicalization, item type confirmation, and source/location enrichment.
