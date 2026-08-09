#!/usr/bin/env python3
"""Synchronize derived mirror columns in the Veritas official-product inventory.

Why this exists
---------------
``data/veritas_official_products.csv`` mixes two kinds of columns:

* **Reviewed columns** — hand-maintained owner decisions:
  ``mapping_status``, ``review_notes`` (and, for non-primary statuses, the
  ``matched_master_uuids`` association itself).
* **Derived mirror columns** — pure functions of the curated master:
  ``normalized_title_match_count`` (``=`` number of matched IDs),
  ``matched_master_titles`` (``" | "``-joined current master titles, in the
  same order as the IDs), and — for rows whose status is
  ``matched_by_primary_source`` — ``matched_master_uuids`` itself, because the
  authoritative primary link is the master's own ``source_url_veritas``
  (see ``derive_primary_relationships`` in ``build_catalogue_pages.py``).

Hand-editing derived mirrors has corrupted them twice (a ``;`` vs `` | ``
separator mix-up and the stale 50491 title-match). This tool recomputes the
derived columns from ``data/research_master_draft.csv`` and rewrites exactly
those cells; reviewed columns are never touched.

Guards (always fail closed, never write on violation)
-----------------------------------------------------
1. A ``matched_by_primary_source`` row whose URL sits on **no** master is a
   modelling error, not drift to fix silently.
2. Any other row whose reviewed cell **contradicts URL evidence** (a master
   carries the product URL yet the cell names different IDs) is a
   contradiction that needs an owner ruling — the tool reports it and exits
   non-zero without writing. (URL evidence is itself a reviewed master field,
   so a contradiction means two reviewed inputs disagree.)
3. Unknown master IDs in a cell fail like the existing inventory validator.

Usage
-----
``python sync_inventory_mirrors.py`` — recompute and rewrite mirror cells.
``python sync_inventory_mirrors.py --check`` — report drift/violations only;
exit 0 when the committed inventory already mirrors the master.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import read_csv, render_csv

MASTER = Path("data") / "research_master_draft.csv"
VERITAS_PRODUCTS = Path("data") / "veritas_official_products.csv"

PRIMARY_STATUS = "matched_by_primary_source"
MIRROR_FIELDS = ("normalized_title_match_count", "matched_master_uuids", "matched_master_titles")


def parse_uuid_cell(cell: str) -> list[str]:
    """Split a ``"; "``-joined matched-master-ID cell into clean IDs."""
    return [part.strip() for part in cell.split(";") if part.strip()]


def compute_targets(
    master_rows: list[dict[str, str]],
    products: list[dict[str, str]],
) -> tuple[dict[str, tuple[str, str, str]], list[str], list[str]]:
    """Return (targets, violations, contradictions) for every inventory row.

    ``targets`` maps product ID to the correct (count, uuids, titles) mirror
    triple. ``violations`` are hard errors (unknown IDs, primary status with no
    URL on any master). ``contradictions`` are URL-evidence conflicts against
    reviewed non-primary cells, which need an owner ruling.
    """
    title_by_uuid: dict[str, str] = {}
    uuids_by_url: dict[str, list[str]] = {}
    for row in master_rows:
        title_by_uuid[row["uuid"]] = row["title"]
        url = row.get("source_url_veritas", "").strip()
        if url:
            uuids_by_url.setdefault(url, []).append(row["uuid"])

    targets: dict[str, tuple[str, str, str]] = {}
    violations: list[str] = []
    contradictions: list[str] = []
    for product in products:
        pid = product["veritas_product_id"].strip()
        status = product["mapping_status"].strip()
        cell = parse_uuid_cell(product["matched_master_uuids"])
        derived = uuids_by_url.get(product["official_product_url"].strip(), [])
        if status == PRIMARY_STATUS:
            if not derived:
                violations.append(
                    f"product {pid}: status {PRIMARY_STATUS!r} but no master carries its URL"
                )
            target = derived
        else:
            target = cell
            if derived and derived != cell:
                contradictions.append(
                    f"product {pid}: reviewed cell {cell} contradicts URL evidence {derived} "
                    f"(status {status!r}); needs an owner ruling"
                )
        unknown = [item for item in target if item not in title_by_uuid]
        if unknown:
            violations.append(f"product {pid}: unknown matched master ID(s) {unknown}")
        titles = " | ".join(title_by_uuid.get(item, "") for item in target)
        targets[pid] = (str(len(target)), "; ".join(target), titles)
    return targets, violations, contradictions


def plan_changes(
    products: list[dict[str, str]],
    targets: dict[str, tuple[str, str, str]],
) -> list[str]:
    """Human-readable list of mirror cells that differ from the committed file."""
    changes = []
    for product in products:
        pid = product["veritas_product_id"].strip()
        count, uuids, titles = targets[pid]
        for field, new in zip(MIRROR_FIELDS, (count, uuids, titles)):
            if product[field] != new:
                changes.append(f"product {pid}: {field} {product[field]!r} -> {new!r}")
    return changes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report only; never write")
    args = parser.parse_args(argv)

    if not MASTER.exists():
        print(f"Run build_research_master.py first; {MASTER} is missing.", file=sys.stderr)
        return 2
    master_rows = read_csv(MASTER)
    products = read_csv(VERITAS_PRODUCTS)

    targets, violations, contradictions = compute_targets(master_rows, products)
    changes = plan_changes(products, targets)

    for line in violations:
        print(f"VIOLATION: {line}", file=sys.stderr)
    for line in contradictions:
        print(f"CONTRADICTION: {line}", file=sys.stderr)
    if violations or contradictions:
        print("Mirror sync refused: resolve the above before rewriting mirrors.", file=sys.stderr)
        return 1
    if not changes:
        print("Inventory mirrors already match the curated master.")
        return 0
    if args.check:
        print("Inventory mirror drift detected:", file=sys.stderr)
        for line in changes:
            print(f"  {line}", file=sys.stderr)
        return 1

    for product in products:
        pid = product["veritas_product_id"].strip()
        count, uuids, titles = targets[pid]
        product["normalized_title_match_count"] = count
        product["matched_master_uuids"] = uuids
        product["matched_master_titles"] = titles
    fieldnames = list(products[0].keys())
    VERITAS_PRODUCTS.write_text(render_csv(fieldnames, products), encoding="utf-8")
    print(f"Wrote {VERITAS_PRODUCTS}: {len(changes)} mirror cell(s) re-derived.")
    for line in changes:
        print(f"  {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
