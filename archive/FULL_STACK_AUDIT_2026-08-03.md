# Full-Stack Audit — 2026-08-03 (current)

**Date:** 2026-08-03
**Branch:** `arena/019fc9b5-docsheet`
**Scope:** entire repository — data pipeline (8 Python modules), generated
artifacts (`data/*.csv/json`, `docs/*.json`), frontend (`docs/index.html`,
`docs/app.js`, `docs/style.css`), test suite, CI/CD (3 GitHub Actions
workflows), documentation, and security posture.
**Supersedes:** the five overlapping 2026-08-03 audit reports now archived
under `archive/` (see `archive/README.md`).

> ## Re-verification refresh — 2026-08-04 (branch `arena/019fc9b5-docsheet`)
>
> Every command in §2 was re-executed after the 2026-08-04 batch (taxonomy
> rulings, NC edition fills, Master-ID sort fix) and is **green**: all 5
> `--check` modes pass; the deterministic suite runs **100/100 tests** at
> **92% coverage** (fixtures now strip edition-keyed overrides when a test
> rewrites the edition layer); `py_compile` on all 8 modules; `node --check`
> on `docs/app.js`, `playwright.config.js`, `tests/csv-export.spec.js`, and
> `tests/column-layout.spec.js`. Re-derived counts: master 356 (307 lecture /
> 38 book / 10 discussion / 1 untyped), 236 catalogue codes, 68 exclusions,
> **110 approved overrides** (was 106 — four `source_url_nightingale_conant`
> fills keyed by edition candidate key), 333 relationships, 7 compilations,
> Everything 376, series taxonomy 179 matched → **169 approved / 0 proposed /
> 10 rejected** (all 10 conflicting 2026-08-04 proposals ruled: 3 approvals
> re-seriesed masters 357/312/313; build confirms exactly 3 series changes).
> Frontend: numeric-column detection now applies Tabulator's built-in
> `number` sorter with empties pinned bottom — the "Master ID not counting
> in order" defect is fixed and guarded by new e2e assertions (Chromium runs
> in CI; ordering additionally verified by replaying Tabulator 6.5.2
> `_sortRow` semantics over committed `docs/master.json` in the sandbox).
> Open items from §7 shrink to: record 246, 8 blank formats, **four**
> always-empty master columns (NC column left the list), wider browser tests.

---

## 1. Executive summary

DocSheet is **verified-healthy with zero critical defects**. Every claim was
independently re-executed in a clean environment (fresh Python 3.11 venv,
pandas 3.0.5, Node 22): all 5 generator `--check` modes pass, the
deterministic suite runs **96/96 tests** in ~2 s at **92% coverage** (gate
80%; every pipeline module ≥ 89%), and all JavaScript parses cleanly. Every
published catalogue count was re-derived from `docs/catalogue-meta.json` and
the generated CSVs and matches the README/handoff exactly. Remaining work is
hygiene-level: five always-empty master columns, record 246, 8 blank formats,
a missing LICENSE, narrow browser-test coverage, and minor frontend dead code.

## 2. Verification matrix (re-executed, not trusted)

| Check | Method | Result |
|---|---|---|
| Python syntax | `python -m py_compile *.py` | ✅ all 8 modules |
| Stale-artifact guards | `process_data.py --check`, `build_research_master.py --check`, `build_catalogue_pages.py --check`, `reconcile_research_master.py --check`, `map_series_taxonomy.py --check` | ✅ 5/5 |
| Deterministic suite | `python -m unittest discover tests` | ✅ 96/96 in ~2 s |
| Coverage gate | `coverage run -m unittest discover tests && coverage report` | ✅ 92% total; all modules 89–99% (`fail_under = 80` in `.coveragerc`) |
| JS syntax | `node --check docs/app.js playwright.config.js tests/csv-export.spec.js` | ✅ |
| Master counts | re-derived from generated files | ✅ 356 (307 lecture / 38 book / 10 discussion / 1 untyped), 236 catalogue codes, work_id 356/356 |
| Everything view | `docs/master.json` row count | ✅ 376 (356 master + 8 veritas + 4 discovery + 4 hayhouse + 4 audible + 0 pending) — updated 2026-08-04 after the Veritas refresh link-up |
| Review state | re-derived | ✅ 68 exclusions, 106 approved overrides, 333 reviewed relationships, 7 series compilations, 26/26 candidates promoted |
| Blank tails | re-derived | ✅ 8 blank formats, 30 blank years, 57 blank months — matches docs |
| Deprecated vocabulary | `item_type ∈ {audio, video}` | ✅ **retired 2026-08-03** (this branch): 0 master rows, constant removed, validators reject it, 4 guard tests |

## 3. Architecture strengths (keep)

- **Review-gated pipeline:** generated artifacts are never hand-edited; every
  generator has a `--check` mode plus tamper-detection tests; the CI workflow
  runs all of them read-only (`permissions: contents: read`).
- **Hard-fail validators:** master-item integrity, work-family coverage,
  Veritas derived-count consistency, and primary-relationship coverage are
  build failures, not warnings.
- **Live-API safety:** `fetch_veritas_catalogue.py` and the Map Veritas
  Catalogue workflow are review-only (diff artifact + intentional fail-gate;
  nothing auto-commits from the network).
- **Frontend security:** strict CSP without `unsafe-inline` for scripts
  (one hashed inline bootstrap — the `script-src` hash was corrected on
  2026-08-04 to the CSP3 whitespace-stripped value after it had drifted out of
  sync with the pre-paint bootstrap), SRI-pinned Tabulator 6.5.2 CDN,
  `object-src 'none'`, `base-uri 'self'`, `connect-src 'self'`; cell editing
  deliberately disabled with an in-code rationale.
