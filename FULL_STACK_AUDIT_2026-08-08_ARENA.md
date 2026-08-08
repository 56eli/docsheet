# DocSheet Full-Stack & Catalogue Audit — 2026-08-08

**Auditor:** Arena.ai helpful agent — Full-Stack Development / Data Engineering pass  
**Repository:** `56eli/docsheet`  
**Commit audited:** `6c96a00e086e37ef8af148c24b1436625899e01f` (`main`, session branch `arena/019fe1a1-docsheet`)  
**Scope:** raw spreadsheet, review ledger, curated master, official inventories, candidate and edition registries, relationships, taxonomy, generated Pages JSON, frontend, tests, CI/CD, GitHub Pages configuration, and living documentation.

> This is an independent checkpoint audit. It does not replace the historical audit logs already in the repository, and it intentionally does not change catalogue data or implementation code.

## 1. Executive verdict

The **current generated catalogue is internally reproducible and the main CI/Pages deployment is green**, but the repository is not fully audit-clean. At the baseline commit I found the following; the two priority operational findings (F-01/F-02) were fixed in the follow-up recorded in §10:

- **2 current operational inconsistencies** that are hidden while all review queues are empty:
  1. the reconciliation report labels all 63 approved candidate/edition rows as unresolved “draft-only” records;
  2. `catalogue-meta.json.master_items` is implemented as an Everything-row count, not a curated-master count, so the public “Master records” stat will be wrong as soon as a candidate lane contains a row;
- **6 engineering/availability guard gaps** that can allow future catalogue drift or frontend unavailability without failing the normal check suite;
- **several stale living/proposal documents at baseline**, whose counts and instructions were corrected or explicitly labelled historical in the docs-cleanup follow-up;
- **one workflow race** between the raw-data auto-regenerator and CI;
- **one open, superseded pull request** and one old open issue requiring repository housekeeping.

The current data itself has no duplicate UUIDs, catalogue codes, filenames, or orphaned Veritas URLs. The two owner-accepted anomalies — the publisher-verbatim malformed URL on master 265 and the `198X` year convention — remain documented and were not reclassified as defects in this audit.

## 2. Verification matrix

All commands below were run from the repository root after installing the declared dependencies in an isolated Python 3.11 virtual environment (`/tmp/docsheet-audit-venv`).

| Check | Result | Notes |
|---|---:|---|
| `python -m py_compile *.py` | PASS | All root Python modules compile. |
| `process_data.py --check` | PASS | 374 raw data rows; 8 published source columns. |
| `build_research_master.py --check` | PASS | 365 master rows; 72 exclusions; 131 approved overrides; 39 manual candidates validated. |
| `build_catalogue_pages.py --check` | PASS | 365 Everything rows. |
| `reconcile_research_master.py --check` | PASS* | The report is byte-current, but its status is semantically misleading; see F-01. |
| `map_series_taxonomy.py --check` | PASS | 186 mappings; 177 approved, 9 rejected, 0 queued. |
| `sync_inventory_mirrors.py --check` | PASS | Derived Veritas mirror fields match the master. |
| `python -m unittest discover tests` | **121/121 PASS** | Offline deterministic suite after the F-01–F-04 follow-up fixes. |
| Coverage | **91% PASS** | 2,038 statements; lowest module coverage 88%; configured floor 85%. |
| Node syntax checks | PASS | `app.js`, Playwright config, and all 3 specs. |
| `npm ci` / npm audit | PASS | Playwright 1.62.1; 0 reported vulnerabilities. |
| Local Playwright execution | BLOCKED | All 16 tests stop before launch because Chromium is not installed in the sandbox. This is environmental, not a test assertion failure. |
| GitHub CI on audited main commit | PASS | Run `31260234470`: CI success; Pages build/deployment also succeeded. |
| `fetch_veritas_catalogue.py --check` | BLOCKED | Sandbox TLS EOF when connecting to `veritaspub.com`; offline API replay tests pass and the failure is documented in project instructions. |
| GitHub Pages configuration | PASS | Source is `main` / `/docs`; status `built`; `.nojekyll` is present. |
| Markdown links | PASS | 0 broken local Markdown links across 103 Markdown files. |
| CSP inline script hash | PASS | Computed SHA-256 matches `docs/index.html`. |

