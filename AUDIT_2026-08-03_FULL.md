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
| Workflow-file push | ❌ App lacks `workflows` permission (re-probed) |

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
CI enablement, SRI/CSP hardening, read-only sheets, candidate promotion,
`format` population, dead-code removal, and documentation consolidation.
