#!/usr/bin/env python3
"""Shared data and file helpers for the docsheet pipeline."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

# Constants
COMPACT_ID_MAX = 1000


def is_compact_id(value: str) -> bool:
    """Check whether a string is a valid compact numeric master ID."""
    return value.isdigit() and 1 <= int(value) <= COMPACT_ID_MAX


def index_csv(path: Path, key: str) -> dict[str, dict[str, str]]:
    """Load a CSV file into a dictionary indexed by a given column name."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        val = row.get(key, "").strip()
        if val:
            result[val] = row
    return result


def require_columns(path: Path, required: set[str]) -> set[str]:
    """Verify that a CSV contains all required column names."""
    if not path.exists():
        raise FileNotFoundError(f"Required CSV missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        cols = set(reader.fieldnames or [])
    missing = required - cols
    if missing:
        raise ValueError(f"{path.name} missing required columns: {sorted(missing)}")
    return cols


def title_for(row: dict[str, str]) -> str:
    """Produce the public display title while retaining the raw legacy title."""
    title = row.get("proposed_title", "").strip() or row.get("title", "").strip()
    tempid = row.get("raw_tempid", "").strip() or row.get("legacy_tempid", "").strip()
    raw_num = row.get("raw_row_number", "").strip()

    if tempid.startswith("LS"):
        return re.sub(r"\s*\([^)]*\)\s*DVD\d+\s*$", "", title).strip()

    title = re.sub(r"\.mp4\s*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s*-\s*converted\s*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^\d{1,3}[.\s]+(?=\S)", "", title)
    title = re.sub(r"\s+", " ", title).strip()

    if raw_num == "224":
        title = title.replace("Volume II-", "Volume I-", 1)
    return title


def notes_for(row: dict[str, str]) -> str:
    """Normalize notes text from ledger row."""
    notes = []
    raw_src = row.get("raw_original_source", "").strip()
    unnamed5 = row.get("raw_unnamed_5", "").strip()
    raw_num = row.get("raw_row_number", "").strip()

    if raw_src and raw_src != "veritas":
        notes.append(f"Raw source note: {raw_src}")
    if unnamed5:
        notes.append(unnamed5)
    if raw_num == "224":
        notes.append(
            "Display title corrects raw 'Volume II' to Volume I: official product 50432 is a two-disc Volume I set."
        )
    return " | ".join(notes)


def month_from_title(title: str, year: str = "") -> str:
    """Extract 2-digit month from a title string if present (e.g. 'January 2003' -> '01')."""
    months = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }
    lowered = title.lower()
    for name, num in months.items():
        if name in lowered:
            return num
    return ""


def assign_compact_ids(
    prefix: str, items: Iterable[dict[str, str]], key: str = "id"
) -> int:
    """Assign deterministic compact IDs (e.g. 'm-1', 'm-2') to items missing an ID."""
    count = 0
    assigned = set()
    for item in items:
        val = item.get(key, "").strip()
        if val:
            assigned.add(val)
    idx = 1
    for item in items:
        if not item.get(key, "").strip():
            while f"{prefix}-{idx}" in assigned:
                idx += 1
            cid = f"{prefix}-{idx}"
            item[key] = cid
            assigned.add(cid)
            count += 1
    return count


def veritas_products_by_id() -> dict[str, dict[str, str]]:
    import build_research_master
    path = getattr(build_research_master, "VERITAS_PRODUCTS", Path("data/veritas_official_products.csv"))
    if not path.exists():
        return {}
    return index_csv(path, "veritas_product_id")


def veritas_products_by_url() -> dict[str, dict[str, str]]:
    import build_research_master
    path = getattr(build_research_master, "VERITAS_PRODUCTS", Path("data/veritas_official_products.csv"))
    if not path.exists():
        return {}
    return index_csv(path, "official_product_url")
