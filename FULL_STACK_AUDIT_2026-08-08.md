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

- `README.md` line 53: "110 tests, no browser/network needed"
- `INSTRUCTIONS.md` line 173: "110 deterministic tests"
- Actual: **112 tests** (handoff §2/§3 and the deep audit already say 112; the
  two extra tests were the filename-uniqueness guard added 2026-08-07).

One-line fix: update both files to "112".

### S2 — CI pins Node 20 (EOL 2026-04)

`.github/workflows/ci.yml` uses `node-version: "20"`. Handoff documents this
as owner action item K (the Arena app cannot push workflow-file changes;
prepared snippet lives in `archive/UNBLOCK_INSTRUCTIONS.md`). Also note the CI
comment says "the six generator --check modes" — there are six in the workflow
and they match the scripts; the wording is fine, but `fetch_veritas_catalogue
--check` is intentionally not run in CI (needs live network).

### S3 — Handoff §5 binding-rules text is stale on the discovery lane

`NEXT_AGENT_HANDOFF.md` §5 still says "only the unreviewed discovery-triage
lane (`data/official_discovery_queue.csv`, 4 NC rows) still carries free-text
`audio` pending an owner ruling." The queue is now **0 rows** (all ruled
2026-08-07; meta `official_discovery_candidates: 0`). The §6 session log
records the rulings, but the binding-rules section should be corrected so the
next agent doesn't chase 4 phantom rows.

### S4 — Stale comment in the browser spec

`tests/csv-export.spec.js` line 88: "the Everything view holds 366 curated
masters" — the master is **365** (309 merged into 221; 246 excluded). The test
is data-driven so it still passes; only the comment is stale.

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
3. **Quick doc fixes (S1, S3, S4):** 112 tests, empty discovery lane,
   "365 masters" comment — 5-minute edits I can do on request.
4. **C4:** document `owned` semantics in README (and optionally badge it).
5. **S2 (Node 20 → 22):** owner applies the workflow snippet
   (`archive/UNBLOCK_INSTRUCTIONS.md`); I can prepare an updated snippet.
6. **C5:** optionally clean the raw CSV (Advaita URLs, `2cds each?` tempid)
   in the owner's Google Sheet; the curated layer is already clean.

No pipeline-breaking defect found; all six `--check` modes and the full test
suite (114) are green on this branch.
