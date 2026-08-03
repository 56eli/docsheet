# TEMP — Agent Response: Independent Full Audit (2026-08-03, second pass)

**One-sentence task summary:** Familiarized with the project, performed an
independent full audit, found and **fixed CI red on `main` plus three coherence
defects**, verified every check green, and documented residual findings with a
prioritized roadmap.

> Temporary response file — delete after owner review.

---

## 1. What this project is (verified, not assumed)

DocSheet is a **static, review-first research catalogue** of David R. Hawkins
material, published to GitHub Pages:

- **Raw evidence:** `hawkins archive clone - Sheet1.csv` (374 rows, immutable).
- **Review layer:** `migration_review_ledger.csv`, exclusions, source overrides,
  manual candidates/leads, mapping decisions, relationships — all declared CSVs.
- **Generators (deterministic, checkable):** `process_data.py` (raw →
  `docs/data.json`), `build_research_master.py` (ledger → master draft),
  `build_catalogue_pages.py` (master + candidates → 20 Pages JSON files),
  `reconcile_research_master.py` (read-only three-way consistency report),
  `fetch_veritas_catalogue.py` (live Veritas refresh, review-only by design).
- **Site:** Tabulator 6.5.2 (pinned, SRI-hash, CSP), 17+ sheets, read-only,
  search/filter/export, dark mode.
- **CI:** three workflows — `ci.yml` (read-only validation), `update_spreadsheet.yml`
  (regenerates raw-derived JSON), `map_veritas_catalogue.yml` (artifact-only live
  refresh; never commits).

The architecture matches its documented design: raw → ledger → master →
Everything + review sheets, with `--check` modes guarding every generated file.

## 2. Verification performed this session

| Check | Result |
|---|---|
| `python -m py_compile *.py` | ✅ PASS |
| `process_data.py --check` | ✅ PASS (374×13 passthrough current) |
| `build_research_master.py --check` | ✅ PASS (317 items, 68 exclusions, 80 overrides, 17 candidates) |
| `build_catalogue_pages.py --check` | ❌ **FAILED at HEAD → ✅ FIXED** |
| `reconcile_research_master.py --check` | ⚠️ passed but report text **false-alarmed** → ✅ FIXED |
| `node --check docs/app.js` / config / specs | ✅ PASS |
| All 20 `docs/*.json` parse | ✅ valid; counts internally consistent |
| Master integrity (317 rows) | ✅ 0 duplicate UUIDs, 0 duplicate catalogue codes |
| `npm audit` | ✅ 0 vulnerabilities |
| `git diff --check` | ✅ clean |

## 3. P0 findings — found and FIXED in this branch

### F1 — CI was red on `main` (root-caused, fixed)
The committed catalogue outputs were built with `--include-pending`
(359 Everything rows), but `build_catalogue_pages.py` defaulted
`include_pending=False` (353 rows), so the plain `--check` in `ci.yml` reported
`docs/master.json` + `docs/catalogue-meta.json` as stale. **Verified:** the last
two CI runs (`#14` merge + PR) failed; plain `--check` fails on a clean
checkout; `--include-pending --check` passes.

**Fix (chosen over editing `ci.yml`, which previously hit the App's missing
`workflows` permission, and over regenerating 353-row outputs, which would have
silently reverted the pending-candidates feature and contradicted the README):**
`--include-pending` is now **default-on** via
`argparse.BooleanOptionalAction`, with `--no-include-pending` as an explicit
local-inspection escape hatch. Plain `--check`, `--include-pending --check`,
and CI all now pass against the committed 359-row outputs. This also implements
the prior session's own P3 suggestion ("--include-pending as default").

### F2 — Reconciliation report contained a false blocking alarm (fixed)
The committed `RECONCILIATION_REPORT.md` claimed *"checked outputs are not yet
fully reconciled … 359 committed vs 353 projected … Required resolution before
rebuilding"* — purely a side effect of the same default mismatch (the
reconciler projects the catalogue through `build_catalogue()`'s default). Its
`--check` "passed" because it regenerated the identical wrong text. After the
fix it now truthfully reports *"All checked master, exclusion, and Everything
Pages outputs match."* ➜ The safeguard works; its input flag was the bug.

### F3 — `catalogue-meta.json` counts didn't sum (fixed)
`everything_record_types` iterated a fixed 5-class tuple, so the published
counts summed to 353 while `master_items` was 359 — the
`candidate_pending_promotion` class was invisible. Added to the tuple; meta now
sums correctly (317/4/24/4/4/6 = 359).

### F4 — README record-type table stale (fixed)
Documented "306" masters (actual 317) and omitted the pending class; updated.

## 4. Security & front-end review (clean, minor notes)

- **XSS surface:** all `innerHTML` writes use hardcoded constants or clear-only
  assignments; the one data-adjacent case (HTTP `Last-Modified` header) is
  same-origin and low-risk. Tabulator renders cell values as text by default.