## 3. Recomputed current catalogue state

| Area | Current result |
|---|---:|
| Raw spreadsheet / ledger | 374 / 374 rows; ledger raw provenance mirrors the CSV with 0 mismatches |
| Curated master | 365 rows: 309 lecture, 40 book, 8 discussion, 7 highlight, 1 other |
| Master identifiers | 365 unique UUIDs; 281 unique catalogue codes |
| Catalogue codes | Lecture/discussion only; 0 duplicates; 19 year-known lecture/discussion rows intentionally have no code because their year was blank when minted |
| Exclusions | 72 retained raw rows |
| Work families | 191 works, 341 approved memberships, 365/365 master coverage |
| Veritas inventory | 191 products: 186 primary-source matches, 0 title matches, 0 normalized-title matches, 5 excluded related-material decisions |
| Veritas source URLs | 336 master rows, all 336 URLs present in the 191-row reviewed inventory; 78 repeated URLs are expected multi-part products |
| Relationships | 343 rendered rows = 336 derived primary + 7 reviewed related-material rows |
| Series compilations | 7 reviewed rows |
| Taxonomy | 186 matched products = 177 approved + 9 rejected + 0 pending |
| Source overrides | 131/131 approved |
| Manual candidates | 39/39 promoted; 0 pending |
| Edition candidates | 24/24 promoted |
| Filename proposal | 365 rows; 365 unique safe names and 365 unique display names |
| Ownership | 296 `true`, 25 `false`, 44 blank/not stated; semantics are documented |
| Year edge cases | 17 blank years: 13 intentional pre-2000 Volume Series + 4 under investigation; 16 Office Series rows use owner-approved `198X` |
| Published frontend contract | 19 HTML tabs ↔ 19 `app.js` views ↔ 19 JSON view files |

## 4. Verified clean invariants

The following were independently checked and do not need corrective work in this pass:

- Generated CSV/JSON outputs are reproducible from their declared inputs and all six local check modes pass.
- Raw CSV values mirrored into `migration_review_ledger.csv` match the source by physical raw-row provenance exactly.
- UUIDs, catalogue codes, proposed filenames, review IDs, promotion keys, mapping IDs, and relationship IDs are unique within their declared tables.
- All master rows have a valid `work_id`, non-empty title, non-empty `legacy_title`, non-empty `year_source`, non-empty `format`, and a filename proposal.
- No `audio` or `video` value appears in a controlled `item_type` field; the remaining `audio` strings in Hay House inventory are carrier metadata, not item types.
- No master has a month without a year, invalid month, book month, or invalid year shape.
- All 131 source overrides point to existing master/candidate provenance and use HTTPS values.
- All 7 stored relationship rows point to current inventory URLs/titles and current masters; all 336 derived primary relationships resolve to current Veritas products.
- Veritas inventory mirror counts and title mirrors are exact; excluded products do not carry accidental master matches.
- Filename metadata mirrors exactly match the final master; part indexes agree with the reviewed `format_detail` markers.
- The frontend CSP hash, tab/view/file mapping, Everything schema, Expert-column fields, and CDN SRI hashes are internally consistent.
- The latest main-branch GitHub CI and Pages deployment completed successfully.

## 5. Findings requiring attention

### F-01 — Reconciliation report misclassifies every promoted non-raw row as unresolved drift

**Severity:** High process/integrity risk  
**Current visibility:** Internal report and CI artifact; not currently visible in the public table  
**Evidence:** `RECONCILIATION_REPORT.md`, `reconcile_research_master.py:56-92`

The current report says there are **63 “draft-only CSV records requiring a provenance decision”** and that the outputs are “not yet fully reconciled.” Those 63 rows are not accidental or unreviewed:

- 39 rows are present in the approved manual-candidate promotion registry;
- 24 rows are present in the approved edition-promotion registry;
- all 63 have a durable `candidate_key`, and all resolve to current promoted master rows;
- the normal master build intentionally mints these rows from the promotion layers.

