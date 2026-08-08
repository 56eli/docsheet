# Full-Stack & Catalogue Audit — 2026-08-08 (Arena V2, post-PR-#39)

**Auditor:** Arena.ai Full-Stack / Data-Engineering agent
**Repository:** `56eli/docsheet` · **Branch:** `arena/019fe329-docsheet`
**Commit audited:** `bbe8b0116ce8ec7506c3a229f7f3b4e278e15e54` (`main` HEAD after PR #39 "audit: independent full-stack pass + D-01 duplicate-row collapse (365 → 362)")
**Scope:** raw CSV, review ledger, curated master, official inventories, candidate/edition registries, relationships, taxonomy, work families, filenames, generated Pages JSON, frontend, tests, CI, and living documentation.
**Method:** fresh Python 3.11 venv (`requirements-dev.txt`, pandas 3.0.5); re-ran every safeguard `--check`, the full unittest suite, and coverage; then wrote independent probes that bypass the project's own validators and cross-check data ↔ JSON ↔ docs. PR states verified with `gh`. No catalogue data or code was modified; the one generator run used for drift verification was restored (`git checkout`) immediately afterwards.

> This audit builds on the declared-current pair (`FULL_STACK_AUDIT_2026-08-08_ARENA.md`, `…_FRESH_EYES.md`) and the independent pass (`FULL_STACK_AUDIT_2026-08-08_INDEPENDENT.md`). Items previously reported are **re-verified against this commit**; new findings are N-01…N-05.

---

## 1. Executive verdict

**Green, with one user-visible data/frontend inconsistency and a tail of known, already-documented open items.** The pipeline remains deterministic: all six `--check` modes pass, 125/125 deterministic tests pass, coverage is 91% (floor 85%, lowest module 88%), JS syntax is clean, and every headline catalogue count in the README recomputes exactly. The single defect that affects what a visitor **sees** is the `owned` value-case drift (N-01): 274 of the 295 owned items do not render as "Owned" anywhere on the site because the data carries Python-style `True` while the frontend only understands lowercase `true`.

---

## 2. Verification matrix (re-run on this commit)

| Check | Result |
|---|---|
| `python process_data.py --check` | PASS — 374 raw rows × 13 cols; view trims to 8 columns |
| `python build_research_master.py --check` | PASS — 362 items; 75 exclusions; 134 overrides; 39 candidates |
| `python build_catalogue_pages.py --check` | PASS — 362 Everything rows |
| `python reconcile_research_master.py --check` | PASS |
| `python map_series_taxonomy.py --check` | PASS — 186 mappings, 0 queued |
| `python sync_inventory_mirrors.py --check` | PASS |
| `python -m unittest discover tests` | PASS — **125/125** in ~3.4s |
| Coverage | **91% total** (`fail_under=85`); every pipeline module 88–100% |
| `node --check` × app.js, playwright.config.js, 3 specs | PASS |
| Browser specs (`tests/*.spec.js`) | **18 tests** present (handoff DOC-02 still says 16); not executed here (no browser) |
| `python generate_migration_ledger.py --check` | ⚠️ **flag absorbed — script has no `--check` mode and silently rewrote the ledger** (N-04); restored via `git checkout` |

---

## 3. Recomputed catalogue state (all independent of project validators)

| Claim | Recomputed | Status |
|---|---|---|
| 362 master records (306 lecture / 40 book / 8 discussion / 7 highlight / 1 other) | 362 exactly (306/40/8/7/1) | ✅ |
| 278 catalogue codes, unique, lecture/discussion-only | 278, unique, 0 books-with-codes, 0 blank-year-with-code | ✅ |
| Code-year prefix matches row year (incl. `198X`) | 0 mismatches across all 278 | ✅ |
| UUID range 1–372 with gaps {225, 226, 227, 246, 249, 264, 281, 284, 302, 309} | Exact match | ✅ |
| 75 retained exclusions | 75 = 31 blank_separator + 21 series_context + 10 research_note + 7 duplicate + 5 source_context + 1 needs_review; every ledger `item` row (299) present in master | ✅ |
| 134 source overrides; 39 promoted / 0 unpromoted candidates | 134 / 39 / 0 (catalogue-meta agrees) | ✅ |
| 340 item-to-product relationships | 333 derived primary (masters with `source_url_veritas`) + 7 `related_material` = 340 | ✅ |
| 191 Veritas products; mirrors | 186 referenced by masters, 5 `excluded_related_material` (decks/journal/promo/Map) — sensible; mirror `matched_master_uuids` ↔ count fields consistent; **0 dangling refs to retired UUIDs** | ✅ |
| 362 proposed filenames | 362 unique, none blank; prefix == year-month wherever a month exists (0 mismatches); year-only rows use `YYYY - …`; Volume Series rows prefix-less as designed | ✅ |
| URLs | All URLs https; 0 non-https across all source/ref columns | ✅ |
| `work_id` | 362/362 assigned (338 via `work_families.csv`, 24 edition rows via `edition_promotions.csv` — see D-03); 191 works | ✅ |
| Series | 22 distinct values, 0 blank; plausible distribution (The Way to God 39 … Hay House 1) | ✅ |
| `docs/*.json` wiring | All 20 JSON files fetched by `docs/app.js`; 0 orphans | ✅ |
| `docs/data.json` | 374 rows, pass-through current | ✅ |
| Same-ish titles spanning multiple works | 1 hit — *A Review of the Work* 2006 vs 2007: two distinct annual works, **not** a duplicate | ✅ |
| Books policy | No book carries a month or a code; years are first-publication | ✅ |

---

## 4. New findings (this pass)

### N-01 — `owned` vocabulary case drift: the site only "sees" 21 of 295 owned items — **High, user-visible**

The master `owned` column mixes two conventions in one controlled vocabulary:

| Source path | Rows | Values |
|---|---|---|
| Raw/ledger-derived | 299 | `True` ×274, `False` ×25 |
| Candidate-minted | 63 | `true` ×21, blank ×42 |

The candidate path is *enforced* lowercase (`build_research_master.py:782`,`1121` reject anything but blank/`true`/`false`), but the ledger path passes values through verbatim. The frontend (`docs/app.js:1412` and facet `:429`) only maps exact lowercase `"true"`/`"false"`:

- the **Owned facet** lists the 21 lowercase rows as *Owned* and buckets all 274 `True` rows (plus blanks) as **"Not stated"** — there is no "Not owned" option at all, because no literal `false` exists;
- the in-grid badge renders the literal strings **"True"/"False"** (style `statusLabel` falls through to the raw value);
- README ("exports keep the raw `true`/`false`/empty values") and the site semantics both document lowercase only.

**Root cause:** `generate_migration_ledger.py:173` now writes lowercase (`✅→true`, `❌→false`), but the committed `migration_review_ledger.csv` still carries the Python-cased values of an older generator version (281 `True` / 25 `False`). Verified by running the generator: the only diff produced was 308 lines of `True→true` / `False→false` (restored after verification). This also means the 2026-08-07 "C4 owned semantics applied" handoff entry implemented the *labels* but the *data* never conformed.

**Fix options (owner decision):**
- (a) **Normalize at build** — one line in `build_research_master.py` (`value.lower()` on the ledger path): zero data churn, keeps ledger as hand-maintained record, master/JSON become uniformly lowercase.
- (b) **Regenerate the ledger** (and rebuild master + Pages JSON): conforms data everywhere, but rewrites 308 ledger lines and every derived artifact.
- (c) Frontend-only case-insensitive matching: hides the symptom, leaves the vocabulary split and exports inconsistent.

Given the pipeline's "validators enforce lowercase" stance everywhere else, (a) plus a validator that rejects mixed case on the ledger path is the most consistent end-state.

### N-02 — Same-named, different-content audit at root and in `archive/` — **Medium**

`FULL_STACK_AUDIT_2026-08-08_INDEPENDENT.md` exists both at root (325 lines, audits commit `aef3cfcd`, 125-test state) and in `archive/` (234 lines, earlier 115-test state, self-marked historical). README's "Documentation layout" names only the ARENA pair as the root audit living docs; the root INDEPENDENT file is undocumented there even though the handoff calls it the "current independent audit". Two files with one name and divergent bodies invite citing the wrong one; rename the root copy (e.g. add `_V2`) or move the stale archive copy's name out of collision.

### N-03 — Handoff header stale after merge — **Low**

`NEXT_AGENT_HANDOFF.md` opens as "current handoff for branch `arena/019fe2db-docsheet` (PR #39, open)" — `gh` shows PR #39 **MERGED** 2026-08-08 20:33 UTC into `main`. Reasonable as a session-time note, but it is now the top line of the entry-point document.

### N-04 — Ledger generator is outside the check-mode safeguard; a bare run silently rewrites the ledger — **Medium**

Every other generator is guarded (`--check` + CI wiring + README "Catalogue-data safeguard"), but `generate_migration_ledger.py` has **no `--check` mode**: invoking it (even with `--check`, which it ignores) unconditionally rewrites `migration_review_ledger.csv` — and per N-01 it currently rewrites 308 lines, instantly desyncing the ledger from the committed master (`build_research_master.py --check` then fails). Add a `--check` (and probably a deliberate `--write`) and list it among the safeguards, or explicitly mark the ledger as hand-owned and make the generator refuse to run without `--force`.

### N-05 — Ledger row 371 still `needs_review` although the work is already minted — **Low**

Raw row 371 ("Dialogues on Consciousness and Spirituality: WHAT IS THIS ⚠️⚠️⚠️") sits as the lone `needs_review` ledger row and appears in the Exclusions sheet with that disposition — yet the work itself was promoted to **master 361** on 2026-08-07 via `candidate:manual-academic-dialogues-1998`. The catalogue already resolved the question; the ledger/exclusion trail doesn't say so (it also means the raw spreadsheet's ⚠️ marker remains open-ended). Needs a one-row owner disposition to close the loop.

