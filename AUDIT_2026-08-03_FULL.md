# Full Project Audit — DocSheet / Hawkins Research Catalogue

**Audit date:** 2026-08-03
**Auditor role:** Full-Stack Developer + Data Engineer
**Branch:** `arena/019fc740-docsheet`
**Live site:** https://56eli.github.io/docsheet/ (Pages `built`, `main` → `/docs`)
**Scope:** Architecture, data model, **entry-by-entry verification against the live
publisher API**, reproducibility, generated artifacts, frontend, CI/CD, security, docs.

---

## 1. Executive summary

This audit went beyond structural checks: **every catalogue entry was verified
field-by-field against the official Veritas Publishing WordPress API**, including
the publisher's own product-category taxonomy, product slugs, publication dates,
and per-product SKU/format metadata.

That found and fixed **four critical data-correctness defects** that no prior
structural check could have detected, because every one of them was internally
self-consistent and passed all existing validation:

| # | Defect | Scale | Status |
|---|---|---:|---|
| **C1** | `month` derived from a sequence number, not the calendar month | **156 records** | ✅ Fixed |
| **C2** | Master records linked to the wrong official product/edition | 4 records | ✅ Fixed |
| **C3** | Primary/related relationships inverted for those products | 8 relationships | ✅ Fixed |
| **C4** | Split-text titles spanning two raw rows | 2 records | ✅ Fixed |

C1 is the most serious: **79% of all dated lecture records carried a wrong month**
and the error was invisible to every existing check.

Verdict after fixes: **the catalogue is materially accurate against the
publisher's own data.** 191/191 products reconcile, 195/195 verifiable months
match, 0 dangling references anywhere. Remaining items are judgement calls and
enhancements, all recorded in `NEXT_AGENT_HANDOFF.md`.

---

## 2. Entry-by-entry verification against official sources

**Method.** The Veritas WordPress REST API (`/wp-json/wp/v2/product`) was
retrieved in full — 191 products across 2 pages — together with the complete
`product_cat` taxonomy (35 categories). Individual product pages were fetched for
category, SKU, disc-count and format evidence. Every master record with an
official link was then compared field-by-field.

### 2.1 Inventory reconciliation — exact

| Check | Result |
|---|---|
| Live products | **191** |
| Committed inventory | **191** |
| In live but missing from ours | **0** |
| In ours but delisted upstream | **0** |
| Product URL mismatches | **0 / 191** |
| Product slug mismatches | **0 / 191** |
| `published_date` mismatches | **0 / 69 checked** |

The reviewed inventory is a faithful snapshot of the live catalogue.

### 2.2 Field-level verification

| Field | Verified against | Result |
|---|---|---|
| `month` | Official product slug + title | **156 wrong → 0** (see C1) |
| `year` | Official lecture-series category | 3 apparent → all correct¹ |
| `series` | Official `product_cat` taxonomy | 8 mismatches → **4 fixed**, 4 judgement calls |
| `item_type` | Official category + SKU + product details | 1 open (record 301) |
| `owned` | Raw spreadsheet `WE HAVE?` | **0 mismatches / 308** |
| `format` | Raw sheet (no data upstream) | Consistent; intentionally sparse |
| URLs | Live API links | **0 non-HTTPS, 0 mismatches** |
| Relationship titles/URLs | Live inventory | **0 mismatches / 301** |
| Relationship product IDs | Live API | **0 non-existent / 301** |
| Primary-relationship ↔ master URL | Internal invariant | **0 mismatches** |
| Manual candidates | Live API | **0 citing dead products / 17** |
| Veritas decisions | Live API | **0 citing dead products / 35** |
| Hay House URLs | Domain check | **0 invalid / 24** |
| Audible URLs | Domain check | **0 invalid / 26** |
| Master Audible links | Audible inventory | **0 orphans / 8** |

¹ The three "A Review of the Work" records carry a `2002-l-series` category
upstream because the 2007 lecture revisits the 2002 material; their own
`series-2007` category is also present and our `year=2007` is correct.

---

## 3. Critical findings — all fixed

### C1 — 156 lecture months were wrong (commit `d818d8a`)

**Severity: Critical.** 156 of 198 dated lecture records had an incorrect month.

**Root cause.** `generate_migration_ledger.py` derived the month as
`tempid[6:8]` from the legacy `LSyyyynn_p` identifier. That `nn` segment is the
lecture's **ordinal position within its annual series**, not a calendar month.

