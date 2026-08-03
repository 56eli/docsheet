# Next-Agent Transition Handoff

**Prepared:** 2026-08-03
**Current branch:** `arena/019fc714-docsheet`
**Purpose:** Resume work safely without rediscovering the compact-ID migration, data model, review boundaries, UX changes, or refresh safeguards.

## Immediate next actions

1. Open and merge the PR from `arena/019fc714-docsheet` when review is complete.
2. Confirm GitHub Pages redeploys from `main` → `/docs` and serves the compact-ID spreadsheet UI.
3. Add the CI workflow after GitHub workflow-file permissions are available; this branch already includes the Playwright CSV export test files and npm scripts.
4. Review the latest **Map Veritas Catalogue** artifact from `main` run `30803991007` outside this sandbox.

Local direct `python fetch_veritas_catalogue.py --check` from this sandbox failed with TLS EOF against `veritaspub.com`; use the GitHub Actions artifact as the operational review path unless direct network access is healthy.

## Current validated state

| Layer | Count | Canonical location |
|---|---:|---|
| Raw spreadsheet data rows | 374 | `hawkins archive clone - Sheet1.csv` |
| Curated master records | 308 | `data/research_master_draft.csv` / `.json` |
| Compact master IDs | 1–308 | `uuid` field retained for compatibility; displayed as Master ID |
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

## Current UX additions on this branch

- View description/count/type/export summary for every tab.
- Readable labels for URL-heavy cells.
- Per-view column ordering, width tuning, and frozen key columns.
- Column chooser with show-all reset.
- Row details drawer for all fields.
- Active search/review filter chips with clear-all control.
- Playwright CSV export smoke tests in `tests/csv-export.spec.js`.

## Required local validation

Run these from repository root before changing or delivering data:

```bash
python -m py_compile *.py
node --check docs/app.js
node --check playwright.config.js
node --check tests/csv-export.spec.js
python build_research_master.py --check
python build_catalogue_pages.py --check
python reconcile_research_master.py --check
npx playwright test --list
git diff --check
```

Full browser execution needs Chromium:

```bash
npm ci
npm run test:e2e:install
npm run test:e2e
```

This sandbox could list Playwright tests, but Chromium download failed with TLS/network resets.

## Live Veritas review

Artifact from `main` run `30803991007`:

- Artifact name: `veritas-inventory-review-30803991007`
- Artifact ID: `8851979247`
- Reported ZIP digest: `3f06b4499dd21840abf995725621f1f7724261f2546e1ae7d6da8c2427f15c3d`
- Expected files:
  - `data/veritas_official_products_candidate.csv`
  - `data/veritas_inventory_diff.patch`

Do not replace the reviewed Veritas inventory without inspecting the diff and updating mapping decisions deliberately.

## Data and review boundaries

- **Raw evidence:** never edit `hawkins archive clone - Sheet1.csv` through a generator.
- **Master:** generated from the migration ledger plus reviewed source overrides; do not hand-edit generated CSV/JSON outputs except through approved migration/rebuild steps.
- **Master IDs:** compact numeric IDs are retained by raw source row number and capped at 10000.
- **Manual candidates:** intentionally `not_promoted`; promotion needs a dedicated reviewed source input and compact ID/code assignment path.
- **Veritas decisions:** `data/veritas_mapping_decisions.csv` persists non-primary mapping dispositions. The fetch script derives exact primary-source/date-aware results, then reapplies this overlay.
- **Relationships:** `data/product_relationships.csv` is specific item-to-product evidence; `data/series_compilation_relationships.csv` records annual Highlights at series level because official pages do not identify individual DVD parts.
- **Pages:** `docs/` is generated/static. The review workspace exposes overview, candidates, leads, exclusions, migration review, source overrides, official discovery, Veritas decisions, product relationships, and series compilations.

## Current priorities

1. PR/merge this branch and verify Pages deployment.
2. Add and verify CI after workflow-file permissions are available.
3. Review the Veritas candidate/diff artifact from `main` run `30803991007`.
4. Disable or clarify session-only editing.
5. Design selective promotion of the 17 manual candidates into the master without direct generated-file edits.
6. Add formal schemas/build manifests and broader browser interaction tests.

## Reference documents

- `PROJECT_STATE_AUDIT.md` — architecture, risks, validation, and full audit.
- `IMPLEMENTATION_PLAN.md` — prioritized roadmap.
- `SPREADSHEET_UX_REVIEW.md` — UX recommendations and implementation status.
- `VERITAS_ARTIFACT_REVIEW.md` — artifact retrieval/access report.
- `VERITAS_MAPPING_DECISIONS.md` — refresh overlay contract.
- `RECONCILIATION_REPORT.md` — current master consistency check.
- `PRODUCT_RELATIONSHIP_SCHEMA.md` / `SERIES_COMPILATION_SCHEMA.md` — relationship contracts.

## Collaboration note

All review decisions that affect data should remain visible in dedicated CSV/Markdown inputs and in the Pages review sheets. Ask the user for a decision before promoting candidates, changing scope, or inferring work/edition identity from a title alone.
