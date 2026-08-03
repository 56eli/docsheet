#!/usr/bin/env python3
"""Build or verify the clean research-master draft from the review ledger.

The raw source CSV and ``docs/data.json`` are never modified.  This generator
writes reviewable draft outputs in ``data/`` and retains UUIDv7 values across
reruns by raw source row number.  Use ``--check`` to compare generated content
with the committed outputs without writing any files.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import random
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

LEDGER = Path("migration_review_ledger.csv")
OUTPUT_CSV = Path("data") / "research_master_draft.csv"
OUTPUT_JSON = Path("data") / "research_master_draft.json"
EXCLUSIONS = Path("data") / "research_master_exclusions.csv"
SOURCE_OVERRIDES = Path("data") / "research_master_source_overrides.csv"

FIELDS = [
    "uuid", "catalog_code", "legacy_tempid", "title", "title_source", "item_type",
    "series", "year", "month", "format", "format_detail", "owned",
    "location_physical", "location_digital", "location_streaming",
    "source_url_veritas", "source_url_hay_house", "source_url_nightingale_conant",
    "source_url_audible", "reference_url_1", "reference_url_2", "notes",
    "raw_row_number",
]
EXCLUSION_FIELDS = [
    "raw_row_number", "disposition", "review_reason", "raw_tempid", "raw_title",
    "raw_we_have", "raw_original_source", "raw_product_link",
]
SOURCE_OVERRIDE_FIELDS = {"source_url_veritas", "source_url_audible"}
SOURCE_OVERRIDE_REQUIRED_COLUMNS = {
    "raw_row_number", "target_field", "override_value", "review_status",
}


@dataclass
class MasterBuild:
    """In-memory result shared by normal builds, checks, and reconciliation."""

    items: list[dict[str, str]]
    exclusions: list[dict[str, str]]
    source_overrides_applied: int
    outputs: dict[Path, str]


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
    """Read retained IDs from the committed draft, if it exists."""
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
    urls = [
        value
        for value in (row["raw_format"], row["raw_unnamed_11"], row["raw_other_links"])
        if value
    ]
    return (urls + ["", ""])[:2]


def csv_text(fieldnames: list[str], rows: list[dict[str, str]]) -> str:
    """Render stable UTF-8 CSV text with LF line endings."""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def apply_source_overrides(items: list[dict[str, str]]) -> int:
    """Apply explicit, approved official-source links after ledger migration.

    The migration ledger preserves raw evidence. This narrowly scoped input
    preserves reviewed official source associations added after the original
    ledger pass, without hand-editing generated master files. It may only add
    an empty Veritas or Audible source field to an existing ledger item.
    """
    if not SOURCE_OVERRIDES.exists():
        return 0

    with SOURCE_OVERRIDES.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing_columns = SOURCE_OVERRIDE_REQUIRED_COLUMNS - columns
        if missing_columns:
            raise ValueError(
                f"{SOURCE_OVERRIDES} is missing required columns: "
                f"{', '.join(sorted(missing_columns))}"
            )
        overrides = list(reader)

    items_by_raw = {row["raw_row_number"]: row for row in items}
    seen: set[tuple[str, str]] = set()
    for line_number, override in enumerate(overrides, start=2):
        raw_row = override["raw_row_number"].strip()
        target_field = override["target_field"].strip()
        value = override["override_value"].strip()
        status = override["review_status"].strip()
        key = (raw_row, target_field)

        if not raw_row or raw_row not in items_by_raw:
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} references a non-item raw row: {raw_row!r}"
            )
        if target_field not in SOURCE_OVERRIDE_FIELDS:
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} cannot override {target_field!r}; "
                f"allowed fields: {', '.join(sorted(SOURCE_OVERRIDE_FIELDS))}"
            )
        if status != "approved":
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} must have review_status 'approved'"
            )
        if not value.startswith("https://"):
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} must contain an HTTPS URL"
            )
        if key in seen:
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} duplicates an override for {raw_row}/{target_field}"
            )
        if items_by_raw[raw_row][target_field] and items_by_raw[raw_row][target_field] != value:
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} conflicts with the raw-ledger value for "
                f"{raw_row}/{target_field}; model a separate relationship instead"
            )
        items_by_raw[raw_row][target_field] = value
        seen.add(key)
    return len(overrides)


def build_master() -> MasterBuild:
    """Prepare all draft outputs in memory without changing the working tree."""
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        ledger = list(csv.DictReader(handle))

    retained_uuids = existing_uuids()
    item_rows = [row for row in ledger if row["disposition"] == "item"]
    excluded_rows = [row for row in ledger if row["disposition"] != "item"]

    sequences: dict[tuple[str, str], int] = {}
    items: list[dict[str, str]] = []
    for row in item_rows:
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
        canonical_title = title_for(row)
        retained_uuid = retained_uuids.get(row["raw_row_number"])
        items.append({
            "uuid": retained_uuid if retained_uuid else uuid7(),
            "catalog_code": code,
            "legacy_tempid": row["raw_tempid"],
            "title": canonical_title,
            "title_source": row["raw_title"] if canonical_title != row["raw_title"] else "",
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

    source_overrides_applied = apply_source_overrides(items)
    exclusions = [
        {field: row[field] for field in EXCLUSION_FIELDS}
        for row in excluded_rows
    ]
    outputs = {
        OUTPUT_CSV: csv_text(FIELDS, items),
        OUTPUT_JSON: json.dumps(items, ensure_ascii=False, indent=2) + "\n",
        EXCLUSIONS: csv_text(EXCLUSION_FIELDS, exclusions),
    }
    return MasterBuild(
        items=items,
        exclusions=exclusions,
        source_overrides_applied=source_overrides_applied,
        outputs=outputs,
    )


def write_outputs(outputs: dict[Path, str]) -> None:
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def stale_outputs(outputs: dict[Path, str]) -> list[Path]:
    """Return missing or different outputs without writing them."""
    return [
        path for path, expected in outputs.items()
        if not path.exists() or path.read_text(encoding="utf-8") != expected
    ]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify committed draft outputs match the current ledger; do not write files",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    build = build_master()

    if args.check:
        stale = stale_outputs(build.outputs)
        if stale:
            print("Research-master outputs are stale relative to the current ledger:")
            for path in stale:
                print(f"  - {path}")
            print("Run the reconciliation report before rebuilding so reviewed additions are not lost.")
            return 1
        print(
            "Research-master outputs match the current ledger and approved source overrides "
            f"({len(build.items)} items; {len(build.exclusions)} excluded rows; "
            f"{build.source_overrides_applied} source overrides)."
        )
        return 0

    write_outputs(build.outputs)
    print(f"Wrote {OUTPUT_CSV} and {OUTPUT_JSON} ({len(build.items)} items)")
    print(f"Wrote {EXCLUSIONS} ({len(build.exclusions)} excluded source rows)")
    print(f"Applied {build.source_overrides_applied} approved source overrides")
    return 0


if __name__ == "__main__":
    sys.exit(main())
