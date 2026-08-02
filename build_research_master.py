#!/usr/bin/env python3
"""Build the clean research-master draft from the approved migration ledger.

This program never modifies the raw source CSV or docs/data.json. It produces
reviewable draft outputs in data/ and preserves excluded raw rows separately.
UUIDv7 values are retained across reruns by raw source row number.
"""

from __future__ import annotations

import csv
import json
import random
import time
import uuid
from pathlib import Path

LEDGER = Path("migration_review_ledger.csv")
OUTPUT_CSV = Path("data") / "research_master_draft.csv"
OUTPUT_JSON = Path("data") / "research_master_draft.json"
EXCLUSIONS = Path("data") / "research_master_exclusions.csv"

FIELDS = [
    "uuid", "catalog_code", "legacy_tempid", "title", "title_source", "item_type",
    "series", "year", "month", "format", "format_detail", "owned",
    "location_physical", "location_digital", "location_streaming",
    "source_url_veritas", "source_url_hay_house", "source_url_nightingale_conant",
    "source_url_audible", "reference_url_1", "reference_url_2", "notes",
    "raw_row_number",
]


def uuid7() -> str:
    """Create an RFC 9562 UUIDv7 using the current Unix millisecond timestamp."""
    timestamp_ms = int(time.time() * 1000)
    value = (timestamp_ms & ((1 << 48) - 1)) << 80
    value |= 0x7 << 76
    value |= random.getrandbits(12) << 64
    value |= 0b10 << 62  # RFC 4122 variant
    value |= random.getrandbits(62)
    return str(uuid.UUID(int=value))


def existing_uuids() -> dict[str, str]:
    if not OUTPUT_CSV.exists():
        return {}
    with OUTPUT_CSV.open(encoding="utf-8", newline="") as handle:
        return {
            row["raw_row_number"]: row["uuid"]
            for row in csv.DictReader(handle)
            if row.get("raw_row_number") and row.get("uuid")
        }


def title_for(row: dict[str, str]) -> str:
    # The lecture-review batch proposed this limited canonicalization only.
    if row["raw_tempid"].startswith("LS"):
        import re
        return re.sub(r"\s*\([^)]*\)\s*DVD\d+\s*$", "", row["proposed_title"]).strip()
    return row["proposed_title"]


def notes_for(row: dict[str, str]) -> str:
    notes = []
    if row["raw_original_source"] and row["raw_original_source"] != "veritas":
        notes.append(f"Raw source note: {row['raw_original_source']}")
    if row["raw_unnamed_5"]:
        notes.append(row["raw_unnamed_5"])
    return " | ".join(notes)


def reference_urls(row: dict[str, str]) -> tuple[str, str]:
    urls = [value for value in (row["raw_format"], row["raw_unnamed_11"], row["raw_other_links"]) if value]
    return (urls + ["", ""])[:2]


def main() -> None:
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        ledger = list(csv.DictReader(handle))

    retained_uuids = existing_uuids()
    items = [row for row in ledger if row["disposition"] == "item"]
    excluded = [row for row in ledger if row["disposition"] != "item"]

    sequences: dict[tuple[str, str], int] = {}
    output_rows = []
    for row in items:
        item_type = row["proposed_item_type"]
        year = row["proposed_year"]
        code = ""
        # The approved rule is UUID-only until type and year are verified.
        # This conservative draft assigns readable codes only where both are proposed.
        if item_type and year:
            key = (item_type.upper(), year)
            sequences[key] = sequences.get(key, 0) + 1
            code = f"{key[0]}-{year}-{sequences[key]:03d}"
        ref_1, ref_2 = reference_urls(row)
        output_rows.append({
            "uuid": retained_uuids.get(row["raw_row_number"], uuid7()),
            "catalog_code": code,
            "legacy_tempid": row["raw_tempid"],
            "title": title_for(row),
            "title_source": row["raw_title"] if title_for(row) != row["raw_title"] else "",
            "item_type": item_type,
            "series": row["proposed_series"],
            "year": year,
            "month": row["proposed_month"],
            "format": row["proposed_format"],
            "format_detail": row["proposed_format_detail"],
            "owned": row["proposed_owned"],
            "location_physical": "",
            "location_digital": "",
            "location_streaming": "",
            "source_url_veritas": row["proposed_source_url_veritas"],
            "source_url_hay_house": "",
            "source_url_nightingale_conant": "",
            "source_url_audible": "",
            "reference_url_1": ref_1,
            "reference_url_2": ref_2,
            "notes": notes_for(row),
            "raw_row_number": row["raw_row_number"],
        })

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    OUTPUT_JSON.write_text(json.dumps(output_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    exclusion_fields = [
        "raw_row_number", "disposition", "review_reason", "raw_tempid", "raw_title",
        "raw_we_have", "raw_original_source", "raw_product_link",
    ]
    with EXCLUSIONS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=exclusion_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row[field] for field in exclusion_fields} for row in excluded)

    print(f"Wrote {OUTPUT_CSV} and {OUTPUT_JSON} ({len(output_rows)} items)")
    print(f"Wrote {EXCLUSIONS} ({len(excluded)} excluded source rows)")


if __name__ == "__main__":
    main()