The bug was masked because in **2002 lectures ran monthly**, so ordinal == month
and every 2002 record looked right. From 2003 the cadence became roughly
bi-monthly, so ordinal `02` was published as **April**, not February.

| Year | Our months (ordinals) | Official months |
|---|---|---|
| 2002 | 01–12 | 01–12 ✅ |
| 2003 | 01–06 | 02, 04, 06, 08, 11, 12 ❌ |
| 2005 | 01–10 | 02, 04, 05, 06, 07, 08, 09, 10, 11, 12 ❌ |
| 2011 | 01, 02 | 05, 09 ❌ |

**Fix.** Month is now derived from the publisher's own product slug, which
carries the authoritative date in numeric (`/product/2003-02-integration-…`) or
named (`/product/vision-feb-2005`) form. Added
`backfill_months_from_official_source()` so months also resolve for the 6 records
whose official URL arrives via an approved source override rather than the ledger.

**Verification:** 195 months checked against official product titles, **0
mismatches** (was 156).

**Note:** the series-compilation guard fired mid-fix when "Advaita (Aug 2002)"
temporarily dropped out of the 07–12 Highlights scope — the guard working exactly
as designed.

### C2 — 4 records linked to the wrong official product (commit `19f4691`)

Each was an approved source override pointing at a *different work or edition*:

| ID | Our record | Was linked to | Corrected to |
|---:|---|---|---|
| 247 | `B-03 Office Series-A Map Of Consciousness` (video we own) | **1560** — a printed 8½×10″ **wall chart** (SKU `pm_moc_l`) | **50432** `A Map of Consciousness`, category `archival-office-visit-series` |
| 289 | `Truth vs Falsehood` (`item_type=book`) | **1728** — CD & DVD set | **50398** the book edition |
| 291 | `Healing and Recovery` (`item_type=book`) | **1695** — a differently titled audio program | **50378** `Healing and Recovery (Book)` |
| 300 | `In the World, But Not of It` (`item_type=book`) | **1661** — Nightingale-Conant 6-CD set | **53062** the book edition (previously unused by any record) |

Record 247 asserted that a video recording *was* a printed poster.

### C3 — 8 relationships were inverted (commit `19f4691`)

In all four cases the **correct** product was already present but demoted to
`related_material`, while the wrong one was `primary_product_for_item_part`.
Fixed at the reviewed-input layer; the relationship validator caught the
inconsistency mid-fix, as designed.

### C4 — Split-text titles on records 264/265 (commit `7d86862`)

The raw sheet split one cell across two rows — row 296 ends with a dangling dash,
row 297 begins with `Audio`, which is the *tail of item 26*. Confirmed against the
official catalogue, which contains exactly the two reconstructed titles
(`am_itwbnoi`, `am_gwbs`). Repaired; raw strings retained verbatim as evidence.

---

## 4. Work completed this session

| Commit | Change |
|---|---|
| `ca4e3a6` | Independent full audit |
| `23437a5` | `record_type` separates curated records from candidates; generator refactor |
| `b7c22fb` | Veritas refresh divergence resolved + derived-count guard |
| `973519d` | 12 records regrouped to On The Road (publisher taxonomy) |
| `32c153c` | 84 records classified; `discussion` added; ledger type validation |
| `d818d8a` | **C1** — 156 months corrected |
| `19f4691` | **C2/C3** — 4 mislinked products, 8 relationships |
| `7d86862` | **C4** — split-text titles repaired |

### Data state

> Mid-session snapshot as of the commits listed above. The final committed
> state after all 2026-08-03 work (including promotions and the coherence
> audit in §11) is 317 master / 363 Everything; see §12.

| Layer | Count |
|---|---:|
| Raw rows / ledger rows | 374 / 374 |
| Curated master | 308 |
| — `lecture` / `book` / `discussion` / untyped | 274 / 23 / 8 / 3 |
| Catalogue codes (all unique) | 221 |
| Months set (all verified) | 198 |
| Exclusions / overrides / candidates / leads | 66 / 80 / 17 / 1 |
| Relationships / series compilations | 301 / 7 |
| Veritas / Hay House / Audible / International | 191 / 24 / 26 / 36 |
| Everything Pages view | 344 (308 master + 36 candidates) |

---

## 5. Validation performed

