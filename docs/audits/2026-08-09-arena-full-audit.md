# Full-Stack & Catalogue Audit — 2026-08-09 (Arena, fresh pass)
> **Status correction (2026-08-09): Historical checkpoint, not current frontend/deployment truth.** PR #54 found that all 70 custom Tabulator rules used the dead descendant root `#spreadsheet .tabulator`; Tabulator attaches `.tabulator` to `#spreadsheet` itself. Current evidence, test counts, CI/Pages findings, and acceptance status live in [`2026-08-09-end-user-row-delivery-postmortem.md`](2026-08-09-end-user-row-delivery-postmortem.md). Point-in-time data findings below remain historical evidence.


**Repo:** 56eli/docsheet · **Branch audited:** `arena/019fe6c1-docsheet` (worktree at `49c91c4`, main HEAD = PR #45)
**Auditor:** Arena.ai Agent Mode — expert Full-Stack Developer / Data Engineer pass
**Date:** 2026-08-09
**Method:** independent pandas/stdlib probes bypassing the project's own validators; every `--check` mode; full unit suite + coverage; static frontend review; doc-vs-state cross-checks.

> This is an independent checkpoint audit. It verifies the state declared by
> `FULL_STACK_AUDIT_2026-08-09_ARENA_EXPERT.md` / `_DEEP_DIVE.md` / `_FULL.md`
> and reports only what is **new or unrecorded** in those documents. Prior
> findings (D-01…D-10, B-01…B-03, I-01, DOC-01…DOC-05, the seven expert-pass
> fixes) are not re-reported unless the current state contradicts them.

---

## 1. Executive verdict

The catalogue is **data-clean and internally consistent**. Every documented
count was reproduced exactly from the raw files (362 masters, 278 codes, 75
exclusions, 134 overrides, 39 promotions, 340 relationships, 7 compilations,
191 works, 191 products, 10 UUID gaps), all six `--check` modes pass, the
126-test suite passes, and coverage is 91% (floor 85%). No data-loss,
duplication, or cross-field contradiction was found in the curated master.

One small data inconsistency and four stale-documentation items are new in
this pass. All are low severity; none affect the generated site's correctness.

## 2. Commands / checks run

| Check | Result |
|---|---|
| `process_data.py --check` | ✅ docs/data.json current (374 rows, 7 view cols) |
| `reconcile_research_master.py --check` | ✅ report current |
| `build_research_master.py --check` | ✅ 362 items; 75 excluded; 134 overrides; 39 candidates |
| `build_catalogue_pages.py --check` | ✅ 362 Everything rows |
| `map_series_taxonomy.py --check` | ✅ 186 mappings; 0 queued |
| `sync_inventory_mirrors.py --check` | ✅ mirrors match |
| `python -m unittest discover tests` | ✅ Ran 126, OK |
| `coverage run … && coverage report` | ✅ 91% (TOTAL 2072 stmts; lowest module 88%) |
| `node --check` (app.js + all 5 spec files) | ✅ clean |
| Static serve of `docs/` (8 assets) | ✅ all 200 |
| `npm ci` | ✅ (@playwright/test 1.62.1 == package-lock) |
| Playwright browser install | ❌ CDN blocked in sandbox (known; CI is the verification point) |
| Live Veritas API refresh | ❌ TLS blocked in sandbox (CI workflow `map_veritas_catalogue.yml` is the verification point) |

## 3. Independent data probes (all pass)

~30 probes beyond the project's own validators, each bypassing project code:

| Probe | Result |
|---|---|
| `item_type` × `format` matrix | ✅ sane: books only `book`/`audiobook`; discussions/highlights `streaming`; no legacy `audio`/`video` |
| Catalogue codes | ✅ 278 unique, all `LECTURE-YYYY-NNN`/`DISCUSSION-YYYY-NNN` (198X codes documented); no code↔year mismatch |
| Code-less lecture/discussion rows (36) | ✅ all documented classes: 4 manual candidates + 16 edition rows + 16 code-minted 198X Office rows excluded from this set by year; every one has a labelled `year_source` |
| `year`/`month` | ✅ all 4-digit or `198X`; months 1–12; 0 month-without-year; 33 lectures with year but no month are all part/streaming rows without a dated Veritas slug (documented) |
| `year_source` | ✅ 0 rows with year but no source; 17 blank-year rows all labelled (13 Volume + 4 under investigation) |
| `owned` vs raw `WE HAVE?` | ✅ 299/299 traced rows match exactly (✅→true, ❌→false, blank→blank); 63 candidate-minted rows have no raw row (all with `candidate_key`) |
| `legacy_tempid` LS-year vs `year` | ✅ 0 mismatches (the old 156-row defect class is fully resolved) |
| Placeholder/TODO text | ✅ 0 rows with `???`/`TODO`/`⚠`/`WHAT IS THIS` remnants in master |
| Duplicate `proposed_filename` | ✅ 0 (223 part-group filenames all distinct via `[n-m]`) |
| Duplicate `legacy_tempid` | ✅ 0 |
| UUIDs | ✅ range 1–372, exactly 10 gaps `{225,226,227,246,249,264,281,284,302,309}`, no ids > 372 |
| Master → Veritas inventory | ✅ all 333 `source_url_veritas` values exist in the 191-product inventory and every product lists the matching master UUID |
| Inventory → master | ✅ all 333 UUID references resolve to masters whose primary URL equals the product URL; 5 unlinked products are all `excluded_related_material` with reasons |
| Mirror invariant | ✅ `normalized_title_match_count == len(matched_master_uuids)` on all 191 rows |
| CSV↔JSON parity | ✅ 13 direct pairs exact (362/374/75/134/39/2/5/191/340/7/29/26/38/4 in `catalogue-meta.json` all verified) |
| Pass-through fidelity (`docs/data.json` vs raw CSV) | ✅ 0 cell diffs across 374×7 |
| `candidate_key` convention | ✅ 63 master rows all `candidate:`-prefixed; 39+24 promotion-registry rows all bare |
| Work-family coverage | ✅ 338 + 24 = 362/362, 0 overlap, 191 distinct works; every master `work_id` present in inputs |
| Series taxonomy | ✅ master series == `mapped_series` for all 177 approved mappings; 0 queued |
| Scoreboard math | ✅ weighted avg 655/83 = 7.9; gate fail state reproduced |
| Six always-empty raw columns | ✅ verified empty in source (`uuid`, `Unnamed: 8–11`, `other links`) |

## 4. New findings

> **Fix status (same session, owner-approved):** F-01 and F-02–F-04 were all
> fixed on this branch after the audit — see
> `data/international_discovery_queue.csv` (market corrected),
> `FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md` (362), `FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md`
> (7 view columns), `.scoreboard/history.md` / `.scoreboard/manual-workflow-edits.md` /
> `docs/audits/2026-08-09-baseline.md` (26 specs). All six `--check` modes and
> the 126-test suite pass after the fix.

### F-01 (data, low) — `market='Spanish'` in the international queue
`data/international_discovery_queue.csv` rows 36–37 (the two Spanish-language
Audible audiobooks, `Disolver el ego`, `El nivel más alto de iluminación`)
carry `market=Spanish`. Every other row uses a country/region in `market`
(Spain, France, Brazil, Germany, Italy, Canada (French)); `Spanish` is a
language value in a country field (their `language` column is also
`Spanish`). The two rows arrived with the B-01 fix (hardcoded
`build_catalogue_pages.py` entries moved to the queue), and the value was
copied over. Master data is unaffected — this is a review-queue input shown
in the International Editions sheet.

Suggested fix: set `market` to the Audible marketplace country (both URLs are
`audible.com`, so `United States` fits the file's country convention), or
define a controlled vocabulary for `market` and validate it in
`build_catalogue_pages.py` (the same pattern already exists for
`review_status` values).

### F-02 (docs, low) — stale "365" in `FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md`
Line 74 says: *"Current counts: 365 total; all 365 safe names and all 365
display names are unique"* — but the doc's own v4.1 amendment (line 77,
2026-08-08 D-01 follow-up) and the live file both say **362**. The paragraph
was not updated when the D-01 collapse retired masters 225/226/227. A reader
hitting line 74 sees an internally contradictory document.

### F-03 (docs, low) — stale "8 view columns" in the declared-current audit
`FULL_STACK_AUDIT_2026-08-09_ARENA_DEEP_DIVE.md` line 25 (verification
matrix) records *"374 raw rows, 8 view columns"*. The current pipeline trims
six always-empty columns and publishes **7** view columns (Unnamed: 11 was
dropped; the `_FULL.md` extension correctly says 7). Since `_DEEP_DIVE.md` is
presented as declared-current, this cell should read 7.

### F-04 (scoreboard docs, low) — stale "19 browser specs" ×2
- `.scoreboard/history.md` (tests row, 2026-08-09 baseline): *"19 browser specs via CI"*
- `.scoreboard/manual-workflow-edits.md` (CI line): *"19 browser specs"*

The suite is **26** specs today (`presentation-ux.spec.js` +7 and
`blank-rows.spec.js` +1 landed after those entries were written).
`.scoreboard/agent-handoff.md` and `SCOREBOARD.md` already say 26 — the two
files above contradict them. (Cosmetic; the CI workflow itself runs all
`tests/*.spec.js` and needs no change.)

## 4b. Addendum — REVISION1 ODS owner revision (same session, after the audit)

The owner uploaded `hawkins-everything-REVISION1.ods` (colour-coded
expert-columns export) and approved applying it as the change authority:
58 filename edits (unified `OTR - ` prefix, Office `A-01…B-06` codes,
`DISCUSSION - ` prefix, year fixes on 356–358, completed uuid 312),
notes → `FRAN GRACE` on 315, year data changes (356/358 cleared, 357 → 2003),
and the colour-group block order for the Everything view + CSV export
(lectures → discussion → satsang → on-the-road → volumes → office → books →
transcription → media-misc → undecided → Fran Grace last). Implemented via new
reviewed inputs (`data/master_year_overrides.csv`,
`data/master_notes_overrides.csv`, `data/catalogue_display_order.csv`) with
validators in `build_research_master.py` / `build_catalogue_pages.py`; the ODS
is committed at `review/hawkins-everything-REVISION1.ods`. Suite 126 → 132,
coverage 90%, all six `--check` green.

## 5. Observations (no action required)

1. **work_id slugs (25/191) are exactly 42 chars, truncated mid-word**
   (`w-devotion-the-way-to-god-through-the-hear`, `w-a-07-office-series-worry-fear-and-anxiet`,
   `w-the-levels-of-consciousness-subjective-s`). This is the known I-01
   "by design" divergence, but the **cap value (42) and the mid-word
   truncation rule are documented nowhere**. Consider one line in
   `EDITION_MODEL_PROPOSAL.md` or the D6a decision record so future
   reviewers don't "fix" approved IDs.
2. **The public Original Spreadsheet tab shows personal Discord channel
   links and private notes verbatim** (rows 279/373 notes: `BARRET?`,
   `SETH HAS IT`, `my pdfs are trash`) — by design pass-through and already
   documented (D-10). Flag for the owner only: the repo and Pages site are
   public, so these are visible to anyone.
3. **The raw sheet's `format` column is entirely empty**, so the Original
   Spreadsheet tab renders an empty Format column while the curated views
   are fully populated (formats come from the ledger). By design; a
   first-time visitor may read it as a bug.
4. **7 publisher-prospecting rows in the international queue** have `market`
   but no `candidate_title`/`language` — intentional scaffolding, but worth
   a column-level note so they aren't mistaken for products.

## 6. What the audit could NOT verify (environment limits)

- Browser e2e suite (26 specs) — Playwright CDN blocked in sandbox; CI is
  green per `gh run list` history and the specs were reviewed statically.
- Live Veritas API inventory freshness — TLS blocked; the
  `map_veritas_catalogue.yml` workflow is the standing refresh mechanism.
- GitHub Pages rendering — unreachable from the sandbox; deployment status
  was previously verified via Actions.

## 7. Scoreboard impact

No AI score changes are proposed: this pass reproduced every aspect's
evidence (tests 9, content quality 9, maintainability 7, etc.) and found no
defect that changes a rating. The F-02…F-04 doc-drift items would normally
land under `repo_organization`/`auditability` evidence, but they are too
small to move those scores. The owner's user scores (presentation 5, UX 5,
content 7, maintainability 6) remain the effective drivers of priority.
