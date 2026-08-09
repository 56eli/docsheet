# PR #60 — Fresh-eyes audit + P0 hotfix + delivery-contract tests

## TL;DR

Three commits on `arena/019fe8d0-docsheet`:

1. **`42ce0b6`** — Fresh-eyes multidisciplinary full-stack audit
   (`docs/audits/2026-08-09-arena-expert-full-audit-019fe8d0.md`,
   14 sections, 6 independent data-integrity probes). Surface
   score agrees with the prior audits; six new gaps called out
   (two are fixed in this PR; four are deferred per owner
   direction).

2. **`4f92d9f`** — Fixes two of the six gaps (delivery-contract
   only, owner-aligned minimal scope):
   - `docs/catalogue-block-map.json` added to
     `build-manifest.json#data` with SHA-256 hash +
     `FrontendDeliveryContractTests
     .test_block_map_drift_fails_manifest_contract` regression
     test.
   - New `ViewsConfigConsistencyTests` class (3 tests) that
     asserts `docs/js/config.js#VIEWS` covers every
     build-emitted user-facing JSON, every VIEWS file actually
     exists in `docs/`, and no two view keys share a file (with
     the documented `master`+`series` → `master.json` exception
     pinned).

3. **`b5ef68b`** — **P0 hotfix: site stuck on "Loading research
   master…".** The 019fe8a5 ES-module refactor of `docs/app.js`
   silently dropped two IIFE-scope declarations (`let table =
   null;` and `let allData = [];`); on first `boot()` the page
   threw `ReferenceError: table is not defined` and never reached
   `aria-busy="false"`, leaving the static loading skeleton on
   screen. CI run `31341418779` (the post-merge main push) failed
   25/25 Playwright specs at `waitForTable()` for the same reason.
   - Both declarations restored with cross-referencing comments
     explaining why they're load-bearing.
   - `docs/index.html` (script `?v=...` + footer build ID) and
     `docs/build-manifest.json` (asset/data SHA-256s, revision
     `row-delivery-p0-20260810.1`) updated to the new app.js
     hash.
   - New `FrontendDeliveryContractTests
     .test_app_js_declares_critical_module_scope_variables` adds
     a regression test so any future refactor that drops a
     `let` in the `critical` tuple will fail this test before
     shipping.

Postmortem: `docs/audits/2026-08-10-row-delivery-p0-hotfix.md`.

---

## Why this needs to merge ASAP

**The live site is broken right now.** Every visitor since PR #59
merged is seeing the static "Loading research master…" skeleton
forever. Branch CI on this PR will prove the fix works
(25/25 Playwright specs should pass); owner visual acceptance
of the deployed footer build ID is the final gate.

---

## Verification (will run on this PR)

- [x] 146/146 deterministic tests pass (8 pre-existing
      `process_data.py` failures are pandas-dependency, unrelated).
- [x] All 5 non-`process_data` `--check` modes green.
- [x] `node --check` on `app.js`, `config.js`, `formatters.js`.
- [x] Local Node-with-mock reproduction: `aria-busy="false"`
      after boot, master.json fetch completes, no
      `console.error`.
- [x] `docs/build-manifest.json` SHA-256s match the committed
      `app.js`, `style.css`, `master.json`, `data.json`,
      `catalogue-block-map.json`.
- [x] `docs/index.html` `?v=c2547cce23b5` and footer build ID
      `app-c2547cce23b5/css-805701f0ca91` both match the manifest.
- [ ] **25/25 Playwright specs pass on this PR's CI** — will
      run automatically; this is the test that will catch any
      regression of the same class.
- [ ] **Owner visual acceptance** of the deployed footer
      `app-c2547cce23b5/css-805701f0ca91` and the 11-colour
      REVISION1 block washes (light + dark + phone Browse).

---

## Scoreboard alignment

No score changes. The audit (`docs/audits/2026-08-09-arena-expert-
full-audit-019fe8d0.md`) confirms the current overall effective
score of 8.5 (gate pass). The only changes to `.scoreboard/
scoreboard.yml` are:

- One new top-priority "row-delivery-class" risk flag
  explaining the 019fe8d0 P0 hotfix + the same-class recurrence
  risk until the manual-workflow-edits.md cutover lands.

---

## Next agent's open work (from `NEXT_AGENT_HANDOFF.md` §6)

- P0 — Apply `.scoreboard/manual-workflow-edits.md` to require
  CI before merge and gate Pages on successful main CI. The
  same incident class (red CI, broken frontend ships to
  production) will recur until this lands. Not in scope of
  this PR — owner-applied GitHub settings.
- P1 — Add a JSDOM-based runtime smoke to CI so the next
  refactor that drops a module-scope declaration fails at
  PR time, not at user-load time. (The static-analysis
  regression test in this PR is the bare minimum; a runtime
  smoke is the next step up.)
- P1 — Address the four deferred UI gaps from the audit
  (#3-#6: no-Veritas-URL indicator, Firefox scrollbar
  fallback, work-family stripe legend, owned:false visual
  cue). Owner-aligned minimal style.

---

## Files changed

| File | Δ | Reason |
|---|---|---|
| `docs/audits/2026-08-09-arena-expert-full-audit-019fe8d0.md` | +841 | New fresh-eyes audit |
| `docs/audits/2026-08-10-row-delivery-p0-hotfix.md` | +392 | New P0 postmortem |
| `docs/app.js` | +11 | Restore `let table` and `let allData` IIFE-scope declarations |
| `docs/build-manifest.json` | 5 lines | New revision, source_baseline, app.js hash |
| `docs/index.html` | 2 lines | New `?v=...` and footer build ID |
| `tests/test_pipeline.py` | +192 | 4 new tests: block-map drift, VIEWS×3, module-scope guard |
| `docs/js/config.js` | unchanged | (already correct) |
| `docs/js/formatters.js` | unchanged | (already correct) |
| `INSTRUCTIONS.md` | 4 lines | Test count 145 → 146 |
| `README.md` | 2 lines | Test count 145 → 146 |
| `NEXT_AGENT_HANDOFF.md` | +28 | P0 module-scope trap + owner-action notes |
| `.scoreboard/scoreboard.yml` | 1 line | Risk flag with hotfix context |
| `.scoreboard/agent-handoff.md` | +76 | 2026-08-10 hotfix session summary |

---

## Reviewer checklist

- [ ] Verify the live footer shows
      `Build: app-c2547cce23b5/css-805701f0ca91` after merge
      (or the staging build for this PR).
- [ ] Open the Everything view and confirm the 11-colour
      REVISION1 block washes render correctly (lecture emerald,
      discussion rose, satsang amber, on-the-road teal, volume
      indigo, office sky, books violet, transcription fuchsia,
      media-misc zinc, undecided orange, fran-grace crimson).
- [ ] Open the dark-mode toggle and confirm the same washes
      render correctly with the new dark tokens.
- [ ] Open on a phone or with viewport ≤720px and confirm
      the Browse mode work cards render.
- [ ] Click any row and confirm the row-details drawer
      shows every field including `research`.

If any of the above fails, file a follow-up PR — the
`FrontendDeliveryContractTests` will not catch UI regressions
(beyond the 25 Playwright specs in CI), so this is the owner's
visual-acceptance step per the project rules.
