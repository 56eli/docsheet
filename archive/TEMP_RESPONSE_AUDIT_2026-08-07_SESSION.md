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

> **✅ All four fixed 2026-08-07 (owner-selected task):** (1) `FULL_STACK_AUDIT_2026-08-07_DEEP.md` current-state counts synced to 280 codes / 127 overrides / 336 relationships / 59 streaming refs / 18+2 blanks / 106 tests, plus a session-sync note in its header; `NEXT_AGENT_HANDOFF.md` §6 notes the 280 current count and the 59-row streaming state, with historical 2026-08-04 point-in-time numbers left intact as history. (2) `reference_url_1` corrected to 59 in the deep audit and the post-PR24 audit (55 → 59, with the "one product maps to several masters" explanation). (3) `INSTRUCTIONS.md` pass-through claim now scoped to the raw-spreadsheet pipeline with a pointer to the curated-catalogue pipeline in the README. (4) `FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md` "Current sample" block updated to the blank-year Volume filenames (the decision log keeps the 1995-1999 estimate as history); `YEAR_COLUMN_PROVENANCE.md` code-count note updated to 280.

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

1. ~~**Fix the 4 doc-drift items**~~ — **done 2026-08-07** (§5): codes 271→280, `reference_url_1` →59, INSTRUCTIONS.md catalogue-pipeline pointer, FILENAME_PROPOSAL_V4 Volume-year prose all synced; dated 08-04 audits left as point-in-time history.
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

---

## Addendum — Volume Series filename investigation (owner follow-up)

**Reported:** `Volume VI-How to Raise Your Level of Consciousness Volume V Undoing the Barriers to Spiritual Progress [4-5].mp4` and `Volume VII A-Conversation with Knowingness Volume V Undoing the Barriers to Spiritual Progress [5-5].mp4`.

