# Full-Stack Audit — 2026-08-08 (Arena, fresh-eyes independent pass)

**Branch:** `arena/019fe244-docsheet` (at `main` HEAD `58247a0`)
**Method:** independent re-verification — ran every safeguard in a clean venv, then
wrote standalone pandas probes that ignore the pipeline's own validators and
cross-check the committed data, generated JSON, docs, and CI from scratch.
**Result:** **pipeline and data are internally consistent; all defects found are
documentation-vs-data drift and repo hygiene** — 0 critical, 0 data-loss risks.

---

## 1. What re-verified clean (do not re-audit)

| Check | Command / probe | Result |
|---|---|---|
| Reconciliation guard | `reconcile_research_master.py --check` | ✅ report current |
| Master build | `build_research_master.py --check` | ✅ 365 items / 72 exclusions / 131 overrides / 39 candidates |
| Pages build | `build_catalogue_pages.py --check` | ✅ 365 Everything rows |
| Series taxonomy | `map_series_taxonomy.py --check` | ✅ 186 mappings, queue 0 |
| Inventory mirrors | `sync_inventory_mirrors.py --check` | ✅ |
| Raw pass-through | `process_data.py --check` | ✅ 374×13 → 8 view cols |
| Test suite | `python -m unittest discover tests` | ✅ **125 tests OK** (~3s) |
| Coverage gate | `coverage run -m unittest … && coverage report` | ✅ **91%** total, floor 85%, worst module 88% |
| JS syntax | `node --check docs/app.js` + config + specs | ✅ |
| Static site serving | `python -m http.server` + curl all key JSON | ✅ 200s; `docs/meta.json` gone as documented |
| Frontend security | review of `docs/index.html` / `app.js` | ✅ CSP present, Tabulator 6.5.2 pinned **with SRI**, only 5 `innerHTML` uses — all static strings, no data interpolation |
| Raw-row accounting | independent pandas probe | ✅ every raw row 3–376 is either a master `raw_row_number` (302) or an `exclusions` row (72); 31 fully-empty raw rows are all individually excluded with reasons |
| Headline counts | independent recount | ✅ 365 master (309/40/8/7/1), 281 codes (unique), 72 exclusions, 131 overrides (all `approved`), 39 promotions, 343 relationships (336 derived + 7 `related_material`), 7 series compilations |
| Identifier integrity | independent probe | ✅ no duplicate uuid / catalog_code / proposed_filename; filename prefix year-month always equals `year`/`month`; no `month` without `year` |
| Retired vocabularies | independent probe | ✅ zero `audio`/`video` item types or formats in master; `format` set = {DVD 253, CD 32, streaming 22, book 31, audiobook 27} |
| Mirror consistency | compare CSV↔JSON | ✅ `research_master_draft.json` = 365; `docs/master.json` = 365 with derived `record_type` + `proposed_filename_display` (27 keys) |
| Office Series B-02/B-05 gap | ledger + exclusions | ✅ **Not a defect** — raw rows "where is B-02? / might not exist" were excluded by owner ruling 2026-08-03; the A-01…B-06 numbering is the publisher's |
| Streaming URL fan-out | code walk (`apply_veritas_streaming_urls`) | ✅ benign — 36 approved products fan out to 56 master rows (multi-part products share one product page); log wording only, see §3-F15 |

## 2. Data findings (catalogue)

| # | Sev | Finding |
|---|---|---|
| D1 | **Medium** | **README contradicts data on 198X codes.** README "Current reviewed catalogue state" says pre-2000 rows with blank/`198X` year ("the 13 Volume Series and 16 Office Series rows") "correctly carry no code". Data: the 13 Volume Series rows are blank and codeless ✅, but all **16 Office Series rows carry `LECTURE-198X-001 … -016`**. The clause is wrong — `198X` was treated as a mintable year. Either amend the README sentence or (bigger call) retire/replace the 16 198X codes (codes are documented as never-renumbered, so doc fix is the sane route). Also flagged at code level by `archive/FULL_STACK_AUDIT_2026-08-08.md` §125–137 and `_INDEPENDENT` §166; the *README-sentence* contradiction is new here. |
| D2 | **Medium** | **`work_id` provenance rule is stale everywhere it's written.** README §Edition-model and handoff §5 (a *binding* rule) say work_id is assigned **only** from approved `data/work_families.csv` rows. In fact 341 memberships come from `work_families.csv` and **24 rows (masters 320–343) get work_id from the approved `work_id` column of `data/edition_promotions.csv`**. Data is fine (both are owner-approved inputs); the two rule sentences need amending to "work_families.csv, or the approved work_id column of edition_promotions.csv for minted edition rows". |
| D3 | Low | **Redundant URL storage on masters 369–372.** `reference_url_1` exactly duplicates `source_url_audible` (369–371) and `source_url_hay_house` (372). Harmless but double-maintained; the Everything sheet will render the same link twice. |
| D4 | Low | **3 Amazon links in the wrong column.** Masters 359–361 (the three academic books) carry Amazon paperback URLs in `reference_url_1` while the dedicated curated `source_url_amazon` column (added 2026-08-07, already used by 18 other rows) stays blank for them. Migrate via the override mechanism, not by hand. |
| D5 | Low | **Master 94 (`Spiritual Traps`) carries an archive.org `…/Hawkins_Lectures_transcoded_actual_files/…` link in `reference_url_1`** — an unofficial redistribution mirror sitting in a column documented as "streaming availability" among otherwise official references. Confirm this is owner-sanctioned; if kept, document the ruling. |
| D6 | Info | **`uuid` is a misnomer**: values are sequential integers 1–372 with 7 gaps (246, 249, 264, 281, 284, 302, 309 = retired duplicates), also surfaced as `member_master_uuid` / `matched_master_uuids`. Handoff §5 already blesses them as "compact master IDs"; no change recommended, but a one-line "despite the name, uuid is a stable integer id" note would save every future reader the confusion. |

