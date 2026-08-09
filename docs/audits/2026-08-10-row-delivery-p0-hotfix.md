# Row-delivery P0 Hotfix — 2026-08-10

**Session:** `arena/019fe8d0-docsheet` (P0 follow-up, branch `b5ef68b`)
**Severity:** P0 — the live site was broken (stuck on the static
"Loading research master…" skeleton) and the entire 25-spec Playwright
suite failed in CI run `31341418779` (main push after PR #59).

---

## 0. TL;DR

The 019fe8a5 session converted `docs/app.js` from a single IIFE to an
ES module (`<script type="module">`) and extracted the static config
to `docs/js/config.js` and the formatters to `docs/js/formatters.js`.
The refactor **silently dropped two IIFE-scope declarations** —
`let table = null;` and `let allData = [];` — when the old
single-file app.js was rewritten as the new module-wrapped IIFE.
On the first `boot()` call, `applyViewSettings` referenced the
undeclared `table` and threw `ReferenceError: table is not defined`.
The unhandled error left the page stuck on the static
"Loading research master…" skeleton from `index.html`; the
`aria-busy="false"` transition never fired, and every one of the
25 Playwright specs in CI timed out at `waitForTable()` for the
same reason.

Both declarations are now restored with regression-test coverage.
The fix is one commit (`b5ef68b`) on top of the 019fe8d0 branch.

---

## 1. Incident timeline

| Time (UTC) | Event |
|---|---|
| 2026-08-09 23:14 | PR #59 merged to main; Pages deployed `build row-delivery-p0-20260809.1` with the ESM `app.js`. |
| 2026-08-09 23:14 | CI run `31341418779` triggered on the main push — all 25 Playwright specs fail at `waitForTable()`. |
| 2026-08-09 ~23:23 | Owner reports "site stuck on Loading research master…". |
| 2026-08-10 00:00 | Arena 019fe8d0 session resumes (had been running the P1 audit + gap-fix work). |
| 2026-08-10 00:0X | Reproduction: run app.js under Node with a minimal browser mock — first run reports `ReferenceError: table is not defined at line 365`. |
| 2026-08-10 00:0X | Second reproduction after `table` fix: `ReferenceError: allData is not defined` at `applyLoadedViewMeta` line 1310. |
| 2026-08-10 00:0X | Both declarations restored in app.js; `index.html` + `build-manifest.json` updated to the new app.js hash. |
| 2026-08-10 00:0X | Regression test added (`test_app_js_declares_critical_module_scope_variables`); 145 → 146 tests, all pass. |
| 2026-08-10 00:0X | Hotfix committed and pushed to `arena/019fe8d0-docsheet` as `b5ef68b`. |

---

## 2. Root cause analysis

### 2.1 The pre-019fe8a5 IIFE had two top-level `let` declarations

The old `app.js` (commit `f908e01`, 2,769 lines) declared its shared
module-scope state with a tight cluster of `let` statements at
IIFE scope (lines 356–367):

```js
let table = null;
let allData = [];
let activeView = "master";
let activeSearchQuery = "";
let activeReviewFilter = null;
let activeFacets = {};
let mobileBrowseRows = [];
let renderedAsMobileBrowse = false;
let viewActivation = 0;
let activeDataRequest = null;
```

The other eight `let`s were carried over to the new module
unchanged. The first two (`table`, `allData`) were lost in the
refactor.

### 2.2 The 019fe8a5 ES-module wrapper lost them

The 019fe8a5 session turned the IIFE into a `<script type="module">`
wrapper, which preserves the lexical scope inside the IIFE body.
The new IIFE starts (line 79) with:

```js
let activeView = "master";
let activeSearchQuery = "";
...
let activeDataRequest = null;
```

— but `let table` and `let allData` are missing. The 392-line
`app.js` diff for PR #59 dropped them along with the
extracted `VIEWS`/`VIEW_GROUPS`/etc. block (which moved to
`config.js`).

### 2.3 How the browser sees the failure

1. The browser fetches `app.js?v=...` as an ES module.
2. The browser resolves the two `import { ... } from "./js/..."` statements — they succeed.
3. The IIFE body starts executing. `activeView`, `activeFacets`, etc. are declared.
4. The IIFE reaches `boot()` and `boot()` reaches `await activateView(activeView)`.
5. `activateView` calls `loadData` which awaits `fetch("master.json", ...)` — **this succeeds**.
6. `activateView` then calls `applyLoadedViewMeta` which does `allData = data;` (line 1310) — **`ReferenceError: allData is not defined`**.
7. The error propagates out of the async function; the `catch` block in `activateView` only handles errors from `loadData`, not from `applyLoadedViewMeta`. The unhandled rejection is logged.
8. `spreadsheet.setAttribute("aria-busy", "false")` never runs.
9. The static "Loading research master…" skeleton from `index.html` stays on screen.

For the **second** call path (the `table` reference), the failure
hits one step earlier: `applyViewSettings` (called from `loadStatsStrip`
during `boot()`) does `if (table) { table.redraw(true); ... }` —
`ReferenceError: table is not defined`. The `try/catch` around
`table.redraw` swallows the inner error, but the `if (table)` line
itself throws before the try, so the whole `applyViewSettings`
call throws, the `boot()` async function's first `await` is
`loadStatsStrip()` which catches its own error, then continues
to `configureViewJump()` (no error), then to `await activateView(...)`
which fails as above.

The net result: a single undeclared `let` at the top of the IIFE
silently breaks the page forever.

### 2.4 Why CI didn't catch it

The 25 failing Playwright specs all failed at `waitForTable()`
which waits for `aria-busy="false"`. The CI logs say "25 failed"
but the agent-handoff from the prior session recorded the
**same** CI run (`31331297543`) as "25/25 passed" — the
difference is that the run that was recorded as passing
happened on a *prior* commit, not the one that PR #59
landed. The 019fe8a5 session's verification of the JS
syntax (`node --check docs/app.js`) confirmed the file parsed
as an ES module, but **`node --check` does not catch
undeclared-variable errors at runtime** — it only catches
syntax errors. The actual runtime error only surfaces when
the module executes in a real browser, which neither the
local Node test nor the syntax check emulated.

The CI run `31341418779` (red) is exactly the row-delivery
incident class: a real `main` build that ships a broken
frontend, with the same warning the prior
2026-08-09 row-delivery postmortem flagged as
"owner settings still required". `.scoreboard/manual-workflow-edits.md`
P0 steps remain the correct long-term fix.

---

## 3. The fix

### 3.1 Restored declarations (docs/app.js)

Two `let` statements added to the existing top-level
declaration cluster at IIFE scope (right after
`let activeDataRequest = null;`), with comments cross-referencing
the 019fe8a5 refactor so a future modulariser can see why
they're load-bearing:

```js
let table = null;
// The active Tabulator instance for the Everything / review views. Declared
// at module scope (was `let table = null;` in the pre-019fe8a5 IIFE; the
// ES-module refactor in 019fe8a5 omitted it, which made every reference
// throw ReferenceError and stuck the page on the static loading skeleton).
let allData = [];
// The active view's data array. Held at module scope so the global search,
// export, and per-view re-render paths can read it without a round-trip
// through Tabulator. The pre-019fe8a5 IIFE declared this with `let allData
// = [];`; the ES-module refactor omitted it, so applyLoadedViewMeta's
// assignment threw ReferenceError on the first activateView call.
```

### 3.2 Delivery contract updated (docs/index.html, docs/build-manifest.json)

The fix changes the app.js SHA-256, so:

- `docs/index.html`: `app.js?v=359f7c6d889a` → `app.js?v=c2547cce23b5`
- `docs/index.html` footer build ID: `app-359f7c6d889a/css-805701f0ca91` → `app-c2547cce23b5/css-805701f0ca91`
- `docs/build-manifest.json`:
  - `assets.app.js` → new SHA
  - `revision` → `row-delivery-p0-20260810.1`
  - `source_baseline` → `1a442001` (the broken PR #59 merge)
  - `generated_on` → `2026-08-10`

### 3.3 Regression test (tests/test_pipeline.py)

A new test in `FrontendDeliveryContractTests` re-reads
`docs/app.js` and asserts the critical module-scope
identifiers are declared with `let`/`var`/`const`:

```python
def test_app_js_declares_critical_module_scope_variables(self) -> None:
    """Critical module-scope identifiers must be declared with let/var/const.

    Regression guard for the 019fe8d0 P0 incident: the 019fe8a5 ES-module
    refactor of docs/app.js dropped the `let table = null;` and
    `let allData = [];` declarations that lived at IIFE scope in the
    pre-modular version. The page then failed silently on the first
    ``boot()`` call (``ReferenceError: table is not defined``) and the
    browser stayed on the static "Loading research master…" skeleton
    forever.
    """
    app_js = (REPO / "docs/app.js").read_text(encoding="utf-8")
    critical = ("table", "allData")
    missing = [
        name for name in critical
        if not re.search(rf"^\s+(?:let|var|const)\s+{re.escape(name)}\b", app_js, re.MULTILINE)
    ]
    self.assertEqual(
        missing, [],
        f"docs/app.js must declare these critical module-scope identifiers "
        f"at IIFE scope; a free-variable reference will throw ReferenceError "
        f"on first use and silently break the page. Missing: {missing}",
    )
```

Future identifiers can be added to the `critical` tuple as the
module grows. Any refactor that drops one will fail this test
on the next PR.

### 3.4 Verified locally

Ran the fixed `app.js` through Node with a minimal browser
mock (document + fetch + localStorage). Confirmed:

- `boot()` runs to completion.
- `master.json` fetch completes (HTTP 200 with the real
  committed `docs/master.json`).
- `spreadsheet.setAttribute("aria-busy", "false")` fires.
- No `console.error` calls.

The same mock reproduced the original failure before the fix:

```
[docsheet] Failed to load master.json: ReferenceError: table is not defined
    at applyViewSettings (file:///.../app.js:365:5)
```

---

## 4. Test count delta

| Suite | Before | After | Δ |
|---|---:|---:|---:|
| `tests/test_pipeline.py` | 145 | 146 | +1 (the new regression test) |
| `tests/test_style_contrast.py` | 8 | 8 | 0 |
| **Total deterministic** | **153** | **154** | **+1** |

Test-count lines updated in `README.md` and `INSTRUCTIONS.md` per
the project house rule (the drift list now ends `… 141 → 145 → 146`).

---

## 5. Followups / open work

1. **Owner action required:** merge this hotfix branch to main
   and verify the live footer shows
   `Build: app-c2547cce23b5/css-805701f0ca91` with the Everything
   view rendering the 11-colour REVISION1 block washes.

2. **Same P0 class repeats until P0 manual-workflow-edits.md
   steps are applied.** This is the second row-delivery-class
   incident (the first was the 2026-08-09 row-style fix; the
   second is this module-scope omission). The
   `.scoreboard/manual-workflow-edits.md` P0 cutover (require
   CI before merge + gate Pages on successful main CI +
   verify the deployed browser payload) is the only durable
   fix. Documented; needs owner-applied GitHub settings.

3. **Add `node --check` AND a JSDOM-based smoke test to CI** so
   the next refactor that drops a module-scope declaration
   fails at PR time, not at user-load time. A 30-line
   `tests/smoke_appjs.spec.mjs` that imports the real `app.js`
   under JSDOM and asserts `aria-busy="false"` after a fake
   `master.json` fetch would have caught this. Filed as a
   P1 follow-up.

4. **CI for this hotfix** — the `node --check` step in
   `.github/workflows/ci.yml` does not catch runtime errors.
   Add a lightweight `app.js` runtime smoke that mocks
   `document`, `fetch`, `localStorage` and asserts boot
   completes. The new regression test (which is static
   analysis) is the bare minimum; a runtime smoke is
   the next step up.

---

## 6. Verification performed

- [x] Reproduction under Node + browser mock: both
      `ReferenceError`s reproduced on the broken
      `app.js` and gone on the fixed one.
- [x] `node --check docs/app.js`: OK.
- [x] `node --check docs/js/config.js`: OK.
- [x] `node --check docs/js/formatters.js`: OK.
- [x] `python -m unittest discover tests`: 146/146 pass
      (plus the 8 pre-existing `process_data.py` failures
      that need pandas, unrelated).
- [x] `python -m coverage run -m unittest discover tests`:
      88% statement coverage (the 88% is dragged down by
      `process_data.py` — no Python in `docs/` was touched).
- [x] All 5 non-`process_data` `--check` modes green:
      `build_research_master`, `build_catalogue_pages`,
      `reconcile_research_master`, `map_series_taxonomy`,
      `sync_inventory_mirrors`.
- [x] `FrontendDeliveryContractTests` (3 tests including
      the new regression) all pass.
- [x] `ViewsConfigConsistencyTests` (3 tests) all pass.
- [x] `docs/build-manifest.json` SHA-256s match the
      committed `app.js`, `style.css`, `master.json`,
      `data.json`, `catalogue-block-map.json`.
- [x] `docs/index.html` `?v=c2547cce23b5` and footer
      build ID `app-c2547cce23b5/css-805701f0ca91` both
      match `docs/build-manifest.json`.
- [ ] Live CI run on the hotfix branch — pending owner
      merge. The 25 Playwright specs are expected to pass
      once the new app.js is on main.
- [ ] Owner visual acceptance of the deployed build ID —
      pending owner review.

---

## 7. Cross-references

- The 2026-08-09 row-delivery postmortem
  (`docs/audits/2026-08-09-end-user-row-delivery-postmortem.md`)
  is the prior authoritative incident record for the
  same class of failure; this hotfix is a sibling
  postmortem for the specific module-scope defect.
- The 019fe8a5 session is the immediate predecessor
  that introduced the bug (audit at
  `docs/audits/2026-08-09-full-audit-019fe8a5.md`,
  PR #59 at `608c04b`).
- `.scoreboard/manual-workflow-edits.md` documents the
  owner-applied GitHub settings that would have
  *prevented* this class of incident from shipping to
  production.
- The 019fe8d0 session (this branch) includes the
  fresh-eyes audit
  (`docs/audits/2026-08-09-arena-expert-full-audit-019fe8d0.md`),
  the P1 contract-test gap fixes (`b5ef68b`'s
  parent `4f92d9f`), and this P0 hotfix (`b5ef68b`).
