#!/usr/bin/env python3
"""Generate a review-only lecture-series batch from the migration ledger."""

from __future__ import annotations

import csv
import re
from pathlib import Path

SOURCE = Path("migration_review_ledger.csv")
OUTPUT = Path("lecture_series_review.csv")


def proposed_canonical_title(title: str) -> str:
    """Remove only the trailing date + DVD-part label; preserve title wording."""
    return re.sub(r"\s*\([^)]*\)\s*DVD\d+\s*$", "", title).strip()


def link_review_status(raw_url: str, proposed_url: str) -> str:
    if raw_url.startswith("https://veritaspub.com/product/https://"):
        return "quarantined_malformed"
    if raw_url:
        return "proposed_valid"
    return "missing"


def main() -> None:
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        ledger = list(csv.DictReader(handle))

    lectures = [row for row in ledger if row["raw_tempid"].startswith("LS")]
    output_rows = []
    for row in lectures:
        output_rows.append({
            "raw_row_number": row["raw_row_number"],
            "legacy_tempid": row["raw_tempid"],
            "proposed_canonical_title": proposed_canonical_title(row["raw_title"]),
            "raw_title": row["raw_title"],
            "proposed_series": row["proposed_series"],
            "proposed_item_type": "lecture",
            "proposed_year": row["proposed_year"],
            "proposed_month": row["proposed_month"],
            "proposed_format": row["proposed_format"],
            "proposed_format_detail": row["proposed_format_detail"],
            "proposed_owned": row["proposed_owned"],
            "proposed_source_url_veritas": row["proposed_source_url_veritas"],
            "raw_product_link": row["raw_product_link"],
            "link_review_status": link_review_status(
                row["raw_product_link"], row["proposed_source_url_veritas"]
            ),
            "approval": "",
            "review_notes": "",
        })

    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote {OUTPUT} ({len(output_rows)} lecture-part candidates)")


if __name__ == "__main__":
    main()
