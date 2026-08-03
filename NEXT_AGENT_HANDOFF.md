# Next-Agent Transition Handoff

**Prepared:** 2026-08-03
**Branch:** `arena/019fc740-docsheet`
**Full audit:** [AUDIT_2026-08-03_FULL.md](AUDIT_2026-08-03_FULL.md)

## Read this first

This session verified **every catalogue entry against the live Veritas
Publishing API** (191 products, full `product_cat` taxonomy, per-product SKU and
format metadata) and fixed four critical data-correctness defects. All are
committed and verified. What remains below is **open work, not known breakage.**

The single most important lesson: **the four critical bugs were all internally
self-consistent and passed every existing check.** They were only detectable by
comparing against the publisher's own data. Structural validation is necessary
but not sufficient for this project.

## Current validated state

| Layer | Count | Canonical location |
|---|---:|---|
| Raw rows / ledger rows | 374 / 374 | `hawkins archive clone - Sheet1.csv`, `migration_review_ledger.csv` |
| Curated master | 317 | `data/research_master_draft.{csv,json}` |
| — `lecture` / `book` / `discussion` / untyped | 277 / 29 / 10 / 1 | |
| Catalogue codes (unique) | 223 | derived from `item_type` + `year` |
| Months (all verified vs official) | 198 | derived from official product slug |
| Exclusions / overrides | 68 / 79 | `data/research_master_*.csv` |
| Candidates / leads | 11 promoted / 6 unpromoted / 1 lead | `data/manual_candidate_promotions.csv`, `data/manual_master_candidates.csv`, `research_manual_leads.csv` |
| Relationships / series compilations | 301 / 7 | `data/product_relationships.csv`, `series_compilation_relationships.csv` |
| Veritas / Hay House / Audible / International | 191 / 24 / 26 / 36 | `data/*_products.csv`, `international_discovery_queue.csv` |
| Everything Pages view | 353 | `docs/master.json` (317 `master` + 36 `candidate_*`) |

Required before delivering any data change:

```bash
python -m py_compile *.py
python build_research_master.py --check
python build_catalogue_pages.py --check
python reconcile_research_master.py --check
node --check docs/app.js && node --check tests/csv-export.spec.js
git diff --check
```

---

## P0 — Blocked on the repository owner

### 1. CI workflow
`.github/workflows/ci.yml` cannot be pushed: the GitHub App lacks `workflows`
permission (re-probed and re-confirmed this session). **Complete drop-in YAML and
step-by-step web-editor instructions are in
[UNBLOCK_INSTRUCTIONS.md](UNBLOCK_INSTRUCTIONS.md) Task A.** Every step except the
Chromium install has been verified locally. Until this lands, all guarantees rest
on someone remembering to run the checks by hand.

### 2. Playwright browser execution
Three tests exist and are discoverable; Chromium cannot be downloaded in the
sandbox. CI (item 1) resolves this.

---

## P1 — Open decisions (evidence gathered, needs a ruling)

### 3. Four series/type judgement calls
Verified against the official taxonomy; each needs a human decision, not more research.

### Decisions applied 2026-08-03

- Records **199–201** moved to `Satsang Series`, following the official Veritas
  taxonomy for their Q&A products.
- Record **301** remains `item_type=book`. The owner confirmed ISBN 1401964990;
  the primary source is now the official Hay House paperback listing. The
  mismatched Veritas/Audible audio associations were removed as primary sources;
  the Veritas audio relationship remains explicitly `related_material`.
- Note-only placeholders **246** (B-02) and **249** (B-05) were moved to
  exclusions. The master is now 306 records with one remaining untyped record.
- Display-title hygiene is applied reproducibly by `build_research_master.py`.
  Every master row has verbatim `legacy_title`; `.mp4`, `-converted`, and leading
  numeric file sequences are removed from public titles, while DVD/CD/PART
  designators remain. Record **203** is corrected to Volume I with its raw title
  and official-evidence note retained.

The only remaining source/type decision from this group is **record 264**:
`“In the World But Not of It” – Audio` is deferred pending physical-edition
confirmation. Its likely product 1661 (`in-the-world-but-not-of-it-cd`, SKU
`am_itwbnoi`) must not be added as a source override until that check is complete.

Also outstanding from earlier: whether `interview` vs `discussion` was the right
call is now settled (`discussion` was added), but **`audio`/`video` remain in the
vocabulary as `DEPRECATED_MEDIUM_ITEM_TYPES`** — consider removing them entirely
once no data uses them.

### 6. Candidate promotion
17 candidates remain `reviewed_candidate` / `not_promoted`. No generator path
promotes them. Needs a promotion-decision input keyed by `candidate_key` that
assigns a compact ID, catalogue code and provenance.

---

## P2 — Hardening and hygiene

7. **SRI + CSP** — ✅ completed 2026-08-03. Tabulator 6.5.2 is version-pinned
   with SHA-384 integrity from the official npm package; the document uses an
   explicit CSP with a SHA-256 hash for the dark-mode bootstrap.
8. **Read-only review sheets** — ✅ completed 2026-08-03. Generated views set
   `editor: false`; the footer and browser test state that published data is
   read-only.
9. **`process_data.py --check`** — ✅ implemented with timestamp-aware metadata
   validation. The extra CI step is prepared locally but cannot be pushed until
   the GitHub App receives `workflows` permission; see `UNBLOCK_INSTRUCTIONS.md`.