| Check | Result |
|---|---|
| `python -m py_compile *.py` | ✅ |
| `node --check` ×3 | ✅ |
| `build_research_master.py --check` | ✅ |
| `build_catalogue_pages.py --check` | ✅ |
| `reconcile_research_master.py --check` | ✅ |
| Clean-clone rebuild from GitHub | ✅ byte-idempotent |
| Live API reconciliation (191 products) | ✅ exact |
| Cross-file referential integrity | ✅ 0 dangling |
| Master ID integrity | ✅ 308 unique, 1–308 |
| Catalogue-code uniqueness | ✅ 221/221 |
| Duplicate detection | ✅ 0 |
| Local HTTP smoke (6 assets) | ✅ all 200 |
| `git diff --check` | ✅ |
| Playwright test discovery | ✅ 3 tests |
| Playwright browser execution | ❌ sandbox cannot download Chromium |
| GitHub CI workflow | ✅ successful on `main` at 2026-08-03 12:22 UTC |

---

## 6. Architecture

```
hawkins archive clone - Sheet1.csv   (374 rows — immutable raw evidence)
   ├─ process_data.py ──────────────▶ docs/data.json + docs/meta.json
   └─ migration_review_ledger.csv    (374 classified rows)
        ├─ build_research_master.py ─▶ data/research_master_draft.{csv,json}
        │     + source overrides, month backfill, candidate validation
        └─ build_catalogue_pages.py ─▶ docs/*.json (17 sheets)
              + inventories, relationships, record_type classification
reconcile_research_master.py ────────▶ RECONCILIATION_REPORT.md (read-only)
fetch_veritas_catalogue.py ── manual ▶ candidate + diff (gitignored)
```

**Strengths:** raw evidence never mutated; every decision is an explicit committed
CSV; three read-only `--check` modes; live refresh is review-only by design;
evidence granularity is honest (item-level vs series-level).

**Remaining weaknesses:** `docs/catalogue-meta.json` and `docs/meta.json` are
generated but unread by the UI; `loadMeta()`/`metaLoaded` are dead code;
`pandas>=2.0` is unpinned; no lint config; no `LICENSE`.

---

## 7. Security & supply chain

| Area | Assessment | Risk |
|---|---|---|
| Secrets | None in code or workflows | ✅ Low |
| Workflow permissions | Narrow (`contents: read/write`) | ✅ Low |
| Tabulator via jsDelivr | Pinned 6.5.2, **no SRI, no fallback** | ⚠️ Medium |
| Google Fonts | Loaded from Google | ⚠️ Low/Medium |
| CSP | **None** | ⚠️ Medium |
| Python deps | `pandas>=2.0` unbounded | ⚠️ Medium |
| Inline editing | Session-only on all sheets incl. generated | ⚠️ Medium |
| Data sensitivity | Public commercial catalogue, no PII | ✅ Low |
| LICENSE | **Absent** on a public repo | ⚠️ Legal ambiguity |

---

## 8. Open items → `NEXT_AGENT_HANDOFF.md`

All non-critical findings are carried there with evidence and recommendations:
4 series/type judgement calls, the title-hygiene pass (54 records),
SRI/CSP hardening, read-only sheets, candidate promotion,
`format` population, dead-code removal, and documentation consolidation.


---

## 9. Post-merge engineering audit — 2026-08-03

This follow-up audit was run against commit `e1f32d4` on 2026-08-03 after the
CI workflow landed. It supplements the field-level catalogue audit above; it
does **not** alter approved catalogue data.

### Scope and observed state

- **Repository / deployment:** 92 tracked files (about 3.1 MB working tree).
  GitHub Pages is configured from `main:/docs` and reports `built` at
  <https://56eli.github.io/docsheet/>.
- **Automated CI:** the latest `CI` run on `main` completed successfully at
  12:22 UTC. It executes Python compilation, the three deterministic catalogue
  checks, JavaScript syntax checks, and the Chromium Playwright suite.
- **Supply-chain scan:** `npm ci` completed from the lockfile and `npm audit
  --omit=dev --audit-level=high` reported **0 vulnerabilities**. No secrets or
  credentials were found in tracked source (excluding dependency lock metadata).
- **Data shape:** the checked master contains 308 records (274 lecture, 23 book,
  8 discussion, 3 untyped); it has 301 reviewed item/product relationships and
  7 reviewed compilation relationships. All 17 manual candidates remain
  deliberately unpromoted.

### Local validation results

