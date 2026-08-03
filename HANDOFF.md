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
- The official Veritas inventory has **191** products; primary source matching, date-aware mapping, relationship evidence, and broad-candidate dispositions are documented in `VERITAS_PRODUCT_MAPPING.md`. A product-ID decision overlay now preserves **35** reviewed non-primary dispositions across live refreshes; its review sheet and contract are documented in `VERITAS_MAPPING_DECISIONS.md`.
- The Pages catalogue has **344** Everything records, separate product/source views, and a review workspace with sheets for overview, candidates, leads, exclusions, migration review, source overrides, official discovery, Veritas decisions, product relationships, and series compilations.
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

1. **No remote CI.** Reproducibility and UI checks are local/documented, not enforced on pull requests.
2. **Manual candidates are intentionally not master records.** Their promotion needs a dedicated reviewed workflow; do not edit generated master files.
3. **Nine official Satsang products remain inventory-only** pending a separate candidate decision.
4. **The public deployment remains `main`.** This branch’s Pages review workspace is visible publicly only after merge/deployment.
5. **Static UI caveats:** Tabulator/Google Fonts are CDN dependencies and inline edits are session-only.
6. **Veritas workflow operational verification is pending a manual GitHub Actions run.** The review-only YAML is synchronized into `main`, but this session's GitHub integration cannot dispatch it; run it once manually and inspect the candidate/diff artifact against the live API.

## Recommended next steps

1. Merge and manually run the review-only Map Veritas workflow; inspect its candidate/diff artifact against the live API.
2. Add PR CI for syntax, deterministic build checks, and static/browser smoke checks.
3. Define/implement selective manual-candidate promotion into the master.
4. Review the nine unmatched Satsang products and remaining inventory-only dispositions.
5. Open/merge a PR only after reviewing the broad data-model and public-data implications.

For full counts, architecture, inconsistencies, and priority rationale, see [PROJECT_STATE_AUDIT.md](PROJECT_STATE_AUDIT.md) and [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).
