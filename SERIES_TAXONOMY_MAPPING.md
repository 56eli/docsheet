# Series Taxonomy Mapping — Schema and Lifecycle

**Status:** Implemented 2026-08-03 and **wired into the master build**:
`build_research_master.py:apply_series_approvals()` applies every `approved`
mapping row to its master ID(s) after item assembly (it never touches
`item_type`). First application was a verified no-op — every approved series
already equalled the curated series.
**Policy:** [CATEGORY_DOMINANCE_POLICY.md](CATEGORY_DOMINANCE_POLICY.md)
**Generator:** `map_series_taxonomy.py` (stdlib only)

## What this layer is

The official Veritas `product_cat` taxonomy is the publisher's own grouping.
This layer translates it, deterministically, into `series` proposals for the
curated master, following the approved dominance rules. It **never** touches
`item_type`, and it never writes master, ledger, or Pages files.

- Publisher categories are persisted verbatim on every product in
  `data/veritas_official_products.csv` (`official_categories`), refreshed from
  `/wp-json/wp/v2/product(_cat)` by `fetch_veritas_catalogue.py`, which resolves
  term IDs to the taxonomy display names used by the policy.
- Only products matched to one or more master IDs (`matched_master_uuids`)
  enter the mapping. Unmatched products keep their own review lane
  (`data/veritas_mapping_decisions.csv`, candidate views).
- Highlights products map at series level through
  `data/series_compilation_relationships.csv`, so they are intentionally out
  of scope here (all seven are unmatched compilations).

## Files

| File | Role |
|---|---|
| `data/series_category_mapping.csv` | One row per matched official product: full publisher category list, chosen dominant category, dominance rule applied, mapped master series, review state |
| `data/series_taxonomy_review_queue.csv` | The subset the policy routes to human review, with an explicit `queue_reason` |

Both are **generated** — regenerate with `python map_series_taxonomy.py`, guard
with `--check`. Hand-edit only `review_status` / `reviewed_on` /
`review_notes` in the mapping CSV; regeneration preserves `approved` /
`rejected` rows exactly and recomputes everything else.

## Column semantics (`series_category_mapping.csv`)

| Column | Meaning |
|---|---|
| `veritas_product_id` | Official product the categories belong to |
| `official_categories` | Complete publisher taxonomy assignment (`; `-joined), preserved per policy |
| `dominant_category` | Single dominant category chosen by the rules; blank when queued |
| `dominance_rule` | Policy rule that fired (`R1`–`R9`) |
| `mapped_series` | Master `series` vocabulary value for the dominant category; blank when queued |
| `review_status` | `proposed` (clean, awaiting owner), `needs_review` (queued), `approved`, `rejected` |
| `reviewed_on` / `review_notes` | Required (ISO date + reason) for `approved`/`rejected` |

## Rules applied (mirrors the policy)

Lecture Highlights (R1, outranking annual series; Satsang + Highlights together
is queued as R2) → Satsang (R2) → Six Book Transcription Series (R5) → the single
annual lecture series (R3; *two or more annual categories on one product is
queued*) → On the Road (R4) → Archival Office Visit (R6) → Card Decks (R7) →
broad collections ranked Books > Discussion > Volume > Media Miscellaneous
(R7). `* * New Products * *` and navigation buckets never dominate (R8).
Anything left — unknown categories, unresolved term IDs — is queued with a
blank series (R9; title-based inference stays banned).

Additional guard beyond the policy: a master ID that would receive **two
different proposed series** from two matched official products (e.g. a book
edition and an audio edition of the same work sharing one master record) is a
conflict, and every involved product is queued. Two conflicting `approved`
rows for one master ID fail the generator outright.

## Review flow

1. `python map_series_taxonomy.py` — regenerate (preserves prior rulings,
   including hand-set dominance overrides like 50521's).
2. Work `data/series_taxonomy_review_queue.csv` top to bottom; record each
   ruling in the mapping CSV as `approved` (with `mapped_series`) or
   `rejected`, plus `reviewed_on` + `review_notes`. Queued rows keep their
   `queue_reason` visible even after a ruling, for transparency.
3. Approved rows apply on the next `python build_research_master.py` run —
   the build fails if approvals reference unknown IDs, lack a series, or give
   one master ID conflicting series.

## Baseline (2026-08-03, post-refresh)

150 matched products: **147 approved** (144 bulk approvals at 286/286
uuid-level agreement with the curated series, plus 3 individually ruled) and
**3 rejected** wrong-edition signals (book/audio products title-matched to the
Volume I DVD record and the 2006 discussion title-matched to the 2006 lecture
record). The queue's 6 rows are all ruled — 2 dual-signal conflicts resolved in
favour of each record's own primary product, 1 multi-annual assignment resolved
to the 2007 series by title evidence and sibling-product categorization.

The first 2026-08-03 inventory refresh (pre-mapping) dropped four stale
primary-source matches from scope (they are now `unreviewed_official_product`
candidates and no longer propose series), and relinked product 1661 from
record 300 to record 264 — matching the deferred record-264 decision
territory without touching sources.