- **Documentation-currency tests:** README/handoff/ledger counts are asserted
  against generated data, so numeric drift fails CI (verified working — they
  guarded this consolidation).

## 4. Findings (ranked)

### Medium — hygiene/decisions pending

1. **Five always-empty master columns** (`location_physical`,
   `location_digital`, `location_streaming`, `source_url_nightingale_conant`,
   `reference_url_2`): populate or drop. Note the handoff previously claimed
   *six* including Hay House — `source_url_hay_house` now holds 28 values;
   corrected in this pass.
2. **Record 246** ("In the World But Not of It" – Audio): the 1 untyped
   record, deferred pending physical-edition confirmation; product 1661 stays
   mapping-row only (no source override until ruled).
3. **8 blank formats** (5 "On The Road Talk Series" lectures UUIDs
   221/225/226/227 + 246 untyped, 3 Discussion Series records 278/281/284):
   no automated inference match; evidence in
   `archive/TEMP_RESPONSE_AUDIT_2026-08-03.md` §11c/§11d.
4. ~~No LICENSE~~ — **resolved 2026-08-04**: MIT `LICENSE` added and linked
   from the README.

### Low — code polish

5. ~~`docs/app.js` header advertises "inline editing"~~ — fixed 2026-08-04
   (comment corrected; the dead `cellEdited` listener and orphaned
   `flashNote`/`FOOTER_IDLE_NOTE` code removed).
6. ~~`footerUpdated.innerHTML` despite dynamic content~~ — fixed 2026-08-04:
   the timestamp is now built with text nodes (`replaceChildren` +
   `textContent`), leaving no `innerHTML` with interpolated data.
7. Root source CSV filename contains spaces — handled everywhere (quoted in
   workflows, glob fallback in `process_data.py`) but a rename removes a
   class of shell-escaping risk.
8. **Playwright coverage is narrow:** 5 specs centered on CSV export; the 17
   tabs, column chooser, row drawer, and dark-mode toggle have no browser
   tests (CI runs them; sandbox cannot download Chromium — documented trap).
9. Python runtime deps are unpinned (`pandas>=2.0,<4`); verified working on
   pandas 3.0.5, but a lock story would make CI byte-reproducible.
10. Version skew by design: sandbox Python 3.11/Node 22 vs CI 3.12/Node 20 —
    documented in the handoff, keep compatible.

### Owner-action carryover (from handoff P0)

11. ~~Re-run the **Map Veritas Catalogue** workflow~~ — **resolved
    2026-08-04**: the failing run's diff was reviewed and accepted (13
    legitimate re-matches to masters minted 2026-08-03), the overlay's 17
    stale suppression rows were lifted (`candidate_veritas` 28 → 8), and the
    inventory was LF-normalized. The next run on `main` after this branch
    merges should pass clean; see `VERITAS_ARTIFACT_REVIEW.md` Addendum 3.

## 5. Documentation consolidation (this pass)

Root Markdown reduced **34 → 20 files**. Archived to `archive/` (indexed in
`archive/README.md`, preserved in git history):

- The five overlapping 2026-08-03 audits this report supersedes:
  `AUDIT_2026-08-03_FULL.md`, `COMPREHENSIVE_AUDIT_2026-08-03.md`,
  `STATUS_QUO_AUDIT_2026-08-03.md`, `TEMP_RESPONSE_AUDIT_2026-08-03.md`,
  `EVERYTHING_VERIFICATION_REPORT_2026-08-03.md`.
- Five applied one-off reports: blank-cells, format, and year/month backfill,
  deduplication/URL-fill, and schema cleanup; plus
  `SESSION_SUMMARY_2026-08-03.md` (superseded by handoff §4).
- Four closed reviews: `SPREADSHEET_AUDIT.md`, `SPREADSHEET_UX_REVIEW.md`,
  `UUID_264_REVIEW.md`, `RELATIONSHIP_EXPANSION_AUDIT.md`.

Prose drift fixed beyond the currency tests' reach: README record-type table
`(350)` → `(356)`; README audit link retargeted here; handoff "six
always-empty columns" corrected to five; every root doc's reference to a
moved file now uses its `archive/` path.

## 6. Grades

| Area | Grade | Note |
|---|---|---|
| Data pipeline correctness | A | Deterministic; all guards green; 92% meaningful coverage |
| Data governance / provenance | A+ | Review CSVs, `decisions/`, no-hand-edit enforcement |
| Frontend | B+ | Accessible, CSP-hardened; minor stale comment + dead listener |
| CI/CD | A− | Thorough read-only CI; unpinned Python deps; no scheduled refresh |
| Documentation | B+ | Depth is excellent; consolidation round 2 restored root to 20 files |
| Security | A− | No secrets, no injection surface, review-only live fetch; add LICENSE |

## 7. Recommended next actions

1. Rule on the five empty columns (populate or drop via schema change).
2. Add a LICENSE.
3. Widen Playwright coverage (all tabs, column chooser, drawer, dark mode).
4. ~~Retire the unused `audio`/`video` item-type vocabulary from rule matrices~~
   — **done 2026-08-03 on `arena/019fc9b5-docsheet`** (see handoff §4 item 14;
   only the unreviewed discovery-triage lane keeps 4 free-text `audio` values
   pending an owner ruling).
5. Owner: re-run the Map Veritas Catalogue workflow (§4 item 11).
