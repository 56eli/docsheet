# End-User Row Delivery Failure Postmortem and Full Audit — 2026-08-09

**Repository:** `56eli/docsheet`  
**Audited baseline:** `ea4e30d` (`main`)  
**Audit branch:** `arena/019fe7c9-docsheet`  
**Scope:** full stack, data pipeline, GitHub Actions, GitHub Pages, and the repeated spreadsheet-row presentation failure  
**Status:** row-delivery incident remains unresolved; this report supersedes any conclusion that a successful Pages artifact alone proves the row problem was fixed for the end user

## 1. Executive verdict

The previous investigations validated the wrong boundary. They proved that commits and generated JSON reached GitHub Pages, then incorrectly treated that as proof that the requested spreadsheet-row experience reached the end user. It did not.

The failure is a chain, not one broken deployment command:

1. **The row implementation itself is still defective.** A later CSS rule replaces the REVISION1 block-colored left accent on 105 default-order rows; filtering and sorting can move the defect to other odd rows.
2. **The browser delivery path is not versioned.** `index.html` loads bare `style.css` and `app.js`, so a successful Pages build does not prove a user's browser consumed the matching CSS/JS pair.
3. **There is no end-user acceptance test.** CI checks source tokens and the presence of a class, not computed row colors, block-specific accents, screenshots, cache freshness, or the deployed URL.
4. **The public UI can hide the affected surface.** Mobile opens in Browse mode and desktop can persist Browse mode, where Tabulator spreadsheet rows are absent.
5. **CI and deployment are independent and unenforced.** PRs #48–#52 were merged before checks completed; red commits were published anyway. The red Actions did not protect users and also obscured the actual visual defect.
6. **Data and presentation were repeatedly conflated.** The owner-reviewed data lives in curated `master.json`, while raw `data.json` intentionally remains unchanged; meanwhile, the visible row-styling request is a browser-rendering concern. A byte-correct payload is not visual acceptance.

PR #53 fixes the stale Playwright selector and adds a five-row curated-payload guard. Those are useful changes, but **PR #53 does not fix or prove the end-user row presentation**.

## 2. Project architecture, as actually deployed

DocSheet is a static GitHub Pages application with two distinct data lanes.

### 2.1 Raw lane

```text
hawkins archive clone - Sheet1.csv
  -> process_data.py
  -> docs/data.json
  -> Original Spreadsheet view
```

- 374 source rows.
- 31 blank visual-separator rows, hidden by default in the UI.
- Seven published columns after six always-empty source columns are trimmed.
- Cell values are intentionally passed through unchanged.
- `.github/workflows/update_spreadsheet.yml` runs only when the raw CSV changes on `main`, or by manual dispatch.

### 2.2 Curated lane

```text
migration_review_ledger.csv + data/*.csv review overlays
  -> build_research_master.py
  -> data/research_master_draft.csv/json
  -> build_catalogue_pages.py
  -> docs/master.json and other review/source JSON files
  -> Everything / Series / review views
```

Current curated state:

- 362 master records.
- 75 excluded ledger rows.
- 134 approved source overrides.
- 39 reviewed manual candidates.
- 338 approved work-family memberships.
- 362 approved display-order rows.
- 191 reviewed Veritas products, 26 Audible products, and 29 Hay House products.

### 2.3 Frontend lane

- `docs/index.html`: static shell and external Tabulator assets.
- `docs/app.js`: 2,692-line SPA controller; data loading, Tabulator, filters, browse mode, exports, drawers, and state persistence.
- `docs/style.css`: 2,382-line stylesheet; theme tokens, responsive modes, table presentation, and block styling.
- GitHub Pages configuration: legacy branch deployment from `main:/docs`.

The frontend fetches JSON with `cache: "no-store"`, but the HTML references local code and CSS without content hashes:

```html
<link rel="stylesheet" href="style.css">
<script src="app.js"></script>
```

That asymmetry matters: data is explicitly refreshed while the code that decides how rows look is not cache-versioned.

## 3. Incident timeline

| UTC time | Commit / PR | What changed | CI | Pages artifact |
|---|---|---|---|---|
| 15:22 | `a981641`, PR #46 | REVISION1 ODS data/order overlays | green | built |
| 15:46 | `8282721`, PR #47 | first current block-row styling implementation | green | built |
| 16:17 | `255d937`, PR #48 | removed stats/overview DOM, retained stale E2E selector; changed row logic | red | built |
| 16:38 | `c884138`, PR #49 | more UI and row styling changes | red | built |
| 16:54 | `52833cf`, PR #50 | neutral palette/zebra attempt | red | built |
| 17:41 | `25906ad`, PR #51 | contrast increase and static regression test | red | built |
| 17:58 | `ea4e30d`, PR #52 | another row presentation rewrite | red | built |
| 18:22–18:27 | PR #53 | stale-selector fix and data-payload guard | green | not on `main` at audit time |

