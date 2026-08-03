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
python process_data.py --check  # verify committed raw-Pages outputs are current
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
python map_series_taxonomy.py --check
```

`RECONCILIATION_REPORT.md` is the read-only review artifact. A master-check
failure indicates a ledger/draft mismatch; do not run the writing build commands
until that review is resolved.

`tests/test_pipeline.py` runs all of the above generators plus tamper
detection and the rule matrices in one command:

```bash
pip install -r requirements-dev.txt
python -m unittest discover tests          # 72 tests, no browser/network needed
coverage run -m unittest discover tests && coverage report
```

The coverage gate (`fail_under = 80` in `.coveragerc`) passes at **92%** as of
2026-08-03; every pipeline module is ≥ 88%. Approved official links added after the ledger
pass live in `data/research_master_source_overrides.csv`; unresolved manual
edition/copy leads live in `data/research_manual_leads.csv` outside the master;
reviewed but unpromoted official candidates live in
`data/manual_master_candidates.csv`. Publisher-taxonomy-to-`series` proposals
live in `data/series_category_mapping.csv`, reviewed through
`data/series_taxonomy_review_queue.csv`, and become master data only after
owner approval — see `SERIES_TAXONOMY_MAPPING.md`.

Approved master-to-product assertions are stored separately in
`data/product_relationships.csv` and rendered in the **Product Relationships**
site tab; evidence-backed annual compilation relationships live in
`data/series_compilation_relationships.csv` and render in **Series
Compilations**. See `PRODUCT_RELATIONSHIP_SCHEMA.md` and
`SERIES_COMPILATION_SCHEMA.md` before adding either relationship type. Live
Veritas inventory refreshes use the approved product-ID overlay in
`data/veritas_mapping_decisions.csv`; see `decisions/VERITAS_MAPPING_DECISIONS.md`. The
inventory's `normalized_title_match_count` is derived and must always equal the
number of IDs in `matched_master_uuids`; `build_catalogue_pages.py` fails the
build otherwise. The latest refresh review is in `VERITAS_ARTIFACT_REVIEW.md`.

## Documentation layout

Living documents sit at the repository root (`README`, `INSTRUCTIONS`,
`NEXT_AGENT_HANDOFF`, policies, schemas, proposals, and the generated
`RECONCILIATION_REPORT.md`). Approved ruling records live in
[`decisions/`](decisions/README.md); superseded status docs, research drafts,
and evidence notes live in [`archive/`](archive/README.md) and are not
normative.

## Curated records vs. official candidates

The **Everything** sheet intentionally shows curated master records next to
official product candidates so they can be compared. Every row therefore carries
an explicit `record_type`:

| `record_type` | Meaning |
|---|---|
| `master` | A curated master catalogue record (317) |
| `candidate_veritas` / `candidate_hayhouse` / `candidate_audible` | An official product listing shown for review; **not** a master record |
| `candidate_discovery` | An entry from the official discovery queue |
| `candidate_pending_promotion` | A reviewed manual candidate awaiting an owner promotion decision; **not** a master record |

Only `master` rows are catalogue records. Use the Record Type filter on that tab
to isolate curated data before exporting. Counts per class are published in
`docs/catalogue-meta.json` under `everything_record_types`.

## Review workspace

The Pages spreadsheet exposes review inputs directly: **Review Overview**,
**Master Candidates**, **Manual Leads**, **Master Exclusions**, **Migration
Review**, **Source Overrides**, **Official Discovery**, **Series
Compilations**, and **Veritas Decisions** are separate sheets alongside the
catalogue and official-product views. Reviewers can search, sort, export, and
filter sheets with multiple review-status values without opening repository
folders.

## Current reviewed catalogue state

The current curated master has **317** records (277 `lecture`, 29 `book`,
10 `discussion`, 1 untyped), **225** catalogue codes, **68** retained exclusions,
**80** approved source overrides (including Nightingale-Conant), **11** promoted
and **6** unpromoted official candidates, **312** item-to-product relationships,
and **7** series-compilation relationships. The master exposes `legacy_title` alongside the cleaned public title
so the verbatim raw spreadsheet text is always exportable.

Every entry was verified field-by-field against the live Veritas Publishing API
on 2026-08-03: 191/191 products reconcile exactly and all 195 verifiable lecture
months match the publisher's own dates. See
[AUDIT_2026-08-03_FULL.md](AUDIT_2026-08-03_FULL.md) for the full audit and
[NEXT_AGENT_HANDOFF.md](NEXT_AGENT_HANDOFF.md) for open work.

### Field semantics

`item_type` records **what a record is** (its content class: `lecture`, `book`,
`discussion`, …). `format` records **the carrier it arrives on** (`DVD`, `CD`, …).
DVD lecture recordings are therefore `item_type=lecture` with `format=DVD`, never
`item_type=video`. The `audio`/`video` values remain in the vocabulary only for
backward compatibility and must not be used for new classifications.

`month` is derived from the official Veritas product slug, which is the
publisher's authoritative date. It is **not** taken from the legacy `LSyyyynn_p`
identifier, whose `nn` segment is an ordinal position within the annual series
(this distinction caused a 156-record defect that was fixed on 2026-08-03).