---

## 5. Previously reported findings — re-verified on this commit

| ID | Status on `bbe8b01` | Note |
|---|---|---|
| D-01 duplicate streaming/DVD rows | **Applied** | 225/226/227 retired; 311/310 single DVD masters; streaming in `reference_url_1`; mirrors re-derived |
| D-02 residual `streaming video` format_detail | **Moot** | Rows retired |
| D-03 editions 320–343 absent from `work_families.csv` | **Still open** | All 24 missing there; their `work_id` comes from `edition_promotions.csv` — two sources of membership truth |
| D-04 Amazon URL also in `reference_url_1` ("Streaming") for 359–361 | **Still open** | Verified: identical URL in both columns on all three |
| D-05 master 362 `format=streaming` but primary URL is `-dvd` slug; `reference_url_1` blank | **Still open** | Verified |
| D-06 `format=streaming` used inconsistently (312/313 streaming-only vs similar Q&A rows on DVD) | **Still open** | Verified |
| D-07 master 327 `format=DVD` + `format_detail="CD & DVD set"` | **Still open** | Carrier contradiction |
| D-08 master 265 malformed double-slug Veritas URL | **Still open** | Owner-accepted per audit trail; flag retained here for visibility |
| B-01 two Spanish Audible titles hardcoded in `build_catalogue_pages.py:797–815` | **Still open** | Verified: intl queue CSV 36 → JSON 38 (the 2 injected) |
| B-02 `catalogue-meta.json` has no international count; Review Overview omits International + Publishers | **Still open** | Verified: meta has no `international*` key; Review Overview lists 14 sheets, missing both |
| B-03 `docs/master.json` strips `candidate_key` (CSV master retains it) | **Still open** | |
| DOC-01 declared-current ARENA audit reports 365 masters/72 exclusions/131 overrides/281 codes/123 tests | **Still open** | Actual: 362/75/134/278/125 |
| DOC-02 handoff says "16 browser tests" | **Still open** | Actual: **18** `test(` blocks across the 3 specs |
| DOC-05 `data/edition_candidates.csv` CRLF line endings | **Still open** | Only CRLF file among data CSVs (others LF) |
| GitHub Issue #18 (ownership cross-check vs lak.nz Drive) | **Open** | External data triage, not repo state |

