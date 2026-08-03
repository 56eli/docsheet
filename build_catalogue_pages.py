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
INTL_QUEUE = Path("data/international_discovery_queue.csv")
VERITAS_PRODUCTS = Path("data/veritas_official_products.csv")
HAYHOUSE_PRODUCTS = Path("data/hayhouse_official_products.csv")
AUDIBLE_PRODUCTS = Path("data/audible_official_products.csv")
PRODUCT_RELATIONSHIPS = Path("data/product_relationships.csv")
OUT_MASTER = Path("docs/master.json")
OUT_VERITAS_PRODUCTS = Path("docs/veritas-products.json")
OUT_PRODUCT_RELATIONSHIPS = Path("docs/product-relationships.json")
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
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class CatalogueBuild:
    """In-memory Pages artifacts shared by normal builds and reconciliation."""

    items: list[dict[str, str]]
    product_relationships: list[dict[str, str]]
    outputs: dict[Path, str]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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
                f"{PRODUCT_RELATIONSHIPS}:{line_number} references an unknown master UUID: {master_uuid!r}"
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
        if relation["raw_row_number"] != master["raw_row_number"]:
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


def json_text(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def build_catalogue(master_items: list[dict[str, str]] | None = None) -> CatalogueBuild:
    """Prepare catalogue Pages files in memory.

    ``master_items`` exists for read-only reconciliation: it lets callers
    project the Pages site from a ledger-derived master without overwriting the
    committed master draft first. Normal builds read ``MASTER`` unchanged.
    """
    items = list(master_items) if master_items is not None else read_csv(MASTER)
    migrated_items = len(items)
    master_records = list(items)
    queue = read_csv(QUEUE)
    veritas_products = read_csv(VERITAS_PRODUCTS)
    product_relationships = validate_product_relationships(master_records, veritas_products)
    hayhouse_products = read_csv(HAYHOUSE_PRODUCTS)
    audible_products = read_csv(AUDIBLE_PRODUCTS)
    intl_queue = read_csv(INTL_QUEUE)
    intl_items: list[dict[str, str]] = []

    for candidate in queue:
        items.append({
            "uuid": "",
            "catalog_code": "",
            "legacy_tempid": "",
            "title": candidate["candidate_title"],
            "title_source": "",
            "item_type": candidate["item_type"],
            "series": candidate["series"],
            "year": candidate["year"],
            "month": "",
            "format": candidate["format"],
            "format_detail": "",
            "owned": "",
            "location_physical": "",
            "location_digital": "",
            "location_streaming": "",
            "source_url_veritas": "",
            "source_url_hay_house": "",
            "source_url_nightingale_conant": candidate["source_url_nightingale_conant"],
            "source_url_audible": candidate["source_url_audible"],
            "reference_url_1": "",
            "reference_url_2": "",
            "notes": candidate["match_notes"],
            "raw_row_number": "",
        })

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
        items.append({
            "uuid": "",
            "catalog_code": "",
            "legacy_tempid": "",
            "title": product["official_title"],
            "title_source": "",
            "item_type": "",
            "series": "",
            "year": product["published_date"][:4],
            "month": "",
            "format": "",
            "format_detail": "",
            "owned": "",
            "location_physical": "",
            "location_digital": "",
            "location_streaming": "",
            "source_url_veritas": product["official_product_url"],
            "source_url_hay_house": "",
            "source_url_nightingale_conant": "",
            "source_url_audible": "",
            "reference_url_1": "",
            "reference_url_2": "",
            "notes": notes,
            "raw_row_number": "",
        })

    for product in hayhouse_products:
        if product["mapping_status"] != "unreviewed_official_product":
            continue
        items.append({
            "uuid": "",
            "catalog_code": "",
            "legacy_tempid": "",
            "title": product["official_title"],
            "title_source": "",
            "item_type": "",
            "series": "",
            "year": "",
            "month": "",
            "format": product.get("format", ""),
            "format_detail": "",
            "owned": "",
            "location_physical": "",
            "location_digital": "",
            "location_streaming": "",
            "source_url_veritas": "",
            "source_url_hay_house": product["official_product_url"],
            "source_url_nightingale_conant": "",
            "source_url_audible": "",
            "reference_url_1": "",
            "reference_url_2": "",
            "notes": "Official Hay House product; unreviewed for deduplication and metadata.",
            "raw_row_number": "",
        })

    for product in audible_products:
        # Spanish-language Audible listings are displayed with international leads.
        if product["official_title"] in ("Disolver el ego", "El nivel más alto de iluminación"):
            intl_items.append({
                "publisher": "Audible",
                "market": "Spanish",
                "candidate_title": product["official_title"],
                "item_type": "audio",
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
        items.append({
            "uuid": "",
            "catalog_code": "",
            "legacy_tempid": "",
            "title": product["official_title"],
            "title_source": "",
            "item_type": "",
            "series": "",
            "year": "",
            "month": "",
            "format": "audio",
            "format_detail": "",
            "owned": "",
            "location_physical": "",
            "location_digital": "",
            "location_streaming": "",
            "source_url_veritas": "",
            "source_url_hay_house": "",
            "source_url_nightingale_conant": "",
            "source_url_audible": product["audible_url"],
            "reference_url_1": "",
            "reference_url_2": "",
            "notes": "Official Audible product; unreviewed for deduplication and metadata.",
            "raw_row_number": "",
        })

    intl_items.extend(intl_queue)
    outputs = {
        OUT_MASTER: json_text(items),
        OUT_VERITAS_PRODUCTS: json_text(veritas_products),
        OUT_PRODUCT_RELATIONSHIPS: json_text(product_relationships),
        OUT_HAYHOUSE_PRODUCTS: json_text(hayhouse_products),
        OUT_AUDIBLE_PRODUCTS: json_text(audible_products),
        OUT_INTERNATIONAL: json_text(intl_items),
        OUT_PUBLISHERS: json_text(PUBLISHERS),
        OUT_META: json_text({
            "master_items": len(items),
            "migrated_items": migrated_items,
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
            "hayhouse_official_products": len(hayhouse_products),
            "audible_official_products": len(audible_products),
            "approved_publishers": len(PUBLISHERS),
            "original_source_rows": 374,
        }),
    }
    return CatalogueBuild(
        items=items,
        product_relationships=product_relationships,
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
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    build = build_catalogue()

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
