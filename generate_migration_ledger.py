#!/usr/bin/env python3
"""Generate a review-only migration ledger from the raw Hawkins CSV.

The source CSV is never modified. The generated ledger records the original
row values, a conservative proposed disposition, and limited non-destructive
metadata suggestions for human review.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

SOURCE = Path("hawkins archive clone - Sheet1.csv")
OUTPUT = Path("migration_review_ledger.csv")

# These are context labels found in the source. They are not catalogue items.
SERIES_HEADINGS = {
    "Series 2002: The Way to God": "The Way to God",
    "Series 2003: Devotional Nonduality": "Devotional Nonduality",
    "Series 2004: Transcending the Mind": "Transcending the Mind",
    "Series 2005: Nonduality Intensive": "Nonduality Intensive",
    "Series 2006: Transcending Levels of Consciousness": "Transcending Levels of Consciousness",
    "Series 2007: Spiritual Reality & Modern Man": "Spiritual Reality & Modern Man",
    "Series 2008: Advanced Spiritual Awareness": "Advanced Spiritual Awareness",
    "Series 2009: In the World but Not of It": "In the World but Not of It",
    "Series 2010: Practical Spirituality": "Practical Spirituality",
    "Series 2011: Love & Spiritual Seeker Qualities": "Love & Spiritual Seeker Qualities",
}

GROUP_HEADINGS = {
    "VOLUME SERIES": "Volume Series",
    "On The Road - Talk Series": "On The Road Talk Series",
    "Office series": "Office Series",
    "Missing satsang audios": "Satsang Series",
    "Media Miscellaneous:": "Media Miscellaneous",
    "Discussion Series with Dr. David Hawkins & Wife Susan": "Discussion Series",
    "Books": "Books",
    "TRANSCRIPTION SERIES BOOKS": "Transcription Series Books",
    "Scott Jeffrey edited books": "Scott Jeffrey Edited Books",
    "Lecture Highlights": "Lecture Highlights",
}


def clean(value: str) -> str:
    return value.strip()


def first_year(*values: str) -> str:
    for value in values:
        match = re.search(r"(?:19|20)\d{2}", value)
        if match:
            return match.group(0)
    return ""


def classify(row: list[str], current_series: str) -> tuple[str, str, str]:
    """Return disposition, reason, and next series context."""
    uuid, tempid, title, owned, source, note, fmt, product, *_rest = row
    values = [clean(value) for value in row]
    title = clean(title)
    tempid = clean(tempid)
    owned = clean(owned)
    product = clean(product)

    if not any(values):
        return "blank_separator", "Empty visual separator row.", current_series

    if title in SERIES_HEADINGS:
        return "series_context", "Annual lecture-series heading.", SERIES_HEADINGS[title]

    for prefix, series in GROUP_HEADINGS.items():
        if title.startswith(prefix):
            return "series_context", "Collection/category heading.", series

    title_upper = title.upper()
    if (
        "MISSING" in title_upper
        or "MORE STUFF MISSING" in title_upper
        or title_upper.startswith("DISSERTATION")
        or title_upper.startswith("SCORPION BOOK")
        or title_upper.startswith("ORTHOMOLECULAR BOOK")
    ):
        return "research_note", "Editorial gap/research note; item identity needs confirmation.", current_series

    if title.startswith(("http://", "https://")) or re.search(r"\shttps?://", title):
        return "source_context", "Landing page or source URL stored in title.", current_series

    if owned in {"✅", "❌"} or tempid:
        if tempid == "2cds each?":
            return "item", "Item candidate; legacy tempid is a repeated placeholder, not an ID.", current_series
        return "item", "Item candidate indicated by ownership status and/or legacy tempid.", current_series

    return "needs_review", "Non-empty row without item ID or ownership status.", current_series


def proposed_item_type(tempid: str, series: str, title: str) -> str:
    if tempid.startswith("LS"):
        return "lecture"
    if "Books" in series:
        return "book"
    if title.lower().endswith(".mp4"):
        return ""  # Video is not in the approved initial controlled vocabulary.
    return ""


def main() -> None:
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.reader(handle))

    data_rows = source_rows[2:]
    current_series = ""
    output_rows: list[dict[str, str]] = []

    for source_row_number, raw in enumerate(data_rows, start=3):
        row = (raw + [""] * 13)[:13]
        disposition, reason, current_series = classify(row, current_series)
        uuid, tempid, title, owned, source, unnamed_5, raw_format, product, unnamed_8, unnamed_9, unnamed_10, unnamed_11, other_links = row
        valid_veritas_product = clean(product)
        if valid_veritas_product.startswith("https://veritaspub.com/product/https://"):
            valid_veritas_product = ""
            reason += " Product URL has duplicated prefix and is quarantined for correction."

        title_clean = clean(title)
        detail_match = re.search(r"\b(DVD\d+)\b", title_clean, re.IGNORECASE)
        raw_owned = clean(owned)
        output_rows.append({
            "raw_row_number": str(source_row_number),
            "disposition": disposition,
            "review_reason": reason,
            "proposed_series": current_series if disposition == "item" else "",
            "proposed_title": title_clean if disposition == "item" else "",
            "proposed_item_type": proposed_item_type(clean(tempid), current_series, title_clean) if disposition == "item" else "",
            "proposed_year": first_year(clean(tempid), title_clean) if disposition == "item" else "",
            "proposed_month": clean(tempid)[6:8] if disposition == "item" and re.fullmatch(r"LS\d{6}_\d+", clean(tempid)) else "",
            "proposed_format": "DVD" if disposition == "item" and detail_match else "",
            "proposed_format_detail": detail_match.group(1).upper() if disposition == "item" and detail_match else "",
            "proposed_owned": {"✅": "true", "❌": "false"}.get(raw_owned, "") if disposition == "item" else "",
            "proposed_source_url_veritas": valid_veritas_product if disposition == "item" else "",
            "raw_uuid": uuid,
            "raw_tempid": tempid,
            "raw_title": title,
            "raw_we_have": owned,
            "raw_original_source": source,
            "raw_unnamed_5": unnamed_5,
            "raw_format": raw_format,
            "raw_product_link": product,
            "raw_unnamed_8": unnamed_8,
            "raw_unnamed_9": unnamed_9,
            "raw_unnamed_10": unnamed_10,
            "raw_unnamed_11": unnamed_11,
            "raw_other_links": other_links,
        })

    fields = list(output_rows[0])
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    counts: dict[str, int] = {}
    for row in output_rows:
        counts[row["disposition"]] = counts.get(row["disposition"], 0) + 1
    print(f"Wrote {OUTPUT} ({len(output_rows)} rows)")
    for key in sorted(counts):
        print(f"  {key}: {counts[key]}")


if __name__ == "__main__":
    main()
