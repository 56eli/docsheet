# Orchestrator Working State

> **ROLLUP NOTICE — 2026-09-22.** Trigger fired: **milestone completion** (maintenance theme closed with PR #77 merge; `main` `ac6608a`). Size before → after: **10335 B → 10210 B**. Pointer statement: the full text of every condensed record lives in this file's git history (`git log -p .orchestrator/local/ORCHESTRATOR_STATE.md` on `arena/01a0cb00-docsheet`). Condensed blocks are marked CLOSED-2026-09-22 tombstones; verbatim core (branch/continuation/tracker fields, lane registry, invariants, task queue, run log) preserved byte-intact; history not rewritten — this notice page commits on top of the old one.

## Orchestrator Branch

`arena/01a0cb00-docsheet` — provisioned by Arena for this session (CORE v4.9.1 Step 8). Distribution channel only; never merges; never an agent base; receives only `.orchestrator/prompts/*` and `.orchestrator/local/ORCHESTRATOR_STATE.md`.

## Continuation

[empty — new engagement; first v4.9.1 orchestrator on this repo, initialized 2026-09-22]

## Canonical Project Tracker

`docs/PROJECT_STATE.md` (resolved once in Phase 1, 2026-09-22; no existing equivalent — `STATUS.md`/`ROADMAP.md` absent, `NEXT_AGENT_HANDOFF.md` retired). Does not exist yet; task 001 creates it.

## Published Task Prompts

| Seq | Prompt path | Task | Agent branch | PR | Status |
|---|---|---|---|---|---|
| 001 | .orchestrator/prompts/001-bootstrap-project-state-tracker.md | Bootstrap canonical tracker docs/PROJECT_STATE.md and record CORE v4.9.1 anchor | arena/01a0cb14-docsheet | #74 | Merged 2026-09-22 (main `39c464e`); tracker + anchor live on main; MERGE reviewed same day |
| 002 | .orchestrator/prompts/002-scoreboard-remnant-cleanup.md | Remove dead .scoreboard/ references from the PR template | arena/01a0cb4e-docsheet (session-locked; work order said fix/scoreboard-remnant-cleanup) | #75 | Merged 2026-09-22 (main `ff0f35b`); zero .scoreboard refs in .github; MERGE reviewed same day |
| 003 | .orchestrator/prompts/003-orchestrator-behavior-gate.md | Add orchestrator behavior gate as a deterministic test stage | arena/01a0cb73-docsheet (session-locked) | #76 | Merged 2026-09-22 (main `923ba55`); gate file on main, duty lines intact; MERGE reviewed same day |
| 004 | .orchestrator/prompts/004-handoff-pointer-hygiene.md | Complete handoff-pointer hygiene and archive the init patch | arena/01a0cbb0-docsheet (session-locked) | #77 | Merged 2026-09-22 (main `ac6608a`); maintenance milestone COMPLETE; MERGE reviewed same day |
| 005 | .orchestrator/prompts/005-final-registry-crosscheck.md | Scope and crosscheck final_registry.csv against the curated master | arena/01a0cbd3-docsheet (session-locked) | #78 | Merged 2026-09-23 (main `1f7dab4`); MERGE reviewed same day; analysis-only deliverables on main (script/report/CSV/tests), registry input untouched |
| 006 | .orchestrator/prompts/006-proposed-filename-underscores.md | Adopt underscore convention for proposed_filename columns | session branch (to be reported) | — | Published — dispatching now (owner directive 2026-09-23: standard `2002-03_The_…_[1-3].mp4`; dash ruling = collapse ` - ` → `_`; scoped unfreeze of proposal sheet + generator outputs only) |

## Active Milestone

Owner-directed phase resumed with task **006 dispatched 2026-09-23** — underscore standard for `proposed_filename` (scoped owner instruction; proposal sheet + generator outputs only). Task **005 closed** — PR #78 merged 2026-09-23 (`main` `1f7dab4`); crosscheck deliverables live, registry input byte-intact; buckets D/E await owner rulings alongside 006. Maintenance & governance hardening CLOSED 2026-09-22 (PRs #74–#77). General research phase remains byte-frozen except the scoped 006 surfaces.

## Task Queue

- [x] PR #74: 001 Tracker bootstrap + CORE anchor (Merged 2026-09-22 — `main` `39c464e`)
- [x] PR #75: 002 Scoreboard remnant cleanup (Merged 2026-09-22 — `main` `ff0f35b`)
- [x] PR #76: 003 Orchestrator behavior gate (Merged 2026-09-22 — `main` `923ba55`; gate live in CI; suite 166)
- [x] PR #77: 004 Handoff-pointer hygiene + owner-ruled patch move (Merged 2026-09-22 — `main` `ac6608a`; redirects/pointers → tracker, §4 marks milestone COMPLETE, init patch in `archive/` blob-identical; MERGE verdict had noted non-blocking 9-line-vs-"one-line" archive note overshoot, disclosed by agent)
- [x] ROLLUP: milestone trigger fired at #77 merge — condensed page committed on top of full history (pointer: `git log -p .orchestrator/local/ORCHESTRATOR_STATE.md`); verbatim core preserved (published `13c8b0d`)
- [x] NEXT PHASE (owner-directed): owner picks first product/research work order (ruling 2026-09-22: research follows maintenance) — **owner selected analysis task 005** (registry directive 2026-09-22)
- [x] 005: Scope + crosscheck `final_registry.csv` (owner's 259 personally-owned files, on `main` `cc7c5e8`) vs curated master — script + review CSV + report buckets A/B/C/D/E + focused tests + count house-rule; ANALYSIS ONLY (byte-freeze stands; no owned-flag writes; issue #18 = cited context, non-authoritative) — PR #78 **merged 2026-09-23** (`main` `1f7dab4`); MERGE reviewed same day; triage: 2 Session Irregularities → both Scoped
- [ ] AWAITING OWNER NEXT: options surfaced 2026-09-23 — (a) owner rulings on report buckets D (15 works) / E (41 evidence matches), (b) research-phase unfreeze instruction, (c) new directed task — **owner chose (c): 006 underscore standard** (D/E rulings remain open in the meantime)
- [ ] 006: Underscore convention for `proposed_filename` (both columns; collapse ` - ` → `_`, then spaces → `_`) — transform `data/filename_proposal_YYYYMM.csv` (363 rows, scoped owner-authorized input edit), crosscheck `proposed_stem` hardening with proven no-op BEFORE transform (bucket counts must hold 234/11/14, D15/E41, Σ259), regenerate generator outputs, delivery-contract refresh, tests/prose/counts (Published — dispatching 2026-09-23)

## Run Log

Seed entry (section established 2026-09-22 for CORE duty 4; destination declared on `main` by task 003):
- 2026-09-22 — engagement initialized (v4.9.1 first orchestrator); not a trigger-phrase fire — section seed only.
- 2026-09-22 — ANTI-DEGRADATION FRESHNESS (milestone: maintenance theme closed — PRs #74/#75/#76/#77 merged, `main` `ac6608a`): boot gate re-run against the canon — CORE sha256 `37b4c4254aa0e2cb418431a28d282041f233c442a1411f20024ea4fa2c697d52` matches tracker anchor (duty 3); five-duty gate **8/8 OK** in a clean clone of merged `main` (duty 5 live); discipline block re-quoted from tracker §1/§2 (research byte-freeze, scoreboard ban, CORE anchor authority, distribution shape). Discipline intact; no degradation signals.
- 2026-09-23 — ANTI-DEGRADATION FRESHNESS (milestone: owner-directed analysis 005 closed — PR #78 merged, `main` `1f7dab4`): CORE sha256 `37b4c4254aa0e2cb418431a28d282041f233c442a1411f20024ea4fa2c697d52` matches tracker anchor in a fresh clone (duty 3); five-duty gate **8/8 OK** online against merged `main` (duty 5 live); CI "Validate data pipeline and site" SUCCESS on `1f7dab4`; suite headcount 213 on main. Discipline re-quoted from tracker §1/§2: research byte-freeze intact through 005 (analysis-only: zero writes to `data/`, `final_registry.csv`, owned flags, `docs/*.json`), scoreboard ban intact (no `.scoreboard/` paths), CORE anchor authority intact, distribution shape intact (prompts+state on `arena/01a0cb00-docsheet` only), one-agent-at-a-time held (005 dispatch singular). Known local-only gap: sandbox lacks pandas (8 env failures locally; CI authoritative — recorded gap, not degradation).

## Interrupted Work

None. (001–004 → PRs #74–#77 merged; 005 → PR #78 reviewed MERGE, awaiting operator merge.)

## Deferred / Technical Debt

- v4.9.0 CORE lineage file absent from `main` (upgraded in place); historical anchor `e33886acbd12448bd2f91ce477c8dd733a49d1fbf12f9bd96f96734433bc18da` preserved in INIT-RECORD; re-materialize only if owner re-designates a source (HUB `56eli/REPOTESTER` presumed private — never auto-fetched).
- Branch protection on `main` unverifiable from sandbox (gh api → HTTP 403 "Resource not accessible by integration"); any future need to push `main` routes through the operator.
- ~55 historical `arena/*` agent branches remain on the remote (pre-orchestrator lineage); not orchestrator state, do not resume, do not delete without owner say-so.

## Scope Boundaries

- Research byte-freeze (standing until owner opens the research phase): `data/`, the schemas, and research docs/outputs untouched by maintenance tasks. Owner 2026-09-22: "We'll do research after we cleaned up the maintenance stuff."
- Scoped owner instruction 2026-09-23 (task 006): underscore standard for `proposed_filename` authorizes writes ONLY to the two filename columns of `data/filename_proposal_YYYYMM.csv` plus that sheet's generator outputs (discovered via build `--check` gates + `git status`). Every other freeze surface stands; raw lane and workflows untouched.
- Scoreboard is dismantled ("it definitely has to go"); no reintroduction, no new `.scoreboard/` paths.
- One agent at a time per repository; no dispatch overlap.
- Archive/ and superseded audits are historical, non-normative, never rewritten.
- Workflows (`.github/workflows/*`) change only on explicit owner instruction.

## Architectural Invariants

- CORE v4.9.1 governs; materialized file `orchestrator/ORCHESTRATOR CORE v4.9.1 — GENERAL PURPOSE.md` sha256 `37b4c4254aa0e2cb418431a28d282041f233c442a1411f20024ea4fa2c697d52` (source: owner-directed link to the `main` file, 2026-09-22). Anchor must be recorded in `docs/PROJECT_STATE.md` by task 001 (boot gap until merged: absent anchor = mismatch under the Initialization spec record law; no governed dispatch beyond 001 until recorded — 001 is the recording task).
- Distribution shape (owner-confirmed 2026-09-22, structured Q5): prompts at `.orchestrator/prompts/`, state at `.orchestrator/local/ORCHESTRATOR_STATE.md`, both on `arena/01a0cb00-docsheet`. Supersedes INIT-RECORD's "Governing Shape" (prompts on `main` under `orchestrator/prompts/`); divergence recorded here and to be recorded on the tracker by 001.
- Orchestrator never opens/merges PRs absent express per-PR operator authorization (verbatim-quote requirement); orchestrator branch never merges.
- Agents: branch from `main`; never from the orchestrator branch; never push to it; guarded publish/verify forms only; checkpoints via the universal one-command cadence.
- Generated artifacts never hand-edited — inputs → generators → `--check` gates green.
- Delivery contract: shipped asset/payload changes refresh `docs/index.html` version IDs + `docs/build-manifest.json` hashes in the same PR.
- Priority order: maintenance/governance first, research after (owner ruling 2026-09-22).
- Owner check-in assertions verified 2026-09-23 (evidence re-read on `main` `1f7dab4`): production chain = website (`https://56eli.github.io/docsheet`) ← migration ledger (`MIGRATION_REVIEW_LEDGER.md` + `migration_review_ledger.csv`, bootstrap-generated then hand-maintained approval surface) ← workflow verification vs Veritas publisher (`map_veritas_catalogue.yml` review-only job → `fetch_veritas_catalogue.py` against `veritaspub.com/wp-json/wp/v2/product*`, diff-vs-reviewed-inventory, contents:read) ← owner review accepting candidates (`manual_master_candidates.csv` 40/40 reviewed→promoted with dated owner approvals; `manual_candidate_promotions.csv` 40; `edition_promotions.csv` 24).
- CSV provenance doctrine (owner 2026-09-23): CSVs in this repo are **starter foundations or the repo's own exports — a full CSV is a PRODUCT, never the origin**. Origin = raw sheet `hawkins archive clone - Sheet1.csv` + external verification (Veritas API et al.) + owner rulings; complete-level CSVs (`research_master_draft.csv`, `migration_review_ledger.csv`, `lecture_series_review.csv`, crosscheck review CSV, `docs/data.json`) are derived products. Owner-supplied foundations (`final_registry.csv`, `filename_proposal_YYYYMM.csv`, reviewed inventories/queues/decisions) are inputs but still not "the origin." Work orders must not treat any full CSV as source-of-truth origin.
- File Name Proposal lineage (owner 2026-09-23): `data/filename_proposal_YYYYMM.csv` came **mostly from owner requests** — V1 "Requested pattern", V2/V3 "per owner request" (archive/FILENAME_PROPOSAL_YYYYMM_DVD01*.md), plus later owner revisions (e.g. 2026-08-09 REVISION1 ODS); task 006 underscore standard is the next request in that lineage. No code generator exists by design — the sheet is the owner-driven source of truth.

## Known Gaps

- Live: shallow clone (boot fetches are depth-1 — deepen per operation as this session already does); duty-5 gate baseline `df85a20` must stay inside the depth-50 window (revisit ~40 orch publishes, fail-closed message guides); no express PR-authorization quotes exist (none given, none needed yet); session `GH_TOKEN` can expire mid-task (orchestrator publishes + PR #78 authoring, 2026-09-22) — halt, report, request operator reconnect; never route around an auth failure.
- CLOSED-2026-09-22 tombstones (full text in this file's git history): boot anchor gap + stale INIT-RECORD row (closed by #74, `main` `39c464e`); `.gitignore` recovery declaration + tracker 158→166 count + handoff/prompt pointers (closed by #77, `main` `ac6608a`); two platform-rewind reconciliations (expected behavior — byte-verified recoveries with zero record loss; 4d71a55 and e9fce19 pin cycles).
- Tracker `docs/PROJECT_STATE.md` §4 still reads 166 tests / "next=owner-directed" — stale after #78 (suite now 213; 005 complete). Orchestrator never pushes `main`; refresh lands inside the next governed PR or by owner instruction.

## Hardening Log

| Date | Seq | Category | Symptom | Impact | Disposition | Hardening |
|---|---|---|---|---|---|---|
| 2026-09-22 | boot | Repository | CORE anchor absent for governing v4.9.1 file (INIT-RECORD still pins v4.9.0 sha; v4.9.0 lineage file missing from main) | boot mismatch under Initialization spec record law; recovery = record anchor via 001 | Hardening candidate | 001 records anchor in docs/PROJECT_STATE.md + fixes INIT-RECORD row |
| 2026-09-22 | boot | Prompt | INIT-RECORD "Governing Shape" (prompts on main) conflicts with CORE v4.9.1 branch model | would have dispatched from wrong ref | Scoped | owner resolved 2026-09-22 (Q5): CORE default; supersession to be recorded on tracker by 001 |
| 2026-09-22 | boot | Repository | .github/pull_request_template.md mandates dead `.scoreboard/manual-workflow-edits.md` path | every PR template shows nonexistent path | Hardening candidate | fixed by PR #75 (pending merge) |
| 2026-09-22 | 002 | Prompt | Work order §8 prescribed free target branch `fix/scoreboard-remnant-cleanup`, but Arena coding sessions are branch-locked to their provisioned `arena/*` branch | agent deviated (content/base correct); branch-name bookkeeping drift | Hardening candidate | from 003 on: §8 target = provisioned session branch; prescribe free-name fallback only for non-locked environments |
| 2026-09-22 | 002 | Prompt | Orchestrator quoted §6 old-side bytes from memory (`docs/audits` slash; Replacement B wrap) instead of copy-pasting command output | no block — §6 prefer-grep note steered agent to `main` bytes | Hardening candidate | authoring rule for self: run the anchor grep at authoring time; paste its literal output as every old side (quote-by-copy) |
| 2026-09-22 | 003 | Prompt | §6 example duty-5 assertion ("zero merge commits") was derived from doctrine, not the live DAG — branch history carries 26 pre-governance PR merges | ~10 min DAG investigation; agent re-derived assertion (merges-since-baseline `df85a20`) | Hardening candidate | authoring rule for self: any history/DAG-sensitive mechanical claim gets verified against the live DAG before authoring, or is marked advisory |
| 2026-09-22 | 005 | Environment | PR #78 authoring: session `GH_TOKEN` expired mid-task; agent halted and requested operator reconnect, retried after re-auth | blocked push until reconnect (minutes); no workaround attempted | Scoped | known platform class; reconnect procedure executed as designed — no new hardening needed |
| 2026-09-22 | 005 | Environment | Sandbox restore reverted local commits AND pushed session branch to base `cc7c5e8` (working tree survived; `/tmp` task copy lost) | checkpoint cadence destroyed — author recommitted as one commit `c86699b`, pushed clean fast-forward | Scoped | expected platform class (same as prior rewinds); author re-verified clean status/ancestry before push, CI green on final SHA — discipline held, no record loss |