## 3. Documentation & project-setup findings

| # | Sev | Finding |
|---|---|---|
| S1 | **Medium** | **Handoff test count is stale (again).** `NEXT_AGENT_HANDOFF.md` §2 and §3 say "123 tests"; the suite is **125** and README/INSTRUCTIONS already say 125. INSTRUCTIONS has a house rule for this exact drift — §3's table breaks it. |
| S2 | **Medium** | **Handoff P1 items contradict its own §3.** Three stale bullets in §6: (a) "Record 246 … deferred pending physical-edition confirmation" — §3 records it **ruled** duplicate-of-329 on 2026-08-07 (uuid 246 is gone, see D6); (b) "Remaining: the 4 free-text `audio` values in the unreviewed discovery triage lane" — §5 says the lane was **ruled empty** 2026-08-07; (c) "`source_url_hay_house` — 28 values" and "`source_url_nightingale_conant` holds 4 values" — actual: **27** and **6**. |
| S3 | Low | **Sheet-count off-by-one in handoff §1**: "emit 20 `docs/*.json` sheets" and "the 20 `docs/*.json` sheets + `docs/catalogue-meta.json`". Reality: **19 sheet JSONs + catalogue-meta.json = 20 JSON files**; app.js loads exactly 19 sheets. |
| S4 | Low | **Undocumented site tabs.** README's "Review workspace" paragraph never mentions the **International Editions** sheet (`docs/international-products.json`, 3 publishers / queue_created) or the **Publishers** sheet. The catalogue-meta keys also lack an international count (unlike every other sheet). |
| S5 | Low | **INSTRUCTIONS circularity:** its curated-catalogue section points readers to `archive/PROJECT_STATE_AUDIT.md` and `archive/IMPLEMENTATION_PLAN.md` "for current risk and roadmap status" — while the README declares `archive/` non-normative. Point at `FULL_STACK_AUDIT_2026-08-08_ARENA.md` / `NEXT_AGENT_HANDOFF.md` instead. |
| S6 | Low | **README "Documentation layout" is self-contradictory**: it says living docs sit at the repository root and then lists `archive/FULL_STACK_AUDIT_2026-08-04_FINAL_358_V2.md`, while the five *actual* root audits (`FULL_STACK_AUDIT_2026-08-07_DEEP`, `…2026-08-08`, `…_ARENA`, `…_DEEP_DIVE`, `…_INDEPENDENT`) go unlisted. **Five full-stack audits at root within 48h** (plus ~95 audit/handoff files in `archive/`) is noise; designate one current audit (README already links `_ARENA`), archive the rest. |
| S7 | Trivial | `.coveragerc` comment says "all eight pipeline modules are measured" — the report now covers **10** modules (incl. `_common.py`, `fetch_veritas_catalogue.py`). |
| S8 | Trivial | **Deceptive log line**: `[streaming] Applied 56 approved Veritas streaming URLs as reference_url_1` — there are only **36** approved rows in `data/veritas_streaming_urls.csv`; 56 is the row fan-out (multi-part products). Rephrase to "filled 56 rows from 36 approved products". Only ever printed during fresh builds (tests), not `--check`. |
| S9 | Trivial | Handoff references commits `6b28e66` / `406116f` that **do not exist in this repo** (visible history is a single squashed commit — likely a clone artifact, not something the project did wrong; flagging so nobody wastes time `git show`-ing them). |
| S10 | Trivial | Source CSV hygiene carried over knowingly: filename with spaces + artifact header row (`archive clbs`) + 5 always-empty columns + 31 fully-blank rows. Everything downstream handles it correctly and it's all documented — listed here only as standing fragility (workflow `paths:` entries must quote the filename). |

