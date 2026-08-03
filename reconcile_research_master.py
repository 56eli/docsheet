#!/usr/bin/env python3
"""Report, without changing catalogue data, where the master draft diverges.

The report compares the committed research-master draft with the in-memory
projection of the current migration ledger. It also projects the Pages
catalogue from that ledger-derived master, so reviewers can see the downstream
impact before any generated file is overwritten.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path

import build_catalogue_pages
import build_research_master

REPORT = Path("RECONCILIATION_REPORT.md")
CURRENT_MASTER = Path("data/research_master_draft.csv")
CURRENT_MASTER_JSON = Path("data/research_master_draft.json")
CURRENT_EXCLUSIONS = Path("data/research_master_exclusions.csv")
CURRENT_CATALOGUE = Path("docs/master.json")
CURRENT_META = Path("docs/catalogue-meta.json")


@dataclass
class DraftComparison:
    """The review-relevant differences between committed and ledger-built draft."""

    extras: list[dict[str, str]]
    missing: list[dict[str, str]]
    changed: list[tuple[dict[str, str], dict[str, str], list[str]]]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def markdown_cell(value: str) -> str:
    """Safely render one compact Markdown table cell."""
    value = value.replace("|", "\\|").replace("\n", " ").strip()
    return value or "—"


def code(value: str) -> str:
    """Render an exact inline value while keeping empty values visible."""
    value = value.replace("`", "\\`").replace("\n", " ")
    return f"`{value or '∅'}`"


def raw_sort_key(row: dict[str, str]) -> tuple[int, int | str, str]:
    raw = row.get("raw_row_number", "")
    return (0, int(raw), row.get("title", "")) if raw.isdigit() else (1, raw, row.get("title", ""))


def compare_drafts(
    committed: list[dict[str, str]], expected: list[dict[str, str]]
) -> DraftComparison:
    """Match rows by non-empty raw provenance key and surface all divergence."""
    expected_by_raw: dict[str, deque[dict[str, str]]] = defaultdict(deque)
    for row in expected:
        raw = row.get("raw_row_number", "")
        if raw:
            expected_by_raw[raw].append(row)

    extras: list[dict[str, str]] = []
    changed: list[tuple[dict[str, str], dict[str, str], list[str]]] = []
    for current in committed:
        raw = current.get("raw_row_number", "")
        candidates = expected_by_raw.get(raw)
        if not raw or not candidates:
            extras.append(current)
            continue
        projected = candidates.popleft()
        changed_fields = [
            field
            for field in build_research_master.FIELDS
            if current.get(field, "") != projected.get(field, "")
        ]
        if changed_fields:
            changed.append((current, projected, changed_fields))

    missing = [
        row
        for candidates in expected_by_raw.values()
        for row in candidates
    ]
    return DraftComparison(
        extras=sorted(extras, key=raw_sort_key),
        missing=sorted(missing, key=raw_sort_key),
        changed=sorted(changed, key=lambda change: raw_sort_key(change[0])),
    )


def render_report() -> str:
    master_build = build_research_master.build_master()
    committed_master = read_csv(CURRENT_MASTER)
    committed_master_json = json.loads(CURRENT_MASTER_JSON.read_text(encoding="utf-8"))
    committed_exclusions = read_csv(CURRENT_EXCLUSIONS)
    comparison = compare_drafts(committed_master, master_build.items)

    # This is deliberately a cascade from the ledger-derived items, rather than
    # a normal page build from the currently committed master CSV.
    projected_catalogue = build_catalogue_pages.build_catalogue(master_build.items)
    committed_catalogue = json.loads(CURRENT_CATALOGUE.read_text(encoding="utf-8"))
    committed_meta = json.loads(CURRENT_META.read_text(encoding="utf-8"))
    projected_meta = json.loads(projected_catalogue.outputs[build_catalogue_pages.OUT_META])
    projected_json = json.loads(master_build.outputs[build_research_master.OUTPUT_JSON])
    projected_catalogue_rows = json.loads(
        projected_catalogue.outputs[build_catalogue_pages.OUT_MASTER]
    )
    is_reconciled = (
        not comparison.extras
        and not comparison.missing
        and not comparison.changed
        and committed_master_json == projected_json
        and committed_exclusions == master_build.exclusions
        and committed_catalogue == projected_catalogue_rows
        and committed_meta == projected_meta
    )
    summary_note = (
        [
            "All checked master, exclusion, and Everything Pages outputs match the current ledger and approved source overrides.",
            "",
            f"The reviewed build applies {master_build.source_overrides_applied} approved official-source overrides; unresolved research leads remain outside the master in their review inputs.",
        ]
        if is_reconciled
        else [
            "The checked outputs are not yet fully reconciled. Review the differences below before rebuilding so reviewed additions are not lost.",
            "",
            "The normal `python build_catalogue_pages.py --check` evaluates Pages files against the **committed** master CSV and may pass while this cascade differs. This report identifies the upstream master/ledger divergence that must be resolved first.",
        ]
    )
    resolution_section = (
        [
            "## Current verification result",
            "",
            "The reconciliation is complete. For future approved changes, update the ledger, reviewed source overrides, or manual-lead input as appropriate; rebuild the master and Pages outputs; then run all three checks below.",
        ]
        if is_reconciled
        else [
            "## Required resolution before rebuilding",
            "",
            "1. Decide whether every draft-only record is an approved item, a documented manual candidate, or should remain outside the curated master.",
            "2. Record approved changes to matching rows in the ledger or a versioned reviewed-overrides input; do not preserve them solely by editing generated draft CSV/JSON files.",
            "3. Re-run this report until the reconciliation is understood and accepted.",
            "4. Only then run `python build_research_master.py`, then `python build_catalogue_pages.py`, and verify both `--check` commands.",
        ]
    )

    lines = [
        "# Research Master Reconciliation Report",
        "",
        "**Status:** Read-only comparison; no raw CSV, review ledger, master draft, or Pages JSON was changed to produce this report.",
        "",
        "## Purpose",
        "",
        "This report compares the committed `data/research_master_draft.csv` with the in-memory output of `build_research_master.py` using the current `migration_review_ledger.csv`. It also checks the paired master JSON and exclusions outputs, then shows the cascade to the Everything Pages dataset if the ledger projection were used. It is a review aid, not approval to overwrite either generated file.",
        "",
        "## Summary",
        "",
        "| Measure | Committed state | Current ledger projection |",
        "|---|---:|---:|",
        f"| Research-master CSV records | {len(committed_master)} | {len(master_build.items)} |",
        f"| Research-master JSON records | {len(committed_master_json)} | {len(projected_json)} |",
        f"| Research-master exclusion records | {len(committed_exclusions)} | {len(master_build.exclusions)} |",
        f"| Draft-only CSV records without a matching ledger `item` | {len(comparison.extras)} | 0 |",
        f"| Ledger `item` records absent from CSV draft | 0 | {len(comparison.missing)} |",
        f"| Matched CSV records with one or more field differences | {len(comparison.changed)} | 0 |",
        f"| `docs/master.json` / ledger-projected Everything records | {len(committed_catalogue)} | {len(projected_catalogue.items)} |",
        "",
        *summary_note,
        "",
        "## Draft-only CSV records requiring a provenance decision",
        "",
        "Each record below is present in the committed draft CSV and therefore included by the current Everything build, but is not an `item` in the current ledger projection. Retain it only by recording its approval and durable provenance in the ledger or a reviewed overrides input; otherwise it will disappear on a normal master rebuild.",
        "",
        "| Raw row | Title | Type | Notes |",
        "|---:|---|---|---|",
    ]
    for row in comparison.extras:
        lines.append(
            "| "
            f"{markdown_cell(row['raw_row_number'])} | "
            f"{markdown_cell(row['title'])} | "
            f"{markdown_cell(row['item_type'])} | "
            f"{markdown_cell(row['notes'])} |"
        )
    if not comparison.extras:
        lines.append("| — | — | — | — |")

    lines.extend([
        "",
        "## Ledger items absent from the committed draft",
        "",
        "| Raw row | Title | Type |",
        "|---:|---|---|",
    ])
    for row in comparison.missing:
        lines.append(
            f"| {markdown_cell(row['raw_row_number'])} | {markdown_cell(row['title'])} | {markdown_cell(row['item_type'])} |"
        )
    if not comparison.missing:
        lines.append("| — | — |")

    lines.extend([
        "",
        "## Field differences for matching provenance rows",
        "",
        "Each entry is an exact current-draft value followed by the current ledger-derived value. UUIDs are included if they differ, because an identity change requires review.",
        "",
    ])
    if comparison.changed:
        for current, projected, fields in comparison.changed:
            raw = current["raw_row_number"]
            lines.append(
                f"### Raw row {raw} — {markdown_cell(current['title'])}"
            )
            lines.append("")
            for field in fields:
                lines.append(
                    f"- `{field}`: {code(current.get(field, ''))} → {code(projected.get(field, ''))}"
                )
            lines.append("")
    else:
        lines.extend(["No matching-record field differences were found.", ""])

    lines.extend([
        "## Downstream Pages impact",
        "",
        "| `catalogue-meta.json` field | Committed Pages value | Ledger-projected value |",
        "|---|---:|---:|",
    ])
    for field in ("master_items", "migrated_items", "implemented_unreviewed"):
        lines.append(
            f"| `{field}` | {committed_meta.get(field, '—')} | {projected_meta.get(field, '—')} |"
        )

    lines.extend([
        "",
        *resolution_section,
        "",
        "## Reproduce",
        "",
        "```bash",
        "python reconcile_research_master.py --check",
        "python build_research_master.py --check",
        "python build_catalogue_pages.py --check",
        "```",
        "",
        "`reconcile_research_master.py --check` verifies that this report still describes the current inputs. Omitting `--check` refreshes this Markdown report only; it does not change catalogue data.",
        "",
    ])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed report matches current inputs; do not write files",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = render_report()
    if args.check:
        if REPORT.exists() and REPORT.read_text(encoding="utf-8") == report:
            print(f"{REPORT} matches the current ledger/master reconciliation.")
            return 0
        print(f"{REPORT} is stale; run python reconcile_research_master.py to refresh it.")
        return 1

    REPORT.write_text(report, encoding="utf-8")
    print(f"Wrote {REPORT} (read-only reconciliation report).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
