#!/usr/bin/env python3
"""Build or verify GitHub Pages datasets for the catalogue views.

The raw source CSV and ``docs/data.json`` are never modified. This generator
builds the derived JSON files consumed by the single-page application in ``docs/``:

- ``docs/master.json`` (the curated Everything view)
- ``docs/series-compilations.json``
- ``docs/product-relationships.json``
- ``docs/review-overview.json``
- ``docs/catalogue-meta.json``
... and the publisher/inventory source files.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

from _common import ISO_DATE, json_text, read_csv
from build_research_master import (
    AUDIBLE_PRODUCTS,
    FILENAME_PROPOSAL,
    HAYHOUSE_PRODUCTS,
    MANUAL_CANDIDATES,
    SOURCE_OVERRIDES,
    VERITAS_PRODUCTS,
    build_master,
)
from pipeline.relationships import (
    PRIMARY_RELATIONSHIP_NOTE,  # noqa: F401
    derive_primary_relationships,
    primary_relationship_note,  # noqa: F401
    validate_product_relationships,
)

PRODUCT_RELATIONSHIPS = Path("data/product_relationships.csv")
MASTER = Path("data/research_master_draft.csv")
DOCS_DIR = Path("docs")
DISPLAY_ORDER = Path("data/catalogue_display_order.csv")
SERIES_COMPILATIONS = Path("data/series_compilation_relationships.csv")
NEW_WORK_QUEUE = Path("data/new_work_review_queue.csv")
QUEUE = Path("data/official_discovery_queue.csv")
INTL_QUEUE = Path("data/international_discovery_queue.csv")
VERITAS_MAPPING_DECISIONS = Path("data/veritas_mapping_decisions.csv")
VERITAS_DECISIONS = VERITAS_MAPPING_DECISIONS
PRIMARY_RELATIONSHIP_NOTES = {
    "candidate:edition-": "Promoted edition row (owner-approved 2026-08-03); master primary Veritas URL matches the official product inventory.",
    "candidate:manual-veritas-satsang-": "Owner-approved Satsang new-work promotion (2026-08-03); master primary Veritas URL matches the official product inventory.",
    "candidate:manual-": "Owner-approved promotion (2026-08-03); master primary Veritas URL matches the official product inventory.",
}
MANUAL_LEADS = Path("data/research_manual_leads.csv")
MASTER_EXCLUSIONS = Path("data/research_master_exclusions.csv")
MIGRATION_LEDGER = Path("migration_review_ledger.csv")

OUT_MASTER = DOCS_DIR / "master.json"
OUT_REVIEW_OVERVIEW = DOCS_DIR / "review-overview.json"
OUT_MANUAL_CANDIDATES = DOCS_DIR / "manual-candidates.json"
OUT_MANUAL_LEADS = DOCS_DIR / "manual-leads.json"
OUT_MASTER_EXCLUSIONS = DOCS_DIR / "master-exclusions.json"
OUT_MIGRATION_REVIEW = DOCS_DIR / "migration-review.json"
OUT_SOURCE_OVERRIDES = DOCS_DIR / "source-overrides.json"
OUT_OFFICIAL_DISCOVERY = DOCS_DIR / "official-discovery.json"
OUT_NEW_WORK_REVIEW = DOCS_DIR / "new-work-review.json"
OUT_VERITAS_MAPPING_DECISIONS = DOCS_DIR / "veritas-mapping-decisions.json"
OUT_VERITAS_PRODUCTS = DOCS_DIR / "veritas-products.json"
OUT_PRODUCT_RELATIONSHIPS = DOCS_DIR / "product-relationships.json"
OUT_SERIES_COMPILATIONS = DOCS_DIR / "series-compilations.json"
OUT_HAYHOUSE_PRODUCTS = DOCS_DIR / "hayhouse-products.json"
OUT_AUDIBLE_PRODUCTS = DOCS_DIR / "audible-products.json"
OUT_INTERNATIONAL = DOCS_DIR / "international-products.json"
OUT_FILENAME_PROPOSAL = DOCS_DIR / "filename-proposal.json"
OUT_PUBLISHERS = DOCS_DIR / "publishers.json"
OUT_BLOCK_MAP = DOCS_DIR / "catalogue-block-map.json"
OUT_META = DOCS_DIR / "catalogue-meta.json"

RECORD_TYPE_MASTER = "master"
RECORD_TYPE_CANDIDATE_DISCOVERY = "candidate_discovery"
RECORD_TYPE_CANDIDATE_VERITAS = "candidate_veritas"
RECORD_TYPE_CANDIDATE_HAYHOUSE = "candidate_hayhouse"
RECORD_TYPE_CANDIDATE_AUDIBLE = "candidate_audible"
RECORD_TYPE_CANDIDATE_PENDING = "candidate_pending_promotion"

PUBLISHERS = [
    {
        "publisher": "Veritas Publishing",
        "official_catalogue_url": "https://veritaspub.com/hawkins-products/",
        "status": "approved",
        "role": "Primary creator-affiliated publisher / catalogue",
    },
    {
        "publisher": "Hay House",
        "official_catalogue_url": "https://www.hayhouse.com/authorbio/david-r-hawkins-m-d-ph-d",
        "status": "approved",
        "role": "Book publisher catalogue",
    },
    {
        "publisher": "Nightingale-Conant",
        "official_catalogue_url": "https://www.nightingale.com/pages/david-hawkins",
        "status": "approved",
        "role": "Audio-program publisher catalogue",
    },
    {
        "publisher": "Audible",
        "official_catalogue_url": "https://www.audible.com/author/David-R-Hawkins/B001H6MLOO",
        "status": "approved",
        "role": "Official platform catalogue; not a publisher",
    },
]

EVERYTHING_FIELDS = [
    "uuid", "work_id", "catalog_code", "legacy_tempid", "title", "proposed_filename",
    "proposed_filename_display", "legacy_title", "item_type",
    "series", "year", "month", "year_source", "format", "format_detail", "edition_note", "owned",
    "source_url_veritas", "source_url_hay_house", "source_url_nightingale_conant",
    "source_url_audible", "source_url_amazon", "reference_url_1", "notes", "research",
    "raw_row_number",
]

RELATIONSHIP_REQUIRED_COLUMNS = {
    "relationship_id", "master_uuid", "raw_row_number", "source_name",
    "source_product_id", "official_product_url", "official_product_title",
    "relationship_type", "review_status", "reviewed_on", "evidence_url",
    "evidence_note",
}
RELATIONSHIP_TYPES = {
    "primary_product_for_item_part",
    "edition_of_same_work",
    "related_material",
    "compilation_part",
    "derivative_excerpt",
}
RELATIONSHIP_STATUSES = {"reviewed", "proposed"}

SERIES_COMPILATION_REQUIRED_COLUMNS = {
    "relationship_id", "source_name", "source_product_id", "official_product_url",
    "official_product_title", "relationship_type", "target_series", "target_year",
    "target_month_start", "target_month_end", "included_lecture_count",
    "review_status", "reviewed_on", "evidence_url", "evidence_note"
}
SERIES_COMPILATION_TYPE = "compilation_draws_from_series"


@dataclass
class CatalogueBuild:
    outputs: dict[Path, str]
    items: list[dict[str, str]]
    product_relationships: list[dict[str, str]]
    series_compilations: list[dict[str, str]]


def everything_record(record_type: str, **values: str) -> dict[str, str]:
    """Emit an Everything view record dictionary with normalized keys."""
    row = {"record_type": record_type}
    for field in EVERYTHING_FIELDS:
        row[field] = values.get(field, "")
    return row


def validate_work_family_coverage(master_items: list[dict[str, str]]) -> None:
    """Validate that every curated master record belongs to a work family."""
    for item in master_items:
        if not item.get("work_id", "").strip():
            raise ValueError(
                f"Master record {item['uuid']} ({item['title']!r}) has a missing work_id"
            )


def apply_display_order(master_records: list[dict[str, str]]) -> list[dict[str, str]]:
    """Reorder master records per the reviewed ``catalogue_display_order.csv``."""
    if not DISPLAY_ORDER.exists():
        return master_records
    with DISPLAY_ORDER.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = {"uuid", "block_id", "block_position", "review_status"} - columns
        if missing:
            raise ValueError(
                f"{DISPLAY_ORDER} is missing required columns: {', '.join(sorted(missing))}"
            )
    order_rows = read_csv(DISPLAY_ORDER)
    master_by_uuid = {record["uuid"]: record for record in master_records}
    seen: set[str] = set()
    blocks: dict[str, list[int]] = {}
    for line_number, row in enumerate(order_rows, start=2):
        uuid = row["uuid"].strip()
        if row["review_status"].strip() != "approved":
            raise ValueError(
                f"{DISPLAY_ORDER.name}:{line_number} uuid {uuid} is not approved"
            )
        if uuid in seen:
            raise ValueError(
                f"{DISPLAY_ORDER.name}:{line_number} duplicates UUID {uuid}"
            )
        seen.add(uuid)
        if uuid not in master_by_uuid:
            raise ValueError(
                f"{DISPLAY_ORDER.name}:{line_number} uuid {uuid} is not a master record"
            )
        block = row["block_id"].strip()
        position = row["block_position"].strip()
        if not block or not position.isdigit():
            raise ValueError(
                f"{DISPLAY_ORDER.name}:{line_number} uuid {uuid} has a malformed block/position"
            )
        blocks.setdefault(block, []).append(int(position))
    missing = sorted(set(master_by_uuid) - seen)
    if missing:
        raise ValueError(
            f"{DISPLAY_ORDER.name} is missing master UUID(s): {', '.join(missing)}"
        )
    for block, positions in blocks.items():
        if sorted(positions) != list(range(1, len(positions) + 1)):
            raise ValueError(
                f"{DISPLAY_ORDER.name} block {block!r} positions are not dense "
                f"(got {sorted(positions)})"
            )
    order_by_uuid = {row["uuid"].strip(): rank for rank, row in enumerate(order_rows)}
    return sorted(master_records, key=lambda record: order_by_uuid[record["uuid"]])


def validate_veritas_inventory(
    veritas_products: list[dict[str, str]],
    master_records: list[dict[str, str]],
) -> None:
    """Fail if an inventory row's derived fields contradict its matched master IDs."""
    inconsistent = []
    title_by_uuid = {record["uuid"]: record["title"] for record in master_records}
    inventory_urls = {
        product.get("official_product_url", "").strip()
        for product in veritas_products
        if product.get("official_product_url", "").strip()
    }
    orphaned_master_urls = sorted({
        record.get("source_url_veritas", "").strip()
        for record in master_records
        if record.get("source_url_veritas", "").strip()
        and record.get("source_url_veritas", "").strip() not in inventory_urls
    })
    for url in orphaned_master_urls:
        inconsistent.append(
            f"master source_url_veritas {url!r} is absent from the official inventory"
        )
    for product in veritas_products:
        uuids = [
            item.strip()
            for item in product["matched_master_uuids"].split(";")
            if item.strip()
        ]
        declared = product["normalized_title_match_count"].strip()
        if declared != str(len(uuids)):
            inconsistent.append(
                f"  - product {product['veritas_product_id']}: "
                f"normalized_title_match_count={declared!r} but "
                f"{len(uuids)} matched master ID(s)"
            )
        unknown = [item for item in uuids if item not in title_by_uuid]
        if unknown:
            inconsistent.append(
                f"  - product {product['veritas_product_id']}: "
                f"unknown matched master ID(s) {unknown}"
            )
            continue
        expected_titles = " | ".join(title_by_uuid[item] for item in uuids)
        if product["matched_master_titles"] != expected_titles:
            inconsistent.append(
                f"  - product {product['veritas_product_id']}: "
                f"matched_master_titles {product['matched_master_titles']!r} "
                f"!= master titles {expected_titles!r}"
            )
    if inconsistent:
        raise ValueError(
            f"{VERITAS_PRODUCTS} has derived fields that contradict their "
            "matched master IDs:\n" + "\n".join(inconsistent)
        )