## 4. What is genuinely in good shape

- **Review-loop discipline is exceptional**: every write path is check-gated, tamper-tested, deterministic (run-twice), and CI enforces all of it plus an 85% coverage floor. I could not desynchronize any committed artifact from its inputs.
- **Raw→ledger→master accounting is airtight**: 374 raw rows → 302 adopted + 72 excluded, every exclusion reasoned, empty rows tracked. This is the property most real-world spreadsheet projects fail.
- **Provenance is unusually complete**: `year_source` labels on 100% of rows justification-classed; `legacy_title` preserves verbatim source text; URL overrides are evidence-keyed and all `approved`.
- **Frontend hygiene**: CSP, SRI-pinned CDN assets, no data-bearing `innerHTML`, abort-safe fetch logic, offline-testable.
- **CI design** avoids the classic race (raw-only push ignored by CI, owned by Update Spreadsheet), uses least-privilege permissions, pinned constraint files, and review-only live-source refresh.

## 5. Remaining (all low priority — everything above them was executed in §6)

1. **D6 note**: document that `uuid` is a stable compact integer id despite the name.
2. **CI badge** in README for the main workflow.
3. **S9/S10**: informational only (squashed clone history; standing raw-CSV fragility).

## 6. Resolution log (this branch, owner-directed via chat)

| Finding | Action taken | Verification |
|---|---|---|
| D5 (owner ruling: remove) | archive.org mirror removed at the source — raw CSV row 106 (`LS200508_1` `other links`) + ledger `raw_other_links` — and all six derived artifacts regenerated in documented order; master 94 `reference_url_1` now blank; CRLF line endings preserved (raw diff = 1 line) | all 6 `--check`s ✅, 125 tests ✅ |
| D1 | README code-minting paragraph corrected: 16 Office Series rows **do** carry `LECTURE-198X-001…-016`; only blank-year (13 Volume Series) and blank-at-minting candidate/edition rows carry no code | doc-only |
| D2 | README §Edition-model and handoff §5 binding rule amended: work_id comes from approved `work_families.csv` rows **or** the approved `work_id` column of `edition_promotions.csv` for minted edition rows (320–343) | doc-only |
| S1 | Handoff §2 + §3 test count 123 → 125 | matches `unittest discover` |
| S2 | Handoff P1 record-246 bullet marked **RULED 2026-08-07**; free-text-`audio` remainder marked resolved 2026-08-07; NC count 4→**6**, Hay House 28→**27** | counts re-verified against master CSV |
| S3 | Handoff §1 "20 sheets" twice corrected to **19 sheets + `catalogue-meta.json` (20 JSON files)** | app.js loads 19 |
| S4 | README review-workspace paragraph now names **International Editions** and **Publishers** sheets | — |
| S5 | INSTRUCTIONS now points at `FULL_STACK_AUDIT_2026-08-08_ARENA.md` + handoff §6 instead of non-normative archive docs | — |
| S6 | README "Documentation layout" line lists the declared-current root audit instead of an archived 2026-08-04 audit | — |
| S7 | `.coveragerc` comment "eight" → "ten" pipeline modules | coverage report has 10 rows |
| S8 | `[streaming]` log line reworded to "Filled reference_url_1 on N master rows from M approved Veritas streaming products" (no test asserted the old text) | 125 tests ✅ |
| D4 (owner ruling: migrate) | 3 candidate-keyed `source_url_amazon` overrides added for masters 359–361 (review_status approved 2026-08-08), full regeneration run; masters now carry the curated Amazon column (21 rows total) — matching the established 369–372 pattern where the minted `reference_url_1` remains as reference evidence | all 6 `--check`s ✅, 125 tests ✅, overrides 131 → **134** (README/handoff bumped) |
| S6-noise (owner pick) | the 4 superseded root audits moved to `archive/` with `git mv`; root keeps the declared-current `…_ARENA.md` + this pass; `archive/README.md` index updated and its stale root pointer fixed; handoff cross-references repathed | grep: no dangling root references |
| D6, S9, S10 | Deferred — D6 rename is cosmetic; S9/S10 informational | — |

Raw/ledger/master/JSON diffs after this session: exactly one cell each (the removed
archive.org value) plus the documentation/code-wording edits above. Everything else byte-identical.

*Prior audits: `FULL_STACK_AUDIT_2026-08-08_ARENA.md` (declared current, kept at root);
the 2026-08-07_DEEP / 2026-08-08 base / DEEP_DIVE / INDEPENDENT passes were moved to
`archive/` in the 2026-08-08 cleanup. This pass independently converged on the D1-class
198X findings and adds D2–D5 plus the handoff-contradiction set (S1–S3).*
