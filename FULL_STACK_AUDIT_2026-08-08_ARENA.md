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

## 12. Fresh current-checkout follow-up — `f0653fbd` (2026-08-08)

**Scope:** a new full-stack/data-engineering pass over the merged `main` state
at `f0653fbd86362eb2209164679d7793d7c31e7b4d` (the sandbox branch starts at
that commit). This section is the newest checkpoint in this document. It
preserves the baseline/follow-up history above and separates current facts from
those historical measurements.

### Verification rerun

| Check | Result |
|---|---:|
| Python compile plus all six generated-output `--check` modes | **PASS** |
| Deterministic Python suite | **125/125 PASS** |
| Coverage | **91%** (2,056 statements; every module >= 88%; 85% enforced floor) |
| JavaScript syntax (`app.js`, Playwright config, all 3 specs) | **PASS** |
| `npm ci` / production `npm audit` | **PASS** / **0 vulnerabilities** |
| Raw CSV ↔ ledger provenance mirrors | **374/374 rows, 0 mismatches** |
| Published JSON/CSV count parity | **14 direct pairs, all match** |
| Local HTTP smoke (`index`, `master.json`, `catalogue-meta.json`, `data.json`) | **200 / served correctly** |
| Inline CSP script hash and all three Tabulator SRI attributes | **PASS** |
| Latest GitHub `main` CI and Pages deployment | **PASS** — runs `31265700227` / `31265699591` |
| GitHub Pages configuration | **PASS** — HTTPS, `main` `/docs`, status `built` |
| Local Playwright browser execution | **BLOCKED** — Chromium bundle is absent in this sandbox; all 18 tests stop before assertion/launch. GitHub CI remains the browser authority. |
| Live Veritas refresh and direct Pages curl | **BLOCKED in sandbox** by TLS handshake failure; this is an environment limitation, not a failed data check. |

The catalogue remains internally consistent: 365 curated records (309 lecture,
40 book, 8 discussion, 7 highlight, 1 other), 281 unique codes, 191 reviewed
Veritas products, 336 derived primary + 7 reviewed related relationships, 191
works/341 approved memberships, 365 unique safe/display filenames, and zero
orphaned master Veritas URLs, duplicate UUIDs, duplicate codes, or duplicate
filenames.

### Architecture reviewed

- The raw view is deliberately pass-through: source CSV -> `process_data.py`
  -> `docs/data.json`; the five raw empty columns are a display-only trim.
- The curated master is a review-gated projection: ledger + source overrides +
  candidate/edition promotion registries + official inventories + taxonomy +
  work families -> `data/research_master_draft.*` -> Pages JSON views.
- The static frontend is a single Tabulator application (`docs/app.js`) with
  per-view JSON fetches, no browser-side editing, CSP/SRI, generated exports,
  and a 19-view navigation contract. Desktop retains Tabulator; phone-sized
  Everything now presents work stacks with Source/Stream actions plus Series
  and Timeline discovery rails, while preserving a persistent Spreadsheet
  escape hatch and the same facet state.
- CI validates the complete local pipeline, coverage, syntax, and Chromium;
  the manual Veritas workflow is intentionally review-only. The raw updater is
  separately scoped to `docs/data.json`.

### Current findings

#### C-01 — Six public DVD part rows have no part metadata in `format_detail`

**Severity:** Medium — catalogue/UX semantic inconsistency, no data loss.

Masters **222–224** (*The Presence of Spiritual Awareness*) and **230–232**
(*Verification of Spiritual Realities*) were title-cleaned against their
official listings. They now have the same visible title, `format=DVD`,
`format_detail` blank, and the same Veritas URL within each three-row group.
Their raw `legacy_title` values still prove `PART1`/`PART2`/`PART3`, and
`data/filename_proposal_YYYYMM.csv` correctly carries `part_index` 1–3 and
unique `[1/3]`-style filenames. The default table's filename rail keeps them
usable, but its Edition column reduces all three parts to indistinguishable
`DVD` rows. Other cleaned multi-part rows retain part information in
`format_detail`.

**Resolved in the audit-policy follow-up:** the six reviewed ledger cells now
carry normalized `Part 1`/`Part 2`/`Part 3` values; master, Pages, and
Migration Review outputs were regenerated. A deterministic regression test
locks this self-describing Edition/export contract.

#### C-02 — The filename policy and two current filenames disagree

**Severity:** Low/Medium — documented naming rule inconsistency.

README and the active v4 filename policy say audiobook labels are removed from
proposed names because `.m4b` already conveys the carrier. However masters
**320** and **331** currently publish:

- `1995 - Power vs. Force (Audiobook).m4b`
- `1995 - Power vs. Force Audio Book.m4b`

**Resolved in the audit-policy follow-up:** the reviewed filenames are now
`1995 - Power vs. Force (Audible).m4b` and
`1995 - Power vs. Force (Veritas).m4b`. This preserves the label-free carrier
rule while using a documented publisher suffix for a same-work/same-year/
same-carrier collision; a deterministic regression test locks both names.

