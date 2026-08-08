# Review-Gated Data Model — Slimming & Dedup Analysis

**Date:** 2026-08-04
**Status:** Historical analysis snapshot; its counts describe the 2026-08-04 state and are not current.
**Scope:** Audit every curated input and review lane in the pipeline for
redundancy and behavior-preserving cleanup potential, per owner request
("do we really need product relationships and migration review? is there
cleanup potential?").

---

## 1. How the model is layered

The curated master (`data/research_master_draft.csv`, 356 records) is **not**
hand-edited. It is assembled by `build_research_master.py` from a set of
review-gated inputs, each of which is a committed CSV that only an approved
reviewer edits:

| Input | Rows | Load-bearing? |
|---|---|---|
| `migration_review_ledger.csv` | 374 | **CORE** — the master source (306 items + exclusions/context) |
| `veritas_official_products.csv` | 191 | **CORE** — official inventory (matching, month/format backfill) |
| `work_families.csv` | 332 | **CORE** — groups edition rows into works (never title-inferred) |
| `manual_master_candidates.csv` + `manual_candidate_promotions.csv` | 26 + 26 | promotion lane → mints master rows |
| `edition_candidates.csv` + `edition_promotions.csv` | 24 + 24 | edition lane → mints master rows |
| `research_master_source_overrides.csv` | 110 | URL additions after the ledger |
| `series_category_mapping.csv` | 179 | taxonomy → `series` approvals |
| `product_relationships.csv` | **333** | reviewed item→product assertions (rendered tab) |
| `series_compilation_relationships.csv` | 7 | compilation links (rendered tab) |
| `veritas_mapping_decisions.csv` | 18 | product-ID overlay re-applied on live refresh |
| `series_taxonomy_review_queue.csv` | 6 | taxonomy review queue |
| `official_discovery_queue.csv` | 4 | discovery queue |
| `new_work_review_queue.csv` | 0 | new-work queue (empty) |
| `international_discovery_queue.csv` | 36 | international leads |
| `research_manual_leads.csv` | 1 | manual leads |
| `audible_official_products.csv` / `hayhouse_official_products.csv` | 26 / 24 | publisher inventories |

---

## 2. Answering the specific questions

### Do we really need **product relationships**?
**Mostly not as a separate file.** `product_relationships.csv` has 333 rows,
but **325 are `primary_product_for_item_part`** — and I verified **all 325
exactly duplicate the master's own `source_url_veritas`** (294/325 are fully
derivable: same `raw_row_number`, same `evidence_url` = same URL; the rest
differ only in trivially-derivable provenance for minted edition/candidate
rows). Only **8 `related_material`** rows are genuinely distinct curated
evidence.

So the master already carries the primary-product link; a separate CSV that
mirrors it 325 times, plus the 113-line `validate_product_relationships` and
39-line `validate_primary_relationship_coverage` guards, is **~97% redundant
bookkeeping**. The primary relationships could be **derived from the master at
render time**, leaving `product_relationships.csv` to hold only the 8 distinct
rows.

> ⚠️ This is behavior-adjacent (the Product Relationships **tab** and its
> validation would be re-derived), so it needs owner confirmation before I
> implement it. It is the single biggest cleanup available.

### Do we really need **migration review**?
**Yes — it *is* the master.** `migration_review_ledger.csv` is the source of
every curated record; there is no master without it. What *can* be trimmed is
the surrounding ceremony:
- `generate_migration_ledger.py` / `generate_lecture_review.py` are **one-off
  bootstrap** tools (documented as such) — their outputs are hand-maintained
  afterward. They're only run by a maintainer resetting the ledger.
- `docs/migration-review.json` (the "Migration Review" tab) is just the ledger
  rendered — not an extra input. It could be dropped if the owner doesn't need
  a browser view of the ledger, but it's free (generated, not maintained).

---

## 3. Cleanup candidates, ranked by value / risk

### F1 — **Product relationships: derive the 325 primary rows** (highest value)
- Eliminates ~325 hand-maintained CSV rows and 152 lines of validation.
- `product_relationships.csv` shrinks to the 8 `related_material` rows.
- Site tab re-renders the same data, derived from `master.source_url_veritas`
  + inventory enrichment.
- **Risk:** medium (tab content must re-derive identically); behavior-adjacent.
- **Effort:** medium.

