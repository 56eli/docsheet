# Full-Stack & Catalogue Audit — 2026-08-09 (Expert Pass)

> **Supporting historical snapshot.** The declared-current audit is
> `docs/audits/2026-08-09-deployment-forensics-full-audit.md`.

**Auditor:** Arena.ai Agent Mode (expert full-stack developer + data engineer, independent probes)
**Date:** 2026-08-09
**Branch audited:** `arena/019fe659-docsheet` at `556bf48` (main HEAD = merge of PR #43)
**Status at audited commit:** all six `--check` modes green, 126/126 tests, 91% coverage, no critical or high-severity findings.

---

## 0. Executive summary

This pass re-verified the full stack from the raw Google-Sheets export through the
review ledger, the curated master, the generated Pages JSON, and the browser
frontend — using **independent pandas probes that bypass the project's own
validators** wherever possible. Every headline count claimed by the README and
the current handoff was reproduced exactly, and the ledger → master → exclusions
→ inventory reconciliation is airtight. The audit found **no data-loss or
correctness defects**. Seven low-severity / process items are reported below
(§3), the most substantive being that the ledger's single `needs_review` row is
simultaneously counted among the 75 "retained exclusions" and has never been
formally re-ruled after master 361 absorbed it (§3.1).

**One-sentence summary:** the catalogue is internally consistent end-to-end
(362 masters / 278 codes / 75 exclusions / 134 overrides / 39 promotions / 340
relationships / 7 compilations all verified), and the project setup is sound;
only a handful of low-severity documentation and classification nits remain.

**Post-audit fixes applied in this session (owner-approved, same branch):**
findings §3.1 (ledger row 371 reclassified `needs_review` → `duplicate` of
master 361, derived artifacts regenerated), §3.2 (SERIES_TAXONOMY_MAPPING.md
corrected), §3.3 (slug note added to
`decisions/HIGHLIGHTS_COMPILATION_DECISIONS.md`), §3.4 (Original Spreadsheet
view now hides the 31 blank separator rows by default, with a "Show blank
separator rows" view setting; browser test added), §3.5 (handoff header
refreshed), §3.6 (pass-through wording clarified in README/INSTRUCTIONS/
process_data.py), and §3.7 (archival footnote added to
`archive/FULL_STACK_AUDIT_2026-08-08_INDEPENDENT_ROOT.md`) are **resolved**.
Verification after the fixes: all six `--check`
modes green, 126/126 tests, 91% coverage.

---

## 1. Automated verification (reproduced)

| Check | Result |
|---|---|
| `process_data.py --check` | ✅ docs/data.json matches the 374-row source |
| `build_research_master.py --check` | ✅ 362 items; 75 excluded; 134 overrides; 39 candidates validated |
| `build_catalogue_pages.py --check` | ✅ 362 Everything rows |
| `reconcile_research_master.py --check` | ✅ RECONCILIATION_REPORT.md current |
| `map_series_taxonomy.py --check` | ✅ 186 mappings; 0 queued |
| `sync_inventory_mirrors.py --check` | ✅ mirrors match the master |
| `python -m unittest discover tests` | ✅ **126/126** (matches README claim) |
| `coverage run … && coverage report` | ✅ **91%** total; lowest module 88% ≥ 85% floor |
| `node --check` on app.js / playwright.config.js / 3 spec files | ✅ clean |
| `npm ci` | ✅ @playwright/test 1.62.1 installed (lockfile in sync) |
| Static serve of `docs/` (index.html, app.js, style.css, all 19 view JSONs) | ✅ 200s |
| GitHub Actions (`gh run list`) | ✅ CI green on `main`; Pages build+deploy green |

**Not verifiable in this sandbox** (no regression implied): Playwright browser
download is blocked by the sandbox network (CDN TLS reset), so the 18 browser
smoke tests could not be re-run locally — CI runs them and is green.
`https://56eli.github.io/docsheet` is likewise unreachable from the sandbox, but
the `pages-build-deployment` workflow succeeded on the latest `main` push.

---

## 2. Catalogue data audit (independent probes)

All of the following were recomputed from the CSVs directly (not via the
project's own validators):

### 2.1 Counts (all match README / handoff exactly)

- **362 masters** = 306 lecture + 40 book + 8 discussion + 7 highlight + 1 other; no untyped rows.
- **278 catalogue codes**, all matching `^(LECTURE|DISCUSSION)-(198X|\d{4})-\d{3}$`; 0 duplicates; per-year sequences are gapless 1..N (2002: 1–36, 2003: 1–25, …, 2012: 1–8, 198X: 1–16); codes only on lecture/discussion; **0 books coded; 0 blank-year rows coded; code year == record year in 278/278 rows**.
- **75 exclusions** = 31 blank_separator + 21 series_context + 10 research_note + 7 duplicate + 5 source_context + 1 needs_review; set-identical to the ledger's 75 non-`item` rows (0 unexplained, 0 missing).
- **134 source overrides** = 71 veritas + 26 hayhouse + 21 amazon + 10 audible + 6 nightingale; 0 stale Advaita overlay rows remain.
- **39 promotions** ↔ 39 manual candidates, 1:1, all `approved`, each mapping to a distinct valid master UUID.
- **340 relationships** = 333 primary (derived from `source_url_veritas`, one per URL-bearing master) + 7 `related_material`; 0 pending.
- **7 series compilations** (products 1800/1808/1824/36857/39238/40747/44429 → highlights masters 362–368); target series/years coherent.
- **UUIDs 1–372 with exactly the 10 documented gaps** {225, 226, 227, 246, 249, 264, 281, 284, 302, 309}; no duplicates; ids never reissued.
- **191 Veritas inventory products**; 186 matched + 5 intentionally unmatched (card deck, guided journal, free-CD promo, Map of Consciousness® poster); `normalized_title_match_count` == count of `matched_master_uuids` on every row (the 5 "mismatches" in a naive probe are just `nan` string artifacts of the 5 unmatched rows).
- **191 work families** = 338 work_families memberships + 24 edition-promotion memberships = 362/362 masters covered; **0 memberships point at retired UUIDs; 0 duplicates; 0 work_id conflicts** (the 24 "conflicts" found when joining master→work_families are exactly the edition-minted rows 320–343, which correctly source `work_id` from `edition_promotions.csv` per the documented design).
- **0 masters with `source_url_veritas` outside the inventory** (the "0 orphaned URLs" claim holds).

### 2.2 Field-level hygiene

- **Format × extension matrix is perfectly diagonal**: DVD→253 mp4, CD→32 mp3, audiobook→27 m4b, book→31 pdf, streaming→19 mp4.
- **Filename prefixes**: all 343 dated rows carry `YYYY-MM -` or `YYYY-` prefixes that equal their record year/month (including 16 `198X` placeholder rows); the 19 blank-year rows (13 Volume + 4 under-investigation + 2 REVISION1 ODS overrides on 356/358) intentionally omit the prefix; the 7 Highlights rows follow the separate owner directive "filename equals title" (documented in FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md §"2026-08-07 Highlights promotion").
- **Filename uniqueness**: 362/362 unique; `proposed_filename_display` is the exact `[1-3]`→`[1/3]` rendering of the on-disk safe name, 0 mismatches.
- **Months**: 0 month-without-year; 0 book-months; values are zero-padded `01`–`12` in the CSV (a naive pandas probe shows `1.0` — a float-parse artifact of the probe, not the data; the same class of bug was fixed in the ledger's `proposed_month` and the master is clean).
- **Year sources**: 68 distinct labelled values, all matching the documented vocabulary; the 16 `198X` Office rows carry codes `LECTURE-198X-001…016` as documented; 13 Volume + 4 under-investigation + 2 REVISION1 ODS overrides (356/358) blanks labelled.
- **Titles/notes**: 0 leading/trailing/double spaces, 0 mojibake/control characters, 0 TODO/FIXME/⚠ markers in notes.
- **URLs**: 100% `https://`; no spaces; `reference_url_1` (53 values) is a strict subset of the 36 approved `veritas_streaming_urls.csv` rows.
- **`legacy_tempid`**: 230 present (198 `LSyyyynn_n`, 32 legacy `SAT2011Q01-03` / `VOLxxx` archive ids — expected), 132 blank (candidate/edition-minted rows).
- **Office Series B-02/B-05 "gaps"** are ruled, not missing: the raw sheet itself contains the placeholder rows "where is B-02? might not exist." (OFF14) and "where is B-05? might not exist." (OFF17), owner-approved exclusions 2026-08-03, retained in the ledger with reasons.
- **Series taxonomy**: 186 mapping rows = 177 approved + 9 rejected + 0 queued; 0 approved rows reference unknown master IDs; 0 ledger↔master series conflicts (the "3 series values changed" in the build log are the intended application of approved mappings).
- **Highlight format**: masters 362–368 are `format=streaming` with `.mp4` filenames; code documents a 2026-08-07 storefront verification ("Product Details: Streaming") — see §3.3 for the one slug that still says "dvd".

### 2.3 Known open item (by design, but see §3.1)

Ledger raw row 371 — the owner's own note row in the raw sheet
(`Dialogues on Consciousness and Spirituality: WHAT IS THIS ⚠️⚠️⚠️`) — is the
single `needs_review` row. Its subject was resolved by the promotion of master
361 from candidate `manual-academic-dialogues-1998`, but the ledger disposition
was never updated. Open GitHub issue #18 (owned-flags cross-check vs. the
lak.nz Drive) remains the only other tracked open item, exactly as the handoff
states.

---

## 3. Findings

### 3.1 — Ledger `needs_review` row counted among the 75 "retained exclusions" (Low, classification)

`data/research_master_exclusions.csv` includes raw row 371 with
`disposition=needs_review`, so the published counts ("75 exclusions") and the
Master Exclusions sheet present an **undecided row as an exclusion**. The
project's own `MIGRATION_REVIEW_LEDGER.md` says `needs_review` means
"Ambiguous non-empty row requiring direct decision before migration" — a
decision that was effectively made (master 361 promotion) but never recorded as
a disposition change.

**Suggestion:** owner reclassifies row 371 (e.g., `duplicate` of master 361 /
`research_note` with the promotion reference) so the disposition vocabulary and
the exclusion count agree; or, if the row is intentionally kept `needs_review`
as provenance, document that choice in MIGRATION_REVIEW_LEDGER.md so "75
exclusions" and "1 needs_review" stop reading as contradictory.

### 3.2 — SERIES_TAXONOMY_MAPPING.md contradicts the mapping data on Highlights (Low, doc drift)

The doc states Highlights products are "intentionally out of scope here (all
seven are unmatched compilations)". In fact all seven (1800/1808/1824/36857/
39238/40747/44429) sit in `data/series_category_mapping.csv` as **approved R1
rows matched to masters 362–368**. The sentence appears to predate the
2026-08-07 highlight promotions and should be corrected (the R1 rule in the
same document already describes exactly how they map).

