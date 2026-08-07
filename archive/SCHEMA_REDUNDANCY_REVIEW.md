# Schema Redundancy Review — Remaining 25 Master Columns (2026-08-07)

**Context:** owner directive after the 4-column drop: "look for other redundant
or basically useless columns to remove — ask for permission for those first."
**Method:** fill-rate + distinct-value analysis on all 365 masters, consumer
grep across scripts/sheet/tests, duplication checks.

**Status:** EXECUTED 2026-08-07 — owner approved all three candidates
(drop `title_source`, stop `docs/meta.json`, trim Original view). Master 25 →
24 columns; suite 112 → 110; all checks green. Details in the handoff's
2026-08-07 session entry.

## Second pass (owner pick 2026-08-07): all 20 published sheets

Every `docs/*.json` sheet was scanned for all-empty / constant columns and
cross-file consumers were grepped (`docs/app.js`, pipeline scripts, tests).

**Reviewed and kept (not proposed):**

- `migration-review.json` / `master-exclusions.json` — their empty
  `raw_unnamed_8/9/10`, `raw_other_links`, `raw_product_link`, `raw_uuid`
  columns are verbatim provenance mirrors of the raw spreadsheet's own empty
  cells, already parked in the app's low-priority field list.
- `manual-candidates.json` `proposed_owned` (all blank) — designed vocabulary
  slot; current owner policy is "ownership intentionally unknown", a future
  candidate may use it.
- Constant vocabulary columns (`review_status: approved`, `source_name:
  veritas`, `record_type: master`, …) — invariant-*bearing*, not redundant;
  they must be able to express other values.
- `new-work-review.json` / `official-discovery.json` (0 rows) — intake lanes,
  adjudicated in hygiene batch 1 (README note still owed).
- `manual-leads.json` (1 row), `international-products.json` notes column,
  `data.json` vs `master.json` (original-raw view vs curated master — different
  sheets by design).

**New candidates found:**

1. **`docs/meta.json` — stop generating (genuinely useless).** Its only
   consumer is `process_data.py`'s own staleness self-check. The app never
   fetches it (per-view `fetch(view.file)` only; the footer uses the HTTP
   `Last-Modified` header, and the `app.js` line-3 "loads meta.json" comment
   is stale). Its `generated_at_utc` also churns every regeneration.
   Removal = delete file + strip emit/self-check from `process_data.py` +
   adapt its 2 failure-path tests + delete the stale app.js comment.
2. **`data.json` (Original Spreadsheet view) — trim 5 all-empty raw columns.**
   `uuid`, `Unnamed: 8/9/10`, `other links` are empty on all 374 rows (the raw
   CSV on disk keeps them untouched). Same class as the dropped master
   columns, but at *view* level. Optional — it trades verbatim-view purity
   for 13 → 8 columns.

(+ the deferred master candidate `title_source` from pass 1.)


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
