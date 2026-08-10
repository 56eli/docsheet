# Full Multidisciplinary Expert Audit — Arena 019feabf

**Date:** 2026-08-10  
**Scope:** Web Design, Full-Stack Development, Data Engineering  
**Baseline:** Branch `arena/019feabf-docsheet` from `main` at `3768fe7` (PR #62 merge)  
**Agent:** Arena Agent Mode (Expert Web Designer + Full-Stack Developer + Data Engineer)

---

## TL;DR

DocSheet is a mature, well-maintained static GitHub Pages catalogue with strong data integrity,
thorough testing, and good accessibility. The project scores **8.5/10 overall** with no critical
defects. The primary debt items are: (1) a CSS monolith with ~400 lines of duplication in the
desktop browse-mode section, (2) app.js still at 2,439 lines despite partial modularization,
(3) an unpublished Pages gating workflow, and (4) 3 temporary files in root that should be archived.

**All 147 tests pass · 90% coverage · 6/6 --check modes green · JS syntax clean · 0 TODO/FIXME/HACK**

---

## 1. Web Design Audit (Score: 8.5/10)

### ✅ Strengths

| Area | Evidence |
|---|---|
| Neutral palette | Light: `#f9f9fb`/`#ffffff`/`#f4f4f5`/`#e4e4e7`. Dark: `#0d0d0d`/`#161616`/`#222222`/`#282828`. No slate-blue hex in `--bg`/`--surface`/`--border` tokens. |
| Zebra contrast | ≥ 10 luminance units light, ≥ 6 dark. Enforced by `test_style_contrast.py` (8 tests). |
| Hover contrast | ≥ 7/8 from zebra (light/dark). Neutral hover tones. |
| Block colour system | 12 catalogue blocks with 8.5% `color-mix` tints + 3.5px inset accent. Semantic `data-block` attributes. |
| Typography | Inter/Roboto with proper font-weight hierarchy (400/500/600/700). Monospace filename column. |
| Dark mode | Pre-paint inline script prevents flash. Full token swap. Tabulator theme swap. localStorage persistence. |
| Accessibility | 41+ ARIA attributes, roving tabindex on tab groups, focus trap in row details drawer, `prefers-reduced-motion` respected, visible `:focus-visible` rings, 44px touch targets on mobile. |
| Mobile-first browse | Phone-optimized work cards, discovery rails, tap-friendly facet chips, full-screen drawer on phones. |

### ⚠️ Issues Found

**W1 — CSS Duplication in §14 (MEDIUM, ~400 lines)**  
The `@media (min-width: 721px) { html.browse-active ... }` block in `docs/style.css` (§14 Desktop Browse Mode) duplicates nearly every mobile browse rule at identical or near-identical values. This creates a maintenance hazard where editing mobile rules requires a matching edit 400+ lines later.  
**Recommendation:** Extract shared base classes into a non-viewport-scoped block, then override only the layout differences (grid columns, padding values) inside each media query. Could reduce CSS by ~350 lines.

**W2 — Duplicate JS Functions (LOW)**  
`escapeRegex()` and `renderHighlightedText()` are defined in both `docs/js/formatters.js` (exports) and `docs/app.js` (local closure). The formatters.js versions are exported but never imported by app.js — app.js redefines them with a closure over `activeSearchQuery`.  
**Recommendation:** Remove the duplicate definitions from `docs/app.js` and import from formatters.js, or remove the unused exports from formatters.js.

**W3 — `!important` Display Overrides (LOW)**  
Several rules require `!important` to fight HTML `hidden` attribute:
- `.review-toolbar[hidden] { display: none; }`
- `.facet-bar[hidden] { display: none; }`
- `.mobile-browse[hidden] { display: none !important; }`
- `#blank-rows-toggle-wrap[hidden] { display: none !important; }`

These are defensive but indicate CSS specificity conflicts between the base layout rules and the HTML hidden attribute.  
**Recommendation:** Acceptable pattern for component libraries but document the `!important` rationale in comments.

**W4 — No Lighthouse Budget (NICE-TO-HAVE)**  
No automated Lighthouse performance/accessibility budget exists. The site is a static SPA with SRI-pinned dependencies, so performance should be excellent, but automated measurement would catch regressions.

### Score Breakdown

| Sub-area | Score | Notes |
|---|---|---|
| Color system | 9 | Neutral tokens, block washes above perception threshold, dark mode pre-paint |
| Typography | 8 | Good hierarchy, monospace filename, minor: no system font fallback chain test |
| Layout | 8 | Responsive breakpoints at 720px/900px, flexbox/grid hybrid. §14 duplication is debt. |
| Accessibility | 8 | ARIA, focus trap, reduced-motion, keyboard nav. No automated axe-core scan. |
| Mobile UX | 9 | Work cards, discovery rails, full-screen drawer, tap-friendly targets. |

---

## 2. Full-Stack Development Audit (Score: 8.5/10)

### ✅ Strengths

| Area | Evidence |
|---|---|
| Two-lane architecture | Raw pipeline (`process_data.py`) and curated pipeline (`build_research_master.py` + `build_catalogue_pages.py`) are cleanly separated. |
| Deterministic builds | Every generator has a `--check` mode; the build fails if outputs drift from inputs. No runtime database. |
| Delivery contract | Content-versioned URLs (12-char SHA-256), visible footer build ID, `build-manifest.json` with full asset + data hashes. `FrontendDeliveryContractTests` enforces freshness. |
| Module extraction | `docs/js/config.js` (278 lines) and `docs/js/formatters.js` (143 lines) cleanly extracted. Pipeline split into `pipeline/` package (helpers, enrichments, validators, relationships). |
| No console.log | Zero `console.log` in production code. Only `console.info`/`console.error` for diagnostics. |
| Clean JS syntax | `node --check` passes on app.js, config.js, formatters.js, playwright.config.js, and all spec files. |

### ⚠️ Issues Found

**F1 — app.js Monolith (MEDIUM, 2,439 lines)**  
Despite the config/formatters extraction, `docs/app.js` still handles 15+ distinct concerns in a single IIFE:
- Data loading, column definitions, column width measurement
- Table init, row formatter, work-family striping
- Global search, facet filtering, review filtering
- Mobile browse mode, discovery rails, work cards
- Series landing browser
- Catalogue overview (hero, stats, series strip)
- Dark mode toggle
- CSV export (desktop + mobile fallback)
- Row details drawer with focus trap
- Column menu, expert toggle, settings menu
- Keyboard shortcuts (/, j, k, y, ?)
- Grid state persistence (sort, scroll, facets)
- View summary, view jump navigation
- Active filter chips

**Recommendation:** Extract into 4-5 modules:
- `table.js` — Tabulator init, column builder, row formatter, striping
- `filters.js` — Search, facets, review filter, active filter chips
- `mobile.js` — Browse mode, work cards, discovery rails
- `navigation.js` — View switching, series landing, catalogue overview
- `drawers.js` — Row details, shortcuts overlay

**F2 — Stale Config/Formatters Version Hashes (LOW)**  
`app.js` line 16-22 imports config.js and formatters.js with manual `?v=` hashes:
```js
from "./js/config.js?v=5189225f358d";
from "./js/formatters.js?v=fe5e058c851f";
```
These are NOT tracked in `build-manifest.json` (which only tracks app.js and style.css). The `FrontendDeliveryContractTests` does not enforce their freshness. If config.js or formatters.js change without updating these hashes, browsers serve stale cached modules.  
**Recommendation:** Add config.js and formatters.js hashes to build-manifest.json and extend the contract test.

**F3 — Hardcoded Row Count in Deploy Workflow (BLOCKER for deploy)**  
`.scoreboard/manual-workflow-edits.md` `deploy_pages.yml` snippet contains:
```bash
test "$(jq length /tmp/live-master.json)" -eq 362
```
But the current master is **363** rows (row 373 added 2026-08-10). This deploy assertion will fail.  
**Recommendation:** Update to 363 or better, read the expected count from `docs/catalogue-meta.json`.

**F4 — CSP `style-src 'unsafe-inline'` (LOW, documented debt)**  
Required for the dark-mode/theme toggle dynamic styles. `script-src` is properly hash-pinned and Tabulator is SRI-pinned. Documented in scoreboard as accepted debt.

**F5 — Root .md Count (18 vs target 12)**  
18 root .md files vs the 12-file consolidation target. 6 additional files:
- `EDITION_MEDIATION_PROPOSAL_019fea62.md` — could archive after merge
- `IMPLEMENTATION_SUMMARY_019fea62.md` — could archive after merge
- `TEMP_AUDIT_RESPONSE.md` — should archive
- `TEMP_FIX_019fea62_mobile_white_highlights.md` — should archive
- `TEMP_RESPONSE_019fea62.md` — should archive
- `PR_60_BODY.md` — could archive

**Recommendation:** Archive the 3 TEMP_ files and PR_60_BODY to `archive/`.

### Score Breakdown

| Sub-area | Score | Notes |
|---|---|---|
| Architecture | 9 | Two-lane, deterministic builds, --check modes, pipeline package |
| Code quality | 8 | 0 lint issues, no console.log, module extraction started but incomplete |
| Error handling | 8 | AbortController for tab changes, try/catch throughout, graceful fallbacks |
| Security | 8 | CSP, SRI, hash-pinned scripts, no inline scripts except pre-paint dark mode |
| Testing | 9 | 147 offline + 25 browser specs, 90% coverage, style contrast guards |
| CI/CD | 7 | Comprehensive CI but Pages ungated; deploy workflow unpublished |

---

## 3. Data Engineering Audit (Score: 9.0/10)

### ✅ Strengths

| Area | Evidence |
|---|---|
| Data integrity | All 363 master records verified: 0 duplicate UUIDs, 0 orphan relationships, 0 blank-required fields. |
| Reconciliation | `reconcile_research_master.py --check` passes — ledger/master/outputs all in sync. |
| Idempotent builds | Every `--check` mode is idempotent: running the generator produces no diff vs committed outputs. |
| Reviewed overlays | Owner overrides go through `data/master_year_overrides.csv`, `data/master_notes_overrides.csv`, `data/edition_notes.csv` — never hand-edits to generated files. |
| Display order | `data/catalogue_display_order.csv` is a dense 1..n covering of all 363 masters; build fails otherwise. |
| Test coverage | 90% total (78–100% per module). Critical paths at 93–99% (build_research_master 93%, reconcile 99%, sync 96%). |

### Verified Counts (Independent Re-derivation)

| Metric | Expected | Found | Status |
|---|---|---|---|
| Raw rows | 374 | 374 (docs/data.json) | ✅ |
| Master rows | 363 | 363 (docs/master.json) | ✅ |
| Exclusions | 75 | 75 (docs/master-exclusions.json) | ✅ |
| Source overrides | 134 | 134 (docs/source-overrides.json) | ✅ |
| Promoted candidates | 40 | 40 (docs/manual-candidates.json) | ✅ |
| Product relationships | 340 | 340 (docs/product-relationships.json) | ✅ |
| Series compilations | 7 | 7 (docs/series-compilations.json) | ✅ |
| Work families | 339 | 339 (pipeline output) | ✅ |
| Veritas products | 191 | 191 (docs/veritas-products.json) | ✅ |
| Hay House products | 29 | 29 (docs/hayhouse-products.json) | ✅ |
| Audible products | 26 | 26 (docs/audible-products.json) | ✅ |
| International products | 38 | 38 (docs/international-products.json) | ✅ |
| Filename proposals | 363 | 363 (docs/filename-proposal.json) | ✅ |
| Edition notes | 2 | 2 (pipeline output) | ✅ |
| Empty review lanes | 2 (official-discovery, new-work-review) | 0 + 0 | ✅ |

### ⚠️ Issues Found

**D1 — 3 Temporary Files in Root (LOW)**  
`TEMP_AUDIT_RESPONSE.md`, `TEMP_FIX_019fea62_mobile_white_highlights.md`, `TEMP_RESPONSE_019fea62.md`
are session outputs that should be archived to `archive/` to keep the root clean.

**D2 — `pipeline/helpers.py` Coverage at 78% (LOW)**  
The lowest module coverage. Lines 103-118 are uncovered — these are the CSV file-reading helpers
that are exercised through the generators but not directly tested. Not a critical gap since
the generators' `--check` modes verify their outputs.

**D3 — Manual Leads Count Inconsistency (DOCUMENTATION)**  
The handoff notes mention "2 manual leads" then "4 manual leads" in different places. The actual
file `data/research_manual_leads.csv` has 4 rows. The README's "2 manual leads" reference is stale.

### Score Breakdown

| Sub-area | Score | Notes |
|---|---|---|
| Schema design | 9 | Clean separation of master, candidates, exclusions, overrides, families |
| Data integrity | 9 | Zero duplicates, zero orphans, all counts match across artifacts |
| Build pipeline | 9 | Deterministic, idempotent, --check enforced, 147 tests |
| Provenance | 9 | Year source, research column, legacy title, edition notes |
| Test coverage | 9 | 90% total, critical paths 93-99% |
| Documentation | 8 | Excellent field semantics docs; minor handoff count drift |

---

## 4. Cross-Cutting Findings

### 4.1 Frontend Modularization Roadmap

The config.js/formatters.js extraction was a good start. The remaining app.js monolith (2,439 lines)
should be further split. A suggested module map:

```
docs/js/config.js       — 278 lines (done)
docs/js/formatters.js   — 143 lines (done, has duplicate exports)
docs/js/table.js        — ~400 lines (column builder, width engine, init, row formatter)
docs/js/filters.js      — ~300 lines (search, facets, review filter, chips)
docs/js/mobile.js       — ~400 lines (browse mode, cards, discovery)
docs/js/navigation.js   — ~350 lines (view switching, series, catalogue overview)
docs/js/drawers.js      — ~200 lines (row details, shortcuts overlay)
docs/app.js             — ~400 lines (boot, wiring, dark mode, export, settings)
```

### 4.2 Deployment Pipeline Gap

The P0 owner-action remains the highest-risk item:
1. Pages deploys independently of CI (legacy branch deployment)
2. PRs #48–#52 merged before CI completed, causing the 2026-08-10 site-down incident
3. The deploy workflow in `.scoreboard/manual-workflow-edits.md` needs the hardcoded row count
   fixed (362 → 363) and should be applied by the owner

### 4.3 Security Posture

| Check | Status | Notes |
|---|---|---|
| CSP header | ✅ | Strict `default-src 'self'`, `script-src` hash-pinned |
| SRI on CDN deps | ✅ | Tabulator CSS and JS both have `integrity` + `crossorigin` |
| `style-src 'unsafe-inline'` | ⚠️ | Required for dark-mode toggle; low risk since no user-generated CSS |
| No user input in DOM | ✅ | Search highlighting uses `textContent`, never `innerHTML` |
| External links | ✅ | All `target="_blank"` have `rel="noopener noreferrer"` |
| No credentials in code | ✅ | GitHub auth via CLI; no tokens/keys in repo |

---

## 5. Prioritized Recommendations

| Priority | Area | Recommendation | Effort |
|---|---|---|---|
| P0 | CI/CD | Owner applies CI-gated Pages + required status checks | Owner action |
| P1 | CSS | Extract shared browse-mode rules from §14 (~350 line reduction) | 2 hours |
| P1 | JS | Add config.js/formatters.js to build-manifest + contract test | 30 min |
| P1 | Deploy | Fix hardcoded 362→363 in deploy_pages.yml workflow | 5 min |
| P2 | JS | Remove duplicate escapeRegex/renderHighlightedText | 15 min |
| P2 | Docs | Archive 3 TEMP_ files + PR_60_BODY to archive/ | 10 min |
| P2 | Docs | Update stale "2 manual leads" → "4 manual leads" in handoff | 5 min |
| P3 | JS | Further modularize app.js into 5-4 modules | 4-6 hours |
| P3 | A11y | Add automated axe-core scan to CI | 1 hour |
| P3 | Perf | Add Lighthouse budget step | 30 min |

---

## 6. Verification Summary

```
✓ Python: All 6 .py files compile successfully
✓ Tests:  147/147 pass (3.9s)
✓ Coverage: 90% total (78-100% per module, floor 85%)
✓ --check: All 6 generator modes pass
✓ JS syntax: app.js, config.js, formatters.js, playwright.config.js, all specs
✓ Data: All 20 JSON sheets verified against expected counts
✓ Security: CSP, SRI, no inline dangerous patterns
✓ Lint: No TODO/FIXME/HACK markers in production code
```

---

*Audit completed by Arena Agent Mode — 2026-08-10 00:00 UTC*
