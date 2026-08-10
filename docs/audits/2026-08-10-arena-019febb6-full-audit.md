# Full Project Audit — Arena 019febb6

**Date:** 2026-08-10  
**Baseline:** `f71843a1222b23d088a386d1f3a71acfac7da2bd` (`main`, merged PR #69)  
**Disciplines:** Web Design · Full-Stack Development · Data Engineering  
**Verdict:** **Healthy / conditional pass (8.1/10)**

## Executive summary

DocSheet is a mature, unusually well-audited static catalogue: a deterministic Python data pipeline publishes a read-only, responsive GitHub Pages application backed by committed JSON. The curated lane has strong domain validation, provenance, reproducible outputs, and broad tests; the frontend has a coherent visitor/expert information architecture, mobile browse mode, spreadsheet mode, accessible controls, CSV/ODS export, and a hash-based delivery contract. The current `main` CI and Pages deployment are green.

No new data-integrity or release-blocking defect was found. The important remaining risk is operational: Pages still deploys directly from `main:/docs`, so a bad commit can publish before CI rejects it. The best agent-safe improvements are to lint every frontend module in CI, add a conventional aggregate `npm test` command, and reduce the remaining large-file/test-maintenance hotspots.

## Architecture understood

### Raw source lane

```text
hawkins archive clone - Sheet1.csv
  → process_data.py
  → docs/data.json
```

This lane preserves source cell values and removes only six consistently empty presentation columns. It is intentionally separate from the curated catalogue.

### Curated catalogue lane

```text
migration_review_ledger.csv + reviewed data/*.csv overlays
  → build_research_master.py
  → data/research_master_draft.{csv,json}
  → map_series_taxonomy.py
  → build_catalogue_pages.py
  → docs/*.json
```

`reconcile_research_master.py` detects ledger/draft divergence; `sync_inventory_mirrors.py` guards inventory mirrors. Generated outputs are checked rather than edited manually. The overlays encode owner decisions for dates, notes, editions, source links, work families, taxonomy, display order, and relationships.

### Presentation lane

`docs/index.html` loads Tabulator plus `docs/app.js`; the latter delegates columns, formatting, filtering, mobile behavior, view utilities, and ODS generation to seven ES modules in `docs/js/`. GitHub Pages serves the static application with no backend and no user data collection.

## Evidence and verification

| Check | Result |
|---|---|
| Python unit/contract/style suite | **149/149 pass** |
| Python coverage | **90%** (2,327 statements; 85% floor) |
| Frontend Node module suite | **4/4 pass** |
| Recursive Python compilation | Pass |
| JavaScript syntax (`app.js`, all modules, all browser specs) | Pass |
| `npm audit` | **0 vulnerabilities** |
| Six deterministic generator `--check` commands | **6/6 pass** locally after installing the constrained dependencies in an isolated audit environment |
| Local Playwright | Browser executable unavailable locally; latest main CI run `31389446626` passed the complete browser job |
| GitHub state | Main CI green; Pages deployment green; one open issue (#18) |

A local `npm run test:e2e` correctly reached Playwright but could not launch Chromium because the sandbox browser binary was absent. This is an environment limitation, not an application failure. The immediately preceding main workflow is stronger evidence because it completed successfully in the declared CI environment.

## Data engineering audit

### Current published inventory

- 374 raw rows, including 31 decorative separators retained in the raw payload.
- 363 curated masters.
- 191 work IDs; 278 unique catalogue codes; 363 unique proposed filenames.
- Item types: 306 lecture, 41 book, 8 discussion, 7 highlight, 1 other.
- Formats: 253 DVD, 32 CD, 32 book, 27 audiobook, 19 streaming.
- Ownership: 289 true, 25 false, 49 blank; blank correctly means “not stated.”
- 340 product relationships and 7 series-compilation relationships.
- Inventories: 191 Veritas, 29 Hay House, 26 Audible, 38 international products.
- 75 exclusions, 134 source overrides, 40 promoted manual candidates, 4 manual leads.
- Display ordering is a dense owner-approved ordering across all 363 masters.

### Strengths

1. **Excellent deterministic-build discipline.** Every major generator supports `--check`, and tests include write/check/tamper paths.
2. **Clear source-of-truth boundaries.** Raw, reviewed inputs, generated drafts, published payloads, and decision records have distinct roles.
3. **Strong domain invariants.** Validators cover identity uniqueness, controlled vocabularies, dates, ownership tri-state semantics, relationships, URL rules, catalogue-code behavior, filenames, and generated consistency.
4. **Provenance-first modelling.** `research`, `year_source`, decision documents, overrides, and review queues preserve why values exist rather than silently overwriting history.
5. **Safe intake design.** Empty discovery queues remain published as standing lanes rather than being removed and recreated ad hoc.

### Risks and recommendations

- **P2 — complexity concentration:** `pipeline/enrichments.py` is 650 lines and `build_catalogue_pages.py` is 942 lines. Continue extracting cohesive transforms and serializers before adding rules.
- **P2 — uneven module coverage:** overall coverage is strong, but `pipeline/helpers.py` is 78%, `relationships.py` 82%, and `validators.py` 85%. Add boundary/error-path tests rather than chasing superficial line coverage.
- **P3 — committed derived-data weight:** published and draft JSON intentionally duplicate data for static hosting/auditability. Keep this trade-off documented and monitor diffs; do not introduce further mirrors without a validator.
- **Owner dependency:** issue #18 requires access to the private Drive inventory and cannot be resolved from repository evidence.

## Full-stack engineering audit

### Strengths

1. **Appropriate architecture.** A static site is the lowest-risk deployment model for a read-only catalogue; there is no unnecessary server or database.
2. **Modularized frontend core.** The monolithic app has been partially decomposed into focused ES modules with direct Node regression coverage.
3. **Race handling.** View loading uses abort signals/current-view checks so stale responses cannot replace a newly selected dataset.
4. **Delivery integrity.** Asset and payload hashes are recorded in `build-manifest.json`; contract tests force cache-version/build-ID refreshes.
5. **Dependency hygiene.** Python CI constraints are pinned, npm lockfile is present, and npm reports zero known vulnerabilities.
6. **Export completeness.** CSV and dependency-free ODS export support the owner’s spreadsheet workflow while preserving humanized headers and color blocks.

### Risks and recommendations

- **P1 — CI static-analysis gap:** CI syntax-checks `docs/app.js` and specs but not `docs/js/*.js`; it also has no `no-undef` lint. Add module syntax checks and ESLint to catch missing imports/globals before browser tests.
- **P1 owner action — deployment race:** convert Pages from legacy `main:/docs` publication to a GitHub Actions deployment that depends on validation success.
- **P2 — oversized frontend files:** `docs/app.js` is 1,828 lines and `style.css` is 2,162 lines. Continue extraction by feature (drawer/modal, export orchestration, storage/state; base/components/views/responsive CSS).
- **P2 — test command ergonomics:** `npm test` is absent. A standard aggregate script should run unit tests and, where browsers are installed, E2E tests; this avoids false starts for contributors and automation.
- **P2 — browser setup clarity:** E2E requires `npm run test:e2e:install`. CI handles this correctly, but local failure output can look like product breakage; consider a preflight script that distinguishes missing browser binaries.
- **P3 — CSP debt:** inline styles remain allowed. Scripts are substantially better protected through hash pinning/SRI; eliminate inline style needs gradually rather than weakening script policy.

## Web design, UX, and accessibility audit

### Strengths

1. **Good audience layering.** Visitor-first columns reduce cognitive load; expert metadata remains one toggle away and row details expose all stored fields.
2. **Responsive interaction model.** Mobile defaults to browse cards with series/timeline discovery and preserves a spreadsheet escape hatch with independent two-axis scrolling.
3. **Useful visual system.** CSS custom properties, dark mode, consistent badges, restrained block colors, density/wrapping controls, and loading/error states form a coherent design language.
4. **Strong navigation for a data-heavy app.** The Jump-to selector scales better than a crowded tab strip across the catalogue and review workspaces.
5. **Accessibility fundamentals.** Semantic controls, labels/states, keyboard shortcuts, focus-managed dialogs/drawers, focus return, and contrast tests are present.
6. **Read-only clarity.** Published catalogue views do not imply in-browser editing and exports make downstream work explicit.

### Risks and recommendations

- **P1 owner review:** explicit visual acceptance remains necessary; hash and automated checks cannot judge scanability, hierarchy, or whether REVISION1 colors match owner expectations.
- **P2 — automated accessibility depth:** add axe-core checks for representative desktop/mobile states and periodic Lighthouse runs. Existing tests cover important mechanics but not the complete accessibility tree.
- **P2 — density/complexity:** 19 workspaces plus many display controls remain inherently demanding. Test the default first-run path with a real user before adding controls; prefer progressive disclosure.
- **P3 — stylesheet maintainability:** split the 2,162-line stylesheet without changing cascade order, and add visual regression snapshots for the highest-risk desktop/mobile states first.
- **P3 — external asset resilience:** Tabulator is CDN-hosted with SRI. This is secure but still availability-dependent; self-host only if offline/reliability requirements justify the repository cost.

## Security and privacy

The static architecture has a small attack surface: no authentication, server-side execution, user database, analytics, or secrets are present in the delivered app. External links use `noopener noreferrer`; data URLs are HTTPS; npm audit is clean. Dynamic HTML construction deserves continued scrutiny, but formatter utilities and tests provide safer rendering boundaries. The residual concerns are CSP `unsafe-inline`, third-party CDN availability, and ensuring future data inserted into HTML remains escaped.

## Documentation and repository audit

Documentation is comprehensive and unusually strong on decision provenance. The weakness is volume: many historical audits can obscure the current truth. The `archive/` convention and “current audit” pointers help, but every new audit should update only the canonical pointer/handoff and avoid duplicating operational instructions in multiple live files. Root documentation should remain normative; dated reports should remain evidence, not policy.

## Prioritized action plan

1. **Owner:** switch Pages to CI-gated Actions deployment.
2. **Owner:** visually accept the deployed desktop/mobile experience and REVISION1 colors.
3. **Agent-safe:** syntax-check all `docs/js/*.js` in CI and add ESLint `no-undef`.
4. **Agent-safe:** add a conventional `npm test` aggregate/preflight command.
5. **Agent-safe:** add focused tests for helper/relationship/validator error boundaries.
6. **Agent-safe:** incrementally split `app.js`, `style.css`, `enrichments.py`, and `build_catalogue_pages.py` behind existing contract tests.
7. **Optional:** add axe-core/Lighthouse automation and a small visual-regression baseline.
8. **Owner + agent:** resolve issue #18 when Drive evidence is available.

## Final assessment

DocSheet is production-capable and data-governance mature. Its strongest quality is not merely test count but the combination of reviewed overlays, deterministic generation, tamper detection, provenance, and a delivery manifest. Its remaining weaknesses are operational gating and maintainability at scale—not current catalogue correctness. Retain the existing **8.1/10 conditional-pass** score until Pages is CI-gated and the owner accepts the visual result.