The decisive process failure is visible in merge timing:

- PR #48 merged six seconds after creation, before its check had meaningfully run.
- PR #49 merged four seconds after creation.
- PR #50 merged before its check finished.
- PR #51 merged before its check finished.
- PR #52 merged five seconds after creation.

The project therefore had neither a validation gate nor an end-user presentation gate during the five row-styling iterations.

## 4. Actions and Pages forensics

### 4.1 CI history

Available CI history contains 154 runs:

- 98 successful.
- 48 failed.
- 8 cancelled.

Failed-step classification:

- 41 failures at **Run browser smoke tests**.
- 4 failures at **Verify Pages catalogue matches its inputs**.
- 3 failures at **Install Python dependencies**.

The recent 11-run cascade from PR #48 through `ea4e30d` had one common test failure:

```text
locator('#show-stats-toggle').check(): Test timeout of 45000ms exceeded
1 failed, 24 passed
```

Commit `255d937` deleted `#show-stats-toggle`, `#stats-strip`, and the stat chips but retained the Playwright test that waited for them. This explains the red CI cascade, but it does **not** explain or resolve the row presentation seen by the user.

### 4.2 Spreadsheet updater history

`Update Spreadsheet` has three available runs, all successful. It was not involved in the REVISION1 curated changes or the later CSS iterations because neither changed the raw source CSV.

### 4.3 Pages history and contradictory status surfaces

The automatic Pages Actions history contains 74 runs:

- 63 successful.
- 5 failed during initial setup on 2026-08-02.
- 6 cancelled, primarily during rapid successive pushes.

The legacy Pages Builds API also reports three zero-duration `errored` build objects for workflow-only commits `f5d6206`, `e1f14dd`, and `435b575` around 10:00 UTC on 2026-08-09, while the Pages Actions run for `435b575` completed successfully. This creates contradictory operational signals.

All row-style commits from PR #47 through PR #52 produced built Pages artifacts. That fact only proves files were accepted by Pages. It does not prove:

- that a browser fetched the newest unversioned assets;
- that matching HTML, JS, and CSS versions were used together;
- that Tabulator's computed row styles matched the intended design;
- that mobile/desktop persisted presentation state exposed the table;
- or that the result met the owner's visual acceptance criteria.

### 4.4 Current observability gap

The public page has no visible commit SHA, build ID, asset content hash, or data revision. The footer displays an HTTP `Last-Modified` value from the JSON response, which does not identify the JS/CSS build rendering the data.

As a result, neither the owner nor an agent can answer “which row implementation am I looking at?” from the page itself.

## 5. Why the row result did not reach the end user

### F-01 — CSS cascade destroys block-specific accents on odd work starts (P0)

Every block rule sets a block-colored inset shadow, for example:

```css
#spreadsheet .tabulator .tabulator-row.row-block-books {
  box-shadow: inset 3.5px 0 0 var(--block-books);
}
```

A later rule sets another `box-shadow`:

```css
#spreadsheet .tabulator .tabulator-row.work-group-start {
  box-shadow: inset 3px 0 0 var(--accent);
}
```

For odd rows, the selectors have equal specificity and the later work-group rule wins. The requested block accent is replaced by the global green accent. In the default 362-row order:

- 215 rows are work-group starts;
- 105 are odd-position work starts where the later rule replaces the block color;
- affected rows span lectures, discussion, satsang, On-the-Road, volume, office, books, transcription, media-misc, and undecided blocks;
- sorting and filtering change row parity, so the broken subset is unstable.

This is a concrete implementation defect, not a deployment-status interpretation.

### F-02 — The most prominent cue is too weak and inconsistent (P0)

Block backgrounds are mixed at 8.5% over neutral row colors. In dark mode they are mixed over `#161616` / `#1e1e1e`; in light mode over white / `#f4f4f5`. The static test accepts any parsed percentage from 8–18%, but does not evaluate the computed color or compare neighboring blocks.

When F-01 changes the conspicuous left edge to a generic green, the remaining block identity is only the faint 8.5% wash. That matches the reported experience that group changes appear absent or unchanged.

### F-03 — Asset URLs are not cache-versioned (P0 delivery gap)

JSON requests use `cache: "no-store"`; `style.css` and `app.js` do not. Rapid deployments reused the same asset URLs five times in roughly two hours.

This permits a user to receive fresh JSON with an older script or stylesheet until cache revalidation. It also prevents support from distinguishing a stale browser from a current rendering. There is no service worker to control or purge this cache, and no content-hash query string in `index.html`.

