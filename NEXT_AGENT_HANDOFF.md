# Next-Agent Transition Handoff

**Prepared:** 2026-08-03
**Current branch:** `arena/019fc714-docsheet`
**Current base:** `2e952227f034a7407945bd13c218934f6a4e9157` (`main`, `origin/main`)
**Purpose:** Resume work safely without rediscovering the data model, review boundaries, or refresh safeguards.

## Immediate next actions

1. Review the latest **Map Veritas Catalogue** artifact from `main` run `30803991007`.
   - The workflow fetched a candidate inventory successfully.
   - It failed intentionally at the candidate-vs-reviewed comparison step.
   - The artifact should contain `data/veritas_official_products_candidate.csv` and `data/veritas_inventory_diff.patch`.
   - Accept no live inventory change until the diff is reviewed and any required mapping-decision updates are explicit.
2. Add read-only pull-request CI for local validation commands and static Pages smoke checks.
3. Only then proceed to candidate-promotion mechanics or inventory-only product decisions.

Local direct `python fetch_veritas_catalogue.py --check` from this sandbox failed with TLS EOF against `veritaspub.com`; use the GitHub Actions artifact as the operational review path unless direct network access is healthy.

## Current validated state

| Layer | Count | Canonical location |
|---|---:|---|
| Raw spreadsheet data rows | 374 | `hawkins archive clone - Sheet1.csv` |
| Curated master records | 308 | `data/research_master_draft.csv` / `.json` |
| Excluded raw rows | 66 | `data/research_master_exclusions.csv` |
| Approved source overrides | 80 | `data/research_master_source_overrides.csv` |
| Manual research leads | 1 | `data/research_manual_leads.csv` |
| Reviewed, unpromoted candidates | 17 | `data/manual_master_candidates.csv` |
| Veritas inventory products | 191 | `data/veritas_official_products.csv` |
| Veritas mapping decisions | 35 | `data/veritas_mapping_decisions.csv` |
| Item-to-product relationships | 301 | `data/product_relationships.csv` |
| Series-compilation relationships | 7 | `data/series_compilation_relationships.csv` |
| Everything Pages records | 344 | `docs/master.json` |
| Original Spreadsheet Pages records | 374 | `docs/data.json` |

## Required local validation

Run these from repository root before changing or delivering data:

```bash
python -m py_compile *.py
node --check docs/app.js
python build_research_master.py --check
python build_catalogue_pages.py --check
python reconcile_research_master.py --check
git diff --check
```

For a non-destructive live Veritas comparison when network access is healthy:

```bash
python fetch_veritas_catalogue.py --check
# Or create a candidate for review:
python fetch_veritas_catalogue.py --output data/veritas_official_products_candidate.csv
```

The candidate CSV and diff patch paths are ignored by Git. Never use a live fetch to overwrite the reviewed inventory without reviewing the resulting diff and any mapping-decision updates.

## Data and review boundaries

- **Raw evidence:** never edit `hawkins archive clone - Sheet1.csv` through a generator.
- **Master:** generated from the migration ledger plus reviewed source overrides; do not hand-edit its CSV/JSON outputs.
- **Manual candidates:** intentionally `not_promoted`; promotion needs a dedicated reviewed source input and UUID/code assignment path.
- **Veritas decisions:** `data/veritas_mapping_decisions.csv` persists non-primary mapping dispositions. The fetch script derives exact primary-source/date-aware results, then reapplies this overlay.
- **Relationships:** `data/product_relationships.csv` is specific item-to-product evidence; `data/series_compilation_relationships.csv` records annual Highlights at series level because official pages do not identify individual DVD parts.
- **Pages:** `docs/` is generated/static. The review workspace exposes overview, candidates, leads, exclusions, migration review, source overrides, official discovery, Veritas decisions, product relationships, and series compilations.

## Current priorities

1. Review the Veritas candidate/diff artifact from `main` run `30803991007`.
2. Add pull-request CI for syntax, master/pages/reconciliation checks, review-input validation, JSON parsing, and static/HTTP tab checks.
3. Design selective promotion of the 17 manual candidates into the master without direct generated-file edits.
4. Review the nine inventory-only Satsang products.
5. Add formal schemas/build manifests and browser interaction tests.

## Reference documents

- `PROJECT_STATE_AUDIT.md` — architecture, risks, and full audit.
- `IMPLEMENTATION_PLAN.md` — prioritized roadmap.
- `HANDOFF.md` — concise state and limitations.
- `VERITAS_MAPPING_DECISIONS.md` — refresh overlay contract.
- `RECONCILIATION_REPORT.md` — current master consistency check.
- `PRODUCT_RELATIONSHIP_SCHEMA.md` / `SERIES_COMPILATION_SCHEMA.md` — relationship contracts.

## Collaboration note

All review decisions that affect data should remain visible in dedicated CSV/Markdown inputs and in the Pages review sheets. Ask the user for a decision before promoting candidates, changing scope, or inferring work/edition identity from a title alone.
