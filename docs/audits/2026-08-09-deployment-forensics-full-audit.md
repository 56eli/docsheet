# Full-Stack, Data, and Deployment Forensics Audit — 2026-08-09

**Repository:** `56eli/docsheet`  
**Audited baseline:** `ea4e30d` (`main`)  
**Audit branch:** `arena/019fe7b6-docsheet`  
**Auditor role:** expert Full-Stack Developer and Data Engineer  
**Status:** current audit; P0 CI regression fixed on this branch, workflow-governance improvements remain open

## 1. Executive verdict

The recent red Actions were **not GitHub Pages deployment failures** and did **not block the REVISION1 row corrections**: eleven CI runs failed on one stale Playwright selector after the stats UI was deleted, while every corresponding Pages deployment succeeded; the corrected rows are present in the deployed commit's curated `docs/master.json`, but by design they do not appear in the separate raw **Original Spreadsheet** payload.

## 2. What happened, precisely

### 2.1 The failure chain

Commit `255d937` (PR #48, 2026-08-09 16:17 UTC) removed these controls from `docs/index.html`:

- `#show-stats-toggle`
- `#stats-strip`
- `.stat-chip[data-jump=...]`

The same commit left `tests/ux-enhancements.spec.js` waiting for `#show-stats-toggle` at the old line 70. That locator can never resolve. Each browser run waited for the full 45-second test timeout and then reported:

```text
1 failed: stats chips and task jump menu navigate to their sheets
24 passed
locator('#show-stats-toggle').check(): Test timeout of 45000ms exceeded
```

From PR #48 through the latest `main` push, this produced **11 failed CI runs** (plus one cancelled superseded run):

| Scope | Commits / PRs | Result | Common cause |
|---|---|---|---|
| Pull requests | #48, #49, #50, #51 (two heads), #52 | 6 failures | Removed `#show-stats-toggle` still referenced by Playwright |
| `main` pushes | `255d937`, `c884138`, `52833cf`, `25906ad`, `ea4e30d` | 5 failures | Same single stale test |

Every Python install, all six generator checks, the then-current 132–139 deterministic tests, the 85% coverage gate, JavaScript syntax, `npm ci`, and Chromium installation passed in those runs. Only the browser smoke-test step failed.

### 2.2 The Pages deployments did not fail

GitHub Pages uses legacy branch deployment from `main:/docs`. It runs independently of `ci.yml`.

- Latest Pages build API state: `built`
- Latest Pages build commit: `ea4e30d00b9e830d54d3e00710d84a5b73e6c085`
- Latest deployment ID: `5821353112`
- Latest deployment status: `success`
- Latest environment URL: `https://56eli.github.io/docsheet/`
- All seven Pages runs from the REVISION1 merge through `ea4e30d` completed successfully.

This distinction matters: a red **CI** badge currently does not stop a green **Pages** deployment. In fact, the current deployment model permits a broken change to go live while CI is red.

### 2.3 The row-fix commit did deploy

The owner-reviewed REVISION1 changes merged in PR #46 as `a981641` at 15:22 UTC.

| Signal | Evidence |
|---|---|
| PR #46 CI | Run `31320944866`: success |
| PR #46 Pages | Run `31320944218`: success, completed at 15:24 UTC |
| Current Pages build | `ea4e30d`, which descends from `a981641` |
| Current `main` file contents | GitHub Contents API bytes for `docs/master.json`, `docs/filename-proposal.json`, `docs/data.json`, `docs/app.js`, and `docs/style.css` match this checkout exactly |
| Current correction payload | UUIDs 312, 315, 356, 357, and 358 carry the approved values in `docs/master.json` |

The current curated payload includes, among the reviewed changes:

- UUID 312: `2012 - DISCUSSION - Permanent Inner Peace.mp4`
- UUID 315: notes = `FRAN GRACE`
- UUID 356: year/month blank; no false 2014 filename prefix
- UUID 357: year = `2003`; `2003 - OTR - Peace is the Natural State.mp3`
- UUID 358: year/month blank; no false 2025 filename prefix
- 32 of 33 On-the-Road records carry the reviewed `OTR - ` convention (UUID 342 is the separately retained audiobook exception)
- Eight discussion filenames carry `DISCUSSION - `
- Sixteen Office filenames carry `198X - A-01…B-06`

### 2.4 Why the fixes could look absent

The site has **two intentionally separate data products**:

```text
Raw source CSV
  └─ process_data.py ─> docs/data.json ─> Original Spreadsheet

Migration ledger + reviewed overlays + candidates + inventories
  └─ build_research_master.py
  └─ build_catalogue_pages.py ─> docs/master.json ─> Everything
```

The REVISION1 ODS updated curated overlays and generated catalogue files, not `hawkins archive clone - Sheet1.csv`. Therefore:

- the corrected records appear in **Everything** (`docs/master.json`);
- they do not alter **Original Spreadsheet** (`docs/data.json`);
- several corrected UUIDs are promoted/manual catalogue records and do not exist in the raw CSV at all;
- no `Update Spreadsheet` workflow was expected for PR #46, because that workflow triggers only when the raw CSV changes.

All three `Update Spreadsheet` runs in the available history succeeded. It was not involved in this incident.

## 3. Remediation applied on this branch

### F-01 — Stale Playwright selector caused the red CI cascade (P0, resolved)

`tests/ux-enhancements.spec.js` now tests the surviving `#view-jump` navigation across Manual Leads, Product Relationships, and Everything. It no longer references deleted stats controls.

### F-02 — No regression guard proved the owner corrections reached the Pages payload (P0, resolved)

A deterministic test now reads the actual committed `docs/master.json` and locks the approved values for UUIDs 312, 315, 356, 357, and 358. The offline suite is now **140 tests**.

### F-03 — Browser-suite count was stale (P2, resolved in current docs)

The UI simplification reduced Playwright from 26 to **25 specs** (1 blank-row + 4 column-layout + 5 CSV/export + 6 presentation + 9 UX). Current operational documentation and scoreboard evidence are corrected; historical audit statements remain historical.

## 4. Full audit matrix

| Area | Verdict | Evidence / assessment |
|---|---|---|
| Product/data architecture | **Good, but confusing at the UI/operations boundary** | Raw and curated pipelines are correctly separated, deterministic, and documented; their live-view distinction is easy to miss. |
| Raw pipeline | **Pass** | 374 rows × 7 published columns, 31 blank separator rows intentionally hidden by default; `process_data.py --check` passes. |
| Curated pipeline | **Pass** | 362 masters, 75 exclusions, 134 source overrides, 39 reviewed candidates; all generated outputs byte-current. |
| Data integrity | **Pass** | Zero duplicate master UUIDs, proposal UUIDs, order UUIDs, Veritas product IDs, relationship IDs, or filenames; zero blank master titles/types/work IDs/filenames. |
| Date integrity | **Pass** | 19 intentional blank years, 16 `198X` Office years, zero malformed years/months, zero blank `year_source` values. |
| URL integrity | **Pass** | 461 populated master URLs, all HTTPS, all parseable; zero orphaned primary Veritas URLs. |
| Display-order integrity | **Pass** | `docs/master.json` UUID order exactly matches the approved dense 362-row display-order overlay. |
| Tests | **Strong after F-01/F-02** | 140 offline tests pass; total coverage 90%; 25 Playwright specs are syntactically clean and the corrected selector path awaits CI confirmation. |
| Coverage claims | **Needs doc correction** | Total floor is correctly enforced at 85%, but current per-module results include `pipeline/helpers.py` 78% and `pipeline/relationships.py` 82%; the former “every pipeline module ≥88%” claim was false. |
| Frontend | **Functionally rich, maintainability debt** | Static read-only SPA, responsive browse/table modes, facets, CSV export, keyboard and drawer flows; `docs/app.js` is 2,692 lines and `docs/style.css` is 2,382 lines. |
| Frontend dead code | **Needs cleanup** | The deleted hero/overview/stats DOM still has nullable bindings, render functions, listeners, and many CSS selectors in `app.js`/`style.css`. |
| Accessibility | **Good manual baseline, incomplete automation** | Labels, focus handling, keyboard shortcuts, semantic controls; no axe/Lighthouse run in this sandbox. |
| Security/privacy | **Good for a static site** | Read-only same-origin JSON, hash-pinned inline script, SRI-pinned Tabulator 6.5.2, no discovered secrets, no PII collection; low-severity `style-src 'unsafe-inline'` remains. |
| Dependencies | **Pass** | Python CI constraints are reproducible; `npm audit` reports zero vulnerabilities; package lock is current. |
| Performance | **Adequate at current scale** | ~1.6 MB tracked JSON payloads; largest initial `master.json` is ~376 KB; client-side Tabulator is suitable for 362 rows. Dead JS/CSS and all-in-one SPA remain optimization opportunities. |
| CI | **Operational, not enforced** | The test regression is fixed, but merges occurred before failing checks completed, and Pages does not depend on CI success. |
| Pages | **Deploying reliably, insufficiently gated** | Every relevant Pages run succeeded and latest deployed SHA is current; no post-deploy content assertion or visible build fingerprint. |
| Documentation | **Thorough but overgrown** | Strong README/instructions/handoff/decision records; 20 root Markdown files plus 86 archived Markdown files, repeated audits, and stale claims increase search cost. |
| Agent readiness | **Good with a caution** | Six checks, tests, scoreboard, and handoff are strong; prior handoff incorrectly said CI was green and did not inspect the latest run. |
| Open product work | **Known** | Issue #18 (owned flags vs. lak.nz Drive) still needs owner data/access and a definition ruling. |

## 5. Remaining findings and priorities

### F-04 — Pages is not gated by CI (P1, open; workflow/settings change)

Observed PRs were merged seconds after creation or before checks completed, and all red `main` commits deployed successfully. Repository rulesets are empty; the classic branch-protection API was inaccessible to this integration, but actual merge behavior proves these checks were not required for the observed merges.

**Recommendation:** require `Validate data pipeline and site` before merge and move Pages to a CI-gated custom deployment workflow (or, at minimum, prevent merges until CI is green). This requires an owner-approved workflow/settings change.

### F-05 — There is no post-deploy assertion or visible build identity (P1, open)

The Pages API proves which SHA GitHub deployed, but the site itself does not expose a commit/build fingerprint and CI never fetches the deployed `master.json` to verify its contents.

**Recommendation:** publish a generated build manifest containing commit SHA/data revision and show it in the footer; after deployment, fetch same-origin `master.json` with retries and assert row count plus a reviewed revision marker.

### F-06 — “Everything” versus “Original Spreadsheet” is operationally ambiguous (P1, open)

The underlying separation is correct, but a user can reasonably read both as one spreadsheet and expect curated corrections in the raw view.

**Recommendation:** label them **Curated Catalogue (Everything)** and **Raw Source (Original Spreadsheet)**, with one-line provenance text in each view.

### F-07 — Removed overview/stats functionality left dead JS and CSS (P2, open)

At least seven missing DOM IDs still have code paths (`catalogue-intro`, `hero`, `hero-dismiss`, `overview-cards`, `series-strip-list`, `stats-strip`, `overview-btn`), and styling for removed components remains. Null guards prevent runtime errors but preserve unnecessary complexity.

**Recommendation:** remove the dead bindings, render helpers, event listeners, settings field, and CSS in one behavior-preserving cleanup backed by the 25 browser specs.

### F-08 — CI is monolithic and warnings are accumulating (P2, open; workflow change)

Python/data and browser validation run serially in one job; a late E2E failure makes the entire two-minute run red and obscures that data validation passed. Actions also warn that Node.js 20 action runtimes are deprecated and forcibly upgraded by the runner.

**Recommendation:** split CI into `data-and-python` and `browser` jobs, update action majors only to versions confirmed to exist, and keep a final required aggregate check. A prior session briefly set nonexistent/unreviewed `@v7` tags and added `-c requirements-ci.txt` before that file existed, causing three dependency-stage failures; workflow edits need review rather than blind “latest” upgrades.

### F-09 — Coverage prose overstated module floors (P2, resolved in current docs)

Actual coverage is 90% total, but `pipeline/helpers.py` is 78% and `pipeline/relationships.py` is 82%. CI enforces only the total 85% floor.

### F-10 — Documentation volume remains high (P3, open)

Twenty root Markdown documents and 86 archived Markdown documents create overlapping “current” audit narratives. This audit is placed under `docs/audits/` rather than adding another root report.

## 6. Verification performed

### Passed locally

- `python process_data.py --check`
- `python build_research_master.py --check`
- `python build_catalogue_pages.py --check`
- `python reconcile_research_master.py --check`
- `python map_series_taxonomy.py --check`
- `python sync_inventory_mirrors.py --check`
- `python -m py_compile *.py pipeline/*.py tests/*.py`
- `python -m unittest discover tests` — **140 passed**
- `coverage run -m unittest discover tests && coverage report` — **90% total**
- `ruff check .` — pass
- `node --check` on app, config, and all specs — pass
- `npm ci` — pass
- `npm audit --audit-level=moderate` — zero vulnerabilities
- `git diff --check` and `git fsck` — pass

### Environment-limited

- Playwright Chromium download is blocked in this sandbox by CDN TLS resets; the 25-spec browser run must be confirmed in GitHub Actions.
- Direct HTTPS fetching of `56eli.github.io` is blocked from this sandbox by TLS EOF; GitHub Pages build/deployment APIs, deployment status, and repository content hashes were used instead.
- Classic branch-protection settings returned HTTP 403 to this integration; rulesets were readable and empty, and observed merges before check completion establish the practical behavior.

## 7. Recommended execution order

1. **Merge this branch only after its CI is green** (stale selector fix + Pages-payload regression test).
2. **Owner decision:** enable required checks and CI-gated Pages deployment.
3. Add a deployed build manifest/post-deploy smoke assertion.
4. Clarify curated vs. raw labels in the UI.
5. Remove dead overview/stats JS and CSS.
6. Split the monolithic CI job and update action versions deliberately.
7. Triage issue #18 when the owner can provide the Drive export/definition.