This audit cannot reconstruct the owner's browser cache after the fact, so cache is a proven delivery gap rather than the sole claimed cause. It must be eliminated before another agent declares success.

### F-04 — Browser presentation modes can remove spreadsheet rows entirely (P1)

At widths up to 720 px, Everything opens in Browse mode. Desktop Browse mode can also persist in local storage under `docsheet-master-presentation`. Browse mode renders cards, not Tabulator rows, so row backgrounds and block accents cannot be seen there.

A Pages artifact can therefore contain row CSS while the end user's active presentation contains no styled rows.

### F-05 — Tests validate implementation tokens, not the user-visible result (P0)

Current row tests provide false confidence:

- `tests/test_style_contrast.py` parses CSS text and checks token luminance/percentages.
- It does not run a browser or resolve the cascade.
- It does not detect the later `work-group-start` shadow override.
- The only Playwright row-style assertion checks that the first row has class `row-block-styled`.
- No test reads `getComputedStyle()` for odd/even rows or multiple blocks.
- No test asserts block-specific shadow colors.
- No visual screenshot test exists.
- No test runs against the deployed Pages URL.
- No test verifies asset revision/freshness.

Thus PR #51's “regression guard” can pass while the central row bug remains.

### F-06 — The first viewport is not representative (P1)

The first 201 rows belong to the lectures block. A reviewer looking at the default viewport sees only one block and cannot verify transitions to discussion, satsang, On-the-Road, books, or other groups without traveling far down a virtualized table.

The existing Playwright check inspects only the first row. It never navigates to a second block.

### F-07 — Data fixes are hidden or shown in a different view (P1)

The two public datasets have different contracts:

- **Everything** reads curated `master.json`.
- **Original Spreadsheet** reads raw `data.json` and intentionally does not receive curated overlays.

Furthermore, proposed filenames and provenance are treated as expert columns in the default Everything table. A user can therefore open a spreadsheet view and not see the fields changed in the REVISION1 review without enabling expert columns or opening row details.

This is an information-architecture failure even when the data bytes are correct.

### F-08 — Pages success was used as a substitute for owner acceptance (P0 process failure)

Agents repeatedly closed the loop using:

- committed-file hashes;
- Pages API state;
- CI source tests;
- prose claims in handoffs.

None of those observe the owner's browser. User feedback must be treated as the acceptance result. A “built” artifact is not a passed visual acceptance test.

## 6. REVISION1 integrity findings

The ODS was decoded independently rather than relying on handoff prose:

- one sheet;
- 362 data rows plus one header row;
- 23 visible columns;
- 8,326 cells compared structurally;
- 362 unique Master IDs.

Filename-cell color styles map to the committed review blocks:

| ODS style group | Committed block | Rows |
|---|---|---:|
| unfilled leading records | lectures-2002-2011 | 201 |
| `ce6` | discussion | 8 |
| `ce5` | satsang | 22 |
| `ce3` | on-the-road | 32 |
| `ce2` | volume-series | 13 |
| `ce4` | office-series | 16 |
| `ce7` | books | 21 |
| `ce8` | transcription-books | 6 |
| `ce10` | media-misc | 3 |
| default tail | undecided | 39 |
| `ce9` | fran-grace | 1 |

The 58 owner-edited filename rows are represented in the curated inputs and generated payload. That is a data-integrity result only; it does not override the end-user delivery findings above.

## 7. Full audit matrix

| Area | Verdict | Evidence / risk |
|---|---|---|
| Data architecture | Strong, but confusing publicly | Raw and curated lanes are deterministic but look like two versions of one spreadsheet. |
| Raw pipeline | Pass | 374 rows, 31 intentional blank separators, seven published columns; updater 3/3 green. |
| Curated pipeline | Pass | 362 masters; all generators byte-check outputs; reviewed overlays are explicit. |
| Data integrity | Pass | Unique UUIDs and filenames; approved dense display order; no missing master title/type/work ID. |
| REVISION1 interpretation | Data pass, UX fail | ODS color groups and edited records were decoded, but visibility and rendering are not assured. |
| Frontend behavior | Feature-rich, high debt | 2,692-line app with persisted modes, virtualized table, and dead overview/stats code. |
| Row presentation | Fail | Definite cascade collision, weak visual acceptance coverage, and unstable parity behavior. |
| Responsive behavior | Mixed | Mobile Browse is useful, but it removes the surface where row changes are expected. |
| Accessibility | Reasonable baseline | Labels, focus restoration, keyboard actions; no automated axe/Lighthouse evidence. |
| Security/privacy | Good for static app | Same-origin JSON, CSP, SRI-pinned Tabulator; `style-src 'unsafe-inline'` remains low-severity debt. |
| Dependency hygiene | Pass | Reproducible Python CI constraints; exact Playwright version; npm audit reports zero vulnerabilities. |
| Offline tests | Strong for data | 139/139 pass at baseline; 90% total coverage, though helpers are 78% and relationships 82%. |
| Visual tests | Fail | Class/token checks are not computed-style or screenshot acceptance tests. |
| CI | Operational but unenforced | 11-run stale-test cascade; merge-before-check behavior; monolithic late browser failure. |
| Pages deployment | Artifact delivery works, user delivery unproven | Legacy branch deploy is independent of CI; no asset version, build identity, or post-deploy browser check. |
| Observability | Fail for end-user support | No visible SHA/version; contradictory Pages status surfaces; no deployed-content report. |
| Documentation | Thorough but misleading/overgrown | Multiple “current” audits and handoffs claimed resolution without browser acceptance. |
| Repository hygiene | Pass | 219 tracked files, no tracked secrets found, clean Git/fsck/diff checks. |
| Maintainability | Needs work | Large frontend/CSS, hard-coded 362-entry block map, duplicated dead selectors, and overlapping row cues. |

