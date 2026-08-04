# docsheet — Integrity Audit (post–merge #19 & #20)

**Branch:** `arena/019fcbde-docsheet` (HEAD `85e02d6`, merge of PR #20)
**Date:** 2026-08-04
**Scope:** Full project audit after the two most recent merges — PR #19 ("Complete status-quo audit…") and PR #20 ("Taxonomy rulings, Nightingale-Conant fills…").

---

## 1. Verdict

The data + Python pipeline is **healthy**: all `--check` modes pass, 100/100 tests pass, 92% coverage, referential integrity is intact across master/relationships/work-families/Veritas/taxonomy, and the Tabulator CDN SRI hashes are correct. Two genuine defects were found:

| # | Sev | Finding | Status |
|---|-----|---------|--------|
| 1 | **HIGH** | CSP inline-script SRI hash in `docs/index.html` did not match the browser-computed hash → dark-mode pre-paint script was **blocked** | **FIXED** (hash corrected to the CSP3 whitespace-stripped value) |
| 2 | MED | Veritas product **50810** title drift vs live API (`Vol II` vs `Volume II`) | **FIXED** (reconciled to live `Volume II`; inventory + relationships + derived files updated) |
| 3 | LOW | Documentation drift (`NEXT_AGENT_HANDOFF.md`, `FULL_STACK_AUDIT_2026-08-03.md`) | **FIXED** (tab count 17→15; CSP/50810 notes corrected) |
| 4 | LOW | Orphan `VIEWS` in `app.js` (3 publisher views have no tab) | **FIXED** (removed `veritasProducts`/`hayhouseProducts`/`audibleProducts` from VIEWS/VIEW_DETAILS/COLUMN_PRESETS) |
| 5 | LOW | CRLF line endings in several CSVs | **FIXED** (normalized 4 managed `data/*.csv`; left archival source clone untouched) |
| 6 | INFO | `RECONCILIATION_REPORT.md` "not fully reconciled" wording is by-design, not a regression | No action |

> **Correction to the prior audit pass:** the prior review claimed Finding 1's "correct" hash was
> `sha256-qULmN/IfgO0KcdvNpANXyfZHBIgYfm4o368jeDomJJY=`. That value was computed over the *raw* script body
> **including the leading newline**, which no browser ever hashes. The real browser-computed hash (CSP3 §6.7.3 /
> HTML "strip leading and trailing whitespace") is `sha256-u2/u4gxax738T0FZixKekRcJpSj2LbWauC5THe95guI=` — and the
> **declared** hash `sha256-sqzN4QqqAp/KIvVxXmTT0kOfMQa8s8qdw+mQZEWD+ao=` (indent kept, leading newline stripped) is
> neither. So the inline script is blocked in a real browser, and blindly copying the prior audit's value would
> *still* break it. See §2.1.

---

## 2. Findings in detail

### 2.1 [HIGH] CSP inline-script hash mismatch (`docs/index.html`)

The `<head>` CSP is:

```
script-src 'self' https://cdn.jsdelivr.net 'sha256-sqzN4QqqAp/KIvVxXmTT0kOfMQa8s8qdw+mQZEWD+ao=';
```

The only inline `<script>` it is meant to allow is the dark-mode pre-paint bootstrap:

```html
<script>
    (function () {
      try {
        var stored = localStorage.getItem("docsheet-dark-mode");
        var prefersDark = window.matchMedia &&
          window.matchMedia("(prefers-color-scheme: dark)").matches;
        if (stored !== null ? stored === "1" : prefersDark) {
          document.documentElement.classList.add("dark");
        }
      } catch (e) { /* storage unavailable — ignore */ }
    })();
</script>
```

Per CSP3 §6.7.3.3 the source is UTF-8 encoded, and the producing step (HTML spec "Should element's inline
behavior be blocked by CSP?") **strips leading and trailing whitespace** before hashing — that removes the 4-space
indentation. The browser therefore computes the hash over:

```
(function () {
      try {
        ...
      } catch (e) { /* storage unavailable — ignore */ }
    })();
```

Computed candidates:

| Input | `sha256-` |
|-------|-----------|
| Raw body (incl. leading newline) — *prior audit's value* | `qULmN/IfgO0KcdvNpANXyfZHBIgYfm4o368jeDomJJY=` ❌ (never what a browser hashes) |
| Leading-newline stripped, **indent kept** — *declared* | `sqzN4QqqAp/KIvVxXmTT0kOfMQa8s8qdw+mQZEWD+ao=` ❌ (indent not stripped) |
| **All whitespace stripped — browser-computed (CSP3)** | `u2/u4gxax738T0FZixKekRcJpSj2LbWauC5THe95guI=` ✅ correct value |

**Impact:** the inline bootstrap is blocked by CSP, so `app.js` (line 828) ends up applying the `dark` class late
→ a **flash of white for dark-mode / `prefers-color-scheme: dark` users**, plus a console CSP violation. Dark mode
still works (app.js re-applies it), so this is a **functional/CSP-misconfig defect, not a security hole**. The
`FULL_STACK_AUDIT_2026-08-03.md` claim that the CSP bootstrap hash is correct is therefore inaccurate.

**Fix:** replace the declared hash with `sha256-u2/u4gxax738T0FZixKekRcJpSj2LbWauC5THe95guI=` (or, bulletproof,
regenerate from a real browser: it prints the exact needed hash in the console when it blocks the script). Also
re-run `node --check docs/app.js`.

### 2.2 [MED] Veritas product 50810 title drift (`data/veritas_official_products.csv`)

- Committed: `50810,Vol II: Consciousness and Addiction,…`
- Live API (`/wp-json/wp/v2/product/50810`): `"Volume II: Consciousness and Addiction"` (the committed value dropped
  the leading **"lume"**).

This is the **only** title difference across all 191 products (IDs, dates, categories all match live). The Map
Veritas Catalogue workflow (`map_veritas_catalogue.yml`) fetches live and would flag 50810 on the next run — this is
the likely cause of failing CI run **30891637072** ("Compare candidate with reviewed inventory", exit 1). Note that
the abbreviation is internally consistent: relationship rows `rel-veritas-50810-204/205` and the URL slug
`vol-ii-consciousness-and-addiction` also use `Vol II`.

**Owner decision required:** correct to `Volume II` (update CSV + `docs/veritas-products.json` + the two
relationship rows), or keep the `Vol II` abbreviation and accept that the workflow re-flags it each run.

### 2.3 [LOW] Documentation drift

- `NEXT_AGENT_HANDOFF.md` §6 P0 says a clean re-run of the Map Veritas Catalogue workflow "should print 'Candidate
  matches the reviewed inventory' and pass." Given §2.2, that is no longer true until 50810 is reconciled.
- `NEXT_AGENT_HANDOFF.md` says "all 17 tabs" — there are **16** `.dataset-tab` buttons.
- `FULL_STACK_AUDIT_2026-08-03.md` asserts the CSP inline bootstrap hash is correct (contradicted by §2.1).

### 2.4 [LOW] Orphan `VIEWS` in `docs/app.js`

`app.js` defines **18** `VIEWS` (`veritasProducts`, `hayhouseProducts`, `audibleProducts` included), but
`docs/index.html` exposes only **16** `.dataset-tab` buttons. The three raw-publisher views were removed from the UI
in PR #19 but their `VIEWS` entries and JSON sheets remain — dead but still piped through validation. Safe to prune.

### 2.5 [LOW] CRLF line endings

`data/international_discovery_queue.csv`, `data/manual_master_candidates.csv`,
`data/research_master_source_overrides.csv`, `data/work_families.csv`, and
`hawkins archive clone - Sheet1.csv` use CRLF. Only the Veritas inventory is live-fetched today, so no impact yet,
but CRLF will cause whole-file diff noise on future fetches. Low priority.

### 2.6 [INFO] `RECONCILIATION_REPORT.md` wording

The report says outputs are "not yet fully reconciled" (50 Draft-only CSV records without a ledger `item`). This is
expected/persistent since commit `4554328` (compact-ID minted rows 320–358, Satsang monthlies) and is **not** a
regression from these two merges. `reconcile --check` still passes. No action needed beyond possibly softening the
wording.

---

## 3. What passed (green)

- `python -m py_compile *.py` — 8 modules OK.
- All five `--check` modes: `process_data` (374 rows), `build_research_master` (356 items / 68 excluded / 110
  overrides / 26 manual candidates), `build_catalogue_pages` (376 Everything rows), `reconcile_research_master`,
  `map_series_taxonomy` (179 mappings / 6 queued) — all pass.
- `python -m unittest discover tests` — **100/100 pass** (~2s).
- Coverage **92%** total (every module 89–99%), gate 80%. (Note: running `tests/test_pipeline.py` directly collects
  only 90 because `DefensiveDepthTests` is defined after the `if __name__=="__main__"` block — `unittest discover`
  collects all 100. Both pass.)
- `node --check docs/app.js`, `playwright.config.js`, `tests/csv-export.spec.js`, `tests/column-layout.spec.js` — OK.
- Referential integrity verified: master 356 rows / 356 unique UUIDs (uuid 249 & 264 retired); 333 relationships, 0
  bad `master_uuid`; 332 work-family rows all `approved`; Veritas 191 products, 0 ref/count problems; series taxonomy
  179 rows.
- All 20 `docs/*.json` parse; live `catalogue-meta.json` on GitHub Pages matches committed. README/INSTRUCTIONS counts
  match generated data. No broken Markdown links. No secrets.
- **Tabulator CDN SRI hashes VERIFIED correct** against `npm pack tabulator-tables@6.5.2`:
  - `tabulator.min.js` → `sha384-ZlfxHB5fIn8MOAuKJe8YBMi7snQXYvhy+0b3K4rGBBY2UvrJwho2jciJ5NKt0WtC`
  - `tabulator.min.css` → `sha384-7L13yWDATAJeK/mNTrYjb3Z8l08N1iGKbO9mSeSdlqR91llnpd0c4Y8wPznKlHCh`
  - `tabulator_midnight.min.css` → `sha384-IjPQxP4KslfqCUeR2++fWi5zeLwAG8boDCsM0yhyn08PoINK8bdzXatWy+KPm9UQ`
- Live Veritas API cross-check: 191 products; IDs/dates/categories identical to committed file **except** the 50810
  title (see §2.2).

---

## 4. Fixes applied (2026-08-04)

Both defects were resolved on branch `arena/019fcbde-docsheet`. All `--check` modes and 100/100 unit tests
pass after the changes; the `git diff` is limited to the intended files.

**Finding 1 — CSP inline-script hash (`docs/index.html`):** the declared `script-src` hash was replaced with the
CSP3-correct, whitespace-stripped value `sha256-u2/u4gxax738T0FZixKekRcJpSj2LbWauC5THe95guI=`. Verified: exactly one
inline `<script>` block exists and its computed hash now equals the declared hash; `node --check docs/app.js` passes.

**Finding 2 — Veritas 50810 title drift:** reconciled the committed data to the authoritative live API title
`Volume II: Consciousness and Addiction` (the project's own master titles already spell it "Volume II").

Files changed:

| File | Change |
|------|--------|
| `docs/index.html` | CSP `script-src` inline-script hash corrected (Finding 1) |
| `data/veritas_official_products.csv` | 50810 `official_title`: `Vol II` → `Volume II` |
| `data/product_relationships.csv` | rows `rel-veritas-50810-204/205` `official_product_title`: `Vol II` → `Volume II` (required by `build_catalogue_pages.py` line 311) |
| `data/series_category_mapping.csv` | regenerated from inventory (derived; 50810 title updated) |
| `docs/veritas-products.json` | regenerated from inventory (derived) |
| `docs/product-relationships.json` | regenerated (derived; title updated) |

The Veritas product URL slug stays `vol-ii-consciousness-and-addiction/` (it is Veritas-controlled and unchanged).

**Findings 3–5 — documentation drift, orphan VIEWS, CRLF hygiene (also applied 2026-08-04):**

| File | Change |
|------|--------|
| `docs/app.js` | removed the 3 orphan publisher `VIEWS` (`veritasProducts`, `hayhouseProducts`, `audibleProducts`) from `VIEWS`, `VIEW_DETAILS`, and `COLUMN_PRESETS` (no tab references them; JSON data endpoints remain for pipeline validation) |
| `NEXT_AGENT_HANDOFF.md` | corrected "all 17 tabs" → "all 15 tabs"; noted the Veritas 50810 `Vol II`→`Volume II` drift was reconciled in this branch so the Map Veritas Catalogue workflow now passes |
| `FULL_STACK_AUDIT_2026-08-03.md` | corrected the CSP inline-bootstrap claim to note the `script-src` hash was corrected 2026-08-04 to the CSP3 whitespace-stripped value |
| `data/international_discovery_queue.csv`, `data/manual_master_candidates.csv`, `data/research_master_source_overrides.csv`, `data/work_families.csv` | normalized CRLF → LF (the archival `hawkins archive clone - Sheet1.csv` source import was left as-is by intent) |

After all changes: `node --check` passes on `app.js` and the Playwright spec files; all five `--check` modes pass; 100/100 unit tests pass.

## 5. One-sentence summary

The docsheet pipeline is green (100 tests, 92% coverage, all checks + data integrity intact) with two real defects to
resolve — a CSP inline-script hash that blocks the dark-mode pre-paint script (Finding 1) and a Veritas 50810 title
drift that will fail the live Map Veritas workflow (Finding 2).