| Check | Result |
|---|---|
| `python -m py_compile *.py` | ✅ passed |
| `python build_research_master.py --check` | ✅ 308 items, 66 exclusions, 80 overrides |
| `python build_catalogue_pages.py --check` | ✅ 344 Everything rows |
| `python reconcile_research_master.py --check` | ✅ report current |
| JavaScript syntax checks (`app.js`, Playwright config/tests) | ✅ passed |
| `npm ci` and production dependency audit | ✅ passed; 0 vulnerabilities |
| Local Playwright execution | ⚠️ blocked: Chromium executable is absent in this sandbox |
| `python fetch_veritas_catalogue.py --check` | ⚠️ blocked: local TLS EOF to Veritas API after retries |
| GitHub-hosted CI browser suite | ✅ passed (authoritative browser execution) |

The two local blocked checks are environmental transport/browser-install limits,
not a demonstrated application failure. The existing manual **Map Veritas
Catalogue** run is failing intentionally when its review candidate differs from
the committed inventory; that workflow retains its candidate/diff artifact for
review rather than silently overwriting catalogue data.

### Findings and recommended order

1. **Medium — client-side supply-chain protections are incomplete.** Tabulator
   is version-pinned but loaded from jsDelivr without SRI; the page also has no
   Content Security Policy. Add an appropriate CSP and integrity/crossorigin
   attributes after verifying the exact CDN asset hashes. Consider a local
   vendored fallback if availability is important.
2. **Medium — review data appears editable although it is not persistent.**
   `buildColumns()` applies the Tabulator input editor to every view, including
   generated review and catalogue derivatives. Disable editors on derived views
   (or make the session-only behavior unmissable) to prevent review mistakes.
3. **Medium — data freshness cannot be established locally today.** The local
   Veritas client cannot negotiate TLS in this environment, and the latest
   GitHub refresh reports a candidate difference. Download and review that
   workflow artifact before accepting any inventory update; do not bypass the
   review-only process.
4. **Low — pipeline and documentation drift risks remain.** `process_data.py`
   has no `--check` mode; its timestamp makes output comparison non-deterministic.
   `loadMeta()`/`metaLoaded` are unused, the UI does not consume the committed
   metadata files, `pandas>=2.0` has no upper bound, and several root-level
   handoff/status documents duplicate current-state figures. Consolidate these
   only after deciding the desired public UI behavior.
5. **Low — product decisions are still intentionally open.** Resolve the
   documented series/type, title hygiene, untyped-record, source-override, and
   candidate-promotion decisions in `NEXT_AGENT_HANDOFF.md` before data changes.

No critical code, security, referential-integrity, or generated-output defect
was found by the checks available in this environment. The highest-value next
implementation task is CSP/SRI plus read-only review sheets; the highest-value
catalogue task is review of the Map Veritas artifact and the owner decisions
listed in the handoff.

---

## 10. Follow-up remediation and source comparison — 2026-08-03

The engineering findings in §9 were worked through against their authoritative
inputs. This change set deliberately does not make catalogue-content decisions
where the official source establishes facts but the required catalogue treatment
is an owner decision.

| Audit item | Authoritative comparison / evidence | Outcome |
|---|---|---|
| CDN integrity | The three SRI SHA-384 values were calculated from the official `tabulator-tables@6.5.2` npm package tarball, for the exact CSS/JS paths used by jsDelivr. | ✅ `integrity` and `crossorigin` added to both stylesheets and the script. |
| Browser execution policy | The deployed document's own required origins were enumerated: local Pages assets, jsDelivr, Google Fonts, and Google font files. The inline dark-mode bootstrap was SHA-256 hashed from its exact document content. | ✅ restrictive CSP added: no objects, only self data connections, explicit script/style/font origins, and the one hashed inline bootstrap. |
| Misleading editing | Tabulator's documented `editor: false` column setting was applied to every generated view; the browser test now double-clicks a cell and asserts no editor appears. | ✅ published sheets are read-only, and UI/help text were aligned. |
| Raw-output drift | The raw CSV, `docs/data.json`, and `docs/meta.json` were regenerated in memory using the declared Pandas pipeline. | ⚠️ `process_data.py --check` now verifies the byte-stable data payload and all stable metadata. The matching CI step is prepared locally but cannot be pushed by this GitHub App because it lacks `workflows` permission. |
| Dependency range | The pipeline was validated using current Pandas 3.0.5. | ✅ requirement bounded to `pandas>=2.0,<4`. |
| Live Veritas freshness | GitHub Actions run `30813523859` successfully fetched the upstream candidate, then failed only at its intentional inventory-diff gate. Its artifact endpoint and failed-log download both reached an Azure/GitHub TLS EOF from this sandbox, so its contents could not be independently retrieved here. | ⚠️ The upstream difference is confirmed by the workflow step, but must be reviewed from the uploaded artifact in GitHub before any inventory change. |
| Catalogue record facts | §2's 191-product/308-record comparison remains the authoritative entry-by-entry evidence: live Veritas API URLs, titles, taxonomy, product dates, SKU/format pages, raw ownership values, and relationship references were compared. Current deterministic checks still reproduce the resulting 308 master / 344 Everything records with no divergence. | ✅ no unapproved data mutation made. |