`compare_drafts()` matches rows only by non-empty `raw_row_number`. Candidate/edition rows have no raw row number, so the function unconditionally puts them in `extras`. The report therefore creates a false “resolve before rebuild” state even though `build_research_master.py --check` and `build_catalogue_pages.py --check` pass.

This is more than wording: `reconcile_research_master.py --check` only verifies that the report text is current; it does not fail when `is_reconciled` is false. A future genuine ledger drift can be hidden in the same noisy section, and maintainers may either ignore a real warning or stop a safe build unnecessarily.

**Recommended fix:** compare raw rows by `raw_row_number` and candidate rows by `candidate_key` against the explicit promotion registries, or split the report into “ledger-backed rows” and “approved candidate-backed rows.” Add a regression test asserting the committed state has zero unclassified extras and that all 63 candidate-backed rows are classified as approved provenance.

### F-02 — `catalogue-meta.json.master_items` has the wrong semantic count

**Severity:** Medium runtime/data-contract risk  
**Current visibility:** Latent; current queues are empty so both counts happen to be 365  
**Evidence:** `build_catalogue_pages.py:834-837`, `docs/app.js:1590-1610`

The builder sets:

```python
"master_items": len(items),          # Everything rows, including candidates
"migrated_items": migrated_items,    # curated master rows only
```

The frontend uses `master_items` for the chip labelled **“Master records.”** With the current all-master state, both values are 365 and the defect is hidden. A sandbox build with one pending candidate produces:

```text
master_items = 366
migrated_items = 365
record_type master = 365
record_type candidate_pending_promotion = 1
```

The public “Master records” stat would then count a review candidate as a curated master. This directly contradicts the repository’s explicit `record_type` boundary.

**Recommended fix:** use `migrated_items` for the master-record stat, rename the current `master_items` field to `everything_items`, or publish both names with unambiguous semantics. Add a test with one pending candidate.

### F-03 — Source-URL relationship coverage silently drops orphaned master links

**Severity:** Medium integrity risk  
**Current visibility:** No current orphan; future drift can pass normal checks  
**Evidence:** `build_catalogue_pages.py:257-263`, `build_research_master.py` master assembly

`derive_primary_relationships()` skips a master row when `source_url_veritas` is non-empty but absent from the reviewed Veritas inventory. The master build does not require every populated Veritas URL to exist in the inventory, and the Pages build does not turn a skipped URL into an error. A typo or stale URL can therefore leave a clickable master source in `docs/master.json` while silently removing its primary relationship and relationship evidence.

The baseline data was clean: 336/336 populated master Veritas URLs resolved. The problem was the missing invariant, not a present orphan.

**Resolution:** `validate_veritas_inventory()` now fails closed on
`master.source_url_veritas - inventory.official_product_url`, and a regression
fixture proves an orphan URL cannot pass the Pages build.

### F-04 — Veritas mapping decisions were not contract-checked by the Pages build

**Severity:** Medium review-integrity risk  
**Baseline visibility:** Four stale rows were present in the 9-row overlay; the normal six checks did not detect them.
**Evidence:** Before this follow-up, `build_catalogue_pages.py` only read `data/veritas_mapping_decisions.csv` for display while `fetch_veritas_catalogue.py:204-302` owned the validation.

The previous product-50491 incident is a concrete precedent: a stale overlay row mapped the product to master 121 while the inventory/master had correctly moved it to primary master 278. The stale row was visible in the Veritas Decisions sheet and would have overridden deterministic matching on the next live refresh, yet the ordinary catalogue build checks did not detect it.

The follow-up URL-evidence sweep found the same class of contradiction for products 53062, 50398, 50378, and 50432, whose exact URLs were already primary on masters 300, 289, 291, and 247.

**Resolution:** the four stale rows were removed, their inventory rows restored to deterministic `matched_by_primary_source`, and the overlay is now 5 excluded-related-material rows. `build_catalogue_pages.py` now validates decision IDs/status/titles/notes against the committed inventory and fails if a decision product URL is an exact master primary URL. Regression tests cover the committed clean overlay, malformed rows, and exact-primary contradictions.

### F-05 — Raw spreadsheet auto-regeneration and CI have a race / PR contract mismatch

