# Independent full-stack audit — 2026-08-10 (Arena 019feb8c)

**Scope:** design, frontend, static delivery, Python data engineering, data integrity,
tests, security, CI/CD, documentation, and operational readiness.

**Audited checkout:** `arena/019feb8c-docsheet` at `f7c58bc2d2cbfbc27979b63e2947ca65a120dbd5` (clean before this audit). This checkout includes the merged PR #66 baseline.

## Verdict

**Conditional pass, 8.1/10 effective.** The static catalogue is well-designed and
deterministic; both data lanes are reproducible, generated artifacts are current,
and the curated data contract is unusually well documented. No new release-blocking
application or data-integrity defect was found. The single material release risk is
operational: GitHub Pages remains a legacy `main:/docs` deployment, so an invalid
commit can publish before CI rejects it. Owner visual acceptance of the current live
build is also still outstanding.

The canonical scoreboard remains the source of scores. This audit independently
corroborates its 2026-08-10 assessment; it does not infer or change any owner score.

## System map

```text
Raw lane
hawkins archive clone - Sheet1.csv → process_data.py → docs/data.json

Curated lane
migration_review_ledger.csv + reviewed data/*.csv overlays
  → build_research_master.py → data/research_master_draft.{csv,json}
  → build_catalogue_pages.py → docs/*.json

Presentation
GitHub Pages docs/ → index.html + app.js + js/*.js + style.css + Tabulator 6.5.2
```

The separation is correct: raw data is preserved as a read-only generated payload,
while reviewed curated records originate only from the ledger and approved overlays.
The UI deliberately no longer exposes the raw spreadsheet view, reducing the risk
that decorative blank raw rows are mistaken for catalogue records.

## Evidence and verification

| Check | Result |
|---|---|
| Git worktree before audit | Clean |
| Raw-payload generator check | PASS — 374 raw rows, 7 retained display columns |
| Curated-master generator check | PASS — 363 masters, 75 exclusions, 134 source overrides, 40 validated manual candidates |
| Catalogue Pages generator check | PASS — 363 Everything rows |
| Reconciliation, taxonomy, inventory-mirror checks | PASS — 6/6 generator checks total |
| Python unit/contract tests | PASS — 149/149 |
| Python coverage | PASS — 90% (2,327 statements; 85% gate) |
| Python dependency resolution | PASS in isolated `.venv`; `pip check` clean |
| JavaScript parsing | PASS — `app.js`, all seven ES modules, Playwright specs, and config |
| Node frontend module tests | PASS — 3/3 |
| Manifest integrity | PASS — every asset, module, and tracked payload SHA-256 matches `docs/build-manifest.json` |
| JSON URL hygiene | PASS — zero non-HTTPS/non-host URL values in Pages JSON URL fields |
| npm dependency audit | PASS — 0 vulnerabilities |
| Browser Playwright suite | NOT RUN locally — sandbox cannot fetch required Debian/Chromium packages (network connection failures) |

The initial system-Python test attempt lacked `pandas`; that is an environment issue,
not a repository failure. Repeating the complete Python checks in a clean virtual
environment with the declared constrained dependencies passed.

## Data-engineering audit

### Integrity and modelling

- **363 curated master records** form **191 works**. Stable integer `uuid` values,
  278 catalogue codes, and all 363 proposed filenames are unique.
- Current taxonomy: **306 lecture**, **41 book**, **8 discussion**, **7 highlight**,
  and **1 other**. Carrier formats are separately modeled: 253 DVD, 32 CD, 32 book,
  27 audiobook, and 19 streaming.
- Ownership uses the documented tri-state model: **289 true / 25 false / 49 blank**.
  Blank means not stated, not “not owned.” Following the owner’s 2026-08-10
  correction, all 27 audiobook rows are blank; the correction record is
  `review/OWNED_AUDIOBOOKS_2026-08-10.md`.
- The approved display-order file is dense and complete, so every master appears
  exactly once in the curated Everything view.
- Master data has 30 verified Veritas links; all non-empty Pages JSON URL fields
  are HTTPS. Relationship data contains 340 product relationships and seven
  series-compilation assertions.
- Generator checks detect drift rather than silently overwriting committed
  artifacts. The test suite additionally exercises write/check/tamper paths and
  rule failure paths in disposable copies.

### Strengths

1. Review overlays prevent direct edits to generated master and Pages files.
2. Provenance, edition, source-override, taxonomy, relationship, and display-order
   contracts are explicit and covered by deterministic tests.
3. Validation is pragmatic: catalogue-code/filename uniqueness, controlled
   vocabulary, URL validation, dense ordering, and mapping cardinalities are all
   enforced near the pipeline.
4. The data has clear semantic distinctions that are preserved through to the UI:
   `item_type` vs. `format`, work vs. edition, owned vs. unknown, and master vs.
   candidate records.

### Remaining data work

No automatic data repair is recommended from this audit. The only known material
content uncertainty is GitHub issue #18’s ownership cross-check, which requires the
owner’s Drive access. The empty discovery/new-work queues are healthy standing intake
lanes, not missing data.

## Web-design and UX audit

### What works well

- The interface is a focused catalogue tool rather than a generic dashboard:
  search, grouped Jump-to navigation, export, filters, columns, and view settings
  are present without obscuring the sheet.
