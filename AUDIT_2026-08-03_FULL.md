# Full Project Audit — DocSheet / Hawkins Research Catalogue

**Audit date:** 2026-08-03
**Auditor role:** Full-Stack Developer + Data Engineer (independent re-audit)
**Branch:** `arena/019fc740-docsheet` (identical to `origin/main` @ `300213a` at audit start)
**Live site:** https://56eli.github.io/docsheet/ (Pages status: `built`, source `main` → `/docs`)
**Scope:** Repo architecture, data model & integrity, reproducibility, generated artifacts, frontend, CI/CD, security, docs, backlog.

---

## 1. Executive summary

The project is in **good, verifiable health**. Every deterministic check passes, the
raw→ledger→master→Pages pipeline is idempotent in a clean clone, and every
cross-file identifier reference resolves. This is a genuinely well-governed
research data repository, not a typical scraped-data project.

The real remaining problems are **not** correctness bugs. They are:

1. **No CI** — nothing enforces the checks that currently only pass because agents run them by hand. Blocked by a GitHub App permission, re-confirmed today.
2. **A data-presentation hazard on the default tab** — the "Everything" view silently mixes 308 curated master records with 36 unpromoted candidates, distinguishable only by an empty ID and free-text `notes`.
3. **Stalled review queues** — 87 master items have no `item_type`, 110 have no catalogue code, 17 candidates are frozen at `not_promoted` with no promotion path implemented, 9 Satsang products are inventory-only.
4. **Documentation sprawl** — 30 Markdown files at repo root, 4 of them overlapping status documents that already reference stale branch names.

Verdict: **safe to build on**. Priorities below are ordered by risk-to-value.

---

## 2. Validation performed in this audit

All commands run from a clean tree; results are my own, not inherited from prior handoffs.

| Check | Result | Notes |
|---|---|---|
| `python -m py_compile *.py` | ✅ Pass | Python 3.11.2 |
| `node --check` on `app.js`, `playwright.config.js`, `tests/csv-export.spec.js` | ✅ Pass | |
| `python build_research_master.py --check` | ✅ Pass | 308 items / 66 exclusions / 80 overrides / 17 candidates |
| `python build_catalogue_pages.py --check` | ✅ Pass | 344 Everything rows |
| `python reconcile_research_master.py --check` | ✅ Pass | Report matches ledger projection |
| **Clean-clone rebuild** (fresh `git clone` → run all 3 generators → `git status`) | ✅ **Pass, zero diff** | Generators are genuinely idempotent — strongest reproducibility signal available |
| `process_data.py` re-run with pandas 3.0.5 | ✅ Pass | `docs/data.json` byte-identical; only `meta.json` timestamp churns (see F-7) |
| Cross-file referential integrity (custom script) | ✅ Pass | 0 dangling IDs across relationships, Veritas decisions, Veritas inventory |
| Ledger arithmetic | ✅ Pass | 308 items + 66 exclusions = 374 ledger rows = 374 raw data rows |
| Master ID integrity | ✅ Pass | 308 unique numeric IDs, contiguous `1`–`308`, no gaps or dupes |
| Tab↔view↔file wiring | ✅ Pass | 17 tabs = 17 view configs = 17 existing JSON files |
| Local HTTP smoke (10 assets) | ✅ Pass | All HTTP 200 |
| `git diff --check` | ✅ Pass | |
| **Workflow-file push permission** | ❌ **Re-confirmed blocked** | Pushed a probe workflow; GitHub rejected: *"refusing to allow a GitHub App to create or update workflow ... without `workflows` permission"*. Probe reverted. |
| Playwright Chromium install | ❌ Blocked | Sandbox network resets on browser CDN; `npm ci` itself succeeds |
| Live Veritas API reachability | ❌ Blocked | TLS EOF from sandbox |
| Veritas review artifact download (`8851979247`) | ❌ Blocked | Artifact **exists and is unexpired**, but the Azure blob redirect resets in this sandbox |
| `https://56eli.github.io` reachability | ❌ Blocked | Sandbox egress; Pages API reports `built` |

**Sandbox network profile:** npm registry ✅, GitHub API ✅ / git push ✅, jsDelivr ❌, Azure artifact blobs ❌, veritaspub.com ❌. Prior handoffs described this as "no network"; it is more precisely **partial egress**, which matters when planning what can be verified locally.

---

## 3. Architecture assessment