---

## 6. What is clean / verified this pass

- Pipeline determinism end-to-end; no hidden state: every generated artifact recomputes byte-identical via `--check`.
- Identifier discipline: catalogue codes stable, unique, year-consistent, and correctly withheld for books/blank-year rows; UUID gaps match docs exactly.
- Edition model: filename prefixes track year/month with zero mismatches; Volume Series and `198X` conventions hold uniformly; books obey the first-publication rule everywhere.
- Veritas mirror integrity: no dangling references to retired UUIDs; the 5 unreferenced products are deliberate `excluded_related_material`; 186/191 coverage fully explained.
- Ledger ↔ master: all 299 `item` rows are in the master; exclusion dispositions add up to 75 exactly; everything reversible.
- Structure/schema: no blank series, no non-https URLs, no duplicate filenames, no orphan Pages JSON files; CI job graph (check → tests → coverage → JS → e2e, least-privilege, race-avoiding) is well designed.
- Security/hygiene: `.gitignore` covers venv/coverage/node artifacts; no credentials in tree; MIT license present.

---

## 7. Recommended order of work

1. **N-01** — pick an `owned`-vocabulary fix path (recommend build-time normalization + ledger-path validator), then rebuild master + Pages JSON; this is the only defect a site visitor can see.
2. **Doc-drift batch (one PR):** DOC-01 (refresh ARENA audit numbers), DOC-02 (18 browser tests), N-02 (resolve the duplicate INDEPENDENT filename), N-03 (handoff header), DOC-05 (LF-normalize `edition_candidates.csv`).
3. **N-04** — give `generate_migration_ledger.py` a `--check` mode (and a `--force` write gate) and add it to the safeguard list + CI.
4. **Owner triage:** D-04 (move Amazon URLs out of the streaming slot or add a third link column), D-05 (362 carrier), D-06/D-07 (carrier conventions), N-05 (close ledger row 371), Issue #18.
5. **Code hygiene:** B-01 (move the 2 Spanish Audible rows into a committed CSV input), B-02 (international count in meta + Review Overview entries), B-03 (keep or document `candidate_key` stripping), D-03 (unify work-family membership source).

