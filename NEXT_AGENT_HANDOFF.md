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
| Curated master | 308 | `data/research_master_draft.{csv,json}` |
| — `lecture` / `book` / `discussion` / untyped | 274 / 23 / 8 / 3 | |
| Catalogue codes (unique) | 221 | derived from `item_type` + `year` |
| Months (all verified vs official) | 198 | derived from official product slug |
| Exclusions / overrides | 66 / 80 | `data/research_master_*.csv` |
| Candidates / leads | 17 / 1 | `data/manual_master_candidates.csv`, `research_manual_leads.csv` |
| Relationships / series compilations | 301 / 7 | `data/product_relationships.csv`, `series_compilation_relationships.csv` |
| Veritas / Hay House / Audible / International | 191 / 24 / 26 / 36 | `data/*_products.csv`, `international_discovery_queue.csv` |
| Everything Pages view | 344 | `docs/master.json` (308 `master` + 36 `candidate_*`) |

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

| ID(s) | Our value | Official says | Question |
|---|---|---|---|
| 199, 200, 201 | series `Love & Spiritual Seeker Qualities` | `satsang`, `satsang2011`, `satsang-series-and-question-and-answer-sessions` | These 2011 Q&A sessions are filed by Veritas under Satsang, not the 2011 lecture series. Move them to `Satsang Series`, or keep them with their year-mates? |
| 301 | `item_type=book`, series `Books` | only `media-miscellaneous`; **no book edition exists** in the catalogue | "The Highest Level of Enlightenment" exists officially **only as audio**. Either it is not a book, or it is a book we hold with no Veritas book product. |

Also outstanding from earlier: whether `interview` vs `discussion` was the right
call is now settled (`discussion` was added), but **`audio`/`video` remain in the
vocabulary as `DEPRECATED_MEDIUM_ITEM_TYPES`** — consider removing them entirely
once no data uses them.

### 4. Title hygiene pass — analysis complete, not applied
[TITLE_HYGIENE_PROPOSAL.md](TITLE_HYGIENE_PROPOSAL.md) is fully researched and
simulated: **54 records** still carry `.mp4`, `-converted`, `PART n`, `A-01`-style
prefixes and leading sequence numbers. (Records 264/265 were fixed this session as
C4 because they were a provable data defect, not cosmetics.)

The proposal follows the existing LS-lecture precedent (clean `title`, verbatim
`title_source`, part designator in `format_detail`) and simulated cleanly:
56 titles → 0 empty, 0 information lost.

**Three open questions in §2a of that document:** whether `A-01`…`B-06` prefixes
leave the title (16 records), whether `Volume N-` prefixes stay (recommend yes),
and whether part designators use `PART1` or `DVD01` (recommend `PART1`, since
`DVD01` asserts an unevidenced medium).

**One resolved finding to apply with it:** record **203** is a confirmed source
typo — its title says "Volume II" but its `102` prefix, its linked two-disc
product (`vs_v1pvf_dvd`, "Two DVD Set") and its own "Applied Kinesiology" subject
all say **Volume I**. The real Volume II ("Consciousness and Addiction") is held
separately as records 204/205.

### 5. The 3 remaining untyped records
- **246** `where is B-02? might not exist.` and **249** `where is B-05? might not exist.`
  Not titles — unresolved research questions. The Office Series officially runs
  A-01…A-12, B-01, B-03, B-04, B-06; **B-02 and B-05 genuinely do not exist**
  upstream. Recommend moving both to `research_master_exclusions.csv`, which would
  make the master 306 records / 100% typed.
- **264** now has a clean title but still no source URL. Its official product is
  almost certainly `1661` (`in-the-world-but-not-of-it-cd`, SKU `am_itwbnoi`) —
  propose it as a reviewed **source override**, then it types as `lecture`.

### 6. Candidate promotion
17 candidates remain `reviewed_candidate` / `not_promoted`. No generator path
promotes them. Needs a promotion-decision input keyed by `candidate_key` that
assigns a compact ID, catalogue code and provenance.

---

## P2 — Hardening and hygiene

7. **SRI + CSP** — `docs/index.html` loads Tabulator 6.5.2 from jsDelivr with no
   Subresource Integrity hash and no CSP. Three lines; highest security value available.
8. **Read-only review sheets** — `buildColumns()` sets `editor: "input"`
   unconditionally, including on generated derivative sheets. Edits are
   session-only and warned about only in a footer string.
9. **`process_data.py --check`** — no check mode; `meta.json` rewrites
   `generated_at_utc` every run, so any "generated files current" CI step needs
   timestamp-aware comparison. `data.json` itself is byte-stable.
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
