#!/usr/bin/env python3
"""Generate a review-only migration ledger from the raw Hawkins CSV.

The source CSV is never modified. The generated ledger records the original
row values, a conservative proposed disposition, and limited non-destructive
metadata suggestions for human review.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

from _common import render_csv

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


VERITAS_DATED_SLUG = re.compile(r"/product/(20\d{2})-(0[1-9]|1[0-2])-")
MONTH_NAMES = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
    "jul": "07", "aug": "08", "sep": "09", "sept": "09", "oct": "10", "nov": "11",
    "dec": "12",
}
VERITAS_SLUG_MONTH_NAME = re.compile(
    r"-(" + "|".join(sorted(MONTH_NAMES, key=len, reverse=True)) + r")-(20\d{2})/?$"
)


def proposed_month(tempid: str, veritas_url: str) -> str:
    """Return the calendar month of a lecture, from the official product URL.

    The ``LSyyyynn_p`` legacy identifier's ``nn`` segment is the lecture's
    ORDINAL POSITION in its annual series, not a calendar month. That only
    coincided with the month in 2002, when lectures ran monthly; from 2003 the
    cadence was roughly bi-monthly, so ordinal 02 is April, not February.

    The authoritative month is published by Veritas in the product slug, in
    either a numeric form (``/product/2003-02-integration-...``) or a
    month-name form (``/product/vision-feb-2005``). Return empty rather than
    guessing when no dated official product is linked.
    """
    if not re.fullmatch(r"LS\d{6}_\d+", tempid):
        return ""
    url = veritas_url or ""
    numeric = VERITAS_DATED_SLUG.search(url)
    if numeric:
        return numeric.group(2)
    named = VERITAS_SLUG_MONTH_NAME.search(url)
    return MONTH_NAMES[named.group(1)] if named else ""


def proposed_item_type(tempid: str, series: str, title: str) -> str:
    if tempid.startswith("LS"):
        return "lecture"
    if "Books" in series:
        return "book"
    if title.lower().endswith(".mp4"):
        return ""  # Video is not in the approved initial controlled vocabulary.
    return ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="read-only report of drift between a fresh bootstrap and the "
             "committed ledger; never writes (exit 1 when they differ)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite the committed, hand-maintained ledger from the raw CSV",
    )
    args = parser.parse_args(argv)

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
            "proposed_month": proposed_month(clean(tempid), valid_veritas_product) if disposition == "item" else "",
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
    rendered = render_csv(fields, output_rows)

    counts: dict[str, int] = {}
    for row in output_rows:
        counts[row["disposition"]] = counts.get(row["disposition"], 0) + 1

    def print_counts() -> None:
        for key in sorted(counts):
            print(f"  {key}: {counts[key]}")

    if args.check:
        committed = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else None
        if committed == rendered:
            print(f"{OUTPUT} matches a fresh bootstrap of the raw CSV.")
            return 0
        differing = -1
        if committed is not None:
            new_lines = rendered.splitlines()
            old_lines = committed.splitlines()
            differing = sum(
                1
                for idx in range(max(len(new_lines), len(old_lines)))
                if (new_lines[idx] if idx < len(new_lines) else None)
                != (old_lines[idx] if idx < len(old_lines) else None)
            )
        print(
            f"{OUTPUT} differs from a fresh bootstrap "
            f"({differing if differing >= 0 else 'all'} line(s) would change). "
            "This is expected while the ledger is hand-maintained; review the "
            "diff with git before regenerating with --force.",
            file=sys.stderr,
        )
        return 1

    if not args.force:
        print(
            f"Refusing to overwrite {OUTPUT}: the committed ledger is a "
            "hand-maintained review artifact. Run with --force to regenerate "
            "it from the raw CSV, or --check for a read-only drift report.",
            file=sys.stderr,
        )
        return 2

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(output_rows)} rows)")
    print_counts()
    return 0


if __name__ == "__main__":
    sys.exit(main())