### 3.3 — Highlights `format=streaming` vs. the `…-2002-dvd` product slug (Low, confirm)

Product 1800's official URL is
`…/the-way-to-god-highlights-of-the-first-6-lectures-of-2002-dvd/`, yet master
362 is `format=streaming`. `build_research_master.py` documents a 2026-08-07
storefront verification ("Product Details: Streaming", checked for the 2003/
2005 pages), so this is an evidence-backed ruling — but the slug is the only
place in the dataset that still says "DVD" for these items, and the ruling
isn't recorded in a `decisions/` doc. A one-line owner confirmation (or a note
in `decisions/`) would close it.

### 3.4 — "Original Spreadsheet" tab renders 31 empty rows (Low, UX)

`docs/data.json` publishes all 374 raw rows, including 31 fully-empty
visual-separator rows from the source sheet; `app.js` `loadData()` performed no
empty-row filtering, so the tab and its CSV export included ~31 blank rows
(including the very first displayed row).

**RESOLVED 2026-08-09:** the Original Spreadsheet view now hides rows with no
non-empty field by default (grid, footer count, and CSV export all follow),
and a **"Show blank separator rows"** checkbox in View settings (visible only
on that tab, persisted per browser) restores the verbatim 374-row sheet.
Covered by `tests/blank-rows.spec.js` (counts derived from `data.json`, never
hardcoded).