- **CSP/SRI:** explicit CSP present; Tabulator pinned to 6.5.2 with SHA-384;
  inline bootstrap covered by SHA-256 hash. `style-src 'unsafe-inline'` remains
  required by Tabulator's inline styles — acceptable, documented.
- **CSV formula injection (LOW, noted only):** Tabulator's CSV exporter does not
  escape cells beginning with `=`, `+`, `-`, `@`. Data is curator-controlled,
  so exposure is minimal; consider a sanitizer if third-party submissions are
  ever imported.
- **Workflows:** live Veritas refresh is correctly artifact-only (read-only perms,
  candidate files git-ignored); `update_spreadsheet.yml` auto-commits only
  `docs/data.json`/`docs/meta.json` scoped to the raw CSV path. Good blast-radius
  control.
- **Dependencies:** `pandas>=2,<4`, Playwright pinned `1.62.1`, lockfile present,
  `npm audit` clean. Python scripts are otherwise stdlib-only.

## 5. Data-quality findings (verified numbers; not blockers)

| Finding | Evidence | Disposition |
|---|---|---|
| 6 (near-)always-empty master columns | `location_physical/digital/streaming` & `reference_url_2`: 317/317 blank; `source_url_hay_house`, `source_url_nightingale_conant`, `reference_url_1`: 316/317 | Owner decision: populate or drop (prior handoff #12) |
| `format` blank on 86/317 records | CSV analysis | Second inference pass possible (prior handoff #13) |
| 92 blank `catalog_code`/`year`, 119 blank `month` | CSV analysis | Expected for non-lecture items; document semantics |
| 1 untyped record; `audio`/`video` still in deprecated vocab | CSV analysis | Final deprecation ruling pending (owner) |
| `format` mixes carrier vocab (`book`, `audio` with `DVD`/`CD`/`streaming`) | 12 `book`, 1 `audio` | Cosmetic; worth a vocabulary note in schema docs |
| `docs/meta.json` + `docs/catalogue-meta.json` fetched by nothing in `app.js` | `fetch()` only loads `view.file` | Either wire meta into the footer or accept as machine-read API; the README already publishes meta as a public contract, so **keep** (documented) |

## 6. Documentation-consistency findings

- 38 root-level Markdown files, incl. 4 overlapping status docs
  (`PROJECT_STATE_AUDIT`, `HANDOFF` [marked superseded], `NEXT_AGENT_HANDOFF`,
  `IMPLEMENTATION_PLAN`), 2 `*_DRAFT.md` beside finalized versions, and several
  `TEMP_*` files self-marked "delete after review"
  (`TEMP_FINAL_AUDIT_ROADMAP_HANDOFF_2026-08-03.md` still references the merged
  `arena/019fc7cd` branch; `UNBLOCK_INSTRUCTIONS.md` is now moot — the CI
  workflow has landed and runs).
- Recommend: owner-approved consolidation into `decisions/` + a single status
  doc (matches prior handoff #16). **Not done unilaterally** — deletions need
  an owner ruling.

## 7. Residual open items (unchanged from prior handoff, re-verified)

1. Record 264 physical-edition confirmation before any source override.
2. Promotion path for the 6 unpromoted manual candidates (needs a
   `promotion-decisions` input keyed by `candidate_key`).
3. CATEGORY_DOMINANCE_POLICY taxonomy mapper as a review layer.
4. Nightingale-Conant provenance pass for the ~5 remaining known products.
5. Playwright coverage: 4 tests / 17+ tabs (Chromium undownloadable in sandbox;
   CI covers it).
6. `LICENSE` file absent on a public repo (MIT recommended).
7. Derived-field invariants: only `normalized_title_match_count` is code-guarded;
   `matched_master_titles` can still desync under hand-edit.

## 8. Changes made in this branch

| File | Change |
|---|---|
| `build_catalogue_pages.py` | `include_pending` default → `True`; `--no-include-pending` opt-out; meta record-types tuple + `candidate_pending_promotion`; comments |
| `docs/catalogue-meta.json` | regenerated (record types now sum to 359) |
| `RECONCILIATION_REPORT.md` | regenerated (false alarm → truthful green state) |
| `README.md` | record-type table: 317 masters + pending class row |
| `TEMP_RESPONSE_AUDIT_2026-08-03.md` | this report |

**Post-fix check battery:** `py_compile`, `process_data --check`,
`build_research_master --check`, `build_catalogue_pages --check` (plain **and**
`--include-pending`), `reconcile --check`, `node --check ×3`, `git diff --check`
— **all PASS.** `--no-include-pending --check` correctly reports the reduced
353-row view as differing from committed outputs (by design, local only).

## 9. Bottom line

The project's engineering is genuinely strong (deterministic checkable
generators, review-only live sync, guarded derived invariants); the found P0 was
a flag/default desync that made `main` red, made the safeguard report cry wolf,
and desynced the published counts — **all three are fixed and verified in this
branch**, with no change to the deployed site's behavior.
