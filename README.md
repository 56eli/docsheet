# DocSheet — Live Spreadsheet

Renders the repository CSV as an interactive, searchable web table on
GitHub Pages (built with [Tabulator](https://tabulator.info/)).

- **Live site:** `https://56eli.github.io/docsheet` (once GitHub Pages is enabled)
- **Pipeline:** `process_data.py` reads the CSV with Pandas and publishes
  `docs/data.json` — data is currently passed through **unchanged**.
- **Automation:** the "Update Spreadsheet" GitHub Actions workflow regenerates
  the data on demand or whenever the CSV changes on `main`.

📖 Full setup and usage guide: **[INSTRUCTIONS.md](INSTRUCTIONS.md)**

## Quick start

```bash
pip install -r requirements.txt
python process_data.py
python -m http.server 8000   # then open http://localhost:8000/docs/
```

## Catalogue-data safeguard

The raw spreadsheet pipeline above is independent from the curated research
catalogue. Before rebuilding curated master or catalogue Pages files, inspect
and acknowledge any ledger/draft divergence first:

```bash
python reconcile_research_master.py --check
python build_research_master.py --check
python build_catalogue_pages.py --check
```

`RECONCILIATION_REPORT.md` is the read-only review artifact. A master-check
failure indicates a ledger/draft mismatch; do not run the writing build commands
until that review is resolved.
