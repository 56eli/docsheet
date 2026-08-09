# Full-Stack & Catalogue Audit — 2026-08-08 (Independent Deep-Dive Pass)

**Auditor:** Arena.ai Full-Stack / Data-Engineering agent
**Repository:** `56eli/docsheet`
**Branch:** `arena/019fe2db-docsheet`
**Commit audited:** `aef3cfcdc25e6420013dd71545aeedfdc09d86c5` (`main`, PR #38 "Standardize Edition column format_detail values")
**Scope:** raw CSV, review ledger, curated master, official inventories, candidate and edition registries, relationships, taxonomy, generated Pages JSON, frontend, tests, CI/CD, and living documentation.
**Method:** fresh Python 3.11 venv with `requirements-dev.txt -c requirements-ci.txt` (pandas 3.0.5 / numpy 2.4.6 / coverage 7.15.4); re-ran every safeguard and the test suite; then wrote independent pandas probes that bypass the project's own validators and cross-check data, generated JSON, docs, and CI from scratch. Also re-read every root policy/proposal/handoff document.

> This is an independent checkpoint. It does **not** modify catalogue data or implementation code; it identifies inconsistencies for owner triage. Prior audits from the same day are preserved in `archive/` and the declared-current pair at root.

---

## 1. Executive verdict

The current generated catalogue is **internally reproducible and CI/Pages are green** (all six `--check` modes, 125/125 deterministic tests, 91% coverage, JS syntax OK, `npm audit` 0 vulns, GitHub Pages `built`). The master has zero duplicate UUIDs, catalogue codes, or filenames; zero orphaned Veritas URLs; validators fail closed on the previously-reported guard gaps.

However, this independent pass surfaced **8 catalogue/data inconsistencies**, **3 build/code inconsistencies**, and **5 documentation/handoff drifts** that are not currently caught by the check suite because they are semantic, cross-table, or wording issues rather than byte-output mismatches. None are data-loss/critical, but three are genuine semantic defects that should be ruled on:

- **D-01 (Medium):** Two work families (`w-devotion-to-truth-talk`, `w-mind-heart-and-service`) contain **duplicate master rows for the same Veritas product — one `format=streaming`, one `format=DVD` — sharing the exact same `source_url_veritas` and streaming `reference_url_1`**. This contradicts the owner's 2026-08-08 evidence note ("model as one work, with streaming availability tracked as `reference_url_1` **when a DVD/CD carrier exists**"). Net effect: the same Veritas product yields two primary product relationships, two catalogue codes/records, and double-counts in the Everything view and product-relationship count.
- **D-02 (Medium):** The two "merged" streaming rows (225, 226/227) still carry the legacy **`streaming video`** in `format_detail`, even though the handoff explicitly says those rows "no longer store `streaming video` as `format_detail`." The DVD copies (310/311) conversely have **blank** `format_detail` — the two errors cancel visually but each is wrong on its own.
- **D-04 (Low/Medium):** Three curated book masters (359–361) carry an Amazon paperback URL in **both** `source_url_amazon` and `reference_url_1`. The UI labels `reference_url_1` as **"Streaming"** and the mobile card renders a "Stream" button for a paperback purchase link — a semantic/UX mismatch introduced when D4 migrated the links onto the curated column but deliberately left the minted reference in place.

Everything else is either owner-accepted (master 265's verbatim malformed URL, the `198X` Office-Series year, blank pre-2000 years), review-gated by design, or a wording/count drift in historical/current docs.

---

## 2. Verification matrix (re-run from scratch)

| Check | Result | Notes |
|---|---|---|
| `python -m py_compile *.py` | **PASS** | All 10 root Python modules compile. |
| `process_data.py --check` | **PASS** | 374 raw rows; 8 published view columns. |
| `build_research_master.py --check` | **PASS** | 365 items; 72 exclusions; **134** approved overrides; 39 manual candidates validated. |
| `build_catalogue_pages.py --check` | **PASS** | 365 Everything rows. |
| `reconcile_research_master.py --check` | **PASS** | Report current; 0 unexplained extras; 0 field differences. |
| `map_series_taxonomy.py --check` | **PASS** | 186 mappings; 177 approved / 9 rejected / 0 queued. |
| `sync_inventory_mirrors.py --check` | **PASS** | Veritas mirror fields match master. |
| `python -m unittest discover tests` | **125/125 PASS** | Offline/deterministic, ~3.3s. |
| Coverage | **91% PASS** | 2,062 statements; lowest module 88%; floor 85%. |
| `node --check` app.js / config / 3 specs | **PASS** | |
| `npm ci` / `npm audit` | **PASS** / **0 vulns** | Playwright 1.62.1. |
| Local HTTP smoke (`/docs/`, key JSON) | **200 OK** | |
| CSP inline script hash | **PASS** | `sha256-qULmN…oJJY=` matches. |
| CSV ↔ JSON row parity (13 direct pairs) | **2 expected enrichments; 11 exact** | International 36→38 (2 hardcoded Audible rows, see B-01); Relationships 7→343 (336 derived primary + 7 stored, by design). |
| GitHub `main` CI / Pages | **PASS** | Run 31274407803 green; Pages `built`. |
| Local Playwright | **BLOCKED** | Chromium not installed in sandbox (environmental; CI runs 18 browser tests). |
| Live Veritas `--check` | **BLOCKED** | TLS EOF to `veritaspub.com` from sandbox (documented); offline replay tests cover the fetcher. |

---

## 3. Recomputed current catalogue state

| Area | Value |
|---|---:|
| Raw spreadsheet rows | 374 (302 `item`, 72 non-item: 31 blank-separator, 21 series-context, 10 research-note, 5 source-context, 4 duplicate, 1 needs-review) |
| Curated master | **365** rows: 309 lecture, 40 book, 8 discussion, 7 highlight, 1 other |
| UUID range / gaps | 1–372, gaps `{246, 249, 264, 281, 284, 302, 309}` (7 retired duplicates) |
| Catalogue codes | 281 unique, 0 duplicates; 36 lecture/discussion rows intentionally codeless (17 blank-year, 19 candidate/edition rows blank-at-minting) |
| Work families | 191 works / 341 approved memberships; master coverage via `work_families.csv` ∪ `edition_promotions.csv` = 365/365 |
| Veritas inventory | 191 products: 186 `matched_by_primary_source`, 5 `excluded_related_material` |
| Master Veritas URLs | 336 populated, **0 orphans** (all present in inventory) |
| Relationships rendered | 343 = 336 derived primary + 7 stored `related_material` across 187 products |
| Series compilations | 7 reviewed rows |
| Source overrides | **134** all `approved` (71 veritas, 26 hayhouse, 21 amazon, 10 audible, 6 nightingale-conant) |
| Manual candidates | 39/39 promoted; 24/24 edition candidates promoted |
| Manual leads | 2 (outside master) |
| Official inventories | Veritas 191, Hay House 29 (27 matched + 2 excluded), Audible 26 (24 matched + 2 excluded) |
| Series taxonomy | 186 products → 177 approved / 9 rejected / 0 queued |
| Filename proposal | 365 rows; 365 unique safe names, 365 unique display names |
| Ownership | 296 `true`, 25 `false`, 44 blank |
| Year edge cases | 17 blank years (13 intentional Volume Series + 4 "under investigation"); 16 `198X` Office-Series rows |
| Frontend contract | 19 HTML tabs ↔ 19 `VIEWS` ↔ 19 JSON sheets + `catalogue-meta.json` |

---

## 4. Catalogue / data findings

### D-01 — Two works carry duplicate streaming + DVD rows for the same Veritas product

**Severity:** Medium (semantic / double-counting)
**Evidence:** masters 225/311 (`w-devotion-to-truth-talk`), 226/227/310 (`w-mind-heart-and-service`)

Both work families were created by the 2026-08-08 owner ruling "raw owned streaming row and promoted official product row share the same Veritas product URL/title/year; **model as one work, with streaming availability tracked as `reference_url_1` when a DVD/CD carrier exists**." The intended end state was a **single** DVD/CD master per work with the streaming page in `reference_url_1` (as was done for the six 2012 discussion rows 278–285 and 312–313). Instead, **both** rows were retained:

| uuid | title | format | format_detail | source_url_veritas | reference_url_1 | candidate_key |
|---:|---|---|---|---|---|---|
| 225 | Devotion to Truth Talk | **streaming** | streaming video | `…/devotion-to-truth-talk/` | `…/devotion-to-truth-video/` | (raw) |
| 311 | Devotion to Truth Talk | **DVD** | *(blank)* | `…/devotion-to-truth-talk/` | `…/devotion-to-truth-video/` | candidate:manual-veritas-55473 |
| 226 | Mind, Heart and Service… [1-2] | **streaming** | streaming video | `…/mind-heart-and-service…/` | `…-stream/` | (raw) |
| 227 | Mind, Heart and Service… [2-2] | **streaming** | streaming video | `…/mind-heart-and-service…/` | `…-stream/` | (raw) |
| 310 | Mind, Heart and Service… | **DVD** | *(blank)* | `…/mind-heart-and-service…/` | `…-stream/` | candidate:manual-veritas-54219 |

Consequences:
- The same Veritas product yields **two primary product relationships** for Devotion (rows 225 and 311), and a three-rows-for-one-product situation for Mind/Heart (226, 227, 310). `derive_primary_relationships` keys off every master with a non-empty `source_url_veritas`, so 343 includes these duplicates.
- The Everything view shows two/three rows for what the ruling itself calls one work × one product.
- The two streaming rows carry `owned=true` (raw marker) while the DVD copies have blank ownership — the work's ownership is now ambiguous.

The `v4.1` filename rule papered over the collision by giving them `(streaming)` / `(DVD)` suffixes (handoff §6, 2026-08-08), but that treats the symptom, not the model contradiction. The established pattern for the same situation (2012 Discussion Series) is **one row per work with the streaming URL demoted to `reference_url_1`**.

**Recommended resolution (owner ruling needed):** either
(a) retire the raw streaming rows 225/226/227 (like 246/309) and keep 310/311 as the DVD master with the streaming URL in `reference_url_1` (matches the ruling text and the 278–285 precedent), or
(b) explicitly amend the ruling to say "two carriers → two master rows" and update the relationship-count narrative, work-family evidence notes, and the duplicate-URL guard so this is intentional rather than accidental.
If (a), retirement requires retiring UUIDs, re-homing `owned=true`, and rerunning the full rebuild + checks.

### D-02 — Residual `streaming video` / blank `format_detail` on the D-01 rows

**Severity:** Low/Medium (catalogue hygiene; contradicts the handoff)
**Evidence:** handoff §6 line 434 ("DVD rows 310/311 no longer store `streaming video` as `format_detail`") vs current data.

The 2026-08-08 follow-up states the streaming `format_detail` text was moved off the DVD rows. In the committed data the DVD rows 310/311 do have it blank, but the **streaming rows 225/226/227 still carry `streaming video`**. Depending on the D-01 resolution, either:
- retire those rows (then the text goes with them), or
- normalise them (e.g. blank or a controlled `streaming` token) so the Edition column doesn't render "streaming · streaming video".

The same family of residual wording applies to master 312 (`streaming discussion/interview`) and 313 (`one disc; ~60 min; streaming`) — both format=`streaming` rows where `format_detail` still references physical "disc" language. 312/313 are not duplicate rows, but the "disc" wording is a leftover from when they were CD candidates.

### D-03 — `edition-promotions`-backed masters (320–343) are absent from `work_families.csv`

**Severity:** Low (coverage-reporting inconsistency; not a data defect)
**Evidence:** `data/work_families.csv` (341 rows) does not list masters 320–343; they get their `work_id` from `data/edition_promotions.csv` instead.

README §Edition-model and handoff §5 document this exception ("for minted edition rows it comes from the approved `work_id` column of `edition_promotions.csv`"), and `build_research_master` enforces it, so master coverage is genuinely 365/365. However, any standalone analysis of `work_families.csv` will report 24 uncovered masters (an independent probe initially flagged this). The fresh-eyes audit's §1 invariant phrasing "191 works, 341 approved memberships, 365/365 master coverage" is only true because it implicitly unions the two inputs. Consider either (a) copying the 24 edition-promotion work memberships into `work_families.csv` as `approved` rows so one input tells the whole story, or (b) adding a one-line note next to every "341 memberships" count in docs/handoff that says "+24 from edition_promotions = 365".

### D-04 — Amazon link sits in the "Streaming" column for masters 359–361

**Severity:** Low/Medium (UX/semantic mismatch)
**Evidence:**

| uuid | title | source_url_amazon | reference_url_1 |
|---:|---|---|---|
| 359 | Orthomolecular Psychiatry: Treatment of Schizophrenia | amazon.com/…/dp/0716708981 | amazon.com/…/dp/0716708981 (same) |
| 360 | Qualitative and Quantitative Analysis… | amazon.com/…/dp/0964326183 | amazon.com/…/dp/0964326183 (same) |
| 361 | Dialogues on Consciousness and Spirituality | amazon.com/…/dp/0964326175 | amazon.com/…/dp/0964326175 (same) |

The fresh-eyes audit (D4) migrated these onto the curated `source_url_amazon` column but **deliberately kept** the minted candidate value in `reference_url_1` "as reference evidence," citing the 369–372 precedent. However:
- `reference_url_1` is labelled **"Streaming"** in `COLUMN_LABELS` (app.js:208) and rendered as a **"Stream"** action on mobile cards (app.js:836–838).
- 369–372 do **not** actually duplicate a source column into `reference_url_1` (independent probe: `reference_url_1` is blank on 369–372) — so the precedent cited in the resolution log does not exist in the committed data.
- For these three **book** rows, the "Stream" button opens an Amazon paperback purchase page.

The URL is harmless and HTTPS, but the column semantics are wrong. Either clear `reference_url_1` on 359–361 (the dedicated Amazon column now carries it), or relabel `reference_url_1` to a neutral "Reference / Streaming" so non-streaming references don't masquerade as streams.

### D-05 — Master 362 `format=streaming` but the primary Veritas URL is the `-dvd` slug

**Severity:** Low (cosmetic; owner-accepted product classification)
**Evidence:** uuid 362 *Highlights of the 2002 Lectures 1-6*, `format=streaming`, `source_url_veritas=https://veritaspub.com/product/the-way-to-god-highlights-of-the-first-6-lectures-of-2002-dvd/`.

The other six Highlights masters (363–368) have clean non-`-dvd` URLs and `format=streaming`. Product 1800's canonical slug ends in `-dvd` (the page lists it as a DVD); the manual candidate notes it as a "streaming compilation." The owner ruling promoted it as a streaming highlight, so the format choice is deliberate, but the slug/format disagreement will read as an anomaly to anyone auditing the URL list. Consider either (a) switching 362 to `format=DVD` to match its product URL, or (b) adding a one-line `notes` clarification.

### D-06 — `format=streaming` is used inconsistently for Q/A and Discussion rows

**Severity:** Low (semantic; owner streaming ruling)
**Evidence:**

- 2011 Q/A sessions (199/200/201) are `format=streaming` with **no** `reference_url_1` and a product URL whose slug is just the product page. The Veritas inventory categories them under "Satsang Series and Question & Answer Sessions." The 22 Satsang CD rows (251–263, 344–352) are `format=CD`. The three Q/A rows are streaming-only per the raw spreadsheet (no `WE HAVE?` marker, no raw format), so `streaming` is defensible — but there is no `format_detail` or note explaining why these three Satsang-adjacent rows stream while the rest are on CD.
- 2012 Discussion rows 278/279/280/282/283/285 are `format=streaming` with a product URL in `source_url_veritas` and a *different*-year streaming slug in `reference_url_1` (e.g. product `…-2/` → streaming `…/2012-…-prayer/`). Their promoted DVD/CD counterparts 312/313 carry `format=streaming` too (with `reference_url_1`), so unlike D-01 these are **not** duplicated across two formats; they were correctly collapsed. But the dual "source product page vs streaming slug" pattern is worth a one-line note in `EDITION_MODEL_PROPOSAL.md` so a future auditor doesn't read it as a mismatch.

These are observations, not defects — they match the documented streaming-reference ruling. Flagged for completeness.

### D-07 — Master 327: `format=DVD` but `format_detail="CD & DVD set"`

**Severity:** Trivial/Info
The merged Edition column renders "DVD · CD & DVD set". The detail is accurate (product 1728 is a CD+DVD set) but the leading carrier is then ambiguous. Acceptable as-is; if a controlled vocabulary for `format_detail` is ever introduced, normalise to e.g. `"CD & DVD set"` with `format` left as the primary carrier.

### D-08 — Master 265's malformed URL remains (owner-accepted, confirmed)

`https://veritaspub.com/product/https-veritaspub-com-product-golden-word-book-signing-january-13-2007/` is the publisher's own canonical slug (verified in prior audits). It is **not** local corruption. `generate_lecture_review.py` still has a `quarantined_malformed` branch for this shape; no action needed, but the URL will keep appearing in naive "valid URL shape" probes.

---

## 5. Build / code inconsistencies

### B-01 — Two Spanish Audible titles are hardcoded into `build_catalogue_pages.py`

**Severity:** Medium (violates the project's "generated from committed CSV inputs, never hand-coded" invariant)
**Evidence:** `build_catalogue_pages.py:797–815` special-cases `official_title in ("Disolver el ego", "El nivel más alto de iluminación")` and appends synthetic international rows to `intl_items`.

Result: `data/international_discovery_queue.csv` has **36 rows** but `docs/international-products.json` has **38**, with no CSV provenance for the two extras. The rows are also:
- labelled `item_type: "book"` / `format: "digital"` — but the retired medium value policy forbids using `audio`/`video` as `item_type`; `"book"` for a Spanish audiobook is consistent with the edition model, yet no reviewed edition/candidate row mints these as masters.
- their source Audible inventory rows are `mapping_status: matched_by_title` with notes "deduplicated 2026-08-07" — i.e. they are **already-deduplicated** inventory entries, not "leads awaiting extraction." Displaying them in the International Editions queue under `match_status: matched_by_title` is contradictory: they are matched, not queued.

The handoff (§6 line 305) calls this "international discovery queue is 36 rows (7 publisher + 19 ES / 6 FR / 4 PT unreviewed)" — it never mentions the 2 hardcoded Audible rows.

**Recommended fix:** add the two Spanish Audible entries as proper rows in `data/international_discovery_queue.csv` with `match_status=matched_by_title` (or a new `deduplicated` status) and remove the hardcoded block from the builder, so CSV↔JSON parity holds and one input file governs the sheet. This is exactly the class of "hand-maintain the input, regenerate the output" rule the rest of the pipeline enforces.

### B-02 — `catalogue-meta.json` has no international count; Review Overview omits International + Publishers

**Severity:** Low (metadata/reporting gap)
**Evidence:** every other sheet has a meta key (e.g. `veritas_official_products`, `hayhouse_official_products`, `audible_official_products`, `approved_publishers`); there is no `international_products` key. The Review Overview sheet (`docs/review-overview.json`, 14 rows) lists every review sheet **except** International Editions and Publishers. A reader of the summary cannot see the international queue size (36/38) without opening the sheet.

**Recommended fix:** add `international_products: len(intl_items)` to the meta dict and two rows to the review-overview builder. Trivial.

### B-03 — `docs/master.json` strips `candidate_key` while the CSV master retains it

**Severity:** Info (intentional, but undocumented)
`data/research_master_draft.csv` / `.json` include `candidate_key` (e.g. `candidate:manual-veritas-54219`) for the 63 promoted rows. `docs/master.json` (25 keys) drops it. The README's "Everything" table doesn't mention this. The raw key is still needed to trace overrides (16 overrides target `candidate:` keys), so the CSV is the provenance source; the public JSON trims it for brevity. This is fine but worth a one-line note in `build_catalogue_pages.py` near the trim and in README's field semantics.

---

## 6. Documentation / handoff drift

### DOC-01 — Declared-current Arena audit still reports 131 overrides (actual 134) and 123 tests (actual 125)

**Severity:** Medium (the "declared current" audit disagrees with the data it audits)
**Evidence:** `FULL_STACK_AUDIT_2026-08-08_ARENA.md`:
- line 32: "365 master rows; 72 exclusions; **131** approved overrides" — actual is **134** (the D4 Amazon migration added 3 on top of the 131 baseline).
- line 63: "Source overrides **131/131** approved" — actual **134/134**.
- line 81: "All **131** source overrides point to…" — **134**.
- line 229–230: "123 tests, 91%" in the doc-drift table — suite is **125**.
- line 269: "deterministic suite is now **123/123**" — **125/125**.

The §12 follow-up (same file) does say "125/125 PASS" and "365 curated records", so the file contradicts itself between the baseline and follow-up sections. The fresh-eyes pass and README/handoff were already bumped to 134/125, but the earlier sections of the same file were not.

**Fix:** bump the five stale 131s to 134 and the two stale 123s to 125 (or annotate them as "baseline at commit X, see §12 for current").

### DOC-02 — Handoff §1 still says "7 browser tests; suite now 16 browser tests"

**Severity:** Low
`NEXT_AGENT_HANDOFF.md:27` says `ux-enhancements.spec.js` is "(7 browser tests; suite now 16 browser tests)" and line 120 repeats "3 spec files / 16 tests". The current `ux-enhancements.spec.js` has **9** tests (4+5+9 = **18** total browser tests); the later §6 entries (lines 597, 487) correctly say 18. The top summary and §2 sandbox block were not updated when the 9th test (keyboard slash) was added.

### DOC-03 — Handoff §6 overstates the 359–361 precedent

`NEXT_AGENT_HANDOFF.md` final bullet says the duplicate-URL pattern is "consistent by precedent … 359–361/369–372". As shown in D-04, masters 369–372 have **blank** `reference_url_1`; only 359–361 duplicate the Amazon URL. The 369–372 half of the precedent is false.

### DOC-04 — PR #38 description claims "Filled blank `format_detail` for single-part items with `Part 1`"

The PR body and merge commit state this. In the committed master, **13 single-part DVD rows have blank `format_detail`** (11 raw single lectures: 213, 214, 266–277 excluding 270/273; plus 310, 311). Single-part DVDs correctly should *not* carry "Part 1" (no other part exists), so the code/data outcome is right, but the PR description overstates what was applied. No code change needed; noted so a future reader doesn't go looking for the `Part 1` values.

### DOC-05 — `data/edition_candidates.csv` uses CRLF line endings

Every other committed CSV (23 of 24 root/data CSVs) uses LF. `edition_candidates.csv` is CRLF (the candidate-promotion loader tolerates this via `csv.DictReader`, so checks pass). Normalise to LF to keep diffs clean.

---

## 7. What remains clean / verified

- All six `--check` modes are byte-current; reconciliation shows **0 unexplained extras, 0 absent projections, 0 field differences**.
- Raw-row accounting is airtight: 374 raw → 302 adopted + 72 excluded (every exclusion has a disposition/reason); the one `needs_review` row (raw 371, "Dialogues on Consciousness and Spirituality: WHAT IS THIS ⚠️") is the provenance note for promoted master 361.
- UUIDs 1–372 with the 7 documented gaps; catalogue codes match `^(LECTURE|DISCUSSION)-(198X|\d{4})-\d{3}$`; 0 duplicates; codes lecture/discussion-only; books never coded.
- Months: 0 month-without-year, 0 invalid months, 0 book-months; years: 0 malformed; 17 blank / 16 `198X` all documented.
- Filenames: 365/365 unique safe + display; extension↔format matrix clean (DVD→mp4, CD→mp3, audiobook→m4b, book→pdf, streaming→mp4); year-month prefix agrees with record year/month for dated rows; the 17 blank-year rows (Volumes + Highlights + under-investigation) intentionally omit the prefix; the only special characters (`©`, curly quotes, `&`, `–`) are publisher-verbatim titles.
  - *Archival footnote (2026-08-09, expert audit §3.7):* the "17 blank-year rows" here are the 13 Volume Series + 4 under-investigation rows — the **7 Highlights rows (362–368) are not blank-year**: they carry years 2002–2007 from their titles and omit the year prefix per the *separate* owner directive "filename equals title" (2026-08-07), documented in FILENAME_PROPOSAL_YYYYMM_DVD01_V4.md §"2026-08-07 Highlights promotion". No data impact; wording corrected for the record.
- URL hygiene: all source/reference URLs HTTPS; no spaces; 0 orphaned master Veritas URLs; Veritas inventory `normalized_title_match_count` equals the number of `;`-separated `matched_master_uuids` for all 191 rows; 5 mapping decisions all resolve to `excluded_related_material` products in the inventory.
- No `audio`/`video` value in any controlled `item_type`; `format` vocabulary = {DVD 253, CD 32, book 31, audiobook 27, streaming 22}.
- Series-taxonomy: 186 matched, 177 approved, 9 rejected, 0 queued; the 50521 R3 conflict was resolved to an approved mapping.
- Work families: 191 works / 341 approved memberships; +24 edition-promotion memberships covers 365/365 masters; no member points at a retired UUID; w-devotion/w-mind-heart anomalies are D-01.
- Frontend: CSP present with correct inline-script hash; Tabulator 6.5.2 pinned with SRI on CSS + JS; only 5 `innerHTML` uses and all are static strings; abort-safe `activateView()` token prevents stale-fetch races; focus trap cycles all visible focusable descendants; mobile Browse mode and Series/Timeline rails wired; no credentials/secrets in tracked files.
- CI: least-privilege `contents: read`; concurrency groups; raw-only `paths-ignore` to avoid racing the Update Spreadsheet workflow; `requirements-ci.txt` pins the exact set; 85% coverage gate enforced; Playwright installs Chromium and runs 18 browser tests in CI.
- No open PRs; Issue #18 (ownership cross-check vs lak.nz Drive) remains open from 2026-08-03 and needs triage.
- Branch protection / required-status-checks on `main` could not be observed with this GitHub token (403 on the branch-protection API) — governance is the only setting not independently verifiable.

---

## 8. Recommended order of work

1. **D-01 ruling (owner)** — decide whether Devotion-to-Truth / Mind-Heart-and-Service keep two carriers as two master rows or collapse to one DVD/CD master with streaming in `reference_url_1`. This is the only finding that changes record count / relationship count.
2. **D-02/D-04** — normalise `format_detail` on the D-01 rows per the ruling; clear or relabel the Amazon `reference_url_1` on 359–361 so "Streaming" doesn't link to a paperback.
3. **B-01** — move the two hardcoded Spanish Audible rows into `international_discovery_queue.csv` (or otherwise review their `matched_by_title` status) so the Pages builder stays input-driven and CSV↔JSON parity holds.
4. **B-02 / DOC-01 / DOC-02 / DOC-03** — add the international meta key and review-overview rows; bump the five stale 131s and two 123s in the declared-current audit; fix the handoff's "16 browser tests" and the false 369–372 precedent. (All doc-only, low risk.)
5. **D-03** — either mirror the 24 edition-promotion work memberships into `work_families.csv` or annotate the "341 memberships" counts.
6. **D-05 / D-07** — optional one-line notes/normalisation for the 362 `-dvd` slug and 327's `CD & DVD set` detail.
7. **DOC-05** — convert `data/edition_candidates.csv` to LF.
8. **Triage Issue #18** and confirm `main` branch protection / required checks outside this token's visibility.
9. Optionally action the long-standing F-08 (local/vendor fallback for Tabulator/Google Fonts) and extend Playwright coverage to the remaining tabs, dark-mode persistence, and settings persistence.

---

## 9. Reproduction commands

```bash
python3 -m venv /tmp/dsv
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

`npm run test:e2e` requires the Chromium bundle (CI-only in this sandbox). `fetch_veritas_catalogue.py --check` requires live access to `veritaspub.com` (TLS EOF from the sandbox); offline replay tests cover its retry/matching logic.

---

## 10. Postscript — D-01 owner ruling applied (2026-08-08)

The owner selected "collapse" for D-01 (retire duplicate streaming masters
225/226/227 and keep promoted DVD masters 311/310 as the single record per
work, with streaming availability in `reference_url_1`, matching the
278–285 precedent). The change has been applied and the post-fix numbers
supersede the pre-fix figures in sections §2–§3 above:

| Measure | Before | After |
|---|---:|---:|
| Curated master | 365 | **362** (306 lecture / 40 book / 8 discussion / 7 highlight / 1 other) |
| Catalogue codes | 281 | **278** (the three retired rows carried codes) |
| Retained exclusions | 72 | **75** (raw rows 249/250/251 moved from `item` to `duplicate`) |
| Derived primary relationships | 336 | **333** |
| Total rendered relationships | 343 | **340** (333 derived + 7 stored `related_material`) |
| Work-family approved memberships | 341 | **338** (225/226/227 memberships removed; 310/311 evidence notes rewritten) |
| Filename proposal rows | 365 | **362** (retired rows removed; 311's `(DVD)` carrier suffix reverted to plain `2003 - Devotion to Truth Talk.mp4`) |
| Veritas inventory mirror 54219 | 3 masters (226; 227; 310) | 1 master (310) |
| Veritas inventory mirror 55473 | 2 masters (225; 311) | 1 master (311) |
| Series taxonomy approvals | 327 master IDs | 324 master IDs |

Other invariants unchanged: 134 overrides, 39/39 promotions, 7 series
compilations, 191 works, 191 Veritas products, 5 mapping decisions, 125/125
tests, 91% coverage. All six `--check` modes pass. `proposed_month` in the
ledger was also normalised back to zero-padded strings (`"01"–"12"`) — a
pre-existing pandas float-formatting regression had left it as `"1.0"–"12.0"`,
which broke the series-compilation validator's string month-range comparison
(caught mid-fix). `data/edition_candidates.csv` still uses CRLF; flagged as
DOC-05 but not normalised in this pass.

Findings D-02 through D-08 and B-01 through B-03 remain open for owner
triage (D-02 is now effectively moot because the rows it described were
retired; D-04's Amazon/Streaming column overlap on masters 359–361 is the
next highest-priority cleanup).
