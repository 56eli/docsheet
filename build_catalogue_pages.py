#!/usr/bin/env python3
"""Build GitHub Pages datasets for the three catalogue tabs.

Page 1 combines the clean migrated draft with discovered-but-unreviewed official
candidates. Page 2 lists approved publishers. Page 3 continues to load the
original pipeline-generated docs/data.json without modification.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

MASTER = Path("data/research_master_draft.csv")
QUEUE = Path("data/official_discovery_queue.csv")
INTL_QUEUE = Path("data/international_discovery_queue.csv")
VERITAS_PRODUCTS = Path("data/veritas_official_products.csv")
HAYHOUSE_PRODUCTS = Path("data/hayhouse_official_products.csv")
AUDIBLE_PRODUCTS = Path("data/audible_official_products.csv")
OUT_MASTER = Path("docs/master.json")
OUT_VERITAS_PRODUCTS = Path("docs/veritas-products.json")
OUT_HAYHOUSE_PRODUCTS = Path("docs/hayhouse-products.json")
OUT_AUDIBLE_PRODUCTS = Path("docs/audible-products.json")
OUT_INTERNATIONAL = Path("docs/international-products.json")
OUT_PUBLISHERS = Path("docs/publishers.json")
OUT_META = Path("docs/catalogue-meta.json")

PUBLISHERS = [
    {"publisher": "Veritas Publishing", "official_catalogue_url": "https://veritaspub.com/hawkins-products/", "status": "approved", "role": "Primary creator-affiliated publisher / catalogue"},
    {"publisher": "Hay House", "official_catalogue_url": "https://www.hayhouse.com/authorbio/david-r-hawkins-m-d-ph-d", "status": "approved", "role": "Book publisher catalogue"},
    {"publisher": "Nightingale-Conant", "official_catalogue_url": "https://www.nightingale.com/pages/david-hawkins", "status": "approved", "role": "Audio-program publisher catalogue"},
    {"publisher": "Audible", "official_catalogue_url": "https://www.audible.com/author/David-R-Hawkins/B001H6MLOO", "status": "approved", "role": "Official platform catalogue; not a publisher"},
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    items = read_csv(MASTER)
    queue = read_csv(QUEUE)
    veritas_products = read_csv(VERITAS_PRODUCTS)
    hayhouse_products = read_csv(HAYHOUSE_PRODUCTS)
    audible_products = read_csv(AUDIBLE_PRODUCTS)
    intl_queue = read_csv(INTL_QUEUE)
    
    # We will build a separate list for the international tab
    intl_items = []
    
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
    # master item. Only unmatched official products become Page 1 candidates.
    for product in veritas_products:
        if product["mapping_status"] not in ("unreviewed_official_product", "unique_item", "compilation_or_new_edition"):
            continue
        notes = "Official Veritas product; unreviewed for deduplication."
        if product["mapping_status"] == "unique_item":
            notes = "Official Veritas product; identified as a unique original item."
        elif product["mapping_status"] == "compilation_or_new_edition":
            notes = "Official Veritas product; identified as a compilation or later edition."
            
        items.append({
            "uuid": "", "catalog_code": "", "legacy_tempid": "",
            "title": product["official_title"], "title_source": "",
            "item_type": "", "series": "", "year": product["published_date"][:4],
            "month": "", "format": "", "format_detail": "", "owned": "",
            "location_physical": "", "location_digital": "", "location_streaming": "",
            "source_url_veritas": product["official_product_url"],
            "source_url_hay_house": "", "source_url_nightingale_conant": "", "source_url_audible": "",
            "reference_url_1": "", "reference_url_2": "",
            "notes": notes,
            "raw_row_number": "",
        })
    for product in hayhouse_products:
        if product["mapping_status"] != "unreviewed_official_product":
            continue
        items.append({
            "uuid": "", "catalog_code": "", "legacy_tempid": "",
            "title": product["official_title"], "title_source": "",
            "item_type": "", "series": "", "year": "",
            "month": "", "format": product.get("format", ""), "format_detail": "", "owned": "",
            "location_physical": "", "location_digital": "", "location_streaming": "",
            "source_url_veritas": "", "source_url_hay_house": product["official_product_url"],
            "source_url_nightingale_conant": "", "source_url_audible": "",
            "reference_url_1": "", "reference_url_2": "",
            "notes": "Official Hay House product; unreviewed for deduplication and metadata.",
            "raw_row_number": "",
        })
    for product in audible_products:
        # Move Spanish/Non-English to international tab
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
                "review_notes": ""
            })
            continue

        if product["mapping_status"] != "unreviewed_official_product":
            continue
        items.append({
            "uuid": "", "catalog_code": "", "legacy_tempid": "",
            "title": product["official_title"], "title_source": "",
            "item_type": "", "series": "", "year": "",
            "month": "", "format": "audio", "format_detail": "", "owned": "",
            "location_physical": "", "location_digital": "", "location_streaming": "",
            "source_url_veritas": "", "source_url_hay_house": "",
            "source_url_nightingale_conant": "", "source_url_audible": product["audible_url"],
            "reference_url_1": "", "reference_url_2": "",
            "notes": "Official Audible product; unreviewed for deduplication and metadata.",
            "raw_row_number": "",
        })
    for row in intl_queue:
        # Include all rows from the international queue
        intl_items.append(row)

    OUT_MASTER.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_VERITAS_PRODUCTS.write_text(json.dumps(veritas_products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_HAYHOUSE_PRODUCTS.write_text(json.dumps(hayhouse_products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_AUDIBLE_PRODUCTS.write_text(json.dumps(audible_products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_INTERNATIONAL.write_text(json.dumps(intl_items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_PUBLISHERS.write_text(json.dumps(PUBLISHERS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_META.write_text(json.dumps({
        "master_items": len(items),
        "migrated_items": len(read_csv(MASTER)),
        "implemented_unreviewed": len(queue) + sum(p["mapping_status"] in ("unreviewed_official_product", "unique_item", "compilation_or_new_edition") for p in veritas_products) + sum(p["mapping_status"] == "unreviewed_official_product" for p in audible_products) + sum(p["mapping_status"] == "unreviewed_official_product" for p in hayhouse_products),
        "veritas_official_products": len(veritas_products),
        "hayhouse_official_products": len(hayhouse_products),
        "audible_official_products": len(audible_products),
        "approved_publishers": len(PUBLISHERS),
        "original_source_rows": 374,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MASTER} ({len(items)} rows), {OUT_PUBLISHERS}, and {OUT_META}")


if __name__ == "__main__":
    main()