### Root cause (investigated, evidence-based)
- The strings are **not in any committed file** (grep over master, proposal CSV, Pages JSONs, raw CSV, docs — zero hits). They are the pre-PR-#25 **visual/export concatenation** of two adjacent Everything-tab columns: `title` = "Volume VI-How to Raise Your Level of Consciousness" + `proposed_filename` = "Volume V Undoing the Barriers to Spiritual Progress [4-5].mp4" (same for 214 → [5-5]).
- The pre-PR25 `data/filename_proposal_YYYYMM.csv` (reconstructed from the PR #25 diff) contained a **data-entry/grouping error in the reviewed file**: rows 213/214 (Volume VI/VII) had `clean_title` = "Volume V Undoing the Barriers to Spiritual Progress" and `part_index/part_total` = 4/5 and 5/5 (folded into Volume V's group of 5); rows 206/207 (Volume III) were folded into Volume II's group as [3/4]/[4/4]. Same signature confirmed in the pre-PR25 master draft (`VOL601`/`VOL701` rows).
- **Not a generator bug:** nothing writes `filename_proposal_YYYYMM.csv` — it is a reviewed input consumed verbatim by `apply_filename_proposal()` (`build_research_master.py:506`). The generator faithfully applied bad reviewed data, and no validator checked that a part group's titles are mutually consistent, so `--check` stayed green. The error entered during the PR #24 full-file rewrite of the CSV (359+359 lines).
- The live site showed it because the PR #25 Pages deploy (which fixed the CSV + regenerated master/Pages JSONs + added the Volume-group pin test) only completed at 2026-08-07 **15:34:48**; before that the site served the PR #24-era build.

### Fix status
- **Data fixed** by PR #25 (merged 15:31, live 15:34): 213 → `Volume VI How to Raise Your Level of Consciousness.mp4`, 214 → `Volume VII A Conversation with Knowingness.mp4`; Volume V group back to [1-3]/[2-3]/[3-3]; Volume III back to its own [1-2]/[2-2]. Verified again this session in the repo and via the live `filename-proposal.json`.
- **Recurrence guard added this session (new code, 2 new tests, suite 104 → 106):**
  - `build_research_master.validate_filename_proposal_groups()` — fails the build when a reviewed proposal row's `clean_title` tokens are not a subset of its own `title` tokens (a Volume VI row can never carry a Volume V clean title), when `part_index > part_total`, when a part group has duplicate `part_index`, or when a group mixes `part_total` values.
  - Verified zero false positives on all 358 current rows (all 7 legitimately multi-title groups — PART1/2/3 suffixes, Volume I raw titles, Power vs Force audiobook label pair — satisfy the token-subset rule).
  - `tests/test_pipeline.py`: `test_filename_proposal_group_coherence_fails` (replays the historical 213→Volume-V fold, expects build failure) + `test_filename_proposal_part_index_out_of_range_fails`.
- All checks re-verified after the change: 106/106 tests, 5 `--check` modes green, coverage 91% (gate 80%). If the user's browser still shows the old strings, it is a stale cache — hard-refresh.

*Addendum end — 2026-08-07.*

---

## Addendum — Date-parenthetical filename cleanup + duplicate-pair ruling (owner follow-up 2)

**Reported:** `Permanent Inner Peace (2012) 2012 - Permanent Inner Peace (2012).mp4`, `Become That Which You Are (June 2004) PART1 2004-06 - Become That Which You Are (June 2004) [1-3].mp4` — filenames repeating the month-year that the `YYYY-MM - ` prefix already carries.

**Fixed (data, reviewed input `data/filename_proposal_YYYYMM.csv`):** stripped the redundant parenthetical from `clean_title` + filenames on 12 rows — Become That Which You Are (June 2004) ×3, Love is a Way of Being (January 2004) ×3, ... Oxford (2003), Live Life As A Prayer (Audio) (audiobook label, `.m4b` indicates), Unity Church of Sedona 2005 March / 2006 June (CD) (date words moved into a `2005-03 -` / `2006-06 -` prefix, month title-derived). All 356 filenames unique.

**New data finding — duplicate pairs (owner ruling 2026-08-07):** the strip collided because legacy archive rows 281 ("Permanent Inner Peace", ledger raw 318) and 284 ("What is Real Success", ledger raw 321) are the **same 2012 Discussion Series talks** as the promoted Veritas product rows 312/313 (products 50485/50488, `matched_by_primary_source`). Per owner ruling, rows 281/284 were **excluded** (ledger disposition `duplicate` with evidence; exclusions 69 → 71), their work-family memberships dropped (201/334 → 199/332), their filename-proposal rows removed, and 312/313's `(2012)` disambiguator stripped → `2012 - Permanent Inner Peace.mp4` / `2012 - What is Real Success.mp4`.

**New counts:** master **356** (307 lecture / 40 book / 8 discussion / 1 untyped), Everything **376**, codes **278**, exclusions **71**, works 199/332, filename proposal 356 rows. Also fixed stale `year_provenance.csv` rows 278/281/284 (blank_under_investigation → ledger_user_input 2012; 281/284 annotated excluded).

**Verified:** 5 `--check` modes green, 106/106 tests, 91% coverage, JS OK. Living docs updated: README, NEXT_AGENT_HANDOFF §3/§6, MIGRATION_REVIEW_LEDGER.md, FILENAME_PROPOSAL_V4.md, YEAR_COLUMN_PROVENANCE.md, deep-audit sync note.

*Addendum 2 end — 2026-08-07.*

---

## Addendum — Annual Highlights promoted to curated master (owner ruling 3)

**Directive:** "Categorize all 'Highlights of the YYYY lectures' as curated master in the category 'Lecture Highlights' with the Year YYYY and proposed file name same as Title."

**Applied (2026-08-07):**
- **7 new master rows 362–368** (products 1800/1808/1824/36857/39238/40747/44429) via the reviewed promotion path: `manual_master_candidates.csv` +7, `manual_candidate_promotions.csv` +7 (master UUIDs 362–368, `item_type=highlight`, `series=Lecture Highlights`, year from the title, format **streaming** — official storefront pages say "Product Details: Streaming", verified live for 2003/2005; `infer_format` gained a "Lecture Highlights" category rule + unit test).
- **Filename = title** per directive: `Highlights of the 2002 Lectures 1-6.mp4` … `Highlights of the 2007 Lectures.mp4` (no year prefix, no bracket).
- **Inventory:** 7 rows → `matched_by_primary_source` (matched_master_uuids 362–368); the 7 mapping-decision suppression rows lifted (18 → 11); taxonomy mapper proposed and (per the ruling) approved `Lecture Highlights` via rule R1 (179 → 186 mappings, 176 approved).
- **Work families:** 7 per-title works added (206 works / 339 members, coverage 363/363); year_provenance register extended; `series_compilation_relationships.csv` kept (7 rows still document what each Highlights product draws from); `decisions/HIGHLIGHTS_COMPILATION_DECISIONS.md` marked superseded.
- **Counts:** master **363** (307 lecture / 40 book / 8 discussion / 7 highlight / 1 untyped), Everything **376** (candidate_veritas 8 → 1 — only the Map poster remains), relationships **343** (335 derived + 8), codes unchanged **278** (highlights never coded), promoted candidates **36**.
- **Hygiene fix found en route:** `manual_candidate_promotions.csv` had 3 historical rows with unquoted commas in `approval_reason` (parsed as an extra column); re-quoted (content unchanged). A crashed in-place write temporarily truncated the file — restored from git HEAD and rebuilt (36 rows) before regenerating.

**Verified:** 5 `--check` modes green, **107/107 tests** (new format-inference test + relationship-count test updated 328/336 → 335/343), 91% coverage, JS OK. Docs synced: README, NEXT_AGENT_HANDOFF §3, FILENAME_PROPOSAL_V4, YEAR_COLUMN_PROVENANCE, deep-audit sync note.

*Addendum 3 end — 2026-08-07.*

---

## Addendum — Discovery/Audible candidate dedup + unique promotions (owner ruling 4)

**Directive:** "Deduplicate the discovery candidates and audible candidates and implement the unique ones as curated masters."

**Dedup analysis (26 Audible + 4 NC discovery candidates, matched against the master + edition layer):**
- **17 `matched_by_title` Audible rows** → already editions of existing masters (edition-audible-* rows) — no change.
- **Identification & Illusion** (possible_related_match) → duplicate of edition master 338 → `matched_by_title`.
- **El nivel más alto de iluminación / Disolver el ego** (Spanish) → Spanish book/audiobook editions of masters 301/299 → `matched_by_title` (still shown in the International lane).
- **Healing** (NC + Audible) → **same NC program as master 328** ("Healing: Achieving Total Wellness Through Higher Levels of Consciousness", ©2010, NC URL already on 328) → `matched_by_title`.
- **Office Visit Set III** (Audible) → 3-program bundle of existing 1982 Office Visit masters → `excluded_related_material` (compilation, not a new work).
- **Naked** (NC + Audible) → multi-contributor best-of (Williamson, Katie, Dyer, Hawkins) → **excluded** (not a Hawkins master record; live NC page verified).

**Unique → promoted as curated masters (owner ruling; live NC/Audible pages verified 2026-08-07):**
- **369 The Discovery** — NC program (7 sessions), `lecture`, series **Nightingale-Conant**, **©2007** (Audible © line), `audiobook`, NC + Audible URLs (overrides), filename `2007 - The Discovery.m4b`.
- **370 The Ultimate David Hawkins Library** — NC 10-volume compilation, `lecture`, series **Nightingale-Conant**, **©2016**, `audiobook`, `2016 - The Ultimate David Hawkins Library.m4b`.
- **371 OM** — Veritas-published mantra/meditation recording (59 min, Tibetan bell), `other`, series **Media Miscellaneous**, **©2017** (P)2022, `audiobook`, `2017 - OM.m4b`.

**Pipeline changes:** candidates 36 → 39, promotions 39, work families 209/342 (coverage 366/366), filename proposal 366 (unique), overrides 127 → 132, discovery queue emptied (4 → 0), audible lane 4 → 0 candidates, Everything **371** (366 master + 1 veritas + 4 hayhouse). Master item types: 309 lecture / 40 book / 8 discussion / 7 highlight / 1 other / 1 untyped. `decisions/NIGHTINGALE_CONANT_MAPPING.md` updated with the four rulings.

**Verified:** 5 `--check` modes green, **107/107 tests**, 91% coverage. Docs synced: README, NEXT_AGENT_HANDOFF §3/§6, deep-audit sync note.

*Addendum 4 end — 2026-08-07.*
