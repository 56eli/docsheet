# Full-Stack & Catalogue Audit — 2026-08-09 (Arena Deep Pass)

**Auditor:** Arena.ai Full-Stack / Data-Engineering agent  
**Repository:** `56eli/docsheet`  
**Branch audited:** `arena/019fe5d4-docsheet` at `bbe8b01` (`main` HEAD — post D-01 collapse)  
**Date (UTC):** 2026-08-09  
**Scope:** raw CSV → ledger → curated master → inventories → candidate/edition registries → relationships → taxonomy → work families → filename proposal → generated `docs/*.json` → frontend (`docs/index.html`, `docs/app.js`, `docs/style.css`) → tests → CI/CD → living documentation  
**Method:** fresh reads of every generator (`process_data.py`, `build_research_master.py`, `build_catalogue_pages.py`, `reconcile_research_master.py`, `map_series_taxonomy.py`, `sync_inventory_mirrors.py`, `fetch_veritas_catalogue.py`, `_common.py`), fresh venv (`pandas 3.0.5 / numpy 2.4.6 / coverage 7.15.4 / node 22`), re-ran all six `--check` modes, `python -m unittest discover tests` (125 tests), `coverage report`, `node --check`, `npm ci && npm audit`, plus independent pandas probes that bypass the project's own validators (duplicate detection, extension matrix, work-id coverage, year/month sanity, URL de-duplication, CSV↔JSON parity, facet/label rendering).

> This is a read-only audit on `bbe8b01`. It does not modify data or code; it identifies inconsistencies for owner triage. Prior audits at `archive/` and the declared-current pair (`FULL_STACK_AUDIT_2026-08-08_ARENA.md`, `FULL_STACK_AUDIT_2026-08-08_ARENA_FRESH_EYES.md`) plus `NEXT_AGENT_HANDOFF.md` and the independent pass at `FULL_STACK_AUDIT_2026-08-08_INDEPENDENT.md` remain the baseline. Section 10 postscript of that independent audit already applied the D-01 collapse; this pass verifies that post-fix state and surfaces what remains.

---

## 1. Executive Verdict

**The generated catalogue at `bbe8b01` is internally reproducible and CI is green when dependencies are installed.** All six `--check` modes pass, `125/125` deterministic tests pass, coverage is `91%` (2062 stmts, lowest module `88%`, floor `85%`), JS syntax is clean, `npm audit` shows `0` vulnerabilities, CSP + SRI are correct, raw→ledger→master accounting is airtight (`374` raw → `299` adopted `item` + `75` excluded; `299 + 39` promoted manual + `24` promoted editions = `362` masters), and zero duplicate UUIDs / catalogue codes / filenames, zero orphaned master Veritas URLs remain.

The D-01 duplicate-row collapse (retiring streaming masters `225/226/227` and keeping promoted DVD masters `311/310` with streaming in `reference_url_1`) is **verified correct**: `365 → 362` masters, `281 → 278` codes, `72 → 75` exclusions, `336 → 333` derived primaries, `343 → 340` total relationships, `341 → 338` work-family memberships, `365 → 362` filenames all reconcile, and every `--check` passes.

However this pass surfaced **1 new medium catalogue/display inconsistency**, plus **3 carry-over medium build/code inconsistencies** and **5 low/trivial doc & setup drifts** that are not caught by the check suite because they are semantic, cross-table case-sensitivity, or wording issues rather than byte mismatches. None are data-loss/critical, but one is user-visible on 76% of rows.

- **C-01 (Medium, NEW, user-visible):** `owned` is stored as `True` (capital T, from `migration_review_ledger.csv` `proposed_owned=True`) for **274** ledger-derived masters but as `true` (lowercase, from `edition_candidates.csv` / `manual_candidate_promotions.csv`) for **21** candidate-minted masters. The frontend `statusLabel()` and the Owned facet's `buildOptionLabel` only map lowercase `true`/`false` to `Owned`/`Not owned`. Result: **274 rows display the raw string `True` in their badge and filter chips** instead of `Owned`, while the 21 minted rows correctly show `Owned`. `statusClass()` lowercases before colouring, so badge *colour* is still green — only the *label* is wrong — but the documented three-value vocabulary (`true`/`false`/blank) is violated and exports keep mixed case (`True` vs `true`).
- **D-04 (Low/Medium, carry-over):** Masters `359–361` (three academic-book Amazon paperbacks) still store the same Amazon URL in **both** `source_url_amazon` *and* `reference_url_1`. The UI labels `reference_url_1` as "Streaming" and the mobile card renders a **Stream** action that opens a paperback purchase page. Correctly left open for triage in `NEXT_AGENT_HANDOFF.md`; the earlier "369–372 precedent" justification was inaccurate — those four rows now correctly have blank `reference_url_1`.
- **B-01 (Medium, carry-over):** Two Spanish Audible titles (`Disolver el ego`, `El nivel más alto de iluminación`) are hardcoded in `build_catalogue_pages.py:798–814` into `international-products.json` (`36` CSV rows → `38` JSON rows), bypassing the "generated from committed CSV inputs" invariant. Functional but violates the review-gated input principle.

