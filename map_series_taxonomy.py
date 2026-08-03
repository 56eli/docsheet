#!/usr/bin/env python3
"""Map the official Veritas product taxonomy to catalogue ``series`` proposals.

Implements the owner-approved rules in ``CATEGORY_DOMINANCE_POLICY.md`` as a
reviewable input/output layer:

* reads the reviewed inventory ``data/veritas_official_products.csv`` (which
  now persists every publisher category in ``official_categories``);
* chooses one dominant category per product by the fixed precedence below;
* maps the dominant category to the human-readable master ``series``
  vocabulary without ever touching ``item_type`` (policy: category rules may
  set ``series`` but must not silently change content class);
* writes ``data/series_category_mapping.csv`` (one proposal per matched
  official product) plus ``data/series_taxonomy_review_queue.csv`` (conflicts
  and unrecognized categories the policy routes to human review).

Review overlay: on regeneration, hand-set ``review_status`` /
``reviewed_on`` / ``review_notes`` values in the committed mapping CSV are
preserved, mirroring the ``veritas_mapping_decisions.csv`` overlay pattern.
Only ``review_status = approved`` rows may later be applied to the ledger
series by a separate, documented step; this script never writes master or
ledger files itself.

Unmatched official products (no ``matched_master_uuids``) are out of scope:
their lane is ``data/veritas_mapping_decisions.csv`` / the candidate views.
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from pathlib import Path

INVENTORY = Path("data/veritas_official_products.csv")
MASTER = Path("data/research_master_draft.csv")
MAPPING = Path("data/series_category_mapping.csv")
QUEUE = Path("data/series_taxonomy_review_queue.csv")

MAPPING_FIELDS = [
    "veritas_product_id", "official_title", "matched_master_uuids",
    "official_categories", "dominant_category", "dominance_rule",
    "mapped_series", "review_status", "reviewed_on", "review_notes",
]
QUEUE_FIELDS = MAPPING_FIELDS + ["queue_reason"]
REVIEWED_STATUSES = {"approved", "rejected"}
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# --- Policy encoding (CATEGORY_DOMINANCE_POLICY.md) ----------------------
# Category display names exactly as persisted in the inventory.
CAT_NEW_PRODUCTS = "* * New Products * *"
CAT_LECTURE_HIGHLIGHTS = "Lecture Highlights"
CAT_HIGHLIGHTS = "Highlights"
CAT_SATSANG = "Satsang"
CAT_SIX_BOOK = "The Six Book 2002 Transcription Series"
CAT_ON_THE_ROAD = "On the Road - Talk Series"
CAT_ON_THE_ROAD_ALT = "* On the Road \u2013 Talk Series"
CAT_OFFICE = "Archival Office Visit Series"
CAT_CARD_DECKS = "Card Decks"

GROUP_SATSANG = {
    CAT_SATSANG, "Satsang Series and Question & Answer Sessions",
    "Satsang 2006", "Satsang 2007", "Satsang 2008", "Satsang 2009",
    "Satsang 2010", "Satsang 2011",
}
GROUP_LECTURE_HIGHLIGHTS = {CAT_LECTURE_HIGHLIGHTS, CAT_HIGHLIGHTS}
GROUP_ON_THE_ROAD = {CAT_ON_THE_ROAD, CAT_ON_THE_ROAD_ALT}

# Annual lecture-series categories (children of "Lectures Series") mapped to
# the existing master series vocabulary.
ANNUAL_SERIES = {
    "Lecture Series 2002: The Way to God": "The Way to God",
    "Lecture Series 2003: Devotional Nonduality": "Devotional Nonduality",
    "Lecture Series 2004: Transcending the Mind": "Transcending the Mind",
    "Lecture Series 2005: Nonduality Intensive": "Nonduality Intensive",
    "Lecture Series 2006: Transcending Levels of Consciousness": "Transcending Levels of Consciousness",
    "Lecture Series 2007: Spiritual Reality & Modern Man": "Spiritual Reality & Modern Man",
    "Lecture Series 2008: Advanced Spiritual Awareness": "Advanced Spiritual Awareness",
    "Lecture Series 2009: In the World but Not of It": "In the World but Not of It",
    "Lecture Series 2010: Practical Spirituality": "Practical Spirituality",
    "Lecture Series 2011: Love & Spiritual Seeker Qualities": "Love & Spiritual Seeker Qualities",
}

# Broad/specific collection categories that map 1:1 to a master series when
# nothing higher in precedence is present. Order encodes their relative
# rank (e.g. Books outranks the Media Miscellaneous catch-all).
COLLECTION_SERIES = {
    "Books Published by Dr. Hawkins": "Books",
    "Discussion Series": "Discussion Series",
    "Volume Series": "Volume Series",
    "Media Miscellaneous": "Media Miscellaneous",
}

# Categories that never dominate (marketing/navigation buckets).
NEVER_DOMINANT = {
    CAT_NEW_PRODUCTS, "* @ Product Catalog", "Lectures Series", "Specials",
}

DIRECT_SERIES = {
    CAT_SATSANG: "Satsang Series",
    CAT_LECTURE_HIGHLIGHTS: "Lecture Highlights",
    CAT_SIX_BOOK: "Transcription Series Books",
    CAT_ON_THE_ROAD: "On The Road Talk Series",
    CAT_OFFICE: "Office Series",
    CAT_CARD_DECKS: "Card Decks",
}


def split_categories(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def choose_dominant(categories: list[str]) -> tuple[str, str, str]:
    """Return ``(dominant_category, dominance_rule, queue_reason)``.

    ``queue_reason`` is empty for a clean mapping; otherwise the product is
    routed to the review queue with a blank dominant category.
    """
    present = set(categories)
    highlights = present & GROUP_LECTURE_HIGHLIGHTS
    satsang = present & GROUP_SATSANG
    # R2: simultaneous Satsang + Lecture Highlights is flagged for review.
    if highlights and satsang:
        return "", "R2", "Satsang + Lecture Highlights conflict"
    if CAT_LECTURE_HIGHLIGHTS in highlights:
        return CAT_LECTURE_HIGHLIGHTS, "R1", ""
    if highlights:
        return sorted(highlights)[0], "R1", ""
    if satsang:
        return (CAT_SATSANG if CAT_SATSANG in satsang else sorted(satsang)[0]), "R2", ""
    if CAT_SIX_BOOK in present:
        return CAT_SIX_BOOK, "R5", ""
    annual = present & set(ANNUAL_SERIES)
    if len(annual) > 1:
        return "", "R3", "Multiple annual lecture-series categories: " + "; ".join(sorted(annual))
    if annual:
        return next(iter(annual)), "R3", ""
    on_the_road = present & GROUP_ON_THE_ROAD
    if on_the_road:
        return (CAT_ON_THE_ROAD if CAT_ON_THE_ROAD in on_the_road else sorted(on_the_road)[0]), "R4", ""
    if CAT_OFFICE in present:
        return CAT_OFFICE, "R6", ""
    if CAT_CARD_DECKS in present:
        return CAT_CARD_DECKS, "R7", ""
    for category, _series in COLLECTION_SERIES.items():
        if category in present:
            return category, "R7", ""
    descriptive = present - NEVER_DOMINANT
    if not descriptive:
        return "", "R8", "Only fallback/navigation categories present"
    unresolved = sorted(c for c in descriptive if c.startswith("unresolved-category-"))
    if unresolved:
        return "", "R9", "Unresolved taxonomy IDs: " + "; ".join(unresolved)
    return "", "R9", "No recognized dominant category: " + "; ".join(sorted(descriptive))


def mapped_series_for(dominant: str) -> str:
    if dominant in DIRECT_SERIES:
        return DIRECT_SERIES[dominant]
    if dominant in ANNUAL_SERIES:
        return ANNUAL_SERIES[dominant]
    if dominant in COLLECTION_SERIES:
        return COLLECTION_SERIES[dominant]
    return ""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_text(buffer.getvalue(), encoding="utf-8")


def csv_text(fields: list[str], rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def load_review_overlay() -> dict[str, dict[str, str]]:
    """Collect hand-reviewed rows so regeneration preserves them.

    Only ``approved``/``rejected`` are review state. ``proposed`` and
    ``needs_review`` are deterministic generator output and are always
    recomputed, so input changes flow through instead of being frozen.
    """
    if not MAPPING.exists():
        return {}
    overlay: dict[str, dict[str, str]] = {}
    for row in read_csv(MAPPING):
        if row["review_status"].strip() in REVIEWED_STATUSES:
            overlay[row["veritas_product_id"]] = row
    return overlay


def build_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    inventory = read_csv(INVENTORY)
    master = read_csv(MASTER)
    master_uuids = {row["uuid"] for row in master}
    overlay = load_review_overlay()

    rows: list[dict[str, str]] = []
    for product in sorted(inventory, key=lambda row: int(row["veritas_product_id"])):
        uuids = [part.strip() for part in product["matched_master_uuids"].split(";") if part.strip()]
        if not uuids:
            continue  # unmatched products live in their own review lane
        unknown = [item for item in uuids if item not in master_uuids]
        if unknown:
            raise ValueError(
                f"{INVENTORY}: product {product['veritas_product_id']} references unknown master IDs {unknown}"
            )
        categories = split_categories(product["official_categories"])
        dominant, rule, queue_reason = choose_dominant(categories)
        review_status = "needs_review" if queue_reason else "proposed"
        row = {
            "veritas_product_id": product["veritas_product_id"],
            "official_title": product["official_title"],
            "matched_master_uuids": product["matched_master_uuids"],
            "official_categories": product["official_categories"],
            "dominant_category": dominant,
            "dominance_rule": rule,
            "mapped_series": mapped_series_for(dominant),
            "review_status": review_status,
            "reviewed_on": "",
            "review_notes": "",
        }
        if product["veritas_product_id"] in overlay:
            kept = overlay[product["veritas_product_id"]]
            row["review_status"] = kept["review_status"]
            row["reviewed_on"] = kept["reviewed_on"]
            row["review_notes"] = kept["review_notes"]
            # Reviewers may override the computed dominant/series (e.g. a
            # manual dominance resolution for a multi-annual assignment);
            # invariants below keep such overrides inside the vocabulary.
            row["dominant_category"] = kept["dominant_category"]
            row["dominance_rule"] = kept["dominance_rule"]
            row["mapped_series"] = kept["mapped_series"]
        rows.append(row)

    # --- validation invariants -------------------------------------------
    seen: set[str] = set()
    for row in rows:
        pid = row["veritas_product_id"]
        if pid in seen:
            raise ValueError(f"duplicate mapping row for product {pid}")
        seen.add(pid)
        status = row["review_status"].strip()
        if status not in {"proposed", "needs_review", *REVIEWED_STATUSES}:
            raise ValueError(f"{MAPPING}: product {pid} has unsupported review_status {status!r}")
        if status not in REVIEWED_STATUSES:
            continue
        if not ISO_DATE.fullmatch(row["reviewed_on"].strip()):
            raise ValueError(f"{MAPPING}: product {pid} needs an ISO reviewed_on date")
        if not row["review_notes"].strip():
            raise ValueError(f"{MAPPING}: product {pid} needs review_notes")
        if row["dominant_category"] and row["dominant_category"] not in split_categories(row["official_categories"]):
            raise ValueError(f"{MAPPING}: product {pid} dominant category is not among its official categories")
        if status == "approved" and (not row["dominant_category"] or not row["mapped_series"]):
            raise ValueError(f"{MAPPING}: product {pid} cannot be approved without a mapped series")
        if row["dominant_category"] and row["dominant_category"] not in split_categories(row["official_categories"]):
            raise ValueError(f"{MAPPING}: product {pid} dominant category is not among its official categories")
        if row["dominant_category"] and row["mapped_series"] != mapped_series_for(row["dominant_category"]):
            raise ValueError(
                f"{MAPPING}: product {pid} mapped series does not follow the vocabulary for its dominant category"
            )

    # --- fan-out consistency: one master ID, one proposed series ----------
    uuid_series: dict[str, set[str]] = {}
    approved_series: dict[str, set[str]] = {}
    for row in rows:
        for uuid in [part.strip() for part in row["matched_master_uuids"].split(";") if part.strip()]:
            if row["mapped_series"]:
                uuid_series.setdefault(uuid, set()).add(row["mapped_series"])
            if row["review_status"] == "approved" and row["mapped_series"]:
                approved_series.setdefault(uuid, set()).add(row["mapped_series"])
    conflicted = {uuid for uuid, series_set in uuid_series.items() if len(series_set) > 1}
    approved_conflicts = {uuid for uuid, series_set in approved_series.items() if len(series_set) > 1}
    if approved_conflicts:
        raise ValueError(
            "approvals give one master ID conflicting series: " + ", ".join(sorted(approved_conflicts))
        )

    queue: list[dict[str, str]] = []
    for row in rows:
        categories = split_categories(row["official_categories"])
        _dominant, _rule, reason = choose_dominant(categories)
        uuids = [part.strip() for part in row["matched_master_uuids"].split(";") if part.strip()]
        row_conflicts = sorted(set(uuids) & conflicted)
        if row_conflicts:
            reason = "; ".join(
                part for part in [
                    reason,
                    f"master ID(s) {', '.join(row_conflicts)} receive conflicting series from multiple products",
                ]
                if part
            )
        if reason:
            if row["review_status"] == "proposed":
                row["review_status"] = "needs_review"
            queue.append({**row, "queue_reason": reason})
        elif row["review_status"] == "needs_review":
            row["review_status"] = "proposed"
    return rows, queue


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify committed mapping and queue match their declared inputs; do not write files",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    rows, queue = build_rows()
    mapping_text = csv_text(MAPPING_FIELDS, rows)
    queue_text = csv_text(QUEUE_FIELDS, queue)

    if args.check:
        stale = [
            path for path, text in ((MAPPING, mapping_text), (QUEUE, queue_text))
            if not path.exists() or path.read_text(encoding="utf-8") != text
        ]
        if stale:
            print("Series-taxonomy outputs are stale relative to their declared inputs:")
            for path in stale:
                print(f"  - {path}")
            print("Run python map_series_taxonomy.py after reviewing the input change.")
            return 1
        print(f"Series-taxonomy outputs match their inputs ({len(rows)} mappings; {len(queue)} queued for review).")
        return 0

    write_csv(MAPPING, MAPPING_FIELDS, rows)
    write_csv(QUEUE, QUEUE_FIELDS, queue)
    print(f"Wrote {MAPPING} ({len(rows)} matched products) and {QUEUE} ({len(queue)} review rows).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
