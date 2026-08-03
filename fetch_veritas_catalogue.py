#!/usr/bin/env python3
"""Fetch and map every published Veritas product through its public WP API.

Creates a complete official-product inventory and a conservative normalized-title
match against the local research-master draft. It never imports a product into
the master automatically.
"""
from __future__ import annotations
import csv, html, json, re
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

API = "https://veritaspub.com/wp-json/wp/v2/product"
MASTER = Path("data/research_master_draft.csv")
OUT = Path("data/veritas_official_products.csv")


def norm(value: str) -> str:
    value = html.unescape(value).lower()
    value = re.sub(r"\s*\([^)]*\)", "", value)
    return re.sub(r"[^a-z0-9]+", "", value)


def get_page(page: int) -> list[dict]:
    query = urlencode({"per_page": 100, "page": page, "_fields": "id,date,link,title,class_list"})
    request = Request(f"{API}?{query}", headers={"User-Agent": "docsheet-catalogue-research/1.0"})
    try:
        with urlopen(request, timeout=60) as response:  # nosec B310: fixed HTTPS API endpoint
            return json.load(response)
    except HTTPError as error:
        # WordPress returns 400 rather than an empty array beyond the final page.
        if error.code == 400 and page > 1:
            return []
        raise


def category(classes: list[str]) -> str:
    categories = [item.removeprefix("product_cat_") for item in classes if item.startswith("product_cat_")]
    return "; ".join(categories)


def main() -> None:
    with MASTER.open(encoding="utf-8", newline="") as handle:
        master = list(csv.DictReader(handle))
    index: dict[str, list[dict[str, str]]] = {}
    for row in master:
        index.setdefault(norm(row["title"]), []).append(row)

    products, page = [], 1
    while True:
        batch = get_page(page)
        if not batch:
            break
        products.extend(batch)
        page += 1

    rows = []
    for product in products:
        title = html.unescape(product["title"]["rendered"])
        matches = index.get(norm(title), [])
        rows.append({
            "veritas_product_id": str(product["id"]),
            "official_title": title,
            "official_product_url": product["link"],
            "published_date": product["date"][:10],
            "official_categories": category(product.get("class_list", [])),
            "normalized_title_match_count": str(len(matches)),
            "matched_master_uuids": "; ".join(item["uuid"] for item in matches),
            "matched_master_titles": " | ".join(item["title"] for item in matches),
            "mapping_status": "matched_by_normalized_title" if matches else "unreviewed_official_product",
            "review_notes": "",
        })
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUT} ({len(rows)} official Veritas products)")


if __name__ == "__main__":
    main()