10. **Pin Python deps** (`pandas>=2,<4` or constraints file) and add a `LICENSE`
    — the repo is public with none.
11. **Dead code** — `loadMeta()` and `metaLoaded` in `docs/app.js` are never
    called; `docs/meta.json` and `docs/catalogue-meta.json` are generated,
    committed and read by nothing.
12. **Six always-empty master columns** — `location_physical`, `location_digital`,
    `location_streaming`, `source_url_hay_house`, `source_url_nightingale_conant`,
    `reference_url_2` are 0/308 populated. Populate or drop.
13. **`format` is blank on 110 records.** Strong evidence was gathered this
    session for a deliberate pass: SKU prefixes (`cd_`, `_dvd`, `vs_v1pvf_dvd`),
    product-detail strings ("Two DVD Set", "Three Compact Disc Set", "6 CD Set"),
    and "Streaming Video is not available for this topic" markers.
14. **Nightingale-Conant provenance gap** — `source_url_nightingale_conant` is
    empty on all 308 records, yet the official page for product 1661 states
    "Publisher: Nightingale-Conant". Worth a provenance pass.

---

## P3 — Enhancements

15. **Enforce the two remaining derived-field invariants.** F-9 swept them and
    they currently hold, but only `normalized_title_match_count` is guarded in
    code. `matched_master_titles` in both the inventory and the decision overlay
    could still desynchronize under a hand-edit.
16. **Documentation consolidation.** 38 Markdown files at repo root. Four
    overlapping status docs (`PROJECT_STATE_AUDIT`, `HANDOFF`, this file,
    `IMPLEMENTATION_PLAN`) restate the same counts and will drift —
    `catalogue-meta.json` already holds them programmatically. Eight decision
    records belong in `decisions/`. Two `*_DRAFT.md` files sit beside their
    finalized versions.
17. **Broader browser tests** — all 17 tabs, search+filter composition, column
    chooser, row drawer, dark mode, console-error assertions.
18. **Re-run Map Veritas Catalogue once.** With the inventory corrected it should
    now **pass** rather than fail, which makes any future failure a genuine
    upstream signal.

---

## Data and review boundaries (unchanged, still binding)

- **Never edit the raw CSV through a generator.**
- **Never hand-edit generated files** (`data/research_master_draft.*`, `docs/*.json`).
  Change the declared input and regenerate.
- **A commercial listing is not master identity.** Do not infer work or edition
  identity from a title alone — this session proved why (C2: four records linked
  to the wrong edition, one to a wall chart).
- **`item_type` = what a record IS; `format` = the carrier.** Set by the 198
  DVD lectures typed `lecture`, not `video`.
- **Compact master IDs are stable once issued.**
- **Relationships stay at the evidence level actually supported** — item-level
  when proven, series-level for annual Highlights.

## Verification tips learned this session

- The Veritas WP API is unreachable via `curl`/`urllib` from the sandbox (TLS EOF)
  but **works through the agent's page-fetch tool**. Use
  `/wp-json/wp/v2/product?per_page=100&page=N&_fields=id,link` and
  `/wp-json/wp/v2/product_cat` — compact `_fields` avoids response chunking.
- Individual product pages expose `Category:` and `SKU:` plus product details
  ("Two DVD Set", running time, ISBN) — the strongest evidence available.
- `product_cat` IDs map to slugs via the `product_cat` endpoint; the taxonomy is
  the authoritative grouping and it resolved several ambiguities outright.

---

## Post-audit merge handoff — 2026-08-03

**Merged PRs:** [#11](https://github.com/56eli/docsheet/pull/11) (full coherence
audit and promotion-status reconciliation) and
[#12](https://github.com/56eli/docsheet/pull/12) (count-independent browser smoke
test). PR #12 CI passed all deterministic pipeline checks and **4/4 Chromium
browser tests**.

### Safe starting point

1. Read `AUDIT_2026-08-03_FULL.md` §11, `CATEGORY_DOMINANCE_POLICY.md`, and this
   file before changing data.
2. Do not hand-edit `data/research_master_draft.*`, `docs/*.json`, or the raw
   spreadsheet. Update declared review inputs, rebuild, then run all checks.
3. The master is 317 records; 11 official candidates are promoted through
   `data/manual_candidate_promotions.csv`; six candidate records remain
   intentionally unpromoted.
4. The only local uncommitted file in this Arena session is the CI workflow
   addition (`python process_data.py --check`). GitHub rejects workflow-file
   updates from this app without `workflows` permission. Follow
   `UNBLOCK_INSTRUCTIONS.md` in GitHub's web editor; do not discard that change
   without applying its equivalent upstream.

### Next implementation priority

Implement the official taxonomy mapper from `CATEGORY_DOMINANCE_POLICY.md` as a
reviewable input/output layer. First refresh or retrieve the official category
snapshot, preserve every publisher category, calculate a dominant category by the
approved hierarchy, and emit an explicit review queue for no-category and
Satsang+Highlights conflicts. Categories may set `series`, but must not silently
change `item_type`.

After that, continue candidate review: rechecked audio candidates, remaining
Unity Church talks, and deferred record 264. Use official product pages as source
evidence and record owner decisions in committed inputs.
