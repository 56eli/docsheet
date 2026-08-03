#!/usr/bin/env python3
"""
process_data.py — "Live Spreadsheet" data pipeline (Phase 1)

Reads the source CSV into a Pandas DataFrame, applies any user-defined
rules in the clearly-marked DATA TRANSFORMATION RULES section below, and
writes the result to:

    docs/data.json   -> array of objects (one object per row)
    docs/meta.json   -> build metadata (row count, timestamp, ...)

The web UI in docs/ fetches these files and renders them with Tabulator.

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
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration (edit paths here if files move)
# ---------------------------------------------------------------------------
DEFAULT_CSV = "hawkins archive clone - Sheet1.csv"  # source spreadsheet
DATA_OUTPUT = Path("docs") / "data.json"          # array of objects
META_OUTPUT = Path("docs") / "meta.json"          # footer metadata
JSON_INDENT = 2                                     # pretty-print for git diffs


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


def find_source_csv(preferred: str) -> Path:
    """Locate the source CSV, falling back to any *.csv in the repo root."""
    preferred_path = Path(preferred)
    if preferred_path.is_file():
        return preferred_path

    # Fallback: allow a renamed/other CSV to be picked up automatically.
    candidates = sorted(Path(".").glob("*.csv"))
    if candidates:
        print(f"[process_data] '{preferred}' not found; using '{candidates[0]}' instead.")
        return candidates[0]

    raise FileNotFoundError(
        f"Source CSV '{preferred}' was not found and no *.csv file exists "
        f"in the repository root."
    )


def verify_outputs(records_json: str, meta: dict) -> None:
    """Ensure committed pipeline outputs still represent the current CSV.

    ``generated_at_utc`` is intentionally excluded from byte comparison because
    it records build time. All other metadata and the data payload must match.
    """
    if not DATA_OUTPUT.is_file() or not META_OUTPUT.is_file():
        raise FileNotFoundError("Generated docs/data.json and docs/meta.json must both exist.")
    if DATA_OUTPUT.read_text(encoding="utf-8") != records_json:
        raise ValueError("docs/data.json is stale; run: python process_data.py")
    try:
        committed_meta = json.loads(META_OUTPUT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"docs/meta.json is not valid JSON: {exc}") from exc
    expected = {key: value for key, value in meta.items() if key != "generated_at_utc"}
    actual = {key: committed_meta.get(key) for key in expected}
    if actual != expected or not isinstance(committed_meta.get("generated_at_utc"), str):
        raise ValueError("docs/meta.json is stale or malformed; run: python process_data.py")


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

        # --- 2. Apply transformation rules (see section above) ---------------
        df = apply_transformations(df)

        # --- 3. Serialize to JSON (array of objects) -------------------------
        records_json = df.to_json(orient="records", force_ascii=False, indent=JSON_INDENT)

        # --- 4. Build or verify outputs -------------------------------------
        meta = {
            "source_file": csv_path.name,
            "total_rows": int(len(df)),
            "column_count": int(len(df.columns)),
            "columns": [str(c) for c in df.columns],
            "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        if args.check:
            verify_outputs(records_json, meta)
            print("[process_data] docs/data.json and docs/meta.json match the current source.")
            return 0

        DATA_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DATA_OUTPUT.write_text(records_json, encoding="utf-8")
        print(f"[process_data] Wrote {DATA_OUTPUT} ({len(records_json)} bytes, "
              f"{len(df)} rows)")
        META_OUTPUT.write_text(
            json.dumps(meta, indent=JSON_INDENT, ensure_ascii=False), encoding="utf-8"
        )
        print(f"[process_data] Wrote {META_OUTPUT}")

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
