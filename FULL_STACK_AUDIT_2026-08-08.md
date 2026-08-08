# Full-Stack Audit — 2026-08-08

**Date:** 2026-08-08
**Scope:** entire repo — 9 Python modules, 24 data/*.csv, 20 docs/*.json,
frontend (`docs/index.html` / `app.js` / `style.css`), 3 GitHub Actions
workflows, test suite, and every living root Markdown document.
**Method:** fresh venv install, all checks re-run live, catalogue cross-checked
field-by-field against the committed data + live Veritas API (via page-fetch),
and every count in the living docs verified against
`docs/catalogue-meta.json` and the CSVs.

> Context: this builds on `FULL_STACK_AUDIT_2026-08-07_DEEP.md`. The pipeline
> is deterministic and the previous audit's core verdict (HEALTHY & VERIFIED)
> still holds. This audit is the 2026-08-08 pass: it re-verifies everything and
> reports the **newly found inconsistencies**, ranked by severity.

---

## 1. Re-verification (all re-run live on this branch)

| Check | Result |
|---|---:|
| `python -m unittest discover tests` | **112/112 pass** (README/INSTRUCTIONS still say 110 — see S1) |
| Coverage total / floor module / gate | **91% / 88%** (`build_catalogue_pages.py`) / 85% gate — matches docs |
| `process_data.py --check` | pass (374 raw rows; 8-column trimmed view) |
| `build_research_master.py --check` | pass (365 master; 72 exclusions; 134 overrides; 39 candidates) |
| `build_catalogue_pages.py --check` | pass (365 Everything rows) |
| `reconcile_research_master.py --check` | pass (report current) |
| `map_series_taxonomy.py --check` | pass (186 mappings: 177 approved / 9 rejected / 0 proposed) |
| `sync_inventory_mirrors.py --check` | pass (mirrors match master) |
| `fetch_veritas_catalogue.py --check` | ⚠️ requires live network; TLS-EOF in sandbox (documented trap; offline replay covered by tests; not part of CI) |
| `node --check` on app.js / playwright.config.js / specs | pass |
| Live site (local http server) | index + data + master.json serve 200 |
| Master shape | 365 rows × 24 cols; 309 lecture / 40 book / 8 discussion / 7 highlight / 1 other; no untyped |
| Codes | 281 distinct (lecture/discussion only) |
| Work families | 208 works / 341 approved memberships; work_id coverage 365/365 |
| Relationships | 343 rendered = 336 derived primary + 7 related; 7 series compilations |
| Filename proposal | 365 rows = 365 unique safe = 365 unique display (v4.1 guard) |
| Ledger dispositions | 302 item / 31 blank_separator / 21 series_context / 10 research_note / 5 source_context / 4 duplicate / 1 needs_review (= 374) |

Every count in the README's "Current reviewed catalogue state" paragraph and
`docs/catalogue-meta.json` was cross-checked and **matches the data**.

---

## 2. Catalogue inconsistencies (ranked)

### C1 — Master 265: malformed Veritas product URL (highest severity, live-site visible)

> ✅ **RULED 2026-08-08 (owner approval, Option A):** URL **kept as-is** (it is
> the publisher's own canonical link — verified via live WP-API, no
> clean-slug equivalent exists) and **documented** in the override row +
> ledger `review_reason` + `archive/RULING_PREP_MASTER_265_GOLDEN_WORD_BOOK_SIGNING.md`.
> Also fixed in the same ruling: `format` corrected to `CD` (see C2) and the
> de-listed US Audible audiobook tracked as a manual lead.

Record **265** (`Golden Word Book Signing – Audio`) carries:

```
source_url_veritas = https://veritaspub.com/product/https-veritaspub-com-product-golden-word-book-signing-january-13-2007/
```

- This is the **only** malformed URL in the entire master (24 URL columns × 365
  rows scanned). It has propagated through every derived layer:
  `data/research_master_source_overrides.csv` (row 297, **approved** 2026-08-03,
  evidence_source = the reviewed inventory), `data/veritas_official_products.csv`
  (product 1552, `matched_by_primary_source`), `docs/master.json`,
  `docs/source-overrides.json`, `docs/product-relationships.json`,
  `docs/veritas-products.json`, and the inventory mirror columns.
- **Live verification (2026-08-08):** the publisher's own WP-API confirms the
  mangled string is the *actual stored slug/link* of product 1552
  (`slug: https-veritaspub-com-product-golden-word-book-signing-january-13-2007`).
  No correctly-slugged duplicate exists (API search returns only 1552). So this
  is an **upstream publisher data defect** that the catalogue faithfully
  mirrors — the catalogue itself did not corrupt it, and "official link" is
  technically true.
- **Why it still needs a ruling:** the link is malformed (double
  `product/`-style prefix, dots→dashes), it is inconsistent with every other
  row's URL shape, and it is what visitors click as the primary Veritas link.
  Options: (a) keep + document as publisher-verbatim (add a note + this audit
  reference), (b) swap the primary link to a corrected URL if the publisher
  fixes it upstream (then re-run `sync_inventory_mirrors.py`), or
  (c) report the defect to Veritas. The approved override row should also
  carry the explanation either way.

### C2 — Master 265: `format=audiobook` contradicts the official listing (same record)

> ✅ **RULED 2026-08-08 (owner approval, Option A + audiobook lead):** ledger
> row 297 now sets `proposed_format=CD` / `proposed_format_detail=three CD; 2h56m`;
> master 265 regenerated with `format=CD`, filename `2007-01 - Golden Word Book
> Signing.mp3`; inference rule tightened (CD markers beat the "– Audio" title
> fallback; malformed slugs return blank); 2 new tests (114 total); US Audible
> audiobook (B00KZ1QMX8, de-listed on audible.com) tracked in
> `data/research_manual_leads.csv`. Evidence memo:
> `archive/RULING_PREP_MASTER_265_GOLDEN_WORD_BOOK_SIGNING.md`.

The publisher's own product page for 1552 says **"Three Compact Disc Set"**
(SKU `am_gwbs`, $29.95, 2h56m). Master 265 has `format=audiobook`,
`format_detail=` empty, `notes=` empty. Every other "– Audio"-titled CD
product in the catalogue is correctly carrier-typed with a detail:
products 1792 → 356 (`CD`, "one CD; 67 min"), 1544 → 353 (`CD`, "three CD;
3h45m"), 1661 → 329 (`CD`, "6-CD set (Nightingale-Conant)").

**Root cause (latent defect):** the format-inference rule in
`build_research_master.py`
(`if "audio" in slug or "– audio" in ot or " audio" in ot: return "audiobook"`)
classifies any official title ending in "– Audio" as an audiobook, even when
the carrier is a CD set. It only affects 265 today because the other CD rows
were hand-set through edition/manual promotions — but the rule will misfire
again on any future promotion or backfill with a "– Audio"-titled CD product.

Suggested fix (owner ruling): set 265 `format=CD`, `format_detail` like
"3-CD set", evidence in `notes`; tighten the inference rule to check the
product slug/category/description for CD markers before the "– Audio" fallback
(e.g. only treat as audiobook when the title says "Audio Book"/"Audiobook" or
an Amazon/Audible source is the carrier evidence).

### C3 — `year = "198X"` placeholder: 16 rows, plus codes and filenames

Master rows 233–250 (Office Series lectures) carry `year=198X`
(`year_source: Ledger: recording date 198X`), `catalog_code=LECTURE-198X-001…
016`, and `proposed_filename=198X - Stress.mp4` etc. (16 of the 365 filenames
contain `X`).

- This is an **intentional owner ruling** (2026-08-07: "all 16 Office Series
  lectures standardized to year 198X"), so it is not accidental — but it is an
  inconsistency with the rest of the catalogue and a data-quality hazard:
  - `198X` is not a valid year; it breaks numeric sorting/filtering of the
    Year column in the UI, and `Year-Month` shows "198X" raw.
  - The same "pre-2000 unknown" situation is handled **differently** for the
    13 Volume Series rows: year **blank** with `year_source=Blank: intentional
    pre-2000 (Volume Series)`. Two conventions for the same fact class.
  - `LECTURE-198X-###` codes cannot be sorted/compared as codes, and
    `198X - *.mp4` are not usable file names as-is.
- Suggested direction: pick one convention for "pre-2000, exact year unknown"
  — blank + `year_source` note (Volume-Series style, keeps codes from carrying
  a fake year), or a documented display convention (e.g. "c. 1980s") that is
  still kept out of the code/filename. Needs an owner ruling; both are valid.
  **Ruling-prep memo drafted: `archive/RULING_PREP_YEAR_198X_OFFICE_SERIES.md`
  (recommends Option 2: keep `198X`, document the convention in README, and
  polish the UI — `c. 1980s` display + deterministic year sorter; Option 1 =
  blank the year, which removes 16 codes and is fully specified there too).**

### C4 — `owned` column mixes three states with no documented semantics

> ✅ **FIXED 2026-08-08:** README "Field semantics" now documents the
> vocabulary — `true` = owned, `false` = explicitly not owned, blank = not
> stated (minted editions/programs without a raw ownership marker); the site
> badges render `Owned` / `Not owned` (blank cells stay empty), while exports
> keep the raw `true`/`false`/empty values.

`owned` values across the master: `true` 296, `false` 25, **empty 44**
(highlights, NC/Hay House programs, Veritas edition rows 327–331, etc.).
Empty is used both for "unknown" and (via candidates with blank
`proposed_owned`) "not stated", while `false` is an explicit "not owned".
The frontend renders the raw strings. README defines `owned` nowhere.

Suggested fix: document the vocabulary (e.g. `true` / `false` / empty=unknown)
in README's "Field semantics", and/or render a badge (`Owned` / `Not owned` /
`?`) in the UI like `record_type`. No data change needed if the semantics are
stated — but the current mixed rendering makes "blank" rows look identical to
explicit "false" rows to a visitor.

### C5 — Raw-source defects mirrored verbatim into the published view

> 📋 **PLAN PREPARED 2026-08-08:** `archive/RULING_PREP_RAW_CSV_HYGIENE.md`
> lists the exact 16 cells (3 broken Advaita URLs on lines 28–30, 13
> `2cds each?` tempid annotations on lines 280–292), what NOT to change (the
> `where is B-02?` rows are excluded provenance, `SAT/VOL/OFF` tempids are
> legitimate schemes, line 1 is needed for header=1), and the post-edit
> follow-up (ledger mirrors + master `legacy_tempid` cleanup on 13 rows).
> Owner applies the Google-Sheet edits; recommendation: fix all 16.

The source spreadsheet (and the pass-through **Original Spreadsheet** tab +
`docs/migration-review.json` raw mirrors) still contains:

- **Broken URL** `https://veritaspub.com/product/https://veritaspub.com/product/
  2002-08-advaita-the-way-to-god-through-mind/` on the three Advaita rows
  (LS200208_1/2/3). The ledger **quarantined** these
  (`Product URL has duplicated prefix and is quarantined for correction`) and
  the curated master carries the **corrected** URL — so this is a raw-source
  hygiene item only; the curated catalogue is unaffected. Visitors to the
  Original tab click a broken link.
- **Junk identifier** `2cds each?` in the `tempid` column of 13 raw Satsang
  rows, mirrored verbatim as `legacy_tempid` on masters 251–263. It is a stray
  annotation in an identifier column of the source CSV.

Both are the owner's raw spreadsheet to clean if desired (the pipeline
correctly passes them through unchanged by design).

---

## 3. Project-setup inconsistencies

### S1 — README / INSTRUCTIONS test-count drift (110 vs 112)

> ✅ **FIXED 2026-08-08:** both files now say **112** (`README.md`:
> "112 tests, no browser/network needed"; `INSTRUCTIONS.md`:
> "112 deterministic tests").

- Originally: `README.md` line 53 "110 tests", `INSTRUCTIONS.md` line 173
  "110 deterministic tests" vs the actual **112 tests** (handoff §2/§3 and the
  deep audit already said 112; the two extra tests are the filename-uniqueness
  guard added 2026-08-07).

### S2 — CI pins Node 20 (EOL 2026-04)

> ✅ **APPLIED 2026-08-08 by owner** — commit `406116f` on `main`
> ("Update Node.js version from 20 to 22 in CI workflow"); `origin/main`
> `ci.yml` now pins `node-version: "22"` (verified via fetch). The prepared
> snippet in `archive/UNBLOCK_INSTRUCTIONS.md` ("Bump the CI Node runtime
> 20 → 22") served as the change plan. Nothing outstanding here.

`.github/workflows/ci.yml` had pinned `node-version: "20"` (EOL 2026-04) —
handoff item K. Also note the CI comment says "the six generator --check
modes" — there are six in the workflow and they match the scripts; the
wording is fine, but `fetch_veritas_catalogue --check` is intentionally not
run in CI (needs live network).

### S3 — Handoff §5 binding-rules text is stale on the discovery lane

> ✅ **FIXED 2026-08-08:** §5 now states the discovery-triage lane was ruled
> empty on 2026-08-07 (3 NC programs promoted to masters 369–371, Map poster
> 1560 excluded) and that no free-text `audio` remains anywhere.

Originally: §5 said "the unreviewed discovery-triage lane
(`data/official_discovery_queue.csv`, 4 NC rows) still carries free-text
`audio` pending an owner ruling" while the queue is **0 rows** (meta
`official_discovery_candidates: 0`).

### S4 — Stale comment in the browser spec

> ✅ **FIXED 2026-08-08:** `tests/csv-export.spec.js` comment now says
> "365 curated masters".

Originally: "the Everything view holds 366 curated masters" — the master is
**365** (309 merged into 221; 246 excluded). The test is data-driven so it
still passed; only the comment was stale.

### S5 — Sandbox/environment notes (not repo defects, confirmed again)

- `pip` refuses system installs (PEP 668) → venv required (documented).
- veritaspub.com unreachable via urllib (TLS EOF) → live `--check` fails in
  the sandbox; page-fetch tool reaches the WP-API fine (used for C1/C2
  evidence).
- Chromium/Playwright cannot be installed in the sandbox → browser specs run
  only in CI.

---

## 4. What verified clean (spot-checked, no action needed)

- All `docs/*.json` are in sync with their inputs (all six `--check` modes
  green on this branch).
- Review inputs are internally consistent: 39/39 manual candidates promoted,
  24/24 edition promotions, 341/341 work-family memberships approved, 7/7
  related-material relationships, 7/7 compilations, 10/10 Veritas decisions,
  134/134 overrides approved, 72/72 exclusions with documented dispositions.
- No duplicate catalogue codes, no duplicate UUIDs, no duplicate
  `proposed_filename`s, no invalid months (all `01`–`12`), no deprecated
  `audio`/`video` item types in the master, all rows have `legacy_title`,
  `year_source`, and `proposed_filename`.
- The international sheet (38 rows) = 36-row queue + 2 Spanish Audible
  listings — intentional per code comment, not drift.
- `docs/catalogue-meta.json` matches every count in README's "Current reviewed
  catalogue state".
- CI workflow, package.json, playwright.config.js, .coveragerc and .gitignore
  are coherent with the pipeline.

---

## 5. Recommended next steps (in suggested order)

1. ✅ **C1/C2 (master 265) — RULED and APPLIED 2026-08-08** (Option A +
   audiobook lead): URL kept & documented; `format=CD` (`three CD; 2h56m`);
   filename `.mp3`; inference rule hardened + 2 new tests (114 total); de-listed
   US Audible audiobook tracked as a manual lead. All six `--check` modes and
   the full suite green. See `archive/RULING_PREP_MASTER_265_GOLDEN_WORD_BOOK_SIGNING.md`.
2. **Owner ruling on C3:** one convention for pre-2000 unknown years (blank vs
   "198X"), then update codes/filenames consistently.
3. ✅ **Doc drifts (S1, S3, S4) — FIXED 2026-08-08:** README/INSTRUCTIONS
   "110 tests" → 112, handoff §5 discovery-lane rule corrected, spec comment
   "366" → "365".
4. ✅ **C4 (`owned` semantics) — FIXED 2026-08-08:** README field semantics
   document `true`/`false`/blank; UI badges now read `Owned` / `Not owned`.
5. **S2 (Node 20 → 22):** ✅ snippet prepared 2026-08-08 in
   `archive/UNBLOCK_INSTRUCTIONS.md` — owner applies it in the web editor.
6. **C5 (raw CSV hygiene):** 📋 plan prepared 2026-08-08 in
   `archive/RULING_PREP_RAW_CSV_HYGIENE.md` — owner applies the 16 cell
   fixes in the Google Sheet; agent follow-up then cleans the ledger mirrors
   and the 13 `legacy_tempid` cells.
4. **C4:** document `owned` semantics in README (and optionally badge it).
5. **S2 (Node 20 → 22):** owner applies the workflow snippet
   (`archive/UNBLOCK_INSTRUCTIONS.md`); I can prepare an updated snippet.
6. **C5:** optionally clean the raw CSV (Advaita URLs, `2cds each?` tempid)
   in the owner's Google Sheet; the curated layer is already clean.

No pipeline-breaking defect found; all six `--check` modes and the full test
suite (114) are green on this branch.

---

## 6. Deeper data pass (2026-08-08, follow-up QA)

A targeted cross-field pass beyond the headline audit — edition parity,
taxonomy, Satsang alignment, work-family naming, code/date consistency.
**Verified clean:** year_source↔year agreement; catalogue-code sequences
(no gaps/duplicates per year); Veritas month backfill year-match rule;
approved taxonomy mappings vs master series; Satsang title-month vs `month`;
edition rows (320–343) all carry valid work_ids; no duplicate carriers within
a work (non-part rows); zero token-overlap between family canonical titles and
member titles; `owned=false` rows are intentionally catalogued reference
records (raw `WE HAVE? = ❌`).

**New finding DP-1 — work families split multi-part lectures into per-part
works (27 rows, 11 groups).** README states DVD lecture parts are "grouped
under one work", and D6a does that for e.g. Causality — but 11 multi-part
groups (Volume I–V, Become That Which You Are, Love is a Way of Being, The
Presence of Spiritual Awareness, Mind Heart and Service, Spiritual Will,
Verification of Spiritual Realities) have each part in its **own** work_id,
keyed to raw titles that embedded `(Part 1)`/`PART1` markers (the 2026-08-07
title cleanup removed those markers from public titles but never re-keyed the
families; the families' own evidence notes say "part rows of one lecture").
Worst case (DP-2): master **202** (Volume I Part 1) is a member of
`w-power-vs-force`, the **book** work (286) — its evidence note flags
"REQUIRES RULING (see 286)" and the 2026-08-07 product rulings never
re-adjudicated it. **RULED 2026-08-08 (owner approval): merged** — the 11 part
groups now share 11 works (208 → **193** works, 341 memberships unchanged,
coverage 365/365; 202 moved into `w-volume-i-power-vs-force-muscle-testing`,
`w-power-vs-force` keeps only the book 286; 26 PART-marker canonical titles
cleaned; 27 `work_id` cells re-synced in the filename proposal). Memo:
`archive/RULING_PREP_WORK_FAMILY_PART_MERGE.md`; all six `--check` modes,
114 tests, and node checks green after regenerating.

## 7. Deeper data pass QA-2 (2026-08-08, relationships / mirrors / provenance)

- **Product relationships: clean.** 336 masters carry `source_url_veritas`, and
  every URL exists in the reviewed inventory (exact-match validation); 182
  inventory products cover the 336 rows (multi-part lectures share product
  URLs — expected). 7 `related_material` rows: no unknown masters, no
  duplicate (master, product) pairs, and none duplicates a master's primary
  product. 343 rendered relationships consistent with the docs.
- **Inventory mirror columns: 0 errors** (`normalized_title_match_count` == ID
  count; `| `-joined titles match master titles; excluded rows carry no
  matches) — `sync_inventory_mirrors.py` state is exact.
- **Series compilations: by design.** All 7 are series-level
  (`compilation_draws_from_series` per the binding rule "series-level for
  annual Highlights"); `included_lecture_count` reflects the official product
  description (e.g. "Highlights of the 2002 Lectures 1-6" = 6), not the total
  master rows in that series+year — no defect.
- **Candidate provenance: clean (cosmetic note).** All 53 candidate-origin
  masters resolve against the promotion registries; the master stores the
  `candidate:` prefix while `manual_candidate_promotions.csv` /
  `edition_promotions.csv` store bare keys — a documented, 100%-resolvable
  representational difference (the builder strips the prefix). Cosmetic only;
  no change proposed.
- **Titles vs legacy_titles:** 265/365 rows differ — expected, since curated
  titles strip raw date/part noise ("(Jan 2002) DVD01") while `legacy_title`
  always preserves the verbatim raw text.
- **Masters 369–372** (NC/Hay House programs): series/format/URLs consistent
  (Nightingale-Conant series + `nightingale.com` URLs for 369/370, Hay House
  for 372, audiobook carriers, `owned` blank per the documented C4 semantics).
- **Live-site spot check:** `docs/master.json` serves 365 rows with the merged
  work_ids live (215/217 → `w-become-that-which-you-are-june-2004`, 202 →
  `w-volume-i-power-vs-force-muscle-testing`); `docs/data.json` 374 rows × 8
  columns intact.

**QA-2 verdict: no new defects.** The only open data-quality items remain C5
(owner's raw CSV hygiene) and the cosmetic `candidate:` prefix convention.

## 8. Deeper data pass QA-3 (2026-08-08, docs references + JSON schema)

- **JSON↔CSV schema sweep: fully consistent** — every `docs/*.json` row count
  matches its source CSV (26/29/191/39/2/72/134/10/7; product-relationships
  343 = 336 derived + 7 stored), and every source-CSV column is present in its
  published JSON.
- **Cross-reference sweep (64 flags, 61 false positives):** most flags are
  intentional glob notation (`docs/*.json`, `data/*.csv`), historical mentions
  of retired artifacts properly framed as stopped/deleted (`docs/meta.json`,
  `data/year_provenance.csv`), or proposed-but-never-created files in
  superseded archive proposals. **3 genuine 404s fixed:** two archive docs
  linked root files without the `../` prefix
  (`archive/VERITAS_ARTIFACT_REVIEW.md` → `SERIES_TAXONOMY_MAPPING.md`,
  `archive/VERITAS_PRODUCT_MAPPING.md` → `decisions/…`) and one non-path
  wording in `archive/RULING_PREP_WORK_FAMILY_PART_MERGE.md` (`docs/work`).

## 9. Deeper data pass QA-4 (2026-08-08, Satsang/CD parity + edge classes)

- **Satsang series: no duplicates.** All 25 Satsang/2011 Q&A rows occupy
  distinct year-month slots (2006 set 344–349, raw-ledger set 251–263,
  promoted monthlies 350 Jul-2008 / 351 Jun-2010 / 352 Sep-2010); 25 distinct
  Veritas slugs; every CD row carries a code; the promoted monthlies' blank
  `owned` vs the raw rows' `false` matches the documented C4 semantics.
- **Cosmetic caveat (documented, no change proposed):** catalogue codes are
  minted in ledger/candidate order, not chronologically — e.g. Satsang
  Sep-2008 = `LECTURE-2008-023` sorts before Jul-2008 = `-024`, and Nov-2010 =
  `-008` before Jun/Sep-2010 = `-009/-010`. Codes are stable identifiers
  (never renumber); re-sorting would only matter if the owner wants
  chronological codes, which would churn 4 rows for pure cosmetics.
- **Edge classes consistent:** the single `other` row is master 371 (OM —
  mantra recording, `Media Miscellaneous`, audiobook, documented promotion
  note); all 8 `discussion` rows are `streaming` in `Discussion Series`;
  highlights are 7 streaming rows in `Lecture Highlights`.

## 10. Deeper data pass QA-5 (2026-08-08, frontend↔data contract)

Frontend↔data contract sweep (tabs ↔ VIEWS map, view files, column presets,
record-type labels): **everything matches except one gap** —

- Tabs (15) ↔ VIEWS keys (15) ↔ JSON files: all present, all files exist.
- Master column preset: every priority field exists in `master.json`
  (`edition`/`year_month` are derived merges).
- **Finding (contract gap):** the README promises *"the master exposes
  `legacy_title` … so the verbatim raw spreadsheet text is always
  exportable"* and the owner's 2026-08-07 visitor-first directive hid
  `legacy_title` and `proposed_filename(_display)` behind the **Expert
  columns** toggle — but the published Everything sheet
  (`docs/master.json`, built from `EVERYTHING_FIELDS` in
  `build_catalogue_pages.py`) **does not carry `legacy_title`,
  `proposed_filename_display`, or `candidate_key`** (only the master CSV
  does). Net effect: the Expert toggle has two dead entries
  (`legacy_title`, `proposed_filename_display`) and the Everything CSV export
  cannot include the verbatim raw title — the README's "always exportable"
  claim holds only via the separate Original Spreadsheet tab.
  Options: (a) restore the two fields to the Everything view; or
  (b) declare them unpublished. **RESOLVED 2026-08-08 (owner approval, option
  (a))**: `legacy_title` added to `EVERYTHING_FIELDS` and
  `proposed_filename_display` derived from the filename-proposal sheet in
  `build_catalogue_pages.py`; `docs/master.json` regenerated (365 rows, now
  carrying both, e.g. 265 legacy `Audio 27. Golden Word Book Signing – Audio`
  and display `… [1/3].mp4`); the README's "verbatim raw text always
  exportable" claim now holds from the Everything tab and the Expert toggle
  entries are live. All six `--check` modes, 114 tests, 91% coverage, and
  node checks green.
