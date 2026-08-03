#!/usr/bin/env python3
"""Build or verify the clean research-master draft from the review ledger.

The raw source CSV and ``docs/data.json`` are never modified.  This generator
writes reviewable draft outputs in ``data/`` and retains compact numeric master
IDs across reruns by raw source row number.  Use ``--check`` to compare generated content
with the committed outputs without writing any files.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

LEDGER = Path("migration_review_ledger.csv")
OUTPUT_CSV = Path("data") / "research_master_draft.csv"
OUTPUT_JSON = Path("data") / "research_master_draft.json"
EXCLUSIONS = Path("data") / "research_master_exclusions.csv"
SOURCE_OVERRIDES = Path("data") / "research_master_source_overrides.csv"
MANUAL_CANDIDATES = Path("data") / "manual_master_candidates.csv"
VERITAS_PRODUCTS = Path("data") / "veritas_official_products.csv"

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
MANUAL_CANDIDATE_REQUIRED_COLUMNS = {
    "candidate_key", "candidate_title", "proposed_item_type", "proposed_year",
    "proposed_format", "proposed_format_detail", "proposed_owned", "source_name",
    "source_product_id", "official_product_url", "official_product_title", "evidence_note",
    "review_status", "reviewed_on", "promotion_status", "promotion_notes",
}
# Controlled vocabulary for ``item_type``.
#
# ``item_type`` records WHAT A RECORD IS (its content class). The physical or
# digital carrier belongs in ``format`` instead. The established precedent is
# explicit: DVD lecture recordings are ``item_type='lecture'`` with
# ``format='DVD'`` -- they are not typed ``video``.
#
# ``audio`` and ``video`` are retained only for backward compatibility with
# existing manual-candidate rows. They describe a medium rather than a content
# class, so they must not be used for new classifications; use the content class
# and record the carrier in ``format``.
CONTENT_ITEM_TYPES = {
    "lecture", "book", "discussion", "interview", "transcript", "highlight",
    "dissertation", "article", "other",
}
DEPRECATED_MEDIUM_ITEM_TYPES = {"audio", "video"}
ITEM_TYPES = CONTENT_ITEM_TYPES | DEPRECATED_MEDIUM_ITEM_TYPES
MANUAL_CANDIDATE_ITEM_TYPES = ITEM_TYPES
MANUAL_CANDIDATE_FORMATS = {"", "DVD", "CD", "audio", "book"}
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class MasterBuild:
    """In-memory result shared by normal builds, checks, and reconciliation."""

    items: list[dict[str, str]]
    exclusions: list[dict[str, str]]
    source_overrides_applied: int
    manual_candidates_validated: int
    outputs: dict[Path, str]


COMPACT_ID_MAX = 10_000


def is_compact_id(value: str) -> bool:
    """Return whether a retained master identifier is in the approved compact range."""
    return value.isdigit() and 1 <= int(value) <= COMPACT_ID_MAX


def assign_compact_ids(
    item_rows: list[dict[str, str]],
    retained_ids: dict[str, str],
) -> dict[str, str]:
    """Assign stable human-scale master IDs in the range 1..10000.

    Existing compact IDs are retained by raw source row number. New or migrated
    rows receive the lowest available integer ID, which keeps identifiers short
    for the public spreadsheet while preserving references across rebuilds.
    """
    ids_by_raw: dict[str, str] = {}
    used: set[str] = set()

    for row in item_rows:
        raw_row = row["raw_row_number"]
        retained = retained_ids.get(raw_row, "").strip()
        if is_compact_id(retained) and retained not in used:
            ids_by_raw[raw_row] = retained
            used.add(retained)

    next_id = 1
    for row in item_rows:
        raw_row = row["raw_row_number"]
        if raw_row in ids_by_raw:
            continue
        while str(next_id) in used:
            next_id += 1
        if next_id > COMPACT_ID_MAX:
            raise ValueError(f"Master item count exceeds compact ID range 1..{COMPACT_ID_MAX}")
        assigned = str(next_id)
        ids_by_raw[raw_row] = assigned
        used.add(assigned)
        next_id += 1
    return ids_by_raw


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


def backfill_months_from_official_source(items: list[dict[str, str]]) -> int:
    """Derive a missing lecture month from an approved official product URL.

    ``proposed_month`` in the ledger is derived from the official Veritas
    product slug, which is the publisher's authoritative statement of when a
    lecture was given. Some official links only arrive later through the
    approved source-override input, so the month must be resolved again once
    those overrides have been applied. Existing months are never overwritten.
    """
    import generate_migration_ledger as ledger_tools

    filled = 0
    for item in items:
        if item["month"] or not item["legacy_tempid"]:
            continue
        month = ledger_tools.proposed_month(
            item["legacy_tempid"].strip(), item["source_url_veritas"]
        )
        if month:
            item["month"] = month
            filled += 1
    return filled


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


def validate_manual_candidates() -> int:
    """Validate reviewed manual candidates without promoting them to the master.

    Manual candidates have no raw spreadsheet row, so their durable candidate
    key and official-product evidence are validated separately. Promotion is a
    later explicit action; this function never emits candidate rows into the
    generated master CSV/JSON.
    """
    if not MANUAL_CANDIDATES.exists():
        return 0

    with MANUAL_CANDIDATES.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing_columns = MANUAL_CANDIDATE_REQUIRED_COLUMNS - columns
        if missing_columns:
            raise ValueError(
                f"{MANUAL_CANDIDATES} is missing required columns: "
                f"{', '.join(sorted(missing_columns))}"
            )
        candidates = list(reader)

    with VERITAS_PRODUCTS.open(encoding="utf-8", newline="") as handle:
        veritas_by_id = {
            row["veritas_product_id"]: row
            for row in csv.DictReader(handle)
        }

    seen_keys: set[str] = set()
    for line_number, candidate in enumerate(candidates, start=2):
        key = candidate["candidate_key"].strip()
        item_type = candidate["proposed_item_type"].strip()
        year = candidate["proposed_year"].strip()
        media_format = candidate["proposed_format"].strip()
        source_name = candidate["source_name"].strip()
        product_id = candidate["source_product_id"].strip()

        if not key.startswith("manual-") or key in seen_keys:
            raise ValueError(
                f"{MANUAL_CANDIDATES}:{line_number} needs a unique candidate_key beginning 'manual-'"
            )
        if not candidate["candidate_title"].strip() or item_type not in MANUAL_CANDIDATE_ITEM_TYPES:
            raise ValueError(
                f"{MANUAL_CANDIDATES}:{line_number} needs a title and valid proposed_item_type"
            )
        if year and (len(year) != 4 or not year.isdigit()):
            raise ValueError(f"{MANUAL_CANDIDATES}:{line_number} proposed_year must be blank or YYYY")
        if media_format not in MANUAL_CANDIDATE_FORMATS:
            raise ValueError(
                f"{MANUAL_CANDIDATES}:{line_number} proposed_format is outside the current controlled vocabulary"
            )
        if candidate["proposed_owned"].strip() not in {"", "true", "false"}:
            raise ValueError(
                f"{MANUAL_CANDIDATES}:{line_number} proposed_owned must be blank, true, or false"
            )
        if candidate["review_status"].strip() != "reviewed_candidate":
            raise ValueError(
                f"{MANUAL_CANDIDATES}:{line_number} must have review_status 'reviewed_candidate'"
            )
        if not ISO_DATE.fullmatch(candidate["reviewed_on"].strip()):
            raise ValueError(f"{MANUAL_CANDIDATES}:{line_number} needs an ISO reviewed_on date")
        if candidate["promotion_status"].strip() != "not_promoted":
            raise ValueError(
                f"{MANUAL_CANDIDATES}:{line_number} must remain not_promoted until a separate approval"
            )
        if not candidate["evidence_note"].strip() or not candidate["promotion_notes"].strip():
            raise ValueError(f"{MANUAL_CANDIDATES}:{line_number} needs evidence and promotion notes")
        if source_name != "veritas" or product_id not in veritas_by_id:
            raise ValueError(
                f"{MANUAL_CANDIDATES}:{line_number} needs a known Veritas source product"
            )
        product = veritas_by_id[product_id]
        if candidate["official_product_url"] != product["official_product_url"]:
            raise ValueError(
                f"{MANUAL_CANDIDATES}:{line_number} official_product_url differs from the inventory"
            )
        if candidate["official_product_title"] != product["official_title"]:
            raise ValueError(
                f"{MANUAL_CANDIDATES}:{line_number} official_product_title differs from the inventory"
            )
        seen_keys.add(key)
    return len(candidates)


def build_master() -> MasterBuild:
    """Prepare all draft outputs in memory without changing the working tree."""
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        ledger = list(csv.DictReader(handle))

    retained_uuids = existing_uuids()
    item_rows = [row for row in ledger if row["disposition"] == "item"]
    excluded_rows = [row for row in ledger if row["disposition"] != "item"]
    compact_ids = assign_compact_ids(item_rows, retained_uuids)

    sequences: dict[tuple[str, str], int] = {}
    items: list[dict[str, str]] = []
    for row in item_rows:
        item_type = row["proposed_item_type"]
        year = row["proposed_year"]
        # The ledger is a hand-maintained review input, so an unknown or
        # misspelled type must fail loudly instead of silently producing a
        # stray catalogue-code prefix.
        if item_type and item_type not in ITEM_TYPES:
            raise ValueError(
                f"{LEDGER} raw row {row['raw_row_number']} uses unsupported "
                f"proposed_item_type {item_type!r}; allowed values are "
                f"{', '.join(sorted(ITEM_TYPES))}"
            )
        code = ""
        # The approved rule is ID-only until type and year are verified.
        # This conservative draft assigns readable codes only where both are proposed.
        if item_type and year:
            key = (item_type.upper(), year)
            sequences[key] = sequences.get(key, 0) + 1
            code = f"{key[0]}-{year}-{sequences[key]:03d}"
        ref_1, ref_2 = reference_urls(row)
        canonical_title = title_for(row)
        items.append({
            "uuid": compact_ids[row["raw_row_number"]],
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
    backfill_months_from_official_source(items)
    manual_candidates_validated = validate_manual_candidates()
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
        manual_candidates_validated=manual_candidates_validated,
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
            f"{build.source_overrides_applied} source overrides; "
            f"{build.manual_candidates_validated} manual candidates validated)."
        )
        return 0

    write_outputs(build.outputs)
    print(f"Wrote {OUTPUT_CSV} and {OUTPUT_JSON} ({len(build.items)} items)")
    print(f"Wrote {EXCLUSIONS} ({len(build.exclusions)} excluded source rows)")
    print(f"Applied {build.source_overrides_applied} approved source overrides")
    print(f"Validated {build.manual_candidates_validated} reviewed manual candidates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