**Severity:** Medium CI reliability risk  
**Current visibility:** Latent until a raw CSV-only change is merged  
**Evidence:** `.github/workflows/update_spreadsheet.yml:11-42`, `.github/workflows/ci.yml:27-54`

`Update Spreadsheet` runs only on a **push to `main`** when the raw CSV changes and then auto-commits `docs/data.json`. CI runs independently on the same push and requires `python process_data.py --check` before that auto-commit exists. A raw-data change can therefore produce this sequence:

1. push raw CSV change;
2. CI sees stale `docs/data.json` and fails;
3. update workflow regenerates and auto-commits `docs/data.json`;
4. the generated commit may not receive a new CI run because it is made by `GITHUB_TOKEN`.

The same mismatch exists on pull requests: the update workflow does not run for PRs, but PR CI still requires the generated raw payload to already be committed. The curated generators have the same general “generated output must be included in the PR” contract, but only the raw pipeline claims to auto-regenerate after merge.

**Resolution status:** the owner has applied the `paths-ignore` raw-only `main`
trigger on main, leaving the raw-source updater as the sole post-merge owner;
PR CI still requires regenerated `docs/data.json` with a raw CSV change. The
first main CI run after the workflow edit fails because `requirements-ci.txt`
is supplied by PR #34 and has not reached main yet; merge the PR and rerun CI.

### F-06 — Root fallback source selection can publish the wrong CSV

**Severity:** Low/Medium data-integrity risk  
**Current visibility:** Latent when the preferred filename is missing  
**Evidence:** `process_data.py:69-79`

When the preferred source CSV is absent, `find_source_csv()` selects the first alphabetically sorted `*.csv` in the repository root. The current repository has multiple root CSVs, including the raw spreadsheet, `lecture_series_review.csv`, and `migration_review_ledger.csv`. If the raw spreadsheet is renamed or removed, the fallback can silently serialize a review ledger or bootstrap CSV into `docs/data.json`.

The fallback exists for convenience and the current default path is present, but it was unsafe for a published data pipeline.

**Resolution:** `process_data.py` now validates the raw spreadsheet header shape,
rejects unrelated root CSVs, and fails on ambiguous multiple raw candidates. Two
regression tests cover unrelated and ambiguous fallback inputs.

### F-07 — Reproducibility is weaker than the documentation implies

**Severity:** Low engineering risk  
**Evidence:** `requirements.txt` uses `pandas>=2.0,<4`; `requirements-dev.txt` uses `coverage>=7.0`; there is no Python lockfile or supported-version matrix.

Node is locked by `package-lock.json`, but Python runtime dependencies are open-ended across major pandas 2 and 3 and all future coverage 7 releases. The current outputs are deterministic under the audited environment, but a dependency upgrade can change CSV parsing or JSON serialization without a repository diff to the dependency specification.

**Resolution status:** added `requirements-ci.txt` with the audited exact
pandas/numpy/coverage set; owner-applied workflow wiring now installs through
it on main. The current main CI failure is the expected missing-file ordering
issue until PR #34 merges this constraint file; project CI remains Python 3.12.

### F-08 — External frontend assets have no local fallback

**Severity:** Low availability risk  
**Evidence:** `docs/index.html` loads Tabulator CSS/JS from `cdn.jsdelivr.net` and fonts from Google Fonts.

SRI hashes and CSP are correctly configured, but if the CDN is unavailable or blocked, `app.js` cannot create a Tabulator table and the published catalogue becomes unusable. This is a deployment resilience issue rather than a current failure; GitHub Pages and the latest CI browser run are healthy.

**Recommended fix:** vendor the pinned Tabulator assets under `docs/vendor/` or provide a local fallback while retaining SRI for remote assets.

## 6. Documentation and repository-state drift

At the baseline commit these were not catalogue-build failures, but they made the repository unsafe to hand to a new maintainer because root documents presented obsolete counts or already-resolved work as current. The repository’s README calls root policies, schemas, proposals, and status files “living documents,” so this follow-up updated normative schemas/counts and added explicit historical-snapshot labels to the proposal/audit artifacts.

