"""Shared helpers for the docsheet generator modules.

The generators are standalone scripts that run in a sandbox (and as
subprocesses in CI), so shared code lives in this one small module that they
all import rather than being copied into each file. Keeping it tiny and
stateless makes it safe to share with no behavioral change.
"""
from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path

# ISO 8601 date (YYYY-MM-DD): the review-date convention across the pipeline.
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a committed CSV into a list of row dicts."""
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def render_csv(fieldnames: list[str], rows: list[dict[str, str]]) -> str:
    """Render rows as stable UTF-8 CSV text with LF line endings."""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def json_text(data: object) -> str:
    """Render data as stable, diff-friendly UTF-8 JSON with a trailing newline."""
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"
