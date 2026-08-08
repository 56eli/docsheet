# Full-Stack Audit — 2026-08-08 (Independent pass, branch `arena/019fe11d-docsheet`)

**Date:** 2026-08-08
**Auditor:** independent full-stack / data-engineering pass on top of
`FULL_STACK_AUDIT_2026-08-08.md` and the `arena/019fe0ef-docsheet` follow-up.
**Method:** fresh venv (`Python 3.11`, `Node 22`), all six `--check` modes, the
115-test suite, coverage, JS syntax, plus independent cross-field sweeps over
every CSV/JSON and the living docs. Nothing was taken on trust from the prior
audits — every count below was recomputed from the committed data.

---

## 1. Re-verification (re-run live)

| Check | Result |
|---|---:|
| `process_data.py --check` | ✅ pass (374 raw rows; 8-col trimmed view) |
| `build_research_master.py --check` | ✅ pass (365 master; 72 exclusions; 131 overrides; 39 candidates) |
| `build_catalogue_pages.py --check` | ✅ pass (365 Everything rows) |
| `reconcile_research_master.py --check` | ✅ pass |
| `map_series_taxonomy.py --check` | ✅ pass (186 mappings; 177 approved / 9 rejected / 0 queued) |
| `sync_inventory_mirrors.py --check` | ✅ pass |
| `unittest discover tests` | ✅ **115/115 pass** (3.2s) |
| coverage | ✅ **90% total**, floor modules 88% (gate 85%) |
| `node --check` (app.js, playwright.config.js, both specs) | ✅ pass |
| CSP inline-script hash | ✅ matches computed sha256 |
| Master shape | 365 × 24 cols; 309 lecture / 40 book / 8 discussion / 7 highlight / 1 other |
| Duplicate UUIDs / codes / filenames | 0 / 0 / 0 |
| Work-family coverage | 365/365 `work_id` non-empty (341 from `work_families.csv` + 24 from `edition_promotions.csv`) |
| Streaming URLs | 36/36 resolve to a primary master and match `reference_url_1` exactly |
| Raw↔ledger mirrors | 0 mismatches across 8 mirrored columns |
| Living-doc markdown links | 0 broken |

**Overall verdict:** the pipeline is healthy, deterministic, and well-tested.
The prior audits' findings (C1–C5, DP-1/2/3, QA-2…7, S1–S5) are genuinely
resolved. One **new catalogue inconsistency** and a handful of **setup/doc
drifts** were found (below); none breaks the build, but D-1 is visible on the
live **Veritas Decisions** sheet.

---

## 2. New catalogue inconsistency

### D-1 — Stale Veritas decision row for product 50491 (HIGH — live-sheet visible, contradicts the inventory and master)

**The contradiction:**

- `data/veritas_official_products.csv` (and `docs/veritas-products.json`) row
  for product **50491** *How to Live Your Life Like A Prayer (2012)* says:
  `mapping_status = matched_by_primary_source`, `matched_master_uuids = 278`,
  with the note *"Remapped 2026-08-07: was matched_by_title to master 121;
  this listing is the 2012 Discussion Series talk (master 278)…"*
- Master **278** *How to Live Your Life Like A Prayer* (discussion, 2012)
  carries `source_url_veritas = …/how-to-live-your-life-like-a-prayer-2/`,
  which is exactly product 50491's URL — a correct primary match.
- **But** `data/veritas_mapping_decisions.csv` row 6 still says:
  `50491, matched_by_title, 121, "Live Your Life Like a Prayer"`, and that row
  is published verbatim in `docs/veritas-mapping-decisions.json`.

So the same product is shown to reviewers as:
- **primary source of master 278** on the *Veritas Products* / *Product
  Relationships* sheets (correct — relationship id `rel-veritas-50491-278`),
  **and**
- a non-primary title match to the **wrong master 121** on the *Veritas
  Decisions* sheet (stale).

**Why the tests don't catch it:** `apply_mapping_decisions()` in
`fetch_veritas_catalogue.py` **overwrites** deterministic matching with the
overlay. I re-ran `build_inventory_rows()` against the committed master +
inventory: deterministically 50491 derives `matched_by_primary_source → 278`,
then the stale overlay flips it back to `matched_by_title → 121`. The committed
inventory was hand-corrected to 278 (which is why all six `--check` modes and
`sync_inventory_mirrors.py` pass), but the overlay row was never removed. The
2026-08-07 handoff and `tests/test_pipeline.py:930` explicitly say the old
`rel-veritas-50491-121` row "was removed" — that removal happened in
`product_relationships.csv` but **not** in `veritas_mapping_decisions.csv`.

