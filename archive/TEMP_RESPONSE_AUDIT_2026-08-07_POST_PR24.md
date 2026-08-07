# Temporary Response — Post-PR #24 Project Audit (2026-08-07)

## One-sentence summary

DocSheet is structurally healthy after PR #24, but the audit found and fixed one generated-output drift: `docs/source-overrides.json` and `docs/review-overview.json` were stale after the new 127 approved source overrides.

## Scope reviewed

- Repository state on branch `arena/019fdcc5-docsheet`, based on `main` commit `fff4613` (PR #24 merged 2026-08-07).
- Recent PR #24 commits and changed files.
- Python data pipeline, generated Pages JSON, catalogue/review data, frontend syntax, CI/test configuration, and existing audit/handoff docs.

## Recent-change summary from PR #24

PR #24 added or changed:

- Year provenance model:
  - `data/year_provenance.csv`
  - `YEAR_COLUMN_PROVENANCE.md`
  - `year_source` exposed next to Year-Month in the Pages UI.
- Amazon direct product-link support:
  - `source_url_amazon` added to master/page outputs.
  - 18 direct Amazon links now present in the master.
  - Approved source overrides increased from 109 to 127.
- Year/format cleanup:
  - 11 edition audiobook blank years fixed through inheritance.
  - Office Series outliers added: Stress 1987 and Death and Dying 1983.
  - Satsang/Discussion/Office docs and filename proposal regenerated.
- Frontend changes:
  - `docs/app.js` updated for Year Source and Amazon source URL display.
- Test coverage:
  - `tests/test_pipeline.py` extended for new year/source behavior.

## Verification performed

### Deterministic checks — pass after generated-output fix

Executed in a clean temporary Python venv:

```bash
python process_data.py --check
python build_research_master.py --check
python build_catalogue_pages.py --check
python reconcile_research_master.py --check
python map_series_taxonomy.py --check
python -m unittest discover tests
coverage run -m unittest discover tests && coverage report
node --check docs/app.js
node --check playwright.config.js
node --check tests/csv-export.spec.js
node --check tests/column-layout.spec.js
```

Results:

- `process_data.py --check`: pass.
- `build_research_master.py --check`: pass.
- `build_catalogue_pages.py --check`: initially failed, then pass after regeneration.
- `reconcile_research_master.py --check`: pass.
- `map_series_taxonomy.py --check`: pass.
- Python unit suite: 104/104 pass.
- Coverage: 91% total, above 80% gate.
- JavaScript syntax checks: pass.

### Browser smoke tests

`npm ci` succeeded. `npm run test:e2e` could not execute because the sandbox had no Playwright browser installed. Attempting `npx playwright install chromium` failed with repeated TLS `ECONNRESET` download failures from the Playwright CDN. This is an environment/network setup failure, not an application-test assertion failure.

## Fixed during audit

`build_catalogue_pages.py --check` reported stale generated Pages files:

- `docs/review-overview.json`
- `docs/source-overrides.json`

Root cause: PR #24 increased approved source overrides to 127, but these two generated JSON files still reflected the old 109-count/old override list.

I regenerated Pages catalogue outputs with:

```bash
python build_catalogue_pages.py
```

The resulting diff is limited to the two expected generated JSONs:

- `docs/review-overview.json`: Source Overrides count updated from 109 to 127.
- `docs/source-overrides.json`: 18 approved Amazon `source_url_amazon` overrides added to the Pages review sheet.

## Current project/data state

From `docs/catalogue-meta.json` and CSV profiling:

| Metric | Current value |
|---|---:|
| Everything rows | 378 |
| Curated master rows | 358 |
| Master record types | 307 lecture, 40 book, 10 discussion, 1 untyped |
| Candidate rows in Everything | 8 Veritas, 4 discovery, 4 HayHouse, 4 Audible, 0 pending promotion |
| Migration review rows | 374 |
| Exclusions | 69 |
| Approved source overrides | 127 |
| Amazon direct links in master | 18 |
| Work-family memberships | 334 approved |
| Edition candidates/promotions | 24/24, all promoted |
| Veritas products | 191 |
| HayHouse products | 24 |
| Audible products | 26 |
| Product relationships rendered | 336 |
| Hand-maintained related-material relationships | 8 |
| Series compilations | 7 |
| Series taxonomy mappings | 179 mappings, 6 queued rows, all ruled approved/rejected |
| Filename proposal coverage | 358/358 |
| Year Source coverage | 358/358 |
| Blank year rows | 18 |
| Blank format rows | 2 |

## Current known gaps / risks

### P0 / immediate

1. **Generated-output drift was present and fixed.** This branch now needs commit/push so `docs/source-overrides.json` and `docs/review-overview.json` match PR #24 inputs.
2. **Playwright e2e not locally verified in sandbox** because browser install failed on CDN TLS resets. CI should still run this because the workflow installs Chromium fresh.

### P1 / data decisions

1. **18 blank year rows remain**:
   - 13 intentional Volume Series blanks (`Blank: intentional pre-2000 (Volume Series)`).
   - 5 under-investigation blanks: Verification of Spiritual Realities parts, `"In the World But Not of It" – Audio`, and `God is Hidden Within the Beauty of the Music`.
2. **2 blank format rows remain**:
   - `Progressive Levels of Consciousness - A Special Talk Presented in Oxford (2003)` has year 2003 but no format.
   - `"In the World But Not of It" – Audio` remains untyped/no format/no year.
3. **Record 246 remains the sole allowed untyped record** and still needs an owner ruling.
4. **Official/discovery queues remain real review work**: 4 NC discovery rows, 4 HayHouse unreviewed, 6 Audible unreviewed, 3 Audible possible-related matches.
5. **Streaming coverage is still partial**: 36 approved streaming rows currently apply **59** master reference URLs (one product can map to several masters/parts); remaining Veritas lectures likely need continued batch review.

### P2 / docs clarity

1. Existing deep audit prose still contains pre-PR #24 baseline counts in places, so I added this post-PR audit file rather than rewriting every historical section.
2. Reconciliation report remains technically accurate but potentially confusing because expected promotion/edition-layer extras can look like unreconciled drift to a new reader.
3. Series taxonomy queue semantics should be clarified: 6 queued rows remain visible for conflict transparency even though all are ruled.

## Recommendations

1. Commit and push the regenerated Pages JSON fix immediately.
2. Run CI after push; treat local Playwright failure as inconclusive unless CI e2e also fails.
3. Next data task: resolve record 246 and the two blank-format rows first because they are small, high-signal catalogue holes.
4. Next docs task: update the main deep-audit doc or handoff to point to this post-PR #24 audit and clarify current counts.
5. Next research task: continue streaming URL mapping in small approved batches.

## Follow-up requested in chat: Volume Series filename mismatch

After the audit summary, the Volume Series proposed filenames were inspected side-by-side. The cause was not in the live build logic; `build_research_master.py` only applies the reviewed `data/filename_proposal_YYYYMM.csv` mapping. The reviewed CSV itself contained bad Volume groupings: UUIDs 206-207 (Volume III) were labeled as Volume II parts 3/4 and 4/4, while UUIDs 213-214 (Volume VI/VII) were labeled as Volume V parts 4/5 and 5/5. I corrected the reviewed filename CSV, regenerated master and Pages JSON, documented the fix in `FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md`, and added a regression test that pins each Volume Series title to its own part group.