```
hawkins archive clone - Sheet1.csv   (374 data rows — immutable raw evidence)
   │
   ├─ process_data.py ─────────────────────────▶ docs/data.json  + docs/meta.json
   │                                                (raw pass-through view)
   └─ migration_review_ledger.csv  (374 classified rows)
        │
        ├─ build_research_master.py ───────────▶ data/research_master_draft.{csv,json}
        │     ├─ + data/research_master_source_overrides.csv (80)
        │     ├─ + validates data/manual_master_candidates.csv (17, not promoted)
        │     └─────────────────────────────────▶ data/research_master_exclusions.csv (66)
        │
        └─ build_catalogue_pages.py ───────────▶ docs/*.json (17 sheets) + catalogue-meta.json
              ├─ + veritas / hayhouse / audible inventories
              ├─ + product_relationships.csv (301) & series_compilation_relationships.csv (7)
              └─ validated against master before write

reconcile_research_master.py ──────────────────▶ RECONCILIATION_REPORT.md (read-only)
fetch_veritas_catalogue.py    ─── manual only ─▶ candidate CSV + diff (gitignored, artifact-only)
```

### What is genuinely well-designed

- **Raw evidence is immutable.** No generator writes the source CSV. This is enforced by structure, not convention.
- **Every review decision is an explicit committed CSV input**, never a hand-edit to a generated file. Overrides, exclusions, candidates, leads, mapping decisions, and relationships are all separate, diffable, human-readable inputs.
- **Read-only `--check` modes on all three generators**, making the whole pipeline CI-ready the moment CI exists.
- **Live-source refresh is review-only by design.** The Veritas workflow deliberately *fails* on divergence and uploads an artifact instead of auto-committing — exactly the right default for curated research data.
- **Evidence granularity is honest.** Item-level relationships where an item is proven; series-level for annual Highlights where official pages don't identify DVD parts. Resisting over-assertion is the hardest discipline in catalogue work and it's being maintained.
- **Compact IDs are stable by raw row number**, so rebuilds don't renumber.

### Structural weaknesses

- ~~`build_catalogue_pages.py` inlines five near-identical 23-key record-shaping dict literals.~~ **✅ Resolved in `23437a5`** — collapsed into a shared `everything_record()` helper that validates field names and enforces one row shape.
- ~~`"original_source_rows": 374` is hard-coded.~~ **✅ Resolved in `23437a5`** — now derived from the ledger row count.
- `docs/catalogue-meta.json` is generated and committed but **referenced by nothing** — neither `app.js` nor `index.html` loads it. It's a dead artifact (or an unimplemented feature).
- `loadMeta()` / `metaLoaded` in `docs/app.js` are **dead code** — `loadMeta` is defined but never called; `docs/meta.json` is therefore never fetched by the UI.
- No dependency lock for Python (`pandas>=2.0`, unbounded — I resolved 3.0.5 today), no lint/format config, no `LICENSE`, no `CONTRIBUTING`.

---

## 4. Data model & integrity findings

### 4.1 Counts (all independently re-verified)

| Layer | Count | File |
|---|---:|---|
| Raw data rows | 374 | `hawkins archive clone - Sheet1.csv` |
| Ledger rows | 374 | `migration_review_ledger.csv` |
| Curated master | 308 | `data/research_master_draft.csv` |
| Exclusions | 66 | `data/research_master_exclusions.csv` |
| Source overrides | 80 | `data/research_master_source_overrides.csv` |
| Manual candidates (all `not_promoted`) | 17 | `data/manual_master_candidates.csv` |
| Manual leads | 1 | `data/research_manual_leads.csv` |
| Veritas inventory | 191 | `data/veritas_official_products.csv` |
| Veritas mapping decisions | 35 | `data/veritas_mapping_decisions.csv` |
| Hay House / Audible products | 24 / 26 | `data/*_official_products.csv` |
| Item→product relationships | 301 | `data/product_relationships.csv` |
| Series compilations | 7 | `data/series_compilation_relationships.csv` |
| International leads | 36 CSV → 38 Pages (+2 Spanish Audible) | `data/international_discovery_queue.csv` |
| Everything Pages view | 344 (308 master + 36 candidates) | `docs/master.json` |

Ledger dispositions: `item` 308, `blank_separator` 31, `series_context` 21, `research_note` 8, `source_context` 5, `needs_review` **1**.

### 4.2 Integrity — clean

