#!/usr/bin/env python3
"""Validation and integrity routines for pipeline data inputs and outputs."""

from __future__ import annotations

import re
from pathlib import Path

from _common import read_csv
from pipeline.helpers import (
    index_csv,
    require_columns,
    veritas_products_by_id,
)

# Constants & Paths (relative to working directory so sandbox tests work)
DATA_DIR = Path("data")
FILENAME_PROPOSAL = DATA_DIR / "filename_proposal_YYYYMM.csv"
MANUAL_CANDIDATES = DATA_DIR / "manual_master_candidates.csv"
EDITION_CANDIDATES = DATA_DIR / "edition_candidates.csv"
EDITION_PROMOTIONS = DATA_DIR / "edition_promotions.csv"
PROMOTIONS = DATA_DIR / "manual_candidate_promotions.csv"
WORK_FAMILIES = DATA_DIR / "work_families.csv"
AUDIBLE_PRODUCTS = DATA_DIR / "audible_official_products.csv"
HAYHOUSE_PRODUCTS = DATA_DIR / "hayhouse_official_products.csv"

CONTENT_ITEM_TYPES = {"lecture", "discussion", "book", "highlight", "other"}
MANUAL_CANDIDATE_FORMATS = {"", "DVD", "CD", "audiobook", "book"}
EDITION_FORMATS = {"DVD", "CD", "audiobook", "book", "streaming"}
EDITION_ROLES = {
    "audiobook", "paperback", "hardcover", "ebook", "cd_set", "dvd_set",
    "streaming_edition", "audio", "video", "book"
}
EDITION_SOURCES = {"veritas", "audible", "hayhouse"}
EDITION_CANDIDATE_STATUSES = {"proposed", "reviewed_candidate", "rejected"}
MANUAL_CANDIDATE_REQUIRED_COLUMNS = {
    "candidate_key", "candidate_title", "proposed_item_type", "proposed_year",
    "proposed_format", "proposed_owned", "source_name", "source_product_id",
    "official_product_url", "official_product_title", "evidence_note",
    "review_status", "reviewed_on", "promotion_status", "promotion_notes"
}
EDITION_CANDIDATE_REQUIRED_COLUMNS = {
    "candidate_key", "work_id", "edition_role", "matched_master_uuid",
    "candidate_title", "proposed_format", "proposed_format_detail", "proposed_year",
    "proposed_owned", "source_name", "source_product_id", "official_product_url",
    "official_product_title", "evidence_note", "review_status", "reviewed_on",
    "promotion_status", "promotion_notes"
}
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _normalized_tokens(text: str) -> set[str]:
    """Lowercased alphanumeric tokens of a title for group-coherence checks."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _normalized_title(title: str) -> str:
    """Lowercase, punctuation-free, whitespace-collapsed key for title matching."""
    lowered = title.lower()
    lowered = re.sub(r"[^a-z0-9 ]", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def validate_filename_proposal_groups() -> None:
    """Fail the build if reviewed filename-proposal part groups are incoherent."""
    if not FILENAME_PROPOSAL.exists():
        return
    require_columns(
        FILENAME_PROPOSAL,
        {"uuid", "title", "clean_title", "part_index", "part_total",
         "proposed_filename", "proposed_filename_display"},
    )
    seen_names: dict[str, str] = {}
    for row in read_csv(FILENAME_PROPOSAL):
        for column in ("proposed_filename", "proposed_filename_display"):
            name = row[column].strip()
            if not name:
                raise ValueError(
                    f"{FILENAME_PROPOSAL}: UUID {row['uuid'].strip()} has an empty {column}"
                )
            other = seen_names.get(f"{column}::{name}")
            if other and other != row["uuid"].strip():
                raise ValueError(
                    f"{FILENAME_PROPOSAL}: {column} {name!r} is used by both "
                    f"UUID {other} and UUID {row['uuid'].strip()} — filenames must be "
                    "globally unique (v4.1: same-work non-part variants carry an explicit "
                    "carrier or publisher suffix)"
                )
            seen_names[f"{column}::{name}"] = row["uuid"].strip()
    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = {}
    for row in read_csv(FILENAME_PROPOSAL):
        key = (row["clean_title"].strip(), row["year"].strip(),
               row["month"].strip(), row["format"].strip())
        groups.setdefault(key, []).append(row)
    for (clean_title, _year, _month, _format), group in groups.items():
        clean_tokens = _normalized_tokens(clean_title)
        if not clean_tokens:
            continue
        for row in group:
            uuid = row["uuid"].strip()
            missing = sorted(clean_tokens - _normalized_tokens(row["title"]))
            if missing:
                raise ValueError(
                    f"{FILENAME_PROPOSAL}: UUID {uuid} clean_title {clean_title!r} "
                    f"is not derived from its own title {row['title']!r} "
                    f"(missing tokens: {', '.join(missing)}) — a row cannot join "
                    "the part group of a different title"
                )
            part_index = row["part_index"].strip()
            part_total = row["part_total"].strip()
            if part_index and part_total and int(part_index) > int(part_total):
                raise ValueError(
                    f"{FILENAME_PROPOSAL}: UUID {uuid} part_index {part_index} "
                    f"exceeds part_total {part_total}"
                )
        indexes = [row["part_index"].strip() for row in group if row["part_index"].strip()]
        totals = {row["part_total"].strip() for row in group if row["part_total"].strip()}
        if len(indexes) != len(set(indexes)):
            raise ValueError(
                f"{FILENAME_PROPOSAL}: part group {clean_title!r} contains "
                "duplicate part_index values"
            )
        if len(totals) > 1:
            raise ValueError(
                f"{FILENAME_PROPOSAL}: part group {clean_title!r} mixes part_total "
                f"values {sorted(totals)}"
            )


def validate_manual_candidates() -> int:
    """Validate reviewed manual candidates without promoting them to the master."""
    if not MANUAL_CANDIDATES.exists():
        return 0

    require_columns(MANUAL_CANDIDATES, MANUAL_CANDIDATE_REQUIRED_COLUMNS)
    candidates = read_csv(MANUAL_CANDIDATES)
    veritas_by_id = veritas_products_by_id()

    promoted_keys: set[str] = set()
    if PROMOTIONS.exists():
        promoted_keys = {row.get("candidate_key", "").strip() for row in read_csv(PROMOTIONS)}

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
        if not candidate["candidate_title"].strip() or item_type not in CONTENT_ITEM_TYPES:
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
        if source_name == "veritas":
            if product_id not in veritas_by_id:
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
        else:
            allowed_external = {"academic", "other", "freeman", "amazon", "openlibrary"}
            if source_name not in allowed_external:
                raise ValueError(
                    f"{MANUAL_CANDIDATES}:{line_number} has unsupported source_name {source_name!r}; "
                    f"allowed: veritas + {', '.join(sorted(allowed_external))}"
                )
            url = candidate["official_product_url"].strip()
            if url and not url.startswith("https://"):
                raise ValueError(
                    f"{MANUAL_CANDIDATES}:{line_number} non-Veritas official_product_url must be blank or HTTPS"
                )
        seen_keys.add(key)
    return len(candidates)


def validate_filename_proposal_mirrors(items: list[dict[str, str]]) -> None:
    """Ensure filename-proposal metadata mirrors the final master rows."""
    if not FILENAME_PROPOSAL.exists():
        return
    mirror_fields = ["work_id", "item_type", "series", "year", "month", "format", "title"]
    require_columns(FILENAME_PROPOSAL, {"uuid", *mirror_fields})
    proposals = read_csv(FILENAME_PROPOSAL)
    proposal_by_uuid: dict[str, dict[str, str]] = {}
    for line_number, row in enumerate(proposals, start=2):
        uuid = row["uuid"].strip()
        if not uuid:
            raise ValueError(f"{FILENAME_PROPOSAL}:{line_number} has a blank uuid")
        if uuid in proposal_by_uuid:
            raise ValueError(f"{FILENAME_PROPOSAL}:{line_number} duplicates UUID {uuid}")
        proposal_by_uuid[uuid] = row

    master_by_uuid = {item["uuid"]: item for item in items}
    sort_uuid = lambda value: (0, int(value)) if value.isdigit() else (1, value)
    missing = sorted(set(master_by_uuid) - set(proposal_by_uuid), key=sort_uuid)
    if missing:
        raise ValueError(
            f"{FILENAME_PROPOSAL} is missing filename proposal row(s) for master UUID(s): "
            f"{', '.join(missing)}"
        )

    if set(proposal_by_uuid) != set(master_by_uuid):
        return

    fields_to_compare = list(mirror_fields)
    if any(not item.get("work_id", "").strip() for item in items):
        fields_to_compare.remove("work_id")

    mismatches: list[str] = []
    for uuid, item in master_by_uuid.items():
        proposal = proposal_by_uuid[uuid]
        for field in fields_to_compare:
            if proposal[field].strip() != item.get(field, "").strip():
                mismatches.append(
                    f"UUID {uuid} field {field}: proposal {proposal[field]!r} "
                    f"!= master {item.get(field, '')!r}"
                )
    if mismatches:
        raise ValueError(
            f"{FILENAME_PROPOSAL} metadata mirrors are stale:\n  - "
            + "\n  - ".join(mismatches)
        )


def validate_master_items_integrity(items: list[dict[str, str]]) -> None:
    """Enforce structural invariants across all assembled master records."""
    seen_uuids: set[str] = set()
    same_product_groups: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = {}
    for item in items:
        uuid = item.get("uuid", "").strip()
        title = item.get("title", "").strip()
        item_type = item.get("item_type", "").strip()
        work_id = item.get("work_id", "").strip()
        media_format = item.get("format", "").strip()
        format_detail = item.get("format_detail", "").strip()

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

        if media_format in {"DVD", "CD"} and "stream" in format_detail.lower():
            raise ValueError(
                f"Master record {uuid} ({title!r}) mixes carrier {media_format!r} "
                f"with streaming format_detail {format_detail!r}; per the 2026-08-08 "
                "owner ruling, streaming availability for DVD/CD items belongs in "
                "reference_url_1, not in the carrier detail"
            )

        if not item_type:
            raise ValueError(
                f"Master record {uuid} ({title!r}) has an empty item_type; "
                "every master record must have a content class"
            )

        url = item.get("source_url_veritas", "").strip()
        if url and title and item_type:
            key = (
                url,
                _normalized_title(title),
                item_type,
                item.get("series", "").strip(),
                item.get("year", "").strip(),
            )
            same_product_groups.setdefault(key, []).append(item)

    for (url, _title_key, item_type, series, year), group in same_product_groups.items():
        work_ids = {row.get("work_id", "").strip() for row in group if row.get("work_id", "").strip()}
        if len(work_ids) > 1:
            details = "; ".join(
                f"UUID {row['uuid']} work_id={row.get('work_id', '')!r} format={row.get('format', '')!r}"
                for row in group
            )
            raise ValueError(
                "Master rows with the same Veritas URL, normalized title, type, "
                f"series, and year must share one work_id ({url}, {item_type}, "
                f"{series}, {year}): {details}"
            )


def validate_edition_candidates(items: list[dict[str, str]]) -> int:
    """Validate reviewed edition candidates without promoting them."""
    if not EDITION_CANDIDATES.exists():
        return 0
    require_columns(EDITION_CANDIDATES, EDITION_CANDIDATE_REQUIRED_COLUMNS)
    candidates = read_csv(EDITION_CANDIDATES)

    veritas_by_id = veritas_products_by_id()
    audible_by_url: dict[str, dict[str, str]] = (
        index_csv(AUDIBLE_PRODUCTS, "audible_url") if AUDIBLE_PRODUCTS.exists() else {}
    )
    hayhouse_by_url: dict[str, dict[str, str]] = (
        index_csv(HAYHOUSE_PRODUCTS, "official_product_url") if HAYHOUSE_PRODUCTS.exists() else {}
    )

    master_by_uuid = {item["uuid"]: item for item in items}
    known_work_ids: set[str] = set()
    if WORK_FAMILIES.exists():
        known_work_ids = {row["work_id"].strip() for row in read_csv(WORK_FAMILIES)}

    promoted_keys: set[str] = set()
    if EDITION_PROMOTIONS.exists():
        promoted_keys = {
            row.get("candidate_key", "").strip()
            for row in read_csv(EDITION_PROMOTIONS)
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