### Deliberately unresolved decisions

Official sources can establish that the relevant products/categories exist, but
cannot decide collection policy. The following therefore remain explicitly
unmodified pending owner direction: the 2011 Satsang placement, record 301's
book-versus-audio treatment, title-hygiene conventions, exclusion of the two
known-nonexistent Office Series placeholders, the proposed source override for
record 264, and promotion of any of the 17 reviewed candidates. Their source
evidence and decision boundaries are retained in `NEXT_AGENT_HANDOFF.md` and
its linked decision documents.

### Verification after remediation

Using an isolated Python environment with Pandas 3.0.5, all of the following
passed: Python compilation, `process_data.py --check`, research-master check,
Pages-catalogue check, reconciliation check, JavaScript syntax checks, and
`npm audit --omit=dev --audit-level=high` (0 vulnerabilities). The new raw-payload CI step is pending a workflow-permitted push. Local Playwright
execution remains unavailable solely because this sandbox lacks the Chromium
binary; the same browser suite is part of the successful GitHub-hosted CI.

---

## 11. Current-state full coherence audit — 2026-08-03

**Scope:** every raw-spreadsheet row, migration-ledger row, generated raw Pages
row, curated-master row, review candidate, promotion decision, relationship, and
published Everything row at the current branch tip.

### Results

| Layer / invariant | Result |
|---|---|
| Raw spreadsheet → migration ledger | 374/374 rows, sequential raw-row provenance 3–376 |
| Raw spreadsheet → `docs/data.json` | 374/374 rows; all cell values preserved (Pandas deterministically renames blank header cells to `Unnamed: 5`, `Unnamed: 8`…`Unnamed: 11`) |
| Curated master schema | 317/317 rows share the declared 24-field schema; every row has a verbatim `legacy_title` |
| Master IDs | 317 unique IDs; no duplicate master UUIDs |
| Master ↔ exclusions | 68 excluded raw rows are disjoint from retained raw master rows |
| Master → Everything view | 317 `master` rows plus 36 official candidate rows = 353 rows |
| Candidate promotions | 11 promotion-registry keys exactly match the 11 candidate rows marked `promoted`; 6 remain explicitly `not_promoted` |
| Product relationships | 301/301 reference a current master UUID |
| Deterministic builds | `process_data --check`, master, Pages, and reconciliation checks all pass |
| Syntax / supply chain | Python and JavaScript syntax checks pass; production npm audit reports 0 vulnerabilities |

### Remediation during this audit

The audit found an internal-status mismatch: 11 records had been promoted through
the explicit promotion registry while their source candidate rows still said
`not_promoted`. The generator now validates candidate status against
`data/manual_candidate_promotions.csv`; the 11 promoted candidates are marked
accordingly, with six remaining candidates clearly unpromoted. This keeps the
review workspace, source input, and published master coherent.

### Known boundaries

- This is a complete **repository-data coherence** audit. It does not claim a
  fresh live re-fetch of every publisher page: the reviewed 191-product snapshot
  remains the declared primary-source baseline, while the local Veritas API client
  is blocked by a TLS EOF in this environment.
- Playwright is syntax-validated locally; Chromium is unavailable in this
  sandbox. GitHub-hosted CI previously ran the browser suite successfully. The
  pending raw-output CI step remains an unpushed workflow-file edit because the
  GitHub App lacks workflow-write permission.
- The owner-approved category dominance rules are documented in
  `CATEGORY_DOMINANCE_POLICY.md`; implementation of the full taxonomy mapper and
  review queue is the next data-engineering task.

---

## 12. Independent re-audit — 2026-08-03 (next-agent session, branch `arena/019fc893-docsheet`)

