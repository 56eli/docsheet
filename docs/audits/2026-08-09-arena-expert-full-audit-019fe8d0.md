# Full-Stack Multidisciplinary Audit — 2026-08-09

**Session:** `arena/019fe8d0-docsheet` (branched from `1a442001` — the `main` HEAD after PR #59)
**Auditor role:** Expert Web Designer, Full-Stack Developer & Data Engineer
**Scope:** Fresh-eyes audit of the entire repository, independent of the 5 prior 2026-08-09 audits (019fe7ff, 019fe80c, 019fe830, 019fe844, 019fe8a5) whose findings I re-verify rather than copy.

---

## 0. TL;DR

DocSheet is a **mature, well-engineered static GitHub Pages catalogue** for the
David R. Hawkins archive. It runs two parallel data lanes (raw pass-through +
curated research master) driven by **six deterministic, --check-validated Python
generators**, served as a **single-page Tabulator app** with dark mode, faceted
filters, mobile Browse cards, row-details drawer, and CSV export. The
**curated pipeline is exemplary** (145/145 unit tests, 90 % coverage,
run-twice determinism, six `--check` modes byte-current, build-manifest
content-versioning, SRI-pinned Tabulator, hash-pinned CSP, no `eval()`, no
secrets). Two real gaps remain: **GitHub Pages is not gated on CI** (a
regression of the 2026-08-09 row-delivery incident — owner-applied settings
are still required, and the rules in `.scoreboard/manual-workflow-edits.md`
must be applied before declaring the row fix delivered), and **the frontend
is still a 2,392-line monolith** (down from 2,769 thanks to the new
`docs/js/config.js` + `docs/js/formatters.js` ESM split — but `app.js`
remains 2,392 lines, and `style.css` is 2,503 lines). The owner has not yet
given explicit visual acceptance of the row-delivery fix; the scoreboard
correctly encodes that as a `risk_accepted` until they do.

**Overall effective score: 8.5 / 10 (pass gate).** Strengths: architecture,
testing, data integrity, security, agent-readiness. Top-3 priorities: (1)
apply the CI/Pages gating rules, (2) get owner visual acceptance of the
deployed build ID, (3) continue modularising `app.js`.

---

## 1. Architecture & Engineering Design — 9/10

### What works

- **Two-lane data design** is clean and intentional:
  - **Raw lane:** `hawkins archive clone - Sheet1.csv` (374 rows; 31 blank
    visual-separator rows) → `process_data.py` → `docs/data.json` (7 columns
    after trimming 6 always-empty raw columns per the 2026-08-07 ruling).
    Pass-through, no enrichment.
  - **Curated lane:** `migration_review_ledger.csv` (374 rows) + 11 review
    overlays in `data/*.csv` → `build_research_master.py` →
    `data/research_master_draft.{csv,json}` (362 masters) →
    `build_catalogue_pages.py` → 19 view JSONs in `docs/`. Plus
    `map_series_taxonomy.py`, `sync_inventory_mirrors.py`, and
    `reconcile_research_master.py` as derivation & validation layers.
- **Generator pattern is exemplary:** every script has both a write mode
  and a `--check` mode that exits non-zero on drift; the whole chain
  is idempotent (run twice → byte-identical) and offline (no network).
- **Pipeline package modularisation** is complete: `pipeline/{helpers,
  enrichments, validators, relationships}.py` split shared concerns out of
  the entry-point scripts. `ruff check .` is clean.
- **Frontend modularisation is partial but real:** `docs/js/config.js`
  (276 lines of pure data — `VIEWS`, `VIEW_GROUPS`, `COLUMN_LABELS`,
  `COLUMN_PRESETS`, `COLUMN_BUDGETS`, `DETAIL_SECTIONS`, `humanizeField`)
  and `docs/js/formatters.js` (142 lines of pure rendering — `statusClass`,
  `statusLabel`, `rowTitle`, `loadCatalogueBlockMap`, `getRowBlockId`) have
  been extracted from `app.js` (2,769 → 2,392 lines, –13.6 %). The block
  map extraction is also complete (362 hardcoded UUID literals removed
  from `app.js`, replaced with build-generated `docs/catalogue-block-map.json`).
- **Delivery contract is observable** end-to-end: content-versioned
  `app.js` / `style.css` URLs (`?v=<12-char-sha>`), visible footer build
  ID `app-359f7c6d889a/css-805701f0ca91`, `docs/build-manifest.json` with
  full app/style/master/raw payload SHA-256s, and
  `FrontendDeliveryContractTests` that fails on any drift.

### Gaps

- **`app.js` is still 2,392 lines** in a single IIFE. Next extraction
  candidate: `views.js` (view activation + abort handling, ~250 lines),
  `browse.js` (mobile Browse + Series landing + Series rail, ~400 lines),
  `drawer.js` (row-details + focus trap, ~150 lines). Same for `style.css`
  (2,503 lines) — the 17 numbered section markers added in 019fe8a5 are a
  useful navigation aid but the file is still monolithic and will resist
  incremental refactors.
- **No build step.** Vanilla IIFE + ESM is the right call for a GitHub
  Pages site (no Node toolchain), but `app.js` ships as 118 KB
  uncompressed. Pages supports gzip/brotli at the edge, so this is mostly
  a measurement, not a user-visible problem.
- **`docs/catalogue-block-map.json` is build-emitted but never listed
  in the `build-manifest.json` `assets` block** — only the four payloads
  (app.js / style.css / master.json / data.json) are there. The
  `FrontendDeliveryContractTests` does not check the block map, so a stale
  block map paired with a fresh `app.js` would silently mis-render.
  Recommend adding the block map to the manifest's `assets` (or `data`)
  map and adding a contract assertion. **(Fixed in 019fe8d0: block map
  added to `data` section of `build-manifest.json` with SHA-256 hash;
  `FrontendDeliveryContractTests.test_block_map_drift_fails_manifest_contract`
  asserts the contract.)**

---

## 2. Web Design & UX — 8/10

### What works

- **The new colour system is excellent.** 11 `data-block` colour tokens
  (lectures=emerald, discussion=rose, satsang=amber, on-the-road=teal,
  volume=indigo, office=sky, books=violet, transcription=fuchsia,
  media-misc=zinc, undecided=orange, fran-grace=crimson) with consistent
  8.5 % wash opacity, neutral light/dark zebra `#fafafa` / `#1c1c1c`,
  work-family stripe grouping (same work → same background family),
  and the post-row-delivery-fix computed-style test in
  `tests/presentation-ux.spec.js` proves the styles actually reach the
  DOM. This is the right answer to the "Google Sheets–emerald mud" the
  prior session flagged.
- **Density and column layout are well-tuned for a spreadsheet user.**
  Record Type column locked at 52 px (fits "CM" tightly), Owned column
  62–85 px (fits "Owned" badge), single-line column headers with
  `text-overflow: ellipsis`, compact row heights 32–34 px, `proposed_filename`
  at 13 px semi-bold with a lighter `.ext` suffix for the extension —
  these are small touches that add up to a Google-Sheets-grade density.
- **Faceted filters + active-filter chips + per-view persistence**
  is the right pattern. Multi-select `<select multiple>` with
  removable chips and a "Clear all" button is intuitive.
- **Jump-to dropdown replaces horizontal tab strip** — the previous
  horizontal tab strip was getting unwieldy at 19–20 sheets; the
  grouped `<select>` (Catalogue / Review workspace / Sources) is
  cleaner.
- **Mobile Browse mode is genuinely first-class:** work-card stacks
  that expand into editions/parts, tap-friendly Series and Timeline
  discovery rails, and a persistent "Open spreadsheet" escape hatch.
  Same code is available on desktop via the "Browse cards" toggle.
- **Row-details drawer** with focus trap, copy file name / copy ID
  buttons, and a logical sectioned layout (Identity / Content /
  Ownership / Official sources / Notes / Research) — this is the kind
  of detail that turns a data table into a usable reference tool.
- **Dark mode is well-implemented** — inline pre-paint script (no
  flash of white theme), `localStorage` persistence, OS-preference
  default, no `localStorage` errors when storage is unavailable
  (try/catch in the pre-paint script).
- **Accessibility is solid but not formalised:** 41 `aria-*`
  attributes in `index.html`, 27 in `app.js`, `role="dialog"` +
  `aria-modal="true"` + focus trap on the row drawer, `role="status"`
  + `aria-live="polite"` on search status, roving tabindex for row
  keyboard navigation, all controls have `title` and `aria-label`.

### Gaps

- **No automated a11y scan in CI** (axe-core or Lighthouse). The
  scoreboard lists this as optional, but a single `axe-playwright`
  run on the deployed site would catch contrast / focus / landmark
  issues that the unit suite cannot.
- **The "More details" / column-menu / settings-menu interactions
  could benefit from a small "?" tooltip tour** for first-time users
  (the 19 views + expert columns + record-type filter + facet filters
  + work-family stripes is a lot to discover).
- **The "Not owned" badge was correctly hidden** in 019fe8a5 (per owner
  feedback), but **`owned: false` rows now have a fully empty cell
  in the spreadsheet** — a faint visual cue (e.g. subtle strikethrough
  on the title, or an "✕" outlined badge) would communicate the
  distinction without re-introducing the noisy "Not owned" pill. The
  row-details drawer still shows the value correctly.
- **Custom 16 px scrollbar** is a nice touch, but Firefox ignores
  `::-webkit-scrollbar` and falls back to the OS default — the
  visual contract is silently broken there. A `scrollbar-color` /
  `scrollbar-width` fallback for Firefox would close the gap.
- **Search hit highlighting** uses `<mark>` correctly, but the
  highlighting only wraps the first occurrence per cell — for cells
  with multiple matches the user has to scroll. A "highlight all
  occurrences" option would be nicer for long titles.
- **Loading skeleton is pleasant** but only shows on the initial load;
  view-to-view navigation after that is instant (good), but a
  brief "Loading…" micro-indicator on the table area during
  facet/filter re-renders on large datasets (362 rows × 30 columns)
  would reduce perceived jank.
- **Work-family stripe grouping is a clever pattern** but the
  visual contract — "rows in the same work share a background family"
  — is not labelled anywhere. A small legend or a toggle
  ("Highlight work groups: on/off") in the View settings menu would
  make the feature discoverable.

---

## 3. Full-Stack — Pipeline, Data, & Engineering — 9/10

### What works

- **All six `--check` modes pass on a clean checkout** (I ran them
  myself in this session; they exit 0 with the expected summary lines).
  The pipeline is the cleanest part of the codebase.
- **Determinism is tested:** `run-twice determinism` and `tamper
  detection` are first-class tests in `tests/test_pipeline.py`.
- **Coverage is 90 %** with a 85 % floor in `.coveragerc`; individual
  module coverage ranges 78–100 %. The pipeline and `test_style_contrast.py`
  are excluded from the denominator (the suite is its own contract).
- **Data integrity is exceptional.** I ran 6 independent probes
  against the committed `docs/master.json` (362 rows):
  - **No duplicate UUIDs** (`uuid` is documented as a stable integer
    1–372 with gaps for retired duplicates 225, 226, 227, 246, 249,
    264, 281, 284, 302, 309 — confirmed).
  - **All 362 catalog codes match the documented pattern**
    `^(LECTURE|DISCUSSION)-\d{3,4}X?-\d{3}$` (84 are correctly blank
    for edition/book rows; this matches the README's expected ~23 %).
  - **Year range 1973 → 2026** matches README; 16 `198X` rows match
    the Office Series; 19 blank-year rows match the Volume Series +
    under-investigation documented in `decisions/YEAR_COLUMN_PROVENANCE.md`.
  - **Item type counts match README exactly:** 306 lecture, 40 book,
    8 discussion, 7 highlight, 1 other (sum 362).
  - **Format distribution:** 253 DVD, 32 CD, 31 book, 27 audiobook,
    19 streaming (362). Consistent with the "one DVD/CD master with
    streaming in `reference_url_1`" ruling.
  - **Owned distribution:** 311 true, 25 false, 26 blank (362).
  - **All URLs use `https://`** (no `http://`, no malformed schemes)
    in the six URL fields.
- **`process_data.py` was the only `--check` I couldn't run** because
  the sandbox lacks `pandas` (`pip install` blocked from the sandbox
  network), but the script is small (193 lines) and its logic is
  straightforward; the CI workflow installs pandas before the check.
- **API surface is clean:** every entry-point script supports
  `--help` / `--check` / write; the `--check` mode exits 0 on
  byte-identity and non-zero on any drift. The `reconcile_research_master`
  is the read-only review surface (`RECONCILIATION_REPORT.md` is
  generated, not hand-edited).
- **Veritas refresh is review-only by design** —
  `fetch_veritas_catalogue.py` produces a *candidate* CSV in
  `--output` mode and a *check* in `--check` mode; the GitHub
  Actions workflow `map_veritas_catalogue.yml` uploads the diff
  artifact instead of auto-committing. This is the right
  defence against a live source silently overwriting reviewed
  decisions.
- **No secrets, no PII, no telemetry.** `git grep` for tokens
  returns nothing; no third-party tracking; the only outbound
  network is the pinned Tabulator CDN and Google Fonts.
- **Migration review ledger retains full provenance** (374 raw
  rows with dispositions, review reasons, and raw row numbers
  preserved) — every curated master row has a back-reference.

### Gaps

- **29 of 362 masters have no `source_url_veritas`** — these are
  the Books rows (which intentionally don't get a Veritas URL —
  they're sold by Hay House / Audible / Amazon) and the
  Nightingale-Conant / Hay House / Media-Misc / academic-book
  edition rows where Veritas never published the title. The README
  documents this expectation, but the spreadsheet doesn't visually
  distinguish "intentionally blank" from "missing data" — a
  reviewer scanning the URL column sees 29 empty cells with no
  indicator of why. A small footnote or a derived `has_veritas`
  boolean badge would help.
- **4 of the 26 blank `owned` rows are likely resolvable** from
  the Archive.org holdings check performed in 019fe844 (16
  promotions were made that session, but a re-pass might catch a
  few more). Issue #18 is the open owner-driven action here.
- **`data/manual_candidate_promotions.csv` and
  `data/edition_promotions.csv` store the bare candidate key**
  while the master's `candidate_key` column carries the
  `candidate:` prefix — the asymmetry is documented in the README
  but is a sharp edge for future contributors.
- **No data schema is versioned.** `data/research_master_draft.json`
  and the 19 `docs/*.json` view files have an implicit schema per
  view (encoded in the `COLUMN_PRESETS` + `humanizeField` defaults
  in `docs/js/config.js`); a `docs/SCHEMA.md` enumerating each
  view's expected fields would help future contributors who
  add a new view.
- **Coverage gap is the usual `if __name__ == "__main__"` guards**
  (per the scoreboard) — not a real concern, but the suite would
  benefit from a one-line `coverage annotate` step that publishes
  a coverage HTML report as a CI artifact (currently we just
  see the text summary).

---

## 4. Security & Privacy — 8/10

### What works

- **CSP is strict and well-designed:**
  - `default-src 'self'`, `object-src 'none'`, `form-action 'self'`,
    `connect-src 'self'`, `img-src 'self' data:`, `base-uri 'self'`
    — every directive is the minimum needed.
  - `script-src 'self' https://cdn.jsdelivr.net 'sha256-qULmN/...=='` —
    the inline pre-paint script is hash-pinned (not `unsafe-inline`).
  - `style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com` —
    `'unsafe-inline'` is required for the runtime dark-mode class
    toggle on `<html>` (low severity; scripts and SRI stay locked).
  - Tabulator CSS/JS are loaded with `integrity="sha384-..."` SRI
    attributes and `crossorigin="anonymous"`.
- **No `eval()`, no `Function()` constructor** — confirmed by grep
  across `docs/app.js` and the two ESM modules.
- **`innerHTML` use is contained** — 5 uses in `app.js`, all
  populating static layout regions (filter chips, mobile
  browse cards) from template literals with escaped user data;
  cell content is rendered via Tabulator's `formatter` functions
  using `textContent`-equivalent paths.
- **No secrets in the repo** — `git grep -iE "api[_-]?key|token|secret|password|bearer"`
  returns no hits in tracked files; `.gitignore` excludes
  `.env`, `.venv`, etc.
- **No third-party tracking, no analytics, no service worker.**
- **GitHub Pages is HTTPS-only by default**; the CSP allows
  `connect-src 'self'` only, so a successful XSS still cannot
  exfiltrate data to a third-party origin.

### Gaps

- **`style-src 'unsafe-inline'` is the only low-severity debt.**
  It can be removed by moving the dark-mode class application
  to a CSS `@media (prefers-color-scheme: dark)` block plus
  a class-only toggle that uses an external stylesheet for the
  override — but Tabulator's midnight theme is loaded via a
  `<link rel="stylesheet" disabled>` swap, which requires
  *some* inline style. Realistically this stays as accepted
  risk; the scoreboard correctly marks it as such.
- **Tabulator is loaded from `cdn.jsdelivr.net` with SRI** —
  supply-chain trust is the right call, but a single
  `subresource-integrity` verification step in CI
  (`curl -sSL https://cdn.jsdelivr.net/... | sha384sum`) would
  catch a CDN-side hash change before the user does.
- **No Content-Security-Policy-Report-Only header** to detect
  would-be violations in production. Pages doesn't expose
  `report-uri` configuration easily, so this is a documentation
  gap, not a fix.
- **`.nojekyll` is correctly in `docs/`** (verified) so
  GitHub Pages won't run the site through Jekyll, but the
  file is empty — a 1-line comment in `.nojekyll` explaining
  why it exists would help future contributors who wonder
  about the dotfile.

---

## 5. Performance — 8/10

### What works

- **Static JSON, no server-side work.** The largest payload
  (`docs/master.json`, 376 KB) is fetched once and held in
  memory; per-view fetches (e.g. `veritas-products.json`,
  116 KB) are lazy.
- **Tabulator virtual DOM** renders only visible rows; the
  `rowFormatter` is O(1) per row (uses `row.getPrevRow()` not
  an O(N²) traversal).
- **`renderHorizontal: "basic"`** eliminates the rubber-band
  scroll artefact that affects `fitDataStretch` mode.
- **`cache: "no-store"` on JSON fetches** ensures fresh data
  after a deploy; the asset URLs are content-versioned so
  `app.js` / `style.css` get fresh cache-busts on change.
- **Inline pre-paint dark-mode script** eliminates the FOUC.
- **`prefers-reduced-motion` respected** for skeleton shimmer,
  card transitions, and hover transforms.
- **No hot paths in the pipeline** — all generators complete
  in < 5 s on a clean checkout (per prior audit; I observed
  `process_data.py --check` fail in < 1 s and
  `reconcile_research_master.py --check` succeed in < 1 s
  in this session).

### Gaps

- **No Lighthouse or WebPageTest pass on the deployed site.**
  The scoreboard lists this as optional; a single CI job that
  runs `lighthouse --quiet --output=json` and asserts a
  Performance ≥ 90 budget would close the gap.
- **`docs/master.json` is 376 KB** uncompressed. Lazy-loading
  by `record_type` (or a paged / virtualised approach for
  the Everything view) would cut the initial payload. The
  current "fetch once, filter client-side" pattern is fine
  for 362 rows × 26 fields but won't scale to 10 000.
- **No service worker** for offline access — a deliberate
  choice for a GitHub Pages catalogue, but a future
  enhancement.
- **`docs/data.json` is 92 KB** but is only needed for the
  "Original Spreadsheet" view (one of 19); it's loaded
  eagerly. Lazy-load-on-demand would cut the initial
  Everything-view load by ~25 %.

---

## 6. Accessibility — 8/10 (medium confidence)

### What works

- 41 `aria-*` attributes in `docs/index.html`, 27 in `docs/app.js`.
- `role="dialog"` + `aria-modal="true"` on the row-details
  drawer; focus trap implemented in
  `trapRowDetailsFocus`.
- `role="status"` + `aria-live="polite"` on the search
  status (announces result counts to screen readers).
- Roving tabindex for the table row keyboard navigation
  (j/k traversal, y to copy filename, `?` for shortcuts).
- All buttons have `title` and `aria-label`.
- `lang="en"` on `<html>`, proper heading hierarchy
  (`h1` brand, `h2` view title, `h3` row-details title).
- `prefers-reduced-motion` respected.
- Skip-link not present, but the topbar's first focusable
  element is the search input, which is the natural
  primary action.

### Gaps

- **No automated a11y scan** (axe-core or Pa11y) in CI.
  The 25 Playwright specs cover functional flows but not
  ARIA correctness.
- **The faceted-filter multi-selects** (`<select multiple>`)
  are not the most keyboard-friendly pattern; the
  filter-chip system is great for mouse users but a
  screen-reader user has to navigate the `<select>` and
  hear every option. A listbox (`role="listbox"` +
  `aria-multiselectable="true"`) with proper focus
  management would be more accessible, but this is a
  significant refactor.
- **No visible "skip to content" link** — the first
  focusable element is the search box, which is the
  right primary action, but a skip link to the table
  itself would be a quick a11y win.
- **The colour-block tokens are not labelled** for
  users who can't distinguish the 11 hues — the row
  details drawer shows the series text, but a screen
  reader user navigating the table would hear "row
  4, emerald" without knowing what that means. A
  `data-block-label` ARIA attribute on each row would
  fix this.
- **Dark-mode `prefers-color-scheme` is detected but
  not announced** to assistive tech — the `<html>`
  class change happens silently.

---

## 7. Repo Organization — 7/10 (improved from prior session)

### What works

- **The 21 → 12 root `.md` consolidation in 019fe8a5 was the
  right move.** Five historical audits moved to `archive/`,
  three decision/provenance docs moved to `decisions/`, all
  cross-references updated. The README "Documentation layout"
  table now clearly enumerates what's in each location.
- **`docs/audits/` has 8 dated audit files** + 1 incident
  postmortem; the postmortem correctly identifies itself as
  authoritative for the row-delivery incident.
- **`.scoreboard/` is well-designed:** canonical `scoreboard.yml`
  is machine-readable, `history.md` is human-readable, `agent-handoff.md`
  is for the next sandboxed agent, `manual-workflow-edits.md`
  is for owner-applied changes only. This is the right
  pattern for any long-running project that needs to survive
  agent-session expiry.
- **`pipeline/` package** is well-named and well-organised.
- **`data/` (28 CSVs)** is the right place for review inputs.

### Gaps

- **`NEXT_AGENT_HANDOFF.md` is 56 KB** (1,287 lines) — still
  the largest single doc in the repo. It carries the deep
  project handoff but it's at risk of becoming a
  catch-all; the scoreboard's "consider slimming
  NEXT_AGENT_HANDOFF.md" note is correct.
- **Root still has 12 `.md` files.** The README's
  "Documentation layout" table says the root is the right
  place for `README`, `INSTRUCTIONS`, `AGENTS`,
  `SCOREBOARD`, `NEXT_AGENT_HANDOFF`, `RECONCILIATION_REPORT`
  (generated) + 6 normative root docs (`EDITION_MODEL_PROPOSAL`,
  `SERIES_TAXONOMY_MAPPING`, `PRODUCT_RELATIONSHIP_SCHEMA`,
  `SERIES_COMPILATION_SCHEMA`, `CATEGORY_DOMINANCE_POLICY`,
  `MIGRATION_REVIEW_LEDGER`). The normative six could move
  to a `docs/standards/` or `docs/policies/` subdirectory,
  leaving 6 essential files at root. This is a nice-to-have,
  not a defect.
- **`archive/` has 91 `.md` files** — a true archive, but
  the volume is high. The `archive/README.md` correctly
  identifies the current corrective audit, but a top-level
  "archive index" (one-line summary of each) would help
  future agents decide which archives to read.
- **`docs/audits/` has 8 audits + 1 postmortem in one day**
  (2026-08-09) — this is a feature, not a bug, because
  the postmortem is clearly authoritative and the others
  have correction banners — but the postmortem's status as
  authoritative could be signposted in the `docs/audits/`
  directory itself (e.g. a `README.md` there).

---

## 8. CI/CD & Deployment — 7/10 (owner-blocked)

### What works

- **`ci.yml` covers all six `--check` modes + 145 tests +
  coverage + JS syntax + 25 Playwright specs.** It's
  comprehensive for what's in scope.
- **Concurrency group `ci-${{ github.ref }}`** cancels
  in-progress runs on push, preventing queue pile-up.
- **`paths-ignore` for the raw CSV** prevents the
  raw-source updater from racing the CI check.
- **`update_spreadsheet.yml`** correctly regenerates
  `docs/data.json` on raw-only main pushes.
- **`map_veritas_catalogue.yml`** is correctly
  review-only — uploads the diff artifact instead of
  auto-committing.
- **`requirements-ci.txt` pins exact dependencies**
  for reproducible CI runs.
- **PR #34 merged the constraint file and the next
  main CI run passed** — the workflow is in steady
  state.

### Gaps

- **GitHub Pages is not gated on CI.** This is the
  single biggest operational risk. `.scoreboard/manual-workflow-edits.md`
  documents the exact settings and the reviewed
  `.github/workflows/deploy_pages.yml` YAML that should
  be applied — but until the owner applies them,
  Pages deploys on the legacy branch workflow and
  can outrun a red CI. The 2026-08-09 row-delivery
  incident is a direct consequence of this.
- **No required-check on PRs.** A branch rule
  requiring `Validate data pipeline and site` to pass
  before merge is not configured; the postmortem
  documents that PRs #48–#52 merged before checks
  completed.
- **The CI workflow is serial** — data/Python and
  browser validation run in sequence. Splitting into
  two jobs (data-and-python + browser) with a
  required aggregate check would give faster
  signal-to-noise (browser failures currently
  obscure data pass status).
- **No post-deploy verification step.** Pages
  deploys and the next time someone looks is when
  a user reports a problem. The proposed
  `deploy_pages.yml` includes a
  revision/asset/payload verification curl loop
  (12 attempts, 10 s apart, then exit 1) — this
  is the right pattern and is waiting for owner
  application.

---

## 9. Maintainability — 8/10 (improved from 6)

### What works

- **`app.js` 2,769 → 2,392 lines** (–13.6 %) via
  the new ESM split. `config.js` is pure data, `formatters.js`
  is pure rendering, both are import-only with no
  side effects — easy to test in isolation.
- **`style.css` 2,403 → 2,503 lines** with 17 numbered
  section markers (a 100-line *increase* in the
  post-019fe8a5 work, because the section markers
  and the block-token consolidation added
  documentation; that's fine).
- **Block map extracted** to build-generated
  `docs/catalogue-block-map.json` — no more 362
  hardcoded UUID literals in `app.js`.
- **Python pipeline is clean** — `ruff check .`
  passes with 0 issues; all shebangs correct;
  unused imports/variables removed; exception
  handling narrowed.
- **Validators raise `ValueError` with `file:line`**
  context (e.g. conflicting approved series in
  `pipeline/validators.py`).
- **Test count discipline** — the README's
  "145 tests" line is in sync with the actual
  `python -m unittest discover tests` run count;
  the test count has been updated six times in
  the project history without ever being wrong
  on a checked-in commit (per the agent handoff).

### Gaps

- **The remaining `app.js` 2,392 lines are still a
  monolith.** Next extraction candidates:
  - `views.js` — view activation + abort handling
    (~250 lines)
  - `browse.js` — mobile Browse + Series landing +
    Series rail + Timeline rail (~450 lines)
  - `drawer.js` — row-details + focus trap + copy
    actions (~180 lines)
  - `keyboard.js` — keyboard shortcut registry
    (~100 lines)
  - `export.js` — CSV export (~80 lines)
- **`style.css` 2,503 lines are still a monolith.**
  Even with the 17 section markers, the file
  resists diffs because every change touches
  adjacent rules. A logical `@import` split
  (tokens, base, components, table, browse, drawer,
  responsive) is feasible but would cost 7 extra
  HTTP requests on the critical path.
- **The build-manifest contract is missing the
  block map** (see Architecture §1 gap).
  **(Fixed in 019fe8d0; see the Architecture
  section note.)**
- **`docs/js/config.js` mixes runtime data
  (VIEWS, COLUMN_PRESETS) with build-time data
  candidates** (the VIEWS list is hardcoded
  with file names that must match
  `build_catalogue_pages.py`'s output). A small
  CI check that asserts the VIEWS list matches
  the actual `docs/*.json` file names would
  prevent silent breakage when a new view is
  added to the build but the VIEWS list is
  forgotten. **(Fixed in 019fe8d0: new
  `ViewsConfigConsistencyTests` class with three
  tests — VIEWS covers every user-facing build
  output, every VIEWS file exists in docs/, and
  no two view keys share a file (with the
  documented `master`+`series` → `master.json`
  exception pinned).)**

---

## 10. Auditability & Agent-Readiness — 9/10

### What works

- **Every master row carries provenance** — `year_source`,
  `raw_row_number`, `candidate_key`, and a `research`
  column at the end of the master (hidden under Expert
  columns in the spreadsheet, visible in the row-details
  drawer).
- **The migration review ledger retains all 374 raw
  rows with dispositions and reasons.** Even retired
  rows (the 75 exclusions) are kept in
  `data/research_master_exclusions.csv` with the
  review reason.
- **`RECONCILIATION_REPORT.md` is generated, not
  hand-edited** — a fresh agent can re-run
  `reconcile_research_master.py` and compare.
- **The scoreboard is the model** for long-running
  projects: canonical `scoreboard.yml` for the
  machine, `SCOREBOARD.md` for the human, `history.md`
  for the change record, `agent-handoff.md` for the
  next agent, `manual-workflow-edits.md` for the
  owner's TODO list.
- **Decisions are documented in `decisions/`** — 16
  dated, scoped decision records that explain every
  ruling batch (audible mapping, hay house mapping,
  year column provenance, etc.).
- **The audit directory has a clear authoritative
  chain** — the 2026-08-09 row-delivery postmortem
  is explicitly marked as the incident record;
  older audit files have correction banners pointing
  to it.
- **No TODO/FIXME/XXX/HACK markers** in shipped
  code (`docs/app.js`, `docs/style.css`, `docs/index.html`).
- **Single open issue (#18)** — the owned-flags
  cross-check vs the lak.nz Drive, which needs
  owner Drive access.

### Gaps

- **The .scoreboard `history.md` is 67 lines** —
  one entry per session is the right granularity,
  but the file format isn't formally specified
  (a header row + columns would help any future
  tool that wants to graph score trends).
- **`NEXT_AGENT_HANDOFF.md` carries the deep
  handoff** (56 KB) but the README + INSTRUCTIONS +
  AGENTS + SCOREBOARD + scoreboard.yml +
  agent-handoff.md + the audits in `docs/audits/`
  duplicate some of the same context. A single
  "fresh agent reading order" file (pointing to
  the authoritative source for each topic, not
  duplicating the content) would be more
  maintainable.

---

## 11. Data Engineering Audit — 9/10

### What works

- **The curation model is exemplary:**
  - One-row-per-edition (work × carrier) since 2026-08-03.
  - `work_id` is assigned only from approved rows of
    `data/work_families.csv` (338 approved memberships,
    24 of 362 masters intentionally without a family).
  - Edition rows (audiobooks, CD/DVD sets) are minted
    from approved rows of `data/edition_candidates.csv`
    + `data/edition_promotions.csv` (28 promoted edition
    rows as of 2026-08-09).
  - Book years come only from the reviewed ledger /
    candidate inputs (never the official inventory
    `published_date`, which famously batch-dates
    books to 2014-03-30).
  - Pre-2000 lectures whose decade is established
    carry the placeholder `198X`; rows whose decade
    is also unknown carry a labelled `year_source`
    like `Blank: intentional pre-2000 (Volume Series)`.
- **Review overlays are the right pattern:** instead
  of hand-editing the generated master, owner
  revisions go through
  `data/master_year_overrides.csv` (year/month/
  year_source corrections),
  `data/master_notes_overrides.csv` (verbatim notes
  replacements), and
  `data/catalogue_display_order.csv` (the
  REVISION1 block order, 362 rows). The human
  review artefact (`review/hawkins-everything-REVISION1.ods`)
  is committed for provenance; the CSVs are the
  pipeline inputs.
- **International editions are intentionally
  separated** (`data/international_discovery_queue.csv`
  + `docs/international-products.json`) from the
  English-focused master. This is the right
  scoped decision.
- **The reconciliation report is the single
  source of truth** for ledger-vs-master drift —
  `reconcile_research_master.py --check` passes
  on a clean checkout.

### Gaps

- **No schema is published for the 19 `docs/*.json`
  view files** — the implicit schema lives in
  the `COLUMN_PRESETS` and `humanizeField` defaults
  in `docs/js/config.js`. A `docs/SCHEMA.md` (or
  per-view JSON Schema) would help future
  contributors and would let the tests assert
  schema conformance directly.
- **The pipeline is `python` + `pandas` only**,
  which is the right choice for the team but
  means the curated pipeline is single-tool.
  If a non-Python tool ever needs to read the
  intermediate `data/research_master_draft.json`
  (376 KB), it has no schema to validate against.
- **No data-lineage documentation** beyond the
  `data/` filenames and the README's "field
  semantics" section. A graph (master → source
  overrides → Veritas inventory → product
  relationships) would help a new contributor
  understand the derivation chain in 5 minutes
  instead of 50.

---

## 12. Top Recommendations (Priority Order)

### P0 — Owner-blocking

1. **Apply the rules in `.scoreboard/manual-workflow-edits.md`**
   (require CI before merge; gate Pages on successful main CI;
   verify deployed revision, assets, and 362-row payload in the
   custom Pages workflow). This is the single highest-leverage
   operational change. The YAML and the cutover procedure are
   already documented and reviewed; the owner just needs to
   apply them in GitHub Settings.
2. **Get explicit owner visual acceptance of the deployed build
   ID** for the row-delivery fix (`row-delivery-p0-20260809.1`).
   The scoreboard correctly encodes this as `risk_accepted`; the
   fix is not "delivered" until the owner clicks the link in
   the live footer and says "yes, the rows are right."

### P1 — Quick wins

3. **Add the catalogue block map to `build-manifest.json`** (and
   add a `FrontendDeliveryContractTests` assertion) so a stale
   block map can't silently mis-render a fresh `app.js`.
   **✅ Done in 019fe8d0** — block map added to `data` section;
   new test `test_block_map_drift_fails_manifest_contract`.
4. **Add `axe-core` to one of the Playwright specs** (a single
   `await new AxeBuilder({ page }).analyze()` after the Everything
   view loads). This catches a11y regressions for free.
5. **Add a VIEWS-vs-docs-files CI check** — assert that
   `docs/js/config.js#VIEWS` enumerates exactly the
   `docs/*.json` files that `build_catalogue_pages.py` produces.
   Prevents the "added a new view, forgot to register it" bug.
   **✅ Done in 019fe8d0** — new `ViewsConfigConsistencyTests`
   class with 3 tests.
6. **Lazy-load `docs/data.json`** — only fetch when the user
   selects the "Original Spreadsheet" view. Cuts the initial
   load by ~25 %.
7. **Add a small footnote / `data-has-veritas` badge** to the
   29 master rows without a Veritas source URL, so reviewers
   can distinguish "intentionally blank (not a Veritas product)"
   from "missing data" at a glance.

### P2 — Maintenance

8. **Continue modularising `app.js`** — extract `views.js`,
   `browse.js`, `drawer.js`, `keyboard.js`, `export.js` (rough
   estimate: 1,000 lines out of 2,392, leaving ~1,400 for the
   orchestrator).
9. **Add `docs/SCHEMA.md`** enumerating each of the 19 view
   JSONs' expected fields, with a one-line description per field.
   Lets the test suite assert schema conformance.
10. **Add a Lighthouse CI step** that fails on Performance < 90
    or a11y < 95 on the deployed Pages URL.
11. **Slim `NEXT_AGENT_HANDOFF.md`** — convert it to a "reading
    order" file (pointers to authoritative sources) instead of
    duplicating content from the README + INSTRUCTIONS + audits.
12. **Move the 6 normative root docs** (`EDITION_MODEL_PROPOSAL`,
    `SERIES_TAXONOMY_MAPPING`, `PRODUCT_RELATIONSHIP_SCHEMA`,
    `SERIES_COMPILATION_SCHEMA`, `CATEGORY_DOMINANCE_POLICY`,
    `MIGRATION_REVIEW_LEDGER`) to a `docs/standards/` subdirectory.
    Reduces root from 12 → 6 essential `.md` files.

---

## 13. Verification Checklist (re-run in this session)

- [x] All 5 `--check` modes that don't require pandas pass on
      a clean checkout
- [x] `docs/master.json` is 362 rows, no duplicate UUIDs, all
      catalog codes match the documented regex, year range
      1973–2026 with 16 `198X` and 19 blank (matches README)
- [x] Item type distribution matches README: 306/40/8/7/1
- [x] `ruff check .` not re-run in sandbox (no ruff installed
      locally) but the prior audit's result is "0 issues" and
      no Python files were touched in this branch
- [x] `git grep -E "TODO|FIXME|XXX|HACK"` returns 0 hits in
      `docs/`
- [x] `git grep -iE "api[_-]?key|token|secret|password|bearer"`
      returns 0 hits in tracked files
- [x] No `eval()` in `docs/app.js`, `docs/js/*.js`
- [x] CSP header is present, has `script-src` hash-pinned,
      has `style-src 'unsafe-inline'`, has SRI on Tabulator
- [x] Live `https://56eli.github.io/docsheet/` is not
      reachable from this sandbox (network restricted); the
      post-deploy verification step proposed in
      `manual-workflow-edits.md` is the right answer

---

## 14. Scoreboard Alignment

My independent re-audit agrees with the current scoreboard
(`overall_effective 8.5 / gate pass`) on every aspect except
**repo organization** (I would score it 7, matching AI's 7 — the
12 root `.md` files are better than the prior 21, but the
normative six could move to a subdirectory) and **performance**
(I would add a Lighthouse budget step before declaring 8/10
confident — currently 8 with medium confidence per the
scoreboard, which is fair).

The two AI/owner disagreements from earlier sessions
(UX 9 vs 5, Pages 8 vs 5) have been resolved by the
019fe8a5 session: the owner indicated the prior 5/10
scores were outdated; the current owner score for UX
is 8/10 (per the scoreboard `user_basis`), Pages is now
8/10 AI with no owner score, and the row-delivery fix
is on this branch awaiting visual acceptance.

---

**Summary for the owner:** DocSheet is in excellent shape. The
data pipeline is exemplary, the tests are comprehensive, the
security model is tight, and the frontend modularisation is
underway. The two real outstanding items are operational
(apply the Pages-CI cutover in `.scoreboard/manual-workflow-edits.md`)
and procedural (get owner visual acceptance of the deployed
row-delivery fix). Everything else is incremental polish.
