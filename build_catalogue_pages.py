#!/usr/bin/env python3
"""Build or verify GitHub Pages datasets for the catalogue views.

The Everything view combines the clean migrated draft with discovered official
candidates. Product inventories and the immutable original spreadsheet remain
separate views. Use ``--check`` to compare generated content with committed
Pages files without writing any files.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

MASTER = Path("data/research_master_draft.csv")
QUEUE = Path("data/official_discovery_queue.csv")
NEW_WORK_QUEUE = Path("data/new_work_review_queue.csv")
INTL_QUEUE = Path("data/international_discovery_queue.csv")
VERITAS_PRODUCTS = Path("data/veritas_official_products.csv")
VERITAS_MAPPING_DECISIONS = Path("data/veritas_mapping_decisions.csv")
HAYHOUSE_PRODUCTS = Path("data/hayhouse_official_products.csv")
AUDIBLE_PRODUCTS = Path("data/audible_official_products.csv")
PRODUCT_RELATIONSHIPS = Path("data/product_relationships.csv")
SERIES_COMPILATIONS = Path("data/series_compilation_relationships.csv")
MANUAL_CANDIDATES = Path("data/manual_master_candidates.csv")
MANUAL_LEADS = Path("data/research_manual_leads.csv")
MASTER_EXCLUSIONS = Path("data/research_master_exclusions.csv")
SOURCE_OVERRIDES = Path("data/research_master_source_overrides.csv")
MIGRATION_LEDGER = Path("migration_review_ledger.csv")
OUT_MASTER = Path("docs/master.json")
OUT_REVIEW_OVERVIEW = Path("docs/review-overview.json")
OUT_MANUAL_CANDIDATES = Path("docs/manual-candidates.json")
OUT_MANUAL_LEADS = Path("docs/manual-leads.json")
OUT_MASTER_EXCLUSIONS = Path("docs/master-exclusions.json")
OUT_MIGRATION_REVIEW = Path("docs/migration-review.json")
OUT_SOURCE_OVERRIDES = Path("docs/source-overrides.json")
OUT_OFFICIAL_DISCOVERY = Path("docs/official-discovery.json")
OUT_NEW_WORK_REVIEW = Path("docs/new-work-review.json")
OUT_VERITAS_MAPPING_DECISIONS = Path("docs/veritas-mapping-decisions.json")
OUT_VERITAS_PRODUCTS = Path("docs/veritas-products.json")
OUT_PRODUCT_RELATIONSHIPS = Path("docs/product-relationships.json")
OUT_SERIES_COMPILATIONS = Path("docs/series-compilations.json")
OUT_HAYHOUSE_PRODUCTS = Path("docs/hayhouse-products.json")
OUT_AUDIBLE_PRODUCTS = Path("docs/audible-products.json")
OUT_INTERNATIONAL = Path("docs/international-products.json")
OUT_PUBLISHERS = Path("docs/publishers.json")
OUT_META = Path("docs/catalogue-meta.json")

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


RELATIONSHIP_REQUIRED_COLUMNS = {
    "relationship_id", "master_uuid", "raw_row_number", "source_name",
    "source_product_id", "official_product_url", "official_product_title",
    "relationship_type", "review_status", "reviewed_on", "evidence_url",
    "evidence_note",
}
RELATIONSHIP_TYPES = {
    "primary_product_for_item_part",
    "same_material_edition",
    "compilation_includes_item",
    "related_material",
    "unresolved",
}
RELATIONSHIP_STATUSES = {"reviewed", "pending", "rejected"}
SERIES_COMPILATION_REQUIRED_COLUMNS = {
    "relationship_id", "source_name", "source_product_id", "official_product_url",
    "official_product_title", "relationship_type", "target_series", "target_year",
    "target_month_start", "target_month_end", "included_lecture_count", "review_status",
    "reviewed_on", "evidence_url", "evidence_note",
}
SERIES_COMPILATION_TYPE = "compilation_draws_from_series"
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Everything-view provenance classes. The Everything sheet deliberately shows
# curated master records next to official candidates so reviewers can compare
# them, so each row must state which one it is instead of relying on an empty
# master ID or free-text notes.
RECORD_TYPE_MASTER = "master"
RECORD_TYPE_CANDIDATE_DISCOVERY = "candidate_discovery"
RECORD_TYPE_CANDIDATE_VERITAS = "candidate_veritas"
RECORD_TYPE_CANDIDATE_HAYHOUSE = "candidate_hayhouse"
RECORD_TYPE_CANDIDATE_AUDIBLE = "candidate_audible"
RECORD_TYPE_CANDIDATE_PENDING = "candidate_pending_promotion"

# Master identity fields carried into the Everything view. ``record_type`` is a
# view-level provenance label and is intentionally not part of the master CSV
# schema, which stays owned by build_research_master.py.
EVERYTHING_FIELDS = [
    "uuid", "work_id", "catalog_code", "legacy_tempid", "title", "title_source", "item_type",
    "series", "year", "month", "format", "format_detail", "owned",
    "location_physical", "location_digital", "location_streaming",
    "source_url_veritas", "source_url_hay_house", "source_url_nightingale_conant",
    "source_url_audible", "reference_url_1", "reference_url_2", "notes",
    "raw_row_number",
]


def everything_record(record_type: str, **values: str) -> dict[str, str]:
    """Return one Everything-view row with a stated provenance class.

    Every Everything row shares the master field order so the sheet, its CSV
    export, and the column presets stay stable regardless of which source
    contributed the row. Unsupplied fields are empty strings rather than
    missing keys.
    """
    unknown = set(values) - set(EVERYTHING_FIELDS)
    if unknown:
        raise ValueError(f"Unknown Everything fields: {sorted(unknown)}")
    row = {"record_type": record_type}
    row.update({field: values.get(field, "") for field in EVERYTHING_FIELDS})
    return row


@dataclass
class CatalogueBuild:
    """In-memory Pages artifacts shared by normal builds and reconciliation."""

    items: list[dict[str, str]]
    product_relationships: list[dict[str, str]]
    series_compilations: list[dict[str, str]]
    outputs: dict[Path, str]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_work_family_coverage(master_items: list[dict[str, str]]) -> None:
    """Validate that every curated master record belongs to a work family."""
    for item in master_items:
        if not item.get("work_id", "").strip():
            raise ValueError(
                f"Master record {item['uuid']} ({item['title']!r}) has a missing work_id"
            )


def validate_veritas_inventory(
    veritas_products: list[dict[str, str]],
    master_records: list[dict[str, str]],
) -> None:
    """Fail if an inventory row's derived fields contradict its matched master IDs.

    ``normalized_title_match_count`` is a derived field: it must always equal the
    number of IDs in ``matched_master_uuids``. A mismatch means the committed
    inventory was written without the approved decision overlay applied, which
    is exactly the drift a live refresh would otherwise report as an upstream
    catalogue change. Catching it here keeps the refresh diff meaningful.

    The same discipline applies to ``matched_master_titles``, a mirror of the
    referenced master records' current titles: hand-edits to either side
    (titles in the master or this mirroring column) must fail the build instead
    of silently diverging.
    """
    inconsistent = []
    title_by_uuid = {record["uuid"]: record["title"] for record in master_records}
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


def validate_product_relationships(
    master_items: list[dict[str, str]],
    veritas_products: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Validate and enrich reviewed master-to-product relationships.

    Source relationships are a separate, explicit layer: a commercial product
    can represent one item part, an edition, a compilation, or merely related
    material. The seed uses Veritas product IDs from the committed inventory;
    support for another source requires its own stable product inventory.
    """
    with PRODUCT_RELATIONSHIPS.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = RELATIONSHIP_REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS} is missing required columns: "
                f"{', '.join(sorted(missing))}"
            )
        relationships = list(reader)

    master_by_uuid = {item["uuid"]: item for item in master_items}
    veritas_by_id = {product["veritas_product_id"]: product for product in veritas_products}
    seen_ids: set[str] = set()
    enriched: list[dict[str, str]] = []

    for line_number, relation in enumerate(relationships, start=2):
        relation_id = relation["relationship_id"].strip()
        master_uuid = relation["master_uuid"].strip()
        source_name = relation["source_name"].strip()
        product_id = relation["source_product_id"].strip()
        relation_type = relation["relationship_type"].strip()
        review_status = relation["review_status"].strip()
        reviewed_on = relation["reviewed_on"].strip()

        if not relation_id or relation_id in seen_ids:
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} has a missing or duplicate relationship_id"
            )
        if not relation_id.startswith("rel-"):
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} relationship_id must start with 'rel-'"
            )
        if master_uuid not in master_by_uuid:
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} references an unknown master ID: {master_uuid!r}"
            )
        if source_name != "veritas":
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} has unsupported source_name {source_name!r}; "
                "add a stable source inventory before using another source"
            )
        if product_id not in veritas_by_id:
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} references unknown Veritas product {product_id!r}"
            )
        if relation_type not in RELATIONSHIP_TYPES:
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} has invalid relationship_type {relation_type!r}"
            )
        if review_status not in RELATIONSHIP_STATUSES:
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} has invalid review_status {review_status!r}"
            )
        if review_status == "reviewed" and not ISO_DATE.fullmatch(reviewed_on):
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} reviewed relationships need an ISO reviewed_on date"
            )
        if not relation["evidence_url"].startswith("https://"):
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} must have an HTTPS evidence_url"
            )
        if not relation["evidence_note"].strip():
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} must explain the relationship"
            )

        master = master_by_uuid[master_uuid]
        product = veritas_by_id[product_id]
        # Check raw_row_number or candidate_key match
        master_provenance = master["raw_row_number"] or master.get("candidate_key", "")
        if relation["raw_row_number"] != master_provenance:
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} raw_row_number does not match {master_uuid}"
            )
        if relation["official_product_url"] != product["official_product_url"]:
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} product URL differs from the Veritas inventory"
            )
        if relation["official_product_title"] != product["official_title"]:
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} product title differs from the Veritas inventory"
            )
        if (
            relation_type == "primary_product_for_item_part"
            and master["source_url_veritas"] != relation["official_product_url"]
        ):
            raise ValueError(
                f"{PRODUCT_RELATIONSHIPS}:{line_number} primary product must match the master Veritas URL"
            )

        enriched.append({
            **relation,
            "master_catalog_code": master["catalog_code"],
            "master_title": master["title"],
            "master_item_type": master["item_type"],
            "master_year": master["year"],
            "source_product_published_date": product["published_date"],
            "source_product_mapping_status": product["mapping_status"],
        })
        seen_ids.add(relation_id)
    return enriched


