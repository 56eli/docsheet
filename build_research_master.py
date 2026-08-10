#!/usr/bin/env python3
"""Build or verify the clean research-master draft from the review ledger.

The raw source CSV and ``docs/data.json`` are never modified. This generator
writes reviewable draft outputs in ``data/`` and retains compact numeric master
IDs across reruns by raw source row number. Use ``--check`` to compare generated content
with the committed outputs without writing any files.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from _common import ISO_DATE, json_text, read_csv, render_csv
from pipeline.enrichments import (
    apply_edition_notes,
    apply_filename_proposal,
    apply_notes_overrides,
    apply_official_title_cleanup,
    apply_series_approvals,
    apply_source_overrides,
    apply_veritas_streaming_urls,
    apply_work_families,
    apply_year_overrides,
    apply_year_source_provenance,
    backfill_months_from_official_source,
    infer_format_from_official_source,
    migrate_notes_to_research,
)
from pipeline.helpers import (
    index_csv,
    is_compact_id,  # noqa: F401
    month_from_title,
    notes_for,
    require_columns,
    title_for,
)
from pipeline.validators import (
    validate_edition_candidates,
    validate_filename_proposal_mirrors,
    validate_manual_candidates,
    validate_master_items_integrity,
)

LEDGER = Path("migration_review_ledger.csv")
OUTPUT_CSV = Path("data") / "research_master_draft.csv"
OUTPUT_JSON = Path("data") / "research_master_draft.json"
EXCLUSIONS = Path("data") / "research_master_exclusions.csv"
SOURCE_OVERRIDES = Path("data") / "research_master_source_overrides.csv"
MANUAL_CANDIDATES = Path("data") / "manual_master_candidates.csv"
VERITAS_PRODUCTS = Path("data") / "veritas_official_products.csv"
AUDIBLE_PRODUCTS = Path("data") / "audible_official_products.csv"
HAYHOUSE_PRODUCTS = Path("data") / "hayhouse_official_products.csv"
PROMOTIONS = Path("data") / "manual_candidate_promotions.csv"
SERIES_MAPPING = Path("data") / "series_category_mapping.csv"
WORK_FAMILIES = Path("data") / "work_families.csv"
EDITION_CANDIDATES = Path("data") / "edition_candidates.csv"
EDITION_PROMOTIONS = Path("data") / "edition_promotions.csv"
VERITAS_STREAMING = Path("data") / "veritas_streaming_urls.csv"
FILENAME_PROPOSAL = Path("data/filename_proposal_YYYYMM.csv")
YEAR_OVERRIDES = Path("data/master_year_overrides.csv")
NOTES_OVERRIDES = Path("data/master_notes_overrides.csv")

FIELDS = [
    "uuid", "work_id", "catalog_code", "legacy_tempid", "title", "proposed_filename", "legacy_title", "item_type",
    "series", "year", "month", "year_source", "format", "format_detail", "edition_note", "owned",
    "source_url_veritas", "source_url_hay_house", "source_url_nightingale_conant",
    "source_url_audible", "source_url_amazon", "reference_url_1", "notes", "research",
    "raw_row_number", "candidate_key",
]
EXCLUSION_FIELDS = [
    "raw_row_number", "disposition", "review_reason", "raw_tempid", "raw_title",
    "raw_we_have", "raw_original_source", "raw_product_link",
]

CODE_ITEM_TYPES = {"lecture", "discussion"}
CONTENT_ITEM_TYPES = {"lecture", "discussion", "book", "highlight", "other"}
MANUAL_CANDIDATE_FORMATS = {"book", "paperback", "audiobook", "DVD", "CD", "streaming", "highlight", "compilation"}
EDITION_FORMATS = {"audiobook", "book", "paperback", "hardcover", "ebook", "CD", "DVD", "streaming"}
EDITION_ROLES = {"audiobook", "paperback", "hardcover", "ebook", "cd_set", "dvd_set", "streaming_edition"}
EDITION_CANDIDATE_STATUSES = {"proposed", "reviewed_candidate", "rejected"}

SOURCE_OVERRIDE_FIELDS = {"source_url_veritas", "source_url_audible"}
SOURCE_OVERRIDE_REQUIRED_COLUMNS = {
    "raw_row_number", "target_field", "override_value", "review_status",
    "reviewed_on", "evidence_note",
}
MANUAL_CANDIDATE_REQUIRED_COLUMNS = {
    "candidate_key", "candidate_title", "proposed_item_type", "proposed_year",
    "proposed_format", "proposed_owned", "source_name", "source_product_id",
    "official_product_url", "official_product_title", "evidence_note",
    "review_status", "reviewed_on", "promotion_status", "promotion_notes",
}
EDITION_CANDIDATE_REQUIRED_COLUMNS = {
    "candidate_key", "work_id", "edition_role", "matched_master_uuid",
    "candidate_title", "proposed_format", "proposed_format_detail", "proposed_year",
    "proposed_owned", "source_name", "source_product_id", "official_product_url",
    "official_product_title", "evidence_note", "review_status", "reviewed_on",
    "promotion_status", "promotion_notes",
}
EDITION_PROMOTION_REQUIRED_COLUMNS = {
    "candidate_key", "master_uuid", "work_id", "edition_role", "item_type",
    "format", "series", "approval_status", "approved_on", "approval_reason",
}
EDITION_SOURCE_URL_COLUMNS = {
    "veritas": "source_url_veritas",
    "audible": "source_url_audible",
    "hayhouse": "source_url_hay_house",
}
WORK_FAMILY_REQUIRED_COLUMNS = {
    "work_id", "member_master_uuid", "canonical_work_title", "evidence_note",
    "review_status", "reviewed_on",
}
WORK_FAMILY_STATUSES = {"approved", "proposed", "rejected"}
SERIES_MAPPING_REQUIRED_COLUMNS = {
    "veritas_product_id", "official_title", "matched_master_uuids",
    "mapped_series", "review_status",
}


@dataclass
class MasterBuild:
    items: list[dict[str, str]]
    exclusions: list[dict[str, str]]
    source_overrides_applied: int
    manual_candidates_validated: int
    outputs: dict[Path, str]


def assign_compact_ids(
    item_rows: list[dict[str, str]], retained_uuids: dict[str, str]
) -> dict[str, str]:
    """Assign stable numeric master IDs to ledger item rows."""
    mapping: dict[str, str] = {}
    used_numbers: set[int] = set()

    for row in item_rows:
        raw_num = row["raw_row_number"]
        retained = retained_uuids.get(raw_num)
        if retained and retained.isdigit():
            num = int(retained)
            mapping[raw_num] = retained
            used_numbers.add(num)

    next_num = 1
    for row in item_rows:
        raw_num = row["raw_row_number"]
        if raw_num in mapping:
            continue
        while next_num in used_numbers:
            next_num += 1
        mapping[raw_num] = str(next_num)
        used_numbers.add(next_num)

    return mapping


def reference_url(row: dict[str, str]) -> str:
    """Choose the best external reference URL from raw evidence."""
    v_url = row.get("proposed_source_url_veritas", "").strip()
    if v_url:
        return ""
    return row.get("raw_product_link", "").strip()


def csv_text(fieldnames: list[str], rows: list[dict[str, str]]) -> str:
    return render_csv(fieldnames, rows)


def veritas_products_by_id() -> dict[str, dict[str, str]]:
    if not VERITAS_PRODUCTS.exists():
        return {}
    return index_csv(VERITAS_PRODUCTS, "veritas_product_id")


def veritas_products_by_url() -> dict[str, dict[str, str]]:
    if not VERITAS_PRODUCTS.exists():
        return {}
    return index_csv(VERITAS_PRODUCTS, "official_product_url")


def existing_uuids() -> dict[str, str]:
    if not OUTPUT_CSV.exists():
        return {}
    retained: dict[str, str] = {}
    for row in read_csv(OUTPUT_CSV):
        raw_num = row.get("raw_row_number", "").strip()
        uuid = row.get("uuid", "").strip()
        if raw_num and uuid:
            retained[raw_num] = uuid
    return retained


def load_promotions() -> list[dict[str, str]]:
    if not PROMOTIONS.exists():
        return []
    candidates = index_csv(MANUAL_CANDIDATES, "candidate_key")
    rows = read_csv(PROMOTIONS)
    promoted = []
    seen_ids: set[str] = set()
    for line, row in enumerate(rows, 2):
        key, uuid = row["candidate_key"].strip(), row["master_uuid"].strip()
        candidate = candidates.get(key)
        if not candidate or not uuid.isdigit() or uuid in seen_ids:
            raise ValueError(f"{PROMOTIONS}:{line} needs a unique numeric master_uuid and known candidate_key")
        item_type = row["item_type"].strip() or candidate["proposed_item_type"].strip()
        if item_type not in CONTENT_ITEM_TYPES:
            raise ValueError(f"{PROMOTIONS}:{line} needs a non-deprecated content item_type")
        promoted.append({**candidate, "uuid": uuid, "item_type": item_type, "series": row["series"].strip()})
        seen_ids.add(uuid)
    return promoted


def load_edition_promotions(existing_ids: set[str]) -> list[tuple[dict[str, str], str]]:
    if not EDITION_PROMOTIONS.exists():
        return []
    require_columns(EDITION_PROMOTIONS, EDITION_PROMOTION_REQUIRED_COLUMNS)
    candidates = index_csv(EDITION_CANDIDATES, "candidate_key")
    rows = read_csv(EDITION_PROMOTIONS)

    minted: list[tuple[dict[str, str], str]] = []
    seen_keys: set[str] = set()
    seen_ids: set[str] = set()
    for line, row in enumerate(rows, 2):
        key = row["candidate_key"].strip()
        candidate = candidates.get(key)
        if not candidate or key in seen_keys:
            raise ValueError(
                f"{EDITION_PROMOTIONS}:{line} needs a known, unique candidate_key"
            )
        if candidate["review_status"].strip() != "reviewed_candidate":
            raise ValueError(
                f"{EDITION_PROMOTIONS}:{line} candidate {key} is still {candidate['review_status']!r}; "
                "review it before promoting"
            )
        approval = row["approval_status"].strip()
        if approval == "rejected":
            seen_keys.add(key)
            continue
        if approval != "approved":
            raise ValueError(
                f"{EDITION_PROMOTIONS}:{line} approval_status must be 'approved' or 'rejected'"
            )
        if not ISO_DATE.fullmatch(row["approved_on"].strip()) or not row["approval_reason"].strip():
            raise ValueError(
                f"{EDITION_PROMOTIONS}:{line} approved rows need an ISO approved_on and a reason"
            )
        work_id = row["work_id"].strip()
        role = row["edition_role"].strip()
        item_type = row["item_type"].strip()
        media_format = row["format"].strip()
        uuid = row["master_uuid"].strip()
        if (
            not work_id or work_id != candidate["work_id"].strip()
            or role != candidate["edition_role"].strip()
        ):
            raise ValueError(
                f"{EDITION_PROMOTIONS}:{line} work_id/edition_role must match the candidate"
            )
        if item_type not in CONTENT_ITEM_TYPES:
            raise ValueError(f"{EDITION_PROMOTIONS}:{line} needs a non-deprecated content item_type")
        if media_format not in EDITION_FORMATS:
            raise ValueError(f"{EDITION_PROMOTIONS}:{line} format is outside the edition vocabulary")
        if not uuid.isdigit() or uuid in seen_ids or uuid in existing_ids:
            raise ValueError(
                f"{EDITION_PROMOTIONS}:{line} needs a unique, unused numeric master_uuid"
            )
        source_column = EDITION_SOURCE_URL_COLUMNS[candidate["source_name"].strip()]
        row_dict = {
            "uuid": uuid, "work_id": work_id, "catalog_code": "", "legacy_tempid": "",
            "title": candidate["candidate_title"], "legacy_title": candidate["candidate_title"],
            "item_type": item_type, "series": row["series"].strip(),
            "year": candidate["proposed_year"].strip(), "month": "",
            "format": media_format, "format_detail": candidate["proposed_format_detail"].strip(),
            "edition_note": "",
            "owned": candidate["proposed_owned"].strip().lower(),
            "source_url_veritas": "", "source_url_hay_house": "",
            "source_url_nightingale_conant": "", "source_url_audible": "", "source_url_amazon": "",
            "reference_url_1": "",
            "notes": f"Promoted edition {role} of work {work_id} from candidate "
                     f"{key}: {candidate['evidence_note']}",
            "raw_row_number": "",
            "candidate_key": f"candidate:{key}",
        }
        row_dict[source_column] = candidate["official_product_url"]
        minted.append((row_dict, candidate["matched_master_uuid"].strip()))
        seen_keys.add(key)
        seen_ids.add(uuid)
    return minted


def build_master() -> MasterBuild:
    """Prepare all draft outputs in memory without changing the working tree."""
    ledger = read_csv(LEDGER)

    for row in ledger:
        if row["proposed_owned"].strip() not in {"", "true", "false"}:
            raise ValueError(
                f"{LEDGER} raw row {row['raw_row_number']} proposed_owned must "
                f"be blank, true, or false; got {row['proposed_owned']!r}"
            )

    retained_uuids = existing_uuids()
    item_rows = [row for row in ledger if row["disposition"] == "item"]
    excluded_rows = [row for row in ledger if row["disposition"] != "item"]
    compact_ids = assign_compact_ids(item_rows, retained_uuids)

    sequences: dict[tuple[str, str], int] = {}
    items: list[dict[str, str]] = []
    for row in item_rows:
        item_type = row["proposed_item_type"]
        year = row["proposed_year"]
        if item_type and item_type not in CONTENT_ITEM_TYPES:
            raise ValueError(
                f"{LEDGER} raw row {row['raw_row_number']} uses unsupported "
                f"proposed_item_type {item_type!r}; allowed values are "
                f"{', '.join(sorted(CONTENT_ITEM_TYPES))}"
            )
        code = ""
        if item_type in CODE_ITEM_TYPES and year:
            key = (item_type.upper(), year)
            sequences[key] = sequences.get(key, 0) + 1
            code = f"{key[0]}-{year}-{sequences[key]:03d}"
        ref_1 = reference_url(row)
        canonical_title = title_for(row)
        items.append({
            "uuid": compact_ids[row["raw_row_number"]],
            "work_id": "",
            "catalog_code": code,
            "legacy_tempid": row["raw_tempid"],
            "title": canonical_title,
            "legacy_title": row["raw_title"],
            "item_type": item_type,
            "series": row["proposed_series"],
            "year": year,
            "month": row["proposed_month"],
            "format": row["proposed_format"],
            "format_detail": row["proposed_format_detail"],
            "edition_note": "",
            "owned": row["proposed_owned"].strip().lower(),
            "source_url_veritas": row["proposed_source_url_veritas"],
            "source_url_hay_house": "",
            "source_url_nightingale_conant": "",
            "source_url_audible": "",
            "source_url_amazon": "",
            "reference_url_1": ref_1,
            "notes": notes_for(row),
            "raw_row_number": row["raw_row_number"],
            "candidate_key": "",
        })

    existing_ids = {item["uuid"] for item in items}
    for candidate in load_promotions():
        if candidate["uuid"] in existing_ids:
            raise ValueError(f"{PROMOTIONS} reuses existing master UUID {candidate['uuid']}")
        year = candidate["proposed_year"]
        item_type = candidate["item_type"]
        code = ""
        if year and item_type in CODE_ITEM_TYPES:
            key = (item_type.upper(), year)
            sequences[key] = sequences.get(key, 0) + 1
            code = f"{key[0]}-{year}-{sequences[key]:03d}"
        veritas_url = ""
        hay_url = ""
        audible_url = ""
        amazon_url = ""
        ref1 = ""
        source_name = candidate.get("source_name", "").strip()
        official_url = candidate.get("official_product_url", "").strip()
        if source_name == "veritas":
            veritas_url = official_url
        elif source_name in ("audible", "hayhouse") or official_url.startswith(("https://www.audible.com/", "https://www.hayhouse.com/", "https://www.amazon.com/")):
            pass
        else:
            ref1 = official_url
        items.append({
            "uuid": candidate["uuid"], "work_id": "", "catalog_code": code, "legacy_tempid": "",
            "title": candidate["candidate_title"], "legacy_title": candidate["candidate_title"],
            "item_type": item_type, "series": candidate["series"],
            "year": year, "month": month_from_title(candidate["candidate_title"], year),
            "format": candidate["proposed_format"],
            "format_detail": candidate["proposed_format_detail"], "edition_note": "", "owned": candidate["proposed_owned"].strip().lower(),
            "source_url_veritas": veritas_url, "source_url_hay_house": hay_url,
            "source_url_nightingale_conant": "", "source_url_audible": audible_url, "source_url_amazon": amazon_url,
            "reference_url_1": ref1,
            "notes": f"Promoted from official candidate {candidate['candidate_key']}: {candidate['evidence_note']}",
            "raw_row_number": "",
            "candidate_key": f"candidate:{candidate['candidate_key']}",
        })
        existing_ids.add(candidate["uuid"])
    edition_rows = load_edition_promotions(existing_ids)
    for row_dict, matched_uuid in edition_rows:
        items.append(row_dict)

    source_overrides_applied = apply_source_overrides(items)
    apply_veritas_streaming_urls(items)
    apply_filename_proposal(items)

    by_uuid = {item["uuid"]: item for item in items}
    for row_dict, matched_uuid in edition_rows:
        if row_dict["source_url_audible"] and matched_uuid in by_uuid:
            master_row = by_uuid[matched_uuid]
            if master_row["source_url_audible"] == row_dict["source_url_audible"]:
                master_row["source_url_audible"] = ""
    backfill_months_from_official_source(items)

    if VERITAS_PRODUCTS.exists():
        veritas_by_id = index_csv(VERITAS_PRODUCTS, "veritas_product_id")
        veritas_by_url = index_csv(VERITAS_PRODUCTS, "official_product_url")
        inferred = 0
        for item in items:
            fmt = infer_format_from_official_source(item, veritas_by_id, veritas_by_url)
            if fmt:
                item["format"] = fmt
                inferred += 1
        if inferred:
            print(f"[format] Inferred {inferred} formats from official Veritas inventory")
        title_cleanups = apply_official_title_cleanup(items, read_csv(VERITAS_PRODUCTS))
        if title_cleanups:
            print(f"[title] Cleaned {title_cleanups} lecture titles against official Veritas listings")

    apply_series_approvals(items)
    apply_work_families(items)

    apply_year_source_provenance(items, ledger)

    apply_year_overrides(items)
    apply_notes_overrides(items)
    apply_edition_notes(items)

    # Move provenance/research notes out of the notes column into a dedicated
    # research column. Only the FRAN GRACE owner marker stays in notes.
    migrate_notes_to_research(items)

    for it in items:
        it.setdefault("year_source", "")
        it.setdefault("source_url_amazon", "")
        it.setdefault("research", "")
        it.setdefault("edition_note", "")

    validate_filename_proposal_mirrors(items)
    validate_master_items_integrity(items)
    validate_edition_candidates(items)
    manual_candidates_validated = validate_manual_candidates()
    exclusions = [
        {field: row[field] for field in EXCLUSION_FIELDS}
        for row in excluded_rows
    ]
    outputs = {
        OUTPUT_CSV: csv_text(FIELDS, items),
        OUTPUT_JSON: json_text(items),
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