- 0 dangling `master_uuid` in relationships; 0 dangling raw-row refs; 0 uuid↔raw-row pairing mismatches.
- 0 dangling master IDs in Veritas decisions or Veritas inventory.
- 0 overlap between exclusion raw rows and master raw rows.
- 198 catalogue codes, all unique, all matching `LECTURE-YYYY-NNN`.
- 308 raw-row provenance keys, all unique.
- All 303 populated source URLs are `https://`.
- Months are all valid `01`–`12` or empty. `owned` is strictly `true`/`false`.

### 4.3 Completeness gaps (the real data debt)

| Field | Filled | Empty | Comment |
|---|---:|---:|---|
| `item_type` | **305** ✅ | **3** | Was 221/87; resolved by IT-1 (`32c153c`). 3 placeholders deferred. |
| `catalog_code` | **221** | 87 | Was 198/110; IT-1 added 23 codes for newly typed records with a year |
| `year` | 221 | 87 | Same 87 rows |
| `month` / `format` / `format_detail` | 198 | 110 | Only lecture items |
| `title_source` | 199 | 109 | |
| `location_physical` / `_digital` / `_streaming` | **0** | 308 | Three schema columns entirely unused |
| `source_url_hay_house` / `_nightingale_conant` | **0** | 308 | Two more entirely unused |
| `reference_url_2` | 0 | 308 | Unused |
| `notes` | 14 | 294 | |

~~**The 87 unclassified rows are not random**~~ — ✅ **Resolved 2026-08-03.** They were
six complete series, confirmed as a single well-bounded task. Now typed by content
class (`32c153c`): 76 `lecture` + 8 `discussion`, with 3 placeholder records
deferred. Two related defects surfaced during the work and were also fixed:

- **SR-1** (`973519d`) — 12 records were filed under `Media Miscellaneous` but are
  in the publisher's official *On the Road – Talk Series* category. Caused by the
  migration reading the raw sheet's `Missing OTR` marker as a `research_note`
  instead of a `series_context` heading.
- **F-10** — the `item_type` vocabulary mixed content classes (`lecture`, `book`)
  with media (`audio`, `video`), which produced two successive wrong proposals
  before the precedent (198 DVDs typed `lecture`, not `video`) settled it. The
  vocabulary is now split into `CONTENT_ITEM_TYPES` and
  `DEPRECATED_MEDIUM_ITEM_TYPES`, and ledger types are validated for the first time.

Six schema columns are 100% empty across all 308 rows. Either populate them or
drop them from `FIELDS` — currently they add width to every export and every
table view for zero information.

### 4.4 Title hygiene

- **55 master titles carry raw filesystem artifacts**: `.mp4`, `-converted`, `PART1`/`PART2`, leading sequence numbers (e.g. `601 Volume VI-How to Raise Your Level of Consciousness-converted.mp4`). These are display titles in a public catalogue.
- **2 titles are unresolved research notes**, not titles: `where is B-02? might not exist.` (ID 246), `where is B-05? might not exist.` (ID 249). These are master records asserting the existence of items whose existence is explicitly in doubt.
- **1 whitespace defect**: ID 264 `title_source` = `'26. "In the World But Not of It" – '` (trailing space + orphan en-dash).
- 1 ledger row still `needs_review`: raw row 371, `Dialogues on Consciousness and Spirituality: WHAT IS THIS ⚠️⚠️⚠️`.
- 13 master items have **no source URL of any kind** — overlapping heavily with the `.mp4` and "might not exist" rows.
- 14 master items have **no product relationship**, including 4 books (Power vs Force, Along the Path to Enlightenment, Dissolving the Ego, The Path to Spiritual Advancement).
- 76 Veritas URLs are shared by more than one master item — expected and correct (multi-DVD lectures share one product page), but worth documenting so it isn't later "fixed".

### 4.5 Open review queues

| Queue | Count | State |
|---|---:|---|
| Master candidates | 17 | `reviewed_candidate` / `not_promoted` — **no promotion mechanism exists** |
| Veritas `unmatched_official_product` (Satsang) | 9 | Inventory-only, awaiting per-item decision |
| Veritas `unique_item` | 9 | Surfaced in Everything as candidates |
| Veritas `compilation_or_new_edition` | 15 | 7 have series-level evidence; 8 undecided |
| Hay House / Audible `unreviewed_official_product` | 4 / 6 | |
| Official discovery queue | 4 | |
| Ledger `needs_review` | 1 | |

---

## 5. Frontend / UX assessment