#### F-01 — Rapid tab switches can render stale data into the active view

**Severity:** Medium — intermittent frontend correctness risk.

**Resolved in the frontend-hardening follow-up:** `activateView()` now creates
an `AbortController` per activation and increments a monotonic token. The loader
is side-effect-free until the current token commits data/footer metadata, so a
slow prior response cannot overwrite the selected view even if an abort races
with its response. A delayed/intercepted Playwright regression test locks the
rapid-tab-switch behavior.

#### F-02 — The row-details modal traps Tab away from its own source links

**Severity:** Medium — keyboard accessibility defect.

**Resolved in the frontend-hardening follow-up:** the focus trap now derives
its cycle from every visible focusable descendant of the modal, including all
official/evidence anchors in the body. Tab and Shift+Tab remain inside the
modal without bypassing source links; the Playwright drawer test now proves the
first body link is keyboard reachable and focus returns to Close with Shift+Tab.

#### S-01 — Raw-only direct pushes can bypass the complete validation suite

**Severity:** Medium, conditional on branch protection.

`ci.yml` intentionally ignores a raw-CSV-only `main` push to avoid racing
`Update Spreadsheet`. The updater then runs only `process_data.py` and
commits `docs/data.json`; it does not run the ledger/master/catalogue/mirror
checks or the test suite. PR CI provides the intended protection, but branch
protection could not be inspected with this GitHub integration (the API returns
403). If direct pushes to `main` are allowed, a raw-source change can publish a
new raw view without proving raw-to-ledger consistency or the whole pipeline.
Require PRs/required checks on `main`, or add a post-regeneration verification
job that fails loudly before publishing. This is a governance/control gap, not
a present output mismatch.

#### D-01 — Active filename documentation contains outdated current examples

**Severity:** Medium documentation drift.

**Resolved in the audit-policy follow-up:** the v4 policy now shows the current
`198X - Stress.mp4` Office Series convention and the two publisher-suffixed
Power-vs-Force audiobook names; the global-uniqueness rule now explicitly
covers source suffixes as well as carrier suffixes.

#### D-02 — Year-provenance documentation does not match current `year_source`

**Severity:** Medium documentation/provenance drift.

**Resolved in the audit-policy follow-up:** the policy now identifies the four
current edition-release backfills (327–330) and explicitly distinguishes them
from lecture recording dates. It also states the actual current provenance of
228–232, 265, and 268.

#### D-03 — Workflow guide includes an incorrect verification snippet

**Severity:** Low documentation drift.

**Resolved in the audit-policy follow-up:** the guide now names
`actions/setup-node@v7`, refers to every Playwright spec, and labels the old
branch-shipping note as historical so it cannot instruct a redundant PR.

#### D-04 — Current audit/report authority needs consolidation

**Severity:** Low maintainability risk.

Several root audits share the same date and overlapping claims. Most older
reports now carry useful historical banners, but the linked current Arena audit
contained trailing corrupted text before this follow-up section, and
`FULL_STACK_AUDIT_2026-08-08.md` interleaved resolved and open state without a
top-level historical/current marker. **Partially resolved in the follow-up:**
the corrupt tail was removed and that earlier audit now carries a historical
banner. Keep this report as the current checkpoint and move remaining
superseded root audits to `archive/` in the next documentation-hygiene pass.

### Observations that remain clean or intentionally bounded

- The verified publisher-verbatim malformed Veritas URL for master 265 remains
  an upstream canonical slug and is documented; it is not a local URL
  corruption.
- The owner-approved `198X` Office Series convention, 17 blank years, and
  four current edition listing-date backfills are explicit evidence boundaries,
  not test failures.
- URL, schema, candidate-promotion, source-override, relationship, taxonomy,
  ownership, and filename uniqueness invariants are clean in the committed
  state. No secret-like values were found in tracked source/configuration.
- External Tabulator/Google Fonts assets remain an availability dependency;
  SRI/CSP are correct, but a local fallback is still a sensible low-priority
  resilience improvement.
- Repository hygiene is otherwise healthy: no open pull requests, one stale
  unassigned issue (#18, ownership cross-check), and current GitHub Pages/CI
  runs passed. Branch-protection enforcement is the only GitHub setting not
  observable with this integration.

### Follow-up delivery and remaining order

The C-01/C-02 catalogue rulings, F-01/F-02 frontend hardening, D-01–D-03
documentation corrections, Mobile Browse mode, and the Series/Timeline rails
are now applied on PR #36. Its latest CI run passed all **18** browser tests.

1. Confirm `main` branch protection/required checks or harden the raw-updater
   validation path; triage issue #18.
2. Consolidate/archive superseded root audits as the remaining D-04 hygiene
   work, preserving the current Arena checkpoint as the live reference.
3. Optionally vendor the pinned Tabulator assets or implement a local fallback.
4. Consider an additional mobile polish pass (owned-state chips, work summary
   counts, or saved quick-filter views) only after visitor feedback.