**Concrete consequences:**
1. `fetch_veritas_catalogue.py --check` against the current master would report
   a diff (deterministic 278 vs overlay-forced 121), i.e. the next Map Veritas
   workflow run would fail on this product even with no upstream change —
   exactly the false "review event" the overlay is meant to prevent.
2. A reviewer reading the **Veritas Decisions** sheet is told product 50491 is
   a non-primary match to master 121 — the opposite of the truth.

**Fix (owner-approved data change, no code needed):** delete the 50491 row from
`data/veritas_mapping_decisions.csv` (primary matches need no overlay row, per
the documented rule — same precedent as the 50411/1542 removal on 2026-08-07),
regenerate `docs/veritas-mapping-decisions.json` and `docs/catalogue-meta.json`
via `build_catalogue_pages.py`, then re-run all checks. Overlay count moves
10 → 9 and `approved_veritas_mapping_decisions` in `catalogue-meta.json`
follows.

I verified no other decision row is stale: the other four `matched_by_title` /
`matched_by_normalized_title` rows (53062→300, 50398→289, 50378→291,
50432→247) are genuinely non-primary (the master's primary URL is a different
product), and all five `excluded_related_material` rows are consistent.

---

## 3. Project-setup / documentation inconsistencies

### D-2 — `decisions/VERITAS_MAPPING_DECISIONS.md` is stale (MEDIUM)

The "Current seed" section says the overlay contains **18** decisions ("7
annual-Highlights compilation products, 4 excluded related products, and 7
non-primary master associations") and describes a "2026-08-04 reduction (35 →
18)". The committed file has **10** rows: 5 `excluded_related_material`,
4 non-primary matches (3 `matched_by_title` + 1 `matched_by_normalized_title`),
and the one stale 50491 row from D-1. The Highlights suppression rows were
lifted on 2026-08-07 and the 50411/1542 rows removed — the doc was never
updated. After the D-1 fix it should read **9** (5 excluded + 4 non-primary).

### D-3 — "15 tabs" / "2 spec files" drift in `NEXT_AGENT_HANDOFF.md` (LOW)

- Line 245: *"Widen browser tests: all **15 tabs**, column chooser, drawer,
  dark mode."* The live site now has **19** tabs (the redesign added Veritas /
  Hay House / Audible Products and Filename Proposal as first-class tabs;
  `docs/index.html` has 19 `dataset-tab` buttons and `app.js` has 19 VIEWS
  keys — I verified they match 1:1). This is a backlog bullet, not a live
  claim, but it is stale.
- The handoff consistently says "2 spec files / 9 tests", which is correct
  (`column-layout.spec.js` has 4, `csv-export.spec.js` has 5).

### D-4 — CI does not syntax-check `tests/column-layout.spec.js` (LOW — coverage gap)

`.github/workflows/ci.yml` "Check JavaScript syntax" step runs `node --check`
on `docs/app.js`, `playwright.config.js`, and `tests/csv-export.spec.js`, but
**not** `tests/column-layout.spec.js`. The handoff §2 says local verification
should cover "every `tests/*.spec.js`", and the file is real JS — a syntax
error there would only surface at the Playwright step. Suggested:

```bash
for spec in tests/*.spec.js; do node --check "$spec"; done
```

(The workflow file is owner-managed — the Arena app cannot push
`.github/workflows/*` — so this is a snippet for the owner to apply, like the
earlier Node 22 bump.)

### D-5 — `NEXT_AGENT_HANDOFF.md` §6 P1 "Edition model" paragraph is stale (LOW)

The block still says *"Master **358 rows** (307 lecture / 40 book / 10
discussion / 1 untyped)… 201 works / 334 members… overrides 127… relationships
336… Everything 378"*. The committed state (and §3 of the same handoff) is
**365 masters / 191 works / 341 memberships / 131 overrides / 343
relationships / Everything 365**. The §3 table is current; the §6 paragraph
was superseded by the 2026-08-07/08 rulings and reads as a half-updated
proposal status rather than current truth.

---

## 4. Items reviewed and confirmed clean

To save the next pass, these were independently re-checked and need no action:

- **Identifiers:** 0 duplicate UUIDs, 0 duplicate catalogue codes, 0 duplicate
  `proposed_filename` (v4.1 global-uniqueness guard holds), all 281 codes match
  `^(LECTURE|DISCUSSION)-\d{4}-\d{3}$` except the 16 intentional
  `LECTURE-198X-###` Office Series codes.
