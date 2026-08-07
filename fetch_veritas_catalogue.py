#!/usr/bin/env python3
"""Fetch and map the public Veritas catalogue without overwriting review decisions.

The public WordPress API supplies the raw commercial inventory. Deterministic
matching derives exact primary-source and date-aware matches; reviewed
non-primary dispositions are then reapplied from a product-ID keyed decision
file. The script never imports a commercial product into the research master.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import time
from json import JSONDecodeError
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from _common import ISO_DATE, read_csv, render_csv

API = "https://veritaspub.com/wp-json/wp/v2/product"
API_CAT = "https://veritaspub.com/wp-json/wp/v2/product_cat"
MASTER = Path("data/research_master_draft.csv")
OUT = Path("data/veritas_official_products.csv")
DECISIONS = Path("data/veritas_mapping_decisions.csv")

OUTPUT_FIELDS = [
    "veritas_product_id", "official_title", "official_product_url", "published_date",
    "official_categories", "normalized_title_match_count", "matched_master_uuids",
    "matched_master_titles", "mapping_status", "review_notes",
]
DECISION_REQUIRED_COLUMNS = {
    "veritas_product_id", "mapping_status", "matched_master_uuids",
    "matched_master_titles", "review_notes", "review_status", "reviewed_on",
    "decision_reason",
}
DECISION_STATUSES = {
    "unique_item", "compilation_or_new_edition", "excluded_related_material",
    "matched_by_title", "matched_by_normalized_title",
}
MAX_PAGE_ATTEMPTS = 4


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


def title_date_key(value: str) -> str | None:
    """Return YYYY-MM when a title carries an explicit Month/Year."""
    match = re.search(
        r"\b(" + "|".join(MONTHS) + r")\.?\s+(20\d{2})\b",
        html.unescape(value).lower(),
    )
    if not match:
        return None
    return f"{match.group(2)}-{MONTHS[match.group(1)]}"


def satsang_date_key(value: str) -> str | None:
    """Backward-compatible name for Satsang-specific date matching."""
    return title_date_key(value)


def get_page(page: int, endpoint: str = API) -> list[dict]:
    """Fetch one API page with retries for transient HTML/empty API responses."""
    if endpoint == API:
        fields = "id,date,link,title,product_cat"
    else:
        fields = "id,name"
    query = urlencode({"per_page": 100, "page": page, "_fields": fields})
    request = Request(
        f"{endpoint}?{query}",
        headers={
            "User-Agent": "docsheet-catalogue-research/1.0 (+https://github.com/56eli/docsheet)",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    last_error: Exception | None = None
    for attempt in range(1, MAX_PAGE_ATTEMPTS + 1):
        try:
            with urlopen(request, timeout=60) as response:  # nosec B310: fixed HTTPS API endpoint
                body = response.read()
                try:
                    payload = json.loads(body)
                except JSONDecodeError as error:
                    preview = body[:160].decode("utf-8", errors="replace").replace("\n", " ")
                    content_type = response.headers.get("Content-Type", "unknown")
                    last_error = RuntimeError(
                        f"Veritas API returned non-JSON for page {page} "
                        f"(Content-Type: {content_type}; preview: {preview!r})"
                    )
                else:
                    if not isinstance(payload, list):
                        last_error = RuntimeError(
                            f"Veritas API returned a {type(payload).__name__}, not a product list, for page {page}"
                        )
                    else:
                        return payload
        except HTTPError as error:
            # WordPress returns 400 rather than an empty array beyond the final page.
            if error.code == 400 and page > 1:
                return []
            last_error = error
        except URLError as error:
            last_error = error

        if attempt < MAX_PAGE_ATTEMPTS:
            time.sleep(attempt)

    raise RuntimeError(
        f"Veritas API page {page} failed after {MAX_PAGE_ATTEMPTS} attempts: {last_error}"
    )


def category_names(product: dict, term_names: dict[str, str]) -> str:
    """Resolve a product's ``product_cat`` term IDs to display names.

    IDs are appended to ``term_names`` on the fly when the taxonomy endpoint
    has never returned them; an ID that cannot be resolved renders as
    ``unresolved-category-<id>`` so the taxonomic signal is lost neither
    silently nor destructively (the series mapper routes such values to the
    review queue).
    """
    categories: list[str] = []
    for term_id in product.get("product_cat", []) or []:
        key = str(term_id)
        name = term_names.get(key)
        if name is None:
            name = f"unresolved-category-{key}"
        categories.append(name)
    return "; ".join(categories)


def fetch_products() -> list[dict]:
    products: list[dict] = []
    page = 1
    while True:
        batch = get_page(page)
        if not batch:
            return products
        products.extend(batch)
        page += 1


def fetch_category_names() -> dict[str, str]:
    """Fetch the official ``product_cat`` taxonomy as ``{term_id: name}``.

    Category *names* (not slugs) are the review surface used by the
    Category Dominance Policy, so they are what the inventory persists.
    """
    names: dict[str, str] = {}
    page = 1
    while True:
        batch = get_page(page, endpoint=API_CAT)
        if not batch:
            return names
        for term in batch:
            names[str(term["id"])] = html.unescape(term["name"])
        page += 1


def build_inventory_rows(
    products: list[dict],
    master: list[dict[str, str]],
    term_names: dict[str, str],
) -> list[dict[str, str]]:
    """Build deterministic source/title/date matches from live products."""
    index: dict[str, list[dict[str, str]]] = {}
    source_url_index: dict[str, list[dict[str, str]]] = {}
    dated_index: dict[str, dict[str, list[dict[str, str]]]] = {}
    satsang_index: dict[str, list[dict[str, str]]] = {}
    for row in master:
        normalized_title = norm(row["title"])
        index.setdefault(normalized_title, []).append(row)
        if row.get("source_url_veritas"):
            source_url_index.setdefault(row["source_url_veritas"], []).append(row)
        # Date keys come from the verbatim raw title (older title_source column
        # was byte-identical to legacy_title on every date-bearing row).
        dated_title = row.get("legacy_title") or row["title"]
        date_key = title_date_key(dated_title)
        if date_key:
            dated_index.setdefault(normalized_title, {}).setdefault(date_key, []).append(row)
        if is_satsang(row["title"]):
            satsang_key = satsang_date_key(row["title"])
            if satsang_key:
                satsang_index.setdefault(satsang_key, []).append(row)

    rows: list[dict[str, str]] = []
    for product in products:
        title = html.unescape(product["title"]["rendered"])
        source_matches = source_url_index.get(product["link"], [])
        if source_matches:
            matches = source_matches
            mapping_status = "matched_by_primary_source"
            review_notes = "Exact master primary Veritas URL match."
        elif is_satsang(title):
            date_key = satsang_date_key(title)
            matches = satsang_index.get(date_key, []) if date_key else []
            mapping_status = "matched_by_date" if matches else "unmatched_official_product"
            review_notes = (
                "Date-specific Satsang mapping; Month/Year must match exactly."
                if matches
                else "No date-specific Satsang master item; retained as official inventory only."
            )
        else:
            normalized_title = norm(title)
            matches = index.get(normalized_title, [])
            product_date = title_date_key(title)
            candidate_dates = dated_index.get(normalized_title, {})
            # Preserve dates only when one normalized title has multiple dated
            # master groups (for example, A Review of the Work in 2006/2007).
            if product_date and len(candidate_dates) > 1:
                matches = candidate_dates.get(product_date, [])
                mapping_status = "matched_by_date" if matches else "unmatched_official_product"
                review_notes = (
                    "Date-aware mapping; Month/Year must match exactly."
                    if matches
                    else "No date-specific master item; retained as official inventory only."
                )
            else:
                mapping_status = "matched_by_normalized_title" if matches else "unreviewed_official_product"
                review_notes = ""
        rows.append({
            "veritas_product_id": str(product["id"]),
            "official_title": title,
            "official_product_url": product["link"],
            "published_date": product["date"][:10],
            "official_categories": category_names(product, term_names),
            "normalized_title_match_count": str(len(matches)),
            "matched_master_uuids": "; ".join(item["uuid"] for item in matches),
            "matched_master_titles": " | ".join(item["title"] for item in matches),
            "mapping_status": mapping_status,
            "review_notes": review_notes,
        })
    return rows


def split_uuids(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def apply_mapping_decisions(
    inventory: list[dict[str, str]],
    master: list[dict[str, str]],
) -> int:
    """Reapply reviewed product-ID decisions after live deterministic matching."""
    with DECISIONS.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = DECISION_REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"{DECISIONS} is missing required columns: {', '.join(sorted(missing))}"
            )
        decisions = list(reader)

    inventory_by_id = {row["veritas_product_id"]: row for row in inventory}
    master_by_uuid = {row["uuid"]: row for row in master}
    seen_ids: set[str] = set()
    for line_number, decision in enumerate(decisions, start=2):
        product_id = decision["veritas_product_id"].strip()
        status = decision["mapping_status"].strip()
        uuids = split_uuids(decision["matched_master_uuids"])

        if not product_id or product_id in seen_ids or product_id not in inventory_by_id:
            raise ValueError(
                f"{DECISIONS}:{line_number} must reference one unique current official product ID"
            )
        if status not in DECISION_STATUSES:
            raise ValueError(
                f"{DECISIONS}:{line_number} uses unsupported reviewed mapping_status {status!r}"
            )
        if decision["review_status"].strip() != "approved" or not ISO_DATE.fullmatch(decision["reviewed_on"].strip()):
            raise ValueError(
                f"{DECISIONS}:{line_number} needs approved review_status and an ISO reviewed_on date"
            )
        if not decision["decision_reason"].strip():
            raise ValueError(f"{DECISIONS}:{line_number} needs a decision_reason")
        if any(item_uuid not in master_by_uuid for item_uuid in uuids):
            raise ValueError(f"{DECISIONS}:{line_number} references an unknown master ID")

        expected_titles = " | ".join(master_by_uuid[item_uuid]["title"] for item_uuid in uuids)
        if decision["matched_master_titles"] != expected_titles:
            raise ValueError(
                f"{DECISIONS}:{line_number} matched_master_titles must match the referenced master IDs"
            )
        if status in {"matched_by_title", "matched_by_normalized_title"} and not uuids:
            raise ValueError(f"{DECISIONS}:{line_number} match statuses require master IDs")
        if status not in {"matched_by_title", "matched_by_normalized_title"} and uuids:
            raise ValueError(f"{DECISIONS}:{line_number} non-match statuses cannot contain master IDs")

        target = inventory_by_id[product_id]
        target["mapping_status"] = status
        target["matched_master_uuids"] = "; ".join(uuids)
        target["matched_master_titles"] = expected_titles
        target["normalized_title_match_count"] = str(len(uuids))
        target["review_notes"] = decision["review_notes"]
        seen_ids.add(product_id)
    return len(decisions)


def csv_text(rows: list[dict[str, str]]) -> str:
    return render_csv(OUTPUT_FIELDS, rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=OUT,
        help=f"write the reviewed inventory to this path (default: {OUT})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fetch, map, and verify the committed inventory matches; do not write files",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.check and args.output != OUT:
        print("--check cannot be combined with a custom --output", file=sys.stderr)
        return 2
    try:
        master = read_csv(MASTER)
        inventory = build_inventory_rows(fetch_products(), master, fetch_category_names())
        decisions_applied = apply_mapping_decisions(inventory, master)
        output = csv_text(inventory)

        if args.check:
            if OUT.exists() and OUT.read_text(encoding="utf-8") == output:
                print(f"{OUT} matches the live inventory with {decisions_applied} reviewed decisions applied.")
                return 0
            print(
                f"{OUT} differs from the live reviewed inventory; write a candidate file and review its diff.",
                file=sys.stderr,
            )
            return 1

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"Wrote {args.output} ({len(inventory)} official Veritas products)")
        print(f"Applied {decisions_applied} reviewed mapping decisions from {DECISIONS}")
        return 0
    except Exception as exc:  # noqa: BLE001 — workflow must fail loud and preserve current inventory
        print(f"[fetch_veritas_catalogue] ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