Reviewed `docs/index.html` (158 lines), `docs/app.js` (827), `docs/style.css` (776).

### Strengths
Per-view descriptions and row counts; readable URL labels instead of raw links;
per-view column presets with frozen key columns; column chooser; row-details
drawer; active-filter chips with clear-all; status badges; dark mode with
pre-paint bootstrap (no flash); `aria-live`/`aria-busy`/`role="tab"` usage;
Escape-key handling; reduced-motion and 720px media queries.

### Findings

- **F-1 (High, data governance) — ✅ RESOLVED 2026-08-03 in `23437a5`.**
  *Was:* `docs/master.json` had 344 rows — 308 curated master records and 36
  official-product candidates — distinguished **only** by an empty `uuid` and a
  free-text `notes` string. A reviewer sorting or exporting "Everything" got a CSV
  where curated and unpromoted rows were visually identical.
  *Fixed by:* an explicit `record_type` field (`master` / `candidate_veritas` /
  `candidate_hayhouse` / `candidate_audible` / `candidate_discovery`) emitted by
  `build_catalogue_pages.py`, rendered as a frozen, distinctly-styled badge column,
  and wired as the review filter for that view. Per-class counts are published in
  `catalogue-meta.json` under `everything_record_types`. The Everything payload is
  byte-identical apart from the new field; all `--check` modes and a clean-clone
  rebuild pass, and a browser test asserts the filter isolates exactly 308 rows.

- **F-2 (High, data governance): every cell in every sheet is editable.**
  `buildColumns()` sets `editor: "input"` unconditionally — including on generated,
  read-only derivative sheets. Edits are session-only, warned about only in a footer
  string. A reviewer can spend an afternoon "correcting" `migration-review.json` and
  lose all of it on refresh, or worse, export the edited CSV and treat it as truth.
  *Fix:* make read-only the default; opt in per view if editing is ever wanted.

- **F-3 (Medium): dead code.** `loadMeta()` is defined and never called; `metaLoaded`
  is assigned and never read. `docs/meta.json` is generated, committed, and never
  fetched. `docs/catalogue-meta.json` likewise has zero consumers.

