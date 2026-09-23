# Orchestrator Working State

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
| 003 | .orchestrator/prompts/003-orchestrator-behavior-gate.md | Add orchestrator behavior gate as a deterministic test stage | arena/01a0cb73-docsheet (session-locked) | #76 | MERGE verdict 2026-09-22 — awaiting operator merge (CI pass 1m27s on ceca7e0; 4-file scope; independent local gate run 8/8 OK + hatch OK; duty-5 baseline judgment call df85a20 documented and verified) |

## Active Milestone

Maintenance & governance hardening — tracker/anchor bootstrap → scoreboard remnants → orchestrator behavior gate → handoff-pointer hygiene — before any research or feature work (owner: "We'll do research after we cleaned up the maintenance stuff.").

## Task Queue

- [x] PR #74: 001 Tracker bootstrap + CORE anchor (Merged 2026-09-22 — `main` `39c464e`)
- [x] PR #75: 002 Scoreboard remnant cleanup (Merged 2026-09-22 — `main` `ff0f35b`)
- [x] PR #76: 003 Orchestrator behavior gate (Merged 2026-09-22 — `main` `923ba55`; gate live in CI; suite 166)
- [ ] 004: Handoff-pointer hygiene + owner-ruled patch move — stub redirects (v4.9.1), prompts-README corrected shape, `.gitignore` recovery line, README/INSTRUCTIONS pointers → tracker, tracker §4 (milestone complete / 166 / next=owner-directed), `git mv` init patch → `archive/` (Published — dispatching 2026-09-22; §2 byte-frozen for gate)
- [ ] After 004: owner-directed product/research work — owner picks first work order (ruling 2026-09-22)

## Run Log

Seed entry (section established 2026-09-22 for CORE duty 4; destination declared on `main` by task 003):
- 2026-09-22 — engagement initialized (v4.9.1 first orchestrator); not a trigger-phrase fire — section seed only.

## Interrupted Work

None. (001 → PR #74 merged; 002 → PR #75 merged; 003 publishing now.)

## Deferred / Technical Debt

- v4.9.0 CORE lineage file absent from `main` (upgraded in place); historical anchor `e33886acbd12448bd2f91ce477c8dd733a49d1fbf12f9bd96f96734433bc18da` preserved in INIT-RECORD; re-materialize only if owner re-designates a source (HUB `56eli/REPOTESTER` presumed private — never auto-fetched).
- Branch protection on `main` unverifiable from sandbox (gh api → HTTP 403 "Resource not accessible by integration"); any future need to push `main` routes through the operator.
- ~55 historical `arena/*` agent branches remain on the remote (pre-orchestrator lineage); not orchestrator state, do not resume, do not delete without owner say-so.

## Scope Boundaries

- Research byte-freeze (standing until owner opens the research phase): `data/`, the schemas, and research docs/outputs untouched by maintenance tasks. Owner 2026-09-22: "We'll do research after we cleaned up the maintenance stuff."
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

## Known Gaps

- Canonical tracker EXISTS on `main` since 2026-09-22 (PR #74 merged, `main` `39c464e`); CORE v4.9.1 anchor recorded there and in INIT-RECORD — boot anchor gap CLOSED. Recompute `sha256sum` against the tracker anchor at every boot/gate.
- Shallow clone (depth-1 fetches): `main` history beyond the tip was unreadable at boot; a depth-50 `_orch` fetch later revealed `bdebc4c` "Delete orchestrator/ORCHESTRATOR CORE v4.9.0 — GENERAL PURPOSE.md" + `7fc942e` "Add files via upload", confirming the in-place v4.9.1 upgrade and the missing-lineage-file finding.
- INIT-RECORD anchor row corrected on `main` by PR #74 (stale-row gap CLOSED).
- No express PR-authorization quotes exist (none given; none needed yet).
- Platform rewind observed 2026-09-22 after the001 publish: worktree returned to `06572b5` while remote pin stayed at `4d71a55`; reconciled by byte-comparing local records against the pin (both equal — no unpublished loss), then reset to the pin per the guarded recovery path. Expected platform behavior, not an irregularity.
- `.orchestrator/local/recovery/` is untracked-by-design (never staged; allowlist enforces). Repo `.gitignore` does not list it — candidate one-line addition for hygiene task 004, since only `main` may change `.gitignore`.
- Duty-5 gate baseline `df85a20` must stay inside the bounded depth-50 fetch window as orchestrator history grows (failure is fail-closed with a deepen/re-anchor message). Revisit when the orch branch accumulates ~40+ publishes.
- Tracker §4 "Current State" still says "158 Python tests" after PR #76 makes the suite 166 (work order forbade touching that line); fold a one-line count refresh into task 004's tracker edit so the canonical tracker stops contradicting README/INSTRUCTIONS.

## Hardening Log

| Date | Seq | Category | Symptom | Impact | Disposition | Hardening |
|---|---|---|---|---|---|---|
| 2026-09-22 | boot | Repository | CORE anchor absent for governing v4.9.1 file (INIT-RECORD still pins v4.9.0 sha; v4.9.0 lineage file missing from main) | boot mismatch under Initialization spec record law; recovery = record anchor via 001 | Hardening candidate | 001 records anchor in docs/PROJECT_STATE.md + fixes INIT-RECORD row |
| 2026-09-22 | boot | Prompt | INIT-RECORD "Governing Shape" (prompts on main) conflicts with CORE v4.9.1 branch model | would have dispatched from wrong ref | Scoped | owner resolved 2026-09-22 (Q5): CORE default; supersession to be recorded on tracker by 001 |
| 2026-09-22 | boot | Repository | .github/pull_request_template.md mandates dead `.scoreboard/manual-workflow-edits.md` path | every PR template shows nonexistent path | Hardening candidate | fixed by PR #75 (pending merge) |
| 2026-09-22 | 002 | Prompt | Work order §8 prescribed free target branch `fix/scoreboard-remnant-cleanup`, but Arena coding sessions are branch-locked to their provisioned `arena/*` branch | agent deviated (content/base correct); branch-name bookkeeping drift | Hardening candidate | from 003 on: §8 target = provisioned session branch; prescribe free-name fallback only for non-locked environments |
| 2026-09-22 | 002 | Prompt | Orchestrator quoted §6 old-side bytes from memory (`docs/audits` slash; Replacement B wrap) instead of copy-pasting command output | no block — §6 prefer-grep note steered agent to `main` bytes | Hardening candidate | authoring rule for self: run the anchor grep at authoring time; paste its literal output as every old side (quote-by-copy) |
| 2026-09-22 | 003 | Prompt | §6 example duty-5 assertion ("zero merge commits") was derived from doctrine, not the live DAG — branch history carries 26 pre-governance PR merges | ~10 min DAG investigation; agent re-derived assertion (merges-since-baseline `df85a20`) | Hardening candidate | authoring rule for self: any history/DAG-sensitive mechanical claim gets verified against the live DAG before authoring, or is marked advisory |