def validate_primary_relationship_coverage(
    master_items: list[dict[str, str]],
    relationships: list[dict[str, str]],
) -> None:
    """Fail when a master's Veritas URL has no primary relationship row.

    The schema invariant in PRODUCT_RELATIONSHIP_SCHEMA.md says every non-empty
    master ``source_url_veritas`` must be covered by a reviewed
    ``primary_product_for_item_part`` row. The promoted-candidate path used to
    leave such a gap (master IDs 309-319); it was closed with 11 reviewed rows
    on 2026-08-03 and the guard was then promoted from a warning to a hard
    failure so the gap can never silently recur.
    """
    primary_masters = {
        relation["master_uuid"].strip()
        for relation in relationships
        if relation["relationship_type"].strip() == "primary_product_for_item_part"
    }
    uncovered = sorted(
        (
            item["uuid"].strip()
            for item in master_items
            if item["source_url_veritas"].strip()
            and item["uuid"].strip() not in primary_masters
            # Promoted edition rows carry their primary product by
            # construction: the promotion itself is the reviewed assertion
            # (see EDITION_MODEL_PROPOSAL.md), so they are self-covered.
            and not item.get("raw_row_number", "").startswith("candidate:edition-")
        ),
        key=int,
    )
    if uncovered:
        raise ValueError(
            "master record(s) have a Veritas source URL but no reviewed "
            f"primary relationship in {PRODUCT_RELATIONSHIPS.name}: "
            + ", ".join(uncovered)
            + " — add reviewed primary_product_for_item_part rows or the "
            "Product Relationships tab stays incomplete."
        )


