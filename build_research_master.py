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
AUDIBLE_PRODUCTS = Path("data") / "audible_official_products.csv"
HAYHOUSE_PRODUCTS = Path("data") / "hayhouse_official_products.csv"
PROMOTIONS = Path("data") / "manual_candidate_promotions.csv"
SERIES_MAPPING = Path("data") / "series_category_mapping.csv"
WORK_FAMILIES = Path("data") / "work_families.csv"
EDITION_CANDIDATES = Path("data") / "edition_candidates.csv"
EDITION_PROMOTIONS = Path("data") / "edition_promotions.csv"

FIELDS = [
    "uuid", "work_id", "catalog_code", "legacy_tempid", "title", "legacy_title", "title_source", "item_type",
    "series", "year", "month", "format", "format_detail", "owned",
    "location_physical", "location_digital", "location_streaming",
    "source_url_veritas", "source_url_hay_house", "source_url_nightingale_conant",
    "source_url_audible", "reference_url_1", "reference_url_2", "notes",
    "raw_row_number", "candidate_key",
]
EXCLUSION_FIELDS = [
    "raw_row_number", "disposition", "review_reason", "raw_tempid", "raw_title",
    "raw_we_have", "raw_original_source", "raw_product_link",
]
SOURCE_OVERRIDE_FIELDS = {
    "source_url_veritas",
    "source_url_hay_house",
    "source_url_audible",
    "source_url_nightingale_conant",
}
SOURCE_OVERRIDE_REQUIRED_COLUMNS = {
    "raw_row_number", "target_field", "override_value", "review_status",
}
MANUAL_CANDIDATE_REQUIRED_COLUMNS = {
    "candidate_key", "candidate_title", "proposed_item_type", "proposed_year",
    "proposed_format", "proposed_format_detail", "proposed_owned", "source_name",
    "source_product_id", "official_product_url", "official_product_title", "evidence_note",
    "review_status", "reviewed_on", "promotion_status", "promotion_notes",
}
SERIES_MAPPING_REQUIRED_COLUMNS = {
    "veritas_product_id", "matched_master_uuids", "official_categories",
    "dominant_category", "mapped_series", "review_status",
}
WORK_FAMILY_REQUIRED_COLUMNS = {
    "work_id", "member_master_uuid", "canonical_work_title",
    "evidence_note", "review_status", "reviewed_on",
}
WORK_FAMILY_STATUSES = {"approved", "proposed", "rejected"}
EDITION_CANDIDATE_REQUIRED_COLUMNS = {
    "candidate_key", "work_id", "edition_role", "matched_master_uuid",
    "candidate_title", "proposed_item_type", "proposed_year", "proposed_format",
    "proposed_format_detail", "proposed_owned", "source_name",
    "source_product_id", "official_product_url", "official_product_title",
    "evidence_note", "review_status", "reviewed_on", "promotion_status",
    "promotion_notes",
}
EDITION_PROMOTION_REQUIRED_COLUMNS = {
    "candidate_key", "master_uuid", "work_id", "edition_role", "item_type", "format",
    "series", "approval_status", "approved_on", "approval_reason",
}
EDITION_ROLES = {"book", "audio", "video", "streaming"}
EDITION_FORMATS = {"DVD", "CD", "audio", "book", "streaming"}
EDITION_SOURCES = {"veritas", "audible", "hayhouse"}
EDITION_CANDIDATE_STATUSES = {"proposed", "reviewed_candidate"}
EDITION_SOURCE_URL_COLUMNS = {
    "veritas": "source_url_veritas",
    "audible": "source_url_audible",
    "hayhouse": "source_url_hay_house",
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
    """Produce the public display title while retaining the raw legacy title.

    Carrier and part designators (for example ``DVD01``, ``CD02``, and
    ``PART2``) intentionally remain in the display title by owner direction.
    Only filesystem/transcoding noise and a leading numeric file sequence are
    removed. The raw source string is always emitted separately as
    ``legacy_title``.
    """
    import re

    title = row["proposed_title"].strip()
    if row["raw_tempid"].startswith("LS"):
        return re.sub(r"\s*\([^)]*\)\s*DVD\d+\s*$", "", title).strip()

    title = re.sub(r"\.mp4\s*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s*-\s*converted\s*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^\d{1,3}[.\s]+(?=\S)", "", title)
    title = re.sub(r"\s+", " ", title).strip()

    # Official product 50432 and its two-disc SKU establish that raw row 224
    # is Volume I, disc 2; the raw "Volume II" text is a transcription error.
    if row["raw_row_number"] == "224":
        title = title.replace("Volume II-", "Volume I-", 1)
    return title


def notes_for(row: dict[str, str]) -> str:
    notes = []
    if row["raw_original_source"] and row["raw_original_source"] != "veritas":
        notes.append(f"Raw source note: {row['raw_original_source']}")
    if row["raw_unnamed_5"]:
        notes.append(row["raw_unnamed_5"])
    if row["raw_row_number"] == "224":
        notes.append(
            "Display title corrects raw 'Volume II' to Volume I: official product 50432 is a two-disc Volume I set."
        )
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
    """Derive missing year/month from Veritas inventory published_date.

    Uses the Veritas inventory's ``published_date`` field (ISO format YYYY-MM-DD)
    to backfill missing year and month values. For books, only year is filled
    (publication months are not meaningful for books). For lectures/discussions,
    both year and month are filled. Existing values are never overwritten.
    
    Also attempts legacy tempid-based month extraction for backward compatibility.
    """
    import generate_migration_ledger as ledger_tools

    # Load Veritas inventory for published_date lookup
    veritas_by_url = {}
    if VERITAS_PRODUCTS.exists():
        with VERITAS_PRODUCTS.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                veritas_by_url[row["official_product_url"]] = row

    filled = 0
    for item in items:
        item_type = item.get("item_type", "")
        url = item.get("source_url_veritas", "").strip()
        
        # Try Veritas inventory published_date first
        if url and url in veritas_by_url:
            pub_date = veritas_by_url[url].get("published_date", "").strip()
            if pub_date:
                try:
                    date_parts = pub_date.split("-")
                    if len(date_parts) >= 2:
                        year = date_parts[0]
                        month = date_parts[1]
                        
                        # For books, only fill year
                        if item_type == "book":
                            if not item.get("year", "").strip():
                                item["year"] = year
                                filled += 1
                        else:
                            # For lectures/discussions, fill both
                            if not item.get("year", "").strip():
                                item["year"] = year
                                filled += 1
                            if not item.get("month", "").strip():
                                item["month"] = month
                                filled += 1
                        continue  # Skip legacy tempid check if we filled from inventory
                except (ValueError, IndexError):
                    pass
        
        # Fallback: legacy tempid-based month extraction
        if item["month"] or not item["legacy_tempid"]:
            continue
        month = ledger_tools.proposed_month(
            item["legacy_tempid"].strip(), item["source_url_veritas"]
        )
        if month:
            item["month"] = month
            filled += 1
    return filled


def infer_format_from_official_source(
    item: dict[str, str],
    veritas_by_id: dict[str, dict[str, str]],
    veritas_by_url: dict[str, dict[str, str]] | None = None,
) -> str:
    """Infer a missing format from Veritas product slug, title, and category.

    Uses reliable signals present in the committed official inventory
    (video/volume slugs → DVD, cd-set/satsang-cd → CD, question-answer → streaming,
    audio markers → audio, book markers → book, and — for ``item_type=book``
    records — the publisher's own ``Books Published by Dr. Hawkins`` category).

    The inventory product is resolved by **exact URL match first** (master
    ``source_url_veritas`` is validated to exist in the inventory) and only
    falls back to the legacy numeric-ID-prefix slug guess, which misses the
    many word-slug URLs (``healing-and-recovery-copy`` → no ID prefix). This
    closed the 17-blank-book gap for every URL-bearing book record.

    Only returns a value when the current format field is blank. This is a
    deterministic, reviewable backfill that never overwrites an existing value.
    """
    if item.get("format"):
        return ""
    url = item.get("source_url_veritas", "").strip()
    slug = url.rstrip("/").split("/")[-1].lower() if url else ""

    prod: dict[str, str] = {}
    if url:
        if veritas_by_url:
            prod = veritas_by_url.get(url, {})
        if not prod:
            pid = slug.split("-")[0] if "-" in slug else slug
            prod = veritas_by_id.get(pid, {})
    ot = (prod.get("official_title", "") or item.get("title", "")).lower()

    if url:
        if any(k in slug for k in ("video", "muscle-testing-video")) or slug.startswith("volume-") or slug.startswith("vol-"):
            return "DVD"
        if "cd-set" in slug or ("satsang" in slug and "cd" in slug):
            return "CD"
        if any(k in slug for k in ("question-answer", "question-and-answer", "q&a")):
            return "streaming"
        if "audio" in slug or "– audio" in ot or " audio" in ot:
            return "audio"
        if "book" in slug or "(book)" in ot:
            return "book"
    # Publisher-category evidence: the product sits on the publisher's own
    # books shelf. Guarded by item_type so a lecture/audio edition that merely
    # shares the category cannot be mislabeled; the carrier of a book-class
    # record is the book edition the master is linked to.
    if (
        item.get("item_type") == "book"
        and "Books Published by Dr. Hawkins" in prod.get("official_categories", "")
    ):
        return "book"
    # Category-based inference for DVD/CD products
    cats = prod.get("official_categories", "")
    if "On the Road - Talk Series" in cats or "Archival Office Visit Series" in cats or "Volume Series" in cats:
        return "DVD"
    if "Satsang" in cats:
        return "CD"
    if "Discussion Series" in cats:
        return "streaming"
    # Book item_type without URL (Hay House books without Veritas storefront)
    if item.get("item_type") == "book" and not url:
        return "book"
    return ""


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

    items_by_raw = {}
    for row in items:
        if row["raw_row_number"]:
            items_by_raw[row["raw_row_number"]] = row
        if row.get("candidate_key"):
            items_by_raw[row["candidate_key"]] = row
    
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
        if status not in {"approved", "proposed"}:
            raise ValueError(
                f"{SOURCE_OVERRIDES}:{line_number} review_status must be 'approved' or 'proposed'"
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
        if status == "approved":
            items_by_raw[raw_row][target_field] = value
        seen.add(key)
    return sum(1 for override in overrides if override["review_status"].strip() == "approved")


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

    promoted_keys: set[str] = set()
    if PROMOTIONS.exists():
        with PROMOTIONS.open(encoding="utf-8", newline="") as handle:
            promoted_keys = {row.get("candidate_key", "").strip() for row in csv.DictReader(handle)}

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
        expected_promotion_status = "promoted" if key in promoted_keys else "not_promoted"
        if candidate["promotion_status"].strip() != expected_promotion_status:
            raise ValueError(
                f"{MANUAL_CANDIDATES}:{line_number} must be {expected_promotion_status!r} "
                "to match the explicit promotion registry"
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


def load_promotions() -> list[dict[str, str]]:
    """Load explicit, owner-approved promotions for official candidates."""
    if not PROMOTIONS.exists():
        return []
    with MANUAL_CANDIDATES.open(encoding="utf-8", newline="") as handle:
        candidates = {row["candidate_key"]: row for row in csv.DictReader(handle)}
    with PROMOTIONS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
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


def apply_work_families(items: list[dict[str, str]]) -> int:
    """Assign ``work_id`` from the reviewed work-families input.

    The edition model (see EDITION_MODEL_PROPOSAL.md) groups master rows of
    the same work (book / audio / video editions) under a stable ``work_id``.
    Identity must never be inferred from titles alone (the C2 lesson), so the
    only source of truth is the reviewed ``data/work_families.csv`` input:
    one row per family member, with ``approved`` rows applied and
    ``proposed``/``rejected`` rows validated for shape but never applied.
    """
    if not WORK_FAMILIES.exists():
        return 0
    with WORK_FAMILIES.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = WORK_FAMILY_REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(
                f"{WORK_FAMILIES.name} is missing required columns: "
                f"{', '.join(sorted(missing))}"
            )
        rows = list(reader)

    master_by_uuid = {item["uuid"]: item for item in items}
    work_id_by_member: dict[str, str] = {}
    for line_number, row in enumerate(rows, start=2):
        work_id = row["work_id"].strip()
        member = row["member_master_uuid"].strip()
        status = row["review_status"].strip()
        reviewed_on = row["reviewed_on"].strip()
        if not work_id or not member:
            raise ValueError(
                f"{WORK_FAMILIES.name}:{line_number} needs non-empty work_id and member_master_uuid"
            )
        if status not in WORK_FAMILY_STATUSES:
            raise ValueError(
                f"{WORK_FAMILIES.name}:{line_number} has invalid review_status {status!r}; "
                f"allowed values are {', '.join(sorted(WORK_FAMILY_STATUSES))}"
            )
        if member not in master_by_uuid:
            raise ValueError(
                f"{WORK_FAMILIES.name}:{line_number} references an unknown master ID: {member!r}"
            )
        if member in work_id_by_member:
            raise ValueError(
                f"{WORK_FAMILIES.name}:{line_number} lists master ID {member} twice; "
                "one row per family member"
            )
        if status == "approved":
            if not ISO_DATE.fullmatch(reviewed_on):
                raise ValueError(
                    f"{WORK_FAMILIES.name}:{line_number} approved rows need an ISO reviewed_on date"
                )
            if not row["evidence_note"].strip():
                raise ValueError(
                    f"{WORK_FAMILIES.name}:{line_number} approved rows must explain the evidence"
                )
            if not row["canonical_work_title"].strip():
                raise ValueError(
                    f"{WORK_FAMILIES.name}:{line_number} approved rows need a canonical work title"
                )
            work_id_by_member[member] = work_id

    applied = 0
    for item in items:
        work_id = work_id_by_member.get(item["uuid"], "")
        if work_id:
            item["work_id"] = work_id
            applied += 1
    if applied:
        print(f"[work-families] Applied {applied} approved work-family memberships")
    return applied


def validate_master_items_integrity(items: list[dict[str, str]]) -> None:
    """Enforce structural invariants across all assembled master records."""
    seen_uuids: set[str] = set()
    for item in items:
        uuid = item.get("uuid", "").strip()
        title = item.get("title", "").strip()
        item_type = item.get("item_type", "").strip()
        work_id = item.get("work_id", "").strip()

        if not uuid or not uuid.isdigit():
            raise ValueError(f"Master record has invalid or missing uuid: {uuid!r} (title: {title!r})")
        if uuid in seen_uuids:
            raise ValueError(f"Master record reuses uuid {uuid!r} (title: {title!r})")
        seen_uuids.add(uuid)

        if not title:
            raise ValueError(f"Master record {uuid} has an empty title")

        if work_id and not work_id.startswith("w-"):
            raise ValueError(
                f"Master record {uuid} ({title!r}) has malformed work_id {work_id!r}; "
                "work_ids must start with 'w-'"
            )

        if not item_type and uuid != "246":
            raise ValueError(
                f"Master record {uuid} ({title!r}) has an empty item_type; "
                "only UUID 246 is permitted as a deferred untyped record"
            )


def validate_edition_candidates(items: list[dict[str, str]]) -> int:
    """Validate reviewed edition candidates without promoting them.

    Edition candidates model the edition model's extra carrier rows
    (audiobook, CD/DVD set, ...) for works already in the master (see
    EDITION_MODEL_PROPOSAL.md). They have no raw spreadsheet row; each
    references a work family, an existing master record, and an official
    product in a committed inventory. Promotion is a later explicit action via
    ``data/edition_promotions.csv``; this function never emits rows.
    """
    if not EDITION_CANDIDATES.exists():
        return 0
    with EDITION_CANDIDATES.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing_columns = EDITION_CANDIDATE_REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(
                f"{EDITION_CANDIDATES} is missing required columns: "
                f"{', '.join(sorted(missing_columns))}"
            )
        candidates = list(reader)

    with VERITAS_PRODUCTS.open(encoding="utf-8", newline="") as handle:
        veritas_by_id = {row["veritas_product_id"]: row for row in csv.DictReader(handle)}
    audible_by_url: dict[str, dict[str, str]] = {}
    if AUDIBLE_PRODUCTS.exists():
        with AUDIBLE_PRODUCTS.open(encoding="utf-8", newline="") as handle:
            audible_by_url = {row["audible_url"]: row for row in csv.DictReader(handle)}
    hayhouse_by_url: dict[str, dict[str, str]] = {}
    if HAYHOUSE_PRODUCTS.exists():
        with HAYHOUSE_PRODUCTS.open(encoding="utf-8", newline="") as handle:
            hayhouse_by_url = {row["official_product_url"]: row for row in csv.DictReader(handle)}

    master_by_uuid = {item["uuid"]: item for item in items}
    known_work_ids: set[str] = set()
    if WORK_FAMILIES.exists():
        with WORK_FAMILIES.open(encoding="utf-8", newline="") as handle:
            known_work_ids = {row["work_id"].strip() for row in csv.DictReader(handle)}

    promoted_keys: set[str] = set()
    if EDITION_PROMOTIONS.exists():
        with EDITION_PROMOTIONS.open(encoding="utf-8", newline="") as handle:
            promoted_keys = {
                row.get("candidate_key", "").strip()
                for row in csv.DictReader(handle)
                if row.get("approval_status", "").strip() == "approved"
            }

    seen_keys: set[str] = set()
    for line_number, candidate in enumerate(candidates, start=2):
        key = candidate["candidate_key"].strip()
        work_id = candidate["work_id"].strip()
        role = candidate["edition_role"].strip()
        media_format = candidate["proposed_format"].strip()
        source_name = candidate["source_name"].strip()
        product_id = candidate["source_product_id"].strip()
        year = candidate["proposed_year"].strip()

        if not key.startswith("edition-") or key in seen_keys:
            raise ValueError(
                f"{EDITION_CANDIDATES}:{line_number} needs a unique candidate_key beginning 'edition-'"
            )
        if not work_id or work_id not in known_work_ids:
            raise ValueError(
                f"{EDITION_CANDIDATES}:{line_number} references an unknown work_id {work_id!r}; "
                "declare the work in work_families.csv first"
            )
        if role not in EDITION_ROLES:
            raise ValueError(
                f"{EDITION_CANDIDATES}:{line_number} has invalid edition_role {role!r}; "
                f"allowed values: {', '.join(sorted(EDITION_ROLES))}"
            )
        if candidate["matched_master_uuid"].strip() not in master_by_uuid:
            raise ValueError(
                f"{EDITION_CANDIDATES}:{line_number} references an unknown matched master ID"
            )
        if not candidate["candidate_title"].strip() or media_format not in EDITION_FORMATS:
            raise ValueError(
                f"{EDITION_CANDIDATES}:{line_number} needs a title and a carrier format "
                f"from {', '.join(sorted(EDITION_FORMATS))}"
            )
        if year and (len(year) != 4 or not year.isdigit()):
            raise ValueError(f"{EDITION_CANDIDATES}:{line_number} proposed_year must be blank or YYYY")
        if candidate["proposed_owned"].strip() not in {"", "true", "false"}:
            raise ValueError(
                f"{EDITION_CANDIDATES}:{line_number} proposed_owned must be blank, true, or false"
            )
        if candidate["review_status"].strip() not in EDITION_CANDIDATE_STATUSES:
            raise ValueError(
                f"{EDITION_CANDIDATES}:{line_number} review_status must be "
                f"{', '.join(sorted(EDITION_CANDIDATE_STATUSES))}"
            )
        if candidate["review_status"].strip() == "proposed":
            # Generated draft rows: shape-validated, never promotable until a
            # reviewer flips them to reviewed_candidate with a date.
            if candidate["reviewed_on"].strip() or candidate["promotion_status"].strip() != "not_promoted":
                raise ValueError(
                    f"{EDITION_CANDIDATES}:{line_number} proposed rows must have an empty "
                    "reviewed_on and promotion_status 'not_promoted'"
                )
        else:
            if not ISO_DATE.fullmatch(candidate["reviewed_on"].strip()):
                raise ValueError(f"{EDITION_CANDIDATES}:{line_number} needs an ISO reviewed_on date")
            expected_promotion_status = "promoted" if key in promoted_keys else "not_promoted"
            if candidate["promotion_status"].strip() != expected_promotion_status:
                raise ValueError(
                    f"{EDITION_CANDIDATES}:{line_number} must be {expected_promotion_status!r} "
                    "to match the explicit edition promotion registry"
                )
        if not candidate["evidence_note"].strip() or not candidate["promotion_notes"].strip():
            raise ValueError(f"{EDITION_CANDIDATES}:{line_number} needs evidence and promotion notes")
        if source_name not in EDITION_SOURCES or not product_id:
            raise ValueError(
                f"{EDITION_CANDIDATES}:{line_number} needs a known source_name and product reference"
            )
        if source_name == "veritas":
            product = veritas_by_id.get(product_id)
        elif source_name == "audible":
            product = audible_by_url.get(product_id)
        else:
            product = hayhouse_by_url.get(product_id)
        if not product:
            raise ValueError(
                f"{EDITION_CANDIDATES}:{line_number} references an unknown {source_name} product {product_id!r}"
            )
        expected_url = product.get("official_product_url", product.get("audible_url", ""))
        if candidate["official_product_url"] != expected_url:
            raise ValueError(
                f"{EDITION_CANDIDATES}:{line_number} official_product_url differs from the inventory"
            )
        if candidate["official_product_title"] != product["official_title"]:
            raise ValueError(
                f"{EDITION_CANDIDATES}:{line_number} official_product_title differs from the inventory"
            )
        seen_keys.add(key)
    return len(candidates)


def load_edition_promotions(existing_ids: set[str]) -> list[tuple[dict[str, str], str]]:
    """Load owner-approved edition promotions and mint master rows.

    Edition rows carry an explicitly assigned compact UUID in the promotion
    registry (like the manual promotions path), so their IDs stay stable no
    matter which other rows are added before them.
    """
    if not EDITION_PROMOTIONS.exists():
        return []
    with EDITION_CANDIDATES.open(encoding="utf-8", newline="") as handle:
        candidates = {row["candidate_key"]: row for row in csv.DictReader(handle)}
    with EDITION_PROMOTIONS.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing_columns = EDITION_PROMOTION_REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(
                f"{EDITION_PROMOTIONS} is missing required columns: "
                f"{', '.join(sorted(missing_columns))}"
            )
        rows = list(reader)

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
                "review it (flip to reviewed_candidate) before promoting"
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
            "title_source": "", "item_type": item_type, "series": row["series"].strip(),
            "year": candidate["proposed_year"].strip(), "month": "",
            "format": media_format, "format_detail": candidate["proposed_format_detail"].strip(),
            "owned": candidate["proposed_owned"].strip(),
            "location_physical": "", "location_digital": "", "location_streaming": "",
            "source_url_veritas": "", "source_url_hay_house": "",
            "source_url_nightingale_conant": "", "source_url_audible": "",
            "reference_url_1": "", "reference_url_2": "",
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


def apply_series_approvals(items: list[dict[str, str]]) -> int:
    """Apply approved taxonomy-to-series mappings after item assembly.

    ``data/series_category_mapping.csv`` is the committed, reproducible
    mapping input required by ``CATEGORY_DOMINANCE_POLICY.md``. Only rows a
    reviewer marked ``approved`` may set ``series``, and they never touch
    ``item_type`` (the policy's content-class boundary). Rulings are edited in
    the mapping CSV; generated master files are never hand-edited.
    """
    if not SERIES_MAPPING.exists():
        return 0
    by_uuid = {item["uuid"]: item for item in items}
    approved: dict[str, str] = {}
    with SERIES_MAPPING.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing_columns = SERIES_MAPPING_REQUIRED_COLUMNS - columns
        if missing_columns:
            raise ValueError(
                f"{SERIES_MAPPING} is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )
        for line_number, row in enumerate(reader, start=2):
            if row["review_status"].strip() != "approved":
                continue
            series = row["mapped_series"].strip()
            if not series:
                raise ValueError(
                    f"{SERIES_MAPPING}:{line_number} approved rows require a mapped_series"
                )
            uuids = [part.strip() for part in row["matched_master_uuids"].split(";") if part.strip()]
            for uuid in uuids:
                if uuid not in by_uuid:
                    raise ValueError(
                        f"{SERIES_MAPPING}:{line_number} references an unknown master ID: {uuid!r}"
                    )
                prior = approved.get(uuid)
                if prior is not None and prior != series:
                    raise ValueError(
                        f"{SERIES_MAPPING}:{line_number} gives master ID {uuid} "
                        f"conflicting approved series ({prior!r} vs {series!r})"
                    )
                approved[uuid] = series
    changed = 0
    for uuid, series in approved.items():
        item = by_uuid[uuid]
        if item["series"] != series:
            item["series"] = series
            changed += 1
    if approved:
        print(
            f"[series-taxonomy] {len(approved)} approved mappings cover "
            f"{len(approved)} master IDs; {changed} series values changed"
        )
    return changed


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
            "work_id": "",
            "catalog_code": code,
            "legacy_tempid": row["raw_tempid"],
            "title": canonical_title,
            "legacy_title": row["raw_title"],
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
            "candidate_key": "",
        })

    existing_ids = {item["uuid"] for item in items}
    for candidate in load_promotions():
        if candidate["uuid"] in existing_ids:
            raise ValueError(f"{PROMOTIONS} reuses existing master UUID {candidate['uuid']}")
        year = candidate["proposed_year"]
        item_type = candidate["item_type"]
        code = ""
        if year:
            key = (item_type.upper(), year)
            sequences[key] = sequences.get(key, 0) + 1
            code = f"{key[0]}-{year}-{sequences[key]:03d}"
        items.append({
            "uuid": candidate["uuid"], "work_id": "", "catalog_code": code, "legacy_tempid": "",
            "title": candidate["candidate_title"], "legacy_title": candidate["candidate_title"],
            "title_source": "", "item_type": item_type, "series": candidate["series"],
            "year": year, "month": "", "format": candidate["proposed_format"],
            "format_detail": candidate["proposed_format_detail"], "owned": candidate["proposed_owned"],
            "location_physical": "", "location_digital": "", "location_streaming": "",
            "source_url_veritas": candidate["official_product_url"], "source_url_hay_house": "",
            "source_url_nightingale_conant": "", "source_url_audible": "",
            "reference_url_1": "", "reference_url_2": "",
            "notes": f"Promoted from official candidate {candidate['candidate_key']}: {candidate['evidence_note']}",
            "raw_row_number": "",
            "candidate_key": f"candidate:{candidate['candidate_key']}",
        })
        existing_ids.add(candidate["uuid"])
    edition_rows = load_edition_promotions(existing_ids)
    for row_dict, matched_uuid in edition_rows:
        items.append(row_dict)

    # Source overrides apply after promotions so they can also target
    # candidate-provenance rows (raw_row_number = candidate:<key>), e.g. the
    # Hay House links for promoted masters 316/318. Month backfill and format
    # inference run afterwards, so override URLs still feed both.
    source_overrides_applied = apply_source_overrides(items)

    # D3 (edition model): the audiobook URL moves from the book row into its
    # audiobook edition row and is cleared from the book row. Runs after
    # overrides so an approved audible override cannot re-set the book row.
    by_uuid = {item["uuid"]: item for item in items}
    for row_dict, matched_uuid in edition_rows:
        if row_dict["source_url_audible"] and matched_uuid in by_uuid:
            master_row = by_uuid[matched_uuid]
            if master_row["source_url_audible"] == row_dict["source_url_audible"]:
                master_row["source_url_audible"] = ""
    backfill_months_from_official_source(items)

    # Format backfill from official Veritas inventory (only fills blanks)
    if VERITAS_PRODUCTS.exists():
        with VERITAS_PRODUCTS.open(encoding="utf-8", newline="") as handle:
            inventory_rows = list(csv.DictReader(handle))
        veritas_by_id = {row["veritas_product_id"]: row for row in inventory_rows}
        veritas_by_url = {row["official_product_url"]: row for row in inventory_rows}
        inferred = 0
        for item in items:
            fmt = infer_format_from_official_source(item, veritas_by_id, veritas_by_url)
            if fmt:
                item["format"] = fmt
                inferred += 1
        if inferred:
            # Note for the build log (visible on manual run)
            print(f"[format] Inferred {inferred} formats from official Veritas inventory")

    series_approvals_applied = apply_series_approvals(items)
    work_families_applied = apply_work_families(items)
    validate_master_items_integrity(items)
    edition_candidates_validated = validate_edition_candidates(items)
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