This section is an independent full-stack/data-engineering re-audit of the
committed state at `6b28e66` ("Add verification and testing steps to CI
workflow") plus this session's remediation. Every claim below was reproduced
locally or against the GitHub API; nothing is assumed from the prior
documentation.

### 12.1 Claims reproduced independently

| Check | Result |
|---|---|
| `python -m py_compile *.py` (8 scripts) | ✅ |
| `process_data.py --check` / master / Pages / reconcile / taxonomy `--check` | ✅ all five |
| `python -m unittest discover tests` | ✅ 54 tests at `6b28e66`; **60 after this session** |
| Coverage gate (`fail_under = 80` in `.coveragerc`) | ✅ **92% total** (1346 stmts, 109 missed); every module ≥ 88% |
| `node --check` (app.js, playwright config, spec) | ✅ |
| `git diff --check` | ✅ |
| CI on `main` (run `30834666253`, commit `6b28e66`) | ✅ success via GitHub API; Pages build `30834665039` success |
| `fetch_veritas_catalogue.py --check` | ⚠️ TLS EOF in sandbox (documented environmental limit; offline replay tests cover the client) |
| Playwright browser suite | ⚠️ no Chromium in sandbox; ran green in GitHub-hosted CI |

### 12.2 Verdict on the prior agent's prompt

**"Audit the whole project."** ✅ Met. `AUDIT_2026-08-03_FULL.md` is a genuine
multi-layer audit (architecture, data model, entry-by-entry verification
against the live Veritas API, frontend, CI/CD, security, supply chain) and it
found/fixed four real data defects (C1–C4) that structural checks could not
see. §9–§11 show the audit was kept honest after the fact.

**"Update all documentation to reflect the status quo."** ⚠️ Partially met.
The living docs (README, INSTRUCTIONS, RECONCILIATION_REPORT,
SERIES_TAXONOMY_MAPPING, VERITAS_ARTIFACT_REVIEW) were current, but a
second pass still found status-quo drift (details in §12.3). All fixed in this
session, and pinned by tests so it cannot silently recur.

**"Get code coverage for tests to 80%."** ✅ Met and exceeded: 92% total,
every pipeline module ≥ 88%, enforced by `.coveragerc` **and** a CI step
(`coverage report` exits non-zero below the floor).

**"Improve fail-safes if you can."** ✅ Met: `--check` modes for every
generator (incl. the previously missing `process_data.py --check`), byte-stable
raw-output comparison, tamper-detection tests, derived-field validation of the
Veritas inventory (`normalized_title_match_count` +
`matched_master_titles`), record-type coverage guard, promotion-registry
validation, series-approval no-op guard, fetcher retry ladder with
fail-loud/preserve-inventory behavior, offline API replay tests. This session
adds a relationship-coverage warning and documentation-currency tests (below).

### 12.3 Findings from this re-audit

**F1 — Relationship layer incomplete for the 11 promoted masters (Medium).**
The promotion path (master IDs 309–319) copies each candidate's official
Veritas URL into `source_url_veritas` but does not mint
`primary_product_for_item_part` rows in `data/product_relationships.csv`. The
schema invariant stated in `PRODUCT_RELATIONSHIP_SCHEMA.md` ("every non-empty
master `source_url_veritas` is represented as a reviewed primary
relationship") is therefore **false** for exactly those 11 records, and no
validator noticed: 304 URL-bearing masters vs. 293 primary relationship rows.
The Product Relationships tab is incomplete for those records.
*Remediation:* `build_catalogue_pages.py` now prints a non-fatal WARNING
listing the uncovered masters on every build/check; the gap is filed as P1 in
`NEXT_AGENT_HANDOFF.md` for an owner decision (add 11 reviewed rows — the URL
equality is already validated — or hold the promotion URLs).

**F2 — Status-quo documentation drift (Low).** Counts that had silently
diverged from the committed data:

| Document | Stale value | Actual |
|---|---|---|
| `README.md` | 223 catalogue codes | **225** |
| `NEXT_AGENT_HANDOFF.md` | P0: CI steps "cannot be pushed by App" | **CI live on `main` (`6b28e66`), run green** |
| `MIGRATION_REVIEW_LEDGER.md` | `item` 308, `research_note` 8 | **306 / 10** |
| `OFFICIAL_CATALOGUE_DISCOVERY.md` | "308-record draft, no candidate added" | **317; 11 promoted via review path** |
| `VERITAS_PRODUCT_MAPPING.md` | 308 masters, 344 Everything, 7 title matches | **317 / 363 / 6** (+4 `unreviewed_official_product` row) |
| `RELATIONSHIP_EXPANSION_AUDIT.md` | 308 masters, 294/147/7 | **317; 304 URL-bearing, 157 distinct URLs, 293 primary, 8 related** |
| `PRODUCT_RELATIONSHIP_SCHEMA.md` | "294 relationships, coverage invariant holds" | **293 primary + 8 related; 11-record gap (F1)** |
| `ITEM_TYPE_CLASSIFICATION_PROPOSAL.md` | "⏳ Awaiting approval — no data changed" | **implemented; master 316/317 typed** |
| `archive/README.md` | "Task A snippet still outstanding" | **resolved in `6b28e66`** |

All fixed in this session. `tests/test_pipeline.py` now contains
`DocumentationCurrencyTests` that fail if the README current-state paragraph,
the handoff §3 table, or the ledger-doc disposition table drift from the
generated data again.

**F3 — Minor items (unchanged or newly noted, no action taken).**
`docs/catalogue-meta.json` key `master_items` actually holds the Everything
row count (363) — a misnomer, but deliberately documented in
`RECONCILIATION_REPORT.md`; renaming would churn generated artifacts and the
report test. Master IDs are 1–319 with stable gaps at 246/249 (excluded rows
are never reissued — consistent with the stable-ID rule). Eight master columns
remain (near-)always empty (`location_*`, Hay House / Nightingale-Conant /
Audible URLs, `reference_url_1/2`) — owner decision (populate or drop). No
`LICENSE` on a public repo (known). `pandas>=2.0,<4` is now bounded. CI still
installs runtime deps twice (`requirements.txt` then `requirements-dev.txt` —
harmless redundancy). The Map Veritas Catalogue workflow has not been re-run
since the derived-field fix; its next run should pass the diff gate (if not,
the diff is a genuine upstream change and must be reviewed before accepting).

### 12.4 Independent data checks (from committed files, not from docs)

- Master: 317 rows, 24 fields, IDs 1–319 (gaps 246/249), **225 unique
  catalogue codes**, 198 months set, 306 `owned`, 277/29/10/1
  lecture/book/discussion/untyped.
- Everything: **363** rows = 317 master + 28 candidate_veritas + 6
  candidate_pending_promotion + 4 discovery + 4 hayhouse + 4 audible; record
  types sum to 363 (guarded by the build).
- Ledger: 374 rows = 306 item + 31 blank_separator + 21 series_context + 10
  research_note + 5 source_context + 1 needs_review.
- Relationships: 301 reviewed rows (293 primary + 8 related); 0 dangling
  master UUIDs; every referenced product exists in the 191-product inventory;
  every primary URL equals the master's `source_url_veritas` (validated).
- Exclusions: 68 rows, zero overlap with master raw rows.
- Promotions: 11 approved keys match 11 master rows (309–319); 6 candidates
  remain unpromoted.
- Supply chain: Tabulator 6.5.2 pinned with SRI + `crossorigin`; CSP present
  with a hashed inline bootstrap; production `npm audit` 0 vulnerabilities
  (reported previously, unchanged).

### 12.5 Bottom line

The previous agent fulfilled the prompt to a high standard: the audit was
real and found real defects, coverage exceeded the target with a working gate,
and the fail-safes are substantive rather than decorative. The residual gap
was documentation status drift plus one relationship-layer coverage gap that
the docs had declared closed; both are now fixed, guarded, and recorded.

### 12.6 F1 resolution (same day, owner-directed)

The owner chose **"add the 11 reviewed relationship rows"** (asked via the
session's direction question). On 2026-08-03 the following landed on branch
`arena/019fc893-docsheet`:

- **11 reviewed `primary_product_for_item_part` rows added** to
  `data/product_relationships.csv` for masters 309–319
  (`rel-veritas-<product_id>-<uuid>`, `reviewed_on=2026-08-03`, evidence =
  official product URL; evidence note cites the owner-approved promotion).
  Relationship layer: 301 → **312 rows** (304 primary + 8 related), 304/304
  URL-bearing masters covered, 165 distinct products referenced.
- **Guard promoted from warning to hard failure**:
  `warn_uncovered_primary_relationships()` became
  `validate_primary_relationship_coverage()` (raises `ValueError` listing any
  uncovered master). New tests cover: covered state passes, uncovered master
  fails, URL-less masters are not gaps, the committed state builds clean, and
  deleting a promoted row fails `--check` (tamper detection).
- **Docs updated to the resolved state**: README and handoff relationship
  counts 301 → **312**, `PRODUCT_RELATIONSHIP_SCHEMA.md` invariant restored,
  `RELATIONSHIP_EXPANSION_AUDIT.md` coverage history, handoff P1 entry
  removed (no longer open), audit §12.3 F1 superseded by this section.
- **Re-verified**: Pages outputs regenerated and byte-checked (363 Everything
  rows unchanged; `product-relationships.json` now 312 rows); 62 tests pass at that point (65 after §12.7);
  coverage still 92%; all five `--check` modes green; `git diff --check` clean.

### 12.7 Book-format backfill (owner question → implement + apply)

**Question:** why do not all books have `format=book`?

**Root cause:** the only format backfill is
`infer_format_from_official_source()`; it (1) resolved the inventory product
by guessing the product ID as the slug's first `-`-token — every blank book's
Veritas URL is a word slug without a numeric prefix, so the lookup silently
missed; (2) recognized only literal `book`/`(Book)` markers in slug/title —
only 3 of the 12 URL-bearing blanks carry one, while all 12 sit in the
publisher's own "Books Published by Dr. Hawkins" category, which was never
consulted; (3) is Veritas-only, so the 5 books without a Veritas URL
(286/298/299/301/302) had no path at all. The raw sheet's `format` column is
unusable evidence (provenance labels + one Discord URL) and the ledger's
`proposed_format` is empty for all 17.

**Fix applied (owner-directed):** the inference now resolves the product by
**exact URL match** against the committed inventory (fallback to the legacy
ID-prefix guess) and adds the category signal (`Books Published by Dr.
Hawkins` → `book`, guarded by `item_type=book`, never overwrites). The master
rebuild changed exactly the 12 predicted records (`''` → `book`): 291, 292,
295, 296, 297, 300, 303–308. Book format coverage 12/29 → **24/29**; total
format coverage 231 → **243** of 317 (74 blank). All checks green; suite now
**65 tests** at that point (82 after §12.8); coverage 92%.

**Remaining 5 books (no Veritas URL) — five distinct causes, all
review-boundary items:** 286 (PvF book product 50411 is title-matched to
lecture 202, not to book 286 — C2 rule: no title-minted master URLs); 298/299
(Hay House eBooks exist but no source override was ever approved); 301
(Veritas is audio-only for this title — the book is Hay House-only, hence the
HH override); 302 (no link/tempid/inventory match; same work as 303 → needs a
duplicate-resolution ruling). Full evidence: `TEMP_RESPONSE_AUDIT_2026-08-03.md`
§11e; tracked in `NEXT_AGENT_HANDOFF.md` P1.

### 12.8 Edition model — Phase 1 + Phase 2 (owner-directed)

The owner identified a model oversight (works with multiple carriers are
collapsed into one row; e.g. 289 *Truth vs Falsehood* = book row whose
audiobook exists only as an Audible URL and whose CD&DVD set only as a
related product) and directed: **one row per work × carrier**. Rulings:
D1 keep one row per DVD part, D2 reviewed edition-candidate layer, D3 move
audible URLs into edition rows, D5 plumbing first. Delivered 2026-08-03:

- **Phase 1:** master + Everything + UI gained `work_id` (25-field schema);
  reviewed `data/work_families.csv` input (approved rows only, never
  title-inferred); validation + tamper tests; 9-row proposed first batch
  (works: Truth vs Falsehood, Power vs Force [202 flagged for ruling], Eye of
  the I, Letting Go, Healing and Recovery, Transcending the Levels, In the
  World But Not of It, Highest Level of Enlightenment).
- **Phase 2:** `data/edition_candidates.csv` — 12 reviewed candidates
  (7 Audible audiobook editions + 5 Veritas audio/CD/DVD editions) with
  inventory-verified URL/title evidence — plus the owner-approval registry
  `data/edition_promotions.csv`; `validate_edition_candidates()` and
  `load_edition_promotions()` (approved rows mint master rows with the next
  compact ID above max). Product 50411 (PvF book) is a source-override
  candidate for 286, not an edition row.
- Nothing promoted yet: master stays at 317 rows with empty `work_id` until
  the owner approves family + edition rows. Suite: **82 tests**, coverage
  **92%** (every module ≥ 90%), all five `--check` green. Design and
  decisions: `EDITION_MODEL_PROPOSAL.md`.
