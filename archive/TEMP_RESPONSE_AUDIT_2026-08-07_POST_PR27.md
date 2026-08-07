# Temporary Response — Full Project Audit & Post-PR #27 Review (2026-08-07)

**Branch:** `arena/019fdd68-docsheet` (based on `main` at commit `918e66512de8bd3cdf13e5c70bd8e78ae61ce28c`, PR #27 merge)
**Date:** 2026-08-07
**Auditor:** Senior Developer & Data Analyst pass (second session of the day)
**Scope:** Full repository audit — 9 Python pipeline modules, 24 `data/*.csv` review overlays, 20 `docs/*.json` generated sheets, frontend (`index.html` / `app.js` / `style.css`), 3 GitHub Actions workflows, 107 unit tests + 8 Playwright specs, root/decisions/archive documentation, and the recent changes from PRs #24–#27 (all merged today).

---

## 1. Executive Summary & Verdict

**Verdict: DATA HEALTHY — 100% RECONCILED & DETERMINISTIC. ONE LIVE DEFECT FOUND: CI RED ON `main` (stale Playwright spec after the 0-candidate ruling) — root-caused and fixed in this branch.**

The catalogue data layer is in the best state it has ever been: 366 curated masters, **zero unreviewed candidates in every lane**, 0 untyped/blank-series/blank-format records, and every `--check` mode green. PR #27's data changes (Map-poster exclusion, 198X Office Series standardization, Power-vs-Force disambiguation, filename hygiene) were independently re-verified row-by-row. However, the Playwright browser suite was **not updated for the new 0-candidate reality**, so the merge of PR #27 left CI failing on `main` (run `31202697657`).

### Key System Health Metrics (independently re-executed this session)

| Check | Result |
|---|---|
| `build_research_master.py --check` | ✅ pass |
| `build_catalogue_pages.py --check` | ✅ pass |
| `reconcile_research_master.py --check` | ✅ pass |
| `map_series_taxonomy.py --check` | ✅ pass |
| `process_data.py --check` | ✅ pass |
| Unit tests | ✅ **107/107** (~3s, offline) |
| Coverage (gate 80%) | ✅ **91% total** / 1,813 stmts (per-module: `_common` 100%, fetch 95%, `process_data` 94%, `generate_lecture_review` 96%, `generate_migration_ledger` 99%, `reconcile` 98%, `build_research_master` 89%, `map_series_taxonomy` 89%, **`build_catalogue_pages` 88%**) |
| JS syntax (`app.js`, both specs) | ✅ pass |
| Live site `56eli.github.io/docsheet` | ✅ serves post-PR #27 state (366 master / 0 candidates; Pages deploy run `31202695865` green) |
| CI on `main` (latest run) | ❌ **failure — 1 of 8 Playwright specs** (see F1) |

### Catalogue state (all cross-checked against `docs/catalogue-meta.json`, the live site, and the generated data)

- **Master:** 366 = 310 lecture / 40 book / 8 discussion / 7 highlight / 1 other; 0 untyped; blank series 0; blank format 0; blank year 17 (13 undated *Volume Series* DVDs + 4 undated *On The Road* lectures — documented exceptions).
- **Everything view:** 366 master + 0 candidates of any type (`everything_record_types` all-zero candidates confirmed in committed meta **and on the live site**).
- **Office Series:** 16/16 lectures standardized to `year=198X` (`year_source = "Ledger: recording date 198X"`), catalogue codes `LECTURE-198X-001..016`.
- **Catalogue codes:** 281 distinct (lecture/discussion only). **Source overrides:** 133 approved (incl. 18 Amazon). **Exclusions:** 72.
- **Source URLs on master:** Veritas 335 (= 335 derived primary relationships), Hay House 28, Nightingale-Conant 6, Audible 21, Amazon 18; `reference_url_1` on 63 masters (36 approved streaming rows).
- **Relationships:** 343 rendered = 335 derived primary + 8 hand-maintained `related_material`; product_relationships CSV correctly holds only the 8 non-primary rows.
- **Work families:** 342 memberships all `approved` → coverage 366/366. **Editions:** 24/24 promoted. **Manual candidates:** 40/40 promoted. **Series taxonomy:** 176 approved / 0 proposed / 10 rejected (186 matched). **Series compilations:** 7.
- **Filename proposal:** 366/366 covered, 366 unique safe + 366 unique display names; PvF pair (320/331) disambiguated; 3 Satsang month prefixes corrected; trailing-dot collision on UUID 245 resolved.
- **Discovery lanes:** `official_discovery_queue.csv` and `new_work_review_queue.csv` are header-only (0 rows); `candidate_pending_promotion` 0.

---

## 2. Findings

### F1 — HIGH (fixed in this branch): CI red on `main` — stale Playwright candidate assertions

- **Symptom:** CI run `31202697657` on the PR #27 merge commit **failed**: *"1 failed — `tests/csv-export.spec.js:65:1 › Everything view separates curated master records from candidates`; 7 passed."* (An identical earlier red run on PR #24's merge, `31190252289`, was a different, already-resolved generated-output drift fixed via PR #25.)
- **Root cause:** PR #27 ruled the last candidate lane to zero (`candidate_veritas` 1 → 0). The spec still asserted the review filter is visible and offers `option[value="candidate_veritas"]`. But `docs/app.js` `configureReviewFilter()` **by design** hides the review toolbar whenever no filter field has more than one distinct value — with 366× `master` rows there is nothing to filter, so the toolbar never renders. The app behavior is *correct*; only the test was stale.
- **Fix (this branch, `tests/csv-export.spec.js`):** the spec is now **data-driven** — it fetches `master.json`, derives the record-type set, and asserts either (a) candidates present ⇒ filter offers every provenance value and selecting *Curated master* filters correctly, or (b) all-master ⇒ `expect(recordTypes).toEqual(['master'])`, the toolbar is hidden, and the status line shows the bare count (`Showing: N`, matching `updateSearchStatus`, which only prints `X of Y` while a filter is active). The badge assertions (all badges read "Curated master") hold in both branches. `node --check` passes; Playwright execution deferred to CI (Chromium cannot be installed in the sandbox — known trap).
- **Action needed:** merge this branch's PR to turn `main` green again.

### F2 — LOW (fixed in this branch): documentation-currency drift in the test-count/coverage claims

- `README.md` §Tests said "**103 tests**" / "passes at **92%** … every pipeline module is **≥ 89%**"; `INSTRUCTIONS.md` repeated both. Measured today: **107 tests**, **91%** total, and `build_catalogue_pages.py` at **88%** (the per-module claim drifted when PR #26 added the 4 doc-currency tests without covering that module's new branches).
- The `tests/test_pipeline.py` documentation-currency guards do **not** cover these two strings, so the drift slipped through. Both files updated in this branch (107 tests; 91% total; every module ≥ 88%). Suggestion (not done): extend the currency guard to parse the README test-count so it cannot drift again.

### F3 — LOW (open, documented since 2026-08-03): four always-empty master columns

`location_physical`, `location_digital`, `location_streaming`, `reference_url_2` are empty on all 366 masters. An owner populate-or-drop decision remains pending (tracked in `NEXT_AGENT_HANDOFF.md` §6).

### F4 — LOW (note): international discovery queue larger than last reported

`data/international_discovery_queue.csv` holds **36 rows** (7 `queue_created` publisher rows + 29 unreviewed editions: 19 Spanish — *Ediciones El Grano de Mostaza*, 6 French — *Guy Trédaniel*, 4 Portuguese — *Pandora*). The archived post-PR #26 audit said "19 records"; the queue was already 36 rows then (PR #26/#27 did not touch the file). Recorded here so the next session's counts are right; no data defect.

### F5 — INFO: `reference_url_1` masters now 63 (docs say 59)

Grew with the 2026-08-07 promotions (362–372) adding reference URLs — expected growth, not drift. Only 6 refs are literal `…-streaming/` URLs; the rest are lecture-page/archive.org refs.

### F6 — INFO: CI deprecation annotation

CI log annotates that `actions/*@v4` target deprecated Node 20 and are being force-run on Node 24. Cosmetic today; bump action majors when they publish Node-24 defaults. (Any workflow edit still requires owner application — the Arena app cannot push `.github/workflows/*`.)

---

## 3. Audit of Recent Changes (PRs #24–#27, all 2026-08-07)

Diffs verified via the GitHub compare API against each PR's base:

- **PR #24** (`fff4613` → year provenance + Amazon links): introduced `data/year_provenance.csv` + `year_source` column (verified: every master year carries a provenance string; the 16 Office rows read `Ledger: recording date 198X`) and 18 Amazon overrides (verified: `source_url_amazon` populated on 18 masters). Left a docs-JSON drift that failed CI on its merge (`31190252289`) and was fixed in PR #25 — confirmed resolved.
- **PR #25** (`4b81e94`): regenerate-only sync (`review-overview.json`, `source-overrides.json`, `docs/international-products.json`, `year_provenance.csv`) + Volume Series filename regrouping; CI green since.
- **PR #26** (`becc873`): promoted Highlights 362–368, NC/Audible programs 369–371, Hay House 372; excluded duplicates 246/281/284 → master 366, 0 untyped; Maps/Audible/HayHouse lanes ruled to a single remaining Veritas candidate. All reflected correctly in generated outputs.
- **PR #27** (`918e665`, HEAD): 21-row diff across ledger/master/filename — verified row-by-row:
  - Map poster (product 1560) → `veritas_mapping_decisions.csv` +1 `excluded_related_material`; Veritas decisions 18, approved 12; Everything candidates all-zero (matches meta + live site).
  - 16 Office Series lectures → `198X` with codes `LECTURE-198X-001..016`; no other series carries `198X`.
  - UUID 331 series `Volume Series` → `Books` (1-row `edition_promotions.csv` diff) + PvF 320/331 title/filename disambiguation (`[1-2]`/`[2-2]` brackets gone).
  - Satsang month prefixes 256/259/262 corrected (`06→05`, `03→02`) — title month now matches filename month; `....mp4` → `.mp4` on 245.
  - Regenerated outputs are internally consistent; all 5 `--check` modes pass.
  - **Miss:** the Playwright spec (F1).

---

## 4. Changes Made in This Branch

1. **`tests/csv-export.spec.js`** — data-driven record_type/review-filter test (F1 fix); `node --check` green.
2. **`README.md`, `INSTRUCTIONS.md`** — test count 103 → **107**; coverage 92% → **91%**; per-module floor claim → **≥ 88%** (F2 fix).
3. **`archive/TEMP_RESPONSE_AUDIT_2026-08-07_POST_PR27.md`** — this report; indexed in **`archive/README.md`**.
4. **`NEXT_AGENT_HANDOFF.md`** — added the post-PR #27 session entry (CI-red cause + fix, corrected claims).

No pipeline code, workflow files, or generated artifacts were touched; `git diff` is test-spec + documentation only.

---

## 5. Verification Command Log (all executed this session)

```bash
for s in build_research_master build_catalogue_pages reconcile_research_master map_series_taxonomy process_data; \
  do /tmp/venv/bin/python $s.py --check; done            # 5× green
/tmp/venv/bin/coverage run -m unittest discover tests     # Ran 107 tests — OK
/tmp/venv/bin/coverage report                             # TOTAL 1813 stmts, 91% (gate 80%)
node --check docs/app.js && node --check tests/csv-export.spec.js && node --check tests/column-layout.spec.js
gh run list --branch main                                 # CI run 31202697657 = failure (F1)
gh api repos/56eli/docsheet/compare/becc873...918e665     # PR #27 diff inspection
curl/fetch_page https://56eli.github.io/docsheet/catalogue-meta.json  # live = 366/0 candidates
```

Sandbox traps re-confirmed: pandas absent from base image → use `/tmp/venv`; PEP 668 blocks system pip; `veritaspub.com` and even `56eli.github.io` unreachable via curl/urllib from the sandbox (use the page-fetch tool); Chromium download fails (Playwright is CI-only).

---

## 6. Prioritized Next Steps

1. **P0 — Merge this branch's PR**: turns `main` CI green (F1) and syncs the doc claims (F2).
2. **P1 — International queue**: rule the 29 unreviewed translated editions (19 ES / 6 FR / 4 PT) and advance the 7 `queue_created` publisher extractions (`data/international_discovery_queue.csv`; see `OFFICIAL_CATALOGUE_DISCOVERY.md`).
3. **P2 — Streaming blind-spot batch**: remaining ~115 Veritas slugs to probe for `-streaming` endpoints (`data/veritas_streaming_urls.csv`, Option A).
4. **P2 — Owner rulings**: populate-or-drop the 4 always-empty columns (F3); currency-guard extension for README/INSTRUCTIONS test-count strings (F2 note).
