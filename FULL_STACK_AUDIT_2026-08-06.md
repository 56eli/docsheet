# Full-Stack Audit — 2026-08-06

**Branch:** `arena/019fd6fa-docsheet` (branched from `main` @ `0b54614`, the PR #23 merge)
**Auditor:** Arena agent session `019fd6fa` — independent re-verification of every claim in
`NEXT_AGENT_HANDOFF.md`, `README.md`, and `archive/FULL_STACK_AUDIT_2026-08-04_FINAL_358_V2.md`,
run from a clean venv (Python 3.11 in-sandbox; CI uses 3.12) plus live checks of the
deployed site and GitHub Actions history.

**Verdict: the pipeline is green and every published count in the guarded docs is
accurate.** No new data defects found. Six findings (all LOW/OPEN), listed in §4.

---

## 1. Verification results (all reproduced independently)

| Check | Claimed | Reproduced | Status |
|---|---|---|---|
| `python -m py_compile *.py` | passes | passes | ✅ |
| `build_research_master.py --check` | matches inputs | 358 items; 69 excluded rows; 109 overrides; 29 candidates validated | ✅ |
| `build_catalogue_pages.py --check` | matches inputs | 378 Everything rows | ✅ |
| `reconcile_research_master.py --check` | matches inputs | report current | ✅ |
| `map_series_taxonomy.py --check` | matches inputs | 179 mappings; 6 queued (see F6) | ✅ |
| `process_data.py --check` | matches source | 374 raw rows × 13 cols | ✅ |
| `python -m unittest discover tests` | 103 tests | **Ran 103 tests — OK** in 2.4s | ✅ |
| `coverage report` | 92%, all modules ≥ 89%, gate 80% | **92% total**; min module `map_series_taxonomy.py` 89% | ✅ |
| `node --check` on `docs/app.js`, `playwright.config.js`, both e2e specs | OK | OK (Node 22 in-sandbox; CI Node 20) | ✅ |
| Live site `https://56eli.github.io/docsheet/` | serves current data | page live, Everything view shows **378 rows**, catalogue codes/cleaned titles present | ✅ |
| CI on `main` | green | latest run `31093916556` (PR #23 merge) **success**; Pages deploy success | ✅ |
| Playwright e2e | runs in CI only | not run in sandbox (Chromium not installable — documented) | ➖ |

## 2. Data-layer counts (regenerated vs. `docs/catalogue-meta.json`)

| Metric | Meta | Independently counted in `docs/master.json` / CSVs | Match |
|---|---|---|---|
| Master records | 358 | 358 (IDs 1–361; 249, 264, 302 retired) | ✅ |
| `item_type` split | 307 lecture / 40 book / 10 discussion / 1 untyped | identical; the 1 untyped is record **246** (deferred) | ✅ |
| Catalogue codes | 271 | 271; 0 codes on `book` rows (rule holds) | ✅ |
| Everything view | 378 = 358 master + 8 veritas + 4 discovery + 4 hayhouse + 4 audible | identical; candidates are the 7 Highlights compilations + Map of Consciousness poster, 4 NC compilations, 4 Hay House, 4 Audible | ✅ |
| Exclusions / source overrides | 69 / 109 | 69 / 109 (`docs/master-exclusions.json`, `docs/source-overrides.json`) | ✅ |
| Product relationships | 333 (325 derived + 8 hand-maintained) | `docs/product-relationships.json` 333; `data/product_relationships.csv` 8 × `related_material` | ✅ |
| Series compilations / Veritas products / decisions | 7 / 191 / 18 | 7 / 191 / 18 | ✅ |
| Series taxonomy | 169 approved / 0 proposed / 10 rejected | identical in `data/series_category_mapping.csv` | ✅ |
| Work families | 201 works / 334 members, coverage 358/358 | `work_id` non-empty on 358/358 master rows | ✅ |
| Hay House / Nightingale-Conant URL fills | 27 / 4 | 27 / 4 non-empty cells (handoff §6 says 28 for Hay House — actual data is **27**; one row lost in the Path dedup, count stale by one) | ⚠️ F1 |

### Data hygiene probes (new this audit, not previously enumerated)

- **Duplicate titles:** 70 `(title, format)` groups appear on >1 master row — all are
  legitimate multi-part works: every group resolves to **distinct `proposed_filename`
  values** (no on-disk collision) and single-part rows carry no bracket. ✅
- **Six of those groups carry *per-part* `work_id`s** (Volume II/III/V, The Presence of
  Spiritual Awareness, Verification of Spiritual Realities) while the rest share one
  `work_id` (e.g. Causality). See F5 — the governing ruling is not recorded in the repo.
- **`year > 2012` on recordings:** 9 recording rows retain posthumous listing-date years
  (228, 229, 230–232, 268, 309, 356, 357) — the handoff's "7 remain flagged" counts title
  groups, not rows; record 358 (`2025`) is legitimately posthumous. Open, needs © evidence.
- **Blank `year`:** 31 rows = 20 pre-2000/deferred + **11 audiobook edition rows
  (UUIDs 333–343)** flagged by the 2026-08-04 audit, still unresolved (needs owner ruling
  on inheriting the work's year).
- **Blank `format`:** 8 rows (221, 225, 226, 227, 246, 278, 281, 284) — matches docs.
- **Always-empty master columns confirmed:** `location_physical`, `location_digital`,
  `location_streaming`, `reference_url_2` are empty on all 358 rows (populate or drop).
- **4 discovery-lane rows still carry free-text `item_type=audio`** — the documented
  triage exemption; validators reject these values everywhere else.
- **CRLF line endings:** only `hawkins archive clone - Sheet1.csv` (Google export,
  harmless) and `data/filename_proposal_YYYYMM.csv` (hand-maintained input). No generator
  rewrites the latter, so no diff-noise risk, but it diverges from the repo LF convention.
- **No orphan data files:** all 24 CSV/JSON inputs in `data/` + the 3 root CSVs are
  consumed by at least one generator.

## 3. Frontend & security review (`docs/index.html`, `docs/app.js`)

- CSP meta present and restrictive: `default-src 'self'`, hash-pinned inline script,
  `object-src 'none'`, `connect-src 'self'`. ✅
- All 3 CDN assets (Tabulator JS + 2 CSS) carry SRI `integrity` + `crossorigin`. ✅
- `innerHTML` used 4×: two clear-to-empty, one static loading message, one error message
  interpolating `view.file` — a value from the hardcoded view config, not user/JSON data.
  Not exploitable today; `textContent` would be cleaner. LOW.
- CSV export is whole-sheet (`rowRange "all"`); record-type labelling on Everything is
  explicit in the UI ("Curated master" vs candidate classes). ✅
- Playwright coverage: 2 specs (CSV export, column layout). Handoff P2 already lists
  widening browser tests (tab set, chooser, drawer, dark mode) as open work.

## 4. Findings

| # | Severity | Finding | Suggested action |
|---|---|---|---|
| F1 | LOW (doc drift) | The trailing "**2026-08-04 Final Audit**" section of `NEXT_AGENT_HANDOFF.md` is stale: master 356 (307/38/10/1), overrides 110, everything 376, work families 332 — actual: **358 (307/40/10/1), 109, 378, 334 members**. Handoff §6 also claims 28 Hay House URLs vs **27** in data. The doc-currency tests only guard §3 of the handoff, so this drifted silently. | Mark the section superseded or delete it (it predates the PR #23 close-out it describes); optionally extend currency tests to any count-bearing handoff section. |
| F2 | OPEN (owner ruling) | 11 audiobook edition rows (UUIDs **333–343**) have blank `year`. | Owner ruling: inherit the work's first-publication year (one reviewed-input edit in `edition_candidates.csv`) or leave blank. |
| F3 | OPEN (evidence) | 9 recording rows keep posthumous listing years (2023/2014); 8 blank `format` rows; record 246 still untyped/deferred; 4 NC discovery rows unruled; 4 always-empty columns. | All are already tracked in handoff §6 — no new action beyond owner decisions. |
| F4 | LOW (governance gap) | Handoff cites a "**D6a per-part ruling**" that exists nowhere in the repo: `EDITION_MODEL_PROPOSAL.md`'s decision table ends at D5, and its D1(a) recommends *one* `work_id` per video edition — yet 6 multi-part groups now have per-part `work_id`s while ~64 others share one. | Record the D6a ruling text in `decisions/` (which series it covers and why), or re-align the 6 groups to one-work-per-series. Currently the split is unverifiable tribal knowledge. |
| F5 | LOW (hygiene) | CI on `main` failed once after the PR #22 merge (run `30934095403`, logs expired —cause unknown); green again since PR #23. Also `data/filename_proposal_YYYYMM.csv` is CRLF in an LF repo. | No current action; watch next main run. Normalize the CSV to LF on its next edit. |
| F6 | INFO (labeling) | `map_series_taxonomy.py --check` prints "6 queued for review" — those 6 queue rows are all *ruled* (3 approved, 3 rejected); nothing is pending. | Cosmetic message tweak if desired. |

## 5. Architecture assessment (unchanged, confirmed sound)

- The review-gated pipeline (raw CSV → hand-maintained ledger → master → Pages JSON with
  `--check` byte-stability gates at every layer) is holding: zero drift between any
  committed input and generated output across all five generators.
- Derived primary relationships (325 auto + 8 curated) eliminated a whole class of
  hand-edit divergence; tamper detection + doc-currency tests guard the rest.
- Test suite remains deterministic, offline, and fast; coverage gate 80% with 92% actual.
- Known structural debt stands as documented: F2-merge of manual + edition candidate
  lanes (deferred, higher-risk); `fetch_veritas_catalogue.py` is the only network-bound
  component and stays review-only by design.

## 6. Bottom line

No blocking issues; no data corruption; every guarded number in the docs is exact.
The only new work items are hygiene-level: refresh one stale handoff section (F1),
document the D6a per-part ruling (F4), and rule on the 11 blank edition years (F2).