- The visitor/expert split is excellent progressive disclosure. Everything opens
  with product facts, source links, and edition information; technical provenance
  remains reachable via Expert columns, the column chooser, and the detail drawer.
- Browse cards make the edition-per-row model understandable on phones. The
  mobile work stack correctly groups related editions and retains a Spreadsheet
  escape hatch for comparison work.
- Faceted filters, removable chips, series browser, timeline rails, keyboard
  shortcuts, persistent display preferences, and full row details make the catalogue
  usable for both casual discovery and archival review.
- The implementation includes conscious accessibility behaviors: labelled controls,
  live status, focus return from row details, a focus-managed shortcut dialog,
  dark-mode preference persistence, responsive alternatives, and reduced-motion
  styling.

### UX caution

The product is feature-rich for a 363-row catalogue. It is therefore important to
retain the current mobile hierarchy (single-row top bar, collapsed discovery rails,
dismissible introduction) and to get owner visual acceptance at desktop light/dark
and phone breakpoints before adding more top-level controls. A usability problem was
not reproduced statically, but browser rendering is the appropriate final authority
for density, overflow, contrast, and touch targets.

## Frontend and security audit

- The browser app uses a small static stack: native ES modules plus pinned Tabulator
  6.5.2. JSON is fetched from same-origin relative paths; no browser-facing code
  calls localhost or submits data externally.
- The code guards stale view responses with activation sequencing/abort handling.
  This is directly regression-tested for rapid view changes.
- Dynamic catalogue values render through DOM nodes/text content rather than
  data-bearing `innerHTML`; fixed loading/help templates are the only template
  strings assigned to `innerHTML`.
- CSP uses `default-src 'self'`, limits `connect-src` to self, blocks objects and
  forms, hash-pins the one inline pre-paint script, and uses SRI for the Tabulator
  CDN CSS/JS. The manifest hashes and content-versioned local assets match exactly.
- No credential material was found in production configuration or payloads. A broad
  keyword scan has expected documentation/comment false positives only.

### Frontend debt (non-blocking)

1. `style-src 'unsafe-inline'` is deliberate but reduces CSP protection for styles.
   It is low-severity debt; retire it only with a tested replacement compatible with
   Tabulator’s runtime styling.
2. `docs/app.js` (1,792 lines) and `docs/style.css` (2,114 lines) remain the main
   maintenance hotspots. The initial module split is useful, but future extraction
   should target state/drawer/settings behavior and CSS tokens/components in small,
   contract-preserving changes.
3. CI parses `docs/app.js` but does **not** explicitly parse `docs/js/*.js`, even
   though this audit did. Add that inexpensive syntax loop and ESLint `no-undef` /
   `no-unused-vars` after owner authorization for workflow changes.

## CI/CD and operational audit

The CI workflow validates compilation, all six generator checks, deterministic
Python tests, coverage, JS syntax, npm install, Chromium setup, and browser tests.
That is strong coverage for a static data site. The primary weak point is deployment
ordering, not code validation:

- Pages is configured as legacy branch deployment from `main:/docs`.
- A branch push can therefore deploy before CI completes or fails.
- Branch protection was previously observed to permit merge-before-check.

### Required owner actions

1. Apply the reviewed branch-rule requirement for the stable **Validate data pipeline
   and site** check.
2. Add the reviewed post-CI Actions Pages deployment and switch Pages source to
   **GitHub Actions**. The exact vetted procedure is maintained in
   [`.scoreboard/manual-workflow-edits.md`](../../.scoreboard/manual-workflow-edits.md).
3. Perform and record visual acceptance for the live build: desktop light, desktop
   dark, and mobile; include source/streaming links, filtering/sorting, and row
   details across lecture, discussion, and office transitions.

## Prioritized recommendations

| Priority | Recommendation | Owner |
|---|---|---|
| P0 | Gate `main` merge and Pages deployment on successful CI | Repository owner |
| P0 | Complete explicit visual acceptance of the deployed revision | Repository owner |
| P1 | Add ES-module syntax checks and ESLint undefined/unused checks to CI | Owner approval required for workflow edit |
| P2 | Add axe-core and a small visual/Web-Vitals budget after acceptance baselines exist | Agent-safe product follow-up |
| P2 | Increase targeted coverage in `pipeline/helpers.py` (78%) and `pipeline/relationships.py` (82%) | Agent-safe engineering follow-up |
| P3 | Resolve issue #18 when Drive access is available | Repository owner |

## Post-audit owner corrections

Two owner-directed corrections were completed after the initial audit evidence:

1. The earlier broad owned-status edit was traced to an incorrect source layer.
   Unrelated ledger values were restored, while all 27 promoted audiobook records
   now correctly have blank/not-stated ownership at their true edition-candidate
   sources. See `review/OWNED_AUDIOBOOKS_2026-08-10.md`.
2. Reported phone Spreadsheet panning was fixed by giving Tabulator’s table holder
   explicit touch-enabled two-axis scrolling and locking the document shell to the
   dynamic viewport. A 390×844 Playwright regression test covers both axes. See
   `review/MOBILE_SPREADSHEET_SCROLL_FIX_2026-08-10.md`.

## Conclusion

DocSheet is a robust reviewed catalogue pipeline with a thoughtful, accessible
research interface and verified generated artifacts; its remaining risk is release
governance, not a discovered code or data defect.
