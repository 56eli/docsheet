# Agent Handoff

Last updated: 2026-08-09 (Arena 019fe830 multidisciplinary re-audit - Web Designer, Full-Stack & Data Engineer)

## Current state

DocSheet is a static GitHub Pages spreadsheet/catalogue with separate raw
(`docs/data.json`) and curated (`docs/master.json`) lanes. The current audits are:

- `docs/audits/2026-08-09-full-audit-019fe830-multidisciplinary.md` **(Declared current - 019fe830 multidisciplinary re-audit, Web/Full-Stack/Data, 9e4ee4d)**
- `docs/audits/2026-08-09-expert-multidisciplinary-audit.md` (Prior 019fe80c multidisciplinary audit)
- `docs/audits/2026-08-09-full-stack-data-engineering-audit.md` (Prior full audit & cleanup)
- `docs/audits/2026-08-09-end-user-row-delivery-postmortem.md` (Authoritative incident/postmortem)

## 2026-08-09 Session Summary - 019fe830 re-audit (Web/Full-Stack/Data)

- **Full multidisciplinary re-audit (this session):** Re-executed all six --check modes, 141/141 tests at 90% (78-100% per module), node --check, CSP/SRI, CSV-JSON parity, token chromaticity, selector topology. Record: `docs/audits/2026-08-09-full-audit-019fe830-multidisciplinary.md` (read-only, promoted as declared-current in README/INSTRUCTIONS). Verified neutral palette (#f9f9fb/#0d0d0d, no slate, washes 8.5%), correct #spreadsheet.tabulator topology (63 correct vs 0 dead), content-versioned assets 39e1208f672b/e67530fcaebe + manifest row-delivery-p0-20260809.1. Confirmed Hay House traqnscending typo already fixed at 9e4ee4d (grep 0, master 294 correct). Updated scoreboard AI scores (maintainability 9->7, pages 7->8).
- **Prior session 019fe80c - Multidisciplinary Audit + UX polish:** Full pass recorded in `docs/audits/2026-08-09-expert-multidisciplinary-audit.md`; unlocked column resizing (fitDataFill + renderHorizontal:"basic"), widened scrollbars 12->16px, proposal-filename 13px semi-bold, work-family striping (#fafafa/#1c1c1c), header width unlock, search highlighting, asset version hashes. 141/141, 6/6 --check, 0 linter, 90% coverage.

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
