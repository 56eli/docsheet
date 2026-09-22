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
| 002 | .orchestrator/prompts/002-scoreboard-remnant-cleanup.md | Remove dead .scoreboard/ references from the PR template | fix/scoreboard-remnant-cleanup (planned) | — | Published — dispatching now |

## Active Milestone

Maintenance & governance hardening — tracker/anchor bootstrap → scoreboard remnants → orchestrator behavior gate → handoff-pointer hygiene — before any research or feature work (owner: "We'll do research after we cleaned up the maintenance stuff.").

## Task Queue

- [x] PR #74: 001 Create `docs/PROJECT_STATE.md` (Knowledge Bridge structure + CORE v4.9.1 anchor) + INIT-RECORD anchor fix (Merged 2026-09-22 — refresh confirmed tracker/anchor on `main` `39c464e`)
- [ ] 002: Scoreboard remnant cleanup — `.github/pull_request_template.md` two dead refs → owner policy; tracker Immediate Next Task → behavior gate (Published — dispatching 2026-09-22)
- [ ] 003 (queued): Orchestrator behavior gate — repo-adaptive mechanical checker covering the five duties, with honest boundary statement (CORE "Orchestrator behavior gating")
- [ ] 004 (queued): Handoff-pointer hygiene — `AGENTS.md` / `NEXT_AGENT_HANDOFF.md` / `orchestrator/prompts/README.md` (still claims superseded prompts-on-main shape) / `.gitignore` line for `.orchestrator/local/recovery/`; root `0001-Init-v4.9.0-…patch` placement question (archive?) flagged for owner at that hand-back
- [ ] Deferred: owner-picked product/research work — begins only after maintenance queue clears (owner ruling 2026-09-22)

## Interrupted Work

None. (001 agent completed normally — PR #74 open, MERGE reviewed.)

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

## Hardening Log

| Date | Seq | Category | Symptom | Impact | Disposition | Hardening |
|---|---|---|---|---|---|---|
| 2026-09-22 | boot | Repository | CORE anchor absent for governing v4.9.1 file (INIT-RECORD still pins v4.9.0 sha; v4.9.0 lineage file missing from main) | boot mismatch under Initialization spec record law; recovery = record anchor via 001 | Hardening candidate | 001 records anchor in docs/PROJECT_STATE.md + fixes INIT-RECORD row |
| 2026-09-22 | boot | Prompt | INIT-RECORD "Governing Shape" (prompts on main) conflicts with CORE v4.9.1 branch model | would have dispatched from wrong ref | Scoped | owner resolved 2026-09-22 (Q5): CORE default; supersession to be recorded on tracker by 001 |
| 2026-09-22 | boot | Repository | .github/pull_request_template.md mandates dead `.scoreboard/manual-workflow-edits.md` path | every PR template shows nonexistent path | Hardening candidate | queued as task 002 |
