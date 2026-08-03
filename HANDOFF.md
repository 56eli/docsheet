# Handoff — Hawkins Research Catalogue

**Updated:** 2026-08-03
**Branch:** `arena/019fc6af-docsheet`
**State audit:** [PROJECT_STATE_AUDIT.md](PROJECT_STATE_AUDIT.md)

## Delivered state

- The raw 374-row spreadsheet remains preserved; generators never modify it.
- The reconciled research master has **308** records and **66** excluded raw rows.
- Review/provenance inputs are explicit and validated:
  - **80** approved official source overrides;
  - **17** reviewed but unpromoted manual candidates;
  - **1** manual research/edition lead;
  - **301** item-to-product relationships;
  - **7** annual series-compilation relationships.
- The official Veritas inventory has **191** products; primary source matching, date-aware mapping, relationship evidence, and broad-candidate dispositions are documented in `VERITAS_PRODUCT_MAPPING.md`.
- The Pages catalogue has **344** Everything records, separate product/source views, and a review workspace with sheets for overview, candidates, leads, exclusions, migration review, source overrides, official discovery, product relationships, and series compilations.
- Review tabs are grouped visually, use human-readable headers and status badges, and provide a status/disposition filter when multiple values exist.
- `Update Spreadsheet` is synchronized from `main` and writes/commits `docs/data.json` plus `docs/meta.json`; Pages is configured for `main` → `/docs`.

## Validation completed

- Python syntax compilation for all repository scripts.
- `node --check docs/app.js`.
- `python build_research_master.py --check`.
- `python build_catalogue_pages.py --check`.
- `python reconcile_research_master.py --check`.
- Isolated clean-directory master/pages rebuild.
- Local HTTP smoke tests for review workspace assets.
- `git diff --check`.

## Current limitations and risks

1. **Veritas refresh can erase curation.** `fetch_veritas_catalogue.py` rebuilds inventory matches but does not yet reapply persistent product-ID mapping decisions; the Map Veritas workflow can overwrite reviewed statuses on a live refresh.
2. **No remote CI.** Reproducibility and UI checks are local/documented, not enforced on pull requests.
3. **Manual candidates are intentionally not master records.** Their promotion needs a dedicated reviewed workflow; do not edit generated master files.
4. **Nine official Satsang products remain inventory-only** pending a separate candidate decision.
5. **The public deployment remains `main`.** This branch’s Pages review workspace is visible publicly only after merge/deployment.
6. **Static UI caveats:** Tabulator/Google Fonts are CDN dependencies and inline edits are session-only.

## Recommended next steps

1. Implement a persistent Veritas mapping-decision overlay and make the refresh workflow review-safe.
2. Add PR CI for syntax, deterministic build checks, and static/browser smoke checks.
3. Define/implement selective manual-candidate promotion into the master.
4. Review the nine unmatched Satsang products and remaining inventory-only dispositions.
5. Open/merge a PR only after reviewing the broad data-model and public-data implications.

For full counts, architecture, inconsistencies, and priority rationale, see [PROJECT_STATE_AUDIT.md](PROJECT_STATE_AUDIT.md) and [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).