- **F-4 (Medium, a11y):** tabs have `role="tab"` and `aria-controls="spreadsheet"`, but
  `#spreadsheet` has no `role="tabpanel"` and the tab strip has no roving-tabindex
  keyboard model (arrow keys don't move between tabs). The pattern is half-implemented.

- **F-5 (Low):** filter chips are labelled "Active filters" but are not interactive —
  no per-chip dismiss, only global "Clear all".

- **F-6 (Low):** `footerUpdated.innerHTML` is set from `Last-Modified` / `meta.generated_at_utc`.
  Values are server/self-controlled so this isn't exploitable today, but it's an
  unnecessary `innerHTML` sink in an otherwise DOM-API-clean file.

---

## 6. CI/CD, workflows, deployment

| Area | State | Assessment |
|---|---|---|
| GitHub Pages | `built`, `main` → `/docs`, public | Healthy |
| `Update Spreadsheet` workflow | dispatch + push-on-CSV-change | Works, but see F-7 |
| `Map Veritas Catalogue` workflow | dispatch only, review-only, artifact upload | **Correctly designed.** Last run `30803991007` failed *intentionally* at the diff guard — that is the safeguard working |
| PR validation CI | **Does not exist** | Test files are committed; no workflow runs them |
| Workflow-file push | **Blocked, re-confirmed today** | GitHub App lacks `workflows` permission |

- **F-7 (Medium, CI hygiene): `process_data.py` has no `--check` mode and writes a
  fresh `generated_at_utc` on every run.** I confirmed today that `docs/data.json` is
  byte-stable across runs but `docs/meta.json` always churns. Any future "verify
  generated files are current" CI step will produce a permanent false positive unless
  the timestamp is treated as dynamic. Add `--check` that compares `data.json` exactly
  and `meta.json` structurally (ignoring the timestamp).

- **F-8 (Medium) — ✅ RESOLVED 2026-08-03 in `b7c22fb`.** The run `30803991007` artifact
  was supplied by the owner and reviewed. **No upstream catalogue change:** all 191
  products unchanged. The diff was six rows differing in one *derived* field,
  `normalized_title_match_count`, which claimed `0` while naming one matched master ID —
  a defect in our committed data, caused by the approved decision overlay recording
  `matched_master_uuids` without carrying through the recomputed count. Re-applying the
  35 approved decisions offline reproduced the artifact's values exactly and touched no
  other field. Corrected the inventory and added `validate_veritas_inventory()` so the
  contradiction cannot recur silently. See `VERITAS_ARTIFACT_REVIEW.md`.

- **F-9 (New, Low–Medium): derived fields rely on generator discipline, not invariants.**
  F-8 was only detectable by a live network refresh because nothing validated that
  `normalized_title_match_count` equals `len(matched_master_uuids)`. I swept the other
  derived/denormalized columns for the same class of drift and **found no further
  defects**:

  | Derived field | Checked against | Result |
  |---|---|---|
  | `veritas_official_products.matched_master_titles` | titles of referenced master IDs | ✅ 0 mismatches / 191 |
  | `veritas_mapping_decisions.matched_master_titles` | titles of referenced master IDs | ✅ 0 mismatches / 35 |
  | `series_compilation_relationships.included_lecture_count` | distinct lectures in the series/year/month scope | ✅ 7 / 7 correct |

  *Note on the last row:* each lecture spans ~3 DVD parts, so the count is distinct
  lectures, not master rows (e.g. product 39238 = 10 lectures across 30 DVD-part
  records). My first pass mis-modelled this and produced a false alarm; the corrected
  check confirms all seven are right.

  Only `normalized_title_match_count` is guarded in code today. The remaining two
  invariants above hold but are unenforced, so a future hand-edit could still
  desynchronize them. Cheap follow-up: extend `validate_veritas_inventory()` to assert
  the title projections too.

---

## 7. Security, privacy, supply chain

| Area | Assessment | Risk |
|---|---|---|
| Secrets | None in code or workflows | ✅ Low |
| Workflow permissions | `contents: read` (Veritas), `contents: write` (spreadsheet) — correctly narrow | ✅ Low |
| Third-party JS/CSS | Tabulator `6.5.2` from jsDelivr, **no SRI hash, no self-hosted fallback** | ⚠️ Medium — a CDN compromise executes arbitrary JS on the public site |
| Google Fonts | Loaded from Google on every visit | ⚠️ Low/Medium privacy dependency |
| CSP | **None** — no header, no meta policy | ⚠️ Medium hardening gap |
| Python deps | `pandas>=2.0` unbounded, no lock | ⚠️ Medium reproducibility risk (I got 3.0.5 today; a future major could break `to_json`) |
| Node deps | `package-lock.json` present ✅; browsers download at runtime | ⚠️ Low |
| `innerHTML` usage | 6 sites, all with controlled input | ✅ Low, but see F-6 |
| Data sensitivity | Public catalogue of published commercial media; no PII | ✅ Low |
| `.gitignore` | Correctly excludes Veritas candidate/diff artifacts | ✅ Good |
| LICENSE | **Absent** — repo is public with no license | ⚠️ Legal ambiguity for a public catalogue |

Adding SRI to two `<link>`s and one `<script>` is a 3-line, zero-risk fix and is the
single highest security-value change available.

---

## 8. Documentation assessment

30 Markdown files at repo root, ~5,300 lines total.

- **Sprawl:** decision records (`SATSANG_MAPPING_DECISIONS`, `VERITAS_MAPPING_DECISIONS`,
  `BOOK_RELATIONSHIP_DECISIONS`, `HIGHLIGHTS_COMPILATION_DECISIONS`,
  `COMPILATION_CANDIDATE_DECISIONS`, `UNIQUE_ITEM_CANDIDATE_DECISIONS`,
  `FINAL_TITLE_MATCH_DECISIONS`, `RECONCILIATION_DECISIONS`) are all valuable provenance
  but are flat in the root next to operational docs. They belong in `docs/decisions/`
  or `decisions/`.
- **Four overlapping status documents** — `PROJECT_STATE_AUDIT.md`, `HANDOFF.md`,
  `NEXT_AGENT_HANDOFF.md`, `IMPLEMENTATION_PLAN.md` — restate the same counts and
  priorities. They will drift; two already cite stale branch names
  (`arena/019fc714`, `arena/019fc6af`) as "current".
- **Two `*_DRAFT.md` files** (`OFFICIAL_SOURCE_REGISTRY_DRAFT`,
  `RESEARCH_MASTER_SCHEMA_MIGRATION_DRAFT`) alongside their finalized versions — unclear
  which is authoritative.
- **Counts are duplicated by hand** across README, audit, handoffs, and plan. Every count
  I spot-checked is currently accurate, but this is manual and will rot. `catalogue-meta.json`
  already holds these numbers programmatically and could be the single source.

---

## 9. Prioritized backlog

### P0 — Enforce what already works
1. **Get `workflows` permission and land CI.** (Blocked on the user reconnecting/expanding the GitHub App scope.) Workflow content is trivial: `py_compile`, three `--check` runs, `node --check`, `npm ci`, `npm run test:e2e`. Everything it needs is already committed. *Without this, all guarantees in this audit are only as good as the last person who remembered to run the checks.*

### P1 — Correctness & governance visible to users
2. ~~**F-1: add `record_type` to the Everything view.**~~ ✅ **Done** (`23437a5`).
3. **F-2: make review sheets read-only by default.**
4. ~~**F-8: review the Veritas artifact**~~ ✅ **Done** (`b7c22fb`) — no upstream change; internal derived-field defect found, fixed, and guarded. Re-running the workflow should now pass cleanly.
5. ~~**Classify the 87 untyped master items**~~ ✅ **Done** (`32c153c`) — 84 typed by content class (coverage 305/308); 3 placeholders deferred. Also corrected a series mis-grouping (`973519d`) and added `discussion` to the vocabulary.
6. **Implement candidate promotion** for the 17 frozen candidates (promotion-decision CSV keyed by `candidate_key` → generator assigns compact ID + code + provenance).

### P2 — Hardening & hygiene
7. **Add SRI hashes + a CSP meta policy** to `docs/index.html`.
8. **`process_data.py --check`** with timestamp-aware comparison (F-7).
9. **Title normalization pass** — strip `.mp4` / `-converted` / leading sequence numbers into a `source_filename` field, preserving raw values; resolve the 2 "might not exist" placeholders and 1 whitespace defect.
10. **Pin Python deps** (`pandas>=2,<4` or a constraints file); add `LICENSE`.
11. **Drop or populate the 6 always-empty master columns.**
12. **Remove dead code** (F-3). ~~Derive `original_source_rows`.~~ ✅ Done (`23437a5`).

### P3 — Maintainability & polish
13. ~~**Refactor `build_catalogue_pages.py`**~~ ✅ **Done** (`23437a5`) — shared `everything_record()` helper.
14. **Consolidate documentation** — one living `STATUS.md` generated from `catalogue-meta.json`; move decision records to `decisions/`; resolve the two `*_DRAFT` files.
15. **Complete the a11y tab pattern** (F-4) and add per-chip dismiss (F-5).
16. **Expand browser tests** to all 17 tabs, search+filter composition, column chooser, row drawer, dark mode, and console-error assertions.

---

## 10. Progress since this audit

| Item | Status |
|---|---|
| F-1 — curated/candidate conflation | ✅ Resolved (`23437a5`) |
| `build_catalogue_pages.py` duplication | ✅ Resolved (`23437a5`) |
| Hard-coded `original_source_rows` | ✅ Resolved (`23437a5`) |
| CI workflow | ⏳ Owner action — see `UNBLOCK_INSTRUCTIONS.md` Task A |
| F-8 — Veritas artifact review | ✅ Resolved (`b7c22fb`) — no upstream change; derived-field defect fixed + guarded |
| F-9 — other derived-field invariants | ✅ Swept, no further defects (2 remain unenforced in code) |
| SR-1 — 12 records mis-grouped as Media Miscellaneous | ✅ Resolved (`973519d`) — confirmed against publisher taxonomy |
| IT-1 — 87 untyped master records | ✅ Resolved (`32c153c`) — 84 typed, coverage 221→305 of 308 |
| F-10 — `item_type` vocabulary mixed content classes with media | ✅ Documented + guarded (`32c153c`) |

## 11. Recommended next step

Unblocked and ready to pick up now:

- **F-2 + SRI/CSP + dead-code removal** — a contained governance/hardening bundle,
  fully verifiable locally.
- **The 87-item classification** — pure data work, well-bounded, but needs your
  decisions on item types for six series.

**Blocked on the owner:** only CI now — `.github/workflows/ci.yml` must be created via
the web editor, since the App cannot push workflow files (re-confirmed by probe).
Step-by-step in [UNBLOCK_INSTRUCTIONS.md](UNBLOCK_INSTRUCTIONS.md) Task A.
Task B (Veritas) is complete; the only optional follow-up is re-running the workflow
once to confirm it now passes.
