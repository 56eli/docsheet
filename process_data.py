#!/usr/bin/env python3
"""
process_data.py — "Live Spreadsheet" data pipeline (Phase 1)

Reads the source CSV into a Pandas DataFrame, applies any user-defined
rules in the clearly-marked DATA TRANSFORMATION RULES section below, and
writes the result to:

    public/data.json   -> array of objects (one object per row)
    public/meta.json   -> build metadata (row count, timestamp, ...)

The web UI in public/ fetches these files and renders them with Tabulator.

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

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration (edit paths here if files move)
# ---------------------------------------------------------------------------
DEFAULT_CSV = "hawkins archive clone - Sheet1.csv"  # source spreadsheet
DATA_OUTPUT = Path("public") / "data.json"          # array of objects
META_OUTPUT = Path("public") / "meta.json"          # footer metadata
JSON_INDENT = 2                                     # pretty-print for git diffs


def apply_transformations(df: pd.DataFrame) -> pd.DataFrame:
    """
    ==========================================================================
    === DATA TRANSFORMATION RULES ===
    Add your data enrichment instructions below this line.

    The DataFrame is available as 'df'.

    Example: df['New Column'] = df['Existing Column'].apply(some_function)

    Save your changes by modifying this section only.
    ==========================================================================
    """

    # ------------------------------------------------------------------------
    # Your rules go BELOW this line (between here and the return statement).
    # For Phase 1 nothing is defined on purpose — the data is passed through
    # unchanged. Do not edit anything outside this section.
    # ------------------------------------------------------------------------

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


def main() -> int:
    try:
        # --- 1. Locate and read the source CSV -------------------------------
        csv_path = find_source_csv(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV)
        print(f"[process_data] Reading {csv_path}")

        # header=1 skips the Google Sheets title row (line 1: "archive clbs").
        # The real header (uuid, tempid, title, ...) is on line 2. All cell
        # values are kept exactly as they appear in the CSV.
        df = pd.read_csv(csv_path, header=1, dtype=str, keep_default_na=True)
        print(f"[process_data] Loaded {len(df)} rows x {len(df.columns)} columns")

        # --- 2. Apply transformation rules (see section above) ---------------
        df = apply_transformations(df)

        # --- 3. Serialize to JSON (array of objects) -------------------------
        records_json = df.to_json(orient="records", force_ascii=False, indent=JSON_INDENT)

        # --- 4. Write outputs ------------------------------------------------
        DATA_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DATA_OUTPUT.write_text(records_json, encoding="utf-8")
        print(f"[process_data] Wrote {DATA_OUTPUT} ({len(records_json)} bytes, "
              f"{len(df)} rows)")

        meta = {
            "source_file": csv_path.name,
            "total_rows": int(len(df)),
            "column_count": int(len(df.columns)),
            "columns": [str(c) for c in df.columns],
            "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
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