| File | Stale/current contradiction | Current computed state |
|---|---|---:|
| `EDITION_MODEL_PROPOSAL.md` | Header says applied but reports 341 master / 387 Everything / 318 relationships and later says no families/editions are approved. | 365 master / 365 Everything / 343 relationships / 191 works / 341 memberships; 24 editions promoted. |
| `PRODUCT_RELATIONSHIP_SCHEMA.md` | “As of 2026-08-04” says 333 = 325 derived + 8 related across 165 products. | 343 = 336 derived + 7 related across 187 products. |
| `SERIES_TAXONOMY_MAPPING.md` | Baseline says 179 matched, 169 approved, 10 rejected and references a 6-row queue. | 186 matched, 177 approved, 9 rejected, 0 queue. |
| `FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md` | Baseline/files section still says 363 rows and contains 356/363 historical intermediate counts while the same document later says 365. | 365 proposal rows; 365/365 safe/display unique. |
| `MIGRATION_REVIEW_LEDGER.md` | Says the Advaita URL on raw rows 28–30 is quarantined and should be resolved; current raw URL and ledger mirror were fixed and are usable. | Rows 28–30 contain the corrected canonical URL and a 2026-08-08 fix note. |
| `LECTURE_SERIES_REVIEW.md` | Calls the 198-row batch review-only, says no IDs changed, and asks the owner to resolve three Advaita links. | The batch has been incorporated into the reviewed ledger/master; links are fixed and compact IDs exist. |
| `CATALOGUE_READABILITY_ROADMAP.md` | Historical proposal ends with “102 tests, 92%, all 5 checks,” and describes old format counts. | 123 tests, 91%, 6 checks; current format has 0 blanks and no deprecated item types. |
| `REVIEW_MODEL_SLIM_ANALYSIS.md` | Dated analysis still presents 356 master rows, 333 relationships, 18 decisions, and 100 tests as the project state. | 365 master rows, 343 relationships, 5 decisions, 123 tests, 91% coverage. |
| `README.md` | The “every entry” historical verification sentence still says 195 verifiable lecture months from the 2026-08-03 snapshot; current date-bearing master/source evidence has grown since then. | Treat the sentence as a dated historical claim or refresh it with a reproducible current metric. |

The old counts inside `archive/` and the superseded sections explicitly labelled as history are acceptable. The problem is that several root files are both linked from active documentation and written in present-tense “applied/current” language.

## 7. Frontend and test coverage observations

- The 19-tab mapping is correct, and the current CI run before this drawer test proves the 15 existing browser specs pass in GitHub’s Chromium environment; the new drawer/focus spec is now included in the next CI run.
- Local browser tests cannot be independently reproduced in this sandbox until `npx playwright install --with-deps chromium` succeeds; the local run produced 15 launch failures, not 15 assertion failures.
- The current browser suite does **not** actually exercise every claim made by `FULL_STACK_AUDIT_2026-08-08_DEEP_DIVE.md`: it does not cover all 19 tabs, dark-mode persistence, the row-details drawer/copy action, or every failure/empty state. The report’s statement that browser coverage verifies the “entire 19-tab layout, view states, expert toggle, and keyboard accessibility” is broader than the test files.
- `app.js` is a large single IIFE (~1,770 lines) with no browser unit tests and several persistence/race-sensitive paths. Rapid tab switching can allow an earlier `fetch()` response to render after a later view activation; static Pages makes this uncommon, but an activation token/request cancellation would make the behavior deterministic.
- The frontend correctly avoids `innerHTML` for row values and only turns `http(s)` values into links. No secret or credential was found in tracked files.

## 8. GitHub/project hygiene

