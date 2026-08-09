# Full-Stack & Catalogue Audit — 2026-08-09 (Arena Deep-Dive, post PR #40)

**Auditor:** Arena.ai Full-Stack / Data-Engineering agent
**Repository:** `56eli/docsheet`
**Branch audited:** `arena/019fe5fc-docsheet` at `d731e1b` (`main` HEAD — Merge of PR #40)
**Date (UTC):** 2026-08-09
**Scope:** raw CSV → ledger → curated master → inventories → candidate/edition registries → relationships → taxonomy → work families → filename proposal → `docs/*.json` → frontend (`docs/index.html`, `docs/app.js`, `docs/style.css`) → tests → CI/CD → living documentation.
**Method:** fresh venv (pandas 3.0.5 / numpy 2.4.6 / coverage 7.15.4 / Python 3.11), re-ran all six `--check` modes, the full 125-test suite, coverage, local HTTP smoke, CSP/SRI recomputation, plus independent stdlib/pandas probes that bypass the project's own validators (cross-table reference integrity, URL sharing across works, orphaned URLs, CSV↔JSON cell parity, sheet-registry ↔ docs-file parity, filename/display conversion, ledger casing, raw-CSV column forensics).

> This is a **read-only** audit — it changes no data or code. Findings are for owner triage.

---

## 1. Executive verdict (one sentence)

The catalogue and pipeline at `d731e1b` are internally consistent and fully reproducible — all checks green, all headline counts from the prior audits verified cell-for-cell — and the three medium findings of the 2026-08-09 Arena audit (C-01 owned casing, D-04 Amazon duplicates, B-01 hardcoded Spanish rows) are **already resolved at this commit**, leaving one small code gap (unvalidated ledger `proposed_owned`), two low data/publish quirks, and a cluster of stale/contradictory root-level audit documents as the only actionable items.

---

## 2. Verification matrix (re-run at `d731e1b`)

| Check | Result | Notes |
|---|---|---|
| `python -m py_compile *.py` | **PASS** | 10 root modules |
| `process_data.py --check` | **PASS** | 374 raw rows, 7 view columns (corrected 2026-08-09: the six always-empty raw columns are trimmed, including `Unnamed: 11`; see the FULL extension) |
| `build_research_master.py --check` | **PASS** | 362 items; 75 exclusions; 134 overrides; 39 candidates validated |
| `build_catalogue_pages.py --check` | **PASS** | 362 Everything rows |
| `reconcile_research_master.py --check` | **PASS** | 0 unexplained diffs |
| `map_series_taxonomy.py --check` | **PASS** | 186 mappings; 0 queued |
| `sync_inventory_mirrors.py --check` | **PASS** | 191/191 mirrors match; count invariant holds |
| `python -m unittest discover tests` | **125/125 PASS** | ~3.2s, deterministic |
| Coverage | **91% PASS** | 2059 stmts; lowest module 88% (`build_research_master`, `map_series_taxonomy`); floor 85% |
| Local HTTP smoke (`/docs/`, `master.json`, `catalogue-meta.json`, `data.json`, `index.html`) | **PASS** | All 200 |
| CSP inline-script hash (recomputed) | **PASS** | `sha256-qULmN/IfgO0KcdvNpANXyfZHBIgYfm4o368jeDomJJY=` matches |
| SRI on Tabulator CSS/JS | **PASS** | 3 integrity attrs present, pin 6.5.2 |
| Master identity integrity | **PASS** | 362 unique uuids (1–372, gaps exactly {225,226,227,246,249,264,281,284,302,309}); 278 unique codes (16×`LECTURE-198X-*` by design); 362 unique filenames |
| Item-type distribution | **PASS** | 306 lecture / 40 book / 8 discussion / 7 highlight / 1 other — matches README |
| Format vocabulary | **PASS** | DVD 253, CD 32, streaming 19, book 31, audiobook 27; zero retired `audio`/`video` |
| `year` / `month` sanity | **PASS** | 1973–2026, 4-digit only (+16×`198X` placeholder); 0 month anomalies; 17 blank years all carry labelled `year_source` (13 Volume Series + 4 under investigation) |
| Work-family coverage | **PASS** | 338 `work_families.csv` rows (all uuids valid, no dupes) + 24 edition rows 320–343 from `edition_promotions.csv` = 362; 191 distinct works |
| Relationship integrity | **PASS** | 7 stored `related_material` (all `master_uuid` refs valid) + 333 derived primaries = 340; 7 series compilations; zero URLs shared across different works; zero duplicate URLs within a row |
| Veritas URL orphan check (`source_url_veritas`) | **PASS** | 0 orphans vs 191-product inventory |
| Inventory mirrors | **PASS** | 186 matched + 5 excluded_related_material = 191; `normalized_title_match_count == len(matched_master_uuids)` everywhere; `matched_master_uuids` format consistent (`"; "` for multi, bare for single) |
| CSV↔JSON parity | **PASS** | 13 direct pairs exact; product-relationships 7→340 by design; international now **38→38** (B-01 fix confirmed) |
| `catalogue-meta.json` | **PASS** | 20 keys; `international_products: 38` now present (B-02 fix confirmed); `everything_record_types` = master 362, all candidate classes 0 |
| Sheet registry ↔ docs files | **PASS** | 20/20 files wired 1:1 in `app.js` |
| `docs/master.json` vs `research_master_draft.csv` cell parity | **PASS** | 0 diffs across key fields |
| `owned` vocabulary | **PASS (fix confirmed)** | `true` 295 / `false` 25 / blank 42 — all lowercase; ledger `proposed_owned` lowercase 281/25/68; frontend maps correctly (C-01 resolved) |
| Amazon URL duplication (D-04) | **PASS (fix confirmed)** | 0 rows with `source_url_amazon == reference_url_1` |
| Hardcoded Spanish rows (B-01) | **PASS (fix confirmed)** | 0 code hits for `Disolver`/`El nivel`; rows live in `international_discovery_queue.csv` (38 rows) |

---

## 3. Findings register

### B-04 — Ledger path still lacks a `proposed_owned` vocabulary validator (Low/Medium, code)

The C-01 casing defect (274 rows showing raw `True`) was resolved by **silent normalization**: `build_research_master.py` now applies `.strip().lower()` on all three ownership paths (lines 1243, 1355, 1406). The manual-candidate and edition-candidate inputs have strict validators (`proposed_owned ∈ {"", "true", "false"}`, lines 782, 1121), but the **ledger path — the original source of the `True` values — still has no such check** (only `proposed_item_type` is validated at line 1327). A future casing slip in `migration_review_ledger.csv` will be silently lowercased instead of caught, and the audits' B-03 root cause therefore remains open.

**Recommendation:** add the same `proposed_owned` vocabulary check to the ledger row loop (mirror lines 782/1121), so the invariant is enforced at the input, not papered over at the build.

### D-09 — Published view still contains an always-empty column; `Unnamed: 5` junk column is visible (Low, data/publish)

- `docs/data.json` (the pass-through "Original Spreadsheet" tab) has **8 columns**, including `Unnamed: 11`, which is empty in **all 374 rows**. Six raw columns are always-empty (uuid, Unnamed: 8/9/10/11, other links); only five are dropped by `VIEW_DROP_COLUMNS` (`process_data.py:57`). The INSTRUCTIONS narrative "5 always-empty raw columns are trimmed" is literally true but incomplete — one always-empty column still ships.
- `Unnamed: 5` (kept) contains two owner note cells (`BARRET?`, `my pdfs are trash`) and renders under the raw header `Unnamed: 5` in the live tab.
- `docs/app.js:320` — the Original Spreadsheet column priority list still names `"other links"`, a column that no longer exists in `data.json` (dead config; harmless but stale).

**Recommendation:** add `"Unnamed: 11"` to `VIEW_DROP_COLUMNS` (then the "always-empty columns are trimmed" claim is exact), drop `"other links"` from the `app.js` priority list, and either relabel `Unnamed: 5` (e.g. map to a friendly header) or decide the junk cells should stay visible.

### D-10 — Raw CSV data-entry quirks visible on the live pass-through tab (Low, data hygiene)

Two rows in the source-of-truth CSV carry owner notes in wrong columns, and both are visible in the published "Original Spreadsheet" view (they are correctly **excluded from the master** — ledger rows 279 `series_context`, 373 `source_context` — so curation is unaffected):

- Row 279: a Discord URL sits in the **`format` column** (`https://discord.com/channels/...`), with `BARRET?` in the unlabeled column.
- Row 373: `SETH HAS IT https://discord.com/...` sits in the **title** column.

**Recommendation:** optionally move these notes out of `format`/`title` (the raw CSV is owner-editable; the pass-through pipeline will reflect the cleanup), or accept and document them as provenance noise.

### DOC-06 — `FULL_STACK_AUDIT_2026-08-09_ARENA.md` (root, dated today) is stale vs HEAD (Medium, docs)

That audit audited `bbe8b01` (pre-merge). Its three headline findings are **all already resolved at `d731e1b`**:

| Audit claim | State at HEAD (verified this pass) |
|---|---|
| C-01: 274 rows `True` vs 21 `true`; ledger `True/False/""` | All lowercase (295/25/42); ledger lowercase (281/25/68); `.lower()` on all build paths |
| D-04: masters 359–361 duplicate Amazon URL in `reference_url_1` | 0 `amazon == reference` duplicates; 359–361 `reference_url_1` blank |
| B-01: two Spanish rows hardcoded in `build_catalogue_pages.py:798–814` | No code hits; rows in `international_discovery_queue.csv`; 38→38 parity |
| B-02: `catalogue-meta.json` missing `international_products` | Key present, value 38 |

Anyone reading the 08-09 audit as "current" will re-open already-fixed work. The README also still declares the 08-08 pair as "(declared current)" and points to `FULL_STACK_AUDIT_2026-08-08_ARENA.md` as "the current full-stack audit" — while the 08-09 file sits at root, unlisted in the documentation layout.

**Recommendation:** archive `FULL_STACK_AUDIT_2026-08-09_ARENA.md` and `EXTERNAL_AUDIT` (or add a status banner noting which findings are resolved), and refresh the README "Documentation layout" to list the declared-current audit.

> **✅ Resolved 2026-08-09 (repo-organization pass):** the 08-08 baseline pair,
> `EXTERNAL_AUDIT.md`, and the implemented `PRESENTATION_UX_PROPOSAL_2026-08-09.md`
> were archived to `archive/` with banners; README "Documentation layout" now
> lists only the declared-current 08-09 audits at root, and INSTRUCTIONS points
> to the 08-09 deep-dive as the current audit.

### DOC-07 — `EXTERNAL_AUDIT` contradicts the 08-09 audit and references a missing tool (Medium, docs)

- It calls "a **21-row** `owned` casing inconsistency (**lowercase** `true`)" the actionable defect — the *opposite* direction of the 08-09 Arena audit's C-01 (uppercase `True`). Both describe the same `bbe8b01` state from different directions; at HEAD neither applies.
- It references `check_docsheet.py` / `audits/docsheet/tools/check_docsheet.py` as a reusable checker — **not present anywhere in the repo**.
- It is a root-level handover file not listed in README's documentation layout.

**Recommendation:** archive it (it is a handover artifact, not a living doc) or convert the missing checker reference into a committed `tools/` script if the audit method is worth keeping.

### DOC-08 — `NEXT_AGENT_HANDOFF.md` header is stale and internally contradictory (Low, docs)

- Header: "Prepared: 2026-08-08 … branch `arena/019fe2db-docsheet` (PR #39, open)" — but HEAD is the **PR #40 merge** (`d731e1b`).
- It already records D-04/B-01 as "RESOLVED … 2026-08-09" — contradicting `FULL_STACK_AUDIT_2026-08-09_ARENA.md` (which lists them open) — a sign the handoff was updated after the audit was written.

**Recommendation:** update the header (date, branch, PR status) and align it with the audit status at HEAD.

### DOC-09 — README wording drift on the Everything view and Record Type filter (Low, docs)

- "The **Everything** sheet intentionally shows curated master records **next to official product candidates** so they can be compared" — `everything_record_types` is currently `master: 362`, every candidate class **0**; the sheet is all-master today (queues are empty by design as standing intake lanes, and all 39 candidates are promoted).
- "Use the Record Type filter on that tab to isolate curated data before exporting" — `configureReviewFilter()` (app.js:1672) **hides the filter toolbar by design when only one record type exists**, so the instruction is not actionable in the current state.

**Recommendation:** soften to "…shows candidates when the intake lanes are populated; currently all rows are master", and note the filter appears only when more than one record type is present.

---

## 4. Verified-clean (previous findings re-confirmed, nothing to do)

- **D-01 collapse** (masters 225/226/227 retired; 311/310 keep streaming in `reference_url_1`): counts reconcile — 362 masters, 278 codes, 75 exclusions, 338 work memberships, 333 primaries, 340 relationships, 10 UUID gaps.
- **`reference_url_1` Veritas links not in the 191-product inventory (53 rows):** live-checked — `https://veritaspub.com/causality-the-egos-foundation-jan-2002-streaming/` returns 200 (paid-subscription streaming pages are intentionally not inventory products). No broken links found; this is a validation-coverage note, not a defect.
- **`matched_master_uuids` formatting:** 76 multi-ID rows consistently `"; "`-joined, 110 single-ID rows bare — matches `sync_inventory_mirrors.py` serialization; no inconsistency.
- **Duplicate titles (75 groups):** 74 are same-work multi-part rows; the single cross-work group (`A Review of the Work` 2006/2007, masters 115–117 vs 142–144) is a recurring annual talk with year-scoped filenames — intentional, no collision.
- **57 lectures with year but blank month:** consistent with the "month comes from the official product slug" rule (no product → no month); no month-without-year rows.
- **`catalogue-meta.json` counts** all match their files (362/39/2/75/374/134/0/5/191/340/0/7/29/26/38/4/0).
- **Review overview** covers 14 review sheets; International Editions/Publishers sit in the "Sources" group by design — not an omission.
- Test count (125), coverage (91%), and the house rule references in README/INSTRUCTIONS are consistent with actual runs.

---

## 5. Recommended next steps (priority order)

1. **B-04** — add the ledger `proposed_owned` validator to `build_research_master.py` (+ one test); closes the root cause of the resolved C-01.
2. **D-09** — add `Unnamed: 11` to `VIEW_DROP_COLUMNS`; drop dead `"other links"` from `app.js` priority; relabel or hide `Unnamed: 5`.
3. **DOC-06/07/08/09** — archive or banner the two stale 08-09 audit files; refresh README layout + Everything-view wording; update the handoff header.
4. **D-10** — optional owner cleanup of the two note rows in the raw CSV (or accept and document).

All four fix areas are small, low-risk, and covered by the existing `--check`/test gates. No critical or data-loss issues exist at this commit.

---

## 6. Resolution status (owner-approved fixes, applied 2026-08-09)

All fixes below were applied on `arena/019fe5fc-docsheet` and re-verified: six
`--check` modes green, **126/126 tests** (one added), 91% coverage, `node
--check` clean, local HTTP smoke green.

| Finding | Resolution |
|---|---|
| **B-04** — ledger `proposed_owned` validator missing | Added: `build_research_master.py` validates every ledger row's `proposed_owned ∈ {"", "true", "false"}` before building (mirrors the candidate validators). New test `test_ledger_owned_casing_fails_build`. The silent `.lower()` on all three ownership paths stays as belt-and-braces. |
| **D-09** — always-empty `Unnamed: 11` published; dead `"other links"` priority | `process_data.py` now drops `Unnamed: 11` (view 8 → 7 columns; all six always-empty columns trimmed); `docs/app.js` Original Spreadsheet priority now lists `notes` instead of the dropped `other links`. |
| **D-10** — raw CSV note rows | Row 279's Discord URL moved out of the `format` column and row 373's `SETH HAS IT` note out of `title` into the notes column (header added: `notes`). Ledger raw mirrors and row 373's `review_reason` updated; exclusions + migration-review artifacts regenerated. The pass-through view now shows clean `format`/`title` cells. |
| **DOC-06** — stale 08-09 Arena audit | SUPERSEDED banner added (its C-01/D-04/B-01/B-02 findings are resolved at HEAD); README documentation layout declares this deep-dive current. |
| **DOC-07** — `EXTERNAL_AUDIT` contradiction + missing `check_docsheet.py` | SUPERSEDED banner added noting the opposite-direction casing claim and that the referenced checker is not in the repo. |
| **DOC-08** — handoff header stale | `NEXT_AGENT_HANDOFF.md` header updated to `d731e1b` / PR #40 merged; this session appended to the §6 log. |
| **DOC-09** — README Everything wording | Softened: candidates appear "whenever the intake lanes are populated"; Record Type filter note now says it appears only when more than one record type is present. |

**Remaining watch items (no action needed):** the 53 `reference_url_1` Veritas
links are not mirrored in the 191-product inventory (all live-checked OK —
they are subscription streaming pages by design); the `a review of the work`
title spans two work families (recurring annual talk, year-scoped filenames).
