# Next-Agent Transition Handoff

**Prepared:** 2026-08-03
**Transition PR:** [#7 — Reconcile catalogue data and safeguard Veritas refreshes](https://github.com/56eli/docsheet/pull/7)
**Purpose:** Resume work safely after this session ends without rediscovering the data model, review boundaries, or refresh safeguards.

## First actions after PR #7 is merged

1. Confirm GitHub Pages deploys `main` → `/docs` successfully.
2. In GitHub Actions, manually run **Map Veritas Catalogue** on `main`.
3. Inspect the `veritas-inventory-review-*` artifact:
   - **No diff:** the workflow succeeds and the committed inventory already matches live, decision-applied data.
   - **Diff:** failure is intentional; download the candidate CSV and diff patch, review source changes, update `data/veritas_mapping_decisions.csv` only where a reviewed decision changes, then regenerate and commit deliberately.
4. Do **not** restore the old auto-commit workflow behavior.

This session could not dispatch the workflow because the GitHub integration returned HTTP 403. Local direct API fetches also encountered transient TLS EOFs; the fetch client now retries transient empty/non-JSON responses, and offline end-to-end mapping/decision simulations pass.

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

## Required local validation

Run these from repository root before changing or delivering data:

```bash
python -m py_compile process_data.py build_research_master.py build_catalogue_pages.py \
  reconcile_research_master.py fetch_veritas_catalogue.py generate_lecture_review.py \
  generate_migration_ledger.py
node --check docs/app.js
python build_research_master.py --check
python build_catalogue_pages.py --check
python reconcile_research_master.py --check
```

For a live Veritas comparison after merge:

```bash
python fetch_veritas_catalogue.py --check
# Or create a non-destructive candidate for review:
python fetch_veritas_catalogue.py --output data/veritas_official_products_candidate.csv
```

The candidate CSV and diff patch paths are ignored by Git. Never use a live fetch to overwrite the reviewed inventory without reviewing the resulting diff and any mapping-decision updates.

## Data and review boundaries

- **Raw evidence:** never edit `hawkins archive clone - Sheet1.csv` through a generator.
- **Master:** generated from the migration ledger plus reviewed source overrides; do not hand-edit its CSV/JSON outputs.
- **Manual candidates:** intentionally `not_promoted`; promotion needs a dedicated reviewed source input and UUID/code assignment path.
- **Veritas decisions:** `data/veritas_mapping_decisions.csv` persists non-primary mapping dispositions. The fetch script deterministically derives exact primary-source and date-aware results, then reapplies this overlay.
- **Relationships:** `data/product_relationships.csv` is specific item-to-product evidence; `data/series_compilation_relationships.csv` records annual Highlights at series level because the official pages do not identify individual DVD parts.
- **Pages:** `docs/` is generated/static. The review workspace exposes overview, candidates, leads, exclusions, migration review, source overrides, official discovery, Veritas decisions, product relationships, and series compilations.

## Current priorities

1. Verify the merged review-only Map Veritas workflow with a manual live Actions run.
2. Add pull-request CI for syntax, master/pages/reconciliation checks, review-input validation, and static/HTTP tab checks.
3. Design selective promotion of the 17 manual candidates into the master without direct generated-file edits.
4. Review the nine inventory-only Satsang products.
5. Add formal schemas/build manifests and browser interaction tests.

## Reference documents

- `PROJECT_STATE_AUDIT.md` — architecture, risks, and full audit.
- `IMPLEMENTATION_PLAN.md` — current prioritized roadmap.
- `HANDOFF.md` — concise state and limitations.
- `VERITAS_MAPPING_DECISIONS.md` — refresh overlay contract.
- `RECONCILIATION_REPORT.md` — current master consistency check.
- `PRODUCT_RELATIONSHIP_SCHEMA.md` / `SERIES_COMPILATION_SCHEMA.md` — relationship contracts.

## Collaboration note

All review decisions that affect data should remain visible in dedicated CSV/Markdown inputs and in the Pages review sheets. Ask the user for a decision before promoting candidates, changing scope, or inferring work/edition identity from a title alone.
