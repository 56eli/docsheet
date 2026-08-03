# Research Master Reconciliation Report

**Status:** Read-only comparison; no raw CSV, review ledger, master draft, or Pages JSON was changed to produce this report.

## Purpose

This report compares the committed `data/research_master_draft.csv` with the in-memory output of `build_research_master.py` using the current `migration_review_ledger.csv`. It also checks the paired master JSON and exclusions outputs, then shows the cascade to the Everything Pages dataset if the ledger projection were used. It is a review aid, not approval to overwrite either generated file.

## Summary

| Measure | Committed state | Current ledger projection |
|---|---:|---:|
| Research-master CSV records | 308 | 308 |
| Research-master JSON records | 308 | 308 |
| Research-master exclusion records | 66 | 66 |
| Draft-only CSV records without a matching ledger `item` | 0 | 0 |
| Ledger `item` records absent from CSV draft | 0 | 0 |
| Matched CSV records with one or more field differences | 0 | 0 |
| `docs/master.json` / ledger-projected Everything records | 348 | 348 |

All checked master, exclusion, and Everything Pages outputs match the current ledger and approved source overrides.

The reviewed build applies 62 approved official-source overrides; unresolved research leads remain outside the master in their review inputs.

## Draft-only CSV records requiring a provenance decision

Each record below is present in the committed draft CSV and therefore included by the current Everything build, but is not an `item` in the current ledger projection. Retain it only by recording its approval and durable provenance in the ledger or a reviewed overrides input; otherwise it will disappear on a normal master rebuild.

| Raw row | Title | Type | Notes |
|---:|---|---|---|
| — | — | — | — |

## Ledger items absent from the committed draft

| Raw row | Title | Type |
|---:|---|---|
| — | — |

## Field differences for matching provenance rows

Each entry is an exact current-draft value followed by the current ledger-derived value. UUIDs are included if they differ, because an identity change requires review.

No matching-record field differences were found.

## Downstream Pages impact

| `catalogue-meta.json` field | Committed Pages value | Ledger-projected value |
|---|---:|---:|
| `master_items` | 348 | 348 |
| `migrated_items` | 308 | 308 |
| `implemented_unreviewed` | 42 | 42 |

## Current verification result

The reconciliation is complete. For future approved changes, update the ledger, reviewed source overrides, or manual-lead input as appropriate; rebuild the master and Pages outputs; then run all three checks below.

## Reproduce

```bash
python reconcile_research_master.py --check
python build_research_master.py --check
python build_catalogue_pages.py --check
```

`reconcile_research_master.py --check` verifies that this report still describes the current inputs. Omitting `--check` refreshes this Markdown report only; it does not change catalogue data.