### 3.5 — NEXT_AGENT_HANDOFF.md header names the previous session's branch (Low, doc)

The handoff says "current handoff for branch `arena/019fe63c-docsheet`"; this
session runs on `arena/019fe659-docsheet`. This is the expected handoff-aging
pattern the previous fresh-eyes audit already noted (§3.2 of that report) —
refresh the header when this audit becomes the handoff.

### 3.6 — "Passed through unchanged" wording vs. the 6-column trim (Nit, doc)

README/INSTRUCTIONS described the raw pipeline as pass-through "unchanged,"
while `process_data.py` drops the six always-empty raw columns (uuid,
Unnamed: 8–11, other links) and keeps `notes`. Cell values are untouched, so
this was only wording.

**RESOLVED 2026-08-09:** README, INSTRUCTIONS, and the `process_data.py`
docstring now state the trim explicitly ("unchanged — cell values are never
modified; the published view trims the six always-empty raw columns").

### 3.7 — Archived fresh-eyes audit mischaracterizes Highlights as "blank-year" (Nit, archive)

`archive/FULL_STACK_AUDIT_2026-08-08_INDEPENDENT_ROOT.md` §7 groups "Volumes +
Highlights + under-investigation" as "the 17 blank-year rows". Highlights
(362–368) have years 2002–2007; their prefix omission is a separate owner
directive ("filename equals title"). No data impact.

**RESOLVED 2026-08-09:** an archival footnote was added to that line
correcting the wording for the record (17 blank-year = 13 Volumes + 4
under-investigation; Highlights carry years from their titles and omit the
prefix per the separate 2026-08-07 owner directive).

### 3.8 — Not findings (verified non-issues)

- `fetch_veritas_catalogue.py` is stdlib-only, so the Map-Veritas workflow
  needs no `pip install` — the missing dependency step is fine.
- CI (`paths-ignore` on the raw CSV) and Update-Spreadsheet (`paths` on the
  raw CSV) cannot race on the same push.
- The `month` "1.0" appearance is a pandas float artifact; CSV and JSON are
  zero-padded.
- The 24 master↔work_families join "conflicts" are the edition-minted rows by
  design.
- CSP, SRI (Tabulator 6.5.2), `.nojekyll`, `.gitignore` (candidate artifacts
  excluded), `.coveragerc` (85% floor) all correct.

---

## 4. Project-setup audit

| Area | Verdict |
|---|---|
| Python env | ✅ pandas 3.0.5 / numpy 2.4.6 / coverage 7.15.4 match `requirements-ci.txt` pins; `requirements*.txt` ranges compatible |
| CI (ci.yml) | ✅ 12 steps: py_compile, 6 `--check` modes, 126 tests, coverage gate, JS syntax, 18 Playwright tests, artifact upload on failure |
| Workflows | ✅ Update Spreadsheet (contents: write) and Map Veritas (read-only + artifact diff, intentional failure on drift) correctly scoped; concurrency groups prevent races |
| Git hygiene | ✅ working tree clean; `.venv/`, `node_modules/`, `.coverage`, `data/veritas_official_products_candidate.csv` + diff correctly ignored; no secrets/tokens in tracked files |
| GitHub state | ✅ `main` HEAD = PR #43 merge; CI + Pages green; no open PRs; one open issue (#18, known) |
| Docs | ✅ README/INSTRUCTIONS counts match reality; superseded banners present on EXTERNAL_AUDIT.md and archive 08-09 audits; 126-test and 91% claims reproduced |
| Repo layout | ✅ 18 root .md files (post-PR #43 slimming), `archive/` and `decisions/` READMEs present, `docs/` self-contained static site |

---

## 5. Recommendations (priority order)

1. ~~Owner ruling: reclassify ledger row 371~~ — **DONE 2026-08-09** (§3.1).
2. ~~Correct the Highlights "out of scope / unmatched" sentence~~ — **DONE
   2026-08-09** (§3.2).
3. ~~Record the Highlights streaming ruling / `-2002-dvd` slug~~ — **DONE
   2026-08-09** in `decisions/HIGHLIGHTS_COMPILATION_DECISIONS.md` (§3.3).
4. ~~Hide fully-empty rows in the Original Spreadsheet view~~ — **DONE
   2026-08-09** with the "Show blank separator rows" toggle (§3.4).
5. ~~Refresh NEXT_AGENT_HANDOFF.md~~ — **DONE 2026-08-09** (§3.5).
6. ~~Clarify the "passed through unchanged" wording~~ — **DONE 2026-08-09**
   (§3.6).
7. ~~Annotate the archived 2026-08-08 audit's "17 blank-year rows (Volumes +
   Highlights + …)" wording~~ — **DONE 2026-08-09** (archival footnote,
   §3.7).

The audit pass itself was read-only; all fixes above were applied afterwards
in the same session (owner-approved) and re-verified: all six `--check` modes
green, 126/126 tests, 91% coverage.
