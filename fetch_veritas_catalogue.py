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


MONTHS = {
    "jan": "01", "january": "01", "feb": "02", "february": "02",
    "mar": "03", "march": "03", "apr": "04", "april": "04",
    "may": "05", "jun": "06", "june": "06", "jul": "07", "july": "07",
    "aug": "08", "august": "08", "sep": "09", "sept": "09", "september": "09",
    "oct": "10", "october": "10", "nov": "11", "november": "11",
    "dec": "12", "december": "12",
}


def is_satsang(value: str) -> bool:
    return "satsang series" in html.unescape(value).lower()


def satsang_date_key(value: str) -> str | None:
    """Return YYYY-MM for a dated Satsang title, preserving date identity."""
    match = re.search(
        r"\b(" + "|".join(MONTHS) + r")\.?\s+(20\d{2})\b",
        html.unescape(value).lower(),
    )
    if not match:
        return None
    return f"{match.group(2)}-{MONTHS[match.group(1)]}"


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
    satsang_index: dict[str, list[dict[str, str]]] = {}
    for row in master:
        index.setdefault(norm(row["title"]), []).append(row)
        if is_satsang(row["title"]):
            date_key = satsang_date_key(row["title"])
            if date_key:
                satsang_index.setdefault(date_key, []).append(row)

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
        if is_satsang(title):
            date_key = satsang_date_key(title)
            matches = satsang_index.get(date_key, []) if date_key else []
            mapping_status = "matched_by_date" if matches else "unmatched_official_product"
            review_notes = (
                "Date-specific Satsang mapping; Month/Year must match exactly."
                if matches
                else "No date-specific Satsang master item; retained as official inventory only."
            )
        else:
            matches = index.get(norm(title), [])
            mapping_status = "matched_by_normalized_title" if matches else "unreviewed_official_product"
            review_notes = ""
        rows.append({
            "veritas_product_id": str(product["id"]),
            "official_title": title,
            "official_product_url": product["link"],
            "published_date": product["date"][:10],
            "official_categories": category(product.get("class_list", [])),
            "normalized_title_match_count": str(len(matches)),
            "matched_master_uuids": "; ".join(item["uuid"] for item in matches),
            "matched_master_titles": " | ".join(item["title"] for item in matches),
            "mapping_status": mapping_status,
            "review_notes": review_notes,
        })
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUT} ({len(rows)} official Veritas products)")


if __name__ == "__main__":
    main()
