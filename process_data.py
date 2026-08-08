#!/usr/bin/env python3
"""
process_data.py — "Live Spreadsheet" data pipeline (Phase 1)

Reads the source CSV into a Pandas DataFrame, applies any user-defined
rules in the clearly-marked DATA TRANSFORMATION RULES section below, and
writes the result to:

    docs/data.json   -> array of objects (one object per row)

The web UI in docs/ fetches this file and renders it with Tabulator; the
footer timestamp comes from the HTTP Last-Modified header (the legacy
docs/meta.json descriptor was dropped by owner ruling 2026-08-07 — nothing
but this script's own self-check ever read it).

HOW TO ADD TRANSFORMATION RULES
-------------------------------
1. Open this file and scroll to the section marked

       === DATA TRANSFORMATION RULES ===

   (it is the apply_transformations() function, right below the config
   block at the top of the file).
2. Add your Pandas code there. The loaded DataFrame is available as 'df'.
   Example: df['New Column'] = df['Existing Column'].apply(some_function)
3. Commit your changes and run the "Update Spreadsheet" workflow from
   the Actions tab (or run `python process_data.py` locally).

NOTE ON THE HEADER ROW
----------------------
The CSV exported from Google Sheets has a stray title row as line 1
("archive clbs") and the real header (uuid, tempid, title, ...) as line 2.
We read with header=1 so the live table shows the real column names.
No cell values are modified — the data is passed through unchanged.
"""

import argparse
import csv
import sys
from pathlib import Path


SOURCE_REQUIRED_HEADERS = {
    "uuid", "tempid", "title", "WE HAVE?", "original source",
    "format", "product link", "other links",
}

# ---------------------------------------------------------------------------
# Configuration (edit paths here if files move)
# ---------------------------------------------------------------------------
DEFAULT_CSV = "hawkins archive clone - Sheet1.csv"  # source spreadsheet
DATA_OUTPUT = Path("docs") / "data.json"          # array of objects
JSON_INDENT = 2                                     # pretty-print for git diffs

# Owner ruling 2026-08-07: the published view trims raw columns that are empty
# on all 374 rows; the source CSV keeps them untouched.
VIEW_DROP_COLUMNS = ["uuid", "Unnamed: 8", "Unnamed: 9", "Unnamed: 10", "other links"]


def apply_transformations(df):
    # === DATA TRANSFORMATION RULES ===
    #
    # Add your data enrichment instructions below this line.
    #
    # The DataFrame is available as 'df'.
    #
    # Example: df['New Column'] = df['Existing Column'].apply(some_function)
    #
    # Save your changes by modifying this section only.

    # (No transformation rules yet — data is passed through as-is.)

    return df


def has_source_header(path: Path) -> bool:
    """Return whether a CSV has the raw spreadsheet header shape.

    The exported spreadsheet has a decorative first row and the real header on
    the second row. Accept a normal one-row CSV too, but require the raw source
    field names so a migration/review CSV can never be selected as a silent
    fallback.
    """
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            for _ in range(2):
                row = next(reader, [])
                if SOURCE_REQUIRED_HEADERS.issubset(set(row)):
                    return True
    except (OSError, UnicodeDecodeError, csv.Error):
        return False
    return False


def find_source_csv(preferred: str) -> Path:
    """Locate a raw source CSV without silently selecting an unrelated dataset."""
    preferred_path = Path(preferred)
    if preferred_path.is_file():
        if has_source_header(preferred_path):
            return preferred_path
        raise ValueError(
            f"Source CSV '{preferred}' does not have the expected raw spreadsheet headers."
        )

    # Fallback: allow a renamed raw spreadsheet only when its header shape is
    # unambiguous. Never choose the first alphabetic CSV (the repo also has
    # review/bootstrap ledgers at its root).
    candidates = [
        path for path in sorted(Path(".").glob("*.csv"))
        if has_source_header(path)
    ]
    if len(candidates) == 1:
        print(f"[process_data] '{preferred}' not found; using '{candidates[0]}' instead.")
        return candidates[0]
    if len(candidates) > 1:
        names = ", ".join(str(path) for path in candidates)
        raise FileNotFoundError(
            f"Source CSV '{preferred}' was not found and fallback is ambiguous "
            f"({names}); pass the raw source path explicitly."
        )

    raise FileNotFoundError(
        f"Source CSV '{preferred}' was not found and no raw spreadsheet CSV with "
        f"the expected headers exists in the repository root."
    )


def verify_outputs(records_json: str) -> None:
    """Ensure the committed pipeline output still represents the current CSV."""
    if not DATA_OUTPUT.is_file():
        raise FileNotFoundError("Generated docs/data.json must exist.")
    if DATA_OUTPUT.read_text(encoding="utf-8") != records_json:
        raise ValueError("docs/data.json is stale; run: python process_data.py")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify the raw spreadsheet Pages payload.")
    parser.add_argument("source_csv", nargs="?", default=DEFAULT_CSV, help="Source CSV path")
    parser.add_argument("--check", action="store_true", help="Verify committed outputs without writing")
    args = parser.parse_args()

    try:
        import pandas as pd

        # --- 1. Locate and read the source CSV -------------------------------
        csv_path = find_source_csv(args.source_csv)
        print(f"[process_data] Reading {csv_path}")

        # header=1 skips the Google Sheets title row (line 1: "archive clbs").
        # The real header (uuid, tempid, title, ...) is on line 2. All cell
        # values are kept exactly as they appear in the CSV.
        df = pd.read_csv(csv_path, header=1, dtype=str, keep_default_na=False)
        print(f"[process_data] Loaded {len(df)} rows x {len(df.columns)} columns")
        df = df.drop(columns=[c for c in VIEW_DROP_COLUMNS if c in df.columns])
        print(f"[process_data] View columns after empty-column trim: {len(df.columns)}")

        # --- 2. Apply transformation rules (see section above) ---------------
        df = apply_transformations(df)

        # --- 3. Serialize to JSON (array of objects) -------------------------
        records_json = df.to_json(orient="records", force_ascii=False, indent=JSON_INDENT)

        # --- 4. Build or verify output --------------------------------------
        if args.check:
            verify_outputs(records_json)
            print("[process_data] docs/data.json matches the current source.")
            return 0

        DATA_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DATA_OUTPUT.write_text(records_json, encoding="utf-8")
        print(f"[process_data] Wrote {DATA_OUTPUT} ({len(records_json)} bytes, "
              f"{len(df)} rows)")

        return 0

    except ModuleNotFoundError as exc:  # e.g. pandas not installed
        print(f"[process_data] ERROR: missing dependency: {exc}", file=sys.stderr)
        print("[process_data] Run:  pip install -r requirements.txt", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"[process_data] ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — fail loudly so CI shows the error
        print(f"[process_data] ERROR: pipeline failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
