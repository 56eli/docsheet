# Full Multidisciplinary Audit — Arena 019feb3e

**Date:** 2026-08-10 (10:42 UTC)
**Audited baseline:** `54b37f7` (`main`, "Merge PR #64: full audit and frontend hardening") — the *current* HEAD and the *currently deployed* live build.
**Disciplines:** Web Design / UX, Full-Stack Development, Data Engineering, Security, Delivery
**Method:** Fresh, read-only, first-hand review. I ran the entire verification suite myself (six `--check` modes, 149-test suite, coverage, Node module tests, recursive compile, JS syntax, `npm audit`, `pip check`), re-computed the data invariants independently with stdlib/pandas (bypassing the project's own validators), scanned the ES-module import graph for unresolved identifiers, inspected the GitHub Actions/Pages state through the GitHub API, and — uniquely this session — **proved the live deployment matches the repository byte-for-byte** by fetching the public `build-manifest.json` and the deployed `columns.js` through the network fetch tool. Prior audits were treated as hypotheses, not evidence.

## Executive verdict

The previously release-blocking frontend defect is **fixed, merged to `main`, and verified live**. PR #64 (`54b37f7`) is deployed: GitHub Pages built it at 10:34 UTC, the `main` CI run `31379726756` passed in 1m31s, and the public `build-manifest.json` is byte-identical to the committed manifest. The live `columns.js` contains `import { isExtraEditionRow } from "./data-utils.js?v=0288c69670bb"` — the exact line whose absence made PR #63 fail 25/25 browser specs. The "broken public baseline" verdict from the 019feaf6 audit is therefore **resolved**.

What remains is not a broken site but a **delivery-discipline gap**: GitHub Pages is still `build_type: legacy` serving `main:/docs` with no CI gate, so a future broken commit can still deploy before CI fails — exactly the race that shipped PR #63. There is also a small amount of residual dead UI code (the retired `.dataset-tab` tab bar) and a static-quality gap (CI syntax-checks `app.js` but not the extracted modules, and there is no `no-undef` lint). None of these are release blockers today; they are the highest-leverage improvements to prevent the next incident.

**Discipline scores at the audited baseline**

| Discipline | Score | Verdict |
|---|---:|---|
| Data engineering | **9.0/10** | Deterministic, reconciled, well-validated; no integrity defect found |
| Web design / UX system | **8.0/10** | Strong responsive visual system and interaction model; minor dead-code and CSS-consolidation debt |
| Full-stack engineering | **8.0/10** | Sound architecture, strong tests, P0 fixed and verified live; module-lint / syntax-coverage gap |
| Security / privacy | **8.0/10** | Appropriate CSP/SRI/read-only posture; low-severity inline-style debt |
| Delivery / operations | **7.0/10** | Live site now healthy & byte-verified, but Pages remains legacy/ungated |
| **Overall repo readiness** | **8.2/10** | **Pass** (up from 7.1/FAIL) — broken-baseline blocker is gone; gate now rests on the ungated-deployment owner action and explicit owner acceptance |

## Verification ledger (all run by me this session)

```text
process_data.py --check                                    PASS  (374 rows, 7 view cols)
reconcile_research_master.py --check                       PASS  (reconciliation report current)
build_research_master.py --check                           PASS  (363 items, 75 excluded, 134 overrides)
build_catalogue_pages.py --check                           PASS  (363 Everything rows)
map_series_taxonomy.py --check                             PASS  (186 mappings, queue empty)
sync_inventory_mirrors.py --check                          PASS  (mirrors match master)
python -m unittest discover tests                          PASS  (149/149)
coverage run ... discover tests                            PASS  (2327 stmts, 90% total; floor 85%)
python -m py_compile *.py pipeline/*.py tests/*.py         PASS
node --check docs/app.js + 7 modules + config/specs        PASS
npm run test:unit (frontend-modules.test.mjs)              PASS  (3/3)
npm audit                                                  PASS  (0 vulnerabilities)
pip check                                                   PASS  (no broken requirements)
independent data-integrity probes (stdlib/pandas)          PASS  (see Data section)
ES-module unresolved-identifier scan                       PASS  (no P0-class free variable)
```

### Network verification (new this session — the prior audit could not reach the network)

```text
GitHub Pages API                                            build_type=legacy, source=main:/docs, status=built
Pages build for 54b37f7                                     built @ 10:34:31Z  (the repair is deployed)
Pages build for aa1f1b7 (prior broken baseline)            built @ 09:15:09Z  (deployed BEFORE its CI failed)
main CI run 31379726756 (54b37f7)                           success, 1m31s
main CI run 31373716254 (aa1f1b7)                           FAILURE, 9m51s  (25/25 browser specs)
https://…/docsheet/build-manifest.json                     byte-identical to committed manifest
https://…/docsheet/js/columns.js                            contains the isExtraEditionRow import (P0 fixed live)
```

### Environment-constrained (unchanged from prior sessions)

```text
Local Playwright                                            NOT RUN — Chromium download ECONNRESET in sandbox
```

The PR #64 CI run already proved 28/28 Playwright specs pass, and I verified the deployed build carries the fix, so this constraint does not weaken the conclusion.

## Priority findings

### P1 — GitHub Pages is still legacy and can deploy before CI (OWNER action)

The Pages API still reports `build_type: legacy`, `source: {branch: main, path: /docs}`. The Pages build for the *current* repair (`54b37f7`) completed in 23s while CI took 1m31s; the Pages build for the *broken* `aa1f1b7` completed at 09:15Z while its CI failed at ~09:25Z. A legacy Pages success only proves files were copied — it does not prove the app rendered. Switching Pages to the Actions-based `workflow` build type (so the deploy job depends on the `Validate data pipeline and site` job) closes the entire incident class. The steps are already drafted in `.scoreboard/manual-workflow-edits.md`; this is the single highest-leverage owner action.

### P2 — CI does not syntax-check the extracted JS modules

`.github/workflows/ci.yml` runs:

```
node --check docs/app.js
node --check playwright.config.js
for spec in tests/*.spec.js; do node --check "$spec"; done
```

It never syntax-checks `docs/js/*.js` (the seven modules that PR #63 extracted). A syntax error in a module is only caught later, at browser-test time — if at all. The fix is one line in the workflow:

```yaml
for m in docs/js/*.js; do node --check "$m"; done
```

This does **not** catch the P0 class (an unresolved identifier is valid syntax), so it should be paired with the P2 lint item below.

### P2 — No `no-undef` static lint for the frontend

The P0 was an ES-module calling `isExtraEditionRow` it never imported — legal syntax, undefined at runtime, invisible to `node --check`, and only surfaced by the browser suite (which Pages outran). There is now a Node module regression test and the browser suite, but no fast, pre-browser static guard. Adding ESLint (or `eslint-plugin-import`) with `no-undef`/`no-unused-vars` to CI would have caught the P0 in milliseconds and is cheap insurance against the same class recurring as `app.js` keeps splitting. My unresolved-identifier scan this session confirms the current graph is clean, so this is preventive.

### P3 — Residual dead code: the retired `.dataset-tab` tab bar

The catalogue tab bar was replaced by the "Jump to" dropdown (`#view-jump` in `index.html`), but the *implementation* was not fully removed:

- `docs/app.js` still queries `.dataset-tab` (lines 1438, 1644, 1651) and `.dataset-tabs` (line 1648) for arrow-key roving navigation — these now match zero elements and silently no-op.
- `docs/style.css` still styles `.dataset-tabs`, `.dataset-tab`, `.dataset-tab.review-tab`, `.dataset-tab.review-tab-start`, and a non-compact-density `.dataset-tab` override (~lines 361–389, 1427).

The PR #64 cleanup removed the hero/stats/overview/review-nav layers but missed this one. Neither path throws (all are null/empty-safe), so this is maintainability/clarity debt, not a bug. Removing the four JS lookups + arrow-key block and the tab-bar CSS would tighten the file and stop documentation/handoffs from implying a tab bar that no longer exists.

### P3 — Optional quality tooling not yet added

- No automated **axe-core** accessibility scan (the a11y foundations are strong — semantic controls, focus traps, roving tabindex, reduced-motion — but there is no automated regressions gate).
- No **Lighthouse** / Core Web Vitals budget (performance is fine at this dataset size, but it is unmeasured and medium-confidence).
- `pipeline/helpers.py` (78%) and `pipeline/relationships.py` (82%) are the lowest-covered modules; total is a healthy 90%.

### Owner-data item (unchanged) — Issue #18

Ownership cross-check against the lak.nz Drive working library still needs owner Drive access. Not an engineering blocker.

## Web design and UX audit

### What is strong (verified against the live and local build)

- **Design tokens:** a single `:root`/`:root.dark` token block (the duplicate-`:root` issue flagged in the 019fe830 audit is fixed), neutral warm-grey surfaces, consistent accent semantics, and a restrained spreadsheet-first aesthetic that matches the owner "sleek greys with accented groups" directive.
- **Table readability:** measured-pixel column widths (offscreen canvas, all rows, rendered labels), frozen lead fields, work-family grouping via `work_id` striping, block-accent rails (`row-block-*`), zebra parity, configurable density/wrapping, and one-click "Expand everything".
- **Responsive model:** desktop spreadsheet plus optional Browse cards; mobile defaults to work-grouped cards with Source/Stream actions, Series and Timeline rails, and a Spreadsheet escape hatch. The same `master.json` drives both; there is no separate mobile data contract.
- **Progressive disclosure:** visitor-facing product columns first; technical metadata (Master ID, Work, proposed file names, provenance) behind an Expert-columns toggle; full field set always in the details drawer.
- **Interaction coverage:** global live search with `<mark>` highlighting wired through a query getter (the stale-highlight P1 is fixed), multi-select facets, removable chips, review filters, full-view CSV export, per-view persistence (sort, scroll, columns, facets, expert, density), and standing empty-state intake lanes.
- **Accessibility foundations:** semantic controls with accessible names, focus-visible styles, reduced-motion rules, roving-tab navigation, a true modal row-details drawer with focus trap + restore, a shortcuts dialog with `aria-modal`/focus/Escape lifecycle, and eight Python contrast tests plus browser computed-style checks.
- **No-flash dark mode:** applied pre-paint from `localStorage` via an inline hash-pinned script.

### What should improve (design)

1. Remove the residual `.dataset-tab` tab bar (P3 above) so the code, CSS, and docs all describe the same "Jump to" dropdown interface.
2. Add an automated axe-core pass for desktop spreadsheet, mobile Browse, both dialogs, and the empty review lane.
3. Add a small viewport matrix (360/390/768/1280/1440) screenshot artifact to CI for visual regression.
4. Continue consolidating `style.css` incrementally (2,137 lines, 12 media-query blocks) toward component-owned sections; it is readable but approaching another extraction threshold.

## Full-stack architecture audit

```text
Raw lane      hawkins archive clone - Sheet1.csv → process_data.py → docs/data.json
Curated lane  migration_review_ledger.csv + reviewed data/*.csv overlays
                → build_research_master.py + pipeline/{helpers,enrichments,validators}
                → data/research_master_draft.{csv,json}
                → build_catalogue_pages.py + pipeline/relationships.py
                → 19 user-facing JSON sheets + catalogue metadata/block map
Frontend      docs/index.html + app.js (1,798 ln) + 7 ES modules + style.css (2,137 ln)
                → Tabulator 6.5.2 from SRI-pinned CDN
                → GitHub Pages legacy main:/docs deployment
```

### Strengths

- Raw and curated lanes are cleanly separated; generated master/Pages JSON is never meant to be hand-edited.
- Six generators expose read-only `--check` modes; all six pass. Builders validate schemas, controlled vocabularies, display order, relationships, candidates, work families, filenames, source mirrors, and reconciliation.
- View activation uses `AbortController` + a monotonic `viewActivation` token, so a stale JSON fetch can never mutate the active sheet.
- Dynamic record data is built with DOM nodes/text content; external links carry `noopener noreferrer`.
- A generic, visible fatal-render state now exists for async table failures (the error-handling P1 from 019feaf6 is addressed in `activateView`'s catch block).
- The frontend delivery contract (`FrontendDeliveryContractTests`) now traverses the **full** module import graph, not just `app.js`'s first import block.

### Maintainability concerns

- `app.js` is down to 1,798 lines (from 2,769) and is well-sectioned, but still centralizes state, boot, navigation, drawers, filters, export, and Tabulator orchestration (83 functions). Further extraction is sound only behind the Node/browser + full-import-graph contracts.
- `style.css` is 2,137 lines; component ownership is still hard to trace.
- `build_catalogue_pages.py` (942 ln) and `pipeline/enrichments.py` (650 ln) are understandable but approaching another extraction threshold.
- Build-manifest/hash maintenance is still manual. Tests detect a forgotten update but do not generate the correct manifest — a generator step would remove the toil and the failure mode.
- Many historical handoffs/audits duplicate state and can contradict current files (the 019feaf6 doc-reconciliation helped; a generated schema/data-dictionary would reduce the prose further).

## Data engineering audit

### Independently reproduced state (recomputed by me, not read from the docs)

| Dataset / invariant | Result |
|---|---:|
| Raw published rows | 374 (31 blank separator rows retained in JSON; hidden by default in UI) |
| Curated master rows | 363 |
| Unique master IDs | 363; **0 duplicates** |
| Work IDs | 363 present (0 blank); **191 unique** |
| Catalogue codes | **278; 278 unique**; 0 invalid patterns |
| Proposed filenames | **363; 363 unique**; 0 blank |
| Item types | 306 lecture / 41 book / 8 discussion / 7 highlight / 1 other |
| Formats | 253 DVD / 32 CD / 32 book / 27 audiobook / 19 streaming |
| Ownership | 312 true / 25 false / 26 blank (tri-state) |
| Non-HTTPS master URLs | **0** |
| Record types | 363 `master` (no candidates currently queued) |
| Veritas / Hay House / Audible products | 191 / 29 / 26 |
| International products | 38 |
| Series mappings | 186; review queue empty |

### Integrity results

- All six generated-output checks pass; reconciliation report is byte-current.
- No duplicate master ID, catalogue code, or filename.
- Every non-empty master URL is HTTPS.
- Controlled vocabularies (`CONTENT_ITEM_TYPES`, `EDITION_FORMATS`, `EDITION_ROLES`, `EDITION_SOURCES`, …) are enforced in `pipeline/validators.py` with explicit `ValueError`s; `audio`/`video` are rejected (retired 2026-08-03).
- `catalogue-meta.json` counts are internally consistent (master_items=migrated_items=363; everything_record_types.master=363).

### Data risks and next improvements

1. Issue #18 ownership cross-check still needs owner Drive access.
2. Keep treating blank year/month/owned as meaningful tri-state/provenance states — do not bulk-fill.
3. A generated schema/data dictionary (field, type, controlled vocabulary, null semantics, source) would cut the prose now spread across README/handoffs/decision docs and reduce drift.

## Security and privacy

| Control | Assessment |
|---|---|
| Secrets | No credential/token/private-key pattern in tracked runtime/data files (scan matched only design-token text in audit docs) |
| Runtime write surface | None — published site is read-only static |
| CSP | Strong `default-src 'self'`; `script-src` self + pinned CDN + one hash-pinned inline dark-mode script; `object-src 'none'`; `connect-src 'self'` |
| Third-party code | Tabulator pinned at 6.5.2 with SRI `integrity` + `crossorigin` |
| External links | `noopener noreferrer` throughout |
| DOM injection | Record data via DOM APIs/text content; the shortcuts/help template and a couple of fixed internal strings use `innerHTML` with no record data |
| Dependency audit | npm 0 vulnerabilities; `pip check` clean |
| Remaining debt | `style-src 'unsafe-inline'` (low severity for this data model); Google Fonts/CDN availability |

No PII, auth, cookies, backend, or database. The primary risk surface is supply/delivery integrity, which is exactly what the P1 Pages-gating item addresses.

## Recommended sequence

1. **OWNER (highest leverage):** switch Pages from legacy `main:/docs` to the Actions `workflow` build type so deploy depends on a green `Validate data pipeline and site` job. Steps are in `.scoreboard/manual-workflow-edits.md`.
2. **OWNER:** obtain explicit visual acceptance of the live build (it is now byte-verified, but acceptance is an owner call per the `acceptance: owner_visual_review_required` manifest field).
3. **Quick CI wins (agent-safe):** add `node --check docs/js/*.js` to the workflow; add an ESLint `no-undef`/`no-unused-vars` step.
4. **Cleanup (agent-safe):** remove the residual `.dataset-tab` JS lookups + arrow-key block and the tab-bar CSS; verify the Node/browser contract stays green.
5. **Optional:** add axe-core + a Lighthouse/Web-Vitals budget; raise coverage on `helpers.py`/`relationships.py`.
6. **OWNER/data:** resolve issue #18 when Drive access is available.

## Final assessment

The catalogue data is trustworthy and the architecture is fundamentally sound. The incident that previously failed the gate — a deployed-but-broken frontend — is now closed: the repair is on `main`, CI is green, and I have proved the live deployment is byte-identical to the source and carries the fix. The project is at a passing readiness level. The work that remains is preventive delivery discipline (CI-gated Pages) and a few low-severity cleanup/quality items, none of which block the current healthy live site.