def validate_series_compilations(
    master_items: list[dict[str, str]],
    veritas_products: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Validate compilations at the evidenced series/lecture level.

    Highlights pages identify all lectures in a year or month range, but not the
    individual DVD part that supplied each clip. This layer records that exact
    evidence without manufacturing per-part inclusion relationships.
    """
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


def validate_new_work_queue(
    rows: list[dict[str, str]],
    veritas_products: list[dict[str, str]],
) -> None:
    """Fail if a new-work queue row drifts from the official inventory.

    The new-work review lane holds official Veritas products with no master
    match (Satsang monthlies, Unity Church CDs, unique audio programs). Every
    row must reference a real inventory product with the exact inventory URL,
    so a hand-edit or a stale product ID cannot silently enter the queue.
    """
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


def json_text(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def build_catalogue(master_items: list[dict[str, str]] | None = None, include_pending: bool = True) -> CatalogueBuild:
    """Prepare catalogue Pages files in memory.

    ``master_items`` exists for read-only reconciliation: it lets callers
    project the Pages site from a ledger-derived master without overwriting the
    committed master draft first. Normal builds read ``MASTER`` unchanged.

    ``include_pending`` defaults to ``True`` so the committed Everything view
    surfaces unpromoted reviewed manual candidates for owner review; pass
    ``False`` (``--no-include-pending``) only for a reduced local inspection
    view — never for committed outputs.
    """
    master_records = list(master_items) if master_items is not None else read_csv(MASTER)
    migrated_items = len(master_records)
    items = [
        everything_record(
            RECORD_TYPE_MASTER,
            **{field: record.get(field, "") for field in EVERYTHING_FIELDS},
        )
        for record in master_records
    ]
    queue = read_csv(QUEUE)
    new_work_queue = read_csv(NEW_WORK_QUEUE)
    veritas_products = read_csv(VERITAS_PRODUCTS)
    validate_work_family_coverage(master_records)
    validate_veritas_inventory(veritas_products, master_records)
    validate_new_work_queue(new_work_queue, veritas_products)
    veritas_mapping_decisions = read_csv(VERITAS_MAPPING_DECISIONS)
    product_relationships = validate_product_relationships(master_records, veritas_products)
    validate_primary_relationship_coverage(master_records, product_relationships)
    series_compilations = validate_series_compilations(master_records, veritas_products)
    hayhouse_products = read_csv(HAYHOUSE_PRODUCTS)
    audible_products = read_csv(AUDIBLE_PRODUCTS)
    intl_queue = read_csv(INTL_QUEUE)
    manual_candidates = read_csv(MANUAL_CANDIDATES)
    manual_leads = read_csv(MANUAL_LEADS)

    # Pending-promotion candidates are surfaced for owner review by default
    # (opt out locally with --no-include-pending).
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

    # Products with a matched master title are represented by the existing
    # master item. Only unmatched official products become Everything candidates.
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
        # Spanish-language Audible listings are displayed with international leads.
        if product["official_title"] in ("Disolver el ego", "El nivel más alto de iluminación"):
            intl_items.append({
                "publisher": "Audible",
                "market": "Spanish",
                "candidate_title": product["official_title"],
                # Audiobook editions of book-typed works: the edition model
                # (EDITION_MODEL_PROPOSAL.md) keeps item_type=book and puts
                # the carrier in format; the retired medium value "audio"
                # must not be used as an item_type.
                "item_type": "book",
                "format": "digital",
                "language": "Spanish",
                "source_url": product["audible_url"],
                "match_status": product["mapping_status"],
                "match_notes": product["review_notes"],
                "review_notes": "",
            })
            continue

        if product["mapping_status"] != "unreviewed_official_product":
            continue
        items.append(everything_record(
            RECORD_TYPE_CANDIDATE_AUDIBLE,
            title=product["official_title"],
            format="audio",
            source_url_audible=product["audible_url"],
            notes="Official Audible product; unreviewed for deduplication and metadata.",
        ))

    intl_items.extend(intl_queue)
    review_overview = [
        {
            "review_sheet": "Master Candidates",
            "record_count": len(manual_candidates),
            "purpose": "Evidence-backed official candidates awaiting an explicit master-promotion decision.",
            "source_file": str(MANUAL_CANDIDATES),
            "current_state": "reviewed_candidate / not_promoted",
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
            "source_file": str(VERITAS_MAPPING_DECISIONS),
            "current_state": "approved mapping decision",
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
        OUT_PUBLISHERS: json_text(PUBLISHERS),
        OUT_META: json_text({
            "master_items": len(items),
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
            "approved_publishers": len(PUBLISHERS),
            "original_source_rows": len(migration_review),
        }),
    }
    return CatalogueBuild(
        items=items,
        product_relationships=product_relationships,
        series_compilations=series_compilations,
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
        help="verify committed Pages catalogue files match their declared inputs; do not write files",
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
            print("Pages catalogue outputs are stale relative to their declared inputs:")
            for path in stale:
                print(f"  - {path}")
            print("Run python build_catalogue_pages.py after reviewing the input change.")
            return 1
        print(f"Pages catalogue outputs match their inputs ({len(build.items)} Everything rows).")
        return 0

    write_outputs(build.outputs)
    print(f"Wrote {OUT_MASTER} ({len(build.items)} rows), {OUT_PUBLISHERS}, and {OUT_META}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
