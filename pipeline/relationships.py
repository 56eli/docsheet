#!/usr/bin/env python3
"""Product relationship and review overview generators."""

from __future__ import annotations

import re
from pathlib import Path

from _common import read_csv
from pipeline.helpers import require_columns

DATA_DIR = Path("data")
PRODUCT_RELATIONSHIPS = DATA_DIR / "product_relationships.csv"
SERIES_COMPILATIONS = DATA_DIR / "series_compilation_relationships.csv"
MANUAL_CANDIDATES = DATA_DIR / "manual_master_candidates.csv"
WORK_FAMILIES = DATA_DIR / "work_families.csv"

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
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

PRIMARY_RELATIONSHIP_NOTE = "Master primary Veritas URL matches the official product inventory."
PRIMARY_RELATIONSHIP_NOTES = {
    "candidate:edition-": "Promoted edition row (owner-approved 2026-08-03); master primary Veritas URL matches the official product inventory.",
    "candidate:manual-veritas-satsang-": "Owner-approved Satsang new-work promotion (2026-08-03); master primary Veritas URL matches the official product inventory.",
    "candidate:manual-": "Owner-approved promotion (2026-08-03); master primary Veritas URL matches the official product inventory.",
}


def primary_relationship_note(item: dict[str, str]) -> str:
    """Choose the evidence note for a derived primary relationship from its master provenance."""
    candidate_key = item.get("candidate_key", "")
    for prefix, note in PRIMARY_RELATIONSHIP_NOTES.items():
        if candidate_key.startswith(prefix):
            return note
    return PRIMARY_RELATIONSHIP_NOTE


def derive_primary_relationships(
    master_items: list[dict[str, str]],
    veritas_products: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Derive primary item→product relationships from the master's own URLs."""
    veritas_by_url = {product["official_product_url"]: product for product in veritas_products}
    derived: list[dict[str, str]] = []
    for item in master_items:
        url = item.get("source_url_veritas", "").strip()
        if not url or url not in veritas_by_url:
            continue
        product = veritas_by_url[url]
        product_id = product["veritas_product_id"]
        derived.append({
            "relationship_id": f"rel-veritas-{product_id}-{item['uuid']}",
            "master_uuid": item["uuid"],
            "raw_row_number": item.get("raw_row_number", "") or item.get("candidate_key", ""),
            "source_name": "veritas",
            "source_product_id": product_id,
            "official_product_url": url,
            "official_product_title": product["official_title"],
            "relationship_type": "primary_product_for_item_part",
            "review_status": "reviewed",
            "reviewed_on": "2026-08-03",
            "evidence_url": url,
            "evidence_note": primary_relationship_note(item),
            "master_catalog_code": item.get("catalog_code", ""),
            "master_title": item.get("title", ""),
            "master_item_type": item.get("item_type", ""),
            "master_year": item.get("year", ""),
            "source_product_published_date": product.get("published_date", ""),
            "source_product_mapping_status": product.get("mapping_status", ""),
        })
    return derived


def validate_product_relationships(
    master_items: list[dict[str, str]],
    veritas_products: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Validate and enrich reviewed master-to-product relationships."""
    if veritas_products is None:
        veritas_products = read_csv(DATA_DIR / "veritas_official_products.csv") if (DATA_DIR / "veritas_official_products.csv").exists() else []

    require_columns(PRODUCT_RELATIONSHIPS, RELATIONSHIP_REQUIRED_COLUMNS)
    explicit_rows = read_csv(PRODUCT_RELATIONSHIPS)
    master_by_uuid = {item["uuid"]: item for item in master_items}
    veritas_by_id = {product["veritas_product_id"]: product for product in veritas_products}
    seen_ids: set[str] = set()
    enriched: list[dict[str, str]] = []

    for line_number, relation in enumerate(explicit_rows, start=2):
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
                f"{PRODUCT_RELATIONSHIPS}:{line_number} has unsupported source_name {source_name!r}"
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
        if review_status == "reviewed" and not ISO_DATE_PATTERN.fullmatch(reviewed_on):
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
