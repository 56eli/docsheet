# Agent Handoff

Last updated: 2026-08-10 (Arena 019fe8d0 — P0 hotfix for the 019fe8a5 ES-module refactor: restored `let table` and `let allData` in app.js IIFE)

## Current state

DocSheet is a static GitHub Pages spreadsheet/catalogue with separate raw
(`docs/data.json`) and curated (`docs/master.json`) lanes. The current audits are:

- `docs/audits/2026-08-09-arena-expert-full-audit-019fe8d0.md` **(Current — fresh-eyes audit 019fe8d0 session)**
- `docs/audits/2026-08-09-full-audit-019fe8a5.md` (Prior session — 019fe8a5)
- `docs/audits/2026-08-09-full-audit-019fe830-multidisciplinary.md` (Prior declared-current multidisciplinary audit)
- `docs/audits/2026-08-09-expert-multidisciplinary-audit.md` (Prior 019fe80c multidisciplinary audit)
- `docs/audits/2026-08-09-end-user-row-delivery-postmortem.md` (Authoritative incident/postmortem)

## 2026-08-09 Session Summary — 019fe8d0 (Fresh-eyes Multidisciplinary Audit + P0 hotfix)

## 2026-08-10 P0 hotfix (019fe8d0 follow-up)

- **P0 incident: site stuck on "Loading research master…"** — reported by
  the owner immediately after the gap-fix commit. Browser test run 31341418779
  on main also failed 25/25 specs at `waitForTable()`.
