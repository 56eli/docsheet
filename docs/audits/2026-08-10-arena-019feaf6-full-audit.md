# Full Multidisciplinary Audit — Arena 019feaf6

**Date:** 2026-08-10
**Audited baseline:** `aa1f1b76465e140b9cb62761d365765f0541d7d8` (`main`, PR #63 merge)
**Disciplines:** Web Design, Full-Stack Development, Data Engineering, Security, Accessibility, Delivery
**Method:** Fresh static review, deterministic builds, data recomputation, unit/coverage execution, dependency audit, GitHub Actions/Pages inspection, and targeted JavaScript runtime probes. Prior audits were treated as hypotheses, not evidence.

## Executive verdict

DocSheet has an excellent deterministic data pipeline and a thoughtful static catalogue design, but the PR #63 frontend extraction introduced a confirmed runtime defect into the currently deployed baseline: `docs/js/columns.js` calls `isExtraEditionRow()` without importing it. A direct module probe reproduces `ReferenceError: isExtraEditionRow is not defined`; main CI run `31373716254` then failed **25/25 Playwright specs** because no `.tabulator-row` rendered. Legacy GitHub Pages had already deployed the commit successfully before that CI failure. This is the same delivery-risk class documented in the prior row-delivery incidents and makes frontend repair plus CI-gated Pages the immediate priorities.

**Discipline scores at the audited baseline**

| Discipline | Score | Verdict |
|---|---:|---|
| Data engineering | **9.0/10** | Deterministic, reconciled, well validated; no data-integrity defect found |
| Web design / UX system | **7.5/10** | Strong responsive visual system and interaction model, reduced by unverified runtime delivery, dead UI layers, and a dialog accessibility defect |
| Full-stack engineering | **7.0/10** | Sound architecture and strong tests, but a production free-variable regression escaped offline checks |
| Security / privacy | **8.0/10** | Appropriate CSP/SRI/read-only posture; limited documented inline-style debt |
| Delivery / operations | **4.5/10** | CI is broad but Pages is still legacy and deployed the baseline before browser validation |
| **Overall repo readiness** | **7.1/10** | **Fail until the P0 frontend defect is repaired and browser CI is green** |

## P0 follow-up implementation on branch 019feaf6

After the audit, the owner selected the recommended P0 repair. This branch now imports `isExtraEditionRow` in `columns.js`, removes redundant imports from `app.js`/`mobile.js`, refreshes the content-version contract, and adds two executable regression layers:

- `tests/frontend-modules.test.mjs` invokes the edition formatter directly and verifies that only Power vs. Force row 373 renders the Extra badge;
- a new Playwright case records page errors, searches for the original hardcover, and asserts its rendered Extra badge, bringing the browser suite from 25 to 26 specs.

`pretest:e2e` runs the Node test automatically before Playwright. Local results are green for the Node test (1/1), Python suite (149/149), 90% coverage, all six checks, syntax, npm audit, and pip check. Local Playwright remains blocked by the sandbox's Chromium-download `ECONNRESET`; a dispatched GitHub browser run is therefore the remaining P0 acceptance gate. The scores below intentionally describe the audited/deployed `aa1f1b7` baseline until that browser run and deployment are verified.

## Priority findings

### P0 — `columns.js` has a production `ReferenceError`

**Evidence**

- `docs/js/columns.js:242` calls `isExtraEditionRow(row)` inside the `edition` formatter.
- The module imports configuration and formatter helpers only; it never imports `isExtraEditionRow` from `docs/js/data-utils.js`.
- `docs/app.js` imports `isExtraEditionRow`, but ES-module bindings are module-scoped and do not become globals available to `columns.js`.
- A direct Node ES-module probe with the minimum DOM shim executes the formatter and returns:

  ```text
  ReferenceError: isExtraEditionRow is not defined
  ```

**Impact**

Every curated row has an `edition` field, so Tabulator reaches this formatter during the primary Everything-view render. Depending on Tabulator's internal error path, this can suppress row rendering or leave edition cells broken. The defect is not theoretical and should be treated as a release blocker.

**Why existing guards missed it**

- `node --check` validates syntax, not unresolved identifiers.
- `FrontendDeliveryContractTests.test_app_js_invokes_every_named_import` examines only the first import block in `app.js`; it does not inspect imports or free variables in extracted modules.
- The 149 Python tests do not execute ES-module formatter bodies.
- Browser CI is the first check capable of detecting this class, but legacy Pages deploys independently and already reported success for commit `aa1f1b7` while CI was still running.

**Required fix**

Import `isExtraEditionRow` in `columns.js`, remove redundant imports from `app.js`/`mobile.js`, add a module-level runtime test that invokes every column formatter, refresh all content hashes, and require browser CI before deployment.

### P0 — GitHub Pages remains independent of CI

GitHub's Pages API reports:

```json
{"build_type":"legacy","source":{"branch":"main","path":"/docs"}}
```

The Pages build for `aa1f1b7` completed successfully at 09:15 UTC while the `CI` workflow's browser step was still in progress. At 09:25 UTC CI run `31373716254` failed all 25 browser specs: every suite waited for a first `.tabulator-row` that never appeared. A Pages artifact success therefore says only that files were copied; it does not prove the application rendered. The owner-applied procedure in `.scoreboard/manual-workflow-edits.md` remains necessary:

1. require `Validate data pipeline and site` before merge;
2. deploy Pages only after successful `main` CI;
3. verify the manifest revision, asset hashes, row count, and browser screenshot after deploy.

### P1 — Search highlighting became stale during module extraction

`app.js` passes the current string value of `activeSearchQuery` into `buildColumns(...)` once, during table initialization. The extracted formatter closures in `columns.js` capture that primitive value. A targeted formatter probe confirms the query received later is still `""`; changing the app's module variable cannot mutate the copied argument.

Filtering still uses the live `activeSearchQuery`, but cell `<mark class="search-highlight">` rendering no longer follows later search input. Pass a getter such as `() => activeSearchQuery`, or pass the live query during formatter execution, and add a browser assertion that searched text receives `.search-highlight`.

### P1 — Nested module imports bypass the new content-version contract

`app.js` imports all seven modules with `?v=<sha-prefix>`, and the manifest records their hashes. However, extracted modules import one another with unversioned URLs:

- `columns.js` → `./config.js`, `./formatters.js`
- `formatters.js` → `./config.js`
- `mobile.js` → `./data-utils.js`, `./formatters.js`
- `filter-utils.js` → `./config.js`
- `view-utils.js` → `./config.js`, `./data-utils.js`, `./mobile.js`

In browser module identity, `config.js?v=...` and `config.js` are different URLs. The graph can therefore fetch and evaluate both versioned and unversioned copies, and nested imports can use stale cached bytes even while the top-level contract passes. This also duplicates stateless modules during initial load.

Use one consistent strategy: version every edge, generate an import map, or bundle the frontend. Extend the contract test to traverse every static import, not only imports originating in `app.js`.

### P1 — Frontend contains a removed UI still implemented in JavaScript and CSS

Ten IDs looked up by `app.js` do not exist in `index.html`:

```text
catalogue-intro, hero, hero-dismiss, overview-btn, overview-cards,
review-nav-groups, review-nav-toggle, series-strip-list,
show-stats-toggle, stats-strip
```

Most references are null-guarded, so they silently no-op. The repository nevertheless retains overview-card builders, catalogue-intro state, hero handlers, collection/series rendering, review-navigation state, and large CSS sections for these absent elements. Handoff/audit documents still describe the hero, stats strip, and series strip as shipped.

Choose one direction explicitly:

- restore the intended HTML and test the feature, or
- remove the unreachable JS/CSS/imports and correct documentation.

Do not keep both a simplified interface and the old interface's dormant implementation.

### P2 — Keyboard-shortcuts dialog is not a complete modal

`toggleShortcutsHelp()` creates `role="dialog"`, but it does not set `aria-modal`, move focus to the Close button, trap focus, restore prior focus, or close on Escape. The dialog itself promises “Esc — Close dialogs,” while the global Escape handler closes menus and row details only. The row-details drawer already implements the correct focus lifecycle and can be reused.

### P2 — Static quality tooling does not cover the extracted frontend

Strengths:

- Python syntax checks pass recursively.
- JavaScript syntax checks pass for `app.js`, all seven modules, Playwright config, and all specs.
- Python tests enforce deterministic generation and an 85% coverage floor.

Gaps:

- Ruff is neither declared nor run in CI despite historical documentation saying “ruff clean.”
- No ESLint/no-undef check exists, which would have caught the P0.
- No JS unit tests execute pure utilities or column formatters.
- No automated axe-core or Lighthouse pass exists.
- `pipeline/helpers.py` is 78% covered and `pipeline/relationships.py` is 82%; total coverage remains strong at 90%.

### P2 — Canonical documentation had contradictory current state

Before this audit:

- `.scoreboard/scoreboard.yml` said summary gate `pass` at 8.3 while its own `quality_gates.repo_ready` said `fail` at 7.8.
- `SCOREBOARD.md` said 8.5/pass.
- the declared-current audit described pre-fix sizes (`app.js` 2,439 lines), an already-resolved module-manifest gap, and a deploy-row assertion already changed to dynamic metadata;
- `AGENTS.md` and the manual workflow proposal still said 141 tests while the suite contains 149;
- `NEXT_AGENT_HANDOFF.md` opened with an older branch/session and had grown to 741 lines of repeated history.

This audit accompanies a documentation reconciliation: a single current audit, a concise current handoff, synchronized test counts/gate status, and archival of three completed temporary/session documents.

## Web design and UX audit

### What is strong

- **Design tokens:** neutral light/dark surfaces, consistent accent semantics, and a restrained spreadsheet-first aesthetic.
- **Table readability:** single-line headers, measured content widths, frozen lead fields, work-family grouping, zebra parity, block accent rails, visible horizontal scrolling, and configurable density/wrapping.
- **Responsive model:** desktop spreadsheet plus optional Browse cards; mobile defaults to work-grouped cards with Source/Stream actions, Series and Timeline rails, and a Spreadsheet escape hatch.
- **Progressive disclosure:** visitor-facing columns first, Expert columns and per-column controls available on demand, full row details in a drawer.
- **Interaction coverage:** global search, multi-select facets, chips, review filters, export, per-view persistence, keyboard movement, dark mode, and standing empty-state lanes.
- **Accessibility foundations:** semantic controls, accessible names, focus-visible styles, reduced-motion rules, roving tab navigation, row labels, and a robust row-details focus trap.
- **Visual regression guards:** eight Python contrast tests plus browser computed-style checks for zebra/block accents.

### What should improve

1. Repair and browser-verify the current formatter runtime before judging visual acceptance.
2. Resolve the dead hero/stats/review-nav implementation rather than carrying invisible design layers.
3. Add axe-core scans for desktop spreadsheet, mobile Browse mode, empty review lane, and both dialogs.
4. Fix the shortcuts modal focus/Escape lifecycle.
5. Add a small viewport matrix (360, 390, 768, 1280, 1440) and screenshot artifacts after successful browser CI.
6. Keep CSS consolidation incremental: `style.css` is 2,398 lines with 11 media-query blocks and many historical override layers. The previous session reduced it by 165 lines, but component ownership is still difficult to trace.

## Full-stack architecture audit

### Architecture map

```text
Raw lane
  Google Sheets CSV (decorative row + 374 data rows)
    -> process_data.py / pandas
    -> docs/data.json (374 rows, 7 visible fields)

Curated lane
  migration_review_ledger.csv + reviewed data/*.csv overlays
    -> build_research_master.py + pipeline/{helpers,enrichments,validators}
    -> data/research_master_draft.{csv,json}
    -> build_catalogue_pages.py + pipeline/relationships.py
    -> 19 user-facing JSON sheets + catalogue metadata/block map

Frontend
  docs/index.html + app.js + 7 ES modules + style.css
    -> Tabulator 6.5.2 from SRI-pinned CDN
    -> GitHub Pages legacy main:/docs deployment
```

### Strengths

- Raw and curated lanes are clearly separated.
- Generated master/Pages files are not intended for manual edits.
- Six generators expose read-only `--check` modes and all six pass.
- Builders validate schemas, controlled vocabularies, display order, relationships, candidates, work families, filenames, source mirrors, and reconciliation.
- Fetcher behavior includes retry/failure-path tests and review-only inventory updates.
- Frontend view activation uses `AbortController` plus a monotonic token to prevent stale responses replacing the active sheet.
- URLs and user-visible text are created with DOM nodes/text content; external links include `noopener noreferrer`.
- Dependencies are small and pinned for CI.

### Maintainability concerns

- `app.js` is improved from 2,769 to 1,933 lines but still contains 83 named functions and centralizes state, boot, navigation, drawers, filters, export, and Tabulator orchestration.
- `style.css` remains 2,398 lines and includes styling for absent components.
- `build_catalogue_pages.py` is 942 lines and `pipeline/enrichments.py` is 650 lines; both are understandable but approaching another extraction threshold.
- Build-manifest/hash maintenance is manual. Tests detect forgotten updates but do not generate the correct manifest.
- The import-use test is structurally incomplete: it checks one `app.js` import block and token presence, not actual module execution or all imports.
- Historical handoffs/audits duplicate substantial state and can contradict current files.

## Data engineering audit

### Independently reproduced state

| Dataset / invariant | Result |
|---|---:|
| Raw published rows | 374 (31 blank separator rows retained in JSON; hidden by default in UI) |
| Curated master rows | 363 |
| Unique master IDs | 363; 0 duplicates |
| Work IDs | 191; 0 blank |
| Catalogue codes | 278; 278 unique; 0 invalid patterns |
| Proposed filenames | 363; 363 unique; 0 blank |
| Item types | 306 lecture, 41 book, 8 discussion, 7 highlight, 1 other |
| Formats | 253 DVD, 32 CD, 32 book, 27 audiobook, 19 streaming |
| Ownership | 312 true, 25 false, 26 blank |
| Display order | 363 IDs, complete coverage, 12 blocks, each block position dense |
| Exclusions | 75 |
| Approved source overrides | 134 |
| Manual candidates | 40 |
| Manual leads | 4 |
| Product relationships | 340 reviewed (333 derived primary + 7 related material) |
| Series compilations | 7 reviewed |
| Veritas products | 191 |
| Hay House / Audible products | 29 / 26 |
| International products | 38 |
| Series mappings | 186; review queue empty |

### Integrity results

- All six generated-output checks pass.
- Reconciliation report is byte-current.
- No duplicate master ID, catalogue code, or filename was found.
- Display-order IDs exactly equal master IDs; all 12 block-position ranges are dense.
- Product relationship master IDs resolve; series compilations resolve through reviewed target-series metadata.
- All non-empty master URL fields use HTTPS.
- Required master fields (`record_type`, `uuid`, `work_id`, title, filename, item type, series, year source, format) are complete.
- Blank years (19), months (126), ownership values (26), and source fields match documented semantics rather than validator leakage.
- `npm audit` reports zero vulnerabilities; `pip check` reports no broken requirements.

### Data risks and next improvements

1. Open issue #18 still requires owner access to cross-check ownership flags against the lak.nz Drive working library.
2. Continue treating blank year/month/owned as meaningful tri-state/provenance states; do not bulk-fill them.
3. Add direct tests for `pipeline/helpers.py` CSV failure paths if coverage is raised beyond the current 85% floor.
4. Consider a generated schema/data dictionary (field, type, controlled vocabulary, null semantics, source) to reduce the amount of prose needed across README and handoffs.

## Security and privacy

| Control | Assessment |
|---|---|
| Secrets | No credential/token/private-key pattern found in tracked runtime/data files |
| Runtime write surface | None; published site is read-only static content |
| CSP | Strong default/script/connect/object restrictions; inline script hash pinned |
| Third-party code | Tabulator version pinned and protected with SRI/crossorigin |
| External links | `noopener noreferrer` used |
| DOM injection | Dynamic record data uses DOM APIs/text content; fixed internal templates use `innerHTML` |
| Dependency audit | npm 0 vulnerabilities; pip dependency graph consistent |
| Remaining debt | `style-src 'unsafe-inline'` and Google Fonts/CDN availability; low severity for current data model |

No personal-data collection, authentication, cookies, backend, or database exists. The primary security risk is supply/delivery integrity rather than account or PII exposure.

## Performance assessment

- Largest payloads: `master.json` 394 KB, `migration-review.json` 364 KB, `product-relationships.json` 324 KB, `filename-proposal.json` 184 KB.
- App/style are approximately 78 KB/80 KB before transfer compression.
- Tabulator virtualizes rows and the largest active sheet is only 374 rows.
- Column width calculation scans every cell on view activation; at this dataset size it is reasonable.
- Search/facets are linear over the active sheet and appropriate at current scale.
- Nested versioned/unversioned module imports create avoidable duplicate requests/evaluation.
- No Lighthouse/Web Vitals measurement or performance budget exists, so the performance score remains medium-confidence.

## Verification ledger

### Passed locally

```text
6/6 generator --check modes                                      PASS
python -m unittest discover tests: 149/149                       PASS
coverage: 2327 statements, 229 missed, 90% total (floor 85%)     PASS
python -m py_compile *.py pipeline/*.py tests/*.py               PASS
node --check app.js + 7 modules + config/specs                   PASS
npm audit (production and all): 0 vulnerabilities                PASS
pip check                                                        PASS
manifest/module/content-version contract tests                   PASS
independent data counts/referential/display-order probes         PASS
```

### Failed or constrained

```text
Targeted columns.js edition formatter probe                      FAIL
  ReferenceError: isExtraEditionRow is not defined

Local Playwright                                                 NOT RUN
  Chromium download failed with ECONNRESET in this sandbox.
  This is an environment download constraint, not a test assertion result.

Live-site curl/hash probe                                        NOT RUN
  TLS connection to 56eli.github.io was blocked in this sandbox.
  GitHub API still confirmed Pages build_type=legacy and successful deploy.
```

### GitHub evidence

- Main Pages run for `aa1f1b7`: completed successfully before CI.
- Main CI run `31373716254` for `aa1f1b7`: Python/check/coverage/syntax/install stages passed, then all **25/25 Playwright specs failed** because `.tabulator-row` never rendered; the failure report was uploaded.
- Prior main commit `3768fe7` had a fully successful CI run, but that does not validate PR #63's extracted modules.

## Recommended sequence

1. **P0:** repair the missing `isExtraEditionRow` import and add executable module/formatter coverage.
2. **P0:** run the added Node formatter regression plus all 26 Playwright specs, then verify the exact deployed build ID/hashes/screenshots.
3. **P0 owner action:** require CI and switch Pages from legacy branch deployment to the gated workflow.
4. **P1:** fix the stale search-highlight closure and test highlighting, not only filtering.
5. **P1:** make cache versioning consistent across the full module graph.
6. **P1:** decide whether to restore or delete the absent hero/stats/review-nav feature set.
7. **P2:** complete shortcuts-dialog accessibility and add axe-core checks.
8. **P2:** add ESLint `no-undef` (or equivalent) and execute pure JS modules in unit tests.
9. **P3:** continue splitting `app.js` by orchestration boundary only after the regression tests exist.
10. **Owner/data:** resolve issue #18 when the Drive inventory is available.

## Final assessment

The catalogue data itself is trustworthy and the architecture is fundamentally good. The current problem is release discipline around a fast-moving frontend: static hash checks and Python contract tests can prove byte consistency while still missing executable JavaScript defects. The next iteration should prioritize a repaired browser build, full-module runtime/lint coverage, and deployment gating before any further visual redesign or modularization.