### F2 — **Merge the two candidate lanes (manual + edition)** (high value)
`manual_master_candidates.csv` + `manual_candidate_promotions.csv` and
`edition_candidates.csv` + `edition_promotions.csv` are **two copies of the
same "candidate → promotion" pattern** (26 + 24 rows, near-identical schemas).
Merging into one `candidates.csv` + `promotions.csv` (with a `lane` column)
would remove ~200 lines of parallel validation (`validate_manual_candidates` +
`load_promotions` + `validate_edition_candidates` + `load_edition_promotions`).
- **Risk:** medium-high (the promotion paths mint master rows with pinned
  UUIDs; must preserve that exactly).
- **Effort:** medium-high.

### F3 — **Consolidate the small review queues** (low-moderate value)
`new_work_review_queue.csv` (0), `official_discovery_queue.csv` (4),
`international_discovery_queue.csv` (36), `research_manual_leads.csv` (1),
`series_taxonomy_review_queue.csv` (6) are five separate tiny lanes with
separate validators. They could merge into one `review_queues.csv` with a
`queue_type` column → removes 4 files + several validators.
- **Risk:** low-moderate (these are display/review lanes, not master inputs).
- **Effort:** low-moderate.

### F4 — **Dedupe validation across generators** (low value, safe)
`build_catalogue_pages.py` re-validates invariants that
`build_research_master.py` already checked (Veritas inventory consistency,
work-family coverage, relationships). Some checks are genuinely
cross-cutting (master↔inventory) and worth keeping; others re-read the same
inputs. A pass to remove the pure overlaps would shave `build_catalogue_pages.py`
(after F1, its `validate_product_relationships` and
`validate_primary_relationship_coverage` largely vanish).
- **Risk:** low. **Effort:** medium.

### F5 — **Drop the empty/redundant review tabs** (low value, safe)
`new_work_review_queue.csv` is empty and `migration-review.json` duplicates the
ledger. If the owner doesn't use those tabs, they can be removed from the UI +
generators.
- **Risk:** low. **Effort:** low.

---

## 4. What is genuinely essential (do not cut)

- **`migration_review_ledger.csv`** — the master itself.
- **`veritas_official_products.csv`** — the official inventory (matching,
  dates, formats).
- **`work_families.csv`** — edition grouping (the C2 lesson: never infer).
- **The promotion registries** (`manual_candidate_promotions.csv`,
  `edition_promotions.csv`) — these are the *approval* record that mints
  master rows; they're the review gate, not overhead.
- **`series_category_mapping.csv`** — the taxonomy ruling record.
- **`research_master_source_overrides.csv`** — post-ledger URL additions.

The rest is either derivable (F1) or consolidatable (F2, F3, F5).

---

## 5. Recommendation

The highest-value, owner-reviewable first cut is **F1 (derive the 325 primary
product relationships)** — it deletes ~97% of a 333-row file and ~150 lines of
validation with a re-derivable result. F3 (queue consolidation) is the safest
additional low-effort win. F2 (candidate-lane merge) is the biggest structural
cut but carries the most risk and should be done carefully and last.

> **Update (2026-08-04):** **F1 is now implemented** on branch
> `arena/019fcd2c-docsheet`. `derive_primary_relationships` in
> `build_catalogue_pages.py` derives the 325 primary rows from the master;
> `data/product_relationships.csv` is 333 → **8 rows** (only `related_material`);
> `validate_primary_relationship_coverage` removed. The rendered
> `docs/product-relationships.json` has the identical 333 relationship IDs
> (only 4 `evidence_note` texts normalize). Tests 101 → 100 (replaced 6
> obsolete coverage-guard tests with 5 `DerivedPrimaryRelationshipTests`), 92%
> coverage, all 5 `--check` modes green.

> **Update (2026-08-04):** **F3 is not recommended and was skipped.** After
> inspecting the five queues' schemas they are distinct domains (candidate /
> international / manual-leads / taxonomy) with different columns; a force-merge
> into one `review_queues.csv` would create a wide, mostly-empty sparse file,
> keep every per-type validator (filtering by `queue_type`), and couple
> unrelated review lanes — a net negative that does not serve the goal of
> slimming the pipeline. The two near-identical candidate queues
> (`new_work_review_queue` + `official_discovery_queue`) could merge, but that
> is cosmetic (they render as separate tabs) and was also left as-is.

The project remains green (100 tests, 92% coverage, all checks).