- Current `main` is healthy: latest CI and Pages runs passed at audited commit `6c96a00`.
- PR [#29](https://github.com/56eli/docsheet/pull/29) remains open with an older `arena/019fe01c-docsheet` head and a failed historical CI run. Its description contains superseded 113-test/243-streaming counts and work that was later replaced by merged PRs #30–#33. It should be closed or rebased so maintainers do not mistake it for the active delivery path.
- Issue [#18](https://github.com/56eli/docsheet/issues/18) remains open from 2026-08-03 for an ownership cross-check; it should be either assigned a current owner/next action or explicitly deferred.
- The local checkout is shallow/grafted, which is a sandbox property rather than a repository defect; GitHub retains the full PR history.

## 9. Recommended order of work

1. **Fix F-01** — make reconciliation candidate-aware and add a zero-unclassified-extras regression test.
2. **Fix F-02** — separate `master_items` from Everything-row count and test with a pending candidate.
3. **F-03/F-04 are now guarded** — retain the regression tests and review F-08’s optional local asset fallback.
4. **F-05/F-06/F-07 workflow sequence:** merge PR #34 so `requirements-ci.txt` reaches main, rerun CI, and confirm the owner-applied workflow changes stay green.
5. **Perform documentation hygiene** — update active schemas/proposals or add a clear `Historical snapshot — do not use for current counts` banner and move obsolete review batches to `archive/`.
6. **Harden reproducibility/availability** — Python constraints, supported-version CI matrix, and optional vendored frontend assets.
7. **Close/rebase PR #29 and triage issue #18.**
8. **Expand browser coverage** for the remaining tabs, empty states, drawer, dark mode, settings persistence, and rapid tab switching.

## 10. Follow-up fixes applied after the baseline audit

After the baseline audit, the owner-selected priority and guard work was applied:

- **F-01:** reconciliation now matches raw rows by `raw_row_number` and promoted manual/edition rows by `candidate_key`; the committed reconciliation report now shows 0 unexplained extras and a complete verification result.
- **F-02:** `catalogue-meta.json.master_items` now reports the curated master count (`migrated_items`) rather than the Everything-row count; a pending-candidate regression test keeps the “Master records” stat correct.
- **F-03:** Pages validation now rejects any populated master Veritas URL absent from the reviewed inventory.
- **F-04:** Pages validation now checks decision IDs/status/titles/notes against the committed inventory and rejects a decision whose product URL is an exact master primary URL. Four stale rows (53062, 50398, 50378, 50432) were removed; the overlay is now 5 excluded-related-material rows.
- Added the guard and hardening regression tests. The deterministic suite is now **123/123**, coverage is **91%**, the lowest module is 88%, and all six generator checks plus Node syntax checks remain green.
- Regenerated `RECONCILIATION_REPORT.md`, inventory/decision Pages mirrors, and the affected decision documents. No raw/master rows changed; four stale mapping decisions were intentionally removed under the owner-selected primary-source ruling.

Remaining immediate work is to merge PR #34 so main CI can find `requirements-ci.txt`, then rerun main CI; optional F-08 local frontend asset fallback and repository housekeeping remain. Final UI CI run `31263676053` passed all 16 Playwright tests; the Record Type width assertion and drawer focus/section test are green.

## 11. Reproduction commands

```bash
python3 -m venv /tmp/docsheet-audit-venv
/tmp/docsheet-audit-venv/bin/pip install -r requirements-dev.txt

/tmp/docsheet-audit-venv/bin/python -m py_compile *.py
/tmp/docsheet-audit-venv/bin/python process_data.py --check
/tmp/docsheet-audit-venv/bin/python build_research_master.py --check
/tmp/docsheet-audit-venv/bin/python build_catalogue_pages.py --check
/tmp/docsheet-audit-venv/bin/python reconcile_research_master.py --check
/tmp/docsheet-audit-venv/bin/python map_series_taxonomy.py --check
/tmp/docsheet-audit-venv/bin/python sync_inventory_mirrors.py --check
/tmp/docsheet-audit-venv/bin/python -m unittest discover tests
/tmp/docsheet-audit-venv/bin/coverage run -m unittest discover tests
/tmp/docsheet-audit-venv/bin/coverage report

node --check docs/app.js
node --check playwright.config.js
for spec in tests/*.spec.js; do node --check "$spec"; done
npm ci
npm run test:e2e
```

`npm run test:e2e` requires the Chromium browser bundle. `fetch_veritas_catalogue.py --check` additionally requires live access to `veritaspub.com`; the sandbox currently returns a TLS EOF, while the committed offline replay tests cover its matching and retry logic.
cover its matching and retry logic.
gic.
 retry logic.
etry logic.
c.