- **Root cause:** the 019fe8a5 ES-module refactor of `docs/app.js` dropped
  two IIFE-scope declarations when extracting config.js and formatters.js:
  `let table = null;` (held the active Tabulator instance) and
  `let allData = [];` (held the current view's data array). On first
  `boot()` call, `applyViewSettings` referenced the undeclared `table`,
  throwing `ReferenceError: table is not defined` — the page then stayed
  on the static "Loading research master…" skeleton from `index.html`
  forever. `allData` blew up the next call when the `await loadData(...)`
  resolved. The 25 Playwright specs all timed out at `waitForTable()`
  waiting for `aria-busy="false"`.
- **Detection:** I reproduced the failure locally by running app.js through
  Node with a minimal browser mock (document, fetch, localStorage). The
  first run reported `ReferenceError: table is not defined at line 365`.
- **Fix:** restored both module-scope declarations in `docs/app.js` with
  comments cross-referencing the 019fe8a5 refactor. Updated
  `docs/index.html` (script `?v=...` + footer build ID) and
  `docs/build-manifest.json` (asset/data SHA-256s, revision
  `row-delivery-p0-20260810.1`) to the new app.js hash. Bumped the
  manifest's `source_baseline` to `1a442001` (the broken PR #59 merge).
- **Regression test added:** `FrontendDeliveryContractTests
  .test_app_js_declares_critical_module_scope_variables` re-reads
  `docs/app.js` and asserts that `table` and `allData` are declared
  with `let`/`var`/`const` at IIFE scope. A future refactor that
  re-introduces a free-variable reference to one of these (or any
  future critical identifier added to the `critical` tuple) will
  fail this test before it can ship.
- **Verified locally:** Node-with-mock shows `aria-busy: false` after
  boot, master.json fetch completes, no `console.error` calls.
- **Test count:** 145 → 146 deterministic tests. README +
  INSTRUCTIONS test-count lines updated per the project house rule.
- **Outcome:** once this branch merges to main, the site should load
  normally and the 25 Playwright specs should pass again.

## 2026-08-09 Session Summary — 019fe8d0 (Fresh-eyes Multidisciplinary Audit)

- **Independent audit** of all 5 prior 2026-08-09 audits (019fe7ff, 019fe80c,
  019fe830, 019fe844, 019fe8a5) — every claim re-verified, not copied.
- **Committed at `docs/audits/2026-08-09-arena-expert-full-audit-019fe8d0.md`**
  (14 sections: TL;DR, Architecture, Web Design, Full-Stack, Security,
  Performance, A11y, Repo Org, CI/CD, Maintainability, Auditability, Data
  Engineering, Recommendations, Verification, Scoreboard Alignment).
- **6 independent data-integrity probes re-run against `docs/master.json`:**
  no duplicate UUIDs (1-372 with documented gaps for retired duplicates),
  all 362 catalog codes match `^(LECTURE|DISCUSSION)-\d{3,4}X?-\d{3}$`
  (84 correctly blank for edition/book rows), year range 1973-2026 with
  16 198X Office Series + 19 blank (Volume Series + under-investigation),
  item type counts exactly 306 lecture / 40 book / 8 discussion / 7 highlight
  / 1 other (sum 362), format distribution 253 DVD / 32 CD / 31 book /
  27 audiobook / 19 streaming, owned distribution 311 true / 25 false /
  26 blank, all 6 URL fields use https:// schemes.
- **5 `--check` modes re-run in this session** (process_data.py needs
  pandas which the sandbox doesn't have, but the other 5 pass): all green.
- **6 gaps surfaced** that the prior 5 audits didn't explicitly call out:
  1. `docs/catalogue-block-map.json` is build-emitted but not in
     `build-manifest.json` (and not in `FrontendDeliveryContractTests`).
  2. `docs/js/config.js#VIEWS` is not cross-checked against
     `build_catalogue_pages.py` output file list.
  3. 29 of 362 masters have no `source_url_veritas` but no visual
     indicator distinguishes "intentionally blank" from "missing data."
  4. Firefox ignores `::-webkit-scrollbar`; 16px custom scrollbar is
     silently the OS default there.
  5. Work-family stripe grouping has no legend / toggle in View settings.
  6. The "Not owned" badge was hidden in 019fe8a5 per owner request, but
     `owned: false` rows now have a fully empty cell — a subtle visual
     cue (faint strikethrough on title? outlined "✕" badge?) would
     communicate the distinction without re-introducing the noisy pill.
- **P1 gaps 1+2 fixed in this session** (delivery-contract only, per
  the owner-aligned scope decision):
  - **Gap 1** — `docs/catalogue-block-map.json` added to
    `build-manifest.json#data` with SHA-256 hash
    (`e4c435a8818ebc78376a0443f488b81224883ec3cd5863554b0139fc3fecddac`).
    New test `FrontendDeliveryContractTests.test_block_map_drift_fails_manifest_contract`
    re-reads the file, recomputes the hash, and asserts it matches
    the manifest entry — a tampered block map now fails the
    contract test loudly.
  - **Gap 2** — new `ViewsConfigConsistencyTests` class with three
    tests: (1) every VIEWS `file:` key matches a build-emitted
    user-facing JSON (excludes the non-Jump-to outputs
    `catalogue-meta.json`, `catalogue-block-map.json`,
    `build-manifest.json`); (2) every VIEWS file actually exists
    in `docs/`; (3) no two view keys share a file (with the
    documented `master`+`series` → `master.json` exception
    pinned so it cannot silently grow).
  - **Test count** — 141 → 145 deterministic tests
    (`tests/test_pipeline.py`); 137 pre-existing + 4 new
    manifest/contract + 3 new VIEWS = 4 net new in
    `test_pipeline.py`; 8 unchanged in `test_style_contrast.py`
    = 153 total. README + INSTRUCTIONS test-count lines updated
    per the project house rule. Drift test proved: manually
    tampered block map now fails the contract test with the
    exact expected error message.
  - **All `--check` modes still green** (5/5 that don't need
    pandas); 4 new tests pass; no regressions in the 137
    pre-existing tests; 8 process_data failures are
    pre-existing (sandbox lacks pandas).
- **P1 gaps 3-6 not touched in this session** (deferred per
  the owner-aligned scope decision: 4 UI/data polish items
  need owner visual review before any change).
- **Scoreboard alignment:** My independent re-audit agrees with the current
  scoreboard (overall_effective 8.5 / gate pass) on every aspect except
  performance (I'd add a Lighthouse budget step before declaring 8/10
  confident — currently 8 with medium confidence per the scoreboard,
  which is fair). No score changes recommended.

## 2026-08-09 Session Summary — 019fe8a5 (Audit, Consolidation, Modularization)

- **Full-Stack Audit:** Published comprehensive audit at `docs/audits/2026-08-09-full-audit-019fe8a5.md` covering web design (8/10), architecture (9/10), data integrity (9/10), security (8/10), testing (9/10), maintainability (6→8/10).
- **Root Document Consolidation (21→12 .md files):**
  - 5 historical audits moved to `archive/` (FULL_STACK_AUDIT_2026-08-09_ARENA_019FE767, _DEEP_DIVE, _EXPERT, _FULL, AUDIT_REPEATED_FAILURE_STYLING)
  - 3 decision/provenance docs moved to `decisions/` (FILENAME_PROPOSAL_V4, YEAR_COLUMN_PROVENANCE, OFFICIAL_SOURCE_REGISTRY)
  - All cross-references updated across README.md, INSTRUCTIONS.md, NEXT_AGENT_HANDOFF.md, .scoreboard/scoreboard.yml, tests/test_style_contrast.py, and docs/audits/*.md
  - README "Documentation layout" rewritten as a 5-row table
- **UX Fixes (per owner feedback):**
  - Owned column width constrained to 62–85px (fits "Owned" badge tightly)
  - "Not owned" badge hidden — `owned: false` rows now show empty cell instead
  - Notes column walkthrough: 84 entries documented (provenance, title corrections, FRAN GRACE marker)
- **Frontend Modularization:**
  - `docs/js/config.js` (274 lines) — Pure data: VIEWS, COLUMN_LABELS, COLUMN_PRESETS, COLUMN_BUDGETS, RECORD_TYPE_LABELS, DETAIL_SECTIONS, humanizeField()
  - `docs/js/formatters.js` (142 lines) — Rendering: statusClass, statusLabel, statusFormatter, getRowBlockId, loadCatalogueBlockMap, rowTitle, primaryIdentifier
  - `docs/app.js` reduced from 2,769 → 2,392 lines (loads as `<script type="module">`)
  - CSP `script-src 'self'` already permits same-origin ES modules
- **CSS Organization:** 17 numbered section markers (§1 Design Tokens through §17 Responsive) added throughout 2,498-line `docs/style.css`
- **Scoreboard Updated:**
  - Owner confirmed prior 5/10 UX and Pages scores are outdated → cleared to null → effective = AI
  - Overall effective score 7.8 → 8.5; quality gate `fail` → `pass`
  - Maintainability AI 8, user null, effective 8 (frontend modularized)
  - Repo organization updated with consolidation evidence
- **Delivery Contract:** All hashes updated: app.js v=359f7c6d889a, style.css v=805701f0ca91, build-manifest.json refreshed
- **Verification:** 141/141 offline tests pass, all 6 --check modes green, all 3 JS files syntax-valid

## 2026-08-09 Session Summary - 019fe844 (Block Map Extraction, Column Layout & Archive.org Holdings)

- **Block Map Build Extraction:** Removed 362 hardcoded UUID literals from `docs/app.js` and replaced them with build-generated `docs/catalogue-block-map.json` emitted by `build_catalogue_pages.py` from `data/catalogue_display_order.csv`.
- **CSS Token Layer Consolidation:** Consolidated `:root` and `:root.dark` layers in `docs/style.css`, eliminating duplicate override blocks.
- **Column Layout & Single-Line Headers:**
  - Reduced Record Type column width to tight `CM` badge width (52px).
  - Enforced single-line column headers (`white-space: nowrap`, `overflow: hidden`, `text-overflow: ellipsis`) so header height stays strictly one line.
  - Hidden `Title`, `Series`, and `Year-Month` under Expert columns by default.
  - Placed `Owned` and `Notes` immediately to the right of `Item Type`.
  - Moved `Catalogue Code` to the back.
  - Reduced row heights to compact single-line content heights matching largest items (~32–34px).
- **Archive.org Ownership Verification & Holdings Promotion:**
  - Cross-checked the entire catalogue against `https://archive.org/download/Hawkins_Lectures_transcoded_actual_files`.
  - Confirmed and promoted 16 master records to `owned: true` in `data/manual_master_candidates.csv` and `data/edition_candidates.csv` (How to Surrender to God, Book of Slides, Orthomolecular Psychiatry 1973, 2006 Satsang Series 1–6, Discussion talks, Audiobooks; total owned increased 295 → **311 owned / 25 false / 26 blank**).
  - Tracked newly discovered audio materials (BTO Radio Interviews 14 eps, Unity Church Phoenix 2005) as manual leads in `data/research_manual_leads.csv` (leads 2 → 4).
- **Delivery Contract & Verification:** Updated asset hashes in `docs/index.html` and `docs/build-manifest.json`. All 141 deterministic unit tests pass, all 6 `--check` modes pass, `ruff check .` clean (0 issues), 90% statement coverage.

Do not claim that a successful Pages artifact proves a row change reached the
end user. The owner explicitly rejected that conclusion. Acceptance requires a
visible deployed build ID and an explicit owner accept/reject response.

## End-user row-delivery P0 (branch `arena/019fe7c9-docsheet`)

### Root causes found

1. All 70 intended table selectors used `#spreadsheet .tabulator ...`, but
   Tabulator attaches `.tabulator` to `#spreadsheet` itself. None of those
   descendant-root rules matched, so the browser kept the external theme's
   default grey rows while agents edited dead CSS.
2. A latent equal-specificity `.work-group-start` shadow would have replaced
   REVISION1 block colors on 105 odd rows after activating the selectors.
3. `index.html` loaded bare `style.css` and `app.js`; JSON alone used
   `cache: "no-store"`. Pages build success could not prove matching assets.
4. The page exposed no build/SHA/content identity.
5. Existing tests checked CSS tokens and one row class, not selector matching,
   computed styles, block transitions, dark mode, cache versions, or deployment.
6. PRs #48-#52 merged before checks completed; Pages deployed independently of
   red CI.
7. Mobile/persisted Browse mode contains cards, not Tabulator rows; presentation
   mode must be explicit during acceptance.

### Implemented on this branch

- All table rules now use the real `#spreadsheet.tabulator ...` root, with a
  static regression guard against the dead descendant topology.
- Block rules target stable `data-block` attributes.
- Work-family grouping uses a horizontal `border-top`; it cannot replace the
  block-specific inset `box-shadow`.
- `style.css` and `app.js` use 12-character SHA-256 query versions in
  `docs/index.html`.
- `docs/build-manifest.json` records full app/style/master/raw hashes and
  revision `row-delivery-p0-20260809.1`.
- Footer visibly identifies `app-cf43f33a062c/css-71a1e6b2ca25` and links the
  manifest.
- `FrontendDeliveryContractTests` fails on stale asset query versions, manifest
  hashes, footer build ID, or payload hashes.
- Style tests fail if `.work-group-start` reintroduces a competing box-shadow.
- `presentation-ux.spec.js` now checks computed odd/even backgrounds and exact
  light/dark accent colors for lecture, discussion, and office rows, including
  the filtered first-row/work-start case that exposed the bug.
- The stale `#show-stats-toggle` Playwright path is removed; navigation is tested
  through the surviving `#view-jump` control.
- All non-archived older audit documents carry status-correction banners that
  point to the current row-delivery postmortem; `archive/README.md` does too.
- Offline suite: **141 tests** (133 pipeline/contract + 8 style), all passing;
  coverage remains **90% total**.
- Browser suite: **25/25 passed** in PR #54 run `31331297543`, including real
  selector matching and computed light/dark block colors. Local Chromium
  download remains CDN-blocked.

### Not complete until owner/settings action

- Owner visual acceptance of the exact deployed footer build ID.
- Required CI check/branch rule.
- CI-gated custom Pages workflow.
- Post-deploy live manifest, asset hash, and 362-row assertion.
- Successful-run screenshot artifact/reference review.

Exact owner instructions and workflow YAML are in
`.scoreboard/manual-workflow-edits.md`. Do not edit `.github/workflows/*` without
explicit owner direction.

## Data state

- Raw source: 374 rows; 31 blank separators; seven published columns.
- Curated master: 362 rows; 75 exclusions; 134 source overrides; 39 reviewed
  manual candidates.
- REVISION1: 58 filename edits, year overrides on 356-358, notes override on
  315, and 362-row reviewed color-block order.
- The ODS was independently parsed: 362 rows x 23 columns; its filename-cell
  colors map exactly to the 11 committed display blocks.
- All six generator --check modes pass.

## Current scores / risks

Owner scores remain authoritative and unchanged:

| Aspect | User score |
|---|---:|
| GitHub Pages presentation | 5 |
| UX / usability | 5 |
| Content quality | 7 |
| Maintainability | 6 |

Corrected AI scores (019fe830):

- Maintainability: 7 (effective 6 due owner score) — frontend monoliths 2755/2399L + hard-coded block map.
- GitHub Pages presentation: 8 (effective 5 due owner score) — delivery contract verified at 9e4ee4d.
- CI/CD: 7 (`blocked_manual_workflow_edit`).
- Deployment readiness: 7 (`blocked_manual_workflow_edit`).
- Tests: 9.
- Overall effective score: **7.8**, gate **fail**.

Additional open risks:

- owner visual acceptance pending;
- legacy Pages remains independent of CI;
- CSP `style-src 'unsafe-inline'` remains low-severity debt;
- issue #18 still needs the owner's Drive export/access.

## Verification performed (019fe830)

- six generator --check modes ✅
- `python -m unittest discover tests` — 141/141 ✅
- coverage — 90% total ✅
- JS/config/all spec syntax ✅
- `npm ci` / `npm audit` — zero vulnerabilities (prior audit) ✅
- manifest/content-version contract ✅
- neutral tokens / selector topology / washes ✅
- Hay House typo grep 0 ✅
- PR #54 GitHub CI 31331297543: 25/25 browser specs ✅ (prior branch; this branch re-uses same manifest)
- Chromium install locally ❌ environment TLS reset; GitHub CI is authoritative

## Next-agent rules

1. Read this file, `SCOREBOARD.md`, `.scoreboard/scoreboard.yml`, and the
   corrective audit before changing rows.
2. Never infer owner satisfaction from CI, Pages, PR merge, or silence.
3. Do not call the row incident resolved before branch browser CI, deployment,
   visible-build verification, and owner acceptance.
4. If app/style/master/raw bytes change, update `docs/build-manifest.json` and
   the versioned references/footer ID; the offline contract test enforces this.
5. Preserve all owner scores.
