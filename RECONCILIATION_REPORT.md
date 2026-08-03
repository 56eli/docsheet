# Research Master Reconciliation Report

**Status:** Read-only comparison; no raw CSV, review ledger, master draft, or Pages JSON was changed to produce this report.

## Purpose

This report compares the committed `data/research_master_draft.csv` with the in-memory output of `build_research_master.py` using the current `migration_review_ledger.csv`. It also checks the paired master JSON and exclusions outputs, then shows the cascade to the Everything Pages dataset if the ledger projection were used. It is a review aid, not approval to overwrite either generated file.

## Summary

| Measure | Committed state | Current ledger projection |
|---|---:|---:|
| Research-master CSV records | 317 | 317 |
| Research-master JSON records | 317 | 317 |
| Research-master exclusion records | 68 | 68 |
| Draft-only CSV records without a matching ledger `item` | 0 | 0 |
| Ledger `item` records absent from CSV draft | 0 | 0 |
| Matched CSV records with one or more field differences | 0 | 0 |
| `docs/master.json` / ledger-projected Everything records | 359 | 353 |

The checked outputs are not yet fully reconciled. Review the differences below before rebuilding so reviewed additions are not lost.

The normal `python build_catalogue_pages.py --check` evaluates Pages files against the **committed** master CSV and may pass while this cascade differs. This report identifies the upstream master/ledger divergence that must be resolved first.

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

Each entry is an exact current-draft value followed by the current ledger-derived value. Master IDs are included if they differ, because an identity change requires review.

No matching-record field differences were found.

## Downstream Pages impact

| `catalogue-meta.json` field | Committed Pages value | Ledger-projected value |
|---|---:|---:|
| `master_items` | 359 | 353 |
| `migrated_items` | 317 | 317 |
| `implemented_unreviewed` | 38 | 38 |

## Required resolution before rebuilding

1. Decide whether every draft-only record is an approved item, a documented manual candidate, or should remain outside the curated master.
2. Record approved changes to matching rows in the ledger or a versioned reviewed-overrides input; do not preserve them solely by editing generated draft CSV/JSON files.
3. Re-run this report until the reconciliation is understood and accepted.
4. Only then run `python build_research_master.py`, then `python build_catalogue_pages.py`, and verify both `--check` commands.

## Reproduce

```bash
python reconcile_research_master.py --check
python build_research_master.py --check
python build_catalogue_pages.py --check
```

`reconcile_research_master.py --check` verifies that this report still describes the current inputs. Omitting `--check` refreshes this Markdown report only; it does not change catalogue data.
