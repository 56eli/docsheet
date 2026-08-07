# Schema Redundancy Review — Remaining 25 Master Columns (2026-08-07)

**Context:** owner directive after the 4-column drop: "look for other redundant
or basically useless columns to remove — ask for permission for those first."
**Method:** fill-rate + distinct-value analysis on all 365 masters, consumer
grep across scripts/sheet/tests, duplication checks.

**Status:** awaiting owner permission on the one real candidate (question at
the end). No data changed.

---

## Audit table (365 rows, 25 columns)

| Column | Filled | Verdict |
|---|---:|---|
| `uuid`, `item_type`, `series`, `title`, `format` | 365 | core identity/classification — keep |
| `work_id` | 365 (208 works) | edition grouping — keep |
| `year` (348) / `month` (238) / `year_source` (365) | partial by design | blanks are rulings (17 blank years documented); `year_source` is the evidence trail that replaced the retired year-provenance mirror — keep |
| `catalog_code` | 281 | intentional blanks (books, blank-year rows) — keep |
| `proposed_filename` | 365 | owner-facing renaming feature — keep |
| `legacy_title` | 365 (265 ≠ title) | verbatim-raw export contract (README) — keep |
| `legacy_tempid` | 243 | raw provenance ID (minted rows never had one) — keep |
| `format_detail` | 279 | carrier detail; intentional blanks — keep |
| `owned` | 321 (44 blank = "unknown" by design) | owner inventory flag — keep |
| `source_url_veritas` (336) / `hay_house` (27) / `nightingale_conant` (6) / `audible` (21) / `amazon` (18) / `reference_url_1` (64) | sparse but all real | official-source registry — the project's core mission; sparse ≠ useless — keep |
| `notes` | 78 | free-text evidence — keep |
| `raw_row_number` / `candidate_key` | 302 + 63 (complementary, every row has exactly one) | one provenance key split across two fields; merging is possible but high-churn/low-gain (reconcile + relationship logic keys on both) — **keep, not proposed** |
| `title_source` | 265 | **the one real redundancy candidate — see below** |

## Candidate: `title_source` — 97.7% self-duplicate

- 265 of 365 rows filled. **259 of those 265 are byte-identical to
  `legacy_title`** (the raw `.mp4`/`DVD01` filenames the clean titles came
  from). Only **6 rows** carry unique information (`Official listing: X` —
  evidence for the official-title cleanups), and 40 promoted/academic rows
  have it empty by construction.
- **Consumers:** one — `fetch_veritas_catalogue.py:199`
  (`dated_title = row.get("title_source") or row["title"]`, feeds the
  refresh workflow's title-dating) — which `legacy_title` can serve equally
  for every consumer case, since all non-empty values except the 6 are
  identical to `legacy_title`.
- **If dropped:** those 6 unique values relocate to `notes`
  (`Title cleaned against official listing: X` — same evidence, existing
  column), the fetcher line switches to `legacy_title or title`, and the
  master goes 25 → 24 columns.
- **If kept:** it remains the dedicated title-provenance trail at the cost of
  a 97.7%-duplicate column.

Everything else earns its place; there are no constant columns, no further
near-duplicates, and no unused consumers.