---

## 8. Reproduction commands

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
for s in process_data build_research_master build_catalogue_pages reconcile_research_master map_series_taxonomy sync_inventory_mirrors; do .venv/bin/python $s.py --check; done
.venv/bin/python -m unittest discover tests
.venv/bin/coverage run -m unittest discover tests && .venv/bin/coverage report
node --check docs/app.js
# N-01 vocabulary census:
.venv/bin/python -c "import csv,collections;print(collections.Counter(x['owned'] for x in csv.DictReader(open('data/research_master_draft.csv'))))"
```

---

## 9. Postscript — N-01 applied (2026-08-08, owner-selected "normalize at build")

Per owner direction this session, the `owned` vocabulary drift (N-01, option (a)) is **fixed**:

- **Code:** `build_research_master.py` gains `normalize_owned()` + an
  `OWNED_VOCABULARY` constant. All three `owned` write sites (ledger path,
  manual-candidate promotions, edition promotions) now emit the canonical
  lowercase vocabulary; the ledger path accepts any casing of the known
  boolean spellings and **hard-fails with a named source on anything else**,
  so the drift class is closed at the build gate.
- **Data:** the hand-maintained `migration_review_ledger.csv` is untouched;
  only derived artifacts were rebuilt (`data/research_master_draft.csv/.json`,
  `docs/master.json`). Master `owned` is now uniformly `true` ×295
  (274 raw + 21 candidate), `false` ×25, blank ×42 — CSV, draft JSON, and
  Pages JSON all agree.
- **Site effect:** the Owned facet/badge now counts all 295 owned records
  (previously 21) and the 25 explicitly-not-owned records render as
  "Not owned"; blanks remain unstated, matching the README vocabulary.
- **Re-verified after the fix:** all six `--check` modes PASS, 125/125 tests
  PASS, coverage 91% (floor 85%), `RECONCILIATION_REPORT.md` byte-identical
  (it does not carry `owned` values).

Remaining open items stay as listed: N-02…N-05, D-03…D-08, B-01…B-03,
DOC-01/DOC-02/DOC-05, and Issue #18.
