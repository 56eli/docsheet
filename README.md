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

Browser smoke tests, including CSV export, are available with Playwright:

```bash
npm ci
npm run test:e2e:install
npm run test:e2e
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
until that review is resolved. Approved official links added after the ledger
pass live in `data/research_master_source_overrides.csv`; unresolved manual
edition/copy leads live in `data/research_manual_leads.csv` outside the master;
reviewed but unpromoted official candidates live in
`data/manual_master_candidates.csv`.

Approved master-to-product assertions are stored separately in
`data/product_relationships.csv` and rendered in the **Product Relationships**
site tab; evidence-backed annual compilation relationships live in
`data/series_compilation_relationships.csv` and render in **Series
Compilations**. See `PRODUCT_RELATIONSHIP_SCHEMA.md` and
`SERIES_COMPILATION_SCHEMA.md` before adding either relationship type. Live
Veritas inventory refreshes use the approved product-ID overlay in
`data/veritas_mapping_decisions.csv`; see `VERITAS_MAPPING_DECISIONS.md`.

## Review workspace

The Pages spreadsheet exposes review inputs directly: **Review Overview**,
**Master Candidates**, **Manual Leads**, **Master Exclusions**, **Migration
Review**, **Source Overrides**, **Official Discovery**, **Series
Compilations**, and **Veritas Decisions** are separate sheets alongside the
catalogue and official-product views. Reviewers can search, sort, export, and
filter sheets with multiple review-status values without opening repository
folders.

## Current reviewed catalogue state

The current curated master has **308** records, **66** retained exclusions,
**80** approved source overrides, **17** reviewed/unpromoted manual candidates,
**301** item-to-product relationships, and **7** series-compilation
relationships. See [PROJECT_STATE_AUDIT.md](PROJECT_STATE_AUDIT.md) for the
current deployment status, known risks, and prioritized backlog.
