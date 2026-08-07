# Full-Stack Project Audit — Session 2026-08-07 (branch `arena/019fdcda-docsheet`)

## One-sentence summary

DocSheet is a healthy, deterministically-verified static catalogue pipeline (358-master / 378-Everything / 280 codes / 127 overrides / 104 tests / 91% coverage, all 5 `--check` modes green) whose most recent changes (PRs #23–#25: filename v4, year provenance + Amazon links, and the post-PR24 drift fix) are sound, with only minor doc drift and the known intentional review queues remaining.

---

## 1. What this project is

A static GitHub Pages catalogue of David R. Hawkins material. A raw Google-Sheets CSV (374 rows) flows through a hand-maintained `migration_review_ledger.csv` + review overlays (`data/*.csv`) into deterministic Python generators that emit `data/research_master_draft.*` and 24 `docs/*.json` sheets, rendered by Tabulator 6.5.2 in `docs/index.html` / `docs/app.js`. Governance is review-gated: nothing enters the master without an approved row in an input file; generated artifacts are never hand-edited (enforced by `--check` modes and 104 tests, 91% coverage, gate 80%).

Pipeline: `process_data.py` (raw pass-through) · `build_research_master.py` (ledger → 358 master) · `build_catalogue_pages.py` (→ 24 Pages JSONs) · `map_series_taxonomy.py` (publisher taxonomy → series) · `reconcile_research_master.py` (→ RECONCILIATION_REPORT.md) · `fetch_veritas_catalogue.py` (live API, review-only). CI on `main` runs all checks + Playwright.

## 2. Recent changes (last 3 merges to main)

| PR | Merged | Title / content | Verdict |
|---|---|---|---|
| **#23** | 2026-08-06 | Proposed-filename column + filename v4 + Volume pre-2000 year strip + streaming blind-spot fix + academic completeness | ✅ Sound |
| **#24** | 2026-08-07 14:57 | Year-provenance model (`year_source`, `data/year_provenance.csv`, `YEAR_COLUMN_PROVENANCE.md`), Amazon direct links (`source_url_amazon`, 18 links, overrides 109 → **127**), 11 edition audiobook years inherited, Office outliers (Stress 1987, Death and Dying 1983), frontend Year-Source/Amazon display | ✅ Sound; left CI red on main (below) |
| **#25** | 2026-08-07 15:31 | Post-PR24 audit branch: regenerated stale `docs/source-overrides.json` + `docs/review-overview.json` (127 overrides), fixed Volume Series filename groupings (206–207, 213–214 mislabeled as Volume II/V parts) + regression test | ✅ Sound, closes the #24 drift |

**PR #24 left CI red on main:** the main-push CI run `31190252289` failed at *"Verify Pages catalogue matches its inputs"* because PR #24 bumped approved overrides to 127 without regenerating `docs/source-overrides.json` / `docs/review-overview.json`. PR #25 (commit `5bdfd238`) regenerated them; the PR #25 merge CI run (`31193089841`) is green. Live Pages deploy for the #25 merge is currently building.

## 3. Independent verification (re-run this session)

All in a clean venv (Python 3.11.2, Node 22.22.3):

| Check | Result |
|---|---|
| `process_data.py --check` | ✅ pass |
| `build_research_master.py --check` | ✅ pass (358 items; 69 excluded; 127 overrides; 29 candidates) |
| `build_catalogue_pages.py --check` | ✅ pass (378 Everything rows) |
| `reconcile_research_master.py --check` | ✅ pass |
| `map_series_taxonomy.py --check` | ✅ pass (179 mappings; 6 queued) |
| `python -m unittest discover tests` | ✅ **104/104** in 2.8s |
| Coverage | ✅ **91%** total (gate 80%); modules 89–100% |
| `node --check` on app.js + 3 test/config JS | ✅ pass |
| Data invariants (own profiling) | ✅ codes only on lecture/discussion; year_source 358/358; 201 work_ids all `w-`; 0 UUID dupes; only 246 untyped |
| `docs/source-overrides.json` | ✅ 127 rows, matches meta |

## 4. Current verified state

| Metric | Value | Source |
|---|---:|---|
| Master rows | 358 (307 lecture / 40 book / 10 discussion / 1 untyped) | master.csv |
| Everything rows | 378 (358 master + 8 veritas + 4 discovery + 4 hayhouse + 4 audible + 0 pending) | catalogue-meta.json |
| Catalogue codes | **280** distinct, lecture/discussion only | master.csv |
| Exclusions / source overrides | 69 / 127 (incl. 18 Amazon) | meta + csv |
| Veritas / HayHouse / Audible inventory | 191 / 24 / 26 | meta |
| Product relationships rendered | 336 (328 derived primary + 8 hand-maintained related) | meta |
| Series compilations | 7 | meta |
| Work families | 201 works / 334 members, coverage 358/358 | master.csv |
| Edition layer | 24 candidates / 24 promoted | csv |
| Filename proposal | 358/358, unique | master.csv |
| Series taxonomy | 179 mappings (169 approved / 10 rejected / 0 proposed), 6 informational queue rows | check |
| Streaming URLs | 36 approved → 59 masters with `reference_url_1` | csv/master |
| Blank year / blank format | **18** / **2** | master.csv |
| Year Source coverage | 358/358 (incl. blank-reason rows) | master.csv |
| Amazon / NC / HayHouse URLs | 18 / 4 / 27 | master.csv |

## 5. Findings

### Strengths (verified, not just claimed)
- **Determinism & tamper detection**: 5 `--check` modes, run-twice-identical outputs, tests tamper inputs to prove failures.
- **Governance**: reviewed-input-only promotion, stable pinned UUIDs, derived primary relationships (328), no title-based inference, evidence-based title hygiene with `legacy_title` preservation.
- **Doc-currency tests** pin README/handoff/ledger counts so the headline numbers cannot silently drift.
- **Security**: CSP with verified inline-script hash, SRI-pinned CDN, no innerHTML injection, no secrets, LF endings.
- **CI governance**: `map_veritas_catalogue.yml` is manual/review-only (never auto-commits), `ci.yml` is read-only.

### Doc drift found this session (new, not previously logged)
1. **Catalogue-code count 271 vs 280.** `NEXT_AGENT_HANDOFF.md` §6 and `FULL_STACK_AUDIT_2026-08-07_DEEP.md` (current-state table) say **271**; the live master has **280** distinct codes (README says 280 and the doc-currency test pins it). The 9-code delta came from PR #24's year fixes (records gaining years gain codes). The deep audit already flags its pre-PR24 baseline; the handoff's §6 parenthetical `(catalogue codes 284→271)` is now stale.
2. **`reference_url_1` count 55/56 vs 59.** Post-PR24 audit says 36 streaming rows apply "55 master reference URLs"; live master has **59** rows with `reference_url_1` (likely from the PR #25 filename-regeneration run).
3. **`INSTRUCTIONS.md` still describes the raw pass-through pipeline** ("The pipeline is intentionally pass-through right now") without pointing to the curated-catalogue pipeline documented in README — misleading for a new reader, though the two pipelines are deliberately separate.
4. **`FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md`** still carries "1995-1999 estimated" Volume-Series prose vs the blank-pre-2000 reality (known from the deep audit; not yet synced).

### Known intentional gaps (documented; need owner rulings, not code fixes)
- **18 blank years**: 13 intentional (Volume Series pre-2000, owner decision) + 5 under investigation (Verification of Spiritual Realities 230–232, record 246, God is Hidden 268).
- **2 blank formats**: UUID 221 (Progressive Levels of Consciousness, Oxford 2003, has year) and record 246.
- **Record 246** (`"In the World But Not of It" – Audio`): sole untyped/formatless/yearless record; deferred pending physical-edition ruling.
- **Review queues**: 4 NC discovery rows, 4 HayHouse + 6 Audible unreviewed, 3 Audible possible-related, 6 informational taxonomy-queue rows (all ruled), 1 manual lead.
- **4 always-empty master columns**: `location_physical`, `location_digital`, `location_streaming`, `reference_url_2` — populate or drop.
- **Streaming coverage partial**: 36/36 approved but ~115+ Veritas lectures not yet mapped.
- **Month blank 119** — by design for year-only records; not flagged as defect.

### Process notes
- **GITHUB_TOKEN Pages-trigger trap** (documented): the Update Spreadsheet workflow's auto-commit does not trigger Pages; manual re-run or PAT needed.
- **Playwright cannot run in this sandbox** (CDN TLS resets) — e2e is CI-only; PR #25 CI e2e passed.
- `RECONCILIATION_REPORT.md`'s "53 extras not yet reconciled" is expected (edition/promotion layer) but reads like a failure to newcomers.

## 6. Grades (updated with this session's numbers)

| Area | Grade | Note |
|---|---|---|
| Pipeline determinism | A+ | 5 checks, run-twice identical, tamper tests |
| Data governance | A+ | review-gated, derived primary, no inference |
| Data completeness | A− | 358 master, 280 codes, but 18 year/2 format blanks + queues |
| Edition/work model | A | 201 works/334 members, 24 editions, coverage 100% |
| Frontend | A | measured widths, numeric sort, CSP/SRI, dark mode, .nojekyll |
| Tests | A+ | 104 deterministic, 91% coverage, doc-currency guards |
| CI/CD | B+ | green again after PR25; Pages-trigger trap remains |
| Docs | B+ | comprehensive; 4 small drift items listed in §5 |

## 7. Recommendations (prioritized)

1. **Fix the 4 doc-drift items** (§5): sync handoff + deep-audit codes 271→280, `reference_url_1` 55/56→59, INSTRUCTIONS.md pointer to the catalogue pipeline, FILENAME_PROPOSAL_V4 Volume-year prose. Cheap, closes the only "stale" findings.
2. **Rule on record 246 + the 2 blank formats** (smallest high-signal catalogue holes; deep audit agrees).
3. **Research the 5 under-investigation years** (Audible © years / product pages) via `fetch_page`, land as `proposed_year` in reviewed inputs.
4. **Rule the discovery queues** (4 NC compilations; HayHouse/Audible unreviewed — most are likely merchandise/excluded).
5. **Continue streaming mapping** in small approved batches (~115 remaining).
6. **Decide on the 4 always-empty columns** (populate or drop).
7. **Optionally** clarify RECONCILIATION_REPORT wording and taxonomy-queue semantics.

## 8. Reproduction commands (all green)

```bash
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install -r requirements-dev.txt
/tmp/venv/bin/python build_research_master.py --check
/tmp/venv/bin/python build_catalogue_pages.py --check
/tmp/venv/bin/python reconcile_research_master.py --check
/tmp/venv/bin/python map_series_taxonomy.py --check
/tmp/venv/bin/python process_data.py --check
/tmp/venv/bin/python -m unittest discover tests          # 104 pass
/tmp/venv/bin/coverage run -m unittest discover tests && /tmp/venv/bin/coverage report  # 91%
node --check docs/app.js && node --check tests/*.spec.js
```

*End of session audit — 2026-08-07.*