## 8. What PR #53 does and does not do

### It does

- remove the stale `#show-stats-toggle` Playwright path;
- restore green browser CI (25/25 specs in two PR runs);
- add a deterministic guard for five curated row values in `docs/master.json`;
- document CI/Pages separation.

### It does not

- fix the block-accent/work-group CSS collision;
- add cache-versioned assets;
- expose a visible deployed revision;
- test computed row colors or screenshots;
- test more than one block in the browser;
- verify the public deployed URL after Pages finishes;
- ensure the user's active mode displays spreadsheet rows;
- or obtain owner visual acceptance.

PR #53 should therefore be described as a **CI regression fix**, not closure of the row-delivery incident.

## 9. Required remediation sequence

### P0 — Establish an observable delivery contract

1. Add content-hashed query versions for `style.css` and `app.js`.
2. Generate and display a build manifest/revision in the footer.
3. Make the public page identify the exact JS, CSS, data revision, and source commit/build.
4. Add a post-deploy job that loads the actual Pages URL after deployment and records the observed revision.

### P0 — Correct and test the row cascade

1. Remove the competing `work-group-start` left `box-shadow`, or compose it without replacing the block accent.
2. Keep work-family grouping on a different visual axis (for example a top separator) if still required.
3. Test computed styles for odd and even rows in at least three nonadjacent blocks.
4. Test after filtering and sorting, because parity and group-start status change.
5. Add light and dark visual snapshots at a fixed desktop viewport.
6. Add an explicit test proving Browse mode is not being mistaken for Spreadsheet mode.

### P0 — Stop deploying unvalidated merges

1. Require the CI check before merge.
2. Stop merging seconds after PR creation.
3. Move Pages to a CI-gated custom workflow or otherwise prevent a failed required check from publishing.
4. Split data/Python and browser jobs so a late UI failure is visible without hiding earlier results.

### P1 — Make the data lanes unmistakable

Rename the views to explicit contracts, for example:

- **Curated Catalogue** instead of Everything.
- **Raw Source Spreadsheet** instead of Original Spreadsheet.

Show a persistent one-line provenance label and make owner-reviewed fields visible in the default curated workflow used for review.

### P1 — Obtain real acceptance

Before calling the row issue fixed:

1. deploy a versioned preview;
2. provide its visible revision;
3. capture desktop light/dark and mobile screenshots;
4. verify block transitions, odd/even rows, filtered rows, and sorted rows;
5. ask the owner to accept or reject that exact revision.

## 10. Verification performed for this audit

Passed:

- all six generator `--check` modes;
- 139/139 offline tests in an isolated virtual environment;
- 90% statement coverage;
- JS and Playwright-spec syntax checks;
- `npm ci` and `npm audit` with zero reported vulnerabilities;
- Git diff/fsck hygiene and tracked-secret scan;
- direct parsing of the REVISION1 ODS structure and color groups;
- GitHub Actions run/job/annotation inspection;
- Pages configuration, build, deployment, and environment inspection;
- live retrieval of current `style.css`, `app.js`, and rendered page content through the available page-fetch path.

Environment-limited:

- local Chromium installation was blocked by repeated CDN TLS resets;
- direct `curl`/`wget` to GitHub Pages was TLS-blocked in the sandbox;
- PR #53 GitHub Actions supplied the current 25-spec browser run, but those specs do not test the failed visual acceptance conditions.

## 11. Final conclusion

The repository can generate correct data and GitHub can build the committed site while the end user still receives no accepted row fix. The missing link is a versioned, observable, browser-level acceptance pipeline, compounded by a concrete CSS cascade bug that current tests cannot see. The incident is unresolved until that path—not merely the repository bytes—is fixed and accepted by the owner.