- **Code/type rule:** no book carries a code; the 36 lectures/discussions
  without a code are exactly the 17 pre-2000/under-investigation rows (blank
  year) and the 19 candidate/edition rows whose `proposed_year` was blank at
  minting time (4 manual candidates 353/356/357/358 + 15 edition rows). This is
  a consequence of the code rule *"readable codes only where type and year are
  both proposed at mint time"* — codes are stable and never retrofitted. The
  README's "codes are lecture/discussion only" is technically true (every code
  is), but it does **not** say every lecture gets a code; if desired, a one-line
  clarification would prevent future confusion. Not a defect.
- **item_type/format vocabulary:** 0 `audio`/`video` item types anywhere in
  `data/*.csv`; 0 books with non-`book` format; 0 non-books with `format=book`;
  all 7 highlights are `streaming` in `Lecture Highlights`; the single `other`
  (master 371 OM) is consistent.
- **URLs:** every populated URL starts with `http(s)`; no duplicate Veritas/
  Audible/Amazon URLs across *different* works (the shared URLs are multi-part
  lectures pointing at one product — expected); the 265 malformed Veritas URL
  is the documented publisher-verbatim slug.
- **Source overrides:** all 131 approved, all target fields valid, no blank
  values, all 13 `candidate:`-keyed overrides resolve to a promoted key, all
  raw-row-number overrides exist in the ledger.
- **Exclusions:** all 72 map to non-`item` ledger dispositions; dispositions sum
  to 374 (302 item + 31 blank_separator + 21 series_context + 10 research_note
  + 5 source_context + 4 duplicate + 1 needs_review).
- **Candidate/edition registries:** 39/39 manual candidates and 24/24 edition
  candidates promoted; every `candidate_key` in the master resolves; every
  registry UUID exists in the master; edition-row `work_id`s all exist in
  `work_families.csv` and match the master.
- **Product relationships:** 336 derived primary + 7 `related_material` = 343;
  no duplicate (master, product) pairs; no related row duplicates a master's
  primary. The 7 related rows all belong to master 202-related book products.
- **Series compilations:** 7, all series-level `Lecture Highlights` rows with
  evidence-backed `included_lecture_count`.
- **Series taxonomy:** 177 approved / 9 rejected / 0 proposed; the 3 re-seriesed
  masters (357 On The Road, 312/313 Discussion) confirmed.
- **Streaming:** 36 approved streaming URLs, all matching `reference_url_1`;
  the other 8 `reference_url_1` values are intentional (1 archive.org link +
  4 Amazon academic + 3 Audible/NC + 1 Hay House program).
- **Year/month:** 0 bad months, 0 non-`198X`/non-4-digit years, 0 month-without-
  year, 0 books with months, 0 books with blank years; `year_source` populated
  on all 365.
- **Frontend contract:** 19 HTML tabs = 19 VIEWS = 19 JSON files; CSP/SRI hashes
  valid; column presets reference fields that exist on their rows; the
  schema-contract test (S-d) is in the suite.

---

## 5. Recommended actions (priority order)

1. **D-1 (data fix, owner-approved mechanical):** remove the stale 50491 row
   from `data/veritas_mapping_decisions.csv`, regenerate
   `docs/veritas-mapping-decisions.json` + `docs/catalogue-meta.json`
   (`python build_catalogue_pages.py`), re-run all six `--check` modes + the
   115 tests. This is the only item that affects what a visitor sees.
2. **D-2 (doc fix):** update `decisions/VERITAS_MAPPING_DECISIONS.md` "Current
   seed" to 9 decisions after D-1 (5 excluded + 4 non-primary), noting the
   2026-08-07 Highlights lift and 50411/1542/50491 removals.
3. **D-4 (CI snippet for owner):** switch the JS-syntax step to loop over
   `tests/*.spec.js` so `column-layout.spec.js` is covered.
4. **D-3 / D-5 (doc hygiene):** update the "15 tabs" backlog bullet to 19 and
   refresh/delete the stale §6 P1 edition-model paragraph in
   `NEXT_AGENT_HANDOFF.md` (§3 is already authoritative).
5. **Optional:** add a one-line README clarification that catalogue codes are
   assigned to lecture/discussion rows *that had a verified year at minting*,
   so edition rows and blank-year candidates correctly have no code.

No code defect and no data-integrity break were found beyond D-1; the
deterministic pipeline, 90%-covered 115-test suite, and six `--check` gates all
pass on this branch.
