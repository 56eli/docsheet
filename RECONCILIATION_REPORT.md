# Research Master Reconciliation Report

**Status:** Read-only comparison; no raw CSV, review ledger, master draft, or Pages JSON was changed to produce this report.

## Purpose

This report compares the committed `data/research_master_draft.csv` with the in-memory output of `build_research_master.py` using the current `migration_review_ledger.csv`. It also checks the paired master JSON and exclusions outputs, then shows the cascade to the Everything Pages dataset if the ledger projection were used. It is a review aid, not approval to overwrite either generated file.

## Summary

| Measure | Committed state | Current ledger projection |
|---|---:|---:|
| Research-master CSV records | 365 | 365 |
| Research-master JSON records | 365 | 365 |
| Research-master exclusion records | 72 | 72 |
| Committed draft records without matching raw/candidate provenance | 0 | 0 |
| Projected records absent from committed draft | 0 | 0 |
| Matched records with one or more field differences | 0 | 0 |
| `docs/master.json` / ledger-projected Everything records | 365 | 365 |

All checked master, exclusion, and Everything Pages outputs match the current ledger and approved source overrides.

The reviewed build applies 134 approved official-source overrides and validates 39 reviewed manual candidates; unresolved research leads remain outside the master in their review inputs.

## Committed draft records without matching provenance

Each record below is present in the committed draft but cannot be matched to either a raw-ledger `raw_row_number` or an approved candidate `candidate_key` in the current projection. It requires a provenance decision before rebuilding.

| Provenance | Title | Type | Notes |
|---|---|---|---|
| — | — | — | — |

## Projected records absent from the committed draft

| Provenance | Title | Type |
|---|---|---|
| — | — |

## Field differences for matching provenance rows

Each entry is an exact current-draft value followed by the current ledger-derived value. Master IDs are included if they differ, because an identity change requires review.

No matching-record field differences were found.

## Downstream Pages impact

| `catalogue-meta.json` field | Committed Pages value | Ledger-projected value |
|---|---:|---:|
| `master_items` | 365 | 365 |
| `migrated_items` | 365 | 365 |
| `implemented_unreviewed` | 0 | 0 |

## Current verification result

The reconciliation is complete. For future approved changes, update the ledger, reviewed source overrides, or manual-lead input as appropriate; rebuild the master and Pages outputs; then run the checks below.

## Reproduce

```bash
python reconcile_research_master.py --check
python build_research_master.py --check
python build_catalogue_pages.py --check
python map_series_taxonomy.py --check
python sync_inventory_mirrors.py --check
```

`reconcile_research_master.py --check` verifies that this report still describes the current inputs. Omitting `--check` refreshes this Markdown report only; it does not change catalogue data.