def validate_series_compilations(
    master_items: list[dict[str, str]],
    veritas_products: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Validate compilations at the evidenced series/lecture level."""
    if not SERIES_COMPILATIONS.exists():
        return []
    with SERIES_COMPILATIONS.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = SERIES_COMPILATION_REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(
                f"{SERIES_COMPILATIONS} is missing required columns: "
                f"{', '.join(sorted(missing))}"
            )
        compilations = list(reader)

    veritas_by_id = {product["veritas_product_id"]: product for product in veritas_products}
    seen_ids: set[str] = set()
    enriched: list[dict[str, str]] = []
    for line_number, compilation in enumerate(compilations, start=2):
        relationship_id = compilation["relationship_id"].strip()
        source_product_id = compilation["source_product_id"].strip()
        year = compilation["target_year"].strip()
        start = compilation["target_month_start"].strip()
        end = compilation["target_month_end"].strip()

        if not relationship_id.startswith("series-compilation-") or relationship_id in seen_ids:
            raise ValueError(
                f"{SERIES_COMPILATIONS}:{line_number} needs a unique series-compilation relationship_id"
            )
        if compilation["source_name"].strip() != "veritas" or source_product_id not in veritas_by_id:
            raise ValueError(
                f"{SERIES_COMPILATIONS}:{line_number} needs a known Veritas source product"
            )
        if compilation["relationship_type"].strip() != SERIES_COMPILATION_TYPE:
            raise ValueError(
                f"{SERIES_COMPILATIONS}:{line_number} must use {SERIES_COMPILATION_TYPE}"
            )
        if compilation["review_status"].strip() != "reviewed" or not ISO_DATE.fullmatch(compilation["reviewed_on"].strip()):
            raise ValueError(
                f"{SERIES_COMPILATIONS}:{line_number} needs reviewed status and an ISO reviewed_on date"
            )
        if not year.isdigit() or len(year) != 4:
            raise ValueError(f"{SERIES_COMPILATIONS}:{line_number} target_year must be YYYY")
        if bool(start) != bool(end) or (start and (start not in {f"{n:02d}" for n in range(1, 13)} or end not in {f"{n:02d}" for n in range(1, 13)} or start > end)):
            raise ValueError(
                f"{SERIES_COMPILATIONS}:{line_number} needs a valid paired month range or blank months"
            )
        if not compilation["evidence_url"].startswith("https://") or not compilation["evidence_note"].strip():
            raise ValueError(
                f"{SERIES_COMPILATIONS}:{line_number} needs HTTPS evidence_url and evidence_note"
            )

        product = veritas_by_id[source_product_id]
        if compilation["official_product_url"] != product["official_product_url"] or compilation["official_product_title"] != product["official_title"]:
            raise ValueError(
                f"{SERIES_COMPILATIONS}:{line_number} product URL/title differs from the Veritas inventory"
            )
        target_parts = [
            item for item in master_items
            if item["item_type"] == "lecture"
            and item["series"] == compilation["target_series"]
            and item["year"] == year
            and item.get("raw_row_number", "").strip()
            and (not start or start <= item["month"] <= end)
        ]
        lecture_titles = sorted({item["title"] for item in target_parts})
        if len(lecture_titles) != int(compilation["included_lecture_count"]):
            raise ValueError(
                f"{SERIES_COMPILATIONS}:{line_number} expected {compilation['included_lecture_count']} lectures, "
                f"found {len(lecture_titles)} in the master scope"
            )
        enriched.append({
            **compilation,
            "target_item_part_count": len(target_parts),
            "target_lecture_titles": " | ".join(lecture_titles),
            "source_product_published_date": product["published_date"],
            "source_product_mapping_status": product["mapping_status"],
        })
        seen_ids.add(relationship_id)
    return enriched


VERITAS_DECISION_STATUSES = {
    "unique_item", "compilation_or_new_edition", "excluded_related_material",
    "matched_by_title", "matched_by_normalized_title",
}
VERITAS_DECISION_REQUIRED_COLUMNS = {
    "veritas_product_id", "mapping_status", "matched_master_uuids",
    "matched_master_titles", "review_notes", "review_status", "reviewed_on",
    "decision_reason",
}


def validate_new_work_queue(
    rows: list[dict[str, str]],
    veritas_products: list[dict[str, str]],
) -> None:
    """Fail if a new-work queue row drifts from the official inventory."""
    veritas_by_id = {product["veritas_product_id"]: product for product in veritas_products}
    seen: set[str] = set()
    for line_number, row in enumerate(rows, start=2):
        product_id = row["source_product_id"].strip()
        url = row["source_url_veritas"].strip()
        if not row["candidate_title"].strip():
            raise ValueError(f"{NEW_WORK_QUEUE}:{line_number} needs a candidate_title")
        if not row["match_status"].strip() or not row["match_notes"].strip():
            raise ValueError(
                f"{NEW_WORK_QUEUE}:{line_number} needs match_status and match_notes"
            )
        if product_id in seen:
            raise ValueError(f"{NEW_WORK_QUEUE}:{line_number} duplicates product {product_id}")
        seen.add(product_id)
        product = veritas_by_id.get(product_id)
        if not product:
            raise ValueError(
                f"{NEW_WORK_QUEUE}:{line_number} references an unknown Veritas product {product_id!r}"
            )
        if url != product["official_product_url"]:
            raise ValueError(
                f"{NEW_WORK_QUEUE}:{line_number} source_url_veritas differs from the inventory"
            )


def validate_veritas_mapping_decisions(
    veritas_products: list[dict[str, str]],
    master_records: list[dict[str, str]],
) -> None:
    """Validate the committed mapping overlay against current URL evidence."""
    path = VERITAS_MAPPING_DECISIONS
    if not path.exists():
        return
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = VERITAS_DECISION_REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(
                f"{path} is missing required columns: "
                f"{', '.join(sorted(missing))}"
            )
        decisions = list(reader)

    inventory_by_id = {row["veritas_product_id"].strip(): row for row in veritas_products}
    master_by_uuid = {row["uuid"].strip(): row for row in master_records}
    primary_ids_by_url: dict[str, list[str]] = {}
    for master in master_records:
        url = master.get("source_url_veritas", "").strip()
        if url:
            primary_ids_by_url.setdefault(url, []).append(master["uuid"].strip())

    errors: list[str] = []
    seen_ids: set[str] = set()
    for line_number, decision in enumerate(decisions, start=2):
        product_id = decision["veritas_product_id"].strip()
        status = decision["mapping_status"].strip()
        matched_ids = [
            value.strip()
            for value in decision["matched_master_uuids"].split(";")
            if value.strip()
        ]
        product = inventory_by_id.get(product_id)

        if not product_id or product_id in seen_ids or product is None:
            errors.append(
                f"{path}:{line_number} must reference one unique current product ID"
            )
            continue
        seen_ids.add(product_id)
        if status not in VERITAS_DECISION_STATUSES:
            errors.append(
                f"{path}:{line_number} uses unsupported mapping_status {status!r}"
            )
        if decision["review_status"].strip() != "approved" or not ISO_DATE.fullmatch(decision["reviewed_on"].strip()):
            errors.append(
                f"{path}:{line_number} needs approved review_status and an ISO reviewed_on date"
            )
        if not decision["decision_reason"].strip():
            errors.append(f"{path}:{line_number} needs a decision_reason")

        unknown = [value for value in matched_ids if value not in master_by_uuid]
        if unknown:
            errors.append(
                f"{path}:{line_number} references unknown master ID(s) {unknown}"
            )
        expected_titles = " | ".join(master_by_uuid[value]["title"] for value in matched_ids if value in master_by_uuid)
        if decision["matched_master_titles"] != expected_titles:
            errors.append(
                f"{path}:{line_number} matched_master_titles drift from matched_master_uuids"
            )
        if status in {"matched_by_title", "matched_by_normalized_title"} and not matched_ids:
            errors.append(
                f"{path}:{line_number} match status requires master IDs"
            )
        if status not in {"matched_by_title", "matched_by_normalized_title"} and matched_ids:
            errors.append(
                f"{path}:{line_number} non-match status cannot contain master IDs"
            )

        if product["mapping_status"] != status:
            errors.append(
                f"{path}:{line_number} status {status!r} disagrees with "
                f"the committed inventory status {product['mapping_status']!r}"
            )
        if product["matched_master_uuids"] != decision["matched_master_uuids"]:
            errors.append(
                f"{path}:{line_number} matched_master_uuids disagrees with the inventory"
            )
        if product["matched_master_titles"] != decision["matched_master_titles"]:
            errors.append(
                f"{path}:{line_number} matched_master_titles disagrees with the inventory"
            )
        if product["review_notes"] != decision["review_notes"]:
            errors.append(
                f"{path}:{line_number} review_notes disagrees with the inventory"
            )

        primary_ids = primary_ids_by_url.get(product["official_product_url"].strip(), [])
        if primary_ids:
            errors.append(
                f"{path}:{line_number} product {product_id} is the exact "
                f"primary URL of master ID(s) {primary_ids}; remove the stale non-primary overlay"
            )

    for product in veritas_products:
        product_id = product["veritas_product_id"].strip()
        if product["mapping_status"].strip() in VERITAS_DECISION_STATUSES and product_id not in seen_ids:
            errors.append(
                f"inventory product {product_id} has reviewed non-primary status "
                f"{product['mapping_status']!r} but no decision row"
            )

    if errors:
        raise ValueError(
            f"{path} contradicts the current inventory/master evidence:\n"
            + "\n".join(errors)
        )


def build_review_overview(
    manual_candidates: list[dict[str, str]],
    manual_leads: list[dict[str, str]],
    master_exclusions: list[dict[str, str]],
    migration_review: list[dict[str, str]],
    source_overrides: list[dict[str, str]],
    queue: list[dict[str, str]],
    new_work_queue: list[dict[str, str]],
    veritas_mapping_decisions: list[dict[str, str]],
    veritas_products: list[dict[str, str]],
    hayhouse_products: list[dict[str, str]],
    audible_products: list[dict[str, str]],
    filename_proposal: list[dict[str, str]],
    product_relationships: list[dict[str, str]],
    series_compilations: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Build the Review Overview sheet summary rows."""
    promoted_candidates = sum(
        1 for cand in manual_candidates if cand.get("promotion_status", "").strip() == "promoted"
    )
    unpromoted_candidates = len(manual_candidates) - promoted_candidates
    return [
        {
            "review_sheet": "Master Candidates",
            "record_count": len(manual_candidates),
            "purpose": (
                "All reviewed official candidates have been promoted to the master."
                if unpromoted_candidates == 0
                else f"{promoted_candidates} reviewed candidates promoted; "
                     f"{unpromoted_candidates} still awaiting an explicit master-promotion decision."
            ),
            "source_file": str(MANUAL_CANDIDATES),
            "current_state": (
                f"{promoted_candidates}/{len(manual_candidates)} promoted"
                if unpromoted_candidates == 0
                else f"{promoted_candidates} promoted / {unpromoted_candidates} not_promoted"
            ),
        },
        {
            "review_sheet": "Manual Leads",
            "record_count": len(manual_leads),
            "purpose": "Manual edition/copy or research leads outside the master.",
            "source_file": str(MANUAL_LEADS),
            "current_state": "research lead",
        },
        {
            "review_sheet": "Master Exclusions",
            "record_count": len(master_exclusions),
            "purpose": "Raw rows intentionally excluded from the curated master, with their disposition and review reason.",
            "source_file": str(MASTER_EXCLUSIONS),
            "current_state": "excluded from master / retained as provenance",
        },
        {
            "review_sheet": "Migration Review",
            "record_count": len(migration_review),
            "purpose": "Raw-row disposition and proposed migration metadata.",
            "source_file": str(MIGRATION_LEDGER),
            "current_state": "review and provenance ledger",
        },
        {
            "review_sheet": "Source Overrides",
            "record_count": len(source_overrides),
            "purpose": "Approved official source associations retained after the original ledger pass.",
            "source_file": str(SOURCE_OVERRIDES),
            "current_state": "approved source override",
        },
        {
            "review_sheet": "Official Discovery",
            "record_count": len(queue),
            "purpose": "Nightingale-Conant and platform candidates awaiting source/relationship review.",
            "source_file": str(QUEUE),
            "current_state": "official discovery queue",
        },
        {
            "review_sheet": "New Work Review",
            "record_count": len(new_work_queue),
            "purpose": "Official Veritas products with no master match (Satsang monthlies, Unity Church CDs, unique audio programs) awaiting a new-work ruling.",
            "source_file": str(NEW_WORK_QUEUE),
            "current_state": "new-work review queue",
        },
        {
            "review_sheet": "Veritas Decisions",
            "record_count": len(veritas_mapping_decisions),
            "purpose": "Approved product-ID mapping dispositions re-applied after every live Veritas refresh.",
            "source_file": str(VERITAS_DECISIONS),
            "current_state": "approved mapping decision",
        },
        {
            "review_sheet": "Veritas Products",
            "record_count": len(veritas_products),
            "purpose": "Reviewed Veritas official-product inventory used for source matching, taxonomy mapping, and refresh diffs.",
            "source_file": str(VERITAS_PRODUCTS),
            "current_state": "reviewed official inventory",
        },
        {
            "review_sheet": "Hay House Products",
            "record_count": len(hayhouse_products),
            "purpose": "Reviewed Hay House official-product inventory used for book and audio-edition links.",
            "source_file": str(HAYHOUSE_PRODUCTS),
            "current_state": "reviewed official inventory",
        },
        {
            "review_sheet": "Audible Products",
            "record_count": len(audible_products),
            "purpose": "Reviewed Audible platform inventory used for audiobook editions and international leads.",
            "source_file": str(AUDIBLE_PRODUCTS),
            "current_state": "reviewed platform inventory",
        },
        {
            "review_sheet": "Filename Proposal",
            "record_count": len(filename_proposal),
            "purpose": "Reviewed proposed filenames plus derived master metadata mirrors used by the filename guard.",
            "source_file": str(FILENAME_PROPOSAL),
            "current_state": "reviewed filename proposal",
        },
        {
            "review_sheet": "Product Relationships",
            "record_count": len(product_relationships),
            "purpose": "Reviewed item-to-product assertions kept separate from master identity.",
            "source_file": str(PRODUCT_RELATIONSHIPS),
            "current_state": "reviewed relationship",
        },
        {
            "review_sheet": "Series Compilations",
            "record_count": len(series_compilations),
            "purpose": "Evidence-backed compilation links to annual lecture series without inventing per-DVD-part inclusion.",
            "source_file": str(SERIES_COMPILATIONS),
            "current_state": "reviewed series compilation",
        },
    ]


def build_catalogue(
    master_items: list[dict[str, str]] | None = None,
    include_pending: bool = True,
) -> CatalogueBuild:
    """Build all docs/*.json datasets for GitHub Pages."""
    if master_items is None:
        m_build = build_master()
        master_items = m_build.items

    master_records = list(master_items)
    migrated_items = len(master_records)
    master_records = apply_display_order(master_records)
    filename_proposal = read_csv(FILENAME_PROPOSAL)
    display_by_uuid = {
        row["uuid"].strip(): row["proposed_filename_display"].strip()
        for row in filename_proposal
    }
    items = [
        everything_record(
            RECORD_TYPE_MASTER,
            **{
                field: record.get(field, "")
                for field in EVERYTHING_FIELDS
                if field != "proposed_filename_display"
            },
            proposed_filename_display=display_by_uuid.get(record["uuid"].strip(), ""),
        )
        for record in master_records
    ]
    queue = read_csv(QUEUE)
    new_work_queue = read_csv(NEW_WORK_QUEUE)
    veritas_products = read_csv(VERITAS_PRODUCTS)
    validate_work_family_coverage(master_records)
    validate_veritas_inventory(veritas_products, master_records)
    validate_new_work_queue(new_work_queue, veritas_products)
    veritas_mapping_decisions = read_csv(VERITAS_DECISIONS)
    validate_veritas_mapping_decisions(veritas_products, master_records)

    primary_relationships = derive_primary_relationships(master_records, veritas_products)
    product_relationships = primary_relationships + validate_product_relationships(master_records, veritas_products)
    series_compilations = validate_series_compilations(master_records, veritas_products)
    hayhouse_products = read_csv(HAYHOUSE_PRODUCTS)
    audible_products = read_csv(AUDIBLE_PRODUCTS)
    intl_queue = read_csv(INTL_QUEUE)
    manual_candidates = read_csv(MANUAL_CANDIDATES)
    manual_leads = read_csv(MANUAL_LEADS)

    if include_pending:
        promoted_keys: set[str] = set()
        prom_path = Path("data/manual_candidate_promotions.csv")
        if prom_path.exists():
            with prom_path.open(encoding="utf-8", newline="") as h:
                promoted_keys = {row.get("candidate_key", "").strip() for row in csv.DictReader(h)}
        for cand in manual_candidates:
            if cand["candidate_key"] not in promoted_keys:
                items.append(everything_record(
                    RECORD_TYPE_CANDIDATE_PENDING,
                    title=cand["candidate_title"],
                    item_type=cand["proposed_item_type"],
                    year=cand["proposed_year"],
                    format=cand["proposed_format"],
                    notes=f"Reviewed candidate (not yet promoted): {cand['evidence_note']}",
                ))
    master_exclusions = read_csv(MASTER_EXCLUSIONS)
    source_overrides = read_csv(SOURCE_OVERRIDES)
    migration_review = read_csv(MIGRATION_LEDGER)
    intl_items: list[dict[str, str]] = []

    for candidate in queue:
        items.append(everything_record(
            RECORD_TYPE_CANDIDATE_DISCOVERY,
            title=candidate["candidate_title"],
            item_type=candidate["item_type"],
            series=candidate["series"],
            year=candidate["year"],
            format=candidate["format"],
            source_url_nightingale_conant=candidate["source_url_nightingale_conant"],
            source_url_audible=candidate["source_url_audible"],
            notes=candidate["match_notes"],
        ))

    for product in veritas_products:
        if product["mapping_status"] not in (
            "unreviewed_official_product",
            "unique_item",
            "compilation_or_new_edition",
        ):
            continue
        notes = "Official Veritas product; unreviewed for deduplication."
        if product["mapping_status"] == "unique_item":
            notes = "Official Veritas product; identified as a unique original item."
        elif product["mapping_status"] == "compilation_or_new_edition":
            notes = "Official Veritas product; identified as a compilation or later edition."
        items.append(everything_record(
            RECORD_TYPE_CANDIDATE_VERITAS,
            title=product["official_title"],
            year=product["published_date"][:4],
            source_url_veritas=product["official_product_url"],
            notes=notes,
        ))

    for product in hayhouse_products:
        if product["mapping_status"] != "unreviewed_official_product":
            continue
        items.append(everything_record(
            RECORD_TYPE_CANDIDATE_HAYHOUSE,
            title=product["official_title"],
            format=product.get("format", ""),
            source_url_hay_house=product["official_product_url"],
            notes="Official Hay House product; unreviewed for deduplication and metadata.",
        ))

    for product in audible_products:
        if product["mapping_status"] != "unreviewed_official_product":
            continue
        items.append(everything_record(
            RECORD_TYPE_CANDIDATE_AUDIBLE,
            title=product["official_title"],
            format="audiobook",
            source_url_audible=product["audible_url"],
            notes="Official Audible product; unreviewed for deduplication and metadata.",
        ))

    intl_items.extend(intl_queue)
    review_overview = build_review_overview(
        manual_candidates, manual_leads, master_exclusions, migration_review,
        source_overrides, queue, new_work_queue, veritas_mapping_decisions,
        veritas_products, hayhouse_products, audible_products, filename_proposal,
        product_relationships, series_compilations,
    )
    everything_record_types = {
        record_type: sum(
            row["record_type"] == record_type for row in items
        )
        for record_type in (
            RECORD_TYPE_MASTER,
            RECORD_TYPE_CANDIDATE_DISCOVERY,
            RECORD_TYPE_CANDIDATE_VERITAS,
            RECORD_TYPE_CANDIDATE_HAYHOUSE,
            RECORD_TYPE_CANDIDATE_AUDIBLE,
            RECORD_TYPE_CANDIDATE_PENDING,
        )
    }
    if sum(everything_record_types.values()) != len(items):
        raise ValueError(
            "catalogue-meta record-type counts "
            f"({sum(everything_record_types.values())}) do not cover every "
            f"Everything row ({len(items)}): an unlabeled record_type leaked in"
        )

    publishers = PUBLISHERS
    order_rows = read_csv(DISPLAY_ORDER) if DISPLAY_ORDER.exists() else []
    block_map = {
        row["uuid"].strip(): row["block_id"].strip()
        for row in order_rows
        if row.get("uuid") and row.get("block_id") and row.get("review_status") == "approved"
    }
    outputs = {
        OUT_MASTER: json_text(items),
        OUT_REVIEW_OVERVIEW: json_text(review_overview),
        OUT_MANUAL_CANDIDATES: json_text(manual_candidates),
        OUT_MANUAL_LEADS: json_text(manual_leads),
        OUT_MASTER_EXCLUSIONS: json_text(master_exclusions),
        OUT_MIGRATION_REVIEW: json_text(migration_review),
        OUT_SOURCE_OVERRIDES: json_text(source_overrides),
        OUT_OFFICIAL_DISCOVERY: json_text(queue),
        OUT_NEW_WORK_REVIEW: json_text(new_work_queue),
        OUT_VERITAS_MAPPING_DECISIONS: json_text(veritas_mapping_decisions),
        OUT_VERITAS_PRODUCTS: json_text(veritas_products),
        OUT_PRODUCT_RELATIONSHIPS: json_text(product_relationships),
        OUT_SERIES_COMPILATIONS: json_text(series_compilations),
        OUT_HAYHOUSE_PRODUCTS: json_text(hayhouse_products),
        OUT_AUDIBLE_PRODUCTS: json_text(audible_products),
        OUT_INTERNATIONAL: json_text(intl_items),
        OUT_FILENAME_PROPOSAL: json_text(filename_proposal),
        OUT_PUBLISHERS: json_text(publishers),
        OUT_BLOCK_MAP: json_text(block_map),
        OUT_META: json_text({
            "master_items": migrated_items,
            "migrated_items": migrated_items,
            "everything_record_types": everything_record_types,
            "reviewed_manual_candidates": len(manual_candidates),
            "manual_research_leads": len(manual_leads),
            "master_exclusion_rows": len(master_exclusions),
            "migration_review_rows": len(migration_review),
            "approved_source_overrides": sum(
                row["review_status"] == "approved" for row in source_overrides
            ),
            "official_discovery_candidates": len(queue),
            "approved_veritas_mapping_decisions": len(veritas_mapping_decisions),
            "implemented_unreviewed": (
                len(queue)
                + sum(
                    product["mapping_status"] in (
                        "unreviewed_official_product",
                        "unique_item",
                        "compilation_or_new_edition",
                    )
                    for product in veritas_products
                )
                + sum(
                    product["mapping_status"] == "unreviewed_official_product"
                    for product in audible_products
                )
                + sum(
                    product["mapping_status"] == "unreviewed_official_product"
                    for product in hayhouse_products
                )
            ),
            "veritas_official_products": len(veritas_products),
            "reviewed_product_relationships": sum(
                relationship["review_status"] == "reviewed"
                for relationship in product_relationships
            ),
            "pending_product_relationships": sum(
                relationship["review_status"] == "pending"
                for relationship in product_relationships
            ),
            "reviewed_series_compilations": sum(
                compilation["review_status"] == "reviewed"
                for compilation in series_compilations
            ),
            "hayhouse_official_products": len(hayhouse_products),
            "audible_official_products": len(audible_products),
            "international_products": len(intl_items),
            "approved_publishers": len(PUBLISHERS),
            "original_source_rows": len(migration_review),
        }),
    }
    return CatalogueBuild(
        outputs=outputs,
        items=items,
        product_relationships=product_relationships,
        series_compilations=series_compilations,
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
        help="verify docs/*.json outputs match current inputs; do not write files",
    )
    parser.add_argument(
        "--include-pending",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="include the unpromoted reviewed manual candidates as "
        "candidate_pending_promotion rows in Everything (default; "
        "--no-include-pending builds a reduced view for local inspection only)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    build = build_catalogue(include_pending=args.include_pending)

    if args.check:
        stale = stale_outputs(build.outputs)
        if stale:
            print("Pages catalogue outputs are stale relative to inputs:")
            for path in stale:
                print(f"  - {path}")
            return 1
        print(f"Pages catalogue outputs match their inputs ({len(build.items)} Everything rows).")
        return 0

    write_outputs(build.outputs)
    print(f"Wrote {len(build.outputs)} catalogue datasets in {DOCS_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