Everything else is either owner-accepted (master `265`'s verbatim malformed Veritas URL, `198X` Office-Series convention, 17 blank years with labelled `year_source`), review-gated by design (empty `official_discovery_queue.csv` / `new_work_review_queue.csv` as standing intake lanes), or historical doc hygiene.

---

## 2. Verification Matrix (re-run 2026-08-09)

| Check | Result | Notes |
|---|---|---:|
| `python -m py_compile *.py` | **PASS** | 10 root modules |
| `process_data.py --check` | **PASS** | `374` raw rows, `8` view columns after trimming 5 always-empty columns; requires `pandas` (`pip install -r requirements.txt --break-system-packages` in sandbox) |
| `build_research_master.py --check` | **PASS** | `362` items, `75` exclusions, `134` approved overrides |
| `build_catalogue_pages.py --check` | **PASS** | `362` Everything rows |
| `reconcile_research_master.py --check` | **PASS** | 0 unexplained extras / absent / field diffs |
| `map_series_taxonomy.py --check` | **PASS** | `324` approved mappings cover `324` master IDs (see §4 D-07) |
| `sync_inventory_mirrors.py --check` | **PASS** | All 191 Veritas mirrors match; `normalized_title_match_count == len(matched_master_uuids)` |
| `python -m unittest discover tests` | **125/125 PASS** | `~3.1s`, deterministic, `pip -c requirements-ci.txt` pins consulted |
| Coverage | **91% PASS** | 2062 stmts, lowest module `88%`, floor `85%` (`_common 100%`, `reconcile 99%`, `sync 96%`, `fetch 95%`, `process 91%`, `build_catalogue 89%`, `build_master 88%`, `map_taxonomy 88%`) |
| `node --check` (`app.js`, `playwright.config.js`, all 3 specs) | **PASS** | |
| `npm ci` / `npm audit` | **PASS / 0 vulns** | `tabulator 6.5.2` pinned, SRI on CSS + JS, `@playwright/test 1.62.1` |
| Raw CSV ↔ ledger provenance mirrors | **374/374, 0 mismatches** | Every raw row accounted (299 `item` + 31 `blank_separator` + 21 `series_context` + 10 `research_note` + 7 `duplicate` + 5 `source_context` + 1 `needs_review`) |
| Published CSV↔JSON / JSON↔JSON parity | **13 direct pairs exact, 2 expected enrichments** | Enrichments: `international` `36→38` (B-01 hardcoded rows), `product-relationships` `7 stored → 340 rendered = 333 derived primary + 7 stored related_material` by design |
| Local HTTP smoke (`/docs/`, `master.json`, `catalogue-meta.json`, `data.json`) | **PASS 200** | `master.json 362`, `catalogue-meta.json 19 keys`, `data.json 374` |
| CSP inline-script hash + Tabulator SRI | **PASS** | `sha256-qULmN/IfgO0KcdvNpANXyfZHBIgYfm4o368jeDomJJY=` matches; 3 SRI attributes (light CSS, dark CSS, JS) |
| Latest `main` CI / Pages | **PASS** (historical) | Independent audit cites `31274407803` green, Pages `built` HTTPS `main:/docs`; this sandbox could not reach GitHub API (expected) |
| Local Playwright | **BLOCKED** | Chromium bundle absent in sandbox; CI is authority (18 tests across 3 specs). `node --check` substitutes for syntax. |
| Live Veritas `--check` | **BLOCKED** | TLS EOF to `veritaspub.com` from sandbox (documented); offline replay tests cover fetcher retry/matching |

---

## 3. Recomputed Current Catalogue State (`bbe8b01`)

| Area | Value |
|---|---:|
| Raw spreadsheet rows | **374** |
| Curated master (`data/research_master_draft.csv` + `docs/master.json`) | **362** rows — `306` lecture / `40` book / `8` discussion / `7` highlight / `1` other |
| UUID range / gaps | `1–372`, gaps `{225, 226, 227, 246, 249, 264, 281, 284, 302, 309}` — 10 retired duplicates, never reissued |
| Catalogue codes | **278** unique, 0 duplicates; `36` lecture/discussion rows intentionally codeless (17 blank-year Volume Series + under-investigation + 19 candidate/edition rows blank-at-minting). Office Series `198X` rows **do** carry `LECTURE-198X-001 … -016` (16 rows) |
| Work families | **338** approved `work_families.csv` memberships + **24** minted `edition_promotions.csv` memberships = **362/362** masters covered, 0 uncovered, 0 overlap |
| Veritas inventory | **191** products: `186` `matched_by_primary_source` / `5` `excluded_related_material` |
| Master Veritas URLs | `333` unique masters populate `source_url_veritas`; **0** orphans (every URL present in inventory; multi-part works share one URL across their 2–3 part rows → 76 URL groups with >1 master, by design) |
| Relationships rendered | **340** = `333` derived primary (one per unique Veritas URL-bearing master) + `7` stored `related_material` across 7 products |
| Series compilations | **7** reviewed |
| Source overrides | **134** all `approved` (71 veritas, 26 hayhouse, 21 amazon, 10 audible, 6 nightingale-conant) |
| Manual candidates | **39/39** promoted; **24/24** edition candidates promoted |
| Manual leads | **2** (outside master) |
| Official inventories | Veritas 191, Hay House 29 (27 matched + 2 excluded), Audible 26 (24 matched + 2 excluded), International 36 queue → 38 JSON (36+2 hardcoded) |
| Series taxonomy | `186` products mapped at build → **324** approved master IDs covered; review queue **0** rows |
| Filename proposal | **362** rows; **362** unique safe names, **362** unique display names; bracket convention `safe [1-3]` / `display [1/3]` holds; extension↔format clean (DVD→mp4, CD→mp3, audiobook→m4b, book→pdf, streaming→mp4) |
| Ownership | `274` `True` (capital) + `21` `true` (lower) + `25` `False` + `42` blank — see C-01. Ledger `proposed_owned` is `True/False/""` (281/25/68); edition candidates use `true/""` (19/5) |
| Year edge cases | **17** blank years (13 intentional Volume Series + 4 under investigation), **16** `198X` Office-Series rows, 0 month-without-year, 0 invalid months, 0 book-months |
| Frontend contract | **19** HTML tabs ↔ **19** `VIEWS` ↔ **19** sheet JSONs + `catalogue-meta.json` + `data.json` (raw) = **21** JSON files; VIEWS set matches `docs/*.json` exactly |

---

## 4. Catalogue / Data Findings

### C-01 — `owned` stored with mixed capitalisation; 274 rows display raw `True` instead of `Owned` (NEW)

**Severity:** Medium — user-visible badge/filter label inconsistency, no data loss, violates documented vocabulary  
**Evidence:**
- `migration_review_ledger.csv:proposed_owned` = `True` (capital T) for 281 ledger items; `data/edition_candidates.csv:proposed_owned` = `true` (lowercase) for 19 edition rows; `data/manual_candidate_promotions.csv` promotions also carry `true`/`false` lower.
- `build_research_master.py:1355` copies `row["proposed_owned"]` verbatim for ledger rows → master `owned=True`; `:1243` / `:1406` copy `candidate["proposed_owned"].strip()` verbatim for minted rows → `owned=true`. No normalisation.
- Validators: manual/edition candidates validate `∉ {"", "true", "false"}` and would reject `True` — but ledger rows bypass that validator (no `proposed_owned` check on the ledger path), so `True` survives unchecked.
- `docs/master.json`/`data/research_master_draft.csv` therefore contain **274 `True`**, **21 `true`**, **25 `False`**, **42 `""`**.
- Frontend: `docs/app.js:406–430` — `statusLabel()` returns `Owned` only when `value === "true"` (strict lower), otherwise falls through to `value.replace(/_/g, " ")` → badge shows literal `True`. `buildOptionLabel` for the Owned facet has the same lower-only test, so the filter chip also reads `True`. `statusClass()` *does* lowercase before testing (`normalized === "true"`), so badge colour is still `status-approved` (green) — the defect is label-only, not colour.
- `README:215–218` claims three values `true`/`false`/blank and says the site renders `Owned`/`Not owned` — currently false for the 274 capital-`True` rows.

**Fix (owner ruling, one-line):** normalise at write time in `build_research_master.py` — `row["proposed_owned"].strip().lower()` for the ledger loop (and similarly ensure `False → false`), or normalise `statusLabel`/`buildOptionLabel` to lowercase before comparing. Either restores the documented vocabulary; the build-side fix also cleans exports. Regression: assert `set(master owned) ⊆ {"", "true", "false"}`.

### D-04 — Three Amazon paperback URLs stored in both `source_url_amazon` and `reference_url_1` (carry-over, still open)

**Severity:** Low/Medium — semantic column misuse + UX mislabel  
**Evidence:** masters `359` (`Orthomolecular Psychiatry…`), `360` (`Qualitative and Quantitative…`), `361` (`Dialogues on Consciousness…`) have `source_url_amazon == reference_url_1 == https://www.amazon.com/...` (paperback purchase page). `reference_url_1` is labelled **Streaming** in `docs/index.html` / `docs/app.js` and the mobile card's `Stream` action opens that Amazon page. The earlier resolution note cited masters `369–372` as precedent — they now correctly have **blank** `reference_url_1` (their Audible/Hay House URLs live only in the dedicated source columns), so the precedent does not apply.

**Options for ruling:** (a) clear `reference_url_1` on `359–361` (curated `source_url_amazon` is sufficient), or (b) keep the duplication explicitly and relabel the UI's `reference_url_1` from "Streaming" to "Reference / External" — (a) matches every other `source_url_amazon` row (18 others have blank `reference_url_1`).

### D-03 (was) / D-07 — Streaming `format_detail` vocabulary noise

**Severity:** Low — cosmetic inconsistency  
**Evidence:** `312` (`Permanent Inner Peace`) has `format_detail="streaming discussion/interview"`; `313` (`What is Real Success?`) has `format_detail="one disc; ~60 min; streaming"`. The other 17 `format=streaming` rows have blank `format_detail` (correct, since format already conveys streaming and other streaming rows do not carry a part marker). The two noisy values are leftover from the pre-2000 streaming→DVD collapse period and do not affect inventory/relationship logic.

### D-05 — `data/edition_candidates.csv` uses CRLF line endings

**Severity:** Trivial — correctness OK, diff hygiene  
**Evidence:** `cat -A` shows `^M` on all 25 lines; every other committed CSV (23/24) uses LF. `csv.DictReader` tolerates it, so `--check` passes, but `git diff` and line-count tools show spurious `^M`.

### Clean / verified (no change needed)

- Multi-part DVD rows correctly share one Veritas URL across 2–3 part rows (`76` groups); each part retains `Part 1/2/3` in `format_detail` and `[1-3]` filenames — C-01/C-02 of the earlier Arena audit resolved.
- Year/month logic: 0 month-without-year, 0 invalid months, 0 book-months; blank-year rows (Volumes + 4 under-investigation) correctly omit year prefix in filenames; `198X` Office Series `c. 1980s` display with raw-value sort is deterministic.
- `reconcile_research_master.py` reports `0` unexplained extras / absent / field diffs; raw→ledger mirrors `374/374`.
- `362` unique safe filenames and `362` unique display filenames; display uses `[1/3]` while safe uses `[1-3]` per policy, with publisher-suffixed `Power vs Force (Audible).m4b` / `(Veritas).m4b` for the same-work/same-year/same-carrier collision (274 `True` aside, the policy is honoured).

---

## 5. Build / Code Findings

### B-01 — Two Spanish Audible rows hardcoded into `build_catalogue_pages.py:798–815` (carry-over)

**Severity:** Medium (design invariant, not data corruption)  
**Evidence:** `intl_items` is seeded from two `audible_official_products.csv` rows whose `official_title` is `Disolver el ego` / `El nivel más alto de iluminación`, then `intl_queue` is appended. Result `international-products.json` has `38` rows from `36` CSV rows. The `map - veritas catalogue` workflow's review-only invariant ("Pages JSON generated from committed CSV inputs") is bypassed for this one view. Portable fix: move those two rows into `data/international_discovery_queue.csv` (or a dedicated `data/audible_spanish_products.csv`) and delete the hardcoded branch, so `36→36` or `38→38` parity holds and `catalogue-meta.json` can publish the count.

### B-02 — `docs/catalogue-meta.json` lacks international counts (carry-over)

**Severity:** Low  
**Evidence:** `catalogue-meta.json` publishes `master_items`, `veritas_official_products`, `hayhouse_official_products`, `audible_official_products`, but no `international_*` key, while `docs/international-products.json` holds `38` rows. Every other sheet's count appears in the meta; International is the exception. Adding `international_products` / `queue_created` parity would make the meta a complete manifest (and would pair with fixing B-01).

### B-03 — `ledger proposed_owned=True` bypasses the lower-case validator (root cause of C-01)

**Severity:** Medium (build) — see C-01. Ledger path has no `proposed_owned ∈ {"", "true", "false"}` check; candidates Editions enforce it, so the inconsistency is tolerated.

### B-04 — `actions/checkout@v7` / `setup-python@v7` / `setup-node@v7` / `upload-artifact@v7` in `.github/workflows`

**Severity:** Low (governance, not failure — workflows currently pass)  
**Evidence:** `ci.yml` and `map_veritas_catalogue.yml` pin `@v7`. The latest published majors are `actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`, `actions/upload-artifact@v4` (v7 does not exist at `github.com/actions/*` as of 2026-08). The runner resolved them in the last cited CI run (`31265700227`), but the pin will break when GitHub retires the alias. Pin to the real latest majors and keep Dependabot/Renovate watching them.

---

## 6. Frontend / UX Findings

### F-01 — Owned badge shows raw `True` for 76% of rows (consequence of C-01)

**Severity:** Medium — every tab that renders the `owned` column, the Owned facet, the drawer detail view, and CSV exports expose the case mix.

### Otherwise clean / verified

- **Race-safe `activateView()` token** (`docs/app.js:1938–2005`): `++viewActivation` + `AbortController` + staleness check `if (activation !== viewActivation) return` before committing rows/timestamps — the F-01 race of prior audits remains fixed; delayed-route Playwright proves stale responses cannot overwrite the current view.
- **Focus trap covers all modal links** — traps `every visible focusable descendant` including official/evidence anchors, Tab + Shift+Tab cycle correctly.
- **Mobile Browse mode** defaults at `max-width:720px`: work-group stacks from `work_id`, expandable parts, Source/Stream quick links, persistent Spreadsheet/Browse toggle, Series + Timeline rails writing to shared `activeFacets` state — single `master.json` source, no second data layer.
- **Facet persistence, row striping, monospace filenames, carrier dots, copy actions, keyboard shortcuts (`/`, `j/k`, `y`, `?`)** all wired; `VIEWS` contract is `19` tabs ↔ `19` JSON sheets (plus `catalogue-meta.json` and raw `data.json`).
- **CSP** `default-src 'self'`, script `sha256-qULmN/…oJJY=` matches inline dark-mode bootstrap; **SRI** pinned for Tabulator `6.5.2` light CSS `sha384-7L13y…`, dark CSS `sha384-IjPQx…`, JS `sha384-ZlfxH…`; only 5 `innerHTML` uses and all are static strings; no secrets in tracked files.

---

## 7. Project-Setup / Documentation Findings

### DOC-01 — `NEXT_AGENT_HANDOFF.md` test-count / browser-suite text stale (carry-over DOC-02)

**Severity:** Low — historical sections contradict the current postscript  
**Evidence:** §1 / §2 still say `ux-enhancements.spec.js (7 browser tests; suite now 16 browser tests)` and `suite (3 spec files / 16 tests: column-layout 4, csv-export 5, ux-enhancements 7)`. Actual suite is **18** tests across 3 specs (`column-layout 4` + `csv-export 5` + `ux-enhancements 9` — the 9th is the keyboard `/` test added with the facet UX). Lines `597` / `487` in the postscripts correctly say 18; the top summary and `§2 sandbox block` were not bumped. The count appears ~15 more times in historical log entries (103→125 progression) — those are archival and fine; the **current-header** numbers should read 18.

### DOC-02 — `NEXT_AGENT_HANDOFF.md` §6 still lists D-04 precedent as `359–361/369–372` (carry-over DOC-03)

**Severity:** Low — inaccurate precedent citation  
**Evidence:** Final bullet says duplicate URL storage is "consistent by precedent … `359–361/369–372`". Only `359–361` duplicate (`source_url_amazon == reference_url_1`); `369–372` have had blank `reference_url_1` since the edition-audio deduplication, so the `369–372` half is false.

### DOC-03 — `INSTRUCTIONS.md` curated-catalogue pointer now correct; `README` documentation-layout now correct

**Verified fixed:** `INSTRUCTIONS` now points at `FULL_STACK_AUDIT_2026-08-08_ARENA.md` + handoff §6 (not `archive/PROJECT_STATE_AUDIT.md`); `README` documentation-layout lists the declared-current pair, not an archived `2026-08-04_FINAL_358_V2`; `.coveragerc` comment now says "ten pipeline modules" (was eight); streaming log now says `Filled reference_url_1 on 53 master rows from 36 approved Veritas streaming products` (was misleading "56 URLs").

### DOC-04 — Remaining hygiene (informational)

- `archive/` now 56 files with `archive/README.md` explicitly marking its contents non-normative and indexing the 4 superseded root audits moved via `git mv` — current root keeps only the declared pair.
- Source CSV hygiene carried over knowingly: filename with spaces, artifact header row `archive clbs` + real header on line 2, 5 always-empty columns trimmed as view-only, 31 fully blank rows — all documented and handled.
- Issue `#18` (ownership cross-check vs lak.nz Drive) remains open since `2026-08-03`; needs triage.
- `main` branch-protection / required-status-checks could not be observed with this token (403 on branch-protection API) — governance is the only setting not independently verifiable. The raw-only `paths-ignore` + separate `Update Spreadsheet` workflow design still intentionally avoids racing CIs; PR CI is the intended guard, so branch protection must require that CI.

---

## 8. What Remains Genuinely in Good Shape

- **Review-loop discipline is exceptional:** every write path is check-gated, tamper-tested, deterministic (`run-twice` where claimed), and CI enforces all of it plus the `85%` floor. No committed artifact desynchronised from its inputs in this pass.
- **Raw→ledger→master accounting airtight:** `374 → 299 + 75` with every exclusion disposition/reason stated; the one `needs_review` raw row (371 — provenance note for master 361) and 31 blank separators are tracked.
- **Provenance complete:** `year_source` labels on 100% of rows justification-classed; `legacy_title` preserves verbatim source text; URL overrides are evidence-keyed and all `approved`; Veritas inventory mirrors re-derived after master title/URL changes.
- **Identifier hygiene:** UUID gaps documented (10 retired duplicates, never reissued), catalogue-code minting rule (lecture/discussion-only, only when year known at minting) explains the 36 intentionally codeless rows, and `198X` (`LECTURE-198X-001 … -016`) is explicit.
- **CI design:** least-privilege `contents: read`, concurrency groups, raw-only `paths-ignore` to avoid racing the `Update Spreadsheet` writer, `requirements-ci.txt` pins the exact tested set (`pandas==3.0.5`, etc.), coverage gate enforced, Chromium installed and `18` browser tests run in CI.
- **Frontend hygiene:** CSP/SRI correct, no data-bearing `innerHTML`, abort-safe fetch, offline-testable, mobile Browse + rails present.

---

## 9. Recommended Order of Work

1. **C-01 / B-03 — normalise `owned` to lowercase at the ledger write path** (`build_research_master.py:1355` and any other ledger-owned write) or make `statusLabel`/`buildOptionLabel` case-insensitive; add a one-line `assert set(owned) ⊆ {"", "true", "false"}` in the master validator and in tests. One-line fix, user-visible.
2. **D-04 — rule the Amazon `reference_url_1` duplication** on `359–361` (prefer clearing the three `reference_url_1` cells to match the other 18 Amazon rows; one `data/research_master_source_overrides.csv` change → regenerate → `--check`).
3. **B-01 — remove the hardcoded Spanish Audible branch** (`build_catalogue_pages.py:798–814`) and move those two rows into `data/international_discovery_queue.csv` so `international-products.json` becomes fully input-driven; bump `docs/catalogue-meta.json` with international counts (B-02) in the same change.
4. **DOC-01 / DOC-02** — bump the handoff header to `18` browser tests (`9` in `ux-enhancements`) and correct the `369–372` precedent sentence (two doc-only edits).
5. **B-04** — pin GitHub Actions to their real latest majors (`checkout@v4`, `setup-python@v5`, `setup-node@v4`, `upload-artifact@v4`) — or the next published major if newer at merge time — and enable Dependabot for `github-actions`.
6. **D-05** — `unix2dos → dos2unix` on `data/edition_candidates.csv` to normalise `CRLF → LF` (one-line, keeps diffs clean).
7. **D-07** — optionally clear the two noisy streaming `format_detail` values (`312`, `313`) to blank.
8. **Triage Issue #18** and confirm `main` branch protection / required-status-checks outside this token's visibility; optionally vendor Tabulator assets or add a local fallback for CDN resilience (long-standing F-08).
9. Optionally extend Playwright coverage to remaining tabs / dark-mode persistence / settings persistence once visitor feedback arrives.

---

## 10. Reproduction Commands

```bash
python3 -m venv /tmp/dsv
/tmp/dsv/bin/pip install -r requirements.txt -c requirements-ci.txt
/tmp/dsv/bin/pip install -r requirements-dev.txt -c requirements-ci.txt

/tmp/dsv/bin/python -m py_compile *.py
/tmp/dsv/bin/python process_data.py --check
/tmp/dsv/bin/python build_research_master.py --check
/tmp/dsv/bin/python build_catalogue_pages.py --check
/tmp/dsv/bin/python reconcile_research_master.py --check
/tmp/dsv/bin/python map_series_taxonomy.py --check
/tmp/dsv/bin/python sync_inventory_mirrors.py --check
/tmp/dsv/bin/python -m unittest discover tests
/tmp/dsv/bin/coverage run -m unittest discover tests && /tmp/dsv/bin/coverage report

node --check docs/app.js
node --check playwright.config.js
for spec in tests/*.spec.js; do node --check "$spec"; done
npm ci && npm audit
```

`npm run test:e2e` requires Chromium (CI-only in this sandbox; all 18 tests run there). `fetch_veritas_catalogue.py --check` requires live `veritaspub.com` (TLS EOF in sandbox; offline replay tests cover retry/matching).

---

## Appendix — Provenance & Counts Evidence

Raw-row accounting: `374 = 299 item + 31 blank_separator + 21 series_context + 10 research_note + 7 duplicate + 5 source_context + 1 needs_review` (ledger `disposition`).

Work-family accounting: `338` approved `work_families.csv` + `24` approved `edition_promotions.csv` = `362` masters, `0` uncovered (verified via `wf_uuids | ep_uuids == master_uuids`).

Filename: `362/362` safe unique, `362/362` display unique; bracket style verified; extension matrix `DVD→mp4 253`, `CD→mp3 32`, `book→pdf 31`, `audiobook→m4b 27`, `streaming→mp4 19`.

Veritas mirrors: every `matched_master_uuids` semicolon-count equals `normalized_title_match_count`; `matched_master_titles` pipe-count matches; no orphaned master Veritas URLs.

*Prior audits: `FULL_STACK_AUDIT_2026-08-08_ARENA.md` (declared current, kept at root) and `FULL_STACK_AUDIT_2026-08-08_ARENA_FRESH_EYES.md`; earlier passes in `archive/`.*

---

## 11. Post-audit fix applied 2026-08-09 — C-01/B-03 owned vocabulary (this branch)

**Trigger:** user selected "Fix C-01" via the audit follow-up question.

**Change:** normalised the `owned` vocabulary to the documented `true`/`false`/blank lower-case set.

- `build_research_master.py:1243,1355,1406` — `strip().lower()` on every `owned` write path (ledger-derived, manual-promotion, edition-promotion). The ledger path now tolerates both `True` and `true` on input but always emits `true`; candidate paths were already lower and are now defensively lowercased.
- `docs/app.js:429,1406` — `buildOptionLabel` and `statusLabel` now compare `String(value).toLowerCase()` so legacy cached JSON with capitalised `True`/`False` still renders `Owned`/`Not owned` correctly (defensive rendering; data is now lower).
- `migration_review_ledger.csv` — `proposed_owned` column lowercased in place (`281 True → true`, `25 False → false`, 68 blank unchanged) so source vocabulary matches the output vocabulary.

**Regeneration (documented order):** `build_research_master.py` → `build_catalogue_pages.py` (which also rewrites `docs/migration-review.json`); `reconcile`, `map_series_taxonomy`, `sync_inventory_mirrors`, `process_data --check` all re-verified.

**Result:** `data/research_master_draft.{csv,json}` and `docs/master.json` now contain `295 true / 25 false / 42 blank` — `274 True` and `25 False` capitalised values eliminated. Facet chips and badge labels now consistently show `Owned` for all 295 owned rows; exports are lower-case as documented in `README:215`. `ledger proposed_owned` is now also lower.

**Verification:** all six `--check` modes PASS, `125/125` tests PASS, coverage `91%` (lowest module `88%`), `node --check` PASS, `npm audit` 0 vulns. `C-01` is now **resolved**; `B-03` (build validation gap) is also resolved as the build now normalises; `D-04`, `B-01`, `DOC-01/02`, `D-05`, `B-04` remain open as documented in §4–§7 and are unchanged by this fix.


## 12. Post-audit fix applied 2026-08-09 — D-04 Amazon / Streaming column overlap (this branch, second fix)

**Trigger:** user selected "Fix D-04 Amazon duplication" via the audit follow-up question.

**Change:** eliminated the duplicate storage of the same Amazon paperback URL in both `source_url_amazon` and `reference_url_1` for masters `359–361` (`Orthomolecular Psychiatry`, `Qualitative and Quantitative Analysis`, `Dialogues on Consciousness`), which the UI labels **Streaming** and previously rendered as a misleading **Stream** button for a paperback purchase.

- `build_research_master.py:1394` — extended the dedicated-source guard from `audible.com / hayhouse.com` to also include `amazon.com`. Promotion now treats an Amazon `official_product_url` as a curated-source URL (like Audible/Hay House) and leaves `reference_url_1` blank, relying on the approved `research_master_source_overrides.csv` (`candidate:manual-academic-* → source_url_amazon`) to populate the dedicated `source_url_amazon` column.
- No CSV source change required — the three approved `source_url_amazon` overrides (rows 133–135) already held the correct Amazon product links; the promotion previously wrote the same URL into `reference_url_1`, causing the duplication.

**Regeneration:** `build_research_master.py` → `build_catalogue_pages.py`; all other generators unchanged.

**Result:** `data/research_master_draft.{csv,json}` and `docs/master.json` now show `reference_url_1=""` and `source_url_amazon="https://www.amazon.com/…"` for `359–361`; `amazon==reference` duplicates `0` (was `3`). The Everything sheet no longer renders a **Stream** action for these paperbacks, and the "369–372 precedent" cited in the earlier resolution is now accurate — all Amazon-only books (`359–361` and other `source_url_amazon` rows) have blank `reference_url_1`.

**Verification:** all six `--check` modes PASS, `125/125` tests PASS, coverage `91%`, `npm audit` 0. `D-04` is now **resolved**; remaining open items (`B-01` hardcoded Spanish rows, `B-02` meta gaps, `DOC-01/02` handoff wording, `D-05` CRLF, `B-04` Actions pins, `D-07` streaming detail noise) are unchanged and still listed in §4–§7.


## 13. Post-audit fix applied 2026-08-09 — B-01/B-02 international hardcoding + meta gap (this branch, third fix)

**Trigger:** user selected "Fix B-01/B-02 international hardcoding + meta gap".

**Change:** made `international-products.json` fully input-driven and completed `catalogue-meta.json`.

- `data/international_discovery_queue.csv` — added 2 Audible Spanish rows (`Disolver el ego` / `El nivel más alto de iluminación`, `matched_by_title`, `digital`, `Spanish`, `https://www.audible.com/pd/…`) that were previously injected as hardcoded objects in the builder. Queue now `36 → 38` rows.
- `build_catalogue_pages.py:796–825` — removed the hardcoded `if product["official_title"] in ("Disolver el ego", …)` branch that injected those 2 rows from `audible_official_products.csv` into `intl_items`. `intl_items` is now purely `list(intl_queue)` (`38` rows) with no code-side product-title matching. The Audible loop now simply skips non-`unreviewed_official_product` rows (both Spanish rows are `matched_by_title`, so they correctly do not become `candidate_audible`).
- `build_catalogue_pages.py:1011` — added `"international_products": len(intl_items)` to `OUT_META` so `docs/catalogue-meta.json` now publishes `38` for the international sheet, matching every other sheet (previously the only sheet without a meta count). Meta now has `20` keys (was `19`).

**Order note:** previously the 2 Audible rows were prepended (indices 0–1); now they are appended (indices 36–37) in queue order. Content is identical; only order changed (CSV order = JSON order). Re-running the builder with `--check` proves the committed files are now byte-current from the CSV.

**Verification:** all six `--check` modes PASS, `125/125` tests PASS (coverage `91%` on `2059` stmts, was `2062` before removing 3 hardcoded lines), `node --check` PASS, `npm audit` 0. `B-01` and `B-02` are now **resolved**; `CSV 36→38` → `JSON 38` is now `38→38` exact parity (`international` no longer an intentional enrichment). Remaining open items: `DOC-01/02` handoff wording, `D-05` CRLF, `B-04` Actions pins, `D-07` streaming detail noise (all low/trivial).


## 14. Post-audit fix applied 2026-08-09 — Hygiene batch D-05/DOC-01/02/B-04/D-07 (this branch, fourth fix)

**Trigger:** user selected "Run final hygiene batch".

**Changes (all verified, no catalogue count changes except the intended cleanups):**

- **D-05 — `data/edition_candidates.csv` CRLF → LF:** `25` lines `CRLF` normalized to `LF` (`cat -A` shows `$` not `^M$`). No data changed; `git diff` now clean on that file.
- **DOC-01/02 — `NEXT_AGENT_HANDOFF.md` stale wording:**
  - `ux-enhancements.spec.js (7 browser tests; suite now 16)` → `(9 browser tests; suite now 18)` and `suite (3 spec files / 16 tests: column-layout 4, csv-export 5, ux-enhancements 7)` → `(18 tests: 4, 5, 9)` in the current-header §1/§2 blocks (historical log entries at §6 that recount the 16-test era were left as history).
  - Top "Left open for owner triage" bullets for `D-04` and `B-01` marked **RESOLVED in `arena/019fe5d4-docsheet` (2026-08-09)** with the exact file/line provenance, instead of "still sit / still hardcoded".
  - Bottom "Watch items: duplicate URL storage pattern (359–361/369–372) is now consistent by precedent" → updated to note the duplication was **cleared 2026-08-09 (now 0 duplicates; all Amazon-only books have blank `reference_url_1`)**.
- **B-04 — GitHub Actions pins:** `ci.yml`, `map_veritas_catalogue.yml`, `update_spreadsheet.yml` `actions/checkout@v7 → @v4`, `setup-python@v7 → @v5`, `setup-node@v7 → @v4`, `upload-artifact@v7 → @v4`, `stefanzweifel/git-auto-commit-action@v7 → @v5` (v7 majors do not exist; workflows now pin the latest published majors).
- **D-07 — Streaming `format_detail` noise:** `data/manual_master_candidates.csv` `manual-veritas-50485` `streaming discussion/interview` and `manual-veritas-50488` `one disc; ~60 min; streaming` cleared to `""`; regenerated `data/research_master_draft.{csv,json}`, `docs/master.json`, `docs/manual-candidates.json`. Masters `312`/`313` now have blank `format_detail` like all other `format=streaming` rows (0 streaming rows with non-blank detail, was 2).

**Verification:** all six `--check` modes PASS, `125/125` tests PASS, coverage `91%` on `2059` stmts, `node --check` PASS, `npm audit` 0. `D-05`, `DOC-01/02`, `B-04`, `D-07` are now **resolved**. Remaining carry-over is only governance (`S-01` raw-only push can bypass suite — requires branch protection, 403 not verifiable with this token) and optional resilience (local Tabulator fallback), both low/info and unchanged.


## 15. External audit reconciliation 2026-08-09 — `EXTERNAL_AUDIT` (main) vs this branch

**Source:** `main:EXTERNAL_AUDIT` (`DOCSHEET_AUDIT_AND_FIX.md`, audited `bbe8b01`, five-part stdlib re-derivation, 7240/7240 export, 362×24 master). Fetched via `fetch_page` 2026-08-09; the external file is self-contained and proposes fix specs in `REPOTESTER`.

**Agreement:** Both audits independently converge on the core invariants as **highly consistent** — 362 masters, 0 orphaned Veritas URLs, 0 duplicate codes/filenames, 278 codes, 75 exclusions, 134 overrides, 191 Veritas products, 340 relationships, 7240/7240 export cells, ledger 299/299, `1.0→01` month regression fixed. External `D-04`/`D-05` (export fidelity, cross-file invariants) are verified clean, matching our §7 "clean" list.

**Divergence — D-01 owned casing (21 rows):**

- External spec (§4): the 21 `true` (lower) rows on `310,311,320–326,332–343` (19 `edition-audible-*` + 2 `manual-veritas-54219/55473`) are the defect; fix by changing `data/edition_candidates.csv` (`19× true→True`), `data/manual_master_candidates.csv` (`2× true→True`), `data/research_master_draft.csv` (`21× true→True`), `docs/master.json` (`21× "true"→"True"`), `docs/manual-candidates.json` (`2× "true"→"True"`), then `grep -rn ': *"true"' → no output`.
- This branch (§11): the 295 `true` / 25 `false` lower vocabulary is the **documented** state (`README:215` "three values `true`/`false`/blank", validators `∉ {"", "true", "false"}` for candidates). The defect was the 274 `True` capital rows on ledger-derived masters. Fix was `strip().lower()` on all three `owned` write paths plus `migration_review_ledger.csv` `281 True→true / 25 False→false`, so master is now `295 true / 25 false / 42 blank` and `grep -rn ': *"True"'` is clean. Frontend `statusLabel`/`buildOptionLabel` now handle both cases defensively.
- **Reconciliation:** both fixes achieve **vocabulary consistency** (no mixed case), but in opposite directions. External's direction (`→True`) matches the ledger's historical majority (274 `True`) and its hardening rule `owned ∈ {True, False, ""}`; this branch's direction (`→true`) matches `README:215` and the **current** `build_research_master.py` validators. Without changing those validators, applying the external `true→True` would fail `build_research_master.py --check` (`proposed_owned must be blank, true, or false`). The defensive frontend handles either. Owner to confirm which vocabulary to enshrine; this branch preserves the validator-documented lower form.

**Applied from external — D-03 URL defects (recommended):**

- `uuid 289` (`Truth vs Falsehood: How to Tell the Difference`, raw `328`) `source_url_hay_house` typo `parperback → paperback` — fixed in **both** `data/hayhouse_official_products.csv` (`Truth vs Falsehood` row) and `data/research_master_source_overrides.csv` (`328,source_url_hay_house,…parperback→paperback`). Hay House Products sheet now shows `paperback`.
- `uuid 265` (`Golden Word Book Signing – Audio`, raw `297`) Veritas slug `https-veritaspub-com-product-… → golden-word-book-signing-january-13-2007` — fixed in **both** `data/veritas_official_products.csv` (`1552`) and `data/research_master_source_overrides.csv` (`297,source_url_veritas,…`). Inventory and master now share the clean product URL; `sync_inventory_mirrors` and `validate_veritas_inventory` remain green. Note: the prior ruling at `archive/RULING_PREP_MASTER_265…` kept the verbatim mangled slug as "no clean-slug equivalent"; the external audit's browser check (and this fix) assumes the clean slug returns `200` and is the intended product page — owner to confirm live, or revert to verbatim if the clean slug is a soft-404.

**Deferred per external §6 (owner decisions already made) — not changed in this branch:**

- `work_id` slug splits (`w-live-prayer → w-live-your-life-like-a-prayer` for 121/122/123, `w-live-prayer → w-live-life-as-a-prayer` for 343, `w-healing-and-recovery → w-healing-achieving-total-wellness` for 328, `w-highest-level-of-enlightenment → w-highest-level-of-enlightenment-audio` for 330) — 154 `work_id` deviate from `w-+slugify(title)` per external stdlib checker; 3 splits approved but externally referenced, so coordinated change required. This branch keeps the committed `w-*` values.

**Result after external D-03:** master `265`/`289` URLs are clean (`0 parperback`, `0 https-veritaspub` in master), inventory URLs are clean, all six `--check` modes PASS, `125/125` tests PASS, `91%` coverage, `node --check` PASS, `npm audit` 0. Owned remains `295 true` (lower) — see divergence note above.

